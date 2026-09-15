import json
import time
from datetime import datetime, timezone
from typing import Dict, Optional
import redis
from pydantic import BaseModel, Field

class IncidentAlert(BaseModel):
    alert_id: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    service: str
    trigger_rule: str
    error_count: int
    window_seconds: int
    sample_error_payload: Dict

class SlidingWindowAggregator:
    def __init__(
            self,
            host: str = "localhost",
            port: int = 6379,
            stream_key: str = "telemetry:raw:stream",
            group_name: str = "opsmedic_aggregators",
            consumer_name: str = "aggregator_worker_1",
    ):
        self.redis = redis.Redis(host=host, port=port, decode_responses=True)
        self.stream_key = stream_key
        self.group_name = group_name
        self.consumer_name = consumer_name

        try:
            self.redis.xgroup_create(
                self.stream_key, self.group_name, id="0", mkstream=True
            )
        except redis.exceptions.ResponseError:
            pass

    def process_event_and_check_alert(
            self,
            event_data: Dict,
            window_seconds: int = 30,
            error_threshold: int = 5,
    ) -> Optional[IncidentAlert]:
        service = event_data.get('service')
        level = event_data.get('level')

        if level not in ["ERROR", "FATAL"]:
            return None

        now = time.time()
        window_start = now - window_seconds
        zset_key = f"window:errors:{service}"

        self.redis.zadd(zset_key, {f"err_{now}": now})

        self.redis.zremrangebyscore(zset_key, "-inf", window_start)

        self.redis.expire(zset_key, window_seconds * 2)

        current_error_count = self.redis.zcard(zset_key)

        if current_error_count >= error_threshold:
            cooldown_key = f"alert:cooldown:{service}"
            if not self.redis.get(cooldown_key):
                self.redis.set(
                    cooldown_key, "ACTIVE", ex=60
                )

                payload = json.loads(event_data.get("payload", "{}"))

                alert = IncidentAlert(
                    alert_id=f"alt_{int(now)}",
                    service=service,
                    trigger_rule=f"ERROR_BURST_EXCEEDED ({error_threshold} errors in {window_seconds}s)",
                    error_count=current_error_count,
                    window_seconds=window_seconds,
                    sample_error_payload=payload.get("payload", {}),
                )

                return alert

        return None

    def consume_stream(self, window_seconds: int = 30, error_threshold: int = 5):
        entries = self.redis.xreadgroup(
            groupname=self.group_name,
            consumername=self.consumer_name,
            streams={self.stream_key: ">"},
            count=10,
            block=1000
        )

        alerts_triggered = []

        if entries:
            for stream_name, message_list in entries:
                for message_id, event_data in message_list:
                    alert = self.process_event_and_check_alert(
                        event_data=event_data,
                        window_seconds=window_seconds,
                        error_threshold=error_threshold
                    )

                    if alert:
                        alerts_triggered.append(alert)

                    self.redis.xack(
                        self.stream_key, self.group_name, message_id
                    )
        return alerts_triggered