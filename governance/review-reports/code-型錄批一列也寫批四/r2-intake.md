# r2 收貨紀錄(code-型錄批一列也寫批四)

- 兩席(審查二、架構對齊二)交回後一次存檔,取自逐字稿;兩席第一版說明文字各有一行等級字樣(「嚴重度:」、總結行「max severity:」),退回該席只改那幾行重交;兩份對 r2-snapshot.patch 全數錨定、已是正規化格式。
- 兩席的臨時目錄 /tmp/lumos-seat-work/code-型錄批一列也寫批四/ 是空的,收貨後刪掉。

| id | 席 | 原報 | 一句 | 重現 | 處置 |
|---|---|---|---|---|---|
| k1 | 審查二 | major | STATE-5 標了批四(Android Lint),但唯一被口徑認得的 RepeatOnLifecycleWrongUsage 只管 repeatOnLifecycle 呼叫的位置,擋不到這列的壞寫法「根本沒包」 | HIT:curl 官方檢查頁原文「The repeatOnLifecycle APIs should be used when the View is created, that is in the onCreate … or onViewCreated」;列的壞寫法是 collectAsState 與 launch 裡直接 collect,沒有呼叫 repeatOnLifecycle,兩者無交集 | 折:那段補「(相關:…)」註記、通電批次退回只標批一;型錄自檢 0 問題 |
| k2 | 審查二 | minor | batch4_expected_tags 的說明與 _batch4_problems 的錯誤訊息還列舊的四個排除字 | HIT:讀碼,字表已是七個 | 折:錯誤訊息改成從 _B4_SKIP 產生、說明改成指向 _B4_SKIP;補斷言「錯誤訊息列齊每個排除字」先紅(缺相近、間接、相關、需標註)後綠,另補「型錄口徑句列齊每個排除字」;筆記那行 WHY 同步 |
| k3 | 審查二 | minor | ARCH-17 的「只管」註記讓人以為單純呼叫 launchWhenStarted 也會被擋 | HIT:官方檢查頁只在 finally/catch 碰 UI 時報 | 折:註記補「不管單純呼叫 launchWhenStarted」;仍照「只管」口徑算接電(擋得到其中一部分) |
| l1 | 架構對齊二 | minor | 同 k2 的函式說明 | HIT:同 k2 | 折:同 k2 |

--regression-set:k2、l1(r1 修補加了三個排除字,沒同步說明文字)。k1、k3 出在第一版的改動,不是 r1 修補造成的。--refuted-set none。

## 先查世界

- PRIOR-ART:k1、k3(同類第二次:r1 退回 TEST-23、UI-1、PERF-2,r2 又出 STATE-5)——查 Android Lint 怎麼確定一條檢查管什麼:官方做法是每個檢查附測試樣本(lint 的 `lint().files(...).run().expect(...)`,https://googlesamples.github.io/android-custom-lint-rules/api-guide.html 〈Testing〉),檢查頁的說明與實作原始碼連結就是「管什麼」的權威(https://googlesamples.github.io/android-custom-lint-rules/checks/RepeatOnLifecycleWrongUsage.md.html)。不靠字面判斷的換形狀做法是「拿每列的壞例真跑一次 Android Lint、命中才算接電」;這要 Android Gradle 外掛與專案骨架,測試環境沒有,這輪不建,回頭條件寫進 Systems/kotlin規則包。這輪改用同一把尺把留下標批四的 8 列全部對過官方檢查頁(審查席查 6 列、編排者補 STATE-5 與 ARCH-17),只有 STATE-5 完全沒交集。排除:靠註記字樣自動判(只能判已寫的註記,判不了沒寫註記的列,正是 STATE-5 漏的原因)。
- PRIOR-ART:k2、l1——同一份字表多處手抄會漂,統一改成從字表產生(Python 常見做法:訊息用 "、".join(常數) 組),不再手抄。
