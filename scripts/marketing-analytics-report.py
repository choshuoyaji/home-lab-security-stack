#!/usr/bin/env python3
"""
Marketing Analytics Report Generator
Fetches analytics from Medium, dev.to, and LinkedIn.
Generates a daily PDF report.

Author: Takahiro Oda
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
REPORTS_DIR = os.path.join(WORKSPACE, "marketing-reports")
ANALYTICS_HISTORY = os.path.join(WORKSPACE, "medium-articles", "analytics-history.json")


def load_config():
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(config_path) as f:
        return json.load(f)


def fetch_devto_stats(api_key):
    """Fetch dev.to article stats via API"""
    print("📊 Fetching dev.to stats...")
    headers = {
        "api-key": api_key,
        "User-Agent": "marketing-analytics",
    }
    
    results = {
        "articles": [],
        "total_views": 0,
        "total_reactions": 0,
        "total_comments": 0,
        "followers": 0,
    }
    
    try:
        # Get published articles
        req = urllib.request.Request(
            "https://dev.to/api/articles/me/published?per_page=20",
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            articles = json.loads(resp.read().decode())
        
        for article in articles:
            art_data = {
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "published_at": article.get("published_at", "")[:10],
                "page_views_count": article.get("page_views_count", 0),
                "positive_reactions_count": article.get("positive_reactions_count", 0),
                "comments_count": article.get("comments_count", 0),
                "reading_time_minutes": article.get("reading_time_minutes", 0),
                "tags": article.get("tag_list", []),
            }
            results["articles"].append(art_data)
            results["total_views"] += art_data["page_views_count"]
            results["total_reactions"] += art_data["positive_reactions_count"]
            results["total_comments"] += art_data["comments_count"]
        
        # Get follower count
        try:
            req = urllib.request.Request(
                "https://dev.to/api/followers/users?per_page=1",
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                # dev.to doesn't have a direct follower count endpoint
                # but we can check the user profile
                pass
        except Exception:
            pass
        
        # Get user profile for follower count
        try:
            req = urllib.request.Request(
                "https://dev.to/api/users/me",
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                user = json.loads(resp.read().decode())
                results["username"] = user.get("username", "")
                results["profile_url"] = f"https://dev.to/{user.get('username', '')}"
        except Exception:
            pass
        
        print(f"  ✅ {len(results['articles'])} articles, {results['total_views']} total views")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return results


def fetch_devto_analytics(api_key):
    """Fetch detailed analytics from dev.to"""
    print("📊 Fetching dev.to analytics (detailed)...")
    headers = {
        "api-key": api_key,
        "User-Agent": "marketing-analytics",
    }
    
    analytics = []
    
    try:
        # Get analytics for each article
        req = urllib.request.Request(
            "https://dev.to/api/articles/me/published?per_page=10",
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            articles = json.loads(resp.read().decode())
        
        for article in articles[:10]:
            article_id = article.get("id")
            try:
                req = urllib.request.Request(
                    f"https://dev.to/api/articles/{article_id}",
                    headers=headers
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    detail = json.loads(resp.read().decode())
                    analytics.append({
                        "id": article_id,
                        "title": detail.get("title", ""),
                        "page_views_count": detail.get("page_views_count", 0),
                        "positive_reactions_count": detail.get("positive_reactions_count", 0),
                        "comments_count": detail.get("comments_count", 0),
                        "published_at": detail.get("published_at", "")[:10],
                    })
            except Exception:
                pass
        
        print(f"  ✅ Got analytics for {len(analytics)} articles")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    return analytics


def load_analytics_history():
    """Load historical analytics data"""
    try:
        with open(ANALYTICS_HISTORY) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_analytics_history(history, today_data):
    """Save today's analytics snapshot"""
    history.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "devto": today_data.get("devto_summary", {}),
        "medium": today_data.get("medium_summary", {}),
        "linkedin": today_data.get("linkedin_summary", {}),
    })
    history = history[-90:]
    with open(ANALYTICS_HISTORY, "w") as f:
        json.dump(history, f, indent=2)


def generate_html_report(devto_stats, devto_analytics, today_str):
    """Generate HTML report that can be converted to PDF"""
    
    # Calculate trends from history
    history = load_analytics_history()
    yesterday = None
    if history:
        yesterday = history[-1]
    
    # Build article rows
    article_rows = ""
    for art in (devto_analytics or devto_stats.get("articles", []))[:10]:
        views = art.get("page_views_count", 0)
        reactions = art.get("positive_reactions_count", 0)
        comments = art.get("comments_count", 0)
        title = art.get("title", "Unknown")[:50]
        published = art.get("published_at", "N/A")
        
        article_rows += f"""
        <tr>
            <td style="padding:8px; border-bottom:1px solid #eee; font-size:13px;">{title}</td>
            <td style="padding:8px; border-bottom:1px solid #eee; text-align:center;">{published}</td>
            <td style="padding:8px; border-bottom:1px solid #eee; text-align:center; font-weight:bold;">{views:,}</td>
            <td style="padding:8px; border-bottom:1px solid #eee; text-align:center;">{reactions}</td>
            <td style="padding:8px; border-bottom:1px solid #eee; text-align:center;">{comments}</td>
        </tr>"""
    
    # Trend indicators
    devto_views_today = devto_stats.get("total_views", 0)
    devto_reactions_today = devto_stats.get("total_reactions", 0)
    
    views_trend = ""
    reactions_trend = ""
    if yesterday and yesterday.get("devto"):
        prev_views = yesterday["devto"].get("total_views", 0)
        prev_reactions = yesterday["devto"].get("total_reactions", 0)
        views_diff = devto_views_today - prev_views
        reactions_diff = devto_reactions_today - prev_reactions
        v_color = "#27ae60" if views_diff >= 0 else "#e74c3c"
        v_arrow = "↑" if views_diff >= 0 else "↓"
        r_color = "#27ae60" if reactions_diff >= 0 else "#e74c3c"
        r_arrow = "↑" if reactions_diff >= 0 else "↓"
        views_trend = f'<span style="color:{v_color}">{v_arrow}{abs(views_diff):,}</span>'
        reactions_trend = f'<span style="color:{r_color}">{r_arrow}{abs(reactions_diff)}</span>'
    
    # Read posting schedule
    schedule_info = ""
    try:
        with open(os.path.join(WORKSPACE, "medium-articles", "posting-schedule-today.json")) as f:
            schedule = json.load(f)
        schedule_info = f"""
        <div style="background:#f0f8ff; padding:15px; border-radius:8px; margin:15px 0;">
            <h3 style="margin:0 0 10px 0; color:#2c3e50;">📅 Today's Posting Schedule</h3>
            <table style="width:100%;">
                <tr><td style="padding:4px;">Medium</td><td style="font-weight:bold;">{schedule.get('medium',{}).get('time_jst','TBD')} JST</td><td style="color:#666;">{schedule.get('medium',{}).get('us_eastern','')}</td></tr>
                <tr><td style="padding:4px;">LinkedIn</td><td style="font-weight:bold;">{schedule.get('linkedin',{}).get('time_jst','TBD')} JST</td><td style="color:#666;">{schedule.get('linkedin',{}).get('us_eastern','')}</td></tr>
                <tr><td style="padding:4px;">dev.to</td><td style="font-weight:bold;">{schedule.get('devto',{}).get('time_jst','TBD')} JST</td><td style="color:#666;">4h after Medium</td></tr>
            </table>
        </div>"""
    except Exception:
        pass
    
    # Read trend report
    trend_info = ""
    try:
        with open(os.path.join(WORKSPACE, "medium-articles", "daily-trend-report.json")) as f:
            trends = json.load(f)
        trend_info = f"""
        <div style="background:#fff8e1; padding:15px; border-radius:8px; margin:15px 0;">
            <h3 style="margin:0 0 10px 0; color:#2c3e50;">🔥 Today's Recommended Topic</h3>
            <p style="font-size:18px; font-weight:bold; color:#e67e22;">{trends.get('recommended_topic','').replace('-',' ').title()}</p>
            <p style="color:#666;">Score: {trends.get('recommended_score','N/A')} | Based on GitHub trending analysis</p>
        </div>"""
    except Exception:
        pass

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 40px; color: #2c3e50; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
        .card {{ background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .metric {{ display: inline-block; text-align: center; padding: 15px 25px; }}
        .metric-value {{ font-size: 28px; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ font-size: 12px; color: #999; text-transform: uppercase; }}
        .metric-trend {{ font-size: 14px; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #f8f9fa; padding: 10px; text-align: left; font-size: 12px; text-transform: uppercase; color: #666; }}
        .section-title {{ font-size: 18px; font-weight: bold; color: #2c3e50; margin: 25px 0 10px 0; }}
        .footer {{ text-align: center; color: #999; font-size: 11px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Daily Marketing Analytics Report</h1>
        <p>{today_str} | Takahiro Oda</p>
    </div>

    {schedule_info}
    {trend_info}

    <div class="section-title">📝 dev.to Performance</div>
    <div class="card">
        <div style="text-align:center;">
            <div class="metric">
                <div class="metric-value">{devto_views_today:,}</div>
                <div class="metric-label">Total Views</div>
                <div class="metric-trend">{views_trend}</div>
            </div>
            <div class="metric">
                <div class="metric-value">{devto_reactions_today}</div>
                <div class="metric-label">Reactions</div>
                <div class="metric-trend">{reactions_trend}</div>
            </div>
            <div class="metric">
                <div class="metric-value">{devto_stats.get('total_comments', 0)}</div>
                <div class="metric-label">Comments</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(devto_stats.get('articles', []))}</div>
                <div class="metric-label">Articles</div>
            </div>
        </div>
    </div>

    <div class="section-title">📰 Article Performance (dev.to)</div>
    <div class="card" style="overflow-x:auto;">
        <table>
            <tr>
                <th>Title</th>
                <th style="text-align:center;">Published</th>
                <th style="text-align:center;">Views</th>
                <th style="text-align:center;">Reactions</th>
                <th style="text-align:center;">Comments</th>
            </tr>
            {article_rows if article_rows else '<tr><td colspan="5" style="padding:20px; text-align:center; color:#999;">No articles published yet</td></tr>'}
        </table>
    </div>

    <div class="section-title">📈 Medium Performance</div>
    <div class="card">
        <p style="color:#666;">Medium analytics require browser access. Stats will be populated when available.</p>
        <p><strong>Profile:</strong> <a href="https://takahiro-oda.medium.com">takahiro-oda.medium.com</a></p>
        <p><em>Tip: Check Medium Partner Program dashboard for detailed read/clap metrics.</em></p>
    </div>

    <div class="section-title">💼 LinkedIn Performance</div>
    <div class="card">
        <p style="color:#666;">LinkedIn analytics require browser access. Stats will be populated when available.</p>
        <p><strong>Followers:</strong> 2,476+</p>
        <p><em>Tip: Check LinkedIn Analytics → Content tab for post impressions and engagement.</em></p>
    </div>

    <div class="section-title">🔗 GitHub Repository</div>
    <div class="card">
        <p><strong>Repo:</strong> <a href="https://github.com/choshuoyaji/home-lab-security-stack">choshuoyaji/home-lab-security-stack</a></p>
        <p><em>Check GitHub Insights → Traffic for clone/visitor stats.</em></p>
    </div>

    <div class="section-title">💡 Recommendations</div>
    <div class="card">
        <ul style="line-height:1.8;">
            <li><strong>Best performing topic:</strong> Analyze which tags get most views and double down</li>
            <li><strong>Cross-platform:</strong> Articles with GitHub code links tend to get more engagement</li>
            <li><strong>Consistency:</strong> Daily posting builds momentum — keep the streak going</li>
            <li><strong>Engagement:</strong> Reply to comments within 2 hours for algorithm boost</li>
        </ul>
    </div>

    <div class="footer">
        <p>Generated automatically by Marketing Analytics Agent | {datetime.now().strftime('%Y-%m-%d %H:%M JST')}</p>
        <p>Medium: takahiro-oda.medium.com | dev.to: dev.to/takahiro_oda | GitHub: github.com/choshuoyaji</p>
    </div>
</body>
</html>"""
    
    return html


def html_to_pdf(html_content, output_path):
    """Convert HTML to PDF using available tools"""
    html_path = output_path.replace(".pdf", ".html")
    
    # Write HTML
    with open(html_path, "w") as f:
        f.write(html_content)
    
    # Try wkhtmltopdf first
    try:
        import subprocess
        result = subprocess.run(
            ["wkhtmltopdf", "--quiet", "--page-size", "A4", "--margin-top", "10", "--margin-bottom", "10", html_path, output_path],
            capture_output=True, timeout=30
        )
        if result.returncode == 0:
            print(f"  ✅ PDF generated with wkhtmltopdf: {output_path}")
            return output_path
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Try weasyprint
    try:
        import weasyprint
        weasyprint.HTML(filename=html_path).write_pdf(output_path)
        print(f"  ✅ PDF generated with weasyprint: {output_path}")
        return output_path
    except ImportError:
        pass
    
    # Try pdfkit
    try:
        import pdfkit
        pdfkit.from_file(html_path, output_path)
        print(f"  ✅ PDF generated with pdfkit: {output_path}")
        return output_path
    except ImportError:
        pass
    
    # Try Chrome/Chromium headless
    try:
        import subprocess
        for browser in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                       "google-chrome", "chromium-browser", "chromium"]:
            try:
                result = subprocess.run(
                    [browser, "--headless", "--disable-gpu", f"--print-to-pdf={output_path}",
                     "--no-margins", html_path],
                    capture_output=True, timeout=30
                )
                if result.returncode == 0 and os.path.exists(output_path):
                    print(f"  ✅ PDF generated with Chrome headless: {output_path}")
                    return output_path
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
    except Exception:
        pass
    
    # Fallback: return HTML
    print(f"  ⚠️ PDF conversion unavailable. HTML report at: {html_path}")
    return html_path


def main():
    config = load_config()
    devto_key = config.get("env", {}).get("DEV_TO_API_KEY", "")
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    print("📊 Marketing Analytics Report Generator")
    print(f"📅 {today_str}")
    print("=" * 50)
    
    # Fetch data
    devto_stats = {}
    devto_analytics = []
    if devto_key:
        devto_stats = fetch_devto_stats(devto_key)
        devto_analytics = fetch_devto_analytics(devto_key)
    else:
        print("  ⚠️ DEV_TO_API_KEY not found")
    
    # Generate HTML
    html = generate_html_report(devto_stats, devto_analytics, today_str)
    
    # Save & convert
    os.makedirs(REPORTS_DIR, exist_ok=True)
    pdf_path = os.path.join(REPORTS_DIR, f"marketing-report-{today_str}.pdf")
    html_path = os.path.join(REPORTS_DIR, f"marketing-report-{today_str}.html")
    
    output = html_to_pdf(html, pdf_path)
    
    # Save analytics history
    today_data = {
        "devto_summary": {
            "total_views": devto_stats.get("total_views", 0),
            "total_reactions": devto_stats.get("total_reactions", 0),
            "total_comments": devto_stats.get("total_comments", 0),
            "article_count": len(devto_stats.get("articles", [])),
        },
        "medium_summary": {},
        "linkedin_summary": {},
    }
    history = load_analytics_history()
    save_analytics_history(history, today_data)
    
    print(f"\n✅ Report generated: {output}")
    print(f"📁 Reports directory: {REPORTS_DIR}")
    
    return output


if __name__ == "__main__":
    main()
