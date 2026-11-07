severity: minor

F1
引句:「// 錯的寫法:有無限動畫時讓時鐘自動推進,測試等不到 idle」
severity: minor
blocking: 否
說明:這行註解跟 T9 開頭的段落(「Compose 1.11 下讓時鐘自動推進的〈壞測試〉在 Robolectric 與模擬器都綠、沒卡住」)互相矛盾。驗證紀錄「E4 跑在哪的對照」與「TEST-29 移出」也寫了同樣的實跑結果:兩邊都綠、沒卡住。AI 照抄這份〈壞測試〉時,會把「自動推進就等不到 idle」當成事實學走。〈測試〉裡的註解「有無限動畫的畫面,關掉自動推進再推時鐘」也是同一個前提。建議把註解改成實測結論,例如「1.11 實測也綠,這裡只示範不推進的寫法」。

F2
引句:「跑在哪:〈測試〉九列在 Robolectric(`app/src/test`);〈測試:無障礙〉只在模擬器(`app/src/androidTest`)」
severity: minor
blocking: 否
說明:「九列」只有把 TEST-29 算進去才成立,但同一段的型錄列清單沒有 TEST-29,只列了 8 列。〈測試〉類別實際有 10 支 `@Test`,驗證紀錄寫「Robolectric 10 格」,矩陣也是 10 支。數字在同一段裡對不上,容易讓 AI 以為少了一支或多了一支。這不影響編譯,也不影響紅綠。

其餘我逐項查過,沒找到會擋的問題:
- **API 與依賴(鏡頭 1)**:
  - Compose 官方無障礙測試頁(developer.android.com/develop/ui/compose/accessibility/testing)確認 `enableAccessibilityChecks(validator)` 與 `AccessibilityValidator().setThrowExceptionFor(WARNING)` 的用法,`tryPerformAccessibilityChecks` 與 `ui-test-junit4-accessibility` 也在。
  - LeakCanary 官方頁(square.github.io/leakcanary/ui-tests/)確認 `androidTestImplementation leakcanary-android-instrumentation:2.14`、`debugImplementation leakcanary-android:2.14` 必須兩個都加,以及 `LeakAssertions.assertNoLeaks()` 丟 `NoLeakAssertionFailedError`。
  - 版本組合(BOM 2026.06.01、navigation 2.9.8、lifecycle 2.10.0 等)我沒有逐一上 Maven Central 查證。驗證紀錄的「版本天花板」節說它們能編過;我只憑 `Verification/2026-11-06_Android儀器測試範本與架構測試實跑.md` 採信。
- **照抄的坑(鏡頭 3)**:`kotlin("test")`、`androidx.test.ext:junit` 與 runner(androidTest)、`isIncludeAndroidResources`、`targetSdk = 36`、`testInstrumentationRunner`,都在 `skills/kotlin-idioms/test-templates.md` 的〈Android 實驗專案骨架〉(約第 56 到 128 行)。T9 另寫了 Compose 外掛、`buildFeatures`、`ui-test-manifest` 與 `robolectric.properties`,沒有漏。
- **對照有效性與跟驗證紀錄對得上(鏡頭 2、4)**:紅綠矩陣的 T9 13 格(Robolectric 10、模擬器 3)與 T10 2 格,跟驗證紀錄的「S4 矩陣」「E4」「E12」數字與結論一致。STATE-12 的 `ComposeTimeoutException`、ARCH-3 的 `autoAdvance` 必要性、UI-110 要傳 WARNING、LeakCanary 少 `debugImplementation` 就錯綠,也都對得上。

總結:最嚴重是 minor(TEST-29 〈壞測試〉註解與實測矛盾、「九列」計數說法),會擋 0 條
