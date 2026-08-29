# r2 補錄:邊界與失敗路徑席(報告晚於彙總記帳送達)
severity: blocker

★本檔為附錄,不改動已記帳的 r2-summary.md(留痕 sha 不可動)。★
該席 2 blocker + 8 major(blocking 8),全部併入 r2 折入集。

## 兩個 blocker
- **F9 範圍口徑自打架(最狠一條)**:`pitfalls` 明文排除 `governance/review-reports/`(scripts/lumos:13207,註解寫明歸檔席報告/快照 .patch 裡**故意埋著 bug**)與測試檔(:13214);`impact` 種子過濾只排除 `docs/` 與 `governance/golden/`(:15549)。合印一份輸出=上半段當該檔不存在、下半段拿它當證據。實測 b5d0735..HEAD 排名第一、score 1.0、kind=incident、必掛★的節點,唯一來源就是 `code-toolfix/r1-snapshot.patch`。
- **F1 vault-free 破約**(與整合 F1、因果 F4 同源,三席獨立命中)。

## 值得記的 major
- **F8 截斷切點落在同分帶**:固定席排序 `(-score, node)`,實測第 4~10 名分數全等於 0.7 → 誰進前 8 由**檔名字母序**決定;spec 舉例的 `Systems/測試假綠形態.md` 實際會被切掉。
- **F7 「還有 N 篇一般的」會少報**:非固定席在 :15646 已被 top(預設 8)截斷,真實數在 `meta.free_total`;實測 free_kept 8 / free_total 20,12 篇無聲蒸發。
- **F5 空結果措辭產生假安心**:既有空句「圖譜對此 diff 無覆蓋」接在「牽連到這些筆記」標題下,讀成「沒牽連=安全」。實測直接編輯圖譜的 commit 也回這句(.md 在種子過濾被剔)。
- **F6 讀不到的筆記靜默消失**:chmod 000 後該節點從清單消失、rc 仍 0、零警告——「我沒去看」與「看過沒有」印成同一句。
- **F11 pre-push 已在跑 impact**:`:112` sync_nudge 每 ref 無條件跑;新 ref 首推 range 有 155 種子檔,實測 **101.81s**;旗標若漏加,tier=high 同 range 會跑兩次 ≈200s。
- **F3 退場門檻設計階段已踩線**:典型帶內抽 10 個真實 range,2/10 超過 10s;48 檔 range 12.3s。
- **F10 同步清單漏 `scripts/hooks/pre-push`**(錨點檔,改它要 anchor approve)。

## 該席查核通過
`--json` 與人可讀確實乾淨分家(collect 後早退);兩個機器消費者都走 collect/--json 不受波及;impact 確實不寫檔;三個 pre-push 行號正確;★圖例與 pinned 定義一致。
