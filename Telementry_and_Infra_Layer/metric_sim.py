import random
from schemas import LogLevel, TelemetryEvent, TelemetryType
from topology import Systemtopologylogy

class MetricSimulator:
    def __init__(self, topologylogy: Systemtopologylogy):
        self.topologylogy = topologylogy

    def generate_tick(self, service: str) -> TelemetryType:
        host = self.topologylogy.get_random_host(service)

        if service == "user-db" and self.topology.db_deadlock_active:
            cpu = round(random.uniform(92.0, 99.8), 2)
            mem = round(random.uniform(85.0, 94.0), 2)
            active_conns = random.randint(95, self.topology.max_db_connections)
        elif service == "payment-gateway" and self.topology.oom_active:
            cpu = round(random.uniform(60.0, 80.0), 2)
            mem = round(random.uniform(96.0, 99.9), 2)
            active_conns = self.topology.active_db_connections
        else:
            cpu = round(random.uniform(12.0, 35.0), 2)
            mem = round(random.uniform(40.0, 65.0), 2)
            active_conns = self.topology.active_db_connections

        return TelemetryEvent(
            service=service,
            host_id=host,
            telemetry_type=TelemetryType.METRIC,
            level=LogLevel.WARN if cpu > 85.0 or mem > 90.0 else LogLevel.INFO,
            payload={
                "cpu_usage_pct": cpu,
                "memory_usage_pct": mem,
                "active_db_connections": active_conns,
                "max_db_connections": self.topology.max_db_connections,
            },
        )