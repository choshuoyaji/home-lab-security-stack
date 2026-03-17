#!/usr/bin/env python3
"""
MCP Server Security Auditor
Scans AI agent MCP configurations for dangerous permissions and toxic data flows.

Author: Takahiro Oda
"""

import json
from pathlib import Path


def audit_mcp_configs():
    """Scan for dangerous MCP server configurations"""

    config_paths = [
        Path.home() / ".config" / "claude" / "claude_desktop_config.json",
        Path.home() / ".cursor" / "mcp.json",
        Path.home() / ".vscode" / "mcp.json",
        Path.home() / ".windsurf" / "mcp.json",
        Path.home() / ".zed" / "mcp.json",
    ]

    findings = []

    for config_path in config_paths:
        if not config_path.exists():
            continue

        try:
            with open(config_path) as f:
                config = json.load(f)
        except (json.JSONDecodeError, PermissionError) as e:
            findings.append({
                "server": str(config_path),
                "risk": "LOW",
                "issue": f"Cannot parse config: {e}",
                "config_path": str(config_path),
            })
            continue

        servers = config.get("mcpServers", {})

        for name, server_config in servers.items():
            args = server_config.get("args", [])

            if any("filesystem" in str(a).lower() for a in args):
                findings.append({
                    "server": name,
                    "risk": "HIGH",
                    "issue": "Filesystem access — can read sensitive files",
                    "config_path": str(config_path),
                })

            for arg in args:
                if isinstance(arg, str) and arg in ["/", "~", "$HOME"]:
                    findings.append({
                        "server": name,
                        "risk": "CRITICAL",
                        "issue": f"Unrestricted path access: {arg}",
                        "config_path": str(config_path),
                    })

            env = server_config.get("env", {})
            if any("API_KEY" in k or "TOKEN" in k for k in env):
                findings.append({
                    "server": name,
                    "risk": "MEDIUM",
                    "issue": "Has API credentials — potential exfiltration vector",
                    "config_path": str(config_path),
                })

    return findings


def main():
    print("🔍 MCP Server Security Audit")
    print("=" * 50)

    findings = audit_mcp_configs()

    if not findings:
        print("✅ No MCP configurations found or no issues detected")
        return

    for f in findings:
        icon = (
            "❌" if f["risk"] == "CRITICAL"
            else "⚠️" if f["risk"] == "HIGH"
            else "ℹ️"
        )
        print(f"{icon} [{f['risk']}] {f['server']}: {f['issue']}")
        print(f"   Config: {f['config_path']}")

    critical = sum(1 for f in findings if f["risk"] == "CRITICAL")
    high = sum(1 for f in findings if f["risk"] == "HIGH")
    print(f"\nSummary: {critical} critical, {high} high, {len(findings)} total")


if __name__ == "__main__":
    main()
