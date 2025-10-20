import { agentService } from './agentService';
import logger from '../utils/logger';
import { v4 as uuidv4 } from 'uuid';
import githubAgentService from './githubAgentService';

export interface WorkflowStep {
  id: string;
  agentName: string;
  taskType: string;
  payload: any;
  dependencies?: string[]; // IDs of steps that must complete first
  retryOnFailure?: boolean;
  timeout?: number; // in milliseconds
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  createdAt: Date;
  status: 'pending' | 'running' | 'completed' | 'failed';
  results?: Map<string, any>;
}

export class WorkflowOrchestrationService {
  private workflows: Map<string, Workflow> = new Map();

  /**
   * Create a new workflow
   */
  async createWorkflow(
    name: string,
    description: string,
    steps: WorkflowStep[]
  ): Promise<Workflow> {
    const workflowId = `workflow_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const workflow: Workflow = {
      id: workflowId,
      name,
      description,
      steps,
      createdAt: new Date(),
      status: 'pending',
      results: new Map(),
    };

    this.workflows.set(workflowId, workflow);

    logger.info(`Created workflow: ${name} (${workflowId}) with ${steps.length} steps`);

    void this.syncToGitHub(workflow, 'pending', 'Workflow registered and awaiting execution.');

    return workflow;
  }

  /**
   * Execute a workflow
   */
  async executeWorkflow(workflowId: string): Promise<Workflow> {
    const workflow = this.workflows.get(workflowId);

    if (!workflow) {
      throw new Error(`Workflow ${workflowId} not found`);
    }

    if (workflow.status === 'running') {
      throw new Error(`Workflow ${workflowId} is already running`);
    }

    logger.info(`Executing workflow: ${workflow.name} (${workflowId})`);

    workflow.status = 'running';
    const completedSteps = new Set<string>();
    const results = new Map<string, any>();

    void this.syncToGitHub(workflow, 'running', 'Workflow execution started.');

    try {
      // Execute steps in dependency order
      while (completedSteps.size < workflow.steps.length) {
        const readySteps = workflow.steps.filter((step) => {
          // Skip already completed steps
          if (completedSteps.has(step.id)) {
            return false;
          }

          // Check if all dependencies are completed
          if (step.dependencies && step.dependencies.length > 0) {
            return step.dependencies.every((depId) => completedSteps.has(depId));
          }

          return true;
        });

        if (readySteps.length === 0) {
          throw new Error('Workflow has circular dependencies or unreachable steps');
        }

        // Execute ready steps in parallel
        const stepPromises = readySteps.map((step) =>
          this.executeStep(step, results)
        );

        const stepResults = await Promise.allSettled(stepPromises);

        // Process results
        for (let i = 0; i < readySteps.length; i++) {
          const step = readySteps[i];
          const result = stepResults[i];

          if (result.status === 'fulfilled') {
            results.set(step.id, result.value);
            completedSteps.add(step.id);
            logger.info(`Step ${step.id} completed successfully`);
          } else {
            logger.error(`Step ${step.id} failed:`, result.reason);

            if (!step.retryOnFailure) {
              throw new Error(`Step ${step.id} failed: ${result.reason}`);
            }

            // Retry the step
            try {
              const retryResult = await this.executeStep(step, results);
              results.set(step.id, retryResult);
              completedSteps.add(step.id);
              logger.info(`Step ${step.id} succeeded on retry`);
            } catch (retryError) {
              throw new Error(`Step ${step.id} failed after retry: ${retryError}`);
            }
          }
        }
      }

      workflow.status = 'completed';
      workflow.results = results;

      logger.info(`Workflow ${workflowId} completed successfully`);

      void this.syncToGitHub(workflow, 'completed', 'Workflow execution completed successfully.');

      return workflow;
    } catch (error: any) {
      workflow.status = 'failed';
      logger.error(`Workflow ${workflowId} failed:`, error);
      void this.syncToGitHub(workflow, 'failed', `Workflow failed with error: ${error.message}`);
      throw error;
    }
  }

  /**
   * Execute a single workflow step
   */
  private async executeStep(
    step: WorkflowStep,
    previousResults: Map<string, any>
  ): Promise<any> {
    logger.info(`Executing step: ${step.id} for agent ${step.agentName}`);

    // Prepare payload with results from dependencies
    const enrichedPayload = {
      ...step.payload,
      dependencyResults: step.dependencies
        ? step.dependencies.reduce((acc, depId) => {
            acc[depId] = previousResults.get(depId);
            return acc;
          }, {} as any)
        : {},
    };

    // Create a job for the agent
    const job = await agentService.createJob({
      agent_name: step.agentName,
      task_type: step.taskType,
      payload: enrichedPayload,
      priority: 0, // Default priority
      correlation_id: uuidv4(), // Generate new correlationId for job, or pass from request if available
    });

    // Wait for the job to complete (with timeout)
    const timeout = step.timeout || 60000; // Default 60 seconds
    const startTime = Date.now();

    while (true) {
      // Check if timeout exceeded
      if (Date.now() - startTime > timeout) {
        throw new Error(`Step ${step.id} timed out after ${timeout}ms`);
      }

      // Get job status
      const jobs = await agentService.getPendingJobs(step.agentName);
      const currentJob = jobs.find((j) => j.id === job.id);

      if (!currentJob) {
        // Job completed or failed
        // In a real implementation, we'd query the job_queue table for the final status
        logger.info(`Step ${step.id} job completed`);
        return { status: 'completed', jobId: job.id };
      }

      // Wait before checking again
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }

  /**
   * Get workflow status
   */
  getWorkflow(workflowId: string): Workflow | undefined {
    return this.workflows.get(workflowId);
  }

  /**
   * List all workflows
   */
  listWorkflows(): Workflow[] {
    return Array.from(this.workflows.values());
  }

  /**
   * Cancel a running workflow
   */
  async cancelWorkflow(workflowId: string): Promise<void> {
    const workflow = this.workflows.get(workflowId);

    if (!workflow) {
      throw new Error(`Workflow ${workflowId} not found`);
    }

    if (workflow.status !== 'running') {
      throw new Error(`Workflow ${workflowId} is not running`);
    }

    workflow.status = 'failed';
    logger.info(`Workflow ${workflowId} cancelled`);

    void this.syncToGitHub(workflow, 'failed', 'Workflow cancelled by operator.');
  }

  /**
   * Create a predefined workflow template
   */
  async createCodeReviewWorkflow(codeContent: string): Promise<Workflow> {
    return this.createWorkflow(
      'Code Review Workflow',
      'Comprehensive code review with analysis, testing, and recommendations',
      [
        {
          id: 'analyze_code',
          agentName: 'code_analyzer',
          taskType: 'analyze_code',
          payload: { code: codeContent },
        },
        {
          id: 'detect_bugs',
          agentName: 'code_analyzer',
          taskType: 'detect_bugs',
          payload: { code: codeContent },
          dependencies: ['analyze_code'],
        },
        {
          id: 'suggest_optimizations',
          agentName: 'code_analyzer',
          taskType: 'suggest_optimizations',
          payload: { code: codeContent },
          dependencies: ['analyze_code'],
        },
        {
          id: 'learn_from_review',
          agentName: 'learning_agent',
          taskType: 'learn_from_feedback',
          payload: { source: 'code_review' },
          dependencies: ['detect_bugs', 'suggest_optimizations'],
        },
      ]
    );
  }

  /**
   * Create a data processing workflow
   */
  async createDataProcessingWorkflow(data: any): Promise<Workflow> {
    return this.createWorkflow(
      'Data Processing Workflow',
      'Validate, process, and analyze data',
      [
        {
          id: 'validate_data',
          agentName: 'data_processor',
          taskType: 'validate_data',
          payload: { data },
        },
        {
          id: 'process_data',
          agentName: 'data_processor',
          taskType: 'process_data',
          payload: { data },
          dependencies: ['validate_data'],
        },
        {
          id: 'analyze_patterns',
          agentName: 'learning_agent',
          taskType: 'identify_patterns',
          payload: { source: 'processed_data' },
          dependencies: ['process_data'],
        },
      ]
    );
  }

  /**
   * Create a system monitoring workflow
   */
  async createMonitoringWorkflow(): Promise<Workflow> {
    return this.createWorkflow(
      'System Monitoring Workflow',
      'Comprehensive system health check and monitoring',
      [
        {
          id: 'health_check',
          agentName: 'monitoring_agent',
          taskType: 'health_check',
          payload: {},
        },
        {
          id: 'check_metrics',
          agentName: 'monitoring_agent',
          taskType: 'check_metrics',
          payload: {},
        },
        {
          id: 'optimize_performance',
          agentName: 'learning_agent',
          taskType: 'optimize_performance',
          payload: {},
          dependencies: ['health_check', 'check_metrics'],
        },
      ]
    );
  }

  private async syncToGitHub(workflow: Workflow, status: Workflow['status'], summary: string): Promise<void> {
    try {
      await githubAgentService.syncWorkflow(workflow, status, summary);
    } catch (error: any) {
      logger.warn(`Failed to sync workflow ${workflow.id} to GitHub: ${error.message}`);
    }
  }
}

export default new WorkflowOrchestrationService();

