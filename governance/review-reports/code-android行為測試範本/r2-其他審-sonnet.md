severity: minor

我跑了 `python3.14 scripts/test_lumos.py -k kotlin_test_templates`,85 條全綠。mutation 在 `/tmp/lumos-seat-work/code-android行為測試範本/其他審-sonnet/repo` 的複本裡做,沒動原 repo。這個複本還沒清,我沒刪;按規則該由編排者在收貨後用字面絕對路徑刪。

## 修補三問

r1 的 5 條修補都修好了:

- **圍欄內假標題(甲 F1)**:改壞四在 `T3` 標題被改掉、只剩圍欄內假標題時,要報兩列,跑得過。整行 `## T3` 的對照組也綠。
- **非 UTF-8(甲 F2)**:我按改壞五的重現跑過,不丟例外,回一筆 `<templates>`。
- **新舊 Turbine 句、主表讀一次、批次口徑**:這三條在 diff 裡有對應的新斷言,我另外確認了 `catalog_problems` 把讀好的列交給 `template_problems(rows)`。
- **新簽名的呼叫者**:`template_problems(rows=None)` 在 repo 內只有 `catalog_problems` 和測試在呼叫,沒有漏改的地方。
- **「`## T<n>` 整行也算」會不會誤認別的行**:不會。比對用 `^## (T\d+)(?:[ \t]|$)`,前面又先剝了圍欄。

## 新發現

F1 剝圍欄的邏輯沒考慮圍欄長度和 info string
severity: minor
blocking: 否
引句:「        m = _FENCE_RE.match(ln)」
file: `configs/ast-grep/kotlin-android/check.py` 的 `_outside_fences`、`_FENCE_RE`
- `_FENCE_RE` 只取前三個字元,收尾圍欄不要求等長、也不要求沒有 info string。四反引號的外層圍欄包三反引號的內層時,開關會錯位。
- 重現:輸入 `` "````md\n```kotlin\nx\n```\n```\n## T3 fake\n```\n````\n## T9 real\n" ``。外層被內層的 `` ```kotlin `` 提早收掉,後面的真標題反而被吞。
- 錯位只會讓真標題被吞,表現成「缺節」,方向是擋下而不是放過,而且現有範本檔沒有四反引號。
- `~~~` 圍欄沒有測試。我把 `_FENCE_RE` 的 `~~~` 拿掉,85 條照綠。未閉合圍欄也沒有測試。

F2 「範本 T<n>」寫成別的樣子時,自檢無聲略過
severity: minor
blocking: 否
引句:「        m = _TEMPLATE_VALUE_RE.fullmatch(behavior_value(c[9]) or "")」
- `fullmatch` 要整段值剛好是 `範本 T3`。`範本 T3(備註)`、`範本T3`、`範本 T3+T4` 都會被當成沒引用,不報。
- 我實測 `behavior_value` 對 `範本 T3(備註)` 回「範本 T3(備註)」,這個值進 `fullmatch` 就落空。
- 現在 `t_kotlin_catalog_c_rows_batch_resolved` 把值限定在白名單,所以暫時抓得到。但 `template_problems` 自己對這種寫法是 fail-open。

F3 內容守衛的 Turbine 禁用清單不全
severity: minor
blocking: 否
引句:「    banned = ("awaitItem(", "awaitError(", "awaitComplete(", "expectNoEvents(", "expectMostRecentItem(")」
- 我在複本把 T0〈測試〉裡的 `cancelAndConsumeRemainingEvents()` 換成 `awaitEvent(); ensureAllEventsConsumed()`,守衛照綠。
- `ensureAllEventsConsumed` 和 `skipItems` 失敗時同樣丟 `TurbineAssertionError`,收證同樣不算斷言,等於原來要防的問題換個名字就繞過。
- 守衛也沒檢查 `.test { }` 區塊結尾有沒有收尾的 `cancelAndConsume…`。

其他守衛我都試過,抓得到:
- 壞寫法標題改名後沒進矩陣:紅。
- T4 的「沒加鎖」矩陣列被改成「綠」:紅。

F4 計劃〈做法〉3 沒跟上新規則
severity: minor
blocking: 否
引句:「主表每列的通電批次裡出現「範本 T<n>」時,範本檔要有一個以 `## T<n> ` 開頭的標題」
- 這段是 diff 裡的未改動前後文(context),描述的是舊行為。
- 現在程式只認「行為測試或正向約束=」那一段,標題後面可以接整行,而且不算圍欄內的行。計劃本文沒同步,和 Systems 新增的 WHY 行不一致。

F5 驗證紀錄和計劃的 E5 條文沒標過期
severity: minor
blocking: 否
引句:「E5:`lifecycle-viewmodel-testing:2.9.4` 的 `viewModelScenario { … }.recreate()` 在純 JVM 能還原 `SavedStateHandle` 內容,T3〈測試〉改用它」
- 同一行還寫「測試品質標準『畫面重建與程序被回收』那條不用補句」。
- 這一輪 T3 預設〈測試〉已改回複製 handle 版,測試品質標準那條也補了句,所以這一行現在是錯的。
- 計劃〈實作〉節的「E5 成立:T3〈測試〉改用 `ViewModelScenario.recreate()`」同樣沒標已被代碼審 r1 推翻。
- 驗證紀錄只有「每格結果」加了「第一版」字樣,E5 這條沒有。

F6 `Systems/test-quality-cli` 沒記這輪改動
severity: minor
blocking: 否
引句:「-  - 社群:用 Turbine 時,每個發出的值都要收掉,或用 `cancelAndIgnoreRemainingEvents()` 明講不管;錯誤用 `awaitError()` 收;不要用 `runCurrent()` 去推 Turbine。要拿來當收證「抓到錯」的那一步時不能靠這些」
- 這一輪動了測試品質標準的三處:Flow 舊句、Flow 指路句、「畫面重建與程序被回收」整條改寫。
- `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md` 沒有在這個修補範圍內(87c825676..cea727087 的差異)裡更新。它第 93 行還只說「兩條各帶一個坑」,沒提第三處。
- 這個 Systems 節點是 `test-quality-standard.md` 的家。

F7 依據表的新行欄數多一欄
severity: minor
blocking: 否
引句:「- T1 逾時是取消的子類(代碼審 r1 改引 API 頁:指南那頁已改寫、沒有這兩句;」
- 這一行比其他行多一個「舊引句」欄,變成 5 欄,其餘是 4 欄(名|引句|來源|對應)。
- 內容我核對過了:WebFetch 開 withTimeout API 頁,三句引文逐字都在。

## 文件對程式

我逐項核對,沒問題的:
- 驗證紀錄「71 格」:我從範本檔的矩陣數出 19+16+11+8+10+7=71。
- 「全綠 19 格」:表上有紅的 52 列,52+19=71,對得上。
- T3 在 Android 模組的描述,和範本 `skills/kotlin-idioms/test-templates.md` 第 2128 行以及驗證紀錄一致。
- Systems 新 PITFALL 的「一律例外紅」和驗證紀錄一致。

總結:最嚴重是 minor(守衛禁用清單不全、剝圍欄邏輯對長圍欄與 `~~~` 沒測、兩處文件過期),會擋 0 條。
