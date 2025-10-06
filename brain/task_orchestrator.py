import threading
import queue
import logging
from typing import Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

class Task:
    def __init__(self, 
                 task_id: str, 
                 func: Callable[..., None], 
                 dependencies: Optional[List[str]] = None,
                 args: Optional[List] = None,
                 kwargs: Optional[Dict] = None):
        self.task_id = task_id
        self.func = func
        self.dependencies = set(dependencies) if dependencies else set()
        self.args = args if args else []
        self.kwargs = kwargs if kwargs else {}
        self.completed = False

    def run(self):
        logger.debug(f"Starting task {self.task_id}...")
        try:
            self.func(*self.args, **self.kwargs)
            self.completed = True
            logger.debug(f"Task {self.task_id} completed.")
        except Exception as e:
            logger.error(f"Task {self.task_id} failed with error: {e}")
            raise

class TaskOrchestrator:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}  # task_id -> dependent tasks
        self.lock = threading.Lock()
        self.ready_queue = queue.Queue()
        self.running_tasks: Set[str] = set()

    def add_task(self, task: Task):
        with self.lock:
            if task.task_id in self.tasks:
                raise ValueError(f"Task with id {task.task_id} already exists.")
            self.tasks[task.task_id] = task

            # Initialize dependency graph
            for dep in task.dependencies:
                self.dependency_graph.setdefault(dep, set()).add(task.task_id)

            # If no dependencies, ready to run
            if not task.dependencies:
                self.ready_queue.put(task.task_id)
            logger.debug(f"Added task {task.task_id} with dependencies: {task.dependencies}")

    def _mark_task_completed(self, task_id: str):
        with self.lock:
            task = self.tasks[task_id]
            task.completed = True
            self.running_tasks.discard(task_id)

            # Enqueue dependent tasks if all dependencies are met
            dependents = self.dependency_graph.get(task_id, set())
            for dependent_id in dependents:
                dependent_task = self.tasks[dependent_id]
                if dependent_task.completed:
                    continue
                if all(self.tasks[dep].completed for dep in dependent_task.dependencies):
                    self.ready_queue.put(dependent_id)
                    logger.debug(f"Task {dependent_id} is now ready to run as all dependencies completed.")

    def _worker(self):
        while True:
            try:
                task_id = self.ready_queue.get(timeout=1)  # timeout allows graceful shutdown
            except queue.Empty:
                # If no tasks and no running tasks, we can exit worker
                with self.lock:
                    if not self.running_tasks and self.ready_queue.empty():
                        break
                continue

            with self.lock:
                if task_id in self.running_tasks:
                    self.ready_queue.task_done()
                    continue
                self.running_tasks.add(task_id)

            task = self.tasks[task_id]
            try:
                task.run()
                self._mark_task_completed(task_id)
            except Exception:
                # Fail early: stop orchestrator or handle retry logic here
                logger.error(f"Task {task_id} execution failed. Stopping orchestrator.")
                break
            finally:
                self.ready_queue.task_done()

    def run(self, num_worker_threads: int = 4):
        threads = []
        for _ in range(num_worker_threads):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            threads.append(t)

        # Wait for all tasks to be processed
        self.ready_queue.join()

        # Wait for threads to exit
        for t in threads:
            t.join()

    def is_all_completed(self) -> bool:
        with self.lock:
            return all(task.completed for task in self.tasks.values())

    def get_task_status(self) -> Dict[str, bool]:
        with self.lock:
            return {task_id: task.completed for task_id, task in self.tasks.items()}
