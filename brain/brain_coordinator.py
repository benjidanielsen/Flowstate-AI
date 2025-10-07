"""
Brain Coordinator for Flowstate-AI
Advanced orchestration system for coordinating multiple AI agents and decision-making processes.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from collections import defaultdict
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainCoordinator:
    """
    Advanced brain coordinator that manages agent orchestration, task delegation,
    and intelligent decision-making across the Flowstate-AI system.
    """
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize the brain coordinator."""
        self.redis = redis_client
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.task_history: List[Dict[str, Any]] = []
        self.agent_performance: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'success_rate': 1.0,
            'avg_response_time': 0.0,
            'total_tasks': 0,
            'successful_tasks': 0
        })
        
    def register_agent(self, agent_id: str, agent_config: Dict[str, Any]) -> None:
        """
        Register a new AI agent with the coordinator.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_config: Configuration including capabilities, priority, etc.
        """
        self.agents[agent_id] = {
            'id': agent_id,
            'name': agent_config.get('name', agent_id),
            'capabilities': agent_config.get('capabilities', []),
            'priority': agent_config.get('priority', 1),
            'status': 'idle',
            'registered_at': datetime.now().isoformat()
        }
        logger.info(f"Agent registered: {agent_id} ({agent_config.get('name')})")
        
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the coordinator."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")
            
    async def delegate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate a task to the most appropriate agent(s) based on capabilities and performance.
        
        Args:
            task: Task dictionary containing type, data, requirements, etc.
            
        Returns:
            Result dictionary with agent responses and final decision
        """
        task_id = task.get('id', f"task_{datetime.now().timestamp()}")
        task_type = task.get('type', 'general')
        required_capabilities = task.get('capabilities', [])
        
        logger.info(f"Delegating task {task_id} of type {task_type}")
        
        # Find suitable agents
        suitable_agents = self._find_suitable_agents(required_capabilities)
        
        if not suitable_agents:
            logger.warning(f"No suitable agents found for task {task_id}")
            return {
                'task_id': task_id,
                'status': 'failed',
                'error': 'No suitable agents available',
                'timestamp': datetime.now().isoformat()
            }
        
        # Execute task with selected agents
        agent_results = await self._execute_with_agents(task, suitable_agents)
        
        # Make final decision based on agent results
        final_decision = self._synthesize_decision(agent_results, task)
        
        # Record task in history
        self._record_task(task_id, task, agent_results, final_decision)
        
        # Update agent performance metrics
        self._update_agent_performance(agent_results)
        
        return {
            'task_id': task_id,
            'status': 'completed',
            'decision': final_decision,
            'agent_results': agent_results,
            'timestamp': datetime.now().isoformat()
        }
        
    def _find_suitable_agents(self, required_capabilities: List[str]) -> List[str]:
        """
        Find agents that match the required capabilities and are currently available.
        
        Args:
            required_capabilities: List of required capability tags
            
        Returns:
            List of suitable agent IDs, sorted by priority and performance
        """
        suitable = []
        
        for agent_id, agent_info in self.agents.items():
            # Check if agent has required capabilities
            if required_capabilities:
                agent_caps = set(agent_info.get('capabilities', []))
                required_caps = set(required_capabilities)
                if not required_caps.issubset(agent_caps):
                    continue
            
            # Check if agent is available
            if agent_info.get('status') not in ['idle', 'available']:
                continue
                
            suitable.append(agent_id)
        
        # Sort by priority and performance
        suitable.sort(key=lambda aid: (
            -self.agents[aid].get('priority', 1),
            -self.agent_performance[aid]['success_rate']
        ))
        
        return suitable
        
    async def _execute_with_agents(self, task: Dict[str, Any], agent_ids: List[str]) -> Dict[str, Any]:
        """
        Execute task with multiple agents in parallel or sequentially based on task requirements.
        
        Args:
            task: Task to execute
            agent_ids: List of agent IDs to use
            
        Returns:
            Dictionary of agent results
        """
        execution_mode = task.get('execution_mode', 'parallel')
        results = {}
        
        if execution_mode == 'parallel':
            # Execute with all agents in parallel
            tasks = [self._execute_with_single_agent(task, agent_id) for agent_id in agent_ids]
            agent_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for agent_id, result in zip(agent_ids, agent_results):
                if isinstance(result, Exception):
                    results[agent_id] = {'error': str(result), 'success': False}
                else:
                    results[agent_id] = result
                    
        elif execution_mode == 'sequential':
            # Execute with agents sequentially, passing results forward
            previous_result = None
            for agent_id in agent_ids:
                task_with_context = {**task, 'previous_result': previous_result}
                result = await self._execute_with_single_agent(task_with_context, agent_id)
                results[agent_id] = result
                previous_result = result
                
        elif execution_mode == 'best_of':
            # Execute with the highest priority agent only
            if agent_ids:
                result = await self._execute_with_single_agent(task, agent_ids[0])
                results[agent_ids[0]] = result
        
        return results
        
    async def _execute_with_single_agent(self, task: Dict[str, Any], agent_id: str) -> Dict[str, Any]:
        """
        Execute task with a single agent.
        
        Args:
            task: Task to execute
            agent_id: Agent ID
            
        Returns:
            Agent result dictionary
        """
        start_time = datetime.now()
        
        try:
            # Update agent status
            self.agents[agent_id]['status'] = 'busy'
            
            # Simulate agent execution (in real implementation, this would call the actual agent)
            # For now, we'll create a placeholder result
            await asyncio.sleep(0.1)  # Simulate processing time
            
            result = {
                'agent_id': agent_id,
                'success': True,
                'output': f"Agent {agent_id} processed task successfully",
                'confidence': 0.85,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Agent {agent_id} failed to execute task: {str(e)}")
            return {
                'agent_id': agent_id,
                'success': False,
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            
        finally:
            # Reset agent status
            self.agents[agent_id]['status'] = 'idle'
            
    def _synthesize_decision(self, agent_results: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize final decision from multiple agent results using advanced aggregation.
        
        Args:
            agent_results: Dictionary of agent results
            task: Original task
            
        Returns:
            Final decision dictionary
        """
        successful_results = [r for r in agent_results.values() if r.get('success', False)]
        
        if not successful_results:
            return {
                'decision': 'failed',
                'reason': 'All agents failed to complete the task',
                'confidence': 0.0
            }
        
        # Calculate weighted consensus
        total_confidence = sum(r.get('confidence', 0.5) for r in successful_results)
        avg_confidence = total_confidence / len(successful_results) if successful_results else 0.0
        
        # Aggregate outputs
        outputs = [r.get('output', '') for r in successful_results]
        
        # For now, use majority voting or highest confidence result
        best_result = max(successful_results, key=lambda r: r.get('confidence', 0.0))
        
        return {
            'decision': 'approved',
            'output': best_result.get('output'),
            'confidence': avg_confidence,
            'agent_count': len(successful_results),
            'consensus_strength': avg_confidence
        }
        
    def _record_task(self, task_id: str, task: Dict[str, Any], agent_results: Dict[str, Any], decision: Dict[str, Any]) -> None:
        """Record task execution in history."""
        record = {
            'task_id': task_id,
            'task': task,
            'agent_results': agent_results,
            'decision': decision,
            'timestamp': datetime.now().isoformat()
        }
        
        self.task_history.append(record)
        
        # Store in Redis for persistence
        try:
            self.redis.set(f"task_history:{task_id}", json.dumps(record))
        except Exception as e:
            logger.error(f"Failed to store task history in Redis: {str(e)}")
            
    def _update_agent_performance(self, agent_results: Dict[str, Any]) -> None:
        """Update agent performance metrics based on task results."""
        for agent_id, result in agent_results.items():
            perf = self.agent_performance[agent_id]
            perf['total_tasks'] += 1
            
            if result.get('success', False):
                perf['successful_tasks'] += 1
                
            perf['success_rate'] = perf['successful_tasks'] / perf['total_tasks']
            
            # Update average response time
            processing_time = result.get('processing_time', 0.0)
            if perf['avg_response_time'] == 0.0:
                perf['avg_response_time'] = processing_time
            else:
                perf['avg_response_time'] = (perf['avg_response_time'] * 0.9) + (processing_time * 0.1)
                
    def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of one or all agents."""
        if agent_id:
            return self.agents.get(agent_id, {})
        return self.agents
        
    def get_agent_performance(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics for one or all agents."""
        if agent_id:
            return dict(self.agent_performance.get(agent_id, {}))
        return {aid: dict(perf) for aid, perf in self.agent_performance.items()}
        
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task history."""
        return self.task_history[-limit:]
        
    async def optimize_agent_allocation(self) -> Dict[str, Any]:
        """
        Analyze agent performance and optimize task allocation strategies.
        
        Returns:
            Optimization recommendations
        """
        recommendations = []
        
        # Analyze agent performance
        for agent_id, perf in self.agent_performance.items():
            if perf['total_tasks'] > 10:  # Only analyze agents with sufficient data
                if perf['success_rate'] < 0.7:
                    recommendations.append({
                        'agent_id': agent_id,
                        'issue': 'low_success_rate',
                        'current_rate': perf['success_rate'],
                        'recommendation': 'Review agent configuration or reduce task complexity'
                    })
                    
                if perf['avg_response_time'] > 5.0:
                    recommendations.append({
                        'agent_id': agent_id,
                        'issue': 'slow_response',
                        'avg_time': perf['avg_response_time'],
                        'recommendation': 'Optimize agent processing or increase resources'
                    })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_agents': len(self.agents),
            'recommendations': recommendations,
            'overall_health': 'good' if len(recommendations) == 0 else 'needs_attention'
        }
