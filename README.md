# 🛡️ Home Lab Security Stack

> Real-world security engineering configurations, detection rules, and automation playbooks — all built and tested in my personal home lab.

[![Medium](https://img.shields.io/badge/Medium-@takahiro--oda-12100E?style=flat&logo=medium)](https://takahiro-oda.medium.com)
[![dev.to](https://img.shields.io/badge/dev.to-@takahiro__oda-0A0A0A?style=flat&logo=devdotto)](https://dev.to/takahiro_oda)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Takahiro_Oda-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/takahiro-oda/)

## 📋 About

This repository documents my journey building a comprehensive security stack in my home lab. Every configuration, rule, and playbook here has been hands-on tested and refined through real experimentation.

**What you'll find:**
- 🔍 **Detection Engineering** — Sigma rules, detection pipelines, threat hunting queries
- 🤖 **SOAR** — Security orchestration playbooks, automated response workflows
- 📊 **Security Monitoring** — SIEM configurations, log parsers, dashboards
- 🛡️ **EDR/XDR** — Endpoint detection tuning, response configurations
- ☁️ **Cloud Security** — Terraform modules, IAM policies, compliance checks
- 🔐 **Product Security** — Vulnerability response automation, SAST/DAST pipelines
- 🧠 **AI Security** — LLM security testing, prompt injection defenses
- 🚨 **Incident Response** — IR playbooks, forensic collection scripts

## 🗂️ Repository Structure

```
home-lab-security-stack/
├── detection-engineering/    # Sigma rules, detection pipelines
│   ├── sigma-rules/         # Custom Sigma detection rules
│   ├── pipelines/           # Detection-as-Code CI/CD
│   └── docs/                # Detection engineering guides
├── soar/                    # Security orchestration & automation
│   ├── playbooks/           # SOAR response playbooks
│   ├── integrations/        # Tool integrations
│   └── docs/                # SOAR architecture docs
├── security-monitoring/     # SIEM & monitoring platform
│   ├── dashboards/          # Security dashboards
│   ├── parsers/             # Log parsers & normalizers
│   ├── data-sources/        # Data source configurations
│   └── docs/                # Monitoring platform docs
├── edr-xdr/                 # Endpoint detection & response
│   ├── configs/             # EDR configurations
│   ├── tuning/              # Detection tuning rules
│   └── docs/                # EDR/XDR optimization guides
├── cloud-security/          # Cloud security infrastructure
│   ├── terraform/           # IaC security modules
│   ├── iam/                 # IAM policies & roles
│   ├── compliance/          # Compliance frameworks
│   └── docs/                # Cloud security guides
├── product-security/        # Application & product security
│   ├── vulnerability-response/  # Vuln management automation
│   ├── sast-dast/           # Security testing pipelines
│   └── docs/                # Product security docs
├── ai-security/             # AI/ML security (NEW!)
│   ├── scripts/             # Red team orchestrator, MCP auditor
│   ├── guardrails/          # Input/output security guardrails
│   ├── configs/             # Garak & CI/CD configs
│   ├── tests/               # Guardrails unit tests
│   └── llm-security/        # LLM security test cases
├── incident-response/       # IR & forensics
│   ├── playbooks/           # IR playbooks
│   ├── forensics/           # Forensic scripts
│   └── docs/                # IR documentation
└── articles/                # Published article source files
```

## 📝 Article Series

Each directory corresponds to an article series published on [Medium](https://takahiro-oda.medium.com) and [dev.to](https://dev.to/takahiro_oda):

| Series | Category | Latest Article |
|--------|----------|---------------|
| Detection Engineering in My Home Lab | Detection Engineering | [Series 1: Building Sigma Rules](https://takahiro-oda.medium.com/detection-engineering-in-my-home-lab-series-1-building-20-sigma-rules-for-multi-source-threat-614015b067e8) |
| SOAR in My Home Lab | SOAR | Coming Soon |
| Security Monitoring in My Home Lab | Security Monitoring | Coming Soon |
| EDR/XDR in My Home Lab | EDR/XDR | Coming Soon |
| Cloud Security in My Home Lab | Cloud Security | Coming Soon |
| Product Security in My Home Lab | Product Security | [Series 1: Vulnerability Response Pipeline](https://takahiro-oda.medium.com/product-security-in-my-home-lab-series-1-building-an-automated-vulnerability-response-pipeline-17a579462805) |
| AI Security in My Home Lab | AI Security | Series 1: LLM Red Teaming (Publishing Today) |
| Incident Response in My Home Lab | Incident Response | Coming Soon |

## 🏠 Home Lab Environment

- **SIEM**: Wazuh + OpenSearch
- **EDR**: CrowdStrike Falcon (evaluation license)
- **SOAR**: Shuffle SOAR
- **IaC**: Terraform + Ansible
- **Cloud**: AWS (personal account)
- **Monitoring**: Grafana + Prometheus
- **Detection**: Sigma rules + custom pipelines
- **Virtualization**: Proxmox VE

## 🔗 References & Inspiration
- [NVIDIA/garak](https://github.com/NVIDIA/garak) — LLM vulnerability scanner
- [AgentSeal/agentseal](https://github.com/AgentSeal/agentseal) — AI agent security toolkit
- [OWASP Top 10 for LLM](https://genai.owasp.org/llm-top-10/) — LLM application security risks
- [SigmaHQ/sigma](https://github.com/SigmaHQ/sigma) — Generic Signature Format for SIEM Systems
- [Shuffle/Shuffle](https://github.com/Shuffle/Shuffle) — Security automation platform
- [wazuh/wazuh](https://github.com/wazuh/wazuh) — Open Source Security Platform
- [Yamato-Security/hayabusa](https://github.com/Yamato-Security/hayabusa) — Sigma-based threat hunting
- [The-Art-of-Hacking/h4cker](https://github.com/The-Art-of-Hacking/h4cker) — Comprehensive security resources
- [meirwah/awesome-incident-response](https://github.com/meirwah/awesome-incident-response) — Curated IR tools
- [turbot/steampipe](https://github.com/turbot/steampipe) — Zero-ETL cloud security queries
- [tenable/terrascan](https://github.com/tenable/terrascan) — IaC security scanning
- [MITRE ATT&CK](https://attack.mitre.org/) — Adversary tactics and techniques

## 🤝 Contributing

Found something interesting? Feel free to open an issue or submit a PR!

## ⚠️ Disclaimer

All content in this repository is based on experiments conducted in my personal home lab and test environment. This work is not affiliated with, endorsed by, or related to any company I currently work for or have worked for. All opinions are my own.

---

⭐ **Star this repo** if you find it useful! Follow my journey on [Medium](https://takahiro-oda.medium.com) and [dev.to](https://dev.to/takahiro_oda).


## 📚 Articles

- **[2026-03-29]** [[Application Security in My Home Lab] Series 1 ~Building a Comprehensive SAST/DAST Pipeline with AI-Enhanced Vulnerability Detection~](articles/2026-03-29-application-security-in-my-home-lab-series-1-building-a-comprehensive-sastdast-pipeline-with-ai-enhanced-vulnerability-detection/) - Code examples and configurations
