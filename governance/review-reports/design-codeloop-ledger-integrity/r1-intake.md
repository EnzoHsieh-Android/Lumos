preflight-4: ran

# 首輪前掃（2026-10-04）

前掃席只讀計劃、原 Issue 與指名函式，檢查未定義詞、壞引用、範圍矛盾、程式語意。`refcheck` 0 missing；`prose-lint` 0 類；`pitfalls --check` 通過；`spec-gate` 判 high，六條條款句式可讀。

- 語意與邊界 1：初稿只說「共用同一把鎖」卻引用 `fcntl.flock`，與 [[Issues/治理帳多個寫入者都沒上鎖]]「沿用 `_excl_lock_try`」相反。改後明訂 `docs/.governance-log.jsonl.lock` 為唯一鎖鍵、沿用 `_excl_lock_try`、等 2 秒、900 秒視為過期、拿不到即失敗，並移除 flock 候選。此為初稿→凍結稿訂正，不作正式 finding。
- 語意與邊界 2：初稿聲稱「讀側共用」但只點三個讀者。改後逐項列出 `scripts/lumos` 內的 rewrite、doctor、gov、關門、逃逸、lint-new 與 code-loop 直接讀者；仍需正式席檢查清單完整性與成本。
- 語意與邊界 3：初稿漏掉 `_loop_gov_mark` 與 `cmd_loop_rewrite` 的「入治理帳」成功訊息。改後把 `_append_governance_log` 所有宣稱已落帳的呼叫端納入回傳值檢查，telemetry 則維持原閘判定並警告。
- 引用 4：前案分支不在本 clone；改成原登記倉庫完整絕對路徑、完整提交與卷證目錄。`git cat-file` 能在原登記倉庫解析該提交。
- 綁定 5：六條 `[test:t_codeloop_ledger_record_integrity]` 目前尚未有測試函式，`spec-gate` 報懸空但不擋；它們是實作前要新增的紅燈，不是本輪已通過的驗證。本輪審設計與最小翻紅條件，不以懸空標記宣稱測試已跑。
