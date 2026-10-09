severity: clean

已讀完整份 233 行 diff,並在 `534a73fc` 上實跑驗證,沒有 finding。

**鏡頭 1,正確性:已讀,無 finding**
- 我跑了 `python3.14 scripts/lumos <cmd> --help`。`test-quality`、`test-quality scan`、`test-quality capabilities`、`test-quality capture`、`test-quality check` 這五條,help 第一行都帶出「什麼時候用:…」。
- `capture` 和 `scan` 因為自己已有說明,沒被覆蓋。
- `code-loop check` 和 `cochange check` 的 help 仍是各自原本的說明,沒被新鍵蓋掉。單名 `check` 不是任何父指令的子指令,頂層 `lumos check` 回「沒有『check』這個指令」。
- 部署不完整的分支(`scripts/lumos:49700`)是 `add_help=False` 的 parser,並由 `_fill_help_when` 填入 description。所以 `--help` 在該分支下仍會帶「什麼時候用」,另外手動處理 `--help` 並印出部署錯誤原因。

**鏡頭 2,掛鉤:已讀,無 finding**
- 我把兩支掛鉤的 `should_exclude` 抽到 `/tmp/lumos-seat-work/code-test-quality-sync-guards/單審-sonnet/`,去掉註解後 diff,只剩空白行不同,兩支完全對齊。
- 實跑結果:
  - 在消費專案(沒有 `skills/lumos-project-notes`),`test_quality.py`、`test_quality_scan.py`、`test_quality_semgrep.py` 這三支都被豁免。
  - 在來源 repo(有 `skills/lumos-project-notes`),三支都不豁免。
  - `scripts/test_quality_x.py` 和 `scripts/foo.py` 兩種環境下都不豁免,沒有被誤放行。
- case 樣式語法沒打錯。

**鏡頭 3,文件:已讀,無 finding**
- 我從 `lumos --help` 的 choices 數出 85 個頂層命令,和 ARCHITECTURE.md、reference.md 的三處數字一致。
- `commands/03-寫回圖譜.md:45` 有連到 `test-quality-standard.md`,刪掉 INDEX 那行重複入口後,接入標準檔仍找得到。
- INDEX.md 現在 4479 字元,在 4500 上限內。
- `t_every_subcommand_has_when`、`t_precommit_whitelist_drift_guard`、`t_docs_command_count`、`t_command_index_complete`、`t_docs_enumeration_drift` 都跑過,全綠。

**鏡頭 4,圖譜筆記:已讀,無 finding**
- 那行 PITFALL 列的四處(指令數、help 的「什麼時候用」、總目錄字數、掛鉤豁免清單)和程式一致。
- 它列的四個防回歸測試名,和我跑綠的那四個一致。
- 「豁免在來源 repo 本身照樣不生效」符合實測。

總結最嚴重 severity: clean;blocking: 0
