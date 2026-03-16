# [SOAR in My Home Lab] Series 1 ~Building an Automated Incident Response Pipeline from Scratch~

In this series, you will learn how to build a SOAR (Security Orchestration, Automation, and Response) pipeline in your home lab. Series 1 covers the architecture, playbook design, and how automation can reduce alert fatigue dramatically.

![Security automation dashboard](https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800)
*Photo by [Taylor Vick](https://unsplash.com/@tvick) on [Unsplash](https://unsplash.com)*

---

*Disclaimer: All content in this article is based on experiments conducted in my personal home lab and test environment. This work is not affiliated with, endorsed by, or related to any company I currently work for or have worked for. All opinions are my own.*

---

## What is SOAR?

SOAR stands for Security Orchestration, Automation, and Response. It is a category of tools that help security teams manage and respond to security events more efficiently.

In simple words, SOAR connects your security tools together and automates the repetitive tasks that security analysts do every day. I was so interested to this concept because manual alert handling is simply not scalable.

Three key components:

- **Orchestration** — Connecting different security tools (SIEM, EDR, ticketing) into one workflow
- **Automation** — Running predefined actions without human intervention
- **Response** — Taking action on security events (blocking IPs, isolating hosts, creating tickets)

## Why Build SOAR in a Home Lab?

Most security engineers I know struggle with alert fatigue. When you have hundreds of alerts per day, it is impossible to investigate every single one manually.

In my home lab, I wanted to solve this problem by building automated response workflows. Even with a small environment, the principles are the same as enterprise SOAR deployments.

One thing I could understand after building this: commercial SOAR platforms often create vendor lock-in. Your playbooks live inside the vendor GUI with no version control, no diff, no rollback. By building with open-source tools, you keep full control of your response logic.

## My Home Lab SOAR Stack

Here is my setup:

- **SIEM**: Splunk (receiving alerts from Sigma rules — see my [previous post on Detection Engineering](https://takahiro-oda.medium.com/detection-engineering-in-my-home-lab-series-1-building-20-sigma-rules-for-multi-source-threat-614015b067e8))
- **SOAR Platform**: Shuffle (open-source SOAR) + n8n for workflow orchestration + custom Python scripts
- **EDR**: CrowdStrike Falcon + Wazuh
- **Ticketing**: Jira (free tier)
- **Communication**: Slack webhooks for notifications
- **Cloud**: AWS (CloudTrail, GuardDuty alerts)
- **Playbook Format**: CACAO v2.0 (JSON-based, portable)

![Network server room](https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800)
*Photo by [Thomas Jensen](https://unsplash.com/@thomasjsn) on [Unsplash](https://unsplash.com)*

## Architecture Overview

The flow looks like this:

```
Alert Source (SIEM/EDR/GuardDuty)
        ↓
   Webhook/API trigger
        ↓
   SOAR Playbook Engine (Shuffle + n8n)
        ↓
   ┌─────────────────────┐
   │  Enrichment Phase   │
   │  - IP reputation    │
   │  - Threat intel     │
   │  - Asset lookup     │
   │  - MITRE ATT&CK map │
   └─────────────────────┘
        ↓
   ┌─────────────────────┐
   │  Decision Logic     │
   │  - Severity check   │
   │  - AI-assisted triage│
   │  - False positive?  │
   │  - Auto-resolve?    │
   └─────────────────────┘
        ↓
   ┌─────────────────────┐
   │  Response Actions   │
   │  - Block IP (WAF)   │
   │  - Isolate host     │
   │  - Create ticket    │
   │  - Notify Slack     │
   └─────────────────────┘
```

## Playbooks-as-Code with CACAO v2.0

One of the biggest lesson I learned was about playbook management. When your playbooks live inside a GUI, you lose all the benefits of version control that we already have for detection rules.

CACAO (Collaborative Automated Course of Action Operations) v2.0 is a standard from OASIS that defines playbooks as JSON files. This means:

- **Version control with Git** — Every change goes through PR and review
- **CI/CD pipeline** — Validate playbook syntax, run tests, deploy automatically
- **Portability** — Not locked to any single vendor platform
- **Collaboration** — Multiple analysts can work on same playbook with proper merge workflows

Here is a simplified CACAO playbook structure:

```json
{
  "type": "playbook",
  "spec_version": "cacao-2.0",
  "id": "playbook--suspicious-login-response",
  "name": "Suspicious Login Response",
  "description": "Automated response for suspicious login alerts",
  "playbook_types": ["investigation", "mitigation"],
  "workflow_start": "start--enrich-ip",
  "workflow": {
    "start--enrich-ip": {
      "type": "start",
      "on_completion": "action--check-reputation"
    },
    "action--check-reputation": {
      "type": "action",
      "name": "Check IP Reputation",
      "commands": [{
        "type": "http-api",
        "command": "GET https://api.abuseipdb.com/api/v2/check"
      }],
      "on_completion": "decision--threat-level"
    },
    "decision--threat-level": {
      "type": "if-condition",
      "condition": "threat_score > 70",
      "on_true": "action--block-ip",
      "on_false": "action--create-ticket"
    }
  }
}
```

## Step 1: Design Your Playbooks

Before writing any code, I designed playbooks on paper first. Each playbook answers three questions:

1. **What triggers it?** (Which alert type?)
2. **What information do we need?** (Enrichment)
3. **What action should we take?** (Response)

### Example Playbook: Suspicious Login Alert

```
Trigger: Failed login attempts > 5 from same IP within 10 minutes
Enrichment:
  - Check IP against threat intel (AbuseIPDB, VirusTotal)
  - Check if IP is from known VPN/Tor exit node
  - Look up user account status
  - Map to MITRE ATT&CK technique (T1110 - Brute Force)
Decision:
  - If threat score > 70: Block IP + Alert
  - If threat score 30-70: Create ticket for review
  - If threat score < 30: Log and monitor
Response:
  - Update firewall rules (AWS Security Group / WAF)
  - Create Jira ticket with enriched context
  - Send Slack notification with summary
```

## Step 2: Build the Enrichment Layer

The enrichment layer is the most important part of SOAR. Without good enrichment, your automation will make bad decisions.

Here is my Python enrichment module:

```python
import requests
import json

class ThreatEnrichment:
    def __init__(self, config):
        self.vt_api_key = config.get('virustotal_api_key')
        self.abuseipdb_key = config.get('abuseipdb_api_key')
    
    def check_ip_reputation(self, ip_address):
        """Check IP against multiple threat intel sources"""
        results = {
            'ip': ip_address,
            'threat_score': 0,
            'sources': [],
            'mitre_techniques': []
        }
        
        # AbuseIPDB check
        abuse_score = self._check_abuseipdb(ip_address)
        if abuse_score:
            results['sources'].append({
                'name': 'AbuseIPDB',
                'score': abuse_score
            })
        
        # VirusTotal check
        vt_score = self._check_virustotal(ip_address)
        if vt_score:
            results['sources'].append({
                'name': 'VirusTotal',
                'score': vt_score
            })
        
        # Calculate combined threat score
        scores = [s['score'] for s in results['sources']]
        if scores:
            results['threat_score'] = sum(scores) / len(scores)
        
        return results
    
    def _check_abuseipdb(self, ip):
        """Query AbuseIPDB API"""
        url = 'https://api.abuseipdb.com/api/v2/check'
        headers = {
            'Key': self.abuseipdb_key,
            'Accept': 'application/json'
        }
        params = {'ipAddress': ip, 'maxAgeInDays': 90}
        
        try:
            resp = requests.get(url, headers=headers, params=params)
            data = resp.json()
            return data['data']['abuseConfidenceScore']
        except Exception as e:
            print(f"AbuseIPDB error: {e}")
            return None
    
    def _check_virustotal(self, ip):
        """Query VirusTotal API"""
        url = f'https://www.virustotal.com/api/v3/ip_addresses/{ip}'
        headers = {'x-apikey': self.vt_api_key}
        
        try:
            resp = requests.get(url, headers=headers)
            data = resp.json()
            stats = data['data']['attributes']['last_analysis_stats']
            malicious = stats.get('malicious', 0)
            total = sum(stats.values())
            return int((malicious / total) * 100) if total > 0 else 0
        except Exception as e:
            print(f"VirusTotal error: {e}")
            return None
```

## Step 3: Add AI-Assisted Triage

This is something that it becomes possible to add intelligence layer on top of rule-based decisions. I integrated a lightweight AI triage step using LLM APIs:

```python
import openai

class AITriageAssistant:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
    
    def analyze_alert(self, alert_data, enrichment_data):
        """Use AI to provide additional context and recommendations"""
        prompt = f"""
        Analyze this security alert and provide:
        1. MITRE ATT&CK technique mapping
        2. Severity assessment (1-10)
        3. Recommended response actions
        4. Similar known attack patterns
        
        Alert: {json.dumps(alert_data)}
        Enrichment: {json.dumps(enrichment_data)}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a SOC analyst assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content
```

The AI triage is not replacing human analysts — it is providing additional context to help with decision-making. For high-severity alerts, human review is still mandatory in my pipeline.

## Step 4: Build Response Actions

Response actions are what make SOAR powerful. Here are some I implemented:

### Auto-Block Malicious IP

```python
import boto3

def block_ip_in_waf(ip_address, reason):
    """Add IP to AWS WAF block list"""
    waf_client = boto3.client('wafv2')
    
    ip_set = waf_client.get_ip_set(
        Name='blocked-ips',
        Scope='REGIONAL',
        Id='your-ip-set-id'
    )
    
    addresses = ip_set['IPSet']['Addresses']
    new_entry = f"{ip_address}/32"
    
    if new_entry not in addresses:
        addresses.append(new_entry)
        waf_client.update_ip_set(
            Name='blocked-ips',
            Scope='REGIONAL',
            Id='your-ip-set-id',
            Addresses=addresses,
            LockToken=ip_set['LockToken']
        )
        
    return f"Blocked {ip_address}: {reason}"
```

### Slack Notification with Rich Context

```python
import requests

def send_slack_alert(webhook_url, alert_data):
    """Send formatted alert to Slack"""
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 {alert_data['title']}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Severity:* {alert_data['severity']}"},
                    {"type": "mrkdwn", "text": f"*Source IP:* {alert_data['source_ip']}"},
                    {"type": "mrkdwn", "text": f"*Threat Score:* {alert_data['threat_score']}"},
                    {"type": "mrkdwn", "text": f"*MITRE:* {alert_data.get('mitre', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Action Taken:* {alert_data['action']}"}
                ]
            }
        ]
    }
    
    requests.post(webhook_url, json=payload)
```

## Step 5: Connect Everything with n8n

While Shuffle handles the core SOAR logic, I use n8n to orchestrate the webhook-to-action flow. n8n provides visual workflow building with the flexibility of custom code nodes.

The n8n workflow:

1. **Webhook Node** — Receives alerts from Splunk via HTTP POST
2. **Function Node** — Runs enrichment Python scripts
3. **IF Node** — Routes based on threat score thresholds
4. **HTTP Request Node** — Calls response APIs (WAF, Jira, Slack)

This combination gives you best of both worlds — visual debugging through n8n interface and powerful SOAR capabilities through Shuffle.

## Step 6: CI/CD for Playbooks

Following the detection-as-code approach from my previous article, I also set up CI/CD for playbook management:

```yaml
# .github/workflows/playbook-ci.yml
name: Playbook Validation
on:
  pull_request:
    paths: ['playbooks/**']

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate CACAO JSON
        run: |
          for f in playbooks/*.json; do
            python -m json.tool "$f" > /dev/null
            echo "✅ Valid: $f"
          done
      
      - name: Run playbook tests
        run: python -m pytest tests/playbook_tests/ -v
      
      - name: Check for hardcoded credentials
        run: |
          if grep -rn "api_key\|password\|secret" playbooks/; then
            echo "❌ Found hardcoded credentials!"
            exit 1
          fi
```

## Results

After building this SOAR pipeline in my home lab:

- **Alert triage time** reduced from average 15 minutes to under 2 minutes for automated cases
- **False positive handling** became automatic for known-good patterns
- **Response time** for high-severity alerts went from manual investigation to instant automated action
- **All response actions** are logged for audit trail and post-incident review
- **Playbook versioning** through Git gave full change history and rollback capability

## Lessons Learned

- **Start small.** Do not try to automate everything at once. Pick the highest-volume alert type first.
- **Enrichment is everything.** The quality of your automated decisions depend of the quality of your threat intelligence data.
- **Always have a manual override.** Automation should assist, not replace human judgment for critical decisions.
- **Use playbooks-as-code.** Managing playbooks in a GUI is not sustainable. CACAO v2.0 + Git gives you proper version control.
- **Test your playbooks regularly.** Automated responses can cause damage if they have bugs. Test with simulated alerts first.
- **Document every playbook.** Future you will thank present you when something goes wrong at 3 AM.

## What is Next?

In Series 2, I will cover advanced SOAR topics including multi-cloud response automation and building custom integrations for these kind of tools that do not have native SOAR connectors.

---

![Security monitoring](https://images.unsplash.com/photo-1563986768609-322da13575f2?w=800)
*Photo by [Markus Spiske](https://unsplash.com/@markusspiske) on [Unsplash](https://unsplash.com)*

## References

- [OASIS CACAO v2.0 Specification](https://docs.oasis-open.org/cacao/security-playbooks/v2.0/security-playbooks-v2.0.html) — Standard for security playbook definition
- [Shuffle SOAR](https://shuffler.io/) — Open-source SOAR platform
- [n8n Workflow Automation](https://n8n.io/) — Open-source workflow orchestration
- [MITRE ATT&CK Framework](https://attack.mitre.org/) — Adversary techniques mapping
- [AbuseIPDB](https://www.abuseipdb.com/) — IP reputation database
- [VirusTotal API](https://developers.virustotal.com/) — Threat intelligence API
- [Sigma HQ](https://github.com/SigmaHQ/sigma) — Detection rules standard
- [NIST Cybersecurity Framework](https://www.nist.gov/cybersecurity) — Security framework guidance
- [CISA Resources](https://www.cisa.gov/) — Cybersecurity advisories and best practices
- [Wazuh Documentation](https://documentation.wazuh.com/) — Open-source security monitoring

---

*Follow me for more practical security engineering content from my home lab. Previous: [Detection Engineering Series 1](https://takahiro-oda.medium.com/detection-engineering-in-my-home-lab-series-1-building-20-sigma-rules-for-multi-source-threat-614015b067e8)*

**Tags:** SOAR, Security Automation, Incident Response, Home Lab, Cybersecurity, Python, DevSecOps
