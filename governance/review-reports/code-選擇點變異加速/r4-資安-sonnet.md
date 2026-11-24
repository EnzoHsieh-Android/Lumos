severity: clean

席名 資安-sonnet。範圍是 r4-snapshot.patch 全部 10 支檔,逐 hunk 讀完。鏡頭是〈工具鏈三類〉:提示注入、讀寫與執行越界、非刻意一步繞過的守衛。沒有可利用的洞。

派工詞附的鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/ec6275be…json.warming` 不存在(ls 回 No such file),沒有東西可處理。我沒建 worktree,也沒建臨時目錄。

## 已驗主張

**① 提示注入:沒有新的外來自由文字進給 AI 的路徑**
引句:「print(f"⚠ {_kill_esc(c.plat)}:{_CHOICE_MERGE_BASE_WHY.get(why, why)},這個平台組這次不合併、照逐支跑", file=sys.stderr)」
- `why` 只來自 `_choice_merge_classify` 與 `_choice_merge_facts` 的固定字串,以及 `f"{len(miss)} 支對不到…"` 這種整數插值。
- 平台名先過 `_kill_esc` 才印。
- 新增的 `--only` 提示印的是 `_kill_esc(only[0])`,行號是整數。
- 快篩通過的存活列帶 `tail` 與 `_kill_res_excerpts`,走既有的逃逸與截斷,不寫進帳。帳只存 `judged`、`merged`、`single`、`base_secs`、`merge_tripped`,都是固定字串、整數或布林。

**② 讀寫與執行越界:圍欄有效**
引句:「return real if real.startswith(os.path.realpath(str(wt)) + os.sep) else None」
- 結果資料夾是 `-p` 的值加 `shape["parts"]` 加固定段。
- `parts` 每段都過 `_SR_MODULE_PART` 且排除 `.`、`..`。
- 拿 realpath 對工作樹 realpath 做前綴檢查,不在樹裡就回 None。`_choice_merge_clear` 的 `shutil.rmtree` 只吃過這道圍欄的路徑。
- 套壞法 `_kill_merge_apply` 也對 `os.path.realpath(os.path.join(c.wt, file))` 做 `startswith(c.wt_real + os.sep)`。絕對路徑與指到樹外的符號連結檔都會被擋,退回逐支流程。
- 還原用 `["git","-C",c.wt,"checkout","--",":(literal)"+relpath]`,沒有 pathspec 注入。
- 測試名進 shell 只經 `_run_cmd_expand` 逐段代換,每段字面與逐支那段相同。接合只用空白與 `--tests`。長度、單雙引號成對、`--tests` 前綴都在 `_choice_merge_shape` 檢查。
- 結果檔先看大小,再逐檔交 `_secev_junit_facts`,不丟例外。`TEST-*.xml` 即使是指到樹外的符號連結,內容也只被當 JUnit 剖析,不回顯,沒有外洩路徑。
- 本 diff 沒碰 hook、安裝腳本與 CI,沒有新的下載來源,沒有新寫進程式、範本或文件的密鑰與信箱。URL 都是公開文件。

**③ 非刻意一步繞過:沒有守衛被意外走過**
引句:「merge = not no_merge and os.environ.get("LUMOS_SKIP_CHOICE_MERGE") != "1"   # 只認 1,其他值與沒設一樣」
- 這個環境變數殘留或設錯,結果只是合併關掉、回到原逐支流程,不是放行。S13 的測試把 0、空字串、`true` 當沒設。
- 合併永遠只能多記「存活」,不判殺掉、編不過、掛住。`_kill_merge_emit` 只交 survived 或 abort 列。
- 存活在推送閘要人處置,所以誤判的方向是多擋,不是放行。
- 第一個訊號的回呼 `_KillMerge.on_signal` 只收帶 `_lumos_merge` 標記的程序群組。`_kill_run` 在 finally 裡才從 `_KILL_RUN_LIVE` 拿掉登記。pid 重用的窗口只有 communicate 返回到 pop 之間幾個位元組碼,沒有可行的攻擊。

## 已看過、不報

- `governance/anchor-baseline.json` 的 `note` 只寫了最近一次增量(拿掉睡眠端到端案例、新增 `t_choice_kill_merge_cap_wiring`、補卡線案例)。但雜湊涵蓋整個分支對 `scripts/test_lumos.py` 的改動。
- 我無法從 patch 判斷使用者原話「簽」涵蓋哪些部分。依本 repo 信賴原則,AI 偽造簽核屬範圍外,不報。
- 雙引號包住 `{method}` 的 run_cmd 形狀(`--tests "{method}"`)下,含 `$(…)` 的測試名在 `"'$(…)'"` 裡會被 shell 展開。這是既有 `_run_cmd_expand` 的行為,逐支路徑同樣如此。
- 新的 `_choice_merge_cmd` 只是把同一代換重複多次,沒有放大攻擊面。測試名與 run_cmd 都來自同一個 repo 內容,攻擊者若能寫其中之一,直接寫 run_cmd 就能執行,沒有額外收益。
- 測試檔:假 Gradle 是寫進臨時目錄的腳本,臨時目錄用 `tempfile.mkdtemp(prefix="gctl-ckm-")` 建、收尾用 `_ck_cleanup` 刪。沒有看起來真能用的憑證,沒有測試執行時會跑到的外部命令拼接。

## 針對修補鏡頭三問

- **歸因與行為證據:未判定。** 我是靜態讀 snapshot 的資安席,沒開 before/after worktree 跑兩版。
- **修補處的相鄰路徑:** 靜態上,`r4-snapshot.patch` 所示的路徑圍欄、`merge` 標記與登記後再看 `interrupted`,沒有開出新的越界或繞過面。
- **新發現的同案例兩版結果:** 沒有 finding,不適用。
- **未驗範圍:** 沒實跑測試,沒讀 r4-repair.patch 與 r4-binding.json,沒驗 S16–S18 三條 manual 條款。

## 讀過的檔(snapshot 全部 10 支)

1. `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md`
2. `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md`
3. `docs/lumos-toolchain-knowledge/Projects/選擇點變異平行_計劃.md`
4. `docs/lumos-toolchain-knowledge/Systems/guard-kill.md`
5. `docs/lumos-toolchain-knowledge/Systems/規格閘.md`
6. `governance/anchor-baseline.json`
7. `scripts/lumos`
8. `scripts/test_lumos.py`
9. `skills/lumos-code-loop/SKILL.md`
10. `skills/lumos-project-notes/commands/06-代碼審與推送.md`

另外用 `git show 100d3851…:scripts/lumos` 取修後版本,讀了 `_run_cmd_expand`、`_kill_proc_group`、`_kill_run` 收尾、`_test_name_ok`、`_secev_junit_facts`、`_under_root`、`_name_filter_escape` 的既有定義,用來佐證上面的判斷。

總結:最高嚴重度 clean
