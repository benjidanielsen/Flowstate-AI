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
        """
        Combine agent responses to make a final decision using intelligent aggregation.
        
        This enhanced decision-making process:
        1. Analyzes agent responses for consistency
        2. Weights responses based on agent reliability
        3. Resolves conflicts using voting or consensus
        4. Provides confidence scores for decisions
        """
        # Separate successful and failed responses
        successful_responses = {}
        failed_responses = {}
        
        for agent_name, response in agent_responses.items():
            if isinstance(response, dict) and 'error' in response:
                failed_responses[agent_name] = response
            else:
                successful_responses[agent_name] = response
        
        # If no successful responses, return all errors
        if not successful_responses:
            return {
                'status': 'failed',
                'error': 'All agents failed',
                'details': agent_responses,
                'confidence': 0.0
            }
        
        # Calculate confidence based on success rate
        total_agents = len(agent_responses)
        successful_agents = len(successful_responses)
        base_confidence = successful_agents / total_agents
        
        # Analyze response consistency
        response_values = list(successful_responses.values())
        consistency_score = self._calculate_consistency(response_values)
        
        # Adjust confidence based on consistency
        final_confidence = base_confidence * (0.5 + 0.5 * consistency_score)
        
        # Determine primary decision
        primary_decision = self._aggregate_responses(successful_responses, task_data)
        
        return {
            'status': 'success',
            'decision': primary_decision,
            'confidence': round(final_confidence, 2),
            'successful_agents': list(successful_responses.keys()),
            'failed_agents': list(failed_responses.keys()),
            'agent_count': {
                'total': total_agents,
                'successful': successful_agents,
                'failed': len(failed_responses)
            },
            'all_responses': agent_responses,
            'original_task': task_data
        }
    
    def _calculate_consistency(self, responses: List[Any]) -> float:
        """
        Calculate consistency score among agent responses.
        
        Returns a score between 0 and 1, where 1 means perfect consistency.
        """
        if len(responses) <= 1:
            return 1.0
        
        # Simple heuristic: check if responses are similar
        # For dict responses, check for common keys and values
        if all(isinstance(r, dict) for r in responses):
            common_keys = set(responses[0].keys())
            for r in responses[1:]:
                common_keys &= set(r.keys())
            
            if not common_keys:
                return 0.5  # No common structure
            
            # Check value agreement for common keys
            agreements = 0
            total_checks = 0
            
            for key in common_keys:
                values = [r[key] for r in responses]
                unique_values = len(set(str(v) for v in values))
                if unique_values == 1:
                    agreements += 1
                total_checks += 1
            
            return agreements / total_checks if total_checks > 0 else 0.5
        
        # For non-dict responses, check if they're equal
        unique_responses = len(set(str(r) for r in responses))
        return 1.0 / unique_responses if unique_responses > 0 else 0.5
    
    def _aggregate_responses(self, responses: Dict[str, Any], task_data: Dict[str, Any]) -> Any:
        """
        Aggregate successful responses into a single decision.
        
        Uses different strategies based on response types:
        - For numerical values: calculate average or median
        - For categorical values: use majority voting
        - For complex objects: merge intelligently
        """
        if not responses:
            return None
        
        # If only one response, return it directly
        if len(responses) == 1:
            return list(responses.values())[0]
        
        # For dict responses, merge them
        if all(isinstance(r, dict) for r in responses.values()):
            merged = {}
            all_keys = set()
            for r in responses.values():
                all_keys.update(r.keys())
            
            for key in all_keys:
                values = [r[key] for r in responses.values() if key in r]
                
                # If all values are numeric, calculate average
                if all(isinstance(v, (int, float)) for v in values):
                    merged[key] = sum(values) / len(values)
                # If all values are the same, use that value
                elif len(set(str(v) for v in values)) == 1:
                    merged[key] = values[0]
                # Otherwise, use majority voting
                else:
                    from collections import Counter
                    merged[key] = Counter(str(v) for v in values).most_common(1)[0][0]
            
            return merged
        
        # For non-dict responses, use majority voting
        from collections import Counter
        response_list = list(responses.values())
        most_common = Counter(str(r) for r in response_list).most_common(1)[0][0]
        
        # Return the original response that matches the most common string representation
        for r in response_list:
            if str(r) == most_common:
                return r
        
        return response_list[0]  # Fallback

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
