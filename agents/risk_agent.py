"""
risk_agent.py
Computes a composite 0-100 risk score for a supplier from its underlying signals.

Weights are tunable. Higher score = higher risk.
"""

from dataclasses import dataclass


@dataclass
class RiskFactors:
    financial_health: float      # 0 (bad) - 100 (great)
    delivery_delay_days: float   # avg days late
    geopolitical_risk: float     # 0-100
    news_sentiment: float        # -1 (very negative) to 1 (very positive)


WEIGHTS = {
    "financial": 0.35,
    "delivery": 0.20,
    "geopolitical": 0.25,
    "sentiment": 0.20,
}


class RiskAgent:
    """Encapsulates the risk-scoring model so it can be swapped for an ML model later."""

    def compute_risk(self, factors: RiskFactors) -> float:
        financial_risk = 100 - factors.financial_health  # invert: low health = high risk
        delivery_risk = min(factors.delivery_delay_days * 8, 100)  # 12.5 days = maxed out
        geo_risk = factors.geopolitical_risk
        sentiment_risk = (1 - factors.news_sentiment) * 50  # -1 -> 100, 1 -> 0

        score = (
            financial_risk * WEIGHTS["financial"]
            + delivery_risk * WEIGHTS["delivery"]
            + geo_risk * WEIGHTS["geopolitical"]
            + sentiment_risk * WEIGHTS["sentiment"]
        )
        return round(max(0.0, min(100.0, score)), 2)

    def severity_for_score(self, score: float) -> str:
        if score >= 80:
            return "critical"
        if score >= 60:
            return "high"
        if score >= 35:
            return "medium"
        return "low"

    def score_supplier(self, supplier) -> float:
        """Accepts a database.Supplier ORM instance, returns risk score."""
        factors = RiskFactors(
            financial_health=supplier.financial_health,
            delivery_delay_days=supplier.delivery_delay_days,
            geopolitical_risk=supplier.geopolitical_risk,
            news_sentiment=supplier.news_sentiment,
        )
        return self.compute_risk(factors)


risk_agent = RiskAgent()
