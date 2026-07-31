"""
simulator_agent.py
Runs lightweight "what-if" disruption simulations for a supplier
(e.g. port closure, factory outage) and estimates downstream impact.
"""

import random
from dataclasses import dataclass


@dataclass
class SimulationResult:
    projected_impact_score: float  # 0-100
    summary: str


SCENARIOS = {
    "port_closure": {"base_impact": 55, "volatility": 15},
    "factory_outage": {"base_impact": 70, "volatility": 20},
    "geopolitical_sanction": {"base_impact": 65, "volatility": 25},
    "raw_material_shortage": {"base_impact": 45, "volatility": 15},
    "labor_strike": {"base_impact": 40, "volatility": 15},
}


class SimulatorAgent:
    def run(self, supplier, scenario: str, disruption_pct: float) -> SimulationResult:
        """
        supplier: database.Supplier ORM instance
        scenario: one of SCENARIOS keys
        disruption_pct: 0-100, how severe the modeled disruption is
        """
        config = SCENARIOS.get(scenario, {"base_impact": 50, "volatility": 15})

        # baseline risk contributes, scenario severity scales it, plus some jitter
        baseline = supplier.risk_score * 0.4
        scenario_component = config["base_impact"] * (disruption_pct / 100)
        jitter = random.uniform(-config["volatility"], config["volatility"]) * 0.3

        impact = baseline + scenario_component + jitter
        impact = round(max(0.0, min(100.0, impact)), 2)

        if impact >= 80:
            outlook = "severe disruption to fulfillment expected; activate contingency sourcing"
        elif impact >= 55:
            outlook = "significant delays likely; consider buffer stock and alternate routes"
        elif impact >= 30:
            outlook = "moderate impact; monitor closely over the simulated window"
        else:
            outlook = "minimal projected impact under this scenario"

        summary = (
            f"Simulated '{scenario}' at {disruption_pct}% severity for {supplier.name}: "
            f"projected impact {impact}/100 — {outlook}."
        )
        return SimulationResult(projected_impact_score=impact, summary=summary)


simulator_agent = SimulatorAgent()
