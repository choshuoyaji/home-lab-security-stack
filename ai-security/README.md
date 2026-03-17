# AI Security

LLM red teaming pipeline with NVIDIA Garak, input/output guardrails, and MCP server auditing.

## Overview

This directory contains tools and configurations for testing and hardening AI/LLM applications in a home lab environment. The pipeline maps automated security tests to the OWASP Top 10 for LLM Applications.

## Components

- **NVIDIA Garak**: LLM vulnerability scanner for prompt injection, jailbreak, data leakage testing
- **Guardrails**: Input/output validation layer with prompt injection detection
- **MCP Auditor**: Security scanner for Model Context Protocol server configurations
- **CI/CD Integration**: GitHub Actions workflow for automated LLM security assessments

## Architecture

```
[Red Team Orchestrator] → [Garak Probes] → [Target LLM (Ollama)]
         ↓                                          ↓
  [OWASP Mapping]                           [Guardrails Layer]
         ↓                                          ↓
  [Assessment Report]                        [Input/Output Filter]
```

## Quick Start

```bash
# Install dependencies
pip install garak agentseal
pip install -r requirements.txt

# Run full LLM assessment against local Ollama
python scripts/llm-red-team.py

# Run guardrails unit tests
pytest tests/test_guardrails.py -v

# Audit MCP server configs
agentseal guard
python scripts/mcp-audit.py
```

## Files

- `scripts/` - Red team orchestrator and MCP audit scripts
- `guardrails/` - Input/output security guardrails module
- `configs/` - Garak configuration and GitHub Actions workflow
- `tests/` - Unit tests for guardrails

## OWASP Coverage

| OWASP Category | Test Method | Tool |
|---------------|-------------|------|
| LLM01: Prompt Injection | Encoded payloads, direct injection | Garak |
| LLM01: Jailbreak | DAN, DUDE, roleplay attacks | Garak |
| LLM02: Insecure Output | Malware generation probes | Garak |
| LLM06: Data Leakage | Training data replay | Garak |
| LLM07: Insecure Plugin | MCP server audit | AgentSeal |
| LLM08: Excessive Agency | Permission boundary testing | Custom |

## Related Article

📄 [AI Security in My Home Lab — Series 1](https://takahiro-oda.medium.com/) - Building an LLM Red Teaming Pipeline with NVIDIA Garak and OWASP Top 10
