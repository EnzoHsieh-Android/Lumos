---
type: system
status: doing
created: 2026-11-05
updated: 2026-11-05
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
verified_by:
  - "[[Verification/2026-11-05_Kotlin規則包真專案實測]]"
---
# kotlin規則包

> 白話:Kotlin/Android 寫法的機械檢查規則包(ast-grep)與它的單一來源型錄。型錄每一列寫一種常見錯誤寫法、官方的標準寫法、出處網址、機器怎麼查、在哪一批接上自動檢查;規則包把能用語法結構比對的列寫成規則,推送前的新增告警閘只擋這次新增的告警,訊息帶型錄編號與最短修法。

## 檔案

- `configs/ast-grep/kotlin-android/sgconfig.yml`:會擋的規則(`rules/` 底下,error 與 warning)。消費專案照 [[Systems/linter精選目錄]] 的範本宣告這一份。
- `configs/ast-grep/kotlin-android/sgconfig-review.yml`:語意覆核級規則(`rules-review/`,ast-grep 的 info 等級):形狀抓得到可疑寫法、但要知道型別或語意才分得出對錯的規則(例:Firebase 的 `setValue` 跟 LiveData 同名)。不擋、也不降成提示級;每個新增命中之後要由盲判代理逐筆判,接法在 [[Projects/規則包語意覆核級命中走盲判_計劃]],接上前範本不接。好例樣本裡檔名開頭 `review-fp-` 的,是這級規則已知會誤報、要靠盲判排除的寫法,自我檢查不算好例誤報。
- `configs/ast-grep/kotlin-android/sgconfig-hints.yml`:提示級規則(`rules-hints/`),誤報可能較高或依據的型錄列出處不全,範本預設不接。
- `rules/`、`rules-review/`、`rules-hints/` 底下的 yml 依型錄主題分檔;每條規則 `samples/bad/<id>/`、`samples/good/<id>/` 各有樣本(只掃測試碼的規則放 `src/test/` 底下)。樣本故意埋壞寫法,風險分級、棧別題與每支檔有家都不把它們當產品碼(`_RULEPACK_SAMPLE_RE`、`.lumos/config.json` 的 `node_home.ignore`)。
- `configs/ast-grep/kotlin-android/check.py`:自我檢查(零依賴),`python3 check.py --sg <ast-grep>` 驗:每條規則壞例至少命中兩處、好例零命中且至少兩段、載入條數等於 id 數、只掃測試碼的規則對「祖先目錄叫 test 的正式碼」不命中、訊息格式;`--catalog-only` 只驗型錄。
- `skills/kotlin-idioms/checks-catalog.md`:型錄。欄位與規則見它開頭的〈輸入與口徑〉;〈情境決策表〉是語意類情境的「看到這個 → 預設這樣寫 → 什麼時候例外」,列編號 D-n 只准往後加;〈待查證〉節不受檢查。

自我檢查程式是零依賴的獨立檔,不 import 單檔主程式,所以 YAML 規則檔與型錄表格用自己的行級讀法:規則檔統一寫成單行 `message:`、`id:` 不加引號,寫成別種形式會被報錯(不會漏報)。樣本目錄排除只認 `configs/ast-grep/<包>/samples/` 底下的 `.kt/.kts`(風險分級那邊的 `_RULEPACK_SAMPLE_RE` 與每支檔有家的 `node_home.ignore` 兩處同一個範圍);消費專案若剛好有同形路徑的正式碼也會被排除,這是接受的取捨。

## 怎麼改

1. 改規則或加規則:同時補樣本,跑 `python3 configs/ast-grep/kotlin-android/check.py --sg <ast-grep>` 到 0 個問題。
2. 改型錄:跑 `--catalog-only`;新寫的標準寫法一定附真的打開讀過的官方網址,查不到就在名稱標「(出處不全)」。
3. 決策表觸發字不准收常用字(停用字表在 check.py 的 `STOP_TRIGGERS`);第二批改檔前推列與第三批情境題靠它不吵。
4. 有消費專案或範例專案時,拿會擋的規則對整份原始碼跑一次,逐條判真假;誤報超過一成照上面那條規則處理,結果寫回型錄的「實測狀態」欄。

## 2026-11-05 真專案實測

實驗專案(13 支 kt 檔)與 Google 官方範例 nowinandroid(310 支 kt 檔)整份掃:修前命中 30 處、誤報 13 處(nowinandroid 誤報率 55%);誤報集中在測試變體目錄(`src/testDemo`)、Compose 預覽與截圖測試、分不出查詢與指令。照實測改形狀 6 條、降提示級 3 條後重掃:實驗專案 8 處(7 真、1 判不準)、nowinandroid 9 處全真。逐條紀錄在型錄「實測狀態」欄,驗證紀錄見 [[Verification/2026-11-05_Kotlin規則包真專案實測]]。
