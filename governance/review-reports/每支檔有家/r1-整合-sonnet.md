severity: major

## 逐節閱讀記錄

- **Frontmatter / decisions d1–d3**：已讀，無 finding。d1–d3 與正文「為什麼」段的敘事、與 `Systems/節點範圍與索引守衛.md` 現有的「不看提到幾個檔」合約（KEY 行：★不看提到幾個檔★）互相對得上，未見矛盾。
- **為什麼（這批的來源）**：已讀，無 finding（三個 POS 消費專案的具體檔案/行數宣稱不在本次可查證範圍內，但用來支撐決策的核心主張——「合約條數提醒不看檔數」「about_code 只加分」——皆與本 repo 現況核對一致，見下方引用）。
- **世界上怎麼做的（PRIOR-ART）**：已讀，無 finding。CODEOWNERS/notowned、diff-cover、Nx module-boundaries 為外部工具，非本 repo 可查證範圍，描述與其公開定位一致。
- **名詞**：有 finding，見 F7（`node_home.ignore` 的「樣式」未定精確語意）。
- **規則一 S1–S6**：有 finding，見 F4（S1「同一份清單」實際對到哪一份不明確）。
- **規則二 S7–S10**：已讀，無 finding。`_impact_reverse_lookup`（`scripts/lumos:19563` 起）確實同時支援完整路徑與唯一裸檔名比對，S7 的重用宣稱屬實；S8/S9/S10 與既有 about_code 只加分（不建連結）的既有 check-s4（`scripts/lumos:1451`）不衝突——check-s4 只會引導使用者把「自己家的檔」用反引號寫出來，不會產生新的「別人的檔」。
- **規則三 S11–S15**：有 finding，見 F3（`scripts/lumos` 已有 30/46 篇既有節點掛它為家，規則三對它實質失效）。
- **規則四 S16–S19**：有 finding，見 F1（S17 與規則標題矛盾）。
- **規則五 S20–S23**：有 finding，見 F5（`lands_in` 格式無法表達 spec 自己「落點」段裡的技能檔項目）與 F8（派工範本檔未列入落點）。
- **在哪裡檢查 S24–S27**：已讀，無 finding，除 F6（`_STATS_NODE_SEMANTICS` 語意標記漏列）。`_disposal_clause_step`／`_CLAUSE_GATE_SINCE`（`scripts/lumos:14840` 起）確實用「首筆帳日期」做不回溯判準，S21 的重用宣稱屬實；`_KNOWN_GATES`（`scripts/lumos:4629`）確實是必須手動登記的單一常數，S27 宣稱屬實。
- **舊帳（S28–S29）**：已讀，無 finding。
- **讓規則被看見 S30**：有 finding，見 F2、F8（列舉的四處未含節點還原 SOP 與架構對齊派工範本）。
- **邊界 S31–S32**：已讀，無 finding。S31 的「-z / errors= / 非 UTF-8 不炸」與本 repo 最近兩筆提交（`b4926d9c`、`1f28cd6b`）已建立的慣例一致；S32「60 幾篇」與本 repo 實際 Systems 節點數 64 吻合。
- **範圍外**：已讀，無 finding。
- **落點**：有 finding，見 F5、F8（見上）。
- **實務隱患**：已讀，部分覆蓋不足，見下方「實務隱患鏡頭」與 F3。
- **驗收怎麼跑**：已讀，無 finding。`-k` 關鍵字與規劃的測試函式名前綴/子字串都能對上。
- **回頭條件**：已讀，無 finding。

## LUMOS-SPEC 節點檢查

`LUMOS-SPEC` 行只指向這份 spec 本身，任務文字裡沒有額外附掛節點清單，故無其他節點需逐條判「破不破壞」。spec 正文自己 `related`／引用到的 `Systems/節點範圍與索引守衛`、`Projects/固定席扇出降權_計劃` 已在下方 F3、及逐節閱讀記錄中判過：對「不看提到幾個檔」合約——不影響（規則四管檔數上限，合約條數提醒本身邏輯未被要求更動，spec 也在落點段承諾照舊）；對「about_code 只加分、必看筆記只認正文路徑」的裁定——不影響（規則二的「別人的檔」定義本就排除自己 about_code 內的檔，不推翻該裁定）。

## Findings

### F1 規則四的擋規則寫成無條件，與規則標題自相矛盾
severity: major
blocking: 是 — 照字面實作,任何新開的 Systems 節點（哪怕只管 1 支檔）都會被擋,遠超過規則標題「一篇管超過上限」所宣稱的範圍,是會讓實作者做出錯誤擋法的內部不一致。
引句：「[S17] **擋**：這次新開的 Systems 節點沒寫 responsibility。」
1. 規則四標題明寫「一篇管超過上限要寫負責範圍」，S18 也明寫「提交後超過上限…而它沒寫 responsibility」才擋,但 S17 沒有任何「超過上限」的限定詞。
2. 兩種讀法（S17 無條件 vs. 呼應標題只在超過上限時才擋）會導出完全不同的系統行為，spec 沒有裁決哪個是對的。
3. 若照 S17 字面（無條件）實作，`lumos new system <模組>` 這個最常見的建節點路徑會全面被擋，除非每次都手動補 `--responsibility`。

### F2 沒列出「節點還原 SOP」——正是本案動機事故的產生源頭，卻沒被排進要同步的地方
severity: major
blocking: 是 — 不改的話,消費專案照現行 SOP 做冷啟動時仍會產出「一個模組一篇、不填 about_code」的節點,直接撞上規則一/規則四的新擋法,或根本沒達成本案要防的效果。
引句：「[S30] 開新 Systems 節點時印的提示、lumos 教寫節點的說明、注入每個專案說明檔的紀律區塊，都寫進這五條的一句話版」
1. file: `skills/lumos-project-notes/reference.md:1094` 〈節點還原（brownfield 冷啟動）〉步驟 4「落節點」寫的是「起手 `lumos new system <模組>`——骨架只有 FLOW/KEY/DEP/TEST 四行」，全文沒有一次提到 `about_code`。
2. file: `skills/lumos-project-notes/commands/09-節點還原.md:10` 的快查表同樣只寫 `lumos new system <模組>`，未提 `--code`/`--responsibility`（S19 新增的旗標）。
3. 這正是 spec「為什麼」段所描述、三個 POS 消費專案長歪的入口（用 `lumos new system <模組>` 起手、about_code 全空），S30／落點列出的四處（提示／教寫節點說明／紀律區塊）都不含這份 SOP，是散落地點清單裡明確缺的一項。

### F3 `scripts/lumos` 已有 30/46 篇既有節點掛它為家，規則三對它形同虛設
severity: major
blocking: 是 — 規則三宣稱的效果（寫回要落在真正相關的家）在本 repo 最大、最常被改的檔上實質漏擋：只要挑 30 篇裡任何一篇寫內容都能通過檢查，不論寫的是不是真的在講那次改動。
引句：「一支很大的檔可以有好幾個家（後端訂單檔本來就分狀態、訂單列、保存三篇）」
1. 機械數字（grep 全部 Systems 節點 frontmatter）：46 篇有 `about_code` 欄的 Systems 節點中，30 篇的 `about_code` 含 `scripts/lumos`（例：`docs/lumos-toolchain-knowledge/Systems/canary-audit.md`、`docs/lumos-toolchain-knowledge/Systems/design-loop.md`、`docs/lumos-toolchain-knowledge/Systems/guard-kill.md` 皆是）。
2. spec 自己落點段又要新增第 31 篇（`Systems/每支檔有家`）把 `scripts/lumos` 列進 about_code，進一步加深這個問題，而「實務隱患」段只討論「誤擋」與「舊專案衝擊」，沒有討論這個「漏擋/規則對主力檔案失效」的方向。
3. 這正好對應到 spec 自己指出的根因③「工具在把人往那篇推」——規則三想解決推錯篇的問題，但對 `scripts/lumos` 這個單檔巨石架構的核心檔，30 選 1 的寬鬆度讓「推錯篇」照樣能通過檢查。

### F4 規則一宣稱重用「改程式要動圖譜」的副檔名清單，但那道閘實際上是四份各自維護、靠專門測試守住一致性的清單，而 scripts/lumos 裡另有一份不同、未受該測試保護的清單
severity: major
blocking: 是 — 兩份清單內容不同（後者缺 .sh/.ps1/.c/.cc/.cpp/.h/.hpp），選錯的話「需要家的檔」判準會跟「改程式要動圖譜」閘實際擋的範圍不一致，出現漏判或誤判。
引句：「程式檔判定跟「改程式要動圖譜」那道閘同一份副檔名清單加首行 `#!`」
1. file: `scripts/hooks/pre-commit:124` 的 Gate 2 註解明寫「四份清單由 `t_code_exts_four_lists_agree` 釘」；file: `scripts/test_lumos.py:7591` 這支守衛測試比對的四份是 `pre-commit`／`post-commit`／`check-graph-sync.py`／`impact-hook.py`，不含 `scripts/lumos` 本身。
2. file: `scripts/lumos:3278` 另有一份 `CODE_EXTS_T`，是給技術棧設定比對用的既有清單，內容與上述四份不同（缺 `.sh .ps1 .c .cc .cpp .h .hpp`），且不受 `t_code_exts_four_lists_agree` 守護。
3. `lumos home check` 依落點規劃要寫進 `scripts/lumos` 本體，實作時最順手可及的就是已經在同一檔案裡的 `CODE_EXTS_T`——但那不是 S1 意指、真正被 gate 使用的那一份，spec 沒有點名該重用哪一支常數，也沒提到要把新用法納入既有的四份一致性守衛。

### F5 規則五的 `lands_in` 格式（僅 `Systems/<名>`）無法表達 spec 自己「落點」段裡的一項落點，暴露格式本身的表達力缺口
severity: major
blocking: 是 — 照字面實作，處置閘只認 `Systems/<名>` 樣式，任何像本案這樣「同時要落 Systems 節點又要落技能/範本檔」的計劃，若把技能檔那項寫進 `lands_in` 會被判「不是 Systems/<名> 的樣子」擋下；若不寫進去則落點清單本身就是不完整的宣告，兩條路都是錯的行為。
引句：「[S20] 計劃筆記多一個清單欄位 `lands_in`，每項寫 `Systems/<名>`」
1. 對照 spec 自己的「## 落點」段第三項：「教寫節點的說明與紀律區塊：各加一句話版（規則見 S30）。」——這一項指向的是技能檔（skill reference）與範本檔（`scripts/templates/graph-discipline.md`），不是 `Systems/<名>`。
2. spec 目前沒有 `lands_in` 欄位（規則尚未實作，可以理解），但這恰好證明：等規則五真的上線後，這篇計劃自己重寫一次 `lands_in` 時，會立刻撞上「有一項不是 `Systems/<名>` 的樣子」而被 S21 判不過。
3. 規則五完全沒有設計「落點是技能/範本檔而非圖譜節點」的表達方式或例外，這是格式本身的缺口，不是單一措辭問題。

### F6 新閘若把「檔案路徑」寫進治理帳的 `nodes` 欄，卻沒有登記進既有的語意標記表，會讓 `gov --stats` 把它跟真正的圖譜節點名混著比
severity: minor
blocking: 否 — 只影響治理統計呈現的可讀性，不影響擋/放行本身的正確性。
引句：「擋下與放行都記進治理帳，閘名登記進已知閘名單（不登記治理帳漂移那支會紅，統計也會漏）」
1. file: `scripts/lumos:4650` 的 `_STATS_NODE_SEMANTICS = {"anchor-approve": "此來源記的是檔案路徑", ...}` 是既有機制，專門標記「哪些 gate 的 `nodes` 欄語意不是圖譜節點」，`anchor-approve` 正是先例（它記的是 `scripts/hooks/pre-push` 這類檔案路徑）。
2. S3/S4（擋新增沒家的檔）在觸發當下，被擋的對象是「檔案」而非「圖譜節點」，若照既有慣例把它塞進 `gov_events` 的 `nodes` 欄，語意會跟其餘記圖譜節點名的閘不同，spec 只講到要登記 `_KNOWN_GATES`（S27），沒提到這個第二張表。

### F7 `node_home.ignore` 的樣式（glob）語法未指定，而 repo 內已有兩種不同的既有慣例
severity: minor
blocking: 否 — 兩種既有慣例都能工作，只是實作者要自己選一種，不會導致明顯錯誤行為，但會造成跟現有慣例不一致的第三種寫法。
引句：「排除 docs/ 與建置輸出夾、測試檔、lumos 自己裝進去而且內容沒改過的檔、專案設定 `node_home.ignore` 列的樣式」
1. file: `scripts/lumos:3816` 的 `file_name_match` 是 basename-only 的 fnmatch。
2. file: `scripts/lumos:19932` 的 `"glob:<pattern>"` 慣例是比對 repo 相對路徑（`fnmatch`/`PurePath.match`）。
3. spec 沒有說明 `node_home.ignore` 的每一項是比對 basename 還是 repo 相對路徑，兩種既有慣例語意不同，實作者得自己猜。

### F8 落點段與 S30 都沒列出架構對齊席派工範本，但 S23 明確要求改它
severity: minor
blocking: 否 — 漏掉不會讓系統做錯事，只會讓 S23 這條規則本身沒人記得去實作，屬於執行清單不完整而非行為錯誤。
引句：「[S23] 架構對齊那一席的派工範本多一題：落點合不合理——該寫進既有那篇，還是另開一篇。」
1. file: `skills/lumos-design-loop/templates.md:253` 〈7.6 架構對齊席派工〉是唯一定義「三問」逐字派工詞的地方（`templates.md:264`「三問，逐問答、每問附對照的 file:line」），S23 要新增的「落點合不合理」必須改在這裡（變成第四問），但 S30／落點的四處清單（提示、教寫節點說明、紀律區塊）都沒點名這個檔案。
2. 找不到 `templates.md` 這個檔案名稱或〈7.6〉小節編號在 spec 正文任何地方出現過。

## 實務隱患鏡頭（整合與知識同步視角，補 spec 自己「實務隱患」段沒答的類別）

- **知識同步散落遺漏**：見 F2、F8——本案自己開了「教寫節點的說明、紀律區塊」這類散落地點的清單，但清單本身不完整，遺漏兩處已驗證會被本案規則直接影響的文件。
- **清單/常數漂移**（副檔名清單、治理帳語意標記表）：見 F4、F6——repo 裡已有專門的漂移守衛慣例（`t_code_exts_four_lists_agree`、`_STATS_NODE_SEMANTICS`），本案新增的判準沒有明確掛進這些既有守衛，等於在守衛之外又長出一份沒人管的複本。
- **spec 自我指涉一致性**（它自己會不會違反自己訂的規則）：見 F5——規則五的欄位格式連 spec 自己的落點段都放不進去，屬於本審查要求③特別點名的檢查項，且確有問題。
- **消費專案相容性（舊帳分批還）**：無——decision d3 與 S5 已明確把「提交前就沒家的舊檔」降為只提醒，三個 POS 專案與兩個舊 Android 專案的既有落差在「範圍外」段也明講留給下次 `lumos update` 後的舊帳處理，機制與宣稱一致。
- **frontmatter schema 白名單同步**（`SCALAR_KEYS`/`LIST_KEYS` 要收 `responsibility`/`lands_in`）：無——這是實作時測試會直接翻紅逼出的必經步驟（`scripts/lumos:10559-10560` 現有 `SCALAR_KEYS`/`LIST_KEYS` 是單一位置的白名單），屬於一般編碼細節而非需要設計前瞻的散落地點，不构成本審查層級的 finding。

總結：最高 severity major，blocking 共 5 條
