"""
Base Agent class for Flowstate-AI v2030
Integrates with Supabase backend for state management, job processing, and memory
"""

import logging
import httpx
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class AgentBase:
    """
    Base class for all AI agents in the Flowstate-AI system.
    Provides core functionality for state management, job processing, and memory.
    """

    def __init__(self, agent_name: str, capabilities: List[str], backend_url: Optional[str] = None):
        """
        Initialize the agent.
        
        Args:
            agent_name: Unique name for this agent
            capabilities: List of capabilities this agent possesses
            backend_url: URL of the backend API (defaults to BACKEND_API_URL env var)
        """
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.backend_url = backend_url or os.getenv("BACKEND_API_URL", "http://localhost:3001")
        self.logger = logging.getLogger(f"agent.{agent_name}")
        self.state: Dict[str, Any] = {}
        
        self.logger.info(f"Initializing agent {agent_name} with capabilities: {capabilities}")

    async def register(self, initial_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Register this agent with the backend.
        
        Args:
            initial_state: Initial state for the agent
            
        Returns:
            The registered agent data
        """
        try:
            state_data = initial_state or {
                "capabilities": self.capabilities,
                "status": "active",
                "registered_at": datetime.now().isoformat(),
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/agents/register",
                    json={
                        "agentName": self.agent_name,
                        "initialState": state_data,
                    },
                )
                response.raise_for_status()
                result = response.json()
                
            self.state = result.get("state", {})
            self.logger.info(f"Agent {self.agent_name} registered successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error registering agent: {e}")
            raise

    async def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of this agent from the backend.
        
        Returns:
            The agent's current state
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/api/agents/{self.agent_name}"
                )
                response.raise_for_status()
                result = response.json()
                
            self.state = result.get("state", {})
            return self.state
            
        except Exception as e:
            self.logger.error(f"Error getting agent state: {e}")
            raise

    async def update_state(self, new_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the state of this agent.
        
        Args:
            new_state: New state data
            
        Returns:
            The updated agent data
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.backend_url}/api/agents/{self.agent_name}",
                    json={"state": new_state},
                )
                response.raise_for_status()
                result = response.json()
                
            self.state = result.get("state", {})
            self.logger.info(f"Agent {self.agent_name} state updated")
            return result
            
        except Exception as e:
            self.logger.error(f"Error updating agent state: {e}")
            raise

    async def get_pending_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get pending jobs for this agent.
        
        Args:
            limit: Maximum number of jobs to retrieve
            
        Returns:
            List of pending jobs
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/api/jobs/agent/{self.agent_name}",
                    params={"limit": limit},
                )
                response.raise_for_status()
                jobs = response.json()
                
            self.logger.info(f"Retrieved {len(jobs)} pending jobs for {self.agent_name}")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error getting pending jobs: {e}")
            raise

    async def update_job_status(
        self, job_id: int, status: str, increment_attempts: bool = False
    ) -> Dict[str, Any]:
        """
        Update the status of a job.
        
        Args:
            job_id: ID of the job to update
            status: New status (pending, processing, completed, failed)
            increment_attempts: Whether to increment the attempts counter
            
        Returns:
            The updated job data
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.backend_url}/api/jobs/{job_id}/status",
                    json={
                        "status": status,
                        "incrementAttempts": increment_attempts,
                    },
                )
                response.raise_for_status()
                result = response.json()
                
            self.logger.info(f"Job {job_id} status updated to {status}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error updating job status: {e}")
            raise

    async def send_message(
        self, to_agent: str, message: str, message_type: str = "info", requires_response: bool = False
    ) -> Dict[str, Any]:
        """
        Send a message to another agent.
        
        Args:
            to_agent: Name of the target agent
            message: Message content
            message_type: Type of message (info, request, response, etc.)
            requires_response: Whether this message requires a response
            
        Returns:
            The created job data
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/jobs",
                    json={
                        "targetAgent": to_agent,
                        "payload": {
                            "type": "inter_agent_message",
                            "fromAgent": self.agent_name,
                            "message": message,
                            "messageType": message_type,
                            "requiresResponse": requires_response,
                        },
                    },
                )
                response.raise_for_status()
                result = response.json()
                
            self.logger.info(f"Message sent from {self.agent_name} to {to_agent}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise

    async def store_memory(
        self,
        content: str,
        memory_type: str = "general",
        tags: Optional[List[str]] = None,
        importance: int = 5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store a memory for this agent.
        
        Args:
            content: Memory content
            memory_type: Type of memory (general, conversation, task_result, learning)
            tags: Tags for categorization
            importance: Importance level (1-10)
            metadata: Additional metadata
            
        Returns:
            The stored document data
        """
        try:
            doc_metadata = {
                "agentName": self.agent_name,
                "type": memory_type,
                "timestamp": datetime.now().isoformat(),
                "tags": tags or [],
                "importance": importance,
                **(metadata or {}),
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/documents",
                    json={
                        "content": content,
                        "metadata": doc_metadata,
                    },
                )
                response.raise_for_status()
                result = response.json()
                
            self.logger.info(f"Memory stored for {self.agent_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            raise

    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task. This method should be overridden by subclasses.
        
        Args:
            task_description: Description of the task to execute
            context: Context data for the task
            
        Returns:
            Task execution result
        """
        self.logger.warning(f"execute_task not implemented for {self.agent_name}")
        return {
            "status": "not_implemented",
            "message": "This agent has not implemented task execution",
        }

    async def process_jobs(self, max_jobs: int = 5) -> List[Dict[str, Any]]:
        """
        Process pending jobs for this agent.
        
        Args:
            max_jobs: Maximum number of jobs to process
            
        Returns:
            List of processing results
        """
        results = []
        
        try:
            jobs = await self.get_pending_jobs(max_jobs)
            
            for job in jobs:
                job_id = job["id"]
                payload = job["payload"]
                
                try:
                    # Mark job as processing
                    await self.update_job_status(job_id, "processing", True)
                    
                    # Process the job based on type
                    job_type = payload.get("type", "generic")
                    
                    if job_type == "inter_agent_message":
                        result = await self.handle_message(payload)
                    else:
                        result = await self.execute_task(
                            payload.get("description", "Generic task"),
                            payload
                        )
                    
                    # Mark job as completed
                    await self.update_job_status(job_id, "completed")
                    
                    results.append({
                        "job_id": job_id,
                        "status": "completed",
                        "result": result,
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error processing job {job_id}: {e}")
                    await self.update_job_status(job_id, "failed")
                    results.append({
                        "job_id": job_id,
                        "status": "failed",
                        "error": str(e),
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in process_jobs: {e}")
            raise

    async def handle_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an inter-agent message. Can be overridden by subclasses.
        
        Args:
            payload: Message payload
            
        Returns:
            Message handling result
        """
        from_agent = payload.get("fromAgent", "unknown")
        message = payload.get("message", "")
        message_type = payload.get("messageType", "info")
        
        self.logger.info(f"Received {message_type} message from {from_agent}: {message}")
        
        # Store the message as a memory
        await self.store_memory(
            content=f"Message from {from_agent}: {message}",
            memory_type="conversation",
            tags=["message", message_type],
            importance=6,
            metadata={"fromAgent": from_agent, "messageType": message_type},
        )
        
        return {
            "status": "message_received",
            "from": from_agent,
            "message": message,
        }

