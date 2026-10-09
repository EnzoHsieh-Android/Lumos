severity: major

## 唯一發現：試行計劃誤成為兩個實作系統的第二個 owner

severity: major  
blocking: 是

引句:「入口與細則放入代碼審 skill 及其 reference；決策脈絡歸 [[Systems/pitfalls-code-loop]]。本計劃只存本 repo 試行登記與回顧，其他專案沿用原流程。」

精確情境：正文把落點限定為 code-loop，但 frontmatter 額外列入 `Systems/codex-harness` 與 `Systems/測試假綠形態`：`docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md:11`。這不是無害標籤：

- `spec-gate` 會從 `lands_in` 抽取 Systems 合約並執行其綁定測試：`scripts/lumos:6130`。
- 推送前只要改到某個 Systems 或其所管程式，所有指向該 Systems 的 doing 計劃都會被拉進 gate：`scripts/lumos:6489`。
- 小改動閘也把 `lands_in` 所管程式視為本計劃的合法實作範圍：`scripts/lumos:6589`。

因此，一次與本試行無關的 `scenario_probe.py` 維護，會因 `codex-harness` 被列為落點而拉入這份試行計劃；改 `test_lumos.py` 也會把「測試假綠」合約與回歸測試帶進來。這份流程試行於是跨層成為平台探針與測試方法的第二個 owner。現行 `codex-harness` 自己也明定不負責其他機制內容是否正確：`docs/lumos-toolchain-knowledge/Systems/codex-harness.md:6`。既有落地驗證則明確只認 `Systems/pitfalls-code-loop` 為系統落點：`docs/lumos-toolchain-knowledge/Verification/2026-10-03_代碼審修復穩定性試行落地.md:27`。

最小修正：把 `lands_in` 收回只剩 `Systems/pitfalls-code-loop`。歷史第1案對探針與測試的影響保留在既有 Verification／Issue 血緣，不要以 Systems `lands_in` 或正文 Systems 連結掛回本計劃。後續被抽中的程式工作仍由該工作自己的計劃與 Systems 家負責落點。

## 已讀且無發現

- S1：入選條件、最多四個後續工作、中止仍占名額與樣本邊界完整。
- S2：根因合併、改變／保持行為、壞例與好例、失敗路徑均與現行 reference 一致：`skills/lumos-code-loop/reference.md:126`。
- S3：同例前後版的四分類與既有 code-loop 嚴重度、處置規則沒有衝突：`skills/lumos-code-loop/reference.md:129`。
- S4：原席窄驗、新席全量查副作用、正式凍結材料、必派席及三輪上限均維持：`skills/lumos-code-loop/reference.md:128`、`skills/lumos-code-loop/SKILL.md:59`。
- S5：既有 `--intake` 可綁定內容雜湊，處置閘會跨輪重驗，沒有另造證據格式：`scripts/lumos:8431`、`scripts/lumos:19768`。
- 收斂性診斷：多入口小表是 S2/S3 的限域展開，未另加全域 gate。
- 試行登記：沿用五格表與既有 intake；未重引候選表、領號器或跨工作樹鎖。
- Pending design gate：目前 `review-repair-pilot-decouple-slim` 機械查詢確為零筆紀錄；圖譜也明列規則尚未生效：`docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:16`。
- 歷史 FAIL：第1案第四輪及正式探針第三輪均未被後續 PASS 或綠測試覆寫：`docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:28`、`docs/lumos-toolchain-knowledge/Verification/2026-10-04_消融派工正式審查修正.md:38`。
- 證據、耗時與觀測窗：未知值、牆鐘口徑、14 天成熟度及不可覆寫 intake 的界線清楚。
- 回退：保留既有證據與帳本、停止試行但不替工作放行，符合 append-only 證據模型。
- 審計修正紀錄及第1案歷史：沒有把診斷輪、樣本外儀器修補或例外第四輪重算成第2案。
- PRIOR-ART：Google 確實支持自足的小變更、相關測試與較易回退；Fowler 也以小步、測試與行為保持描述重構。提案沒有把兩者冒稱為本試行成效證據。[Google Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)、[Martin Fowler](https://martinfowler.com/articles/refactoring-external-service.html)

最高等級：major  
blocking count: 1
