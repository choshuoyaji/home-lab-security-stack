# HEARTBEAT.md

## Security Trend Research (Run FIRST before article writing)
- Run `python3 scripts/security-trend-researcher.py` to get today's trend report
- Read `medium-articles/daily-trend-report.json` for the recommended topic and top repos
- Use the recommended topic as today's article subject (NOT the fixed rotation)
- The researcher scores categories by: global GitHub momentum, new repos in 30 days, and recency penalty (avoids repeating recent topics)

## Daily Medium Article Task
- Check `medium-articles/daily-routine.md` for the publishing schedule and ALL rules
- If today's article hasn't been posted yet and it's within the scheduled posting window, write and publish the next article
- After publishing, check yesterday's article performance (views, claps, followers) on Medium AND dev.to
- Report analytics to Takahiro in Slack #all-ai thread
- **RULES**: No PayPay/Toyota references, all home lab context, English with Japanese-English style, Unsplash images included
- Post at a DIFFERENT time each day (vary between 8:00-22:00 JST)
- **4 hours after Medium post**: Cross-post to dev.to via API (with canonical_url to Medium)
- **Technical review**: Spawn separate agent to verify technical accuracy before publishing
- **Authenticity**: Read past Takahiro posts, write in his voice, include Trial & Error section
- **Daily improvement**: Check analytics, find what works, improve one thing each day
- **GitHub sync**: After publishing, push article's code/configs to https://github.com/choshuoyaji/home-lab-security-stack and update README links
