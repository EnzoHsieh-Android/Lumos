severity: minor

# 資源席 r4 報告(資源-sonnet,範本包 templates)

**白話結論:** 這次修補把「收到 SIGHUP 或 SIGQUIT 時整個收尾被跳過」補好了,也補上了「pid 還沒回來就被中斷」的路徑。我沒找到修補造成的資源回歸。剩下三個小洞,兩版都有,修補沒碰到,我都列 minor。

所有實跑都在假工具上,沒碰 adb 裝置。
- 做法:仿 `_ms_collect` 的假 adb、tp、jhd、驅動,兩版各取一個 worktree(修前 `f0d41453`、修後 `5fc4e715`)。
- 為了縮短等待,我把 T_SHORT 與 REAP 做成環境變數,另存成 `collect-short.sh` 副本再跑。
- 暫存目錄、worktree 已刪;我的 harness 在 `/tmp/lumos-seat-work/code-android-mem-stability/資源-sonnet/h/`(mk.py、run.py、sq.py),留作重現用。

## 三問的答案

### ① 中斷時收不收得乾淨

**正常中斷:修復有效。** 在驅動執行中(假 sleeper 孫程序在跑)、`cwd` 為各案例暫存專案、退出碼與觀測如下:

| 訊號 | 修前 | 修後 |
|---|---|---|
| SIGTERM、SIGINT | rc=2,裝置收了、`logcat.raw` 刪了、無殘留程序 | 同左 |
| SIGHUP | rc=-1(被預設動作殺掉)。驅動、sleeper 孤兒殘留,`logcat.raw` 還在,裝置沒收到 kill、rm | rc=2,無殘留程序,`logcat.raw` 已刪,裝置收到 `kill -TERM 4321` 與 `rm -f` |
| SIGQUIT | rc=-3,殘留同上 | rc=2,收乾淨 |

驅動、java_heap_dump、trace_processor 都走 `run()` 的整組殺掉;logcat 走 `lc.kill()`。這兩條我只實跑驅動與 logcat,jhd 與 tp 只讀碼確認,未實跑中斷。

**pid 還沒回來就被中斷:**
- 做法:假 perfetto 先睡 4 秒再回 pid,等 adb.log 出現 perfetto 呼叫時送 SIGTERM。
- 修前:adb 呼叫為零,錄製留在裝置上。
- 修後:送出 `pkill -TERM -f /data/misc/perfetto-traces/lumos-stability-run1.pftrace`,再 `rm -f`。
- 修復有效。

**pkill -f 在裝置上的成本與範圍:**
- 比對樣式是完整追蹤檔路徑。
- 掃 `/proc/*/cmdline` 的成本很小。
- 能誤殺的只有命令列含同一路徑的程序,而 run-id 字元集裡的 `.` 在正規式是萬用字元。
- 結論:實務上等於只殺自己的錄製,別的 run 要 run-id 幾乎相同才會被殺。
- 這點只讀碼推得,沒在裝置上驗(派工詞禁止)。**toybox 有沒有 pkill、是否支援 `-f` 未驗。**
- `abort_record` 不檢查 pkill 的結果,不存在或失敗時只會剩 `rm`,錄製活到 `max_record_s`。

**收尾中再來一次中斷(修復有效):**
- 做法:假 `kill -TERM` 睡 6 秒,依序送 TERM、INT、TERM、QUIT,間隔 0.7 秒。
- 修前:第二個 INT 在 cleanup 裡丟出 KeyboardInterrupt,rc=-2,`logcat.raw` 留著,沒有 rm。
- 修後:四個訊號全被忽略,6.1 秒後 rc=2,`logcat.raw` 已刪。
- 連發同一訊號(TERM,TERM)間隔 2ms、10ms、50ms,每格 6 次,修後 0 次失敗;修前 6/6、6/6、4/6 失敗。

### ② 時間預算

**stop_record 在 ps 一直失敗時:**
- 實測(STOP_WAIT=5、ps 立刻回 255):修前 2.3 秒,修後 7.4 秒,多等整個 STOP_WAIT。預設 30 秒就是多等 30 秒,並補一次 KILL。
- 修前把 ps 失敗當成「已停」,結果是誤報「錄製在 N 輪跑完前就到了上限」。修後改報「問不到它還在不在,已補 KILL」,報錯方向修對了。
- ps 每次都卡到 120 秒逾時的最壞情況:
  - 修後約 6 個 120 秒呼叫:alive 的 ps、kill TERM、迴圈第一次 ps(已過期限)、最後一次 ps、kill KILL、rm,合計約 720 秒。
  - 修前約 5 個呼叫,約 600 秒。
  - 假工具縮短版量到 ps 次數:修前 3、修後 4,與公式相符。

**收尾裡的裝置呼叫離線時加起來多久:**
- 實測(TSHORT=2,假 adb 每次睡過頭):修前、修後都是 4.0 秒,也就是 2 次呼叫乘上單次上限。
- 換算真值是 2×120=240 秒。逾時後的 reap 另外最多 10 秒。
- 兩版相同,修補沒有加長。

### ③ 大檔與二次方

- **cycle.sql 的 swap 區間配對**(`sq.py`,Python 內建 sqlite3,N 個 anon 點配 N 個 swap 點):
  - N=2400(600 秒錄製)0.22 秒。
  - N=9600 3.53 秒。
  - N=19200 13.97 秒。
  - 確實是二次方,但錄製長度受驅動上限 T_LONG=1800 秒約束,取樣點約 7200 以下,約 2 秒,可接受。`max_record_s` 就算設到上限 86400,查詢也受 T_LONG 逾時殺掉。
- **`unreachable()` 的輸出整份進記憶體**(假 adb 吐 300MB 傾印,`/usr/bin/time -l`):
  - 修前、修後的 maximum resident set size 都是約 1.12GB,放大約 3.7 倍。
  - 在 300MB 上跑該 regex 找不到時 9.2 秒,屬線性,無災難性回溯。
  - 見 finding 3。

## 正向主張的證據

- **「SIGHUP、SIGQUIT 現在收得乾淨」。** 命令:`python3 run.py c_{pre,post}{HUP,QUIT} {pre,post} {HUP,QUIT}`,cwd 為 h/。
  - 修前:rc=-1 與 -3,殘留驅動與 sleeper,`logcat.raw` 在,termed 為 False。
  - 修後:rc=2,無殘留,`logcat.raw` 不在,termed 為 True。
- **「正常 TERM 與 INT 路徑仍成立」。** 兩版 rc 都是 2,收尾結果相同。
- **「ps 失敗不再被誤報成錄到上限」。** 命令:`run.py c_{pre,post}ps {pre,post} NONE STOP=5 +ps_fail:`。
  - 修前報「到了上限」。
  - 修後報「問不到它還在不在,已補 KILL」。

## Findings

### 一、收尾剛開始的毫秒級視窗內,連續到兩個不同訊號仍會讓 cleanup 整個不跑完
severity: minor
blocking: 否
引句:「for s in INTERRUPTS + (signal.SIGINT,):」

位置:`cleanup()` 逐個把訊號設成忽略,而 handler 在 except 區塊裡也會被觸發。

- 輸入:TERM 之後在同一毫秒內再來 HUP 或 QUIT。例如 `kill -TERM x; kill -HUP x`,或終端關閉時 HUP 與外部 TERM 同時到。
- 預期:cleanup 照跑。
- 實際:`run.py c_race4 post TERM,HUP`(GAP=0)6/6 次 rc=1,印出 Terminated 的 traceback。
  - 裝置錄製沒收到 kill。
  - `logcat.raw` 還在。
  - logcat 孤兒留著。
- 視窗寬度:間隔 0.3ms、1ms、5ms 各 8 次,分別 0、1、0 次失敗。實務上很窄,所以只列 minor。
- 對照:修前同案例 rc=-1,孤兒驅動加 `logcat.raw` 殘留;TERM 連發同一訊號則已被補好。
- 建議:讓 `on_term` 本身在丟例外前把四個訊號一次設成 SIG_IGN。
- 歸因:有證據的原有漏查。修前同案例更糟,修後視窗縮小但沒關,不是回歸。

### 二、收尾期間四種中斷全部忽略,使用者最久約 4 分鐘按什麼都停不下來,而且沒有任何提示
severity: minor
blocking: 否
引句:「signal.signal(s, signal.SIG_IGN)」

- 場景:裝置離線,使用者 Ctrl-C 之後,cleanup 的 `kill -TERM` 與 `rm -f` 各卡 120 秒。
- 實測(假 adb 睡過頭、TSHORT=2):收尾 4.0 秒,換算 240 秒;逾時後 reap 最多再加 10 秒。
- 這段期間 SIGINT、SIGTERM、SIGHUP、SIGQUIT 全被忽略,只有 SIGKILL 有效。
- 腳本在這段時間不印任何訊息,最後才印「擋下:…」。使用者看起來就是「Ctrl-C 沒反應」。
- 有上限、不是永遠卡死,所以只列 minor。建議忽略之前先印一行「收尾中,最久約 4 分鐘,按 Ctrl-C 無效」。
- 歸因:未判定。這是 r3 修補有意引入的取捨,修前連按兩次 Ctrl-C 反而會中斷收尾並漏刪日誌(實測 rc=-2,`logcat.raw` 留著)。

### 三、`unreachable()` 把整份傾印讀進記憶體,只為了找一行總量
severity: minor
blocking: 否
引句:「rc, out, err = shell(f"dumpsys -t 300 meminfo --unreachable {pid}", timeout=T_LONG)」

- 輸入:`--unreachable` 輸出 300MB 的十六進位傾印。
- 預期:只留總量那一行。
- 實際:`run()` 的 communicate 整份收進記憶體,RSS 約 1.12GB,放大約 3.7 倍;before 與 after 各一次,序列進行。
- 嚴重度考量:真實洩漏很大的 App 才會到這個量。
- 歸因:有證據的原有漏查。修前修後都是 1.12GB,修補沒碰這段。

### 四、perfetto 啟動呼叫回非零或逾時,但錄製其實已經開起來,沒有補殺
severity: minor
blocking: 否
引句:「shell(f"rm -f {remote_cfg} {remote_trace}")   # 開不起來也要收掉推上去的設定檔」

- 場景:`adb shell perfetto …` 在裝置已啟動錄製、pid 已印出後,adb 傳輸失敗回 255,或逾時回 None。
- 實測:假 perfetto 印 4321 但 rc=255。兩版都只送 `rm -f`,沒有 `kill -TERM` 或 `pkill`,裝置端錄製沒停。
- 後果:這個錄製(含 72MB ring buffer)活到 `max_record_s`,預設 600 秒,上限 86400 秒。
- 注意:同一個檔裡的 `abort_record` 已經有 pkill 邏輯,只是這條失敗路徑沒走它。
- 這是假工具重現,真機是否發生未判定。
- 歸因:有證據的原有漏查,兩版相同。

## 未驗範圍

- 真機上的 `pkill -f` 行為與 toybox 支援度(禁止碰裝置)。
- jhd、tp 的中斷收尾只讀碼確認,沒實跑中斷。
- `Popen` 回來與 `GROUPS.append(p)` 之間來訊號,孤兒子程序的視窗:視窗在位元組碼等級,我沒能穩定重現。
- 單次 adb 呼叫真的卡滿 120 秒是用縮短版加乘法推得,沒有真的等 120 秒。

## 圖譜鏡頭

固定席節點如 `bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop` 等,牽連檔只有 `scripts/lumos` 與 `scripts/test_lumos.py`。本包(`scripts/templates/` 下的收集腳本、SQL、pbtxt)沒有改到這兩支檔,所以不影響它們宣稱的行為與合約。表態記錄裡:
- `infra-signal satisfied`(腳本第 43 行引用)在我實測下成立,但有上面 finding 一的毫秒視窗。
- `infra-timeout satisfied` 成立:T_SHORT、T_LONG、REAP 都有上限,但離線最壞累計時間長(finding 二)。
- `infra-shared satisfied` 我沒獨立驗。

最嚴重 severity:minor,blocking 共 0 條(minor 共 4 條)。
