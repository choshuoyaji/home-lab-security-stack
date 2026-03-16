#!/usr/bin/env python3
"""
Posting Time Optimizer / Marketing Agent
Determines optimal posting times for Medium, dev.to, and LinkedIn
based on global engagement research and Takahiro's constraints.

Author: Takahiro Oda
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
OUTPUT_FILE = os.path.join(WORKSPACE, "medium-articles", "posting-schedule-today.json")
HISTORY_FILE = os.path.join(WORKSPACE, "medium-articles", "posting-time-history.json")

# =============================================================================
# RESEARCH-BASED OPTIMAL POSTING TIMES (LinkedIn/Medium/dev.to)
# =============================================================================
# Sources: HubSpot, Hootsuite, Buffer, Sprout Social, CoSchedule research
#
# LinkedIn optimal times (UTC):
#   - Best days: Tue, Wed, Thu
#   - Best times: 7-8 AM, 12 PM, 5-6 PM (reader's local time)
#   - Peak engagement: Tuesday 10-11 AM EST = 00:00-01:00 JST (next day)
#   - Secondary peak: Wednesday 12 PM EST = 02:00 JST (next day)
#   - For global audience: 14:00-17:00 UTC (good for US morning + EU afternoon)
#
# Medium optimal times:
#   - Best: Tuesday-Thursday, 7-11 AM EST
#   - Also good: Saturday morning
#   - JST equivalent: 21:00-01:00 JST
#
# dev.to optimal times:
#   - Developer audience: US morning hours
#   - Best: Mon-Thu, 7-9 AM EST = 21:00-23:00 JST
#
# KEY INSIGHT: Takahiro's target audience is GLOBAL (English articles)
# Primary readers: US, EU, India, Southeast Asia
# So posting when US/EU are awake is critical.
# =============================================================================

# Takahiro's constraints
WORK_HOURS_START = 8   # JST - can't post during work
WORK_HOURS_END = 18    # JST - can't post during work
TOO_EARLY = 5          # JST - suspicious if posting before this
TOO_LATE = 24          # JST - don't post after midnight

# Allowed posting windows (JST) - outside work hours, not suspicious
# Window 1: Evening after work (18:00-23:30 JST) — BEST for global reach
#   18:00 JST = 09:00 UTC = US East Coast morning ✨
#   20:00 JST = 11:00 UTC = US East Coast late morning ✨
#   22:00 JST = 13:00 UTC = US East Coast early afternoon
# Window 2: Early morning before work (6:00-7:45 JST) — OK for EU audience
#   6:00 JST = 21:00 UTC (prev day) = EU late evening
#   7:00 JST = 22:00 UTC (prev day) = US West Coast afternoon ✨

POSTING_WINDOWS = {
    "medium": {
        "primary": {  # Best window - evening (catches US morning)
            "start": 18,  # 18:00 JST
            "end": 23,    # 23:00 JST
            "weight": 0.7,
            "reason": "US East Coast morning peak, EU afternoon"
        },
        "secondary": {  # Before work (catches EU morning)
            "start": 6,
            "end": 7,     # 7:45 JST max (leave buffer before work)
            "weight": 0.2,
            "reason": "EU morning readers, India afternoon"
        },
        "weekend": {  # Weekend flexibility
            "start": 8,
            "end": 22,
            "weight": 0.1,
            "reason": "Weekend casual reading times"
        }
    },
    "devto": {
        # Always 4 hours after Medium (per existing rules)
        "offset_hours": 4,
        "reason": "Cross-post 4h after Medium with canonical_url"
    },
    "linkedin": {
        "primary": {  # After work, catches US morning
            "start": 18,
            "end": 21,
            "weight": 0.5,
            "reason": "LinkedIn peak: US morning, EU afternoon engagement"
        },
        "secondary": {  # Late evening, catches US business hours
            "start": 21,
            "end": 23,
            "weight": 0.3,
            "reason": "US business hours, good for professional content"
        },
        "early": {  # Before work
            "start": 6,
            "end": 7,
            "weight": 0.2,
            "reason": "Early professional readers in Asia/EU"
        }
    }
}

# Day of week multipliers (0=Mon, 6=Sun)
DAY_MULTIPLIERS = {
    "linkedin": {0: 0.8, 1: 1.2, 2: 1.3, 3: 1.1, 4: 0.7, 5: 0.4, 6: 0.3},
    "medium":   {0: 0.9, 1: 1.1, 2: 1.2, 3: 1.0, 4: 0.8, 5: 1.0, 6: 0.7},
}


def load_history():
    """Load posting time history to avoid patterns"""
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_history(history, today_schedule):
    """Save today's schedule to history"""
    history.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "medium_time": today_schedule["medium"]["time_jst"],
        "linkedin_time": today_schedule["linkedin"]["time_jst"],
        "devto_time": today_schedule["devto"]["time_jst"],
    })
    # Keep last 90 days
    history = history[-90:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def pick_random_time(window, recent_times=None):
    """Pick a random time within a window, avoiding recent patterns"""
    start_h = window["start"]
    end_h = window["end"]
    
    # Generate random hour and minute
    hour = random.randint(start_h, end_h - 1)
    minute = random.randint(0, 59)
    
    # Avoid exact same time as recent posts
    if recent_times:
        for _ in range(10):  # Try up to 10 times
            time_str = f"{hour:02d}:{minute:02d}"
            too_close = False
            for recent in recent_times[-3:]:  # Check last 3 posts
                if abs(int(recent.split(":")[0]) - hour) == 0 and abs(int(recent.split(":")[1]) - minute) < 15:
                    too_close = True
                    break
            if not too_close:
                break
            minute = random.randint(0, 59)
            hour = random.randint(start_h, end_h - 1)
    
    return f"{hour:02d}:{minute:02d}"


def select_window(windows, day_of_week, is_weekend):
    """Select which posting window to use based on weights"""
    if is_weekend and "weekend" in windows:
        candidates = ["primary", "weekend"]
        weights = [0.6, 0.4]
    else:
        candidates = [k for k in windows if k not in ("offset_hours", "reason", "weekend") and isinstance(windows[k], dict)]
        weights = [windows[k].get("weight", 0.5) for k in candidates]
    
    # Normalize weights
    total = sum(weights)
    weights = [w / total for w in weights]
    
    chosen = random.choices(candidates, weights=weights, k=1)[0]
    return windows[chosen]


def generate_todays_schedule():
    """Generate today's optimized posting schedule"""
    now = datetime.now()
    day_of_week = now.weekday()
    is_weekend = day_of_week >= 5
    day_name = now.strftime("%A")
    
    history = load_history()
    recent_medium_times = [h["medium_time"] for h in history[-7:]]
    recent_linkedin_times = [h["linkedin_time"] for h in history[-7:]]
    
    # Medium time
    medium_windows = POSTING_WINDOWS["medium"]
    medium_window = select_window(medium_windows, day_of_week, is_weekend)
    medium_time = pick_random_time(medium_window, recent_medium_times)
    
    # dev.to time (4 hours after Medium)
    medium_hour = int(medium_time.split(":")[0])
    medium_min = int(medium_time.split(":")[1])
    devto_hour = (medium_hour + 4) % 24
    devto_time = f"{devto_hour:02d}:{medium_min:02d}"
    
    # LinkedIn time (independent, optimized for engagement)
    linkedin_windows = POSTING_WINDOWS["linkedin"]
    linkedin_window = select_window(linkedin_windows, day_of_week, is_weekend)
    linkedin_time = pick_random_time(linkedin_window, recent_linkedin_times)
    
    # Ensure LinkedIn is at least 30 min different from Medium
    linkedin_hour = int(linkedin_time.split(":")[0])
    if abs(linkedin_hour - medium_hour) < 1:
        linkedin_hour = (linkedin_hour + 2) % 24
        if WORK_HOURS_START <= linkedin_hour < WORK_HOURS_END:
            linkedin_hour = 19  # fallback to safe time
        linkedin_time = f"{linkedin_hour:02d}:{random.randint(0, 59):02d}"
    
    # Day quality score
    linkedin_day_score = DAY_MULTIPLIERS["linkedin"].get(day_of_week, 1.0)
    medium_day_score = DAY_MULTIPLIERS["medium"].get(day_of_week, 1.0)
    
    schedule = {
        "date": now.strftime("%Y-%m-%d"),
        "day": day_name,
        "is_weekend": is_weekend,
        "medium": {
            "time_jst": medium_time,
            "window_reason": medium_window.get("reason", ""),
            "day_score": medium_day_score,
            "utc_equivalent": f"{(int(medium_time.split(':')[0]) - 9) % 24:02d}:{medium_time.split(':')[1]} UTC",
            "us_eastern": f"{(int(medium_time.split(':')[0]) - 14) % 24:02d}:{medium_time.split(':')[1]} EST",
        },
        "devto": {
            "time_jst": devto_time,
            "note": "4 hours after Medium (canonical_url cross-post)",
        },
        "linkedin": {
            "time_jst": linkedin_time,
            "window_reason": linkedin_window.get("reason", ""),
            "day_score": linkedin_day_score,
            "utc_equivalent": f"{(int(linkedin_time.split(':')[0]) - 9) % 24:02d}:{linkedin_time.split(':')[1]} UTC",
            "us_eastern": f"{(int(linkedin_time.split(':')[0]) - 14) % 24:02d}:{linkedin_time.split(':')[1]} EST",
        },
        "recommendations": [],
    }
    
    # Add recommendations
    if linkedin_day_score >= 1.1:
        schedule["recommendations"].append(f"📈 {day_name} is a GREAT day for LinkedIn ({linkedin_day_score}x engagement)")
    elif linkedin_day_score <= 0.5:
        schedule["recommendations"].append(f"⚠️ {day_name} has lower LinkedIn engagement ({linkedin_day_score}x) — consider a lighter post")
    
    if is_weekend:
        schedule["recommendations"].append("🏖️ Weekend: casual/personal content tends to perform better")
    
    # Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(schedule, f, indent=2)
    
    save_history(history, schedule)
    
    return schedule


def main():
    print("📅 Posting Time Optimizer")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M JST')}")
    print("=" * 50)
    
    schedule = generate_todays_schedule()
    
    print(f"\n📝 Today: {schedule['day']} ({schedule['date']})")
    print(f"\n🕐 Medium:   {schedule['medium']['time_jst']} JST ({schedule['medium']['us_eastern']})")
    print(f"   Reason:   {schedule['medium']['window_reason']}")
    print(f"   Day score: {schedule['medium']['day_score']}x")
    
    print(f"\n🕐 dev.to:   {schedule['devto']['time_jst']} JST")
    print(f"   Note:     {schedule['devto']['note']}")
    
    print(f"\n🕐 LinkedIn: {schedule['linkedin']['time_jst']} JST ({schedule['linkedin']['us_eastern']})")
    print(f"   Reason:   {schedule['linkedin']['window_reason']}")
    print(f"   Day score: {schedule['linkedin']['day_score']}x")
    
    if schedule["recommendations"]:
        print(f"\n💡 Tips:")
        for r in schedule["recommendations"]:
            print(f"   {r}")
    
    print(f"\n📁 Schedule saved to: {OUTPUT_FILE}")
    return schedule


if __name__ == "__main__":
    main()
