import axios, { AxiosInstance } from 'axios';
import featureFlagService from './featureFlagService';
import logger from '../utils/logger';
import { Workflow } from './workflowOrchestrationService';

interface GitHubIssue {
  number: number;
  title: string;
  body?: string;
  state: string;
}

class GitHubAgentService {
  private client: AxiosInstance | null = null;
  private owner: string | null = null;
  private repo: string | null = null;

  constructor() {
    const token = process.env.GITHUB_TOKEN;
    this.owner = process.env.GITHUB_REPO_OWNER || null;
    this.repo = process.env.GITHUB_REPO_NAME || null;

    if (token && this.owner && this.repo) {
      this.client = axios.create({
        baseURL: `https://api.github.com/repos/${this.owner}/${this.repo}`,
        headers: {
          Authorization: `token ${token}`,
          Accept: 'application/vnd.github+json',
          'User-Agent': 'flowstate-ai-orchestrator',
        },
      });
    } else {
      logger.warn('GitHubAgentService disabled - missing GITHUB_TOKEN, GITHUB_REPO_OWNER, or GITHUB_REPO_NAME');
    }
  }

  private isEnabled(): boolean {
    return !!this.client;
  }

  private buildLabels(workflow: Workflow): string[] {
    return ['automation', 'workflow', `workflow:${workflow.id}`];
  }

  async syncWorkflow(workflow: Workflow, status: Workflow['status'], summary: string): Promise<void> {
    if (!this.isEnabled()) {
      return;
    }

    const enabled = await featureFlagService.shouldServe('github_workflow_sync', {
      fallbackId: workflow.id,
    });

    if (!enabled) {
      return;
    }

    try {
      const existing = await this.findIssue(workflow.id);
      if (!existing) {
        await this.createIssue(workflow, status, summary);
      } else {
        await this.updateIssue(existing, workflow, status, summary);
      }
    } catch (error: any) {
      logger.warn(`GitHub workflow sync failed for ${workflow.id}: ${error.message}`);
    }
  }

  private async findIssue(workflowId: string): Promise<GitHubIssue | null> {
    const response = await this.client!.get<GitHubIssue[]>('/issues', {
      params: {
        labels: `workflow:${workflowId}`,
        state: 'all',
      },
    });
    return response.data.length ? response.data[0] : null;
  }

  private async createIssue(workflow: Workflow, status: Workflow['status'], summary: string): Promise<void> {
    const body = this.composeBody(workflow, status, summary);
    await this.client!.post('/issues', {
      title: `[Workflow] ${workflow.name} (${status})`,
      body,
      labels: this.buildLabels(workflow),
    });
    logger.info(`Created GitHub issue for workflow ${workflow.id}`);
  }

  private async updateIssue(issue: GitHubIssue, workflow: Workflow, status: Workflow['status'], summary: string): Promise<void> {
    const body = this.composeBody(workflow, status, summary);
    await this.client!.patch(`/issues/${issue.number}`, {
      title: `[Workflow] ${workflow.name} (${status})`,
      body,
      labels: this.buildLabels(workflow),
      state: status === 'completed' ? 'closed' : 'open',
    });
    await this.client!.post(`/issues/${issue.number}/comments`, {
      body: `Workflow **${workflow.id}** updated to **${status.toUpperCase()}** at ${new Date().toISOString()}\n\n${summary}`,
    });
    logger.info(`Updated GitHub issue #${issue.number} for workflow ${workflow.id}`);
  }

  private composeBody(workflow: Workflow, status: Workflow['status'], summary: string): string {
    const stepList = workflow.steps
      .map((step) => `- ${step.id} · agent: \`${step.agentName}\` · task: \`${step.taskType}\``)
      .join('\n');
    return `**Workflow ID:** ${workflow.id}\n**Status:** ${status}\n**Created:** ${workflow.createdAt.toISOString()}\n\n---\n${summary}\n\n**Defined steps**\n${stepList}`;
  }
}

export default new GitHubAgentService();
