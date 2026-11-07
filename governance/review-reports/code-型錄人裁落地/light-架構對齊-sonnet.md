severity: minor

審查對象是 light-snapshot.patch。我讀了整份 patch,對照既有的 `rules-unwired/` 規則、型錄列和 `check.py`,並跑了 `-k kotlin_rulepack`(111 過)與 `-k kt_catalog`(48 過)。`check.py --catalog-only` 的輸出是「型錄問題 0 個、還沒逐列查證 0 列」。我另外用程式重數,規則包條數 211、其中 `rules-unwired/` 14 條,跟型錄〈統計〉一致。主表沒有查證紀錄的非 D 列剛好 13 列,也跟「13 列都已標出處不全」對得上。

## 問 1:分層與依賴方向

搬過去的規則、樣本、型錄列寫法,跟既有那批一致,沒有跨層問題。

- **規則本體**:`kt-async-await-immediately` 逐字搬進 `rules-unwired/api.yml` 檔尾,`kt-compose-test-node-by-index` 和 `kt-compose-test-node-by-literal-text` 搬進 `rules-unwired/testing.yml` 檔尾。`id`、`message`、`files`、`rule` 內容沒改,連 `# T33(索引)` 這種前綴註解都保留,跟同檔既有的 `# T35`、`# T14` 寫法一樣(`configs/ast-grep/kotlin-android/rules-unwired/testing.yml:1`、`:25`)。
- **來源檔清乾淨**:`rules/`、`rules-hints/` 兩邊都已刪乾淨。
- **樣本不用搬**:樣本按規則 id 命名(`samples/bad/kt-async-await-immediately`、`samples/good/kt-compose-test-node-by-index` 等),不按規則所在目錄分。所以搬規則不會漏樣本。`t_kotlin_rulepack_samples` 跑過 27 秒,樣本都仍被命中或放行。
- **目錄與等級規則**:`check.py` 的 `rules-unwired` 收任何等級(`configs/ast-grep/kotlin-android/check.py:29`)。引用出處不全列的規則必須在 `rules-unwired/`(`check.py:401`)。搬完後 `t_kotlin_rulepack_unwired_dir` ⑥⑦ 都過,符合這兩條。
- **型錄列**:API-14、TEST-31 的通電批次寫成「告警帶寫法=未接(規則在 rules-unwired/:型錄這列出處不全)」,跟既有 12 列(例如 `skills/kotlin-idioms/checks-catalog.md:639` TEST-16、`:656` TEST-33、`:165` 同批)逐字一樣。

## 問 2:命名與錯誤處理

大部分一致,有兩處小出入。

- **一致的部分**:名稱尾巴「(出處不全)」的位置,和 `checks-catalog.md:187`(API-36)、`:639` 一樣。「規則 … :樣本實測中壞例、好例不報」這一欄沒動。
- **一致的部分(續)**:API-14、TEST-31 沒有〔查證〕紀錄,和 TEST-16(`:639`)、API-36(`:187`)同型,所以「出處不全」列可以沒有查證紀錄。
- **統計數字**:都跟程式算的對得上。35 列出處不全、501 列有查證、13 列沒有。「人裁的列:3」沒動是對的,因為 DATA-12 本來就不帶(人裁)標。

**finding 1:DATA-12 的〔查證〕紀錄格式是新的**

severity: minor
blocking: 否

既有〔查證 日期:網址…〕裡只放日期與網址。這一列在括號內塞了英文原文和「使用者裁」的過程紀錄。我用正規式掃過,整本型錄只有這一處這樣寫。這格式不會被 `catalog_problems` 擋(已跑),但來源欄會被其他機械讀取,而且過程紀錄本來該放在計劃筆記或 git。
引句:「2026-11-08 使用者裁改成取捨提醒〕」
既有對照 `skills/kotlin-idioms/checks-catalog.md:398`(只有網址的〔查證 2026-11-07:https://raw.githubusercontent.com/square/okhttp/master/okhttp/src/commonJvmAndroid/kotlin/okhttp3/OkHttpClient.kt〕);改法是只留網址,原文引句放計劃筆記。

**finding 2:DATA-12 的「情境」欄還是舊語意**

severity: minor
blocking: 否

這一列的名稱、標準寫法、後果都改成「transform 跑太久、後面的寫入排隊」。但「情境」欄仍寫「要看 transform 內呼叫的是不是副作用」,指的是舊版「做副作用」的判法。照字面讀,取捨提醒的判斷依據跟這格對不上。
引句:「語意:要看 transform 內呼叫的是不是副作用」
既有對照 `skills/kotlin-idioms/checks-catalog.md:639`(TEST-16 的情境欄寫的就是該列名稱所說的事);改法是把這欄改成「要看 transform 內做的事會不會很久」。

## 問 3:第二種做法

沒有引入新做法。沿用 2026-11-08 早先拆規則進 `rules-unwired/` 的同一套流程:型錄標出處不全、規則放 `rules-unwired/`、通電批次寫未接、`check.py` 的目錄檢查把關。DATA-12 沒掛規則,只改型錄文字,也沒新機制。

**finding 3:計劃筆記的「守衛面」排除項現在不成立**

severity: minor
blocking: 否

`Android寫法型錄逐列查證_計劃.md` 的實務隱患節,有一行沒被這次 diff 改到:這一批不改任何擋停,要降級的兩條拆到〈待人裁〉。但這次提交正是讓三條原本會擋或提示的規則不再接閘。計劃的〈待人裁〉節已記了代價(消費專案推送前不再擋這兩種寫法),但這行排除項沒同步。
引句:「已排除:守衛面:這一批不改任何擋停——規則包等級沒動」
既有對照 `skills/kotlin-idioms/checks-catalog.md:11`(通電批次欄值說明已寫「未接」的列不擋);改法是把這行改成「守衛面:API-14、TEST-31 兩列的三條規則 2026-11-08 起不接閘,見〈待人裁〉」。

不對齊共 3 條,其中 major 0 條。
