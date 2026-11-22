severity: major

這份計劃的分層、命名、落點都跟第二批一致。它改了 API 列「方法名」錨點的行為,改法和第二批不同,我判 major。

## 1. 分層與依賴方向

大致對齊,但有一處不對齊(見 a1)。

- 規則放 `configs/ast-grep/kotlin-choice/rules-choice/api.yml`,規則 id 等於列號。第二批的 C-34 到 C-37 就是這樣放的:`configs/ast-grep/kotlin-choice/rules-choice/api.yml:1`。
- 樣本另開新檔 `samples/choice-batch3.kt`。第二批也是另開 `samples/choice-batch2.kt`。
- 產壞法的擴充放在 `_choice_anchor`、`_choice_anchor_edits`、`_choice_api_edits`、`_choice_also`,呼叫鏈是 `_choice_pick` → `_choice_edits` → `_choice_anchor_edits` → `_choice_api_edits`。這跟第二批同一條鏈,沒有跨層直呼:`scripts/lumos:77549-77616`。
- check.py 不動。第二批加新類別和新錨點時才改它:`configs/ast-grep/kotlin-android/check.py:1393-1394`。
- 作用域兩列、`replay`、`NonCancellable` 用「運算元起始」錨點,規則命中整數或識別字本身。UOI 的 C-17 已有同一種用法:`skills/kotlin-idioms/checks-catalog.md:1684`。
- 「整個呼叫」用 `pattern: '$A.retry($$$B)'` 命中,不算第二種規則形狀。`nul.yml` 的 C-32 已經用 `pattern: '$A ?: $B'` 加後設變數 `$A`:`configs/ast-grep/kotlin-choice/rules-choice/nul.yml:9`。aor、lcr、ror 也都用 `pattern:`。`api.yml` 目前都是 `kind: navigation_suffix`,但 `pattern:` 加 `$A` 這個機制專案裡早就有。

## 2. 命名與錯誤處理

對齊。

- 規則 id 是 C-38 起的列號,且只在過實測門檻後才給號,同第二批範圍 1。
- 測試命名是 `t_choice_points_batch3_*`、`t_choice_samples_batch3`、`t_choice_table_batch3`、`t_choice_points_batch3_stable`。這跟 `t_choice_points_batch2_api`、`t_choice_samples_batch2`、`t_choice_table_batch2`、`t_choice_points_batch2_stable` 對得上:`scripts/test_lumos.py:146355-146596`。
- 回退章節三條照第二批,規則是撤列時列號寫進 `已撤列號:`。
- 錯誤處理沿用既有做法:產不出壞法就回 None,不丟例外,見 `scripts/lumos:77608`。
- 計劃沒寫「`$A` 存在但範圍不對」時回什麼,只寫了有 `$A` 與沒有 `$A` 兩條路。這點留給實作時補。

## 3. 第二種做法

這題有一條 major,兩個不判。

- 判 major:a1,「方法名」錨點靠命中節點有沒有 `$A` 來分流。
- 不判,留給編排者(⚠):等價排除寫進命中規則(作用域少於兩個子協程、`LAZY` 後立刻 `.await()`、`finally` 裡的 `NonCancellable`、`Result.retry()`)。
  - 〈乾節點規則〉的定位是「命中範圍內不產生壞法、由人照回饋手動增補」:`skills/kotlin-idioms/checks-catalog.md:1708`。
  - 但第二批自己也把等價排除寫進命中規則,例如 `.let` 的 value-pos、`combine` 排除完整套件名、`?.` 排除前面是註解:`configs/ast-grep/kotlin-choice/rules-choice/api.yml:146`。
  - 鄰居本身就這樣做,所以第三批跟鄰居一致,只是跟型錄的文字說明不一致。
- 不判(⚠):`_choice_also` 新增「運算元起始、取 `b[s:e]`、不要求 `op`」的分支。
  - 它跟「方法名」分支共用同一組檔頭掃描和 `_situation_rule_imports_problem`,判定規則一樣,只是入口多一條。
  - 既有的「運算元起始」列 C-17 沒有要補的 import,所以沒有前例可對:`scripts/lumos:77680-77692`。

## 4. 落點合不合理

合理,對齊。

- `Systems/kotlin規則包` 管規則檔和樣本檔,`about_code` 在 `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:36-37` 已列了 `nul.yml` 和 `choice-batch2.kt`。第二批的 WHY 也寫在這篇(第 101 行)。第三批的 WHY 和新樣本檔照寫進去即可,不用另開一篇。
- `Systems/規格閘` 管 choice-points 的程式和 `gov --stats`,`responsibility` 已寫改動選擇點掃描與挑壞法。第二批「依列號」的 WHY 也在這篇(第 80 行)。「整個呼叫命中」的錨點位置說明寫進這篇是對的。

## a1 「方法名」錨點靠命中形狀分流,沒有新增錨點
severity: major
blocking: 是
引句:「命中帶 `$A` 後設變數時(整個呼叫命中),從 `$A` 結尾開始跳過空白與換行再比對」
file: `scripts/lumos:77408`

- **既有做法:** 第二批遇到「同一類換法但命中形狀不同」時,是新增錨點,再用 `row["anchor"]` 分流。「安全呼叫符」和「引數」都是這樣來的:`scripts/lumos:77410-77418`。
- **編輯端也一樣:** `_choice_anchor_edits` 同樣按錨點名稱分支:`scripts/lumos:77582-77605`。
- **這份的做法:** 計劃規定「不加新錨點」,卻讓 retry 兩列仍叫「方法名」,命中的卻是整個呼叫。`_choice_anchor` 和 `_choice_api_edits` 靠 `mv` 裡有沒有 `A` 去走兩套不同的位置與刪法。
  - `drop_call` 這個樣板因此有兩種意思:有 `$A` 時刪「`$A` 結尾到命中結尾」,沒有 `$A` 時刪「`.方法名()`」。
- **後果一:** check.py 的錨點白名單分不出這兩種「方法名」。
- **後果二:** 型錄欄位說明(`skills/kotlin-idioms/checks-catalog.md:1658`)對「方法名」的定義(navigation_suffix 的識別字)跟 retry 兩列不再相符。
- **為什麼算第二種做法:** 專案原本是「錨點名稱決定編法」,現在變成「錨點名稱加隱含的命中形狀」一起決定。
- **對齊的做法:** 新增一個錨點(例如「整個呼叫」),再在 check.py、`_choice_anchor`、`_choice_anchor_edits` 各加一個明確分支,跟安全呼叫符和引數同形。

## a2 文件落點的同步項目比第二批少
severity: minor
blocking: 否
引句:「Systems/kotlin規則包 `about_code` 加 `samples/choice-batch3.kt`,補一條 WHY 行」
file: `docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md:55`

- 第二批範圍 6 還做了兩件事,第三批沒寫。
  - 改 `Projects/改動選擇點都要有需求守住_計劃` 〈天花板〉第 1 條,加指向新批次的連結。目前那條只指到第二批(第 326 行)。
  - 更新 `Systems/kotlin規則包` 裡逐檔列規則和樣本的那段(第 150、153 行)。
- 這兩處不補,第三批上線後母計劃天花板會只提第二批,規則包的樣本清單會缺第三批樣本。結構是對的,只是同步項目漏了。

不對齊共 2 條,其中 major 1 條

臨時目錄:我沒建任何臨時檔,不需清理。
