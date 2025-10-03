#!/usr/bin/env python3
"""
🧠 ADVANCED SELF-CORRECTION AND LEARNING SYSTEM
⚡ GODMODE: Recursive self-optimization with machine learning
🎯 Mission: Continuously learn, adapt, and improve error resolution capabilities
🚀 Features: Pattern learning, success tracking, predictive fixing, auto-optimization
"""

import asyncio
import json
import logging
import platform
import os
import pickle
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

from aiosqlite import connect as aio_connect

# Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DB_PATH = os.getenv('LEARNING_DB_PATH', 'godmode-learning.db')

# Setup logging

# Ensure UTF-8 encoding for stdout on Windows to support emoji logging
if platform.system() == 'Windows':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='🧠 [LEARNING-v2] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/advanced-self-correction.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FixStrategy(Enum):
    """Fix strategy types"""
    DIRECT = "direct"  # Direct command execution
    ITERATIVE = "iterative"  # Multiple attempts with variations
    COLLABORATIVE = "collaborative"  # Requires multiple agents
    PREVENTIVE = "preventive"  # Prevents future occurrences


@dataclass
class ErrorPattern:
    """Learned error pattern"""
    pattern_id: str
    error_signature: str
    category: str
    frequency: int = 0
    successful_fixes: List[str] = field(default_factory=list)
    failed_fixes: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    last_seen: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FixAttempt:
    """Fix attempt record"""
    attempt_id: str
    error_signature: str
    fix_command: str
    strategy: FixStrategy
    success: bool
    execution_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningMetrics:
    """System learning metrics"""
    total_errors_encountered: int = 0
    total_fixes_attempted: int = 0
    total_fixes_successful: int = 0
    overall_success_rate: float = 0.0
    patterns_learned: int = 0
    avg_fix_time: float = 0.0
    improvement_rate: float = 0.0


class AdvancedSelfCorrectionSystem:
    """
    Advanced self-correction system with machine learning capabilities
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.db_path = self.project_root / DB_PATH
        
        # Database connection
        self.db: Optional[Any] = None
        
        # In-memory learning state
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.fix_attempts: List[FixAttempt] = []
        self.learning_metrics = LearningMetrics()
        
        # Pattern matching cache
        self.pattern_cache: Dict[str, str] = {}
        
        # Running state
        self.running = False
        
        logger.info("🚀 ADVANCED SELF-CORRECTION SYSTEM INITIALIZED")
    
    async def initialize(self):
        """Initialize the learning system"""
        try:
            # Initialize database
            await self._init_database()
            
            # Load learned patterns
            await self._load_learned_patterns()
            
            # Load metrics
            await self._load_metrics()
            
            logger.info("✅ Advanced Self-Correction System initialized")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def _init_database(self):
        """Initialize SQLite database for learning"""
        self.db = await aio_connect(str(self.db_path))
        
        # Error patterns table
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS error_patterns (
                pattern_id TEXT PRIMARY KEY,
                error_signature TEXT NOT NULL,
                category TEXT,
                frequency INTEGER DEFAULT 0,
                successful_fixes TEXT,
                failed_fixes TEXT,
                success_rate REAL DEFAULT 0.0,
                last_seen TEXT,
                metadata TEXT
            )
        ''')
        
        # Fix attempts table
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS fix_attempts (
                attempt_id TEXT PRIMARY KEY,
                error_signature TEXT NOT NULL,
                fix_command TEXT NOT NULL,
                strategy TEXT NOT NULL,
                success INTEGER NOT NULL,
                execution_time REAL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Learning metrics table
        await self.db.execute('''
            CREATE TABLE IF NOT EXISTS learning_metrics (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_errors_encountered INTEGER DEFAULT 0,
                total_fixes_attempted INTEGER DEFAULT 0,
                total_fixes_successful INTEGER DEFAULT 0,
                overall_success_rate REAL DEFAULT 0.0,
                patterns_learned INTEGER DEFAULT 0,
                avg_fix_time REAL DEFAULT 0.0,
                improvement_rate REAL DEFAULT 0.0,
                last_updated TEXT
            )
        ''')
        
        await self.db.commit()
        logger.info("📊 Learning database initialized")
    
    async def _load_learned_patterns(self):
        """Load previously learned error patterns"""
        try:
            async with self.db.execute('SELECT * FROM error_patterns') as cursor:
                async for row in cursor:
                    pattern_id = row[0]
                    self.error_patterns[pattern_id] = ErrorPattern(
                        pattern_id=pattern_id,
                        error_signature=row[1],
                        category=row[2],
                        frequency=row[3],
                        successful_fixes=json.loads(row[4]) if row[4] else [],
                        failed_fixes=json.loads(row[5]) if row[5] else [],
                        success_rate=row[6],
                        last_seen=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
                        metadata=json.loads(row[8]) if row[8] else {}
                    )
            
            logger.info(f"✅ Loaded {len(self.error_patterns)} learned error patterns")
            
        except Exception as e:
            logger.error(f"❌ Error loading patterns: {e}")
    
    async def _load_metrics(self):
        """Load learning metrics"""
        try:
            async with self.db.execute('SELECT * FROM learning_metrics WHERE id = 1') as cursor:
                row = await cursor.fetchone()
                
                if row:
                    self.learning_metrics = LearningMetrics(
                        total_errors_encountered=row[1],
                        total_fixes_attempted=row[2],
                        total_fixes_successful=row[3],
                        overall_success_rate=row[4],
                        patterns_learned=row[5],
                        avg_fix_time=row[6],
                        improvement_rate=row[7]
                    )
            
            logger.info(f"✅ Loaded learning metrics: {self.learning_metrics.overall_success_rate:.1%} success rate")
            
        except Exception as e:
            logger.error(f"❌ Error loading metrics: {e}")
    
    def generate_error_signature(self, error: Dict[str, Any]) -> str:
        """Generate a unique signature for an error"""
        # Extract key components
        error_type = error.get('source', 'unknown')
        message = error.get('message', '').lower()
        
        # Normalize message (remove specific values like paths, numbers)
        import re
        normalized = re.sub(r'/[^\s]+', '<path>', message)
        normalized = re.sub(r'\d+', '<num>', normalized)
        normalized = re.sub(r'[a-f0-9]{8,}', '<hash>', normalized)
        
        # Create signature
        signature = f"{error_type}:{normalized[:200]}"
        return signature
    
    async def learn_from_error(self, error: Dict[str, Any]):
        """Learn from a new error encounter"""
        try:
            signature = self.generate_error_signature(error)
            
            # Update or create pattern
            if signature in self.error_patterns:
                pattern = self.error_patterns[signature]
                pattern.frequency += 1
                pattern.last_seen = datetime.now()
            else:
                pattern_id = f"pattern_{int(datetime.now().timestamp() * 1000)}"
                pattern = ErrorPattern(
                    pattern_id=pattern_id,
                    error_signature=signature,
                    category=error.get('source', 'unknown'),
                    frequency=1
                )
                self.error_patterns[signature] = pattern
                self.learning_metrics.patterns_learned += 1
            
            # Update metrics
            self.learning_metrics.total_errors_encountered += 1
            
            # Persist to database
            await self.db.execute('''
                INSERT OR REPLACE INTO error_patterns 
                (pattern_id, error_signature, category, frequency, successful_fixes, 
                 failed_fixes, success_rate, last_seen, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id, pattern.error_signature, pattern.category,
                pattern.frequency, json.dumps(pattern.successful_fixes),
                json.dumps(pattern.failed_fixes), pattern.success_rate,
                pattern.last_seen.isoformat(), json.dumps(pattern.metadata)
            ))
            await self.db.commit()
            
            logger.info(f"📚 Learned from error: {signature[:50]}... (frequency: {pattern.frequency})")
            
        except Exception as e:
            logger.error(f"❌ Error learning from error: {e}")
    
    async def predict_fix(self, error: Dict[str, Any]) -> Optional[Tuple[str, float]]:
        """Predict the best fix for an error based on learned patterns"""
        try:
            signature = self.generate_error_signature(error)
            
            # Check if we've seen this pattern before
            if signature in self.error_patterns:
                pattern = self.error_patterns[signature]
                
                # Return the most successful fix
                if pattern.successful_fixes:
                    best_fix = pattern.successful_fixes[0]
                    confidence = pattern.success_rate
                    
                    logger.info(f"🎯 Predicted fix with {confidence:.1%} confidence")
                    return (best_fix, confidence)
            
            # Check for similar patterns
            similar_pattern = await self._find_similar_pattern(signature)
            if similar_pattern:
                if similar_pattern.successful_fixes:
                    best_fix = similar_pattern.successful_fixes[0]
                    confidence = similar_pattern.success_rate * 0.7  # Reduce confidence for similar patterns
                    
                    logger.info(f"🎯 Predicted fix from similar pattern with {confidence:.1%} confidence")
                    return (best_fix, confidence)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error predicting fix: {e}")
            return None
    
    async def _find_similar_pattern(self, signature: str) -> Optional[ErrorPattern]:
        """Find a similar error pattern"""
        # Simple similarity check based on common words
        words = set(signature.split())
        
        best_match = None
        best_similarity = 0.0
        
        for pattern_sig, pattern in self.error_patterns.items():
            pattern_words = set(pattern_sig.split())
            
            # Calculate Jaccard similarity
            intersection = len(words & pattern_words)
            union = len(words | pattern_words)
            
            if union > 0:
                similarity = intersection / union
                
                if similarity > best_similarity and similarity > 0.5:
                    best_similarity = similarity
                    best_match = pattern
        
        return best_match
    
    async def record_fix_attempt(
        self,
        error: Dict[str, Any],
        fix_command: str,
        strategy: FixStrategy,
        success: bool,
        execution_time: float
    ):
        """Record a fix attempt for learning"""
        try:
            signature = self.generate_error_signature(error)
            attempt_id = f"attempt_{int(datetime.now().timestamp() * 1000)}"
            
            attempt = FixAttempt(
                attempt_id=attempt_id,
                error_signature=signature,
                fix_command=fix_command,
                strategy=strategy,
                success=success,
                execution_time=execution_time
            )
            
            self.fix_attempts.append(attempt)
            
            # Update pattern
            if signature in self.error_patterns:
                pattern = self.error_patterns[signature]
                
                if success:
                    if fix_command not in pattern.successful_fixes:
                        pattern.successful_fixes.insert(0, fix_command)
                    # Remove from failed if it was there
                    if fix_command in pattern.failed_fixes:
                        pattern.failed_fixes.remove(fix_command)
                else:
                    if fix_command not in pattern.failed_fixes:
                        pattern.failed_fixes.append(fix_command)
                
                # Update success rate
                total_attempts = len(pattern.successful_fixes) + len(pattern.failed_fixes)
                pattern.success_rate = len(pattern.successful_fixes) / total_attempts if total_attempts > 0 else 0.0
                
                # Persist pattern update
                await self.db.execute('''
                    UPDATE error_patterns 
                    SET successful_fixes = ?, failed_fixes = ?, success_rate = ?
                    WHERE pattern_id = ?
                ''', (
                    json.dumps(pattern.successful_fixes),
                    json.dumps(pattern.failed_fixes),
                    pattern.success_rate,
                    pattern.pattern_id
                ))
            
            # Update metrics
            self.learning_metrics.total_fixes_attempted += 1
            if success:
                self.learning_metrics.total_fixes_successful += 1
            
            if self.learning_metrics.total_fixes_attempted > 0:
                self.learning_metrics.overall_success_rate = (
                    self.learning_metrics.total_fixes_successful / 
                    self.learning_metrics.total_fixes_attempted
                )
            
            # Update average fix time
            total_time = sum(a.execution_time for a in self.fix_attempts)
            self.learning_metrics.avg_fix_time = total_time / len(self.fix_attempts)
            
            # Persist fix attempt
            await self.db.execute('''
                INSERT INTO fix_attempts 
                (attempt_id, error_signature, fix_command, strategy, success, 
                 execution_time, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                attempt_id, signature, fix_command, strategy.value,
                1 if success else 0, execution_time, attempt.timestamp.isoformat(),
                json.dumps(attempt.metadata)
            ))
            
            # Persist metrics
            await self.db.execute('''
                INSERT OR REPLACE INTO learning_metrics 
                (id, total_errors_encountered, total_fixes_attempted, total_fixes_successful,
                 overall_success_rate, patterns_learned, avg_fix_time, improvement_rate, last_updated)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.learning_metrics.total_errors_encountered,
                self.learning_metrics.total_fixes_attempted,
                self.learning_metrics.total_fixes_successful,
                self.learning_metrics.overall_success_rate,
                self.learning_metrics.patterns_learned,
                self.learning_metrics.avg_fix_time,
                self.learning_metrics.improvement_rate,
                datetime.now().isoformat()
            ))
            
            await self.db.commit()
            
            logger.info(f"📝 Recorded fix attempt: {'✅ SUCCESS' if success else '❌ FAILED'}")
            
        except Exception as e:
            logger.error(f"❌ Error recording fix attempt: {e}")
    
    async def calculate_improvement_rate(self):
        """Calculate the system's improvement rate over time"""
        try:
            # Get recent attempts (last 24 hours)
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_attempts = [a for a in self.fix_attempts if a.timestamp > recent_cutoff]
            
            if len(recent_attempts) < 10:
                return
            
            # Calculate success rate for recent attempts
            recent_successes = sum(1 for a in recent_attempts if a.success)
            recent_rate = recent_successes / len(recent_attempts)
            
            # Compare with overall rate
            if self.learning_metrics.overall_success_rate > 0:
                improvement = (recent_rate - self.learning_metrics.overall_success_rate) / self.learning_metrics.overall_success_rate
                self.learning_metrics.improvement_rate = improvement
                
                logger.info(f"📈 Improvement rate: {improvement:+.1%}")
            
        except Exception as e:
            logger.error(f"❌ Error calculating improvement rate: {e}")
    
    async def get_learning_report(self) -> Dict[str, Any]:
        """Generate a learning report"""
        return {
            'total_errors_encountered': self.learning_metrics.total_errors_encountered,
            'total_fixes_attempted': self.learning_metrics.total_fixes_attempted,
            'total_fixes_successful': self.learning_metrics.total_fixes_successful,
            'overall_success_rate': f"{self.learning_metrics.overall_success_rate:.1%}",
            'patterns_learned': self.learning_metrics.patterns_learned,
            'avg_fix_time': f"{self.learning_metrics.avg_fix_time:.2f}s",
            'improvement_rate': f"{self.learning_metrics.improvement_rate:+.1%}",
            'top_patterns': await self._get_top_patterns(5)
        }
    
    async def _get_top_patterns(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top error patterns by frequency"""
        sorted_patterns = sorted(
            self.error_patterns.values(),
            key=lambda p: p.frequency,
            reverse=True
        )[:limit]
        
        return [
            {
                'signature': p.error_signature[:100],
                'frequency': p.frequency,
                'success_rate': f"{p.success_rate:.1%}",
                'category': p.category
            }
            for p in sorted_patterns
        ]
    
    async def shutdown(self):
        """Gracefully shutdown"""
        logger.info("🛑 Shutting down Advanced Self-Correction System...")
        
        if self.db:
            await self.db.close()
        
        logger.info("✅ Shutdown complete")


# Main entry point
async def main():
    project_root = Path(__file__).parent.parent
    system = AdvancedSelfCorrectionSystem(project_root)
    await system.initialize()
    
    # Example usage
    report = await system.get_learning_report()
    logger.info(f"📊 Learning Report: {json.dumps(report, indent=2)}")
    
    await system.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
