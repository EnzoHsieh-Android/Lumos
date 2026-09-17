severity: blocker

## 逐條 Finding

**F1**
severity: blocker
blocking: 是
spec 第四節「新閘 `lumos spec-gate`」與 design-loop ★INVARIANT★ 落地新文字草稿。
問題:新草稿要求「測試存在」才算過,但現行 `_disposal_clause_step`/`clause_bindings`(懸空 dangling/unrecognized/mentioned)只印一句提醒、不擋、照樣回傳 `"ok"`,而且 test_lumos.py 裡對這個「懸空→只提醒照過」行為明文釘了翻紅釘測試;spec 沒交代 `_clause_check(plan, door=one-way)` 是否要保留這條既有寬鬆行為,implementer 兩種寫法字面上都能通過 spec,但一種會靜默改掉固定席 `Systems/design-loop` ★INVARIANT★ 的既有語意(既有測試變假綠或直接翻紅)。
引句:「測試存在且名字互異;不合文法印『格式看不懂』;判定與 `lumos spec-gate` 同源」
file: `scripts/lumos:15792-15801`(懸空只提醒不擋、無論如何回 "ok")、`scripts/test_lumos.py:5397` 附近(docstring 明寫「懸空→只提醒照過」為翻紅釘鎖定的行為)。

**F2**
severity: major
blocking: 是
spec 第四節「留痕」段。
問題:文字自承「至少 9 處硬寫 kind 白名單的讀側,落地時逐處決定」,但接著標的綁定測試是「S23」——S23 實際定義是「已排除行不在實務隱患節或類名不在四類時照掃」(與 kind 白名單完全無關),真正處理 `_round_valid_m2` 的是 S28;grep 出的 10 處硬寫 kind 白名單讀側(`scripts/lumos:5315,6060,7176,7235,7302,7403,7854,7863,7891,8823`)裡,只有 `_round_valid_m2` 這一處被 S28 覆蓋,其餘 9 處毫無驗收條件也毫無正確的測試錨點。
引句:「接手席數到 `scripts/lumos` 裡至少 9 處硬寫 kind 白名單的讀側,落地時逐處決定(計數型排除、判定型忽略),S23 綁測試。」

**F3**
severity: major
blocking: 否
spec 第四節「留痕」段與第六節「計數口徑寫死」段。
問題:`door_rule` 版本號兩次被寫成留痕欄位與第六節退場計數的依據,但 27 條 `[S]` 條款裡沒有一條約束它的寫入時機、格式或遞增規則,也沒有任何測試名——本案自己在第二節主張「翻不成句式的是指引不是條款」,`door_rule` 這兩段正是描述了行為卻沒被翻成條款的指引,卻被拿來當機械退場門檻的分母依據。
引句:「每筆留痕帶 `door_rule` 版本;門判定規則改版 → 從零重數 30 份」

**F4**
severity: major
blocking: 否
spec 第六節「撤除條件」與 decisions d12。
問題:d12 明講逐條嚴重度沒給時「退回輪級判準並在逃逸帳標 `precision: round`」,且承認輪級判準會把一條 spec 型 major 配一條 code 型 minor 誤記,但第六節的三個絕對門檻(blocker 一份即退、前 30 份 major≥3)完全沒提 `precision: round` 的記錄算不算數;一次低精度誤配就可能觸發整套雙向門機制被撤回,接手的人無從決定要不要把這類記錄剔除。
引句:「前 30 份雙向門計劃裡 major 以上逃逸 ≥ 3 份(10%)→ 退回」

**F5**
severity: major
blocking: 否
spec「回退」節。
問題:CLAUDE.md 鐵則四要求「承認風險要附回頭看的條件」,本篇其他未定事項都掛了 `REVISIT:2026-10-17`,唯獨「回退基準 sha:(待填)」這個佔位字串沒有對應的 REVISIT 或 doctor 檢查;r1/r2 兩輪就是因為「沒有錨的原本那一版會變成猜」才加這一格,結果新格子本身又沒有防止被遺忘的機制,S8 落地時若忘了填,沒有任何機制會唸。
引句:「落地那次提交的 sha 落地時填進這裡」

**F6**
severity: minor
blocking: 否
S21 與第二節文法規則。
問題:S21 在同一條款裡塞了兩個判準——「當推送前檢查時」的觸發,加上句尾「任一紅即擋」這個未帶觸發詞、也未用「應」字(用「即擋」)的第二個隱性條件,違反第二節自訂的「一條條款只准一個觸發子句;複合觸發…一律拆成兩條」;機械檢查只認開頭觸發詞,不會抓到句中埋的第二個條件,正好示範句式檢查「驗形狀不驗意思」的自陳限制。
引句:「推送閘應對本次範圍碰到且仍 doing 的雙向門留痕裡的測試清單全跑,任一紅即擋」

**F7**
severity: major
blocking: 否
spec 第四節「推送前」段與驗收條款 S25。
問題:S25(`t_spec_gate_keeps_bypass_rejected`)判準要靠 `git log -S"def <測試名>" --diff-filter=A --format=%ad` 讀真實 git 歷史,跟 S21 同樣依賴真 git 沙盒,但文中只對 S21 明講「這支測試要建真 git 沙盒…比其他條款重,寫明」,對同樣需要真實 git log 的 S25 隻字未提,同一份文件對同類測試成本採了兩套標準。
引句:「這支推送閘的測試要建真 git 沙盒(本 repo 有先例),比其他條款重,寫明」

## 固定席逐條判(會不會破壞其宣稱的行為/合約)

- `Systems/design-loop`(★INVARIANT★ 處置閘第五步):**會影響**——見 F1,新 INVARIANT 草稿要求「測試存在」跟現行「懸空只提醒不擋」的既有測試釘子沒有交代如何相容。
- `Systems/bound-tests-gate`(★INVARIANT★ code-loop 逐支真跑):**不影響**——spec-gate 的存在性檢查沿用 `_clause_bindings_for`(處置閘第五步既有那支),跟 bound-tests-gate 驗證 code-loop 合約行是不同呼叫路徑,兩者不互相覆寫;`scripts/lumos` 裡兩支函式互不呼叫。
- `Systems/lumos-cli-lifecycle`(★INVARIANT★ re-inject 只覆蓋 sentinel 之間):**不影響**——本案沒有動 CLAUDE.md 的 re-inject 機制,只是改了模板裡表格的一行文字,走既有 `lumos update` 流程。
- `Systems/lumos-cli-read`(★INVARIANT★ search 排除 superseded):**不影響**——本案沒有改 search/濾網邏輯。
- `Systems/測試假綠形態`(★INVARIANT★ 修 bug 要配翻紅釘):**有關聯但未違反**——本案自己也強調要先紅後綠、翻紅釘;唯一風險是 F1 指出的那個交界點若沒人補翻紅釘,會正好落進這條 INVARIANT 想擋的「第④型」空洞。
- `Issues/code-loop守衛main-direct盲區`(status: done):**不相關**——該盲區已用 push range 取代 merge-base 修掉,S21 的範圍問題是新的、不同的隱患。
- `Systems/anchor-integrity`(★RISK★):**不影響設計本身**——pre-push 改動走既有 `anchor approve` 流程,spec 未改動錨點判定邏輯。
- `Systems/每支檔有家`:**已滿足**——`lands_in` 列了 `Systems/design-loop` 與新開 `Systems/規格閘`,兩支要動的檔都有家可歸。

## 逐節閱讀狀態

- 為什麼(數字表)、兩層要分開、一(門怎麼判)、二(條款句式,除 F6)、三(綁定規則)、五(逃逸自動記,除 F4)、進度、要動什麼、實務隱患、誠實界線、審計修正紀錄:已讀,無 finding。
- 四(新閘):F1、F2、F7。
- 六(退場條件):F3、F4。
- 回退:F5。
- 驗收條款(S1–S28):F1、F2、F6、F7 之外的條款照文法讀順,句式合法。

## 最後一行

最嚴重 severity:blocker;blocking 計 2 條(F1、F2)。
