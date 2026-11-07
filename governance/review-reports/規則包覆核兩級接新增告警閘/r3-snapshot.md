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
    valid: false
    superseded_by: "#d2"
    ended: 2026-11-08
  - content: 這一版範本只接覆核級(sgconfig-review.yml);提示級照規則包有效的 RULE(誤報超過一成不擋)先不接、另開計劃量誤報;不接閘的目錄叫 rules-unwired/,收出處不全與還沒量過誤報的新規則,不限嚴重度;取代 d1 的目錄名與「有出處的提示級一起接」
    id: d2
    context: 設計審 r2 通才席指出提示級裡有當初因誤報才降級的規則,一起接閘等於推翻 kotlin規則包那條欄位齊全、近期確認的 RULE;r1 整合席指出覆核級接閘後試水溫流程會消失
    why_chosen: 照專案 CLAUDE.md:欄位齊全且近半年確認過的 RULE 有挑戰效力,不自行推翻;使用者 2026-11-08「語意覆核照計畫重寫」的範圍內縮最小
    decided: 2026-11-08
    valid: true
---
# 規則包覆核兩級接新增告警閘_計劃

> 白話:Kotlin 規則包有兩級規則一直沒接上:語意覆核級(`rules-review/`,12 條,形狀抓得到可疑寫法、分不出對錯)與提示級(`rules-hints/`,50 條)。它們既不擋、也不量、也沒人看。這份計劃直接用既有的「新增告警閘」接上:專案宣告了這兩份規則設定,推送前每一筆這次新帶進來的命中就跟一般新增告警一樣被擋,作者要嘛改掉,要嘛用既有的 `lint-waive <指紋> --note "<理由>"` 放行(誤報或接受風險都寫進理由)——放行會記規則、檔名、理由與誰放的,AI 放的進待看清單、統計看得到。型錄裡標「出處不全」的列所掛的 8 條提示級規則,依「依據不足的規則不准擋人」搬到一個不接閘的目錄。前案 [[Projects/規則包語意覆核級命中走盲判_計劃]] 設計審三輪沒收斂,使用者 2026-11-08 裁「語意覆核照計畫重寫」。

PRIOR-ART: SonarQube 的「Clean as You Code」只擋新程式的新問題,作者可以把問題標成誤報或接受(Won't Fix)並附理由,標記跟著問題身分走(https://docs.sonarsource.com/sonarcloud/improving/clean-as-you-code 、https://docs.sonarsource.com/sonarqube-server/latest/user-guide/issues/solution-overview/ )。Semgrep 的規則模式決定擋不擋,AI 判誤報只做註解(https://semgrep.dev/docs/semgrep-code/policies )。本專案的新增告警閘加 `lint-waive` 就是這個形狀(只擋新增、指紋綁規則加檔名加命中行、放行要理由、AI 放行待人看),前案三版重新發明它而三輪都接錯介面;採用既有的閘,不另造。
RETIRE-IF: 在實驗專案上線八週後人工看 `lint-waive --list` 與推送前檢查的擋下紀錄:某條覆核級規則被放行的筆數過半、而且放行理由都是誤報 → 那條搬回 `rules-unwired/` 或改形狀;八週內覆核級新增命中少於 10 筆 → 撤回範本裡覆核級那條宣告(放行與擋下只在有帳的專案看得到,工具鏈看不到消費專案;這條靠人看,不是機器算)。

## 狀態

設計第三版(2026-11-08,折入設計審 r2 四席:這版只接覆核級、拿掉分級改動、收工只准會擋的那份)。

## 跟前案的關係

前案的使用者裁定照舊成立:d5「每筆新命中要作者交代、沒交代就擋、AI 判定不決定擋不擋」由新增告警閘直接滿足(擋的是沒放行、放行要寫理由、沒有 AI 判定);d6「誤報抽查、誤報樣本回流、改形狀與升擋候選」這一版不做,另開計劃(見〈不做〉),先看上線一個月的放行量。前案的設計審卷證留在 governance/review-reports/規則包語意覆核級命中走盲判/。

## 範圍

### 做

1. **不接閘的目錄 `rules-unwired/`**(r1 整合 F3:規則包既有「新規則先試水溫、量過才擋」的流程):新增 `rules-unwired/` 與只載它的 `sgconfig-unwired.yml`,範本不宣告它,收工檢查也不跑它。它收「依據還不夠擋人」的規則:(a) 引用型錄「出處不全」列的規則;(b) 還沒在真專案量過誤報的新規則。嚴重度不限(試水溫的規則照它將來要升到的等級寫,搬出去時不用改等級)。2026-11-08 主線上 (a) 有 8 條,用型錄自檢的讀表函式數出:API-36、ARCH-3、UI-103、CO-37、FLOW-14、STATE-9、TEST-16、TEST-33 這 8 列各掛一條,分散在 `rules-hints/` 的 7 支檔裡(每支同檔還有 4 到 6 條有出處的規則),所以是拆檔:照 `---` 切出那幾條,搬到 `rules-unwired/` 的同名主題檔,原檔留下其餘規則;壞例、好例樣本以規則 id 分目錄,不用搬。
2. **型錄自檢跟著改**:`configs/ast-grep/kotlin-android/check.py` 的 `CONFIGS` 加第四組;`_DIR_SEVERITY` 對 `rules-unwired` 不限嚴重度;「引用出處不全的列只准 hint 級」那條檢查改成「只准放在 `rules-unwired/`」(放在 `rules/`、`rules-review/`、`rules-hints/` 任一個都報,原因句照既有二元組格式:「引用出處不全的 <列>,只准放 rules-unwired/」),讀規則所在目錄一律用 `r.get("dir")`(既有測試的假規則沒有這個鍵,缺鍵照「不在 unwired」算)。另外兩句寫死三個目錄的訊息(嚴重度與目錄不符那句、「一條規則都沒讀到」那句)補第四個目錄。好例檢查裡「已知誤報樣本不算好例誤報」那條改成對 `rules-review/` 與 `rules-unwired/` 生效(擴 `review_ids`)。`scripts/test_lumos.py` 的 `t_kotlin_rulepack_samples` 裡「規則目錄全空」那段迴圈要把第四個目錄加進去(改測試檔要簽名)。
3. **SARIF 真的有輸出,並綁測試**:r1 整合席已用 ast-grep 0.51.1 實測——拿壞例樣本掃三份設定,覆核級 60 筆、提示級 148 筆、會擋的 488 筆都出現在 SARIF,覆核與提示級的 level 都是 `note`;r2 整合席在臨時專案照新範本端到端實跑:新增告警閘照收 note、擋下訊息印得出 `lint-waive` 指令、放行後轉乾淨、零命中時是合法 SARIF。為了讓工具鏈換版本時有東西會紅:型錄自檢的完整模式多一項,拿 `rules-review/` 的 `kt-livedata-setvalue-background` 與 `rules-hints/` 的 `kt-value-assign-background` 兩條規則的壞例樣本用 `--format sarif` 掃,結果裡要各有一筆 `ruleId` 是那條規則;沒有就報「SARIF 掃壞例樣本沒有 <規則> 的結果」(原因句含「樣本」二字,`t_kotlin_rulepack_samples` 只留含「壞例、好例、樣本、載入、祖先」的問題);掃描共用既有的逾時旗標,讀不懂輸出照「跑不起來」報、不丟例外。
4. **宣告範本這一版只接覆核級**(r2 通才 F3:提示級有不少是當初因誤報才降級的規則,型錄也自標「誤報多」;規則包那條 RULE「誤報超過命中的一成就降提示級或改形狀」欄位齊全、近期確認過,有效力,不推翻):[[Systems/linter精選目錄]] 的 Kotlin 規則包範本從一條改成兩條:`sgconfig.yml`(排第一)與 `sgconfig-review.yml`(兩份設定檔主線上都已存在,只改範本文字;同一個寫法、各自 `{LINT_FILES}`、`{LINT_SARIF_OUT}`)。提示級照舊不接,那句改成「提示級是誤報較高的那一級,要先在專案量過誤報低於一成才接;依據不夠的規則在 `sgconfig-unwired.yml`,不接」。安裝句從「0.51.1 以上」改成釘 `pipx install ast-grep-cli==0.51.1`(brew 的版本另寫「規則包的 SARIF 輸出只在 0.51.1 實測過」)。另寫明:預算不夠時沒跑到的 ast-grep 那條會讓推送被擋(不是安靜略過),Kotlin 專案同時宣告 detekt 時把 ast-grep 排在前面。
5. **收工檢查只准會擋的那份**(r1 整合 F1;r2 三席:用兩個檔名當黑名單擋不住新設定與大小寫變體):`scripts/lumos` 的 `_lint_wt_allow` 在既有「真實路徑在工具鏈 `configs/ast-grep/` 底下」之後再加一條:真實路徑要跟 `configs/ast-grep/kotlin-android/sgconfig.yml` 是同一支檔(用既有判目錄時的 `os.path.samefile` 救濟,不比字串),不是就回 `(None, "工作樹模式只自動執行規則包會擋的 sgconfig.yml,<那支檔名> 留給推送前")`。覆核級、`sgconfig-unwired.yml` 與將來任何新設定都只在推送前判(或不判)。
6. **文字同步**(r2 整合 F3 用主線 git grep 列齊):
   - `skills/kotlin-idioms/checks-catalog.md`:第 11 行通電批次欄的定義,覆核級改成「語意覆核級=規則在 `rules-review/`,新增命中照新增告警擋、誤報用 lint-waive 附理由放行」,另定義「不接(rules-unwired)=規則在 `rules-unwired/`,依據不夠或還沒量過誤報」;寫「接上前不擋」的 7 格(API-17、STATE-1、STATE-7、STATE-16、CO-44、DATA-10、DATA-36,其中 STATE-16 同列另有提示級規則,格子兩級都要講)與覆核級卻標「批一」的 3 格(API-11、STATE-4、TEST-5)照新定義改;出處不全那 8 列的格子改成「不接(rules-unwired)」;其餘提示級的 32 格不動(提示級照舊不接)。新文字保留「告警帶寫法=批一」前綴,括號裡不放分號。
   - `configs/ast-grep/kotlin-android/`:`check.py` 開頭三級說明、`REVIEW_FP_PREFIX` 與好例檢查那兩處「要靠盲判排除」的註解;`rules-review/` 五支 yml 檔頭與內文講「接上前不擋」「要靠盲判」的 7 處註解;兩支 `review-fp-*.kt` 樣本第一行註解。
   - [[Systems/kotlin規則包]]:「查不到的列標(出處不全),引用它的規則只准提示級」那條 WHY 改成「只准放 rules-unwired/」,`[test:]` 改掛 `t_kt_rulepack_unwired_dir`;「誤報超過一成就降提示級或改形狀」那條 RULE 改成「降到提示級或 rules-unwired/,或改形狀」並重新 `[confirmed:]`(提示級照舊不接,所以原意不變、只多一個去處);工作流程「新規則先放語意覆核級」改成「先放 rules-unwired/」;檔案節分檔那行補第四個目錄、`sgconfig-review.yml` 與 `sgconfig-hints.yml` 兩行照新接法改寫、補一行 `sgconfig-unwired.yml`。
   - 其他計劃:前案 [[Projects/規則包語意覆核級命中走盲判_計劃]] 已標 `superseded`;[[Projects/Android協程與API寫法機械檢查標準_計劃]] 第 73、126 行與條款 [S2](綁 `t_kotlin_rulepack_messages_cite_catalog`,寫「應 是提示級」)、[[Projects/Android寫法語意情境表態與盲判_計劃]] 指向前案那句、[[Projects/Android寫法型錄逐列查證_計劃]] 第 36、48 行「應降到 rules-hints/」改成新說法(已實作的計劃改條款只改字面、不改測試意圖,改法在審計修正紀錄寫一行)。

### 不做

- 不做表態題、盲判抽查、人複查、推翻、另開宣告檔(前案三版的機制,整組不要)。
- 不接提示級(理由見做 4);另開計劃在實驗專案量誤報,量過一成以下的規則才接。
- 不改 `pitfalls --diff` 的分級(第二版的做 6 拿掉:r2 兩席指出所有自動路徑都帶 `--no-lint`,lint 命中本來就不進代碼審分級;r2 通才席指出讀被審分支自己的放行檔會讓它自己決定要不要被審)。
- 不做誤報抽查與誤報樣本回流(前案 d6):另開計劃,從 `lint-waive --list` 裡覆核級規則的放行紀錄出發。
- 不替出處不全的 8 條補出處(型錄逐列查證那條線)。
- 不改新增告警閘的判定本身(指紋、只擋新增、放行、逾時與工具沒裝的處置都照舊)。
- 不自動替消費專案改 `.lumos/lint.json`,也不做「範本停在舊版」的偵測(lint-check 只驗格式);範本改了,消費專案要自己抄。

## 實務隱患

- **誤擋量**:接閘的是覆核級 12 條,在真專案的命中量沒量過。上線前在實驗專案照新範本、`.lumos/config.json` 開 `{"lint_new": {"include_test_paths": ["kt"]}}`(覆核級有測試主題的規則)跑一次推送前檢查,推送內容是實驗專案最近一個功能分支對主線的範圍,新增命中筆數記進這份計劃。
- **作者隨手放行**:放行只要理由,AI 也能放;AI 放的進待看清單、doctor 印軟提醒(不擋)。收工檢查不跑覆核級(做 5),所以 AI 只在推送前才會被它擋。
- **指紋綁整段命中範圍**:覆核級不少規則命中的是整個區塊,區塊裡改任何一行指紋就變、重擋一次;同檔同片段放行一次,之後同片段的新命中也一起放行(同一般新增告警)。
- **新規則一進去就擋**:新寫的規則一律先放 `rules-unwired/`,量過才搬進接閘目錄(做 1、做 6 的工作流程)。
- **預算耗盡會擋**:新增告警閘沒跑到的 ast-grep 那條判擋(做 4 寫進範本說明)。
- **消費專案的 ast-grep 版本**:範本釘 0.51.1;用 brew 裝的不受控,工具鏈 CI 也看不到。
- 已排除:金流:不碰付款
- 已排除:對外送出:只讀本機檔與跑本機 ast-grep,不連網
- 已排除:不可逆:拆規則檔、改自檢與收工白名單、改範本與註解文字,退提交即回原狀;消費專案已照新範本接的,退回後刪掉覆核級那條宣告即可
- 守衛面:不排除——範本讓消費專案多一份會擋的規則設定、收工白名單變窄;風險是誤擋變多(上線前量測)與收工時看不到覆核級命中(推送前才擋)

REVISIT:2026-12-08 在實驗專案看上線一個月:覆核級新增命中幾筆、放行幾筆與理由(`lint-waive --list`)、AI 放行幾筆沒人看;決定要不要開「提示級量誤報後接閘」與「誤報抽查」兩份計劃、哪幾條覆核級規則該搬回 rules-unwired/

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 只擋新增、作者標誤報或接受並附理由 | SonarQube Clean as You Code 與問題狀態 | https://docs.sonarsource.com/sonarcloud/improving/clean-as-you-code 、https://docs.sonarsource.com/sonarqube-server/latest/user-guide/issues/solution-overview/ |
| 擋不擋由規則設定決定、AI 不決定;新規則先試水溫 | Semgrep 規則模式(Monitor/Comment/Block);使用者裁定 d5 | https://semgrep.dev/docs/semgrep-code/policies ;使用者 2026-11-07:「我會希望近判斷，證偽的可以回頭來eval判別方式」 |
| 依據不足的規則不准擋人、誤報超過一成不擋 | 規則包既有 WHY 與 RULE | [[Systems/kotlin規則包]] 的 WHY「查不到的列標(出處不全),引用它的規則只准提示級」、RULE「規則在真專案誤報超過命中的一成就降提示級或改形狀」 |
| 改用既有閘重寫 | 使用者裁定 | 使用者 2026-11-08:「語意覆核照計畫重寫」 |
| 覆核級與提示級在 SARIF 有輸出、閘照收 | 實測 | 2026-11-08 設計審 r1、r2 整合席在臨時目錄裝 ast-grep 0.51.1 實掃與端到端實跑(卷證 r1-整合-sonnet.md F2、r2-整合-sonnet.md) |
| 兩級 62 條一起處理 | 使用者裁定;這一版先接覆核級 12 條、提示級等量測 | 使用者 2026-11-07:「62 條一起處理，先建語意覆核接盲判的計劃」 |

## 驗收條款

- [S1] 當型錄自檢讀規則包時,引用出處不全列的規則放在 `rules/`、`rules-review/` 或 `rules-hints/` 任一個 應 報問題;放在 `rules-unwired/`(任何嚴重度) 應 不報;真實規則包 應 0 個問題 [test:t_kt_rulepack_unwired_dir]
- [S2] 當型錄自檢的完整模式跑時,兩條指定規則的壞例樣本用 SARIF 格式掃 應 各有一筆 ruleId 是那條規則的結果;沒有 應 報一個含「樣本」的問題 [test:t_kotlin_rulepack_samples]
- [S3] 當收工檢查的工作樹模式遇到 `--config` 指向規則包 `sgconfig.yml` 以外任何設定時,它 應 不自動執行那條並印出原因;指向 `sgconfig.yml`(含 `$HOME/` 寫法與大小寫變體) 應 照舊執行 [test:t_lint_wt_allow_only_blocking_pack]
- [S4] 當 `.lumos/lint.json` 照新範本宣告兩份設定、這次改動帶進一筆覆核級規則的新命中時,新增告警閘 應 擋;`lint-waive <指紋> --note` 之後 應 放行;提示級與 `rules-unwired/` 規則的命中 應 不出現 [manual:上線前在實驗專案照範本接上,造一筆命中跑一次推送前檢查與 lint-waive,結果記進這份計劃]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 一條引用出處不全列的 hint 規則放在 `rules-hints/` | 報問題 | 範圍做 2:出處不全只准不接閘的目錄 |
| S1 | 同一條放在 `rules-review/` | 報問題 | 範圍做 2:出處不全只准不接閘的目錄 |
| S1 | 同一條放在 `rules-unwired/`、warning 級 | 不報 | 範圍做 1、2:不接閘目錄不限等級 |
| S1 | 假規則沒有 dir 鍵、引用出處不全列 | 報問題 | 範圍做 2:缺鍵照不在 unwired 算 |
| S1 | 真實規則包(8 條拆完) | 0 個問題 | 範圍做 1、2:拆檔後自檢要乾淨 |
| S2 | `kt-livedata-setvalue-background` 壞例用 SARIF 掃 | 有那條 ruleId 的結果 | 範圍做 3:SARIF 要真的有輸出 |
| S2 | 假 ast-grep 對 SARIF 掃描回別條規則的結果 | 報含「樣本」的問題 | 範圍做 3:要驗目標規則、換版本會紅 |
| S3 | 收工檢查遇到 `--config …/sgconfig-review.yml` | 不自動執行,印原因 | 範圍做 5:收工只跑會擋的那份 |
| S3 | 收工檢查遇到 `--config …/SGCONFIG-UNWIRED.YML` | 不自動執行 | 範圍做 5:比同一支檔不比字串 |
| S3 | 收工檢查遇到 `--config $HOME/…/kotlin-android/sgconfig.yml` | 照舊執行 | 範圍做 5:會擋的那份照舊 |
| S4 | 照新範本接上、新增一筆覆核級命中 | 推送前擋 | 範圍做 4:範本兩條宣告照新增告警閘擋 |
| S4 | 同一筆 `lint-waive <指紋> --note "<理由>"` 之後 | 放行 | 範圍做 4:範本兩條宣告照新增告警閘擋 |

## 回退

退回本計劃的提交:8 條規則回到 `rules-hints/`、`rules-unwired/` 與 `sgconfig-unwired.yml` 不在、自檢回到只看嚴重度、範本回到一條、收工白名單回到改動前;已照新範本接的消費專案刪掉覆核級那條宣告即回原狀,放行檔裡覆核規則的放行紀錄留著無害(指紋不會再出現)。

## 天花板

1. 擋的是沒放行,不是判斷錯;放行理由真假沒人驗(誤報抽查另開計劃)。
2. AI 也能放行,只會進待看清單。
3. 規則包的 SARIF 輸出只在 0.51.1 實測過;做 3 的自檢只在工具鏈 CI(釘 0.51.1)上跑,消費專案升版後若輸出形狀變了,工具鏈看不到。
4. 收工檢查不跑覆核級,寫的當下看不到這一級的命中,推送前才擋。
5. 提示級 42 條這一版仍不接,使用者「62 條一起處理」只先做到覆核級 12 條與 8 條出處不全的歸位。

## 審計修正紀錄
- r1(2026-11-08,四席 sonnet:通才、正確性、整合、架構對齊):22 條/blocking 5/收工檢查也會跑兩級、放行過的命中仍推高分級、SARIF 自檢會被既有測試濾掉、覆核級接閘讓試水溫流程消失、SARIF 有沒有輸出沒實測;整合席實測 0.51.1 提示級與覆核級都有輸出(level note);全部折入做 1–7,新目錄改名 rules-unwired 兼收出處不全與還沒量過的新規則;分組在 r1-intake.md。
- r2(2026-11-08,四席 sonnet 新席):27 條/blocking 5/做 6 的指紋算法對不上而且自動路徑本來就不算 lint(兩席)、讀被審分支自己的放行檔會自己逃審、提示級接閘推翻有效的誤報一成 RULE、消費專案版本漂移看不到、收工黑名單擋不住新設定;第三版這版只接覆核級、拿掉做 6、收工改白名單只准 sgconfig.yml、範本釘版本、文字同步清單照主線 git grep 列齊;分組在 r2-intake.md。
