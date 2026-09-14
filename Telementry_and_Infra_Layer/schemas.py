import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class TelemetryType(str, Enum):
    LOG = "LOG"
    METRIC = "METRIC"

class LogLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"

class TelemetryEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    environment: str = "production"
    service: str
    host_id: str
    telemetry_type: TelemetryType
    level: LogLevel = LogLevel.INFO
    payload: Dict[str, Any]

    def to_json(self) -> str:
        return self.model_dump_json()