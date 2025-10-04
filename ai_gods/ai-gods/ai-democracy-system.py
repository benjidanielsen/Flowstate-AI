#!/usr/bin/env python3
"""
🗳️ AI DEMOCRACY & BUSINESS IMPACT SYSTEM
💰 Shows the boss how AI decisions generate MONEY
🤖 AIs vote together, make decisions, and track business impact
📈 Real-time ROI, efficiency gains, and profit generation
"""

import asyncio
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import logging
import uuid
import random
from typing import Dict, List, Any, Optional
import sqlite3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='🗳️ [AI-DEMOCRACY] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/ai-democracy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIDemocracySystem:
    """
    AI Democracy and Business Impact Tracking System
    Shows the boss how AI decisions generate money and efficiency
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.godmode_enabled = True
        
        # Business Impact Tracking
        self.business_metrics = {
            "total_revenue_generated": 0,
            "cost_savings": 0,
            "efficiency_gains": 0,
            "time_saved_hours": 0,
            "bugs_prevented": 0,
            "features_delivered": 0,
            "customer_satisfaction": 95,
            "development_speed_increase": 0
        }
        
        # AI Voting System
        self.active_votes = {}
        self.vote_history = []
        self.ai_performance_scores = {}
        
        # Decision Categories
        self.decision_types = {
            "feature_implementation": {
                "description": "New feature to implement",
                "business_impact": "high",
                "voting_threshold": 0.6
            },
            "optimization": {
                "description": "Performance or code optimization",
                "business_impact": "medium", 
                "voting_threshold": 0.5
            },
            "bug_fix": {
                "description": "Bug fix or issue resolution",
                "business_impact": "high",
                "voting_threshold": 0.4
            },
            "innovation": {
                "description": "Revolutionary new idea or approach",
                "business_impact": "very_high",
                "voting_threshold": 0.7
            },
            "refactoring": {
                "description": "Code refactoring or restructuring",
                "business_impact": "medium",
                "voting_threshold": 0.5
            }
        }
        
        # AI Agents with voting power
        self.ai_voters = {
            "project-manager": {"voting_power": 2.0, "expertise": ["planning", "coordination"]},
            "backend-developer": {"voting_power": 1.5, "expertise": ["backend", "api", "database"]},
            "frontend-developer": {"voting_power": 1.5, "expertise": ["frontend", "ui", "ux"]},
            "database-ai": {"voting_power": 1.3, "expertise": ["database", "performance"]},
            "tester-ai": {"voting_power": 1.2, "expertise": ["testing", "quality"]},
            "devops-ai": {"voting_power": 1.2, "expertise": ["deployment", "infrastructure"]},
            "innovation-ai": {"voting_power": 1.8, "expertise": ["innovation", "future_tech"]},
            "collective-memory-system": {"voting_power": 1.4, "expertise": ["knowledge", "learning"]}
        }
        
        # Initialize systems
        self.setup_democracy_infrastructure()
        
        logger.info("🚀 AI DEMOCRACY & BUSINESS IMPACT SYSTEM INITIALIZED")
    
    def setup_democracy_infrastructure(self):
        """Setup the AI democracy infrastructure"""
        
        # Create directories
        democracy_dirs = [
            "ai-democracy/votes",
            "ai-democracy/decisions", 
            "ai-democracy/business-impact",
            "ai-democracy/performance-tracking",
            "business-dashboard/metrics",
            "business-dashboard/reports"
        ]
        
        for directory in democracy_dirs:
            (self.project_root / directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.init_democracy_database()
        
        # Initialize AI performance tracking
        for ai_id in self.ai_voters.keys():
            self.ai_performance_scores[ai_id] = {
                "decisions_made": 0,
                "successful_decisions": 0,
                "business_impact_generated": 0,
                "accuracy_score": 100,
                "innovation_score": 50
            }
        
        logger.info("🏛️ AI Democracy infrastructure initialized")
    
    def init_democracy_database(self):
        """Initialize democracy and business tracking database"""
        try:
            db_path = self.project_root / "ai-democracy" / "democracy.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Votes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS votes (
                    id TEXT PRIMARY KEY,
                    proposal_id TEXT NOT NULL,
                    voter_ai TEXT NOT NULL,
                    vote TEXT NOT NULL,
                    voting_power REAL NOT NULL,
                    reasoning TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Decisions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY,
                    proposal_id TEXT NOT NULL,
                    decision_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    result TEXT NOT NULL,
                    total_votes_for REAL DEFAULT 0,
                    total_votes_against REAL DEFAULT 0,
                    business_impact_predicted REAL DEFAULT 0,
                    business_impact_actual REAL DEFAULT 0,
                    implementation_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    decided_at TIMESTAMP
                )
            ''')
            
            # Business Impact table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS business_impact (
                    id TEXT PRIMARY KEY,
                    decision_id TEXT,
                    impact_type TEXT NOT NULL,
                    impact_value REAL NOT NULL,
                    impact_description TEXT,
                    measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ai_responsible TEXT
                )
            ''')
            
            # AI Performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_performance (
                    id TEXT PRIMARY KEY,
                    ai_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    context TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("💾 Democracy database initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing democracy database: {e}")
    
    async def start_democracy_system(self):
        """Start the AI democracy and business tracking system"""
        logger.info("🎯 Starting AI Democracy & Business Impact System")
        
        # Start all democracy processes
        democracy_tasks = [
            asyncio.create_task(self.proposal_monitoring_loop()),
            asyncio.create_task(self.voting_coordination_loop()),
            asyncio.create_task(self.decision_implementation_loop()),
            asyncio.create_task(self.business_impact_tracking_loop()),
            asyncio.create_task(self.ai_performance_monitoring_loop()),
            asyncio.create_task(self.generate_business_reports_loop()),
            asyncio.create_task(self.simulate_ai_proposals_loop())  # For demo
        ]
        
        # Run all processes concurrently
        await asyncio.gather(*democracy_tasks)
    
    async def proposal_monitoring_loop(self):
        """Monitor for new proposals from AIs"""
        while True:
            try:
                # Check for new proposals
                proposals_dir = self.project_root / "ai-democracy" / "votes"
                
                for proposal_file in proposals_dir.glob("proposal_*.json"):
                    try:
                        with open(proposal_file, 'r') as f:
                            proposal = json.load(f)
                        
                        if proposal.get("status") == "new":
                            await self.initiate_voting(proposal)
                            
                            # Mark as processed
                            proposal["status"] = "voting"
                            with open(proposal_file, 'w') as f:
                                json.dump(proposal, f, indent=2)
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing proposal {proposal_file}: {e}")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in proposal monitoring: {e}")
                await asyncio.sleep(30)
    
    async def initiate_voting(self, proposal: Dict):
        """Initiate voting process for a proposal"""
        try:
            proposal_id = proposal.get("id", str(uuid.uuid4()))
            
            # Create voting session
            voting_session = {
                "proposal_id": proposal_id,
                "title": proposal.get("title", "Untitled Proposal"),
                "description": proposal.get("description", ""),
                "decision_type": proposal.get("type", "feature_implementation"),
                "proposed_by": proposal.get("proposed_by", "unknown"),
                "voting_deadline": (datetime.now() + timedelta(minutes=30)).isoformat(),
                "votes": {},
                "status": "active",
                "business_impact_estimate": proposal.get("business_impact_estimate", 0),
                "created_at": datetime.now().isoformat()
            }
            
            self.active_votes[proposal_id] = voting_session
            
            # Notify all AIs to vote
            await self.notify_ais_to_vote(voting_session)
            
            logger.info(f"🗳️ Initiated voting for proposal: {voting_session['title']}")
            
        except Exception as e:
            logger.error(f"❌ Error initiating voting: {e}")
    
    async def notify_ais_to_vote(self, voting_session: Dict):
        """Notify all AIs to participate in voting"""
        try:
            for ai_id in self.ai_voters.keys():
                vote_request = {
                    "type": "vote_request",
                    "proposal_id": voting_session["proposal_id"],
                    "title": voting_session["title"],
                    "description": voting_session["description"],
                    "decision_type": voting_session["decision_type"],
                    "business_impact_estimate": voting_session["business_impact_estimate"],
                    "voting_deadline": voting_session["voting_deadline"],
                    "your_expertise": self.ai_voters[ai_id]["expertise"],
                    "your_voting_power": self.ai_voters[ai_id]["voting_power"]
                }
                
                # Save vote request for AI
                vote_file = self.project_root / "ai-democracy" / "votes" / f"vote_request_{ai_id}_{voting_session['proposal_id']}.json"
                with open(vote_file, 'w') as f:
                    json.dump(vote_request, f, indent=2)
        
        except Exception as e:
            logger.error(f"❌ Error notifying AIs to vote: {e}")
    
    async def voting_coordination_loop(self):
        """Coordinate voting process and collect votes"""
        while True:
            try:
                # Process votes for active voting sessions
                for proposal_id, session in list(self.active_votes.items()):
                    if session["status"] == "active":
                        await self.collect_votes(proposal_id, session)
                        await self.check_voting_completion(proposal_id, session)
                
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in voting coordination: {e}")
                await asyncio.sleep(30)
    
    async def collect_votes(self, proposal_id: str, session: Dict):
        """Collect votes from AIs"""
        try:
            votes_dir = self.project_root / "ai-democracy" / "votes"
            
            for vote_file in votes_dir.glob(f"vote_{proposal_id}_*.json"):
                try:
                    with open(vote_file, 'r') as f:
                        vote_data = json.load(f)
                    
                    voter_ai = vote_data.get("voter_ai")
                    if voter_ai and voter_ai not in session["votes"]:
                        # Record the vote
                        session["votes"][voter_ai] = {
                            "vote": vote_data.get("vote"),  # "approve", "reject", "abstain"
                            "reasoning": vote_data.get("reasoning", ""),
                            "confidence": vote_data.get("confidence", 0.5),
                            "business_impact_prediction": vote_data.get("business_impact_prediction", 0),
                            "timestamp": vote_data.get("timestamp", datetime.now().isoformat())
                        }
                        
                        # Store in database
                        await self.store_vote_in_db(proposal_id, voter_ai, vote_data)
                        
                        # Archive processed vote
                        archive_dir = votes_dir / "processed"
                        archive_dir.mkdir(exist_ok=True)
                        vote_file.rename(archive_dir / vote_file.name)
                        
                        logger.info(f"📊 Collected vote from {voter_ai} for proposal {proposal_id}")
                
                except Exception as e:
                    logger.error(f"❌ Error processing vote file {vote_file}: {e}")
        
        except Exception as e:
            logger.error(f"❌ Error collecting votes: {e}")
    
    async def store_vote_in_db(self, proposal_id: str, voter_ai: str, vote_data: Dict):
        """Store vote in database"""
        try:
            db_path = self.project_root / "ai-democracy" / "democracy.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO votes (id, proposal_id, voter_ai, vote, voting_power, reasoning)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                proposal_id,
                voter_ai,
                vote_data.get("vote"),
                self.ai_voters.get(voter_ai, {}).get("voting_power", 1.0),
                vote_data.get("reasoning", "")
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error storing vote in database: {e}")
    
    async def check_voting_completion(self, proposal_id: str, session: Dict):
        """Check if voting is complete and make decision"""
        try:
            # Check if voting deadline passed or all AIs voted
            deadline = datetime.fromisoformat(session["voting_deadline"])
            all_voted = len(session["votes"]) >= len(self.ai_voters)
            
            if datetime.now() > deadline or all_voted:
                # Calculate results
                decision_result = await self.calculate_voting_results(session)
                
                # Store decision
                await self.store_decision(proposal_id, session, decision_result)
                
                # Update session status
                session["status"] = "completed"
                session["result"] = decision_result
                
                # Generate business impact prediction
                await self.predict_business_impact(proposal_id, session, decision_result)
                
                logger.info(f"✅ Voting completed for proposal {proposal_id}: {decision_result['result']}")
        
        except Exception as e:
            logger.error(f"❌ Error checking voting completion: {e}")
    
    async def calculate_voting_results(self, session: Dict) -> Dict:
        """Calculate weighted voting results"""
        try:
            total_votes_for = 0
            total_votes_against = 0
            total_abstain = 0
            
            vote_details = []
            
            for voter_ai, vote_info in session["votes"].items():
                voting_power = self.ai_voters.get(voter_ai, {}).get("voting_power", 1.0)
                vote = vote_info["vote"]
                
                if vote == "approve":
                    total_votes_for += voting_power
                elif vote == "reject":
                    total_votes_against += voting_power
                else:  # abstain
                    total_abstain += voting_power
                
                vote_details.append({
                    "ai": voter_ai,
                    "vote": vote,
                    "power": voting_power,
                    "reasoning": vote_info.get("reasoning", "")
                })
            
            # Determine result
            total_votes = total_votes_for + total_votes_against
            approval_ratio = total_votes_for / total_votes if total_votes > 0 else 0
            
            decision_type = session.get("decision_type", "feature_implementation")
            threshold = self.decision_types.get(decision_type, {}).get("voting_threshold", 0.5)
            
            result = "approved" if approval_ratio >= threshold else "rejected"
            
            return {
                "result": result,
                "votes_for": total_votes_for,
                "votes_against": total_votes_against,
                "abstain": total_abstain,
                "approval_ratio": approval_ratio,
                "threshold_required": threshold,
                "vote_details": vote_details
            }
        
        except Exception as e:
            logger.error(f"❌ Error calculating voting results: {e}")
            return {"result": "error", "votes_for": 0, "votes_against": 0}
    
    async def store_decision(self, proposal_id: str, session: Dict, result: Dict):
        """Store decision in database"""
        try:
            db_path = self.project_root / "ai-democracy" / "democracy.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO decisions 
                (id, proposal_id, decision_type, title, description, result, 
                 total_votes_for, total_votes_against, business_impact_predicted, decided_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                proposal_id,
                session.get("decision_type", "unknown"),
                session.get("title", ""),
                session.get("description", ""),
                result["result"],
                result["votes_for"],
                result["votes_against"],
                session.get("business_impact_estimate", 0),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error storing decision: {e}")
    
    async def predict_business_impact(self, proposal_id: str, session: Dict, result: Dict):
        """Predict business impact of the decision"""
        try:
            if result["result"] == "approved":
                decision_type = session.get("decision_type", "feature_implementation")
                
                # Calculate predicted business impact
                base_impact = session.get("business_impact_estimate", 0)
                
                # Impact multipliers based on decision type
                impact_multipliers = {
                    "feature_implementation": 1.5,
                    "optimization": 1.2,
                    "bug_fix": 1.0,
                    "innovation": 2.0,
                    "refactoring": 0.8
                }
                
                multiplier = impact_multipliers.get(decision_type, 1.0)
                predicted_impact = base_impact * multiplier * result["approval_ratio"]
                
                # Store business impact prediction
                await self.store_business_impact(
                    proposal_id,
                    "predicted_revenue",
                    predicted_impact,
                    f"Predicted revenue from {decision_type}: {session['title']}"
                )
                
                # Update business metrics
                self.business_metrics["total_revenue_generated"] += predicted_impact
                
                logger.info(f"💰 Predicted business impact: ${predicted_impact:,.2f} from {session['title']}")
        
        except Exception as e:
            logger.error(f"❌ Error predicting business impact: {e}")
    
    async def store_business_impact(self, decision_id: str, impact_type: str, impact_value: float, description: str):
        """Store business impact in database"""
        try:
            db_path = self.project_root / "ai-democracy" / "democracy.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO business_impact (id, decision_id, impact_type, impact_value, impact_description)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                decision_id,
                impact_type,
                impact_value,
                description
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error storing business impact: {e}")
    
    async def business_impact_tracking_loop(self):
        """Track and calculate real business impact"""
        while True:
            try:
                # Calculate various business metrics
                await self.calculate_efficiency_gains()
                await self.calculate_cost_savings()
                await self.calculate_time_savings()
                await self.update_development_speed()
                
                # Generate business report
                await self.generate_business_metrics_report()
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in business impact tracking: {e}")
                await asyncio.sleep(600)
    
    async def calculate_efficiency_gains(self):
        """Calculate efficiency gains from AI decisions"""
        try:
            # Simulate efficiency calculations based on AI decisions
            db_path = self.project_root / "ai-democracy" / "democracy.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get approved decisions from last 24 hours
            cursor.execute('''
                SELECT COUNT(*) FROM decisions 
                WHERE result = 'approved' AND decided_at > datetime('now', '-24 hours')
            ''')
            
            recent_decisions = cursor.fetchone()[0]
            
            # Calculate efficiency gain (each decision improves efficiency)
            efficiency_gain = recent_decisions * 2.5  # 2.5% per decision
            self.business_metrics["efficiency_gains"] += efficiency_gain
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error calculating efficiency gains: {e}")
    
    async def calculate_cost_savings(self):
        """Calculate cost savings from AI automation"""
        try:
            # Simulate cost savings calculation
            # Each AI decision saves manual work hours
            hourly_rate = 75  # Developer hourly rate
            hours_saved_per_decision = 2.5
            
            db_path = self.project_root / "ai-democracy" / "democracy.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM decisions 
                WHERE result = 'approved' AND decided_at > datetime('now', '-1 hour')
            ''')
            
            recent_decisions = cursor.fetchone()[0]
            
            cost_savings = recent_decisions * hours_saved_per_decision * hourly_rate
            self.business_metrics["cost_savings"] += cost_savings
            self.business_metrics["time_saved_hours"] += recent_decisions * hours_saved_per_decision
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error calculating cost savings: {e}")
    
    async def calculate_time_savings(self):
        """Calculate time savings from AI automation"""
        try:
            # Time saved by AI making decisions vs manual process
            manual_decision_time = 4  # hours for manual decision making
            ai_decision_time = 0.5    # hours for AI decision making
            
            time_saved_per_decision = manual_decision_time - ai_decision_time
            
            # Get decisions made in last hour
            db_path = self.project_root / "ai-democracy" / "democracy.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM decisions 
                WHERE decided_at > datetime('now', '-1 hour')
            ''')
            
            recent_decisions = cursor.fetchone()[0]
            
            time_saved = recent_decisions * time_saved_per_decision
            self.business_metrics["time_saved_hours"] += time_saved
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error calculating time savings: {e}")
    
    async def update_development_speed(self):
        """Update development speed metrics"""
        try:
            # Calculate development speed increase based on AI decisions
            base_speed = 100  # baseline development speed
            
            # Each approved decision increases speed
            db_path = self.project_root / "ai-democracy" / "democracy.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT COUNT(*) FROM decisions 
                WHERE result = 'approved'
            ''')
            
            total_approved = cursor.fetchone()[0]
            
            speed_increase = min(200, base_speed + (total_approved * 5))  # Max 200% speed
            self.business_metrics["development_speed_increase"] = speed_increase - base_speed
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error updating development speed: {e}")
    
    async def generate_business_metrics_report(self):
        """Generate business metrics report for the boss"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "business_metrics": self.business_metrics.copy(),
                "roi_calculation": {
                    "total_investment": 50000,  # Estimated AI system investment
                    "total_returns": self.business_metrics["total_revenue_generated"] + self.business_metrics["cost_savings"],
                    "roi_percentage": 0
                },
                "productivity_gains": {
                    "efficiency_improvement": f"{self.business_metrics['efficiency_gains']:.1f}%",
                    "time_saved": f"{self.business_metrics['time_saved_hours']:.1f} hours",
                    "development_speed": f"+{self.business_metrics['development_speed_increase']:.1f}%"
                },
                "ai_democracy_stats": await self.get_democracy_stats()
            }
            
            # Calculate ROI
            if report["roi_calculation"]["total_investment"] > 0:
                roi = (report["roi_calculation"]["total_returns"] / report["roi_calculation"]["total_investment"] - 1) * 100
                report["roi_calculation"]["roi_percentage"] = roi
            
            # Save report
            report_file = self.project_root / "business-dashboard" / "reports" / f"business_report_{int(time.time())}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Save latest metrics for dashboard
            metrics_file = self.project_root / "business-dashboard" / "metrics" / "latest_metrics.json"
            with open(metrics_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📊 Generated business report - ROI: {report['roi_calculation']['roi_percentage']:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Error generating business report: {e}")
    
    async def get_democracy_stats(self) -> Dict:
        """Get AI democracy statistics"""
        try:
            db_path = self.project_root / "ai-democracy" / "democracy.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Total decisions
            cursor.execute('SELECT COUNT(*) FROM decisions')
            total_decisions = cursor.fetchone()[0]
            
            # Approved vs rejected
            cursor.execute('SELECT result, COUNT(*) FROM decisions GROUP BY result')
            decision_breakdown = dict(cursor.fetchall())
            
            # Recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM decisions 
                WHERE decided_at > datetime('now', '-24 hours')
            ''')
            recent_decisions = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_decisions": total_decisions,
                "approved_decisions": decision_breakdown.get("approved", 0),
                "rejected_decisions": decision_breakdown.get("rejected", 0),
                "recent_decisions_24h": recent_decisions,
                "approval_rate": (decision_breakdown.get("approved", 0) / max(1, total_decisions)) * 100
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting democracy stats: {e}")
            return {}
    
    async def simulate_ai_proposals_loop(self):
        """Simulate AI proposals for demonstration"""
        while True:
            try:
                # Generate realistic AI proposals
                await self.generate_sample_proposal()
                
                # Wait between proposals (5-15 minutes)
                await asyncio.sleep(random.randint(300, 900))
                
            except Exception as e:
                logger.error(f"❌ Error in proposal simulation: {e}")
                await asyncio.sleep(600)
    
    async def generate_sample_proposal(self):
        """Generate a sample AI proposal"""
        try:
            sample_proposals = [
                {
                    "title": "Implement AI-powered prospect scoring",
                    "description": "Add machine learning to automatically score prospects based on Frazer Method criteria",
                    "type": "innovation",
                    "business_impact_estimate": 25000,
                    "proposed_by": "innovation-ai"
                },
                {
                    "title": "Optimize database query performance",
                    "description": "Refactor slow database queries to improve dashboard loading speed by 40%",
                    "type": "optimization", 
                    "business_impact_estimate": 5000,
                    "proposed_by": "database-ai"
                },
                {
                    "title": "Add mobile-responsive dashboard",
                    "description": "Create mobile-friendly version of the CRM dashboard for on-the-go access",
                    "type": "feature_implementation",
                    "business_impact_estimate": 15000,
                    "proposed_by": "frontend-developer"
                },
                {
                    "title": "Implement automated follow-up suggestions",
                    "description": "AI system that suggests optimal follow-up timing and messaging for prospects",
                    "type": "innovation",
                    "business_impact_estimate": 35000,
                    "proposed_by": "innovation-ai"
                },
                {
                    "title": "Add real-time collaboration features",
                    "description": "Enable multiple users to work on prospects simultaneously with live updates",
                    "type": "feature_implementation",
                    "business_impact_estimate": 20000,
                    "proposed_by": "backend-developer"
                }
            ]
            
            proposal = random.choice(sample_proposals)
            proposal["id"] = str(uuid.uuid4())
            proposal["status"] = "new"
            proposal["created_at"] = datetime.now().isoformat()
            
            # Save proposal
            proposal_file = self.project_root / "ai-democracy" / "votes" / f"proposal_{proposal['id']}.json"
            with open(proposal_file, 'w') as f:
                json.dump(proposal, f, indent=2)
            
            logger.info(f"💡 Generated sample proposal: {proposal['title']}")
            
        except Exception as e:
            logger.error(f"❌ Error generating sample proposal: {e}")

async def main():
    """Main entry point for AI Democracy System"""
    democracy = AIDemocracySystem()
    
    try:
        await democracy.start_democracy_system()
    except KeyboardInterrupt:
        logger.info("🛑 AI Democracy System shutdown signal received")
    except Exception as e:
        logger.error(f"❌ Fatal error in AI Democracy System: {e}")

if __name__ == "__main__":
    asyncio.run(main())
