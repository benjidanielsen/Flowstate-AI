# Dependency Automation

This document describes the automated dependency management system for Flowstate-AI.

## Overview

The project uses Dependabot to automatically update dependencies daily, and GitHub Actions to automatically merge passing updates.

## Components

### 1. Dependabot Configuration (`.github/dependabot.yml`)

Dependabot is configured to check for dependency updates daily at 3:00 AM UTC for:

- **Backend** (npm) - `/backend/package.json`
- **Frontend** (npm) - `/frontend/package.json`
- **Python Worker** (pip) - `/python-worker/requirements.txt`
- **Root Python** (pip) - `/requirements.txt`
- **GitHub Actions** (weekly) - Workflow files
- **Docker** (weekly) - Dockerfile base images

#### Key Configuration Options:

- **Daily updates**: All package managers check daily (except GitHub Actions and Docker, which check weekly)
- **Open PR limit**: Maximum of 10 PRs for npm/pip, 5 for GitHub Actions/Docker
- **Labels**: All PRs are tagged with `dependencies`, package type, and `automerge`
- **Commit messages**: Prefixed with conventional commit format (e.g., `chore(backend):`)

### 2. Auto-Merge Workflow (`.github/workflows/dependabot-auto-merge.yml`)

This workflow automatically manages Dependabot pull requests:

#### Behavior by Update Type:

**Patch and Minor Updates (e.g., 1.0.0 → 1.0.1 or 1.0.0 → 1.1.0)**
- ✅ Automatically approved
- ✅ Auto-merge enabled
- ✅ Will merge when CI passes
- 💬 Receives a comment confirming auto-merge is enabled

**Major Updates (e.g., 1.0.0 → 2.0.0)**
- ⏸️ Requires manual review
- 💬 Receives a comment alerting about breaking changes
- ❌ Will NOT auto-merge
- ✅ Must pass CI before manual merge

#### How It Works:

1. Dependabot opens a PR for a dependency update
2. The auto-merge workflow is triggered
3. The workflow uses Dependabot metadata to determine the update type
4. For patch/minor: PR is approved and auto-merge is enabled
5. GitHub waits for all required CI checks to pass
6. Once CI passes, GitHub automatically merges the PR
7. For major: PR is commented but requires manual review

### 3. CI Pipeline (`.github/workflows/ci.yml`)

The CI pipeline ensures that:

- Backend tests pass
- Frontend tests pass
- Python worker linting passes
- Build succeeds for all components
- Integration tests pass

#### CI Robustness:

The CI is configured to fail only on real errors:

- **Backend**: Tests and linting must pass
- **Frontend**: Tests and linting must pass
- **Python Worker**: 
  - Critical syntax errors (E9, F63, F7, F82) must not exist
  - Tests run only if test files exist
  - Missing tests don't cause failure (graceful)

## Manual Intervention Required For:

1. **Major version updates** - May include breaking changes
2. **Failed CI checks** - Auto-merge will not proceed
3. **Security advisories** - Review and merge manually

## Benefits

- 🔄 **Always up-to-date**: Daily checks ensure dependencies are current
- 🛡️ **Security**: Automated security patches applied quickly
- ⏱️ **Time-saving**: No manual dependency updates needed for minor/patch versions
- 🧪 **Safe**: All updates must pass CI before merging
- 📊 **Visibility**: All updates tracked in pull requests with clear metadata

## Monitoring

You can monitor dependency updates by:

1. Watching the [Pull Requests](https://github.com/benjidanielsen/Flowstate-AI/pulls) page
2. Filtering by label: `dependencies`
3. Checking Dependabot alerts in the Security tab
4. Reviewing the Actions tab for workflow runs

## Configuration Changes

To modify the automation:

1. **Change update frequency**: Edit `schedule.interval` in `.github/dependabot.yml`
2. **Adjust PR limits**: Edit `open-pull-requests-limit` in `.github/dependabot.yml`
3. **Modify auto-merge rules**: Edit conditions in `.github/workflows/dependabot-auto-merge.yml`
4. **Add new package managers**: Add new entries to `.github/dependabot.yml`

## Troubleshooting

### Auto-merge not working?

Check:
- [ ] CI is passing for the PR
- [ ] PR is labeled with correct update type (patch/minor)
- [ ] Auto-merge workflow ran successfully
- [ ] Repository settings allow auto-merge

### Too many Dependabot PRs?

Adjust:
- Reduce `open-pull-requests-limit` in `.github/dependabot.yml`
- Change update frequency from `daily` to `weekly`
- Group updates using `groups` configuration

### CI failing on Dependabot PRs?

1. Check if the failure is legitimate (actual test/lint failure)
2. If it's a flaky test, fix the test first
3. If dependency causes breakage, review the update manually
4. Consider pinning problematic dependencies with version constraints

## Best Practices

1. **Review major updates**: Always review breaking changes before merging
2. **Monitor CI**: Ensure CI stays green to enable auto-merge
3. **Update regularly**: Don't disable the automation for long periods
4. **Pin cautiously**: Only pin versions when absolutely necessary
5. **Test locally**: For complex updates, test locally before merging

## Resources

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [GitHub Auto-merge](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request)
- [Semantic Versioning](https://semver.org/)
