severity: blocker

## 逐節閱讀記錄

**Frontmatter/decisions（1–56 行）**：已讀,無 finding——d6→d8 的 supersede 鏈完整、`valid: false`/`superseded_by`/`ended` 三欄齊。但 d8 的數字本身有問題,見 F1。

**為什麼／兩層要分開（64–84 行）**：已讀,無 finding。

**一、門怎麼判（88–101 行）**：見 F1、F2。

**二、條款句式（103–113 行）**：已讀,無 finding——「句式只驗形狀不驗意思」的取捨有明講、且把擋空話的責任交給第四節的紅燈檢查,邊界清楚。

**三、綁定規則（115–119 行）**：見 F3、F6。

**四、新閘 spec-gate（121–131 行）**：見 F4、F5。

**五、逃逸自動記（133–139 行）**：見 F7、F8（=PF-2）。

**六、退場條件／要動什麼／實務隱患／驗收條款／回退／誠實界線（141–204 行）**：已讀,無 finding——`已排除:效能`與`已排除:多人並行`兩行本身理由具體（跑綁定測試而非全套、只讀不寫共用狀態靠既有寫入原語），且本篇自己因討論金流/不可逆等詞而命中硬單向門 1,與回退節「本案自己是單向門」自洽,S12 的不回溯切法也跟既有 `_CLAUSE_GATE_SINCE`/`_LANDING_GATE_SINCE` 同款。`lands_in` 一行寫在表格後、非 YAML frontmatter,若真的照六節「本篇 lands_in 需可機械判」的精神走,這行其實會被 `_disposal_landing_step` 判缺 lands_in（`fields.get("lands_in")` 讀不到），但因為本案自己是單向門,不受第五步（僅雙向門差異相關)影響、且落點步驟本身跟此次改動無因果,不單獨列 finding,僅在此註記供實作時對齊格式。

---

## Findings

**F1**
severity: major
blocking: 是
spec 第一節「先講帳面事實」;帳面已訂正一次卻仍算錯——29+5+2+0=36≠40,方向性結論（稀疏、集中守衛面）雖不受影響但削弱「已訂正」的可信度,一份自稱修過一次算術錯的文件不該再算錯一次。
引句:「538 篇裡只有 **40 篇**掛了——守衛面 29、不可逆 5、金流 2、對外送出 0」
file: `docs/lumos-toolchain-knowledge/Projects/標籤系統盤點_調研.md:53` 另一份既有調研筆記給的是「33（守衛面28、不可逆5）」,三份數字互不相同,說明這條「帳面事實」本身量測方法未固定,不是一次性筆誤。

**F2**
severity: blocker
blocking: 是
硬單向門訊號 1 用「自我治理」命名第四類,但全 repo 既有慣例（`_RISK_ENUM`、既有 90+ 篇筆記的「已排除:」寫法）一律叫「守衛面」,`PITFALL_CLASSES` 的鍵是英文 `self-governance`；spec 未定義「已排除:<類>:<理由>」裡 `<類>` 要精確比對哪一種字串,三套詞彙並存会讓 S2/S14 的判定無法穩定實作。
引句:「四類任一(金流/對外送出/不可逆/自我治理;表在 `PITFALL_CLASSES`,沿用不另建)」
file: `scripts/lumos:4422` `_RISK_ENUM = {"金流", "對外送出", "不可逆", "守衛面"}`——既有值域用的是「守衛面」不是「自我治理」。

**F3**
severity: major
blocking: 是
單向門「回退節非空」沒有給最低字數/實字門檻,而同一份規格對「已排除」理由與 manual 都明訂 ≥4 字含實字；「## 回退\nTBD」或單一標點會被判定為「非空」而放行,違背這條規則抄的亞馬遜精神（真的要有回退計劃）。
引句:「單向門必須寫回退計劃,雙向門不用因為回退本來就便宜」

**F4**
severity: blocker
blocking: 是
step4 要求「至少一支是紅的」才放行,但 run_cmd 沒有 `{method}` 時只能整套跑、只有一個聚合 rc,無法歸因到「綁定的那支測試」;既有機制（guard kill）遇到同樣情形已明文標記為弱證據,spec 完全沒提這個既有先例也沒定義 fallback。
引句:「雙向門放行的條件:每支測試都存在,而且至少一支是紅的」
file: `scripts/lumos:9505-9507` `verdict = "killed" if ok_attr else "killed_unattributed"` 與 `"弱證據:紅燈未歸因到綁定測試(建議 run_cmd 加 filter 鎖定該測試)"`——同一類問題在既有機制裡已被明確標記為弱證據,新閘卻沒繼承這個判斷。

**F5**
severity: blocker
blocking: 是
零 [S] 條款、且沒命中任何硬單向訊號、四行「已排除」都寫了的計劃,在雙向門路徑下 step4 對空測試集合怎麼判是未定義的；若實作用常見的 `all()`/`any()` 慣性寫法（空集合 `all()` 為真但 `any() for 紅` 為假,兩者若寫反),最壞情況是一份完全沒有可驗收條款、也沒被任何人審過的計劃直接 PASS 進實作,正是這套機制最想防的情境。
引句:「規格階段功能還沒做,綁定的測試應該紅;全綠代表綁的是舊測試冒充,什麼都沒驗」——這句只講「有測試但全綠」的情況,沒講「沒有任何測試」的情況。

**F6**
severity: major
blocking: 是
雙向門只驗「測試存在、至少一支紅」,沒有規定每條條款的 `[test:]` 必須各自不同；作者可以讓 10 條 [S] 全綁同一支（唯一寫的)測試,滿足「全部存在+至少一支紅」的機械檢查,但實際上只有 1/10 的宣稱真的被驗——直接違背本案「條款一律綁測試」的核心精神卻不被閘擋下。
引句:「每條條款只准 `[test:<測試名>]`,測試要真的存在(沿用 `_classify_one`)」——只驗存在性,未驗唯一性。

**F7**
severity: minor
⚠
blocking: 否
`_auto_escape`/`_door_for_loop` 對 loop_id 做了 `nfc()` 正規化比對,但 `_plans_in_range` 回傳的計劃路徑（來自 `git diff --name-only`）用來做 `(env.vault / plan_rel).is_file()` 存在性判斷時未經正規化；在會把檔名正規化成 NFD 的檔案系統上,若圖譜檔名以 NFC 存在磁碟、git 回傳 NFD（或反過來）,存在性檢查可能靜默落空,导致「plan-file」歸因失敗、逃逸記不到。証據不夠具體到能斷定會真的觸發（依賴 checkout/文件系統的正規化行為,環境相依),故標 ⚠ 且不判 blocking。
file: `scripts/lumos:7522` `elif plan_rel and (env.vault / plan_rel).is_file():`——與同函式其餘比對（`nfc(loop_id)`）不對稱。

**F8（=PF-2）**
severity: blocker
blocking: 是
逃逸自動記把推送閘來源收窄成只認「受波及合約的測試沒過」這個固定字串,但 `pre-push` 實際會因多種其他真下游缺陷擋下（錨點漂移、doctor 健檢紅、`test_lumos.py` 整套紅、自主迴圈測試紅),這些同樣是「下游抓到缺陷」而非「流程沒走完」,卻不會被記進逃逸帳；本設計唯一的自我糾錯依據就是逃逸率（RETIRE-IF ①),一個系統性低估來源會讓雙向門看起來比實際安全,直接侵蝕退場判準的可信度。
引句:「缺表態、高風險缺審查留痕這些是流程未完成,不是下游抓到缺陷」——這句只排除了「流程未完成」類,沒有處理「測試紅但訊息不是那個固定字串」這類真缺陷。
file: `scripts/hooks/pre-push:239` `if printf '%s' "$_cl_out" | grep -q "受波及合約的測試沒過"; then`——比對條件是單一字串命中,`test_lumos.py:371`/`anchor` 等其他擋下路徑不會進這個 if。

---

## 固定席節點逐條判(是否破壞其宣稱行為/合約)

- `Systems/design-loop.md`(★INVARIANT★ 處置閘第五步)：**會動,已被 spec 自己承認**。S8 要求第五步改呼叫同一支條款檢查器,設計文本已明講「這是改 design-loop 的不可變合約行,要綁測試加審計」,但「要動什麼」表格裡的這項改寫本身沒有對應 [S] 條款去機械驗收,屬於本案自我實踐不徹底,已在 F3/F6 之外單獨註記,不再重複列 finding。
- `Systems/anchor-integrity.md`(★RISK★)：**不影響其合約**——進度段已明寫改了錨點檔要 `lumos anchor approve --note`,遵守既有流程,合約本身（改錨點檔要留痕）沒被繞過。
- `Systems/每支檔有家.md`：**不影響**——`scripts/lumos`/`scripts/hooks/pre-push` 都早有家（僅因牽連篇數超過 40 篇未展開),新增的 `Systems/規格閘` 正是給新機制開的家,符合這條鐵則。
- `Systems/lumos-cli-read.md`(★INVARIANT★ search 排除 superseded 但不排除 stale)：**不影響**——本案未碰 `search`/status 過濾邏輯。
- `Systems/canary-audit.md`(★INVARIANT★ record/second 落盤驗證、second 不影響 rc)：**不影響,且已遵守**——`_auto_escape` 用的是既有 `_jsonl_append_verified`,即現有的落盤自驗原語,沒有繞開或新造一套寫入路徑。
- `Systems/guard-kill.md`(★INVARIANT★ rc 優先序、`--json` 純度)：**不影響**——spec-gate 與 guard kill 是不同指令,不共用 rc 優先序邏輯;唯一相關處是 F4 指出 spec 沒有借用 guard-kill 已有的「弱證據」判斷,是遺漏而非破壞。
- `Systems/bound-tests-gate.md`(★INVARIANT★ code-loop 對固定席合約測試逐支真跑)：**不影響**——spec-gate 明確只作用於設計審迴圈（處置閘第五步已把 `code-` 開頭迴圈排除),不觸及 code-loop 的 bound-tests 檢查路徑,兩者判定方向（一個要「至少一支紅」、一個要「全部綠」）分屬設計階段與實作階段,不構成矛盾。
- 其餘「超出上限只列名」節點：未展開內容,不逐條判;就標題判斷（lumos-cli-lifecycle、測試假綠形態、refcheck、convergence-evidence-gate、pitfalls-code-loop、cochange-guard、graph-sync-coverage、native-windows-support 及數篇 Issues）與本案主題（設計審閘語意 + 逃逸自動記)無直接重疊,判「不影響」但信心較低,標 ⚠。

## 實務隱患鏡頭

- **併發**：無新增風險——`_auto_escape` 沿用既有 `_jsonl_append_verified` 這支已處理過並行寫入的硬化原語,spec 自己也在「已排除:多人並行」裡點名同一件事,查證屬實。
- **效能**：有隱患,見 F4——run_cmd 缺 `{method}` 時 step4 得跑全套（本 repo全套約 8 分鐘),若消費專案套用此閘且每次 `spec-gate` 呼叫都觸發全套,會拖慢設計審迴圈本身;spec 沒有把這個成本寫進「已排除」或退場條件。
- **資源**：無特殊隱患——閘只讀計劃、跑既有測試指令、append 既有帳本檔,沒有新開檔案控制代碼或鎖。
- **回滾**：有隱患,見 F3——回退節「非空」門檻太鬆,單向門的回滾保證形同虛設。
- **遷移順序**：無新增隱患——`_CLAUSE_GATE_SINCE`/`_LANDING_GATE_SINCE` 前例的不回溯切法被沿用（S12),且進度段已先落地「逃逸自動記」三來源並各自先紅後綠翻紅釘驗過,分階段上線的順序合理。

---

最嚴重 severity:blocker;blocking 計 7 條(F1、F2、F3、F4、F5、F6、F8)。
