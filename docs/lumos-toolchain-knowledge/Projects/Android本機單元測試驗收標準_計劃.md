---
type: project
status: doing
created: 2026-11-01
updated: 2026-11-01
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/test-quality-cli
related:
  - "[[Systems/test-quality-cli]]"
  - "[[Projects/Kotlin慣例對齊Android官方與本機detekt_計劃]]"
  - "[[Projects/Room資料庫測試守衛_計劃]]"
---
# Android本機單元測試驗收標準_計劃

> 白話:測試品質標準對 Android 只寫了資料層(Room)怎麼測,以及原生測試報告怎麼收證;ViewModel、用例、協程、Flow、Robolectric、Compose 本機測試這些「本機單元測試要有哪些、怎麼寫才算數、跑出什麼證據才算驗收過」都沒寫。這份計劃把官方指引整理成一節,接在原生收證那一節後面。

## 問題與最小解

立案:Enzo 2026-11-01 在 [[Projects/Kotlin慣例對齊Android官方與本機detekt_計劃]] 進行中提出「順帶把 Android Unit Test 的驗收標準整理出來」「上網搜全」「接在測試驗收檢查那段」;問過放哪一段,Enzo 選測試品質標準的〈C#、Android、iOS 的原生收證接入〉那一節後面。

現況(2026-11-01 主線 8b1a1cfb0):測試品質標準的 Android 內容只有〈Android 資料層(Room)的撰寫補充〉與原生收證表裡的一列(「JVM全綠不能當装置實跑;Compose/UI/生命週期/其他API另驗」)。kotlin-idioms R22 有假實作與 StateFlow 斷言兩句,但只對寫 Kotlin 的審查生效,不是驗收標準。

最小解:只加一節說明文字與一句指路,不加指令、不改任何判定。驗收的機械部分照既有的 `lumos test-quality capture/check` 收證,不另做。

PRIOR-ART: 內容借 Android 官方十頁(要測什麼、測試策略、測試替身、本機單元測試、命令列測試、協程測試、Flow 測試、Robolectric、截圖測試、大型測試穩定性)與 Hilt 測試指南、Gradle 測試篩選文件、Now in Android 的測試策略 wiki、Turbine 說明。官方另有一個 Android 測試設定 skill(`android skills add testing-setup`)產生測試策略文件,這份不重做,只寫 lumos 驗收要看的條件。形狀照抄同一份標準的〈Android 資料層(Room)〉節與它的守衛測試。
RETIRE-IF: 官方「要測什麼」或「協程測試」頁改寫到這一節的條目跟它衝突、而且半年內沒人更新這一節時,撤掉這一節改成只放官方連結 [retire:人裁] [until:2027-11-01]。

## 做法

1. 測試品質標準在〈C#、Android、iOS 的原生收證接入〉之後、〈適配器資格考卷〉之前,加〈Android 本機單元測試的驗收標準〉一節,分三段:
   - **要有哪些**:必有的單元(ViewModel、資料層、用例、工具類別)與每支的邊界情況;不要寫的(驗框架本身、Activity/Fragment/Service 入口);碰到框架時的選擇順序(Robolectric 是最後手段;Room 照前面的〈Android 資料層(Room)〉節)。
   - **怎麼寫才算數**:假實作優先、不用 Hilt 建被測物件、不開 `isReturnDefaultValues`;協程(一支一個 `runTest`、注入 dispatcher 共用排程器、MainDispatcherRule、Standard 與 Unconfined 的選法、`backgroundScope`、不用真實時間);Flow(StateFlow 斷言 value、`stateIn` 要先起收集者、有限流與不結束的流、Turbine 的收法、事件化成狀態的三步);Compose 本機行為測試與截圖測試(選配)。
   - **什麼證據才算過**:指令與報告位置、收證照上一節;無效證據清單(零選中、編譯錯、逾時、靠預設回傳值才綠、本機綠當裝置綠、重試到過);涵蓋率只拿來找漏;故障證明挑本次需求。
   - 社群做法(Now in Android、Turbine、變異測試工具)標明非官方;每個官方來源列核對當天看到的更新日期。
2. `03-寫回圖譜.md`〈實作測試品質〉那一句加指路到新的一節。
3. `Systems/test-quality-cli` 記一行這次加了什麼。
4. 測試照 Room 節的守衛形狀:新節在指定位置、三段依序、幾個關鍵詞在、03 指得到。

## 驗收條款

- [S1] 當讀測試品質標準時,〈Android 本機單元測試的驗收標準〉一節應緊接在〈C#、Android、iOS 的原生收證接入〉之後,「要有哪些」「怎麼寫才算數」「什麼證據才算過」三段依序出現並提到 MainDispatcherRule、isReturnDefaultValues、Robolectric、零選中與故障;03〈實作測試品質〉應有一句指到這一節。 [test:t_test_quality_standard_android_unit_section]
- [S2] 這一節的每一條官方規定,都應找得到列在來源裡、帶核對日期的官方頁;非官方的做法應標明是社群做法。 [manual:逐條對照來源頁核對出處]

## 回退

還原這次提交即可:標準裡的一節、03 的一句指路、test-quality-cli 的一行、一支新測試。不碰任何帳本與判定。

## 實務隱患

- 效能:只多一支讀兩個檔的測試。
- 已排除:金流:不碰任何金流或支付資料。
- 已排除:對外送出:不對外寄送任何東西。
- 已排除:不可逆:全部是文字與測試,還原提交即可回退。
- 已排除:守衛面:只加說明文字與一支讀檔測試,不改任何判定與擋下條件。

## 審計修正紀錄

- 代碼審 r1(standard,單席加架構對齊,跟 [[Projects/Kotlin慣例對齊Android官方與本機detekt_計劃]] 同一個迴圈):新節開頭補單源指向這篇(兄弟節都有);守衛測試的檔案存在檢查改用既有的 `_need_src`。席報告:`governance/review-reports/code-Kotlin慣例對齊與Android單元測試驗收/`。
