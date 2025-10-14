# Flowstate-AI Automation

This document describes the automated workflows in Flowstate-AI.

## Overview

Flowstate-AI includes automated workflows that run in GitHub Actions to handle repetitive CRM tasks without manual intervention. These workflows ensure your CRM operations continue running smoothly 24/7.

## CRM Automation Workflow

### What Gets Automated

The CRM automation workflow handles the following tasks automatically:

1. **Lead Qualification**
   - Fetches new leads from the CRM system
   - Uses AI (GPT-4) to analyze lead information
   - Classifies leads as MQL (Marketing Qualified Lead) or SQL (Sales Qualified Lead)
   - Updates lead status in the CRM

2. **Deal Creation**
   - Automatically creates sales deals for SQL-qualified leads
   - Initializes deals with appropriate pipeline and stage
   - Links deals to their corresponding contacts

3. **Deal Monitoring**
   - Monitors active deals in the pipeline
   - Logs deal status and activity
   - Prepares insights for sales team follow-up

### Schedule

The automation runs on the following schedule:

- **Every 4 hours**: Automatic execution via GitHub Actions cron
- **Manual trigger**: Can be triggered on-demand from GitHub Actions UI
- **On code changes**: Runs when automation-related files are updated

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                GitHub Actions Runner                 │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌────────────┐    ┌──────────────┐                │
│  │   Redis    │◄───│   CRM API    │                │
│  │  Service   │    │  (Flask)     │                │
│  └────────────┘    └──────┬───────┘                │
│                            │                         │
│                            │                         │
│                    ┌───────▼──────────┐             │
│                    │  CRM Automation  │             │
│                    │     Agent        │             │
│                    │  (Python + AI)   │             │
│                    └──────────────────┘             │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### Configuration

#### Required Secrets

The automation requires the following GitHub secret:

- **`OPENAI_API_KEY`**: Your OpenAI API key for AI-powered lead qualification

To add this secret:
1. Go to your GitHub repository
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `OPENAI_API_KEY`
5. Value: Your OpenAI API key
6. Click "Add secret"

#### Environment Variables

The workflow uses these environment variables:

- `REDIS_HOST`: localhost (provided by GitHub Actions service)
- `REDIS_PORT`: 6379 (provided by GitHub Actions service)
- `OPENAI_API_KEY`: From repository secrets

### Usage

#### Viewing Workflow Status

1. Go to the **Actions** tab in your GitHub repository
2. Select **"CRM Automation"** from the workflows list
3. View recent runs and their status

#### Manual Triggering

To manually trigger the automation:

1. Go to **Actions** → **CRM Automation**
2. Click **"Run workflow"** button (top right)
3. Select the branch (usually `main`)
4. Click **"Run workflow"**

#### Viewing Logs

Automation logs are available in two ways:

1. **Real-time logs** (during workflow execution):
   - Go to Actions → Select the running workflow
   - Click on the job name
   - Expand each step to see logs

2. **Artifact logs** (after workflow completion):
   - Go to Actions → Select the completed workflow
   - Scroll to the bottom to "Artifacts" section
   - Download `crm-automation-logs-{run_number}`
   - Extract and view `crm_automation_agent.log`

Artifacts are retained for 30 days.

### Monitoring

#### Success Indicators

A successful automation run will:
- ✅ Start Redis service
- ✅ Start CRM API successfully
- ✅ Pass health check
- ✅ Process all leads
- ✅ Complete without errors

#### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Health check fails | CRM API didn't start | Check Redis service logs; verify API startup |
| OpenAI error | Invalid or missing API key | Verify `OPENAI_API_KEY` secret is set correctly |
| No leads processed | No leads in CRM | This is expected; workflow will complete normally |
| Redis connection error | Service didn't start | Check Redis service health in workflow logs |

### Customization

#### Changing Schedule

To modify the automation frequency, edit `.github/workflows/crm-automation.yml`:

```yaml
schedule:
  - cron: '0 */4 * * *'  # Current: Every 4 hours
```

Common alternatives:
- `'0 * * * *'` - Every hour
- `'0 */2 * * *'` - Every 2 hours
- `'0 0 * * *'` - Daily at midnight
- `'0 9 * * 1-5'` - Weekdays at 9 AM

Use [crontab.guru](https://crontab.guru/) to create custom schedules.

#### Adding Custom Logic

To extend the automation:

1. Edit `agents/crm_automation_agent.py`
2. Add your custom methods to the `CRMAutomationAgent` class
3. Call your methods from `run_automation_cycle()`
4. Test locally first, then push to trigger automation

### Cost Considerations

The automation uses:

1. **GitHub Actions minutes**: Free tier includes 2,000 minutes/month
   - Each run takes ~2-5 minutes
   - Running every 4 hours = 6 runs/day = 180 runs/month
   - Estimated usage: 360-900 minutes/month

2. **OpenAI API**: Charges per token
   - Lead qualification uses GPT-4-mini (cost-effective)
   - Cost depends on number of leads processed
   - Estimated: $0.01-0.10 per run

3. **Redis**: Runs in GitHub Actions (no cost)

### Best Practices

1. **Monitor regularly**: Check workflow runs weekly for errors
2. **Review logs**: Download and review logs periodically
3. **Test changes**: Always test automation changes in a feature branch first
4. **Rate limits**: Be aware of OpenAI API rate limits
5. **Scale gradually**: Start with 4-hour intervals, adjust based on needs
6. **Keep secrets secure**: Never commit API keys to code

### Future Enhancements

Planned improvements:

- Email notifications for qualified leads
- Slack/Discord integration for real-time alerts
- Advanced analytics and reporting
- Multi-stage deal progression automation
- Integration with email automation sequences
- Predictive lead scoring

### Support

If you encounter issues with the automation:

1. Check workflow logs in GitHub Actions
2. Download and review artifact logs
3. Verify all secrets are configured
4. Review [.github/workflows/README.md](.github/workflows/README.md)
5. Open an issue on GitHub with:
   - Workflow run URL
   - Error messages from logs
   - Expected vs actual behavior

## Additional Workflows

### CI/CD Pipeline

The repository includes additional workflows for:

- **Continuous Integration**: Automated testing on push/PR
- **Code Quality**: Linting and static analysis
- **Docker Builds**: Container image building and testing
- **Backend Tests**: Dedicated backend testing

See `.github/workflows/` directory for all workflow configurations.

## Related Documentation

- [GitHub Actions Workflows README](.github/workflows/README.md)
- [CRM Automation Agent](../agents/crm_automation_agent.py)
- [CRM API Documentation](api/crm_api_documentation.md)
- [System Architecture](../SYSTEM_ARCHITECTURE.md)
