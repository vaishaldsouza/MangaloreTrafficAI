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


# ---------------------------------------------------------------------------
# Training demo
# ---------------------------------------------------------------------------

def train_gcn_lstm_demo(n_nodes: int = 20, T: int = 50, epochs: int = 30):
    """
    Minimal training loop for demonstration purposes.
    In production, replace synthetic data with real SUMO junction states.
    """
    model = SpatialTemporalModel(node_features=4, hidden=64, lstm_hidden=128)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()

    # Dummy fully-connected graph for the demo
    src = torch.arange(n_nodes).repeat_interleave(n_nodes)
    dst = torch.arange(n_nodes).repeat(n_nodes)
    edge_index = torch.stack([src, dst])

    print(f"[GCN-LSTM] Training demo ({n_nodes} nodes, {T} timesteps, {epochs} epochs)...")
    for epoch in range(epochs):
        x_seq = _make_synthetic_node_data(n_nodes, T)   # (T, N, 4)
        target = torch.rand(n_nodes)                     # congestion score per node

        model.train()
        pred = model(x_seq, edge_index)
        loss = criterion(pred, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0 or epoch == epochs - 1:
            print(f"  Epoch {epoch:3d}/{epochs} | Loss: {loss.item():.4f}")

    os.makedirs("models", exist_ok=True)
    torch.save(model.state_dict(), "models/gcn_lstm.pt")
    print("Saved: models/gcn_lstm.pt")
    return model


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    train_gcn_lstm_demo(n_nodes=20, T=50, epochs=30)
