severity: major

## 範圍與方法
我讀完整份凍結審材,並對照工作樹 `scripts/lumos` 現況。風險詞的兩條新正規式和路徑樣式,我都用 python3.14 在 `re.I` 下實際跑過。實驗目錄已用字面路徑刪除。

## 1. 前端判準 `_FE_PLAN_WHEN` 會把只提到前端的後端計劃整份改成前端(做法 1、4、3)
severity: major
blocking: 是(照 spec 字面做,後端計劃的設計審鏡頭會被換掉,「判錯只是多列幾題」不成立)

- **spec 的說法**:做法 1 寫「判錯的代價是多列幾題,不擋任何東西」。做法 4 寫被審計劃是前端時「五個設計審鏡頭的立場照下表換成前端版措辭」,用的是換成,不是補上。
- **判準會誤判的例子**:判準收「前端」「瀏覽器」和 React / Vite 等字,只比全文有沒有出現一次。後端計劃寫「回傳欄位給前端用」「本期不碰前端」「Vite」,都會判成前端。
  - 我實測 `前端呼叫此 API`、`回傳欄位給前端`、`React to failures` 都命中。
  - 本 repo 的 274 份 `_計劃.md` 有 25 份命中(加 re.I 是 32 份),「前端」一詞就出現 96 次。
- **照 spec 會得到什麼**:一份「改 API、加 DB 欄位」的後端計劃只要提到一次「前端」,`pitfalls --check` 就多印「這份計劃是前端」。編排者照做法 4 把「回滾」鏡頭換成「使用者手上的舊 bundle」,把「資源併發」鏡頭換成「計時器、輪詢、卸載」。原本的遷移順序、連線池、鎖就沒人看了。混合型計劃(前端加後端 API)也一樣。
- **驗收缺口**:S2 只測「完全沒有前端字樣」的計劃。沒有任何條款釘「後端計劃只在敘述裡提到前端時,不印前端提醒、不換鏡頭」。
- 佐證:
引句:「被審計劃是前端(做法 1 的判準、`pitfalls --check` 印了前端提醒)時,五個設計審鏡頭的立場照下表換成前端版措辭」
file: `scripts/lumos:47671` 的 `_pitfalls_stage` 對計劃全文逐條做 `re.search(w, text)`,沒有權重或次數門檻。

## 2. infra 題的 when 預設會剝掉字串,引號裡的 /tmp/ 與 localhost:埠 比不到(做法 6)
severity: major
blocking: 是(infra-shared 的主要觸發寫法在 shell 裡多半寫在引號內,照 spec 做出來的題組對最常見寫法不亮)

- **spec 的說法**:做法 6 的 `_STACK_QUESTION_SPECS` 形狀只有 id/q/when。
- **現況**:file: `scripts/lumos:30502` 的 `_stack_norm_line` 在 `when` 比對前,先用 `_strip_string_literals` 把字串字面挖空,只有題目另寫的 `when_raw` 才看字串內容。
- **失敗場景**:新增行是 `LOCK_FILE="/tmp/e2e.lock"`、`PIDFILE="/tmp/e2e.pid"` 或 `curl "http://localhost:3000/health"`。剝字串後變成 `LOCK_FILE=""`,`/tmp/` 與 `localhost:數字` 都比不到,infra-shared 不亮。而這正是示範事故「/tmp 鎖與狀態檔」的寫法。
- **S12 的限制**:S12 的測試行寫成 `kill "$pid"` 加 `/tmp/`,若 `/tmp/` 沒放在引號裡就會綠。照字面寫出來的測試過得了,但擋不到真實寫法。
- **spec 缺的條款**:沒有說 `/tmp/`、`localhost:數字`、`--name` 該放 `when_raw`,也沒有引號裡的寫法的驗收條款。

## 3. PAYMENT 例外的實際範圍比 WHY 寫的寬(做法 9)
severity: minor
blocking: 否(d1 是使用者裁定,而且 RETIRE-IF 已留撤回口;這裡只是範圍沒寫清楚)

- **spec 的說法**:WHY 說「例外只收 payment 一字」並「收窄到量得到的範圍」。
- **實測**:正規式把所有緊貼底線的全大寫 PAYMENT 都放掉,下面這些我都跑過,全部不命中:
  - `PAYMENT_GATEWAY_URL`
  - `PAYMENT_API_KEY`
  - `PAYMENT_SECRET`
  - `ENABLE_PAYMENT`(金流開關)
  - `MY_PAYMENT_ENABLED`
- **失敗場景**:計劃只寫「新增環境變數 `PAYMENT_GATEWAY_URL`、`PAYMENT_API_KEY` 串接新金流商」,沒有「金流」二字。詞表也沒有「付款」(現行 payment 類是 金流、payment、stripe、billing、退款、refund、扣款),所以這行以前判金流、現在判風險低。
- **驗收缺口**:S25 只釘 `STRIPE_SECRET_KEY` 仍命中,那個詞靠 stripe 命中,跟 PAYMENT 例外無關。沒有條款釘 `PAYMENT_API_KEY` 或 `ENABLE_PAYMENT`。〈實務隱患〉的天花板也只寫了「送出」那一條。

## 4. 送出的去處只認緊貼的給/到/至/往,「資料」「內容」「後」隔一個詞就漏(做法 9)
severity: minor
blocking: 否(實務隱患已承認「隔了別的字」是天花板,但舉的例子只有一種形狀,漏的形狀更常見)

我實測下面這些都不命中,舊版會命中:
- 「使用者送出表單資料給第三方」
- 「送出表單內容至客服信箱」
- 「表單送出後通知客戶」(`notify` 只收英文,「通知」不在詞表)
- 「送出請求後將資料同步到 ERP」
- 「送出請求的結果寄給客戶」

這幾句的去處都在同一行,只是不緊貼。spec 否決「同一句有『到』就照算」的理由是「收到」誤中。這裡可以只在「送出」後面幾字內找給/至/往,不含到,但 spec 沒討論。S21 到 S22 只釘緊貼的形狀。0 份改判的量測只代表現有 356 份計劃,不代表這類寫法。

## 5. 測試路徑樣式會把產品程式的 e2e 加密模組判成 infra(做法 7)
severity: minor
blocking: 否(出現機率低,但會讓一支產品檔同時失去棧別題與代碼型樣掃描)

- `_TEST_INFRA_PATH_RE` 只看檔名,不分副檔名。`src/crypto/e2e.ts`、`lib/e2e_encryption.py`、`src/e2e.py` 實測都命中。
- e2e 在聊天、通訊類專案常指端對端加密(end-to-end encryption)。這種產品程式檔會被判成 infra:不再走 py / node 棧別題,代碼型樣也跳過,分級可能因此降低。
- 〈實務隱患〉只討論了 `seeds/`(維運腳本放進去)的風險,沒提 e2e 字樣會撞到 E2EE。

## 已讀,無 finding
- **做法 2、3(前端面各列)**:除了 finding 1 的判準,各列本身無誤。
- **做法 5(資安席八項)**:無 finding。
- **做法 8(測試品質前端節)**:無 finding。
- **測試名與釘住值**:S27(版本 13、判法維持 8)與現況 `_DOOR_RULE_VERSION=12`、`_DOOR_SCAN_LOGIC_VERSION=8` 一致。
- **新正規式本身**:`(?-i:…)` 在 `re.I` 下編譯得過、行為如 spec 所述。lookbehind 的各分支等寬。
- **S18 到 S24**:我逐條實測,結果都符合。

## 風險類
- **守衛面**:見 1、3、4、5。
- **舊帳相容**:無新增 finding,門規則版本升 13 讓舊留痕重數,是既有規矩。
- **在途分支**:無新增 finding。
- **跨計劃交界**:無新增 finding,`_stack_key_for_file` 的順序 spec 已寫明。

最嚴重 severity:major,blocking 共 2 條(finding 1、2)。
