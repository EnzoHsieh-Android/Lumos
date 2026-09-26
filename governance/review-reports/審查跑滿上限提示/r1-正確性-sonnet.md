severity: major

## F1 「有無彙總帳」的判準沒排除「0 發現的合法空輪」,會誤判成「判不了」
severity: major
blocking: 是(照字面實作,會在明明可以算出建議的狀態下印「判不了,自己看」,讓「跑滿上限時給建議」這個功能的核心承諾失效)

引句:「那一輪彙總那筆帳的折入清單條數;那一輪沒有彙總帳(只有各席留痕)就印」

計劃把「有沒有彙總帳」的判準寫成「有沒有找到彙總帳那一列」,並在 S6 規定:只要任何一輪沒有彙總帳就整份印「判不了,自己看」、不給建議。但程式碼裡「沒有彙總帳」這個狀態本來就有兩種截然不同的原因,而且都合法:

file: `scripts/lumos:18366-18376` — `_loop_status_disposal` 裡 `carrier is None` 分兩種情況:一種是這輪真的沒記處置帳(印「✗ — 判定輪有發現但無處置帳」,`fails.append("無處置帳")`,判定 FAIL);另一種是 `latest and all(_fz)`(這輪每一列 findings 都是 0)→ 判成 `vacuous = True`,印「✓ — 這輪 0 條發現,沒有東西要處置(空輪;留痕仍要重驗)」,是合法通過的一輪。兩種狀態從「有沒有 findings_set 這個 carrier 欄位」上看,外觀完全一樣(都沒有 carrier),只有把該輪所有列的 findings 加總比對是否全為 0 才能分辨。

具體會出錯的狀態:某個 high 分級迴圈,r1 折入 5 條(有 carrier),r2、r3 都是 0 發現的乾淨空輪(vacuous,但因為 ⑤條款綁定或⑥資安席或⑦落點缺漏而整體 DISPOSAL FAIL),第三輪跑滿 cap=5……不,取 cap=3 示例:r1 折入 5、r2 0 發現(vacuous,因資安席缺席整體 FAIL)、r3 0 發現(vacuous,同樣原因 FAIL),third round 跑滿上限、處置閘沒過,觸發「跑滿上限」報告。這時 r2、r3 依計劃字面判準(有沒有 `findings_set` 這個 carrier)都會被歸類成「沒有彙總帳」,S6 直接判「判不了,自己看」——但實際上折入數走勢是 5→0→0,清楚在降,而且最高嚴重度也可能一路都 ≤ minor,依規則 S5 本該印「附理由放行」或「再一輪還有進展」這種有意義的建議。計劃沒有交代「彙總帳有沒有記」要不要先扣掉「findings 全 0 的合法空輪」這個情況,若照字面(只認 carrier 存不存在)實作,會把「資料完整、能判」的狀態誤判成「資料不足、判不了」。

要修:判「這輪有沒有彙總帳」時,要比照 `_loop_status_disposal` 自己的邏輯(`latest and all(_fz)`)先排除「findings 全 0 的空輪」,把它算成折入數 0、正常參與 S4/S5 的比較,而不是直接落入 S6 的「沒記處置」。

---

已看,無:出口修正(一)的重現與 r1-intake.md 記的一致——`loop next` 對已定錨的新迴圈(panel_fmt=True、ts≥2026-08-26)目前經由 `cmd_loop_status(..., gate=True, panel=True)` 委派進 `_loop_status_panel`,在 `_panel_retired_for` 為真時印「擋下:panel 閘自 2026-08-25 甲裁後僅供舊迴圈回放」並回 rc=2(`scripts/lumos:8284-8289`),`loop next` 收到 rc==2 立刻 `return 2`(`scripts/lumos:10669-10671`),完全到不了 `rounds_count >= cap` 那段判斷(`scripts/lumos:10676`)——計劃「先修出口」這個診斷成立,S1/S9 描述的分流(post-cutoff 走處置閘、pre-cutoff 照舊)在既有 `_panel_retired_for` 機制上是可行的,不會破壞既有合約。S9(舊迴圈判定路徑不變)也成立:`_panel_retired_for` 只擋 `panel_fmt=True` 且首筆 ts≥cutoff 的迴圈,pre-cutoff 迴圈的 ts 判斷會維持假、繼續回放,不受這份計劃影響。折入數/嚴重度的資料來源(`folded_set`、各席 `severity`,`_SEV_ORDER` 常數在 `scripts/lumos:7124`)與代碼審「major 一律折,accepted 必空」的既有規則(`scripts/lumos:18392`)一致,S5 的「最後一輪最高嚴重度 ≤ minor → 附理由放行」不會跟處置閘既有的放行條件打架。S7 早熔斷只讀帳本彙總列、不讀凍結審材,跟計劃「已排除:效能」的說法一致,沒發現會拖慢或誤判的路徑。條款回退段(拔掉兩處呼叫、還原判定段)對應到的正是 F1 指出的那段新邏輯,回退範圍涵蓋得到,沒有遺漏。

最嚴重 severity: major;blocking 共 1 條。
