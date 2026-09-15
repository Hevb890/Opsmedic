import time
from opsmedic.Telementry_and_Infra_Layer import LogEngine, SystemTopology, MetricSimulator, LoghubReplayer



def run_layer1_simulation():
    print("==================================================")
    print("      OPSMEDIC - LAYER 1 TELEMETRY HARNESS       ")
    print("==================================================\n")

    topology = SystemTopology()
    metrics = MetricSimulator(topology)
    log_engine = LogEngine(topology)
    replayer = LoghubReplayer()

    services = list(topology.SERVICES.keys())

    print("[*] Starting Normal Telemetry Stream (1 log/sec)...\n")
    for step in range(1, 12):
        print(f"--- TICK #{step} ---")

        # 1. Inject Chaos at Step 5
        if step == 5:
            print(
                "\n[!] >>> CHAOS INJECTION TRIGGERED: DB DEADLOCK INCIDENT"
                " <<<\n"
            )
            topology.trigger_incident("db_deadlock")

        # 2. Clear Incident at Step 9
        if step == 9:
            print("\n[*] >>> RECOVERY TRIGGERED: CLEARING INCIDENTS <<<\n")
            topology.clear_incidents()

        # Emit telemetry for each service
        for srv in services:
            # Emit Metric
            m_event = metrics.generate_tick(srv)
            print(f"[METRIC] [{m_event.service}] => {m_event.payload}")

            # Emit Log
            l_event = log_engine.emit_log(srv)
            print(
                f"[{l_event.level.value}] [{l_event.service}] =>"
                f" {l_event.payload}"
            )

        time.sleep(1)

    print("\n[*] Replaying Benchmark Sample Logs from Loghub Replayer:")
    for benchmark_event in replayer.replay_steam():
        print(
            f"[LOGHUB REPLAY] [{benchmark_event.level.value}] =>"
            f" {benchmark_event.payload['raw_log']}"
        )

    print("\n[✔] Layer 1 Execution Finished Successfully!")


if __name__ == "__main__":
    run_layer1_simulation()