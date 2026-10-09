severity: major

審查依據:只讀被審設計與 repo `/Users/enzo/harness/lumos-toolchain-target-arch`(HEAD f1c86606)。

## 1. 分層與依賴方向

不一樣。pitfalls 這一層既有的紀律是不載圖譜,新設計要它讀圖譜節點。

ID: ARC-1
severity: major
blocking: 是
引句:「並逐條貼出規則內容（貼內容不貼路徑）」
file: `scripts/lumos:41200`
- 既有做法:`pitfalls` 明寫 vault-free,理由是它在 pre-push 熱路徑上。見 `scripts/lumos:41200`(「★vault-free★,pitfalls 在 pre-push 熱路徑上不載圖譜」)和 `scripts/lumos:41848`(載圖譜實測 4.7s,pitfalls 0.18s)。
- 設定也是直讀 JSON,不走載 vault 的 helper。見 `scripts/lumos:26807`(「★不走載 vault 的 helper★——check 跑在 pre-push,自稱 vault-free」)。
- 新設計:做法第 3 點要求 `pitfalls --diff` 把目標節點的規則內容貼出來。驗收條款 [S3] 要求它判斷節點存不存在、有沒有規則。[S4] 要 `code-loop check` 印節點。這些都得解析圖譜節點,等於 vault-free 那一層直呼圖譜層。
- 「實務隱患」的效能段只算「設定讀取與 glob 比對」,漏了節點解析的成本。
- 既有的對應做法:圖譜內容由有 vault 的派工端附上(`LUMOS-IMPACT` / `LUMOS-SPEC`,見 `skills/lumos-design-loop/templates.md:324` 起的欄位),不是 pitfalls 自己讀。

ID: ARC-2
severity: minor
blocking: 否
引句:「6. **防成為後門**：範圍寫在版控的設定檔」
file: `scripts/lumos:26721`
- 既有做法:會改變審查判準的宣告,`review_roles` 讀起點版本(`_json_at_ref(root, base, ".lumos/config.json")`),理由是「被審的分支不能自己改宣告決定自己拿到哪張卡」。見 `scripts/lumos:26625`、`scripts/lumos:45168`。
- 新設計:`arch_targets` 同樣會改變審查席的判準。它只說「寫在版控」,沒說讀哪個版本。如果照 `_stack_questions_config` 直讀工作樹,被審分支可以自己加宣告來躲掉鄰居比對。
- 目標規則的內容也來自圖譜,同樣需要「只信起點」。

## 2. 命名與錯誤處理

結構大致對,但錯誤處理的粒度、欄位形狀、輸出形狀三處不同。

ID: ARC-3
severity: minor
blocking: 否
引句:「宣告錯誤時印一行警告、該檔退回鄰居基準，`lumos doctor` 報錯。」
file: `scripts/lumos:26625`
- 既有做法:壞宣告「整份不用」,退回不宣告的判定,回一句固定原因的警告,不回填專案寫的值。見 `scripts/lumos:26627-26630`(`review_roles`)和 `scripts/lumos:26805`(`stack_questions`)。印法是 stderr 的「提醒:」,見 `scripts/lumos:41586`。
- 新設計:改成逐檔退回。它沒定義警告走哪個通道,也沒說會不會回填節點名或路徑。
- 「重疊就算錯」跟既有的「第一條命中的算數」也不同。見 `scripts/lumos:40547` 的 `_glob_first_match`,以及 `review_roles` 的取法。

ID: ARC-4
severity: minor
blocking: 否
引句:「每項 `{ "node": "Systems/<目標架構節點>", "paths": ["app/Domain/**", ...] }`」
file: `scripts/lumos:26625`
- 欄位名 `arch_targets` 的 snake_case 跟既有一致。
- 形狀不同:`review_roles` 是清單,每項 `{path, role}`,一條一個樣式,用 `set(item) != {"path","role"}` 嚴格驗形狀。這裡 `paths` 是陣列。
- 新設計沒說用哪一支 glob。`app/Domain/**` 要靠 `_cochange_excluded` 那套「星號跨斜線」的語意才比得到。見 `scripts/lumos:40530` 和 `scripts/lumos:40547`。應明寫沿用 `_glob_first_match`。

ID: ARC-9
severity: minor
blocking: 否
引句:「`--json` 的 `arch_alignment` 每支檔多 `baseline: neighbors|target` 與 `target_node`」
file: `scripts/lumos:41083`
- 既有形狀:`arch_alignment["files"]` 是 `{改動檔: [對照檔字串…]}`,值是 list。見 `scripts/lumos:41083-41107` 和 `scripts/lumos:41563-41565`(`', '.join(sibs)`)。
- 「每支檔多欄位」得把值改成物件,會弄壞既有消費者(`scripts/test_lumos.py:12275` 的測試、`scripts/lumos:48117`)。
- 目標基準的檔沒有對照檔,`_tension_candidates_into` 會因為沒有 sibs 靜默跳過它(`scripts/lumos:41146` 起)。
- ⚠ 建議交編排者:改成另開並列的鍵,不要改值型別。

## 3. 第二種做法

ID: ARC-5
severity: major
blocking: 是
引句:「每條以 `[A<序號>]` 開頭（A1、A2…在該節點內遞增，跟驗收條款的 `[S<序號>]` 同一種寫法、用 A 區分是架構規則）一行一條，可帶 `[test:]` 綁到該棧的架構規則測試」
file: `scripts/lumos:6873`
- 專案已有三種承載方式,各自附帶機械把關:
  - 程式碼看不到的限制用 `RULE:`,要有 `[依據][since][retire][confirmed]` 生命週期欄位(`scripts/lumos:3871`、`scripts/lumos:3894`)。
  - 載重宣稱用 `KEY:★INVARIANT★` 加 `[test:]`,由 doctor Check T 驗綁定與審計(`scripts/lumos:2057`)。
  - 驗收條款用 `[S<n>]`(`scripts/lumos:6873-6875`)。
- `[A<n>]` 是第四種一行一條的規則行,還自帶 `[test:]` 綁定。它繞過了 Check T 的審計,也不受 `RULE:` 的撤除與確認約束。
- 說它跟 `[S<序號>]`「同一種寫法」不成立:`SPEC_CLAUSE_RE = \[S(\d+)\]` 和 `_CLAUSE_LEAD_RE` 都寫死 S,只在 Projects 計劃裡解析。要用就得複製解析器,或把它參數化。
- 目標規則本質上是「程式碼看不到的限制」和「可綁測試的合約」。「規則要有編號好引用」這個需求是真的,但可以在 `RULE:` 或合約行上加編號欄位來滿足,不必另立 `[A]`。
- ⚠ 編號需求是否足以另立語法,請編排者最終判。

ID: ARC-6
severity: minor
blocking: 否
引句:「正文有一節〈目標規則〉」
file: `docs/lumos-toolchain-knowledge/Systems/arch-alignment-lens.md:1`
- 既有慣例:分類規則靠摘要行前綴(`RULE:` / `WHY:` / `KEY:★…★`)。CLAUDE.md 也寫明正文段落只算「線索」,不能推翻程式。
- 新設計把有約束力的規則放在正文的一節,靠標題認出。「目標架構節點」因此成了只有靠一個標題約定才識別得出的新節點角色,而不是靠既有的摘要行機制。
- 這個設計的規則是否真的拿來審,取決於它,而 doctor 的「節點沒有任何規則」檢查要另寫一套認節點的邏輯。

ID: ARC-7
severity: minor
blocking: 否
引句:「三問改為①有沒有違反宣告的哪一條目標規則（引規則編號）②範圍內新寫的程式彼此一致嗎③有沒有從範圍內直接依賴範圍外舊寫法、而目標規則禁止的」
file: `skills/lumos-design-loop/templates.md:343`
- 既有條件分支寫法:在同一份範本裡加一段「遇到 X 時」(`templates.md:343` 的 tension 段),三問和輸出格式(`templates.md:355`「輸出:三問…最後『不對齊共 N 條,其中 major M 條』」)不動,只補口徑。
- 新設計是整組換問。新的第③問把原本的「第二種做法」問拿掉了,而「第二種做法」正是 major 錨的來源。輸出骨架和席位 roster 測試也要一起跟著變。
- 建議改成加一段「拿到目標基準時」,保留三問,把對照物從鄰居檔換成規則編號。

## 4. 落點

ID: ARC-8
severity: minor
blocking: 否
引句:「- Systems/arch-alignment-lens」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:121`
- 這份計劃會改 `scripts/lumos`、`skills/lumos-design-loop/templates.md`、`doctor` 和 `code-loop check`。
- `scripts/lumos` 的家是 `Systems/pitfalls-code-loop`(`about_code` 列了它)。`templates.md` 的家是 `Systems/design-loop`(`design-loop.md:155` 起)。
- `arch-alignment-lens` 沒有 `about_code`,不是這些檔的家。CLAUDE.md 鐵則 5 要求「改了程式要寫說明就寫進改到那支檔的家」。
- 同類的前例是 `Projects/代碼審前後端角色鏡頭_計劃.md`,它的 `lands_in` 列了 `design-loop`、`pitfalls-code-loop` 等多篇。
- 建議:概念和〈目標基準〉分支寫進既有的 `arch-alignment-lens`(53 行,放得下,不需另開)。設定讀取、`--json` 欄位、`check` 輸出寫進 `pitfalls-code-loop`。`templates.md` 分支寫進 `design-loop`。`lands_in` 補齊這三篇,不用另開新節點。

不對齊共 9 條,其中 major 2 條
總結最嚴重 severity: major；blocking 共 2 條
