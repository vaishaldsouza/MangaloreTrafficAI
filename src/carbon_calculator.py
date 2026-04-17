"""
src/carbon_calculator.py — CO₂ & fuel savings estimator.

Based on Indian urban traffic emission assumptions:
  • Idle fuel consumption  : ~0.6 L/hour per vehicle
  • Petrol CO₂ factor      : 2.31 kg CO₂ / litre
  • Signalised junctions in Mangalore : ~47

The simulation gives us vehicle-steps of waiting. We convert that to
real-world fuel savings across the full Mangalore junction network.
"""

# ── Physical constants ─────────────────────────────────────────────────────────
IDLE_FUEL_LITRE_PER_HOUR  = 0.60      # litres/hour per idling vehicle (Indian urban avg)
CO2_KG_PER_LITRE_PETROL   = 2.31      # kg CO₂ emitted per litre of petrol burned
MANGALORE_SIGNALISED_JNS  = 47        # approximate number of signalised intersections
DAILY_PEAK_HOURS           = 4        # hours/day the signal is in "peak" mode
WORKING_DAYS_PER_YEAR      = 313      # (365 - 52 Sundays)

# ── Derived ────────────────────────────────────────────────────────────────────
IDLE_FUEL_PER_VEHICLE_SEC  = IDLE_FUEL_LITRE_PER_HOUR / 3600   # L / (vehicle · second)


def estimate_savings(
    baseline_avg_queue: float,
    method_avg_queue: float,
    sim_steps: int,
    step_duration_sec: float = 5.0,
) -> dict:
    """
    Estimate fuel and CO₂ savings of a method vs the fixed-cycle baseline.

    Args:
        baseline_avg_queue  : avg vehicles waiting / step for fixed-cycle
        method_avg_queue    : avg vehicles waiting / step for the chosen method
        sim_steps           : total simulation steps in the episode
        step_duration_sec   : seconds of real time per simulation step (default 5 s)

    Returns:
        dict with keys:
            queue_reduction_pct     (%)
            vehicle_wait_sec_saved  (per episode, for one junction)
            fuel_litres_saved_ep    (per episode)
            co2_kg_saved_ep         (per episode)
            co2_kg_saved_daily      (across all 47 Mangalore junctions, peak hours)
            co2_tonnes_saved_yearly (annual projection)
            trees_equivalent        (1 tree absorbs ~21 kg CO₂/year)
    """
    if baseline_avg_queue <= 0:
        return _zero_dict()

    queue_reduction_pct = (baseline_avg_queue - method_avg_queue) / baseline_avg_queue * 100

    # vehicle-seconds of waiting saved in this episode (1 junction)
    vehicle_wait_sec_saved = (
        (baseline_avg_queue - method_avg_queue) * sim_steps * step_duration_sec
    )
    vehicle_wait_sec_saved = max(0.0, vehicle_wait_sec_saved)

    fuel_litres_saved_ep = vehicle_wait_sec_saved * IDLE_FUEL_PER_VEHICLE_SEC
    co2_kg_saved_ep      = fuel_litres_saved_ep * CO2_KG_PER_LITRE_PETROL

    # Scale to all Mangalore junctions × daily peak hours
    ep_duration_hours = (sim_steps * step_duration_sec) / 3600
    if ep_duration_hours > 0:
        scale_factor = (MANGALORE_SIGNALISED_JNS * DAILY_PEAK_HOURS) / ep_duration_hours
    else:
        scale_factor = 0.0

    co2_kg_saved_daily  = co2_kg_saved_ep * scale_factor
    co2_tonnes_yearly   = co2_kg_saved_daily * WORKING_DAYS_PER_YEAR / 1000
    trees_equivalent    = co2_tonnes_yearly * 1000 / 21   # 21 kg CO₂/tree/year

    return {
        "queue_reduction_pct":      round(queue_reduction_pct, 1),
        "vehicle_wait_sec_saved":   round(vehicle_wait_sec_saved, 0),
        "fuel_litres_saved_ep":     round(fuel_litres_saved_ep, 3),
        "co2_kg_saved_ep":          round(co2_kg_saved_ep, 3),
        "co2_kg_saved_daily":       round(co2_kg_saved_daily, 1),
        "co2_tonnes_saved_yearly":  round(co2_tonnes_yearly, 2),
        "trees_equivalent":         round(trees_equivalent, 0),
    }


def _zero_dict():
    return {k: 0 for k in [
        "queue_reduction_pct","vehicle_wait_sec_saved","fuel_litres_saved_ep",
        "co2_kg_saved_ep","co2_kg_saved_daily","co2_tonnes_saved_yearly","trees_equivalent"
    ]}


def format_impact_summary(savings: dict) -> str:
    """Return a human-readable impact summary string."""
    if savings["queue_reduction_pct"] <= 0:
        return "This method performs similarly to or worse than the fixed-cycle baseline."
    return (
        f"Queue reduced by **{savings['queue_reduction_pct']:.1f}%**. "
        f"Across all {MANGALORE_SIGNALISED_JNS} Mangalore junctions, this saves "
        f"approximately **{savings['co2_kg_saved_daily']:.0f} kg of CO₂ per day** "
        f"and **{savings['co2_tonnes_saved_yearly']:.1f} tonnes per year** — "
        f"equivalent to planting **{savings['trees_equivalent']:.0f} trees**."
    )


# ── Quick smoke-test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    s = estimate_savings(
        baseline_avg_queue=15.0,
        method_avg_queue=9.3,    # ~38% improvement
        sim_steps=360,
    )
    for k, v in s.items():
        print(f"  {k:<30} {v}")
    print(format_impact_summary(s))
