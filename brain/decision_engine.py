import heapq
from typing import List, Dict, Any, Tuple, Optional

class Task:
    """Represents a task with priority and resource requirements."""
    def __init__(self, task_id: str, description: str, priority: int, resource_requirements: Dict[str, int]):
        self.task_id = task_id
        self.description = description
        self.priority = priority  # Higher number means higher priority
        self.resource_requirements = resource_requirements  # e.g., {"cpu": 2, "memory": 512}
        self.allocated_resources = {}
        self.status = "pending"  # could be pending, running, completed, failed

    def __lt__(self, other: 'Task'):
        # For priority queue, invert because heapq is min-heap
        return self.priority > other.priority

class ResourcePool:
    """Tracks available resources and allocation."""
    def __init__(self, total_resources: Dict[str, int]):
        self.total_resources = total_resources.copy()
        self.available_resources = total_resources.copy()

    def can_allocate(self, requirements: Dict[str, int]) -> bool:
        for r, amount in requirements.items():
            if self.available_resources.get(r, 0) < amount:
                return False
        return True

    def allocate(self, requirements: Dict[str, int]) -> bool:
        if not self.can_allocate(requirements):
            return False
        for r, amount in requirements.items():
            self.available_resources[r] -= amount
        return True

    def release(self, requirements: Dict[str, int]) -> None:
        for r, amount in requirements.items():
            self.available_resources[r] += amount
            if self.available_resources[r] > self.total_resources[r]:
                self.available_resources[r] = self.total_resources[r]

class DecisionEngine:
    """Handles task prioritization, resource allocation, and strategic decisions."""
    def __init__(self, total_resources: Dict[str, int]):
        self.resource_pool = ResourcePool(total_resources)
        self.task_queue: List[Task] = []  # priority queue
        self.running_tasks: Dict[str, Task] = {}

    def add_task(self, task_id: str, description: str, priority: int, resource_requirements: Dict[str, int]) -> None:
        task = Task(task_id, description, priority, resource_requirements)
        heapq.heappush(self.task_queue, task)

    def _allocate_resources_to_task(self, task: Task) -> bool:
        if self.resource_pool.allocate(task.resource_requirements):
            task.allocated_resources = task.resource_requirements.copy()
            task.status = "running"
            self.running_tasks[task.task_id] = task
            return True
        return False

    def prioritize_and_allocate(self) -> List[Task]:
        """
        Try to allocate resources to highest priority tasks first.
        Returns list of tasks that started running this cycle.
        """
        started_tasks = []
        # We will try tasks in priority order but if cannot allocate, skip and try next

        # Use a temporary list to hold tasks that can't be allocated now
        temp_tasks = []

        while self.task_queue:
            task = heapq.heappop(self.task_queue)
            if self._allocate_resources_to_task(task):
                started_tasks.append(task)
            else:
                # Cannot allocate now, keep for next time
                temp_tasks.append(task)

        # Put back tasks that were not allocated
        for task in temp_tasks:
            heapq.heappush(self.task_queue, task)

        return started_tasks

    def complete_task(self, task_id: str, success: bool = True) -> None:
        task = self.running_tasks.pop(task_id, None)
        if not task:
            return
        # Release resources
        self.resource_pool.release(task.allocated_resources)
        task.status = "completed" if success else "failed"

    def get_status(self) -> Dict[str, Any]:
        """Returns current state for monitoring or strategic decisions."""
        return {
            "available_resources": self.resource_pool.available_resources.copy(),
            "running_tasks": {tid: t.status for tid, t in self.running_tasks.items()},
            "pending_tasks": [t.task_id for t in self.task_queue],
        }

    def strategic_decision(self) -> Optional[str]:
        """
        Placeholder for strategic decision logic.
        For example, preempt low priority tasks if high priority task cannot be allocated.
        Returns a string describing action or None if no action.
        """
        if not self.task_queue:
            return None

        highest_priority_task = self.task_queue[0]
        if self.resource_pool.can_allocate(highest_priority_task.resource_requirements):
            return None  # No action needed

        # Try to preempt lower priority running tasks
        low_priority_tasks = [t for t in self.running_tasks.values() if t.priority < highest_priority_task.priority]
        if not low_priority_tasks:
            return None

        # Sort low priority tasks ascending by priority (lowest first)
        low_priority_tasks.sort(key=lambda t: t.priority)

        # Try releasing resources by preempting tasks until enough resources
        resources_needed = highest_priority_task.resource_requirements.copy()

        # Calculate current available + resources that could be freed by preemption
        available = self.resource_pool.available_resources.copy()
        for r in available:
            resources_needed[r] = max(0, resources_needed.get(r, 0) - available.get(r, 0))

        tasks_to_preempt = []

        def resources_sufficient(needed: Dict[str, int]) -> bool:
            return all(amount <= 0 for amount in needed.values())

        for task in low_priority_tasks:
            # Subtract task resources from needed
            for r, amount in task.allocated_resources.items():
                resources_needed[r] = max(0, resources_needed.get(r, 0) - amount)
            tasks_to_preempt.append(task)
            if resources_sufficient(resources_needed):
                break

        if not resources_sufficient(resources_needed):
            return None  # Cannot free enough resources

        # Preempt identified tasks
        for task in tasks_to_preempt:
            self.complete_task(task.task_id, success=False)

        return f"Preempted tasks {[t.task_id for t in tasks_to_preempt]} to allocate task {highest_priority_task.task_id}"