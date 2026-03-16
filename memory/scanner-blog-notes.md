# Scanner.dev Blog Notes (for LinkedIn posting)

## About Scanner
- CEO: Cliff Crosland
- Product: Security Data Lake with fast indexed search
- Key tech: Inverted indexes at ingestion → queries in 1-3 sec vs 30+ min (Athena/Presto)
- MCP server for AI agent integration (Claude Desktop, Claude Code, Cursor)

## Key Articles & Insights

### 1. Building AI SOC Agents Part 1 (Jan 2026)
- **Why now:** Alert volumes > headcount. Manual triage = low value. Agents free analysts for detection engineering.
- **Human-AI partnership:** LLM alone = 71% accuracy (51 false Malicious!). With Socdown framework = 78% + ZERO false Malicious.
- **Key insight:** "Questions, not instructions" — agents should ask "Is this user authorized?" instead of "Disable this account"
- **Trust spectrum:** Read-only (safe) → Staging/drafts (human review) → Response actions (avoid initially)
- **Socdown:** Open source framework on GitHub (scanner-inc/socdown)

### 2. Building AI SOC Agents Part 2 (Feb 2026)  
- **Lambda for triage:** $5/month compute, pay-per-invocation, 15-min hard timeout = trust boundary
- **Threat Hunt Agent:** ECS Fargate, runs every 6h, pulls CISA KEV + ThreatFox + OTX IOCs, hunts across 1 year of logs
- **Key insight:** "The gap between 'it works' and 'it's working'" — laptop demo ≠ production deployment
- **Architecture:** SQS-triggered Lambda (triage) + scheduled Fargate (threat hunt)
- **All code open source:** github.com/scanner-inc/first-soc-agents

### 3. Security Data Lake: Agentic AI in SecOps Part 4 (Dec 2025)
- **AI-assisted detection engineering:** Claude Code + Scanner MCP = write detection rules conversationally
- **Time savings:** 4 hours manual → 15 minutes conversation
- **Use cases:** Migrate rules from Splunk/Datadog, reduce false positives, analyze MITRE ATT&CK coverage gaps
- **Key insight:** AI agents need fast, cheap queries to be effective. Expensive slow queries kill the iterative investigation flow.

### 4. Scanner MCP Announcement (Dec 2025)
- **Problem:** Traditional data lake tools (Athena, Presto) too slow/expensive for AI agents
- **Solution:** Scanner MCP = remote MCP server, 1-3 sec queries, pennies per query
- **3 use cases:** Interactive investigations, AI-assisted detection engineering, autonomous triage
- **Key stat:** "AI agents now handle more Scanner queries than humans" (happened in 8 weeks)

### 5. AI in the SOC Test (Sep 2025)
- **Cross-industry learnings:** Medicine (90-100% diagnosis with GPT-4), Law (review iteration loops), Software (context/state management)
- **Why security is harder:** 16K security papers vs 38M medical papers. IT evolves faster than biology.
- **Key finding:** LLMs + humans > LLMs alone > humans alone
- **Best practice:** Summarize key moments/decisions for future context (from Cognition/Devin)

### 6. Security Data Lake Series (Oct-Nov 2025)
- **Part 1:** Why data lakes > SIEM (cost, scale, control)
- **Part 2:** ETL + search (making data queryable, high perf)
- **Part 3:** Detection engineering approaches: scheduled queries, streaming event-based, streaming query-based

### 7. Cliff's LinkedIn Activity
- Shares about AI SOC agents, security data lakes, MCP
- Liked posts about: CrowdStrike, Monad (decouple SIEM), BSides Seattle, AI threat hunting
- Shared: Notion security team building agents with Scanner
