# GitHub Actions Workflows

This directory contains automated workflows for Flowstate-AI.

## Workflows

### CRM Automation (`crm-automation.yml`)

Automated CRM workflow that runs the CRM automation agent to process leads and monitor deals.

**Schedule**: Runs every 4 hours automatically

**Triggers**:
- Scheduled (cron): Every 4 hours (`0 */4 * * *`)
- Manual dispatch: Can be triggered manually from GitHub Actions tab
- Push to main: Runs when CRM-related files are modified

**What it does**:
1. Starts Redis service for data storage
2. Starts the CRM API backend service
3. Runs the CRM automation agent which:
   - Processes new leads
   - Qualifies leads using AI (MQL vs SQL)
   - Creates deals for qualified leads
   - Monitors existing deals

**Requirements**:
- `OPENAI_API_KEY` secret must be configured in repository settings

**Outputs**:
- Automation logs are uploaded as artifacts and retained for 30 days

### CI/CD Pipeline (`ci.yml`)

Main continuous integration and deployment pipeline.

**Triggers**: Push to main/develop, pull requests to main

**What it does**:
- Tests backend, frontend, and Python worker
- Runs linting and builds
- Performs integration tests
- Docker build validation
- Code quality checks

### Backend Tests (`backend-tests.yml`)

Dedicated backend testing workflow.

**Triggers**: Changes to backend files

**What it does**:
- Runs backend unit and integration tests
- Detects open handles and potential issues

### Main Pipeline (`main.yml`)

Legacy Flowstate-AI CI/CD pipeline.

**Triggers**: Push to main/feature branches, pull requests

**What it does**:
- Multi-OS testing (Ubuntu, Windows)
- Static analysis and security checks
- Evaluation harness

## Configuration

### Required Secrets

Add these secrets in GitHub repository settings (Settings → Secrets and variables → Actions):

- `OPENAI_API_KEY`: OpenAI API key for AI-powered features

### Manual Triggering

To manually trigger the CRM automation workflow:

1. Go to the Actions tab in GitHub
2. Select "CRM Automation" from the workflows list
3. Click "Run workflow" button
4. Select the branch and click "Run workflow"

## Monitoring

### Viewing Logs

1. Go to Actions tab
2. Click on the workflow run
3. Click on the job name
4. Expand the steps to view logs
5. Download artifacts for detailed logs

### Artifacts

The CRM automation workflow uploads logs as artifacts:
- **Name**: `crm-automation-logs-{run_number}`
- **Contents**: `crm_automation_agent.log`
- **Retention**: 30 days

## Troubleshooting

### CRM Automation Fails

1. Check if `OPENAI_API_KEY` secret is configured
2. Verify Redis service started successfully
3. Check CRM API health check step
4. Review automation logs artifact

### API Connection Issues

If the agent can't connect to the API:
- Verify the CRM API started successfully (check "Start CRM API service" step)
- Ensure the health check passed
- Check if port 5001 is available
- Review Redis service logs

## Development

### Testing Workflows Locally

You cannot run GitHub Actions locally, but you can test the components:

```bash
# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Start CRM API
cd backend
python crm_api.py &

# Wait for API to start
sleep 5

# Run automation agent
OPENAI_API_KEY=your_key python agents/crm_automation_agent.py
```

### Modifying Schedules

To change the automation frequency, edit the cron expression in `crm-automation.yml`:

```yaml
schedule:
  - cron: '0 */4 * * *'  # Every 4 hours
```

Common cron patterns:
- `0 * * * *` - Every hour
- `0 */2 * * *` - Every 2 hours
- `0 0 * * *` - Daily at midnight
- `0 9 * * 1-5` - Weekdays at 9 AM

Use [crontab.guru](https://crontab.guru/) to help create cron expressions.
