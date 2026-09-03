# r1 席報告:架構對齊(sonnet,不佔人數)

## 問一 分層
### 讀 fold.json+驗證三條要不要抽 helper,未表態
severity: major
blocking: 是
--from-pitfalls 把複雜解析外包給 `_pitfall_diff_collect`(:13929),cmd 內只留十行分組膠水(:4831-4880)。
fold.json 要逐席逐 quote 呼叫 _quote_rows、核 id、席內去重、組 finder——複雜度不低於 by_source 分組,材料沒表態要不要抽 `_fold_collect`。
引句:「只讀 JSON 檔,不開帳、不開圖譜」

### ★內容驗證 fail-closed rc2,與最貼近的既有案例相反★
severity: major ⚠
blocking: 是
全 repo 唯一同款「引句錨定+對人手寫 manifest 做內容檢查」的既有指令是 seat-check(:12000-12070):
等價失敗類別(out_of_scope)恆 rc0 只觀測不擋,只有檔讀不到才 rc2(測試 :22758 出界仍 rc0、:22779 檔案不存在才 rc2)。
capture-counts 自己唯一 rc2 案例也只是 git IO 錯誤(:4838-4840)。材料要把內容驗證失敗升成阻斷,沒對照這兩個案例、沒解釋為何更嚴。
引句:「每條 `quote` 必須錨得回該輪凍結快照」

## 問二 命名/錯誤處理/落點
檔名 rN-fold.json 與 rN-dispatch.json/rN-snapshot.md/rN-intake.md 同慣例,落點同 loop_dir(:3883),欄位 snake_case 一致——對齊。
### seats 鍵型態與 dispatch.json 不一致
severity: minor
blocking: 否
dispatch.json 的 seats 是★陣列★、元素帶 auditor(`_roster_dispatch_entries` :5773-5787);fold.json 提案是★以席名為 key 的物件★。同家族同鍵名不同型態。
引句:「`"seats":{"<席名>":[{"quote":"<該席報告的一句逐字引句>","id":"<去重後 id>"}`」
### rc2 訊息文字未草擬
severity: minor ⚠
blocking: 否
引句:「寫入驗證(fail-closed,rc2)」

## 問三 第二種做法
### ★carrier_findings_set 是帳上 findings_set 的手寫影子——同一事實兩份、一份機器驗一份沒有★
severity: major
blocking: 是
帳上 findings_set 由 record 寫入、處置閘實際核 F/FO/AC(:11550,11588-11591),是「這輪正式發現 id 全集」唯一被機器驗過的來源。
fold.json 另定義手寫 carrier_findings_set,只驗自己內部一致、不驗與帳一致;作者看到了(「要不要讓 disposal 閘也讀…另案」)卻選擇先出兩份不互核的拷貝。
PRIOR-ART 只比 dispatch/intake 的形狀,沒把這個語意幾乎同名的欄位放進比較。
引句:「要不要讓 disposal 閘也讀 fold.json 核 `findings_set` 一致:本案不動閘;若日後接,是另案。」
### 與 seat-check 同家族,不合併的理由(時序)沒明講
severity: minor
blocking: 否
引句:「本 repo 自己的 `rN-dispatch.json`/`rN-intake.md` 就是同型的每輪結構化留痕」

不對齊共 6,major 3。
