severity: minor

這份 diff 大致沿用專案既有做法,沒有引入第二種做法,也沒有跨層直呼。有一處判定規則另寫了一小段,列為 minor。

severity: minor
blocking: 否 — 這是 vault-free 的字串版判定,寧可多算,而且底層沿用 `_vault_slug_of`;「圖譜在 docs/knowledge/」也有既有佈局可對照,不是另一套互斥規則
引句:「if _vault_slug_of(rel) is not None or rel.startswith("docs/knowledge/"):」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos:44845`(`_vault_slug_of`,三個讀者共用的「路徑是不是圖譜」判定);file: `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos:26340`(`_vault_in` 認 `docs/knowledge`)
判定理由:`_residual_graph_file` 以 `_vault_slug_of` 為主,另外補兩條:`docs/knowledge/`,以及「`.md` 且路徑段含殘留指標的頂層資料夾」。前者在 `_vault_in` 有同樣的佈局先例。後者是新規則,只用在「舊索引不知道決策在哪篇」這條寧可多算的分支。`_vault_slug_of` 目前不認 `docs/knowledge/`,所以這個函式不能直接被取代,但三處佈局判斷可以收攏。這是一致性的小債,不是第二套做法。

## 逐項檢查

1. **`notes` 欄寫法**:欄位寫在 `_residual_index_entries`,比對鍵在 `_residual_index_row_key`,差異報告的 `names` 元組也同步加了 `notes`。三處和 `residuals`、`about_code`、`test_files` 走同一條路徑,沒有另開讀寫路。這欄的型別是 dict,其他欄是 list。比對時轉成排序後的元組,舊索引沒有這欄也讀得進來。
2. **deadline 傳遞**:`_lens_residual_section` 吃的 deadline 是 `_t0 + _LENS_INNER_BUDGET - _LENS_FALLBACK_RESERVE`,和 `_lens_extcode_section` 同一個算法。逐次 git 呼叫前先夾剩餘秒數,不足 1 秒就停,也和既有寫法一致。
3. **`_residual_blob_at` 讀某版檔案**:現在改包 `_lens_git(binary=True)`,和 `_lens_residual_decision` 的 `_lens_git("show", ...)` 是同一個入口。殘留相關的讀版本只剩這一種寫法。`ls-tree` 的 missing 分辨是這支多出的一層,文件註解有講明。`_git_env_no_replace` 與 `no_replace` 參數已全數移除,grep 沒有殘留。
4. **入口清 git 環境**:`main()` 開頭統一設 `GIT_NO_REPLACE_OBJECTS`、`GIT_GRAFT_FILE`,並移除 `GIT_DIFF_OPTS` 與 `GIT_EXTERNAL_DIFF`。這個分支沒有逐呼叫的另一套(例如 `env=`)。`_diff_range_ends` 與 `_residual_tier_hits` 的 `env=` 都已拿掉。

最高等級 minor,blocking 0 條。
