import asyncio
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evolution_framework.synthetic_load_scheduler import SyntheticLoadScheduler


class DummyPerformanceTuner:
    def __init__(self):
        self.reports = []

    async def process_bottleneck_report(self, report):
        self.reports.append(report)
        return {"status": "ok"}


class DummyCostOptimizer:
    def __init__(self):
        self.reports = []

    async def process_bottleneck_report(self, report):
        self.reports.append(report)
        return {"status": "ok"}


@pytest.mark.asyncio
async def test_scheduler_runs_and_notifies_components():
    tuner = DummyPerformanceTuner()
    optimizer = DummyCostOptimizer()
    scheduler = SyntheticLoadScheduler(tuner, optimizer, task_volume=2000, batch_size=500, interval_seconds=1)

    report = await scheduler.run_once(correlation_id="corr-test")

    assert report["total_tasks"] == 2000
    assert report["correlation_id"] == "corr-test"
    assert tuner.reports[0]["correlation_id"] == "corr-test"
    assert optimizer.reports[0]["correlation_id"] == "corr-test"
    assert "latency" in report["bottlenecks"]


@pytest.mark.asyncio
async def test_scheduler_background_loop_stops_cleanly():
    tuner = DummyPerformanceTuner()
    optimizer = DummyCostOptimizer()
    scheduler = SyntheticLoadScheduler(tuner, optimizer, task_volume=2000, batch_size=500, interval_seconds=1)

    scheduler.start()
    await asyncio.sleep(0.1)
    await scheduler.stop()

    assert scheduler._task is None
