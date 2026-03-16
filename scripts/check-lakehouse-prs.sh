#!/bin/bash
# Monitor merged PRs for Mmodarre/Lakehouse_Plumber
# Stores last seen merged PR timestamp to avoid duplicates

STATE_FILE="$HOME/.openclaw/workspace/scripts/.lakehouse-pr-state"
REPO="Mmodarre/Lakehouse_Plumber"
API_URL="https://api.github.com/repos/${REPO}/pulls?state=closed&sort=updated&direction=desc&per_page=10"

# Get last seen timestamp (default to now if first run)
if [ -f "$STATE_FILE" ]; then
  LAST_SEEN=$(cat "$STATE_FILE")
else
  # First run: set to current time so we only catch new merges going forward
  LAST_SEEN=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "$LAST_SEEN" > "$STATE_FILE"
  echo "First run — baseline set to $LAST_SEEN"
  exit 0
fi

# Fetch recent closed PRs
RESPONSE=$(curl -s "$API_URL")

# Parse merged PRs newer than last seen
NEW_PRS=$(echo "$RESPONSE" | python3 -c "
import json, sys
from datetime import datetime

data = json.load(sys.stdin)
last_seen = '$LAST_SEEN'

merged = []
for pr in data:
    merged_at = pr.get('merged_at')
    if merged_at and merged_at > last_seen:
        merged.append({
            'number': pr['number'],
            'title': pr['title'],
            'url': pr['html_url'],
            'author': pr['user']['login'],
            'merged_at': merged_at,
            'body': (pr.get('body') or '')[:500],
            'labels': [l['name'] for l in pr.get('labels', [])]
        })

# Sort oldest first so we notify in order
merged.sort(key=lambda x: x['merged_at'])

if merged:
    print(json.dumps(merged))
else:
    print('[]')
" 2>/dev/null)

if [ "$NEW_PRS" = "[]" ] || [ -z "$NEW_PRS" ]; then
  echo "NO_NEW_PRS"
  exit 0
fi

# Output the new PRs as JSON for the cron task to process
echo "$NEW_PRS"

# Update state to the latest merged_at
LATEST=$(echo "$NEW_PRS" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(max(pr['merged_at'] for pr in data))
" 2>/dev/null)

if [ -n "$LATEST" ]; then
  echo "$LATEST" > "$STATE_FILE"
fi
