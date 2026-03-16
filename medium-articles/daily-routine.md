# Medium Daily Publishing Routine

## Rules
- Post 1 article per day from the category rotation
- **NEVER include PayPay, Toyota, or any company-specific numbers/metrics**
- All content framed as "home lab" or "personal test environment" projects
- **MANDATORY DISCLAIMER**: Every article MUST include this disclaimer near the top (after intro):
  > *Disclaimer: All content in this article is based on experiments conducted in my personal home lab and test environment. This work is not affiliated with, endorsed by, or related to any company I currently work for or have worked for. All opinions are my own.*
- Written in English with INTENTIONAL subtle Japanese-English mistakes (see style guide below)
- Post at a DIFFERENT random time each day
- Analyze previous article performance and adjust strategy

## Categories (rotate)
1. Detection Engineering
2. SOAR
3. Security Monitoring Platform
4. EDR/XDR
5. Cloud Security
6. Product Security
7. AI Security

## Series Format
`[Category in My Home Lab] Series N ~Subtitle~`

## Writing Style (matching Takahiro's existing posts)
- Educational/tutorial tone: "In this series, you will learn..."
- Structured with clear H2 headers
- Bullet point features/lists
- Include images (Unsplash)
- Include code examples where relevant
- 4-6 min read length

### Japanese-English Style Guide (30s Male Japanese Engineer)
The author is a 30-year-old Japanese male engineer. English is his second language.
He is competent but makes SUBTLE, NON-CRITICAL mistakes that Japanese speakers typically make.
Sprinkle 3-5 of these per article — NOT in every sentence, just enough to feel natural.

**Types of mistakes to include (pick randomly):**
- Missing articles: "I built detection pipeline" instead of "I built a detection pipeline"
- Wrong article: "the each rule" instead of "each rule"
- Plural confusion: "many informations" / "these kind of" / "several datas"
- Preposition errors: "I'm interested to" instead of "interested in" / "depend of" instead of "depend on"
- Tense inconsistency: switching between past and present in narrative ("I built the pipeline and then I test it")
- Overuse of "very" or "so": "it was so useful" / "very easy to understand"
- Direct translation patterns: "I could understand" instead of "I understood" / "It becomes possible to" instead of "You can"
- Slightly stiff/formal tone in casual context: "I would like to introduce" instead of "Here's"
- Occasional word order: "I in my home lab tested this" 
- "the" before proper nouns: "the Python", "the AWS"

**DO NOT:**
- Make spelling errors (Japanese engineers are careful with spelling)
- Make errors in code/YAML/technical syntax (technical accuracy is critical)
- Make errors that change meaning of security concepts
- Overdo it — keep it subtle and natural, like a real non-native speaker

## Publishing Schedule Tracker
| Date | Category | Title | Time Posted | Views | Claps | Link |
|------|----------|-------|-------------|-------|-------|------|
| 2026-03-15 | Detection Engineering | Series 1 ~Sigma Rules~ | 20:40 JST | TBD | TBD | https://takahiro-oda.medium.com/detection-engineering-in-my-home-lab-series-1-building-20-sigma-rules-for-multi-source-threat-614015b067e8 |
| 2026-03-16 | SOAR | Series 1 ~SOAR Pipeline~ | TBD | - | - | - |
| 2026-03-17 | Security Monitoring | Series 1 ~Multi-Source Platform~ | TBD | - | - | - |
| 2026-03-18 | EDR/XDR | Series 1 ~EDR Optimization~ | TBD | - | - | - |
| 2026-03-19 | Cloud Security | Series 1 ~IAM Migration~ | TBD | - | - | - |
| 2026-03-20 | Product Security | Series 1 ~Vulnerability Response~ | TBD | - | - | - |
| 2026-03-21 | AI Security | Series 1 ~LLM Security~ | TBD | - | - | - |

## GitHub Repository Integration
- **Repo**: https://github.com/choshuoyaji/home-lab-security-stack
- Every article MUST have corresponding code/config pushed to the GitHub repo
- Article must link to the GitHub repo (and specific files/directories)
- GitHub README must link back to the article
- Update the repo's article table in README.md after each publish
- Each article's code goes in the matching directory (e.g., detection-engineering/ for Detection Engineering articles)
- This creates a virtuous cycle: Medium → GitHub → more stars → more Medium reads

## Cross-Posting to dev.to
- **Timing**: Post to dev.to exactly 4 hours AFTER Medium publication
- **API Key**: Stored in env.DEV_TO_API_KEY
- **canonical_url**: Always set to the Medium article URL (SEO dedup)
- **Tags**: Map to dev.to tag format (max 4 tags, lowercase)
- **Series**: Use same series name as Medium

## Post-Publish Checklist
1. ✅ Research: Fetch top 3-5 popular Medium articles in the same topic tag
2. ✅ Gap analysis: Compare our draft with popular articles — what are they covering that we're not?
3. ✅ Collect official references: Find trusted/official documentation sources worldwide
4. ✅ Research common errors/pitfalls: Search worldwide for real-world troubleshooting posts, Stack Overflow, GitHub issues related to the topic. Document what errors people encounter and how to fix them.
5. ✅ Write/improve article with MANDATORY "Trial and Error" section (see below)
6. ✅ Safety check #1: Scan for PayPay/Toyota/company-specific numbers/names. ALL numbers and names must be generic.
7. ✅ Safety check #2: Re-scan entire article for any indirect company references
8. ✅ Safety check #3: **Technical review by separate agent** — spawn a reviewer agent to verify all technical claims, code, configs are correct. DO NOT publish if review fails.
9. ✅ Safety check #4: **AI-detection check** — Read all of Takahiro's past Medium posts. Write in his voice. English must NOT be perfect (see Japanese-English style guide). The article must read as if a real human wrote it.
10. ✅ Publish on Medium with tags and Unsplash image
11. ✅ 4 hours later: Cross-post to dev.to via API
12. ✅ Share on LinkedIn (match Takahiro's style: emoji headers, 🔹 bullet points, hashtags)
13. ✅ Report analytics from previous day

## Quality Improvement Process (MUST improve daily)
### Step A: Research Popular Articles
- Fetch medium.com/tag/{topic}/recommended to find trending articles
- Read top 3-5 articles to understand what readers engage with
- Note: depth of technical content, diagrams, code examples, real-world scenarios

### Step B: Gap Analysis
- What topics do popular articles cover that ours doesn't?
- Are there architectural diagrams or flowcharts we should add?
- Do they reference official tools/frameworks we should mention?
- What makes their titles/subtitles more clickable?

### Step C: Trial and Error Section (MANDATORY in every article)
Every article MUST include a "Troubleshooting" or "What Went Wrong" section that:
- Describes 2-3 real errors/pitfalls that people commonly encounter with this topic
- Research worldwide: Stack Overflow, GitHub issues, Reddit, blog posts about common problems
- Write as if Takahiro personally hit these issues in his home lab
- Show the error message/symptom
- Explain what caused it
- Show how it was resolved
- This makes articles feel authentic and human (not AI-generated)

### Step D: Technical Review (MANDATORY before publish)
- Spawn a separate reviewer agent to validate:
  - All code examples compile/run correctly
  - YAML/JSON configs are syntactically valid
  - Tool versions and API endpoints are current
  - Security concepts are accurately described
  - MITRE ATT&CK technique IDs are correct
- If reviewer finds issues → fix before publishing
- NEVER publish an article that fails technical review

### Step E: Authenticity Check (MANDATORY before publish)
- Read Takahiro's past Medium posts to match his voice
- Ensure English has 3-5 subtle Japanese-English patterns (see style guide)
- Verify the article does NOT sound AI-generated:
  - No perfect parallel structures
  - No overly smooth transitions
  - Include personal opinions and "I think" / "I feel" statements
  - Reference previous articles naturally
  - Vary sentence length (mix short punchy with longer explanations)

### Step F: Company Reference Safety Check (MANDATORY)
- NO PayPay, Toyota, or ANY company-specific references
- ALL numbers must be generic (no real transaction volumes, user counts, etc.)
- ALL system names must be generic or well-known open-source names
- If in doubt, use fictional/generic names
- Scan the entire article TWICE before publishing

### Step G: Official References (MUST INCLUDE)
Every article must end with a "References" section linking to trusted official sources:
- MITRE ATT&CK: https://attack.mitre.org/
- Sigma HQ: https://github.com/SigmaHQ/sigma
- NIST: https://www.nist.gov/cybersecurity
- AWS Security Docs: https://docs.aws.amazon.com/security/
- CrowdStrike Docs: https://www.crowdstrike.com/resources/
- Splunk Docs: https://docs.splunk.com/
- OWASP: https://owasp.org/
- CISA: https://www.cisa.gov/
- Wiz Academy: https://www.wiz.io/academy
- And any other relevant official docs for the topic

## LinkedIn Posting Style (from Takahiro's existing posts)
- Emoji headers (✨, 🔹, 🚨, 🔍)
- Casual but professional tone
- Short punchy sentences
- Hashtags at the end (5-10 relevant tags)
- Link to Medium article
- **MUST include GitHub repo link**: https://github.com/choshuoyaji/home-lab-security-stack
- Format example: "🔗 Full code & configs on GitHub: <repo link>"
- 2,476 followers to engage

### LinkedIn AI Detection Prevention (MANDATORY before posting)
Before posting ANY LinkedIn content, run this checklist:
1. **Read Takahiro's last 5 LinkedIn posts** — match tone, emoji usage, sentence structure
2. **No AI-typical patterns**: 
   - NO "In today's rapidly evolving..." / "In the ever-changing landscape..."
   - NO "I'm excited to share..." / "I'm thrilled to announce..."
   - NO perfect bullet point symmetry (vary lengths)
   - NO "Key takeaways:" followed by perfect parallel structure
   - NO overuse of "leverage", "utilize", "streamline", "empower"
3. **Add human imperfections**:
   - Occasional casual abbreviation (tbh, btw)
   - One or two slightly informal expressions
   - Reference specific personal experience ("spent 3 hours debugging this lol")
   - Include a personal opinion that's slightly strong ("I think X is overrated")
4. **Japanese-English naturalness**: Same subtle patterns as Medium articles (see style guide above)
5. **Final AI-detection test**: Re-read the post. Would a human LinkedIn user flag this as AI? If yes, rewrite.

## Performance Analysis (DAILY — report to Slack #all-ai)
Check daily on ALL platforms and report findings:
### Medium
- Views, reads, read ratio
- Claps and responses
- New followers gained

### dev.to
- Views, reactions, comments
- New followers gained
- Bookmark count

### LinkedIn
- Impressions (visible in post analytics)
- Likes, comments, reposts
- Profile views change
- Which topics perform best

### Daily Improvement Actions
Based on analytics, MUST improve at least one thing daily:
- Title/subtitle optimization based on click-through
- Content depth based on read ratio
- Tag strategy based on reach
- Posting time optimization
- Topic selection based on engagement
- Cross-platform performance comparison
- Document what was changed and why in the schedule tracker
