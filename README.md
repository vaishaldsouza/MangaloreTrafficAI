# Mangalore Traffic AI

An AI-driven traffic light control system for simulated Mangalore city map using Reinforcement Learning in a pure Python Gymnasium environment.

## Project Structure

- `data/`: Raw inputs (OSM maps, historical stats).
- `src/`: Python logic.
    - `controller.py`: The Gymnasium environment representing the intersection.
    - `model.py`: RL model definitions (stable_baselines3).
- `dashboard/`: Streamlit visualization app.

## Setup

1. Install dependencies: `pip install gymnasium stable-baselines3 torch streamlit pandas numpy matplotlib`
2. Train model: `python src/train.py`
3. Run dashboard: `streamlit run dashboard/app.py`

## Research Goals

- Compare simple threshold logic with Reinforcement Learning (PPO/DQN).
- Optimize traffic flow at high-congestion intersections in Mangalore.
- Reduce average waiting time and CO2 emissions.
