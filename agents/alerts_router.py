"""
alerts_router.py
Exposes /alerts endpoints — list, acknowledge, and (optionally) notify via
email/telegram. Kept alongside the agents since alerts are agent output.
"""

import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, Alert
from auth import get_current_user
from notification.email import send_alert_email
from notification.telegram import send_telegram_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertOut(BaseModel):
    id: int
    supplier_id: int
    severity: str
    message: str
    recommendation: str
    acknowledged: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[AlertOut])
def list_alerts(
    unacknowledged_only: bool = False,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(Alert)
    if unacknowledged_only:
        query = query.filter(Alert.acknowledged == False)  # noqa: E712
    return query.order_by(Alert.created_at.desc()).all()


@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/{alert_id}/notify")
def notify_alert(
    alert_id: int,
    email_to: Optional[str] = None,
    use_telegram: bool = False,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    results = {}
    if email_to:
        results["email"] = send_alert_email(
            email_to, f"SentinelX-AI Alert [{alert.severity.upper()}]", alert.message
        )
    if use_telegram:
        results["telegram"] = send_telegram_alert(f"[{alert.severity.upper()}] {alert.message}")

    return {"alert_id": alert_id, "results": results}
