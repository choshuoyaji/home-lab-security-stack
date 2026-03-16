# Daily Security Audit Report Task

Run a comprehensive security audit covering OpenClaw, Tailscale, and Claude Code. Generate a concise report and send it to the user.

## Steps

1. **OpenClaw Security Audit**
   - Run `openclaw security audit --deep --json`
   - Run `openclaw update status`
   - Check gateway bind: `openclaw config get gateway.bind` (should be `loopback`)
   - Check gateway auth: `openclaw config get gateway.auth` (should have token mode)
   - Check file permissions: `ls -la ~/.openclaw/openclaw.json ~/.openclaw/credentials/ 2>/dev/null`
   - Check for suspicious session activity: `ls -lt ~/.openclaw/agents/*/sessions/*.jsonl 2>/dev/null | head -5`

2. **Tailscale Audit**
   - Run `tailscale status` — check for unexpected devices
   - Run `tailscale version` — note if outdated
   - Run `tailscale debug prefs 2>/dev/null | head -20` or `tailscale status --json | python3 -c "import sys,json; d=json.load(sys.stdin); print('MagicDNS:', d.get('MagicDNSSuffix','?')); print('OS:', d.get('Self',{}).get('OS','?'))"` — check key config

3. **Claude Code Audit**
   - Run `claude --version` — note version
   - Check permissions config: `cat ~/.claude/settings.json 2>/dev/null || echo "no settings file"`
   - Check for allowed tools/permissions that might be too broad

4. **Generate Report**
   Format a concise report with:
   - 🟢 OK / 🟡 Warning / 🔴 Critical for each area
   - Version info for all three tools
   - Any findings or recommendations
   - Date/time of audit

   Save report to `~/.openclaw/workspace/reports/audit-YYYY-MM-DD.md`

5. **Alert if issues found**
   - If any critical or warning findings, notify the user
   - If all clear, still deliver a brief summary

## Important
- Redact tokens, keys, and sensitive values in the report
- Do NOT modify any settings — this is read-only
- Create `reports/` directory if it doesn't exist
