import json
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import ApprovalRequest, Decision, Event
from src.handlers.actions import execute_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/approvals", tags=["approvals"])

@router.get("/")
async def list_approvals(db: Session = Depends(get_db)):
    approvals = db.query(ApprovalRequest).filter(
        ApprovalRequest.status == "pending"
    ).order_by(ApprovalRequest.created_at.desc()).all()
    return approvals

@router.post("/{approval_id}/approve")
async def approve(approval_id: str, db: Session = Depends(get_db)):
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if approval.status != "pending":
        raise HTTPException(status_code=400, detail=f"Approval is already {approval.status}")

    decision = db.query(Decision).filter(Decision.id == approval.decision_id).first()
    event = db.query(Event).filter(Event.id == decision.event_id).first()

    result = execute_action(decision.action, event.id, event.project_id, event.context)

    decision.executed = True
    approval.status = "approved"
    approval.resolved_at = datetime.utcnow()
    db.commit()

    logger.info(json.dumps({
        "event": "approval_resolved",
        "approval_id": approval_id,
        "status": "approved",
        "action": decision.action,
    }))
    return {
        "approval_id": approval_id, 
        "status": "approved", 
        "result": result
    }

@router.post("/{approval_id}/reject")
async def reject(approval_id: str, db: Session = Depends(get_db)):
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if approval.status != "pending":
        raise HTTPException(status_code=400, detail=f"Approval is already {approval.status}")

    approval.status = "rejected"
    approval.resolved_at = datetime.utcnow()
    db.commit()

    logger.info(json.dumps({
        "event": "approval_resolved",
        "approval_id": approval_id,
        "status": "rejected",
    }))
    return {"approval_id": approval_id, "status": "rejected"}