# Flowstate-AI v2030 Architecture Blueprint

This document outlines the core architectural design and principles guiding the development of Flowstate-AI v2030, an autonomous, self-evolving CRM-OS.

## 1. Core Principles

The system is built on several foundational principles:

-   **Autonomous Evolution**: The system can modify and improve itself over time.
-   **Multi-Agent Architecture**: Specialized AI agents work collaboratively to achieve complex goals.
-   **Collective Memory with Semantic Search**: Agents share a common knowledge base, powered by vector embeddings and semantic search for efficient information retrieval.
-   **Inter-Agent Communication**: A robust job queue system facilitates seamless and asynchronous communication between agents.
-   **Continuous Learning**: Agents learn from experiences and feedback, adapting their strategies and parameters.
-   **Modularity and Extensibility**: Designed for easy addition of new agents, services, and integrations.

## 2. System Layers

Flowstate-AI v2030 comprises three main layers, ensuring a clear separation of concerns and scalability:

### 2.1. Database Layer

-   **Technology**: Supabase (PostgreSQL with `pgvector` extension).
-   **Purpose**: Persistent data storage, real-time capabilities, and vector embeddings for semantic search.
-   **Key Tables**:
    -   `agent_states`: Stores the state and metadata for each AI agent.
    -   `documents`: Stores agent memories and knowledge with vector embeddings.
    -   `job_queue`: Manages inter-agent communication and task distribution.

### 2.2. Backend Layer (Node.js/TypeScript)

-   **Technology**: Express.js for RESTful APIs, Drizzle ORM for type-safe database operations, `postgres-js` for PostgreSQL client.
-   **Purpose**: Acts as the central hub for agent interactions with the database and external services. Manages agent lifecycle, job processing, and memory services.
-   **Key Services**:
    -   `AgentService`: Manages agent registration, state updates, and job creation.
    -   `JobProcessorService`: Handles job queue polling, processing, and inter-agent message routing.
    -   `MemoryService`: Manages agent memory storage and retrieval.
    -   `EmbeddingService`: Generates vector embeddings for text using OpenAI API.
    -   `VectorSearchService`: Provides semantic search, similarity search, hybrid search, recommendations, and clustering.
    -   `WorkflowOrchestrationService`: Orchestrates complex multi-agent workflows.

### 2.3. AI Worker Layer (Python)

-   **Technology**: FastAPI for high-performance asynchronous API framework, `httpx` for backend communication.
-   **Purpose**: Execution environment for the AI agents. Hosts specialized agents, handles job execution, and facilitates inter-agent communication.
-   **Key Components**:
    -   `AgentBase` class: Provides core functionality for all agents (registration, state management, job processing, memory interaction).
    -   `Specialized Agents`: Implement specific functionalities (e.g., `CodeAnalyzerAgent`, `DataProcessorAgent`, `CoordinatorAgent`, `LearningAgent`, `MonitoringAgent`).

## 3. Inter-Agent Communication Flow

Agents communicate asynchronously through the `job_queue`:

1.  **Task Initiation**: An agent (or external system) creates a job in the `job_queue` table via the `AgentService`.
2.  **Job Processing**: The `JobProcessorService` in the backend continuously polls for pending jobs.
3.  **Delegation**: When a job is picked up, it's routed to the appropriate Python AI agent based on `target_agent`.
4.  **Execution**: The Python agent processes the job, executes its task, and updates the job status.
5.  **Feedback/New Task**: The agent can store new memories, update its state, or create new jobs for other agents, forming a continuous feedback loop.

## 4. Memory System and Semantic Search

The `documents` table serves as the collective memory for all agents. It stores content with associated metadata and vector embeddings.

-   **Embedding Generation**: The `EmbeddingService` generates 1536-dimensional embeddings for textual content using OpenAI's `text-embedding-3-small` model.
-   **Semantic Search**: The `VectorSearchService` leverages `pgvector` to perform highly efficient semantic similarity searches, allowing agents to retrieve relevant information from their collective memory based on meaning, not just keywords.

## 5. Workflow Orchestration

The `WorkflowOrchestrationService` enables the definition and execution of complex multi-agent workflows. It supports:

-   Dependency-based step execution.
-   Parallel execution of independent steps.
-   Retry logic for failed steps.
-   Timeout handling.
-   Predefined workflow templates for common tasks.

---

**Document Version**: 1.0  
**Last Updated**: October 17, 2025  
**Prepared by**: Manus AI

