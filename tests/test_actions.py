from src.handlers.actions import execute_action

def test_rollback_action():
    result = execute_action("rollback", "event-123", "payments-api", {})
    assert result["action"] == "rollback"
    assert result["status"] == "executed"

def test_restart_action():
    result = execute_action("restart", "event-123", "payments-api", {})
    assert result["action"] == "restart"
    assert result["status"] == "executed"

def test_scale_up_action():
    result = execute_action("scale_up", "event-123", "payments-api", {})
    assert result["action"] == "scale_up"
    assert result["status"] == "executed"

def test_notify_human_action():
    result = execute_action("notify_human", "event-123", "payments-api", {})
    assert result["action"] == "notify_human"
    assert result["status"] == "executed"

def test_no_action():
    result = execute_action("no_action", "event-123", "payments-api", {})
    assert result["action"] == "no_action"
    assert result["status"] == "recorded"

def test_unknown_action():
    result = execute_action("unknown", "event-123", "payments-api", {})
    assert result["action"] == "unknown"
    assert result["status"] == "error"