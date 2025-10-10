# ADR 0005: ESLint and Bandit Security Scanning

**Date**: 2025-10-10  
**Status**: Accepted  
**Context**: Security Enhancement  
**Decision Makers**: Flowstate-AI Development Team

## Context and Problem Statement

While the project already has CodeQL security scanning configured, there was a need for language-specific security analysis tools that provide deeper, more specialized scanning for JavaScript/TypeScript and Python code. CodeQL provides broad coverage across multiple languages, but specialized tools can catch language-specific security issues and code quality problems that general-purpose scanners might miss.

The project needed additional security scanning that would provide language-specific security analysis for JavaScript/TypeScript and Python, integrate seamlessly with existing GitHub security infrastructure, run automatically on code changes, provide actionable feedback to developers, and maintain minimal performance impact on CI/CD pipelines.

## Decision Drivers

Several factors influenced the decision to add ESLint and Bandit security scanning. **Language specificity** was crucial, as specialized tools understand language-specific security patterns and common vulnerabilities better than general scanners. **Developer familiarity** played a role since ESLint is already widely used in JavaScript/TypeScript projects, and Bandit is the standard for Python security scanning. **Integration quality** was important for seamless integration with GitHub Security tab and SARIF format support. **Cost effectiveness** required free, open-source tools with no licensing costs. **Performance** demanded fast scanning with minimal CI/CD overhead.

## Considered Options

### Option 1: Continue with CodeQL Only

CodeQL provides comprehensive multi-language security analysis with deep semantic analysis, official GitHub support, and regular updates. However, it has limitations including less specialized for language-specific patterns, slower scan times compared to focused tools, and fewer JavaScript/TypeScript-specific security rules.

### Option 2: Add Commercial Security Platform

Commercial platforms like Snyk, Checkmarx, or Veracode offer comprehensive security coverage, professional support, and advanced features. However, they come with significant costs including licensing fees, potential vendor lock-in, and complexity in setup and maintenance.

### Option 3: Add ESLint + Bandit (Selected)

ESLint for JavaScript/TypeScript and Bandit for Python provide language-specific security analysis, are free and open-source, integrate well with GitHub, have fast scan times, and are widely adopted in the community.

## Decision Outcome

**Chosen Option**: Option 3 - Add ESLint and Bandit security scanning alongside existing CodeQL

This solution provides the best balance of comprehensive coverage, cost effectiveness, and developer experience.

### Implementation Details

**ESLint Security Scanning** uses ESLint version 8.x+ with security plugins including eslint-plugin-security for security-focused rules and @typescript-eslint for TypeScript-specific analysis. It outputs results in SARIF format using @microsoft/eslint-formatter-sarif and scans both backend (Node.js/TypeScript) and frontend (React/TypeScript) code.

**Bandit Security Scanning** uses Bandit version 1.7+ with SARIF output support. It scans root Python files and the python-worker directory, skips common false positives (B101: assert_used, B601: paramiko_calls), and provides Python-specific security issue detection.

### Workflow Configuration

Both workflows are configured with multiple triggers. They run on push to main and develop branches when relevant files change, on pull requests to main and develop branches, on a weekly schedule (Monday 3 AM UTC), and can be manually triggered via workflow_dispatch.

The workflows have appropriate permissions including read access to repository contents, write access to security-events for SARIF upload, and read access to actions for workflow status.

### Scan Coverage

**ESLint scans** cover the backend directory (Node.js/Express/TypeScript) and frontend directory (React/TypeScript/Vite). It checks for security vulnerabilities, code quality issues, TypeScript type safety, and React best practices.

**Bandit scans** cover root-level Python files and the python-worker directory (FastAPI). It checks for hardcoded passwords/secrets, SQL injection vulnerabilities, command injection risks, insecure cryptography usage, and unsafe deserialization.

### Integration with GitHub Security

Both tools upload results to the GitHub Security tab using the CodeQL action's SARIF upload functionality. Results appear alongside CodeQL findings with separate categories (eslint-backend, eslint-frontend, bandit-root, bandit-worker). They provide detailed vulnerability descriptions, suggested fixes, and severity ratings. Results are retained for 30 days as workflow artifacts.

## Consequences

### Positive

The implementation delivers numerous benefits. **Enhanced security coverage** comes from language-specific security analysis that catches issues CodeQL might miss, complementary scanning approaches providing defense in depth, and faster feedback on security issues. **Better developer experience** includes familiar tools that developers already know, actionable feedback with specific code locations, and integration with existing development workflows. **Cost effectiveness** results from free, open-source tools with no licensing costs and minimal infrastructure overhead. **Improved code quality** comes from security scanning that also catches code quality issues, consistent enforcement of security best practices, and automated checks preventing security regressions.

### Negative

There are some limitations to consider. **Additional CI/CD time** means approximately 2-3 minutes added to workflow runs and increased GitHub Actions minutes usage. **Maintenance overhead** requires keeping ESLint and Bandit dependencies updated, managing false positives and exclusions, and reviewing and triaging additional security findings. **Potential noise** can come from false positives requiring configuration and overlap with CodeQL findings in some cases.

### Neutral

Some aspects are neither clearly positive nor negative. **Learning curve** exists for teams unfamiliar with these tools, though it is minimal for most developers. **Configuration needs** may require adjusting rules and exclusions over time based on project needs and team preferences.

## Technical Implementation

### ESLint Configuration

The ESLint workflow installs necessary dependencies including eslint core, @microsoft/eslint-formatter-sarif for SARIF output, eslint-plugin-security for security rules, and @typescript-eslint packages for TypeScript support. It scans JavaScript, JSX, TypeScript, and TSX files with security-focused rules enabled. Results are uploaded to GitHub Security and stored as artifacts.

### Bandit Configuration

The Bandit workflow installs Bandit with SARIF support using `bandit[sarif]`. It scans all Python files recursively, excluding virtual environments and build directories. Common false positives are skipped (B101 for assert statements, B601 for paramiko calls if not used). Results are uploaded to GitHub Security and stored as artifacts.

### Customization Options

Teams can customize the scanning through several mechanisms. **ESLint rules** can be configured via .eslintrc files in backend and frontend directories. **Bandit configuration** can use .bandit files for project-specific settings. **Workflow triggers** can be adjusted to run more or less frequently. **Exclusions** can be added for specific files or directories as needed.

### Performance Optimization

Several optimizations ensure efficient scanning. **Path filters** trigger workflows only when relevant files change. **Caching** uses npm and pip caching to speed up dependency installation. **Parallel execution** runs ESLint for backend and frontend in parallel. **Continue on error** ensures workflows complete even if issues are found, allowing full results to be uploaded.

## Compliance and Standards

The security scanning implementation aligns with industry best practices. **SARIF format** follows the Static Analysis Results Interchange Format (SARIF) standard. **Security standards** check for OWASP Top 10 vulnerabilities and CWE (Common Weakness Enumeration) patterns. **GitHub integration** uses official GitHub Actions and CodeQL integration. **Open source** leverages community-maintained, widely adopted tools.

## Maintenance and Evolution

### Regular Maintenance

The security scanning requires ongoing maintenance including weekly automated scans to catch new issues, regular dependency updates for ESLint and Bandit, review and triage of security findings, and configuration adjustments based on false positives.

### Future Enhancements

Potential future enhancements include adding custom ESLint rules specific to project needs, implementing Bandit baseline for tracking progress, adding security metrics dashboards, integrating with IDE plugins for real-time feedback, and expanding to additional security tools as needed.

### Monitoring

Security scanning health is monitored through several mechanisms. GitHub Actions workflows report scan status, the Security tab shows all findings across tools, workflow artifacts preserve detailed results, and summary reports provide quick overview of scan results.

## Integration with Existing Security Infrastructure

The new scanning tools complement existing security measures. **CodeQL** provides broad multi-language semantic analysis. **ESLint** adds JavaScript/TypeScript-specific security and quality checks. **Bandit** adds Python-specific security analysis. **Gitleaks** (if configured) scans for secrets in code. **Dependabot** monitors dependency vulnerabilities. **Trivy** (in Docker workflow) scans container images.

Together, these tools provide comprehensive, defense-in-depth security coverage across the entire stack.

## Expected Outcomes

After implementing ESLint and Bandit scanning, the project will benefit from earlier detection of security issues in the development cycle, reduced security vulnerabilities in production code, improved code quality and maintainability, better developer awareness of security best practices, and automated enforcement of security standards.

### Success Metrics

Success will be measured by reduction in security vulnerabilities found in production, faster time to detect and fix security issues, increased developer confidence in code security, and decreased security-related incidents.

## Migration and Rollout

The rollout of security scanning follows a phased approach. **Phase 1 (Initial Deployment)** adds workflows to repository and runs initial scans. **Phase 2 (Baseline Establishment)** reviews and triages initial findings, configures exclusions for false positives, and establishes baseline security posture. **Phase 3 (Enforcement)** enables required checks for pull requests, integrates findings into development workflow, and trains team on addressing security issues. **Phase 4 (Optimization)** fine-tunes rules and configurations, adds custom rules as needed, and optimizes scan performance.

## References

- [ESLint Documentation](https://eslint.org/)
- [ESLint Security Plugin](https://github.com/eslint-community/eslint-plugin-security)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [SARIF Format Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-10-10 | Flowstate-AI Development Team | Initial decision and implementation |

---

**Approved By**: Flowstate-AI Evolution Framework  
**Next Review**: 2026-01-10 (Quarterly review)

