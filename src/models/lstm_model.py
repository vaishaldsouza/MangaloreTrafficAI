"""
src/models/lstm_model.py

Method 3 — LSTM for traffic volume prediction.
Predicts the next-step vehicle count per lane using a sequence of past
observations (default: last 12 steps = 1 hour of 5-min intervals).

Architecture based on:
    Hochreiter & Schmidhuber (1997) — LSTM networks
    Literature target: > 90% accuracy on highway volume data

Run:
    python -m src.models.lstm_model
"""
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import os


# ---------------------------------------------------------------------------
# Model definition
# ---------------------------------------------------------------------------

class TrafficLSTM(nn.Module):
    """
    Predicts next-step vehicle count per lane.

    Input:  (batch, seq_len, n_features)
    Output: (batch, n_lanes)
    """

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        n_lanes: int = 4,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, n_lanes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (batch, seq_len, input_size)"""
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])   # use only the last timestep


# ---------------------------------------------------------------------------
# Data utilities
# ---------------------------------------------------------------------------

def make_sequences(data: np.ndarray, seq_len: int = 12):
    """
    Sliding window over time-series data.

    Args:
        data:    np.array shape (T, n_features)
        seq_len: lookback window (12 × 5 min = 1 hour)

    Returns:
        X: (T-seq_len, seq_len, n_features)
        y: (T-seq_len, n_lanes)  — first 4 columns are lane counts
    """
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len, :4])   # first 4 cols = N/S/E/W lane counts
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def generate_lstm_data(n_hours: int = 1440, seed: int = 42) -> np.ndarray:
    """
    Synthetic Mangalore traffic data as a normalised numpy array.
    Columns: [N_count, S_count, E_count, W_count, hour_sin, hour_cos]
    """
    np.random.seed(seed)
    timestamps = np.arange(n_hours)
    hours = timestamps % 24
    records = []
    for h in hours:
        if 8 <= h <= 10:
            base = 80
        elif 17 <= h <= 19:
            base = 90
        elif 0 <= h <= 5:
            base = 10
        else:
            base = 40
        records.append([
            np.random.poisson(base * 1.2),  # North
            np.random.poisson(base * 1.0),  # South
            np.random.poisson(base * 0.7),  # East
            np.random.poisson(base * 0.8),  # West
            np.sin(h * (2 * np.pi / 24)),   # hour_sin
            np.cos(h * (2 * np.pi / 24)),   # hour_cos
        ])
    arr = np.array(records, dtype=np.float32)
    # Normalise lane counts to [0, 1]
    arr[:, :4] /= 150.0
    return arr


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_lstm(
    data_array: np.ndarray,
    epochs: int = 50,
    lr: float = 1e-3,
    seq_len: int = 12,
    batch_size: int = 64,
    device: str = "cpu",
) -> TrafficLSTM:
    """
    Train the LSTM on a normalised numpy array.

    Args:
        data_array: (T, n_features) — columns must start with 4 lane counts.

    Returns:
        Trained TrafficLSTM model.
    """
    X, y = make_sequences(data_array, seq_len)
    split = int(len(X) * 0.8)
    X_tr, X_te = X[:split], X[split:]
    y_tr, y_te = y[:split], y[split:]

    tr_loader = DataLoader(
        TensorDataset(torch.tensor(X_tr), torch.tensor(y_tr)),
        batch_size=batch_size,
        shuffle=False,
    )

    model = TrafficLSTM(
        input_size=X.shape[2],
        hidden_size=128,
        num_layers=2,
        n_lanes=4,
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    print("[LSTM] Starting training...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for xb, yb in tr_loader:
            xb, yb = xb.to(device), yb.to(device)
            pred = model(xb)
            loss = criterion(pred, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        if epoch % 10 == 0 or epoch == epochs - 1:
            model.eval()
            with torch.no_grad():
                val_pred = model(torch.tensor(X_te).to(device))
                val_loss = criterion(val_pred, torch.tensor(y_te).to(device))
            print(
                f"  Epoch {epoch:3d}/{epochs} | "
                f"Train loss: {total_loss/len(tr_loader):.4f} | "
                f"Val loss: {val_loss.item():.4f}"
            )

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/lstm_traffic.pt")
    print("\nSaved: models/lstm_traffic.pt")
    return model


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating synthetic traffic sequences (1440 hours)...")
    data = generate_lstm_data(n_hours=1440)
    train_lstm(data, epochs=50)
