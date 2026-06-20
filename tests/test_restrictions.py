from unittest.mock import MagicMock
from src.reasoning.engine import apply_restrictions
from src.db.models import Event
from datetime import datetime


def make_event(severity="high", environment_id="prod"):
    event = MagicMock(spec=Event)
    event.severity = severity
    event.environment_id = environment_id
    return event

def test_critical_severity_forces_safe_to_auto_false():
    event = make_event(severity="critical")
    decision = {"action": "restart", "confidence": 0.9, "reasoning": "test", "safe_to_auto": True}
    result = apply_restrictions(event, decision)
    assert result["safe_to_auto"] is False

def test_low_confidence_forces_safe_to_auto_false():
    event = make_event(severity="low")
    decision = {"action": "restart", "confidence": 0.5, "reasoning": "test", "safe_to_auto": True}
    result = apply_restrictions(event, decision)
    assert result["safe_to_auto"] is False

def test_prod_rollback_forces_safe_to_auto_false():
    event = make_event(severity="high", environment_id="prod")
    decision = {"action": "rollback", "confidence": 0.9, "reasoning": "test", "safe_to_auto": True}
    result = apply_restrictions(event, decision)
    assert result["safe_to_auto"] is False

def test_prod_scale_up_forces_safe_to_auto_false():
    event = make_event(severity="high", environment_id="prod")
    decision = {"action": "scale_up", "confidence": 0.9, "reasoning": "test", "safe_to_auto": True}
    result = apply_restrictions(event, decision)
    assert result["safe_to_auto"] is False

def test_dev_restart_high_confidence_safe_to_auto_true():
    event = make_event(severity="high", environment_id="dev")
    decision = {"action": "restart", "confidence": 0.9, "reasoning": "test", "safe_to_auto": True}
    result = apply_restrictions(event, decision)
    assert result["safe_to_auto"] is True