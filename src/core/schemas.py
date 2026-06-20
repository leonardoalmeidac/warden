from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, field_validator

VALID_SEVERITIES = {"low", "medium", "high", "critical"}
VALID_ENVIRONMENTS = {"dev", "qa", "stg", "prod"}

class EventPayload(BaseModel):
    project_id: str
    environment_id: str
    severity: str
    signal : str
    context: Optional[dict [str, Any]] = None
    timestamp: datetime

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, value):
        if value not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity level: {value}. Must be one of {VALID_SEVERITIES}.")
        return value

    @field_validator('environment_id')
    @classmethod
    def validate_environment(cls, value):
        if value not in VALID_ENVIRONMENTS:
            raise ValueError(f"Invalid environment: {value}. Must be one of {VALID_ENVIRONMENTS}.")
        return value