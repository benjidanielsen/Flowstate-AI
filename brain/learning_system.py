"""
Learning System for Flowstate-AI
Enables continuous learning and improvement of AI agents through experience and feedback.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import redis
import numpy as np
from .error_handler import with_retry, with_error_handling, default_fallback_value

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LearningSystem:
    """
    Advanced learning system that enables AI agents to learn from experience,
    adapt to new patterns, and continuously improve their performance.
    """
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize the learning system."""
        self.redis = redis_client
        self.learning_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.patterns: Dict[str, Any] = {}
        self.feedback_history: List[Dict[str, Any]] = []
        
    @with_error_handling(fallback=default_fallback_value)
    @with_retry(expected_exception=redis.exceptions.ConnectionError)
    def record_experience(self, agent_id: str, experience: Dict[str, Any]) -> None:

        """
        Record an experience for an agent to learn from.
        
        Args:
            agent_id: Agent identifier
            experience: Dictionary containing task, action, result, and feedback
        """
        experience_record = {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'task_type': experience.get('task_type'),
            'action_taken': experience.get('action'),
            'result': experience.get('result'),
            'success': experience.get('success', False),
            'feedback_score': experience.get('feedback_score', 0.0),
            'context': experience.get('context', {})
        }
        
        self.learning_data[agent_id].append(experience_record)
        
        # Store in Redis for persistence
        try:
            key = f"learning:experience:{agent_id}:{datetime.now().timestamp()}"
            self.redis.set(key, json.dumps(experience_record))
            self.redis.expire(key, 86400 * 30)  # Keep for 30 days
        except Exception as e:
            logger.error(f"Failed to store experience in Redis: {str(e)}")
            
        logger.info(f"Recorded experience for agent {agent_id}")
        
    @with_error_handling(fallback=default_fallback_value)
    def analyze_patterns(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze patterns in agent experiences to identify successful strategies.
        
        Args:
            agent_id: Optional agent ID to analyze specific agent, or None for all agents
            
        Returns:
            Dictionary of identified patterns and insights
        """
        if agent_id:
            experiences = self.learning_data.get(agent_id, [])
        else:
            experiences = []
            for agent_experiences in self.learning_data.values():
                experiences.extend(agent_experiences)
        
        if not experiences:
            return {'patterns': [], 'message': 'No experiences to analyze'}
        
        # Analyze success patterns
        successful_experiences = [e for e in experiences if e.get('success', False)]
        failed_experiences = [e for e in experiences if not e.get('success', False)]
        
        # Calculate success rate by task type
        task_type_success = defaultdict(lambda: {'total': 0, 'successful': 0})
        for exp in experiences:
            task_type = exp.get('task_type', 'unknown')
            task_type_success[task_type]['total'] += 1
            if exp.get('success', False):
                task_type_success[task_type]['successful'] += 1
        
        success_rates = {
            task_type: stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            for task_type, stats in task_type_success.items()
        }
        
        # Identify common patterns in successful experiences
        successful_actions = defaultdict(int)
        for exp in successful_experiences:
            action = exp.get('action_taken', 'unknown')
            successful_actions[action] += 1
        
        # Identify common patterns in failed experiences
        failed_actions = defaultdict(int)
        for exp in failed_experiences:
            action = exp.get('action_taken', 'unknown')
            failed_actions[action] += 1
        
        patterns = {
            'total_experiences': len(experiences),
            'successful_experiences': len(successful_experiences),
            'failed_experiences': len(failed_experiences),
            'overall_success_rate': len(successful_experiences) / len(experiences) if experiences else 0,
            'success_rates_by_task_type': success_rates,
            'most_successful_actions': dict(sorted(successful_actions.items(), key=lambda x: x[1], reverse=True)[:5]),
            'most_failed_actions': dict(sorted(failed_actions.items(), key=lambda x: x[1], reverse=True)[:5]),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Store patterns
        if agent_id:
            self.patterns[agent_id] = patterns
        else:
            self.patterns['global'] = patterns
        
        return patterns
        
    @with_error_handling(fallback=default_fallback_value)
    def get_recommendations(self, agent_id: str, task_type: str) -> Dict[str, Any]:
        """
        Get recommendations for an agent based on learned patterns.
        
        Args:
            agent_id: Agent identifier
            task_type: Type of task to get recommendations for
            
        Returns:
            Dictionary of recommendations
        """
        # Analyze agent-specific patterns
        agent_patterns = self.analyze_patterns(agent_id)
        
        # Get success rate for this task type
        task_success_rate = agent_patterns.get('success_rates_by_task_type', {}).get(task_type, 0.0)
        
        # Get most successful actions
        successful_actions = agent_patterns.get('most_successful_actions', {})
        
        recommendations = {
            'agent_id': agent_id,
            'task_type': task_type,
            'current_success_rate': task_success_rate,
            'recommended_actions': list(successful_actions.keys())[:3],
            'confidence': min(task_success_rate + 0.1, 1.0),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add specific recommendations based on success rate
        if task_success_rate < 0.5:
            recommendations['advice'] = 'Consider alternative approaches or request human guidance'
        elif task_success_rate < 0.7:
            recommendations['advice'] = 'Continue current approach but monitor closely'
        else:
            recommendations['advice'] = 'Current approach is effective, maintain strategy'
        
        return recommendations
        
    @with_error_handling(fallback=default_fallback_value)
    @with_retry(expected_exception=redis.exceptions.ConnectionError)
    def record_feedback(self, task_id: str, feedback: Dict[str, Any]) -> None:
        """
        Record feedback on a completed task for learning purposes.
        
        Args:
            task_id: Task identifier
            feedback: Feedback dictionary with score, comments, etc.
        """
        feedback_record = {
            'task_id': task_id,
            'timestamp': datetime.now().isoformat(),
            'score': feedback.get('score', 0.0),
            'positive_aspects': feedback.get('positive', []),
            'negative_aspects': feedback.get('negative', []),
            'suggestions': feedback.get('suggestions', []),
            'user_satisfaction': feedback.get('satisfaction', 'neutral')
        }
        
        self.feedback_history.append(feedback_record)
        
        # Store in Redis
        try:
            key = f"learning:feedback:{task_id}"
            self.redis.set(key, json.dumps(feedback_record))
            self.redis.expire(key, 86400 * 90)  # Keep for 90 days
        except Exception as e:
            logger.error(f"Failed to store feedback in Redis: {str(e)}")
            
        logger.info(f"Recorded feedback for task {task_id}")
        
    @with_error_handling(fallback=default_fallback_value)
    def get_learning_progress(self, agent_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get learning progress for an agent over a specified period.
        
        Args:
            agent_id: Agent identifier
            days: Number of days to analyze
            
        Returns:
            Dictionary with learning progress metrics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get experiences within the time window
        experiences = [
            exp for exp in self.learning_data.get(agent_id, [])
            if datetime.fromisoformat(exp['timestamp']) >= cutoff_date
        ]
        
        if not experiences:
            return {
                'agent_id': agent_id,
                'message': f'No experiences in the last {days} days',
                'progress': 'insufficient_data'
            }
        
        # Calculate success rate over time (weekly buckets)
        weekly_success = defaultdict(lambda: {'total': 0, 'successful': 0})
        
        for exp in experiences:
            exp_date = datetime.fromisoformat(exp['timestamp'])
            week_key = exp_date.strftime('%Y-W%W')
            weekly_success[week_key]['total'] += 1
            if exp.get('success', False):
                weekly_success[week_key]['successful'] += 1
        
        # Calculate success rate trend
        weekly_rates = []
        for week in sorted(weekly_success.keys()):
            stats = weekly_success[week]
            rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            weekly_rates.append(rate)
        
        # Calculate trend (improving, stable, or declining)
        if len(weekly_rates) >= 2:
            recent_avg = np.mean(weekly_rates[-2:]) if len(weekly_rates) >= 2 else weekly_rates[-1]
            earlier_avg = np.mean(weekly_rates[:2]) if len(weekly_rates) >= 2 else weekly_rates[0]
            
            if recent_avg > earlier_avg + 0.1:
                trend = 'improving'
            elif recent_avg < earlier_avg - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'agent_id': agent_id,
            'period_days': days,
            'total_experiences': len(experiences),
            'current_success_rate': weekly_rates[-1] if weekly_rates else 0.0,
            'average_success_rate': np.mean(weekly_rates) if weekly_rates else 0.0,
            'trend': trend,
            'weekly_success_rates': dict(zip(sorted(weekly_success.keys()), weekly_rates)),
            'timestamp': datetime.now().isoformat()
        }
        
    @with_error_handling(fallback=default_fallback_value)
    def export_learning_data(self, agent_id: Optional[str] = None, format: str = 'json') -> str:

        """
        Export learning data for analysis or backup.
        
        Args:
            agent_id: Optional agent ID to export specific agent data
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported data as string
        """
        if agent_id:
            data = {
                'agent_id': agent_id,
                'experiences': self.learning_data.get(agent_id, []),
                'patterns': self.patterns.get(agent_id, {}),
                'export_timestamp': datetime.now().isoformat()
            }
        else:
            data = {
                'all_agents': dict(self.learning_data),
                'patterns': self.patterns,
                'feedback_history': self.feedback_history,
                'export_timestamp': datetime.now().isoformat()
            }
        
        if format == 'json':
            return json.dumps(data, indent=2)
        elif format == 'csv':
            # Simplified CSV export (would need more complex implementation for full data)
            return "CSV export not yet implemented"
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
    @with_error_handling(fallback=default_fallback_value)
    def reset_learning_data(self, agent_id: Optional[str] = None) -> None:
        """
        Reset learning data for an agent or all agents.
        
        Args:
            agent_id: Optional agent ID to reset specific agent, or None for all
        """
        if agent_id:
            self.learning_data[agent_id] = []
            if agent_id in self.patterns:
                del self.patterns[agent_id]
            logger.info(f"Reset learning data for agent {agent_id}")
        else:
            self.learning_data.clear()
            self.patterns.clear()
            self.feedback_history.clear()
            logger.info("Reset all learning data")
            
    @with_error_handling(fallback=default_fallback_value)
    def get_insights(self) -> Dict[str, Any]:
        """
        Get high-level insights from all learning data.
        
        Returns:
            Dictionary of insights and recommendations
        """
        all_experiences = []
        for agent_experiences in self.learning_data.values():
            all_experiences.extend(agent_experiences)
        
        if not all_experiences:
            return {'message': 'No learning data available'}
        
        # Calculate overall metrics
        total_experiences = len(all_experiences)
        successful_experiences = sum(1 for e in all_experiences if e.get('success', False))
        overall_success_rate = successful_experiences / total_experiences if total_experiences > 0 else 0
        
        # Identify top performing agents
        agent_performance = {}
        for agent_id, experiences in self.learning_data.items():
            if experiences:
                success_count = sum(1 for e in experiences if e.get('success', False))
                agent_performance[agent_id] = success_count / len(experiences)
        
        top_agents = sorted(agent_performance.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Identify areas for improvement
        task_type_performance = defaultdict(lambda: {'total': 0, 'successful': 0})
        for exp in all_experiences:
            task_type = exp.get('task_type', 'unknown')
            task_type_performance[task_type]['total'] += 1
            if exp.get('success', False):
                task_type_performance[task_type]['successful'] += 1
        
        weak_areas = []
        for task_type, stats in task_type_performance.items():
            success_rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            if success_rate < 0.6 and stats['total'] >= 5:  # Only consider tasks with sufficient data
                weak_areas.append({
                    'task_type': task_type,
                    'success_rate': success_rate,
                    'total_attempts': stats['total']
                })
        
        return {
            'total_experiences': total_experiences,
            'overall_success_rate': round(overall_success_rate, 3),
            'top_performing_agents': [{'agent_id': aid, 'success_rate': round(rate, 3)} for aid, rate in top_agents],
            'areas_for_improvement': weak_areas,
            'total_agents_learning': len(self.learning_data),
            'timestamp': datetime.now().isoformat()
        }
