"""
Test script for the Flowstate-AI v2030 agent system
Tests agent registration, job processing, inter-agent communication, and memory
"""

import asyncio
import logging
from evolution_framework.specialized_agents import (
    CodeAnalyzerAgent,
    DataProcessorAgent,
    CoordinatorAgent,
    LearningAgent,
    MonitoringAgent,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_agent_registration():
    """Test registering all agents"""
    logger.info("=" * 60)
    logger.info("TEST 1: Agent Registration")
    logger.info("=" * 60)
    
    agents = [
        CodeAnalyzerAgent(),
        DataProcessorAgent(),
        CoordinatorAgent(),
        LearningAgent(),
        MonitoringAgent(),
    ]
    
    for agent in agents:
        try:
            result = await agent.register()
            logger.info(f"✓ Successfully registered {agent.agent_name}")
            logger.info(f"  State: {result.get('state', {})}")
        except Exception as e:
            logger.error(f"✗ Failed to register {agent.agent_name}: {e}")
    
    return agents


async def test_memory_storage(agents):
    """Test storing memories for agents"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Memory Storage")
    logger.info("=" * 60)
    
    code_analyzer = agents[0]
    
    try:
        # Store different types of memories
        await code_analyzer.store_memory(
            content="Analyzed Python code with 95% quality score",
            memory_type="task_result",
            tags=["code_analysis", "success"],
            importance=7,
        )
        logger.info(f"✓ Stored task result memory for {code_analyzer.agent_name}")
        
        await code_analyzer.store_memory(
            content="Learned that type hints improve code maintainability",
            memory_type="learning",
            tags=["learning", "best_practices"],
            importance=9,
        )
        logger.info(f"✓ Stored learning memory for {code_analyzer.agent_name}")
        
        await code_analyzer.store_memory(
            content="User asked about code optimization techniques",
            memory_type="conversation",
            tags=["conversation", "user_interaction"],
            importance=6,
        )
        logger.info(f"✓ Stored conversation memory for {code_analyzer.agent_name}")
        
    except Exception as e:
        logger.error(f"✗ Failed to store memories: {e}")


async def test_inter_agent_communication(agents):
    """Test inter-agent communication"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Inter-Agent Communication")
    logger.info("=" * 60)
    
    coordinator = agents[2]
    code_analyzer = agents[0]
    data_processor = agents[1]
    
    try:
        # Coordinator sends message to code analyzer
        await coordinator.send_message(
            to_agent=code_analyzer.agent_name,
            message="Please analyze the latest code submission",
            message_type="task_request",
            requires_response=True,
        )
        logger.info(f"✓ Coordinator sent message to {code_analyzer.agent_name}")
        
        # Coordinator sends message to data processor
        await coordinator.send_message(
            to_agent=data_processor.agent_name,
            message="Process the customer data from yesterday",
            message_type="task_request",
            requires_response=True,
        )
        logger.info(f"✓ Coordinator sent message to {data_processor.agent_name}")
        
    except Exception as e:
        logger.error(f"✗ Failed to send inter-agent messages: {e}")


async def test_job_processing(agents):
    """Test job processing"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Job Processing")
    logger.info("=" * 60)
    
    code_analyzer = agents[0]
    data_processor = agents[1]
    
    try:
        # Process jobs for code analyzer
        logger.info(f"Processing jobs for {code_analyzer.agent_name}...")
        results = await code_analyzer.process_jobs(max_jobs=5)
        logger.info(f"✓ Processed {len(results)} jobs for {code_analyzer.agent_name}")
        for result in results:
            logger.info(f"  Job {result['job_id']}: {result['status']}")
        
        # Process jobs for data processor
        logger.info(f"Processing jobs for {data_processor.agent_name}...")
        results = await data_processor.process_jobs(max_jobs=5)
        logger.info(f"✓ Processed {len(results)} jobs for {data_processor.agent_name}")
        for result in results:
            logger.info(f"  Job {result['job_id']}: {result['status']}")
        
    except Exception as e:
        logger.error(f"✗ Failed to process jobs: {e}")


async def test_task_delegation(agents):
    """Test task delegation through coordinator"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Task Delegation")
    logger.info("=" * 60)
    
    coordinator = agents[2]
    
    try:
        # Delegate code analysis task
        result = await coordinator.delegate_task(
            target_agent="code_analyzer",
            task_payload={
                "description": "Analyze code quality for main.py",
                "taskType": "analyze_code",
                "code": "def hello(): print('Hello, World!')",
            },
        )
        logger.info(f"✓ Delegated code analysis task: {result}")
        
        # Delegate data processing task
        result = await coordinator.delegate_task(
            target_agent="data_processor",
            task_payload={
                "description": "Process customer data",
                "taskType": "process_data",
                "data": {"customer_id": "123", "name": "John Doe"},
            },
        )
        logger.info(f"✓ Delegated data processing task: {result}")
        
    except Exception as e:
        logger.error(f"✗ Failed to delegate tasks: {e}")


async def test_workflow_coordination(agents):
    """Test multi-step workflow coordination"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Workflow Coordination")
    logger.info("=" * 60)
    
    coordinator = agents[2]
    
    try:
        workflow = {
            "name": "Code Review Workflow",
            "steps": [
                {
                    "agent": "code_analyzer",
                    "task": {
                        "description": "Analyze code quality",
                        "taskType": "analyze_code",
                        "code": "def process_data(data): return data",
                    },
                },
                {
                    "agent": "data_processor",
                    "task": {
                        "description": "Validate test data",
                        "taskType": "validate_data",
                        "data": {"test": "data"},
                    },
                },
                {
                    "agent": "learning_agent",
                    "task": {
                        "description": "Learn from code review results",
                        "taskType": "learn_from_feedback",
                        "feedback": {"message": "Code quality is good"},
                    },
                },
            ],
        }
        
        result = await coordinator.coordinate_workflow(workflow)
        logger.info(f"✓ Coordinated workflow with {len(workflow['steps'])} steps")
        logger.info(f"  Results: {result}")
        
    except Exception as e:
        logger.error(f"✗ Failed to coordinate workflow: {e}")


async def test_monitoring(agents):
    """Test monitoring agent"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: System Monitoring")
    logger.info("=" * 60)
    
    monitoring_agent = agents[4]
    
    try:
        # Perform health check
        result = await monitoring_agent.perform_health_check()
        logger.info(f"✓ Health check completed: {result}")
        
        # Send test alert
        result = await monitoring_agent.send_alert({
            "severity": "info",
            "message": "Test alert from monitoring system",
        })
        logger.info(f"✓ Alert sent: {result}")
        
    except Exception as e:
        logger.error(f"✗ Failed monitoring tests: {e}")


async def test_state_management(agents):
    """Test agent state management"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 8: State Management")
    logger.info("=" * 60)
    
    code_analyzer = agents[0]
    
    try:
        # Get current state
        state = await code_analyzer.get_state()
        logger.info(f"✓ Retrieved state for {code_analyzer.agent_name}")
        logger.info(f"  Current state: {state}")
        
        # Update state
        new_state = {
            **state,
            "tasks_completed": (state.get("tasks_completed", 0) + 1),
            "last_activity": "Code analysis completed",
        }
        result = await code_analyzer.update_state(new_state)
        logger.info(f"✓ Updated state for {code_analyzer.agent_name}")
        logger.info(f"  New state: {result.get('state', {})}")
        
    except Exception as e:
        logger.error(f"✗ Failed state management tests: {e}")


async def main():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("FLOWSTATE-AI V2030 AGENT SYSTEM TEST SUITE")
    logger.info("=" * 60 + "\n")
    
    try:
        # Test 1: Register agents
        agents = await test_agent_registration()
        
        # Test 2: Memory storage
        await test_memory_storage(agents)
        
        # Test 3: Inter-agent communication
        await test_inter_agent_communication(agents)
        
        # Test 4: Job processing
        await test_job_processing(agents)
        
        # Test 5: Task delegation
        await test_task_delegation(agents)
        
        # Test 6: Workflow coordination
        await test_workflow_coordination(agents)
        
        # Test 7: Monitoring
        await test_monitoring(agents)
        
        # Test 8: State management
        await test_state_management(agents)
        
        logger.info("\n" + "=" * 60)
        logger.info("ALL TESTS COMPLETED")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

