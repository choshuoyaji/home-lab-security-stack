# CrowdStrike Falcon EDR Tuning Guide

> Lessons learned from tuning CrowdStrike in my home lab environment

## False Positive Reduction Strategy

### High-Volume FP Sources (Home Lab)
1. **Developer tools** — Compilers, interpreters, debuggers
2. **Security tools** — Vulnerability scanners, pen testing tools
3. **Automation scripts** — Ansible, Terraform, CI/CD agents

### Exclusion Policy
```json
{
  "exclusion_type": "process",
  "rules": [
    {
      "name": "VS Code Server",
      "path": "*\\Microsoft VS Code\\*",
      "applies_to": ["machine-learning", "sensor-based"],
      "justification": "High-volume FP from language servers"
    },
    {
      "name": "Terraform Provider",
      "path": "*\\.terraform\\providers\\*",
      "applies_to": ["sensor-based"],
      "justification": "Provider binaries trigger on execution"
    }
  ]
}
```

### Custom IOA Rules
| Rule | MITRE ID | Severity | Description |
|------|----------|----------|-------------|
| LOLBin + Network | T1218 | High | LOLBin with external connection |
| Encoded PowerShell | T1059.001 | Medium | Base64 encoded commands |
| LSASS Access | T1003.001 | Critical | Non-standard LSASS access |

## Performance Optimization
- Sensor CPU target: < 5% average
- Memory usage: < 200MB
- Scan exclusions for build directories
- Reduced logging for known-good paths
