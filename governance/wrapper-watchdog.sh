#!/bin/bash
# 每日治理 wrapper 的看門狗:讀它的健康狀態檔,逾期或有步驟失敗就出聲。
#
# ★為什麼要獨立一支★(2026-09-07 全 repo 審視 #18,設計審 r1 兩席判 blocker):
# 9/5 那次 wrapper 跑到第二步就死了、後三步全沒跑、整天沒人發現——因為
# ①它不管發生什麼都回 0 ②沒有任何東西在讀它印的東西。
# 而圖譜裡同一週剛好記過一條教訓:「監看的東西和被監看的東西同命」。
# 所以告警器不能住在 wrapper 裡,也不能只靠「有人跑健檢時順便看到」
# ——那正是這個 repo 前科事故失敗過的做法(一條軟提醒響了 46 天、18,283 次沒人發現)。
#
# 這支只做三件事:讀健康檔 → 判斷 → 有事說出去。不改任何東西。
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEALTH="$DIR/.daily-governance-health.json"
LOCKDIR="$DIR/.daily-governance.lock"     # 被監看那支的鎖(拿來分辨「正在跑」和「死了」)
STATE="$DIR/.wrapper-watchdog-state"      # 上次喊過什麼(邊緣觸發用;不進版控)
WLOCK="$DIR/.wrapper-watchdog.lock"       # 這支自己的鎖
LOG="$DIR/logs/wrapper-watchdog.log"
ts() { date '+%Y-%m-%d %H:%M:%S'; }

# 逾期門檻:排程是每天一次,給到 36 小時(睡過一天還有機會補)。
STALE_SEC=$(( 36 * 3600 ))
# ★「機器醒著多久」要問「上次從睡眠醒來」,不是「開機多久」★
# (設計審 r2 通才席判 blocker,實測:這台閉蓋 Mac 開機 59 天沒重開過,
#  「開機超過兩小時」永遠成立,那個條件從第一天就是空的、而且不會有任何錯誤訊息)。
# 真實紀錄裡有過一次 129 小時的合法空窗(長假),這條就是為了不在那種時候誤報。
AWAKE_MIN_SEC=$(( 2 * 3600 ))

awake_sec() {
  # macOS:kern.waketime 給「上次真正從睡眠醒來」的時間。拿不到就失敗,呼叫端當「不確定」處理。
  # ★第一版用 sed 's/.*sec = \([0-9]*\).*/\1/' 剖,抓到的是 usec 不是 sec★
  #   ——`.*` 貪婪會吃到最後一個「sec = 」,而輸出長這樣:
  #     { sec = 1788609050, usec = 942190 } Sat Sep  5 19:50:50 2026
  #   真的用下去就是拿微秒當秒數,結果永遠判成「剛醒來」→ 這條防護永遠不喊,而且不會報錯。
  #   改用 python 明確抓第一個 `sec = `,不靠貪婪比對。
  local wt
  wt="$(python3 -c "
import subprocess,re,sys
o=subprocess.run(['sysctl','-n','kern.waketime'],capture_output=True,text=True).stdout
m=re.search(r'\bsec = (\d+)',o)
sys.stdout.write(m.group(1) if m else '')" 2>/dev/null || echo '')"
  [ -z "$wt" ] && return 1
  echo $(( $(date +%s) - wt ))
}

# ★話要講到有人聽得到的地方★(2026-09-07 代碼審 r1 外家否決席判 blocker,說得對):
# 第一版只 echo 一行 + 追加一個本機紀錄檔,而 launchd 又把 stdout 導進另一個檔案
# ——完整重現了它想防的那件事:「沒有任何東西在讀它印的東西」。
# 所以現在走三條:
#   ①桌面通知:不需要任何人記得去開檔案,狀態一變就跳出來。
#     是這三條裡唯一「不靠人主動查」的,也是這支存在的理由。
#   ②這支自己的紀錄檔:留時間序,事後要回頭查哪天開始壞的靠它。
#   ③健檢的 [A1] 段:那段直接讀同一份健康檔,`lumos doctor` 一跑就看得到,並且接得上治理帳。
# ★三條裡①②住在 launchd,③住在 Claude Code 的收工健檢——後者才是真正的獨立失敗域★
#   (第一版計劃寫「再開一支 launchd job 就是獨立失敗域」,那句話是錯的:
#    兩支 launchd job 共用同一個 launchd、同一個使用者 session、同一顆磁碟)。
# 通知走兩條,前面那條有就用前面那條:
#   ①`~/Library/Application Support/Lumos/LumosWatchdog.app`——安裝腳本建的最小 app,
#     有 Lumos 自己的圖示。★osascript 直接發的通知沒辦法指定圖片★,它顯示的是呼叫者
#     (從 launchd 跑就是 Script Editor 的圖示),要換圖只能包成 app。
#   ②沒建成 app 就退回 osascript 直接發:圖示是系統預設的,但話還是講得出去。
#     ★寧可醜也要發得出去★——這支的價值在「有人看得到」,不在好看。
# ★路徑從 $DIR 算,不寫死家目錄★(代碼審 r1 架構對齊席):產生物放 repo 樹內、
# .gitignore 蓋掉,跟 scripts/bin/ 那支下載二進位的做法同款。install-watchdog.sh 建它。
NOTIFIER_DIR="$DIR/.notifier"
NOTIFIER="$NOTIFIER_DIR/LumosWatchdog.app"
notify() {
  # 訊息走檔案不走參數:applet 的 handler 寫成 `on run argv` 時,用 open --args 啟動會
  # ★整個不執行★而 open 照樣回 0(實測)。所以寫成 `on run`,訊息從檔案讀。
  #
  # ★退路要靠 applet 自己留的印子,不能只看 open 的回傳碼★
  # (代碼審 r1 外家否決席判 blocker,查證後修正它的推論):
  #   它說「open 回 0 不代表通知送出去,所以退路是死碼」——前半對(故意 error 的 applet 實測 rc=0)。
  #   現在改成 applet 跑完自己摸一個印子,等不到就走 osascript 退路,退路真的走得到了。
  # ★但「跑到了」不等於「使用者看得到」★:通知權限被關掉時 display notification 不報錯,
  #   shell 這一層沒有辦法分辨。那個洞交給另外兩條不受通知權限影響的通道:
  #   這支自己的紀錄檔、健檢的 [A1] 段。
  if [ -x "$NOTIFIER/Contents/MacOS/applet" ] && command -v open >/dev/null 2>&1; then
    if printf '%s' "$1" > "$NOTIFIER_DIR/message.txt" 2>/dev/null; then
      rm -f "$NOTIFIER_DIR/.ran" 2>/dev/null || true
      if open -a "$NOTIFIER" >/dev/null 2>&1; then
        local i
        for i in 1 2 3 4 5 6 7 8 9 10; do
          [ -f "$NOTIFIER_DIR/.ran" ] && return 0
          python3 -c "import time;time.sleep(0.5)" 2>/dev/null || sleep 1
        done
      fi
    fi
  fi
  command -v osascript >/dev/null 2>&1 || return 0
  osascript -e 'on run argv
    display notification (item 1 of argv) with title "Lumos 治理看門狗"
  end run' "$1" >/dev/null 2>&1 || true
}
emit() {   # $1=kind  $2=一句話
  local kind="$1" msg="$2"
  echo "[$(ts)] $msg"
  notify "$msg"
  mkdir -p "$DIR/logs" 2>/dev/null || true
  printf '{"ts":"%s","kind":"%s","note":"%s"}\n' \
    "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$kind" "$msg" >> "$LOG" 2>/dev/null || true
}

# ★這支自己也要一把鎖★(代碼審 r1 併發席:被監看的有鎖、監看的自己沒有,是不對稱的疏漏。
# 手動測試撞上排程那一次,兩份會各自判成「狀態改變」、重複寫帳)。
# ★但故意不學 wrapper 那套 pid 身分驗證★:監看器被一把殘鎖永久關掉,比偶爾兩份同時跑嚴重
# 得多,所以這裡一律用時間兜底、寧可搶——這支跑幾秒就結束,鎖超過 10 分鐘一定是殘的。
wlock_release() { rm -rf "$WLOCK" 2>/dev/null || true; }
take_wlock() {
  mkdir "$WLOCK" 2>/dev/null && return 0
  local age
  age="$(python3 -c "import os,time;print(int(time.time()-os.path.getmtime('$WLOCK')))" 2>/dev/null || echo 99999)"
  [ "$age" -lt 600 ] && return 1
  mv "$WLOCK" "$WLOCK.dead.$$" 2>/dev/null || return 1
  rm -rf "$WLOCK.dead.$$" 2>/dev/null || true
  mkdir "$WLOCK" 2>/dev/null || return 1
  return 0
}

# 被監看那支現在是不是真的在跑(看它的鎖)。回傳 0=在跑,1=沒在跑。
# ★不看鎖就會誤報★(代碼審 r1 併發席實測):自主迴圈那段可以跑三小時,只看
# finished_at 的年齡,會在它正在跑的時候喊「超過 36 小時沒跑完、它不會自己喊」
# ——而那句話還會誘使人去 kill 一個其實正常的行程,一 kill 就掉進殘鎖接管那條路。
wrapper_running() {
  [ -d "$LOCKDIR" ] || return 1
  local p; p="$(cat "$LOCKDIR/pid" 2>/dev/null || echo '')"
  case "$p" in ''|*[!0-9]*) return 1 ;; esac
  kill -0 "$p" 2>/dev/null || return 1
  local cmd; cmd="$(ps -p "$p" -o command= 2>/dev/null || echo '')"
  case "$cmd" in *daily-governance*) return 0 ;; *) return 1 ;; esac
}
lock_age() {
  python3 -c "import os,time;print(int(time.time()-os.path.getmtime('$LOCKDIR')))" 2>/dev/null || echo ''
}

# ★健康檔不在時,要去問第二個來源再開口★(2026-09-08 真的講錯話之後補的)。
# 出過的事:健康檔不存在,這支就每天喊一次「這台機器上的 wrapper 從來沒跑完過」
# ——而 wrapper 自己的紀錄檔裡,前一天和當天都白紙黑字寫著「完成」。
# 原因是「寫健康檔」是後來才加進 wrapper 的,排程當時跑的還是舊版,舊版不寫那個檔。
# ★這支只有一個來源,而那個來源的沉默被它當成了「沒發生過」。★
# 現在的規矩:健康檔不在 → 去看 wrapper 自己的紀錄檔;它最近有跑完的話,
# 講的話要換成「有在跑但沒留下健康檔」,而不是「從來沒跑完過」。
# ★仍然要喊★:那個狀態代表這支看門狗是瞎的,值得知道一次;只是不能講假話。
# 紀錄檔的路徑跟 launchd 那份 plist 的 StandardOutPath 對齊;檔不在就當問不出來,
# 退回原本的判斷(fail-safe:第二個來源缺席不會讓警報消失)。
WRAPPER_LOG="$DIR/logs/daily-wrapper.log"
wrapper_log_last_finish() {   # 印出最後一次「完成」的時間(本地時間字串);問不出來印空字串
  [ -f "$WRAPPER_LOG" ] || { echo ''; return 0; }
  python3 - "$WRAPPER_LOG" <<'PY' 2>/dev/null || echo ''
import re, sys
last = ""
try:
    with open(sys.argv[1], encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            m = re.match(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*wrapper 完成", ln)
            if m:
                last = m.group(1)
except OSError:
    pass
print(last)
PY
}
secs_since_local() {   # $1="YYYY-MM-DD HH:MM:SS"(本地);印出距今幾秒,算不出來印空字串
  [ -n "$1" ] || { echo ''; return 0; }
  python3 -c "
import datetime,sys
d=datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d %H:%M:%S')
print(int((datetime.datetime.now()-d).total_seconds()))" "$1" 2>/dev/null || echo ''
}

# 健康檔一次讀出四件事,四行:finished_at / 哪些步驟非零 / total 跟 steps 對不對得上 / steps 讀不讀得到。
# ★不能只讀 total★(代碼審 r1 邊界席):健檢的 [A1] 段讀的是 steps,這支第一版讀 total,
# 餵一份「五步全 0、只有 total 壞掉」的檔,兩邊會講出完全相反的結論——而我在健檢那段
# 的註解裡還寫了「兩條讀同一份健康檔,所以不會各說各話」,那句話當場被打臉。
# 現在兩邊都以 steps 為準,total 只當交叉檢查:對不上就是這份檔壞了,單獨喊一種狀態。
read_health() {
  python3 - "$HEALTH" <<'PY' 2>/dev/null || return 1
import json, sys
d = json.load(open(sys.argv[1]))
fin = d.get("finished_at")
fin = fin if isinstance(fin, str) else ""
steps = d.get("steps")
if isinstance(steps, dict):
    bad = ",".join(str(k) for k, v in steps.items() if v != 0)
    agg = 1 if bad else 0
    mismatch = "1" if d.get("total") != agg else "0"
    readable = "1"
else:
    bad, mismatch, readable = "", "0", "0"
print(fin); print(bad); print(mismatch); print(readable)
PY
}

main() {
  take_wlock || { echo "[$(ts)] 另一份看門狗正在跑,這次跳過"; return 0; }
  trap wlock_release EXIT

  # ★邊緣觸發★(設計審 r2 外家席):照字面每小時寫一筆,故障持續期間一天寫 24 筆同樣的東西
  # ——而這一案自己正在處理帳本膨脹。只在「第一次發現 / 狀態改變 / 換日 / 恢復」時寫。
  local prev=""; [ -f "$STATE" ] && prev="$(cat "$STATE" 2>/dev/null || echo '')"
  local today; today="$(date +%F)"
  local now_state="" msg=""

  if wrapper_running; then
    local la; la="$(lock_age)"
    if [ -n "$la" ] && [ "$la" -gt "$STALE_SEC" ]; then
      now_state="hung|$today"
      msg="每日治理 wrapper 從 $(( la / 3600 )) 小時前就一直在跑、沒有結束——多半是卡住了。鎖在 $LOCKDIR。"
    else
      now_state="running|$today"   # 正在跑,沒事,不喊
    fi
  elif [ ! -f "$HEALTH" ]; then
    # ★檔案不存在 ≠ 死掉★(設計審 r1 外家席:第一版完全沒定義這個語意)。
    # 新機、重新 clone、清過紀錄都會這樣,訊息要跟「死掉了」分開講,而且不算逾期。
    # ★而且不存在也 ≠ 沒跑過★(2026-09-08):先問 wrapper 自己的紀錄檔。
    local lf ls_
    lf="$(wrapper_log_last_finish)"; ls_="$(secs_since_local "$lf")"
    if [ -n "$ls_" ] && [ "$ls_" -le "$STALE_SEC" ]; then
      now_state="nohealth|$today"
      msg="每日治理 wrapper 有在跑(它自己的紀錄檔:最後一次完成 $lf),但沒有留下健康狀態檔——這支看門狗因此看不到它的結果。多半是排程跑的還是舊版本,或者那個檔被清掉了。"
    else
      now_state="never|$today"
      msg="這台機器上的每日治理 wrapper 從來沒跑完過(沒有健康狀態檔,它自己的紀錄檔裡也找不到最近跑完的紀錄)。第一次跑過就會有。"
    fi
  else
    local hr fin bad mismatch readable age
    if ! hr="$(read_health)"; then
      now_state="unreadable|$today"
      msg="每日治理 wrapper 的健康狀態檔讀不動($HEALTH)——看不出它跑了沒。"
    else
      fin="$(printf '%s\n' "$hr" | sed -n 1p)"
      bad="$(printf '%s\n' "$hr" | sed -n 2p)"
      mismatch="$(printf '%s\n' "$hr" | sed -n 3p)"
      readable="$(printf '%s\n' "$hr" | sed -n 4p)"
      age=""
      [ -n "$fin" ] && age="$(python3 -c "
import datetime,sys
d=datetime.datetime.fromisoformat(sys.argv[1].replace('Z','+00:00'))
print(int((datetime.datetime.now(datetime.timezone.utc)-d).total_seconds()))" "$fin" 2>/dev/null || echo '')"
      if [ -z "$age" ] || [ "$readable" != "1" ]; then
        # ★時間讀不動就是讀不動,不能往下掉進「沒事」★(代碼審 r1 外家 finder 實測:
        # 第一版時間解析失敗只讓 age 變空字串,控制流直接落到下面比 total,total 剛好是 0
        # 就靜默判成正常——一份完全讀不懂的健康檔換來一個綠燈)。
        now_state="unreadable|$today"
        msg="每日治理 wrapper 的健康狀態檔內容不對($HEALTH:時間或 steps 欄讀不動)——看不出它跑了沒。"
      elif [ "$age" -gt "$STALE_SEC" ]; then
        local aw; aw="$(awake_sec || echo '')"
        if [ -n "$aw" ] && [ "$aw" -lt "$AWAKE_MIN_SEC" ]; then
          now_state="justwoke|$today"   # 剛醒來,排程還沒輪到——不喊(那 129 小時空窗的形態)
        else
          now_state="stale|$today"
          msg="每日治理 wrapper 超過 36 小時沒跑完(最後一次 $fin)——第 3-5 步可能整批沒跑,而它不會自己喊。"
        fi
      elif [ "$mismatch" = "1" ]; then
        now_state="inconsistent|$today"
        msg="每日治理 wrapper 的健康狀態檔自相矛盾($HEALTH 的 total 跟 steps 對不上)——這份檔不能拿來判斷。"
      elif [ -n "$bad" ]; then
        now_state="failed|$today"
        msg="每日治理 wrapper 最後一次跑完但這些步驟失敗:$bad(見 $HEALTH 的 steps 欄)。"
      else
        now_state="ok|$today"
      fi
    fi
  fi

  # 恢復也記一筆(不然帳上只看得到壞掉、看不到修好)
  case "${prev%%|*}" in
    ""|ok|running) ;;
    *) case "${now_state%%|*}" in
         ok|running) emit "recovered" "每日治理 wrapper 恢復正常(前一個狀態:${prev%%|*})。" ;;
       esac ;;
  esac
  if [ -n "$msg" ] && [ "$now_state" != "$prev" ]; then
    emit "${now_state%%|*}" "$msg"
  fi

  # ★狀態檔寫不進去要喊,不能默默吞掉★(代碼審 r1 邊界席實測:第一版寫
  # `> "$STATE" 2>/dev/null || true`,狀態檔變成目錄或唯讀時 ①bash 會在套用 2>/dev/null
  # 之前就把錯誤印到真的 stderr,吞不掉 ②邊緣觸發整個失效,故障期間每小時重複喊一次
  # ——正好是這支自己設計要避免的那件事)。
  local stmp="$STATE.tmp.$$"
  if ! { printf '%s' "$now_state" > "$stmp"; } 2>/dev/null \
     || ! mv -f "$stmp" "$STATE" 2>/dev/null \
     || [ "$(cat "$STATE" 2>/dev/null || echo '')" != "$now_state" ]; then
    rm -f "$stmp" 2>/dev/null || true
    emit "state-unwritable" "看門狗自己的狀態檔寫不進去($STATE)——它會開始每小時重複喊同一件事,先把那個路徑清掉。"
  fi
  return 0
}

main "$@"; exit
