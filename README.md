# 🚦 Mangalore Traffic AI (v2.1)

An AI-driven adaptive traffic signal control system for Mangalore city, built with Deep Reinforcement Learning (PPO/DQN), spatial-temporal graph models (GNN), and a real-time SUMO microsimulation dashboard.

---

## 🚀 Key Features

### 1. 🧠 Advanced AI Controllers
- **🤖 Reinforcement Learning**: PPO and DQN agents trained to minimize queue lengths and waiting times.
- **📷 Computer Vision Integration**: Real-time vehicle counting using a simulated top-down camera pipeline (CVPipeline).
- **🚨 Emergency Preemption**: Automatic "Green Wave" generation for emergency vehicles detected in the network.
- **🔮 Predictive Logic**: LSTM and GNN-based forecasting to anticipate congestion before it happens.
- **🚦 Multi-Agent RL (MARL)**: Cooperative control across multiple junctions using a Joint-Action PPO approach.

### 2. ⚙️ Simulation & Digital Twin
- **Physics-Based (SUMO)**: High-fidelity microsimulation using the Eclipse SUMO engine.
- **Mangalore City Map**: A 2km radius digital twin of Mangalore city (Hampankatta, KSRTC, etc.) extracted from OSM.
- **Adaptive Pedestrian Phases**: Programmatic injection of all-red pedestrian clearance intervals.

### 3. 📊 Analytics & Research Hub
- **📈 Real-Time Dashboards**: Two dashboard options:
  - **V2 (Premium)**: Next.js + TailwindCSS + WebSockets for a low-latency "Control Center" experience.
  - **Standard**: Streamlit-based hub for deep data analysis and A/B testing.
- **⚖️ LoS Grading**: Automatic Level of Service (LoS A-F) grading based on HCM (Highway Capacity Manual) standards.
- **🌿 Environmental Impact**: Real-time tracking of CO₂ emissions and fuel consumption.
- **🔬 Explainable AI (XAI)**: SHAP-based feature importance visualization.
- **📁 Dataset Import**: Direct CSV/JSON traffic pattern injection to simulate specific real-world scenarios.
- **🧪 Comparative Benchmarking**: Automatic indexing and report generation for historical simulation runs.


---

## 📂 Project Structure

```
MangaloreTrafficAI/
├── src/
│   ├── controller.py          # Gym environment with CV & Preemption logic
│   ├── multi_agent_rl.py      # Joint PPO training for multiple junctions
│   ├── cv/                    # Computer Vision pipeline & virtual camera
│   └── models/                # PPO, DQN, LSTM, and GNN architectures
├── dashboard_v2/              # Premium Next.js + WebSocket Frontend
├── simulation/                # SUMO network, config, and route files
├── run_api.py                 # FastAPI backend entry point
└── requirements.txt           # Python dependencies
```

---

## 🛠️ Setup & Installation

1. **Install SUMO**: Download and install [Eclipse SUMO](https://sumo.dlr.de/docs/Installing/index.html).
2. **Environment**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure**:
   ```bash
   copy .env.example .env
   # Set SUMO_HOME to your installation path (e.g., D:/SUMO)
   ```
4. **Launch**:
   - **Backend**: `python run_api.py`
   - **Frontend**: `cd dashboard_v2 && npm install && npm run dev`

---

## 🏆 Research Impact
In Mangalore city simulations, the **Joint-Action PPO** controller achieved a **~42% reduction** in peak-hour queue lengths and a **~18% decrease** in localized CO₂ emissions compared to standard fixed-cycle timings.

---

## 📄 License
Research-grade implementation for academic and urban planning purposes.
Created by [Vaishal Dsouza](https://github.com/vaishaldsouza).
