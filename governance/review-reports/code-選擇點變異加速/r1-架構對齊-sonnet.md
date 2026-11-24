severity: minor

我只對照 scripts/lumos 的新碼與鄰居(行號是工作樹 /Users/enzo/harness/lumos-choice-speed/scripts/lumos 的現況),沒有跑重現:這份報告沒有 major,所以不需要。

**問 1,分層與依賴方向:大致對齊,有兩處小偏差。**
- 新增的選用參數物件 `merge`(`_KillMerge`)跟 `_KillHooks` 同形。choice-kill 建它、傳進 `cmd_guard_kill`,不傳時行為不變。`_ChoiceKillRun` 呼叫 `cmd_guard_kill`,沒有跨層直呼(`scripts/lumos:78965`、`78972` 附近的 patch 內容)。
- 路徑圍欄沿用 `_under_root`(`scripts/lumos:16833`),再用 `realpath(wt) + os.sep` 前綴判斷。這跟 `_kill_run_dir` 的寫法一致(`scripts/lumos:26839`)。
- 讀 JUnit 走既有的 `_secev_junit_facts`(`scripts/lumos:9046`),Maestro 那條讀法也是同一支(`scripts/lumos:46731`)。沒有另一套 XML 解析。
- 子程序登記沿用 `_KILL_RUN_LIVE`,沒有新建登記表。
- 訊號處理在 `_situation_rule_signals` 加選用回呼 `on_first`,沒有另一套訊號處理。不設回呼的呼叫端行為不變。

不對齊 1:合併標記是掛在 Popen 物件上的臨時屬性
severity: minor
blocking: 否
引句:「proc._lumos_merge = True   # 先標再登記:回呼看得到它時一定已帶標記」
file: `scripts/lumos:28194`
鄰居的做法是 `_KILL_RUN_LIVE` 只存 pid 對 Popen,`_KILL_WT_LIVE` 另開一張表。整個檔沒有在 Popen 上掛自訂屬性的先例(`grep "_lumos_\w* *="` 只有這一處)。結構是對的,沒有第二張登記表。只是「這支程序屬於合併」的資訊藏在物件屬性裡,不在登記表上。

不對齊 2:`merge` 在建構後才設定,跟 `_KillHooks` 的建構子參數寫法不同
severity: minor
blocking: 否
引句:「hk.merge = merge」
file: `scripts/lumos:28664` 附近的 `_KillHooks.__init__`
同一個類別其餘三個選用參數(`stop_group_on`、`on_row`、`should_stop`)都走 `__init__`,`merge` 卻是類別屬性預設值 `None` 加事後賦值。

**問 2,命名與錯誤處理:對齊。**
- 提示一律印到標準錯誤,前綴 `⚠` 並用 `_kill_esc` 跳脫,跟 `lost` 那條警告同款(`scripts/lumos:79040` 附近)。
- 每個壞法一行的進度輸出在標準輸出,這個沒變。
- 環境變數只認 `"1"`:`LUMOS_SKIP_CHOICE_MERGE` 寫成 `!= "1"`,跟 `scripts/lumos:80568` 同形,也跟 `scripts/lumos:79053` 以外的其他略過變數同慣例。
- 回呼的 `try/except Exception: pass` 跟 `_situation_rule_force_exit` 沖輸出那段一樣。
- 新增的治理帳欄位已登記進 `_GOV_FIELD_TYPES`(`scripts/lumos:18456`),型別宣告方式與鄰居一致。
- 內部函式以 `_choice_merge_*`、`_kill_merge_*` 命名,跟 `_choice_kill_*`、`_kill_*` 同款。

**問 3,第二種做法:有一處要交編排者判斷。**

⚠ 不對齊 3:新增一支 Gradle 單元測試任務解析,與既有的 `_gradle_test_module` 並存
severity: minor
blocking: 否
引句:「不動 _gradle_test_module(它的呼叫端靠「變體任務回 None」判不擋)」
file: `scripts/lumos:77411`
`_gradle_unit_test_task` 做的是「任務名拆成模組各段加任務名」,跟 `_gradle_test_module` 近似,差別在多收 `test<變體>UnitTest`。diff 自己註明不能改舊函式,因為它的呼叫端(`scripts/lumos:77430`)靠「變體任務回 None」判不擋。這是有理由的並存,但兩支函式模組各段檢查的條件(`_SR_MODULE_PART` 加上排除 `.`、`..`)是各自複製的一份。我判不準這算「第二種做法」,還是「合理的新功能」。`_gradle_test_module` 的語意本來就不同,專案裡沒有現成可以共用的版本,所以我不硬判 major。

其餘新工具函式我都沒有找到鄰居已有同功能的版本。`_choice_merge_fullname`、`_choice_merge_hits`、`_choice_merge_too_long`、`_choice_merge_clear` 在檔內沒有對應函式。`shutil.rmtree(..., ignore_errors=True)` 的寫法跟 `scripts/lumos:28149` 一致。

不對齊共 3 條,其中 major 0 條(1 條標 ⚠ 交編排者)

總結:最高嚴重度 minor
