"""Synthetic load tester that feeds PerformanceTuner and CostOptimizer."""

import asyncio
import os
import random
import statistics
import time
from typing import Any, Dict, Optional
from uuid import uuid4

from .observability import record_agent_action


class SyntheticLoadScheduler:
    """Run synthetic workloads and forward reports to optimizers."""

    def __init__(
        self,
        performance_tuner: Any,
        cost_optimizer: Any,
        task_volume: int = 100_000,
        batch_size: int = 5_000,
        interval_seconds: int = 900,
    ) -> None:
        self.performance_tuner = performance_tuner
        self.cost_optimizer = cost_optimizer
        self.task_volume = task_volume
        self.batch_size = batch_size
        self.interval_seconds = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()

    async def run_once(self, correlation_id: Optional[str] = None) -> Dict[str, Any]:
        correlation = correlation_id or str(uuid4())
        start = time.perf_counter()
        samples = []
        costs = []
        for _ in range(0, self.task_volume, self.batch_size):
            batch = [random.uniform(0.05, 0.35) for _ in range(self.batch_size)]
            samples.extend(batch)
            costs.extend(random.uniform(0.0005, 0.002) for _ in range(self.batch_size))
        elapsed = time.perf_counter() - start
        latency_p95 = statistics.quantiles(samples, n=100)[94] * 1000
        performance_metrics = {
            "latency_p95": round(latency_p95, 2),
            "error_rate": round(random.uniform(0.01, 0.06), 4),
            "throughput": round(self.task_volume / max(elapsed, 0.001), 2),
            "correlation_id": correlation,
        }
        cost_metrics = {
            "monthly_cost_usd": round(sum(costs) * 30, 2),
            "unit_cost": round(statistics.mean(costs), 6),
            "correlation_id": correlation,
        }
        report = {
            "correlation_id": correlation,
            "component": "synthetic_task_engine",
            "performance_metrics": performance_metrics,
            "cost_metrics": cost_metrics,
            "total_tasks": self.task_volume,
            "bottlenecks": self._identify_bottlenecks(performance_metrics, cost_metrics),
        }
        record_agent_action("synthetic_load.report", correlation, {
            **performance_metrics,
            **cost_metrics,
        })
        if hasattr(self.performance_tuner, 'process_bottleneck_report'):
            await self.performance_tuner.process_bottleneck_report(report)
        if hasattr(self.cost_optimizer, 'process_bottleneck_report'):
            await self.cost_optimizer.process_bottleneck_report(report)
        return report

    def start(self) -> None:
        if self._task is None:
            self._stop_event.clear()
            self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._stop_event.set()
        await self._task
        self._task = None

    async def _loop(self) -> None:
        while not self._stop_event.is_set():
            await self.run_once()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.interval_seconds)
            except asyncio.TimeoutError:
                continue

    def _identify_bottlenecks(self, performance: Dict[str, Any], cost: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "latency": performance.get("latency_p95", 0) > 450,
            "error_rate": performance.get("error_rate", 0) > 0.05,
            "cost_spike": cost.get("monthly_cost_usd", 0) > 500,
        }


def build_scheduler(performance_tuner: Any, cost_optimizer: Any) -> SyntheticLoadScheduler:
    interval = int(os.getenv("SYNTHETIC_LOAD_INTERVAL_SECONDS", "900"))
    task_volume = int(os.getenv("SYNTHETIC_LOAD_TASKS", "100000"))
    batch_size = int(os.getenv("SYNTHETIC_LOAD_BATCH", "5000"))
    return SyntheticLoadScheduler(performance_tuner, cost_optimizer, task_volume, batch_size, interval)
