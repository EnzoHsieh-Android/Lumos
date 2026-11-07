---
type: issue
status: open
created: 2026-11-07
updated: 2026-11-07
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
summary: |-
  FLAG:TECHNICAL
  PITFALL:範本 T12 建清單的 Gradle 片段在 archunitFreezeInit 條件區塊外多寫一份常駐 true 的 systemProperty,資料測試照綠 [出處:2026-11-07 代碼審 code-android儀器測試範本 r3 通才席 F1] [根因:_kt_instr_template_problems 只查兩行在不在條件區塊內,沒查區塊外的出現次數] [test:t_kotlin_test_templates_content_guards]
  REVISIT:2026-11-21 補區塊外出現次數為 0 的檢查與改壞案例,順手把驗證紀錄〈做法〉例外條那句 T12 建清單基準改成跟範本矩陣前導句一致,修完改 status 為 done
---
# T12凍結設定守衛沒擋區塊外多一份常駐true

## 症狀

範本 `skills/kotlin-idioms/test-templates.md` T12〈依賴〉建凍結清單那段 `build.gradle.kts`,兩行 `systemProperty("archunit.freeze.store.default.allowStoreCreation", "true")`、`systemProperty("archunit.freeze.store.default.allowStoreUpdate", "true")` 應該只在 `if (project.hasProperty("archunitFreezeInit"))` 區塊裡。代碼審 r3 通才席在複本把同樣兩行無條件地多寫一份在區塊外(條件區塊照留),`python3.14 scripts/test_lumos.py -k kotlin_test_templates_content_guards` 仍 210 passed。範本若真的被改成這樣,照抄的人兩個屬性常駐 true,`allowStoreUpdate=false` 擋新規則被靜默凍結的防護整組失效,守衛卻是綠的。

另一處同類:驗證紀錄 `Verification/2026-11-06_Android儀器測試範本與架構測試實跑` 的〈做法〉例外條仍寫 T12 每格先用〈好寫法〉建凍結清單,跟範本矩陣前導句「前七格零違規、最後四格〈好寫法〉加 TagRepository 一筆舊違規」對不上(同輪通才席 F2)。格數守衛只比數字,抓不到這句。

## 根因

資料測試 `_kt_instr_template_problems` 對這兩行只檢查「有出現在條件區塊裡」,沒檢查「區塊外出現 0 次」;代碼審 r2 修補時只想到「搬走」與「條件改成永遠成立」兩種改壞,沒想到「另外複製一份在外面」。驗證紀錄那句是 r2 修補只改了範本矩陣前導句與〈做法〉重跑那條,同一節例外條沒一起改。

## 現在怎麼繞

範本現在的內容是對的(兩行只在條件區塊裡),只是守衛擋不住這一種回退;改範本 T12 那段時人工確認區塊外沒有這兩行。讀驗證紀錄時以範本矩陣前導句與 E13 為準。

## 什麼條件算修好

`_kt_instr_template_problems` 在兩行出現在條件區塊外時報錯,並有一支改壞案例(區塊外多一份、條件區塊照留)會紅;驗證紀錄〈做法〉例外條改成跟範本矩陣前導句一致。兩件做完把這篇 status 改成 done。
