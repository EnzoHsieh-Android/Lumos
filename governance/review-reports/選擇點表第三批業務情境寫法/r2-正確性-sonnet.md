severity: major

## c1 作用域規則的實作機制寫成「inside 加 stopBy」,照字面做不出「這個作用域有兩個以上子協程」
severity: major
blocking: 是(中心規則缺一個可照做的機制,照字面做會讓 S5 的列誤命中)
引句:「「最近一層 lambda」用 ast-grep 關係規則的 `inside` 加 `stopBy: {kind: lambda_literal}` 寫」
- 對應段落:範圍 2 作用域兩列、〈用詞〉子協程、〈用詞〉作用域有兩個以上子協程。
- 問題:命中節點是 `supervisorScope`/`coroutineScope` 識別字。`inside` 只能從子協程往外找,沒辦法從識別字出發,也沒辦法把「最近一層 lambda」綁到這一個呼叫。「兩個以上」是計數,計劃沒寫用哪種機制做。
- 失敗場景一(我實跑 ast-grep 0.51.2):「`async` 的最近一層 lambda 是某個作用域的大括號」只綁到「某個」作用域時,`supervisorScope { val x = coroutineScope { async{1}.await() }; val y = coroutineScope { async{2}.await() } }` 的外層會命中。`coroutineScope { list.map { coroutineScope { async { x() } } } }` 的外層也會命中。這兩個正好是預期值表 S5 要求不命中的列。
- 實測可行的寫法(我自寫的規則,在 a.kt、c.kt 兩份樣本上各案命中與否都符合〈用詞〉):
  - 從作用域那一側往下用 `has`:呼叫 → `call_suffix` → `annotated_lambda` → `lambda_literal` L,再在 L 之下用 `has` 加 `stopBy: {kind: lambda_literal}` 找子協程。
  - 「兩個」用 `any`:迴圈呼叫、for 或 while 裡有子協程;或兩個互為兄弟的分支都含子協程,即「X 含子協程 且 `precedes`(stopBy end)含子協程的 Y」。
  - 迴圈呼叫的 lambda 要沿固定鏈 `call_suffix`→`annotated_lambda`→`lambda_literal` 找。我第一版用 `stopBy: end` 找 lambda,會把內層作用域的 `async` 算進迴圈,`list.map { coroutineScope { async } }` 的外層就誤命中。
  - 驗證:`stopBy` 的「停下那一層也算」成立,範圍 2 的說法對。`launch` 與 `async` 兩個在 `if`/`else` 不同分支時會被算成兩個,天花板沒寫。
- 為什麼擋:計劃的〈用詞〉三段是這批翻案的核心,範圍 2 卻只給出一半機制(最近一層 lambda 的判斷),計數與「綁到本呼叫」都缺。建議在範圍 2 寫明上面的 `has`/`precedes` 結構。

## c2 作用域規則照正面關聯寫,重犯規則包已記的次要標記 PITFALL,卻沒採同節的雙重否定修法
severity: minor
blocking: 否(輸出變大時落成驗不了、只提醒,不會誤擋;修法有現成的)
引句:「巢狀作用域深度 100 層約 34MB、200 層約 263MB,掃描時間深度 150 層約 10 秒、300 層約 166 秒」
- 對應段落:實務隱患「深層巢狀」;圖譜鏡頭對 `Systems/kotlin規則包` 的判定。
- 該節點有兩條 PITFALL(C-18 與第二批 inside 規則),根因都是關聯規則命中的節點會被記成次要標記,修法是改寫成 `not: not:` 的雙重否定。計劃接受大輸出,理由是「真實程式不會巢狀到這個深度」,沒提這個現成修法。
- 實測(我的 c1 規則,深度 300 的巢狀 `coroutineScope`,每層兩個 `launch`):正面關聯寫法輸出 308,373,052 位元組。外包一層 `not: {not: …}` 後輸出 188,998 位元組,命中集合不變(深度 100 與樣本檔 a.kt 都核對過)。
- 影響:節點宣稱的行為(掃描輸出受控)沒被破壞,因為計劃有「驗不了只提醒」兜底。但這是同族第三次犯,而修法零成本。

## c3 範圍 1「對應決策表」欄的填法與 `single` 兩列的理由互相牴觸
severity: minor
blocking: 否(結果「—」本身是對的,只是理由出處矛盾,會讓照寫的人兩邊都能引)
引句:「不看型錄觸發字表標的「決策不問」(觸發字表管的是推送前要不要出表態題,跟這一欄不同)」
- 同一範圍的下一條寫 `singleOrNull`、`single` 填「—」,理由卻是「型錄觸發字表標「無決策」」,等於用了上一條才說不看的東西。
- 型錄觸發字表第 1441 行與 1442 行把 `single`、`singleOrNull` 標成「一般集合式/轉換運算子,非情境選擇」,跟這批「多筆算不算資料錯誤」的情境前提正面衝突。〈舊否決比對〉沒列這一條,說明段同步也沒處理。
- 照上一條的填法,`singleOrNull`、`single` 應該去看有沒有 D 列涵蓋「多筆算不算資料錯誤」。我查了決策表,沒有,所以「—」對,但理由要改成這個。file: `skills/kotlin-idioms/checks-catalog.md:1441`

## 圖譜鏡頭逐節點判定(不另開 finding)
- `Systems/kotlin規則包`:規則、樣本、about_code、WHY 的增補都是新增列,不破壞既有第一、二批列的行為。唯一碰到的是上面的 PITFALL 同族(c2)。
- `Systems/規格閘`:處置鍵 `(檔, 行指紋)` 那條 WHY 不受影響,只加列、不改鍵,回退第 3 項也如實寫了外溢。ERROR 兄弟位置那條 PITFALL 的修法是「行範圍有交集就略過」。計劃對「整個呼叫」錨點改成只看錨點行到結尾行,理由站得住:我用 `flow {` 加一行中文識別字再接 `}.retry(3)` 實跑,`$A.retry($$$B)` 仍命中,刪的只有 `.retry(3)`。ERROR 落在更早的接收者行時,刪尾巴不會產出結構錯的壞法;ERROR 吃掉接收者結構時 `_choice_anchor` 找不到 `.` 或 `?.` 會回 (None, None),不會誤刪。

## 其餘逐項查證結果(沒找到洞,不標 finding)
- 「整個呼叫」錨點:`$A.retry($$$B)` 在 `x!!`、`(x as T)`、`a[0]`、`this.flow`、`x::foo`、`?.` 換行等接收者形狀下,`mv["A"]` 的結尾都落在 `.` 或 `?.` 前,後接 `_CHOICE_GAP_SKIP_RE` 比對成立。
- 夾註解時樣式不命中,計劃的說法正確。
- `Result.retry()` 與 `ListenableWorker.Result.retry()` 也命中樣式,要靠 `$A` 的 regex 排除,範圍 2 有寫。
- `replay` 規則:value_argument 裡的名稱節點是 `simple_identifier`(沒有 `value_argument_label`)。我用它寫出的規則,對 6 種形狀的命中與排除都跟範圍 2 一致。
- `NonCancellable` 的「不在 finally 裡」可寫,節點種類是 `finally_block`。
- `LAZY` 的「直接接 `.await()`/`.join()`」可寫。要用固定鏈而不是 `stopBy: end`,否則巢狀 LAZY 會被外層誤排除。
- `_choice_also` 擴充、`_choice_anchor_edits` 的分支順序、S6 對 `t_choice_samples_batch2` 篩選範圍的描述,都跟現有程式吻合。

總結:最高嚴重度 major,blocking 共 1 條
