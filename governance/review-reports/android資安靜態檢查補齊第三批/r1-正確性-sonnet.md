severity: minor

我拿初稿在 ast-grep 0.51.1 上實跑了約 30 個密碼欄寫法和 20 個 Jackson 寫法。預期值表的 12 列都對得上實際輸出,沒有 major。下面四條都是文件精度或天花板漏列。

**1.**
severity: minor
blocking: 否

〈實務隱患〉說「照實寫在〈天花板〉」,〈天花板〉卻沒有這一項,也沒列實跑量到的幾種漏報。

實跑的結果如下,這些寫法規則都不報:
- `val vt = PasswordVisualTransformation()` 之後寫 `visualTransformation = vt`,不報。
- `keyboardOptions = KeyboardOptions.Default`、`KeyboardOptions(autoCorrect = false)`、`KeyboardOptions(keyboardType = KeyboardType.Text)`,都不報。
- 帶型別參數的 `TextField&lt;String&gt;(…)`,不報。
- `Foo.TextField(` 和 `MyTextField(`,不報。

前三項合乎範圍字面。但第二項的 keyboardOptions 沒有設 Password,就是 MASTG-TEST-0258 說的「沒用不快取的輸入類型」,規則卻放行,而〈天花板〉只寫了「完整套件名」。

名單裡的 `SecureTextField`、`OutlinedSecureTextField` 沒有 `visualTransformation` 參數,這條規則對它們永遠不會報。這是我的推論,沒有查 Compose 的簽章,所以只當附註。

引句:「非敏感的遮字欄位(例:遮住的非秘密文字)會誤報:語料 120 處裡沒見到,照實寫在〈天花板〉。」
佐證:實跑檔 `/tmp/lumos-seat-work/android資安靜態檢查補齊第三批/正確性-sonnet/t.kt`(第 7、8、9、10、18 行不報)。

**2.**
severity: minor
blocking: 否

D-57 的標準寫法有一種寫法沒有字面特徵,證據樣式還是只寫了 `setPublicVersion\(|VISIBILITY_SECRET`。

標準寫法的第一種是「通知只說『有一則新訊息』」,這種寫法找不到對應的特徵。型錄的規定是「同一段裡有寫不出特徵的寫法」就寫 `(無)`。AI 選這個變體表態時,證據行不會有 `setPublicVersion(`,每次都會跳「證據樣式對不上」的提醒。後果只是提醒加待盲判,不會擋推送。

引句:「證據樣式主寫 `setPublicVersion\(|VISIBILITY_SECRET`(VISIBILITY_PRIVATE 是預設值,單寫它不算照做;要附遮掉內容的版本或整則藏起來)、例外 `(無)`」
佐證:`skills/kotlin-idioms/checks-catalog.md:730`(「同一段裡有寫不出特徵的寫法…寫 `(無)`」),`scripts/lumos:73705`(第一條樣式必須配得上 evidence 那一行,否則提醒)。

**3.**
severity: minor
blocking: 否

D-57 加進去後,型錄〈統計〉裡「情境決策表列數」那一行括號內的證據樣式分項沒有同步更新。

計劃只寫要把 56 改成 57。但 D-57 的例外欄是 `(無)`,所以括號裡「例外寫 `(無)` 的 31 列」會變成 32。`stats_problems` 不核對這一行,這個數字就會一直是錯的。

引句:「情境決策表列數那行 `stats_problems` 不核對,照手數改成 57」
佐證:`skills/kotlin-idioms/checks-catalog.md:1123`(「情境決策表列數:56(證據樣式:主寫 `(無)` 的 8 列、例外寫 `(無)` 的 31 列、兩段都 `(無)` 的 5 列)」)。

**4.**
severity: minor
blocking: 否

Jackson 那條的形狀有兩個〈天花板〉沒寫的邊界。規則已放在不接閘那邊,影響小。

- 只認帶 `.` 的呼叫。`ObjectMapper().apply { activateDefaultTyping(ptv) }` 是隱含接收者,不報;沒有接收者的 `activateDefaultTyping(ptv)` 也不報。`.also { it.enableDefaultTyping() }` 會報。
- 同一條鏈上有兩個 activateDefaultTyping 時(例如 `mapper.activateDefaultTyping(a).activateDefaultTyping(b)`),會在同一行報兩次。預期值表只驗了單層鏈 `….activateDefaultTyping(ptv).build()`,那個確實只報一次。

引句:「呼叫的被呼叫端是 `.activateDefaultTyping`、`.enableDefaultTyping`、`.activateDefaultTypingAsProperty`、`.enableDefaultTypingAsProperty`」
佐證:實跑檔 `/tmp/lumos-seat-work/android資安靜態檢查補齊第三批/正確性-sonnet/j.kt`(第 4、15 行不報,第 7 行報兩次)。

**我查過但不構成問題的地方**
- 具名參數、`PasswordVisualTransformation(mask = '*')`、`remember { PasswordVisualTransformation() }`、`if/else` 切換顯示、尾隨逗號、尾隨 lambda,都照計劃字面報。
- 子 lambda 裡的 `visualTransformation`(例如寫在 `label = { … }` 裡)不會讓外層誤報。
- 外層沒有 keyboardOptions、只有巢狀 lambda 裡有的情況,外層照報。
- `keyboardOptions=opts` 和斷行的 `keyboardOptions\n = opts` 都視為有帶,不報。
- D-57 的證據行會先剝掉註解和字串再比對,所以註解和字串裡的 `setPublicVersion(`、`VISIBILITY_SECRET` 不會誤配。
- UI-112、DATA-99、DATA-100 是接在現有最大號 UI-111、DATA-98 之後,D-57 是接在 D-56 之後,編號對得上。

最高等級 minor;blocking 0 條
