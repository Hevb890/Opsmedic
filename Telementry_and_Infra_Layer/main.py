import time
from log_engine import LogEngine
from loghub_replayer import LoghubReplayer
from metric_sim import MetricSimulator
from topology import SystemTopology


def run_layer1_simulation() -> None:
    topology = SystemTopology()
    metrics = MetricSimulator(topology)
    log_engine = LogEngine(topology)
    replayer = LoghubReplayer()

    services = list(topology.SERVICES.keys())

    for step in range(1,12):
        if step == 5:
            topology.trigger_incident("db_deadlock")
        if step == 9:
            topology.clear_incidents()

        for srv in services:
            m_event = metrics.generate_tick(srv)

            l_event = log_engine.emit_log(srv)

        time.sleep(1)

        for benchmark_event in replayer.replay_steam():
            print(
            f"[LOGHUB REPLAY] [{benchmark_event.level.value}] =>"
            f" {benchmark_event.payload['raw_log']}"
        )



        