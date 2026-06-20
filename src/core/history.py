import os
from sqlalchemy.orm import Session
from src.db.models import Event, Decision, ApprovalRequest

def get_workload_history(project_id: str, current_event_id: str, db: Session) -> list:
    limit = int(os.getenv("HISTORY_LIMIT", 5))
    events = (
        db.query(Event)
        .filter(Event.project_id == project_id, Event.id != current_event_id)
        .order_by(Event.created_at.desc())
        .limit(limit)
        .all()
    )

    history = []
    for event in events:
        decision = db.query(Decision).filter(Decision.event_id == event.id).first()
        if not decision:
            continue
        
        approval = db.query(ApprovalRequest).filter(
            ApprovalRequest.decision_id == decision.id
        ).first()
        
        history.append({
            "signal": event.signal,
            "action": decision.action,
            "executed": decision.executed,
            "feedback": approval.status if approval else None
        })
    return history