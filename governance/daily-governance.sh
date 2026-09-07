#!/bin/bash
# 每日治理 wrapper:一個喚醒窗內「連續」跑 治理日報 → 自主迭代 loop → lint-watch 版本掃描。
#
# 為什麼合併:閉蓋(clamshell)的 Mac 幾乎一直在睡,launchd StartCalendarInterval
# 不會把機器叫醒、且只在 FullWake 補跑 GUI agent。解法是用 pmset 每天叫醒「一次」:
#   sudo pmset repeat wakeorpoweron MTWRFSU 09:28:00
# 那一次喚醒只夠跑「一段連續工作」——分成 09:30 / 10:10 兩支,機器會在中間又睡著、
# 第二支照樣漏。故把兩件事串成這一支,趁機器醒著一口氣跑完(腳本執行中系統不會 idle-sleep)。
#
# 由 launchd com.enzo.lumos.daily-governance(09:30)觸發。各子腳本仍各自寫自己的 log。
# 第 3 步 lint-watch-check:每日查 linter 新版 → 候選暫存 governance/lint-upgrades/ + LINE 通知。
set -uo pipefail   # 不用 -e:前一支失敗不擋後一支

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ts() { date '+%Y-%m-%d %H:%M:%S'; }

mkdir -p "$DIR/logs"

# ★主體包進 main()、結尾「main "$@"; exit」(2026-09-05 第四輪稽核+代碼審 r1):bash 是邊讀邊執行,腳本在跑的時候
# (自主迴圈那段可跑三小時)被人改檔,回來會從新檔的同一個 byte 位置接著讀,讀到半行就 syntax error 整支死掉——
# 今天 09:30 那次就這樣,lint-watch/doctor/testmap 全沒跑。
# 函式體要找到配對的 } 才會執行,所以主體是一口氣讀完的;上面 set/DIR/ts/mkdir 四行前奏仍是逐行讀(量過從啟動到進 main
# 約 36 毫秒,窗口存在但不是三小時那種)。結尾同一行接 exit 是必要的:沒有它,main 跑完 bash 會回頭從舊 byte 位置
# 續讀,檔案長度變了就讀到垃圾、甚至把整支再跑一遍(scratch 實驗實證:step1/step2 印了兩次)。守衛測試釘這三件。
main() {
  # ★所有東西都在 main() 體內★(守衛 t_daily_governance_wrapper_is_function_wrapped 釘死):
  # bash 是邊讀邊執行,main() 外面的任何一行——包含變數指派與函式定義——在檔案被截斷或
  # 邊跑邊改時都會先被執行。函式體要找到配對的 } 才算讀完,所以整包放進來才是真的安全。
  # 第一版把鎖與健康檔那幾支放在 main() 外面,守衛當場擋下,而它是對的。
  HEALTH="$DIR/.daily-governance-health.json"   # 不進版控:每台機器各自的事實
  LOCKDIR="$DIR/.daily-governance.lock"
  # ── 整跑鎖 ──────────────────────────────────────────────────────────────────
  # ★同源:autonomous-loop.sh 的取鎖段★(2026-09-07 全 repo 審視 #18 抄過來)。
  # 那邊改了這裡要跟著改;守衛 t_daily_wrapper_lock_matches_source 會比對兩份的關鍵行為。
  #
  # 抄的時候要知道這幾件事(第一版的計劃寫錯或漏了其中三件,設計審 r1 三席抓出來;
  # 另外五件是代碼審 r1 五席各自「真的跑實驗」跑出來的,不是讀碼推論):
  #  ① 建目錄是唯一的原子取鎖點。
  #  ② ★判「持鎖的還活著嗎」不能只用 kill -0★——作業系統會把 pid 回收給完全無關的行程,
  #     那時 kill -0 說「活著」,這支就永遠讓行、五步永遠不跑,而且完全沒有訊息。
  #     ★第一版是再問「那個 pid 的指令長得像不像我們這支」,那個做法錯了★
  #     (2026-09-07 code-batch19 通才席實跑打穿:持鎖者換個名字啟動就認不出來,
  #     鎖被搶走、兩個行程同時跑)。現在改成硬身分——取鎖時把自己的啟動時刻寫進鎖裡,
  #     之後拿 pid 去問系統要同一個值來比。細節在下面 holder_alive 的註解。
  #     問不出來不是無條件讓行,是掉到③的鎖齡兜底:無條件讓行那條路上沒有兜底,
  #     一旦誤判就回到「永久停擺而且完全沒有訊息」。
  #  ③ 60 分鐘只用在「pid 讀不到」那個競態(對方剛建好目錄還沒寫 pid)。
  #     ★「讀不到」包含「內容不是數字」★:pid 檔被寫壞(寫到一半被砍)時,第一版兩個分支
  #     都不成立,直接掉到「接管」,連 0 秒齡的新鎖都搶。
  #  ④ ★接管要用 mv 把舊鎖原子搬走,不是「rm 掉再 mkdir」★。rm+mkdir 擋不住這個排列:
  #     A 刪 → A 建(成功)→ B 刪(把 A 剛建好的砍掉)→ B 建(成功),兩邊都以為自己拿到鎖。
  #     實測:八個行程搶同一把殘鎖,30 輪有 19 輪出現多人同時拿到;拿真腳本跑,15 輪有 2 輪雙開。
  #     改用 mv 之後,兩個接管者只有一個的 rename 會成功,另一個的來源已經不在。
  #     附帶好處:mv 要的是外層目錄的寫權限,所以鎖目錄自己變唯讀時也不會卡死。
  #  ⑤ ★清除靠 trap EXIT,而且 trap 要裝在取鎖之前★:這支用 set -u,踩到未設變數會立刻中止,
  #     手寫在結尾的清除根本不會執行。裝在取鎖之後則留下一個「拿到鎖但還沒裝 trap」的窗口。
  #     裝在前面之所以安全,是因為 finalize 會先確認鎖裡的 pid 就是自己才動手。
  finalize() {
    [ "$(cat "$LOCKDIR/pid" 2>/dev/null || echo '')" = "$$" ] || return 0
    # ★先搬走再確認★(2026-09-07 code-batch19 外家席 f5):讀 pid 跟刪目錄中間還有一段,
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
        echo "[$(ts)] ★收尾搬到的不是自己的鎖、又還不回去★:留在 $held,要人來看" >&2
    fi
  }
  lock_secs_since() {   # $1=路徑;印出它幾秒前被動過;問不出來印空字串
    python3 -c 'import os,sys,time;print(int(time.time()-os.path.getmtime(sys.argv[1])))' "$1" 2>/dev/null || echo ''
  }
  lock_proc_start() {   # $1=pid;印出那個行程的啟動時刻;pid 不存在或問不出來印空字串
    ps -p "$1" -o lstart= 2>/dev/null | sed 's/^ *//;s/ *$//' || echo ''
  }
  holder_alive() {   # $1=pid;0=就是當初建這把鎖的那個行程 1=確定不是 2=問不出來
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
  write_pid() {   # 兩個檔都走暫存→改名:這個 repo 的教訓是共用檔一律原子寫入
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
    # ★寫 pid 失敗要當成沒拿到★(外家席 f1):這支沒開 set -e(檔頭第 12 行寫了理由),
    # 所以 write_pid 失敗會被整個吞掉,然後照樣回報「拿到了」。
    # 後果是我們在寫紀錄,鎖裡卻沒有 pid;60 分鐘後別人用鎖齡兜底接管 → 雙開。
    if mkdir "$LOCKDIR" 2>/dev/null; then
      write_pid && return 0
      rmdir "$LOCKDIR" 2>/dev/null || true
      echo "[$(ts)] ★鎖建起來了但 pid 寫不進去($LOCKDIR)★——這次五步都沒跑,要人來看" >&2
      return 2
    fi
    local oldpid; oldpid="$(cat "$LOCKDIR/pid" 2>/dev/null || echo '')"
    case "$oldpid" in ''|*[!0-9]*) oldpid="" ;; esac   # 見③:壞內容等同讀不到
    if [ -n "$oldpid" ]; then
      # ★不要寫成「呼叫;讀 $?」★:這支沒開 set -e 所以現在沒事,但那個寫法一旦被
      # 抄到有開 errexit 的地方,「持鎖者已死」這條完全正常的路會整支中止。
      local hv=0; holder_alive "$oldpid" || hv=$?
      if [ "$hv" -eq 0 ]; then
        echo "[$(ts)] 另一份 daily-governance 正在跑(pid $oldpid),本次退出——不搶寫紀錄"
        return 1
      fi
    fi
    if [ "$oldpid" = "" ] || [ "${hv:-2}" -eq 2 ]; then
      # 身分問不出來(舊格式的鎖、ps 讀不到)也走這條,不是無條件讓行——
      # 無條件讓行那條路上沒有兜底,一旦誤判就是永久停擺而且完全沒有訊息。
      local age; age="$(lock_secs_since "$LOCKDIR")"
      if [ -z "$age" ] || [ "$age" -lt 3600 ]; then
        echo "[$(ts)] 另一份疑似剛起步(鎖存在 ${age:-量不出}s、身分驗不出),本次退出讓行"
        return 1
      fi
    fi
    echo "[$(ts)] 發現殘鎖(pid ${oldpid:-讀不到} 不是這支、或鎖齡過老),接管"
    # ★接管要整段互斥,不是只有搬走那一下原子★(2026-09-07 代碼審 r1 之後自己再量出來的:
    # 第一版改用 mv 之後,八個行程搶同一把殘鎖 12 輪還有 1 輪雙開)。原因是
    # 「判定它死了」跟「動手搬」中間隔了一段:
    #   A 搬走殘鎖 → A 重建鎖 → A 開始跑 → D(老早就判定要接管)把 A 那把全新的鎖也搬走 → D 也開始跑。
    # mv 本身確實原子,但 D 搬的已經是另一把鎖了。所以接管整段要走一把「接管權」小鎖,
    # 進去之後★再確認一次殘鎖還是我看到的那一把★(pid 對不對得上)。
    # 這把小鎖自己也可能殘留(接管中途被砍),用時間兜底:接管只花毫秒,超過 60 秒一定是殘的。
    local steal="$LOCKDIR.steal"
    if ! mkdir "$steal" 2>/dev/null; then
      local sage; sage="$(lock_secs_since "$steal")"
      if [ -z "$sage" ] || [ "$sage" -lt 60 ]; then
        echo "[$(ts)] 另一個接管者正在處理,本次退出"
        return 1
      fi
      # ★破接管權也要原子★(外家席 f2):原本寫成「rm 掉再 mkdir」,
      # 那正是這把鎖在修的同一個形態——兩個人可以各刪一次各建一次,雙雙進到下面那段,
      # 然後各自在結尾無條件刪掉接管權,把還在裡面的第三個人曝出去。
      # 改用 mv:同一個目錄只有一個人搬得走,搬不走的就是輸的那個,直接讓行。
      local sdead="$steal.dead.$$"
      mv "$steal" "$sdead" 2>/dev/null || { echo "[$(ts)] 接管權剛被別人處理掉,本次退出"; return 1; }
      rm -rf "$sdead" 2>/dev/null || true
      rm -rf "$steal".dead.* 2>/dev/null || true
      mkdir "$steal" 2>/dev/null || { echo "[$(ts)] 接管失敗(接管權搶不到),本次退出"; return 1; }
    fi
    local rc=1
    local nowpid; nowpid="$(cat "$LOCKDIR/pid" 2>/dev/null || echo '')"
    case "$nowpid" in ''|*[!0-9]*) nowpid="" ;; esac
    if [ "$nowpid" != "$oldpid" ]; then
      echo "[$(ts)] 進來後發現鎖已經換人(pid ${nowpid:-讀不到}),不接管,本次退出"
    else
      local dead="$LOCKDIR.dead.$$"
      if ! mv "$LOCKDIR" "$dead" 2>/dev/null; then
        if [ ! -w "$DIR" ]; then
          echo "[$(ts)] ★鎖搬不走而且 $DIR 寫不進去★——這次五步都沒跑,要人來看" >&2
          rc=2
        else
          echo "[$(ts)] 接管失敗(鎖剛被釋放),本次退出"
        fi
      else
        rm -rf "$dead" 2>/dev/null || true
        rm -rf "$LOCKDIR".dead.* 2>/dev/null || true   # 前幾次刪不掉的殘留(例如目錄被改成唯讀)
        if ! mkdir "$LOCKDIR" 2>/dev/null; then
          echo "[$(ts)] ★接管後鎖建不起來($LOCKDIR)★——這次五步都沒跑,要人來看" >&2
          rc=2
        elif ! write_pid; then
          rmdir "$LOCKDIR" 2>/dev/null || true
          echo "[$(ts)] ★接管後 pid 寫不進去($LOCKDIR)★——這次五步都沒跑,要人來看" >&2
          rc=2
        else
          rc=0
        fi
      fi
    fi
    rm -rf "$steal" 2>/dev/null || true
    return "$rc"
  }

  # ★原子寫入健康檔★:寫暫存 → 自驗讀得回來 → 換上 → ★再回頭確認真的落在那個路徑★。
  # 暫存檔跟目的檔★同一層★(跨檔案系統改名會失敗;這也是 scripts/lumos 既有寫檔的做法)。
  # 最後那一次回讀是代碼審 r1 邊界席逼出來的:$HEALTH 這個路徑如果意外變成一個「目錄」
  # (中斷殘留、備份工具建了同名資料夾),mv 會把暫存檔**搬進那個目錄**而不是回報失敗
  # ——於是 wrapper 天天印成功、健檢說「沒事」、看門狗說「從沒跑過」,三層同時失明且零訊號。
  write_health() {   # $1..$5 = 五步的 rc;$6 = 加總
    if [ -e "$HEALTH" ] && [ ! -f "$HEALTH" ]; then
      echo "[$(ts)] ★健康檔的位置不是一個普通檔案($HEALTH)★——先把它清掉才寫得進去" >&2
      return 1
    fi
    local tmp="$HEALTH.tmp.$$"
    printf '{"started_at":"%s","finished_at":"%s","run_id":"%s","steps":{"governance":%s,"autonomous":%s,"lint_watch":%s,"doctor":%s,"testmap":%s},"total":%s}\n' \
      "$STARTED_AT" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$RUN_ID" "$1" "$2" "$3" "$4" "$5" "$6" \
      > "$tmp" 2>/dev/null || { rm -f "$tmp" 2>/dev/null; return 1; }
    python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$tmp" 2>/dev/null || { rm -f "$tmp"; return 1; }
    mv -f "$tmp" "$HEALTH" 2>/dev/null || { rm -f "$tmp"; return 1; }
    python3 -c "import json,sys;sys.exit(0 if json.load(open(sys.argv[1])).get('run_id')==sys.argv[2] else 1)" \
      "$HEALTH" "$RUN_ID" 2>/dev/null || return 1
    return 0
  }

  trap finalize EXIT                     # ⑤ 裝在取鎖之前;finalize 自己會確認鎖是不是我的
  local _lk; take_lock; _lk=$?
  [ "$_lk" -eq 1 ] && return 0           # 正常讓行
  [ "$_lk" -ne 0 ] && return 3           # 鎖壞了:回非零,不要偽裝成成功
  STARTED_AT="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  RUN_ID="$(date '+%Y%m%d-%H%M%S')-$$"
  echo "[$(ts)] daily-governance wrapper 開始(run $RUN_ID)"

  # ★每一步的結果要存進「自己的」變數,而且指令與賦值同一行★
  # (2026-09-07 全 repo 審視 #18,設計審 r1 通才席實測):
  # 原本第 1、2 步寫成 `cmd` 然後 `echo "... rc=$?"`——那個 $? 抓到的是 echo 裡
  # $(ts) 這個指令替換自己的結束碼(幾乎恆為 0),不是前面那支腳本的。
  # 實測:`bash -c 'false; echo "[$(date +%s)] rc=$?"'` 印出 rc=0。
  # 而且原本第 3-5 步共用同一個變數名 rc,互相覆蓋,只有最後一步留得下來。

  # 1) 治理日報(自設 PATH/token;log → governance.log)
  "$DIR/ai-governance-research.sh" >> "$DIR/logs/governance.log" 2>&1; rc1=$?
  echo "[$(ts)] 治理日報 段結束 rc=$rc1"

  # 2) 週期觀測 + 自主迭代 loop(log → autonomous.log)
  #    ★無條件呼叫★:暫停開關住在 autonomous-loop.sh 裡、只包住真正燒錢的派工段(2026-09-06
  #    全 repo 審視 #4 訂正)。前半的檢索考卷、情境探針、空轉提醒與 14 天升級鏈、回放週跑、
  #    backlog 每日衰減照跑——2026-09-05 那版把開關寫在這裡,等於連監看一起關掉。
  #    要臨時開回派工:LUMOS_AUTOLOOP_OFF=0。REVISIT 2026-10-05 決定給它真產出路徑或正式退場。
  "$DIR/autonomous-loop.sh" --dry-run 6 >> "$DIR/logs/autonomous.log" 2>&1; rc2=$?
  echo "[$(ts)] 週期觀測+自主 loop 段結束 rc=$rc2"

  # 3) lint-watch 版本掃描(fail-open;log → lint-watch.log)
  "$DIR/lint-watch-check.sh" >> "$DIR/logs/lint-watch.log" 2>&1; rc3=$?
  echo "[$(ts)] lint-watch 段結束 rc=$rc3"

  # 4) doctor 每日跑(fail-open;log → doctor-daily.log)
  # intake守衛 T4 排程線(2026-08-30 d1,外家 r3 唯一補件):T4 的滾動窗計數器住在 doctor 的
  # [I] 段;此前 doctor 只在 push/CI 跑——「doctor 每天跑」曾是未查證的假宣稱,這行讓它成真。
  ( cd "$DIR/.." && python3 scripts/lumos doctor --ci ) >> "$DIR/logs/doctor-daily.log" 2>&1; rc4=$?  # --ci=治理事件入帳(回訪掃描 v3 接電條款:無此則 nags 14 天升級鏈斷路)
  echo "[$(ts)] doctor 段結束 rc=$rc4"

  # 5) testmap 每日重建(2026-09-05 第二輪審視 d5:建過一次後落後 614 個 commit 沒人重建;0.6 秒)
  ( cd "$DIR/.." && python3 scripts/lumos testmap build ) >> "$DIR/logs/testmap.log" 2>&1; rc5=$?
  echo "[$(ts)] testmap 重建 rc=$rc5"

  # ★「加總」是邏輯聚合,不是算術相加★(設計審 r2 通才席實測):
  # 退出碼只吃 0-255。兩步各回 128(被訊號中止的慣例編碼)算術相加是 256,取模變 0
  # ——兩個真實失敗會被壓成「全部成功」,跟原本「恆回 0」是同一種靜默失敗。
  local total=0
  for _r in "$rc1" "$rc2" "$rc3" "$rc4" "$rc5"; do
    [ "$_r" -ne 0 ] && total=1
  done

  # ★寫不進健康檔 = 這一次算失敗★(代碼審 r1 外家 finder 實測:第一版只印一句提醒、
  # total 不動,五步全成功時整支照樣回 0——排程端看到「成功」,而看門狗那邊要等 36 小時
  # 才會從舊時間戳發現不對。既然這一批的核心賣點就是「死了要有人知道」,不能在自己的
  # 收尾這一步製造一個「回 0 但其實沒留下任何紀錄」的洞)。
  if ! write_health "$rc1" "$rc2" "$rc3" "$rc4" "$rc5" "$total"; then
    echo "[$(ts)] ★健康狀態檔寫不進去($HEALTH)★——看門狗會把這次當成沒跑完,所以這一次整支算失敗" >&2
    total=1
  fi

  echo "[$(ts)] 五步 rc=$rc1/$rc2/$rc3/$rc4/$rc5,加總 $total"
  echo "[$(ts)] daily-governance wrapper 完成"
  # ★函式最後一行要是真正的加總★:原本最後一條是無條件的收尾 echo,
  # 所以這支不管發生什麼都回 0(不是我原本以為的「回最後一步的結果」)。
  return "$total"
}

main "$@"; exit
