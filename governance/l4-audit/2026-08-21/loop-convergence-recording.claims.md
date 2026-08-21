C1. `lumos canary record` 指令列格式為 `caught|missed --loop <id> --severity clean|minor|major|blocker [--auditor] [--token] [--note]` | 預期驗證點: scripts/lumos cmd_canary 參數解析（loop/severity 為選用鍵）

C2. cmd_canary 寫入邏輯僅在有提供值時才寫入對應鍵：`if loop: rec["loop"]=loop` 與 `if severity: rec["severity"]=severity`；未提供則沿用舊有 ad-hoc canary 行為（不寫入該鍵） | 預期驗證點: scripts/lumos cmd_canary 內對 rec dict 的組裝邏輯

C3. `lumos loop status <id> [--need K]` 為唯讀指令，K 預設值為 2，讀取 `.canary-log.jsonl` 時依「append 序」而非依 ts 排序 | 預期驗證點: scripts/lumos cmd_loop_status 的預設參數與讀檔排序方式

C4. loop status 預設（panel）模式的 CONVERGED 判準：append 序最後 K 筆記錄（tail-K 滑動窗）須全部 `kind=caught` 且 `severity` ∈ {clean, minor} | 預期驗證點: scripts/lumos cmd_loop_status 收斂判斷邏輯；test:t_loop_status

C5. 篩選規則為 `rec.get("loop")==loop_id` 的嚴格等值比對，非模糊比對 | 預期驗證點: scripts/lumos cmd_loop_status 過濾記錄的程式碼

C6. 記錄缺少 `severity` 欄位時視同未收斂，不會被當作 `clean` 處理 | 預期驗證點: scripts/lumos cmd_loop_status 對缺 severity 記錄的判斷分支

C7. 符合條件記錄數 < K（含完全無記錄，即「還沒開始審」）時，回傳未收斂，exit code = 1 | 預期驗證點: scripts/lumos cmd_loop_status 記錄數不足時的 return code

C8. `--need` 參數有防呆下限：`need = max(1, need)`，傳入小於 1 的值會被夾到 1，且不視為參數錯誤（不會走 exit 2） | 預期驗證點: scripts/lumos cmd_loop_status 對 --need 參數值的處理

C9. loop status 輸出格式：第一行為 status 字串，接著每輪一行、以 tab 分隔的欄位順序為 `順位\tkind\tseverity\tts\tnote` | 預期驗證點: scripts/lumos cmd_loop_status 的輸出組裝邏輯

C10. loop status 的 exit code 語意固定為三種：`0`=CONVERGED、`1`=未收斂（含無記錄情況）、`2`=真錯誤（argparse 參數錯誤或檔案讀取失敗） | 預期驗證點: scripts/lumos cmd_loop_status 各分支的 sys.exit 值

C11. `cmd_gov` 的 canary mapper 在組裝 `detail` 欄位時，若 `d.get("loop")` 存在，會在 detail 最前面加上格式化字串 `f"loop={d['loop']} sev={d.get('severity','?')} · "`（放最前是為了避開後續的 `[:50]` 截斷） | 預期驗證點: scripts/lumos cmd_gov 中 canary mapper 的 detail 組裝程式碼

C12. `lumos loop status --settle <清單檔>`（opt-in 第四模式）的收斂判準為：清單全結清 ∧ G1 ∧ G3（其中 G3 要求末筆 result=現檔），且此模式與 `--panel`（預設）/`--light`/`--need`/`--min-seats` 等選項互斥，同時使用會回傳 exit code 2 | 預期驗證點: scripts/lumos cmd_loop_status settle 分支的收斂合取條件與互斥檢查

C13. settle 模式下，「caught 輪」的收緊定義為 `kind=caught ∧ auditor 非空`（比 panel 模式的定義更嚴格） | 預期驗證點: scripts/lumos cmd_loop_status settle 分支對 caught 輪的篩選條件

C14. `lumos loop status --disposal`（opt-in 第五模式，design-loop 專用）的收斂判準為四條合取：`G3 ∧ 處置集合重算(findings_set/folded/accepted 互斥+聯集+blocker 不得 accepted) ∧ 留痕 sha 重驗 ∧ quote-check 引句全錨定`；canary 的 caught/missed 不計入此合取；且與 `--panel`/`--light`/`--settle`/`--need`/`--min-seats` 互斥 | 預期驗證點: scripts/lumos cmd_loop_status disposal 分支的四條件邏輯；test:t_loop_status_disposal_gate

C15. 設計決策 d1（valid: true）：收斂排序鍵使用檔案 append 序而非時間戳 ts，理由是 ts 只精確到秒、同秒兩輪會無法定序，而 append 序唯一且天然反映時間先後 | 預期驗證點: scripts/lumos cmd_loop_status 讀檔後排序/篩選所用的鍵是否為檔案寫入順序而非 ts 欄位排序
