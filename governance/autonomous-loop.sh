#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
MODE="${1:---dry-run}"          # --dry-run | --pr
MAXR="${2:-6}"                  # design-loop 最大輪數(dry-run 測試可傳小值)
TODAY="$(date +%F)"
REPORT="$SCRIPT_DIR/reports/governance-$TODAY.json"
PENDING="$SCRIPT_DIR/pending";  mkdir -p "$PENDING"
LOGDIR="$SCRIPT_DIR/logs";      mkdir -p "$LOGDIR"
SCRATCH="/tmp/auto-loop-$TODAY"; mkdir -p "$SCRATCH/kg"
log(){ echo "[$(date '+%F %T')] $*"; }

# --- 驗當日日報(R3-F-R3-3:缺日跳過;dry-run 測試 fallback 最近一份)---
if [ ! -f "$REPORT" ]; then
  if [ "$MODE" = "--dry-run" ]; then
    REPORT="$(ls -t "$SCRIPT_DIR/reports/"governance-2*.json 2>/dev/null | head -1 || true)"
    [ -n "$REPORT" ] && log "今日無日報,dry-run fallback 最近一份:$REPORT" || { log "無任何日報,結束"; exit 0; }
  else
    log "今日無日報($TODAY),跳過(不視為錯誤)"; exit 0
  fi
fi

# --- gap_select(N=1 gate)---
GAP_JSON="$(cd "$REPO" && python3 -c "
import sys, json; sys.path.insert(0,'governance')
from autonomous_loop import gap_select
mode = 'pr' if '$MODE'=='--pr' else 'dryrun'
g = gap_select.select('$REPORT', '$SCRIPT_DIR/backlog.jsonl', '$PENDING', mode, '$TODAY')
print(json.dumps(g, ensure_ascii=False) if g else '')
")"
[ -n "$GAP_JSON" ] || { log "無可展開 gap(N=1 gate 擋 或 backlog 空),結束"; exit 0; }
log "選中 gap:$GAP_JSON"

# --- 跑 orchestrator(brainstorm + design-loop)---
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

# --- 解析 orchestrator 結果 ---
PARSED="$(cd "$REPO" && python3 -c "
import json, re, sys
try: o=json.load(open('$ORCH_OUT'))
except Exception as e: print('PARSE_FAIL outer:'+str(e)); sys.exit(0)
res=o.get('result','')
m=re.search(r'\{.*\}', res, re.S)
if not m: print('NO_JSON_IN_RESULT'); sys.exit(0)
try: r=json.loads(m.group(0))
except Exception as e: print('PARSE_FAIL inner:'+str(e)); sys.exit(0)
print(json.dumps(r, ensure_ascii=False))
")"
log "orchestrator 回傳:$PARSED"
case "$PARSED" in PARSE_FAIL*|NO_JSON*|"") log "orchestrator 輸出無法解析,中止放行(log 留 $ORCH_OUT)"; exit 1;; esac

CONVERGED="$(echo "$PARSED" | python3 -c "import json,sys;print(json.load(sys.stdin).get('converged'))")"
TOPIC="$(echo "$PARSED" | python3 -c "import json,sys;print(json.load(sys.stdin).get('topic',''))")"
SPEC="$(echo "$PARSED" | python3 -c "import json,sys;print(json.load(sys.stdin).get('spec_path',''))")"

# --- 放行閘 ---
RESIDUAL='["severity 自報直接決定收斂門檻(judge 不覆蓋)——全自動判收斂最弱環","自動 brainstorm 無人回澄清,選錯方向風險高於有人時","AI 自選 gap=自己決定改自己方向,有自我強化偏誤","唯一外部錨點是你 review 這個產出"]'
if [ "$CONVERGED" != "True" ]; then
  log "未收斂(converged=$CONVERGED),不放行。"
  python3 -c "
import sys; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t='$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)'
m=line_notify.build_message('$TOPIC','⚠ 今日 spec 未收斂、未開 PR(撞 cap)', None)
print('LINE', line_notify.send(m,t) if t else 'no-token-skip')" || true
  exit 0
fi

REPORT_MD="$(cd "$REPO" && python3 -c "
import sys, json; sys.path.insert(0,'governance')
from autonomous_loop import confidence_report
print(confidence_report.build_report('$SCRATCH/.canary-log.jsonl','$TOPIC', json.loads('''$RESIDUAL''')))
")"
SUMMARY="$(echo "$REPORT_MD" | head -3 | tail -1)"

if [ "$MODE" = "--dry-run" ]; then
  cp "$REPO/$SPEC" "$PENDING/" 2>/dev/null || true
  printf '%s\n' "$REPORT_MD" > "$PENDING/$(basename "$SPEC" .md)-confidence.md"
  log "dry-run:spec + 可信度報告寫入 $PENDING/"
  python3 -c "
import sys; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t='$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)'
m=line_notify.build_message('$TOPIC','(dry-run)收斂、待你看 pending/', None)
print('LINE', line_notify.send(m,t) if t else 'no-token-skip')" || true
else
  cd "$REPO"
  BR="auto/spec-$TOPIC-$TODAY"
  git checkout -b "$BR"; git add "$SPEC"; git commit -m "auto-spec: $TOPIC（自主迭代 loop 收斂產出，待人放行）"
  echo "$REPORT_MD" | gh pr create --title "auto-spec: $TOPIC" --body-file - || true
  log "已開 PR(branch $BR)"
fi
log "完成。"
