# Security Scanning Guide

**Last Updated**: 2025-10-10  
**Maintained By**: Flowstate-AI Development Team

## Overview

Flowstate-AI implements comprehensive, multi-layered security scanning to identify and prevent security vulnerabilities across the entire codebase. This document describes the security scanning tools, their configuration, and how to work with security findings.

## Security Scanning Tools

### 1. CodeQL (GitHub Native)

**Purpose**: Broad multi-language semantic security analysis  
**Languages**: JavaScript, TypeScript, Python  
**Frequency**: On push to main/develop, on PRs, weekly schedule  
**Location**: `.github/workflows/codeql.yml`

**What it scans**:
- Semantic code analysis across multiple languages
- Complex security patterns and data flow analysis
- SQL injection, XSS, path traversal, and more
- CWE (Common Weakness Enumeration) patterns

**Viewing results**: GitHub Security tab → Code scanning alerts → Filter by "CodeQL"

### 2. ESLint Security Scan

**Purpose**: JavaScript/TypeScript-specific security and quality analysis  
**Languages**: JavaScript, TypeScript, JSX, TSX  
**Frequency**: On push to main/develop, on PRs, weekly schedule  
**Location**: `.github/workflows/eslint.yml`

**What it scans**:
- Backend (Node.js/Express/TypeScript)
- Frontend (React/TypeScript/Vite)
- Security vulnerabilities (eslint-plugin-security)
- TypeScript type safety issues
- React best practices and security

**Viewing results**: GitHub Security tab → Code scanning alerts → Filter by "eslint-backend" or "eslint-frontend"

### 3. Bandit Security Scan

**Purpose**: Python-specific security analysis  
**Languages**: Python  
**Frequency**: On push to main/develop, on PRs, weekly schedule  
**Location**: `.github/workflows/bandit.yml`

**What it scans**:
- Root-level Python files
- Python worker (FastAPI application)
- Hardcoded passwords/secrets
- SQL injection vulnerabilities
- Command injection risks
- Insecure cryptography usage
- Unsafe deserialization

**Viewing results**: GitHub Security tab → Code scanning alerts → Filter by "bandit-root" or "bandit-worker"

### 4. Gitleaks (Secret Scanning)

**Purpose**: Detect hardcoded secrets and credentials  
**Languages**: All (text-based scanning)  
**Frequency**: On every push  
**Location**: `.github/workflows/codeql.yml` (integrated)

**What it scans**:
- API keys, tokens, passwords
- AWS credentials, database connection strings
- Private keys, certificates
- Any pattern matching secret formats

**Viewing results**: GitHub Security tab → Secret scanning alerts

### 5. Trivy (Container Scanning)

**Purpose**: Container image vulnerability scanning  
**Target**: Docker images  
**Frequency**: On Docker image builds  
**Location**: `.github/workflows/docker.yml`

**What it scans**:
- OS package vulnerabilities
- Application dependency vulnerabilities
- Misconfigurations in Dockerfiles
- Known CVEs in base images

**Viewing results**: GitHub Security tab → Code scanning alerts → Filter by "trivy"

### 6. Dependabot (Dependency Scanning)

**Purpose**: Automated dependency vulnerability detection and updates  
**Languages**: npm (JavaScript/TypeScript), pip (Python)  
**Frequency**: Daily checks  
**Configuration**: `.github/dependabot.yml`

**What it scans**:
- npm package vulnerabilities (backend, frontend)
- Python package vulnerabilities (root, python-worker)
- Outdated dependencies with security fixes

**Viewing results**: GitHub Security tab → Dependabot alerts

## Security Scanning Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Code Push / Pull Request                  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌────────┐      ┌────────┐     ┌────────┐
    │ CodeQL │      │ ESLint │     │ Bandit │
    │  Scan  │      │  Scan  │     │  Scan  │
    └────┬───┘      └────┬───┘     └────┬───┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  SARIF Results       │
              │  Upload to GitHub    │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  GitHub Security Tab │
              │  - Code Scanning     │
              │  - Secret Scanning   │
              │  - Dependabot        │
              └──────────────────────┘
```

## Working with Security Findings

### Viewing Security Findings

1. Navigate to the **Security** tab in the GitHub repository
2. Select the appropriate category:
   - **Code scanning** - CodeQL, ESLint, Bandit, Trivy findings
   - **Secret scanning** - Gitleaks findings
   - **Dependabot** - Dependency vulnerabilities

3. Filter by:
   - **Tool** - CodeQL, eslint-backend, eslint-frontend, bandit-root, bandit-worker
   - **Severity** - Critical, High, Medium, Low
   - **Status** - Open, Fixed, Dismissed
   - **Branch** - main, develop, feature branches

### Triaging Security Findings

When a security finding is reported, follow this process:

1. **Assess Severity**:
   - **Critical/High**: Address immediately, block PR if necessary
   - **Medium**: Address before merging to main
   - **Low**: Address in next sprint or dismiss if false positive

2. **Verify the Finding**:
   - Review the code location
   - Understand the vulnerability
   - Check if it's a true positive or false positive

3. **Take Action**:
   - **Fix**: Modify code to address the vulnerability
   - **Dismiss**: If false positive, dismiss with reason
   - **Create Issue**: If can't fix immediately, create tracking issue

4. **Document**:
   - Add comments explaining the fix or dismissal
   - Update security documentation if needed
   - Share learnings with the team

### Fixing Security Issues

**For CodeQL/ESLint/Bandit findings**:

1. Click on the finding in the Security tab
2. Review the **Description** and **Recommendation**
3. Click **Show paths** to see the data flow (for CodeQL)
4. Navigate to the code location
5. Implement the recommended fix
6. Commit and push the fix
7. Verify the finding is resolved in the next scan

**For Dependabot findings**:

1. Review the Dependabot alert
2. Check the **Patched versions** section
3. Option A: Accept Dependabot's automatic PR
4. Option B: Manually update the dependency
5. Test thoroughly before merging
6. Verify the alert is closed after merge

### Dismissing False Positives

If a finding is a false positive:

1. Click on the finding in the Security tab
2. Click **Dismiss alert**
3. Select a reason:
   - **False positive** - Not actually a vulnerability
   - **Won't fix** - Accepted risk
   - **Used in tests** - Only in test code
4. Add a comment explaining why
5. Click **Dismiss alert**

### Configuring Exclusions

**ESLint exclusions**:

Create or modify `.eslintrc.json` in backend or frontend:

```json
{
  "rules": {
    "security/detect-object-injection": "off"
  },
  "ignorePatterns": ["dist/", "build/", "*.test.ts"]
}
```

**Bandit exclusions**:

Create `.bandit` file in project root:

```yaml
exclude_dirs:
  - /venv/
  - /tests/
  - /node_modules/

skips:
  - B101  # assert_used
  - B601  # paramiko_calls
```

**CodeQL exclusions**:

Modify `.github/workflows/codeql.yml`:

```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    queries: +security-extended
    paths-ignore:
      - '**/test/**'
      - '**/tests/**'
```

## CI/CD Integration

### Pull Request Checks

Security scans run automatically on all pull requests:

- **CodeQL**: Scans changed files and dependencies
- **ESLint**: Scans changed JavaScript/TypeScript files
- **Bandit**: Scans changed Python files
- **Gitleaks**: Scans for new secrets

**PR will be blocked if**:
- Critical or High severity findings are introduced
- Secrets are detected in the code
- Required security checks fail

### Branch Protection

Main and develop branches have required status checks:

- CodeQL analysis must pass
- ESLint scan must complete
- Bandit scan must complete
- No new high-severity findings

### Manual Workflow Triggers

You can manually trigger security scans:

1. Go to **Actions** tab
2. Select the workflow (CodeQL, ESLint, or Bandit)
3. Click **Run workflow**
4. Select branch and click **Run workflow**

## Security Scan Schedule

| Tool | Trigger | Frequency |
|------|---------|-----------|
| CodeQL | Push, PR, Schedule | Weekly (Monday 3 AM UTC) |
| ESLint | Push, PR, Schedule | Weekly (Monday 3 AM UTC) |
| Bandit | Push, PR, Schedule | Weekly (Monday 3 AM UTC) |
| Gitleaks | Push | Every push |
| Trivy | Docker build | On image builds |
| Dependabot | Automatic | Daily |

## Best Practices

### For Developers

1. **Run scans locally** before pushing:
   ```bash
   # ESLint
   cd backend && npx eslint .
   cd frontend && npx eslint .
   
   # Bandit
   bandit -r . --exclude ./venv,./node_modules
   ```

2. **Address findings promptly**:
   - Don't let security findings accumulate
   - Fix high-severity issues before merging
   - Document any dismissals with clear reasoning

3. **Learn from findings**:
   - Understand why the issue was flagged
   - Apply learnings to future code
   - Share knowledge with the team

4. **Keep dependencies updated**:
   - Review Dependabot PRs regularly
   - Test dependency updates thoroughly
   - Don't ignore security patches

### For Reviewers

1. **Check security tab** before approving PRs
2. **Verify fixes** for security findings
3. **Question dismissals** - ensure they're justified
4. **Educate contributors** on security best practices

### For Maintainers

1. **Monitor security trends**:
   - Track number of findings over time
   - Identify recurring vulnerability patterns
   - Adjust scanning configuration as needed

2. **Keep tools updated**:
   - Update ESLint and plugins regularly
   - Update Bandit version
   - Review CodeQL query updates

3. **Tune configurations**:
   - Reduce false positives through configuration
   - Add project-specific rules as needed
   - Balance security with developer productivity

## Troubleshooting

### Scan Failures

**ESLint fails with "Cannot find module"**:
- Ensure dependencies are installed: `npm install`
- Check cache is working correctly
- Verify package.json is up to date

**Bandit fails with "No Python files found"**:
- Check path exclusions aren't too broad
- Verify Python files exist in scanned directories
- Check file permissions

**CodeQL fails with timeout**:
- CodeQL can be slow on large codebases
- Consider increasing timeout in workflow
- Optimize queries if possible

### False Positives

**Too many false positives**:
1. Review common patterns causing false positives
2. Configure tool-specific exclusions
3. Consider dismissing categories of false positives
4. Document exclusion rationale in ADR

**Legitimate code flagged as vulnerable**:
1. Verify the code is actually safe
2. Add inline comments explaining safety
3. Use tool-specific ignore comments if appropriate
4. Dismiss with detailed explanation

### Performance Issues

**Scans taking too long**:
1. Check if scans are running on correct paths only
2. Optimize exclusion patterns
3. Consider splitting large components
4. Review caching configuration

## Security Metrics

Track these metrics to measure security posture:

- **Total open findings** by severity
- **Mean time to remediation** for security issues
- **False positive rate** per tool
- **Scan success rate** (% of scans that complete)
- **Dependency update lag** (time between release and update)

## Additional Resources

- [GitHub Code Scanning Documentation](https://docs.github.com/en/code-security/code-scanning)
- [ESLint Security Plugin Rules](https://github.com/eslint-community/eslint-plugin-security#rules)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

## Support

For questions or issues with security scanning:

1. Check this documentation first
2. Review ADR 0005: Security Scanning
3. Check GitHub Actions workflow logs
4. Open an issue in the repository
5. Contact the security team

---

**Document Owner**: Flowstate-AI Development Team  
**Last Review**: 2025-10-10  
**Next Review**: 2026-01-10

