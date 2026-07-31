"""
simulate_router.py
Exposes /simulate (what-if scenarios via simulator_agent) and /chat
(natural-language Q&A via decision_agent) endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, Supplier, Simulation
from auth import get_current_user
from agents.simulator_agent import simulator_agent
from agents.decision_agent import decision_agent

router = APIRouter(tags=["simulate"])


class SimulateIn(BaseModel):
    supplier_id: int
    scenario: str
    disruption_pct: float = 50.0


class SimulateOut(BaseModel):
    supplier_id: int
    scenario: str
    disruption_pct: float
    projected_impact_score: float
    summary: str


@router.post("/simulate", response_model=SimulateOut)
def run_simulation(payload: SimulateIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == payload.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    result = simulator_agent.run(supplier, payload.scenario, payload.disruption_pct)

    record = Simulation(
        supplier_id=supplier.id,
        scenario=payload.scenario,
        disruption_pct=payload.disruption_pct,
        projected_impact_score=result.projected_impact_score,
        summary=result.summary,
    )
    db.add(record)
    db.commit()

    return SimulateOut(
        supplier_id=supplier.id,
        scenario=payload.scenario,
        disruption_pct=payload.disruption_pct,
        projected_impact_score=result.projected_impact_score,
        summary=result.summary,
    )


class ChatIn(BaseModel):
    question: str


class ChatOut(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    answer = decision_agent.answer_question(db, payload.question)
    return ChatOut(answer=answer)
