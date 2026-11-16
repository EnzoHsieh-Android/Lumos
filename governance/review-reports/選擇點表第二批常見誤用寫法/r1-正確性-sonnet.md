severity: major

審查範圍:整份 r1-snapshot.md 逐節讀完。用 ast-grep 0.51.2 看了語法樹,也讀了 `scripts/lumos` 與 `check.py` 對應的函式。

1. `?.` 在行首的鏈式寫法,壞法 `!!.` 編不過,但規則照樣命中
severity: major
   - blocking: 是,會造成大量跑不出結果,把「依列號」統計與 RETIRE-IF 的分子灌水,而且一行只有一個壞法名額,這一行就沒有別的壞法可用。
   - spec 段落:〈用詞〉新錨點「安全呼叫符」、〈範圍〉3 的 `_choice_edits` 分支、S2、S6 樣本清單。
   - 輸入:
     ```
     val n = repo.getUser()
         ?.profile
         ?.name
     ```
   - 問題:設計只把那兩個字元換成 `!!.`,產出 `repo.getUser()\n    !!.profile`。Kotlin 的 `!!` 前面不能換行,而 `.`、`?.` 前面可以。
   - 查證:用 ast-grep 解析 `a\n  !!.b`,得到兩個陳述,第二個是 `prefix_expression` 加 `ERROR`;`a\n  ?.b` 則是正常的 `navigation_expression`。機器上沒有 kotlinc,所以這是語法樹的結果,沒有用編譯器實證。
   - 設計在〈範圍〉2 把「鏈式另起一行」列為要命中的樣本,卻沒有處理壞法本身。Android 專案裡這種寫法很常見。
   - 引句:「只把那兩個位元組換成 `!!.`」
   - file: `scripts/lumos:77281` 的 `_choice_api_edits` 與 `scripts/lumos:77252` 的 `_choice_edits` 都是就地換記號。沒有任何一處看「前一個非空白字元是不是換行」。

2. `.let` → `.also` 在陳述位置是必然等價的存活,設計沒有提到,也沒有前提擋
severity: major
   - blocking: 是,必然存活的壞法會擋推送,逼人逐行放行。
   - spec 段落:〈範圍〉1 的 `.let` 列(型別前提「(無)」)與〈實務隱患〉「編不過」「等價存活」兩條。
   - 輸入:`x?.let { show(it) }` 單獨成一個陳述,回傳值沒人用。
   - 問題:換成 `also` 後行為完全相同,任何單元測試都分不出來。〈實務隱患〉只講「結果有被用到時編不過」,以及 `$A!!` 與 `LaunchedEffect` 的等價,漏了這種最常見的用法。
   - 查證:`x?.let { show(it) }` 在語法樹裡是 `call_expression`,位置夠明確,可以用語法情境近似成型別前提(例如排除陳述位置)。
   - 目前只靠 RETIRE-IF 兩個月後讀統計來收拾。

3. nul.yml 的 elvis 規則若只寫 `kind: elvis_expression`,拿不到 `$A`、`$B`
severity: minor
   - blocking: 否,實作時 S1 的測試一跑就紅。
   - spec 段落:〈範圍〉2 的「`nul.yml`(`elvis_expression`;…)」。
   - 問題:〈範圍〉1 的前提「`$A` 或 `$B` 是 null 字面值」與候選 `$A!!`,都靠規則帶出後設變數 A、B。
   - 查證:`_choice_excluded` 讀 `hit["mv"]["A"/"B"]`(`scripts/lumos:77202`),`_choice_edits` 的 `$A` 取代拿不到值就回 None(`scripts/lumos:77274`)。純 kind 規則的 `metaVariables` 是空的,整列會靜默產不出壞法。
   - 我用 pattern `$A ?: $B` 實測能同時取到 A、B,包括 `a ?: b ?: c` 的外層(A 是 `a ?: b`)。設計沒寫明要用 pattern。

4. `LaunchedEffect` 的「引數」整個被換掉,會連同具名 lambda 一起刪
severity: minor
   - blocking: 否,罕見,落成跑不出結果。
   - spec 段落:〈範圍〉2、S4。
   - 輸入:`LaunchedEffect(Unit, block = { work() })` 或 `LaunchedEffect(k, block = { … })`。
   - 問題:`value_arguments` 裡含 `block = {…}`,整段改成 `(Unit)` 就把 lambda 刪了,編不過。
   - 查證:ast-grep pattern `LaunchedEffect($$$A)` 命中第 10 行 `LaunchedEffect(Unit, block = { x })`。`remember` 因為要求尾隨 lambda,沒有這個問題。

5. 〈實務隱患〉與〈範圍〉2 對 `LaunchedEffect` 常數 key 的說法不一致
severity: minor
   - blocking: 否,只是多一些等價存活,由放行吸收。
   - 引句:「`LaunchedEffect` 的 key 本來就是常數時規則不命中(範圍 2)」
   - 問題:〈範圍 2〉實際只排除單一 key 是 `Unit`、`true`、`false`。`LaunchedEffect("init")`、`LaunchedEffect(0)`、`LaunchedEffect(Unit, Unit)`、`LaunchedEffect(null)` 照樣命中,換成 `(Unit)` 都是等價。
   - 查證:對照〈範圍〉2 的字面條件,常數 key 的其他寫法沒被排除。

6. 接收者 `combine` 規則會誤中完整套件名的頂層呼叫
severity: minor
   - blocking: 否,罕見,落成跑不出結果。
   - 輸入:`kotlinx.coroutines.flow.combine(a, b) { x, y -> x }`。
   - 問題:語法樹是 `navigation_expression` 的 `.combine` 外面套 `call_expression`,跟 `a.combine(b)` 同形。命中後換成 `kotlinx.coroutines.flow.zip(a, b) {…}`,`zip` 沒有頂層版本,編不過。
   - 查證:ast-grep 解析該輸入,方法名那段是 `navigation_suffix`,位置跟既有 API 規則(`scripts/lumos` 對應的 `rules-choice/api.yml` 的 `inside navigation_expression inside call_expression`)相同。
   - 同理,其他型別自己的 `.combine`(例如函數式函式庫)也會命中。

7. S1 與〈範圍〉3 對「何時加括號」的判準不一致
severity: minor
   - blocking: 否,只是括號多餘,不影響語意。
   - 引句:「`$A` 不是單一記號時先包成 `($A)` 再接 `!!`」
   - 問題:S1 說「單一記號」,實作要沿用 `_choice_atomic`。`_choice_atomic` 對 `a.b()`、`a?.b`、`list.f { }` 都判「不用括號」(`scripts/lumos:77193`),測試作者照字面會期待 `(a.b())!!`。
   - 查證:`_choice_atomic` 的判斷依據是 `_CHOICE_ATOMIC_RE = [\w.?!]+`(`scripts/lumos:76879`),只留識別字、點、`?`、`!`。

8. S8 的放行理由分類跟現行詞表對不上
severity: minor
   - blocking: 否。
   - 引句:「被回報存活後的放行理由分布(等價、不是需求、其他)」
   - 問題:現行放行標籤只有「等價」「不是需求」「不適用」三種,沒有「其他」。
   - 查證:`scripts/lumos:77660` 的 `_CHOICE_WAIVE_LABELS = ("等價", "不是需求", "不適用")`。
   - RETIRE-IF 只算「等價」「不是需求」,「不適用」(型別不合那類)怎麼歸沒寫。
   - 「壞法數 / 殺掉數 / 存活數」是算事件數還是以(檔, 指紋)去重,也沒定義。同一個壞法先存活後被殺掉時,S8 的 4 = 1 + 2 + 1 對不上。

已讀,無 finding:
- 〈白話〉、〈舊否決比對〉、〈用詞〉。
- 〈不做〉、〈回退〉、〈天花板〉。
- 〈依據來源〉:引用的來源網址本身我沒有逐一上網核對,只核對了內部交叉引用。
- 〈驗收條款〉S3 的頂層 `combine(a, b)` 不命中:規則要求 `navigation_suffix`,頂層寫法沒有,成立。

已確認成立的宣稱:
- 「`$A ?: $B` 單節點」:pattern 可行,`a ?: b ?: c` 外層 A 是 `a ?: b`,內層也命中,但外層錨點相同且範圍較大,依 `scripts/lumos:77378` 的排序會先挑外層。
- 「`?.` 在 navigation_suffix 開頭」:`?.b` 的 suffix 從 `?.` 起。
- 「`LaunchedEffect` 與 `remember` 的 value_arguments」:在 `call_suffix` 裡,與 `annotated_lambda` 同屬一次呼叫,「帶尾隨 lambda 時命中」可以用語法樹判。
- 新錨點「引數」與「運算元起始」:`_choice_anchor` 預設分支本來就回節點開頭(`scripts/lumos:77130`),設計宣稱的改動只是文字上的擴充。

實務隱患逐類:
- 編不過與等價:見第 1、2、4、5、6 條。
- 換壞法:有效處置的鍵是(檔, 行指紋)而且不含壞法內容(`_choice_disposition`,`scripts/lumos:77723`),「已記的殺掉照算」成立。
- Compose 測試成本、掃描量:設計已列,我沒找到新的錯。
- 併發、金流、對外送出、不可逆:無,因為只改本機型錄、規則與壞法產生程式,沿用單人單機依序操作,不碰金額、不送資料,治理帳照舊追加。
- 守衛面:S7 只保證不含新語法的行不變,含新語法的既有行(很常見的 `?.filter`)會換壞法,設計已承認。

對自動附加節點的影響:
- Systems/規格閘:其中 WHY「有效處置以 (檔, 行指紋) 為鍵」與「回報上限抽法」都以(檔, 指紋)為單位,新增列不改鍵,不會破壞。
- 「依 (列號, 外層宣告) 數放行」那條的乾節點候選統計只加不改,不影響。
- Systems/kotlin規則包:PITFALL「C-18 規則把外層陳述清單塞進每個命中致使輸出過大」要提醒實作新規則時別用 `$$$` 抓整段 lambda。這是風險提醒,不是破壞。

查證用的暫存目錄 `/private/tmp/lumos-seat-work/選擇點表第二批常見誤用寫法/正確性-sonnet` 已刪除。

最嚴重 severity: major;blocking 共 2 條(第 1、2 條)。
