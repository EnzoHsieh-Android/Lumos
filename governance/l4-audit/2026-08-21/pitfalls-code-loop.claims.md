# pitfalls-code-loop 主張萃取

C1. `lumos pitfalls` 有三種模式：spec 模式（剝除對齊 assess_spec+防呆，掃 PITFALL_CLASSES 四類並印通用3問+命中類追問）、--check 模式（命中類且無「## 實務隱患」節則回傳 rc=1）、--diff 模式（掃新增行輸出 manifest+tier，rc 恆為 0）。 | 預期驗證點: scripts/lumos cmd_pitfalls 函式的三模式分支邏輯與各分支 rc 值

C2. `lumos pitfalls --diff` 輸出的 manifest 中每筆風險項目含 file、line、class、pattern、question 欄位；命中 kt/cs/vue/sql 等棧時附加 stack_questions（源自「效能檢核目錄」節點）。 | 預期驗證點: scripts/lumos cmd_pitfalls 中 --diff 分支的 manifest 建構邏輯與 stack_questions 附加條件

C3. `lumos pitfalls --diff` 輸出尾行帶 tier 分級（trivial/standard/high），三種 tier 分流三種終審路徑：trivial 跳過（commit 需註明）、standard 走單一 reviewer 終審、high 觸發 lumos-code-loop 對抗審計。 | 預期驗證點: scripts/lumos cmd_pitfalls 的 tier 判定與尾行輸出格式；lumos-code-loop 觸發條件（tier=high）

C4. `lumos pitfalls --diff` 的行號（line）由 diff 的 `@@` hunk header 推導取得。 | 預期驗證點: scripts/lumos cmd_pitfalls --diff 解析 `@@` 的程式碼段落

C5. `lumos pitfalls --diff` 排除 `governance/review-reports/` 路徑下的檔案，不將其內容納入代碼風險掃描；此排除不外溢到該路徑之外含相同內容的檔案（照掃不排除）。 | 預期驗證點: 測試 t_pitfalls_diff_skips_review_report_artifacts

C6. `lumos pitfalls --diff` 額外排除簿記帳檔案/目錄（常數 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIR`，涵蓋治理帳、usage-log、ci-log、anchor-baseline、code-loop 留痕），且此白名單常數與 code-loop 留痕失效豁免邏輯共用同一組常數定義（不得各自維護區域變數，否則會漂移）。 | 預期驗證點: 測試 t_pitfalls_diff_skips_bookkeeping_ledgers；scripts/lumos 中 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIR` 定義處，以及 code-loop 留痕邏輯是否引用同一常數（而非區域變數）

C7. code-loop `pass`/`skip` 的留痕有效性規則：留痕 sha 之後若只出現動到簿記檔案（治理帳/usage-log/anchor-baseline/code-loop 留痕）的新 commit，且該留痕 sha 仍是目標分支的祖先，則 pass 仍視為有效；只要有任何非簿記檔案的新 commit，pass 即失效；改寫歷史（rebase/amend）一律視為失效不再承認。 | 預期驗證點: 測試 t_codeloop_pass_survives_bookkeeping_commits；code-loop pass 有效性檢查函式（判斷「留痕 sha 之後的 commit 是否僅動簿記檔」）

C8. `cmd_loop_status --gate` 的 `--spec` 參數改為可選：未帶 `--spec` 時 G1 閘直接 skip（供 code-loop 吃 G2 枯竭錨）。 | 預期驗證點: 測試 t_loop_gate_no_spec；scripts/lumos cmd_loop_status 的 --gate 邏輯中 G1 判定分支（--spec 缺省時的行為）

C9. `PITFALL_CLASSES` 的四個類別名稱與 `difficulty.RISK_CLASSES` 完全相同（≡）；`_PITFALL_BLACKLIST` 與 `difficulty._BLACKLIST` 完全相同（≡）；此一致性由 test_autonomous_loop.py 中的 TestPitfallsDrift（2 條測試：類名比對+黑名單比對）作為漂移守衛，且此守衛屬 toolchain-only（非 vendored），詞表/pattern 表自帶於 scripts/lumos（difficulty.py 不 vendored）。 | 預期驗證點: test_autonomous_loop.py 中 TestPitfallsDrift 類（2 條測試）；PITFALL_CLASSES/_PITFALL_BLACKLIST 定義處（scripts/lumos）與 difficulty.py 中 RISK_CLASSES/_BLACKLIST 定義處的內容比對

C10. `--diff` 模式的風險分類軸是「代碼形態類軸」（併發/效能/資源），非 spec 模式所用的四項業務類；pattern 判定有去重疊規則：SELECT 語句歸類為效能類（N+1 疑慮），INSERT/UPDATE/DELETE 語句歸類為併發類（交易疑慮）。 | 預期驗證點: scripts/lumos cmd_pitfalls --diff 中的 pattern→class 對應表（SELECT vs INSERT/UPDATE/DELETE 的分類結果）

C11. `--diff` 模式的檔案/行過濾繼承 doctor Check H 全套規則：跳過 .md/.txt/.rst 副檔名檔案、跳過測試檔、跳過註解行。 | 預期驗證點: scripts/lumos 中 doctor Check H 的過濾函式定義，以及 --diff 分支是否呼叫/複用同一過濾邏輯

C12. `lumos pitfalls --check` 只驗證「## 實務隱患」節是否存在（節存在即通過），不驗證節內內容正確性或完整性。 | 預期驗證點: scripts/lumos cmd_pitfalls 的 --check 分支邏輯（僅檢查節標題字串是否存在於文件）

C13. panel 在 tier=high 且存在收斂中的 spec 時，會追加一個 spec-conformance 審查席位（slot），依四類判斷實作與 spec 的關係：已實作/縮水/多做/未實作；此規則記於 templates §7.5。 | 預期驗證點: lumos-code-loop 相關 templates 檔案 §7.5 段落內容；panel 組建邏輯中 spec-conformance slot 的觸發條件（tier=high 且有收斂 spec）

C14. codestage S1 規定：綁約合約（bound contract）的 pass 之前必須真跑（真執行）綁定測試，且解析測試路徑的三種優先順位（三順位）不得靜默跳過任一步。 | 預期驗證點: codestage S1 相關實作程式碼中「真跑優先」檢查點與三順位解析邏輯（解析失敗時是否會靜默跳過）

C15. 完整測試涵蓋：t_pitfalls_spec 共 9 條、t_pitfalls_diff 共 11 條（含行號值案例與併發寫入案例）、TestPitfallsDrift 共 2 條、t_loop_gate 案 14 翻契約（gate 反向案例）與 t_loop_gate_no_spec；整體回歸測試套件跑出 374 passed。 | 預期驗證點: 執行對應 pytest/test 套件，核對 t_pitfalls_spec(9)、t_pitfalls_diff(11)、TestPitfallsDrift(2)、t_loop_gate 案14、t_loop_gate_no_spec 是否存在且通過，以及整體套件是否為 374 passed
