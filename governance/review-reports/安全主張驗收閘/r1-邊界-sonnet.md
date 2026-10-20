severity: major

設計審 邊界-sonnet,凍結審材 `r1-snapshot.md`(LUMOS-SPEC 9f4f47f6)。審材共 491 行,我讀完全文與 `r1-intake.md`。

查證過的現況有兩點。第一,CI 三個 job 的 checkout 都是 `fetch-depth: 0`(`.github/workflows/ci.yml:30,105,158`),所以簽章核對用得到母提交與 blame,淺複製不成問題。第二,審材 S1 到 S30 沒有任何一條碰到 review 獨立性或過期、`evidence_fence_invalid`、`vulndb_stale`、`unsupported_format`、治理帳資安背書(`backing_missing`)。這是用 grep 對這些代碼和 S 條款交叉比對得出的。

### F1 `targets` 給空陣列時,合格條件空洞成立
- 位置:〈二〉鍵名與必填表的 `targets` 列,加上「每種格式的合格判定」的 JUnit、SARIF、k6 三列。
- 引句:「用不到的鍵省略,該種類要的鍵缺了判 invalid」
- 問題:只規定「鍵缺了」判 invalid,沒規定「鍵在但為空陣列」。JUnit 的 qualified 條件是「宣告的非法案例與合法對照案例都在、都 passed」。SARIF 是「對宣告規則沒有未處置的命中」。k6 是「安全門檻全過」。這三句對空集合都是空洞為真。
- 具體例:behavior 證據的 `tests:[]`、`legit_controls:[]`、`preconditions:[]`,報告是任一個通過的無關測試。全域「案例數大於 0」成立,宣告的目標零個,沒有一個缺席或失敗,結果判 qualified。S6 只寫「沒有宣告或找不到」,沒涵蓋「宣告了空陣列」。`rules:[]`、`thresholds:[]`、`recipe_ids:[]` 同理。
- 這正是「為了合格而合格」的最短路徑,作者連最低要求都不用寫。
severity: major
- blocking: 是(照字面實作會做出可被空陣列繞過的 qualified)。

### F2 d2 與數個新代碼沒有任何驗收條款
- 位置:〈五〉S1 到 S30 對照〈原因代碼〉表和〈機械做不到的判斷〉。
- 引句:「缺紀錄判 `missing:review_record_missing`,綁定一變判 `stale`,過期判 `stale:review_expired`,`reviewer` 等於 `author` 判 `invalid:review_not_independent`」
- 問題:review 的四種判法是使用者已裁的 d2,卻沒有 S 條款綁測試。只有 S8 測「缺 review 證據」。下列代碼同樣沒有條款:`review_not_independent`、`review_expired`、`evidence_fence_invalid`(新的嚴格圍欄解析,全篇最容易出錯處之一)、`vulndb_stale`、`unsupported_format`、`backing_missing` 與整條「本機算資安背書寫進治理帳」的新路徑。revisions 紀錄的簽章要求只在 S26 的例外列樣本裡出現,S29 的「有完整核可修訂紀錄」樣本沒有未簽的對照。
- 具體例:實作者把 `reviewer == author` 漏掉,所有 S 條款仍可全綠,d2 的唯一機械內容無人守。
- 這等於 spec 的條款集合與自己的代碼表不對齊。
severity: major
- blocking: 是(漏掉合約,實作者不會知道哪些要寫測試)。

### F3 簽章會被 rebase、squash、merge 弄丟,spec 沒規定哪個提交算數
- 位置:〈四〉「例外核准用簽章金鑰」的「找出要驗的提交」與「驗章」。
- 引句:「在要推的提交上用 `git blame --porcelain` 找出最後改到那幾行的每個提交。」
- 問題:本專案規則是做到一半的本機提交推前壓成一個(專案 CLAUDE.md〈提交與推送〉)。squash、rebase、cherry-pick 或 PR 合併都會重寫提交,原簽章消失,新提交由重寫者簽或不簽。
- 具體例:使用者簽了含例外列的提交,AI 隨後 rebase 或 squash,blame 指到未簽或 GitHub web-flow 簽的提交,例外判 `exception_unsigned`。CI 在 main 的 push 事件跑,PR 以 squash 合入後,原本本機放行的例外在 main 上被判無效,這就是「本機放行、CI 擋」,與「完全相同」的宣稱矛盾。
- 另一個缺口:合併提交有兩個母提交,「母提交那一版清單」取哪個,spec 沒寫。
- S26 的四份樣本全是線性單母提交歷史,沒涵蓋這些。
severity: major
- blocking: 是(實作者必須自己決定重寫歷史與合併提交的行為,而這決定會讓例外功能在本專案慣用流程下失效或被誤判)。

### F4 到期當天、30 天整的語意沒定義,S25 的「當天」寫不成測試
- 位置:〈四〉例外核可與記帳,以及 S23、S25。
- 引句:「到期日減核可日超過 30 天、或核可日晚於今天,例外無效。」
- 問題:「超過 30 天」表示恰好 30 天有效,但 S23 的樣本只有「超過」,沒有 30 與 31 的邊界對。S25 要測「到期前、當天、隔天」三點,可是 `expires_on` 當天算不算有效,全文沒說。
- 「今天」用哪個時區也沒說:`observed_at` 要求含時區,`expires_on` 與核可日卻是純日期。台灣本機與 UTC 的 CI 在每天 8 小時內對「今天」不同日,S28 宣稱的「完全相同」在日界附近不成立,除非日期是注入的。
- 具體例:`expires_on` 為 11-01,本機 11-01 02:00(台灣)與 CI 的 UTC 日期 10-31,兩邊判定不同。
severity: major
- blocking: 是(S25 當天那點照字面寫不出斷言;跨時區閘會在日界不一致)。

### F5 `vulndb_stale` 有代碼、無門檻、無法算齡
- 位置:〈二〉「依賴掃描結果跟著漏洞庫變」,以及 Q5(待人)、`vulndb` 鍵。
- 引句:「超過多少天算 stale 待使用者裁(Q5,建議 14 天)。」
- 問題:代碼表已含 `vulndb_stale`,但門檻未裁。`vulndb` 欄位又是「漏洞庫版本或抓取時間」二選一的自由字串,版本號沒有時間,算不出幾天。
- 具體例:`vulndb: "v2026.10.1"` 或 `"2026-10-10T00:00Z"`,閘無從判。邊界「剛好 14 天整」也沒定。
- 這一項無法照字面實作,也沒有條款(見 F2)。
severity: major
- blocking: 是(實作者得自己編門檻與格式)。

### F6 review_record 的邊界:到期日無上限、身分比對未規範、紀錄本身無簽章
- 位置:〈二〉鍵名表的 `reviewer`、`author`、`expires_on`。
- 問題一:`expires_on` 沒有最長期限。例外有 30 天上限,review 可以寫 2099 年。
- 問題二:`reviewer` 等於 `author` 沒說明比對方式。「Enzo」與「enzo 」、「claude」與「Claude」是否算同一人,spec 未規定。`author` 是單一字串,多作者的被審內容怎麼寫也沒定。
- 問題三:⚠ 交編排者。review_record 寫在 Verification 圍欄裡,AI 可寫,沒有 d6 的簽章保護。AI 寫 `reviewer:"X", author:"claude", expires_on:"2099-01-01"` 就能讓 review 種類永遠 qualified。spec 承認「審查人身分只核欄位」,但這讓 d2 的閘形同虛設。這一點超出本席鏡頭,是否要把 review_record 也納入簽章要求,請編排者與資安席定奪。
severity: minor
- blocking: 否(問題一二是補欄位規範;問題三需裁示,不在本席判斷範圍)。

### F7 證據檔過大時的行為未定,且沒有對應代碼
- 位置:〈實務隱患〉資源一段。
- 引句:「沿用盤點的單檔與總量上限,超限判讀取不完整並擋。」
- 問題:盤點的上限是為筆記設計的,SARIF 與依賴掃描輸出遠大於筆記。超限判「讀取不完整」是整道擋(〈四〉擋下條件),不是單條 invalid,所以一份大 SARIF 會讓整個專案所有推送被擋。代碼表沒有 `evidence_too_large` 類的單條代碼。「1000 條護欄、每條 10 份證據」的量測是「實作時再定上限」,沒有可驗收的數字。
- 具體例:Semgrep 對大專案的 SARIF 超過單檔上限,整個推送被擋,訊息卻看不出是哪份證據。
severity: minor
- blocking: 否(可在實作時補,但實作者要先決定單條還是整道)。

### F8 k6 計數器為零時指標可能不出現在摘要裡
- 位置:〈三〉「k6 第一個接」與〈二〉k6 列的 `k6_metric_missing`。
- 引句:「宣告的安全指標不在結果裡」
- 問題:⚠ 我未實跑 k6,依我對 k6 的了解,自訂 Counter 從未被呼叫時不會出現在摘要。若成立,最理想的結果(`foreign_effects` 等於 0,從未被加過)反而被判 `k6_metric_missing`。spec 沒要求腳本對該指標做 `add(0)`。「請求數下限」也由作者宣告,下限寫 1 即可過,spec 沒有最小下限。
- 建議編排者在 order-demo 的 k6 v2.3.0 上實測一次再定。
severity: minor
- blocking: 否(實作時會自己踩到,但在 order-demo 首案之前應先釐清)。

### F9 凍結起點取「遠端舊值」時,多次推送可逐步縮小必驗集合
- 位置:〈四〉「必驗集合以 merge-base 版為底」的起點。
- 引句:「有給 diff 範圍時用範圍起點(CI 的 before、pre-push 的遠端舊值」
- 問題:起點是上次推送的位置,不是分支的 merge-base。若某個縮小必驗集合的提交曾在閘未生效或被繞過時推上遠端,之後每次推送的起點版都已經沒有那條護欄,縮小永遠不會被偵測。母計劃 G1 要的是「凍結」,這裡凍的是上次推送而非基準版。
- 威脅模型是單人且 AI 依序操作,繞過需要閘不在或 `--no-verify`。上線順序第 1、2 步的過渡期就是這種情況。
severity: minor
- blocking: 否(窗口僅在閘上線前後,但至少要在回頭條件裡寫明)。

### 其他節
- 〈一〉區隔、〈三〉工具接入、〈世界解與採用判斷〉:已讀,無 finding。
- 〈回退〉:已讀,無 finding。

### 風險類逐類
- 守衛面:有 F1、F3、F4 三處會讓放行或擋下與意圖不符。
- 舊資料與舊帳:`schema v2` 的 candidate 與只有 candidate 的專案在〈四〉已有處理,我未發現邊界洞。
- 已在途分支:見 F9。
- 與其他會談或計劃的交界:`t_prepush_cl_reason_sentences_match_plan` 的四句改五句,spec 已寫清楚,無 finding。

### 對自動附加節點的判斷
- 《Systems/test-quality-cli》(家,`scripts/test_quality.py`):spec 說「JUnit 沿用 junit()」、test-quality 閘門要把 `check()` 核對本體抽成只吃資料的函式。這是對家節點的修改,不破壞宣稱的行為,前提是抽出前後既有測試照綠,spec 已有此要求。不影響。
- 《Systems/lumos-cli-lifecycle》的 ★INVARIANT★(re-inject 只覆蓋 sentinel 之間 body):本計劃不碰 re-inject 與 CLAUDE.md 注入,只改 `code-loop check`、`security evidence`、pre-push 對照表與 `lumos update` 的版本說明。不影響。
- 《Verification/測試品質第四輪修補驗證》:spec 沿用 `load_receipt` 與三階段核對,不改其語意。不影響。

最嚴重 severity:major。blocking 共 5 條(F1、F2、F3、F4、F5)。
