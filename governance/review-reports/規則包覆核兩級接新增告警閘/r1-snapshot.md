---
type: project
status: doing
created: 2026-11-08
updated: 2026-11-08
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/kotlin規則包
  - Systems/linter精選目錄
related:
  - "[[Projects/規則包語意覆核級命中走盲判_計劃]]"
  - "[[Systems/kotlin規則包]]"
  - "[[Systems/linter精選目錄]]"
decisions:
  - content: 覆核級 12 條與有出處的提示級規則,直接用既有新增告警閘的宣告接上:每筆新命中照新增告警擋,作者用 lint-waive 附理由放行(誤報或接受風險都寫進理由);出處不全列上的 8 條提示級規則搬到不接閘的 rules-hints-unsourced/;不另做表態題、人複查、推翻、宣告檔
    id: d1
    context: 前案(規則包語意覆核級命中走盲判)設計審三輪 55/50/48 條沒收斂,第三輪 24 條大問題集中在新機制接不上既有介面(逾時與工具沒裝的處置、快照比對、指紋、統計欄位);既有新增告警閘加 lint-waive 已有逐筆擋、理由必填、記規則與檔、AI 放行待看、統計
    why_chosen: 使用者 2026-11-08 原話「語意覆核照計畫重寫」;d5「每筆新命中要作者交代、沒交代就擋、AI 判定不決定擋」由既有閘直接滿足
    decided: 2026-11-08
    valid: true
---
# 規則包覆核兩級接新增告警閘_計劃

> 白話:Kotlin 規則包有兩級規則一直沒接上:語意覆核級(`rules-review/`,12 條,形狀抓得到可疑寫法、分不出對錯)與提示級(`rules-hints/`,50 條)。它們既不擋、也不量、也沒人看。這份計劃直接用既有的「新增告警閘」接上:專案宣告了這兩份規則設定,推送前每一筆這次新帶進來的命中就跟一般新增告警一樣被擋,作者要嘛改掉,要嘛用既有的 `lint-waive <指紋> --note "<理由>"` 放行(誤報或接受風險都寫進理由)——放行會記規則、檔名、理由與誰放的,AI 放的進待看清單、統計看得到。型錄裡標「出處不全」的列所掛的 8 條提示級規則,依「依據不足的規則不准擋人」搬到一個不接閘的目錄。前案 [[Projects/規則包語意覆核級命中走盲判_計劃]] 設計審三輪沒收斂,使用者 2026-11-08 裁「語意覆核照計畫重寫」。

PRIOR-ART: SonarQube 的「Clean as You Code」只擋新程式的新問題,作者可以把問題標成誤報或接受(Won't Fix)並附理由,標記跟著問題身分走(https://docs.sonarsource.com/sonarcloud/improving/clean-as-you-code 、https://docs.sonarsource.com/sonarqube-server/latest/user-guide/issues/solution-overview/ )。Semgrep 的規則模式決定擋不擋,AI 判誤報只做註解(https://semgrep.dev/docs/semgrep-code/policies )。本專案的新增告警閘加 `lint-waive` 就是這個形狀(只擋新增、指紋綁規則加檔名加命中行、放行要理由、AI 放行待人看),前案三版重新發明它而三輪都接錯介面;採用既有的閘,不另造。
RETIRE-IF: 上線八週後,覆核兩級的新增命中有八成以上被放行、而且放行理由多是誤報 → 那幾條規則改形狀或刪掉;整兩級八週內新增命中少於 10 筆 → 撤回範本裡的兩條宣告。

## 狀態

設計第一版(2026-11-08)。

## 跟前案的關係

前案的使用者裁定照舊成立:d5「每筆新命中要作者交代、沒交代就擋、AI 判定不決定擋不擋」由新增告警閘直接滿足(擋的是沒放行、放行要寫理由、沒有 AI 判定);d6「誤報抽查、誤報樣本回流、改形狀與升擋候選」這一版不做,另開計劃(見〈不做〉),先看上線一個月的放行量。前案的設計審卷證留在 governance/review-reports/規則包語意覆核級命中走盲判/。

## 範圍

### 做

1. **出處不全的 8 條搬目錄**:型錄主表標「出處不全」的列所掛的提示級規則(2026-11-08 主線上用型錄自檢的讀表函式數到 8 條:API-36、ARCH-3、UI-103、CO-37、FLOW-14、STATE-9、TEST-16、TEST-33 這 8 列各掛一條;實作時照程式重算)從 `rules-hints/` 搬到新目錄 `rules-hints-unsourced/`,檔名照原主題(例 `api.yml`);新增 `sgconfig-hints-unsourced.yml` 只載這個目錄。壞例、好例樣本以規則 id 分目錄,不用搬。
2. **型錄自檢跟著改**:`configs/ast-grep/kotlin-android/check.py` 的 `CONFIGS` 加第四組、`_DIR_SEVERITY` 讓 `rules-hints-unsourced` 只收 hint;「引用出處不全的列只准 hint 級」那條檢查改成「只准放在 `rules-hints-unsourced/`」(放在 `rules/`、`rules-review/`、`rules-hints/` 任一個都報)。好例檢查裡「語意覆核級規則已知誤報樣本不算好例誤報」那條照舊只對 `rules-review/`。
3. **SARIF 真的有輸出**(實作第一步、先做實驗):新增告警閘讀 SARIF;ast-grep 的提示級在 SARIF 裡對應 `note`、在 GitHub 註解輸出被略過(ast-grep 0.42.0 原始碼 `print/cloud_print.rs`),0.51.1 沒人驗過。型錄自檢的完整模式(要 ast-grep,CI 跑)多一項:拿一條覆核級、一條提示級規則的壞例樣本各跑一次 `--format sarif`,結果要至少一筆;沒有就報問題。若實驗發現提示級在 SARIF 裡不出現,改把 `rules-hints/` 的嚴重度提到 info(`_DIR_SEVERITY` 跟著改),並在這份計劃記下。
4. **宣告範本**:[[Systems/linter精選目錄]] 的 Kotlin 規則包範本從一條改成三條:原本的 `sgconfig.yml`,加 `sgconfig-review.yml` 與 `sgconfig-hints.yml`(三條同一個寫法、各自 `{LINT_FILES}`、`{LINT_SARIF_OUT}`);「提示級規則預設不接」那句改成「覆核兩級一起接、命中照新增告警擋,誤報用 `lint-waive` 附理由放行;出處不全的規則在 `sgconfig-hints-unsourced.yml`,不接」。測試檔要掃的提醒(`include_test_paths`)照舊留著。
5. **文字同步**:`skills/kotlin-idioms/checks-catalog.md` 第 11 行通電批次欄的定義、那 41 格「批一(只有提示級規則,預設不接)」與 7 格「接上前不擋」照新的接法改寫(搬到 unsourced 的那 8 條對應的列保留「預設不接」);`check.py` 開頭三級說明的註解;[[Systems/kotlin規則包]] 補 WHY;前案計劃標作廢、指向本計劃。

### 不做

- 不做表態題、盲判抽查、人複查、推翻、另開宣告檔(前案三版的機制,整組不要)。
- 不做誤報抽查與誤報樣本回流(前案 d6):另開計劃;那份計劃從 `lint-waive --list` 裡覆核兩級規則的放行紀錄出發。
- 不替出處不全的 8 條補出處(型錄逐列查證那條線)。
- 不改新增告警閘本身(指紋、只擋新增、放行、逾時與工具沒裝的處置都照舊)。
- 不自動替消費專案改 `.lumos/lint.json`:範本改了,消費專案要自己抄。

## 實務隱患

- **誤擋量**:62 條在真專案的命中量沒量過(2026-11-05 只跑了會擋的那份)。上線前用實驗專案與 nowinandroid 各跑一次兩份設定,量新增命中筆數,記進這份計劃;量出來太多就先只接覆核級。
- **作者隨手放行**:放行只要理由,AI 也能放;AI 放的進待看清單、doctor 數(跟一般新增告警同一個天花板)。
- **改名、重新縮排讓命中換指紋**:同一般新增告警,改了就重新擋一次。
- **提示級在 SARIF 裡沒輸出**:做 3 的實驗先驗;不驗就接,等於接了沒效。
- 已排除:金流:不碰付款
- 已排除:對外送出:只讀本機檔與跑本機 ast-grep,不連網
- 已排除:不可逆:搬規則檔、改自檢與範本文字,退提交即回原狀;消費專案已照新範本接的,退回後照舊範本刪兩條宣告即可
- 守衛面:不排除——範本讓消費專案多兩份會擋的規則設定,動的是守衛面

REVISIT:2026-12-08 看上線一個月:覆核兩級新增命中幾筆、放行幾筆與理由、AI 放行幾筆沒人看;決定要不要開誤報抽查那份計劃

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 只擋新增、作者標誤報或接受並附理由 | SonarQube Clean as You Code 與問題狀態 | https://docs.sonarsource.com/sonarcloud/improving/clean-as-you-code 、https://docs.sonarsource.com/sonarqube-server/latest/user-guide/issues/solution-overview/ |
| 擋不擋由規則設定決定、AI 不決定 | Semgrep 規則模式;使用者裁定 d5 | https://semgrep.dev/docs/semgrep-code/policies ;使用者 2026-11-07:「我會希望近判斷，證偽的可以回頭來eval判別方式」 |
| 依據不足的規則不准擋人 | 規則包既有規矩 | [[Systems/kotlin規則包]] 的 WHY「查不到的列標(出處不全),引用它的規則只准提示級」 |
| 改用既有閘重寫 | 使用者裁定 | 使用者 2026-11-08:「語意覆核照計畫重寫」 |
| 提示級在 SARIF 對應 note | ast-grep 原始碼 | https://docs.rs/crate/ast-grep/0.42.0/source/src/print/cloud_print.rs |
| 兩級 62 條一起處理 | 使用者裁定 | 使用者 2026-11-07:「62 條一起處理，先建語意覆核接盲判的計劃」 |

## 驗收條款

- [S1] 當型錄自檢讀規則包時,引用出處不全列的規則放在 `rules/`、`rules-review/` 或 `rules-hints/` 任一個 應 報問題;放在 `rules-hints-unsourced/` 而且是 hint 級 應 不報;真實規則包 應 0 個問題 [test:t_kt_rulepack_unsourced_dir]
- [S2] 當型錄自檢的完整模式跑時,覆核級與提示級各一條規則的壞例樣本用 SARIF 格式掃 應 各至少一筆結果;沒有結果 應 報問題 [manual:CI 的型錄自檢那一步(要 ast-grep 0.51.1)看最後兩行沒有 SARIF 相關問題]
- [S3] 當 `.lumos/lint.json` 照新範本宣告三份設定、這次改動帶進一筆覆核級規則的新命中時,新增告警閘 應 擋;`lint-waive <指紋> --note` 之後 應 放行;出處不全規則的命中 應 不出現 [manual:上線前在實驗專案照範本接上,造一筆命中跑一次推送前檢查與 lint-waive,結果記進這份計劃]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 一條引用出處不全列的 hint 規則放在 `rules-hints/` | 報問題 | 範圍做 2:出處不全只准不接閘的目錄 |
| S1 | 同一條放在 `rules-review/`(info) | 報問題 | 範圍做 2:出處不全只准不接閘的目錄 |
| S1 | 同一條放在 `rules-hints-unsourced/`、hint 級 | 不報 | 範圍做 2:出處不全只准不接閘的目錄 |
| S1 | 一條 info 級規則放在 `rules-hints-unsourced/` | 報問題(只收 hint) | 範圍做 2:出處不全只准不接閘的目錄 |
| S1 | 真實規則包(8 條搬完) | 0 個問題 | 範圍做 1、2:搬目錄後自檢要乾淨 |
| S2 | 覆核級壞例樣本用 SARIF 掃 | 至少一筆結果 | 範圍做 3:SARIF 要真的有輸出 |
| S2 | 提示級壞例樣本用 SARIF 掃 | 至少一筆結果;沒有就報問題並照做 3 改嚴重度 | 範圍做 3:SARIF 要真的有輸出 |
| S3 | 照新範本接上、新增一筆覆核級命中 | 推送前擋 | 範圍做 4:範本三條宣告照新增告警閘擋 |
| S3 | 同一筆 `lint-waive <指紋> --note "<理由>"` 之後 | 放行 | 範圍做 4:範本三條宣告照新增告警閘擋 |
| S3 | 新增一筆出處不全規則的命中 | 不出現在新增告警裡 | 範圍做 1、4:不接閘的目錄不進宣告 |

## 回退

退回本計劃的提交:8 條規則回到 `rules-hints/`、`sgconfig-hints-unsourced.yml` 不在、自檢回到只看嚴重度、範本回到一條;已照新範本接的消費專案刪掉兩條宣告即回原狀,放行檔裡覆核規則的放行紀錄留著無害(指紋不會再出現)。

## 天花板

1. 擋的是沒放行,不是判斷錯;放行理由真假沒人驗(誤報抽查另開計劃)。
2. AI 也能放行,只會進待看清單。
3. 提示級在 SARIF 的輸出只在 CI 用 0.51.1 驗過一次;換版本要重驗。

## 審計修正紀錄
