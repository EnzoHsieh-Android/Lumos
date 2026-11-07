severity: minor

第二輪 6 條我逐條核對過,都修到位,沒有發現新的 major。核對方式:在 `git clone --shared` 複本跑 `python3.14 scripts/test_lumos.py -k kotlin`(389 passed、0 failed),再改壞範本看守衛有沒有紅。

**第二輪核對**
- 通才 F1(T12 矩陣基準):末四格改成〈好寫法〉加〈壞寫法:CO-1 資料層寫死 withContext〉,修掉舊違規那格移到被測程式欄。跟 E13 一致:清單帶一筆舊違規 `TagRepository`,四格的結果欄也都對得上。
- 通才 F2(`systemProperty` 只認 `archunitFreezeInit` 條件區塊內):`if (true)`、別的屬性、拿掉條件這幾種改壞都會紅。例外是 F1 那條,見下。
- 通才 F3(改描述刪舊條目):範本第 2 步與 E14 一致,E14 的實驗專案也已刪除。
- 通才 F4(格數):T12 矩陣 11 列、各組格數加總 65,都對得上;計劃表 T4 Ktor 那列也對,範本實際綁 `getLoopbackAddress()`。
- 架構對齊 F1(開頭取自 `_kt_template_sections`)與 F2(圍欄語言取法):都已收成一支。
- 圍欄語言取第一個字整字比對:範本檔現有圍欄只有 `kotlin`、`properties`、`xml` 三種,沒有帶註記或別名的,所以不會漏判。

F1
severity: minor
blocking: 否
引句:「# 兩個 systemProperty 只准出現在 -ParchunitFreezeInit 條件區塊裡:條件拿掉或改成 if (true) 就是常駐 true」
說明:條件守衛只檢查「這兩行有沒有出現在條件區塊裡」,不檢查「區塊外有沒有同一行」。我在複本的 `tasks.withType<Test>().configureEach {` 區塊內、`if (project.hasProperty("archunitFreezeInit")) {` 之前,多加兩行無條件的 `systemProperty("archunit.freeze.store.default.allowStoreCreation", "true")` 與 `allowStoreUpdate` 版本,條件區塊留著。結果 `-k kotlin_test_templates_content_guards` 仍是 210 passed、0 failed。範本因此會教人把兩個屬性常駐成 true,等於整組 `allowStoreUpdate=false` 防護失效,守衛卻是綠的。這正是通才 F2 要擋的失敗,只擋了「搬走」,沒擋「複製一份在外面」。修法:除了「在區塊內」,也要求兩行在區塊外出現次數為 0。

F2
severity: minor
blocking: 否
引句:「- 重跑:JVM 與 Robolectric 每格連跑 20 次(`--rerun`),模擬器每格 5 次(每次重裝 APK);例外是 T12 由 E13 新加的 4 格,每格跑一次(理由見 E13 末條)。」
說明:這輪只改了驗證紀錄〈做法〉的「重跑」那一條。同一節「例外」條裡仍寫「T12 每格先用〈好寫法〉帶 `-ParchunitFreezeInit` 建凍結清單再換回那格程式跑」,這句沒動,所以它仍然說 T12 的 11 格都用零違規的〈好寫法〉建清單。這跟本輪改過的範本矩陣前導句(「前七格…零違規」「最後四格…〈好寫法〉加 `TagRepository` 一筆舊違規」)互相矛盾,也跟 E13 對不上。這是通才 F1 同一類基準不一致,只修了範本沒修紀錄。守衛 `_kt_instr_records_problems` 只比格數,抓不到。
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-06_Android儀器測試範本與架構測試實跑.md:21`

總結:最嚴重是 minor,會擋 0 條
