#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
MODE="${1:---dry-run}"
MAXR="${2:-6}"
# 非 dry-run 停用(2026-07-29 使用者裁定,Codex 外審採納):子 agent 權限隔離
# (Systems/nested-agent-permission-scope,planned)落地前,confused-deputy 已知漏洞
# 不留可執行入口——--pr 直接拒跑。解禁條件:read-only child isolation 落地+過 code-loop。
if [ "$MODE" != "--dry-run" ]; then
  echo "autonomous-loop: 非 dry-run 已停用(2026-07-29 裁定,詳見圖譜 nested-agent-permission-scope);dry-run 照常" >&2
  exit 2
fi
# ── 整跑鎖(code-r1 s2-f1/f2):launchd+人工同時跑會互蓋 backlog/archive——mkdir 原子搶鎖,
# 鎖裡放 PID;持鎖行程已死(kill -0 不到)視為殘鎖接管。SIGKILL 殘鎖靠這條自癒。
LOCKDIR="$SCRIPT_DIR/.autonomous-loop.lock"
if ! mkdir "$LOCKDIR" 2>/dev/null; then
  OLDPID="$(cat "$LOCKDIR/pid" 2>/dev/null || echo '')"
  if [ -n "$OLDPID" ] && kill -0 "$OLDPID" 2>/dev/null; then
    echo "[$(date '+%F %T')] 另一份 autonomous-loop 正在跑(pid $OLDPID),本次退出——不搶寫 backlog"; exit 0
  fi
  # ★空 pid ≠ 殘鎖★(r2 d-f2 TOCTOU):對方可能剛 mkdir 成功、還沒來得及寫 pid——
  # 「pid 沒寫」與「pid 寫過但行程死了」不能走同一條接管路。只有鎖齡超過 60 分鐘
  # (真跑最長也早該寫完 pid)才視為殘鎖;年輕的空 pid 鎖一律讓行。
  if [ -z "$OLDPID" ]; then
    LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCKDIR" 2>/dev/null || echo 0) ))
    if [ "$LOCK_AGE" -lt 3600 ]; then
      echo "[$(date '+%F %T')] 另一份 autonomous-loop 疑似剛起步(鎖存在 ${LOCK_AGE}s、pid 未寫),本次退出讓行"; exit 0
    fi
  fi
  echo "[$(date '+%F %T')] 發現殘鎖(pid ${OLDPID:-?} 已不在或鎖齡過老),接管"
  rm -rf "$LOCKDIR"; mkdir "$LOCKDIR"
fi
echo $$ > "$LOCKDIR/pid"

TODAY="$(date +%F)"
REPORT="$SCRIPT_DIR/reports/governance-$TODAY.json"
PENDING="$SCRIPT_DIR/pending";  mkdir -p "$PENDING"
LOGDIR="$SCRIPT_DIR/logs";      mkdir -p "$LOGDIR"
SCRATCH="$(mktemp -d "/tmp/auto-loop-$TODAY.XXXXXX")"; mkdir -p "$SCRATCH/kg" "$SCRATCH/spec"   # mktemp:防可預測路徑搶佔(外審 minor)
log(){ echo "[$(date '+%F %T')] $*"; }

# ── 收尾器(auto-loop-repair-v2 [S1]+[S3]+[S4]):trap EXIT 統一做四件事——
# ①未處置 gap 原分放回(失敗不丟件,涵蓋全部早退點;滿 3 次熔斷 covered+喊人)
# ②結局落帳(結構化欄 --outcome/--usd;與成本抽取解耦,PARSE_FAIL 也有帳)
# ③連兩個有跑日全失敗 → LINE 喊人(素訊息,不套「備好待放行」模板)
# ④七天產出一行(失敗日也印——放 trap 就是為了這個)
# 內部所有指令都要 fail-open(|| true / if 判),trap 裡一個炸掉會吞掉後面全部。
# ★誠實邊界(code-r1 s2-f3)★:trap EXIT 接得住 bash 攔得到的退出,接不住 SIGKILL/斷電;
# 那個窗口由 in-flight 標記檔補——選中 gap 先落標記,下次開場發現殘留標記就放回。
GAP_JSON=""; GAP_DISPOSED=""; OUTCOME=""; COST_ARGS=""; FINAL_DONE=""; ROUND_RECORDED=""
INFLIGHT="$SCRIPT_DIR/.inflight-gap.json"
finalize(){
  [ -n "$FINAL_DONE" ] && return 0; FINAL_DONE=1
  rm -f "${PROMPT_FILE:-}" 2>/dev/null || true
  [ -n "${SCRATCH:-}" ] && rm -rf "$SCRATCH" 2>/dev/null || true   # code-r1 s2-f5:暫存不累積
  if [ -z "$GAP_JSON" ]; then rm -rf "$LOCKDIR" 2>/dev/null || true; return 0; fi   # 還沒選中 gap 的早退(無日報/無 gap):無輪無帳
  if [ -z "$GAP_DISPOSED" ]; then
    RQ="$(echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
g=json.load(sys.stdin)
print(gap_select.requeue_pipeline_fail('$SCRIPT_DIR/backlog.jsonl', g, '$SCRIPT_DIR/covered.jsonl'))
" 2>>"$LOGDIR/finalize-$TODAY.err" || echo '?')"
    log "失敗不丟件:gap 已放回 backlog($RQ;分數不動,pipeline_failures 累計,滿 3 次轉 covered 留人)"
    if [ "$RQ" = "covered" ]; then
      MSG="⚠ 自主迴圈:某 gap 連 3 次管線失敗,已轉 covered 留人手動(weakness 見 governance/covered.jsonl 末行)"       LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_alert(os.environ['MSG']), t) if t else 'no-token')" || true
    fi
  fi
  if [ -z "$ROUND_RECORDED" ]; then   # skip 迭代已當場落帳的輪不重複記(code-r1 s1-f1/s3-f1)
    # shellcheck disable=SC2086  # COST_ARGS 故意不引號:要拆成多參數
    if ! (cd "$REPO" && python3 scripts/lumos canary record none --loop "auto-$TODAY"           --auditor orchestrator --outcome "${OUTCOME:-pipeline_fail:parse_fail}" $COST_ARGS           --note "自主迴圈結局帳(trap 收尾統一落;成本欄=claude -p 實際回傳,非估算)")           >>"$LOGDIR/cost-$TODAY.log" 2>&1; then
      log "結局帳:record 失敗——帳上沒有這輪(詳情 $LOGDIR/cost-$TODAY.log)"
    fi
  fi
  if [ -n "$GAP_DISPOSED" ] || [ "${RQ:-}" = "requeued" ] || [ "${RQ:-}" = "covered" ]; then
    rm -f "$INFLIGHT" 2>/dev/null || true   # gap 真有去向才解除斷電保險(r2 d-f3)
  else
    log "⚠ gap 放回未確認(${RQ:-無}),in-flight 標記保留給下次開場回收"
  fi
  LEDGER_OUT="$(cd "$REPO" && python3 -c "
import sys; sys.path.insert(0,'governance')
from autonomous_loop import run_ledger
lg='docs/.canary-log.jsonl'
print(run_ledger.format_week_line(run_ledger.summarize_week(lg,'$TODAY')))
print('CONSEC_FAIL' if run_ledger.consecutive_fail_days(lg,'$TODAY') else 'OK')
" 2>>"$LOGDIR/finalize-$TODAY.err" || echo '')"
  if [ -n "$LEDGER_OUT" ]; then
    log "$(echo "$LEDGER_OUT" | head -1)"
    if echo "$LEDGER_OUT" | grep -q CONSEC_FAIL; then
      log "⚠ 連兩個有跑日全是管線失敗——不是天氣,喊人"
      MSG="⚠ 自主迴圈連兩個有跑日管線全失敗($(echo "$LEDGER_OUT" | head -1));死因分類看 canary 帳 outcome 欄,log $LOGDIR/"       LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_alert(os.environ['MSG']), t) if t else 'no-token')" || true
    fi
  else
    log "七天彙總:算不出來(詳 $LOGDIR/finalize-$TODAY.err)——不擋收尾,但這行沒了要查"
  fi
  rm -rf "$LOCKDIR" 2>/dev/null || true
}
trap finalize EXIT

# ── in-flight 殘留回收(code-r1 s2-f3):上次被 SIGKILL/斷電砍在半路的 gap 放回 ──
if [ -f "$INFLIGHT" ]; then
  RQ0="$(python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
g=json.load(open('$INFLIGHT'))
print(gap_select.requeue_pipeline_fail('$SCRIPT_DIR/backlog.jsonl', g, '$SCRIPT_DIR/covered.jsonl'))
" 2>>"$LOGDIR/finalize-$TODAY.err" || echo '?')"
  case "$RQ0" in
    requeued|covered)
      log "上次執行被硬砍(SIGKILL/斷電),殘留的選中 gap 已放回($RQ0)"; rm -f "$INFLIGHT";;
    *)
      log "⚠ 上次被硬砍的 gap 放回失敗($RQ0)——標記保留,下次開場再試;唯一證據不自我銷毀(詳 $LOGDIR/finalize-$TODAY.err)";;
  esac
fi

if [ ! -f "$REPORT" ]; then
  if [ "$MODE" = "--dry-run" ]; then
    REPORT="$(ls -t "$SCRIPT_DIR/reports/"governance-2*.json 2>/dev/null | head -1 || true)"
    [ -n "$REPORT" ] && log "今日無日報,dry-run fallback:$REPORT" || { log "無任何日報,結束"; exit 0; }
  else log "今日無日報($TODAY),跳過"; exit 0; fi
fi

# ── 週期考卷(2026-08-05 掛載):雙庫檢索考卷 ≥7 天未跑就補跑——把「hook 調參靠記得」
# 變「定期發生」;fail-open,考卷失敗只記 log 不阻斷 gap 流程。判定/漂移細節在
# retrieval_eval.py 自己的 gate 輸出與 history jsonl,此處只管排程。
run_exam(){ local repo="$1" tag="$2"
  local hist="$repo/governance/eval/retrieval-eval-history.jsonl"
  local gold="$repo/governance/eval/retrieval-goldset.json"
  [ -f "$gold" ] || { log "考卷($tag):無 goldset,跳過"; return 0; }
  # 取「最後一筆帶 ts 的 goldset 列」(單席快審 F3:末行可能是無 ts 的 auto-cochange 列→誤判 1970 天天重考)
  local last; last="$(python3 -c '
import json,sys
last="1970-01-01"
try:
    for l in open(sys.argv[1],encoding="utf-8"):
        try: d=json.loads(l)
        except ValueError: continue
        if d.get("ts") and d.get("mode","goldset")=="goldset": last=d["ts"]
except OSError: pass
print(last)' "$hist" 2>/dev/null || echo 1970-01-01)"
  local last_s; last_s="$(date -j -f %F "$last" +%s 2>/dev/null || echo 0)"
  local age=$(( ( $(date +%s) - last_s ) / 86400 ))
  if [ "$age" -ge 7 ]; then
    log "考卷($tag):距上次 ${age} 天(>7),補跑 held split"
    (cd "$repo" && python3 governance/eval/retrieval_eval.py --goldset "$gold" --split held) > "$LOGDIR/exam-$tag-$TODAY.log" 2>&1 || true
    # 完成判定看「gate 總判定」行,不看 rc——部分版本 gate FAIL 即回非零,那是調參訊號非執行失敗
    if grep -q 'gate 總判定' "$LOGDIR/exam-$tag-$TODAY.log"; then
      log "考卷($tag)完成:$(grep 'gate 總判定' "$LOGDIR/exam-$tag-$TODAY.log" | tail -1)"
      # ── 標註刷新 S4 薄接線(2026-08-18):unjudged 超通知線→產 delta 表+LINE 等人放行。
      # 邏輯全在 refresh_labels.py signal(受測);此處只 grep over=yes,不看 rc(advisory)。
      local sig; sig="$(cd "$repo" && python3 governance/eval/refresh_labels.py signal --history "$hist" 2>/dev/null || echo '')"
      log "考卷($tag)未標率:${sig:-NA}"
      if echo "$sig" | grep -q 'over=yes'; then
        # ★rc+產物存在雙查後才通報★(code-r1 資源席 F2:原 || true 吞錯照發「已產表」=假成功);
        # token 走 env 傳遞(code-r1 外家席:inline $() 展開含引號的 token 會炸 python 且被 || true 吞掉)
        local delta_rc=0
        (cd "$repo" && python3 governance/eval/refresh_labels.py delta \
          --out "$repo/governance/eval/retrieval-delta-$TODAY") >> "$LOGDIR/exam-$tag-$TODAY.log" 2>&1 || delta_rc=$?
        if [ "$delta_rc" -eq 0 ] && [ -f "$repo/governance/eval/retrieval-delta-$TODAY-sheet.md" ]; then
          log "考卷($tag)未標率超線,已產 delta 表 retrieval-delta-$TODAY-sheet.md 等人放行補標"
          MSG="📝 檢索考卷($tag)未標率超線($sig)——delta 表已備:governance/eval/retrieval-delta-$TODAY-sheet.md,補標流程見 Projects/標註刷新_計劃" \
          LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')  # \$REPO(工具鏈本體)刻意非 \$repo:line_notify 模組只存在於本體
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('labeling-refresh', os.environ['MSG'], None), t) if t else 'no-token')" || true
        else
          log "⚠ 考卷($tag)未標率超線但 delta 表產製失敗(rc=$delta_rc),不通報假成功;詳 $LOGDIR/exam-$tag-$TODAY.log"
        fi
      fi
    else
      log "⚠ 考卷($tag)執行失敗(fail-open 不阻斷),詳 $LOGDIR/exam-$tag-$TODAY.log"
    fi
  else
    log "考卷($tag):${age} 天前跑過,略"
  fi
}
# ── 情境探針週抽(工具鏈補強十件 #1,2026-08-22):每週抽 8 題看 Claude 會不會自己敲 lumos——
# 改了 CLAUDE.md 區塊或 skill 之後「規則有沒有退化」要有數字可看,不靠有人想起來重測。
# fail-open:探針失敗只記 log;有題沒過才 LINE。上限每週一次、8 題,避免變成燒 token 的機器。
# ★--max-turns 18 不是隨便給的★:absence 題組(缺席推論)天生要「查不到→換方法再查」,
# 實測要 11-12 步才給得出答案;預設 8 會在它開口之前截斷 → 三題全假紅(2026-08-22 實測)。
# 既有三個題庫 2-3 步就收,提高上限對它們無影響(未逐題複驗,見驗證節點誠實缺口)。
run_probe(){
  local hist="$REPO/governance/scenarios/history.jsonl"
  local week; week="$(date +%G-W%V)"
  if grep -q "\"seed\": \"$week\"" "$hist" 2>/dev/null; then
    log "情境探針:本週($week)已抽過,跳過"; return 0
  fi
  command -v claude >/dev/null 2>&1 || { log "情境探針:沒有 claude CLI,跳過"; return 0; }
  log "情境探針:本週($week)抽 8 題開跑"
  (cd "$REPO" && python3 scripts/scenario_probe.py \
      --scenarios governance/scenarios/commands.jsonl,governance/scenarios/paraphrase.jsonl,governance/scenarios/discipline.jsonl,governance/scenarios/absence.jsonl \
      --sample 8 --seed "$week" --timeout 600 --max-turns 18 --ts "$TODAY" --history "$hist" \
      --out "$REPO/governance/scenarios/run-$TODAY-weekly.json") > "$LOGDIR/probe-$TODAY.log" 2>&1 || true
  # ★|| true 必要★:probe 沒產出結果行時 grep rc1+pipefail+set -e=整支腳本死在這、
  # 連 gap 都還沒選(潛伏生產 bug,2026-08-26 沙箱測試觸發抓到)
  local line; line="$(grep -E '個情境 Claude 自己敲對了' "$LOGDIR/probe-$TODAY.log" | tail -1 || true)"
  log "情境探針結果:${line:-無結果(看 $LOGDIR/probe-$TODAY.log)}"
  local pp tt; pp="${line%%/*}"; tt="$(echo "$line" | sed -E 's#^[0-9]+/([0-9]+) .*#\1#')"
  if [ -n "$line" ] && [ "$pp" != "$tt" ]; then
    MSG="情境探針本週有題沒過:$line(沒過的題在 governance/scenarios/history.jsonl;改規則後用 scripts/scenario_probe.py --only <id> 重跑)" \
    LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('scenario-probe', os.environ['MSG'], None), t) if t else 'no-token')" || true
  fi
}

# ── 機制空轉週報(Issues/自足性審計提醒空轉四十六天 的出口,2026-08-22):同一道閘對同一篇連喊 ≥14 天
# 還沒人理,就是「機制有跑、沒人看」——每週跑一次 gov --nags,有就 LINE,不再靠順手 grep 發現。
run_nags(){ local repo="$1" tag="$2"
  local stamp="$repo/governance/nags-last-week.txt"; local week; week="$(date +%G-W%V)"
  [ "$(cat "$stamp" 2>/dev/null)" = "$week" ] && { log "空轉週報($tag):本週已跑"; return 0; }
  local out; out="$(cd "$repo" && python3 scripts/lumos gov --nags 14 --since 120 2>/dev/null || true)"
  echo "$week" > "$stamp"
  log "空轉週報($tag):$(echo "$out" | head -1)"
  if echo "$out" | grep -q "空轉清單"; then
    MSG="[$tag] 機制空轉週報:$(echo "$out" | head -1 | cut -c1-80);清單:$(echo "$out" | grep -E '^\s+[0-9]+ 天' | head -5 | sed -E 's/^ +//' | tr '\n' ';')" \
    LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('gov-nags', os.environ['MSG'], None), t) if t else 'no-token')" || true
  fi
}

run_exam "$REPO" toolchain
[ -d "$HOME/backend/LandmarkMember/governance/eval" ] && run_exam "$HOME/backend/LandmarkMember" landmark
run_probe
run_nags "$REPO" toolchain
[ -d "$HOME/backend/LandmarkMember/docs" ] && run_nags "$HOME/backend/LandmarkMember" landmark

# ── backlog 每日衰減([S2]:冪等按日差;先歸檔後刪+讀回自驗,archive 失敗 live 不動) ──
DECAY_OUT="$(cd "$REPO" && python3 -c "
import sys, json; sys.path.insert(0,'governance')
from autonomous_loop import backlog
r=backlog.daily_decay('$SCRIPT_DIR/backlog.jsonl','$SCRIPT_DIR/backlog-archive.jsonl',
                      '$SCRIPT_DIR/autonomous_loop/decay-state.json','$TODAY')
print(json.dumps(r))" 2>>"$LOGDIR/finalize-$TODAY.err" || echo '{\"status\":\"error\"}')"
log "backlog 衰減:$DECAY_OUT(ok=衰減完成/noop=今天已衰過/archive-fail=歸檔失敗 live 未動明天重試)"

SKIP_CAP=3; skip_n=0
while : ; do
GAP_JSON="$(cd "$REPO" && python3 -c "
import sys, json; sys.path.insert(0,'governance')
from autonomous_loop import gap_select
mode='pr' if '$MODE'=='--pr' else 'dryrun'
g=gap_select.select('$REPORT','$SCRIPT_DIR/backlog.jsonl','$PENDING',mode,'$TODAY','$SCRIPT_DIR/covered.jsonl')
print(json.dumps(g, ensure_ascii=False) if g else '')
")"
if [ -z "$GAP_JSON" ]; then
  # ★體檢 #2(2026-08-21)★:N=1 閘被 pending/ 裡的舊檔卡住 38 天,每天 rc=0 靜默結束——
  # 「排程有跑、什麼都沒做、回報成功」是最糟的失敗形態。pending 超過 3 天就喊人,不再默默退出。
  STALE="$(find "$PENDING" -maxdepth 1 -name '*.md' -mtime +3 2>/dev/null | head -5)"
  if [ -n "$STALE" ]; then
    log "⚠ pending/ 有超過 3 天未放行的檔,N=1 閘卡住自主 loop:$(echo "$STALE" | tr '\n' ' ')"
    MSG="自主 loop 被 pending/ 卡住 >3 天(放行或歸檔到 pending/archive/):$(echo "$STALE" | xargs -n1 basename | tr '\n' ' ')" \
    LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" \
    python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('autonomous-loop', os.environ['MSG'], None), t) if t else 'no-token')" || true
  else
    log "無可展開 gap(backlog 空或 N=1 閘),結束"
  fi
  exit 0
fi
log "選中 gap:$GAP_JSON"
GAP_DISPOSED=""; OUTCOME=""; COST_ARGS=""; ROUND_RECORDED=""   # code-r1 s1-f1:換 gap 全重置,成本不跨 gap 殘留
printf '%s\n' "$GAP_JSON" > "$INFLIGHT.tmp" && mv "$INFLIGHT.tmp" "$INFLIGHT"   # 斷電保險

# 錨點完整性:驗證器被污染時跑出的「收斂/綠」全是假訊號,寧停。
# loop 入口比 pre-push 嚴:missing baseline 亦硬擋(無人看顧場景無人眼兜底)。
if [ ! -f "$REPO/governance/anchor-baseline.json" ] || ! (cd "$REPO" && python3 scripts/lumos anchor verify); then
  log "錨點完整性失敗(anchor verify 不過或 baseline 缺失),loop 拒跑;gap 由收尾放回 backlog"
  OUTCOME="pipeline_fail:anchor_fail"
  MSG="⚠ 錨點完整性失敗,自主 loop 拒跑(anchor verify)" LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('anchor-integrity', os.environ['MSG'], None), t) if t else 'no-token')" || true
  exit 1
fi

# ── tier 分級(risk-tiered-review):gap 文本 assess → 注入 NEED/TIER/MAXR_EFF ──
read -r TIER NEED < <(echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import difficulty
g=json.load(sys.stdin)
a=difficulty.assess((g.get('weakness','') or '')+'\n'+(g.get('suggestion','') or ''))
p=difficulty.params(a['tier'])
print(a['tier'], p['need'])")
MAXR_EFF="$MAXR"
[ "$TIER" = "high" ] && MAXR_EFF="$(( MAXR > 8 ? MAXR : 8 ))"
log "tier 分級:$TIER(need=$NEED, maxr=$MAXR_EFF)"

PROMPT_FILE="$(mktemp)"
sed -e "s#__SCRATCH__#$SCRATCH#g" -e "s#__DATE__#$TODAY#g" -e "s#__MAXR__#$MAXR_EFF#g" \
    -e "s#__NEED__#$NEED#g" -e "s#__TIER__#$TIER#g" \
    "$SCRIPT_DIR/autonomous_loop/orchestrator-prompt.md" > "$PROMPT_FILE"
printf '\n\n## 要處理的 gap\n%s\n模式:%s\n' "$GAP_JSON" "$MODE" >> "$PROMPT_FILE"
export ANTHROPIC_API_KEY=""
export CLAUDE_CODE_OAUTH_TOKEN="$(cat "$HOME/.config/ai-daily/claude_oauth_token" 2>/dev/null)"
ORCH_OUT="$LOGDIR/orchestrator-$TODAY.json"
log "派 orchestrator(claude -p,最多 $MAXR_EFF 輪)..."
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
# 解析不到時把死因帶出來(2026-08-24 實踩:API 529 過載殺掉整輪,log 只寫 NO_JSON,死因要人工解剖 json 才看得到)
print(json.dumps(r, ensure_ascii=False) if r else 'NO_JSON:' + ('is_error=' + str(o.get('is_error')) + ' | ' + str(o.get('result',''))[-160:]).replace(chr(10), ' '))
")"
log "orchestrator 回傳:$PARSED"

# ── 成本落帳(★填既有欄,不建新機制★)──────────────────────────────────────────
# `claude -p --output-format json` 的頂層本來就吐 total_cost_usd / duration_ms /
# num_turns / usage,一直沒人接;canary 帳的 --tokens / --wallclock-min 兩個欄也早就
# 在、零筆填過。這裡把兩邊接起來:抽出來 log 一行 + 記進既有欄。
# ★fail-open★——抽不到就只 log 一句,絕不影響 loop(與 run_probe / run_nags 同款)。
COST_OUT="$(cd "$REPO" && python3 -c "
import json, sys
sys.path.insert(0, 'governance')
from autonomous_loop import orchestrator_result as orr
try:
    o = json.load(open('$ORCH_OUT'))
except Exception:
    sys.exit(0)
c = orr.extract_cost(o)
if not c:
    sys.exit(0)
print('US\$%s | %s 分鐘 | %s 輪 | %s tokens(另快取讀 %s)' % (
    c['usd'], c['wallclock_min'], c['turns'], c['tokens'], c['cache_read']))
print(' '.join(orr.cost_cli_args(c)))
" 2>/dev/null)" || COST_OUT=""
if [ -n "$COST_OUT" ]; then
  log "本輪成本:$(echo "$COST_OUT" | head -1)"
  COST_ARGS="$(echo "$COST_OUT" | tail -1)"
  # record 移到 trap 收尾統一落帳([S3]:成本抽取與結局是獨立失敗維度,不在這裡綁死;
  # 「回報成功≠已落盤」的 rc 判斷也一併在 trap 裡做)
else
  log "本輪成本:沒抽到——orchestrator 輸出裡沒有成本欄,或形狀變了(看 $ORCH_OUT)"
fi

case "$PARSED" in PARSE_FAIL*|NO_JSON*|"")
  OUTCOME="pipeline_fail:$(echo "$PARSED" | python3 -c "
import sys; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import orchestrator_result
print(orchestrator_result.classify_death(sys.stdin.read()))" 2>/dev/null || echo parse_fail)"
  log "orchestrator 輸出無法解析,中止——死因=$OUTCOME(收尾會把 gap 放回 backlog 並落結局帳;log $ORCH_OUT)"
  exit 1;; esac

get(){ echo "$PARSED" | python3 -c "import json,sys;print(json.load(sys.stdin).get('$1',''))"; }
SKIPPED="$(get skipped)"; CONVERGED="$(get converged)"; TOPIC="$(get topic)"; SPEC="$(get spec_path)"
CROSS_VERDICT="$(get cross_verdict)"; CROSS_WORST="$(get cross_worst)"; CROSS_SUMMARY="$(get cross_summary)"
TIER_RESULT="$(get tier)"
CROSS_SUMMARY="${CROSS_SUMMARY//$'\n'/ }"   # F3 防破版:換行→空格

if [ "$SKIPPED" = "True" ]; then
  skip_n=$((skip_n+1))
  # skip 迭代自己真跑過 orchestrator、真花了錢——當場落自己的帳,不等 trap
  # (code-r1 s1-f1/s3-f1:trap 只落最後一筆,早期迭代的花費會張冠李戴或直接蒸發)
  OUTCOME="skipped"
  # shellcheck disable=SC2086
  if (cd "$REPO" && python3 scripts/lumos canary record none --loop "auto-$TODAY" \
        --auditor orchestrator --outcome skipped $COST_ARGS \
        --note "自主迴圈結局帳(skip 迭代當場落;成本欄=claude -p 實際回傳,非估算)") \
        >>"$LOGDIR/cost-$TODAY.log" 2>&1; then
    ROUND_RECORDED=1
  else
    log "結局帳:skip 迭代 record 失敗——這筆花費帳上會缺(詳 $LOGDIR/cost-$TODAY.log)"
  fi
  # covered 寫入成功才算有去向;失敗就留給 trap 放回(code-r1 ext-f1:不准寫失敗還標已處置)
  if echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
w=json.load(sys.stdin).get('weakness','')
if w: gap_select.mark_covered('$SCRIPT_DIR/covered.jsonl', w)
" 2>>"$LOGDIR/finalize-$TODAY.err"; then
    GAP_DISPOSED=1
    rm -f "$INFLIGHT" 2>/dev/null || true
  else
    # continue 會把 $GAP_JSON 蓋掉,trap 的安全網接不到這筆(r2 d-f1 實跑重現:gap+已燒成本
    # 三檔皆無)——所以當場放回,放回也失敗就 exit 保住變數讓 trap/in-flight 接手
    RQF="$(echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
g=json.load(sys.stdin)
print(gap_select.requeue_pipeline_fail('$SCRIPT_DIR/backlog.jsonl', g, '$SCRIPT_DIR/covered.jsonl'))
" 2>>"$LOGDIR/finalize-$TODAY.err" || echo '?')"
    case "$RQF" in
      requeued|covered)
        GAP_DISPOSED=1; rm -f "$INFLIGHT" 2>/dev/null || true
        log "⚠ covered 寫入失敗——gap 已當場放回 backlog($RQF),不冒充已處置";;
      *)
        log "⚠ covered 寫入失敗且當場放回也失敗($RQF)——中止本輪,收尾與 in-flight 標記接手"
        exit 1;;
    esac
  fi
  log "gap 已被既有 spec 覆蓋,skip(reason: $(get reason));已記入 covered、永久不再選。循環選下一個($skip_n/$SKIP_CAP)。"
  [ "$skip_n" -ge "$SKIP_CAP" ] && { log "連 skip $SKIP_CAP 個已覆蓋 gap,今天結束(剩餘留 backlog 明天再選)。"; exit 0; }
  continue
fi
break
done

RESIDUAL='["跨家族複核已加(qwen3-max 放行前複核 opus 設計、補同門盲點);但 degrade 時退回單一 opus、qwen 也是 AI、verdict 判定仍在 orchestrator(prompt 層自律)","severity 由 judge 評(已斷 orchestrator 自填)但 judge 也是 AI、且同輪判 canary+severity=集中化","type d canary 沒測(限 a/b/c)","自動 brainstorm 無人回澄清;AI 自選 gap=自己決定改自己方向(自我強化偏誤)","唯一外部錨點是你 review 這個 PR"]'
if [ "$CONVERGED" != "True" ]; then
  if [ "$CROSS_VERDICT" = "disputed" ]; then
    OUTCOME="unconverged:disputed"
    MSG="⚠ 跨家族否決(qwen 持續異議):$CROSS_SUMMARY"; log "未收斂(跨家族否決 disputed),不放行:$CROSS_SUMMARY"
  elif [ "$CROSS_VERDICT" = "degraded" ] && [ "$TIER" = "high" ]; then
    OUTCOME="unconverged:degraded-high"
    MSG="⚠ 高風險級複核缺席(degraded)、fail-closed 擋下:$CROSS_SUMMARY"; log "未收斂(高風險級複核 degraded fail-closed),不放行:$CROSS_SUMMARY"
  else
    OUTCOME="unconverged:cap"
    MSG="⚠ 今日 spec 未收斂、未放行(撞 cap)"; log "未收斂(converged=$CONVERGED),不放行,scratch 不入庫。"
  fi
  MSG="$MSG" LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('$TOPIC',os.environ['MSG'],None),t) if t else 'no-token')" || true
  # 副作用 A:未收斂 gap 回 backlog 降分 + 累計 unconverged;達 3 次 → covered(放棄自動、留人),不立即消失
  RQ="$(echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
g=json.load(sys.stdin)
print(gap_select.requeue_unconverged('$SCRIPT_DIR/backlog.jsonl', g, '$SCRIPT_DIR/covered.jsonl'))
" 2>/dev/null || echo '?')"
  case "$RQ" in requeued|covered) GAP_DISPOSED=1;; *) log "⚠ requeue 回報異常($RQ)——gap 改由收尾放回,不冒充已處置";; esac
  log "未收斂 gap 處置:$RQ(回 backlog 降分重試 / 累計達 3 次 covered)"
  exit 0
fi

[ -n "$CROSS_VERDICT" ] && log "跨家族複核:$CROSS_VERDICT($CROSS_WORST)— $CROSS_SUMMARY"

# ── tier 收檔守衛:不信自報 converged——wrapper 自算 tier、以其 need 重驗 gate ──
if [ -z "$SPEC" ] || [ ! -f "$SPEC" ]; then
  OUTCOME="tier-blocked:spec"
  log "tier 守衛擋下:converged=True 但 spec_path 空或不存在($SPEC)"
  MSG="⚠ tier 守衛擋下:自報收斂但 spec_path 無效" LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('$TOPIC',os.environ['MSG'],None),t) if t else 'no-token')" || true
  RQ="$(echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
g=json.load(sys.stdin)
print(gap_select.requeue_unconverged('$SCRIPT_DIR/backlog.jsonl', g, '$SCRIPT_DIR/covered.jsonl'))
" 2>/dev/null || echo '?')"
  case "$RQ" in requeued|covered) GAP_DISPOSED=1;; *) log "⚠ requeue 回報異常($RQ)——gap 改由收尾放回";; esac
  log "未收斂 gap 處置:$RQ(tier 守衛/spec_path)"
  exit 0
fi
REPORT_MD="$(cd "$REPO" && python3 -c "
import sys, json; sys.path.insert(0,'governance')
from autonomous_loop import confidence_report, difficulty
a=difficulty.assess_spec(open('$SPEC').read())
print(confidence_report.build_report('$SCRATCH/.canary-log.jsonl','$TOPIC', json.loads('''$RESIDUAL'''),
      tier=a['tier'], hits=a['hits'], reported_tier='$TIER_RESULT'))
")"
TIER_FINAL="$(cd "$REPO" && python3 -c "
import sys; sys.path.insert(0,'governance')
from autonomous_loop import difficulty
print(difficulty.assess_spec(open('$SPEC').read())['tier'])")"
NEED_FINAL="$NEED"
if [ "$TIER_FINAL" = "high" ] && [ "$NEED_FINAL" -lt 3 ]; then NEED_FINAL=3; fi
if ! (cd "$REPO" && python3 scripts/lumos --vault "$SCRATCH/kg" loop status "$TOPIC" --need "$NEED_FINAL" --gate --spec "$SPEC" --repo "$REPO"); then
  OUTCOME="tier-blocked:gate"
  log "tier 守衛擋下:自報收斂但 gate 重驗不過(自算 tier=$TIER_FINAL, need=$NEED_FINAL)"
  MSG="⚠ tier 守衛擋下:自報收斂但 gate 重驗不過(tier=$TIER_FINAL)" LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('$TOPIC',os.environ['MSG'],None),t) if t else 'no-token')" || true
  RQ="$(echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
g=json.load(sys.stdin)
print(gap_select.requeue_unconverged('$SCRIPT_DIR/backlog.jsonl', g, '$SCRIPT_DIR/covered.jsonl'))
" 2>/dev/null || echo '?')"
  case "$RQ" in requeued|covered) GAP_DISPOSED=1;; *) log "⚠ requeue 回報異常($RQ)——gap 改由收尾放回";; esac
  log "未收斂 gap 處置:$RQ(tier 守衛)"
  exit 0
fi
if [ "$TIER_FINAL" = "high" ] && [ "$CROSS_VERDICT" != "endorsed" ]; then
  OUTCOME="tier-blocked:cross"
  log "tier 守衛擋下:high 級 cross_verdict=$CROSS_VERDICT 非乾淨 endorsed,不放行"
  MSG="⚠ tier 守衛擋下:high 級複核非乾淨 endorsed(=$CROSS_VERDICT)" LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('$TOPIC',os.environ['MSG'],None),t) if t else 'no-token')" || true
  RQ="$(echo "$GAP_JSON" | python3 -c "
import sys, json; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import gap_select
g=json.load(sys.stdin)
print(gap_select.requeue_unconverged('$SCRIPT_DIR/backlog.jsonl', g, '$SCRIPT_DIR/covered.jsonl'))
" 2>/dev/null || echo '?')"
  case "$RQ" in requeued|covered) GAP_DISPOSED=1;; *) log "⚠ requeue 回報異常($RQ)——gap 改由收尾放回";; esac
  log "未收斂 gap 處置:$RQ(tier 守衛/cross)"
  exit 0
fi

if [ "$MODE" = "--dry-run" ]; then
  if cp "$SPEC" "$PENDING/" 2>/dev/null; then
    OUTCOME="converged"   # 「備好待放行」=converged 且 pending 寫入成功([S4] Z 的定義)
    GAP_DISPOSED=1        # spec 真的備好了,gap 才算消化(code-r1 ext-f2:寫失敗不冒充已處置)
  else
    OUTCOME="pipeline_fail:pending_write"
    log "⚠ 收斂但 pending 寫入失敗($SPEC → $PENDING/)——spec 沒備好;gap 由收尾放回 backlog"
  fi
  printf '%s\n' "$REPORT_MD" > "$PENDING/$(basename "$SPEC" .md)-confidence.md" 2>/dev/null || true
  log "dry-run:收斂!spec + 可信度報告寫入 $PENDING/(repo 未動)"
  LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('$TOPIC','(dry-run)收斂[跨家族:$CROSS_VERDICT]、待你看 pending/',None),t) if t else 'no-token')" || true
else
  cd "$REPO"; BR="auto/spec-$TOPIC-$TODAY"
  cp "$SPEC" "docs/design/$(basename "$SPEC")"
  git checkout -b "$BR"; git add "docs/design/$(basename "$SPEC")"
  git commit -m "auto-spec: $TOPIC（自主迭代 loop 收斂產出，待人放行）"
  echo "$REPORT_MD" | gh pr create --title "auto-spec: $TOPIC" --body-file - || true
  OUTCOME="converged"; GAP_DISPOSED=1
  log "已開 PR(branch $BR)"
fi
log "完成。"
