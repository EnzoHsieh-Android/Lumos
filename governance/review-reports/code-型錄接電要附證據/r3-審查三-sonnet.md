severity: clean

審查結論:這輪修補沒有帶出回歸,三項鏡頭都沒找到會做錯的問題。

我在 repo 根跑了 `python3.14 scripts/test_lumos.py -k kt_catalog`:197 passed、0 failed。`check.py --catalog-only` 回報型錄問題 0 個。`scripts/test_lumos.py` 的雜湊值(`cfa22d2d…`)跟 `governance/anchor-baseline.json` 一致。

1. 回歸與判定對得上通電批次(鏡頭①)
   - 引句:「+| UI-54 | 公開 composable 沒 modifier 參數 | `@Composable fun Card(title: String)` | `fun Card(title: String, modifier: Modifier = Modifier)` | 呼叫端無法調版面 | cr:compose:modifier-missing-check / ModifierMissing;slack:ComposeModifierMissing | A | 形狀:public 發出 UI 的 composable 沒有 Modifier 參數 | 告警帶寫法 | 告警帶寫法=未接(登記的現成檢查擋不到這列壞寫法,見〈接電證據〉)」
   - 佐證:`/tmp/lumos-seat-work/lint-rerun/app/build/reports/lint-results-debug.txt` 對 ARCH-39、40、41、70、81、86 報的檢查項與「接電證據」判定一致,行號只差檔頭 2 行。
   - 佐證:`/tmp/lumos-seat-work/lint-rerun/app/src/main/java/wiring/` 底下 ARCH-25、39、40、41、70、81、86 的樣本,逐字等於 repo 的 `configs/ast-grep/kotlin-android/samples/lint-wiring/` 樣本。
   - UI-54 和 ARCH-25 改回「擋不到」、通電批次改「未接」,跟型錄自檢一致,屬於少宣稱,不會造成錯誤放行。
   - 一個沒重跑到的缺口:UI-54 的 detekt 判定沿用第一次真跑的結果。重跑目錄裡的 `detekt.log`(16:24)是 UI-54 還帶 `Text(title)` 時跑的,樣本 16:42 改回空本體後 detekt 沒重跑。引句:「+| UI-54 | 推送前:detekt 外掛 compose-rules | modifier-missing-check | 擋不到 | 沒報 | 沒報:壞寫法欄只寫簽名,樣本照寫空本體,這條只管會畫東西的元件(2026-11-08 第一次真跑) |」。這個判定只會少宣稱,而且文字已寫明沿用第一次真跑,所以不算缺陷。

2. 10 列樣本有沒有另加觸發條件(鏡頭②)
   - ARCH-40:壞寫法欄寫「當路由沒有 @Serializable;enum 參數 minify 下沒 @Keep」。樣本的 `composable<Detail>`、`composable<Home>` 就是「當路由」。
   - ARCH-40:`@Serializable data class Filter(val kind: Kind)` 加 `composable<Filter>` 是 enum 參數成立的最小外殼,沒有它「enum 參數」那一項寫不出來。這兩處我都算欄裡寫的,不算另加觸發條件。
   - 引句:「+    composable<Filter> { }」
   - ARCH-39、41、70、72、73、81、86 逐一對過壞寫法欄,各只多了欄裡寫的那一項:createGraph 的 startDestination、`activity` 加 `deepLink`、`FLAG_MUTABLE` 配 `Intent()`、隱式 action 加 manifest 註解、`cache-path` 的 `.` 與絕對路徑、`AUTOFILL_TYPE_TEXT`、`@IntDef` 加 `m(3)`。ARCH-39 的 `createGraph` 這一項能引用 `ARCH_39.kt:20` 的 `WrongStartDestinationType` 報告支持。
   - ARCH-41 的 `DeepLinkInActivityDestination` 判擋不到,重跑的 lint 結果裡確實只有 `EmptyNavDeepLink`。

3. 新測試能不能被改壞而照綠(鏡頭③)
   - 引句:「+    mutate("UI-24 通電批次沒有告警帶寫法只有批四", lambda ls: setcol(ls, 9, "批四(" + lint + ")", main24), "UI-24", "只准寫在")」
   - 我在 `/tmp/lumos-seat-work/code-型錄接電要附證據/審查三-sonnet/` 下的 repo 副本(沒動 repo 本身),對 `_batch4_have` 的三個條件各拿掉一次,跑 `-k kt_catalog_batch4_evidence`。結果:
     - 拿掉 `i < 0`:S2/S4「沒有告警帶寫法只有批四」變紅。
     - 拿掉 `"=" in …`:「批四寫在告警帶寫法之後的別的子段」變紅。
     - 拿掉 `ms[0].start() < i`:「批四寫在行為測試那段」變紅。
   - 三個條件各自都有改壞例,沒有照綠的缺口。

沒有找到 major 以上的問題,因此沒有 blocking。

清理:我自己的暫存都已刪掉,包括三個 `gctl-run-*` 現場和我的 repo 副本。

最高等級 clean;blocking 0 條
