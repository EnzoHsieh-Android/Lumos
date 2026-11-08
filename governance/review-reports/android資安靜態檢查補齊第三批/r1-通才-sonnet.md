severity: major

本機沒有 ast-grep,規則形狀只能讀程式與測試推論,沒有實跑。

## Finding 1
照範圍 4 實作,`t_kt_catalog_stats_consistent` 會整支紅。計劃沒有要求同步改測試裡寫死的〈統計〉舊值。

失敗場景:
- 三列進型錄後,型錄〈統計〉會變成 535 列、UI 112、DATA 100、語意類 107、規則包 229 條(error 48、不接閘 30)等。
- 照計劃只改型錄,測試端的 `_KT_STATS_LINES` 仍寫著「總列數:532」「UI 111」「DATA 98」「語意類 106」「規則包條數:227」「error 46」「其中 29 條」「:128」等舊值。
- 該測試的改壞動作是在型錄複本裡把這些字樣換成加 1 的數字。
- 型錄已經換成新數,舊字樣找不到,替換等於沒動。
- 於是「★前置★ 改壞有套上」(`mut != text`)一律失敗,整支測試紅。
- 驗收條款 S3、S4 綁的是 `t_kotlin_catalog_rows_wired` 與 `t_kotlin_rulepack_security_rules`,沒有綁這支。
- 條款全綠、全套才紅,推送前的閘會晚一步才發現。
- 範圍 4 與〈回退〉的「測試擴充」都沒點名要改 `_KT_STATS_LINES`。

引句:「〈統計〉由 `stats_problems` 核對的數照程式重數(總列數、各主題、各級、情境、規則包條數與不接閘、被會擋的規則守到的列數、逐列查證)」

佐證:
- `scripts/test_lumos.py:129450`(`_KT_STATS_LINES`)
- `scripts/test_lumos.py:129509`(改壞有套上的檢查)

severity: major
blocking: 是

## Finding 2
`keyboardOptions` 只要出現就放行,字面寫法裡完全沒設密碼鍵盤的密碼欄漏報,而且預期值表沒有這一列。

失敗場景:
- 登入表單常見 `TextField(visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done))`。
- 這欄沒設 `keyboardType = Password`,鍵盤照樣會記住輸入。
- 這正是 UI-112 名稱所說的「只遮字沒設密碼鍵盤」,規則卻因為有 `keyboardOptions =` 而不報。
- 字面的 `KeyboardOptions(...)` 其實可以查有沒有 `keyboardType`,只有變數才真的看不到。
- S1 預期值表只放了「變數 `opts`」一列,沒放字面但缺 keyboardType 的列。
- 實作者照字面寫,漏報就被固化,測試也不會紅。
- 〈天花板〉只寫了完整套件名會漏報,沒寫這一類。

引句:「帶了 `keyboardOptions`(不管值是字面還是變數)不報」

佐證:
- 草稿規則 `experiment/draft-rules.yml.txt` 的 `not: has: value_argument regex '^keyboardOptions\s*='` 只判參數名。
- 判讀準則 `experiment/judge-pwd.md` 把「呼叫裡沒有 keyboardOptions」當 TP 定義,所以量測也量不到這類漏報。

severity: minor
blocking: 否

## Finding 3
〈統計〉最後一行除了列數,括號裡還有三個證據樣式分項數,計劃只改列數。這三個數 `stats_problems` 不核對,過期了不會有人發現。

失敗場景:
- 現行寫法是「證據樣式:主寫 `(無)` 的 8 列、例外寫 `(無)` 的 31 列、兩段都 `(無)` 的 5 列」。
- D-57 的例外寫 `(無)`,「例外寫 `(無)` 的列數」應變成 32。
- 照字面只改成 57,括號內的數字就和重數不符。
- 計劃自己也說這行不核對。

引句:「情境決策表列數那行 `stats_problems` 不核對,照手數改成 57」

佐證:`skills/kotlin-idioms/checks-catalog.md:1123`

為什麼標 minor:數字不影響任何閘,只是文件過期。

severity: minor
blocking: 否

## Finding 4
密碼欄規則的呼叫名單裡,部分名稱沒有對應測試,部分名稱本身就是死字。

失敗場景:
- 預期值表 S1 只用 `TextField` 與 `OutlinedTextField` 兩種呼叫名。
- 有人把規則的正規式裡 `BasicTextField2?` 那一支拿掉,所有驗收條款仍全綠。
- `SecureTextField`、`OutlinedSecureTextField` 這類名稱沒有 `visualTransformation` 參數,列在名單裡永遠不會命中,也沒有測試證明它們無害。

引句:「呼叫名是 TextField、OutlinedTextField、SecureTextField、OutlinedSecureTextField、BasicTextField 或 BasicTextField2」

佐證:`scripts/test_lumos.py:126828`(`_KTSEC_CASES` 是逐例測試,新規則要自己補 BasicTextField 那一列)

為什麼標 minor:名單多列不會做出錯誤行為,只是改壞抓不到。

severity: minor
blocking: 否

## 沒有成立的疑慮
- D-57 的證據樣式 `setPublicVersion\(|VISIBILITY_SECRET`:推送前對不上只提醒、記帳、待盲判,不擋(型錄 730 行)。通知類程式碼常見(前景服務之類)會被問,但不會誤擋。
- D-57 樣本:`main-ok` 加 `bad` 兩段,配上例外 `(無)`,符合 `situation_sample_problems` 的要求,不會紅。
- Compose Multiplatform 的 `commonMain` 沒被排除,是對的:Android 與 iOS 目標都適用。
- PIN 欄用 NumberPassword:Compose 裡只能寫在 `keyboardOptions`,有帶就不報,沒有正當寫法被誤擋。
- 自訂元件不認:是漏報,不是誤擋,計劃〈實務隱患〉已承認。

最高等級 major;blocking 1 條
