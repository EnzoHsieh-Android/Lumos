# canary-audit 主張萃取（來源：canary-audit.note.md，協議已於 2026-08-14 停用）

C1. [現況] `lumos canary record` 指令仍存在，`kind` 選項在既有 `caught`/`missed` 之外新增 `none`（作為無植入輪的純處置帳載體） | 預期驗證點: scripts/lumos `cmd_canary`，argparse `kind` positional 的 `choices`

C2. [現況] panel／light／循序（sequential）／verify-progress／settle 五處閘的判定邏輯已明確納入 `kind=none`（不當缺失值處理） | 預期驗證點: scripts/lumos 中對應 panel/light/sequential/verify-progress/settle 五處 gate 判斷函式對 `kind` 的分支處理

C3. [現況] 有測試 `t_loop_panel_none_kind` 存在，涵蓋三向斷言：none 輪視為有效、嚴重度合取不對 none 列視而不見（不盲）、單席仍判無效 | 預期驗證點: 測試檔（如 test_lumos*.py）中 `grep t_loop_panel_none_kind`

C4. [現況] `lumos gov` 仍將 `.canary-log.jsonl` 當第 4 資料源讀取，作為唯讀彙整（歷史 caught/missed 帳可回放，不再新增判定邏輯消費它） | 預期驗證點: scripts/lumos `cmd_gov` 第 4 source 的 mapper 函式

C5. [現況] canary 工具（`cmd_canary` 本體）未被移除或拆除，只是協議（植入/判定/抽樣分權/漏抓懲罰）停用 | 預期驗證點: scripts/lumos 是否仍定義 `cmd_canary` 及其子命令 `record`

C6. [現況] `lumos gov` 的 dedup key 第 5 鑑別子使用 `r.get("token","")` 而非 `r["token"]`（避免舊三源事件無 token 鍵時 KeyError） | 預期驗證點: scripts/lumos `cmd_gov` 的 dedup key 組成程式碼

C7. [現況] `--token` 未給時，`record` 自動鑄 `CANARY-<secrets.token_hex(4)>`（使用 `secrets.token_hex`，非時間戳） | 預期驗證點: scripts/lumos `cmd_canary` 中 token 自動生成邏輯，是否 `import secrets` 並呼叫 `token_hex(4)`

C8. [現況] `record` 的資料 schema 至少含 `{ts,kind,auditor,token,note}`，另有選配欄位 `--loop`／`--severity`／`--scope-lines`／`--canary-type`／`--probe` | 預期驗證點: scripts/lumos `cmd_canary` 的 argparse 參數定義與寫入 JSON 的欄位

C9. [現況] canary 寫入自己的獨立 log 檔 `<vault.parent>/.canary-log.jsonl`，不寫入 doctor 使用的 `.governance-log.jsonl` | 預期驗證點: scripts/lumos `cmd_canary` 的寫入路徑，對照 `cmd_doctor`／`.governance-log.jsonl` 的寫入路徑，兩者應為不同檔案

C10. [歷史] 協議核心流程：工作副本偷植 1 個「純加性」canary（指向不存在章節/引用未定義詞）並給唯一 token；不告知審計員；審計員清楚且正確描述瑕疵＝caught，否則＝missed（判決作廢、換不同 canary 重跑） | 預期驗證點: skills/lumos-project-notes/SKILL.md 是否仍保留該協議文字段落（應為封存/保留但標記停用，而非仍在指示新工作採用）

C11. [歷史] v1 canary 只收純加性(additive)瑕疵，明確禁止「與另一節矛盾的需求」這類非局部型瑕疵 | 預期驗證點: `docs/design/2026-06-19-canary-audit.md` 是否仍存在此限制條款文字（保留為設計稿歷史紀錄）

C12. [歷史] panel 變體：N 個審計員各自被植入不同 canary，漏抓自己那個的席位從投票中剔除 | 預期驗證點: scripts/lumos 或 skill 文件中是否仍有 panel 變體的程式碼或文字描述（預期為僅文字描述、從未機械實作，或已隨停用不再被引用）

C13. [歷史] 2026-08-04（d4）canary 曾在 design-loop 中「降級為觀測」：missed 不再作廢該席 findings、不擋收斂；disposal 閘不消費 caught/missed；且撤銷了先前的 code-loop 排除 | 預期驗證點: scripts/lumos disposal 閘（design-loop 收斂判定）邏輯是否讀取或消費 `caught`/`missed` 欄位（依 d5 應已完全不消費，僅消費 `kind=none` 相關邏輯）

C14. [歷史] `--canary-type`/`--probe` 選配欄搭配 `canary-stats` 指令做型別×探針×caught 報表；D 案（型別輪替表，帶型別記錄攢滿 15 筆才開工）| 預期驗證點: scripts/lumos 是否仍有 `canary-stats`／型別統計相關函式（工具封存不拆，預期程式碼仍在但功能因協議停用而不再被要求使用）

C15. [歷史] `loop next` 在 plant-canary 階段印出 `scope_cap` 量尺（軟上限 1800 行/≈30K token），`canary record --scope-lines N` 超標則在帳上標記 `scope_oversize` | 預期驗證點: scripts/lumos `loop next`（plant-canary 階段）與 `cmd_canary`（`--scope-lines` 處理）中 `scope_cap`／`scope_oversize` 相關程式碼是否仍存在
