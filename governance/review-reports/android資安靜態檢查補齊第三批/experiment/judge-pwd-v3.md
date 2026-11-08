# 判讀準則:kt-compose-password-keyboard(Compose 密碼欄只遮字沒設密碼鍵盤)

依據:OWASP MASTG-TEST-0258(https://mas.owasp.org/MASTG/tests/android/MASVS-PLATFORM/MASTG-TEST-0258/)與 MASTG-KNOW-0055(https://mas.owasp.org/MASTG/knowledge/android/MASVS-STORAGE/MASTG-KNOW-0055/):處理敏感資料的輸入欄沒用不快取的輸入類型(Compose 是 `KeyboardOptions(keyboardType = KeyboardType.Password)` 或 NumberPassword),鍵盤可能記住輸入、之後當建議顯示;測試判定:有任何處理敏感資料的欄位沒用不快取的輸入類型就算不過。

規則認的形狀(第三版,雜湊見 pwd-v3-frozen.sha.txt):TextField / OutlinedTextField / BasicTextField / BasicTextField2 的呼叫帶了 `visualTransformation = …PasswordVisualTransformation(…)`,而且①這個呼叫完全沒有 `keyboardOptions =` 參數,或②`keyboardOptions` 是字面的 `KeyboardOptions.Default` 或 `KeyboardOptions(…)`、裡面沒設 Password 或 NumberPassword 鍵盤。

每處看前後 20 行(ctx 檔標頭有原檔路徑,原檔在本機語料目錄,必要時打開整支看)。判:
- TP:正式碼的密碼、PIN、密語、金鑰這類敏感欄位,用了 PasswordVisualTransformation 卻沒設密碼鍵盤(呼叫裡沒有 keyboardOptions,或字面寫的 KeyboardOptions 沒設 Password、NumberPassword)。
- FP,理由欄開頭寫「FP型:<型>;」:
  - 已防護:別處設了密碼鍵盤(要逐檔往外找:同檔呼叫這個元件的地方、包住它的元件參數)(例:包在自訂元件裡、外層用 Modifier 或 CompositionLocal 設了;或這個呼叫是某個共用元件內部,鍵盤選項由別的參數帶進來)。
  - 非敏感:遮字但欄位不是敏感資料(要寫清楚是什麼)。
  - 測試或範例碼:只看兩樣東西,①檔案路徑有 `test`、`sample`、`demo`、`example`、`tutorial` 這類目錄或模組名;②repo 名(owner/名字的「名字」那段)含 sample、demo、example、tutorial、practice、lab、template、starter、course、codelab、exercise、homework、assignment 其中一個字(不分大小寫,可以是字的一部分,例:`LoginDemo`、`compose-practice`)。兩樣都沒有就照正式碼判,不因為套件名是 `com.example` 或 `org.example.project`、畫面看起來簡單、或 README 說是練習而改判。
  - 函式庫原始碼複本。
- UNSURE:看完判不出,寫缺什麼。
輸出:每處一行 TSV:序號<TAB>檔:行<TAB>TP|FP|UNSURE<TAB>理由(一句)。最後一行總計。
