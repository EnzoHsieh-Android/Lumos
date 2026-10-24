severity: major

驗證用假工具跑兩版,實跑全部在 `/tmp/lumos-seat-work/code-android-mem-stability/正確性-sonnet/`。假工具取自 `_MS_FAKE_ADB`、`_MS_FAKE_TP`、`_MS_FAKE_JHD`,新增了讓 ps 在指定次數失敗、`--unreachable` 回 offline 或卡住的開關。修前和修後版本都用 `git archive` 取出,沒動 android-mem-stability 工作樹。實驗完我已刪掉這個臨時目錄,下面的輸出是當時抓的。

共同派工詞第 12–19 行的輸出格式和第 30–33 行的鏡頭我都照做。但它引用的「資料狀態五問」在那份檔案裡找不到原文,所以我沒有逐題作答。我只在下面標出資料狀態相關的後果,例如拿到被截斷的追蹤檔。

## 三個 finding

### 1. ps 偶發失敗一次(第一次問)、而錄製已因上限自己結束:被截斷的追蹤檔被當成完整一輪收下
severity: major
blocking: 是
引句:「alive = perfetto_alive(pid)   # None(不知道)當成還在跑」
引句:「if alive is False:」
歸因:有證據的修復回歸

失敗場景:
- 輸入:`max_record_s` 到了,perfetto 自己結束,N 輪還沒跑完。收尾時第一次 `ps -A -o PID,NAME` 剛好失敗(adb 偶發 255)。
- 預期:跟修前一樣標「錄製在 N 輪跑完前就到了上限」,追蹤檔不可用。
- 實際:`alive` 是 None,`if alive is False` 不成立。程式往下拉回被截斷的追蹤檔,標 `cycle_trace: ok`。峰值被低估,可能讓判定誤放行。

兩版查證,命令為 `python3.14 tools/run.py <old|new> psflake_cap ps_fail_at=0 record_dies_early=1`:
- 修前:`cycle_trace: {'status': 'failed', 'reason': '錄製在 N 輪跑完前就到了上限(stability.max_record_s)'}`
- 修後:`cycle_trace: {'status': 'ok', 'peak_anon_swap_kb': 200000, ...}`
- 控制組 `record_dies_early=1` 且 ps 正常:兩版都是 failed(上限)。差別只來自 ps 失敗。

### 2. 等錄製停下的最後一次確認遇到 ps 偶發失敗:好的追蹤檔被補 KILL 丟掉
severity: minor
blocking: 否
引句:「if perfetto_alive(pid) is not False:   # 等完還在(或一直問不到):補 KILL」
歸因:有證據的修復回歸

失敗場景:
- 輸入:錄製正常停下,等待迴圈裡 ps 回 False 而跳出。接著 `if perfetto_alive(pid) is not False` 那次多餘的 ps 剛好失敗。
- 預期:追蹤檔完整,照拉回。修補自己的註解也說「不把好的追蹤檔丟掉」。
- 實際:None 被當成「還在」,補 `kill -KILL`,回「還停不下來(或問不到它還在不在)」。完整追蹤檔被丟,`cycle_trace` 變 failed。

兩版查證,命令為 `... psflake3 ps_fail_at=2`(第三次 ps 失敗):
- 修前:`cycle_trace: ok`,四個數字齊全。
- 修後:`cycle_trace: {'status': 'failed', 'reason': '錄製收到 TERM 等了 2 秒還停不下來(或問不到它還在不在),已補 KILL'}`

### 3. unreachable 失敗原因丟掉 adb 的 stderr 與逾時原因,還謊稱「輸出含 App 記憶體內容」
severity: minor
blocking: 否
引句:「dumpsys meminfo --unreachable 讀不到總量那行(回傳碼 {rc});輸出含 App 記憶體內容,不留」
歸因:有證據的修復回歸

失敗場景:
- 輸入:裝置離線(stderr 是 `error: device offline`),或 `--unreachable` 超過上限而逾時。
- 預期:原因說得出為什麼讀不到。計劃 S27 只要求不帶裝置輸出,也就是 stdout。stderr 與 `run()` 回的「逾時(N 秒)」不是 App 記憶體傾印。
- 實際:兩種情況都只剩回傳碼。逾時時 rc 是 None,原因寫成「回傳碼 None;輸出含 App 記憶體內容」,但實際輸出是空的。

兩版查證:
- 離線,命令為 `... offline unreach_offline=1`:
  - 修前:`讀不到結果:error: device offline`
  - 修後:`讀不到總量那行(回傳碼 1);輸出含 App 記憶體內容,不留`
- 逾時,命令為 `... hang unreach_hang=1 ENV:LUMOS_STABILITY_LONG_TIMEOUT=1`:
  - 修前:`讀不到結果:逾時(1.0 秒)`
  - 修後:`讀不到總量那行(回傳碼 None);輸出含 App 記憶體內容,不留`

## 順帶發現(沒標 finding,屬原有漏查)
`start_record` 的失敗分支(perfetto 回傳碼 0 但 pid 解析不出來,或 shell 逾時)只 `rm` 設定檔與追蹤檔,沒有 pkill,錄製可能還在裝置上跑。

引句:「return None, f"perfetto 開不了錄製:」

修前也一樣,沒有修復造成的回歸,所以不列 finding。修補新增了 pkill,但這條路徑不走它,不一致。

## 三問

**① 原問題的修復效果(兩版都有證據)**
- pid 還沒回來時被中斷。命令:`tools/intr.py <ver> slowpid SIGTERM "shell perfetto" perfetto_slow=1`。
  - 修前:adb 日誌只有 perfetto 開錄那條,沒有任何停止或刪除,rc=2。
  - 修後:出現 `shell pkill -TERM -f /data/misc/perfetto-traces/lumos-stability-run1.pftrace` 與 `rm -f`,rc=2。
- SIGHUP、SIGQUIT 在驅動執行中送出。
  - 修前:rc=-1(SIGHUP)、rc=-3(SIGQUIT)。沒走收尾,adb 日誌沒有 kill 或 rm,`logcat.raw` 還在。
  - 修後:兩者 rc=2,有 `kill -TERM 4321` 與 `rm -f`,`logcat.raw` 已刪。
- SIGINT:兩版都 rc=2。
- 日誌暫存提早登記、unreachable 不帶輸出尾巴:我只對 unreachable 做了離線與逾時兩個失敗形狀,結果就是 finding 3。「開檔前登記」這條沒有另外構造輸入逐一驗。

**② 修補處的正常、錯誤與相鄰路徑**
- 正常路徑:baseline 兩版都 rc=0,四個數字相同,ps 與 kill 的呼叫順序一致。仍成立。
- 錯誤與相鄰路徑:新增的 finding 1、2 就是 ps 失敗這條相鄰路徑上的回歸。
- 其他已走過的形狀:
  - `abort_record` 遇到 `(None, 原因, None)` 會直接 return,不報錯。
  - 日誌暫存在 `Popen` 前登記,也能被刪。
  - 修補在收尾開頭把 SIGINT、TERM、HUP、QUIT 設成 SIG_IGN,而 SIG_IGN 會被子程序繼承。我用假 adb 記錄:收尾後的 `pkill` 與 `rm` 呼叫,四個訊號的處置都是 1(忽略),修前是預設。
  - 後果:收尾期間 adb 子程序收不到 TERM 或 INT。程式只靠 SIGKILL 整組收掉逾時的呼叫,所以不壞,代價是收尾卡住時只有 SIGKILL 能停。我判為設計取捨,不列 finding。

**③ 新發現的同一案例在兩版的結果**
都在各 finding 內附上。

## 未驗範圍(未判定)
- `pkill -f` 在真機上會不會連帶殺到執行它的 `sh -c` 父殼。假 adb 無法重現,我判不出。樣式本身以追蹤檔完整路徑為準,不會錯殺別的 run-id 的錄製,這點我看過了。
- `json.dump` 寫結果檔的那一瞬間(在 `try` 之外)收到訊號,可能留下半份 `stability.json`。這條沒實跑,窗口極小,不列。
- 使用者圖譜鏡頭(固定席節點逐條判斷與殘留問答)我沒有逐條處理。這包只有範本腳本。

最嚴重 severity:major,blocking 共 1 條。
