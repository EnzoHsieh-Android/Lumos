severity: minor

## delivery-資安-security-controls-codex-F1：新增 waiver 的撤回條件沒有進入機械判定

severity: minor  
blocking: 否

引句:「並在測試家寫回計劃綁2026-10-20重驗；超過52就撤回這筆精確放行。」

觀察：本批新增的 waiver 宣稱只放行複雜度 52，超過便撤回；但告警指紋只雜湊規則、檔名及命中行的程式片段。Ruff 複雜度通常命中函式宣告，因此只增加函式內分支而不改宣告時，指紋仍相同。載入與過濾邏輯只看 key 是否存在，不解析 reason、日期或複雜度上限。之後 `_nodehome_evaluate` 增至 53 以上仍可能被靜默豁免。

本批新增：是；262 筆變為 263 筆，唯一語意新增是 key `36c23613f0cfca05`，其餘 waiver 變化只是 JSON 欄位排序。

file: `scripts/lumos:27752`  
file: `scripts/lumos:27796`  
file: `scripts/lumos:27822`  
file: `scripts/lumos:28043`  
file: `docs/lumos-toolchain-knowledge/Projects/已宣告測試家的同次寫回_計劃.md:125`

建議：讓 waiver 帶可驗證的 `max_complexity`／`expires_at`，或把函式體內容指紋納入此類 C901 waiver；補一例「宣告不變、複雜度升至 53」必須重新被擋的測試。因已有接電的 2026-10-20 `REVISIT`，且利用路徑仍需有人提交函式內變更，故定為 minor。

## 已讀分節

- waiver：完整做 base/HEAD 語意比較；除 F1 外無 finding。
- anchor：完整讀取該 hunk；`scripts/test_lumos.py` 實際 SHA-256 與新 baseline `35b3a866…` 相符，無 finding。
- replay：讀取四份完整 JSON 物件；皆有凍結時間、spec/report/snapshot 雜湊與 `verdict.rc=0`。依派工限制未開其他席報告內容，未發現本 patch 自身的不一致。
- canary/governance/escape/kill journal：只完成部分語意 delta，未在已讀部分發現新 finding；覆蓋不足，不能宣稱此節完整 clean。

## 圖譜固定席逐條判定

- `Issues/canary-record未落盤事件`：影響；新增 canary/kill/fix-check 帳目，但未改落盤程式。已讀部分無 finding。
- `Systems/lumos-cli-read`：不影響；沒有更動 search 過濾行為。
- `Systems/design-loop`：影響；新增四份 replay verdict，且四份 `spec_path` 都是 `.md` 計劃，未違反鏡頭合約。
- `Systems/pitfalls-code-loop`：影響；新增 lint waiver，對應 F1。
- `Systems/bound-tests-gate`：不影響；未改合約測試執行或 blocked 判定。
- `Systems/guard-kill`：影響；追加 kill 帳，但未改 rc 優先序或 JSON 輸出。
- `Systems/授權與歸屬`：不影響；無授權檔、vendoring 或 deinit 白名單變更。
- `Systems/測試假綠形態`：影響；更新測試檔 anchor。雜湊相符，但本席未執行測試，不能由 anchor 推論測試殺傷力。

鏡頭只列名的節點：

- `loop-convergence-recording`：影響；追加審查帳及 replay。
- `lumos-cli-lifecycle`：不影響；無 CLI lifecycle 控制變更。
- `reversibility-governance-ledger`：影響；追加 governance/escape 日誌。
- `lumos-deinit`：不影響。
- `節點範圍與索引守衛`：不影響控制程式；只有測試 anchor 更新。
- `check-t-sentinel`：不影響。
- `doctor-irreversible-hint`：不影響。
- `check-r-guard`：不影響。
- `cochange-guard`：不影響。
- `lumos-refcheck`：不影響 refcheck 行為。
- `canary-audit`：影響；新增 canary 帳與 replay。
- `slim-get-一行安裝`：不影響。
- `slim-install-安裝器`：不影響。
- `slim-uninstall-一行卸載`：不影響。
- `雙向門放行_計劃`：不影響放行規則。
- `規格落成可驗收條件_計劃`：影響；新增凍結 verdict，未改判定器。
- `引用座標依實際換行_計劃`：不影響。
- `逃逸自動記_計劃`：影響；追加 escape 日誌，未改自動記邏輯。
- `異常派工單回報輸入錯誤_計劃`：不影響輸入驗證。
- `core-invariant-baseline`：影響；更新一支測試檔 anchor，實際雜湊相符。
- `judge-severity-gate`：影響帳面 severity/replay，未改 gate 行為。

## 覆蓋與限制

- 固定 HEAD：已核對為 `c09d12037d1f0d5a5ce92bd09ccda1ed048a2319`。
- 規則：完整讀 265 行；另因首次輸出截斷重讀 `lumos-code-loop` 70 行。
- 鏡頭：57 行完整讀；曾有一次截斷後重讀。
- raw patch：完整逐行讀 `1–150`；另定點核對 `2784–2785`、anchor hunk及四份 replay 物件。
- 搜索與索引：約 730 行可見輸出；一次過寬的 name-status/hunk 查詢意外回傳 642 行，使總耗用連同派工與規則超過 1800 行上限。
- 未讀：`controls.patch` 大部分 raw journal 區與 waiver 排序區未逐行閱讀；waiver 已改用完整 base/HEAD 語意比較補足。`journal-semantic-delta.txt` 第 101–251 行未讀，前 100 行亦有單行過長造成的工具截斷。因此本報告不是完整 clean 驗收。