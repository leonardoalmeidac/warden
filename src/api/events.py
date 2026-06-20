import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.schemas import EventPayload
from src.db.database import get_db
from src.db.models import Event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["events"])

@router.post("/")
async def ingest_event(payload: EventPayload, db: Session = Depends(get_db)):
    try:
        event = Event(
            project_id=payload.project_id,
            environment_id=payload.environment_id,
            severity=payload.severity,
            signal=payload.signal,
            context=payload.context,
            timestamp=payload.timestamp,
            status='received'
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        logger.info(json.dumps({
            "event": "event_received",
            "event_id": event.id,
            "project_id": event.project_id,
            "severity": event.severity,
        }))

        return {"event_id": event.id, "status": "received"}
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/")
async def list_events(db: Session = Depends(get_db)):
    try:
        events = db.query(Event).order_by(Event.created_at.desc()).all()
        return events
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{event_id}")
async def get_event(event_id: int, db: Session = Depends(get_db)):
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")