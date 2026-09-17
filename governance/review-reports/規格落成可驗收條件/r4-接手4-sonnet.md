severity: major

以下是逐節審查後的 finding 清單(凍結稿:/tmp/規格落成可驗收條件-r4.md)。

**F1(第五節/門判定規則版本,major,blocking:是)**
`_DOOR_RULE_VERSION` 的「改到哪些函式就該 bump」規則引用 S32 當綁定測試,但 S32 實際驗的是「測試篩選匹配到兩支以上」(`t_spec_gate_red_needs_exactly_one`),跟版本號 bump 條件完全無關;真正記錄 `door_rule` 的是 S33(`t_spec_gate_records_door_rule`),而 S33 也只驗「留痕裡的值等於常數」,不驗「改動觸發了 bump」。等於「代碼審看」這條規則現在零機械測試撐,且引用編號本身是錯的。
引句:「改到 `PITFALL_CLASSES`、合約行掃描、已排除規則任一支就 bump,代碼審看;S32 綁測試」
severity: major
blocking: 是

**F2(第四節/推送前檢查,major,blocking:是)**
文字承諾推送閘要抓「本次推送範圍碰到該計劃檔**或它 `lands_in` 的家**」,並說對回沿用逃逸帳同一支 `_plans_in_range`;但 `_plans_in_range`(scripts/lumos:7468)的實作只回傳提交範圍裡改到的 `Projects/*.md` 路徑,完全沒有讀 `lands_in`、也沒有比對其他檔案是否是某計劃的落點,「要動什麼」表也沒列這支函式要改。照文字實作等於只做到「碰到計劃檔」半句,漏了「或它 lands_in 的家」——例如只改 `Systems/design-loop.md`、不改計劃檔本身的推送,會漏掉本該擋的檢查。
引句:「對回用逃逸帳同一支 `_plans_in_range`」
severity: major
blocking: 是

**F3(第四節/處置閘第五步新合約草稿,major,blocking:是)**
第三節明寫單向門「計劃必須有『## 回退』節,內容 ≥20 字含實字」,且「要動什麼」表說 `_clause_check(plan, door)` 涵蓋「句式+綁定+回退節」;但打算逐字落地進 `design-loop.md` 的 ★INVARIANT★ 草稿只講句式與 `[test:]`/`[manual:]`,完全沒提回退節檢查。若草稿是未來實作者唯一會讀的合約文字,回退節這條要嘛被靜默漏掉,要嘛 S8「兩邊對同一份計劃給出相同判定」在「單向門缺回退節」這個情境下會是假的(spec-gate 擋、處置閘不擋)。
引句:「每條 `[SN]` 定義行要合一條文法、綁 `[test:]` 或 `[manual:≥4 字]`;沒標的擋」
severity: major
blocking: 是

**F4(第一節/硬單向門訊號 vs S1,major,blocking:是)**
硬單向門定義了三個訊號(關鍵字表命中、合約/風險標籤連結、作者寫 `door: one-way`),且明寫「作者寫 `door: one-way` 有意義(直接硬單向)」;但唯一對應的驗收條款 S1(`t_spec_gate_door_signals`)字面只驗前兩個訊號("命中關鍵字表任一類、或連到...節點"),整份 33 條裡沒有任何一條提到 `door: one-way` 這個作者覆寫訊號。若只照條款清單實作,作者手動升級的路徑會沒有機械測試撐住。
引句:「當計劃文字命中關鍵字表任一類、或連到帶不可逆/檢查點合約或風險標籤的節點」
severity: major
blocking: 否

**F5(第四節/S13 健檢,major,blocking:否)**
段落承諾 S13 健檢要「順便印『每份雙向門計劃的條款數與紅測試數』」,用來讓 RETIRE-IF ② 的訊號出現時分得清是規則太嚴還是沒空;但 S13 的實際條款文字只講「按門與階段分開印出放行數與逃逸數,並提醒逃逸帳有未提交列」,完全沒提條款數/紅測試數這個診斷指標。這是「設計節寫了機制但條款沒對應」的典型:RETIRE-IF ②的判讀能力寫在正文卻沒進閘。
引句:「S13 健檢要順便印「每份雙向門計劃的條款數與紅測試數」」
severity: major
blocking: 否

**F6(要動什麼/每支檔有家,major,blocking:是)**
落點段落寫「`Systems/規格閘` 管...與 pre-push 新增的『條款測試全綠』段落」,但 `scripts/hooks/pre-push` 目前的家已經是 `Systems/anchor-integrity.md`(該節點 `about_code` 明列 `scripts/hooks/pre-push`,file: `docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md:43`)。若照字面把 pre-push 也列進 `Systems/規格閘` 的 `about_code`,會撞上本 repo 鐵則五(每支檔只准一個家)、被 `node_home`/pre-commit Gate H 擋下;若不列,「管...pre-push」這句在文件層面就是錯的,新增段落實際上該記在 anchor-integrity.md 或走 `[[連結]]`。
引句:「`Systems/規格閘` 管 `cmd_spec_gate`、`_clause_check`、`_excluded_line` 與 pre-push 新增的『條款測試全綠』段落」
severity: major
blocking: 是

**F7(第四節/S28 讀側數量,minor,blocking:否)⚠**
文字說「10 處硬寫 kind 白名單的讀側」全部要涵蓋 S28;我自己數到至少三支獨立實作「輪有效」判定的函式各自硬寫 `("caught","missed","none")`(`_round_valid_m2` scripts/lumos:6362、`_panel_round_conjuncts` scripts/lumos:~6420-6426、`_loop_status_panel_clusters` scripts/lumos:~6611-6613),但「要動什麼」表只點名 `_round_valid_m2` 要同步。因為雙向門計劃(d1)本來就不派審查員、不會產生 caught/missed/none 記錄,和真實審查輪共用同一 `loop` id 的機率低,實務碰撞風險小,判不準精確是否漏了幾處,標 ⚠。
引句:「接手席數到 `scripts/lumos` 裡 10 處硬寫 kind 白名單的讀側(r3 接手席重數)」
severity: minor
blocking: 否

**F8(固定席:bound-tests-gate,minor,blocking:否,判「不影響」)**
規格閘的「紅」判準是新寫的支數解析,spec 已明確排除跟 `_ran_evidence_check` 共用邏輯的誤讀,不修改也不呼叫 bound-tests-gate 的既有機制,不影響該節點合約。
引句:「解析支數是**新寫的判準**,不是借來的」
severity: minor
blocking: 否

**F9(固定席:code-loop守衛main-direct盲區,minor,blocking:否,判「不影響」)**
推送閘的範圍計算明文沿用 pre-push 既有 push-range、不自算 merge-base,正是為了避免重開這個既有事故,不影響其合約。
引句:「range 沿用 pre-push 現有的 push-range 計算、不得自算 merge-base」
severity: minor
blocking: 否

**F10(固定席:anchor-integrity,minor,blocking:否,判「不影響」)**
本案會多次改動 pre-push(錨點檔),但流程已示範過(進度段落)要用 `lumos anchor approve` 走正規解鎖,不繞過錨點機制本身;「落地順序」8 步沒有逐步重申這件事,是流程提醒缺口而非破壞合約。
引句:「`scripts/hooks/pre-push` 與 `scripts/test_lumos.py` 都是錨點檔,這次改了」
severity: minor
blocking: 否

**F11(固定席:lumos-cli-lifecycle,minor,blocking:否,判「不影響」)**
CLAUDE.md 的改動是模板 sentinel 區塊內的一行表格,走 `lumos update` re-inject,正是該不變量允許保留 sentinel 外內容、只覆寫 sentinel 內 body 的設計路徑,不構成破壞。
引句:「跟模板第 60 行是同一句;模板改了要在本 repo 跑一次 `lumos update`」
severity: minor
blocking: 否

**F12(固定席:lumos-cli-read,minor,blocking:否,判「不影響」)**
本案完全未觸及 `search` 的 status 過濾邏輯,借用的既有機制只到 `_classify_one`、實務隱患反問與 `run_cmd`,不碰檢索濾網。
引句:「借用不自建:條款存在性檢查沿用 [[Projects/條款綁測試算進度_計劃]] 的 `_classify_one`」
severity: minor
blocking: 否

**F13(固定席:canary-audit,minor,blocking:否,判「不影響」)**
`spec-gate` 留痕沿用同一支 `cmd_canary` 寫入口,不另開路徑,readback 驗證天然涵蓋新 `kind` 值;second 判者(telemetry-only)邏輯本案完全沒觸碰,兩條 INVARIANT 都不受影響。
引句:「留痕走既有審查帳寫入口 `cmd_canary`,把 `kind` 的封閉列舉擴充一個 `spec-gate`」
severity: minor
blocking: 否

---

**已讀、無 finding 的節**:frontmatter/decisions(d1–d12 鏈路自洽,valid/superseded_by 一致)、「兩層要分開」、「為什麼」數字表(逐句核對與正文口徑一致)、第二節「條款句式」文法(逐條核對 33 條全部合文法,含 S8/S13 正確落入無條件型,無停用詞誤判)、第三節「綁定規則」kescs 三層防護、第五節逃逸自動記表格、第六節退場條件、「回退」節、「審計修正紀錄」r1–r3 統計數字(與卷證目錄結構一致)、skill/模板同步四檔(`lumos-design-loop/{SKILL.md,templates.md,reference.md}`、`lumos-project-notes/commands/{05,INDEX}`)目前確實都還沒有 spec-gate/規格閘字樣,和「還沒做」的進度陳述相符。

**條款編號/測試名檢查**:S1–S34(去 S14)共 33 條,編號連續且理由已交代(S14 併入 S2);33 個 `[test:]` 名字互不相同;S9/S10/S11/S18/S19/S20/S22 七條測試已在 `scripts/test_lumos.py` 中找到定義,與「驗收條款」段開頭聲稱的「S9–S11、S18–S20、S22 已存在且綠」完全吻合,S8 等其餘條款測試確認尚未寫,亦與聲稱一致。

---

最嚴重 severity: major
blocking 數:5(F1、F2、F3、F6,加上重新核對後 F4 我標記 blocking:否——故實際為 F1/F2/F3/F6 共 4 條 blocking:是)
