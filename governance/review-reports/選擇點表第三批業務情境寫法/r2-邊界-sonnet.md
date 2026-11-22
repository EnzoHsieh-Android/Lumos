severity: minor

我拿 ast-grep 0.51.2 對計劃描述的規則條件實跑了四類樣本,也逐項核對了 scripts/lumos 與 check.py 的函式。

- **作用域兩列的「有兩個以上子協程」**:我用 `has` 加 `precedes` 寫出了等價規則,可以做完。23 型樣本逐型核對,結果跟 S5 預期一致。
- **`retry` 整個呼叫的規則**:單行、換行、`?.`、帶 lambda、`Result` 排除都對。
- **`replay` 與 `LAZY`**:兩列的排除條件也都能寫成規則,過了樣本。
- **ERROR 節點**:接收者裡有 ERROR、`.retry` 那行沒有時,命中仍在,所以 S2 第三列做得出來。

以下是計劃沒寫到、或寫了但跟實跑對不上的地方。

## b1 作用域「兩個以上」的寫法指引方向錯了
severity: minor
blocking: 否,實作者靠 S5 樣本能自己摸到對的寫法,只是計劃的指引會誤導。

〈範圍〉2 的作用域條件。命中節點是 call_expression 的第一個子節點那個識別字,子協程是它的後代,所以關係要用 `has`,不是 `inside`。`inside` 加 `stopBy` 只能表達「某個 `async` 的最近一層 lambda 是誰」,表達不了「有兩個」。ast-grep 沒有計數,實跑可行的是:
- 從作用域的 lambda 往下用 `has`,`stopBy` 設成 lambda_literal。
- 找兩個含子協程的兄弟節點,用 `precedes` 配對。
- 再外加迴圈那一支:`for`、`while`,以及迴圈呼叫的 lambda 裡有一個子協程。

計劃沒有交代配對這個做法。照 `inside` 寫會一直卡在「怎麼數到二」。

引句:「用 ast-grep 關係規則的 `inside` 加 `stopBy: {kind: lambda_literal}` 寫」

## b2 「少於兩個子協程的必然等價由規則排除」過度宣稱
severity: minor
blocking: 否,多出來的是等價放行,RETIRE-IF 會承接。

`coroutineScope { if (cached) async { a() } else async { b() } }` 或 `when` 的各分支各一個 `async`,字面上有兩個子協程。實跑這個形狀會命中。但執行期同時只有一個子協程,換成 `supervisorScope` 必然等價。〈用詞〉只數語法樹上的個數,沒有排除互斥分支。〈實務隱患〉把「必然等價」整個說成已由範圍 2 排除,講過頭了。

引句:「作用域兩列少於兩個子協程的必然等價由範圍 2 排除」

## b3 〈天花板〉3 漏列規則實際漏判的幾種形狀
severity: minor
blocking: 否,漏判不誤擋,但使用者會以為這幾種有被抓到。

以下是用上面那條規則實跑、確認命中不到的形狀:
- 巢狀迴圈呼叫:`coroutineScope { a.map { b.forEach { launch { } } } }`。〈用詞〉規定迴圈呼叫的外一層 lambda 必須是作用域本身。
- `do { launch { } } while (c)`。〈用詞〉只寫了 `for`、`while`。
- 完整套件名的作用域:`kotlinx.coroutines.supervisorScope { … }`,第一個子節點是 navigation_expression,不是識別字。
- 完整套件名的 `kotlinx.coroutines.flow.MutableSharedFlow<Int>(replay = 1)`,同樣命中不到。

型錄 C-35 已有「完整套件名的頂層呼叫不收」的先例,這批沒補。〈天花板〉3 只列了「清單以外的迴圈函式」、位置引數與 `retry` 夾註解。

引句:「落在〈用詞〉迴圈呼叫清單以外的迴圈函式(含標準庫的 `mapNotNull`、`onEach`、`associate` 系列等)裡的,命中不到(漏判)」

## b4 作用域規則沒採圖譜已記的雙重否定修法
severity: minor
blocking: 否,計劃已寫實作第一步重量並以「驗不了」兜底。

kotlin規則包已有兩條同族 PITFALL:關聯規則(`inside`、`has`)命中的節點會被記成次要標記,輸出平方成長。修法是改寫成雙重否定,命中集合不變。file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:99`、`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:102`。

我的作用域規則(`has`、`precedes`、`stopBy`)實測:
- 巢狀 300 層:正寫約 16MB,外面包一層 `not: {not: …}` 後約 0.14MB。
- 兩種寫法在 23 型樣本上的命中集合相同(行 1、2、3、4、11、12、14、15、16、19–22)。

計劃把新規則的輸出量留到實作第一步才量,沒有把已證實的修法寫成該列的寫法。

引句:「新規則在實作第一步用同一組巢狀輸入重量、數字寫進 Verification」

## b5 欄位名「行為差異」在型錄裡不存在
severity: minor
blocking: 否,實作者看得出是指哪欄,但照字面搜會找不到。

計劃三處稱型錄列有「行為差異」欄,包括範圍 1 的 LAZY 列要求寫進該欄的註明。實際表頭是「為什麼行為不同」。`check.py` 讀的也是 `get("為什麼行為不同")`。file: `skills/kotlin-idioms/checks-catalog.md:1665`、`configs/ast-grep/kotlin-android/check.py:1459`。

引句:「行為差異欄註明:`coroutineScope` 裡沒啟動的 LAZY 子協程會讓作用域永不結束」

## b6 `allWarningsAsErrors` 的隱患只算在 `firstOrNull`,漏了 `toIntOrNull` 三列
severity: minor
blocking: 否,RETIRE-IF 的「跑不出結果超過一半」機制會把這幾列撤掉,但〈實務隱患〉與〈天花板〉2 沒預告。

S4 自己的範例 `val n = s.toInt() ?: 0` 就是「非空型別接 `?:`」。這種寫法在 Kotlin 是 USELESS_ELVIS 警告,開 `allWarningsAsErrors` 的專案會編不過。`toIntOrNull`、`toLongOrNull`、`toDoubleOrNull` 最常見的用法正是接 `?:` 或 `?.`,所以這三列在這類專案裡多半落成「跑不出結果」。計劃只把這個風險寫在 `firstOrNull`。⚠ 本機沒有 kotlinc,這條警告等級是依 Kotlin 已知行為判的,沒有實編。

引句:「`firstOrNull` → `first` 在結果後面接 `?.`、`?:` 時 K2 只出警告,專案開 `allWarningsAsErrors` 時會編不過,落成跑不出結果」

## 實務隱患鏡頭(逐類)
- **併發與交易**:無。計劃已排除,本 repo 單人單機依序操作。
- **金流**:無。只改型錄、規則與產壞法的程式。
- **對外送出**:無。掃描都在本機跑。
- **不可逆**:無。治理帳逐筆追加,撤列沿用既有處置。
- **資源與效能**:有,見 b4。`retry` 的 `$A` 後設變數會帶整段接收者文字,鏈很長時輸出放大。計劃已量過這項(3000 個 retry 約 837MB)並以「驗不了」兜底,我沒有新發現。
- **守衛面**:有,計劃已列。再補一項我核對過的:既有樣本 `arid.kt` 的 `retry` 只是參數名,`choice-batch2.kt` 只有 `combineLatest`(不是 `mapLatest`)。S7 的既有釘值不會被新列誤改。

## 圖譜固定席
- **Systems/kotlin規則包**:不影響宣稱的行為或合約。節點只有 WHY 與 PITFALL,沒有 INVARIANT。計劃只加列、規則與樣本,並更新 `about_code` 與 WHY。唯一相關的是上面兩條 PITFALL,見 b4。
- **Systems/規格閘**:不影響。處置鍵 (檔, 行指紋) 不變,「依列號」統計的口徑不變。第 81 行那條 RULE 管的是型錄主表的〈接電證據〉,跟選擇點表無關。第 85 行 SIGXFSZ 事故的現行保護(整批失敗再逐檔重跑)繼續有效。

臨時目錄已刪除。

總結:最高嚴重度 minor,blocking 共 0 條
