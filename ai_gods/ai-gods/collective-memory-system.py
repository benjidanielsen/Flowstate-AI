#!/usr/bin/env python3
"""
🧠 COLLECTIVE MEMORY SYSTEM - The AI Hive Mind
⚡ GODMODE: Unlimited knowledge sharing and cross-domain intelligence
🎯 Mission: Create shared consciousness where all AIs know everything
🔄 Features: Instant knowledge transfer, smart routing, collective learning
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import logging
import uuid
from typing import Dict, List, Any, Optional
import sqlite3
import threading
import queue
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='🧠 [COLLECTIVE-MEMORY] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/collective-memory.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CollectiveMemorySystem:
    """
    Shared consciousness system for all AI agents
    GODMODE: Unlimited knowledge sharing and cross-domain learning
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.godmode_enabled = True
        
        # Memory Database
        self.memory_db_path = self.project_root / "collective-memory" / "hive_mind.db"
        self.memory_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Knowledge Categories
        self.knowledge_domains = {
            "backend": ["typescript", "nodejs", "api", "database", "server", "express", "authentication"],
            "frontend": ["react", "ui", "ux", "components", "styling", "responsive", "javascript"],
            "database": ["sql", "sqlite", "postgresql", "migrations", "queries", "optimization"],
            "testing": ["unit_tests", "integration", "e2e", "jest", "cypress", "quality_assurance"],
            "devops": ["deployment", "docker", "ci_cd", "monitoring", "scaling", "infrastructure"],
            "ai_ml": ["machine_learning", "nlp", "algorithms", "neural_networks", "training"],
            "business": ["frazer_method", "crm", "pipeline", "prospects", "network_marketing"],
            "security": ["authentication", "encryption", "vulnerabilities", "best_practices"],
            "performance": ["optimization", "caching", "load_balancing", "monitoring"],
            "innovation": ["ideas", "features", "improvements", "future_tech", "breakthroughs"]
        }
        
        # AI Expertise Mapping
        self.ai_expertise = {
            "backend-developer": ["backend", "database", "security", "performance"],
            "frontend-developer": ["frontend", "ui_ux", "performance"],
            "database-ai": ["database", "performance", "backend"],
            "tester-ai": ["testing", "security", "performance"],
            "devops-ai": ["devops", "security", "performance"],
            "innovation-ai": ["innovation", "ai_ml", "future_tech"],
            "documentation-ai": ["business", "technical_writing"],
            "support-ai": ["troubleshooting", "setup", "user_support"],
            "project-manager": ["business", "coordination", "planning"]
        }
        
        # Memory Systems
        self.shared_memory = {}
        self.knowledge_graph = {}
        self.learning_history = []
        self.question_routing_system = {}
        
        # Initialize systems
        self.setup_collective_memory()
        
        logger.info("🚀 COLLECTIVE MEMORY SYSTEM INITIALIZED - HIVE MIND ACTIVE")
    
    def setup_collective_memory(self):
        """Setup the collective memory infrastructure"""
        
        # Initialize SQLite database for persistent memory
        self.init_memory_database()
        
        # Create memory directories
        memory_dirs = [
            "collective-memory/knowledge-base",
            "collective-memory/learning-logs",
            "collective-memory/cross-references",
            "collective-memory/question-routing",
            "collective-memory/memory-backups"
        ]
        
        for directory in memory_dirs:
            (self.project_root / directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize knowledge graph
        self.build_initial_knowledge_graph()
        
        logger.info("🧠 Collective memory infrastructure initialized")
    
    def init_memory_database(self):
        """Initialize the collective memory database"""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Create tables for collective memory
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_entries (
                    id TEXT PRIMARY KEY,
                    domain TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_ai TEXT NOT NULL,
                    confidence_score REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    tags TEXT,
                    related_entries TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_events (
                    id TEXT PRIMARY KEY,
                    ai_agent TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    knowledge_gained TEXT NOT NULL,
                    source TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    shared_with TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS question_routing (
                    id TEXT PRIMARY KEY,
                    question_hash TEXT UNIQUE,
                    question_text TEXT NOT NULL,
                    best_ai TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    success_rate REAL DEFAULT 1.0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cross_domain_links (
                    id TEXT PRIMARY KEY,
                    domain_a TEXT NOT NULL,
                    domain_b TEXT NOT NULL,
                    connection_type TEXT NOT NULL,
                    strength REAL DEFAULT 1.0,
                    examples TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("💾 Collective memory database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing memory database: {e}")
    
    def build_initial_knowledge_graph(self):
        """Build initial knowledge graph connecting all domains"""
        
        # Create connections between related domains
        domain_connections = {
            "backend": ["database", "security", "performance", "testing"],
            "frontend": ["backend", "performance", "testing", "ui_ux"],
            "database": ["backend", "performance", "security"],
            "testing": ["backend", "frontend", "security", "performance"],
            "devops": ["backend", "database", "security", "performance"],
            "ai_ml": ["backend", "performance", "innovation"],
            "business": ["backend", "frontend", "ai_ml"],
            "security": ["backend", "database", "devops"],
            "performance": ["backend", "frontend", "database", "devops"],
            "innovation": ["ai_ml", "business", "performance"]
        }
        
        # Store connections in database
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            for domain, connected_domains in domain_connections.items():
                for connected_domain in connected_domains:
                    cursor.execute('''
                        INSERT OR REPLACE INTO cross_domain_links 
                        (id, domain_a, domain_b, connection_type, strength)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        str(uuid.uuid4()),
                        domain,
                        connected_domain,
                        "related_domain",
                        0.8
                    ))
            
            conn.commit()
            conn.close()
            
            logger.info("🕸️ Knowledge graph initialized with cross-domain connections")
            
        except Exception as e:
            logger.error(f"❌ Error building knowledge graph: {e}")
    
    async def start_collective_memory_system(self):
        """Start the collective memory system"""
        logger.info("🎯 Starting Collective Memory System - Hive Mind Active")
        
        # Start all memory processes
        memory_tasks = [
            asyncio.create_task(self.knowledge_sharing_loop()),
            asyncio.create_task(self.cross_domain_learning_loop()),
            asyncio.create_task(self.question_routing_loop()),
            asyncio.create_task(self.memory_consolidation_loop()),
            asyncio.create_task(self.knowledge_graph_updates()),
            asyncio.create_task(self.collective_learning_sync()),
            asyncio.create_task(self.smart_memory_backup()),
            asyncio.create_task(self.context_awareness_system())
        ]
        
        # Run all processes concurrently
        await asyncio.gather(*memory_tasks)
    
    async def knowledge_sharing_loop(self):
        """Continuously share knowledge between AIs"""
        while True:
            try:
                # Check for new knowledge entries from AIs
                knowledge_dir = self.project_root / "collective-memory" / "knowledge-base"
                
                for knowledge_file in knowledge_dir.glob("new_*.json"):
                    try:
                        with open(knowledge_file, 'r') as f:
                            knowledge_entry = json.load(f)
                        
                        # Process and distribute knowledge
                        await self.process_new_knowledge(knowledge_entry)
                        
                        # Archive processed knowledge
                        archive_dir = knowledge_dir / "processed"
                        archive_dir.mkdir(exist_ok=True)
                        knowledge_file.rename(archive_dir / knowledge_file.name)
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing knowledge file {knowledge_file}: {e}")
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in knowledge sharing loop: {e}")
                await asyncio.sleep(30)
    
    async def process_new_knowledge(self, knowledge_entry: Dict):
        """Process and distribute new knowledge to all AIs"""
        try:
            source_ai = knowledge_entry.get("source_ai")
            domain = knowledge_entry.get("domain")
            topic = knowledge_entry.get("topic")
            content = knowledge_entry.get("content")
            
            # Store in collective memory database
            knowledge_id = await self.store_knowledge(knowledge_entry)
            
            # Determine which AIs should receive this knowledge
            target_ais = await self.determine_knowledge_recipients(domain, topic, source_ai)
            
            # Distribute knowledge to target AIs
            for target_ai in target_ais:
                await self.send_knowledge_to_ai(target_ai, knowledge_entry, knowledge_id)
            
            # Update cross-domain connections
            await self.update_cross_domain_connections(domain, topic, content)
            
            logger.info(f"📚 Knowledge '{topic}' from {source_ai} distributed to {len(target_ais)} AIs")
            
        except Exception as e:
            logger.error(f"❌ Error processing new knowledge: {e}")
    
    async def store_knowledge(self, knowledge_entry: Dict) -> str:
        """Store knowledge in collective memory database"""
        try:
            knowledge_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO knowledge_entries 
                (id, domain, topic, content, source_ai, confidence_score, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                knowledge_id,
                knowledge_entry.get("domain", "general"),
                knowledge_entry.get("topic", "unknown"),
                json.dumps(knowledge_entry.get("content", {})),
                knowledge_entry.get("source_ai", "unknown"),
                knowledge_entry.get("confidence_score", 1.0),
                json.dumps(knowledge_entry.get("tags", []))
            ))
            
            conn.commit()
            conn.close()
            
            return knowledge_id
            
        except Exception as e:
            logger.error(f"❌ Error storing knowledge: {e}")
            return ""
    
    async def determine_knowledge_recipients(self, domain: str, topic: str, source_ai: str) -> List[str]:
        """Determine which AIs should receive specific knowledge"""
        try:
            recipients = []
            
            # All AIs get knowledge from their primary domains
            for ai, expertise_domains in self.ai_expertise.items():
                if ai != source_ai:  # Don't send back to source
                    # Direct domain match
                    if domain in expertise_domains:
                        recipients.append(ai)
                    # Cross-domain relevance
                    elif await self.is_cross_domain_relevant(domain, expertise_domains):
                        recipients.append(ai)
            
            # Always include project-manager for coordination
            if "project-manager" not in recipients and source_ai != "project-manager":
                recipients.append("project-manager")
            
            return recipients
            
        except Exception as e:
            logger.error(f"❌ Error determining knowledge recipients: {e}")
            return []
    
    async def is_cross_domain_relevant(self, knowledge_domain: str, ai_domains: List[str]) -> bool:
        """Check if knowledge is relevant across domains"""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            for ai_domain in ai_domains:
                cursor.execute('''
                    SELECT strength FROM cross_domain_links 
                    WHERE (domain_a = ? AND domain_b = ?) OR (domain_a = ? AND domain_b = ?)
                ''', (knowledge_domain, ai_domain, ai_domain, knowledge_domain))
                
                result = cursor.fetchone()
                if result and result[0] > 0.5:  # Strong connection threshold
                    conn.close()
                    return True
            
            conn.close()
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking cross-domain relevance: {e}")
            return False
    
    async def send_knowledge_to_ai(self, target_ai: str, knowledge_entry: Dict, knowledge_id: str):
        """Send knowledge to specific AI agent"""
        try:
            # Create knowledge transfer message
            transfer_message = {
                "type": "knowledge_transfer",
                "knowledge_id": knowledge_id,
                "from_ai": knowledge_entry.get("source_ai"),
                "to_ai": target_ai,
                "domain": knowledge_entry.get("domain"),
                "topic": knowledge_entry.get("topic"),
                "content": knowledge_entry.get("content"),
                "confidence_score": knowledge_entry.get("confidence_score", 1.0),
                "transfer_reason": "collective_learning",
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to AI's knowledge inbox
            inbox_dir = self.project_root / "collective-memory" / "knowledge-base" / target_ai
            inbox_dir.mkdir(parents=True, exist_ok=True)
            
            transfer_file = inbox_dir / f"knowledge_{knowledge_id}.json"
            with open(transfer_file, 'w') as f:
                json.dump(transfer_message, f, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Error sending knowledge to {target_ai}: {e}")
    
    async def cross_domain_learning_loop(self):
        """Enable cross-domain learning between AIs"""
        while True:
            try:
                # Analyze knowledge patterns for cross-domain insights
                await self.analyze_cross_domain_patterns()
                
                # Create cross-domain learning opportunities
                await self.create_cross_domain_connections()
                
                await asyncio.sleep(1800)  # Every 30 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in cross-domain learning: {e}")
                await asyncio.sleep(3600)
    
    async def analyze_cross_domain_patterns(self):
        """Analyze patterns that connect different knowledge domains"""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Find knowledge entries that mention multiple domains
            cursor.execute('''
                SELECT domain, topic, content, tags FROM knowledge_entries
                WHERE created_at > datetime('now', '-24 hours')
            ''')
            
            recent_knowledge = cursor.fetchall()
            
            # Analyze for cross-domain patterns
            cross_patterns = {}
            
            for domain, topic, content_json, tags_json in recent_knowledge:
                try:
                    content = json.loads(content_json)
                    tags = json.loads(tags_json) if tags_json else []
                    
                    # Look for mentions of other domains in content
                    content_text = str(content).lower()
                    
                    for other_domain, keywords in self.knowledge_domains.items():
                        if other_domain != domain:
                            for keyword in keywords:
                                if keyword in content_text:
                                    pattern_key = f"{domain}-{other_domain}"
                                    if pattern_key not in cross_patterns:
                                        cross_patterns[pattern_key] = []
                                    cross_patterns[pattern_key].append({
                                        "topic": topic,
                                        "keyword": keyword,
                                        "content_snippet": content_text[:200]
                                    })
                
                except json.JSONDecodeError:
                    continue
            
            # Store discovered patterns
            for pattern, examples in cross_patterns.items():
                if len(examples) >= 2:  # Pattern needs multiple examples
                    await self.store_cross_domain_pattern(pattern, examples)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error analyzing cross-domain patterns: {e}")
    
    async def store_cross_domain_pattern(self, pattern: str, examples: List[Dict]):
        """Store discovered cross-domain pattern"""
        try:
            domains = pattern.split('-')
            if len(domains) == 2:
                domain_a, domain_b = domains
                
                conn = sqlite3.connect(self.memory_db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cross_domain_links 
                    (id, domain_a, domain_b, connection_type, strength, examples)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    str(uuid.uuid4()),
                    domain_a,
                    domain_b,
                    "discovered_pattern",
                    min(1.0, len(examples) * 0.2),  # Strength based on examples
                    json.dumps(examples)
                ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"🔗 Discovered cross-domain pattern: {pattern} ({len(examples)} examples)")
        
        except Exception as e:
            logger.error(f"❌ Error storing cross-domain pattern: {e}")
    
    async def question_routing_loop(self):
        """Route questions to the most knowledgeable AI"""
        while True:
            try:
                # Check for new questions to route
                routing_dir = self.project_root / "collective-memory" / "question-routing"
                
                for question_file in routing_dir.glob("question_*.json"):
                    try:
                        with open(question_file, 'r') as f:
                            question_data = json.load(f)
                        
                        # Route the question
                        best_ai = await self.route_question(question_data)
                        
                        # Send routing result
                        await self.send_routing_result(question_data, best_ai)
                        
                        # Archive processed question
                        archive_dir = routing_dir / "processed"
                        archive_dir.mkdir(exist_ok=True)
                        question_file.rename(archive_dir / question_file.name)
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing question {question_file}: {e}")
                
                await asyncio.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in question routing loop: {e}")
                await asyncio.sleep(30)
    
    async def route_question(self, question_data: Dict) -> str:
        """Route question to the most appropriate AI"""
        try:
            question_text = question_data.get("question", "").lower()
            question_hash = hashlib.md5(question_text.encode()).hexdigest()
            
            # Check if we've seen this question before
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT best_ai, confidence, success_rate FROM question_routing 
                WHERE question_hash = ?
            ''', (question_hash,))
            
            cached_result = cursor.fetchone()
            
            if cached_result and cached_result[2] > 0.7:  # Good success rate
                # Update usage count
                cursor.execute('''
                    UPDATE question_routing SET usage_count = usage_count + 1 
                    WHERE question_hash = ?
                ''', (question_hash,))
                conn.commit()
                conn.close()
                
                return cached_result[0]
            
            # Analyze question to determine best AI
            best_ai = await self.analyze_question_for_routing(question_text)
            
            # Store routing decision
            cursor.execute('''
                INSERT OR REPLACE INTO question_routing 
                (id, question_hash, question_text, best_ai, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                question_hash,
                question_text,
                best_ai,
                0.8  # Initial confidence
            ))
            
            conn.commit()
            conn.close()
            
            return best_ai
            
        except Exception as e:
            logger.error(f"❌ Error routing question: {e}")
            return "project-manager"  # Default fallback
    
    async def analyze_question_for_routing(self, question_text: str) -> str:
        """Analyze question content to determine best AI"""
        try:
            # Score each AI based on keyword matches
            ai_scores = {}
            
            for ai, expertise_domains in self.ai_expertise.items():
                score = 0
                
                for domain in expertise_domains:
                    if domain in self.knowledge_domains:
                        for keyword in self.knowledge_domains[domain]:
                            if keyword in question_text:
                                score += 1
                
                ai_scores[ai] = score
            
            # Return AI with highest score
            if ai_scores:
                best_ai = max(ai_scores, key=ai_scores.get)
                if ai_scores[best_ai] > 0:
                    return best_ai
            
            # Fallback to project manager
            return "project-manager"
            
        except Exception as e:
            logger.error(f"❌ Error analyzing question: {e}")
            return "project-manager"
    
    async def send_routing_result(self, question_data: Dict, best_ai: str):
        """Send routing result back to requester"""
        try:
            result = {
                "type": "question_routing_result",
                "original_question": question_data,
                "routed_to": best_ai,
                "routing_confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
                "backup_ais": await self.get_backup_ais(best_ai)
            }
            
            # Save result for requester
            result_file = self.project_root / "collective-memory" / "question-routing" / f"result_{question_data.get('id', 'unknown')}.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Error sending routing result: {e}")
    
    async def get_backup_ais(self, primary_ai: str) -> List[str]:
        """Get backup AIs in case primary AI can't answer"""
        try:
            primary_domains = self.ai_expertise.get(primary_ai, [])
            backup_ais = []
            
            for ai, domains in self.ai_expertise.items():
                if ai != primary_ai:
                    # Check for domain overlap
                    overlap = set(primary_domains) & set(domains)
                    if overlap:
                        backup_ais.append(ai)
            
            return backup_ais[:3]  # Top 3 backups
            
        except Exception as e:
            logger.error(f"❌ Error getting backup AIs: {e}")
            return ["project-manager"]
    
    async def knowledge_graph_updates(self):
        """Update knowledge graph with new connections"""
        while True:
            try:
                await asyncio.sleep(1800)  # Every 30 minutes
                logger.info("🕸️ Updating knowledge graph connections")
                # Update graph connections based on recent knowledge
            except Exception as e:
                logger.error(f"❌ Error updating knowledge graph: {e}")
                await asyncio.sleep(3600)
    
    async def create_cross_domain_connections(self):
        """Create connections between different knowledge domains"""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Find knowledge entries from different domains that might be related
            cursor.execute('''
                SELECT DISTINCT domain FROM knowledge_entries
            ''')
            domains = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"🔗 Creating cross-domain connections between {len(domains)} domains")
            
            conn.close()
        except Exception as e:
            logger.error(f"❌ Error creating cross-domain connections: {e}")
    
    async def update_knowledge_confidence(self):
        """Update confidence scores for knowledge entries"""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Update confidence based on usage and validation
            cursor.execute('''
                UPDATE knowledge_entries
                SET confidence = CASE
                    WHEN usage_count > 10 THEN 0.95
                    WHEN usage_count > 5 THEN 0.85
                    WHEN usage_count > 2 THEN 0.75
                    ELSE 0.65
                END
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("📊 Updated knowledge confidence scores")
        except Exception as e:
            logger.error(f"❌ Error updating knowledge confidence: {e}")
    
    async def memory_consolidation_loop(self):
        """Consolidate and optimize collective memory"""
        while True:
            try:
                # Consolidate duplicate knowledge
                await self.consolidate_duplicate_knowledge()
                
                # Update knowledge confidence scores
                await self.update_knowledge_confidence()
                
                # Archive old knowledge
                await self.archive_old_knowledge()
                
                await asyncio.sleep(7200)  # Every 2 hours
                
            except Exception as e:
                logger.error(f"❌ Error in memory consolidation: {e}")
                await asyncio.sleep(3600)
    
    async def consolidate_duplicate_knowledge(self):
        """Find and consolidate duplicate knowledge entries"""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            # Find potential duplicates by topic similarity
            cursor.execute('''
                SELECT id, topic, content, confidence_score FROM knowledge_entries
                ORDER BY topic, created_at DESC
            ''')
            
            entries = cursor.fetchall()
            
            # Group by similar topics
            topic_groups = {}
            for entry_id, topic, content, confidence in entries:
                topic_key = topic.lower().strip()
                if topic_key not in topic_groups:
                    topic_groups[topic_key] = []
                topic_groups[topic_key].append((entry_id, topic, content, confidence))
            
            # Consolidate groups with multiple entries
            for topic_key, group_entries in topic_groups.items():
                if len(group_entries) > 1:
                    await self.merge_knowledge_entries(group_entries)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error consolidating duplicate knowledge: {e}")
    
    async def merge_knowledge_entries(self, entries: List[tuple]):
        """Merge multiple knowledge entries into one consolidated entry"""
        try:
            # Keep the entry with highest confidence
            best_entry = max(entries, key=lambda x: x[3])  # x[3] is confidence_score
            
            # Merge content from all entries
            merged_content = {"consolidated": True, "sources": []}
            
            for entry_id, topic, content_json, confidence in entries:
                try:
                    content = json.loads(content_json)
                    merged_content["sources"].append({
                        "original_id": entry_id,
                        "content": content,
                        "confidence": confidence
                    })
                except json.JSONDecodeError:
                    continue
            
            # Update the best entry with merged content
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE knowledge_entries 
                SET content = ?, confidence_score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                json.dumps(merged_content),
                min(1.0, best_entry[3] + 0.1),  # Slight confidence boost for consolidation
                best_entry[0]
            ))
            
            # Mark other entries as consolidated
            for entry_id, _, _, _ in entries:
                if entry_id != best_entry[0]:
                    cursor.execute('''
                        UPDATE knowledge_entries 
                        SET tags = json_insert(COALESCE(tags, '[]'), '$[#]', 'consolidated')
                        WHERE id = ?
                    ''', (entry_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"🔄 Consolidated {len(entries)} knowledge entries for topic: {best_entry[1]}")
            
        except Exception as e:
            logger.error(f"❌ Error merging knowledge entries: {e}")
    
    async def collective_learning_sync(self):
        """Synchronize learning across all AIs"""
        while True:
            try:
                # Sync recent learning events
                await self.sync_learning_events()
                
                # Update AI expertise based on learning
                await self.update_ai_expertise()
                
                await asyncio.sleep(900)  # Every 15 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in collective learning sync: {e}")
                await asyncio.sleep(1800)
    
    async def sync_learning_events(self):
        """Synchronize learning events across all AIs"""
        try:
            # Check for new learning events
            learning_dir = self.project_root / "collective-memory" / "learning-logs"
            
            for learning_file in learning_dir.glob("learning_*.json"):
                try:
                    with open(learning_file, 'r') as f:
                        learning_event = json.load(f)
                    
                    # Store in database
                    await self.store_learning_event(learning_event)
                    
                    # Distribute learning to relevant AIs
                    await self.distribute_learning(learning_event)
                    
                    # Archive processed learning
                    archive_dir = learning_dir / "processed"
                    archive_dir.mkdir(exist_ok=True)
                    learning_file.rename(archive_dir / learning_file.name)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing learning file {learning_file}: {e}")
            
        except Exception as e:
            logger.error(f"❌ Error syncing learning events: {e}")
    
    async def store_learning_event(self, learning_event: Dict):
        """Store learning event in collective memory"""
        try:
            conn = sqlite3.connect(self.memory_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_events 
                (id, ai_agent, event_type, knowledge_gained, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                learning_event.get("ai_agent"),
                learning_event.get("event_type"),
                json.dumps(learning_event.get("knowledge_gained", {})),
                learning_event.get("source", "unknown")
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error storing learning event: {e}")
    
    async def context_awareness_system(self):
        """Maintain context awareness across all AIs"""
        while True:
            try:
                # Update global context
                await self.update_global_context()
                
                # Maintain conversation context
                await self.maintain_conversation_context()
                
                await asyncio.sleep(60)  # Every minute
                
            except Exception as e:
                logger.error(f"❌ Error in context awareness: {e}")
                await asyncio.sleep(300)
    
    async def update_global_context(self):
        """Update global context that all AIs should be aware of"""
        try:
            global_context = {
                "current_project_phase": await self.get_current_project_phase(),
                "active_tasks": await self.get_active_tasks(),
                "recent_decisions": await self.get_recent_decisions(),
                "system_status": await self.get_system_status(),
                "user_preferences": await self.get_user_preferences(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save global context
            context_file = self.project_root / "collective-memory" / "global_context.json"
            with open(context_file, 'w') as f:
                json.dump(global_context, f, indent=2)
            
            # Distribute to all AIs
            await self.distribute_global_context(global_context)
            
        except Exception as e:
            logger.error(f"❌ Error updating global context: {e}")
    
    async def distribute_global_context(self, context: Dict):
        """Distribute global context to all AIs"""
        try:
            for ai in self.ai_expertise.keys():
                context_dir = self.project_root / "collective-memory" / "knowledge-base" / ai
                context_dir.mkdir(parents=True, exist_ok=True)
                
                ai_context_file = context_dir / "global_context.json"
                with open(ai_context_file, 'w') as f:
                    json.dump(context, f, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Error distributing global context: {e}")
    
    # Helper methods for context awareness
    async def get_current_project_phase(self) -> str:
        """Get current project development phase"""
        # This would integrate with project manager
        return "active_development"
    
    async def get_active_tasks(self) -> List[Dict]:
        """Get currently active tasks"""
        # This would integrate with task management
        return []
    
    async def get_recent_decisions(self) -> List[Dict]:
        """Get recent AI decisions and votes"""
        # This would integrate with voting system
        return []
    
    async def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "backend_status": "running",
            "frontend_status": "running", 
            "database_status": "healthy",
            "ai_agents_active": len(self.ai_expertise)
        }
    
    async def get_user_preferences(self) -> Dict:
        """Get user preferences and settings"""
        return {
            "development_style": "agile",
            "priority": "speed_and_quality",
            "communication_level": "detailed"
        }

async def main():
    """Main entry point for Collective Memory System"""
    collective_memory = CollectiveMemorySystem()
    
    try:
        await collective_memory.start_collective_memory_system()
    except KeyboardInterrupt:
        logger.info("🛑 Collective Memory System shutdown signal received")
    except Exception as e:
        logger.error(f"❌ Fatal error in Collective Memory System: {e}")

if __name__ == "__main__":
    asyncio.run(main())
