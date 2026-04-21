"""
src/database.py — SQLite persistence for simulation runs.

Stores every run's summary stats and full step-by-step DataFrame so you
can reload any past episode in the History tab.
"""
import os
import sqlite3
import json
import pandas as pd
from datetime import datetime
import hashlib
import secrets

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "simulation_history.db")


class SimulationDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    # ── schema ────────────────────────────────────────────────────────────────

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp      TEXT    NOT NULL,
                    method         TEXT    NOT NULL,
                    steps          INTEGER,
                    avg_reward     REAL,
                    avg_queue      REAL,
                    peak_queue     REAL,
                    high_cong_pct  REAL,
                    free_cong_pct  REAL,
                    notes          TEXT,
                    df_json        TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    username       TEXT UNIQUE NOT NULL,
                    password_hash  TEXT NOT NULL,
                    salt           TEXT NOT NULL,
                    created_at     TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reset_tokens (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    username       TEXT NOT NULL,
                    token          TEXT UNIQUE NOT NULL,
                    expires_at     REAL NOT NULL
                )
            """)
            conn.commit()

    # ── admin auth ────────────────────────────────────────────────────────────

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()

    def register_admin(self, username: str, password: str) -> tuple[bool, str]:
        username = (username or "").strip()
        password = password or ""
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."

        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO admins (username, password_hash, salt, created_at)
                       VALUES (?, ?, ?, ?)""",
                    (username, password_hash, salt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                )
                conn.commit()
            return True, "Admin registered successfully."
        except sqlite3.IntegrityError:
            return False, "Username already exists."

    def authenticate_admin(self, username: str, password: str) -> bool:
        username = (username or "").strip()
        password = password or ""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT password_hash, salt FROM admins WHERE username=?",
                (username,),
            ).fetchone()
        if not row:
            return False
        saved_hash, salt = row
        return saved_hash == self._hash_password(password, salt)

    def has_admins(self) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
        return count > 0

    # ── recovery ──────────────────────────────────────────────────────────────

    def create_reset_token(self, username: str, expires_in: int = 3600) -> str:
        """Generates a secure token for password reset."""
        import time
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + expires_in
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM reset_tokens WHERE username = ?", (username,))
            conn.execute(
                "INSERT INTO reset_tokens (username, token, expires_at) VALUES (?, ?, ?)",
                (username, token, expires_at)
            )
            conn.commit()
        return token

    def validate_reset_token(self, token: str) -> str | None:
        """Returns the username if token is valid, else None."""
        import time
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username FROM reset_tokens WHERE token = ? AND expires_at > ?",
                (token, time.time())
            )
            row = cursor.fetchone()
            if row:
                username = row[0]
                # Consume token
                conn.execute("DELETE FROM reset_tokens WHERE token = ?", (token,))
                conn.commit()
                return username
        return None

    def reset_password(self, username: str, new_password: str):
        """Updates admin password with new hash and salt."""
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(new_password, salt)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE admins SET password_hash = ?, salt = ? WHERE username = ?",
                (password_hash, salt, username)
            )
            conn.commit()

    # ── write ─────────────────────────────────────────────────────────────────

    def save_run(self, method: str, df: pd.DataFrame, notes: str = "") -> int:
        """Persist a completed simulation run. Returns the new run id."""
        high_pct = float((df["congestion"] == "high").mean() * 100)
        free_pct = float((df["congestion"] == "free").mean() * 100)
        record = {
            "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "method":        method,
            "steps":         len(df),
            "avg_reward":    float(df["reward"].mean()),
            "avg_queue":     float(df["total_queue"].mean()),
            "peak_queue":    float(df["total_queue"].max()),
            "high_cong_pct": high_pct,
            "free_cong_pct": free_pct,
            "notes":         notes,
            "df_json":       df.to_json(orient="records"),
        }
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """INSERT INTO runs
                   (timestamp,method,steps,avg_reward,avg_queue,peak_queue,
                    high_cong_pct,free_cong_pct,notes,df_json)
                   VALUES (:timestamp,:method,:steps,:avg_reward,:avg_queue,
                           :peak_queue,:high_cong_pct,:free_cong_pct,:notes,:df_json)""",
                record,
            )
            return cur.lastrowid

    # ── read ──────────────────────────────────────────────────────────────────

    def get_all_runs(self) -> pd.DataFrame:
        """Return summary table of all runs (no raw step data)."""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql(
                """SELECT id, timestamp, method, steps,
                          ROUND(avg_reward,4)    AS avg_reward,
                          ROUND(avg_queue,2)     AS avg_queue,
                          ROUND(peak_queue,0)    AS peak_queue,
                          ROUND(high_cong_pct,1) AS high_cong_pct,
                          ROUND(free_cong_pct,1) AS free_cong_pct,
                          notes
                   FROM runs ORDER BY id DESC""",
                conn,
            )
        return df

    def get_run_df(self, run_id: int) -> pd.DataFrame | None:
        """Load the full step DataFrame for a single run."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT df_json FROM runs WHERE id=?", (run_id,)
            ).fetchone()
        if row:
            return pd.read_json(row[0], orient="records")
        return None

    def get_run_meta(self, run_id: int) -> dict | None:
        """Load summary metadata for one run."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """SELECT id,timestamp,method,steps,avg_reward,avg_queue,
                          peak_queue,high_cong_pct,free_cong_pct,notes
                   FROM runs WHERE id=?""",
                (run_id,),
            ).fetchone()
        if row:
            cols = ["id","timestamp","method","steps","avg_reward","avg_queue",
                    "peak_queue","high_cong_pct","free_cong_pct","notes"]
            return dict(zip(cols, row))
        return None

    def delete_run(self, run_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM runs WHERE id=?", (run_id,))

    def run_count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
