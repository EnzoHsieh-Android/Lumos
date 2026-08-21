# lumos-cli-write claims（階段一萃取）

C1. `scripts/lumos` 的專案層圖譜寫入原語表格列出 7 個子指令(對應 cmd_*):set / append / self-audit / decision-add / decision-supersede / new / archive | 預期驗證點: scripts/lumos 原語總表 / CLI dispatcher 子指令清單

C2. 2026-08-11 新增第 8 個寫入原語 `remove <note> <key> <value>`,是 append 的逆操作,用來移除 list 項(T1 list 項移除) | 預期驗證點: scripts/lumos cmd_remove

C3. `set` 子指令的純量白名單 SCALAR_KEYS = {status, updated, created, type, self_audit, signed_off, regen} | 預期驗證點: scripts/lumos SCALAR_KEYS 常數

C4. `append` 子指令的清單白名單 LIST_KEYS = {verified_by, plan_refs, related, tags},且 2026-08-11 起將 core_refs 也納入 LIST_KEYS | 預期驗證點: scripts/lumos LIST_KEYS 常數

C5. 呼叫 set/append 時若 key 不在對應白名單內,直接回傳 rc=2(拒絕寫入) | 預期驗證點: scripts/lumos cmd_set / cmd_append 的白名單檢查與回傳碼；t_append_block_key_rejected

C6. 所有 frontmatter mutation 都經過 atomic_write_verify(path, new_lines, key, expected_check) 四步驟:寫入 `.lumos-tmp` → re-parse 新 frontmatter 並跑 expected_check 斷言該 key 真的寫成目標值 → 比對 lint 指紋(new_lint - orig_lint 必須為空,不准引入新指紋)→ 全過才 `os.replace` 原子換入;任一步失敗丟 RuntimeError、tmp 丟棄、原檔零變動 | 預期驗證點: scripts/lumos atomic_write_verify

C7. `load_raw_for_edit` 讀取 raw bytes 時拒絕 BOM、拒絕 CRLF,不做靜默正規化,遇到異常直接報錯 | 預期驗證點: scripts/lumos load_raw_for_edit

C8. `_write_lf` 是唯一的檔案寫入原語,用 write_bytes 強制輸出 UTF-8/LF/no-BOM,不依賴 text mode 或 Python 3.10 的 newline= 參數 | 預期驗證點: scripts/lumos _write_lf

C9. `append` 對多個 wikilink 的 dedup 比對邏輯使用 `link_target()` 函式,結構性保證一項一行寫入 list,不會把多個 [[]] 字串串接進同一值 | 預期驗證點: scripts/lumos link_target, cmd_append

C10. `remove` 的比對邏輯同樣沿用 `link_target()`(精確 target 比對,不做前綴/basename 匹配);未命中時一律回傳 rc=2,不會靜默 no-op 後回傳成功 | 預期驗證點: scripts/lumos cmd_remove

C11. `remove` 清空某 list key 的最後一項後,會將整個 key 行一併移除,而非留下裸鍵(裸鍵會被 YAML 解析成 null) | 預期驗證點: scripts/lumos cmd_remove 空清單處理邏輯

C12. `decision-add` 指派新決策 id 為 `d<max+1>`,且該 id 一旦分配後(即使後續翻案)永不重用 | 預期驗證點: scripts/lumos cmd_decision_add ID 指派邏輯

C13. `decision-supersede` 用內容子字串比對命中目標決策;若命中多筆則回傳 rc=2 並列出候選,可用 `#dN` 精確定址單一決策 | 預期驗證點: scripts/lumos cmd_decision_supersede 命中/多重命中分支

C14. `decision-supersede` 對已經帶有 `superseded_by`(已被 supersede 過)的決策拒絕重插,避免重複鍵 | 預期驗證點: scripts/lumos cmd_decision_supersede 重複 supersede 檢查

C15. decision-* 系列要求 decisions 區塊為標準 2-space 縮排;遇到 0-indent 或 tab 縮排的 decisions 區塊會直接報錯,不自動處理/不靜默轉換 | 預期驗證點: scripts/lumos cmd_decision_add / cmd_decision_supersede 縮排解析邏輯
