#!/usr/bin/env bash
# lint-watch 每日排程:查 registry 新穩定版 → 新候選暫存 + LINE 通知(fail-open,不阻斷 wrapper)。
# autonomous-loop.sh 用 python3 scripts/lumos 不用裸 lumos(cron 下 ~/.local/bin 不保證在 PATH);
# 此腳本同樣用 python3 確保排程環境可解析。
#
# 2026-07-17 收網三修(見 Issues/lint-watch空轉假綠):
#   ① SSL_CERT_FILE——本機 python urllib 憑證鏈壞(CERTIFICATE_VERIFY_FAILED),全 fetch 回 None;
#     curl 走 macOS 鑰匙圈所以看不出。指到 macOS 內建 /etc/ssl/cert.pem。
#   ② 多 repo 撒網——原本只掃源 repo(零依賴、無宣告檔)=恆空轉;真宣告在消費專案。
#   ③ 心跳行——candidates/failed 計數落 log,全失敗(如憑證鏈壞)不再無聲 rc0。
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOLCHAIN="$(cd "$SCRIPT_DIR/.." && pwd)"
DIR="$TOOLCHAIN/governance/lint-upgrades"
mkdir -p "$DIR"
TODAY="$(date +%Y-%m-%d)"
DEDUP="$TOOLCHAIN/governance/autonomous_loop/lint_watch_dedup.py"
TOKEN_FILE="$HOME/.config/ai-daily/line_token"

# ① python urllib 缺 CA bundle → 指到 macOS 內建(未設定才 export,不覆蓋外部設定)
[ -z "${SSL_CERT_FILE:-}" ] && [ -f /etc/ssl/cert.pem ] && export SSL_CERT_FILE=/etc/ssl/cert.pem

# ② 撒網清單:有 .lumos/lint-watch.json 的才有魚;無宣告檔者跳過並留一行痕
REPOS=(
  "$TOOLCHAIN"
  "$HOME/backend/LandmarkMember"
)

ts() { date '+%Y-%m-%d %H:%M:%S'; }
for REPO in "${REPOS[@]}"; do
  NAME="$(basename "$REPO")"
  if [ ! -f "$REPO/.lumos/lint-watch.json" ]; then
    echo "[$(ts)] $NAME: 無 .lumos/lint-watch.json,跳過"
    continue
  fi
  SEEN="$DIR/seen-$NAME.jsonl"
  PENDING="$DIR/pending-$NAME-$TODAY.json"
  RAW="$(python3 "$TOOLCHAIN/scripts/lumos" lint-watch --repo "$REPO" --json 2>/dev/null)" || true
  # ③ 心跳:每 repo 一行計數,log 不再 0 bytes
  SUMMARY="$(printf '%s' "$RAW" | python3 -c "import sys,json
d=json.load(sys.stdin)
print('candidates=%d checked=%s failed=%d' % (len(d.get('candidates',[])), d.get('checked',0), len(d.get('failed',[]))))" 2>/dev/null || echo '輸出不可解析')"
  echo "[$(ts)] $NAME: $SUMMARY"
  MSG="$(printf '%s' "$RAW" | python3 "$DEDUP" "$SEEN" "$PENDING" "$TODAY")" || true
  if [ -n "$MSG" ] && [ -f "$TOKEN_FILE" ]; then
    MSG="$MSG" python3 -c "import os,json,sys; sys.path.insert(0,'$TOOLCHAIN/governance'); from autonomous_loop import line_notify; line_notify.send(json.loads(os.environ['MSG']), open('$TOKEN_FILE').read().strip())" || true
  fi
done
exit 0
