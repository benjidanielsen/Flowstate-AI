import threading
import queue
import time
from typing import Any, Dict, List, Callable, Optional

class BrainCoreIntelligence:
    """
    Central decision-making system that coordinates all AI agents.
    Manages incoming tasks, delegates to agents, aggregates results, and makes final decisions.
    """

    def __init__(self):
        # Registry of AI agents: name -> callable(agent_input) -> agent_output
        self.agents: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        # Task queue for incoming decision requests
        self.task_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        # Thread for processing tasks
        self._worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self._worker_thread.start()
        # Storage for results keyed by task id
        self.results: Dict[str, Any] = {}
        # Lock for synchronizing access to results
        self._results_lock = threading.Lock()

    def register_agent(self, name: str, agent_callable: Callable[[Dict[str, Any]], Any]) -> None:
        """Register a new AI agent with a unique name."""
        if name in self.agents:
            raise ValueError(f"Agent with name '{name}' already registered.")
        self.agents[name] = agent_callable

    def submit_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Submit a new task to be processed.
        task_id: unique identifier for the task
        task_data: dictionary containing input data and any instructions
        """
        self.task_queue.put({'task_id': task_id, 'data': task_data})

    def get_result(self, task_id: str, timeout: Optional[float] = None) -> Optional[Any]:
        """Retrieve the result for a given task_id.
        If timeout is set, will wait up to timeout seconds.
        Returns None if result not available within timeout.
        """
        start_time = time.time()
        while True:
            with self._results_lock:
                if task_id in self.results:
                    return self.results.pop(task_id)
            if timeout is not None and (time.time() - start_time) > timeout:
                return None
            time.sleep(0.1)

    def _process_tasks(self) -> None:
        """Internal worker thread function to process tasks from the queue."""
        while True:
            task = self.task_queue.get()
            if task is None:
                break  # Allow graceful shutdown if needed

            task_id = task['task_id']
            task_data = task['data']

            try:
                # Delegate to all agents and collect their responses
                agent_responses = {}
                for name, agent_callable in self.agents.items():
                    try:
                        agent_responses[name] = agent_callable(task_data)
                    except Exception as e:
                        agent_responses[name] = {'error': str(e)}

                # Make final decision based on agents' responses
                final_decision = self._make_decision(agent_responses, task_data)

                with self._results_lock:
                    self.results[task_id] = final_decision

            except Exception as e:
                with self._results_lock:
                    self.results[task_id] = {'error': f'Core processing error: {str(e)}'}

            self.task_queue.task_done()

    def _make_decision(self, agent_responses: Dict[str, Any], task_data: Dict[str, Any]) -> Any:
        """Combine agent responses to make a final decision.
        This is a placeholder for decision logic.
        """
        # Example: aggregate all successful responses into a list
        successful_responses = [resp for resp in agent_responses.values() if not isinstance(resp, dict) or 'error' not in resp]

        if not successful_responses:
            # If no successful responses, return all errors
            return {'error': 'All agents failed', 'details': agent_responses}

        # For demonstration, just return all agent results combined
        return {
            'aggregated_results': successful_responses,
            'all_agent_responses': agent_responses,
            'original_task': task_data
        }

# Example usage/testing
if __name__ == "__main__":
    def dummy_agent_1(data):
        return {'agent1_output': f"processed {data.get('input', '')}"}

    def dummy_agent_2(data):
        if data.get('fail_agent2'):
            raise RuntimeError("Simulated failure")
        return {'agent2_output': len(str(data.get('input', '')))}

    brain = BrainCoreIntelligence()
    brain.register_agent('agent1', dummy_agent_1)
    brain.register_agent('agent2', dummy_agent_2)

    test_task_id = 'task_123'
    brain.submit_task(test_task_id, {'input': 'Hello AI agents!'})

    # Wait and get result
    result = brain.get_result(test_task_id, timeout=5)
    print(f"Result for {test_task_id}: {result}")
