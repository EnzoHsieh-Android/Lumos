severity: minor

整體判斷:r1 的修補大多到位,我沒找到會做出錯行為的新洞。我在 `/Users/enzo/harness/lumos-reach2` 逐支跑了六支新測試,全綠。`_choice_cov_analyze_cmd` 與 `_choice_cov_exec_path` 改走共用函式後,第一段覆蓋路徑的輸出沒變;測試釘了分析指令的字面輸出。我試過把 `audit_unsure` 相關改動拿掉再跑 `t_choice_cov_audit_noresult`,但在複製的目錄裡該測試連原版都紅(`skills/kotlin-idioms/checks-catalog.md` 對不上,偵測不到選擇點),所以沒能驗證它能否抓到這個改壞。複製目錄已刪。

**發現**

severity: minor
blocking: 否
`scripts/lumos:80232`(`_choice_cov_pkg_of`)。r1 把註解剝法換成 `_strip_c_comments(..., kotlin=True)`,而掃主程式套件(`scripts/lumos:80272`)對 `.java` 也用這支。Kotlin 的區塊註解可巢狀,Java 不行。
具體場景:Java 檔開頭是 `/* see a/* b */` 再接 `package com.a.b;`,現在讀成 `''`,舊的非巢狀正規式讀成 `com/a/b`。我在 `lumos-reach2` 上實際跑過,結果如上。後果是該 `.java` 的套件算成空字串,只碰那個套件的測試判成不明、照跑,只變慢、不判錯。
只有檔頭註解裡出現未配對的 `/*` 才會觸發(例如 javadoc 寫路徑樣式),實務上很少見。要修的話,`.java` 改走非 kotlin 的剝法。
引句:「m = _CHOICE_COV_PKG_RE.search(_strip_c_comments(text, keep_length=True, kotlin=True))」

severity: minor
blocking: 否
`scripts/lumos:80272`(掃主程式套件)。換成 `_kt_strip_spans` 後,每支檔頭(最多 32KB)我實測約 3 到 4.5 ms;舊正規式更快。
具體場景:套件數量逼近 `_CHOICE_COV_SRC_MAX`(20000 支)的大型專案,冷掃會多約 60 到 90 秒,每次 choice-kill 都付一次。一般專案幾百支檔只多一兩秒。
修法:先用 `_CHOICE_COV_PKG_RE` 直接找,只有命中位置前面疑似落在註解裡才走完整剝法。
引句:「head = text.encode("utf-8")[:_CHOICE_COV_SRC_HEAD].decode("utf-8", "replace")」

**同類位置與引入新問題的檢查**

- **`_strip_c_comments` 的 `blank_strings`**:預設 `False`,所以字串內容保留;字串裡的 `package` 字樣不會被抹掉。又因 `_CHOICE_COV_PKG_RE` 要求行首,字串裡的 `package` 也不會被誤判成宣告。
- **`_choice_task_swap` 與 `_choice_unit_variant`**:四個呼叫點(`scripts/lumos:29322`、`:80348`、`:80361`、`:80365`)行為跟舊版一致。`:80365` 的 `or shape["task"][...]` 備援實際走不到,無害。
- **`_platform_compile_flag` 改用 `_choice_compile_cmd(run_cmd) is not None`**:`scripts/lumos:6463`、`:6480` 兩處傳的是設定檔的 `run_cmd`,跟 `:81130` 實際使用的同源。run_cmd 沒有 `{method}` 的 Android 平台,預設從 true 變 false,但那種平台本來就組不出合批指令,屬預期。
- **`UNVERIFIED` 哨兵**:`one_batch` 與 `probe` 的所有讀取處都有擋;`apply_compile` 的其他呼叫者無遺漏。
- **探針逐個單獨編**:在 `len(ranges)==1` 時不重複編,預算由 `cap()` 控管,沒有無界迴圈。
- **`audit_done` 的 `no_result` 分支**:`finish` 呼叫它時 `p["done"]` 已設,`_resolve` 重入安全。clause 類的 `no_result` 不設 `audit_unsure`,行為合理。
- **`units()` 的 `.git` 與 `_kill_old_issue`、`_kill_new_issue` 過濾**:跟 `_kill_merge_apply` 同源,測試涵蓋三種被擋的輸入。

總結:最高等級是 minor
