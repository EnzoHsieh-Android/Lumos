#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
MODE="${1:---dry-run}"
MAXR="${2:-6}"
TODAY="$(date +%F)"
REPORT="$SCRIPT_DIR/reports/governance-$TODAY.json"
PENDING="$SCRIPT_DIR/pending";  mkdir -p "$PENDING"
LOGDIR="$SCRIPT_DIR/logs";      mkdir -p "$LOGDIR"
SCRATCH="/tmp/auto-loop-$TODAY"; mkdir -p "$SCRATCH/kg" "$SCRATCH/spec"
log(){ echo "[$(date '+%F %T')] $*"; }

if [ ! -f "$REPORT" ]; then
  if [ "$MODE" = "--dry-run" ]; then
    REPORT="$(ls -t "$SCRIPT_DIR/reports/"governance-2*.json 2>/dev/null | head -1 || true)"
    [ -n "$REPORT" ] && log "今日無日報,dry-run fallback:$REPORT" || { log "無任何日報,結束"; exit 0; }
  else log "今日無日報($TODAY),跳過"; exit 0; fi
fi

SKIP_CAP=3; skip_n=0
while : ; do
GAP_JSON="$(cd "$REPO" && python3 -c "
import sys, json; sys.path.insert(0,'governance')
from autonomous_loop import gap_select
mode='pr' if '$MODE'=='--pr' else 'dryrun'
g=gap_select.select('$REPORT','$SCRIPT_DIR/backlog.jsonl','$PENDING',mode,'$TODAY','$SCRIPT_DIR/covered.jsonl')
print(json.dumps(g, ensure_ascii=False) if g else '')
")"
[ -n "$GAP_JSON" ] || { log "無可展開 gap(N=1 gate 或 backlog 空),結束"; exit 0; }
log "選中 gap:$GAP_JSON"

PROMPT_FILE="$(mktemp)"
sed -e "s#__SCRATCH__#$SCRATCH#g" -e "s#__DATE__#$TODAY#g" -e "s#__MAXR__#$MAXR#g" \
    "$SCRIPT_DIR/autonomous_loop/orchestrator-prompt.md" > "$PROMPT_FILE"
printf '\n\n## 要處理的 gap\n%s\n模式:%s\n' "$GAP_JSON" "$MODE" >> "$PROMPT_FILE"
export ANTHROPIC_API_KEY=""
export CLAUDE_CODE_OAUTH_TOKEN="$(cat "$HOME/.config/ai-daily/claude_oauth_token" 2>/dev/null)"
ORCH_OUT="$LOGDIR/orchestrator-$TODAY.json"
log "派 orchestrator(claude -p,最多 $MAXR 輪)..."
(cd "$REPO" && claude -p "$(cat "$PROMPT_FILE")" \
  --allowedTools "Read,Edit,Bash,Grep,Glob,Agent" \
  --permission-mode acceptEdits --output-format json) > "$ORCH_OUT" 2>"$LOGDIR/orchestrator-$TODAY.err" || true
rm -f "$PROMPT_FILE"

PARSED="$(cd "$REPO" && python3 -c "
import json, sys; sys.path.insert(0,'governance')
from autonomous_loop import orchestrator_result
try: o=json.load(open('$ORCH_OUT'))
except Exception as e: print('PARSE_FAIL:'+str(e)); sys.exit(0)
r=orchestrator_result.extract_json(o.get('result',''))
print(json.dumps(r, ensure_ascii=False) if r else 'NO_JSON')
")"
log "orchestrator 回傳:$PARSED"
case "$PARSED" in PARSE_FAIL*|NO_JSON*|"") log "orchestrator 輸出無法解析,中止(log $ORCH_OUT)"; exit 1;; esac

get(){ echo "$PARSED" | python3 -c "import json,sys;print(json.load(sys.stdin).get('$1',''))"; }
SKIPPED="$(get skipped)"; CONVERGED="$(get converged)"; TOPIC="$(get topic)"; SPEC="$(get spec_path)"
CROSS_VERDICT="$(get cross_verdict)"; CROSS_WORST="$(get cross_worst)"; CROSS_SUMMARY="$(get cross_summary)"
CROSS_SUMMARY="${CROSS_SUMMARY//$'\n'/ }"   # F3 防破版:換行→空格

if [ "$SKIPPED" = "True" ]; then
  skip_n=$((skip_n+1))
  echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
w=json.load(sys.stdin).get('weakness','')
if w: gap_select.mark_covered('$SCRIPT_DIR/covered.jsonl', w)
" 2>/dev/null || true
  log "gap 已被既有 spec 覆蓋,skip(reason: $(get reason));已記入 covered、永久不再選。循環選下一個($skip_n/$SKIP_CAP)。"
  [ "$skip_n" -ge "$SKIP_CAP" ] && { log "連 skip $SKIP_CAP 個已覆蓋 gap,今天結束(剩餘留 backlog 明天再選)。"; exit 0; }
  continue
fi
break
done

RESIDUAL='["跨家族複核已加(qwen3-max 放行前複核 opus 設計、補同門盲點);但 degrade 時退回單一 opus、qwen 也是 AI、verdict 判定仍在 orchestrator(prompt 層自律)","severity 由 judge 評(已斷 orchestrator 自填)但 judge 也是 AI、且同輪判 canary+severity=集中化","type d canary 沒測(限 a/b/c)","自動 brainstorm 無人回澄清;AI 自選 gap=自己決定改自己方向(自我強化偏誤)","唯一外部錨點是你 review 這個 PR"]'
if [ "$CONVERGED" != "True" ]; then
  if [ "$CROSS_VERDICT" = "disputed" ]; then
    MSG="⚠ 跨家族否決(qwen 持續異議):$CROSS_SUMMARY"; log "未收斂(跨家族否決 disputed),不放行:$CROSS_SUMMARY"
  else
    MSG="⚠ 今日 spec 未收斂、未放行(撞 cap)"; log "未收斂(converged=$CONVERGED),不放行,scratch 不入庫。"
  fi
  MSG="$MSG" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t='$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)'
print('LINE', line_notify.send(line_notify.build_message('$TOPIC',os.environ['MSG'],None),t) if t else 'no-token')" || true
  # 副作用 A:未收斂 gap 回 backlog 降分 + 累計 unconverged;達 3 次 → covered(放棄自動、留人),不立即消失
  RQ="$(echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
g=json.load(sys.stdin)
print(gap_select.requeue_unconverged('$SCRIPT_DIR/backlog.jsonl', g, '$SCRIPT_DIR/covered.jsonl'))
" 2>/dev/null || echo '?')"
  log "未收斂 gap 處置:$RQ(回 backlog 降分重試 / 累計達 3 次 covered)"
  exit 0
fi

REPORT_MD="$(cd "$REPO" && python3 -c "
import sys, json; sys.path.insert(0,'governance')
from autonomous_loop import confidence_report
print(confidence_report.build_report('$SCRATCH/.canary-log.jsonl','$TOPIC', json.loads('''$RESIDUAL''')))
")"

[ -n "$CROSS_VERDICT" ] && log "跨家族複核:$CROSS_VERDICT($CROSS_WORST)— $CROSS_SUMMARY"
if [ "$MODE" = "--dry-run" ]; then
  cp "$SPEC" "$PENDING/" 2>/dev/null || true
  printf '%s\n' "$REPORT_MD" > "$PENDING/$(basename "$SPEC" .md)-confidence.md"
  log "dry-run:收斂!spec + 可信度報告寫入 $PENDING/(repo 未動)"
  python3 -c "
import sys; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t='$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)'
print('LINE', line_notify.send(line_notify.build_message('$TOPIC','(dry-run)收斂[跨家族:$CROSS_VERDICT]、待你看 pending/',None),t) if t else 'no-token')" || true
else
  cd "$REPO"; BR="auto/spec-$TOPIC-$TODAY"
  cp "$SPEC" "docs/design/$(basename "$SPEC")"
  git checkout -b "$BR"; git add "docs/design/$(basename "$SPEC")"
  git commit -m "auto-spec: $TOPIC（自主迭代 loop 收斂產出，待人放行）"
  echo "$REPORT_MD" | gh pr create --title "auto-spec: $TOPIC" --body-file - || true
  log "已開 PR(branch $BR)"
fi
log "完成。"
