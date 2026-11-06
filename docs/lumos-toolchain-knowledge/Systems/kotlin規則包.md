---
type: system
status: doing
created: 2026-11-05
updated: 2026-11-06
responsibility: 負責 Kotlin/Android 寫法的 ast-grep 規則包(規則、樣本、自我檢查)與型錄 checks-catalog.md 的格式;不負責新增告警閘本身的判定(那在 pitfalls-code-loop)、不負責 detekt 共用設定
aliases: []
about_code:
  - configs/ast-grep/kotlin-android/check.py
  - configs/ast-grep/kotlin-android/sgconfig.yml
  - configs/ast-grep/kotlin-android/sgconfig-hints.yml
  - skills/kotlin-idioms/checks-catalog.md
  - configs/ast-grep/kotlin-android/sgconfig-review.yml
tags:
  - type/system
  - status/doing
  - scope/stack-knowledge
summary: |-
  WHY:標準寫法的單一來源是型錄 checks-catalog.md,每列要有真的打開讀過的官方出處;查不到的列標(出處不全),引用它的規則只准提示級 [出處:2026-11-05 使用者「你的標準、最佳寫法來源要有依據,不要你自己寫」] [因:AI 自己寫的標準寫法會跟官方現況打架(查證時 18 列與官方衝突、DataStore 加密整組已棄用)] [test:t_kotlin_catalog_rows_wired]
  WHY:規則訊息格式「[型錄編號] 錯在哪;改用 <最短修法>」且不超過 120 字,完整寫法用編號查型錄 [出處:[[Projects/Android協程與API寫法機械檢查標準_計劃]] 設計審 r1] [因:新增告警閘解析 SARIF 截 120 字、擋下訊息也印 120 字] [test:t_kotlin_rulepack_messages_cite_catalog]
  PITFALL:只掃測試碼的規則若寫 `**/test/**`,祖先目錄叫 test 時整個反轉;還有測試變體目錄 `src/testDemo` 會被當正式碼 [出處:2026-11-05 設計審 r2 實測、nowinandroid 實測] [根因:ast-grep 的 files/ignores 相對規則設定檔所在目錄、比對完整路徑] [修法:錨在 `**/src/test*/**`、`**/src/androidTest*/**`] [test:t_kotlin_rulepack_samples]
  PITFALL:ast-grep 規則把 follows 與 not.has $A 平行寫在同一層時,$A 還沒綁定就被比對,規則對任何程式都不命中 [出處:2026-11-05 樣本實測 kt-sequential-independent-await 0 命中] [根因:ast-grep 不保證同層條件的執行順序] [修法:用 all 排順序] [test:t_kotlin_rulepack_samples]
  RULE:規則在真專案誤報超過命中的一成就降提示級或改形狀 [依據:外部] [since:2026-11-05] [retire:人裁] [until:2027-05-05] [confirmed:2026-11-05] [查:Google Tricorder「沒用的告警壓在一成以下」]
  REVISIT:2027-02-05 拿兩個以上新的真 Android 專案再量一次會擋的規則(2026-11-05 只量實驗專案與 nowinandroid 共 30 處命中,多數規則只命中 1–3 處,估不準每條的誤報率)
  SEE:[[Systems/linter精選目錄]] [[Systems/pitfalls-code-loop]]
  PITFALL:規則包測試用 rglob 的第一個檔去改壞,在 Linux 上可能挑到剛放進去的 review-fp 樣本、把它蓋掉,兩條改壞驗證跟著失效(macOS 綠、CI 紅) [出處:2026-11-05 PR #158 合併後主線 CI] [根因:目錄列舉順序依檔案系統而定,APFS 恰好照名稱排、ext4 不是] [修法:照檔名挑或整個目錄都改,不用 next(rglob)] [test:t_kotlin_rulepack_samples]
  WHY:型錄〈情境決策表〉加「證據樣式」欄(主與例外兩段,各是(無)或一到三條正規式,照那一列標準寫法與不適用時的字面特徵推,不另立寫法);格式檢查改依表頭名稱取欄,另驗證據樣式能編譯、條數對、停用列的觸發字與證據樣式都是(無),列編號連號照舊 [出處:2026-11-06 [[Projects/Android寫法語意情境表態與盲判_計劃]] 範圍 1] [因:推送前情境題要拿樣式核表態指的那一行] [test:t_kt_catalog_evidence_patterns]
  WHY:決策表的讀法只有 check.py 的 dt_table/dt_row 一套(依表頭取欄、停用列不讀觸發字與證據樣式、標了換列的列例外一定要是(無)),scripts/lumos 用 importlib 借用;換列的列認「不適用時」格子裡出現的(換列)標記(格子任何位置都算),不從「見下一列」這類中文用語推 [出處:代碼審 code-android情境題與表態對程式 r1 D7、D10] [因:原本 lumos 與 check.py 各寫一套讀表、必有欄已經分歧(6 欄對 8 欄),換列靠中文字樣推、改個說法就悄悄變成可選例外] [test:t_kt_situation_catalog_single_reader]
  WHY:每列證據樣式附正例與反例(samples/situation/<列編號>.kt.txt,副檔名不是 .kt 免得推送閘把教材當產品碼),自檢經 scripts/lumos 真的切段與核對程式跑:正例要有一行對得上、反例要每一行都對不上(推送前對不上只提醒,自測守的是樣式本身沒壞,代碼審 r2)、樣本要切得出含那一列的段,反例要碰得到樣式真正在管的地方(順序、型別參數,r2 邊界 F12);壞寫法跟標準寫法只差在語意時那一段寫(無)交盲判 [出處:代碼審 r1 D1;ast-grep test 的 valid/invalid https://ast-grep.github.io/guide/test-rule.html ;Semgrep 的 ok/ruleid https://docs.semgrep.dev/writing-rules/testing-rules ] [因:人逐列寫的樣式在 56 列裡有 9 列擋掉型錄自己的標準寫法或放過對應的壞寫法] [不選:靠人逐列看] [test:t_kt_situation_evidence_samples]
  WHY:自檢程式的 dt_table 讀表那一輪順手帶出處(每列多 source 來源格、refs 展開後的網址、check_refs 對應檢查在型錄主表的名稱與來源與網址,縮寫照〈來源縮寫〉表展開;縮寫表讀法 _abbr_table 與比對 _abbr_hit 跟 catalog_problems 共用一套;縮寫表那兩支檔內輔助用底線開頭(代碼審 code-android情境題盲判 r2 戊);情境證據樣本的 situation_dir、situation_samples、load_lumos 沒加底線),lumos 從列上取出處給盲判材料;主表或縮寫表找不到時那幾格留空不報錯(讀得懂讀不懂歸 dt_table 與 catalog_problems) [出處:2026-11-06 [[Projects/Android寫法語意情境表態與盲判_計劃]] 範圍 4;使用者 2026-11-05 第 3 要點(來源與依據在語意盲判時輔助判別)] [因:讀表只留一套,出處也從同一輪讀(代碼審 code-android情境題盲判 r1 架構對齊 F6:原本另有 dt_sources 再走一輪決策表、縮寫比對的正規式寫了三處)] [不選:lumos 自己再寫一套讀主表;另一支 dt_sources 再走一輪] [test:t_kt_catalog_sources_in_rows] [test:t_blind_judge_template_excludes_dispositions] [test:t_kt_catalog_private_helpers]
  WHY:型錄第四批通電批次照固定口徑判(切段、認規則碼、排除待查、預設關、相近、opt-in 與官方預設關的六條),由型錄自檢 check.py 的 batch4_expected_tags 逐列重算比對(代碼審 r1 架構席:口徑只住一處) [出處:2026-11-06 Projects/Android現成檢查接上CI與推送前_計劃 設計審 r1] [因:兩席指出 compose-rules 預設關的三條會被標成已接電,實際沒在跑] [不選:一次性腳本改完就算(沒有守衛,下次改型錄就漂)] [test:t_kt_catalog_batch4_wiring]
verified_by:
  - "[[Verification/2026-11-05_Kotlin規則包真專案實測]]"
---
# kotlin規則包

> 白話:Kotlin/Android 寫法的機械檢查規則包(ast-grep)與它的單一來源型錄。型錄每一列寫一種常見錯誤寫法、官方的標準寫法、出處網址、機器怎麼查、在哪一批接上自動檢查;規則包把能用語法結構比對的列寫成規則,推送前的新增告警閘只擋這次新增的告警,訊息帶型錄編號與最短修法。

## 檔案

- `configs/ast-grep/kotlin-android/sgconfig.yml`:會擋的規則(`rules/` 底下,error 與 warning)。消費專案照 [[Systems/linter精選目錄]] 的範本宣告這一份。
- `configs/ast-grep/kotlin-android/sgconfig-review.yml`:語意覆核級規則(`rules-review/`,ast-grep 的 info 等級):形狀抓得到可疑寫法、但要知道型別或語意才分得出對錯的規則(例:Firebase 的 `setValue` 跟 LiveData 同名)。不擋、也不降成提示級;每個新增命中之後要由盲判代理逐筆判,接法在 [[Projects/規則包語意覆核級命中走盲判_計劃]],接上前範本不接。好例樣本裡檔名開頭 `review-fp-` 的,是這級規則已知會誤報、要靠盲判排除的寫法,自我檢查不算好例誤報。
- `configs/ast-grep/kotlin-android/sgconfig-hints.yml`:提示級規則(`rules-hints/`),誤報可能較高或依據的型錄列出處不全,範本預設不接。
- `rules/`、`rules-review/`、`rules-hints/` 底下的 yml 依型錄主題分檔;每條規則 `samples/bad/<id>/`、`samples/good/<id>/` 各有樣本(只掃測試碼的規則放 `src/test/` 底下)。樣本故意埋壞寫法,風險分級、棧別題、新增告警閘(含測試防竄改比對)、Room 守衛與每支檔有家都不把它們當產品碼(`_RULEPACK_SAMPLE_RE`、`.lumos/config.json` 的 `node_home.ignore`)。
- `configs/ast-grep/kotlin-android/check.py`:自我檢查(零依賴),`python3 check.py --sg <ast-grep>` 驗:每條規則壞例至少命中兩處、好例零命中且至少兩段、載入條數等於 id 數、只掃測試碼的規則對「祖先目錄叫 test 的正式碼」不命中、訊息格式;`--catalog-only` 驗型錄,另跑情境題證據樣式的正反例自測(situation_sample_problems)。
- `skills/kotlin-idioms/checks-catalog.md`:型錄。欄位與規則見它開頭的〈輸入與口徑〉;〈情境決策表〉是語意類情境的「看到這個 → 預設這樣寫 → 什麼時候例外」,列編號 D-n 只准往後加;〈待查證〉節不受檢查。

自我檢查程式是零依賴的獨立檔,YAML 規則檔與型錄表格用自己的行級讀法(只有情境題證據樣式自測用 load_lumos 把旁邊的 scripts/lumos 當模組載入,借它的比對函式;載不到就把原因當問題報出):規則檔統一寫成單行 `message:`、`id:` 不加引號,寫成別種形式會被報錯(不會漏報)。樣本目錄排除只認 `configs/ast-grep/<包>/samples/` 底下的 `.kt/.kts`(風險分級、測試防竄改比對、Room 守衛共用的 `_RULEPACK_SAMPLE_RE` 與每支檔有家的 `node_home.ignore` 兩處同一個範圍);消費專案若剛好有同形路徑的正式碼也會被排除,這是接受的取捨。

## 怎麼改

1. 改規則或加規則:同時補樣本,跑 `python3 configs/ast-grep/kotlin-android/check.py --sg <ast-grep>` 到 0 個問題。新規則一律先放語意覆核級(`rules-review/`),對真專案量過誤報低於一成才升到會擋的 `rules/`;審查中被點出形狀分不出對錯的,不再放寬形狀,直接留在覆核級(代碼審跑滿回顧,卷證 `governance/review-reports/code-kotlin規則包/cap-retro.json`:三輪的最大宗都是放寬形狀又帶出新誤報)。
2. 改型錄:跑 `--catalog-only`(連證據樣式自測一起跑,會載入旁邊的 scripts/lumos;改了某列的證據樣式就同時改 `samples/situation/<列編號>.kt.txt` 的正反例,到 0 個問題);新寫的標準寫法一定附真的打開讀過的官方網址,查不到就在名稱標「(出處不全)」。
3. 決策表觸發字不准收常用字(停用字表在 check.py 的 `STOP_TRIGGERS`);第二批改檔前推列與第三批情境題靠它不吵。情境沒有不常見的字面特徵時觸發字寫「(無)」(全形半形括號都認),`dt_triggers` 解析成空清單、不出情境段;「(無)」跟別的觸發字並列、或格子空白,自我檢查都會報。第二、三批讀觸發字要走 `dt_triggers`,不要自己拆格子,不然「(無)」會被當成一個字去比對。
4. 有消費專案或範例專案時,拿會擋的規則對整份原始碼跑一次,逐條判真假;誤報超過一成照上面那條規則處理,結果寫回型錄的「實測狀態」欄。

## 2026-11-05 真專案實測

實驗專案(13 支 kt 檔)與 Google 官方範例 nowinandroid(310 支 kt 檔)整份掃:修前命中 30 處、誤報 13 處(nowinandroid 誤報率 55%);誤報集中在測試變體目錄(`src/testDemo`)、Compose 預覽與截圖測試、分不出查詢與指令。照實測改形狀 6 條、降提示級 3 條後重掃:實驗專案 8 處(7 真、1 判不準)、nowinandroid 9 處全真。逐條紀錄在型錄「實測狀態」欄,驗證紀錄見 [[Verification/2026-11-05_Kotlin規則包真專案實測]]。
