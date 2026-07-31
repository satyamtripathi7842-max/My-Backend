"""
supplier_agent.py
Owns supplier CRUD operations and keeps risk_score in sync via risk_agent.
Exposes a FastAPI router mounted at /suppliers.
"""

import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, Supplier
from auth import get_current_user
from agents.risk_agent import risk_agent
from agents.news_agent import news_agent
from agents.decision_agent import decision_agent

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


class SupplierIn(BaseModel):
    name: str
    country: str
    category: str = "general"
    lat: float = 0.0
    lng: float = 0.0
    financial_health: float = 70.0
    delivery_delay_days: float = 0.0
    geopolitical_risk: float = 20.0


class SupplierOut(SupplierIn):
    id: int
    news_sentiment: float
    risk_score: float
    last_updated: datetime.datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[SupplierOut])
def list_suppliers(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Supplier).all()


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.post("", response_model=SupplierOut)
def create_supplier(payload: SupplierIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    supplier = Supplier(**payload.dict())
    supplier.news_sentiment = news_agent.fetch_sentiment(supplier.name)
    supplier.risk_score = risk_agent.score_supplier(supplier)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    # decision agent evaluates whether the new supplier already warrants an alert
    decision_agent.evaluate_and_alert(db, supplier)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, payload: SupplierIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for key, value in payload.dict().items():
        setattr(supplier, key, value)
    supplier.news_sentiment = news_agent.fetch_sentiment(supplier.name)
    supplier.risk_score = risk_agent.score_supplier(supplier)
    supplier.last_updated = datetime.datetime.utcnow()
    db.commit()
    db.refresh(supplier)

    decision_agent.evaluate_and_alert(db, supplier)
    return supplier


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(supplier)
    db.commit()
    return {"detail": "deleted"}


@router.post("/{supplier_id}/refresh", response_model=SupplierOut)
def refresh_supplier_risk(supplier_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Re-pulls news sentiment and recomputes risk score for one supplier."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier.news_sentiment = news_agent.fetch_sentiment(supplier.name)
    supplier.risk_score = risk_agent.score_supplier(supplier)
    supplier.last_updated = datetime.datetime.utcnow()
    db.commit()
    db.refresh(supplier)

    decision_agent.evaluate_and_alert(db, supplier)
    return supplier
