"""
decision_agent.py
Turns a supplier's risk score into actionable alerts + recommendations,
and answers free-text questions for the AI Chat panel (rule-based; swap
in an LLM call here if desired).
"""

from sqlalchemy.orm import Session

from database import Supplier, Alert
from agents.risk_agent import risk_agent

ALERT_THRESHOLD = 60.0  # risk_score at/above this raises an alert

RECOMMENDATIONS = {
    "critical": "Immediately activate contingency supplier and flag procurement for review.",
    "high": "Increase monitoring cadence and request updated delivery commitments from supplier.",
    "medium": "Add supplier to watchlist; review again within 2 weeks.",
    "low": "No action needed; continue routine monitoring.",
}


class DecisionAgent:
    def evaluate_and_alert(self, db: Session, supplier: Supplier) -> Alert | None:
        severity = risk_agent.severity_for_score(supplier.risk_score)
        if supplier.risk_score < ALERT_THRESHOLD:
            return None

        message = (
            f"{supplier.name} ({supplier.country}) risk score is {supplier.risk_score}/100 "
            f"— severity: {severity}."
        )
        alert = Alert(
            supplier_id=supplier.id,
            severity=severity,
            message=message,
            recommendation=RECOMMENDATIONS[severity],
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return alert

    def answer_question(self, db: Session, question: str) -> str:
        """Very lightweight rule-based Q&A over current supplier/alert state.
        Replace with a call to an LLM (with retrieved context) for richer answers."""
        q = question.lower()

        if "highest risk" in q or "riskiest" in q:
            supplier = db.query(Supplier).order_by(Supplier.risk_score.desc()).first()
            if not supplier:
                return "No suppliers on record yet."
            return f"{supplier.name} currently has the highest risk score at {supplier.risk_score}/100."

        if "how many alerts" in q or "alert count" in q:
            count = db.query(Alert).filter(Alert.acknowledged == False).count()  # noqa: E712
            return f"There are {count} unacknowledged alerts."

        if "critical" in q:
            suppliers = db.query(Supplier).filter(Supplier.risk_score >= 80).all()
            if not suppliers:
                return "No suppliers are currently at critical risk."
            names = ", ".join(s.name for s in suppliers)
            return f"Suppliers at critical risk: {names}."

        return (
            "I can answer questions about supplier risk, alert counts, and critical "
            "suppliers. Try asking: 'which supplier is highest risk?'"
        )


decision_agent = DecisionAgent()
