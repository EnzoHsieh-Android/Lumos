severity: major

我只讀了被審材料與對照檔,沒有改 repo。

## ① 模組邊界

F1
severity: minor
blocking: 否
引句:「`skills/kotlin-idioms/test-templates.md`(新增)。Markdown,一組一節」
範本檔放 `skills/kotlin-idioms/` 大致對得上,但計劃對照的是錯的鄰居。計劃自述照 DDD 與前端兩份照抄式範本的放法,那兩份其實放在 `skills/lumos-project-notes/commands/target-arch-ddd-template.md:1`,不在技能目錄。
- 真正的先例是同目錄的 `checks-catalog.md`:它是 `check.py` 讀取的資料檔,位置由 `configs/ast-grep/kotlin-android/check.py:20` 的 `CATALOG` 寫死。範本檔同樣是 `check.py` 要讀的資料檔,放 `skills/kotlin-idioms/` 站得住。
- 但「照抄式範本放 `commands/`」與「`check.py` 讀的資料放 `kotlin-idioms/`」是兩種放法。計劃只引前者當先例,卻放在後者的位置。
- 建議計劃改引 `checks-catalog.md` 當放置依據。這是理由寫錯,不是結構錯,不擋。

F2
severity: major
blocking: 是
引句:「`configs/ast-grep/kotlin-android/check.py` 加 `--lab <空資料夾>` 入口與一支函式」
`--lab` 放進 `check.py` 有邊界問題。
- `check.py` 的職責是唯讀自檢,檔頭用法只有 `--sg`、`--json`(`check.py:9`),`main` 裡只有 `--catalog-only`、`--sg`、`--json`(`check.py:368-395`)。
- `--lab` 會讓它第一次寫檔、第一次產出別的專案結構。計劃自己也說不新增 lumos 子命令,等於承認這不是檢查。
- repo 裡已有「讀資料檔、組出 Gradle/Kotlin 產物」的產生器:`scripts/lumos` 的 `cmd_arch_template`(`scripts/lumos:61552`)。
- 抽出實驗專案的對象是範本檔,不是型錄。我判這是同一職責的第二個住處,只是這次是 Markdown 當單一來源、輸出到資料夾。
- 拆開的做法:`check.py` 只留 `template_problems`,抽出器另放,或明寫為什麼要與自檢共用同一支解析器。
- 這點與③的 F6 同根。

F3
severity: minor
blocking: 否
引句:「`scripts/templates/android-arch-target.md` 某一支 `test` 塊裡的 `// 型錄:` 註解」
K 測試進產生器資料檔是對的。K1–K3 是 `=== test *` 塊,本來就是 `scripts/templates/android-arch-target.md:149` 起那類塊的延伸。但有兩個連帶問題。
- `template_problems` 要在 `check.py` 裡認領 `// 型錄:`,就得自己解析 `scripts/templates/android-arch-target.md`。
- 這個資料檔的解析器是 `scripts/lumos:61338` 的 `_ARCH_TPL_BLOCK_RE` 與 `_arch_tpl_blocks`。`check.py` 是獨立的零依賴小檔,不能 import `scripts/lumos`。
- 結果是同一種塊格式有兩份解析程式。計劃沒交代兩邊怎麼不漂移,見②的 F5。

## ② 既有做法

F4
severity: major
blocking: 是
引句:「塊頭改用圍欄的資訊字串而不是 `===` 行,因為範本是給人與 AI 讀的文件」
計劃自己承認要換一種區塊標頭。
- 既有格式是產生器資料檔的 `=== <種類> <條件> [convention]`,由 `scripts/lumos:61338` 解析。檔頭註解寫「格式:每塊從一行 `===` 開始」(`scripts/templates/android-arch-target.md:3`)。
- 新格式是 `kotlin T1 template` 這種圍欄資訊字串。我 grep 了 `skills/` 與 `scripts/templates/`,沒有任何現有 Markdown 用資訊字串當區塊標頭。DDD 範本的圍欄只標語言(`target-arch-ddd-template.md:12,32`)。
- 這是引入第二種區塊格式,正好撞你們的嚴重度錨「第二種做法」。「給人讀」的理由只說明為什麼不想用 `===`,沒說明為什麼不能用既有格式。
- `=== test`、`=== code` 就是在 Markdown 裡放 Kotlin 片段的既有做法。
- 若堅持圍欄資訊字串,至少要在計劃裡寫成有依據的取捨,並明寫兩種格式各自的解析器歸誰、怎麼防漂移。

F5
severity: minor
blocking: 否
引句:「`template_problems()`(在同一支 `check.py`,掛在 `catalog_problems` 同一條路徑」
型錄自檢新增一項,報錯形狀要與既有一致,計劃沒有寫死。
- 既有 `catalog_problems(rules=None)`(`check.py:129`)回傳 `(id, why)` 二元組,id 是型錄編號,或 `<catalog>`、`<pack>` 這種尖括號佔位(`check.py:142,203,306`)。
- 計劃的預期值表寫「報 API-1 沒人認領」「報 T4 缺 bad 圍欄」,但沒寫新函式回 `(id, why)`,也沒說節代號 `T4` 放在 id 欄還是 why 欄。
- 「掛在同一條路徑」也含糊:`catalog_problems` 是被 `--catalog-only`(`check.py:370`)直接呼叫,不是 `check()` 內的步驟。
- 另外,既有測試靠 `_ktpack(copy=True)`(`scripts/test_lumos.py:125451`)只複製規則包與型錄(`_KTPACK_REL`、`_KTCAT_REL`)。
- `template_problems` 要讀範本檔與 `scripts/templates/android-arch-target.md`,測試替身目前複製不到這兩支。S1、S2 要「改壞一份看自檢抓不抓得到」,必須擴充 `_ktpack`。計劃的做法節沒列這項。

## ③ 第二種做法

F6
severity: major
blocking: 是
引句:「範本與型錄的對應由既有的型錄自我檢查 `configs/ast-grep/kotlin-android/check.py` 多驗一項,不另開檢查程式」
正向、反向、形狀三項核對,repo 內已有可借的同類機制,計劃沒對照。
- 既有機制一:`catalog_problems` 的「決策表對應檢查要在型錄主表」(`check.py:194`)、「語意類要被決策表收進去」(`check.py:201`)。這是雙向對應核對,形狀與計劃的「`涵蓋:` ↔ 型錄編號」相同。
- 既有機制二:`scripts/lumos` 對 `test` 塊與 RULE 行的 `[test:]` 綁定、`_ARCH_TPL_TEST_FUN_RE`(`scripts/lumos:61339`)。「RULE 行綁測試名、測試名要在塊裡找得到」與計劃的「矩陣點名的測試名要在圍欄裡找得到 `fun <名>(`」是同一件事。
- 計劃的 PRIOR-ART 第③點只說「用型錄自檢」,沒說明為何不沿用 `[test:]` 綁定這套已有的綁定語意,另造 `涵蓋:` 與 `// 型錄:` 兩種新認領語法。
- 實驗專案抽出同樣沒對照。`cmd_arch_template` 已是「資料檔 → 產物」的路徑(F2)。
- 我判新增 `涵蓋:` 與 `// 型錄:` 兩種認領語法,加上 F4 的圍欄標頭,等於一個功能引入三種新語法,而 repo 已有對應機制。
- 判不準的 ⚠:`涵蓋:` 是範本檔專用,而 `// 型錄:` 與 `[test:]` 的分工是否刻意,請編排者向計劃作者確認。

F7
severity: minor
blocking: 否
引句:「`MainDispatcherRule` 照 nowinandroid `core/testing` 同名類別」
這條不算第二種做法,算對得上。借用外部官方範本並明寫來源,與既有的「依據」欄和型錄出處規則(`check.py:171,173`)一致。

不對齊共 7 條,其中會擋的 3 條。
