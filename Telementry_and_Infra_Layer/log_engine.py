import random

from schemas import LogLevel, TelemetryType, TelemetryEvent
from topology import SystemTopology

class LogEngine:
    def __init__(self, topology: SystemTopology):
        self.topology = topology

    def emit_log(self, service: str) -> TelemetryEvent:
        host = self.topology.get_random_host(service)

        if self.topolgy.db_deadlock_active and service in [
            "payment-gateway",
            "user-db",
        ]:
            if service == "user-db":
                return TelemetryEvent(
                    service=service,
                    host_id=host,
                    telemetry_type=TelemetryType.LOG,
                    level=LogLevel.ERROR,
                    payload={
                        "message": (
                            "transaction_lock_timeout: Process 1042 waiting "
                            "for ShareLock on transaction 884931"
                        ),
                        "error_code": "ERR_DB_LOCK_TIMEOUT",
                        "latency_ms": random.randint(4000, 8000),
                    },
                )
            else:
                return TelemetryEvent(
                    service=service,
                    host_id=host,
                    telemetry_type=TelemetryType.LOG,
                    level=LogLevel.FATAL,
                    payload={
                        "message": (
                            "Failed to process transaction: DB connection pool"
                            " exhausted"
                        ),
                        "error_code": "ERR_POOL_EXHAUSTED",
                        "latency_ms": 5000,
                        "status_code": 504,
                    },
                )

        if self.topology.oom_active and service == "auth-service":
            return TelemetryEvent(
                service=service,
                host_id=host,
                telemetry_type=TelemetryType.LOG,
                level=LogLevel.FATAL,
                payload={
                    "message": (
                        "FATAL: Out of Memory (OOMKilled) container id:"
                        " auth-service-7f98"
                    ),
                    "error_code": "OOM_KILLED",
                    "exit_code": 137,
                },
            )

        # Normal operational log emitter
        endpoints = ["/api/v1/health", "/api/v1/users", "/checkout/process"]
        return TelemetryEvent(
            service=service,
            host_id=host,
            telemetry_type=TelemetryType.LOG,
            level=LogLevel.INFO,
            payload={
                "endpoint": random.choice(endpoints),
                "message": "HTTP Request Processed",
                "status_code": 200,
                "latency_ms": random.randint(8, 45),
            },
        )