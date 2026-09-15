import redis
from opsmedic.Telementry_and_Infra_Layer.schemas import TelemetryEvent

class RedisStreamProducer:
    def __init__(self, host: str = 'localhost', port: int = 6379, stream_key: str = 'telemetry:raw:stream'):
        self.stream_key = stream_key
        self.redis_client = redis.Redis(
            host = host, port = port, decode_responses=True
        )

    def publish_event(self, event: TelemetryEvent) -> str:
        data = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "service": event.service,
            "host_id": event.host_id,
            "telemetry_type": event.telemetry_type.value,
            "level": event.level.value,
            "payload": event.to_json(),
        }

        entry_id = self.redis_client.xadd(
            self.stream_key, fields = data, maxlen = 10000, approximate=True
        )

        return entry_id