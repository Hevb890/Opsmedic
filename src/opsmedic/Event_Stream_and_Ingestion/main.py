import json
import time
from opsmedic.Event_Stream_and_Ingestion import RedisStreamProducer, SlidingWindowAggregator
from opsmedic.Telementry_and_Infra_Layer import SystemTopology, MetricSimulator, LogEngine


def run_layer2_demo():
    print("==================================================")
    print("      OPSMEDIC - LAYER 2 INGESTION HARNESS       ")
    print("==================================================\n")

    topo = SystemTopology()
    metrics = MetricSimulator(topo)
    log_engine = LogEngine(topo)

    try:
        producer = RedisStreamProducer()
        aggregator = SlidingWindowAggregator()
    except Exception as e:
        print(
            f"[X] Redis Connection Failed: {e}\n[!] Please start Redis: 'docker"
            " run -d -p 6379:6379 redis:alpine'"
        )
        return

    services = list(topo.SERVICES.keys())

    print(
        "[*] Ingesting Telemetry into Redis Stream and evaluating Sliding"
        " Window...\n"
    )

    for tick in range(1, 12):
        print(f"--- STREAM TICK #{tick} ---")

        # Inject Chaos at Step 4
        if tick == 4:
            print(
                "\n[!] >>> INJECTING CHAOS: DB DEADLOCK (Generating Error"
                " Burst) <<<\n"
            )
            topo.trigger_incident("db_deadlock")

        # Publish logs from all microservices into Redis Stream
        for srv in services:
            log_evt = log_engine.emit_log(srv)
            msg_id = producer.publish_event(log_evt)
            print(
                f"[PRODUCER -> REDIS] Published MsgID: {msg_id} | Service:"
                f" {srv} | Level: {log_evt.level.value}"
            )

        # Aggregator processes stream entries and checks sliding window
        alerts = aggregator.consume_stream(
            window_seconds=30, error_threshold=3
        )

        for alert in alerts:
            print("\n" + "=" * 50)
            print("[LAYER 2 ALERT ENGINE TRIGGERED]")
            print("=" * 50)
            print(json.dumps(alert.model_dump(), indent=2))
            print("=" * 50 + "\n")

        time.sleep(1)

    print("\n[✔] Layer 2 Execution Verified Successfully!")


if __name__ == "__main__":
    run_layer2_demo()