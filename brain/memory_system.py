#!/usr/bin/env python3
"""
🧠 MEMORY SYSTEM
⚡ Collective memory for the AI system - learns from past experiences
🎯 Mission: Remember everything, learn continuously, improve over time
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MemorySystem')

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"
MEMORY_FILE = PROJECT_ROOT / "collective-memory" / "system_memory.json"

class MemorySystem:
    """Collective memory system for the AI agents"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.memory_file = MEMORY_FILE
        self.memory_file.parent.mkdir(exist_ok=True)
        self.short_term_memory = {}
        self.long_term_memory = self._load_long_term_memory()
        
    def _load_long_term_memory(self) -> Dict:
        """Load long-term memory from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load memory file: {e}")
        
        return {
            'patterns': [],
            'best_practices': [],
            'common_errors': [],
            'successful_approaches': [],
            'agent_performance': {},
            'task_statistics': {},
            'learned_at': datetime.now().isoformat()
        }
    
    def _save_long_term_memory(self):
        """Save long-term memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.long_term_memory, f, indent=2)
            logger.info("💾 Long-term memory saved")
        except Exception as e:
            logger.error(f"❌ Failed to save memory: {e}")
    
    def remember_task_outcome(self, task_id: int, success: bool, details: Dict):
        """Remember the outcome of a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store in database
        cursor.execute('''
            INSERT INTO system_learnings (task_id, success, feedback, learned_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (task_id, 1 if success else 0, json.dumps(details)))
        
        conn.commit()
        conn.close()
        
        # Update statistics
        if 'task_statistics' not in self.long_term_memory:
            self.long_term_memory['task_statistics'] = {}
        
        stats = self.long_term_memory['task_statistics']
        stats['total_tasks'] = stats.get('total_tasks', 0) + 1
        stats['successful_tasks'] = stats.get('successful_tasks', 0) + (1 if success else 0)
        stats['failed_tasks'] = stats.get('failed_tasks', 0) + (0 if success else 1)
        stats['success_rate'] = stats['successful_tasks'] / stats['total_tasks']
        
        self._save_long_term_memory()
        
        logger.info(f"📝 Remembered task #{task_id} outcome: {'success' if success else 'failure'}")
    
    def learn_pattern(self, pattern: Dict):
        """Learn a new pattern from observations"""
        if 'patterns' not in self.long_term_memory:
            self.long_term_memory['patterns'] = []
        
        pattern['learned_at'] = datetime.now().isoformat()
        pattern['confidence'] = pattern.get('confidence', 0.5)
        
        # Check if pattern already exists
        existing = next((p for p in self.long_term_memory['patterns'] 
                        if p.get('name') == pattern.get('name')), None)
        
        if existing:
            # Increase confidence if pattern repeats
            existing['confidence'] = min(existing['confidence'] + 0.1, 1.0)
            existing['occurrences'] = existing.get('occurrences', 1) + 1
            logger.info(f"🔄 Pattern reinforced: {pattern['name']} (confidence: {existing['confidence']:.2f})")
        else:
            pattern['occurrences'] = 1
            self.long_term_memory['patterns'].append(pattern)
            logger.info(f"✨ New pattern learned: {pattern['name']}")
        
        self._save_long_term_memory()
    
    def remember_best_practice(self, practice: Dict):
        """Remember a best practice"""
        if 'best_practices' not in self.long_term_memory:
            self.long_term_memory['best_practices'] = []
        
        practice['learned_at'] = datetime.now().isoformat()
        self.long_term_memory['best_practices'].append(practice)
        
        self._save_long_term_memory()
        logger.info(f"✅ Best practice remembered: {practice.get('title', 'Untitled')}")
    
    def remember_error(self, error: Dict):
        """Remember a common error to avoid in the future"""
        if 'common_errors' not in self.long_term_memory:
            self.long_term_memory['common_errors'] = []
        
        error['learned_at'] = datetime.now().isoformat()
        error['occurrences'] = 1
        
        # Check if error already exists
        existing = next((e for e in self.long_term_memory['common_errors'] 
                        if e.get('error_type') == error.get('error_type')), None)
        
        if existing:
            existing['occurrences'] += 1
            existing['last_seen'] = datetime.now().isoformat()
            logger.info(f"⚠️  Error seen again: {error['error_type']} (total: {existing['occurrences']})")
        else:
            self.long_term_memory['common_errors'].append(error)
            logger.info(f"❌ New error remembered: {error['error_type']}")
        
        self._save_long_term_memory()
    
    def get_relevant_memories(self, context: str) -> List[Dict]:
        """Retrieve relevant memories based on context"""
        relevant = []
        
        context_lower = context.lower()
        
        # Search patterns
        for pattern in self.long_term_memory.get('patterns', []):
            if any(keyword in context_lower for keyword in pattern.get('keywords', [])):
                relevant.append({
                    'type': 'pattern',
                    'data': pattern,
                    'relevance': pattern.get('confidence', 0.5)
                })
        
        # Search best practices
        for practice in self.long_term_memory.get('best_practices', []):
            if any(keyword in context_lower for keyword in practice.get('keywords', [])):
                relevant.append({
                    'type': 'best_practice',
                    'data': practice,
                    'relevance': 0.8
                })
        
        # Search common errors
        for error in self.long_term_memory.get('common_errors', []):
            if any(keyword in context_lower for keyword in error.get('keywords', [])):
                relevant.append({
                    'type': 'error_to_avoid',
                    'data': error,
                    'relevance': 0.9  # High relevance to avoid repeating errors
                })
        
        # Sort by relevance
        relevant.sort(key=lambda x: x['relevance'], reverse=True)
        
        return relevant
    
    def get_agent_performance(self, agent_name: str) -> Dict:
        """Get performance statistics for an agent"""
        if 'agent_performance' not in self.long_term_memory:
            self.long_term_memory['agent_performance'] = {}
        
        return self.long_term_memory['agent_performance'].get(agent_name, {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'average_duration': 0,
            'success_rate': 0.0
        })
    
    def update_agent_performance(self, agent_name: str, task_success: bool, duration: int):
        """Update performance statistics for an agent"""
        if 'agent_performance' not in self.long_term_memory:
            self.long_term_memory['agent_performance'] = {}
        
        if agent_name not in self.long_term_memory['agent_performance']:
            self.long_term_memory['agent_performance'][agent_name] = {
                'tasks_completed': 0,
                'tasks_failed': 0,
                'total_duration': 0,
                'average_duration': 0,
                'success_rate': 0.0
            }
        
        perf = self.long_term_memory['agent_performance'][agent_name]
        
        if task_success:
            perf['tasks_completed'] += 1
        else:
            perf['tasks_failed'] += 1
        
        perf['total_duration'] += duration
        total_tasks = perf['tasks_completed'] + perf['tasks_failed']
        perf['average_duration'] = perf['total_duration'] / total_tasks
        perf['success_rate'] = perf['tasks_completed'] / total_tasks
        
        self._save_long_term_memory()
        logger.info(f"📊 Updated performance for {agent_name}: {perf['success_rate']:.2%} success rate")
    
    def get_insights(self) -> Dict:
        """Get insights from accumulated memories"""
        insights = {
            'total_patterns': len(self.long_term_memory.get('patterns', [])),
            'total_best_practices': len(self.long_term_memory.get('best_practices', [])),
            'total_errors_seen': len(self.long_term_memory.get('common_errors', [])),
            'task_statistics': self.long_term_memory.get('task_statistics', {}),
            'top_performing_agents': [],
            'most_common_errors': []
        }
        
        # Get top performing agents
        agent_perf = self.long_term_memory.get('agent_performance', {})
        sorted_agents = sorted(agent_perf.items(), 
                             key=lambda x: x[1].get('success_rate', 0), 
                             reverse=True)
        insights['top_performing_agents'] = [
            {'name': name, 'success_rate': perf.get('success_rate', 0)}
            for name, perf in sorted_agents[:5]
        ]
        
        # Get most common errors
        errors = self.long_term_memory.get('common_errors', [])
        sorted_errors = sorted(errors, 
                             key=lambda x: x.get('occurrences', 0), 
                             reverse=True)
        insights['most_common_errors'] = [
            {'type': err.get('error_type'), 'occurrences': err.get('occurrences', 0)}
            for err in sorted_errors[:5]
        ]
        
        return insights
    
    def consolidate_memories(self):
        """Consolidate and clean up old memories"""
        logger.info("🧹 Consolidating memories...")
        
        # Remove patterns with low confidence
        if 'patterns' in self.long_term_memory:
            original_count = len(self.long_term_memory['patterns'])
            self.long_term_memory['patterns'] = [
                p for p in self.long_term_memory['patterns']
                if p.get('confidence', 0) >= 0.3
            ]
            removed = original_count - len(self.long_term_memory['patterns'])
            if removed > 0:
                logger.info(f"🗑️  Removed {removed} low-confidence patterns")
        
        # Keep only recent errors (last 30 days)
        if 'common_errors' in self.long_term_memory:
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            original_count = len(self.long_term_memory['common_errors'])
            self.long_term_memory['common_errors'] = [
                e for e in self.long_term_memory['common_errors']
                if e.get('last_seen', e.get('learned_at', '')) >= cutoff_date
            ]
            removed = original_count - len(self.long_term_memory['common_errors'])
            if removed > 0:
                logger.info(f"🗑️  Removed {removed} old errors")
        
        self._save_long_term_memory()
        logger.info("✅ Memory consolidation complete")

if __name__ == "__main__":
    print("🧠 Memory System")
    print("=" * 60)
    
    memory = MemorySystem()
    
    print("\n📊 Current Insights:")
    insights = memory.get_insights()
    print(json.dumps(insights, indent=2))
    
    print("\n✨ Learning a new pattern...")
    memory.learn_pattern({
        'name': 'Task Completion Pattern',
        'description': 'Tasks with clear descriptions complete faster',
        'keywords': ['task', 'description', 'completion'],
        'confidence': 0.7
    })
    
    print("\n✅ Remembering a best practice...")
    memory.remember_best_practice({
        'title': 'Always validate input data',
        'description': 'Input validation prevents most errors',
        'keywords': ['validation', 'input', 'error prevention']
    })
    
    print("\n🧹 Consolidating memories...")
    memory.consolidate_memories()
    
    print("\n🧠 Memory System operational!")
