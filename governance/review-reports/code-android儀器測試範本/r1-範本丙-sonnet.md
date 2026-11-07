severity: major

我查了 Maven Central:ArchUnit 1.5.1、Konsist 0.17.3 與 1.0.0-beta.1、Hilt 2.58、Robolectric 4.17 都存在。ArchUnit 1.5.1 的原始碼我也讀了。T11、T12、T13 的 API 用法、`ImportOption` 路徑排除、`goAsync` 豁免、凍結清單的行號正規化,都沒查到會編不過或誤報的地方。

F1
severity: major
blocking: 是
位置:T12〈舊違規凍結〉第三段,「為什麼不常駐 true」。
引句:「設 false 時清單不見就丟 `StoreInitializationFailedException`,測試紅」
問題:範本把 `allowStoreCreation=false` 當成「清單被刪或漏提交就會紅」的守衛。ArchUnit 1.5.1 的原始碼不是這樣:
- `allowStoreCreation` 只管索引檔 `stored.rules` 存不存在。`getStoredRulesFile()` 在索引檔不存在且 `allowStoreCreation=false` 時才丟例外。
- 索引檔存在之後,規則描述不在索引裡時,`FreezingArchRule.evaluate` 走 `storeViolationsAndReturnSuccess`。它把當下全部違規存起來並回傳成功,不看 `allowStoreCreation`。`allowStoreUpdate` 預設 true,所以存檔也過得了。
- 規則描述是 `ArchRule.getDescription()`,在範本裡是 `classes().should(ArchCondition("…"))` 的描述字串。

失敗場景,照抄範本會遇到:
1. 照三步建好清單並提交。
2. 之後有人加第三支 `@Test`(例如新的 K3 規則),或改了 `ArchCondition` 的描述字串,或用 `.as(…)` 改名。
3. 這條規則在索引裡找不到,第一次跑就把現有所有違規凍結並回綠,不用 `-ParchunitFreezeInit`,也不丟 `StoreInitializationFailedException`。
4. 凍結後的檔案只是工作目錄裡多出一個 `.txt`,不提交也不會紅。

這等於範本宣稱「清單只能縮小、新增要在代碼審說明」,實際上新增規則或改描述會繞過去。矩陣步驟①~⑤只驗了「整個清單目錄不見」,沒驗「索引在、規則是新的」。
審材外佐證:ArchUnit 1.5.1 sources jar 的 `com/tngtech/archunit/library/freeze/FreezingArchRule.java`,`evaluate` 裡的 `!store.contains(delegate)` 分支。同一個 jar 裡 `TextFileBasedViolationStore.java` 的 `getStoredRulesFile`,只檢查索引檔。
修法方向:
- 範本明講 `allowStoreCreation=false` 只擋「索引檔整份不見」。
- 新增規則或改描述要視為重新凍結,走代碼審。
- 可加一道守衛,例如單元測試斷言 `archunit_store/stored.rules` 的鍵集合等於已知規則描述。

F2
severity: minor
blocking: 否
位置:T11 STATE-17 說明。
引句:「背景執行緒連 `postValue` 兩次後 `shadowOf(getMainLooper()).idle()`,斷言觀察者總共看到兩筆」
問題:文字說的是觀察者總共看到兩筆,但測試斷言的是 `seen.lastOrNull()` 等於包含兩則訊息的那一份清單。好寫法下,因為 `postValue` 在主執行緒處理前合併,觀察者只收到一次通知,那一次的內容有兩則訊息。照字面讀的 AI 可能把斷言改成 `seen.size == 2`,好寫法反而紅。

總結:最嚴重是 F1(凍結清單守衛說得比實際強,新增規則或改描述會被靜默凍結成綠),會擋 1 條。
