---
type: project
status: doing
created: 2026-11-07
updated: 2026-11-07
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
related:
  - "[[Projects/計劃依據來源必填_計劃]]"
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Systems/kotlin規則包]]"
lands_in:
  - Systems/kotlin規則包
---

# Android寫法型錄逐列查證_計劃

> 白話:Kotlin/Android 寫法型錄(`skills/kotlin-idioms/checks-catalog.md`)主表 473 列,原本只有 142 列在來源欄留了逐列查證紀錄,其餘只寫縮寫或首頁網址。使用者要求每列要有真的打開讀過的官方出處、查不到的標出處不全(2026-11-05「你的標準、最佳寫法來源要有依據，不要你自己寫」);[[Projects/計劃依據來源必填_計劃]] 做法 6 把缺口變成型錄自檢的一個數字,並把補齊交給這份計劃。這次把 331 列逐列查完、套回型錄,並把那個數字接上電。

PRIOR-ART: 型錄每列對到官方文件或官方規則說明頁,做法跟 Android Lint、detekt、compose-rules 每條規則附說明頁一樣;查證紀錄寫進來源欄的〔查證 日期:網址〕是型錄 2026-11-05 起既有的格式,不另立欄位。
RETIRE-IF: 型錄自檢的「還沒逐列查證」連續八週都是 0、而且新增的列都在同一個提交裡帶了查證紀錄 → 這份計劃結案,數字照留當守衛。

## 狀態

已實作,等推送。DATA-12 待使用者裁定(見〈待人裁〉)。

## 範圍

### 做

1. **逐列查 331 列**:主表裡來源欄沒有〔查證〕的列,照類別切 12 批,各派一個代理用 WebFetch 打開官方頁面(developer.android.com、kotlinlang.org、androidx 原始碼 KDoc、官方 lint 規則說明、detekt.dev、compose-rules、Square 與 Google 官方 GitHub),每列判 verified(附網址與逐字原文)、weak(找不到權威原文)、contradicted(官方說法相反)。部落格、問答網站只當線索、不當出處。
2. **抽查**:編排者隨機抽 20 列 verified,用 curl 直接抓原頁比對引句(WebFetch 的回傳可能是摘要,不一定逐字):20 列都找得到(17 列逐字、3 列字詞全中)。contradicted 3 列、二次深查新 verified 3 列也逐一抓原頁核對,全中。
3. **套回型錄**:verified 的列在來源欄尾加〔查證 2026-11-07:網址〕;weak 的列名稱標(出處不全);contradicted 的列照官方原文改(CO-27 後果、UI-100 標準寫法與情境怎麼認)。
4. **掛著會擋規則的 weak 列再深查一次**:API-14、DATA-37、FLOW-8、STATE-21、TEST-31 第一次查不到、但掛著 `rules/` 底下會擋的規則,另派一個代理深查;DATA-37、FLOW-8、STATE-21 找到官方原文(都是官方建議的寫法,壞寫法是從建議推出來的),補上查證紀錄,規則照擋;API-14、TEST-31 仍找不到,這一批不標出處不全(一標就違反「出處不全只准提示級」、等於同時降級會擋的規則),留在「還沒逐列查證」的數字裡,降不降級交使用者裁(見〈待人裁〉)。
5. **接上數字**:`check.py` 新增 `catalog_unverified`,`--catalog-only` 與完整檢查的文字輸出都另印一行「還沒逐列查證 N 列」與前 20 個編號(`--json` 例外:維持純 JSON,這個數字不在 JSON 裡),不進問題清單、不改退出碼([[Projects/計劃依據來源必填_計劃]] S5 的實作,那條條款原本懸空等兩條分支合併)。
6. **統計節**:規則包等級條數、會擋規則守到的列數、出處不全列數照程式重算,另加一行逐列查證列數。

### 不做

- 不補已經有〔查證〕紀錄的 142 列(那批 2026-11-05 已查)。
- 不改〈待查證〉節的「待查」「未開頁核對」字樣:那一節由程式從原始欄位撈,改它要動撈法,另案。
- 不替 weak 的列自己找替代出處或改寫成「推論」。

## 待人裁

- **兩條會擋規則要不要降級**:API-14(`kt-async-await-immediately`)、TEST-31 用索引找節點那半(`kt-compose-test-node-by-index`)兩次查證都找不到官方原文。照「出處不全只准提示級」應降到 `rules-hints/`;降了之後消費專案這兩種寫法不再被擋,動到守衛面,所以拆出來等使用者裁定,裁定前規則照擋、型錄自檢的數字顯示這 2 列。
- **DATA-12**(updateData 裡做副作用或耗時 I/O):型錄寫「transform 只放純計算」,官方 `DataStore.updateData` 文件寫「the transform itself is a coroutine so it can perform heavy work such as RPCs」,兩者相反;情境決策表 D-42 早已標「無官方依據,見 notes 人裁」。這列沒有掛規則。建議改成取捨提醒(寫入排隊執行,transform 跑太久會讓後面的寫入一起等),等使用者裁定;裁定前不動這一列。

## 實務隱患

- **官方建議不是官方禁令**:verified 裡有不少列,官方原文只支持標準寫法,壞寫法的錯因或後果是推出來的(各列細節在卷證 JSON 的 note);標 verified 的口徑是「核心主張有官方原文、而且不相反」。
- **網頁會改**:查證紀錄綁日期;官方頁改版後原文可能不在。
- 已排除:金流:不碰付款
- 已排除:對外送出:查證時只讀公開網頁,型錄與規則包沒有對外呼叫
- 已排除:不可逆:改的是型錄文件與一支提醒函式,退提交即回原狀
- 已排除:守衛面:這一批不改任何擋停——規則包等級沒動,新的數字只另印一行、不進問題清單、不改退出碼;要降級的兩條拆到〈待人裁〉

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 每列要有打開讀過的官方出處、查不到標出處不全 | 使用者要求 | 使用者 2026-11-05:「你的標準、最佳寫法來源要有依據，不要你自己寫」 |
| 還沒逐列查證的數字只提醒、不改退出碼 | 計劃依據來源必填做法 6 與條款 S5 | `docs/lumos-toolchain-knowledge/Projects/計劃依據來源必填_計劃.md` |
| WebFetch 引句要抓原頁抽查 | 查證代理自己回報 WebFetch 回傳是摘要、不一定逐字;實測 20 列抽查 | 實測 2026-11-07:20 列抽查 17 列逐字、3 列字詞全中(卷證 all-results.json) |
| 三列相反照官方改 | 官方原文 | https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/with-context.html 、https://raw.githubusercontent.com/mrmans0n/compose-rules/main/docs/rules.md |

## 驗收條款

- [S1] 當型錄主表有一列來源欄只有縮寫或只有網址、沒有查證紀錄、名稱沒標出處不全時,型錄自檢 應 把它算進「還沒逐列查證」並另印一行;有查證紀錄或標了出處不全的列 應 不算;問題清單與退出碼 應 不因這個數字改變 [test:t_kt_catalog_unverified_rows]
- [S2] 當跑型錄自檢時,真實型錄 應 是 0 個問題、還沒逐列查證 2 列(API-14、TEST-31,待人裁) [manual:跑 python3.14 configs/ast-grep/kotlin-android/check.py --catalog-only 看最後兩行]

## 回退

退回本計劃的提交:型錄來源欄的〔查證 2026-11-07〕紀錄與出處不全標記拿掉、CO-27 與 UI-100 改回、`catalog_unverified` 與它的測試拿掉、統計節改回。卷證留著。

## 天花板

1. 查證是單家族模型做的,抽查只有 20 列加 6 列。
2. verified 的口徑是「核心主張有官方原文、不相反」,不是「每個細節都有原文」。

REVISIT:2026-12-07 看型錄自檢的「還沒逐列查證」有沒有因新增列而變多;API-14、TEST-31 與 DATA-12 的人裁有沒有結

## 審計修正紀錄

- 2026-11-07 實作:331 列查完(verified 312、weak 16、contradicted 3);二次深查 5 列救回 3 列;套回後型錄 459 列有查證紀錄,出處不全 34 列;API-14、TEST-31 的降級與 DATA-12 待人裁。卷證:governance/review-reports/android寫法型錄逐列查證/(12 批結果、二次深查、彙總)。
- 2026-11-07 推送前:提醒函式的正規式原本直接寫龜甲括號,ruff 判成可疑字元、新增告警讓代碼審分級升到高;改成 `\u3014`/`\u3015` 跳脫,行為不變(`t_kt_catalog_unverified_rows` 照綠)。
- 2026-11-07 代碼審 r1(2 席):4 條 minor/blocking 0/折 3 條半(節點數字、標記比對、完整路徑測試、函式位置),正規式跳脫附理由放行;卷證 governance/review-reports/code-android寫法型錄逐列查證/。
- 2026-11-07 代碼審 r2(2 席):2 條 minor/blocking 0/全折(計劃補 `--json` 例外並加測試守純 JSON、欄位取成具名變數);卷證同上。
- 2026-11-07 r3 之後:catalog_unverified 的說明文字也有龜甲括號、被新增告警閘抓到(RUF002),改成文字描述;只動說明文字,行為與測試不變。
