severity: major

做完了。全程只讀,沒改任何東西,暫存的探針目錄已刪。被審材料第一處就有一個我實際跑過會撞牆的衝突(第 3 問第 1 條)。

## 第 1 問 分層與依賴方向:大致對齊,有一處沒寫清楚

對齊的部分有三處:
- 推送前檢查只讀兩本帳,不碰 Gradle 報告。這跟鄰居 `_spec_gate_push_scan` 一致(`scripts/lumos:16248`),沒有跨層直呼。
- 讀報告的動作放在規格閘跑完測試那一端。簽核指令只寫治理帳,不改審查帳。
- 借 `_secev_junit_facts` 有先例:Android 端到端驗收的 `_e2e_junit_ok` 也直接呼叫它(`scripts/lumos:41777`)。

沒寫清楚的地方是「紅因」要加在哪一層。設計沒指明位置。`_spec_gate_judge_items`(`scripts/lumos:15105`)是規格閘、相依回歸、推送前重跑、修正關卡共用的。如果把紅因判讀加在裡面,生效日的判斷拿不到計劃資訊,還會連帶改到那幾個呼叫端的判定。鄰居的做法是在 `cmd_spec_gate` 跑完後,對逐支列另外加工(`_redbase_collect`,`scripts/lumos:14306`)。這條列在第 11 條。

## 第 2 問 命名與錯誤處理:結構對,細節不一致(見第 8、9、10 條)

- 欄位名 `clause_verdicts`(蛇形、單數語意)跟留痕鄰居 `n_red`、`clause_sha`、`redbase_skipped` 同調,沒問題。
- 擋下訊息把「寫死風險低」改成照計劃風險講,設計自己有提到,也是對的。
- 其餘要補的細節:閘名與 kind 的取法、事件裡「誰簽的」的欄位名、寫帳失敗怎麼辦、擋下事件的 kind、`clause_verdicts` 裡測試的身分格式。

## 第 3 問 第二種做法:有三處,另有數處待釘

1. **預期值表的格式跟條款定義語法打架**
   - 表列第一格寫 `[S2]`,會被現有條款解析當成「第二次定義 [S2]」。
   - 我用 `clause_bindings` 實測:驗收條款有 `[S2]` 加表裡兩列 `| [S2] |`,結果 S2 變成 `duplicate`,`dup_lines=[4,10,11]`。
   - `duplicate` 會讓規格閘擋下(`scripts/lumos:13806`)。「一條可有多列」一定觸發,只寫一列也會因為跟驗收條款那行重複而觸發。
   - 這等於讓行首 `[SN]` 有兩種意思:專案裡是「定義」,設計裡的表是「引用」。
   - 引句:「條款欄寫條款編號(例 `[S3]`),一條可有多列。」
   - file: `scripts/lumos:13703`(`_CLAUSE_LEAD_RE` 的前綴字元類含 `|`)
   - file: `scripts/lumos:14843`(重複定義判法)
severity: major
   - blocking: 是

2. **「首筆規格閘留痕」是第二套不回溯基準**
   - 專案既有的基準是 `_loop_first_ts_key`(`scripts/lumos:14975`)。它取審查帳裡這條迴圈第一筆非結局帳(任何 kind),跟 `_SPEC_GATE_SINCE` 比(用法在 `scripts/lumos:14999`)。
   - 設計改成「最早一筆 kind=spec-gate」。同一個函式裡,句式與回退節看「首筆帳」,新增的紅因、先紅、預期值表看「首筆規格閘留痕」。
   - 同一份計劃在設計審階段就有帳、規格閘留痕卻在生效日之後,兩套基準會判出不同結果。設計沒說為什麼不能直接用 `_loop_first_ts_key`。
   - 附帶:常數寫法鄰居有兩種,完整時間戳含時區(`scripts/lumos:13714`)和純日期(`_NOTE_LINT_PLAN_SINCE`,`scripts/lumos:12694`)。設計只說「寫成程式常數」,沒指定哪一種。
   - 引句:「首筆規格閘留痕:審查帳裡這份計劃的迴圈編號最早的一筆規格閘留痕(kind=spec-gate)。」
severity: major
   - blocking: 是

3. **推送前找紅的證據,只讀審查帳、而且要掃全部留痕,跟鄰居讀法不同**
   - 鄰居用「兩本帳合併、同迴圈取 ts 最晚一筆」,也就是 `_spec_gate_latest_merged`(`scripts/lumos:15519`),`_spec_gate_push_scan` 還特別在 live 候選時載入治理帳(`scripts/lumos:16248` 起)。理由寫在 B3:消費專案的審查帳被 gitignore,乾淨 clone 只有治理帳。
   - 設計寫「只讀審查帳」,又要掃「所有留痕」。這是第二種讀規格閘留痕的方式。
   - 在 gitignore 審查帳的專案,先紅的證據永遠找不到,會誤擋。設計自己的天花板二只提到 CI 讀不到,沒提這個。
   - 引句:「在審查帳這份計劃的所有規格閘留痕裡,找「同一個條款編號、同一個測試名、判定是紅」的紀錄」
   - file: `scripts/lumos:15492`(`_spec_gate_gov_index`,治理帳那半)
severity: major
   - blocking: 是

4. **JUnit 讀法:說借 `_secev_junit_facts`,但它回的東西不夠用 ⚠**
   - `_secev_junit_facts` 只回 `{id: (狀態, 斷言布林)}`。設計要的是「失敗內文的例外鏈」,還要分清「有型別但非斷言」跟「沒有型別」。這些在 facts 裡都拿不到。
   - `test_quality.junit()` 其實有 `reason` 欄,但 facts 把它丟了。
   - 還有一個行為落差:手機端(沒型別)的報告,`assertion_failure` 會看堆疊判成斷言(True)(`scripts/test_quality.py:108` 的 `not kind` 分支)。所以設計的 (c)「沒型別 → 未判」實際會落進 (a)「斷言」。
   - 實作者要嘛擴 `_secev_junit_facts` 的回傳(影響 3 個呼叫端),要嘛另寫一個讀報告的 helper。設計要先選一個。
   - 引句:「再讀那一筆 testcase 的失敗內文,例外鏈出現」
   - file: `scripts/lumos:8883`
severity: minor
   - blocking: 否

5. **列指紋的正規化是第四套配方 ⚠**
   - 鄰居有三套。`_clause_block_sha` 把所有空白去掉(`scripts/lumos:14144`)。`_residual_claim_fp` 做 NFKC、壓空白、去 Cf/Cc 不可見字元,取 sha256 前 16 碼(`scripts/lumos:26726`)。`_door_scan_text` 另有一套。
   - 設計的「NFKC、壓空白、Tab 接起來」跟 `_residual_claim_fp` 最像但沒有剝不可見字元。鄰居本身已不一致,所以標 ⚠。
   - 建議設計寫明為何不直接用 `_residual_claim_fp` 的前半。
   - 引句:「預期值表一列的四格各自去掉頭尾空白、連續空白壓成一個、全形半形統一(NFKC)之後,用 Tab 接起來算 sha256。」
severity: minor
   - blocking: 否

6. **找節與解析表格:沒說走既有 helper**
   - 專案有 `_h2_section_lines(text, h2_re)`(`scripts/lumos:13774`)。它的說明寫著「找節邏輯不准長出第三套」,回退節與實務隱患節共用它。設計沒提 `## 預期值表` 怎麼找節。
   - 表格解析專案裡沒有共用 helper,而是三處各自內聯 `strip("|").split("|")`(`scripts/lumos:27561`、`scripts/lumos:51363`、`_note_audit_parse_report`)。
   - 設計寫「自建」不算錯,但會變第四份內聯。建議找節走 `_h2_section_lines`,表格解析抽成一支。
   - 引句:「格式:計劃裡一節 `## 預期值表`,底下一張表,表頭固定四欄「條款 | 輸入 | 預期 | 來源」」
severity: minor
   - blocking: 否

7. **「沒有互動終端記成 AI」的呈現方式跟鄰居不同 ⚠**
   - 「誰簽的」判法沿用 `_waive_origin_tty`,這是對齊的(`scripts/lumos:38429`,Android 端到端驗收放行和 lint-waive 共用)。
   - 但鄰居的 AI 放行有一套固定做法:記 `acked` 欄,`lumos doctor` 的 AE 段和開場掛鉤一直列「還沒人看過的 AI 放行」,用 `--ack` 清掉(`scripts/lumos:4187`、`scripts/lumos:4200`、`scripts/lumos:43517`)。
   - 設計只在 `gov --stats` 數人簽與 AI 簽的列數,不設 `--ack`,doctor 與開場也不提醒。
   - 這是 Enzo 在 d3 與「不做」節明裁的,所以我不判成缺陷,只標 ⚠。請設計補一句「與 lint-waive、e2e waive 的 `--ack` 機制不同是刻意」,免得接手的人以為漏做。
   - 引句:「不設金鑰簽、不防 AI 代簽、AI 簽的列不在開場與 doctor 一直提醒」
severity: minor
   - blocking: 否

## 第 3 問(接)命名與錯誤處理不一致

8. **閘名、kind、欄位名 ⚠**
   - 專案已有 `signoff` 閘,kind 是 `signed`(`scripts/lumos:17017`)。規格閘的事件聚在 `spec-gate` 閘下,kind 有 `spec-gate-record`、`spec-gate-run`。
   - 新增獨立的 `expected-signoff` 閘加 `expected-sign` kind,閘名與 kind 重複,也讓簽核分在兩個閘名下。
   - 「人或 AI」的欄位名設計沒寫。鄰居不一致:Android 端到端驗收放行用 `by`(`scripts/lumos:43524`,`by` 已在 `_GOV_FIELD_TYPES`,`scripts/lumos:16918`),lint-waive 用 `origin`(`scripts/lumos:38524`),所以標 ⚠。
   - 鄰居一律留了簽核人(`--by`、`_e2e_who`、`USER`)。設計只記「人或 AI 類別」,沒有誰簽的。
   - 設計還漏了:新欄位要進 `_GOV_FIELD_TYPES`,fix-check 就是這樣做的。
   - 引句:「閘名 `expected-signoff`(加進 `_KNOWN_GATES`)、kind `expected-sign`」
severity: minor
   - blocking: 否

9. **錯誤處理缺口**
   - **寫帳失敗**:`_gate_event_or_warn` 的語意是「永遠不改判定」(`scripts/lumos:1925`),適合觀測。簽核事件本身就是證據,寫不進去應該回非零,像 `cmd_signoff` 寫帳失敗會丟 `WriteBlocked`(`scripts/lumos:16533`)。`_gate_event` 還會在沒有 `docs/` 時回 None,設計沒講這種情況。
   - **擋下事件缺 kind**:RETIRE-IF 要數「沒有先紅」與「預期值沒簽」各被擋幾次,但設計沒新增擋下事件。pre-push 只記一般的 spec-gate 擋下。鄰居有專屬 kind,例如 `nogo-light-review-missing`(`scripts/lumos:16099`)。
   - **測試品質模組讀不到**:`_e2e_junit_ok` 有處理 `_secev_tq()` 回 None(`scripts/lumos:41777`),設計的 (d) 只處理報告被拒收。
   - **訊息措辭**:`_waive_origin_tty` 答 n 時印「沒放行」,用在簽核會顯示成「沒放行」,措辭對不上。
   - 引句:「風險高計劃在推送前因「沒有先紅」或「預期值沒簽」被擋的次數為 0」
severity: minor
   - blocking: 否

10. **`clause_verdicts` 裡的測試身分格式**
    - 設計寫「每條條款記 `{判定, 紅因, 測試名}`」,推送前比對「同一個測試名」。
    - 鄰居的身分是(平台, 方法)。多平台專案的留痕 `tests` 寫成「平台:名字」(`scripts/lumos:14263`),紅燈版也用(平台, 方法)(`scripts/lumos:14306`)。
    - 一條條款可綁多支測試,設計像是一條只記一筆。只用測試名會在多平台、同名測試的專案裡撞名。
    - 引句:「每條條款記 `{判定, 紅因, 測試名}`;風險高也照記。」
severity: minor
    - blocking: 否

11. **紅因判讀的位置與找報告的方式**
    - 位置:見第 1 問。應放在 `cmd_spec_gate` 的 `_spec_gate_run_clauses` 之後、`_redbase_collect` 之前,不要放進共用的 `_spec_gate_judge_items`。設計沒指明。
    - 找報告的方式:設計寫死「名叫 `build` 的目錄」。鄰居找報告都靠設定宣告的目錄,例如 `macrobench.json` 的 `results_dirs`(`scripts/lumos:40500`)、`compose-metrics.json` 的 `reports_dir`。
    - 設計的「誤擋一」已承認自訂輸出位置會判成弱證據,是明知取捨。但這是第二套找報告的方式,所以列為 minor。
    - 引句:「在 repo 裡名叫 `build` 的目錄底下找這次跑出來的報告」
severity: minor
    - blocking: 否

## 第 4 問 落點:合理,預期值表與簽核不必另開一篇

- `Systems/規格閘.md`
  - 約 66KB、175 行、40 行 summary、0 條合約。
  - 負責範圍已寫明含:條款句式、綁定、紅燈版、留痕、推送前讀留痕(`--push-check`)。
  - 預期值表檢查、紅因判讀、先紅檢查、`clause_verdicts` 都在這個範圍內。
  - 規格閘已經很大,要避免再長成讀不完的節點。
- `Systems/reversibility-governance-ledger.md`
  - 約 22.8KB、146 行,管 `scripts/lumos` 和 `scripts/hooks/post-commit`。
  - 該篇用 WHY 行記新增閘名與事件種類:`fix-check`、`drift-check`、`spec-gate-record` 都這樣記,所以 `expected-signoff` 寫進這篇有先例。
  - 這篇的 KEY 也有「signoff 簽核留痕」,簽核也沒有更合適的家。
  - 但這篇沒有 `responsibility` 欄位(有 S10 風險)。寫進新職責前,建議先補一句負責範圍。

## 彙總

不對齊共 11 條,其中 major 3 條。

標 ⚠ 交編排者決定的有 4 條:第 4、5、7、8 條。原因是鄰居本身就不一致,或是 Enzo 已明裁。

第 1 條(表格與條款語法衝突)已用現有程式實測,證據確定,其他審查席可以直接引用。

相關檔案:
- `/Users/enzo/harness/lumos-highrisk-evidence/scripts/lumos`
- `/Users/enzo/harness/lumos-highrisk-evidence/scripts/test_quality.py`
- `/Users/enzo/harness/lumos-highrisk-evidence/governance/review-reports/高風險測試證據加嚴/r1-snapshot.md`
