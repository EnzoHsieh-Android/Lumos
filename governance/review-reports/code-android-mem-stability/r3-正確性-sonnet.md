severity: minor

# 正確性席 r3 報告(收集腳本與兩支查詢範本、錄製設定)

先講結論:修補把 r2 點名的洞補上了,正常路徑也還成立。我找到 3 條不影響結果對錯的邊角問題,都是收尾順序或空窗,沒有 major。其中兩條在修前就存在,第一條的原始日誌刪除步驟是修補新增的。

做法:用 `git worktree add --detach` 取出 44d93aba(pre)與 f0d41453(post),在 `/tmp/lumos-seat-work/code-android-mem-stability/正確性-sonnet/` 照 `_ms_prepare` 的假 adb、tp、jhd 與驅動,各跑一次同一案例。兩版都在暫存專案裡 `git init`,.gitignore 寫 `.lumos/artifacts/`。沒碰實體裝置,也沒動被審工作樹。實驗用的 worktree 與暫存檔已用字面路徑刪掉。

## Finding 1:清理順序把「刪原始日誌」排在最慢的裝置呼叫後面,連按兩次 Ctrl-C 會留下含機密的 logcat.raw

severity: minor
blocking: 否

引句:「drop_raw(state.get("raw"))」

失敗場景:
- 設定宣告 strictmode,日誌裡有 `token=SECRET123`。
- 驅動跑到一半,按 Ctrl-C。
- `cleanup()` 先跑 `abort_record`,它對 adb 送兩次 `shell`,每次上限 `T_SHORT`=120 秒。裝置斷線或卡住時要等很久。
- 使用者不耐煩,再按一次 Ctrl-C。`KeyboardInterrupt` 從 `cleanup()` 裡冒出去,排在最後的 `drop_raw` 沒機會跑。

預期是計劃 S22「原始串流不管串流斷了、被中斷還是正常結束都刪掉」。實際上 `logcat.raw` 留在磁碟。這個檔只在本機、且被 git 忽略,所以我標 minor。

命令與結果:
- 假 adb 讓 `kill -TERM` 睡 60 秒,SIGINT 之後 2 秒再送一次 SIGINT。
- pre:rc=-2,目錄有 `logcat.raw`、`record.pbtxt`,raw 內含 SECRET123。
- post:rc=-2,目錄有 `logcat.raw`、`record.pbtxt`,raw 內含 SECRET123。

單次中斷時,cleanup 做完就會刪,post 實測 `files=['record.pbtxt']`。把 `drop_raw` 移到 `cleanup` 最前面(本機、瞬間完成)就能避開。

歸因:有證據的原有漏查。兩版同樣結果,pre 本來就不刪。但 r2 宣稱「每條路都要刪」,修補的 `drop_raw` 放在最後一步,這個宣稱在雙中斷下不成立。

## Finding 2:啟動錄製與日誌的空窗被中斷時,裝置上的錄製和設定檔洩漏,訊息卻說「已收掉」

severity: minor
blocking: 否

引句:「state["rec"] = start_record(pkg, run_dir, st.get("max_record_s", 600))」

失敗場景:
- `state["rec"]` 要等 `start_record` 整個回傳才有值。
- `start_record` 內有 `adb push` 與 `perfetto --background` 兩次 `run()`。SIGTERM 落在這兩次呼叫之中,裝置上的 perfetto 可能已經啟動,`cleanup` 卻看不到它。
- 結果是沒有送 TERM,也沒有 `rm -f` 設定與追蹤檔,錄製會一直跑到 `max_record_s`(預設 600 秒)。
- 同形狀的鄰居是 `state["lc"], state["raw"] = start_logcat(...)`。`start_logcat` 內先 `open(raw,"w")` 再 `Popen`,中斷落在中間時 raw 與 adb logcat 子程序也沒登記。

預期是 S23「收到 SIGTERM 時應停掉裝置上的錄製並刪暫存」。實際上 stderr 照印「擋下:收集被中斷,裝置上的錄製與暫存已收掉,沒寫結果檔」,但裝置上什麼都沒收。r2 補的 `interrupt_windows` 只涵蓋「等日誌跟上、停錄製之前」兩個空窗,啟動這端沒補。

命令與結果:
- 假 adb 的 perfetto 回應睡 5 秒,第 2.5 秒送 SIGTERM。
- pre:rc=2,遠端 kill 或 rm 呼叫為 `[]`。
- post:rc=2,遠端 kill 或 rm 呼叫為 `[]`。

實機上 `perfetto --background` 幾乎立刻回來,所以空窗很窄。adb 卡住時才實際會碰到。

歸因:有證據的原有漏查。這是修補沒涵蓋的鄰近路徑,不是修補造成。

## Finding 3:`perfetto_alive` 把 ps 呼叫失敗當成「錄製已結束」,會丟掉好的追蹤檔並寫錯原因

severity: minor
blocking: 否

引句:「return rc == 0 and any(line.split()[:1] == [pid] for line in out.splitlines())」

失敗場景:
- `stop_record` 開頭 `alive = perfetto_alive(pid)`。adb 偶發失敗(rc 非 0 或逾時)就回 False。
- 之後 `if not alive:` 直接回 `None,"錄製在 N 輪跑完前就到了上限(stability.max_record_s)"`。
- 錄製其實正常,追蹤檔被丟掉,cycle_trace 記成 failed,原因文字是錯的。

命令與結果:
- 假 adb 讓第一次 `ps -A` 回 1。
- pre:cycle_trace = `{'status':'failed','reason':'錄製在 N 輪跑完前就到了上限(stability.max_record_s)'}`。
- post:同上。

另一條路我也試了:TERM 之後迴圈裡 ps 失敗。後面還有一次 `if perfetto_alive(pid)` 複查,會補 KILL 並記 failed,所以那條不成立。這條只會偽失敗、不會偽成功,所以是 minor。

歸因:有證據的原有漏查,兩版相同。

## 修補鏡頭三問

① **原問題的修復效果**:有行為證據。
- 原始日誌洩漏:SIGINT 與 SIGTERM 各打在 driver 階段與 stop 階段共 4 種,pre 都留下 `logcat.raw`。post 都只剩 `record.pbtxt`,rc=2,遠端有送 `kill -TERM` 與 `rm -f`。這項修復在單次中斷下有效。
- 每個子程序自成群組:驅動啟動另開 session 的孫程序握著輸出管線,`LUMOS_STABILITY_LONG_TIMEOUT=2` 時,pre 總耗時 52.6 秒,post 26.1 秒。post 的 `reap` 上限生效,driver status=failed,reason=「驅動回 None:逾時(2.0 秒)」。26.1 秒是暖機與量測兩次驅動各約 12 秒(2 秒逾時加最多 10 秒等管線)。
- run-id 重用:同 run-id 跑第二次,pre rc=0 會覆蓋結果;post rc=2 並印「run-id run1 已經有結果檔了」。這符合 S24。

② **修補處的正常、錯誤與相鄰路徑**:
- 正常路徑仍成立:strictmode 宣告時的完整一輪,pre 與 post 都 rc=0,檔案同為 `cycle.pftrace`、`logcat.txt`、`record.pbtxt`、`stability.json`。
- 相鄰路徑沒修:見 Finding 1、2、3。

③ **新發現在兩版的結果**:Finding 1、2、3 兩版結果相同,都是原有漏查。沒有修補造成的回歸。

## 圖譜鏡頭

固定席節點多是 scripts/lumos 與測試的合約(search 濾網、bound-tests、guard-kill、re-inject 等)。這份 diff 只動 `scripts/templates/` 的範本,沒碰 scripts/lumos 與它們綁定的測試,所以我判不影響這些合約。pitfalls-code-loop 標 ★RISK★ 但只牽連 scripts/lumos,同樣判不影響。

表態記錄裡的 `infra-signal`(collect.sh:40)與 `infra-shared`(:281)是可反駁的宣稱。信號面,Finding 1 與 2 是反例。共享面,`/data/misc/perfetto-*` 的路徑用 run-id 命名,同 run-id 並行屬威脅模型外。殘留「算不出來」那條我沒法逐條答,表態與問答列沒在我這包裡。

## 未驗範圍

- stability.json 是非原子寫入。`json.dump` 中途被中斷或磁碟寫滿會留下半截檔,而新的 run-id 檢查會因為檔案存在擋住重跑。窗口極小,我沒實跑。
- 實機的 `am instrument` 原始輸出格式:我只讀了程式,沒對真裝置核對。
- SQL 兩支範本只讀不跑。
- `LUMOS_STABILITY_*` 環境變數改名,我 grep 過 repo,範本、測試、skill reference.md 的名稱一致。

相關路徑:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/templates/android-stability-collect.sh`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/governance/review-reports/code-android-mem-stability/r3-pkg-templates.patch`

最嚴重 severity:minor,blocking 共 0 條。
