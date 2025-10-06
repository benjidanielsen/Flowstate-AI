#!/usr/bin/env python3
"""
👶 AGENT SPAWNER
⚡ Births all specialized agents for the Flowstate-AI system
🎯 Mission: Create a complete multi-agent workforce
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from brain.agent_identity_system import AgentIdentitySystem
from brain.agent_communication import AgentCommunication
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AgentSpawner')

def spawn_all_agents():
    """Spawn all specialized agents"""
    
    identity_system = AgentIdentitySystem()
    comm_system = AgentCommunication()
    
    print("=" * 70)
    print("👶 SPAWNING SPECIALIZED AGENTS")
    print("=" * 70)
    print()
    
    # Define all agents to spawn
    agents_to_spawn = [
        {
            'role': 'Project Manager',
            'gender': 'female',
            'description': 'Coordinates all agents, makes strategic decisions, oversees project'
        },
        {
            'role': 'Project Manager Assistant',
            'gender': 'female',
            'description': 'Assists PM with planning, handles routine tasks, escalates issues'
        },
        {
            'role': 'Frontend Specialist',
            'gender': 'female',
            'description': 'React/TypeScript expert, UI/UX design, component development'
        },
        {
            'role': 'Backend Specialist',
            'gender': 'male',
            'description': 'API development, database design, server-side logic'
        },
        {
            'role': 'Testing Specialist',
            'gender': 'female',
            'description': 'QA testing, automated tests, bug detection and reporting'
        },
        {
            'role': 'CRM Support Agent',
            'gender': 'female',
            'description': 'Handles customer feedback, support chat, system improvement suggestions'
        },
        {
            'role': 'DevOps Engineer',
            'gender': 'female',
            'description': 'Deployment, CI/CD, infrastructure, monitoring, scaling'
        },
        {
            'role': 'Database Administrator',
            'gender': 'female',
            'description': 'Database optimization, migrations, data integrity, backups'
        },
        {
            'role': 'Security Specialist',
            'gender': 'male',
            'description': 'Security audits, vulnerability scanning, authentication, encryption'
        },
        {
            'role': 'Documentation Writer',
            'gender': 'female',
            'description': 'Technical writing, API docs, user guides, system documentation'
        }
    ]
    
    spawned_agents = []
    
    for agent_spec in agents_to_spawn:
        # Check if agent already exists
        existing_agents = identity_system.get_all_active_agents()
        exists = any(a['role'] == agent_spec['role'] for a in existing_agents)
        
        if exists:
            print(f"⏭️  {agent_spec['role']} already exists, skipping...")
            continue
        
        # Birth the agent
        agent = identity_system.birth_agent(
            role=agent_spec['role'],
            gender=agent_spec['gender']
        )
        
        spawned_agents.append(agent)
        
        print(f"✅ {agent['agent_number']} - {agent['human_name']} ({agent['gender']})")
        print(f"   Role: {agent['role']}")
        print(f"   Personality: {agent['personality_traits']}")
        print(f"   Photo: {agent['profile_photo_url']}")
        print()
    
    print("=" * 70)
    print(f"✅ SPAWNED {len(spawned_agents)} NEW AGENTS")
    print("=" * 70)
    print()
    
    # Get all active agents
    all_agents = identity_system.get_all_active_agents()
    
    print("📊 AGENT ROSTER:")
    print("-" * 70)
    for agent in all_agents:
        print(f"  {agent['agent_number']} - {agent['human_name']} ({agent['gender']})")
        print(f"    Role: {agent['role']}")
        print(f"    Stats: {agent['tasks_completed']} completed, {agent['tasks_failed']} failed")
    print()
    
    # Set up initial communications
    print("💬 SETTING UP AGENT COMMUNICATIONS...")
    print("-" * 70)
    
    # Find Project Manager and Assistant
    pm = next((a for a in all_agents if a['role'] == 'Project Manager'), None)
    pm_assistant = next((a for a in all_agents if a['role'] == 'Project Manager Assistant'), None)
    
    if pm and pm_assistant:
        # PM welcomes assistant
        comm_system.send_message(
            pm['human_name'],
            pm_assistant['human_name'],
            'status_update',
            'Welcome to the Team!',
            f"Hi {pm_assistant['human_name']}! I'm {pm['human_name']}, the Project Manager. "
            f"You'll be my assistant. Let's coordinate closely to keep everything running smoothly!",
            priority=3
        )
        print(f"  ✅ {pm['human_name']} → {pm_assistant['human_name']}: Welcome message")
        
        # Assistant acknowledges
        comm_system.send_message(
            pm_assistant['human_name'],
            pm['human_name'],
            'acknowledgment',
            'Ready to Assist!',
            f"Thank you {pm['human_name']}! I'm ready to help with planning, coordination, "
            f"and any routine tasks. I'll escalate important issues to you immediately.",
            priority=3
        )
        print(f"  ✅ {pm_assistant['human_name']} → {pm['human_name']}: Acknowledgment")
    
    # PM broadcasts to all agents
    if pm:
        comm_system.broadcast_message(
            pm['human_name'],
            'status_update',
            'Team Introduction',
            f"Hello everyone! I'm {pm['human_name']}, your Project Manager. "
            f"We have an amazing team assembled. Let's work together to build something incredible! "
            f"Feel free to reach out if you need anything.",
            priority=5
        )
        print(f"  ✅ {pm['human_name']}: Broadcast to all agents")
    
    print()
    print("=" * 70)
    print("🎉 AGENT SPAWNING COMPLETE!")
    print("=" * 70)
    print()
    print(f"Total Active Agents: {len(all_agents)}")
    print(f"Female Agents: {sum(1 for a in all_agents if a['gender'] == 'female')}")
    print(f"Male Agents: {sum(1 for a in all_agents if a['gender'] == 'male')}")
    print()
    print("✅ All agents are ready to work!")
    print("✅ Communication system is operational!")
    print("✅ Multi-agent collaboration enabled!")
    print()

if __name__ == "__main__":
    spawn_all_agents()
