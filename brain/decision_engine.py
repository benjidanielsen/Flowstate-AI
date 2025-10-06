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

    def analyze_task_dependencies(self, task_dependencies: Dict[str, List[str]]) -> List[str]:
        """
        Analyze task dependencies and return optimal execution order.
        
        Args:
            task_dependencies: Dict mapping task_id to list of prerequisite task_ids
            
        Returns:
            List of task_ids in topological order (dependencies first)
        """
        # Topological sort using Kahn's algorithm
        in_degree = {task_id: 0 for task_id in task_dependencies}
        
        for task_id, deps in task_dependencies.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[task_id] += 1
        
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            task_id = queue.pop(0)
            result.append(task_id)
            
            # Reduce in-degree for dependent tasks
            for other_task_id, deps in task_dependencies.items():
                if task_id in deps:
                    in_degree[other_task_id] -= 1
                    if in_degree[other_task_id] == 0:
                        queue.append(other_task_id)
        
        return result
    
    def optimize_resource_allocation(self) -> Dict[str, Any]:
        """
        Optimize resource allocation using a greedy algorithm.
        
        Returns:
            Dictionary with optimization recommendations
        """
        recommendations = {
            'reallocate_tasks': [],
            'scale_up_resources': [],
            'estimated_improvement': 0.0
        }
        
        # Calculate current utilization
        total_capacity = sum(self.resource_pool.total_resources.values())
        current_usage = sum(
            self.resource_pool.total_resources[r] - self.resource_pool.available_resources[r]
            for r in self.resource_pool.total_resources
        )
        utilization = current_usage / total_capacity if total_capacity > 0 else 0
        
        # If utilization is very high, recommend scaling
        if utilization > 0.85:
            for resource, total in self.resource_pool.total_resources.items():
                available = self.resource_pool.available_resources[resource]
                if available < total * 0.15:  # Less than 15% available
                    recommendations['scale_up_resources'].append({
                        'resource': resource,
                        'current': total,
                        'recommended': int(total * 1.5),
                        'reason': 'High utilization detected'
                    })
        
        # Analyze pending tasks for potential reallocation
        if len(self.task_queue) > 5:
            recommendations['reallocate_tasks'] = [
                {
                    'task_id': task.task_id,
                    'priority': task.priority,
                    'waiting_time': 'high',
                    'recommendation': 'Consider splitting or deferring'
                }
                for task in sorted(self.task_queue, key=lambda t: t.priority)[:3]
            ]
        
        # Estimate improvement
        recommendations['estimated_improvement'] = len(recommendations['scale_up_resources']) * 0.2
        
        return recommendations
    
    def predict_task_completion(self, task_id: str, historical_data: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Predict task completion time based on historical data.
        
        Args:
            task_id: ID of the task to predict
            historical_data: Optional dict mapping task types to average completion times
            
        Returns:
            Dictionary with prediction details
        """
        task = self.running_tasks.get(task_id)
        
        if not task:
            return {'error': 'Task not found or not running'}
        
        # Default completion time estimates based on resource requirements
        base_time = sum(task.resource_requirements.values()) * 10  # 10 seconds per resource unit
        
        # Adjust based on historical data if available
        if historical_data:
            task_type = task.description.split()[0] if task.description else 'unknown'
            if task_type in historical_data:
                base_time = historical_data[task_type]
        
        # Factor in current system load
        utilization = 1.0 - (sum(self.resource_pool.available_resources.values()) / 
                            sum(self.resource_pool.total_resources.values()))
        adjusted_time = base_time * (1 + utilization * 0.5)  # Up to 50% slower under full load
        
        return {
            'task_id': task_id,
            'estimated_completion_seconds': round(adjusted_time, 2),
            'confidence': 0.7 if historical_data else 0.5,
            'factors': {
                'base_time': base_time,
                'system_utilization': round(utilization, 2),
                'adjustment_factor': round(1 + utilization * 0.5, 2)
            }
        }
    
    def make_strategic_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a strategic decision based on current system state and context.
        
        Args:
            context: Dictionary with additional context for decision-making
            
        Returns:
            Dictionary with decision and reasoning
        """
        status = self.get_status()
        
        # Analyze current state
        pending_count = len(status['pending_tasks'])
        running_count = len(status['running_tasks'])
        resource_utilization = 1.0 - (sum(status['available_resources'].values()) / 
                                     sum(self.resource_pool.total_resources.values()))
        
        decision = {
            'action': 'continue',
            'reasoning': [],
            'recommendations': []
        }
        
        # Decision logic based on system state
        if pending_count > 10 and resource_utilization < 0.5:
            decision['action'] = 'scale_up_parallelism'
            decision['reasoning'].append('Many pending tasks with available resources')
            decision['recommendations'].append('Increase parallel task execution')
        
        if resource_utilization > 0.9:
            decision['action'] = 'throttle_new_tasks'
            decision['reasoning'].append('System resources nearly exhausted')
            decision['recommendations'].append('Defer non-critical tasks')
        
        if running_count == 0 and pending_count > 0:
            decision['action'] = 'investigate_blockage'
            decision['reasoning'].append('Tasks pending but none running')
            decision['recommendations'].append('Check for resource allocation issues')
        
        # Consider external context
        if context.get('high_priority_incoming'):
            decision['action'] = 'prepare_for_priority_tasks'
            decision['reasoning'].append('High priority tasks expected')
            decision['recommendations'].append('Consider preemptive resource reservation')
        
        return decision
