import json
import logging
import os
from groq import Groq
from src.db.models import Decision, Event
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
VALID_ACTIONS = {"rollback", "restart", "scale_up", "notify_human", "no_action"}
SYSTEM_PROMPT = """You are Warden, an autonomous remediation agent for an Internal Developer Platform.
You receive degradation signals from services and must decide the best remediation action.

You must respond ONLY with a valid JSON object with this exact structure:
{
    "action": "<rollback|restart|scale_up|notify_human|no_action>",
    "confidence": <float between 0.0 and 1.0>,
    "reasoning": "<explanation of your decision>"
    "safe_to_auto": <true|false>
}

Guidelines:
- rollback: use when a recent deploy caused the issue
- restart: use when the service is unresponsive or crashing
- scale_up: use when the issue is caused by high load
- notify_human: use when the situation is unclear or too risky
- no_action: use when the signal is informational only

Always respond in Spanish.
"""

def build_prompt(event: Event, history: list = []) -> str:
    prompt = f"""
Degradation event received: 
- Project: {event.project_id}
- Environment: {event.environment_id}
- Severity: {event.severity}
- Signal: {event.signal}
- Context: {json.dumps(event.context)}
- Timestamp: {event.timestamp}
    """

    if history:
        prompt += "\nRecent history of related events and actions:\n"
        for h in history:
            prompt += f"- Signal: {h['signal']} | Action: {h['action']} | Auto executed: {h['executed']} | Feedback: {h.get('feedback', 'none')}\n"
    return prompt

def apply_restrictions(event: Event, decision: dict) -> dict:
    reasons = []

    if event.severity == "critical":
        decision["safe_to_auto"] = False
        reasons.append("Critical severity requires human review.")

    if decision["confidence"] < 0.7:
        decision["safe_to_auto"] = False
        reasons.append("Confidence below 0.7")

    if event.environment_id == "prod" and decision["action"] in {"rollback", "scale_up"}:
        decision["safe_to_auto"] = False
        reasons.append("Production environment requires human review for disruptive actions.")
    
    if reasons:
        logger.info(json.dumps({
            "event": "restriction_applied",
            "reasons": reasons,
            "safe_to_auto": False
        }))
    
    return decision

def reason(event: Event, db: Session, history: list = []) -> Decision:
    prompt = build_prompt(event, history)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        raw = response.choices[0].message.content
        logger.info(json.dumps({
            "event": "llm_response",
            "raw": raw
        }))

        decision_data = json.loads(raw)

        if decision_data["action"] not in VALID_ACTIONS:
            decision_data["action"] = "notify_human"
        
        decision_data = apply_restrictions(event, decision_data)

        decision = Decision(
            event_id=event.id,
            action=decision_data["action"],
            confidence=decision_data["confidence"],
            reasoning=decision_data["reasoning"],
            safe_to_auto=decision_data["safe_to_auto"]
        )

        db.add(decision)
        db.commit()
        db.refresh(decision)

        logger.info(json.dumps({
            "event": "decision_created",
            "event_id": event.id,
            "action": decision.action,
            "confidence": decision.confidence,
            "safe_to_auto": decision.safe_to_auto,
        }))

        return decision
    
    except Exception as e:
        logger.error(f"Error during reasoning: {e}")
        return Decision(
            event_id=event.id,
            action="notify_human",
            confidence=1.0,
            reasoning="Error during reasoning, defaulting to notify_human.",
            safe_to_auto=False
        )