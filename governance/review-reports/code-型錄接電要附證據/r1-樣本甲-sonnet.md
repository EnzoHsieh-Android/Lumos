severity: major

我逐支對照了 56 支樣本的壞寫法欄(主表第 3 欄)與〈接電證據〉判定。我沒有重跑 Android Lint 或 detekt。環境裡沒有真跑工程,以下判斷都靠比對文字。

1. UI-13:判「擋得到」的 AutoboxingStateValueProperty,樣本改用隱含接收者寫法
severity: major
blocking: 是
- 壞寫法欄寫的是「`MutableIntState` 用 `.value` 讀寫」,也就是明確寫出 `.value` 的讀寫。
- 樣本把它改成擴充函式裡不帶接收者的裸 `value`。
- 判定理由也自承「用隱含接收者讀的 value」,而且樣本沒有任何寫入。
- 若檢查只在隱含接收者寫法下才報,型錄就是靠壞寫法欄沒說的觸發條件多宣稱 CI 會擋。
- 建議補一支帶明確 `s.value` 讀寫的樣本(例如 `fun f(s: MutableIntState) { s.value; s.value = 1 }`)重跑。報得出才維持原判,否則改「擋不到」。
- 引句:「@Composable fun MutableIntState.Read() {」
- 佐證:壞寫法欄在 `skills/kotlin-idioms/checks-catalog.md:340`,判定在 `skills/kotlin-idioms/checks-catalog.md:888`。

2. API-23:UsingHttp 判「擋不到」,樣本只放 manifest
severity: minor
blocking: 否
- 壞寫法欄有兩種寫法:baseUrl `"http://…"` 與 manifest `usesCleartextTraffic="true"`。
- 理由說「… 不能抄」,所以只做了 manifest 那一種。
- 但 `…` 只是佔位,規則允許補成最小寫法,例如 `val baseUrl = "http://example.com"`。
- 少了這一種,UsingHttp 的「擋不到」只驗了半條,型錄可能少宣稱,方向安全。
- 引句:「<application android:usesCleartextTraffic="true" />」
- 佐證:`skills/kotlin-idioms/checks-catalog.md:175`、`skills/kotlin-idioms/checks-catalog.md:861`。

3. API-44:DefaultTrustedUserCerts 判「擋不到」,樣本漏了壞寫法欄第二種
severity: minor
blocking: 否
- 壞寫法欄第二種寫法是「targetSdk 低於 24 又沒有 network_security_config」。
- 判定理由自承「沒做樣本」。
- 樣本只放了 `<certificates src="user" />`,而且 targetSdk 是 36。
- 這條檢查正是針對第二種寫法,沒對它做樣本就判「擋不到」,結論不成立。
- 同一模組內,x_api_46(targetSdk 27)已經證明資安包有載入,補樣本不難。
- 引句:「<certificates src="user" />」
- 佐證:`skills/kotlin-idioms/checks-catalog.md:196`、`skills/kotlin-idioms/checks-catalog.md:868`。

4. API-47:UnintendedExposedUrl 判「擋不到」,樣本只放程式裡的 const
severity: minor
blocking: 否
- 壞寫法欄寫的是「設定檔或程式裡」的位址。
- 樣本只做了程式內的 `const val`,沒有設定檔版本(例如 `strings.xml`、`buildConfigField`)。
- 另外,`192.168.1.10` 對應的 UnintendedPrivateIpAddress 因為「、」切段沒被列為候選,所以沒有獨立判定。
- 樣本其實已經含這個 IP,若它會報,型錄少宣稱。
- 引句:「const val STAGING_URL = "http://staging-app.com"」
- 佐證:`skills/kotlin-idioms/checks-catalog.md:199`、`skills/kotlin-idioms/checks-catalog.md:870`。

5. UI-23:LocalContextGetResourceValueCall 判「擋不到」,理由「編不過」站不住
severity: minor
blocking: 否
- 壞寫法欄第二個例子是 `LocalContext.current.getString(...)`。
- 理由說 `getString(...)` 編不過所以不放。
- `...` 是佔位,補成 `getString(0)` 或帶資源 id 即可編過。
- 樣本只有 `resources.configuration.orientation` 這一行,因此這條「擋不到」其實沒驗到它該檢查的寫法,型錄可能少宣稱。
- 引句:「LocalContext.current.resources.configuration.orientation」
- 佐證:`skills/kotlin-idioms/checks-catalog.md:350`、`skills/kotlin-idioms/checks-catalog.md:899`。

6. UI-54:樣本本體是空的,兩列「擋不到」的前提不成立;Android Lint 那列的理由還指錯對象
severity: minor
blocking: 否
- 壞寫法欄只有簽名 `@Composable fun Card(title: String)`,名稱「Card」暗示會畫東西。
- 樣本用空本體,詳見 detekt 那列理由:本體是空的、沒畫任何東西。
- ModifierMissing 這類規則只管會輸出 UI 的 composable,空本體不會報,所以「擋不到」是樣本造成的。
- 這是少宣稱,方向安全,但判定沒有反映壞寫法欄的真意。
- Android Lint 那列的理由只寫「沒報(理由同上)」。
- 表中它的上一列是 UI-49 的 ConstantContentStateKeyInItemsCall,「同上」指向錯誤。這一列的理由寫在下一列的 detekt 儲存格裡,對不上。
- 引句:「@Composable fun Card(title: String) {」
- 佐證:`skills/kotlin-idioms/checks-catalog.md:381`、`skills/kotlin-idioms/checks-catalog.md:915`、`skills/kotlin-idioms/checks-catalog.md:916`。

7. UI-65 與 UI-56:理由欄寫「樣本自驗沒過,見第 3 節」,沒有交代
severity: minor
blocking: 否
- 兩列都判「擋得到」,但理由說樣本自驗沒過,見第 3 節。
- 型錄理由欄的讀者看不到「第 3 節」是哪裡,也不知道自驗失敗的原因和是否已處理。
- 判「擋得到」的依據不清楚,理由跟樣本對不上。
- 引句:「override fun onAttach() { currentValueOf(LocalX) }」
- 佐證:UI-65 判定在 `skills/kotlin-idioms/checks-catalog.md:933`;UI-56 判定在 `skills/kotlin-idioms/checks-catalog.md:919`。

8. UI-3:理由說 `delay(..)` 編不過,不成立
severity: minor
blocking: 否
- 壞寫法欄是 `LaunchedEffect(Unit) { delay(..); onTimeout() }`。
- `delay(1000)` 在 LaunchedEffect 的 suspend lambda 裡可以編過。
- 樣本刪掉 delay 只是少放一個元素,不會多出觸發條件,所以「擋得到」仍可信。
- 但理由的陳述有誤。
- 引句:「LaunchedEffect(Unit) {」
- 佐證:`skills/kotlin-idioms/checks-catalog.md:330`、`skills/kotlin-idioms/checks-catalog.md:876`。

9. UI-16:理由說 `SimpleDateFormat(...)`、`Regex(...)` 編不過,不成立
severity: minor
blocking: 否
- `...` 是佔位,`SimpleDateFormat("yyyy")` 和 `Regex("a")` 都編得過。
- 「擋得到」靠 Animatable 等其他例子成立,結論不受影響。
- 理由有誤,且這兩個寫法沒進樣本。
- 引句:「val d by derivedStateOf { }」
- 佐證:`skills/kotlin-idioms/checks-catalog.md:343`、`skills/kotlin-idioms/checks-catalog.md:892`。

其餘 47 支我看過,沒有發現加了壞寫法欄沒說的觸發條件,或理由與樣本對不上。
- API-22 的樣本把類別寫成 `abstract` 是為了省 `getAcceptedIssuers` 的回傳行。規則允許補回傳值,所以這不是新增觸發條件。
- UI-31、UI-8、UI-43、UI-49、UI-62 把大括號或 lambda 換到下一行,只是排版,不影響檢查。
- UI-57、UI-58 自宣告空殼 `Text`,屬於允許的外層宣告。

看過 56 列(API-9、22、23、37、38、39、42、43、44、46、47;STATE-15、22;UI-2、3、4、5、8、9、10 至 17、20、22 至 27、31、41、43 至 46、49、54 至 60、62 至 65、68、69、72、73)。
最高等級 major;blocking 1 條。

被審 patch:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/governance/review-reports/code-型錄接電要附證據/r1-snapshot-samples-a.patch`。
型錄對照:`/Users/enzo/orca/workspaces/lumos-toolchain/android-unwired-sem/skills/kotlin-idioms/checks-catalog.md`。

這次沒有建立任何臨時目錄或暫存檔,也沒有改 repo 裡的檔案。
