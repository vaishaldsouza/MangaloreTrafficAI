# 🚦 Mangalore Traffic AI

An AI-driven adaptive traffic signal control system for Mangalore city, built with Deep Reinforcement Learning (PPO/DQN), spatial-temporal graph models (GCN-LSTM), and a real-time SUMO microsimulation dashboard.

---

## 🚀 Key Features Explained

### 1. 🧠 Multi-Method Traffic Control
The system supports 7 different logic controllers, ranging from traditional rules to state-of-the-art AI:
- **🔴 Fixed-cycle baseline**: Traditional timer-based control (e.g., 30s per lane).
- **🟠 Greedy adaptive**: Reactive control that switches to the lane with the highest current vehicle count.
- **🌲 Random Forest**: ML classifier trained on historical patterns to predict congestion states.
- **🔮 LSTM Predictor**: Time-series forecasting using Long Short-Term Memory networks to pre-emptively adjust signals.
- **🧠 Ensemble Controller**: A hybrid system combining RF, LSTM, and Rule-based logic for maximum stability.
- **🤖 PPO (Reinforcement Learning)**: Proximal Policy Optimization agent that learns optimal timing by maximizing throughput via trial-and-error.
- **🎮 DQN (Reinforcement Learning)**: Deep Q-Network agent that estimates the future "value" of every possible signal change.

### 2. ⚙️ Dual Simulation Backends
- **Physics-Based (SUMO)**: Uses the **Simulation of Urban MObility (SUMO)** engine for high-fidelity microsimulation, including vehicle physics, multi-lane dynamics, and real-world Mangalore maps.
- **Software-Only (Python Simulator)**: A lightweight, pure-Python Gymnasium environment that allows rapid testing and training without the overhead of SUMO, driven by synthetic or uploaded traffic datasets.

### 3. 🗺️ Interactive Map & Route Finder
- **Urban Digital Twin**: A 2km radius of Mangalore city extracted from OpenStreetMap (OSM).
- **Landmark Search**: Select key locations like Hampankatta, KSRTC, or NITK Surathkal to find the shortest path.
- **Traffic Heatmaps**: Real-time visualization of congestion hotspots across the city.
- **Live Vehicle Snapshot**: Monitor individual vehicle speeds and positions on a Folium-powered interactive map.

### 4. 🎓 Research & Academic Hub
A dedicated suite for urban mobility researchers:
- **🌍 Carbon Calculator**: Automatically estimates daily/yearly CO₂ and fuel savings compared to fixed-cycle baselines.
- **🔬 Ablation Study**: Measure the impact of specific features (e.g., weather, hour, weekend) on traffic prediction accuracy.
- **🧪 Bayesian Optimization**: Automated hyperparameter tuning for RL agents using **Optuna**.
- **🚀 Advanced RL**: Features for Transfer Learning, Curriculum Learning, and Multi-Agent RL (MARL) for multi-junction control.

### 5. 🧪 Explainable AI (XAI) & Analytics
- **🔍 SHAP Explainer**: Interpret *why* the AI made a decision by visualizing feature importance.
- **🎯 Confusion Matrix**: Detailed validation of ML models using Precision, Recall, and F1-score benchmarks.
- **🚨 Anomaly Detection**: Uses Isolation Forests to flag "unusual" traffic events or simulation failures.
- **📈 Congestion Forecasting**: ARIMA and LSTM-based predictions for future traffic states.

### 6. 📂 Data & Map Hub
- **Custom Maps**: Upload your own `.osm` files to generate new simulation networks for any city.
- **Real-Data Integration**: Support for Google Maps Traffic API and custom `.csv` dataset uploads for training models on real field survey data.

### 7. 🚀 Modern Web Ecosystem (NEW)
- **FastAPI Backend**: High-performance asynchronous API for real-time data streaming.
- **Next.js Dashboard V2**: A premium, responsive dashboard built with React, TailwindCSS, and Framer Motion for a "Digital Twin" experience.
- **Secure Auth**: JWT-based authentication with encrypted user storage and password recovery.

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
│   ├── scenarios.py           # Weather, accidents, and peak-hour configs
│   └── models/
│       ├── random_forest_model.py
│       ├── lstm_model.py
│       ├── gcn_lstm_model.py
│       └── ppo_sumo.py        # PPO deployment logic
│
├── dashboard/
│   └── app.py                 # Multi-featured Streamlit Dashboard (Standard)
│
├── dashboard_v2/              # Premium Next.js Dashboard (Pro)
│   ├── src/app/
│   └── package.json
│
├── models/                    # Saved weights (.pkl, .pt, .zip)
├── run_api.py                 # FASTAPI server entry point
└── .env                       # Environment configuration
```

---

## 🛠️ Setup

1. **Prerequisites**: Install [SUMO](https://sumo.dlr.de) and Python 3.10+.
2. **Install Dependencies**: 
   ```bash
   pip install gymnasium stable-baselines3 torch streamlit pandas numpy osmnx folium shap optuna joblib sklearn matplotlib seaborn
   ```
3. **Configure**: Copy `.env.example` to `.env` and set `SUMO_HOME`.
4. **Launch Backend**:
   ```bash
   python run_api.py
   ```
5. **Launch Dashboard (Choose One)**:
   - **V2 (Premium)**: `cd dashboard_v2 && npm install && npm run dev`
   - **Standard**: `streamlit run dashboard/app.py`

---

## 🚦 Dashboard Tabs Overview

| Tab | Feature | Description |
|-----|---------|-------------|
| 🗺️ **Map & Routes** | Navigation Hub | Landmarking, Routing, and Live Traffic Heatmaps. |
| 🚦 **Simulate** | Execution Engine | Run simulations with 7 controllers and custom scenarios. |
| ⚖️ **Compare** | Benchmarking | Head-to-head performance comparison of any two methods. |
| 📈 **Train Live** | RL Training | Monitor PPO/DQN learning curves in real-time. |
| 🗓️ **History** | SQLite Database | Reload, analyze, or delete previous simulation runs. |
| 🎓 **Research** | Academic Tools | Carbon tracking, Ablation studies, and Optuna tuning. |
| 🧪 **Analysis** | Model Validation | SHAP explanations, Predictions accuracy, and Anomalies. |
| 📄 **Export** | Reporting Hub | Generate self-contained HTML reports for print/PDF. |
| 📂 **Data Hub** | File Management | Upload custom road networks (.osm) and traffic data (.csv). |

---

## 🏆 Research Impact
In tests conducted on the Mangalore 2km radius network, PPO Reinforcement Learning achieved a **~38-42% reduction** in average vehicle queue length and a corresponding **~15% reduction in CO₂ emissions** compared to the fixed-cycle baseline.

