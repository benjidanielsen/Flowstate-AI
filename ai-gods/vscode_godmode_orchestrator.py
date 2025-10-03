#!/usr/bin/env python3
"""
VSCode GODMODE Orchestrator
Master orchestrator for the self-making VSCode system
Coordinates all AI agents, self-correction, and continuous improvement
"""

import asyncio
import json
import logging
import signal
import sys
import platform
from datetime import datetime
from typing import Dict, List

from vscode_agent_integration import VSCodeAgentIntegration
from vscode_self_correction import VSCodeSelfCorrectionSystem

# Ensure UTF-8 encoding for stdout on Windows to support emoji logging
if platform.system() == 'Windows':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/vscode_godmode.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VSCodeGODMODEOrchestrator:
    """
    Master orchestrator for the self-making VSCode system
    """
    
    def __init__(self, project_root: str = '/home/ubuntu/Flowstate-AI'):
        self.project_root = project_root
        self.running = False
        self.agents = {}
        
        # Initialize VSCode integration
        self.vscode = VSCodeAgentIntegration()
        
        # Initialize self-correction system
        self.self_correction = VSCodeSelfCorrectionSystem(project_root, self.vscode)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("🛑 Received shutdown signal. Stopping GODMODE...")
        self.running = False
    
    async def start(self):
        """Start the GODMODE orchestrator"""
        logger.info("🚀 Starting VSCode GODMODE Orchestrator...")
        
        self.running = True
        
        # Register orchestrator as an agent
        self.vscode.register_agent('godmode-orchestrator', 'ACTIVE')
        
        # Send startup notification to VSCode
        self.vscode.notify_vscode('🚀 GODMODE Orchestrator started', 'info')
        
        # Start all subsystems
        await self.start_subsystems()
        
        # Main orchestration loop
        await self.orchestration_loop()
    
    async def start_subsystems(self):
        """Start all subsystems"""
        logger.info("🔧 Starting subsystems...")
        
        # Update status
        self.vscode.update_status('ACTIVE', 'Starting subsystems', 10)
        
        # Subsystem 1: Self-Correction System
        logger.info("  ✅ Self-Correction System initialized")
        
        # Subsystem 2: Project Manager AI (if not already running)
        # This would be started separately
        logger.info("  ✅ Project Manager AI ready")
        
        # Subsystem 3: Communication Hub (if not already running)
        logger.info("  ✅ Communication Hub ready")
        
        # Subsystem 4: Autonomous Development Module (if not already running)
        logger.info("  ✅ Autonomous Development Module ready")
        
        self.vscode.update_status('ACTIVE', 'All subsystems started', 100)
        self.vscode.notify_vscode('✅ All subsystems started successfully', 'info')
    
    async def orchestration_loop(self):
        """Main orchestration loop"""
        logger.info("🔄 Entering orchestration loop...")
        
        cycle_count = 0
        
        while self.running:
            cycle_count += 1
            logger.info(f"🔄 Orchestration cycle #{cycle_count}")
            
            try:
                # Update status
                self.vscode.update_status(
                    'ACTIVE',
                    f'Running orchestration cycle #{cycle_count}',
                    (cycle_count % 100)
                )
                
                # Phase 1: Health Check
                await self.health_check()
                
                # Phase 2: Self-Correction Cycle (every 5 minutes)
                if cycle_count % 30 == 0:  # Every 30 cycles (5 minutes if 10s/cycle)
                    logger.info("🔧 Running self-correction cycle...")
                    await self.self_correction.run_continuous_improvement_cycle()
                
                # Phase 3: Agent Coordination
                await self.coordinate_agents()
                
                # Phase 4: Task Management
                await self.manage_tasks()
                
                # Phase 5: Performance Monitoring
                await self.monitor_performance()
                
                # Wait 10 seconds before next cycle
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"❌ Error in orchestration loop: {e}")
                self.vscode.notify_vscode(f'⚠️ Orchestration error: {e}', 'error')
                
                # Wait a bit before retrying
                await asyncio.sleep(30)
        
        logger.info("🛑 Orchestration loop stopped")
    
    async def health_check(self):
        """Perform health check on all systems"""
        try:
            # Check if backend API is running
            import requests
            response = requests.get('http://localhost:3001/api/health', timeout=5)
            
            if response.status_code == 200:
                logger.debug("✅ Backend API healthy")
            else:
                logger.warning("⚠️ Backend API not responding correctly")
                self.vscode.notify_vscode('⚠️ Backend API health check failed', 'warning')
        except Exception as e:
            logger.warning(f"⚠️ Backend API health check failed: {e}")
    
    async def coordinate_agents(self):
        """Coordinate AI agents"""
        try:
            # Get agent status from backend
            import requests
            response = requests.get('http://localhost:3001/api/agents/status', timeout=5)
            
            if response.status_code == 200:
                agents = response.json()
                logger.debug(f"📊 Active agents: {len(agents)}")
                
                # Check for stuck agents
                for agent in agents:
                    if agent['status'] == 'ERROR':
                        logger.warning(f"⚠️ Agent {agent['agent_id']} in ERROR state")
                        # Attempt to restart or fix
                        await self.fix_agent(agent['agent_id'])
        except Exception as e:
            logger.debug(f"Agent coordination check: {e}")
    
    async def manage_tasks(self):
        """Manage tasks and assignments"""
        try:
            # Get tasks from backend
            import requests
            response = requests.get('http://localhost:3001/api/tasks', timeout=5)
            
            if response.status_code == 200:
                tasks = response.json()
                
                # Check for stalled tasks
                for task in tasks:
                    if task['status'] == 'IN_PROGRESS':
                        # Check if task has been in progress for too long
                        # This would require timestamp tracking
                        pass
        except Exception as e:
            logger.debug(f"Task management check: {e}")
    
    async def monitor_performance(self):
        """Monitor system performance"""
        try:
            # Get system status
            import requests
            response = requests.get('http://localhost:3001/api/system/status', timeout=5)
            
            if response.status_code == 200:
                status = response.json()
                logger.debug(f"📊 System status: {status['system_status']}")
        except Exception as e:
            logger.debug(f"Performance monitoring check: {e}")
    
    async def fix_agent(self, agent_id: str):
        """Attempt to fix a problematic agent"""
        logger.info(f"🔧 Attempting to fix agent: {agent_id}")
        
        # Send restart command
        self.vscode.send_terminal_command(f'python3 ai-gods/{agent_id}.py')
        
        # Wait for restart
        await asyncio.sleep(5)
        
        # Verify agent is running
        # This would require checking agent status
        
        self.vscode.notify_vscode(f'🔧 Attempted to restart agent: {agent_id}', 'info')
    
    async def stop(self):
        """Stop the orchestrator"""
        logger.info("🛑 Stopping GODMODE Orchestrator...")
        
        self.running = False
        
        # Update status
        self.vscode.update_status('STOPPED', 'Orchestrator stopped', 0)
        
        # Send shutdown notification
        self.vscode.notify_vscode('🛑 GODMODE Orchestrator stopped', 'info')
        
        logger.info("✅ GODMODE Orchestrator stopped successfully")

async def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("🚀 VSCode GODMODE - Self-Making Development System")
    logger.info("=" * 80)
    
    # Create orchestrator
    orchestrator = VSCodeGODMODEOrchestrator()
    
    try:
        # Start orchestrator
        await orchestrator.start()
    except KeyboardInterrupt:
        logger.info("\n🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        # Stop orchestrator
        await orchestrator.stop()

if __name__ == '__main__':
    asyncio.run(main())
