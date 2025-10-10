# ADR 0002: Supply Chain Security Implementation

**Status:** Accepted  
**Date:** 2025-01-10  
**Deciders:** Development Team  
**Technical Story:** Phase B - Supply Chain Security

## Context and Problem Statement

Modern software supply chains are increasingly targeted by attackers. We need to implement comprehensive supply chain security measures to ensure the integrity and authenticity of our artifacts, dependencies, and deployments. This includes cryptographic signing, software bill of materials (SBOM), provenance attestation, and continuous vulnerability scanning.

## Decision Drivers

- **Security:** Protect against supply chain attacks and tampering
- **Compliance:** Meet industry standards for software supply chain security
- **Transparency:** Provide visibility into dependencies and vulnerabilities
- **Automation:** Integrate security checks into CI/CD pipelines
- **Verifiability:** Enable users to verify artifact authenticity

## Considered Options

### Option 1: Minimal Security (Status Quo)
- Basic vulnerability scanning with Trivy
- No artifact signing
- No SBOM generation
- Manual dependency review

**Pros:**
- Low implementation effort
- No additional tooling required

**Cons:**
- Vulnerable to supply chain attacks
- No artifact authenticity verification
- Poor visibility into dependencies
- Manual processes prone to errors

### Option 2: Comprehensive Supply Chain Security (Selected)
- Artifact signing with cosign (Sigstore)
- SBOM generation with syft
- SLSA Level 3 provenance
- Automated dependency review
- Multi-tool vulnerability scanning

**Pros:**
- Strong protection against tampering
- Industry-standard security practices
- Automated security checks
- Full transparency and verifiability
- Meets compliance requirements

**Cons:**
- Higher implementation complexity
- Additional CI/CD time
- Requires learning new tools

### Option 3: Hybrid Approach
- Artifact signing only
- Basic SBOM generation
- No provenance attestation
- Limited vulnerability scanning

**Pros:**
- Moderate implementation effort
- Some security improvements

**Cons:**
- Incomplete security coverage
- Missing key supply chain protections
- Limited compliance value

## Decision Outcome

**Chosen option:** Option 2 - Comprehensive Supply Chain Security

We will implement a full supply chain security solution including artifact signing, SBOM generation, SLSA provenance, and comprehensive vulnerability scanning.

### Implementation Details

#### 1. Container Image Security

**Enhanced docker.yml workflow:**
- Keyless signing with cosign using OIDC
- SBOM generation in SPDX format using syft
- SBOM attachment and signing
- Trivy vulnerability scanning with SARIF upload
- Signature verification in CI
- Build provenance and attestation

**Benefits:**
- Images cryptographically signed
- Complete dependency transparency
- Automated vulnerability detection
- Verifiable build provenance

#### 2. Release Automation

**New release.yml workflow:**
- Semantic version validation
- Multi-component artifact building
- Artifact signing with cosign
- SLSA Level 3 provenance generation
- Automated changelog generation
- GitHub Release creation with attestations

**Benefits:**
- Reproducible builds
- Tamper-evident releases
- Automated release process
- Full supply chain transparency

#### 3. Dependency Security

**New dependency-review.yml workflow:**
- Automated dependency review on PRs
- Vulnerability detection before merge
- License compliance checking
- Configurable severity thresholds

**Benefits:**
- Prevent vulnerable dependencies
- Enforce license policies
- Early detection of security issues
- Automated compliance checks

#### 4. Continuous Security Scanning

**New security-scan.yml workflow:**
- Daily scheduled scans
- Multi-tool scanning (Trivy, Grype, Safety, npm audit)
- SARIF upload to GitHub Security
- Automated issue creation for critical findings

**Benefits:**
- Continuous security monitoring
- Early vulnerability detection
- Multiple scanning perspectives
- Automated alerting

### Verification Commands

Users can verify artifacts using these commands:

```bash
# Verify container image signature
cosign verify \
  ghcr.io/benjidanielsen/flowstate-ai:backend@sha256:... \
  --certificate-identity-regexp="https://github.com/benjidanielsen/flowstate-ai/*" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com

# Verify artifact signature
cosign verify-blob \
  --bundle artifact.cosign.bundle \
  --certificate-identity-regexp="https://github.com/benjidanielsen/flowstate-ai/*" \
  --certificate-oidc-issuer=https://token.actions.githubusercontent.com \
  artifact.tar.gz

# Verify SLSA provenance
slsa-verifier verify-artifact \
  --provenance-path provenance-v1.0.0.intoto.jsonl \
  --source-uri github.com/benjidanielsen/flowstate-ai \
  artifact.tar.gz

# View SBOM
cosign download sbom ghcr.io/benjidanielsen/flowstate-ai:backend@sha256:...
```

## Consequences

### Positive

- **Enhanced Security:** Strong protection against supply chain attacks
- **Transparency:** Complete visibility into dependencies and vulnerabilities
- **Compliance:** Meets SLSA Level 3 and industry standards
- **Automation:** Security checks integrated into CI/CD
- **Trust:** Users can verify artifact authenticity
- **Early Detection:** Vulnerabilities caught before production

### Negative

- **CI/CD Time:** Additional 2-3 minutes per workflow run
- **Complexity:** More tools and processes to maintain
- **Learning Curve:** Team needs to understand new security tools
- **Storage:** SBOMs and attestations increase artifact size

### Neutral

- **Tooling:** Relies on Sigstore ecosystem (cosign, syft)
- **GitHub Dependency:** Uses GitHub Security features
- **Maintenance:** Requires keeping security tools updated

## Compliance and Standards

This implementation aligns with:

- **SLSA Level 3:** Build provenance and non-falsifiable attestations
- **NIST SSDF:** Secure Software Development Framework
- **OpenSSF Best Practices:** Signed releases, vulnerability scanning
- **SBOM Standards:** SPDX format for software bill of materials

## Monitoring and Metrics

We will track:

- Number of vulnerabilities detected per scan
- Time to remediate critical vulnerabilities
- Dependency update frequency
- Failed signature verifications
- License compliance violations

## Related Decisions

- ADR 0001: Phase 0 Baseline Establishment
- Future: ADR 0003 - Container Optimization (Phase C)
- Future: ADR 0004 - Deployment Strategy (Phase E)

## References

- [Sigstore Documentation](https://docs.sigstore.dev/)
- [SLSA Framework](https://slsa.dev/)
- [SPDX Specification](https://spdx.dev/)
- [GitHub Dependency Review](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

