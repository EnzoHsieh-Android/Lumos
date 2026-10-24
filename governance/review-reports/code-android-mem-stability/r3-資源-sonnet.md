severity: minor

下面是資源席對 `r3-pkg-templates.patch` 的報告。我跑了兩版(修前 44d93aba、修後 f0d41453),用 `git archive` 取出 `scripts/lumos` 和 `scripts/templates`,再套用 `test_lumos.py` 的 `_ms_prepare` 假 adb、假 tp、假 java_heap_dump 與假驅動,全在我自己的臨時目錄跑,沒碰 adb 裝置。用到的環境變數新舊名稱都有給。實驗用的臨時目錄已用字面絕對路徑刪除。

我沒有找到 blocker 或 major。找到四條 minor,兩條是修補造成的退步,兩條是原本就有的漏查。

## 發現

### 發現 1:收到 SIGHUP 或 SIGQUIT 時,java_heap_dump 與 trace_processor 變成孤兒
severity: minor
blocking: 否
引句:「每個子程序都自成一個程序群組,」

失敗場景:
- 快照階段終端機斷線(SIGHUP,例如 ssh 掉線),或收到 Ctrl-\(SIGQUIT)。
- 預期:收集腳本跟著結束時,子程序也被收掉。
- 實際:腳本只註冊了 SIGTERM 的處理,Python 收到 SIGHUP 或 SIGQUIT 就直接結束,`finally` 與 `cleanup` 都不跑。
- 修前,java_heap_dump 與 trace_processor 跟腳本同群組,終端機的 SIGHUP 會一起送到它們。修後,每個子程序都用 `start_new_session=True`,收不到終端機訊號,腳本一死它們就留著。

實跑(`kill -HUP` 打整個群組,時機是快照卡住時):
- 修前:rc=-1,jhd、sleeper 都沒殘留。
- 修後:rc=-1,殘留 `jhd` 1 個與它底下的 sleeper 1 個(pgrep 查到)。
- 殘留的 java_heap_dump 最長可跑 `T_LONG`(1800 秒),跑完還會往 `run_dir` 寫快照檔。

附帶:Ctrl-C 沒有這個問題。SIGINT 讓 Python 丟 `KeyboardInterrupt`,走 `run()` 裡的整組殺。實跑(`killpg(SIGINT)`,時機是驅動在跑):
- 修前:rc=2,錄製有收,logcat.raw 殘留。
- 修後:rc=2,錄製有收,logcat.raw 刪掉,沒有孤兒。

歸因:有證據的修復回歸。只有 SIGHUP/SIGQUIT 這條路是退步,修前 jhd 與 trace_processor 有被連帶收掉;驅動在修前就已自成群組,所以驅動收不到 SIGHUP 不算退步。

### 發現 2:cleanup 中第二次 SIGTERM 會讓清理中斷,且刪原始日誌排在最後
severity: minor
blocking: 否
引句:「    drop_raw(state.get("raw"))」

失敗場景:
- 收到第一次 SIGTERM 後,`cleanup` 先對裝置跑兩次 `shell()`(`kill -TERM`、`rm -f`)。裝置慢或離線時每次最長 `T_SHORT` 120 秒。
- 這段時間內外層再送一次 SIGTERM。`on_term` 不會解除,又丟 `Terminated`,從 `cleanup` 內往上炸成 traceback。
- 預期:原始日誌(帳號、權杖)與裝置上的設定檔、追蹤檔被刪。
- 實際:
  - `rm -f /data/misc...` 沒送,裝置上殘留設定檔與追蹤檔。
  - 排在最後的 `drop_raw` 沒跑,主機上殘留 logcat.raw。
  - rc=1 並印 traceback,不是文件宣稱的 rc=2 加「擋下:」。

實跑(假 adb 在 `kill -TERM` 睡 2 秒,第一次 SIGTERM 後 1 秒送第二次),修前、修後結果相同:
- rc=1。
- adb 日誌裡有 `kill -TERM 4321`,沒有 `rm -f /data/misc`。
- stderr 末行是 `Terminated`。
- `logcat.raw exists: True`。
- 孤兒:logcat、驅動都是 0,因為整組殺在前面已完成。

改法:`drop_raw` 是本機即時動作,應該排在會卡 120 秒的裝置呼叫之前;`on_term` 進入 cleanup 後改成忽略。
歸因:有證據的原有漏查。修前就是 rc=1 加殘留;修補新增的 `drop_raw` 排在最後,所以在這條路上同樣沒跑到。

### 發現 3:perfetto 已在裝置上啟動、但 `state["rec"]` 還沒賦值時被中斷,錄製與暫存檔都沒收
severity: minor
blocking: 否
引句:「    state["rec"] = start_record(pkg, run_dir, st.get("max_record_s", 600))」

失敗場景:
- 先 `adb push` 設定檔,再 `perfetto --background` 起了背景錄製,然後 SIGTERM 落在 `start_record` 還沒回傳之前。
- 預期:`abort_record` 停掉錄製並刪裝置上的 pbtxt 與 pftrace。
- 實際:`state["rec"]` 還是空的,`cleanup` 不知道有錄製。實跑(假 adb 的 perfetto 啟動後睡 3 秒,第 0.5 秒送 SIGTERM),兩版皆 rc=2,adb 日誌既沒有 `kill -TERM` 也沒有 `rm -f`。
- 裝置上錄製會跑到 `max_record_s`(預設 600 秒),設定檔和追蹤檔留在 `/data/misc/`。主機端 run 目錄殘留 `record.pbtxt`。

歸因:有證據的原有漏查。兩版行為相同,不是修補造成。

### 發現 4:中斷後主機上仍殘留快照、追蹤檔與設定檔,但訊息說「暫存已收掉」
severity: minor
blocking: 否
引句:「擋下:收集被中斷,裝置上的錄製與暫存已收掉,沒寫結果檔」

失敗場景:
- 中斷落在快照之後或拉回追蹤檔之後。
- 預期:訊息宣稱收掉了,主機上不該留下含使用者資料的檔。
- 實際:`cleanup` 只刪 logcat.raw。`record.pbtxt`、`heap-before.pftrace`、`heap-after.pftrace`(含使用者資料,可能是 java_heap_dump 被殺後的半截檔)、`cycle.pftrace` 都留著。
- 實跑(Ctrl-C,驅動在跑時):修後 run 目錄剩 `['record.pbtxt']`。
- 這些檔要等下一次執行的 `prune_old_snapshots` 才會清,而且只清超過 7 天的 `heap-*.pftrace`。

歸因:未判定。保存規則可能本來就容許快照留 7 天,我沒有逐一對照計劃,但「已收掉」這句話本身不精確。

## 逐條回答三個鏡頭

### ① 子程序殘留與回收
- **逾時路徑(修後有效)**:
  - 實跑:java_heap_dump 的孫程序用 `start_new_session=True` 握著輸出管線,`T_LONG=2`。
  - 修前:兩次快照共卡 65.4 秒,等到孫程序自己結束。
  - 修後:26.3 秒,約等於 2×(2+10)。`REAP` 的 10 秒上限有效,管線有關。
  - 代價:另開群組的孫程序無法收掉,殘留 2 個(各 30 秒後自己結束)。真的 java_heap_dump 的 adb 子程序與它同群組,會被整組殺,實際影響小。
- **SIGTERM、Ctrl-C 路徑**:整組殺有效,logcat、驅動、sleeper 都沒有孤兒;修後的 `logcat.raw` 也刪了(發現 1 附帶的 C 實驗)。
- **每個子程序都自成群組後,Ctrl-C 還收得到嗎**:收得到,靠的是 `KeyboardInterrupt` 加 `kill_group`,不是靠終端機訊號。SIGHUP 與 SIGQUIT 收不到(發現 1)。
- **例外路徑**:`except BaseException` 會整組殺再往上丟,正常。
- **第二次 SIGTERM**:見發現 2。
- **logcat 串流**:不在新 session 裡,只靠 `lc.kill()` 收。我沒做它專屬的實驗;`cleanup` 先整組殺驅動和其他子程序,再 `lc.kill()`。
- **adb server**:每個 adb 呼叫都自成群組。若 adb server 剛好在某次呼叫逾時時才被拉起,整組殺會連 server 一起殺掉。我沒有實驗,這是推論。

### ② 時間預算
- **git 呼叫**:`rev-parse` 加 7 次 `check-ignore`,在 15707 個追蹤檔的 repo 實測合計 0.16 秒,慢機器上也夠用。
  - `check-ignore` 逾時會回 None,被誤報成「沒被 git 忽略」。這是誤報,不是放行。
  - `rev-parse` 逾時或找不到 git 時 `in_git` 為 False,忽略檢查整段跳過(修前修後同樣如此,實跑 PATH 無 git 時 rc=0、結果檔照寫)。沒有 git 就沒有提交風險,所以不算洞。
- **T_SHORT=120 秒**:套在 `adb pull` 追蹤檔上。錄製緩衝是 64MB 加 8MB,需要約 0.6MB/s 以上才拉得完。USB 夠用,無線 adb 偏慢時會變成「拉不回追蹤檔」,且 `cycle.pftrace` 留半截檔。我沒實測。
- **`stop_record`**:迴圈每圈呼叫的 `perfetto_alive` 各自最長 `T_SHORT`,裝置卡住時實際等待可能超過 `STOP_WAIT` 約 120 秒。我沒實測。
- **SQL 預算(實跑)**:`android-stability-cycle.sql` 的區間配對是平方成長。我用 Python sqlite3 照該 SQL 建同名表跑:

| 取樣點數 | 秒數 |
|---|---|
| 2400(預設 600 秒) | 0.22 |
| 14400(1 小時) | 8.0 |
| 57600(4 小時) | 133 |
| 57600、swap 取樣稀 10 倍 | 13 |

  以 250ms 一個取樣點算,`max_record_s` 要超過約 11 小時才會碰到 `T_LONG`。但錄製緩衝只有 64MB 的 ring buffer,實際取樣點數會先被緩衝限制,所以預算內沒有問題。檔頭註解寫的「預設約 2400 個取樣點影響不到」成立。

### ③ 記憶體與二次方
- **`run()` 的輸出**:`communicate()` 把全部 stdout 讀進記憶體,驅動的 `out + err` 又複製一次。
  - 實跑:驅動輸出 1M 行(約 115MB),子程序 maxrss 修前 444MB、修後 437MB;4M 行(約 460MB)修後 1709MB,約為輸出的 3.7 倍。
  - 驅動最長跑 1800 秒,輸出很吵的話(maestro 開詳細日誌)有爆記憶體的可能。
  - 歸因:有證據的原有漏查,兩版相同。修補沒有讓它變差。
- **logcat.raw**:逐行串流讀,沒問題。
- **`load_mapping`**:逐行讀,沒問題。
- **`parse_exit_info`**:線性。

## 三問總結
1. **原問題的修復效果**:
   - 子程序整組殺加 reap 上限在逾時路徑有效,見 ① 的 65.4 秒對 26.3 秒。
   - Ctrl-C 路徑的 logcat.raw 刪除有效(修前殘留、修後刪掉)。
   - 修補沒有解決第二次 SIGTERM 落在 cleanup 的情形,見發現 2。
2. **修補處的正常、錯誤與相鄰路徑**:
   - 正常路徑:假工具下完整收集仍回 rc=0 並寫出結果檔(`test_lumos.py` 的 `_ms_collect` 假工具,兩版)。
   - 退步:SIGHUP 與 SIGQUIT 路徑(發現 1)。
   - 相鄰路徑:發現 3、4 在兩版相同。
3. **同一案例兩版結果**:都附在各發現裡。我沒跑 `python3.14 scripts/test_lumos.py -k` 的整套測試,只用同一組假工具各跑一次;時機相關的結果(SIGTERM 的第 0.5 秒與第 1.0 秒)每個案例只各跑一次,穩定性未判定。

## 圖譜鏡頭
固定席節點都在 `scripts/lumos` 與 `scripts/test_lumos.py` 一帶,這份改動只動 `scripts/templates/` 下的檔。

我讀了列出的節點,沒有機械式地逐個核對合約,判斷依據是「合約描述的對象都是 `scripts/lumos` 的行為,本包沒改它」:
- `lumos-cli-read`:search 排除 superseded 的合約。收集腳本沒碰 search。
- `測試假綠形態`:修 bug 的「還原翻紅釘」需要前置斷言。本包新增的測試有前置斷言(例如 `前置:中斷時還在{window}`)。
- `bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop`:都綁 `scripts/lumos` 的邏輯,本包未動。

表態記錄裡 `infra-timeout`、`infra-signal` 的 `satisfied` 是可反駁的宣稱:`infra-signal` 在 SIGTERM 和 Ctrl-C 成立,但在 SIGHUP、SIGQUIT 與 cleanup 內第二次 SIGTERM 不成立(發現 1、2)。

最後一行:最嚴重 severity 為 minor,blocking 共 0 條。
