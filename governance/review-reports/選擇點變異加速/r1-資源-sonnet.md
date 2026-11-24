severity: major

我預設的看法是子程序會殘留、時序會最糟，所以逐條對照 spec 與 `scripts/lumos` 的 `_kill_run`、`_isolated_worktree`、`cmd_guard_kill`、`_ChoiceKillRun`、`_situation_rule_signals`。圖譜鏡頭見最後一節。

## 逐節走查

- 白話與兩條 WHY：已讀，無 finding。
- 〈做法〉1 合併呼叫：判讀順序與編不過、被系統收掉的衝突見 finding 5，逾時上限見 finding 4。
- 〈做法〉2 平行分片：見 finding 1、2、3、6、7、8。
- 〈做法〉3 基線：已讀，無 finding。
- 〈預期效益〉：沒把掛住的壞法算進去，見 finding 4。
- 〈不做〉、〈回退〉、〈依據來源〉、〈人裁紀錄〉：已讀，無 finding。
- 驗收條款與預期值表：S8、S9 的預期對不上現行程式，見 finding 1、2、4。

## Finding

### 主程序的判定迴圈出例外時，沒有收掉各份的測試程序群組與工作樹
severity: major
blocking: 是

位置：〈做法〉2「分工」「帳由主程序串行寫」「某份當掉」「中斷」。

spec 把每一份開成 daemon 執行緒，主程序迴圈取列、判定、寫帳、印一行。收尾路徑只寫了兩種：某份的執行緒丟例外（印「第 k 份中斷」），和收到訊號。主程序自己的迴圈出例外時沒寫任何收尾。

引句:「每份是一條 daemon 執行緒,各自呼叫一次 `cmd_guard_kill`」
引句:「主程序的迴圈每次最多等 0.1 秒取列,交給既有的 `_ChoiceKillRun.on_row` 判定、寫治理帳、印一行」

時序：
1. `--jobs 3 nohup ... | head`，或 stdout 管線被關掉，主程序在 `finish()` 的 `print(..., file=self.out)` 丟 BrokenPipeError。`_choice_kill_judge` 或 `_choice_event_extra` 遇到沒預期的列也會丟例外。
2. 例外穿出主迴圈，沒有人設停止旗標，也沒有人 join 各份。
3. 解譯器結束時 daemon 執行緒直接被砍，三份的 `_isolated_worktree` 的 finally 都不會跑。
4. 三份正在跑的 `_kill_run` 是 `start_new_session=True` 開的，不在主程序的訊號群組裡，也沒有人呼叫 `_kill_proc_group`。三組 gradlew 客戶端和它們帶起來的測試行程繼續跑到各自逾時，最長是合併基準耗時的 5 倍。
5. 三棵工作樹與 `git worktree` 登記留著，要等一天後的清殘骸才收，使用者也沒有被告知路徑。

現行單執行緒版沒有這個洞：例外會沿呼叫堆疊穿過 `_kill_run` 與 `_isolated_worktree` 的 finally。多執行緒化後這條保證消失，spec 沒補回。S8 只驗訊號路徑，沒有驗「主程序自己出例外」。

需要在 spec 寫明：主迴圈外層一個 try/finally，無論怎麼離開都先設停止旗標，再收掉 `_KILL_RUN_LIVE` 裡所有程序群組，最後 join 各份並印留下的工作樹路徑。

佐證:
file: `scripts/lumos:28168`（`_kill_run` 只在自己的執行緒內處理 KeyboardInterrupt 與逾時）
file: `scripts/lumos:28097`（工作樹登記與收尾都在執行緒內的 finally）

### 「工作樹建不起來」在程式裡不是例外，而是交出 error 列；照 spec 的偵測方式，那一份的壞法會被記成 no_result
severity: major
blocking: 是

位置：〈做法〉2「某份當掉」、S9、預期值表 S9。

引句:「那一份的執行緒丟例外、或那份的工作樹建不起來 → 主程序印一行「第 k 份中斷:<原因>」」
引句:「那一份沒判完的壞法(含已交出部分列的) 應 不記帳也不記缺結果、算進沒跑、rc 2」

現行 `cmd_guard_kill` 遇到 `not _iw.ok` 不丟例外，而是呼叫 `_kill_err_all` 替該平台每條配方記一列 verdict=error，然後 `continue`。函式最後 `hk.flush()` 把這些列全交給 `on_row`。執行緒是正常 return 的。

例子（`--jobs 3`，第 2 份遇到磁碟滿，或 git 鎖，`git worktree add` 失敗）：
1. 第 2 份交出分到的每個壞法 × 每支測試的 error 列「worktree add 失敗」。
2. 主程序的 `_ChoiceKillRun.on_row` 看到每支測試都有列，就呼叫 `finish`。
3. `_choice_kill_judge` 對 error 判 no_result，記一筆 choice-kill，attempt 加 1。
4. spec 要的「不記帳、不印第 k 份中斷」都沒發生。

另外，「已交出部分列」的壞法本來就會被主程序在收到決定性列的當下記帳（`on_row` 的 decisive 分支），不是靠收尾那段。所以 S9「含已交出部分列的不記帳」和〈做法〉2 只改收尾那一段的寫法互相衝突。

spec 沒有定義執行緒怎麼把「建樹失敗」與「正常結束」區分給主程序，也沒有定義已經 decisive 判掉的壞法算不算帳。照字面實作會讓 S9 的第一案（工作樹建不起來）直接紅，或讓實作者自行發明一個與帳相關的旗標。

這是一個會寫進推送閘用的帳的錯誤紀錄：no_result 都會被下次呼叫重跑，不會造成假通過，但會污染 attempt 計數與 run 統計。

佐證:
file: `scripts/lumos:28428`（`if not _iw.ok:` 之後走 `_kill_err_all` 再 continue）
file: `scripts/lumos:26813`（`_kill_err_all` 只加列、不丟例外）
file: `scripts/lumos:78208`（`_choice_kill_judge` 把 error 判成 no_result）

### 基準共用：第一份失敗、或在基準階段收到中斷時，其餘份的啟動規則沒有定義
severity: minor
blocking: 否

位置：〈做法〉2「基準只量一次」。

引句:「choice-kill 先只啟動第一份,等旗號立起(或第一份結束)才啟動其餘各份」

三種時序：

1. 第一份的執行緒在量基準中丟例外，例如 OSError，或工作樹建不起來。旗號沒立，「第一份結束」成立，其餘兩份同時啟動，表是空的。spec 寫「表是空的 → 這一份照常量基準」，兩份同時各自冷編譯、各自量，沒寫誰的結果算數，也沒寫可以只啟動一份。兩份冷編譯同時搶，反而讓基準耗時變長、逼近逾時。
2. 基準階段沒有任何停止檢查。逐支模式「在第一個壞法之前把每條測試指令的基準全量完」，是 64 次連續呼叫，`should_stop` 只在配方之間被呼叫。Ctrl-C 的第一個訊號在這段只能等它跑完，一般約 5–6 分鐘，最壞每支 600 秒。合併基準上限 1920 秒。
3. 主程序「等旗號立起」的等待迴圈有沒有看停止旗標，spec 沒寫。第一個訊號進來後仍可能啟動其餘兩份，各自建工作樹（大型 Android repo 的 checkout 要幾秒）才在 `between()` 被 `_KillHalt` 擋下。

需要在 spec 補：第一份失敗時其餘份的行為（建議只在旗號立起後才啟動、第一份失敗就整體停）、基準階段是否檢查停止旗標、等旗號的迴圈是否看停止旗標。

### 合併跑的逾時上限含冷編譯，掛住的壞法會佔一份 25 分鐘以上；中斷等待與孤兒行程估算也被推翻
severity: minor
blocking: 否

位置：〈做法〉1「逾時」、〈做法〉2「停」、〈實務隱患〉「中斷等待變長」、〈預期效益〉。

引句:「合併跑壞法的上限 = max(合併基準耗時 × 5, 下限)(沿用「基準耗時 5 倍」的算法,基準換成合併那一次)」
引句:「第一個 Ctrl-C 要等正在跑的那次合併跑完(估 1–2 分鐘)」

時序：合併基準含冷編譯與 64 支測試，例如 300 秒。無窮迴圈型的壞法（迴圈條件或 `i++` 被改掉，這是常見變異）讓某支測試卡住，上限是 1500 秒。

後果：
1. 該份被卡 25 分鐘，才退回逐支；逐支的卡住那支再燒掉 max(單支基準 × 5, 20 秒)。現行逐支跑裡，這種壞法只花一個 25 秒左右的上限。
2. 〈預期效益〉的估算沒有算這個成本。183 個壞法裡有 5% 掛住就是約 9 × 25 分鐘，比整體估的 1.2–3 小時還大。
3. 這段時間送第一個 Ctrl-C，各份「把正在跑的那次跑完就停」得等到逾時。「估 1–2 分鐘」的承諾是錯的，提示訊息只說再按一次強制結束。
4. ⚠ 交編排者：逾時時 `_kill_run` 只殺 gradlew 客戶端的程序群組，卡住的測試行程是 Gradle 背景程序的子程序、在別的 session。是否留下以 100% CPU 空轉的 Gradle Test Executor，我沒有環境能驗證。若會留，`--jobs 3` 下每個掛住的壞法留一個，記憶體估計與搶 CPU 都會失準。

### 判讀順序把「被系統收掉」的幾種形式分散：Kotlin 編譯背景程序 OOM 會被當成「壞法編不過」，測試行程被收掉不在偵測清單
severity: minor
blocking: 否

位置：〈做法〉1「判讀順序」「乾淨才採信」。

引句:「②編不過(rc 不是 0、輸出符合 `_KILL_COMPILE_RE`);③測試程序被系統訊號收掉(見下)」

`_KILL_COMPILE_RE` 內含 `Execution failed for task '...compile...Kotlin...'`。記憶體吃緊時（`--jobs 3`、macOS 壓縮與換頁），Kotlin 編譯背景程序或 JVM 因 OOM 失敗，Gradle 的輸出多半也是這一行。②排在③前面，所以記成 no_result「壞法編不過」。

這個壞法正是「同組停、整個壞法一次判定、不退回」的路徑。使用者看到「壞法編不過」，會用 `lint-waive` 寫「不適用」放行，一個真實的選擇點因環境 OOM 被放行。

③列的三種跡象是 rc 負數、rc 大於等於 128、`daemon disappeared unexpectedly`。若被收掉的是測試行程而不是 Gradle 背景程序，gradlew 回的是 rc 1，訊息是 Gradle Test Executor 的 non-zero exit value。三種都不中，落到「某支沒有 testcase」→ 退回逐支，在記憶體不足下再跑一輪 64 次，也就是 spec 自己說要避免的「白燒時間」。

S9 第三案只模擬 Gradle 自己被 kill -9，沒有涵蓋這兩條。⚠ 精確訊息文字沒在此環境驗證，交編排者。

### 清殘骸跳過登記中路徑的比對，在 macOS 上會因 `/var` 與 `/private/var` 不同而永遠不命中
severity: minor
blocking: 否

位置：〈做法〉2「建與收工作樹排隊」。

引句:「清殘骸(`sweep_repo`,清超過一天的 `lumos-kill-*`)要跳過 `_KILL_WT_LIVE` 裡登記中的路徑」

`_isolated_worktree` 登記的是 `tempfile.mkdtemp` 回的路徑，`_isolated_worktree_sweep` 掃的是 `os.path.realpath(tempfile.gettempdir())` 底下。我在本機實測：mkdtemp 回 `/var/folders/.../T/x-...`，gettempdir 的 realpath 是 `/private/var/folders/.../T`。直接字串比對永遠不命中，要先 realpath 再比。spec 沒寫，也沒有測試守這點。

另外：這個清殘骸依父資料夾的 mtime，而工作樹內容的變動不會改父資料夾 mtime；而且每份只在啟動時掃一次，三份在啟動後幾十分鐘內都掃完了。所以「多份跑超過一天時後起的份把別份清掉」在單程序內其實不會發生。真正的風險是另一個 lumos 程序，登記表不跨程序，spec 沒提。

佐證:
file: `scripts/lumos:28123`（`_isolated_worktree_sweep` 掃 realpath 後的 gettempdir）
file: `scripts/lumos:28097`（`_KILL_WT_LIVE` 登記 mkdtemp 原路徑）

### 主程序迴圈的結束判斷順序沒寫，會漏掉執行緒結束前最後交的列
severity: minor
blocking: 否

位置：〈做法〉2「帳由主程序串行寫」「某份當掉」。

時序：第 k 份執行緒把最後幾列放進佇列、隨即結束。主程序迴圈若先 `queue.get` 判空、再看「所有執行緒都結束」，就會在中間漏掉那幾列，壞法不記帳、算沒跑。順序必須是先確認執行緒全死、再清空佇列。spec 只寫「每次最多等 0.1 秒取列」，沒定結束條件。這會讓 S7「恰好 7 筆」偶發少一筆。

### 記憶體上限只看實體記憶體，沒有可用記憶體或磁碟的檢查
severity: minor
blocking: 否

位置：〈做法〉2「份數與記憶體保護」。

引句:「記憶體上限 = floor(實體記憶體 × 0.6 ÷ 每份估計)」

在 32GB 的 macOS 開發機上，Android Studio、模擬器與瀏覽器常駐，可用記憶體遠小於 0.6 × 32GB。6144MB 是推估，spec 自己的人裁紀錄也寫「推估值」。預設就按 3 份上線，要到 2026-12-31 才複查，期間遇到記憶體不足的後果是整機壓縮變慢、逾時、被系統收掉（見 finding 5）。

每份是一棵完整工作樹加 Android 建置輸出，數 GB；沒有任何磁碟空間檢查，ENOSPC 發生在編譯當中時只會表現成 finding 5 說的誤判。

## 圖譜鏡頭

- `Systems/guard-kill` 的 rc 優先序合約：新增的只是 `cmd_guard_kill` 的選用參數，且 spec 寫了不傳時行為不變（S12）。我讀了 rc 計算那一段，沒有新路徑碰到它。不影響。
- `Systems/guard-kill` 的 `--json` 純度合約：choice-kill 走 `redirect_stdout` 收起來，不走 `--json`；各份是從執行緒呼叫，沒有改 `as_json` 路徑。不影響。但 finding 1 的收尾缺失在 `--json` 一般呼叫上不會出現，因為那是單執行緒。
- `Systems/規格閘`：choice-kill 那行 `[不選:每個壞法一棵工作樹...]` 的比對，spec 已寫。我不重複判。

## 總結

守衛面的風險方向我查了：合併與平行路徑下，我沒找到會把未被守住的選擇點誤記成殺掉的具體時序，多是記成 no_result 或誤放行的「不適用」。最需要補的是兩件：多執行緒下「各份與主程序失敗時的收尾」沒有被當成合約（finding 1、2），和基準共用的失敗與中斷時序（finding 3）。

資源類別逐類答：
- 子程序殘留：見 finding 1、4。
- 工作樹：見 finding 1、2、6。
- Gradle 背景程序：spec 已承認不自動停，finding 4 補上掛住壞法的孤兒測試行程（⚠）。
- 記憶體：見 finding 8。
- 磁碟：見 finding 8。
- 鎖與競態：見 finding 6、7。
- 回滾：spec 的〈回退〉足夠，無 finding。

發現共 8 條
