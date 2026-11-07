# r1 收貨紀錄(code-android行為測試範本)

## 收貨

- 第 1 輪,standard。材料 3931 行超過 1800,拆三包:甲 r1-snapshot-甲.patch(程式、型錄、測試、筆記,1063 行)、乙 r1-snapshot-乙.md(範本檔開頭加 T0–T1,1407 行)、丙 r1-snapshot-丙.md(範本檔開頭加 T2–T5,1167 行);整份凍結 r1-snapshot.patch(sha256 78989b7d…)。四席全 sonnet(甲審、乙審、丙審、架構對齊);外家預設不派,結論寫成「單家族視角下」。
- 從逐字稿存檔,全部正規化、引句全錨。乙、丙兩席在純 JVM 與 Android library 模組實跑變形格,重現檔在席位臨時目錄。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 五丙1 | 丙審 F1 | T3 viewModelScenario 版放進 Android library 模組跑 testDebugUnitTest | HIT(席位實跑):`Method containsKey in android.os.BaseBundle not mocked` |
| 五丙2 | 丙審 F2 | 範本好寫法 TokenAuthenticator 5 執行緒並行 401 | HIT:刷新 4 次 |
| 五丙3 | 丙審 F3 | DATA-72 標準寫法 `String? = null` | HIT:誤紅 `[null, null]` |
| 五乙1 | 乙審 F1 | TEST-6 只取一次快照的變形 | HIT:照綠 |
| 五乙2 | 乙審 F2 | CO-14 第二種標準寫法(區塊內 try/finally) | HIT:誤紅 `Success(false)` |

refuted: none

## 先查世界

- PRIOR-ART: 兩類對稱問題——斷言比型錄那列要的多(把某一種實作的細節寫死,誤擋合法寫法:五丙3、五乙2、丙 F8)與斷言比要的少(只驗一次或只驗一半,放過壞寫法變形:五乙1、五丙2、丙 F7)。業界測試原則「測行為不測實作」(Android 官方測試基本頁 https://developer.android.com/training/testing/fundamentals 、Google Testing Blog「Test Behavior, Not Implementation」)。採用:每支範本測試只斷言型錄那列「後果」欄描述的可觀察行為;型錄有兩種以上標準寫法的,斷言要對每一種都成立(或明寫要專案表態);每支測試至少驗兩次狀態變化或一次並行,才算驗到「跟隨」「加鎖」。
- PRIOR-ART: T3 在 Android 模組跑不起來——官方 SavedStateHandle 測試頁寫「create a new instance of SavedStateHandle with the test values」(https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate );Android 單元測試的 android.jar 是空殼、要 Robolectric 才有 Bundle(https://developer.android.com/training/testing/local-tests )。採用:Android 專案預設用複製 handle 版,viewModelScenario 版標成純 JVM/KMP 模組或加 Robolectric 才用,並寫明兩版各自不涵蓋什麼(provider、Bundle 可存型別)。

## 逐條去向

全部折入(21 條:甲審 3、乙審 7、丙審 9、架構對齊 2),細目由修補提交與修正紀錄對照。
