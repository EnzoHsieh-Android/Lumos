severity: major

## 逐節閱讀記錄

**Frontmatter / summary**:已讀,無 finding——三行 KEY 摘要與內文條款(S1–S6)所述機制一致,`decisions` 欄的 d5/d6 已存在(下方會指出這兩筆決策內容本身與本 spec 的規則矛盾,見 A3)。

**緣起**:已讀,無 finding——「190 份派工單 8–9 個帶安全味鏡頭」「9 個消費專案零資安鏡頭」這類否定式盤點宣稱,summary 已註明「我查一次、另一個乾淨 agent 用原始問題獨立再查一次,兩邊一致」,滿足 CLAUDE.md 對「要說沒有/缺」類斷言的雙源查證鐵則,不要求審稿人重跑歷史語料掃描去覆核。

**人裁(三問三答)/PRIOR-ART**:已讀,無 finding。

**[S1] 編制表**:見 A1(家族選擇未交代)、A2(會打翻既有測試)。

**[S2] 處置閘步驟**:見 A3(命名與已入庫的圖譜決策矛盾)、A4(訊息格式與同層步驟不一致,minor)。凍結/回放那段(不重讀報告檔、只看帳列)邏輯我對照 `cmd_loop_replay` 的兩段式凍結/回放呼叫(`scripts/lumos:634-649`、`:792-794`)驗證過,`files` 字典只收判定輪路徑、`_disposal_clause_step` 的 `spec_sha_override is not None` 分支確實不重讀活檔——這段跟現有 `_disposal_clause_step` 的凍結豁免同構,設計合理,無 finding。

**[S3] 生效日**:已讀,無 finding——`_CLAUSE_GATE_SINCE`/`_loop_ts_key` 比對寫法(`scripts/lumos:4388`、`:6625`)與本條款描述一致,格式套用正確。

**[S4] 派工範本內容**:已讀,無 finding——XXE/JWT/PII 皆有隨文解釋,「不報」與「附料」邊界跟 d4(`--no-lint` 恆跳過 lint)不衝突。

**[S5] skill 說明同步**:見 A5。

**[S6] 決策落地**:已用 `lumos decisions Systems/pitfalls-code-loop` 實跑驗證——d5 已標 `superseded_by: d6`(❌ 圖示)、d6 為 `valid: true`(✅ 圖示),`[manual:]` 可執行、結論屬實。但 d6 決策內容本身的文字有問題,見 A3。

**邊界與不做 / 承認的限制**:已讀,無 finding——四條 REVISIT 格式(`REVISIT:YYYY-MM-DD 一句話`,獨立行、緊鄰原句)逐條核對過 `scripts/lumos` 的 E5 解析邏輯(`scripts/lumos:1877-1921`,判準是 strip 後以 `REVISIT:` 開頭且不是表格行),四條全部合規。

**實務隱患**:已讀,無 finding——實際跑了 `python3 scripts/lumos pitfalls --check` 對這份 spec,確認命中類別正是 `payment / external-send / prod-irreversible`;逐一查了觸發字來源(「金流」出現在 REVISIT 審計項舉例與排除理由自身、「對外」出現在人裁選項描述、「遷移」出現在可逆性與排除清單自身),三個都是關鍵字誤命中而非真實金流/外送/不可逆改動,排除理由站得住。

**驗收**:見 A2(既有測試會翻紅)。

---

## Findings

### A1

severity: major
blocking: 是

引句:「同門(相對於編排者,Codex 編排時就是 Codex 子代理)、不佔 W」

[S1] 把「資安」席宣告為跟編排者「同門」,但同一個 `("code","high")` 編制表裡本來就有「外家finder」「外家否決」這組 `required-fail-closed` 席,專門解決「同門盲點」——file: `skills/lumos-design-loop/templates.md:53` 明文「判決單點最怕同門盲點」,file: `scripts/lumos:7629-7630` 顯示這正是外家finder/外家否決被設成 fail-closed 的理由。資安審查恰恰最需要對抗式的攻擊者視角(spec 自己在 [S4] 也要求「每條發現必附攻擊路徑」),spec 全篇沒有一句話交代為什麼這個最需要跳出同溫層的鏡頭反而選了同門,不改的話實作者會複製一個看起來合理、實際上重演了外家席想解決的那個問題的設計。

### A2

severity: major
blocking: 是

引句:「既有測試:roster / disposal / loop_next 相關子集全綠。」

這句宣稱不成立:file: `scripts/test_lumos.py:27731-27732` 的 `t_loop_next_roster` 硬編碼斷言 `sum(1 for s in s2 if not s["occupies_w"]) == 3`(對應「5佔W+3不佔W 含架構對齊」),我已實跑 `python3 scripts/test_lumos.py -k t_loop_next_roster` 確認目前 8 個斷言全綠、其中這條算出的就是 3。[S1] 把「資安」加成 `("code","high")` 第 4 個不佔 W 的 required 席後,這個數字會變成 4,此斷言必翻紅,而 spec 的 [S1]/驗收兩節都沒有把「更新這條既有斷言」列進要做的事。

### A3

severity: major
blocking: 是

引句:「已經是條款綁定(它對 code 迴圈恆 skip,所以功能不撞,但名字會撞)」

Spec 自己在 [S2] 明文禁止把新步驟叫「第五條」,理由是條款綁定(`_disposal_clause_step`)已經是既有的「第五步」(file: `scripts/lumos:14830` docstring 自稱「處置閘第五步」、`scripts/lumos:15192` 呼叫處註解標「⑤ 條款綁定」)——但 [S6] 標記「已做」的圖譜寫入,file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:35` 的 KEY 行與 `:71` 的 d6 決策內容,兩處都逐字寫著「處置閘第五條合取」,直接踩到 spec 自己劃的紅線。而且這個數字本身也算錯:現有 disposal 合取項目已有 G3/處置集合/留痕/quote-check/條款綁定共 5 項,資安席若加入應是第 6 項而非第 5 項。這是已提交進圖譜、且被 `lumos decisions` 判定為 `valid: true` 的正式決策記錄,若不修正,往後任何人查 `pitfalls-code-loop` 這個單一事實來源都會拿到跟實作矛盾的說法。

### A4

severity: minor
blocking: 否

引句:「不成立 → 問閘未過(退出碼 1;退出碼 2 保留給帳面壞或參數錯),訊息三段式:缺什麼 → 為什麼在意 → 下一步指令獨立一行。」

要求新步驟用「發生什麼→為何在意→指令獨立一行」三段式,但同一個函式裡緊鄰的既有步驟並非如此:file: `scripts/lumos:15047`(留痕失敗)是單行訊息、file: `scripts/lumos:14891-14892`(條款綁定失敗)是兩行且第二行是格式提示而非可執行指令。新步驟做成三段式會跟同層的其他 `[disposal]` 失敗訊息風格不一致,但不影響任何判定邏輯,純屬輸出風格落差。

### A5

severity: major
blocking: 是

引句:「出現的每一處為清單逐一對過(commands/06、code-loop reference.md、design-loop SKILL.md 等),列席位的地方都補上。」

[S5] 的條款文字要求把「架構對齊」出現的每一處都比照補上「資安」,我實地 grep 過,「架構對齊」作為席位描述至少出現在 6 處:`skills/lumos-code-loop/SKILL.md:20`、`skills/lumos-code-loop/reference.md:86,106,283`、`skills/lumos-design-loop/SKILL.md:20`、`skills/lumos-project-notes/commands/06-代碼審與推送.md:5`、`skills/lumos-project-notes/reference.md:1084`。但驗收綁的機械測試只有 `[test:t_skill_code_loop_mentions_security_seat]` 一個,只鎖 `lumos-code-loop/SKILL.md` 步驟 2 這一處。這個 repo 本身已經有對付這種「口徑住在多處文字,漏散落清單」風險的先例——file: `scripts/test_lumos.py:34759-34770`(`t_tension_doc_sync`)與 `scripts/test_lumos.py:5452`(`t_marker_doc_sync`)都是逐檔列舉、確保關鍵字全數同步的漂移守衛——[S5] 卻只給單點測試而非同款多檔漂移守衛,實作者跑過那顆測試就會誤以為同步完成,實際上散落的 5 處參考文字大概率被漏掉。

---

## 圖譜鏡頭(固定席節點逐條判)

- **Systems/pitfalls-code-loop.md**:會影響——本案直接改寫這個節點宣稱的處置閘結構(新增合取項),而且已寫入的 d6/KEY 內容本身跟 spec 自己的規則矛盾(見 A3),此節點需要跟著本案一併訂正,不能維持現狀。
- **Systems/hook信任邊界.md**:不影響——本案完全不碰 hook 的 `_trusted_lumos()` 解析路徑或三支 hook 檔,新增的是既有已受信任的 `scripts/lumos` 內部一段判定與一份派工範本,不涉及「打開陌生資料夾就跑對方程式」這個節點宣稱的風險面。
- **Systems/arch-alignment-lens.md**:不影響——本案沒有改動「架構對齊」自己在 `_TIER_ROSTER` 的既有項、§7.6 派工詞或 `pitfalls --diff` 的 `arch_alignment` 對照組邏輯;唯一交集是共用的 §7.7 立場表新增一列給「資安」,不動既有「架構對齊」那一列的內容。

---

## 總結

最嚴重 severity:major。blocking 共 4 條(A1、A2、A3、A5);non-blocking 1 條(A4,minor)。
