"""
src/report_generator.py — HTML report builder.

Generates a self-contained HTML file (charts embedded as base64 PNG)
that can be downloaded from the dashboard and opened/printed in any browser.
No external dependencies beyond matplotlib and pandas.
"""
import io
import base64
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd


# ── chart helpers ──────────────────────────────────────────────────────────────

DARK_FG   = "#c9d1d9"
DARK_BG   = "#0d1117"
GRID_CLR  = "#21262d"
BLUE      = "#58a6ff"
GREEN     = "#3fb950"
RED       = "#f85149"
AMBER     = "#d29922"
PURPLE    = "#bc8cff"


def _apply_dark_style(ax, fig):
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor("#161b22")
    ax.tick_params(colors=DARK_FG, labelsize=9)
    ax.xaxis.label.set_color(DARK_FG)
    ax.yaxis.label.set_color(DARK_FG)
    ax.title.set_color(DARK_FG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_CLR)
    ax.grid(color=GRID_CLR, linestyle="--", linewidth=0.5)


def _fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight",
                facecolor=DARK_BG, edgecolor="none", dpi=120)
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return data


def _chart_reward(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(df["step"], df["reward"], color=GREEN, linewidth=1.2, alpha=0.9)
    ax.axhline(df["reward"].mean(), color=BLUE, linewidth=1, linestyle="--",
               label=f"Mean: {df['reward'].mean():.4f}")
    ax.set_xlabel("Step"); ax.set_ylabel("Reward")
    ax.set_title("Reward over Time (higher = less waiting)"); ax.legend(fontsize=8)
    _apply_dark_style(ax, fig)
    return _fig_to_b64(fig)


def _chart_queue(df: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.fill_between(df["step"], df["total_queue"], color=RED, alpha=0.3)
    ax.plot(df["step"], df["total_queue"], color=RED, linewidth=1.2)
    ax.set_xlabel("Step"); ax.set_ylabel("Vehicles")
    ax.set_title("Total Queue Length per Step")
    _apply_dark_style(ax, fig)
    return _fig_to_b64(fig)


def _chart_congestion_pie(df: pd.DataFrame) -> str:
    counts = df["congestion"].value_counts()
    labels = [k.title() for k in counts.index]
    colors = [GREEN if k == "free" else AMBER if k == "moderate" else RED
              for k in counts.index]
    fig, ax = plt.subplots(figsize=(4, 4))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=140,
        textprops={"color": DARK_FG, "fontsize": 10},
    )
    for at in autotexts:
        at.set_color(DARK_BG); at.set_fontweight("bold")
    ax.set_title("Congestion Distribution", color=DARK_FG)
    return _fig_to_b64(fig)


def _chart_lane_heatmap(df: pd.DataFrame) -> str:
    lane_cols = [c for c in df.columns if c.startswith("lane_")]
    if not lane_cols:
        return ""
    data = df[lane_cols].tail(100).T.values
    fig, ax = plt.subplots(figsize=(10, max(2, len(lane_cols) * 0.4)))
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn_r",
                   vmin=0, vmax=data.max() or 1)
    ax.set_yticks(range(len(lane_cols)))
    ax.set_yticklabels(lane_cols, fontsize=7)
    ax.set_xlabel("Step (last 100)", fontsize=8)
    ax.set_title("Lane Queue Heatmap (red = congested)", fontsize=9)
    plt.colorbar(im, ax=ax, fraction=0.02)
    _apply_dark_style(ax, fig)
    return _fig_to_b64(fig)


def _chart_comparison_bar(runs_df: pd.DataFrame) -> str:
    """Bar chart comparing avg_queue across multiple saved runs."""
    if runs_df is None or len(runs_df) == 0:
        return ""
    labels = [f"[{r['id']}] {r['method'][:18]}" for _, r in runs_df.iterrows()]
    values = runs_df["avg_queue"].tolist()
    colors = [GREEN if v == min(values) else BLUE for v in values]
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 1.2), 4))
    bars = ax.bar(labels, values, color=colors, edgecolor=GRID_CLR, linewidth=0.5)
    ax.set_ylabel("Avg queue (vehicles/step)")
    ax.set_title("Average Queue Comparison Across Runs")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{val:.2f}", ha="center", va="bottom", fontsize=9, color=DARK_FG)
    plt.xticks(rotation=25, ha="right", fontsize=8)
    _apply_dark_style(ax, fig)
    return _fig_to_b64(fig)


# ── HTML template ──────────────────────────────────────────────────────────────

def generate_html_report(
    method: str,
    df: pd.DataFrame,
    carbon: dict | None = None,
    all_runs_df: pd.DataFrame | None = None,
    notes: str = "",
) -> str:
    """
    Generate a self-contained HTML report.

    Args:
        method       : controller method name
        df           : full step DataFrame for this run
        carbon       : dict from carbon_calculator.estimate_savings()
        all_runs_df  : summary table of all historical runs
        notes        : optional user notes

    Returns:
        HTML string (with embedded charts).
    """
    now       = datetime.now().strftime("%Y-%m-%d %H:%M")
    r_chart   = _chart_reward(df)
    q_chart   = _chart_queue(df)
    pie_chart = _chart_congestion_pie(df)
    lane_chart= _chart_lane_heatmap(df)
    cmp_chart = _chart_comparison_bar(all_runs_df) if all_runs_df is not None else ""

    avg_rw    = df["reward"].mean()
    avg_q     = df["total_queue"].mean()
    peak_q    = df["total_queue"].max()
    hi_pct    = (df["congestion"] == "high").mean() * 100
    free_pct  = (df["congestion"] == "free").mean() * 100

    # carbon section (conditional)
    carbon_html = ""
    if carbon and carbon.get("queue_reduction_pct", 0) > 0:
        carbon_html = f"""
        <div class="section">
          <h2>🌍 Environmental Impact</h2>
          <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Queue reduction vs fixed-cycle</td><td><b>{carbon['queue_reduction_pct']:.1f}%</b></td></tr>
            <tr><td>Vehicle-wait-seconds saved (this episode)</td><td>{carbon['vehicle_wait_sec_saved']:,.0f} s</td></tr>
            <tr><td>Fuel saved (this episode, 1 junction)</td><td>{carbon['fuel_litres_saved_ep']:.3f} L</td></tr>
            <tr><td>CO₂ saved (this episode, 1 junction)</td><td>{carbon['co2_kg_saved_ep']:.3f} kg</td></tr>
            <tr><td>CO₂ saved daily (all 47 Mangalore junctions)</td><td><b>{carbon['co2_kg_saved_daily']:.1f} kg/day</b></td></tr>
            <tr><td>CO₂ saved annually</td><td><b>{carbon['co2_tonnes_saved_yearly']:.2f} tonnes/year</b></td></tr>
            <tr><td>Equivalent trees planted</td><td>🌳 {carbon['trees_equivalent']:.0f} trees</td></tr>
          </table>
        </div>
        """

    # historical comparison section (conditional)
    history_html = ""
    if all_runs_df is not None and len(all_runs_df) > 1:
        rows = "".join(
            f"<tr><td>{r['id']}</td><td>{r['timestamp']}</td><td>{r['method']}</td>"
            f"<td>{r['avg_reward']}</td><td>{r['avg_queue']}</td>"
            f"<td>{r['high_cong_pct']}%</td><td>{r['notes'] or '—'}</td></tr>"
            for _, r in all_runs_df.iterrows()
        )
        cmp_img = f'<img src="data:image/png;base64,{cmp_chart}" style="width:100%">' if cmp_chart else ""
        history_html = f"""
        <div class="section">
          <h2>🗓️ Historical Run Comparison</h2>
          {cmp_img}
          <table>
            <tr>
              <th>ID</th><th>Timestamp</th><th>Method</th>
              <th>Avg Reward</th><th>Avg Queue</th><th>High Cong%</th><th>Notes</th>
            </tr>
            {rows}
          </table>
        </div>
        """

    notes_html = f'<p class="notes"><b>Notes:</b> {notes}</p>' if notes else ""

    lane_img  = f'<img src="data:image/png;base64,{lane_chart}" style="width:100%">' if lane_chart else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Mangalore Traffic AI — Simulation Report</title>
<style>
  body {{
    background: #0d1117; color: #c9d1d9;
    font-family: 'Segoe UI', Arial, sans-serif;
    margin: 0; padding: 2rem;
  }}
  h1  {{ color: #58a6ff; border-bottom: 2px solid #21262d; padding-bottom: .5rem; }}
  h2  {{ color: #c9d1d9; margin-top: 2rem; }}
  .section {{ background: #161b22; border: 1px solid #21262d;
              border-radius: 8px; padding: 1.5rem; margin: 1.5rem 0; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
  th {{ background: #21262d; color: #58a6ff; padding: .5rem .75rem;
        text-align: left; font-size: .9rem; }}
  td {{ padding: .45rem .75rem; border-bottom: 1px solid #21262d;
        font-size: .88rem; }}
  tr:hover td {{ background: #1c2333; }}
  .metric-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem; margin: 1rem 0;
  }}
  .metric {{ background: #1c2333; border-radius: 6px; padding: 1rem;
             text-align: center; border: 1px solid #30363d; }}
  .metric .val {{ font-size: 1.8rem; font-weight: 700; color: #58a6ff; }}
  .metric .lbl {{ font-size: .75rem; color: #8b949e; margin-top: .3rem; }}
  .badge {{ display:inline-block; padding:.2rem .6rem; border-radius:99px;
            background:rgba(35,134,54,.25); color:#3fb950;
            font-size:.8rem; font-weight:600; margin-left:.5rem; }}
  .notes {{ color: #8b949e; font-style: italic; }}
  img {{ border-radius: 6px; margin-top: .5rem; }}
  footer {{ text-align:center; color:#30363d; margin-top:3rem; font-size:.8rem; }}
</style>
</head>
<body>
<h1>🚦 Mangalore Traffic AI — Simulation Report</h1>
<p>Generated: <b>{now}</b> &nbsp;|&nbsp; Controller: <b>{method}</b> <span class="badge">AI</span></p>
{notes_html}

<div class="section">
  <h2>📈 Summary Metrics</h2>
  <div class="metric-grid">
    <div class="metric"><div class="val">{len(df)}</div><div class="lbl">Total steps</div></div>
    <div class="metric"><div class="val">{avg_rw:.4f}</div><div class="lbl">Avg reward/step</div></div>
    <div class="metric"><div class="val">{avg_q:.2f}</div><div class="lbl">Avg queue (cars)</div></div>
    <div class="metric"><div class="val">{peak_q:.0f}</div><div class="lbl">Peak queue (cars)</div></div>
    <div class="metric"><div class="val">{free_pct:.1f}%</div><div class="lbl">Free-flow steps</div></div>
    <div class="metric"><div class="val">{hi_pct:.1f}%</div><div class="lbl">High-congestion steps</div></div>
  </div>
</div>

<div class="section">
  <h2>📊 Reward Over Time</h2>
  <img src="data:image/png;base64,{r_chart}" style="width:100%">
</div>

<div class="section">
  <h2>🚗 Queue Length Over Time</h2>
  <img src="data:image/png;base64,{q_chart}" style="width:100%">
</div>

<div class="section">
  <h2>🌡️ Lane Queue Heatmap</h2>
  {lane_img if lane_img else '<p>No lane data available.</p>'}
</div>

<div class="section">
  <h2>🔴 Congestion Distribution</h2>
  <img src="data:image/png;base64,{pie_chart}" style="width:350px;display:block;margin:auto">
</div>

{carbon_html}
{history_html}

<footer>Mangalore Traffic AI &nbsp;•&nbsp; Report generated automatically &nbsp;•&nbsp; {now}</footer>
</body>
</html>"""
