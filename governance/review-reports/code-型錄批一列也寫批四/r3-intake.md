# r3 收貨紀錄(code-型錄批一列也寫批四)

- 兩席(審查三、架構對齊三)交回後一次存檔,取自逐字稿;兩份對 r3-snapshot.patch 全數錨定、已是正規化格式。兩席沒有建臨時目錄。

| id | 席 | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|---|
| m1 | 審查三 | major | ARCH-17 註記自己寫「不管單純呼叫 launchWhenStarted」,這列壞寫法只有單純呼叫,卻因字面是「只管」照算接電 | HIT:官方檢查頁摘要「Unsafe UI operation in finally/catch of Lifecycle.whenStarted」;註記原文自承擋不到;batch4_expected_tags 回 Android Lint | 折:註記改「相關:…擋不到這列的單純呼叫」、退回只標批一;型錄口徑句寫明「只管」只限擋得到該列壞寫法欄至少一個例子 |
| m2 | 審查三 | minor | 筆記 WHY 仍寫補了 8 列含 STATE-5;計劃結案註記寫 11 列都補成批四 | HIT:讀筆記第 57 行、計劃那行 closed | 折:改成 6 列並寫明退回的兩列;計劃結案註記改成 6 列補、5 列照標批一 |
| m3 | 審查三 | minor | 口徑句斷言比對整段開頭說明,別行也有「待查」會遮住 | HIT:開頭說明第 15 行有「待查」 | 折:斷言縮到口徑句那一行,加前置斷言恰好一行;改壞「口徑句拿掉待查」→ 紅 |
| n1 | 架構對齊三 | minor | 新回頭條件放在筆記正文檔尾,同篇另兩條在摘要區塊 | HIT:讀筆記 | 折:刪正文那行,用 summary-add 加進摘要 |

--regression-set:m2、m3、n1(m2 是 r2 修補退回 STATE-5 沒同步筆記;m3、n1 出在 r2 修補新加的斷言與回頭條件)。m1 出在第一版的改動(ARCH-17 從第一版就標批四),r2 修補只補了註記沒退回。--refuted-set none。

## 先查世界

- PRIOR-ART:m1(同類第三次:r1 三列、r2 STATE-5、r3 ARCH-17)——判讀靠註記字樣連三輪被打穿。不靠字面的做法是拿每列壞例真跑 Android Lint(官方檢查本身就是用測試樣本定義管什麼:https://googlesamples.github.io/android-custom-lint-rules/api-guide.html 〈Testing〉),測試環境沒有 Android 建置工具做不到,已寫成 Systems/kotlin規則包 的回頭條件(2027-02-08)。這輪改的形狀:把「只管」能不能照算的判準從「字面」改成「擋不到該列壞寫法欄任何一個例子就寫相關」寫進口徑句,並且三輪合計已把留下標批四的 6 列逐列對過官方檢查頁(r2 審查席 UI-10、UI-16、ARCH-16、ARCH-44、UI-3、API-9;r3 審查席重看 API-9、UI-3 並附官方頁原文)。天花板:自檢仍只驗註記與標籤一致,驗不了註記本身對不對。
- PRIOR-ART:m2、m3、n1——專案既有寫法,沒有要另查的。
