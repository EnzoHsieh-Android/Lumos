C1. `★IRREVERSIBLE★` 標記缺實質回退時，doctor `--ci` 與 `cmd_lint` 單檔版判為 error 級（硬擋） | 預期驗證點: scripts/lumos `run_doctor` Check R 區段(約 L736)、`cmd_lint`(約 L2083)；測試 `t_reversibility_guard_doctor`

C2. `★CHECKPOINT★` 標記缺回退只是 warning，不計入 issues、doctor `--ci` 下仍 rc0 | 預期驗證點: scripts/lumos `warn_soft()` 函式；測試 `t_reversibility_doctor` 斷言「只有 checkpoint 缺回退 → rc0」

C3. `★IRREVERSIBLE★` 合規判定為兩軌任一為真即放行：`[rollback:decisions]`（事後回退）或 `[guard:decisions]`（事前冪等/核可閘） | 預期驗證點: scripts/lumos `_rollback_resolved`(約 L1823) 與 `_guard_resolved`(約 L1830) 的 OR 邏輯；測試 `t_reversibility_guard_doctor`

C4. `★CHECKPOINT★` 標記不讀 guard_ref（只認 rollback） | 預期驗證點: scripts/lumos Check R 對 CHECKPOINT_RE 匹配後的處理分支，未呼叫 `_guard_resolved`

C5. 「實質回退」判定要求 ref 字面必須恰為 `decisions`，且該節點 `decisions[]` 至少 1 條非空 `rollback`（或 `guard`）內容；其他 ref 值一律視為未解析 | 預期驗證點: scripts/lumos `_rollback_resolved`/`_guard_resolved` 函式邏輯

C6. 可逆性標記走獨立平行函式 `extract_reversibility`，完全不觸碰 `extract_contracts` 的 7 個既有 callsite | 預期驗證點: scripts/lumos `extract_reversibility` 定義與呼叫點；測試 `t_reversibility_doctor`

C7. 可逆性標記僅允許出現在 `type: system` 節點；標在 Issue/Verification 等其他型別節點會被判為 error；`type` 欄位缺失或非字串不會導致崩潰或誤報 | 預期驗證點: scripts/lumos Check R 對 node type 的檢查邏輯；測試 `t_reversibility_doctor`

C8. `lumos gov` 是唯讀彙整器，讀取六個來源檔：`.bypass-log.jsonl`（L2）、`.rot-queue.jsonl`（L3）、`.governance-log.jsonl`（doctor `--ci` 寫入）、`.canary-log.jsonl`、`.kill-log.jsonl`、`.signoff-log.jsonl` | 預期驗證點: scripts/lumos `cmd_gov` 函式讀取的檔案清單

C9. `lumos gov` 的 dedup 發生在讀取時（而非寫入時），去重 key 為 `(commit, frozenset(nodes), gate, kind, token)` | 預期驗證點: scripts/lumos `cmd_gov` 內 dedup 邏輯，key tuple 組成

C10. doctor 是 `.governance-log.jsonl` 唯一的新寫入者，且只在 `--ci` 模式下 append；非 git repo 或取不到 HEAD 時跳過寫入、不報錯 | 預期驗證點: scripts/lumos `run_doctor` 對 `.governance-log.jsonl` 的 append 呼叫，需在 `--ci` 條件內；git HEAD 取得失敗的例外處理路徑

C11. `lumos gov` 預設 `--since 90`（單位天），且 `.bypass-log.jsonl`/`.rot-queue.jsonl`/`.governance-log.jsonl` 等帳檔皆列於 `.gitignore`（本機本地檔案） | 預期驗證點: scripts/lumos `cmd_gov` 的 `--since` 預設值；專案根目錄 `.gitignore` 內容

C12. Check H 僅在 `--ci` 下掃描 `git diff`，用 `IRREVERSIBLE_HINT_PATTERNS`（含 `prod`/`smtplib`/`DROP TABLE`/`requests.post`/`boto3` 等）做正則比對；命中且該節點無 `★IRREVERSIBLE★` 標記時只軟提醒、不擋（rc 不受影響） | 預期驗證點: scripts/lumos `run_doctor` Check H 區段(約 L955)、`IRREVERSIBLE_HINT_PATTERNS` 常數(約 L1751)

C13. gov 去噪規則：對 advisory 類發現（軟性/warned、無 token 無 detail），同一 `(day, gate, kind, node)` 組合跨多個 commit 會被折疊成一行並標註出現次數（×N）；同群組節點數 >6 時進一步收斂成「N 節點(前3個)…×次數」摘要行；帶 `--full` 旗標可還原逐筆輸出 | 預期驗證點: scripts/lumos `cmd_gov` 的去噪/折疊邏輯與 `--full` 旗標；測試 `t_gov_denoise`

C14. gov 對抗層增量帳：在 canary 分帳段末尾追加「折入 N 筆缺陷」統計（依 severity 分佈與審計員切分），只計入 caught 輪中對抗辯方裁決後存活的真缺陷，missed 輪不計入此統計 | 預期驗證點: scripts/lumos `cmd_gov` 中 canary 分帳段的「折入」計算邏輯；測試 `t_gov_adversarial_increment`

C15. `[rollback:]`（獨立 extractor 自剝的標籤指針）與 `decisions[].rollback`（frontmatter 實際回退內容欄位）是兩個不同的資料結構，程式實作上分開處理，未共用 `INV_TAG_RE`/`strip_test_refs` | 預期驗證點: scripts/lumos 中 `[rollback:]` 標籤解析邏輯 vs `decisions[].rollback` 欄位存取邏輯的分離；對照 `INV_TAG_RE`/`strip_test_refs` 未被觸及
