severity: major

這次審了 patch 本體,另外為了對上落點也讀了 HEAD 的 `stop-lint-hook.py`、`impact-hook.py`、`_hookshared.py`。ast-grep 本機沒裝,我用一支假的 `ast-grep`(固定吐 SARIF)在 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/正確性-sonnet/` 的臨時 repo 實跑。

- **有問題:** 白名單可被繞過(F1)、檔名含空白會讓整次檢查崩潰(F2)、被中止時漏收暫存檔(F3)。
- **逐題結果:**
  - 題 1(新舊互讀)、題 3(決策列)、題 4 的子程序群組收尾,實跑都沒問題。
  - 題 2 的 `--config` 路徑判定(`..`、符號連結、大小寫)實跑都擋得住,但佔位符那條白名單洞(F1)是漏的。
  - 題 4 的 `.pgids` 登記檔由 lint-new 自己不刪、由鉤子刪;鉤子被 SIGTERM 時若 lint-new 在寬限內自己收掉,登記檔會留下(`stop-lint-hook.py:106-137`)。這在 patch 外,而且只留一個空檔,沒標成 finding。
- **角色鏡頭(be-api-compat、be-authz):** 這批改動沒有對外 API 欄位變更,也沒有新增端點。`decision_rows` 是 `impact --json` 的條件鍵,舊消費者讀不到只是少一個鍵。

### F1 白名單放行「佔位符當旗標值」,檔名含 `$(…)` 時會執行白名單外的命令
- 引句:「if w in ("--format", "--filter", "--globs"):」
- 位置:`scripts/lumos:40138`
- 原因:`--format`、`--filter`、`--globs` 的值只過 `_LINT_WT_BAD_CHARS`,而 `{`、`}` 不在其中,所以 `{LINT_FILES}` 或 `{LINT_FILES_CSV}` 能當旗標值通過。白名單接著把它 `shlex.quote` 成 `'{LINT_FILES}'`。之後 `_lint_cmd_with_files`(`scripts/lumos:41180` 起)把真檔名換進這串引號裡面。`shlex.quote` 過的檔名 `'x$(…).kt'` 被外層單引號切開,`$(…)` 落在引號外,由 `shell=True` 執行。
- 這違反 S3 的「送進 shell 的命令不含 `$`」與 RULE「專案設定放寬不了」。
- 輸入:已提交且乾淨的 `.lumos/lint.json` 寫 `ast-grep scan --config <toolchain>/configs/ast-grep/kotlin-android/sgconfig.yml --filter {LINT_FILES} {LINT_FILES} > {LINT_SARIF_OUT}`。回合內碰到(新增或修改)一支檔名為 `app/x$(touch${IFS}PWN2).kt` 的檔。
- 預期:`_lint_wt_allow` 拒絕。
- 實際:通過,產出的命令是 `--filter ''x$(touch${IFS}PWN2).kt'' '…'`。跑 `lumos lint-new --worktree --json` 後,repo 根出現 `PWN2`,命令真的被執行了。
- 修法方向:這三個旗標的值拒絕任何佔位符,最好整個只收固定字面值。
- 不是併發問題,是白名單設計目標本身(不讓被開啟的專案執行任意命令)被繞過。

severity: major
blocking: 是

### F2 新檔路徑含空白時,`_lint_wt_blobs` 崩潰,整次檢查沒跑、鉤子靜默放行
- 引句:「if len(head) == 3 and head[1] == b"blob":」
- 位置:`scripts/lumos:40272`
- 原因:`git cat-file --batch` 對 HEAD 沒有的物件輸出 `HEAD:<路徑> missing`。路徑含一個空白時 `split()` 得到三個詞,不符合 blob 的條件,掉進 `elif len(head) == 3:` 分支,執行 `int(head[2])`,而 `head[2]` 是 `b'missing'`,拋出 `ValueError`。
- 輸入:HEAD 乾淨,新增(未追蹤或 `git add`)一支 `app/sp ace.kt`,內容含 `GlobalScope`,跑 `lumos lint-new --worktree --json --repo .`。
- 預期:對這支檔判 base 為空、報新增告警(rc1 加 JSON);或至少 rc3。
- 實際:Traceback,`ValueError: invalid literal for int() with base 10: b'missing'`,結束碼是 1。檢查實際上沒做。
- 影響:
  - 鉤子只在「rc1 加最後一行是 JSON 加 blocked」才擋,traceback 沒有 JSON,所以鉤子整批放行。同一回合其他檔的告警也一起漏掉。
  - CLI 直接用的人會看到 rc1,而 rc1 的語意是「擋」。
- 對照:中文檔名、`-` 開頭、含 `'`、`"`、`$` 的新檔都正常,只有空白會觸發。HEAD 已有且含空白的檔也正常,因為 blob 標頭裡是 sha 不是路徑。
- 這也是「例外的 rc1 不會誤擋」註解背後的洞:例外確實被當成放行,但代價是漏擋。

severity: major
blocking: 是

### F3 SIGTERM 中止時,每次留下一個 0 位元組的 `lumos-lint-*.sarif` 在 TMPDIR
- 引句:「shutil.rmtree(reg["work"], ignore_errors=True)」
- 位置:`scripts/lumos:40233`(處理器);暫存檔在 `scripts/lumos:40994` 附近用 `tempfile.mkstemp` 建、`scripts/lumos:41097` 才刪
- 原因:處理器收掉工具群組並刪快照目錄後直接 `os._exit(3)`。`_lint_run_and_parse` 的 `temp_path`(系統暫存區的 `lumos-lint-*.sarif`)靠函式尾端清掉,`_exit` 讓它跑不到。
- 輸入:`FAKE_SLEEP=60`,背景跑 `lint-new --worktree --pgid-file …`,3 秒後 `kill -TERM`。
- 預期:印「被中止」並 rc3,且沒有殘留。
- 實際:rc3、工具群組已死、`.lumos/lintbase-*` 已刪、`stderr` 也印了「被中止」,但 `$TMPDIR` 多一個 `lumos-lint-xxxx.sarif`。鉤子每次逾時都會漏一個。
- 這與 S4 的收乾淨、以及使用者對暫存累積的規定相衝。
- 處理器若一併刪登記的暫存檔即可。這些檔我已刪掉。

severity: minor
blocking: 否

總結:最嚴重是白名單可被佔位符旗標值加惡意檔名繞過、能執行白名單外的命令(F1),另有新檔路徑含空白會讓整次檢查崩潰並靜默漏擋(F2),會擋 2 條。

相關路徑:
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/scripts/hooks/claude/stop-lint-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-hooks/governance/review-reports/code-android寫法回合結束檢查/r1-snapshot-甲.patch`

臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/正確性-sonnet/` 還在,留給編排者收貨後刪。repo 本身沒有被我修改。
