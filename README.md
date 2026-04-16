# Mangalore Traffic AI

An AI-driven adaptive traffic signal control system for Mangalore city, built with Reinforcement Learning, classical ML baselines, and a real-time SUMO microsimulation dashboard.

---

## Project Overview

Traditional traffic lights in Mangalore use fixed timing cycles that ignore real vehicle queues. This project compares **5 control methods** — from naive rule-based to state-of-the-art PPO reinforcement learning — against a real physics simulation of Mangalore's road network.

**Expected result:** PPO achieves ~38% reduction in average vehicle queue length vs the fixed-cycle baseline.

---

## Project Structure

```
MangaloreTrafficAI/
├── simulation/
│   ├── generate_network.py     # Download OSM map → SUMO network
│   └── config.sumocfg          # SUMO simulation configuration
│
├── src/
│   ├── controller.py           # Gymnasium environment wrapping SUMO via TraCI
│   ├── model.py                # SB3 PPO/DQN wrapper (TrafficRLModel)
│   ├── train.py                # Quick PPO training entry point
│   ├── baselines/
│   │   └── fixed_cycle.py      # Method 1: Fixed-cycle baseline
│   └── models/
│       ├── random_forest_model.py  # Method 2: Random Forest classifier
│       ├── lstm_model.py           # Method 3: LSTM traffic predictor
│       ├── gcn_lstm_model.py       # Method 4: GCN + LSTM spatial-temporal
│       └── ppo_sumo.py             # Method 5: PPO + compare_all_methods()
│
├── dashboard/
│   └── app.py                  # Streamlit dashboard (3-tab UI)
│
├── models/                     # Saved model files (git-ignored)
├── .env.example                # Environment variable template
└── README.md
```

---

## Setup

### 1. Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10 – 3.13 | [python.org](https://python.org) |
| SUMO | ≥ 1.18 | [sumo.dlr.de](https://sumo.dlr.de) |
| Git | any | [git-scm.com](https://git-scm.com) |

### 2. Clone and install dependencies

```bash
git clone https://github.com/YourUsername/MangaloreTrafficAI.git
cd MangaloreTrafficAI

py -m pip install gymnasium stable-baselines3 torch streamlit \
    pandas numpy matplotlib scikit-learn joblib \
    osmnx folium streamlit-folium
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set SUMO_HOME to your SUMO installation path
```

### 4. Generate the Mangalore road network

```bash
py simulation/generate_network.py
```

This downloads the Mangalore OSM map, converts it to SUMO format, and generates vehicle routes.

---

## Running the Methods

```bash
# Method 2 — Random Forest  (~5 s)
py -m src.models.random_forest_model

# Method 3 — LSTM            (~30 s)
py -m src.models.lstm_model

# Method 5 — PPO training    (~30–60 min, produces the best model)
py src/train.py

# Compare all methods → Results Table
py -c "
import sys; sys.path.insert(0,'src')
from models.ppo_sumo import compare_all_methods
compare_all_methods()
"
```

---

## Launch the Dashboard

```bash
py -m streamlit run dashboard/app.py
```

Open **http://localhost:8501** in your browser.

### Dashboard Tabs

| Tab | Features |
|-----|---------|
| 🗺️ Map & Route Finder | Interactive Mangalore map, 18 landmark locations, shortest-path route finder, traffic heatmap overlay |
| 🚦 Run Simulation | Choose any of 5 controllers, live vehicle positions on map, real-time metrics |
| 📊 Results & Analysis | Frame-by-frame vehicle replay, reward/queue charts, lane heatmap, CSV export |

---

## The 5 Control Methods

| # | Method | Type | Description |
|---|--------|------|-------------|
| 1 | **Fixed-cycle baseline** | Rule | Rotates phases every 30 s (traditional signal) |
| 2 | **Greedy adaptive** | Rule | Always greens the most congested lane |
| 3 | **Random Forest** | ML | Classifies congestion and maps to a phase |
| 4 | **LSTM predictor** | Deep ML | Uses 12-step history to forecast demand |
| 5 | **PPO (RL)** | RL | Neural network trained end-to-end in SUMO |

---

## Research Goals

- Quantify the inefficiency of fixed-cycle signals using SUMO microsimulation.
- Demonstrate that ML and RL controllers reduce waiting time.
- Provide an interactive educational dashboard for comparing methods.
- Target: **≥ 38% reduction** in average queue length vs fixed-cycle.
