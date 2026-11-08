severity: major

我抽了 10 個以上的樣本回語料原檔核對,判讀本身沒有發現錯誤。兩份樣本外的 repo 清單沒有重疊(file: `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/5b6d202a-9139-47f7-b6b9-deb227707ba4/scratchpad/b6/corpus-pwd/`、`corpus-pwd2/`)。第二份的 40 個檔,除了 ricky1211 的另一個密碼欄(有設 `NumberPassword`)外,其餘檔案裡都找不到別處設鍵盤的痕跡。我查看的 TP 都是真的敏感欄位:API key、PIN、登入密碼、備份密語。

1.
severity: major
blocking: 是
場景:規則以 error 進 `rules/compose.yml`,消費專案一新增密碼欄就在推送前被擋。但「過升級條件」是靠合計才成立,而這個合計站不住。
- 第一份樣本外(`7/40`)單獨是 17.5%,不過條件。作者看過這份之後才加上桌面四項排除,所以它對第二版其實是樣本內。
- 第一份的 7 筆誤報裡,四項排除只擋得到 1 筆。其餘 `src/main/kotlin/DesktopUI.kt`、`demo3/src/main/kotlin/example/changepassword.kt` 的路徑都不在四項裡。第二版套回這份仍是 6/40 = 15%。
- 第二份的 0/40 是 40 個檔全沒有 Compose Desktop 特徵(judge 自己寫的),第一份卻有 3/40 桌面。這是兩份語料組成不同,不是運氣;作者自己也承認 0 誤報「主要是語料組成不同,不是排除那四項的功勞」。
- 合計 7/80 的 Wilson 95% 上界約 17%,第二份單獨 0/40 的上界約 8.8%,兩者都不是穩過 10%。
- 第二份的 40 個 TP 全來自同一批 repo,同 repo 多筆(IMIH3 三筆、Pandora、ricky1211、Organigasto 各兩筆),樣本不獨立,也沒做第二批那種 fork 去重。
- 第一、二批的用法:升級條件逐份樣本外單獨看。第二批每條規則只有一份「樣本外」,附 95% 上界(例如 `kt-webview-mixed-content-always` 寫 1.7%,上界 5.9%),形狀凍結有雜湊(`experiment/new3-frozen.sha.txt`)。第一批有一條「已達 10.5%」的舊版 TLS,直接放 `rules-unwired/`。我在這兩份計劃裡找不到任何「合計兩份」的先例。
- 這批沒有凍結雜湊,四項桌面排除是看過第一份之後才補的。RETIRE-IF 的「放行超過三成才降回」也比升級條件寬鬆三倍。
- 照字面實作的後果:一條實測值本來就在邊界的 error 規則被放進會擋的規則包。
- 建議:密碼欄先放 `rules-unwired/`,或用凍結雜湊、查詢不帶 `keyboardType` 的第三份語料重量。重量之前不要宣稱過條件。

引句:「兩份樣本外合起來 80 處誤報 7 處(8.75%),在升級條件的一成以內但很勉強;照兩份合計判,放 `rules/`。」
佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/governance/review-reports/android資安靜態檢查補齊第三批/experiment/pwd-oos-judge.md:1`(桌面 FP,路徑不在四項裡)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/governance/review-reports/android資安靜態檢查補齊第三批/experiment/pwd-oos-judge.md:29`(桌面 FP,路徑不在四項裡)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/governance/review-reports/android資安靜態檢查補齊第三批/experiment/pwd-oos2-judge.md:46`(第二份判讀理由寫明 40 個檔都沒有桌面特徵)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:108`(第二批逐條單份樣本外加上界)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/docs/lumos-toolchain-knowledge/Projects/Android資安與崩潰靜態檢查補齊_計劃.md:94`(第一批 10.5% 就放 `rules-unwired/`)

2.
severity: minor
blocking: 否
場景:兩份判讀用的準則寬嚴不一,而這會直接動到合計的分子。
- 第一份把 `org.example.project` 預設套件的登入畫面、大學 `lab7` 判成「測試或範例碼」FP。
- 第二份把 `Jetpack-Compose-Simple-Login-UI`(登入 UI 範本)、`Android-Startup-File`(範本)、`Supabase-Auth-Practices`(練習)、`projectDemo` 判成 TP。判讀代理對前三個寫了「但程式是正式的 App 碼」,對 `projectDemo` 沒給理由。
- 第一份的標準套在第二份,最多多出 4 筆誤報,第二份變 10%、合計 11/80 = 13.75%。這個推算是我的假設,未逐檔證實,但準則的「範例碼」界線沒有跨兩份統一。
- 建議:判讀準則補一句範例碼的操作定義,兩份用同一個標準重判。

引句:「第二版跟第一版只差路徑排除,第二份樣本外的 0 誤報主要是語料組成不同,不是排除那四項的功勞。」
佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/governance/review-reports/android資安靜態檢查補齊第三批/experiment/pwd-oos2-judge.md:5`(Login-UI 範本判 TP)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/governance/review-reports/android資安靜態檢查補齊第三批/experiment/pwd-oos2-judge.md:17`(Supabase-Auth-Practices 判 TP)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/governance/review-reports/android資安靜態檢查補齊第三批/experiment/pwd-oos2-judge.md:27`(Android-Startup-File 判 TP)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/governance/review-reports/android資安靜態檢查補齊第三批/experiment/pwd-oos-judge.md:2`(預設套件判 FP)

3.
severity: minor
blocking: 否
場景:天花板有一句承認缺口的話,沒有拆成獨立的回頭條件行,也沒有日期或事件。專案規則是這種話要拆成一行 REVISIT。
- 第二份判讀的結語也說,「已防護」只比對了呼叫本身和共用元件的參數,沒有逐檔找外層的設法。
- 2027-05-08 的 REVISIT 只管「查詢不帶 `keyboardType`」,沒管外層設法這個缺口。
- 天花板也沒寫密碼欄漏報沒量。第二批的〈天花板〉有寫「誤報只量了命中裡的比例,漏報沒量」,這批沒有對應句。
- RETIRE-IF 的「消費專案推送前一個月內被放行超過三成」沒寫誰在何時量。
- 建議:把這三句各拆成帶日期或事件的 REVISIT 行。

引句:「判讀只看了呼叫本身與共用元件的參數,沒有逐檔找外層用別的方式設密碼鍵盤的寫法。」
佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/governance/review-reports/android資安靜態檢查補齊第三批/experiment/pwd-oos2-judge.md:47`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-new-rules/docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:221`

最高等級 major;blocking 1 條
