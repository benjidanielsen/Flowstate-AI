# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Flowstate-AI seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via:
- **Email:** security@flowstate-ai.com (or repository owner's email)
- **GitHub Security Advisories:** Use the "Security" tab in this repository

### What to Include

Please include the following information in your report:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response:** Within 48 hours
- **Status Update:** Within 5 business days
- **Fix Timeline:** Varies based on severity and complexity

### Security Update Process

1. The security report is received and assigned a primary handler
2. The problem is confirmed and affected versions are determined
3. Code is audited to find any similar problems
4. Fixes are prepared for all supported versions
5. Fixes are released as soon as possible

## Security Best Practices

### For Users

- Always use the latest stable version
- Keep dependencies up to date
- Use strong passwords and secure authentication
- Enable two-factor authentication where available
- Regularly review access logs and audit trails
- Follow the principle of least privilege for user permissions

### For Contributors

- Never commit secrets, API keys, or credentials
- Use environment variables for sensitive configuration
- Follow secure coding practices
- Sanitize all user inputs
- Implement proper authentication and authorization
- Use parameterized queries to prevent SQL injection
- Keep dependencies updated and scan for vulnerabilities

## Security Features

Flowstate-AI implements the following security measures:

- **Authentication & Authorization:** Role-Based Access Control (RBAC)
- **Data Protection:** PII redaction at ingestion and logging layers
- **Secret Management:** Environment variables and secure vaults
- **Audit Trails:** Comprehensive logging of all critical actions
- **Vulnerability Scanning:** Automated scanning via Trivy and Dependabot
- **Code Analysis:** CodeQL for security vulnerability detection
- **Secret Scanning:** Automated detection of committed secrets
- **Supply Chain Security:** Artifact signing with cosign and SLSA provenance

## Compliance

Flowstate-AI is designed with security and privacy by design principles:

- Data encryption in transit and at rest
- Regular security audits
- Compliance with industry best practices
- GDPR-compliant data handling (where applicable)

## Contact

For security-related questions or concerns, please contact:
- **Security Team:** security@flowstate-ai.com
- **Repository Owner:** [GitHub Profile](https://github.com/benjidanielsen)

## Acknowledgments

We appreciate the security research community's efforts in responsibly disclosing vulnerabilities. Contributors who report valid security issues will be acknowledged in our security advisories (unless they prefer to remain anonymous).

---

**Last Updated:** October 10, 2025

