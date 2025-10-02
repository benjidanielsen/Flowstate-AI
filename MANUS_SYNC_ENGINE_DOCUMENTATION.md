# MANUS_SYNC_ENGINE Documentation

## Overview

The **MANUS_SYNC_ENGINE** is a real-time coordination system designed to enable multiple Manus instances to work together at maximum speed with perfect synchronization and zero conflicts. This document provides comprehensive guidance on its architecture, features, usage, and best practices.

## Table of Contents

1. [Architecture](#architecture)
2. [Core Features](#core-features)
3. [Data Models](#data-models)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Performance Optimization](#performance-optimization)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Architecture

The MANUS_SYNC_ENGINE employs a centralized coordination model using SQLite as the synchronization database. The architecture consists of several key components that work together to provide seamless multi-instance coordination.

### Core Components

The system comprises four primary components. The **Sync Engine** serves as the central coordinator managing all Manus instances, tasks, and file locks. **Manus Instances** represent individual AI agents registered with the engine, each possessing unique capabilities and roles. The **Task Queue** maintains a prioritized list of tasks with automatic assignment based on instance capabilities and workload. Finally, the **File Locking System** prevents conflicts by ensuring exclusive file access when needed.

### Database Schema

The synchronization database contains four main tables. The `manus_instances` table stores information about registered Manus instances including their ID, role, capabilities, current task, status, progress, claimed files, last heartbeat timestamp, and performance score. The `sync_tasks` table tracks all tasks with details such as ID, title, description, assigned instance, priority level, status, dependencies, estimated duration, timestamps for creation, start, and completion, and involved files. The `file_locks` table manages file access control with file path, locking instance, lock timestamp, and lock reason. The `communication_log` table records inter-instance messages including sender, recipient, message type, content, timestamp, and processing status.

## Core Features

### Real-time Task Distribution

The engine automatically assigns tasks to the most suitable Manus instance based on multiple factors. The assignment algorithm considers current workload by evaluating how many tasks each instance is currently handling. It matches capabilities by checking if the instance has the required skills for the task. Performance history is factored in through the instance's performance score. File conflicts are avoided by checking if required files are already locked by another instance.

### Automatic Conflict Resolution

The system prevents conflicts through several mechanisms. File locking ensures exclusive access to files when needed. Dependency tracking prevents tasks from starting before their dependencies are completed. Task prioritization allows critical tasks to take precedence. Intelligent reassignment moves tasks if an instance becomes unavailable.

### Performance Optimization

Performance is enhanced through various optimization techniques. In-memory caching reduces database queries significantly. Batch operations minimize database transactions. Connection pooling improves resource management. Lazy loading loads data only when needed. The optimized version reduces database queries by approximately ninety percent.

### Live Progress Tracking

The system provides comprehensive real-time monitoring capabilities. Heartbeat monitoring tracks instance availability and responsiveness. Task progress is monitored with percentage completion tracking. Performance metrics include task completion rates and time tracking. System health monitoring provides overall system status and health scores.

## Data Models

### ManusRole Enumeration

The system defines four primary roles for Manus instances. The **SPEED_DEVELOPER** role focuses on rapid development and quick iterations. The **QUALITY_ENHANCER** role emphasizes code quality, testing, and optimization. The **AI_SPECIALIST** role handles AI-specific tasks and integrations. The **COORDINATOR** role manages overall project coordination and planning.

### TaskPriority Enumeration

Tasks are assigned one of four priority levels. **CRITICAL** priority with value one indicates must be completed immediately. **HIGH** priority with value two represents important tasks requiring prompt attention. **MEDIUM** priority with value three denotes standard priority tasks. **LOW** priority with value four indicates tasks that can be deferred.

### TaskStatus Enumeration

Tasks progress through several status states. **PENDING** indicates the task is waiting to be started. **IN_PROGRESS** means the task is currently being worked on. **COMPLETED** shows the task has been finished successfully. **BLOCKED** indicates the task cannot proceed due to dependencies or issues. **NEEDS_REVIEW** means the task requires review before completion.

### ManusInstance Dataclass

Each Manus instance is represented by a dataclass containing essential information. The unique identifier distinguishes each instance. The role defines the instance's primary function. Capabilities list the skills and technologies the instance can handle. The current task field shows which task is currently assigned. Status indicates whether the instance is active or idle. Progress shows the completion percentage of the current task. Files claimed lists files currently locked by this instance. Last heartbeat records the timestamp of the last activity. Performance score reflects the instance's historical performance rating.

### SyncTask Dataclass

Tasks are represented with comprehensive metadata. The unique identifier distinguishes each task. The title provides a brief description. The description offers detailed information about the task. Assigned to indicates which Manus instance is responsible. Priority defines the task's urgency level. Status shows the current state of the task. Dependencies list tasks that must be completed first. Estimated duration indicates expected completion time in minutes. Created at records when the task was created. Started at shows when work began. Completed at indicates when the task finished. Files involved lists files related to the task.

## API Reference

### ManusSyncEngine Class

#### Initialization

```python
engine = ManusSyncEngine(project_root=".")
```

The constructor initializes the sync engine with the specified project root directory. It creates the necessary database structure and loads the current state from the database.

#### register_manus

```python
success = engine.register_manus(
    manus_id="manus_1",
    role=ManusRole.COORDINATOR,
    capabilities=["python", "planning", "coordination"]
)
```

This method registers a new Manus instance with the engine. It requires a unique identifier, a role from the ManusRole enumeration, and a list of capability strings. The method returns True if registration succeeds, False otherwise.

#### create_task

```python
task_id = engine.create_task(
    title="Implement feature X",
    description="Detailed description of the task",
    priority=TaskPriority.HIGH,
    files_involved=["file1.py", "file2.py"],
    dependencies=["task_id_1"],
    estimated_duration=120
)
```

This method creates a new task and automatically assigns it to the most suitable Manus instance. It requires a title and description, accepts a priority level, optional list of involved files, optional list of dependency task IDs, and estimated duration in minutes. The method returns the unique task identifier.

#### heartbeat

```python
engine.heartbeat(manus_id="manus_1")
```

This method updates the last heartbeat timestamp for a Manus instance, indicating it is still active and responsive. It should be called periodically by each Manus instance.

#### claim_files

```python
success = engine.claim_files(
    manus_id="manus_1",
    files=["file1.py", "file2.py"]
)
```

This method attempts to claim exclusive access to specified files. It returns True if all files were successfully claimed, False if any file is already locked by another instance.

#### release_files

```python
engine.release_files(
    manus_id="manus_1",
    files=["file1.py", "file2.py"]
)
```

This method releases previously claimed files, making them available for other instances.

#### start_task

```python
success = engine.start_task(
    manus_id="manus_1",
    task_id="abc123"
)
```

This method marks a task as in progress. It returns True if the task was successfully started, False if the task is not assigned to this instance or is already in progress.

#### complete_task

```python
success = engine.complete_task(
    task_id="abc123"
)
```

This method marks a task as completed and updates relevant metrics.

#### send_message

```python
engine.send_message(
    from_manus="manus_1",
    to_manus="manus_2",
    message_type="TASK_ASSIGNMENT",
    content={"task_id": "abc123", "details": "..."}
)
```

This method sends a message from one Manus instance to another for coordination purposes.

#### get_messages

```python
messages = engine.get_messages(manus_id="manus_1")
```

This method retrieves unprocessed messages for a specific Manus instance and marks them as processed.

## Usage Examples

### Basic Setup

```python
from MANUS_SYNC_ENGINE import ManusSyncEngine, ManusRole, TaskPriority

# Initialize the engine
engine = ManusSyncEngine(project_root="/path/to/project")

# Register Manus instances
engine.register_manus(
    manus_id="manus_speed",
    role=ManusRole.SPEED_DEVELOPER,
    capabilities=["python", "javascript", "rapid_prototyping"]
)

engine.register_manus(
    manus_id="manus_quality",
    role=ManusRole.QUALITY_ENHANCER,
    capabilities=["testing", "optimization", "code_review"]
)
```

### Creating and Managing Tasks

```python
# Create a high-priority task
task_id = engine.create_task(
    title="Implement user authentication",
    description="Add JWT-based authentication to the API",
    priority=TaskPriority.HIGH,
    files_involved=["auth.py", "middleware.py"],
    estimated_duration=180
)

# Start working on the task
engine.start_task(manus_id="manus_speed", task_id=task_id)

# Update progress
engine.update_task_progress(
    manus_id="manus_speed",
    task_id=task_id,
    progress=50
)

# Complete the task
engine.complete_task(task_id=task_id)
```

### File Locking

```python
# Claim files before modifying
if engine.claim_files(manus_id="manus_speed", files=["auth.py"]):
    # Perform file operations
    # ...
    
    # Release files when done
    engine.release_files(manus_id="manus_speed", files=["auth.py"])
else:
    print("Files are locked by another instance")
```

### Inter-Instance Communication

```python
# Send a message
engine.send_message(
    from_manus="manus_speed",
    to_manus="manus_quality",
    message_type="CODE_REVIEW_REQUEST",
    content={
        "files": ["auth.py"],
        "description": "Please review authentication implementation"
    }
)

# Receive messages
messages = engine.get_messages(manus_id="manus_quality")
for msg in messages:
    print(f"Message from {msg['from_manus']}: {msg['content']}")
```

## Performance Optimization

### Using the Optimized Engine

The optimized version of the MANUS_SYNC_ENGINE provides significant performance improvements through caching and reduced database operations.

```python
from MANUS_SYNC_ENGINE_OPTIMIZED import OptimizedManusSyncEngine

# Use the optimized engine
engine = OptimizedManusSyncEngine(project_root="/path/to/project")

# API remains the same
engine.register_manus(...)
engine.create_task(...)
```

### Performance Improvements

The optimized engine provides approximately ninety percent reduction in database queries through in-memory caching. Batch operations reduce database transactions significantly. Connection pooling improves resource utilization. Lazy loading minimizes unnecessary data retrieval. Cache TTL of ten seconds balances freshness with performance.

## Best Practices

### Heartbeat Management

Each Manus instance should send heartbeats regularly, ideally every thirty to sixty seconds. This ensures the system can detect unresponsive instances and reassign their tasks if necessary.

### Task Granularity

Tasks should be appropriately sized, typically ranging from thirty minutes to four hours of estimated work. Very large tasks should be broken down into smaller subtasks. Very small tasks create unnecessary overhead.

### File Locking Strategy

Files should be claimed only when necessary and released as soon as possible. Avoid holding locks for extended periods. Consider using finer-grained locking for large files.

### Error Handling

Always implement proper error handling when interacting with the sync engine. Check return values from operations like claim_files and start_task. Handle database connection errors gracefully.

### Resource Cleanup

Ensure proper cleanup when a Manus instance terminates. Release all claimed files. Mark in-progress tasks as pending or blocked. Send a final heartbeat with inactive status.

## Troubleshooting

### Common Issues

**Excessive Database Queries**: If you notice performance degradation due to frequent database access, consider using the OptimizedManusSyncEngine which implements caching and batch operations.

**File Lock Conflicts**: If tasks frequently fail to claim files, review your file locking strategy. Ensure files are released promptly and consider breaking tasks into smaller units with fewer file dependencies.

**Stale Instances**: If instances appear stale despite being active, verify that heartbeats are being sent regularly. Check for network or database connectivity issues.

**Task Assignment Issues**: If tasks are not being assigned optimally, review the capabilities defined for each Manus instance. Ensure they accurately reflect the instance's abilities.

### Debugging Tips

Enable verbose logging to track database operations and task assignments. Monitor the communication_log table to understand inter-instance messaging. Use the dashboard at localhost:3334 to visualize system state in real-time. Check the last_heartbeat timestamps to identify unresponsive instances.

## Conclusion

The MANUS_SYNC_ENGINE provides a robust foundation for coordinating multiple AI agents working on a shared project. By following the guidelines and best practices outlined in this documentation, you can achieve efficient, conflict-free collaboration between Manus instances while maintaining high performance and reliability.
