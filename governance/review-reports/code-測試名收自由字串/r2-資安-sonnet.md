severity: clean

這輪修補我沒找到能被利用的洞。我逐行讀了 r2-repair-lumos.patch,再用關鍵字掃 r2-repair-tests.patch 和 r2-repair-docs.patch。我沒有實際執行任何程式。

**① 提示注入:已看,無。**
- 新增的擋下訊息、撞名訊息和遷移提示,凡是帶筆記或設定來的字(`_pe.prefix`、測試名、檔名、`file_name_match`),都經過 `_kill_esc`。
- 訊息只印到 stderr 或 doctor 輸出,沒有進到給 AI 的派工詞或 hook 附加段。

**② 讀寫與執行越界:已看,無。**
- **git grep:** `_test_in_tree` 的多個 `-e` 都放在 `--` 之前,pathspec 在 `--` 之後。測試名以 `-` 開頭的情形已被 `_test_name_ok` 擋掉,控制字元和換行也在 `_path_special_chars` 擋掉。就算放行,`-e` 也會把它當成樣式而不是選項。
- **regex_tail:**
  - `_name_filter_escape` 先跳脫 `.*+?^${}()|[]\` 和 `/`,再拼成 `(?:^|\s)<名>$`,最後仍由 `_run_cmd_expand` 用 shell 引號包起來。名字裡沒有任何路徑能跑出正規式。
  - POSIX 上靠 shlex 引號。Windows 上新增的 `_WIN_CMD_SPECIAL` 讓 `& | < > ^ % " !` 判為不合法。
- **file_name_match:**
  - 設定覆蓋後只做 `fnmatch` 比對檔案的 basename,不碰目錄。
  - 掃描仍走既有的 `_walk_test_files`,被限制在平台 root 底下。
  - `_anchor_migration_hint` 只在綁定已經不是真測試時才多掃一次,而且只讀檔、不執行。
- **其他:** 這輪新增的字面量裡沒有密鑰或信箱,沒有新的環境變數覆蓋點,也沒有 shell 插值。測試檔的 `subprocess.run` 用的是 list 參數。

**③ 非刻意走過守衛:已看,無。**
- **撞名判定:** 推送前閘、規格閘、`guard kill` 現在共用 `_name_collision_reason`。`guard kill` 原本沒有撞名判定,這輪補上,少了一條被意外跳過的路。
- **被跳過的綁定測試判綠:** 我找不到用一般操作就能把被跳過的測試判綠的方法。
  - Playwright 的宣告正規式現在要求字面後接逗號,`test.skip('原因')` 這類執行期標註不再被收成宣告。
  - `_RAW_TITLE_RE` 刻意放寬,連 `it.skip`、`.each` 等掃描不收的標題都計入撞名,只會判得比較嚴。
  - 不存在的名字有 `_ran_evidence_re` 擋(playwright 對不到會回 1、印 No tests found),同名但被跳過的測試沒有走出這些守衛的路。
- **guard bind/settle 共用的 `_bind_name_problem`:** 補上了 settle 原本沒有的名稱檢查,而且擋掉了多平台下含冒號的名字被誤當平台前綴的情形。
- **`_kill_method_name`:** 回頭沿用舊版剝前綴的行為,結果仍然要過 `_test_name_ok`,不會繞過檢查。
- 資源耗盡類的修補(`_C_STRIP_RE` 展開式、vitest 摘要正規式限長)歸資源席,不報。

最嚴重 severity:clean,blocking 共 0 條。
