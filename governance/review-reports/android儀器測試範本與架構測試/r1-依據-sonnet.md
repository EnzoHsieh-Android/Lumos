severity: major

**F1 Room 3 已是穩定版,計劃卻把它排到 2027-05 才查,T6 的依據頁也已不是 Room 2 的寫法**
severity: major
blocking: 是
引句:「REVISIT:2027-05-06 查 Room 3(`androidx.room3`)的穩定度與消費專案有沒有人用;有就替 T6 加一份 Room 3 的〈依賴〉與 import」
- 官方版本頁 developer.android.com/jetpack/androidx/releases/room3 寫 3.0.0 在 2026-07-01 發布,穩定版 3.0.3(2026-09-09),3.1.0-alpha03 在 2026-10-21。
- T6 的主要依據頁 developer.android.com/training/data-storage/room/migrating-db-versions,現版的 `MigrationTestHelper` 範例和「Test all migrations」整段都是 `androidx.room3:room3-testing:3.0.3`,沒有 Room 2 的版本。
- 計劃卻把它當成 Room 2.7 的依據,見下一條引句。
引句:「〈依賴〉寫 Room 2.7 以上;DATA-17、DATA-19 一支逐版 `runMigrationsAndValidate`」
- 我沒在頁面上找到支持「Room 2.7 起的形狀」的原文。
- room-guard 已在 2026-10-29 用 Room 3.0.3 實驗專案實跑過,見 `docs/lumos-toolchain-knowledge/Systems/room-guard.md` 的 PITFALL 行。
- 測試品質標準也寫了 Room 3,見 `skills/lumos-project-notes/commands/test-quality-standard.md:94`。
- 後果:照計劃只做 Room 2 的範本,新專案抄到的就是舊套件,而〈依賴〉版本又沒有依據頁可對。T6 要同時寫兩份(Room 2.8.5 與 Room 3.0.3),REVISIT 的前提也要改。

**F2 前半計劃的 S2 與 REVISIT 跟本計劃綁同一支測試,本計劃沒說要改前半**
severity: major
blocking: 是
引句:「允許的範本組從 T0–T5 擴成 T0–T13;未接值清單(`_KT_UNWIRED`)拿掉」
- 前半計劃 `docs/lumos-toolchain-knowledge/Projects/Android行為測試範本與架構測試_計劃.md:181` 的 S2 也綁 `t_kotlin_catalog_c_rows_batch_resolved`,期望值是「範本 T0 到 T5、架構測試後續計劃 3、Ktor 1」。
- 同一支測試被兩份有效條款要求相反的結果。
- 前半 `:175` 的 `REVISIT:2027-01-31 開「架構測試後續計劃」` 也沒有被結案。
- 計劃的〈做法〉6 與〈回退〉都沒有處理這兩處。回退後 S2 恢復,但推進時前半條款會變成假的。
- 需要在〈做法〉加「前半 S2 改綁或標被取代、REVISIT 結案」。

**F3 K3 說 `java.time.Instant`「沒有壞處」,跟官方強跳過頁和型錄 UI-39 其餘欄位對不上**
severity: major
blocking: 是
引句:「`java.time.Instant` 這類不可變型別每次狀態更新都是新實例,沒有壞處」
- 官方強跳過頁(developer.android.com/develop/ui/compose/performance/stability/strongskipping)原文有這兩句:
  - 「Unstable parameters are compared using instance equality (`===`)」。
  - 「Add `@Stable` or `@Immutable` when the compiler can't infer stability (such as classes from non-Compose modules) and new instances with identical values are frequently allocated」。
- 頁面把「外部模組類別 + 值相同的新實例」列為需要補標註的情況,因為會多餘重組。所以 `Instant` 不是「沒有壞處」,只是壞處比較輕。
- 型錄 `skills/kotlin-idioms/checks-catalog.md:347` 的標題與壞寫法欄仍寫「外部模組型別」「欄位含 `java.time.*`」。計劃只改後果欄,見下一條引句,結果型錄壞寫法欄說壞、T13 說綠,同一列內部矛盾。
引句:「UI-39 的「後果」欄改寫成強跳過模式下的後果(見決定 2,附出處)」
- 「var 或可變集合就地改、實例不變所以畫面被跳過」是正確的推論,但頁面沒有這句話,依據欄把它當成頁面寫的。
- 建議把壞寫法欄與標題一起改,並把 `Instant` 那段降成「輕微多餘重組、不判」。

**F4 凍結清單的設定和 E5 的預期自相矛盾,刪掉清單檔會變全綠而不是全紅**
severity: major
blocking: 是
引句:「`src/test/resources/archunit.properties` 寫 `freeze.store.default.allowStoreCreation=true`」
- ArchUnit 手冊 8.6.2(archunit.org/userguide/html/000_Index.html)說這個鍵預設 `false`,必須設 `true` 才能建立新的違規清單。
- 計劃把它永久設成 `true`,所以清單檔不見或沒提交時,下一次跑會把當下所有違規重新凍結,測試綠。
引句:「改壞(刪掉清單檔)後舊違規全部重新紅」
- 這句和上面的設定相反。永久開著建立權限時,刪檔得到的是綠。
- 具體失敗場景:消費專案漏提交清單檔,CI 第一次跑就把全部舊違規凍結並通過。
- 範本應只在第一次建清單時暫時開,平時關閉;E5 的預期要對應改。

**F5 Robolectric 版本不是現況**
severity: minor
blocking: 否
引句:「**Robolectric 4.16:兩支都綠——無障礙檢查在 Robolectric 不報**」
- Maven Central 現有 4.16.1 與 4.17 穩定版(4.18-beta-1 為預覽)。
- 預實驗 P1、P2(「JDK 17 對 SDK 36 例外」「無障礙不報」)都只在 4.16 量到,依據欄卻當成一般結論。
- 至少要在 REVISIT 或〈依賴〉註明在 4.17 重跑。

**F6 ARCH-3 的測法沒有處理自動時鐘,好寫法可能也會多一頁**
severity: minor
blocking: 否
引句:「ARCH-3 同一個節點 `performClick()` 兩次後斷言返回堆疊只多一頁」
- 型錄好寫法是 `dropUnlessResumed`,只擋「生命週期低於 RESUMED」的點擊。
- Compose 測試時鐘預設 `autoAdvance = true`,第一次點擊後轉場立刻跑完,第二次點擊時生命週期已回到 RESUMED,好寫法也會多一頁。
- 同一份計劃的 TEST-29 才寫了 `mainClock.autoAdvance = false`,ARCH-3 沒寫。
- 這是我讀文件推出的失敗場景,實驗 E1、E2 應該會抓到,所以只標 minor。

**依據逐行核對**
- 網址打得開、原文吻合的有:
  - ArchUnit 1.5.1 與位元組碼原句。
  - sqlite.org limits:999 / 32766。
  - LeakCanary:2.14 與 `NoLeakAssertionFailedError`。
  - dagger.dev:兩句原文。
  - Ktor `execute`:兩句原文在不同多載,計劃有分開寫「不帶區塊的」,沒問題。
  - Robolectric `FragmentScenario` 原句。
  - Compose 無障礙頁:「small touch target size」。
  - Room 測試頁:「We don't recommend Android local unit tests with Robolectric」。
  - 強跳過頁的 `===` 與 Kotlin 2.0.20 兩句。
- 版本現況:
  - Konsist 1.0.0-beta.1、LeakCanary 2.14(2.x 最新,3.0 為 alpha)、WorkManager 2.12.0、Room 2.8.5 都屬實。
  - Ktor 現為 3.6.1,計劃交給 E8 實測,沒問題。
- 我沒有逐一開 Paging、WorkManager 測試頁和 Compose 同步頁,這幾條只做了版本號核對。

**型錄與落點**
- 型錄現況:
  - 68 列 C 列,範本 32、不接 7、未接(儀器批)25、未接(架構測試後續計劃)3、未接(Ktor 範本後續)1。
  - 計劃預期值表「範本 60、不接 8」的算術成立。
- 落點:`Systems/kotlin規則包` 與 `Systems/test-quality-cli` 都已經是範本檔、型錄、測試品質標準的家,lands_in 沒問題。
- 還沒抽查的:10 列裡 STATE-17、DATA-58 的實際例外行為(E1 實驗才驗得到)。

總結:最嚴重是 Room 3 已穩定但 T6 只做 Room 2、前半 S2 與 REVISIT 沒處理、`Instant`「沒有壞處」與官方頁不符、凍結清單設定與預期矛盾,會擋 4 條。
