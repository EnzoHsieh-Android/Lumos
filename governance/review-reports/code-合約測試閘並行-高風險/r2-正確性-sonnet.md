severity: minor

我逐 hunk 走完 `_run_bound_tests` 的並行路徑、`_bound_tests_parallel`、單調時鐘和九支新測試,沒有找到會讓閘判錯紅綠或結果順序錯亂的輸入。以下三條都在測試端,可靠度上有缺口,但不改變產品判定。

我跑了 `-k bound_tests_parallel`(41 passed)和 `-k bound_tests_secs`(5 passed)。完整的 `-k bound_tests` 超過 120 秒,我中途停掉,沒看到結果。

**1. S7 中斷測試靠固定 0.6 秒送 SIGINT,沒有「已進入等待迴圈」的交握**

severity: minor
blocking: 否
引句:「_time.sleep(0.6)
+        pr.send_signal(_sig.SIGINT)」
1. 探針子程序要先載入約 4.8 萬行的 `scripts/lumos`。本 repo 有位元組碼快取,載入約 0.05 秒,不是問題。
2. 快取沒命中時,我把 `scripts/lumos` 複製到暫存目錄跑,載入約 2.0 秒。SIGINT 會落在 `exec_module` 裡,探針從 `try` 之外噴 KeyboardInterrupt。
3. 實測這樣跑的結果:「S7 前置:中斷有送到」變紅;`len(started) <= 2` 因為實際 0 支而空洞通過。慢機器或冷快取會假紅,不會假綠。
4. 修法:探針進入 `_run_bound_tests` 後印一個就緒標記,測試端讀到標記才送 SIGINT;並加上 `len(started) >= 1` 的下限斷言。
5. 歸因:有證據的原有漏查。這支測試是修補區間才加的,修前版本沒有它。

**2. S2 設定值測試很慢,離逾時上限餘裕不到 3 倍**

severity: minor
blocking: 否
引句:「for val, want_par, want_warn in ((3, True, False), (None, False, False), (1, False, False), (0, False, True),」
1. 我跑的結果:`t_bound_tests_parallel_config_values` 耗時 60.9 秒,測試框架自己標了「餘裕不足 3 倍」。
2. 原因是每個循序案例的固定替身都要等滿 2 秒才確認沒有別支同時在跑,十個值乘上兩次呼叫。
3. 機器負載高時,逼近單支測試 180 秒上限就會假紅。
4. 修法:循序案例的等待窗口縮短,或把十個值拆成多支測試。
5. 歸因:有證據的原有漏查。

**3. S5 和 S7 收尾用 `pgrep -f str(d)` 殺子程序,實際殺不到測試子程序**

severity: minor
blocking: 否
引句:「out = _sp.run(["pgrep", "-f", str(d)], capture_output=True, text=True).stdout.split()」
1. 固定替身的指令是 `{python} run.py {method}`,路徑是相對的,工作目錄才是 `d`。測試子程序的命令列不含 `d`,`pgrep -f` 比對不到。
2. 後果有限:S5 的慢測試在 `rmtree` 之後約 2 秒就自己因為找不到 `log/` 而退出;S7 的測試只睡 1.5 秒就結束。
3. 實測收尾後沒有殘留的 `run.py t_*` 程序,但「確實收掉」的機制是巧合,不是設計。
4. 修法:在 `pgrep` 之外改比對 cwd,或讓 `run.py` 用絕對路徑啟動。
5. 歸因:有證據的原有漏查。

## 逐項判定:找不到出錯輸入的部分

**並行排程(`_worker` 與主流程等待迴圈)**
- 每個 `errs`、`seen`、`todo` 的讀寫都走過了。中斷或工作執行緒出錯時,`errs` 一律在 `lock` 內 append,工作執行緒的 `while not errs` 就不再派新的,主流程立刻往外丟。
- `errs` 是每次呼叫自己的區域變數,中斷不會影響後續別的呼叫者。
- 只有 `th.start()` 迴圈本身不在 `try` 內,Ctrl-C 剛好落在那幾微秒才會漏。這個窗口不構成可舉出的失敗場景,不列為 finding。
- 工作執行緒是 daemon,所以前景可以馬上結束。已開跑的子程序在自己的程序群組裡,跟循序時按 Ctrl-C 的行為一致。

**結果組裝**
- 重新組裝時,`how` 長度 2 和 3 的分支不會混淆。
- 去重鍵、逾時和跑過證據判定與修前相同,`seen[key]` 一定存在。
- `_kill_run` 沒有共用狀態,只用區域暫存檔和 `Popen(start_new_session=True)`。

**單調時鐘**
- `_wall` 改用 `time.monotonic()`。`_kill_run` 內部用 `time.time()`,所以修前版本在時鐘往回調時,逐項相加的 secs 會是負數,`t_bound_tests_secs_monotonic` 在修前實作下真會紅。
- `_bound_tests_check` 裡的 `_time` 本來就有定義(`scripts/lumos` 約 48386 行已在用)。

**設定與提醒**
- 十種輸入(沒寫、1、0、負數、布林、小數、字串、17、區塊非物件、3)的行為與測試期望一致。
- 提醒去重的鍵是「解析後的專案根加值的 repr」,不會因為值不可雜湊而出錯。

**新舊互讀**
- `secs_kind` 沒有被 `_GOV_FIELD_TYPES` 拒收。
- 我沒找到把 bound-tests 的 `secs` 當自動門檻來讀的程式。「三次超過 3 分鐘」只是回頭條件,靠人讀。

## 三問(修補鏡頭)

證據來源是 `behavior_cases`,我獨立核對了 repair 與 preserve。

1. **原問題的修復效果**
   - GA 等待不空轉:`t_bound_tests_parallel_wait_is_quiet` 實測 CPU 0.02 秒對牆上 4.1 秒。
   - GA 中斷後停派:我用變異法移除 `errs.append(e)`,測試變紅。但那次變紅是因為載入太慢的假紅(見 finding 1),不是我要驗證的原因,所以停派的修復效果**未判定**。
   - GT 時鐘往回調:`t_bound_tests_secs_monotonic` 在修後版本綠。
   - GB 與 GD:`t_bound_tests_parallel_repo_config_valid` 與 `t_bound_tests_parallel_config_values` 綠。
   - 缺修前證據,我沒有實測修前版本,所以這幾條沒有逐一做修前紅的確認。
2. **修補處的正常、錯誤與相鄰呼叫路徑**
   - 單支、全懸空、N=1 都走原循序分支。
   - `len(jobs) == 1` 時即使 `workers > 1` 也走循序,沒有問題。
   - 規格閘(`_spec_gate_judge_items`)與修正關卡(約 7661 行)共用 `_run_bound_tests`,回傳形狀不變。
3. **新發現案例的修前修後**
   - 三條 finding 都是測試端。只有修後版本含這些測試,修前沒有可比較的版本。

## 圖譜鏡頭

- **guard-kill**:`guard kill` 只用 `_kill_run`,簽名與行為沒變,不受影響。
- **bound-tests-gate**:紅、未證跑過、懸空擋 rc1 的合約維持不變。判定與順序沒動,只改排程與 secs 的語意,新增的筆記段也說明了。
- **測試假綠形態**(前置斷言):S6、S7 有前置斷言。S7 缺「已開跑至少 1 支」的下限,見 finding 1。
- **lumos-cli-read、lumos-cli-lifecycle、design-loop**:這份 diff 沒有動到它們的行為或合約。

總結:最高等級 minor
