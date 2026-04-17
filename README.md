# Mangalore Traffic AI

An AI-driven adaptive traffic signal control system for Mangalore city, built with Deep Reinforcement Learning (PPO/DQN), spatial-temporal graph models (GCN-LSTM), and a real-time SUMO microsimulation dashboard.

---

## 🚀 Key Features

- **Multi-Method Control**: Supports 7 methods including Fixed-cycle, Greedy Adaptive, Random Forest, LSTM, and State-of-the-Art RL (PPO & DQN).
- **Urban Digital Twin**: Real physics simulation using a 2km radius of Mangalore city extracted from OpenStreetMap.
- **Advanced RL Training**: Live training cockpit with real-time reward curve tracking.
- **Research Hub**: Integrated carbon footprint calculator, automated ablation studies, and Bayesian hyperparameter tuning (Optuna).
- **Explainable AI (XAI)**: SHAP-based feature importance tools to interpret AI decisions.
- **Data Hub**: Upload custom road networks (.osm) and traffic datasets (.csv) to generalize the simulation.

---

## 📂 Project Structure

```
MangaloreTrafficAI/
├── simulation/
│   ├── generate_network.py    # Download OSM map → SUMO network converter
│   ├── config.sumocfg         # SUMO simulation configuration
│   └── routes.xml             # Current traffic routes
│
├── src/
│   ├── controller.py          # Gymnasium environment wrapping SUMO
│   ├── train.py               # PPO/DQN training entry point
│   ├── analysis.py            # SHAP and Confusion Matrix reporting
│   ├── scenarios.py           # Weather, accidents, and peak-hour configurations
│   ├── database.py            # SQLite history management
│   └── models/
│       ├── random_forest_model.py
│       ├── lstm_model.py
│       ├── gcn_lstm_model.py
│       └── ppo_sumo.py        # PPO deployment logic
│
├── dashboard/
│   └── app.py                 # Multi-featured Streamlit Dashboard
│
├── models/                    # Saved weights (.pkl, .pt, .zip)
└── .env                       # Environment configuration
```

---

## 🛠️ Setup

1. **Prerequisites**: Install [SUMO](https://sumo.dlr.de) and Python 3.10+.
2. **Install Deps**: `pip install gymnasium stable-baselines3 torch streamlit pandas numpy osmnx folium shap optuna`
3. **Configure**: Copy `.env.example` to `.env` and set `SUMO_HOME`.
4. **Generate Network**: `python simulation/generate_network.py`

---

## 🚦 Dashboard Tabs

| Tab | Feature |
|-----|---------|
| 🗺️ **Map & Routes** | Interactive map, landmark selection, and shortest-path routing. |
| 🚦 **Simulate** | Run live simulations with 7 different controllers & scenarios. |
| ⚖️ **Compare** | Head-to-head comparison of two methods with improvement delta. |
| 📈 **Train Live** | Real-time monitoring of PPO/DQN training iterations. |
| 🎓 **Research Hub** | Carbon saving metrics, ablation studies, and Optuna optimization. |
| 🧪 **Analysis** | SHAP explanations, anomaly detection, and congestion forecasting. |
| 📂 **Data Hub** | Upload custom .osm maps and traffic .csv datasets. |

---

## 📈 Research Result
PPO Reinforcement Learning consistently achieves **~38-42% reduction** in average vehicle queue length compared to the fixed-cycle baseline in peak Mangalore traffic.
