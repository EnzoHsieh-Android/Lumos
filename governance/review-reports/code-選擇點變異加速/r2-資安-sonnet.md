severity: clean

資安-sonnet,代碼審第 2 輪。按〈工具鏈三類〉站在攻擊者那邊看,沒有能被利用的洞,0 條 finding。

## 逐類結論

**① 提示注入:已看,無**
- 新增的 stderr 輸出只印 `_kill_esc(c.plat)`,以及固定字串表 `_CHOICE_MERGE_BASE_WHY` 或 `f"{len(miss)} 支對不到…"`,都不含作者可控的自由文字。
- 測試輸出尾巴 `tail` 只進 `_choice_merge_classify` 做正則判斷,也進 abort 列的 `fail_excerpt`。這兩處都走舊有的 `_kill_fail_excerpt` / `_kill_res_excerpts`,沒有新增回顯。
- 新欄位 `judged` 只可能是 `merged` 或 `single`,`--only` 提示用的是 `_kill_esc(only[0])`。派工詞、hook 附加段都沒有新的外來文字入口。

**② 讀寫與執行越界:已看,無**
- 合併指令組裝(`_choice_merge_cmd`):每支測試名在 `_kill_merge_ready` 都先過 `_test_name_ok` 與撞名檢查,再交 `_run_cmd_expand`。這跟逐支路徑是同一支代換、同一套引號。`_choice_merge_shape` 還要求含 `{method}` 的那一段單雙引號各自成對。測試名不能夾帶 shell 字元,run_cmd 本身來自設定檔,信任面沒有變大。
- 刪除:`_choice_merge_clear` 的 `rmtree(rdir)` 只收 `_choice_merge_results_dir` 回傳的值。該值已經 realpath,並要求以工作樹路徑加 `os.sep` 開頭。`-p` 是絕對路徑、含 `..`、符號連結,或模組段含 `.`/`..`(`_gradle_module_parts` 擋)都回 None,不合併。
- 寫壞法:`_kill_merge_apply` 沿用逐支那段的 `realpath` 加 `startswith(c.wt_real + os.sep)` 圍欄。還原用 `git checkout -- :(literal)<相對路徑>`。這些都只動隔離工作樹,不動使用者的工作目錄。
- 讀結果檔:先看大小(單檔 8MB、合計 64MB),再交 `_secev_junit_facts`。該函式拒收 DTD,並處理剖析錯誤、過深、案例數超限。沒有 XXE 或實體展開路徑。
- 結果資料夾裡的符號連結可由測試程式在基準與快篩之間植入。但測試程式本來就在工作樹裡執行任意碼,這不是權限升級,不報。
- 沒有新寫進程式、範本或公開文件的密鑰與信箱(我對整份 patch grep 過信箱、金鑰、curl/wget、`~/`、`os.system`、eval、pickle),沒有安裝腳本或下載網址的改動。

**③ 非刻意、一步就能繞過的守衛:已看,無**
- 合併快篩永遠不判 killed。判 survived 的前提是「全部乾淨通過」,有失敗、沒跑乾淨、對不到名字、rc 不是 0 一律丟掉,改走原本的逐支流程。這個方向是多擋、不是放行。
- `LUMOS_SKIP_CHOICE_MERGE` 只認恰好等於 `1`,而且它只會關掉加速,殘留在 shell 裡只會變慢,不會放行任何東西。
- 按一次 Ctrl-C:`on_signal` 收掉帶合併標記的程序群組。`_kill_merge_screen` 在 `_kill_run` 之後先還原壞法,再看 `mg.interrupted` 並丟出 `_KillHalt`;停止旗標在套壞法與開快篩之間也先還原才停。被中斷的壞法不記帳,不會漏還原。
- `_kill_run` 在登記之後再看一次 `merge.interrupted`,補上第一輪指出的訊號空窗。
- 檔名帶空白或中文:合併段沿用 `_run_cmd_expand`,每段與逐支逐字相同。
- 新舊帳互讀:舊帳缺 `judged` 讀成 single(`d.get("judged") or "single"`)。`_GOV_FIELD_TYPES` 新增欄位型別檢查,型別錯會跳過那一行,不會擋下推送閘。

## 已驗主張(逐字引句)

引句:「if mut is None and len(names) == 1:」(測試用假 Gradle 的片段,範圍是測試檔)
引句:「real if real.startswith(os.path.realpath(str(wt)) + os.sep) else None」(rmtree 目標的圍欄)
引句:「merge = not no_merge and os.environ.get("LUMOS_SKIP_CHOICE_MERGE") != "1"」(關閉旋鈕只往保守方向)
引句:「if mg.interrupted:   # 快篩被第一個訊號收掉:這個壞法不交任何列(不記帳)、停」(中斷路徑已先還原再停)

未驗範圍:沒有跑 before/after 兩版測試。依鏡頭只做靜態攻擊路徑審查,安全面的主張沒有行為證據,只有靜態推論。鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/a58fc97a…json.warming` 檢查時不存在,所以沒有動它。沒有建 worktree,臨時目錄沒有需要清的東西。

## 讀過的檔(snapshot 的 10 支全部讀過)
1. `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md`
2. `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md`(以 cut -c1-420 截行寬讀過,正文後半以 grep 掃描)
3. `docs/lumos-toolchain-knowledge/Projects/選擇點變異平行_計劃.md`
4. `docs/lumos-toolchain-knowledge/Systems/guard-kill.md`
5. `docs/lumos-toolchain-knowledge/Systems/規格閘.md`
6. `governance/anchor-baseline.json`
7. `scripts/lumos`(全部 hunk 逐行讀)
8. `scripts/test_lumos.py`(假 Gradle 固件與 `merge=None` 測試逐行讀,其餘測試以 grep 掃描危險樣式)
9. `skills/lumos-code-loop/SKILL.md`
10. `skills/lumos-project-notes/commands/06-代碼審與推送.md`

總結:最高嚴重度 clean
