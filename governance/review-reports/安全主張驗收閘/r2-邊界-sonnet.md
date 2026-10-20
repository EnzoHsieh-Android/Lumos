severity: major

審查席:邊界-sonnet(第 2 輪)。報告裡的 finding 1 到 6 是 blocking,7 到 13 是 minor。主要的洞有三類:簽章能被重放、空輸入會讓護欄空洞通過、起點判斷會在本機缺 ref 時放寬。

## 已讀,無 finding
- 〈承接對照〉、〈六〉上線順序、〈回退〉:已讀,無 finding。
- pre-push 刪除遠端 ref:現況 `scripts/hooks/pre-push` 在 code-loop 前就對 `local_sha` 全零 `continue`。新增的 `--security-only` 不會誤擋 tag 或分支刪除,不報。

## Findings

### 1. 威脅類別為空陣列或全是未知 id 時,護欄空洞地判 sound
- spec 段落:〈一〉彙總規則、〈二〉最低種類怎麼算
- 問題:`threat_categories_missing` 只對「沒宣告」。宣告了 `[]`,或只寫了表裡沒有的 id,最低種類聯集算出來是空集合,彙總規則 2「每個必要種類都 qualified → sound」對空集合也成立。
- 具體例:一條 active 的 security 護欄寫 `threat_categories: ["typo_cat"]`、`required_evidence: []`。
  - 預期:unsound。
  - 照 spec:聯集為空,整體判 sound,閘放行,零證據。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Projects/資安風險提問分階段_計劃.md:148,219`。未知類別只進 `cell_errors` 的 `unknown_category`,「閘門不讀 `cell_errors`」。
  - 沒有任何 S 條款覆蓋這個輸入。

引句:「每個必要種類（含 review）都是 qualified → sound」

severity: major
blocking: 是
判準:照字面實作會讓零證據的護欄通過,守衛面被放寬。

### 2. 簽章沒有重放防護,四種簽過的東西可以從 git 歷史搬回來
- spec 段落:〈四〉擋或只提醒的設定、核可修訂紀錄、公鑰清單本身的修改
- 問題:內容簽章只證明「這份內容曾被簽過」,沒有到期日,也沒綁當前狀態。AI 可以從歷史撈舊簽章貼回去。
  - gate warn:簽的內容是 `{"type":"gate_setting","value":"warn","approved_on":…}`,沒有 `expires_on`,也沒綁專案。
    - 使用者簽 warn 當過渡期、之後移除,AI 把舊 warn 區塊貼回,簽章仍有效,整道閘被關。
    - 同一把金鑰釘在多個專案時,A 專案的 warn 簽章也能貼進 B 專案。
  - 修訂紀錄:只有 `approved_on`,沒有到期。使用者核可刪除某護欄、護欄之後用同樣內容重建,AI 再刪一次,舊紀錄照樣有效。
  - `.lumos/security-approvers.sig`:簽的只是新清單全文,沒綁 merge-base 清單。
    - 使用者先簽 L0 變 L1(加 K1),之後簽 L1 變 L2(撤銷外洩的 K1)。
    - AI 用 L1 加舊 `.sig` 推上去,merge-base 版清單 L2 裡的 K0 驗得過,被撤銷的 K1 復活。
  - 例外有 `expires_on` 和 `approved_on`,不受影響。
- 具體例(gate):使用者簽 warn 試行,收尾時刪掉 `security_evidence.gate`,AI 之後把當時整個區塊貼回。預期:當成 block。照 spec:簽章對得上 merge-base 版金鑰,warn 生效。
- 佐證:
  - 〈四〉那句「刪了只會少一筆可用的核可，不會放寬」只對「刪掉」成立,對「再貼回來」不成立。
  - S45、S26、S29 的樣本都沒有重放案例。

引句:「舊紀錄可以直接刪，刪了只會少一筆可用的核可，不會放寬。」

severity: major
blocking: 是
判準:照字面實作,d7「AI 不能自己放自己」可被歷史簽章繞過,漏掉合約。

### 3. 人審紀錄的簽章沒蓋 `kind` 和 bindings,簽了仍可改
- spec 段落:〈二〉機械做不到的判斷,「審查人種類(d8)」
- 問題:人審簽的內容是護欄 id、revision、判定輸入雜湊、`judgments`、`reviewer`、`expires_on`。不含 `kind`(review 或 deployment)、`bindings`、`author`、`observed_at`。
- 具體例 A(bindings):
  - 使用者人審並簽名時,實作是 blob X。
  - AI 之後改實作成 Y,把紀錄的 `bindings` 改成 Y 的 blob,簽章仍驗得過(revision 和判定輸入沒變)。
  - 預期(d2):綁定的程式一變就要重審。
  - 照 spec:review 判 qualified。
- 具體例 B(kind):
  - 把一筆人簽的 review 紀錄複製一份,`kind` 改成 `deployment`。
  - 簽章驗得過,deployment「一律要人」被滿足,但人從沒審過 deployment。
- 佐證:〈二〉的「綁定的程式與護欄 revision 等於要推的提交，一變判 stale」比對的是紀錄裡自填的 `bindings`,而它不在簽章內。

引句:「紀錄綁版本，綁定的程式或護欄修訂一變就要重審」

severity: major
blocking: 是
判準:照字面實作會讓人審簽章在程式換掉後仍放行,漏掉 d2 的版本綁定合約。

### 4. 「預設分支還不存在」沒定義怎麼判,本機看不到 ref 會變成 fail-open
- spec 段落:〈四〉起點一律是 merge-base
- 問題:spec 沒說「預設分支不存在」靠什麼判,也沒說預設分支名從哪取(`origin/HEAD`?config?)。
  - 如果只看本機的 `origin/<預設分支>` 追蹤 ref,以下情況都會落到「起點＝空樹，所有護欄當成新增」:
    - `git clone --single-branch --branch feature`。
    - 預設分支叫 `master` 或遠端不叫 origin。
    - 追蹤 ref 被刪。
  - 這時凍結比對整個失效,刪護欄、改弱判定輸入都不算變弱。
  - 這跟同節「判不清不放行」相反。
- 具體例:
  - 本機只有 `refs/remotes/origin/feature`,遠端 main 其實存在且有 10 條 active 護欄。
  - 推送的提交刪掉其中 5 條。
  - 預期:5 條 `control_removed_unapproved`。
  - 照 spec:起點是空樹,5 條被當成沒存在過,放行。
- 佐證:spec 只列了三個起點判法(空樹、`freeze_base_unavailable`、`shallow_clone`),沒區分「不存在」與「本機看不到」,也沒說要不要用 `git ls-remote`。

引句:「預設分支還不存在（新 repo 的第一次推送，根提交就帶登記）：起點＝空樹，所有護欄當成新增照判。」

severity: major
blocking: 是
判準:照字面實作會在追蹤 ref 缺失時靜默放寬凍結比對,守衛面放寬。

### 5. `evidence_refs` 的「換掉」沒定義列的身分,重新驗證會變成每次都要簽修訂
- spec 段落:〈四〉判定輸入也凍結
- 問題:`evidence_refs` 的列是 (kind, node)(file: `docs/lumos-toolchain-knowledge/Projects/資安護欄唯讀盤點_計劃.md:86`)。
  - 重新收證通常是新開一篇 Verification 節點,舊的標 stale 或 superseded,所以 `evidence_refs` 的 node 被換掉,判為變弱。
  - 沒有簽章修訂紀錄就用聯集判,新舊兩份都要 qualified。
  - 舊節點的綁定一定已過期,判 `stale:verification_node_stale`,這條護欄就永遠 unsound。
- 具體例:
  - OD-01 有 `{kind: behavior, node: Verification/A}`。
  - 實作改了,重跑測試,新開 Verification/B,evidence_refs 改指 B。
  - 預期:B 合格就放行。
  - 照 spec:A 被換掉算變弱,聯集要求 A 也合格,A 是 stale,被擋。使用者得為每次正常重驗簽一筆修訂。
- 佐證:〈四〉只有「只新增不刪除不算變弱」,「新增 B 並移除舊的 A」沒有例外。S31 只測「被換掉」要走聯集,沒有「換成更新的證據」這個正常樣本。

引句:「變弱而沒有核可修訂紀錄時，用新舊兩版的聯集判」

severity: major
blocking: 是
判準:照字面實作會讓正常的證據更新永遠被擋,做出無法用的系統。

### 6. SARIF 的「未處置的命中」沒定義,實作者要自己決定,容易讓 AI 自行處置
- spec 段落:〈二〉每種格式的合格判定,SARIF 列;S11、S12
- 問題:spec 沒定義三件事。
  - 什麼算「命中」:`level` 是 note、warning、error 哪些?`kind: pass`/`fail`/`notApplicable` 怎麼算?
  - 什麼算「處置」:是 SARIF `suppressions`、baselineState,還是 in-source 的 `nosemgrep`/`# nosec`?
  - 誰能處置:AI 自己加抑制註解再重跑掃描,結果 `suppressions` 有值。
- 具體例:AI 在程式碼加 `# nosec` 後重掃,SARIF 該 result 帶 `suppressions[{kind:inSource}]`。實作者若把有 suppression 的當「已處置」,就是 qualified。預期:應該要有人的核可;spec 沒說。
- S12 的 manual 樣本只列 results null、invocation 失敗、通知 error、覆蓋證明缺,沒有 suppressions、level 分層的樣本,條款寫不成測試。

引句:「對宣告規則沒有未處置的命中」

severity: major
blocking: 是
判準:這個詞決定 failed 與 qualified 的分界,兩種實作都合字面但行為相反,實作者會做錯決定。

### 7. `approved_on` 取 UTC 日期,台灣清晨簽的例外會有 8 小時無效
- spec 段落:〈四〉30 天怎麼算,S23、S25
- 問題:規則是「`approved_on` 晚於今天（UTC）無效」。`security payload` 沒說 `approved_on` 填 UTC 日期還是本地日期。台灣 00:00 到 08:00 簽,本地日期比 UTC 大一天;若 payload 用本地日期,例外在這 8 小時內判核可日在未來,無效。
- S23 的五種壞例外沒有「核可日在未來」。S25 只測到期判定,沒測核可日。這個規則缺測試。

引句:「到期日減核可日恰為 30 天的有效例外應放行」

severity: minor
blocking: 否
判準:最壞是例外多等 8 小時才生效,不會做出壞系統,但缺條款。

### 8. spec 對 `junit()` 現況的描述與程式不符,一個不相關的 error 會讓整份報告 invalid
- spec 段落:〈二〉JUnit 列、「同次判定快取:一份專案級 JUnit 被一千條護欄引用」
- 問題:spec 寫「拒 suite 層 error」。實際 `scripts/test_quality.py` 的 `junit()` 對整份檔案任何 `<error>` 元素都 `raise ValueError('runner/suite errors')`,包含不相關測試的 error。同名測試也整份拒:`duplicate test identities`。
- 實跑:
  - 兩個 testcase 中一個帶 `<error>`,`junit()` 拋 `runner/suite errors`。
  - 兩個同 classname 同 name 的 testcase,拋 `duplicate test identities`。
- 結果:
  - 專案級 JUnit 只要有一個無關測試 error,所有引用它的護欄都判 invalid。
  - `junit()` 的報錯是英文字串,spec 要對映成 `suite_error`、`zero_cases`、`count_mismatch` 等代碼,這個對映沒說。
  - 這是 fail-closed,不會放行壞東西。

引句:「拒重複身份、拒零案例、拒 suite 層 error」

severity: minor
blocking: 否
判準:實作者會發現並自己處理,最壞是過度擋下,不會放寬。

### 9. `unexpected_empty` 與 `control_removed_unapproved` 重疊,S3 的預期代碼不明
- spec 段落:〈四〉必驗集合、擋下條件「必驗集合意外為空」、S3
- 問題:必驗集合的定義已經把 merge-base 版被刪的條目加回來。所以「merge-base 版非空、要推的版全空、沒有核可修訂」時,必驗集合不會是空的,每條都已判 `control_removed_unapproved`。`unexpected_empty` 這條條件走不到,或和前者同時成立。
- S3 的樣本「全部條目被刪」沒說預期印哪個代碼。

引句:「而 merge-base 版的必驗集合不是空的、這中間又沒有把它們全部移出的核可修訂紀錄」

severity: minor
blocking: 否
判準:兩個代碼都擋,行為相同,只是測試預期和訊息文字不明。

### 10. 「本機與 CI 永遠同一個答案」在 UTC 午夜跨日時不成立
- spec 段落:〈一〉彙總規則的結尾、S28
- 問題:例外到期、`review_expired`、`vulndb_stale` 都依「今天(UTC)」。台灣 07:55 本機推送通過(UTC 前一天 23:55),CI 在 08:05 跑,例外已隔天過期,CI 判擋。
- 後果:CI 在 main 更新後才紅(d9 已承認紅燈收不回)。
- S25 的台灣清晨樣本只驗閘本身的 UTC 取法,沒驗「本機放行後 CI 在跨日後重判」。

引句:「所以本機與 CI 也是同一個答案」

severity: minor
blocking: 否
判準:只影響午夜前後的推送,寫進天花板就能說清,不會做出壞系統。

### 11. 資源上限的總量條款少了測試樣本和順序
- spec 段落:〈二〉讀不可信資料的上限、S41
- 問題:
  - S41 條款寫「單一證據檔超過 16 MiB 或一次判定的證據總量超過 256 MiB」,manual 樣本只有 17 MiB 單檔,沒有 256 MiB 總量的樣本。
  - 總量超過後「超過之後的每一項」判 `evidence_too_large`,依哪個順序累計沒說(護欄順序?路徑排序?)。順序不固定時,`security evidence` 與閘門對同一提交可能判出不同的幾項。
  - 證據項總數上限 10000 超過時怎麼判沒有寫。

引句:「一份 17 MiB 合成 SARIF 與一份小 JUnit 同庫」

severity: minor
blocking: 否
判準:實作者會自行選順序並可通過 S41 的單檔樣本,只缺總量的可測性。

### 12. 簽章人身分、日期比較、未來時間三個小洞
- spec 段落:〈四〉驗、〈二〉review 與 vulndb
- 問題:
  - `ssh-keygen -Y verify` 需要 `-I <簽章人>`,但核可物件表沒有存簽章人的欄位,payload 也沒有。實作者要自行決定(或改用 find-principals)。
  - `expires_on`(日期)與 `observed_at + 90 天`(含時區的時間)比較,怎麼換成 UTC 日期、剛好 90 天算不算超過,沒說。S39 只測「太遠」。
  - `vulndb_fetched_at` 沒有「不晚於 `observed_at`」的檢查,只有 `observed_at` 有 `observed_in_future`。填未來日期永遠不會 stale。
  - 這三項都靠作者自填,不是新攻擊面,但邊界沒寫。

引句:「晚於要推的提交的提交時間判 `invalid:observed_in_future`」

severity: minor
blocking: 否
判準:實作者可自行補,錯了影響很小。

### 13. k6 REVISIT 的實測結果,以及請求數下限的對象不一致
- spec 段落:〈二〉k6 的坑、k6 summary 列
- 實測(k6 v2.3.0,`--new-machine-readable-summary`):
  - 從沒呼叫過的自訂 Counter 在 `results.metrics` 裡不出現。
  - `add(0)` 過的 Counter 出現,`values.count` 是 0。所以「先 `add(0)`」的前提成立,REVISIT 那題可以用這個結果收掉。
  - `config.script` 與檔案位元組相等(含 CRLF、BOM),腳本雜湊比對可行。
  - 摘要只記主腳本全文,import 進來的模組不在內,要靠 bindings 涵蓋。
- 請求數下限的對象不一致:
  - 表格寫「請求數不少於工具清單登記的下限」,指整體請求數。
  - 〈三〉k6 範例卻拿 `foreign_rejected` 不少於下限來判。兩者數字不同(整體含合法流量),實作者要選一個,選錯會讓下限形同虛設。

引句:「請求數不少於工具清單登記的下限」

severity: minor
blocking: 否
判準:修一個詞就能對齊,不會做出壞系統,但要在實作前說清楚。

最嚴重 severity:major,blocking 共 6 條。

本席建的臨時目錄 `/private/tmp/claude-501/secgate-r2-邊界-sonnet` 已刪除。
