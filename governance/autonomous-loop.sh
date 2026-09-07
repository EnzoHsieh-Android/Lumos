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
# 鎖裡放 PID;持鎖行程已死視為殘鎖接管。SIGKILL 殘鎖靠這條自癒。
#
# ★2026-09-07 補三個洞,三個都實測過★(全 repo 審視 #18 在抄這段時被五席挖出來,
#  當時只修了抄過去那一份,這裡是回頭把來源也修掉;守衛 t_daily_wrapper_lock_matches_source
#  比的是四個行為還在不在、不比逐字,所以兩邊寫法不必一樣):
#
#  ①★雙開★:「rm 掉舊鎖再 mkdir」擋不住這個排列——
#    A 刪 → A 建(成功)→ B 刪(把 A 剛建好的砍掉)→ B 建(成功),兩邊都以為自己拿到鎖。
#    ★set -e 幫不上忙★:兩個 mkdir 都成功,沒有非零可攔。實測這一段的舊邏輯
#    30 輪 × 8 行程有 1 輪多人同時拿到(比 daily-governance 的 19/30 低,是因為
#    set -e 攔掉了「輸的那個 mkdir 失敗」那半,但沒攔掉這條)。
#    改法:接管整段走一把「接管權」小鎖,進去後再確認殘鎖還是原來那一把。
#
#  ②★pid 被作業系統回收給無關的活行程★ → kill -0 說「活著」→ 這支永遠讓行、
#    自主迴圈永久停擺而且完全沒有訊息。實測:10 天前的殘鎖 + 一個活著的無關行程,
#    舊邏輯印「另一份正在跑」直接退出。改法:再問一次「那個 pid 的指令像不像我們這支」。
#    ★問不出來就保守當成活著★:誤判成死掉會雙開,比多讓一次行嚴重得多。
#
#  ③★pid 檔內容不是數字★(寫到一半被砍)→ 兩個分支都不成立 → 直接掉到「接管」,
#    連 0 秒齡的新鎖都搶。實測:pid 寫 garbage、鎖 0 秒齡,舊邏輯當場接管。
#    改法:非數字一律當成「pid 讀不到」,走鎖齡兜底那條。
# ★同源:daily-governance.sh 的取鎖段★。兩邊是同一把鎖的兩份拷貝,
# 血緣是雙向的——#18 那批先在 daily-governance.sh 上被五席修好,code-batch19 這批
# 再把修法搬回來,而 batch19 自己的三席又同時修了兩邊。任何一邊改了另一邊要跟著改;
# 守衛 t_daily_wrapper_lock_matches_source 會比對兩份的關鍵行為(雙向都查)。
LOCKDIR="$SCRIPT_DIR/.autonomous-loop.lock"
lock_secs_since() {   # $1=路徑;印出它幾秒前被動過;問不出來印空字串
  python3 -c 'import os,sys,time;print(int(time.time()-os.path.getmtime(sys.argv[1])))' "$1" 2>/dev/null || echo ''
}
lock_proc_start() {   # $1=pid;印出那個行程的啟動時刻;pid 不存在或問不出來印空字串
  ps -p "$1" -o lstart= 2>/dev/null | sed 's/^ *//;s/ *$//' || echo ''
}
lock_holder_alive() {   # $1=pid;0=就是當初建這把鎖的那個行程 1=確定不是 2=問不出來
  # ★不再用「指令列長得像不像我們」認人★(2026-09-07 code-batch19 通才席 blocker)。
  # 那個做法它實跑打穿了:持鎖者只要換個名字啟動(符號連結、包一層 wrapper、
  # 未來重構成 bin/run-with-lock.sh …),ps 的指令列裡就沒有我們的名字,
  # 活著的持鎖者會被判成死的,鎖當場被搶走——★它量到兩個行程同時跑起來★,
  # 而那正是這把鎖存在的唯一理由。改名字錨也只是把洞縮小,沒有關掉。
  #
  # 改用硬身分:pid 加上「那個行程的啟動時刻」。取鎖時把啟動時刻一起寫進鎖裡,
  # 之後拿 pid 去問系統要同一個值來比。pid 會被回收、名字會變,
  # 但「同一個 pid 而且啟動時刻一模一樣」只可能是同一個行程。
  # 舊格式的鎖(只有 pid 沒有啟動時刻)問不出來 → 回 2 → 呼叫端走鎖齡兜底。
  kill -0 "$1" 2>/dev/null || return 1
  local want got
  want="$(cat "$LOCKDIR/start" 2>/dev/null || echo '')"
  [ -z "$want" ] && return 2
  got="$(lock_proc_start "$1")"
  [ -z "$got" ] && return 2
  [ "$want" = "$got" ] && return 0
  return 1
}
lock_write_pid() {   # 兩個檔都走暫存→改名:這個 repo 的教訓是共用檔一律原子寫入
  # ★啟動時刻要先寫★:這樣「pid 檔存在」就保證「啟動時刻也在」,
  # 讀的人不會拿到只有一半的身分。
  local st; st="$(lock_proc_start $$)"
  [ -z "$st" ] && return 1
  local t="$LOCKDIR/start.tmp"
  echo "$st" > "$t" 2>/dev/null && mv -f "$t" "$LOCKDIR/start" 2>/dev/null || return 1
  t="$LOCKDIR/pid.tmp"
  echo $$ > "$t" 2>/dev/null && mv -f "$t" "$LOCKDIR/pid" 2>/dev/null
}
take_lock() {   # 0=拿到  1=別人在跑,正常讓行  2=鎖壞了,不正常
  # ★寫 pid 失敗要當成沒拿到★(r1 外家席 f1):這個函式被寫成 `take_lock || {...}`
  # 的左手邊,而 bash 在那個位置會把整個函式體的 set -e 關掉——
  # 所以「寫 pid 失敗就自動中止」是假的,失敗會被吞掉然後照樣回報成功。
  # 後果是我們在動 backlog,鎖裡卻沒有 pid;60 分鐘後別人用鎖齡兜底接管 → 雙開。
  if mkdir "$LOCKDIR" 2>/dev/null; then
    lock_write_pid && return 0
    rmdir "$LOCKDIR" 2>/dev/null || true
    echo "[$(date '+%F %T')] ★鎖建起來了但 pid 寫不進去($LOCKDIR)★——這次沒跑,要人來看" >&2
    return 2
  fi
  local oldpid; oldpid="$(cat "$LOCKDIR/pid" 2>/dev/null || echo '')"
  case "$oldpid" in ''|*[!0-9]*) oldpid="" ;; esac   # 見③:壞內容等同讀不到
  if [ -n "$oldpid" ]; then
    # ★不要寫成「呼叫;讀 $?」★:那個寫法只有在 take_lock 本身被當成 `||` 左手邊
    # 呼叫時才安全(bash 那時才會關掉 errexit)。誰哪天改成直接呼叫 take_lock,
    # 這裡就會在「持鎖者已死」這條完全正常的路上整支中止(通才席查證點 1)。
    local hv=0; lock_holder_alive "$oldpid" || hv=$?
    if [ "$hv" -eq 0 ]; then
      echo "[$(date '+%F %T')] 另一份 autonomous-loop 正在跑(pid $oldpid),本次退出——不搶寫 backlog"
      return 1
    fi
  fi
  if [ "$oldpid" = "" ] || [ "${hv:-2}" -eq 2 ]; then
    # 身分問不出來(舊格式的鎖、ps 讀不到)也走這條,不是無條件讓行——
    # 無條件讓行那條路上沒有兜底,一旦誤判就是永久停擺而且完全沒有訊息。
    # ★空 pid ≠ 殘鎖★(r2 d-f2 TOCTOU):對方可能剛 mkdir 成功、還沒來得及寫 pid。
    # 鎖齡用 python 算(stat -f 是 BSD 專屬,Linux 上整句壞掉;r3 e-f1)。
    # ★量不出=讓行★:寧可少跑一天,不搶對方剛拿到的鎖。
    local age; age="$(lock_secs_since "$LOCKDIR")"
    if [ -z "$age" ] || [ "$age" -lt 3600 ]; then
      echo "[$(date '+%F %T')] 另一份 autonomous-loop 疑似剛起步(鎖存在 ${age:-量不出}s、身分驗不出),本次退出讓行"
      return 1
    fi
  fi
  echo "[$(date '+%F %T')] 發現殘鎖(pid ${oldpid:-讀不到} 不是這支、或鎖齡過老),接管"
  # 見①:接管整段要互斥,而且進去之後要再確認一次
  local steal="$LOCKDIR.steal"
  if ! mkdir "$steal" 2>/dev/null; then
    local sage; sage="$(lock_secs_since "$steal")"
    if [ -z "$sage" ] || [ "$sage" -lt 60 ]; then
      echo "[$(date '+%F %T')] 另一個接管者正在處理,本次退出"; return 1
    fi
    # ★破接管權也要原子★(r1 外家席 f2):原本寫成「rm 掉再 mkdir」,
    # 那正是這一批在修的同一個形態——兩個人可以各刪一次各建一次,雙雙進到下面那段,
    # 然後各自在結尾無條件刪掉接管權,把還在裡面的第三個人曝出去。
    # 改用 mv:同一個目錄只有一個人搬得走,搬不走的就是輸的那個,直接讓行。
    # ★誠實記:這一改沒有行為層的守衛★——真正的互斥在下一層(`mv "$LOCKDIR"` 同一個來源
    # 只有一個人搬得走),所以就算兩個人都以為自己拿到接管權,也只有一個接管得成。
    # 通才席跑 15 輪 × 8 行程量到 0/15;我寫的「量得到」的測試量錯了(把合法的接續
    # 當成同時),CI 上翻紅才發現。留著的理由是「同一個形態不要留第二份」,
    # 守衛是結構層的:t_daily_wrapper_lock_matches_source 釘住兩支都要用 mv,改回去會紅。
    local sdead="$steal.dead.$$"
    mv "$steal" "$sdead" 2>/dev/null || { echo "[$(date '+%F %T')] 接管權剛被別人處理掉,本次退出"; return 1; }
    rm -rf "$sdead" 2>/dev/null || true
    rm -rf "$steal".dead.* 2>/dev/null || true
    mkdir "$steal" 2>/dev/null || { echo "[$(date '+%F %T')] 接管失敗(接管權搶不到),本次退出"; return 1; }
  fi
  local rc=1
  # ★進來之後再確認一次殘鎖還是我看到的那一把★。它守的窗口是「B 讀到舊 pid 決定接管、
  # 卡在接管權外面,A 在這期間完成接管並釋放接管權,B 才進去」——沒有這一句,
  # B 會把 A 那把全新的鎖搬走,兩邊同時跑。
  # ★這句話我原本寫成「沒辦法從外部穩定構造,所以沒有守衛」,那是錯的★(r1 外家席 f6 指出):
  # 只要在 B 印出「發現殘鎖」之後把 B 停住(SIGSTOP)、替它把鎖換成 A 的新鎖、再放行,
  # 順序就是穩定的。守衛已補在 test_autonomous_loop.py 的 takeover_rechecks_pid 那支。
  local nowpid; nowpid="$(cat "$LOCKDIR/pid" 2>/dev/null || echo '')"
  case "$nowpid" in ''|*[!0-9]*) nowpid="" ;; esac
  if [ "$nowpid" != "$oldpid" ]; then
    echo "[$(date '+%F %T')] 進來後發現鎖已經換人(pid ${nowpid:-讀不到}),不接管,本次退出"
  else
    local dead="$LOCKDIR.dead.$$"
    if ! mv "$LOCKDIR" "$dead" 2>/dev/null; then
      if [ ! -w "$SCRIPT_DIR" ]; then
        echo "[$(date '+%F %T')] ★鎖搬不走而且 $SCRIPT_DIR 寫不進去★——這次沒跑,要人來看" >&2
        rc=2
      else
        echo "[$(date '+%F %T')] 接管失敗(鎖剛被釋放),本次退出"
      fi
    else
      rm -rf "$dead" 2>/dev/null || true
      rm -rf "$LOCKDIR".dead.* 2>/dev/null || true
      if ! mkdir "$LOCKDIR" 2>/dev/null; then
        echo "[$(date '+%F %T')] ★接管後鎖建不起來($LOCKDIR)★——這次沒跑,要人來看" >&2
        rc=2
      elif ! lock_write_pid; then
        rmdir "$LOCKDIR" 2>/dev/null || true
        echo "[$(date '+%F %T')] ★接管後 pid 寫不進去($LOCKDIR)★——這次沒跑,要人來看" >&2
        rc=2
      else
        rc=0
      fi
    fi
  fi
  rm -rf "$steal" 2>/dev/null || true
  return "$rc"
}

release_lock() {
  # ★只清自己的那把★:收尾原本是無條件 rm——如果這支跑到一半被別人★合法接管★走了
  # (殘鎖判定成立時真的會發生),那一下刪的是別人正在用的鎖。
  # 判準是鎖裡的 pid 是不是自己,不另外用旗標:旗標只知道「我曾經拿到過」,
  # 而且「拿到鎖」跟「設旗標」之間有一個收不到訊號的窗口(r1 外家席 f3)。
  [ "$(cat "$LOCKDIR/pid" 2>/dev/null || echo '')" = "$$" ] || return 0
  # ★先搬走再確認★(r1 外家席 f5):讀 pid 跟刪目錄中間還有一段,
  # 那段時間裡鎖可能已經合法換人,無條件 rm 刪掉的是新持有者正在用的鎖。
  # mv 是原子的:搬得走才輪到我處置,搬完再看一次裡面的 pid 是不是自己。
  local held="$LOCKDIR.rel.$$"
  mv "$LOCKDIR" "$held" 2>/dev/null || return 0
  if [ "$(cat "$held/pid" 2>/dev/null || echo '')" = "$$" ]; then
    rm -rf "$held" 2>/dev/null || true
  else
    # 搬到的是別人的:原樣還回去。還不回去(對方已經另建一把)就留著不刪
    # ——留一坨看得見的證據,比默默刪掉別人的鎖好。
    mv "$held" "$LOCKDIR" 2>/dev/null || \
      echo "[$(date '+%F %T')] ★收尾搬到的不是自己的鎖、又還不回去★:留在 $held,要人來看" >&2
  fi
}
# ── 收尾器:★整支只有這一個 trap,而且裝在取鎖之前★
# 這是照 daily-governance.sh 註解⑤的既有做法寫的(那支也是單一 trap 裝在取鎖前,
# 靠收尾器自己確認鎖裡的 pid 是不是自己)。r1 架構對齊席 F1 指出這批原本改成
# 「臨時 trap + 全域旗標 + 中途換 trap」,那是這個 repo 原本沒有的第二種做法。
# 定義搬到取鎖之前之所以安全:收尾器開頭就用 GAP_JSON 空不空判「還沒選中題目」,
# 空的話只清鎖就回去,底下那些要跑到後面才有值的變數(LOGDIR/TODAY/REPO…)碰都不會碰到。
# 所以下面那排記帳變數必須跟著搬上來(set -u:沒宣告就讀會當場中止)。
#
# ── 收尾器做的四件事(auto-loop-repair-v2 [S1]+[S3]+[S4]):trap EXIT 統一做四件事——
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
  if [ -z "$GAP_JSON" ]; then release_lock; return 0; fi   # 還沒選中 gap 的早退(無日報/無 gap):無輪無帳
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
  release_lock
}
# ★取鎖與收尾之間不能有裸奔的窗口★:取鎖成功到「裝好收尾」之間如果收到 TERM/HUP,
# 鎖就會留到 60 分鐘後才自癒(r1 架構對齊席 F1 + 外家席 f3)。
# 收尾器自己會驗鎖裡的 pid 是不是自己,沒拿到鎖時呼叫它是空操作,
# 所以 trap 可以無條件裝在取鎖之前,不需要旗標,也不需要中途換 trap。
trap finalize EXIT
take_lock || { _lk=$?; [ "$_lk" -eq 2 ] && exit 3; exit 0; }

TODAY="$(date +%F)"
REPORT="$SCRIPT_DIR/reports/governance-$TODAY.json"
PENDING="$SCRIPT_DIR/pending";  mkdir -p "$PENDING"
LOGDIR="$SCRIPT_DIR/logs";      mkdir -p "$LOGDIR"
SCRATCH="$(mktemp -d "/tmp/auto-loop-$TODAY.XXXXXX")"; mkdir -p "$SCRATCH/kg" "$SCRATCH/spec"   # mktemp:防可預測路徑搶佔(外審 minor)
log(){ echo "[$(date '+%F %T')] $*"; }


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
  # ★全新機器第一天不抽★(2026-09-06 代碼審 r1 外家席):這支會跑 8 題 `claude -p`,是整支腳本
  # 唯一真的燒模型配額的東西。以前它被「暫停派工」順帶關掉,現在 wrapper 無條件呼叫,沒有任何
  # 歷史的機器裝好當天就會立刻抽 8 題——那不是使用者要的。第一次遇到就先蓋本週印記、下週才開抽。
  if [ ! -s "$hist" ]; then
    mkdir -p "$(dirname "$hist")" 2>/dev/null || true   # 全新機器連 scenarios/ 夾都還沒有
    printf '{"seed": "%s", "note": "首次執行:先不抽,下週開始"}\n' "$week" >> "$hist" 2>/dev/null || true
    log "情境探針:這台機器沒有任何歷史(第一次跑)——先不抽,免得裝好當天就燒配額;下週開始"
    return 0
  fi
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

# ── 改制回測 [S4] 週跑(2026-08-26):補漏凍結+新凍必跑+存量輪替抽 5 包,預算 300s;
# 紅(邏輯漂移/帳被動/凍結檔被動)與 golden 過期分開喊;fail-open 不擋主流程。
run_replay(){
  local stamp="$REPO/governance/replay/.weekly-stamp"; local week; week="$(date +%G-W%V)"
  [ "$(cat "$stamp" 2>/dev/null)" = "$week" ] && { log "回放週跑:本週已跑"; return 0; }
  mkdir -p "$REPO/governance/replay"
  # LINE 文字在 python 端組好單行、shell 只抽前綴——與 run_exam/run_nags 的 bash 組裝不同,
  # 是刻意的新慣例:通知文字進得了單元測試網(TestReplayWeekly 蓋 build_msg);後續新週期任務照此。(cb3 arch-f1)
  local out; out="$(cd "$REPO" && python3 governance/autonomous_loop/replay_weekly.py "$REPO" 2>>"$LOGDIR/replay-$TODAY.err" || true)"
  if ! echo "$out" | grep -q "^{"; then
    # cb3 finder-f4:模組炸掉(import/語法/未捕捉例外)時不蓋週戳——蓋了=整週靜默停擺;明天重試
    log "回放週跑:模組失敗無輸出,本週不蓋章明天重試(錯誤在 replay-$TODAY.err)"
    return 0
  fi
  echo "$week" > "$stamp"
  # 2026-09-05 第二輪審視 d4:原本 cut -c1-160 剛好把 red/stale/errors 切掉,翻案了也看不見。
  # 照本檔慣例(python 端組文字、shell 只抽前綴):replay_weekly.py 印 LOG: 行,這裡逐行 log;原始 JSON 全文另存一行。
  echo "$out" | sed -n 's/^LOG://p' | while IFS= read -r _l; do log "回放週跑:$_l"; done
  log "回放週跑原始:$(echo "$out" | head -1)"
  local msg; msg="$(echo "$out" | sed -n 's/^MSG://p' | head -1)"
  if [ -n "$msg" ]; then
    MSG="$msg" LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)" python3 -c "
import sys, os; sys.path.insert(0,'$REPO/governance')
from autonomous_loop import line_notify
t=os.environ.get('LINE_TOKEN','')
print('LINE', line_notify.send(line_notify.build_message('regime-replay', os.environ['MSG'], None), t) if t else 'no-token')" || true
  fi
}

run_exam "$REPO" toolchain
[ -d "$HOME/backend/LandmarkMember/governance/eval" ] && run_exam "$HOME/backend/LandmarkMember" landmark
run_probe
run_nags "$REPO" toolchain
run_replay
[ -d "$HOME/backend/LandmarkMember/docs" ] && run_nags "$HOME/backend/LandmarkMember" landmark

# ── backlog 每日衰減([S2]:冪等按日差;先歸檔後刪+讀回自驗,archive 失敗 live 不動) ──
DECAY_OUT="$(cd "$REPO" && python3 -c "
import sys, json; sys.path.insert(0,'governance')
from autonomous_loop import backlog
r=backlog.daily_decay('$SCRIPT_DIR/backlog.jsonl','$SCRIPT_DIR/backlog-archive.jsonl',
                      '$SCRIPT_DIR/autonomous_loop/decay-state.json','$TODAY')
print(json.dumps(r))" 2>>"$LOGDIR/finalize-$TODAY.err" || echo '{\"status\":\"error\"}')"
log "backlog 衰減:$DECAY_OUT(ok=衰減完成/noop=今天已衰過/archive-fail=歸檔失敗 live 未動明天重試)"

# ★派工段的暫停開關放在這裡,不在 wrapper★(2026-09-06 全 repo 審視 #4)
# 為什麼:2026-09-05 決定「暫停派工」時,開關寫在 daily-governance.sh 裡包住整支腳本,結果
# 上面那五段便宜的週期觀測(檢索考卷、情境探針、空轉提醒與 14 天升級鏈、回放週跑、backlog
# 每日衰減)一起停了——而三處筆記白紙黑字寫著「便宜的日常段照跑」,落地當下那句就是假的。
# ★監看的東西和被監看的東西同命★:回訪到期的升級鏈因此沒有出口,那正是同一次審視裡「五件
# 逾期沒人管」的上游原因。世界解是 feature toggle 只包真正要停的最小單元(Fowler),所以
# 開關搬到這裡——上面照跑,只停下面真正燒錢的派工。
if [ "${LUMOS_AUTOLOOP_OFF:-1}" = "1" ]; then
  log "派工段暫停中(LUMOS_AUTOLOOP_OFF=1,2026-09-05 起預設暫停;上面的週期觀測照跑)"
  log "要臨時開回:LUMOS_AUTOLOOP_OFF=0 governance/autonomous-loop.sh --dry-run 6"
  exit 0
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
    -e "s#__TIER__#$TIER#g" \
    "$SCRIPT_DIR/autonomous_loop/orchestrator-prompt.md" > "$PROMPT_FILE"
    # 2026-08-27 遷處置閘:__NEED__ 佔位符退役(K-streak 不用),prompt 與此不再注入
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
# 2026-08-27 遷處置閘:--disposal 是單輪收斂(每個發現折或放行),不用 K-streak,故不再算 NEED_FINAL
if ! (cd "$REPO" && python3 scripts/lumos --vault "$SCRATCH/kg" loop status "$TOPIC" --disposal --spec "$SPEC" --repo "$REPO"); then
  OUTCOME="tier-blocked:gate"
  log "tier 守衛擋下:自報收斂但處置閘重驗不過(自算 tier=$TIER_FINAL;2026-08-27 遷處置閘,--disposal 與 --need 互斥故不帶 need)"
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
