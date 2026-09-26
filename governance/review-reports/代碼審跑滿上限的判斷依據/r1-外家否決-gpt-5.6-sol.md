severity: blocker

## F1 現有帳本無法把聚合發現對回席次、引句與新增行
severity: blocker
blocking: 是；核心判據依賴帳本目前沒有保存的關聯，照字面實作無法算出「修正引起的比例」。

引句:「最後一輪的每條發現,拿它的第一句引句去最後一輪的凍結審材定位」
file: `scripts/lumos:18339` `findings_set` 只由每輪單一 carrier 席保存，內容可聚合多席發現，但沒有逐筆發現到來源席次及報告的映射。
file: `scripts/lumos:17865` `_quote_rows` 只產生 `quote` 與 `ok`，沒有 finding ID、命中行號或 diff 正負號。
file: `scripts/lumos:7891` quote-check 只核對 carrier 自己的報告；其他席的報告可沒有可定位引句。
file: `docs/.canary-log.jsonl:1819` 同一 carrier 記錄聚合 ID `r1a-F1,r1a-F2,r1b-F1`，卻只有一個 `report_path`。其中 `r1b-F1` 無從取得其「第一句引句」，即使引句命中也無從判斷命中的是新增行。S2、S7、S8 因而缺少可執行的資料模型。

## F2 「折入幾條」在規格範例中混用了兩種不同指標
severity: major
blocking: 是；同一資料可得到不同走勢與熔斷結果，實作者必須自行猜測應採報告發現數還是實際折入數。

引句:「每一輪折入幾條(帳本的折入清單,整輪各席加總)」
file: `scripts/lumos:7364` 現有 `_review_yield_round` 明確區分 `N`（各席 `findings` 加總）與 `F`（carrier 的 `folded_set` 長度），兩者不是同一指標。
file: `scripts/lumos:18340` 每輪只允許一席攜帶 `findings_set`／`folded_set`，不存在可供「整輪各席加總」的多份折入清單。
file: `docs/.canary-log.jsonl:1306` 「工具自裝檔」第一輪各席 `findings` 合計 28，但 carrier 的 `folded_set` 只有 12；spec 摘要採 28。
file: `docs/.canary-log.jsonl:1479` 「記憶清理」第一輪各席 `findings` 合計 42，但 carrier 的 `folded_set` 是 26；spec 摘要改採 26。前一案例若採實際折入數便不會觸發「單輪超過 20 條」，判斷會直接翻轉。

## F3 「最後一輪只剩 minor」沒有指定輪級嚴重度算法
severity: major
blocking: 是；照 carrier 的席次嚴重度實作，其他席仍有 major 時也會輸出放行建議。

引句:「走勢下降,且最後一輪只剩 minor → **附理由放行**」
file: `scripts/lumos:7759` `finding_severities` 是選填的逐發現映射；若有提供才檢查是否覆蓋聚合 finding ID。
file: `docs/.canary-log.jsonl:1819` carrier 自身的 `severity` 可為 minor，但同筆聚合 `finding_severities` 仍包含 major。spec 沒有規定取各席最高級、逐發現最高級、carrier 級別，或欄位缺失時回報未知；採任一席次欄位即可在 major 尚存時誤報「只剩 minor」。

## F4 建議矩陣沒有納入 disposition 硬閘失敗原因
severity: major
blocking: 是；證據雜湊或必要安全席失敗時，規格仍能建議放行，會把硬性證據缺口包裝成可接受的收斂結果。

引句:「只印不擋,也不改任何閘的判定」
file: `scripts/lumos:18327` G3 會因審材雜湊或證據不符而失敗。
file: `scripts/lumos:18560` 高風險 code loop 會因缺少安全席或安全席未覆蓋 landing 而失敗。
file: `scripts/lumos:18574` `loop status --disposal` 會根據上述條件回傳 FAIL。最後一輪即使呈下降且表面只剩 minor，只要缺安全席或 G3 失敗，規格矩陣仍輸出「附理由放行」；「只印不擋」只避免自動越閘，沒有避免人依錯誤建議作出放行決定。

## F5 對寫到一半末行的處理與既有 fail-closed 合約衝突
severity: major
blocking: 是；不改既有閘就必須回傳錯誤，忽略壞行則會改變既有 disposition 結果，兩項要求不能同時成立。

引句:「讀到寫一半的最後一行要當沒這行,不得整段報錯」
file: `scripts/lumos:9593` `loop status` 目前將任何無法解析的 JSONL 行計入 malformed records，沒有末行例外。
file: `scripts/lumos:18279` disposal 遇 malformed record 會先行以 rc=2 fail-closed。
file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:35` 現行合約明載壞帳本行必須 rc=2 fail-closed。若新分析共用 disposal 的讀取結果，「當沒這行」就破壞合約；若保留 rc=2，則無法做到「不得整段報錯」。spec 未定義獨立的容錯分析讀取器與其輸出時序。

## F6 效能條款與早期熔斷條件形成循環依賴
severity: major
blocking: 是；不先做跨輪定位便不知道是否觸發熔斷，但規格又禁止在觸發前做該計算。

引句:「只在輪數達上限或觸發熔斷條件時才算,平常不算」
file: `代碼審跑滿上限的判斷依據-r1.md:56` S8 要求從第二輪起判斷連續兩輪「修正引起比例 > 50%」並立即熔斷。這個比例必須先讀兩輪凍結審材、定位引句並判斷新增行，才能知道熔斷條件是否成立。規格沒有新增快取或預先記帳欄位；實作只能每輪計算而違反效能條款，或等到上限才計算而漏掉早期熔斷。

## F7 選填及歷史欄位的缺失、部分填寫語義未定義
severity: major
blocking: 是；相容舊帳本或只填部分分類時，缺值可被當成零、未知或未重複，三種處理會產生不同建議。

引句:「若沒有任何一輪填了問題類別,則同類重複一項應印」
file: `scripts/lumos:7735` `folded_set` 只允許出現在帶 `findings_set` 的 carrier 記錄，歷史相容資料不保證具有新分析所需的報告、快照或分類欄位。
file: `scripts/lumos:7759` 現有逐發現欄位對「提供後必須覆蓋所有 finding ID」已有明確驗證；新 `--finding-class <id>=<短名>` 卻未定義可否重複、ID 必須等於或只是隸屬 `findings_set`、部分分類是否合法、短名如何正規化，以及實際寫入的 JSON 欄位。
規格只處理「任何一輪都沒填分類」，沒有處理某輪缺失、同輪部分填寫、舊輪缺折入清單或缺可比快照；例如兩輪各有四條發現、只替其中一條標同類時，實作者可算成 1/1 重複、1/4 重複或未知，足以把「縮圈重整」判斷翻轉。

## F8 RETIRE-IF 所需的採納與推翻資料沒有記錄路徑
severity: major
blocking: 是；撤除條件不可量測，錯誤建議即使長期多於正確建議也不會觸發規格宣稱的退場機制。

引句:「連續 8 週內,建議被人推翻的次數 > 被採納的次數」
file: `scripts/lumos:549` `_loop_gov_mark` 只記錄 loop 結論種類與 note，沒有本功能輸出的建議、人的最終處置或採納／推翻關係。
file: `docs/.governance-log.jsonl:1` 現有治理帳是事件式紀錄，沒有可把本次建議與後續人工決定配對的欄位。
file: `docs/.escape-log.jsonl:1` 逃逸帳同樣沒有建議採納狀態。spec 唯一新增的帳本資料是 finding class，且分析器宣稱只讀；因此八週統計沒有資料生產者、關聯鍵或查詢入口。

## F9 「agentnative 停止條件整理」不是可核對的交叉引用
severity: minor
blocking: 否；不影響核心算法執行，但讀者無法重現 prior-art 查證。

引句:「agentnative 停止條件整理把輪數上限、連續無進展」
spec 沒有為該名稱提供作者、標題、URL、版本或本地節點；它既不是 repo 內可定位節點，也無法唯一對應公開資料。其餘外部引用均能定位，包括 [VRR-Stop](https://arxiv.org/abs/2607.17641)、[Cloudflare AI review](https://blog.cloudflare.com/ai-code-review/)、[Google Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)、[Google review standard](https://google.github.io/eng-practices/review/reviewer/standard.html) 與 [openedclaude README](https://github.com/openedclaude/claude-reviews-claude/blob/main/README_EN.md)。

已看,無: spec 與 LUMOS-SPEC 內容一致，以上問題全部適用於計劃節點；本地交叉引用 `Projects/節點還原SOP_計劃`、`Systems/design-loop`、`Systems/loop-convergence-recording` 均存在。`loop next`、`loop status --disposal`、`canary record`、`quote-check`、`loop escape`、`gov` 的 help 與實作入口均已核對。對 `Systems/loop-convergence-recording` 而言，純顯示建議本身不改閘；F5 的末行忽略會破壞其 fail-closed 合約，F3、F4 則會產生與閘結果相反的人工作業建議。實務風險中，併發寫入見 F5，效能見 F6，守衛面見 F3、F4、F5；金流、對外送出、秘密處理及不可逆操作均無，因功能僅讀本地帳本與審材並輸出文字；無額外 async、外呼、子程序或資源釋放風險，資料量也受有限輪次與本地 JSONL 範圍約束。

最嚴重 severity: blocker，blocking 共 8 條。
