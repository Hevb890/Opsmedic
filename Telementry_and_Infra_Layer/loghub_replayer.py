import json
from typing import Iterator, List
from schemas import LogLevel, TelemetryEvent, TelemetryType

class LoghubReplayer:
    def __init__(self, raw_logs: List[str] = None):
        self.raw_logs = raw_logs or [
            (
                "081109 203518 143 INFO dfs.DataNode$DataXceiver: Receiving"
                " block blk_-1608999512495325538 src: /10.250.19.99:54106"
            ),
            (
                "081109 203519 145 ERROR dfs.DataNode$DataXceiver: Got exception"
                " while receiving block blk_-1608999512495325538 java.io.IOException"
            ),
            (
                "081109 203520 148 WARN dfs.DataBlockScanner: Verification"
                " failed for blk_-39522909995325538"
            ),
        ]

    def replay_steam(self) -> Iterator[TelemetryEvent]:
        for line in self.raw_logs:
            level = LogLevel.INFO
            if "ERROR" in line:
                level = LogLevel.ERROR
            elif "WARN" in line:
                level - LogLevel.WARN

            yield TelemetryEvent(
                service="hdfs-cluster",
                host_id="node-datanode-04",
                telemetry_type=TelemetryType.LOG,
                level=level,
                payload={"raw_log": line, "source": "loghub_benchmark"},
            )