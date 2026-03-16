# [Detection Engineering in My Home Lab] Series 1 ~Building 20+ Sigma Rules for Multi-Source Threat Detection~

In this series, you will learn how to build a Detection Engineering pipeline from scratch using your home lab. Series 1 covers writing Sigma rules across multiple data sources.

---

## What is Detection Engineering?

Detection Engineering is the practice of designing, building, testing, and maintaining threat detection logic as code. Instead of relying on out-of-the-box vendor alerts, you write custom detection rules tailored to your environment.

Key concepts:

- **Detection-as-Code** — Detection logic stored in version control (Git)
- **Sigma Rules** — Open standard for detection rules, portable across SIEMs
- **MITRE ATT&CK** — Framework for mapping detection coverage to adversary techniques

## Why Sigma?

Sigma is to log detection what YARA is to file detection. Write once, deploy anywhere.

Benefits:

- Portability across SIEMs (Splunk, Elastic, Sentinel)
- Version control with Git — PRs, reviews, history
- Thousands of community-maintained rules
- One consistent format across all data sources

## My Home Lab Setup

Here is what I am working with:

- **SIEM**: Splunk (dev license)
- **EDR**: CrowdStrike Falcon + Wazuh
- **Cloud**: AWS multi-account environment
- **Infrastructure**: EKS cluster, EC2 instances, on-prem VMs
- **CNAPP**: Wiz
- **Automation**: Python, Bash, GitHub Actions CI/CD

This setup simulates a realistic enterprise environment with multiple data sources, cloud-native workloads, and endpoints.

## Step 1: Map Coverage Gaps with MITRE ATT&CK

Before writing any rules, I mapped existing detections against the MITRE ATT&CK framework.

The result: roughly 15% coverage of relevant techniques. Clearly not enough.

I prioritized three areas:

- **Credential Access** (T1003, T1110) — Protecting authentication and secrets
- **Lateral Movement** (T1021, T1570) — Containing breaches early
- **Defense Evasion** (T1562, T1070) — Detecting attackers who try to hide

## Step 2: Understand Your Data Sources

My lab has multiple data sources feeding into Splunk:

- **Endpoint**: CrowdStrike + Wazuh telemetry
- **Network**: VPC Flow Logs, DNS logs
- **Cloud**: AWS CloudTrail, GuardDuty
- **Application**: API gateway logs, custom app logs
- **Identity**: IAM events, SSO authentication logs

Each source has a different schema, different noise patterns, and different false positive potential. Understanding these is critical before writing any detection rule.

## Step 3: Write Sigma Rules

Here are two examples from my collection.

### Example 1: Suspicious Cross-Account IAM Role Assumption

This rule detects unexpected cross-account IAM role assumptions in AWS CloudTrail:

```yaml
title: Suspicious Cross-Account IAM Role Assumption
id: a1b2c3d4-e5f6-7890-abcd-ef1234567890
status: experimental
description: |
  Detects IAM role assumptions from accounts 
  not in the known allowlist
author: Takahiro Oda
logsource:
    product: aws
    service: cloudtrail
detection:
    selection:
        eventName: AssumeRole
        eventSource: sts.amazonaws.com
    filter_known:
        requestParameters.roleArn|contains:
            - 'arn:aws:iam::known-account-1'
            - 'arn:aws:iam::known-account-2'
    condition: selection and not filter_known
falsepositives:
    - Legitimate cross-account access from new accounts
    - CI/CD pipelines using temporary roles
level: medium
tags:
    - attack.credential_access
    - attack.t1078.004
```

### Example 2: EDR Agent Tampering Detection

This rule catches attempts to stop or disable endpoint security agents:

```yaml
title: EDR Agent Service Stopped
id: b2c3d4e5-f6a7-8901-bcde-f12345678901
status: experimental
description: |
  Detects attempts to stop or disable EDR 
  agent services on endpoints
author: Takahiro Oda
logsource:
    category: process_creation
    product: windows
detection:
    selection_cmd:
        CommandLine|contains:
            - 'sc stop'
            - 'net stop'
    selection_target:
        CommandLine|contains:
            - 'CSFalconService'
            - 'WazuhSvc'
            - 'MsMpSvc'
    condition: selection_cmd and selection_target
falsepositives:
    - Legitimate maintenance windows
    - Authorized agent upgrades
level: high
tags:
    - attack.defense_evasion
    - attack.t1562.001
```

## Step 4: Build the CI/CD Pipeline

Every rule goes through an automated pipeline:

1. **Validate** — Sigma syntax check
2. **Backtest** — Run against 30 days of historical logs
3. **Tune** — If false positive rate exceeds 5%, refine filters
4. **Review** — Git commit and review the diff
5. **Deploy** — GitHub Actions converts Sigma to Splunk SPL and deploys via API

Simplified deployment script:

```bash
#!/bin/bash
for rule in sigma-rules/*.yml; do
    sigma convert -t splunk -p sysmon "$rule" \
      > "splunk-queries/$(basename $rule .yml).spl"
    
    if [ $? -eq 0 ]; then
        echo "[OK] $rule"
    else
        echo "[FAIL] $rule"
        exit 1
    fi
done

python3 deploy_to_splunk.py --input-dir splunk-queries/
```

## Results

After building this pipeline:

- 20+ production-ready Sigma rules covering critical ATT&CK techniques
- MITRE ATT&CK coverage improved from ~15% to ~45%
- Mean time to detect dropped from hours to minutes
- Git commit to live detection in under 5 minutes

## Lessons Learned

- **Start with the data, not the rule.** Map your data sources first. Understand what fields exist before writing detections.
- **False positives teach you about your environment.** Document every FP. They become your tuning guide and asset inventory.
- **Invest in the pipeline.** Writing rules is 20% of the work. The CI/CD pipeline is the other 80%, but it pays off exponentially.
- **Home labs are underrated.** You do not need an enterprise environment. A few VMs, a free SIEM tier, and AWS free-tier accounts are enough to build real Detection Engineering skills.

## What is next?

In Series 2, I will cover how I built a SOAR pipeline that automates incident response based on these Sigma rule detections.

---

*Follow me for more practical security engineering content from my home lab.*
