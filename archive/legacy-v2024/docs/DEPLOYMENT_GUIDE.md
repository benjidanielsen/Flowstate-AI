# Flowstate-AI v2030 Deployment Guide

## Overview

This guide covers the deployment and testing of the Flowstate-AI v2030 agent-based CRM-OS system with Supabase integration.

## System Architecture

The system consists of three main components:

1. **Supabase Database**: PostgreSQL database with three core tables
   - `agent_states`: Stores agent state and metadata
   - `documents`: Stores agent memories and knowledge
   - `job_queue`: Manages inter-agent communication and task distribution

2. **Backend (Node.js/TypeScript)**: API server that manages database operations
   - Agent registration and state management
   - Job queue processing
   - Memory storage and retrieval
   - RESTful API endpoints

3. **Python Worker**: AI agent execution environment
   - Specialized agents (Code Analyzer, Data Processor, Coordinator, Learning Agent, Monitoring Agent)
   - Job processing and task execution
   - Inter-agent communication
   - Memory management

## Prerequisites

- Node.js 22.13.0 or higher
- Python 3.11 or higher
- Supabase project with credentials
- PostgreSQL database access

## Database Setup

The database schema has already been created in Supabase with the following tables:

### agent_states
```sql
CREATE TABLE agent_states (
  id SERIAL PRIMARY KEY,
  agent_name TEXT NOT NULL,
  state JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### documents
```sql
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  content TEXT,
  metadata JSONB,
  embedding TEXT
);
```

### job_queue
```sql
CREATE TABLE job_queue (
  id SERIAL PRIMARY KEY,
  payload JSONB NOT NULL,
  target_agent TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  attempts INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP
);
```

## Installation

### Backend Setup

```bash
cd /home/ubuntu/Flowstate-AI/backend

# Install dependencies
pnpm install

# Environment variables are already configured in .env file
# DATABASE_URL, SUPABASE_URL, SUPABASE_ANON_KEY, etc.

# Build the TypeScript code
pnpm build

# Start the backend server
pnpm start
```

### Python Worker Setup

```bash
cd /home/ubuntu/Flowstate-AI/python-worker

# Install dependencies
pip3 install -r requirements.txt

# Install additional required packages
pip3 install httpx

# Environment variables
export BACKEND_API_URL="http://localhost:3001"
export PYTHON_API_PORT="8000"

# Start the Python worker
python3 src/main_updated.py
```

## Agent System Components

### Core Services

1. **AgentService** (`backend/src/services/agentService.ts`)
   - Agent registration and state management
   - Job queue operations
   - Document storage and retrieval

2. **JobProcessorService** (`backend/src/services/jobProcessorService.ts`)
   - Automatic job processing
   - Inter-agent message routing
   - Retry logic and error handling

3. **MemoryService** (`backend/src/services/memoryService.ts`)
   - Memory storage and categorization
   - Conversation history tracking
   - Learning and task result storage

### Specialized Agents

1. **CodeAnalyzerAgent**
   - Capabilities: code_analysis, optimization, bug_detection
   - Tasks: analyze_code, detect_bugs, suggest_optimizations

2. **DataProcessorAgent**
   - Capabilities: data_processing, transformation, validation
   - Tasks: process_data, validate_data, transform_data

3. **CoordinatorAgent**
   - Capabilities: coordination, workflow_management, task_delegation
   - Tasks: delegate_task, coordinate_workflow

4. **LearningAgent**
   - Capabilities: learning, pattern_recognition, performance_optimization
   - Tasks: learn_from_feedback, identify_patterns, optimize_performance

5. **MonitoringAgent**
   - Capabilities: monitoring, alerting, health_checks
   - Tasks: health_check, check_metrics, send_alert

## API Endpoints

### Backend API (Port 3001)

#### Agent Management
- `POST /api/agents/register` - Register a new agent
- `GET /api/agents` - Get all agents
- `GET /api/agents/:agentName` - Get agent state
- `PUT /api/agents/:agentName` - Update agent state

#### Job Queue
- `POST /api/jobs` - Create a new job
- `GET /api/jobs/pending` - Get all pending jobs
- `GET /api/jobs/agent/:agentName` - Get pending jobs for an agent
- `PUT /api/jobs/:jobId/status` - Update job status

#### Documents/Memory
- `POST /api/documents` - Store a document
- `GET /api/documents/:id` - Get a document
- `GET /api/documents/search` - Search documents

### Python Worker API (Port 8000)

#### Agent Operations
- `GET /agents` - List all agents and capabilities
- `GET /agents/{agent_name}/status` - Get agent status
- `POST /agents/{agent_name}/task` - Execute a task on an agent
- `POST /agents/message` - Send inter-agent message
- `POST /agents/{agent_name}/memory` - Store agent memory

#### Workflow
- `POST /workflow/coordinate` - Coordinate a multi-step workflow

#### System
- `GET /health` - Health check
- `POST /system/health-check` - Comprehensive system health check

## Testing

### Running the Test Suite

```bash
cd /home/ubuntu/Flowstate-AI/python-worker

# Make sure the backend is running first
# Then run the test suite
python3 test_agent_system.py
```

The test suite covers:
1. Agent registration
2. Memory storage
3. Inter-agent communication
4. Job processing
5. Task delegation
6. Workflow coordination
7. System monitoring
8. State management

### Manual Testing Examples

#### 1. Register an Agent
```bash
curl -X POST http://localhost:3001/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agentName": "test_agent",
    "initialState": {
      "status": "active",
      "capabilities": ["testing"]
    }
  }'
```

#### 2. Create a Job
```bash
curl -X POST http://localhost:3001/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "targetAgent": "code_analyzer",
    "payload": {
      "type": "ai_task",
      "taskType": "analyze_code",
      "data": {
        "code": "def hello(): print(\"Hello, World!\")"
      }
    }
  }'
```

#### 3. Send Inter-Agent Message
```bash
curl -X POST http://localhost:8000/agents/message \
  -H "Content-Type: application/json" \
  -d '{
    "from_agent": "coordinator",
    "to_agent": "code_analyzer",
    "message": "Please analyze the latest code submission",
    "message_type": "task_request",
    "requires_response": true
  }'
```

#### 4. Execute a Task
```bash
curl -X POST http://localhost:8000/agents/code_analyzer/task \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "code_analyzer",
    "task_description": "Analyze code quality",
    "context": {
      "taskType": "analyze_code",
      "code": "def process_data(data): return data"
    }
  }'
```

#### 5. Store a Memory
```bash
curl -X POST http://localhost:8000/agents/code_analyzer/memory \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Learned that type hints improve code quality",
    "memory_type": "learning",
    "tags": ["learning", "best_practices"],
    "importance": 9
  }'
```

## Monitoring and Debugging

### Logs

Backend logs:
```bash
# View backend logs
cd /home/ubuntu/Flowstate-AI/backend
pnpm start | tee backend.log
```

Python worker logs:
```bash
# View Python worker logs
cd /home/ubuntu/Flowstate-AI/python-worker
python3 src/main_updated.py | tee worker.log
```

### Database Queries

Check agent states:
```sql
SELECT * FROM agent_states ORDER BY updated_at DESC;
```

Check pending jobs:
```sql
SELECT * FROM job_queue WHERE status = 'pending' ORDER BY created_at;
```

Check recent memories:
```sql
SELECT * FROM documents WHERE metadata->>'agentName' = 'code_analyzer' 
ORDER BY metadata->>'timestamp' DESC LIMIT 10;
```

## Job Processing Flow

1. **Job Creation**: A job is created via the API and stored in the `job_queue` table
2. **Job Discovery**: The JobProcessorService polls for pending jobs every 5 seconds
3. **Job Assignment**: Jobs are assigned to the target agent specified in the job
4. **Job Execution**: The agent executes the task and updates the job status
5. **Result Storage**: Results are stored in the agent's state and/or documents table
6. **Completion**: Job status is updated to 'completed' or 'failed'

## Inter-Agent Communication Flow

1. **Message Creation**: Agent A sends a message to Agent B via the `send_message` method
2. **Job Creation**: A job is created in the queue with type 'inter_agent_message'
3. **Job Processing**: Agent B's job processor picks up the message
4. **Message Handling**: Agent B processes the message via `handle_message`
5. **Memory Storage**: The message is stored in Agent B's memory
6. **Response (Optional)**: If response is required, Agent B creates a job for Agent A

## Memory System

### Memory Types
- `general`: General-purpose memories
- `conversation`: Conversation history
- `task_result`: Task execution results
- `learning`: Learnings and insights

### Memory Importance Levels
- 1-3: Low importance
- 4-6: Medium importance
- 7-9: High importance
- 10: Critical importance

### Memory Retrieval
Memories are retrieved based on:
- Agent name
- Memory type
- Tags
- Importance level
- Timestamp (recency)

## Troubleshooting

### Backend won't start
- Check DATABASE_URL in .env file
- Verify Supabase credentials
- Ensure PostgreSQL is accessible
- Check port 3001 is available

### Python worker won't start
- Check BACKEND_API_URL environment variable
- Verify Python dependencies are installed
- Check port 8000 is available
- Ensure backend is running first

### Agents not processing jobs
- Check job_queue table for pending jobs
- Verify JobProcessorService is running
- Check agent registration status
- Review backend and worker logs

### Database connection errors
- Verify DATABASE_URL format
- Check Supabase project is active
- Verify network connectivity
- Check database credentials

## Next Steps

1. **Implement Vector Embeddings**: Add pgvector extension for semantic search
2. **Add Authentication**: Implement JWT authentication for API endpoints
3. **Deploy to Production**: Set up production environment with proper secrets
4. **Add More Agents**: Create specialized agents for specific tasks
5. **Implement CI/CD**: Set up GitHub Actions for automated testing and deployment
6. **Add Monitoring**: Integrate with monitoring tools (Prometheus, Grafana)
7. **Scale Horizontally**: Deploy multiple worker instances for load balancing

## References

- [Supabase Documentation](https://supabase.com/docs)
- [Drizzle ORM Documentation](https://orm.drizzle.team/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Express.js Documentation](https://expressjs.com/)

## Support

For issues and questions:
- Check the logs for error messages
- Review the database tables for data integrity
- Test individual components in isolation
- Consult the project roadmap documents in `/home/ubuntu/upload/`

