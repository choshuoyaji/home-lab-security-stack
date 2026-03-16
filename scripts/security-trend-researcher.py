#!/usr/bin/env python3
"""
Security Trend Researcher
Analyzes global security trends on GitHub to determine daily article topics.
Runs daily before article writing to maximize relevance and demand.

Author: Takahiro Oda
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
OUTPUT_FILE = os.path.join(WORKSPACE, "medium-articles", "daily-trend-report.json")
HISTORY_FILE = os.path.join(WORKSPACE, "medium-articles", "trend-history.json")

# Our focus categories mapped to GitHub search queries
CATEGORIES = {
    "detection-engineering": {
        "queries": [
            "sigma rules detection",
            "detection-as-code",
            "threat detection SIEM",
            "yara rules malware",
            "sigma backend converter",
        ],
        "topics": ["sigma", "detection-engineering", "threat-hunting", "yara"],
        "keywords": ["sigma", "detection", "threat-hunting", "sysmon", "splunk-queries"],
    },
    "soar": {
        "queries": [
            "SOAR security orchestration automation",
            "security playbook automation",
            "incident response automation",
        ],
        "topics": ["soar", "security-automation", "security-orchestration"],
        "keywords": ["soar", "playbook", "orchestration", "shuffle", "phantom"],
    },
    "security-monitoring": {
        "queries": [
            "SIEM open source monitoring",
            "wazuh security monitoring",
            "security dashboard grafana",
            "log analysis security",
        ],
        "topics": ["siem", "wazuh", "security-monitoring", "opensearch"],
        "keywords": ["siem", "wazuh", "monitoring", "opensearch", "elk"],
    },
    "edr-xdr": {
        "queries": [
            "EDR endpoint detection response",
            "XDR extended detection",
            "endpoint security open source",
        ],
        "topics": ["edr", "xdr", "endpoint-security"],
        "keywords": ["edr", "xdr", "endpoint", "crowdstrike", "velociraptor"],
    },
    "cloud-security": {
        "queries": [
            "cloud security AWS terraform",
            "cloud security posture management",
            "kubernetes security",
            "IAM security audit",
        ],
        "topics": ["cloud-security", "aws-security", "kubernetes-security", "cspm"],
        "keywords": ["cloud-security", "terraform", "iam", "cspm", "cnapp"],
    },
    "product-security": {
        "queries": [
            "application security vulnerability",
            "SAST DAST security testing",
            "supply chain security SBOM",
            "container security scanning",
        ],
        "topics": ["application-security", "devsecops", "vulnerability-scanning"],
        "keywords": ["appsec", "sast", "dast", "sbom", "devsecops"],
    },
    "ai-security": {
        "queries": [
            "LLM security prompt injection",
            "AI security machine learning",
            "AI red team adversarial",
            "GenAI security guardrails",
        ],
        "topics": ["ai-security", "llm-security", "prompt-injection", "ai-safety"],
        "keywords": ["llm-security", "prompt-injection", "ai-safety", "guardrails"],
    },
    "incident-response": {
        "queries": [
            "incident response DFIR forensics",
            "threat intelligence feeds",
            "malware analysis sandbox",
            "cyber threat intelligence",
        ],
        "topics": ["incident-response", "dfir", "forensics", "threat-intelligence"],
        "keywords": ["dfir", "forensics", "incident-response", "threat-intel", "ioc"],
    },
}


def github_api(url, retries=3):
    """Make authenticated GitHub API request with retry"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "security-trend-researcher",
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 403:  # Rate limited
                reset = int(e.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(reset - int(time.time()), 5)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  API error: {e.code} for {url}")
                return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  Error: {e}")
                return None
    return None


def search_trending_repos(query, sort="stars", created_after=None, per_page=5):
    """Search GitHub repos with filters"""
    q = urllib.request.quote(query)
    if created_after:
        q += urllib.request.quote(f" created:>{created_after}")
    url = f"https://api.github.com/search/repositories?q={q}&sort={sort}&order=desc&per_page={per_page}"
    data = github_api(url)
    if not data:
        return []
    return data.get("items", [])


def get_topic_repos(topic, per_page=5):
    """Get top repos for a GitHub topic"""
    url = f"https://api.github.com/search/repositories?q=topic:{topic}&sort=stars&order=desc&per_page={per_page}"
    data = github_api(url)
    if not data:
        return []
    return data.get("items", [])


def analyze_category(category_name, config):
    """Analyze trending repos for a category"""
    print(f"\n📊 Analyzing: {category_name}")
    
    results = {
        "category": category_name,
        "trending_repos": [],
        "new_repos_30d": [],
        "most_active": [],
        "total_stars": 0,
        "avg_stars": 0,
        "momentum_score": 0,
    }
    
    seen_repos = set()
    all_repos = []
    
    # Search by queries (recently created = trending)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    for query in config["queries"][:3]:  # Limit queries to save API calls
        # All-time popular
        repos = search_trending_repos(query, sort="stars", per_page=3)
        for r in repos:
            if r["full_name"] not in seen_repos:
                seen_repos.add(r["full_name"])
                all_repos.append(r)
        
        # New in last 30 days
        new_repos = search_trending_repos(query, sort="stars", created_after=thirty_days_ago, per_page=3)
        for r in new_repos:
            if r["full_name"] not in seen_repos:
                seen_repos.add(r["full_name"])
                results["new_repos_30d"].append({
                    "name": r["full_name"],
                    "stars": r["stargazers_count"],
                    "description": (r.get("description") or "")[:120],
                    "url": r["html_url"],
                    "created": r["created_at"][:10],
                    "language": r.get("language"),
                })
        
        time.sleep(2.5)  # Stay within search rate limit (30/min)
    
    # Search by topics
    for topic in config["topics"][:2]:
        repos = get_topic_repos(topic, per_page=3)
        for r in repos:
            if r["full_name"] not in seen_repos:
                seen_repos.add(r["full_name"])
                all_repos.append(r)
        time.sleep(2.5)
    
    # Process top repos
    all_repos.sort(key=lambda r: r["stargazers_count"], reverse=True)
    for r in all_repos[:10]:
        results["trending_repos"].append({
            "name": r["full_name"],
            "stars": r["stargazers_count"],
            "forks": r["forks_count"],
            "description": (r.get("description") or "")[:120],
            "url": r["html_url"],
            "language": r.get("language"),
            "updated": r["updated_at"][:10],
            "topics": r.get("topics", [])[:5],
        })
    
    # Calculate momentum score
    if all_repos:
        results["total_stars"] = sum(r["stargazers_count"] for r in all_repos[:10])
        results["avg_stars"] = results["total_stars"] // max(len(all_repos[:10]), 1)
        new_count = len(results["new_repos_30d"])
        new_stars = sum(r["stars"] for r in results["new_repos_30d"])
        results["momentum_score"] = (new_count * 10) + (new_stars // 100) + (results["avg_stars"] // 1000)
    
    return results


def determine_todays_topic(category_results, history):
    """Determine the best topic for today based on trends and history"""
    
    # Get recently covered topics
    recent_topics = []
    if history:
        for entry in history[-7:]:  # Last 7 days
            recent_topics.append(entry.get("category", ""))
    
    # Score each category
    scored = []
    for result in category_results:
        cat = result["category"]
        score = result["momentum_score"]
        
        # Penalize recently covered topics
        days_since = None
        for i, t in enumerate(reversed(recent_topics)):
            if t == cat:
                days_since = i + 1
                break
        
        if days_since is None:
            score *= 2.0  # Never covered = bonus
        elif days_since <= 1:
            score *= 0.1  # Yesterday = strong penalty
        elif days_since <= 3:
            score *= 0.5  # Last 3 days = moderate penalty
        else:
            score *= 1.0  # 4+ days ago = no penalty
        
        # Bonus for new repos (hot topics)
        new_repo_bonus = len(result["new_repos_30d"]) * 5
        score += new_repo_bonus
        
        scored.append({
            "category": cat,
            "final_score": round(score, 1),
            "momentum": result["momentum_score"],
            "new_repos": len(result["new_repos_30d"]),
            "days_since_covered": days_since,
        })
    
    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored


def generate_article_suggestions(winner, category_result):
    """Generate specific article suggestions based on trending repos"""
    suggestions = []
    
    # Based on trending repos
    for repo in category_result["trending_repos"][:3]:
        suggestions.append({
            "type": "trending_repo_deep_dive",
            "title_idea": f"Deep Dive: {repo['name']} — How to Use It in Your Home Lab",
            "repo": repo["name"],
            "stars": repo["stars"],
            "reason": f"Top repo with {repo['stars']}⭐, high demand",
        })
    
    # Based on new repos
    for repo in category_result["new_repos_30d"][:2]:
        suggestions.append({
            "type": "new_tool_review",
            "title_idea": f"New Tool Alert: {repo['name']} — First Impressions from My Home Lab",
            "repo": repo["name"],
            "stars": repo["stars"],
            "reason": f"New repo (created {repo['created']}), gaining traction",
        })
    
    return suggestions


def load_history():
    """Load trend research history"""
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_history(history, today_result):
    """Save today's result to history"""
    history.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": today_result["recommended_topic"],
        "momentum_scores": {r["category"]: r["momentum"] for r in today_result["rankings"]},
    })
    # Keep last 90 days
    history = history[-90:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def main():
    global GITHUB_TOKEN
    if not GITHUB_TOKEN:
        # Try to load from config
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        try:
            with open(config_path) as f:
                config = json.load(f)
            token = config.get("env", {}).get("GITHUB_TOKEN", "")
            if token:
                GITHUB_TOKEN = token
        except Exception:
            pass
    
    if not GITHUB_TOKEN:
        print("ERROR: GITHUB_TOKEN not set")
        sys.exit(1)
    
    print("🔍 Security Trend Researcher")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Load history
    history = load_history()
    
    # Analyze all categories
    category_results = []
    for name, config in CATEGORIES.items():
        result = analyze_category(name, config)
        category_results.append(result)
        print(f"  ⭐ Total stars: {result['total_stars']:,} | Momentum: {result['momentum_score']}")
        print(f"  🆕 New repos (30d): {len(result['new_repos_30d'])}")
    
    # Determine today's topic
    rankings = determine_todays_topic(category_results, history)
    winner = rankings[0]
    winner_data = next(r for r in category_results if r["category"] == winner["category"])
    
    # Generate suggestions
    suggestions = generate_article_suggestions(winner, winner_data)
    
    # Build report
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "recommended_topic": winner["category"],
        "recommended_score": winner["final_score"],
        "rankings": rankings,
        "suggestions": suggestions,
        "top_trending_repos": winner_data["trending_repos"][:5],
        "new_repos_30d": winner_data["new_repos_30d"],
        "all_categories": {r["category"]: {
            "momentum": r["momentum_score"],
            "total_stars": r["total_stars"],
            "new_repos": len(r["new_repos_30d"]),
            "top_repo": r["trending_repos"][0]["name"] if r["trending_repos"] else "N/A",
        } for r in category_results},
    }
    
    # Save report
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    # Save to history
    save_history(history, report)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"🏆 TODAY'S RECOMMENDED TOPIC: {winner['category'].upper()}")
    print(f"   Score: {winner['final_score']} (momentum: {winner['momentum']})")
    print(f"\n📊 Full Rankings:")
    for i, r in enumerate(rankings):
        marker = "👑" if i == 0 else f" {i+1}."
        days = f"(last covered {r['days_since_covered']}d ago)" if r['days_since_covered'] else "(never covered)"
        print(f"   {marker} {r['category']}: score={r['final_score']} {days}")
    
    if suggestions:
        print(f"\n💡 Article Suggestions:")
        for s in suggestions[:3]:
            print(f"   • {s['title_idea']}")
            print(f"     Reason: {s['reason']}")
    
    print(f"\n📁 Report saved to: {OUTPUT_FILE}")
    return report


if __name__ == "__main__":
    main()
