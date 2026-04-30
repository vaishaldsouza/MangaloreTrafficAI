import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
import xml.etree.ElementTree as ET

class TrafficGNN(nn.Module):
    """Node = junction. Edge = road connecting two junctions."""
    def __init__(self, node_features: int, n_actions: int, hidden: int = 64):
        super().__init__()
        self.conv1 = GCNConv(node_features, hidden)
        self.conv2 = GCNConv(hidden, hidden)
        self.head  = nn.Linear(hidden, n_actions)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = F.relu(self.conv2(x, edge_index))
        return self.head(x)   # logits per junction node

def build_edge_index_from_net(net_xml_path: str):
    """
    Parses SUMO .net.xml to find all connections between junctions.
    Returns torch.tensor of shape [2, E] (undirected).
    """
    tree = ET.parse(net_xml_path)
    root = tree.getroot()
    
    # 1. Identify all junctions (nodes)
    junction_ids = [node.attrib["id"] for node in root.findall("junction") if node.attrib.get("type") != "internal"]
    j_to_idx = {jid: i for i, jid in enumerate(junction_ids)}
    
    edges = []
    # 2. Iterate over edges to find from/to junction connections
    for edge in root.findall("edge"):
        from_j = edge.attrib.get("from")
        to_j = edge.attrib.get("to")
        
        if from_j in j_to_idx and to_j in j_to_idx:
            u, v = j_to_idx[from_j], j_to_idx[to_j]
            edges.append((u, v))
            edges.append((v, u)) # undirected
            
    # Remove duplicates
    edges = list(set(edges))
    
    if not edges:
        return torch.zeros((2, 0), dtype=torch.long)
        
    return torch.tensor(edges, dtype=torch.long).t().contiguous()

def train_gnn(epochs: int = 20, net_path: str = "simulation/mangalore.net.xml"):
    """
    Trains a GNN to predict optimal phases across all junctions.
    Uses synthetic 'traffic pressure' labels for this demo.
    """
    edge_index = build_edge_index_from_net(net_path)
    # Re-parse to get junction count
    tree = ET.parse(net_path)
    root = tree.getroot()
    junction_ids = [node.attrib["id"] for node in root.findall("junction") if node.attrib.get("type") != "internal"]
    n_nodes = len(junction_ids)
    
    model = TrafficGNN(node_features=8, n_actions=4)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    print(f"Training GNN on {n_nodes} nodes for {epochs} epochs...")
    
    for epoch in range(epochs):
        # Synthetic data: node features (normalized queue, wait, etc)
        x = torch.randn(n_nodes, 8)
        # Target: random 'optimal' phase index [0, 3]
        target = torch.randint(0, 4, (n_nodes,))
        
        optimizer.zero_grad()
        out = model(x, edge_index)
        loss = F.cross_entropy(out, target)
        loss.backward()
        optimizer.step()
        
        if epoch % 5 == 0:
            print(f"  Epoch {epoch:3d} | Loss: {loss.item():.4f}")
            
    import os
    os.makedirs("models", exist_ok=True)
    torch.save(model, "models/gnn_policy.pt")
    print("Model saved to models/gnn_policy.pt")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--epochs", type=int, default=20)
    args = parser.parse_args()
    
    if args.train:
        train_gnn(epochs=args.epochs)
