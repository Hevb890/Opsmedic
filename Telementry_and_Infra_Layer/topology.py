import random
from typing import Dict, List

class Systemtopologylogy:
    SERVICES: Dict[str, List[str]] = {
        "frontend-proxy": ["prod-frontend-a1","prod-frontend-a2"],
        "auth-service": ["prod-auth-b1", "prod-auth-b2"],
        "payment-gateway": ["prod-payment-c1", "prod-payment-c2"],
        "user-db": ["db-primary-node-1"]
    }

    def __init__(self):
        self.active_db_connections: int = 15
        self.max_db_connections: int = 100
        self.db_deadlock_active: bool = False
        self.oom_active: bool = False

    def get_random_host(self, service: str) -> str:
        hosts = self.SERVICES.get(service, ["prod-unknown-01"])
        return random.choice(hosts)

    def trigger_incident(self, incident_type: str) -> None:
        if incident_type == "db_deadlock":
            self.db_deadlock_active = True
            self.active_db_connections = 98
        elif incident_type == "oom_kill":
            self.oom_active = True

    def clear_incidents(self) -> None:
        self.db_deadlock_active = False
        self.oom_active = False
        self.active_db_connections = 15