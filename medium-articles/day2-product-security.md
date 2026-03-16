# [Product Security in My Home Lab] Series 1 ~Building an Automated Vulnerability Response Pipeline with Trivy and GitHub Actions~

In this series, you will learn how to build a Product Security pipeline in your home lab. Series 1 covers how I automated vulnerability scanning, triage, and response using open-source tools.

---

*Disclaimer: All content in this article is based on experiments conducted in my personal home lab and test environment. This work is not affiliated with, endorsed by, or related to any company I currently work for or have worked for. All opinions are my own.*

---

![Security scanning terminal with code](https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=1200)
*Photo by [Markus Spiske](https://unsplash.com/@markusspiske) on [Unsplash](https://unsplash.com)*

## What is Product Security?

Product Security is the practice of finding and fixing security vulnerabilities in the software you build — before attackers find them first. It covers the entire software development lifecycle, from code review to dependency scanning to runtime protection.

Key areas:

- **SAST (Static Application Security Testing)** — Scanning source code for vulnerabilities
- **SCA (Software Composition Analysis)** — Checking dependencies for known CVEs
- **DAST (Dynamic Application Security Testing)** — Testing running applications
- **Container Security** — Scanning container images for vulnerabilities
- **SBOM (Software Bill of Materials)** — Knowing exactly what is in your software

## Why Automate Vulnerability Response?

Most security teams I know have same problem: they can find vulnerabilities easily, but responding to them is still very manual process. You run a scan, get 500 findings, export to spreadsheet, then spend hours triaging.

In my home lab, I wanted to build pipeline that automatically scans, triages, and creates actionable tickets — without human touching anything until the decision point.

## My Home Lab Product Security Stack

Here is what I am working with:

- **Scanner**: Trivy (open-source, covers containers + IaC + SBOM)
- **CI/CD**: GitHub Actions
- **Registry**: GitHub Container Registry (GHCR)
- **Ticketing**: Jira (free tier)
- **Notification**: Slack webhooks
- **Policy Engine**: OPA (Open Policy Agent) for custom policies
- **SBOM Format**: CycloneDX

## Architecture Overview

The flow looks like this:

```
Developer pushes code
        ↓
   GitHub Actions triggered
        ↓
   ┌─────────────────────────┐
   │  Trivy Scan Phase       │
   │  - Container image scan │
   │  - IaC misconfig scan   │
   │  - Dependency scan      │
   │  - Secret detection     │
   │  - SBOM generation      │
   └─────────────────────────┘
        ↓
   ┌─────────────────────────┐
   │  Policy Evaluation      │
   │  - OPA severity rules   │
   │  - SLA assignment       │
   │  - Auto-fix candidates  │
   └─────────────────────────┘
        ↓
   ┌─────────────────────────┐
   │  Response Actions       │
   │  - Block deploy (CRIT)  │
   │  - Create Jira ticket   │
   │  - Slack notification   │
   │  - SBOM upload          │
   └─────────────────────────┘
```

## Step 1: Set Up Trivy in GitHub Actions

First, I configured Trivy to run on every pull request and main branch push. The key is scanning multiple targets in one workflow:

```yaml
# .github/workflows/security-scan.yml
name: Security Scan Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  vulnerability-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build container image
        run: docker build -t myapp:${{ github.sha }} .
      
      # Container image vulnerability scan
      - name: Trivy image scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'json'
          output: 'trivy-image-results.json'
          severity: 'CRITICAL,HIGH,MEDIUM'
      
      # Infrastructure as Code scan
      - name: Trivy IaC scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: '.'
          format: 'json'
          output: 'trivy-iac-results.json'
      
      # Dependency scan
      - name: Trivy filesystem scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'json'
          output: 'trivy-fs-results.json'
      
      # Generate SBOM
      - name: Generate SBOM
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'image'
          image-ref: 'myapp:${{ github.sha }}'
          format: 'cyclonedx'
          output: 'sbom.json'
      
      # Process results
      - name: Triage and respond
        run: python3 scripts/vuln-triage.py
        env:
          JIRA_TOKEN: ${{ secrets.JIRA_TOKEN }}
          SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
```

## Step 2: Build the Triage Engine

The triage engine is where the magic happens. It takes raw scan results and makes decisions based on custom policies. This is the part that many articles do not cover — the decision logic between "found vulnerability" and "what do we do about it."

```python
import json
from datetime import datetime, timedelta

class VulnTriageEngine:
    """Automated vulnerability triage with SLA assignment"""
    
    # SLA definitions (days to remediate)
    SLA_MAP = {
        'CRITICAL': 3,
        'HIGH': 14,
        'MEDIUM': 30,
        'LOW': 90
    }
    
    # Known false positive patterns
    FALSE_POSITIVE_PATTERNS = [
        {'pkg': 'linux-libc-dev', 'reason': 'Kernel vuln not exploitable in container'},
        {'pkg': 'libsystemd0', 'reason': 'Not used in container runtime'},
    ]
    
    def __init__(self, scan_results):
        self.results = scan_results
        self.triaged = []
    
    def triage(self):
        """Process all vulnerabilities through triage logic"""
        for vuln in self.results.get('Results', []):
            target = vuln.get('Target', '')
            for v in vuln.get('Vulnerabilities', []):
                decision = self._evaluate(v, target)
                self.triaged.append(decision)
        
        return self.triaged
    
    def _evaluate(self, vuln, target):
        """Evaluate single vulnerability"""
        cve_id = vuln.get('VulnerabilityID', '')
        severity = vuln.get('Severity', 'UNKNOWN')
        pkg = vuln.get('PkgName', '')
        fixed_version = vuln.get('FixedVersion', '')
        
        result = {
            'cve': cve_id,
            'severity': severity,
            'package': pkg,
            'target': target,
            'installed': vuln.get('InstalledVersion', ''),
            'fixed': fixed_version,
            'title': vuln.get('Title', ''),
            'action': 'investigate',
            'sla_days': self.SLA_MAP.get(severity, 90),
            'due_date': None,
            'auto_fixable': False
        }
        
        # Check false positive patterns
        for fp in self.FALSE_POSITIVE_PATTERNS:
            if fp['pkg'] in pkg:
                result['action'] = 'suppress'
                result['reason'] = fp['reason']
                return result
        
        # Auto-fixable if fixed version exists
        if fixed_version:
            result['auto_fixable'] = True
            if severity in ('CRITICAL', 'HIGH'):
                result['action'] = 'auto_pr'
            else:
                result['action'] = 'ticket'
        
        # No fix available
        if not fixed_version:
            if severity == 'CRITICAL':
                result['action'] = 'escalate'
            else:
                result['action'] = 'monitor'
        
        # Calculate SLA due date
        result['due_date'] = (
            datetime.now() + timedelta(days=result['sla_days'])
        ).strftime('%Y-%m-%d')
        
        return result
```

## Step 3: OPA Policy for Deployment Gates

I use Open Policy Agent to enforce deployment policies. This is what makes the pipeline a real security gate — not just a notification system:

```rego
# policy/deploy-gate.rego
package security.deploy

default allow = true

# Block deployment if any CRITICAL vulnerability has no fix suppression
deny[msg] {
    input.vulnerabilities[i].severity == "CRITICAL"
    input.vulnerabilities[i].action != "suppress"
    input.vulnerabilities[i].fixed != ""
    msg := sprintf("CRITICAL vuln %s in %s has fix available (%s) - must patch before deploy", 
        [input.vulnerabilities[i].cve, 
         input.vulnerabilities[i].package,
         input.vulnerabilities[i].fixed])
}

# Warn if HIGH vulns exceed threshold
warn[msg] {
    high_count := count([v | 
        v := input.vulnerabilities[_]
        v.severity == "HIGH"
        v.action != "suppress"
    ])
    high_count > 5
    msg := sprintf("Too many HIGH vulnerabilities: %d (threshold: 5)", [high_count])
}

# Require SBOM for all production deployments
deny[msg] {
    input.environment == "production"
    not input.sbom_generated
    msg := "SBOM is required for production deployments"
}
```

## Step 4: Automated Response Actions

When the triage engine makes a decision, these response actions execute automatically:

### Auto-Create PR for Fixable Vulnerabilities

```python
import subprocess

def create_fix_pr(vuln_data):
    """Create automated PR for dependency update"""
    pkg = vuln_data['package']
    fixed = vuln_data['fixed']
    cve = vuln_data['cve']
    
    branch_name = f"security-fix/{cve.lower()}"
    
    # Create branch
    subprocess.run(['git', 'checkout', '-b', branch_name])
    
    # Update dependency (example for Python)
    update_requirement(pkg, fixed)
    
    # Commit and push
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 
        f'fix(security): update {pkg} to {fixed} ({cve})'])
    subprocess.run(['git', 'push', 'origin', branch_name])
    
    # Create PR via GitHub CLI
    subprocess.run(['gh', 'pr', 'create',
        '--title', f'[Security] Fix {cve}: Update {pkg} to {fixed}',
        '--body', generate_pr_body(vuln_data),
        '--label', 'security,automated'])
```

### Slack Notification with Context

```python
import requests

def notify_security_team(triaged_vulns):
    """Send summary to Slack with actionable context"""
    
    critical = [v for v in triaged_vulns if v['severity'] == 'CRITICAL']
    high = [v for v in triaged_vulns if v['severity'] == 'HIGH']
    auto_fixed = [v for v in triaged_vulns if v['action'] == 'auto_pr']
    
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", 
                     "text": "🔒 Security Scan Results"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", 
                 "text": f"*Critical:* {len(critical)}"},
                {"type": "mrkdwn", 
                 "text": f"*High:* {len(high)}"},
                {"type": "mrkdwn", 
                 "text": f"*Auto-PR Created:* {len(auto_fixed)}"},
                {"type": "mrkdwn", 
                 "text": f"*Total Findings:* {len(triaged_vulns)}"}
            ]
        }
    ]
    
    # Add critical vuln details
    for v in critical[:3]:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn",
                     "text": f"🚨 *{v['cve']}* — `{v['package']}`\n"
                             f"Action: {v['action']} | "
                             f"SLA: {v['due_date']}"}
        })
    
    requests.post(webhook_url, json={"blocks": blocks})
```

## Step 5: SBOM Management

SBOM generation is not just compliance checkbox anymore. With EU Cyber Resilience Act and US Executive Order requirements, knowing exactly what is in your software becomes critical.

```python
def process_sbom(sbom_path, artifact_name):
    """Process and store SBOM for compliance tracking"""
    
    with open(sbom_path) as f:
        sbom = json.load(f)
    
    # Extract key metrics
    components = sbom.get('components', [])
    
    summary = {
        'artifact': artifact_name,
        'generated': datetime.now().isoformat(),
        'format': 'CycloneDX',
        'total_components': len(components),
        'licenses': list(set(
            c.get('licenses', [{}])[0].get('license', {}).get('id', 'unknown')
            for c in components if c.get('licenses')
        )),
        'direct_deps': len([c for c in components 
                           if c.get('scope') == 'required']),
        'transitive_deps': len([c for c in components 
                               if c.get('scope') != 'required']),
    }
    
    # Store for tracking
    store_sbom_history(summary)
    
    return summary
```

## Results After 3 Months

After running this pipeline in my home lab for three months:

- **Mean time to detect** new vulnerability: from next scheduled scan (days) to every PR (minutes)
- **Auto-fix rate**: about 40% of critical and high vulnerabilities had auto-generated PRs
- **False positive reduction**: OPA policies and suppression rules eliminated roughly 60% of noise
- **SLA compliance**: every vulnerability now has clear owner and deadline
- **SBOM coverage**: 100% of container images have SBOM generated automatically

## Trial & Error Section

Not everything worked on first try. Here is what I learned the hard way:

1. **Trivy scan timeout in CI**: My first pipeline kept timing out because I was scanning a 2GB image. Solution was to use `.trivyignore` for known acceptable findings and scan the base image separately.

2. **Too many Jira tickets**: Initially I created ticket for every single finding. Within one week I had 200+ tickets. Solution was to group vulnerabilities by package and create one ticket per package update.

3. **OPA policy too strict at beginning**: I blocked all deployments with any HIGH finding. Nobody could deploy for two days. Had to gradually tighten the policy — start with CRITICAL only, then add HIGH threshold.

4. **SBOM was not so useful without tracking**: Generating SBOM is easy. But without storing history and comparing changes, it is just a JSON file sitting there. I added a simple diff tool to show what changed between versions.

## What is Next?

In Series 2, I will cover how I integrated runtime vulnerability scanning with Falco and built a feedback loop from production back to the CI pipeline.

---

## References

- **Trivy** (Aqua Security): https://github.com/aquasecurity/trivy
- **OWASP Dependency-Check**: https://owasp.org/www-project-dependency-check/
- **OPA (Open Policy Agent)**: https://www.openpolicyagent.org/
- **CycloneDX SBOM Standard**: https://cyclonedx.org/
- **EU Cyber Resilience Act**: https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act
- **NIST SSDF (Secure Software Development Framework)**: https://csrc.nist.gov/projects/ssdf
- **CISA Known Exploited Vulnerabilities (KEV)**: https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- **GitHub Actions Security Hardening**: https://docs.github.com/en/actions/security-guides

---

*Follow me for more practical security engineering content from my home lab.*
