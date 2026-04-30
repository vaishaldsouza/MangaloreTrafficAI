"""
src/models/gcn_lstm_model.py

Method 4 — Graph Convolutional Network + LSTM (spatial-temporal model).
Models both HOW congestion spreads across the road network (spatial, via GCN)
and WHEN it occurs (temporal, via LSTM).

Based on: DCRNN — Li et al. (2018)
    "Diffusion Convolutional Recurrent Neural Network: Data-Driven Traffic Forecasting"

Requires: pip install torch-geometric

Run:
    python -m src.models.gcn_lstm_model
"""
import torch
import torch.nn as nn
import numpy as np
import os


# ---------------------------------------------------------------------------
# Model definition
# ---------------------------------------------------------------------------

class SpatialTemporalModel(nn.Module):
    """
    GCN captures how congestion propagates across junctions.
    LSTM captures time-series patterns per junction.

    Args:
        node_features: Number of features per junction per timestep.
        hidden:        GCN hidden dimension.
        lstm_hidden:   LSTM hidden dimension.
    """

    def __init__(
        self,
        node_features: int,
        hidden: int = 64,
        lstm_hidden: int = 128,
    ):
        super().__init__()
        # Lazy import so the rest of the project works without torch-geometric
        try:
            from torch_geometric.nn import GCNConv
            self.gcn1 = GCNConv(node_features, hidden)
            self.gcn2 = GCNConv(hidden, hidden)
            self._has_pyg = True
        except ImportError:
            print("[GCN-LSTM] torch-geometric not installed — using linear fallback.")
            self.gcn1 = nn.Linear(node_features, hidden)
            self.gcn2 = nn.Linear(hidden, hidden)
            self._has_pyg = False

        self.lstm = nn.LSTM(hidden, lstm_hidden, batch_first=True)
        self.fc   = nn.Sequential(
            nn.Linear(lstm_hidden, 32),
            nn.ReLU(),
            nn.Linear(32, 1),   # congestion score per node
        )

    def _gcn_step(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        if self._has_pyg:
            return torch.relu(self.gcn2(torch.relu(self.gcn1(x, edge_index)), edge_index))
        else:
            return torch.relu(self.gcn2(torch.relu(self.gcn1(x))))

    def forward(
        self,
        x_seq: torch.Tensor,
        edge_index: torch.Tensor,
    ) -> torch.Tensor:
        """
        Args:
            x_seq:      (T, N, node_features) — T timesteps, N junctions
            edge_index: (2, E)               — road graph edges

        Returns:
            (N,) congestion prediction per junction
        """
        spatial_out = []
        for t in range(x_seq.size(0)):
            h = self._gcn_step(x_seq[t], edge_index)
            spatial_out.append(h)

        # (N, T, hidden) → LSTM
        h_seq = torch.stack(spatial_out, dim=1)
        lstm_out, _ = self.lstm(h_seq)          # (N, T, lstm_hidden)
        pred = self.fc(lstm_out[:, -1, :])      # (N, 1)
        return pred.squeeze(-1)                 # (N,)


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph_from_sumo_net(net_path: str = "simulation/mangalore.net.xml"):
    """Build edge_index from SUMO .net.xml — no internet needed."""
    import xml.etree.ElementTree as ET

    if not os.path.exists(net_path):
        print(f"[GCN] Error: {net_path} not found.")
        return torch.empty((2, 0), dtype=torch.long), {}

    tree = ET.parse(net_path)
    root = tree.getroot()

    # Collect junction IDs (skip internal :junctions)
    junctions = [j.attrib["id"] for j in root.findall("junction")
                 if not j.attrib["id"].startswith(":")]
    node_idx = {jid: i for i, jid in enumerate(junctions)}

    edges = []
    for edge in root.findall("edge"):
        if edge.attrib.get("id", "").startswith(":"):
            continue
        src = edge.attrib.get("from")
        dst = edge.attrib.get("to")
        if src in node_idx and dst in node_idx:
            edges.append([node_idx[src], node_idx[dst]])

    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
    print(f"[GCN] {len(junctions)} junctions, {len(edges)} road edges")
    return edge_index, node_idx


def build_mangalore_graph(radius_m: int = 2000):
    """
    Build a PyTorch Geometric edge_index from the Mangalore OSM road graph.
    Returns:
        edge_index: (2, E) LongTensor
        node_idx:   dict mapping OSM node id → integer index
    """
    try:
        import osmnx as ox
    except ImportError:
        raise ImportError("pip install osmnx")

    CENTER = (12.8700, 74.8436)
    print(f"[GCN] Downloading Mangalore OSM graph (radius={radius_m}m)...")
    G = ox.graph_from_point(CENTER, dist=radius_m, network_type="drive")

    nodes = list(G.nodes())
    node_idx = {n: i for i, n in enumerate(nodes)}

    edges = []
    for u, v in G.edges():
        if u in node_idx and v in node_idx:
            edges.append([node_idx[u], node_idx[v]])
            edges.append([node_idx[v], node_idx[u]])   # undirected

    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
    print(f"[GCN] Graph: {len(nodes)} junctions, {len(edges)//2} road segments")
    return edge_index, node_idx


# ---------------------------------------------------------------------------
# Synthetic training data
# ---------------------------------------------------------------------------

def _make_synthetic_node_data(n_nodes: int, T: int = 50, n_feat: int = 4) -> torch.Tensor:
    """Returns (T, N, n_feat) synthetic junction feature tensor."""
    data = torch.rand(T, n_nodes, n_feat)
    return data


def collect_sumo_node_features(node_idx: dict, step_data: list) -> torch.Tensor:
    """
    Convert simulation history rows into (T, N, 4) node feature tensor.
    
    step_data: list of dicts with keys junction_id, queue, wait, phase, vehicles
    node_idx:  junction_id -> integer index
    """
    n_nodes = len(node_idx)
    T = len(step_data)
    x = torch.zeros(T, n_nodes, 4)

    for t, row in enumerate(step_data):
        for jid, idx in node_idx.items():
            jdata = row.get(jid, {})
            x[t, idx, 0] = jdata.get("queue",    0) / 20.0   # normalised
            x[t, idx, 1] = jdata.get("wait",     0) / 300.0
            x[t, idx, 2] = jdata.get("phase",    0) / 4.0
            x[t, idx, 3] = jdata.get("vehicles", 0) / 50.0
    return x


# ---------------------------------------------------------------------------
# Training demo
# ---------------------------------------------------------------------------

def train_gcn_lstm(
    net_path:   str = "simulation/mangalore.net.xml",
    step_data:  list = None,   # from collect_sumo_node_features
    epochs:     int  = 50,
    seq_len:    int  = 12,     # 12 steps × 5s = 1 min lookback
    lr:         float = 1e-3,
):
    edge_index, node_idx = build_graph_from_sumo_net(net_path)
    n_nodes = len(node_idx)

    if step_data is None:
        print("[GCN] No step_data — using synthetic fallback")
        x_all = _make_synthetic_node_data(n_nodes, T=200)
    else:
        x_all = collect_sumo_node_features(node_idx, step_data)  # (T, N, 4)

    T = x_all.size(0)
    model    = SpatialTemporalModel(node_features=4, hidden=64, lstm_hidden=128)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.5)

    # Sliding window dataset: predict queue at t+1 from last seq_len steps
    best_loss = float("inf")
    for epoch in range(epochs):
        epoch_loss = 0.0
        n_batches  = 0

        for t in range(seq_len, T - 1):
            x_seq  = x_all[t - seq_len : t]          # (seq_len, N, 4)
            target = x_all[t + 1, :, 0]              # queue at next step (N,)

            model.train()
            pred = model(x_seq, edge_index)
            loss = criterion(pred, target)
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_loss += loss.item()
            n_batches  += 1

        scheduler.step()
        avg = epoch_loss / max(n_batches, 1)
        if avg < best_loss:
            best_loss = avg
            os.makedirs("models", exist_ok=True)
            torch.save(model.state_dict(), "models/gcn_lstm_best.pt")

        if epoch % 10 == 0 or epoch == epochs - 1:
            print(f"  Epoch {epoch:3d}/{epochs} | Loss: {avg:.4f} | Best: {best_loss:.4f}")

    torch.save(model.state_dict(), "models/gcn_lstm.pt")
    print("Saved: models/gcn_lstm.pt  (best: models/gcn_lstm_best.pt)")
    return model


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    train_gcn_lstm_demo(n_nodes=20, T=50, epochs=30)
