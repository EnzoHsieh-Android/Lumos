---
type: issue
status: open
created: 2026-11-01
updated: 2026-11-01
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
  - scope/stack-knowledge
summary: |-
  FLAG:TECHNICAL
  PITFALL:新加的文件守衛測試只驗結構與關鍵詞,節內指路字樣、來源日期、引用語氣改壞照綠 [出處:2026-11-01 代碼審 code-Kotlin慣例對齊與Android單元測試驗收 r3] [根因:守衛測試只釘結構不釘每一句] [repro:把測試品質標準 Android 單元測試節指名 Room 的兩處改回「上一節」,t_test_quality_standard_android_unit_section 照綠]
related:
  - "[[Projects/Kotlin慣例對齊Android官方與本機detekt_計劃]]"
  - "[[Projects/Android本機單元測試驗收標準_計劃]]"
---
# Android驗收標準與Kotlin慣例第三輪留下的小問題

> 白話:Kotlin 慣例對齊與 Android 單元測試驗收標準那一批,代碼審第三輪(standard 的最後一輪)找到五條 minor。改了就沒有下一輪可以審,所以那一輪附理由放行、延後到這篇,推上主線之後另一批修。

## 症狀

1. 測試品質標準〈Android 本機單元測試的驗收標準〉一節裡,指名〈Android 資料層(Room)〉節的兩處沒有測試守著:改回「上一節」(上一節其實是原生收證)時,守衛測試照綠(審查席實測 10 passed)。
2. 同一節的來源清單,Hilt 測試、Gradle 測試篩選、程式碼涵蓋率三個連結沒寫核對日期,其餘十個都有;節首卻寫「各頁當天的更新日期列在最後」。
3. 同一節 Turbine 那條寫「不要用 `runCurrent()` 去推 Turbine」,Turbine README 原文是「不必再用」(you might never need `runCurrent()` again),語氣比出處重。
4. Kotlin 慣例對齊那份計劃的做法 3 說 R21 會寫「用開發者選項『不保留活動』測」,實際交付的 R21 沒有這句(那個選項只模擬畫面被銷毀,不是程序被殺,刻意沒寫),計劃沒跟著改。
5. 洩漏審查題多問了 ViewModel 收 Context 或繼承 `AndroidViewModel`,效能檢核目錄「記憶體洩漏(Context 持有)」那一列沒同步(題目與目錄要雙向同步)。
6. detekt 設定範例那支測試的暫存目錄前綴是 `lumos-kt-idioms-detekt-`,同檔慣例是 `gctl-` 開頭(runner 的暫存隔離與殘骸辨識認這個前綴)。

## 根因

新加的文件守衛測試只釘結構(節位置、三段順序、關鍵詞),沒有釘每一句;修補時列出處清單也只列了程式與條款,沒列到效能檢核目錄的另一列、計劃筆記的做法段。第 6 條是寫測試時沒照同檔慣例取前綴。

## 現在怎麼繞

讀那一節時以官方連結原文為準;讀計劃筆記時以手冊實際內容為準。暫存目錄前綴不影響結果:runner 本來就把 TMPDIR 隔離在 `gctl-run-` 底下,測試的 finally 也會刪。

## 什麼條件算修好

六條都改好,而且第 1、2 條各有一條斷言守著(改回「上一節」、拿掉任一個官方連結的日期都會紅);那一批的代碼審過了、推上主線。
