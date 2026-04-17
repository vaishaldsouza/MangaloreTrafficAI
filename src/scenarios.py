"""
src/scenarios.py — Traffic scenario configurations for Mangalore simulation.

Each ScenarioConfig carries:
  • demand_multiplier  — scales vehicle spawn density (applied to routes.xml sampling)
  • speed_factor       — scales road max-speed (simulates weather / road conditions)
  • accident_step      — if set, a random controlled lane is blocked at that step
  • description        — human-readable label shown in the dashboard
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScenarioConfig:
    name: str
    description: str
    icon: str
    demand_multiplier: float   # 1.0 = normal traffic density
    speed_factor: float        # 1.0 = normal road speed
    accident_step: Optional[int] = None   # step to simulate a lane closure

    # Derived helpers
    @property
    def weather_label(self) -> str:
        if self.speed_factor >= 1.0:   return "Clear ☀️"
        if self.speed_factor >= 0.80:  return "Light rain 🌦️"
        if self.speed_factor >= 0.65:  return "Heavy rain 🌧️"
        return "Extreme ⛈️"

    @property
    def demand_label(self) -> str:
        if self.demand_multiplier <= 0.7:  return "Light"
        if self.demand_multiplier <= 1.2:  return "Normal"
        if self.demand_multiplier <= 1.8:  return "Heavy"
        return "Extreme"


# ── Available scenarios ────────────────────────────────────────────────────────

SCENARIOS: dict[str, ScenarioConfig] = {
    "Normal": ScenarioConfig(
        name="Normal",
        description="Standard weekday traffic — baseline comparison scenario.",
        icon="🌤️",
        demand_multiplier=1.0,
        speed_factor=1.0,
    ),
    "Rush Hour AM": ScenarioConfig(
        name="Rush Hour AM",
        description="Morning peak (7–10 AM) — 2× inbound commuter density, "
                    "slight speed reduction from congestion.",
        icon="🌅",
        demand_multiplier=2.0,
        speed_factor=0.85,
    ),
    "Rush Hour PM": ScenarioConfig(
        name="Rush Hour PM",
        description="Evening peak (5–8 PM) — 1.8× outbound traffic, "
                    "higher accident probability.",
        icon="🌆",
        demand_multiplier=1.8,
        speed_factor=0.80,
    ),
    "Weekend": ScenarioConfig(
        name="Weekend",
        description="Sunday traffic — 40% lower density, leisure travel patterns.",
        icon="🏖️",
        demand_multiplier=0.6,
        speed_factor=1.0,
    ),
    "Light Rain": ScenarioConfig(
        name="Light Rain",
        description="Light drizzle — 15% speed reduction, 20% more vehicles "
                    "(commuters avoid walking).",
        icon="🌦️",
        demand_multiplier=1.2,
        speed_factor=0.85,
    ),
    "Heavy Rain": ScenarioConfig(
        name="Heavy Rain",
        description="Monsoon conditions — 30% speed reduction, 40% more vehicles, "
                    "increased rear-end incidents.",
        icon="🌧️",
        demand_multiplier=1.4,
        speed_factor=0.70,
    ),
    "Accident": ScenarioConfig(
        name="Accident",
        description="A lane is closed at step 50 simulating a road accident. "
                    "See how each AI adapts to the sudden congestion spike.",
        icon="🚨",
        demand_multiplier=1.5,
        speed_factor=0.65,
        accident_step=50,
    ),
}


def get_scenario(name: str) -> ScenarioConfig:
    return SCENARIOS.get(name, SCENARIOS["Normal"])
