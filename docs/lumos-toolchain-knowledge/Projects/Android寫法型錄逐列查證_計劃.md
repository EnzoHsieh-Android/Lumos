---
type: project
status: done
created: 2026-11-07
updated: 2026-11-08
tags:
  - type/project
  - status/done
  - scope/stack-knowledge
related:
  - "[[Projects/計劃依據來源必填_計劃]]"
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/kotlin規則包
decisions:
  - content: API-14、TEST-31 標出處不全、引用它們的三條規則搬 rules-unwired/;DATA-12 照官方 updateData 原文改成取捨提醒
    id: d1
    decided: 2026-11-08
    valid: true
---

# Android寫法型錄逐列查證_計劃

> 白話:Kotlin/Android 寫法型錄(`skills/kotlin-idioms/checks-catalog.md`)主表 473 列,原本只有 142 列在來源欄留了逐列查證紀錄,其餘只寫縮寫或首頁網址。使用者要求每列要有真的打開讀過的官方出處、查不到的標出處不全(2026-11-05「你的標準、最佳寫法來源要有依據，不要你自己寫」);[[Projects/計劃依據來源必填_計劃]] 做法 6 把缺口變成型錄自檢的一個數字,並把補齊交給這份計劃。這次把 331 列逐列查完、套回型錄,並把那個數字接上電。

PRIOR-ART: 型錄每列對到官方文件或官方規則說明頁,做法跟 Android Lint、detekt、compose-rules 每條規則附說明頁一樣;查證紀錄寫進來源欄的〔查證 日期:網址〕是型錄 2026-11-05 起既有的格式,不另立欄位。
RETIRE-IF: 型錄自檢的「還沒逐列查證」連續八週都是 0、而且新增的列都在同一個提交裡帶了查證紀錄 → 這份計劃結案,數字照留當守衛。

## 狀態

已上線;〈待人裁〉的三項(API-14、TEST-31、DATA-12)2026-11-08 使用者裁定、照建議做完(DATA-12 原本說的「取捨提醒」,設計審 r1 後改成型錄既有的人裁列)。DATA-12 的官方原文:All operations are serialized, and the transform itself is a coroutine so it can perform heavy work such as RPCs(https://developer.android.com/reference/kotlin/androidx/datastore/core/DataStore)。

## 範圍

### 做

1. **逐列查 331 列**:主表裡來源欄沒有〔查證〕的列,照類別切 12 批,各派一個代理用 WebFetch 打開官方頁面(developer.android.com、kotlinlang.org、androidx 原始碼 KDoc、官方 lint 規則說明、detekt.dev、compose-rules、Square 與 Google 官方 GitHub),每列判 verified(附網址與逐字原文)、weak(找不到權威原文)、contradicted(官方說法相反)。部落格、問答網站只當線索、不當出處。
2. **抽查**:編排者隨機抽 20 列 verified,用 curl 直接抓原頁比對引句(WebFetch 的回傳可能是摘要,不一定逐字):20 列都找得到(17 列逐字、3 列字詞全中)。contradicted 3 列、二次深查新 verified 3 列也逐一抓原頁核對,全中。
3. **套回型錄**:verified 的列在來源欄尾加〔查證 2026-11-07:網址〕;weak 的列名稱標(出處不全);contradicted 的列照官方原文改(CO-27 後果、UI-100 標準寫法與情境怎麼認)。
4. **掛著會擋規則的 weak 列再深查一次**:API-14、DATA-37、FLOW-8、STATE-21、TEST-31 第一次查不到、但掛著 `rules/` 底下會擋的規則,另派一個代理深查;DATA-37、FLOW-8、STATE-21 找到官方原文(都是官方建議的寫法,壞寫法是從建議推出來的),補上查證紀錄,規則照擋;API-14、TEST-31 仍找不到,這一批不標出處不全(一標就違反「出處不全只准放不接閘的 rules-unwired/」、等於同時降級會擋的規則),留在「還沒逐列查證」的數字裡,降不降級交使用者裁;2026-11-08 人裁後改標出處不全、三條規則搬 rules-unwired/(見〈待人裁〉)。
5. **接上數字**:`check.py` 新增 `catalog_unverified`,`--catalog-only` 與完整檢查的文字輸出都另印一行「還沒逐列查證 N 列」與前 20 個編號(`--json` 例外:維持純 JSON,這個數字不在 JSON 裡),不進問題清單、不改退出碼([[Projects/計劃依據來源必填_計劃]] S5 的實作,那條條款原本懸空等兩條分支合併)。
6. **統計節**:規則包等級條數、會擋規則守到的列數、出處不全列數照程式重算,另加一行逐列查證列數。

### 不做

- 不補已經有〔查證〕紀錄的 142 列(那批 2026-11-05 已查)。
- 不改〈待查證〉節的「待查」「未開頁核對」字樣:那一節由程式從原始欄位撈,改它要動撈法,另案。
- 不替 weak 的列自己找替代出處或改寫成「推論」。

## 待人裁(2026-11-08 已裁)

使用者 2026-11-08 對編排者的建議回「照你建議」,三件照建議定案:

- **API-14、TEST-31 標出處不全**:兩列名稱加(出處不全),引用它們的規則 `kt-async-await-immediately`(原在 `rules/api.yml`)、`kt-compose-test-node-by-index`(原在 `rules/testing.yml`)、`kt-compose-test-node-by-literal-text`(原在 `rules-hints/testing.yml`,同一列的另一半)搬到 `rules-unwired/`,照規則包 WHY「引用出處不全列的規則只准放 rules-unwired/」。代價:消費專案推送前不再擋這兩種寫法。
- **DATA-12 改成人裁列**(型錄既有口徑:只剩業務判斷的列名稱標(人裁)、接電方式只寫表態對程式,不派盲判席;不掛規則、不擋):照官方 `DataStore.updateData` 原文(All operations are serialized, and the transform itself is a coroutine so it can perform heavy work such as RPCs)改寫:官方允許 transform 做耗時工作,但同一個 DataStore 的寫入依序執行,transform 跑多久後面的寫入就等多久;拿掉(出處不全)、補查證紀錄。這列沒有掛規則。

## 實務隱患

- **官方建議不是官方禁令**:verified 裡有不少列,官方原文只支持標準寫法,壞寫法的錯因或後果是推出來的(各列細節在卷證 JSON 的 note);標 verified 的口徑是「核心主張有官方原文、而且不相反」。
- **網頁會改**:查證紀錄綁日期;官方頁改版後原文可能不在。
- 已排除:金流:不碰付款
- 已排除:對外送出:查證時只讀公開網頁,型錄與規則包沒有對外呼叫
- 已排除:不可逆:改的是型錄文件與一支提醒函式,退提交即回原狀
- 守衛面:2026-11-08 使用者裁定後,API-14、TEST-31 兩列的三條規則(`kt-async-await-immediately`、`kt-compose-test-node-by-index`、`kt-compose-test-node-by-literal-text`)改放 rules-unwired/,推送前不再擋這兩種寫法(見〈待人裁〉);其餘規則包等級沒動

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 每列要有打開讀過的官方出處、查不到標出處不全 | 使用者要求 | 使用者 2026-11-05:「你的標準、最佳寫法來源要有依據，不要你自己寫」 |
| 還沒逐列查證的數字只提醒、不改退出碼 | 計劃依據來源必填做法 6 與條款 S5 | `docs/lumos-toolchain-knowledge/Projects/計劃依據來源必填_計劃.md` |
| WebFetch 引句要抓原頁抽查 | 查證代理自己回報 WebFetch 回傳是摘要、不一定逐字;實測 20 列抽查 | 實測 2026-11-07:20 列抽查 17 列逐字、3 列字詞全中(卷證 all-results.json) |
| 三列相反照官方改 | 官方原文 | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-context.html 、https://raw.githubusercontent.com/mrmans0n/compose-rules/main/docs/rules.md |
| API-14、TEST-31 標出處不全、DATA-12 改成人裁列 | 使用者人裁 | 使用者 2026-11-08「照你建議」;DATA-12 官方原文 https://developer.android.com/reference/kotlin/androidx/datastore/core/DataStore |

## 驗收條款

- [S1] 當型錄主表有一列來源欄只有縮寫或只有網址、沒有查證紀錄、名稱沒標出處不全時,型錄自檢 應 把它算進「還沒逐列查證」並另印一行;有查證紀錄或標了出處不全的列 應 不算;問題清單與退出碼 應 不因這個數字改變 [test:t_kt_catalog_unverified_rows]
- [S2] 當跑型錄自檢時,真實型錄 應 是 0 個問題、還沒逐列查證 0 列(2026-11-08 人裁後;原本是 API-14、TEST-31 兩列) [test:t_kt_catalog_security_lint_ids]
- [S3] 當型錄某列名稱標了(出處不全)時,訊息引用那一列編號的規則 應 全在 `rules-unwired/`;API-14、TEST-31 兩列標出處不全之後,`kt-async-await-immediately`、`kt-compose-test-node-by-index`、`kt-compose-test-node-by-literal-text` 應 在 `rules-unwired/`、不在 `rules/` 或 `rules-hints/` [test:t_kotlin_rulepack_unwired_dir]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 型錄複本一列來源欄只有縮寫、沒查證紀錄、沒標出處不全 | 還沒逐列查證多算這一列,問題清單不變 | 計劃依據來源必填做法 6 與條款 S5 |
| S2 | 真實型錄跑 `check.py --catalog-only` | 0 個問題、還沒逐列查證 0 列 | 使用者 2026-11-08「照你建議」:API-14、TEST-31 標出處不全 |
| S3 | 真實規則包:引用 API-14、TEST-31 的三條規則 | 都在 `rules-unwired/` | 規則包 WHY:引用出處不全列的規則只准放 rules-unwired/ |
| S3 | 假規則引用出處不全列、放在 `rules/` | 型錄自檢報這條要搬 rules-unwired/ | 規則包 WHY:引用出處不全列的規則只准放 rules-unwired/ |

## 回退

退回本計劃的提交:型錄來源欄的〔查證 2026-11-07〕紀錄與出處不全標記拿掉、CO-27 與 UI-100 改回、`catalog_unverified` 與它的測試拿掉、統計節改回。卷證留著。

## 天花板

1. 查證是單家族模型做的,抽查只有 20 列加 6 列。
2. verified 的口徑是「核心主張有官方原文、不相反」,不是「每個細節都有原文」。

REVISIT:2026-12-07 看型錄自檢的「還沒逐列查證」有沒有因新增列而變多
REVISIT:2027-02-08 重查 API-14 與 TEST-31 的官方出處(線索:JetBrains IDE 有「Redundant 'async' call」檢查,建議把 async(...).await() 改成 withContext;Compose 測試官方頁對用索引與顯示文字找節點的說法),找到就把那一列的(出處不全)拿掉、規則搬回 `rules/`(拆出 literal-text 那條回 `rules-hints/`)
REVISIT:2027-02-08 型錄自檢「出處不全只准 unwired」只看規則訊息開頭的編號,不看型錄列的現成規則欄(STATE-9 標出處不全,它列的 kt-statein-lazily-or-no-timeout 訊息開頭是 [STATE-4]、在 rules/);看要不要改成也比現成規則欄

## 審計修正紀錄

- 2026-11-07 實作:331 列查完(verified 312、weak 16、contradicted 3);二次深查 5 列救回 3 列;套回後型錄 459 列有查證紀錄,出處不全 34 列;API-14、TEST-31 的降級與 DATA-12 待人裁。卷證:governance/review-reports/android寫法型錄逐列查證/(12 批結果、二次深查、彙總)。
- 2026-11-07 推送前:提醒函式的正規式原本直接寫龜甲括號,ruff 判成可疑字元、新增告警讓代碼審分級升到高;改成 `\u3014`/`\u3015` 跳脫,行為不變(`t_kt_catalog_unverified_rows` 照綠)。
- 2026-11-07 代碼審 r1(2 席):4 條 minor/blocking 0/折 3 條半(節點數字、標記比對、完整路徑測試、函式位置),正規式跳脫附理由放行;卷證 governance/review-reports/code-android寫法型錄逐列查證/。
- 2026-11-07 代碼審 r2(2 席):2 條 minor/blocking 0/全折(計劃補 `--json` 例外並加測試守純 JSON、欄位取成具名變數);卷證同上。
- 2026-11-07 r3 之後:catalog_unverified 的說明文字也有龜甲括號、被新增告警閘抓到(RUF002),改成文字描述;只動說明文字,行為與測試不變。
- 2026-11-08 文字同步([[Projects/規則包覆核兩級接新增告警閘_計劃]]):「出處不全的規則只准提示級」改成「只准放不接閘的 rules-unwired/」、指向前案的連結改指新計劃;只改字面,條款綁的測試與意圖不變。
- 2026-11-08 人裁落地:API-14、TEST-31 標出處不全,三條規則搬 rules-unwired/;DATA-12 照官方改成取捨提醒;型錄自檢「還沒逐列查證」0 列。
- 2026-11-08 輕量代碼審(架構對齊 1 席):3 條 minor 全折(DATA-12 查證紀錄只留網址、原文搬到〈狀態〉;情境怎麼認改成看 transform 會不會很久;實務隱患守衛面那行照實改)。
- 2026-11-08 設計審 r1(4 席):16 條 minor/blocking 0/DATA-12 改成既有的人裁列(只表態、不盲判)並補「新值靠目前值算的不要搬出去」;補兩行回頭條件(重查出處、出處不全檢查只看訊息編號);補(出處不全)定義;D-1、D-2 註記 API-14 出處不全;改 linter 目錄範例、規則包節點與覆核級計劃的舊數字;卷證 governance/review-reports/android寫法型錄逐列查證/。
