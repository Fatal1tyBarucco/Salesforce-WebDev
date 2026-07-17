#!/bin/sh
cd /workspace/Salesforce-WebDev
REMOTE=$(git remote get-url origin)
TOKEN=$(echo "$REMOTE" | sed -E 's#.*://([^@]+)@.*#\1#')
REPO=Fatal1tyBarucco/Salesforce-WebDev

deadline=$(($(date +%s) + 540))
while [ "$(date +%s)" -lt "$deadline" ]; do
  resp=$(curl -s -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$REPO/actions/runs?per_page=10")
  echo "$resp" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
except Exception as e:
    print('JSON parse error:', e); sys.exit(0)
runs = d.get('workflow_runs', [])
if not runs:
    print('No workflow runs found yet')
else:
    for r in runs[:6]:
        print('RUN', r['id'], '|', r['name'], '|', r['status'], '|', r['conclusion'], '|', r['head_branch'], '|', r['created_at'])
    latest = runs[0]
    if latest['status'] == 'completed':
        print('LATEST_COMPLETED', latest['id'], latest['conclusion'])
        sys.exit(7)
"
  rc=$?
  if [ "$rc" -eq 7 ]; then
    echo "=== Latest run completed, stopping poll ==="
    break
  fi
  sleep 30
done
