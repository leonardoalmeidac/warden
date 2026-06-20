import json
import logging

logger = logging.getLogger(__name__)

def rollback(event_id: str, project_id: str, context: dict):
    logger.info(json.dumps({
        "event": "action_executed",
        "action": "rollback",
        "event_id": event_id,
        "project_id": project_id,
        "mock": True
    }))

    return {
        "action": "rollback",
        "status": "executed",
        "detail": f"Rollback executed for event {event_id} in project {project_id}."
    }

def restart(event_id: str, project_id: str, context: dict):
    logger.info(json.dumps({
        "event": "action_executed",
        "action": "restart",
        "event_id": event_id,
        "project_id": project_id,
        "mock": True
    }))

    return {
        "action": "restart",
        "status": "executed",
        "detail": f"Restart executed for event {event_id} in project {project_id}."
    }

def scale_up(event_id: str, project_id: str, context: dict):
    logger.info(json.dumps({
        "event": "action_executed",
        "action": "scale_up",
        "event_id": event_id,
        "project_id": project_id,
        "mock": True
    }))

    return {
        "action": "scale_up",
        "status": "executed",
        "detail": f"Scale up executed for event {event_id} in project {project_id} by 1 replica."
    }

def notify_human(event_id: str, project_id: str, context: dict):
    logger.info(json.dumps({
        "event": "action_executed",
        "action": "notify_human",
        "event_id": event_id,
        "project_id": project_id,
        "mock": True
    }))

    return {
        "action": "notify_human",
        "status": "executed",
        "detail": f"Human notified for event {event_id} in project {project_id}."
    }

def no_action(event_id: str, project_id: str, context: dict):
    logger.info(json.dumps({
        "event": "action_executed",
        "action": "no_action",
        "event_id": event_id,
        "project_id": project_id
    }))

    return {
        "action": "no_action",
        "status": "recorded",
        "detail": f"No action taken for event {event_id} in project {project_id}."
    }

HANDLERS = {
    "rollback": rollback,
    "restart": restart,
    "scale_up": scale_up,
    "notify_human": notify_human,
    "no_action": no_action
}

def execute_action(action: str, event_id: str, project_id: str, context: dict):
    handler = HANDLERS.get(action)
    if not handler:
        logger.error(json.dumps({
            "event": "action_not_found",
            "action": action,
            "detail": "Unknown action",
        }))
        return {
            "action": action,
            "status": "error",
            "detail": f"Action '{action}' not found for event {event_id} in project {project_id}."
        }
    return handler(event_id, project_id, context or {})