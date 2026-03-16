# Product Security

Part of the [Home Lab Security Stack](https://github.com/choshuoyaji/home-lab-security-stack).

## Articles

| Series | Title | Medium | dev.to |
|--------|-------|--------|--------|
| 1 | Building an Automated Vulnerability Response Pipeline with Trivy and GitHub Actions | [Read](https://takahiro-oda.medium.com/product-security-in-my-home-lab-series-1-building-an-automated-vulnerability-response-pipeline-17a579462805) | Coming soon |

## Components

### vulnerability-response/
- `vuln-triage.py` — Automated vulnerability triage engine with SLA assignment
- `deploy-gate.rego` — OPA policy for deployment gates

### .github/workflows/
- `security-scan.yml` — GitHub Actions workflow for Trivy scanning pipeline

## Stack
- **Scanner**: Trivy (containers + IaC + SBOM)
- **CI/CD**: GitHub Actions
- **Policy Engine**: OPA (Open Policy Agent)
- **SBOM Format**: CycloneDX

See the `docs/` directory for detailed documentation.
