severity: blocker

**逐節審查**

一、Frontmatter/decisions(d1–d8)
- Finding 1(PF-1 重驗,見下)。其餘決策內容(d1/d2/d3/d4/d5/d7)已讀,邏輯自洽,無 finding。

二、為什麼(數字表)、雙向門判定的"帳面事實"(第一節開頭)
1. 用 `lumos query --tag risk/金流` 與 `--tag risk/對外送出` 即時查證,本 repo 538 篇裡兩者皆為 **0 篇**,不是文件宣稱的「2」與「0」;`risk/守衛面`=29、`risk/不可逆`=5,與文件相符。29+5+2+0=36 本身就不等於文件寫的「40 篇」——這個「前掃訂正過」的數字既算術不自洽、也跟現場查證的即時結果對不上,實際總數是 34(29+5+0+0),恰好等於文件自己說「已訂正掉」的舊數字。
   引句:「守衛面 29、不可逆 5、金流 2、對外送出 0」
   file: `scripts/lumos`(query --tag 邏輯即時驗證,見上;無對應行號,為執行結果)
   這個數字是「預設反轉為單向門」(d8)論證的唯一實證依據,而且文件標榜是「機械數」;數字方向性的結論(稀疏、集中守衛面)即使訂正後仍成立甚至更成立,但引用的具體數字是錯的,且違反本 repo 自己的鐵則「審計紀錄數字必機械數」。
severity: major
   blocking: 是(判準:文件自稱已機械核對卻仍錯,若不修正,後續任何人拿 40/29/5/2/0 這組數字做決策或寫進圖譜決策記錄都會延續錯誤;修正成本低但必須在凍結前訂正)

三、第五節「逃逸自動記」來源收窄(PF-2 重驗)
2. 推送閘只認「受波及合約的測試沒過」型才記逃逸,把「高風險缺審查留痕」排除在外;但「雙向門判斷本該審查卻沒被審、事後在推送閘因缺審查留痕被擋」正是門判定誤判最直接的下游訊號,窄化後這型訊號永遠進不了逃逸帳。
   引句:「只認「受波及合約的測試沒過」那型;缺表態、高風險缺審查留痕這些是流程未完成,不是下游抓到缺陷」
   file: `scripts/hooks/pre-push:245`(`grep -q "受波及合約的測試沒過"` 才呼叫 `loop escape --auto`,其餘 `cl_rc=1` 分支不記)
   第六節「主要指標只有一個:每種門的逃逸率」完全靠這個來源,窄化後雙向門的逃逸率會被系統性低估,RETIRE-IF ① 可能永遠不觸發,即使真的在漏審。
severity: major
   blocking: 是(判準:直接損害第六節聲明的「唯一主要指標」的可靠性,而第六節本身是退場機制的承重牆)

四、第二節「條款句式」五型表(EARS 關鍵字綁定)
3. 表格把「狀態」型鎖死在字面關鍵字「期間」("While"),但本文自己第 S4、S12 兩條驗收條款都沒用「期間」,若按字面規則兩條都會被判「格式看不懂」——這正是本文誠實界線承諾的「自己先寫十五條驗證得出寫不出來就回頭改」的失敗案例。
   引句:「在雙向門的計劃裡,若條款帶 [manual:],則規格閘應擋下並提示綁測試或升門」
   引句:「在閘上線前第一筆帳的迴圈上,規格閘與處置閘第五步應跳過句式與門的檢查」
   引句:「在<狀態>期間,<主體>應<回應>」
   反過來,若實作為了收容這兩條而放寬「狀態」型不要求「期間」字面,則「無條件」型(`<主體>應<回應>`)的判準若不明確排除以「當/在/若」開頭的行,幾乎任何句子都能落入「無條件」型兜底,五型硬擋(d3 的核心賣點)形同虛設;`t_spec_gate_ears_shapes` 在動筆前必須先定死這個排除規則,spec 未給。
severity: blocker
   blocking: 是(判準:這是 d3「句式硬擋」的機制核心,自證失敗且無兜底規則,`t_spec_gate_ears_shapes` 現狀寫不出來)

五、第一節「硬單向門」訊號 2、雙向門「已排除」四類
4. 硬單向門訊號 1 沿用 `PITFALL_CLASSES`(內部鍵為英文 `payment`/`external-send`/`prod-irreversible`/`self-governance`,程式現行印法也是英文鍵,見 `scripts/lumos:16979` 附近 `', '.join(hits)`),但雙向門要求逐類寫「已排除:<類>:<理由>」用的是中文標籤(金流/對外送出/不可逆/守衛面),spec 未定義中文標籤 ↔ PITFALL_CLASSES 鍵的對照表、也未定義行格式的容錯(全形冒號/大小寫/多行)。
   引句:「且「實務隱患」節裡對四類各有一行 `已排除:<類>:<理由>`」
   file: `scripts/lumos:16962`(`PITFALL_CLASSES` 定義,鍵為英文)
   這正是 `t_spec_gate_twoway_needs_four_exclusions` 的核心判準,沒有這張對照表寫不出精確 parser。
severity: major
   blocking: 是

5. 硬單向門訊號 2(連到節點帶 ★IRREVERSIBLE★/★CHECKPOINT★ 合約行或 `risk/` 標籤)需要走圖節點(`related`/`lands_in`/正文 `[[連結]]`)去讀被連節點的合約行與標籤,這是 `cmd_contracts`/`IRREVERSIBLE_RE`/`CHECKPOINT_RE`(`scripts/lumos:3859-3860,4029`)這條線,不是「要動什麼」表裡寫的「借實務隱患的風險類偵測」——實務隱患的風險類偵測只掃**本文文字**,不掃連結節點。
   引句:「門判定(借實務隱患的風險類偵測)」
   file: `scripts/lumos:4029`(`cmd_contracts`,與 pitfall 掃描是完全不同的兩支既有機制)
severity: major
   blocking: 是(判準:要動什麼表只點名了一支既有機制,漏了另一支必要的,不是措辭問題而是真的漏列實作依賴)

六、第四節「推送前」條款測試全綠
6. 「推送前:同一批條款的測試必須全綠才准推」若沿用第五節同款的 diff-based 對回啟發式(`_plans_in_range`,只認**這次推送有沒有碰到 `Projects/*.md`**),典型工作流是 spec-gate 那次推送才會碰計劃檔,之後多次「只改實作程式碼、不再碰計劃.md」的推送完全偵測不到「這次推的是哪份計劃的條款」,這條新閘在最常見的場景裡永遠不會被觸發——恰好是它要擋的那種情境。
   file: `scripts/lumos:7441`(`_plans_in_range` 只匹配 `Projects/*.md` 是否出現在本次 diff)
   spec 沒有交代推送閘要怎麼反向查「這次改的程式碼屬於哪份已過 spec-gate 的計劃」,這是第四節「規格閘要紅、推送閘要綠,兩頭夾住」這句話能不能兌現的關鍵缺口。
severity: major
   blocking: 是

七、第一節門判定的兩層 SINCE 疊加(S12 與既有 `_CLAUSE_GATE_SINCE`)
7. `_disposal_clause_step` 現有 `_CLAUSE_GATE_SINCE`(2026-09-09)只決定整步跳不跳;S12 要求另一條不回溯線(閘上線那天)只擋句式+門檢查那一段,兩條 SINCE 在同一步裡疊加、順序與各自管哪個子檢查沒寫清楚。
   引句:「在閘上線前第一筆帳的迴圈上,規格閘與處置閘第五步應跳過句式與門的檢查」
   file: `scripts/lumos:15673`(`_CLAUSE_GATE_SINCE = "2026-09-09T00:00:00+08:00"`)
severity: minor
   blocking: 否(判準:實作時多加一個常數即可解,不影響能不能做,只是說明不夠精確)

八、`door:` frontmatter 欄位
8. `door: one-way` 是新欄位,現行 lint 對未登記鍵只軟提醒(`_KNOWN_FRONTMATTER_KEYS`/`extra_frontmatter_keys`),不擋;spec 的「要動什麼」表沒提到要把 `door` 登記進已知欄位清單,實作時會漏掉一步小事。
   file: `scripts/lumos:4266,4383`(`_KNOWN_FRONTMATTER_KEYS`、未知鍵只 warn)
severity: minor
   blocking: 否

九、雙向門完全不審 → skill 手冊同步範圍
9. 「要動什麼」表只提到改 `lumos-design-loop/SKILL.md` 入口與 `commands/05`,但完整流程另外兩個同樣完整描述迴圈的檔案(`templates.md` §3/§7、`reference.md`)未列入同步範圍;本 repo 自己的記憶就記過「知識同步散落會漏——機制同步只改最相關段、漏散落的列舉表/清單」,這正是同一種形狀。
severity: major
   blocking: 否(判準:不影響機制能不能跑,但會製造「手冊講的跟閘做的不一樣」的散落,屬於已知會重複發生的類別,不阻塞實作但應在同一輪處理掉)

十、其餘節落——已讀、無 finding
- 「兩層要分開」節:規格書/驗收條款分層清楚,翻譯範例具體,無 finding。
- 「三、綁定規則」除了與 F4 重疊的四類對照缺口外,雙向門禁 `[manual:]`、單向門要求「## 回退」節非空的規則本身自洽,無新增 finding。
- 「五、逃逸自動記」除 F2 外,已落地的三個來源(code-loop/CI/push-gate)、去重鍵、`_auto_escape`/`_door_for_loop` 的程式碼與 `t_escape_auto_from_code_loop`/`_from_prepush`/`_dedup` 三支測試皆存在且與文件描述一致(`scripts/lumos:7477,7495`;`scripts/test_lumos.py:31273,31315,31340,31356`),無 finding。
- 「進度」節逐項可查證:`git -c core.quotePath=false` 的坑、`lumos anchor approve` 的必要性、S9–S11 已落地皆與程式碼吻合,無 finding。
- 「六、退場條件」、「回退」、「誠實界線」三節內部自洽,誠實界線甚至提前預告了本審查抓到的部分問題(「如果實作時發現自己都寫不出來,設計就有問題」),態度誠實,無 finding。
- 「實務隱患」節:本文自證單向門(命中「pre-push hook」「anchor verify」等 `self-governance` 關鍵字),四類已排除格式雖與 F4 相關但因本文本身是單向門不受此規則約束,判「不影響」——理由:單向門路徑不要求已排除四行。

**固定席節點逐條判**
- `Systems/design-loop.md`(★INVARIANT★ 處置閘第五步):**會被修改**,spec 自己承認且承諾「要綁測試加審計」;但 S8 要求「同一份計劃給出相同判定」時,step5 目前不做句式/門判定,只做標籤存在性——擴大檢查範圍必須靠 S12 的新 SINCE 才不回溯,見 F7,設計上有交代但細節不夠。
- `Issues/code-loop守衛main-direct盲區.md`:**不影響**——理由:該事故談的是 main-direct 分支判斷邏輯,本 spec 未觸碰 `_range`/`_hrange` 判斷段。
- `Systems/anchor-integrity.md`(★RISK★):**不影響其合約**——理由:spec 進度節已示範走 `lumos anchor approve` 走正規簽名流程,未繞過。
- `Systems/每支檔有家.md`:**部分影響**——`lands_in` 只寫了 `design-loop`/新 `Systems/規格閘`,未指名 `scripts/hooks/pre-push` 新增的「條款測試全綠」段落該記進哪個既有家(pre-push 本身家在別篇),屬於 F6/F10 同類的散落風險,非阻斷。
- `Systems/lumos-cli-lifecycle.md`(re-inject INVARIANT):**不影響**——理由:`graph-discipline.md` 第 60 行改動落在 sentinel body 內,不動 sentinel 邊界,不破壞「sentinel 外 byte-equal」合約。
- `Systems/測試假綠形態.md`:**不影響**——理由:spec 要求「至少一支紅」正是在防同型態假綠,方向一致,未違反。
- `Systems/bound-tests-gate.md`:**不影響**——理由:spec-gate 步驟四沿用 `.lumos/config.json` 的 `run_cmd`(`scripts/lumos` 內已驗證存在),與現行 bound-tests 執行模型相容。
- `Systems/canary-audit.md`:**不影響**——理由:`_auto_escape`/`spec-gate` 留痕走 `.canary-log.jsonl`/`.escape-log.jsonl` 既有 append 機制,未改動 record/second 的成功語意。

**實務隱患鏡頭(逐類)**
- 併發:無新增風險——理由:留痕沿用既有 `.canary-log.jsonl`/`.escape-log.jsonl` 的 append-only 寫法(`_jsonl_append_verified`),未引入新的共用可變狀態。
- 效能:無——spec 自己在「已排除:效能」已排除,且步驟四只跑綁定測試不跑全套,合理。
- 資源:無——spec-gate 只讀計劃、跑既有 `run_cmd`,未新增檔案控制代碼/連線/worktree 之類長壽資源。
- 回滾:見 F7——兩層 SINCE 疊加沒寫清楚順序,回滾時(RETIRE-IF ①觸發)哪些欄位/哪些迴圈的判定要一起退回未定義,屬於遷移順序問題的延伸,已計入 F7。
- 遷移順序:見 F6、F7——推送閘新增條款何時開始生效、跟哪次 spec-gate 留痕綁定的先後關係,是本輪最大的實作缺口。

**結論**
最嚴重 severity:blocker(1 條:Finding 3,五型句式表與本文自身驗收條款矛盾,`t_spec_gate_ears_shapes` 判準未定);blocking 共 6 條(Finding 1、2、3、4、5、6)。
