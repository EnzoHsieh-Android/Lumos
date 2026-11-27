severity: major
三問之下共 4 條不一致,其中 2 條 major。我只讀了 `r1-pack-code.patch` 和 `scripts/lumos` 的既有鄰居,沒跑測試。派工詞指的鎖檔 `…291a78….json.warming` 不存在,所以沒有動鎖,照派工詞審。

severity: major

**問 1:分層與依賴方向**
結構上大致對得上既有做法。
- `_KillCompile` 掛在 `_KillPrep` 底下,和 `_KillCovBase` 同層。
- `_KillCompile` 靠 `prep` 的回呼(`on_invalid`、`on_swap`、`probes`)往上回報,不直呼 choice-kill 那層。
- 它用 `_kill_run(..., merge=self.prep)`,與 `_kill_run` 既有簽名(`merge` 參數)的用法一致。
- 輸出截斷的字樣判斷,`scripts/lumos:29021` 的既有讀者也有人在讀 `...[truncated `。

唯一有分層疑慮的是設定層(`load_platforms` → `_platform_compile_flag`)。它為了算預設值,自己看 `run_cmd` 的 Gradle 任務長相。`_platform_cov_flag`(`scripts/lumos:6406`)是純讀布林鍵,不碰 `run_cmd`。這點併進下面第 1 條。

**問 2:命名與錯誤處理**
命名與既有一致:`_choice_*` 前綴、`_Kill*` 類別、`ValueError` 訊息格式照 `_platform_cov_flag`。錯誤處理的差異在第 3 條:還原失敗時丟 `_KillPrepAbort`,而 `_kill_merge_restore`(`scripts/lumos:29847`)是記一列 error 後作廢那一組。
- 這是被呼叫端接住的異常類別,形狀合理,類別也和 `_KillHalt` 同樣繼承 `Exception`。
- 不算錯誤處理風格不一致,只在第 3 條一併列出差異。

**問 3:第二種做法**

severity: major
blocking: 是
引句:「return profile_name in ("kotlin-junit", "java-junit") and bool(_PLATFORM_ANDROID_UNIT_RE.search(str(run_cmd or "")))」
- 另立了一套 Gradle 單元測試任務的判法:新正規式 `_PLATFORM_ANDROID_UNIT_RE`(`(?<!\S)\S*:test[A-Z]…UnitTest`),直接在整串 `run_cmd` 上搜。
- 既有工具已經在做這件事:`_gradle_unit_test_task` 和 `_GRADLE_UNIT_TASK_RE`(`scripts/lumos:27xxx` 一帶,即 `_choice_merge_shape` 內部用的)。`_choice_merge_shape`(`scripts/lumos:28886`)已經能從 `run_cmd` 推出 `shape["task"]`。
- 覆蓋那條的 `_choice_cov_data_path`(`scripts/lumos:80323`)也是「`_choice_merge_shape` 加 `re.fullmatch(test<變體>UnitTest)`」。
- 新正規式不分 Gradle 段、不管任務是否落在 `--tests` 之前,判準和既有兩處會漂移。預設值該跟 `_KillCompile` 實際能不能組出指令(`_choice_compile_cmd(run_cmd) is not None`)同源。

severity: major
blocking: 是
引句:「if not old or _count_overlapping(src, old, stop=2) != 1:」
- `_choice_compile_apply` 自己寫了一套套壞法的切片拼接,docstring 還說是「泛化 `_kill_merge_apply`」。
- `_kill_merge_apply`(`scripts/lumos:29979`)套壞法之前先過 `_kill_old_issue(r0)` 和 `_kill_new_issue(r0)`。`_kill_old_issue`(`scripts/lumos:27242`)的 docstring 明講「兩邊各寫一份就會對不上」。
- 新路徑沒過這兩道檢查:`units()` 只查 `isinstance(str)`,不查 `new` 含不含寫不成 UTF-8 的替身字元。
- 這種 `new` 會在 `fh.write` 時才出錯,落進 `_KillCompile.run` 的泛用 `except Exception`,整組被標 env。

severity: minor
blocking: 否
引句:「subprocess.run(["git", "-C", c.wt, "checkout", "--", ":(literal)" + os.path.relpath(t, c.wt_real)], capture_output=True)」
- 這是第三份「等新的一秒、`git checkout`、讀回修改時間」的還原。
- 前兩份是 `scripts/lumos:28657` 和 `_kill_merge_restore`(`scripts/lumos:29847`),docstring 也寫「照逐支那段」。
- 新版多了內容比對與直接寫回,失敗時丟 `_KillPrepAbort`;舊版是記 error 列並回 None。
- 差異有理由,但把「還原」拆出一個共用的小函式比再抄一份更貼近現有慣例。
- ⚠ 這條可升 major,請編排者裁。我判 minor 的依據是新版的語意(多檔、內容驗證、丟異常)和舊版確實不同。

severity: minor
blocking: 否
引句:「m = re.fullmatch(r"test([A-Z][A-Za-z0-9]*)UnitTest", shape["task"])」
- `_choice_compile_cmd` 把「拿掉 `--tests` 那段、用 `shape["parts"]` 拼模組、`fullmatch` 任務名」又抄了一次。
- 同樣的形狀已存在於 `_choice_cov_analyze_cmd` 和 `_choice_cov_data_path`(`scripts/lumos:80323` 起)。
- 結構一致(都是從 `shape` 推),只是第三份拷貝,沒抽共用。

**帳事件與設定鍵讀法(問 3 的另外兩項)**
- `_choice_ledger_aux` 的擴充沿用 `_CHOICE_REACH_TYPES` 型別表加 `kind` 分流。
- gov 計數的 `_gov_choice_count_*` 分派表,與同檔既有型別表和計數函式的做法對得上,沒有另立一套。
- 設定鍵 `compile_check` 的讀法與 `_platform_cov_flag` 同形,只有「預設值怎麼算」是第 1 條那件事。

不對齊共 4 條,其中 major 2 條
