#!/usr/bin/env bash
# lint-watch 每日排程:查 registry 新穩定版 → 新候選暫存 + LINE 通知(fail-open,不阻斷 wrapper)。
# autonomous-loop.sh 用 python3 scripts/lumos 不用裸 lumos(cron 下 ~/.local/bin 不保證在 PATH);
# 此腳本同樣用 python3 "$REPO/scripts/lumos" 確保排程環境可解析。
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO="$SCRIPT_DIR/.."
DIR="$REPO/governance/lint-upgrades"
mkdir -p "$DIR"
TODAY="$(date +%Y-%m-%d)"
SEEN="$DIR/seen.jsonl"
PENDING="$DIR/pending-$TODAY.json"
DEDUP="$REPO/governance/autonomous_loop/lint_watch_dedup.py"

MSG="$(python3 "$REPO/scripts/lumos" lint-watch --repo "$REPO" --json 2>/dev/null | python3 "$DEDUP" "$SEEN" "$PENDING" "$TODAY")" || true
TOKEN_FILE="$HOME/.config/ai-daily/line_token"
if [ -n "$MSG" ] && [ -f "$TOKEN_FILE" ]; then
  MSG="$MSG" python3 -c "import os,json,sys; sys.path.insert(0,'$REPO/governance'); from autonomous_loop import line_notify; line_notify.send(json.loads(os.environ['MSG']), open('$TOKEN_FILE').read().strip())" || true
fi
exit 0
