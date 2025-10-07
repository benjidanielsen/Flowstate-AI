import asyncio
import os
import sys
import sqlite3
from pathlib import Path

import pytest
import pytest_asyncio
from aiosqlite import connect as aio_connect

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set environment variables for testing
os.environ["PM_DB_PATH"] = "test-godmode-state.db"

from ai_gods.project_manager_v2 import (
    AgentStatus,
    ProjectManagerV2,
    TaskPriority,
    TaskStatus,
)


# Fixture to provide a clean ProjectManagerV2 instance for each test
@pytest_asyncio.fixture
async def pm_instance():
    """Provides a clean, initialized ProjectManagerV2 instance for each test."""
    db_path = Path(os.environ["PM_DB_PATH"])
    if db_path.exists():
        db_path.unlink()

    pm = ProjectManagerV2()
    # Disable redis for these unit tests
    pm.redis_available = False
    await pm.initialize()

    yield pm

    # Teardown: shutdown and cleanup
    await pm.shutdown()
    if db_path.exists():
        db_path.unlink()


@pytest.mark.asyncio
async def test_create_and_retrieve_task(pm_instance: ProjectManagerV2):
    """
    Tests basic task creation and retrieval.
    """
    pm = pm_instance
    task_name = "Test Task"
    task_description = "A simple task for testing."

    # Create a new task
    created_task = await pm.create_task(
        name=task_name,
        description=task_description,
        priority=TaskPriority.HIGH,
    )

    assert created_task is not None
    assert created_task.name == task_name
    assert created_task.status == TaskStatus.QUEUED

    # Retrieve the task from the in-memory dictionary
    retrieved_task = pm.tasks.get(created_task.id)
    assert retrieved_task is not None
    assert retrieved_task.name == task_name

    # Verify it was written to the database
    async with aio_connect(str(pm.db_path)) as db:
        async with db.execute(
            "SELECT name, description, status FROM tasks WHERE id = ?",
            (created_task.id,),
        ) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == task_name
            assert row[1] == task_description
            assert row[2] == TaskStatus.QUEUED.value


@pytest.mark.asyncio
async def test_register_and_retrieve_agent(pm_instance: ProjectManagerV2):
    """
    Tests agent registration and retrieval.
    """
    pm = pm_instance
    agent_id = "test_agent_001"
    capabilities = ["python", "testing"]

    # Register a new agent
    success = await pm.register_agent(
        agent_id=agent_id, capabilities=capabilities, max_load=5
    )

    assert success is True

    # Retrieve the agent from the in-memory dictionary
    retrieved_agent = pm.agents.get(agent_id)
    assert retrieved_agent is not None
    assert retrieved_agent.agent_id == agent_id
    assert retrieved_agent.capabilities == capabilities
    assert retrieved_agent.max_load == 5

    # Verify it was written to the database
    async with aio_connect(str(pm.db_path)) as db:
        async with db.execute(
            "SELECT agent_id, capabilities, max_load FROM agents WHERE agent_id = ?",
            (agent_id,),
        ) as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == agent_id
            assert row[1] == '["python", "testing"]'
            assert row[2] == 5


@pytest.mark.asyncio
async def test_task_assignment(pm_instance: ProjectManagerV2):
    """
    Tests the assignment of a task to a suitable agent.
    """
    pm = pm_instance

    # Register an agent
    agent_id = "test_agent_002"
    await pm.register_agent(agent_id=agent_id, capabilities=["general"], max_load=2)

    # Create a task
    task = await pm.create_task(
        name="Assignable Task", description="A task to be assigned."
    )
    assert task is not None

    # Manually trigger assignment
    assignment_result = await pm.assign_next_task()

    assert assignment_result is not None
    assigned_task_id, assigned_agent_id = assignment_result

    assert assigned_task_id == task.id
    assert assigned_agent_id == agent_id

    # Verify task status
    assert pm.tasks[task.id].status == TaskStatus.ASSIGNED
    assert pm.tasks[task.id].assigned_to == agent_id

    # Verify agent status
    assert pm.agents[agent_id].current_load == 1
    assert pm.agents[agent_id].status == AgentStatus.ACTIVE
