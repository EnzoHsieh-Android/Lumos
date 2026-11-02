severity: major

整合/知識同步鏡頭的審查結果。我讀完整份 spec,逐節對照程式碼、既有測試、圖譜與研讀報告。「機械 refcheck 與前掃已處理的措辭、未定義詞」我沒有重報。

## 〈問題與最小解〉、〈名詞〉、〈第二批〉、〈回退〉
已讀,無 finding(研讀結論抽查另列在最後)。

## 〈做法〉一、比對工具

**F1**
severity: major
blocking: 是(不改,實作者會做出「單次放行就永久放行同類作弊」的閘)
- 位置:一、「指紋 = sha256(規則代號、檔案、身分字串)」與 `tq/skip-added`、`tq/build-config`、`tq/ci-config`、`tq/expected-changed`。
- 問題:放行綁指紋、永久有效,身分字串用「正規化後的那一行」,沒帶所在函式或區塊,也沒有第幾次出現。
  - 同一支檔裡放行過一條 `@Ignore("flaky")`、`ignoreFailures = true` 或 `continue-on-error: true`,日後在同一支檔新加的同文字作弊會被自動放行。
  - 例:`detekt { ignoreFailures = true }` 是合理的,放行後 `tasks.withType<Test> { ignoreFailures = true }` 就是同一把鑰匙。
  - `tq/expected-changed` 的身分若用「換成佔位後」的那行,一次放行會涵蓋該行形狀的所有日後改動。spec 沒講身分用哪種正規化。
- 佐證:file: `scripts/lumos:38629` `_lint_new_key` 與 `scripts/lumos:38707` `_lint_waivers_add`(只用 key 判放行,不看次數)。`scripts/lumos:38654` `_lint_new_diff_claims` 雖然算次數,但放行檔是依 key 整批扣掉,註解寫明「放行綁指紋不綁版本」。
- 判準:身分要含所在測試函式名或區塊,`expected-changed` 要用含常值的原行。
引句:「指紋 = sha256(規則代號、檔案、身分字串)前 16 碼」

**F2**
severity: major
blocking: 是
- 位置:一、〈測試函式〉定義(「Kotlin 認 `fun 名稱(`;用括號配對找函式本體,略過字串與註解裡的括號」)。
- 問題:切函式本體的規則漏了 Kotlin 特有寫法,而這些寫法是標準自己推薦的。
  - 運算式本體 `fun x() = runTest { … }`,標準寫「一支測試一個 `runTest`,寫成運算式本體」。
  - 單行 `= assertEquals(…)`。
  - 反引號函式名(含空白與括號)。
  - 回傳型別 `: Unit`。
  - raw string `"""`、字串樣板 `"${m["k"]}"` 裡的引號與大括號、字元常值 `'{'`、巢狀 `/* */` 註解。
  - 若只找 `)` 後的 `{`,標準推薦寫法會被當成空本體,每支都列 `tq/no-assertion`。
  - 同名配對在 `@Nested` 內層類別、重複名稱時也未定義。
- 佐證:file: `skills/lumos-project-notes/commands/test-quality-standard.md`〈怎麼寫才算數〉協程條「寫成運算式本體」。S1–S5 的測試敘述沒有任何一例是運算式本體或反引號名。
- 判準:切分規則不補齊,偵測結果因寫法而異,實作者只能自己猜。
引句:「用括號配對找函式本體,略過字串與註解裡的括號」

**F3**
severity: major
blocking: 是
- 位置:一、規則表 `tq/test-removed` 對照〈六〉「正常改動對照:改測試名…不應出候選」。
- 問題:兩處互相矛盾。
  - 規則寫「改動前有的測試函式,改動後同一支檔沒有了,而且其他測試檔也沒有同名」。
  - 把一支測試函式改名(同檔)就滿足這條,會列 `tq/test-removed`,但〈六〉與 S14 要求「改測試名不應出候選」。
  - 「(含改名後)」只指檔案改名,不是函式改名。
  - 加上 spec 自己的實測(101 條候選有 85 條是 `test-removed`、大多是合理重寫),預設 block 下最吵的規則沒有任何事前收窄設計。
- 判準:S14 照規則文字不可能通過,實作者得自己決定改名偵測怎麼做。
引句:「改動前某測試檔有的測試函式,改動後同一支檔(含改名後)沒有了」

**F4**
severity: major
blocking: 是 ⚠
- 位置:一、`tq/expected-changed`、`tq/timeout-raised`「同一個 diff 區塊一行刪掉、一行新增」。
- 問題:字面是 1 比 1。
  - 表格式測試連續改多行預期值(N 行刪、N 行增)時不會配對,逃過最典型的作弊(把一串預期值改成程式輸出)。
  - S4 只測單行,沒有規定 N 比 N 要不要按位置配。
  - 我讀不出規則意圖是否涵蓋 N 比 N,所以標 ⚠。
- 判準:作弊型態與測試之間有缺口,且 spec 沒有把這個限制列入「抓不到」清單。
引句:「同一個 diff 區塊一行刪掉、一行新增,兩行都有斷言字」

**F5**
severity: major
blocking: 是
- 位置:一、`tq/ci-config`(`-x` 接含 `test`/`check`、`|| true`)與〈二〉「純 Python 這類專案不受影響」。
- 問題:CI 檔屬五類之一,任何棧改 CI 檔都會觸發。
  - `pytest -x tests/` 的 `-x` 後面是 `tests/`,含 `test`,會被當成 Gradle 的 `-x test` 擋下。
  - `|| true` 是 CI 腳本的常見慣用句,規則沒限定在測試步驟。
  - 本 repo 自己的 CI 就有至少 7 行 `|| true`,另有 `continue-on-error: true`。
  - 研讀報告對這類固定關鍵字說「誤報應該很少」,但報告只推論 Gradle 專案。
  - `tq/build-config` 的 `exclude(…`**`…)` 對 jacoco、packaging 的排除清單(`**/BuildConfig.*`)也會誤報。
- 佐證:file: `.github/workflows/ci.yml:41`、`.github/workflows/ci.yml:93`、`.github/workflows/ci.yml:299`(`|| true`)、`.github/workflows/ci.yml:289`(`continue-on-error: true`)。
- 判準:「非 Android 專案不受影響」這句不成立,影響到所有消費專案的 CI 編輯。
引句:「沒碰到就不載入、不判,純 Python 這類專案不受影響」

**F6**
severity: minor
blocking: 否
- 位置:一、斷言字名單與 `tq/no-assertion`。
- 問題:名單沒有截圖或黃金檔比對類呼叫。例如 Paparazzi 的 `snapshot {}`、Roborazzi 的 `captureRoboImage`、`compareRoboImage`,而標準自己列了截圖測試為選配。
  - 專案自訂 helper 沒有宣告口:研讀報告 smells 提到要仿既有 `--check-helper`,spec 沒對應機制。
  - 每個新截圖測試與自訂 helper 測試都會被列成無斷言。
- 佐證:file: `governance/eval/results/ai-test-verification-research-20261102/smells.md:393`(「專案自訂 helper 要明示」)。
- 判準:只會製造需逐個放行的誤報,放行是出口,所以不是 blocking。
引句:「另認 Kotest 的 `should` 開頭中綴」

**F7**
severity: minor
blocking: 否
- 位置:一、`tq/too-large`。
- 問題:單檔上限取自新增告警閘設定的 `max_file_lines`、`max_file_bytes`。
  - 該設定正是給「慢工具的專案自己調小」用的。
  - 調成 4000 的專案,每個動到的大檔(含只需看新增行的正式程式檔)都會同時出現原有的 oversize 與 `tq/too-large`,要放行兩次。
  - 正式程式檔只需讀 diff,不必讀整份。
- 佐證:file: `scripts/lumos:38262`(註解寫明慢工具專案自己調小)、file: `scripts/lumos:38744` `_lint_new_oversize`。
引句:「測試檔、正式程式檔或建置檔任一版本超過新增告警閘的單檔上限(行數或位元組)」

**F8**
severity: minor
blocking: 否 ⚠
- 位置:一、效能段與 S10;〈實務隱患〉效能。
- 問題:
  - 實務隱患寫「S10 釘住 20 萬行 10 秒內」,S10 本文是 5.9 萬行(20 萬行只列 `tq/too-large`、沒有秒數條款)。前掃漏掉這處。
  - 只量過單檔大小;改動檔案數、截圖基準圖數量(重錄常數百張)沒有上限,也沒說超出 300 秒預算怎麼處理。既有路徑是預算不足視為擋下。
  - 基準圖指紋寫「綁路徑與內容」,應該用 git blob id,不必讀位元組。
  - S10 的牆鐘 10 秒斷言在分片 CI 上可能不穩;原型 1.86 秒的餘裕約 5 倍。
- 判準:判不準,標 ⚠。
引句:「S10 釘住 20 萬行 10 秒內」

**F9**
severity: minor
blocking: 否 ⚠
- 位置:一、使用範圍(推送範圍)。
- 問題:〈六〉自己指出合併提交會把另一條分支的改動算進來,所以量測排除合併;但真實推送時,把 main 併進功能分支再推,範圍 `遠端舊值..新頂端` 會含別人的測試刪除與改動,全算在推送者頭上。spec 只在量測段處理,閘的行為未處理。
- 佐證:file: `scripts/hooks/pre-push:488`(`_brange` 的範圍算法)。
引句:「合併提交跟第一個父提交比會把另一條分支的改動算進來」

## 〈做法〉二、併進新增告警閘

**F10**
severity: major
blocking: 是
- 位置:二,「閘設 warn 時只報不擋」;〈回退〉;〈實務隱患〉守衛面。
- 問題:現行程式碼 warn 模式其實不報。
  - `_cl_say_ok_extras` 對 status `warn` 也印「新增告警閘:沒有新增的告警(跑了 N 條檢查命令)」,候選一條都不印。
  - 我用假 verdict(status `warn`、`new` 有 1 條 `tq/skip-added`)實跑,輸出是「沒有新增的告警(跑了 0 條檢查命令)」。
  - spec 把 warn 當作比對擋錯人時的標準出口,出口本身會把候選藏起來。
  - 該印 warn 候選、`not-checked` 之外的文字、純比對模式下「跑了 0 條」的誤導字樣,spec 一個都沒列。
- 佐證:file: `scripts/lumos:68967`、file: `scripts/lumos:68990`(`_head` 只對映 env-unavailable 與 not-checked)、file: `scripts/lumos:38785`。
引句:「把 `lint_new.gate` 設成 `warn`(只報不擋)」

**F11**
severity: major
blocking: 是
- 位置:二,「比對工具自己出錯時擋下而不是放行」與〈實務隱患〉守衛面「壞的是推送體驗、不是靜默漏判」。
- 問題:spec 只規定「載入失敗」要擋。執行期例外沒有規定。
  - 比對工具在 `_lint_new_verdict` 裡丟出例外,會被 `_codeloop_lint_new_step` 的 `except Exception` 吃掉,走 `_gate_failopen`、整道放行。
  - 這正是 spec 宣稱「否決照新增告警閘出錯就放行」要避免的行為。
  - 解析器遇到未預期的 Kotlin 寫法(見 F2)丟例外就會靜默漏判。
  - 實作者必須在比對工具內部自行包例外並轉成擋下,spec 沒講。
- 佐證:file: `scripts/lumos:67954` `_codeloop_lint_new_step`(try/except → `_gate_failopen`)。
引句:「比對工具自己出錯時擋下而不是放行,壞的是推送體驗、不是靜默漏判」

**F12**
severity: minor
blocking: 否
- 位置:二,「只有碰到五類檔才載入比對工具;沒碰到就不載入」。
- 問題:配套在 `main()` 開頭對每個 lumos 指令無條件載入全部檔(`_test_quality_load_bundle()`),結果存成區域變數 `quality_deployment_error`,`_lint_new_verdict` 讀不到。
  - 真實 CLI 路徑上「沒碰到就不載入」不成立。
  - 實作者要照 `_secev_tq()` 的寫法再叫一次載入函式。
  - 「沒碰到不載入」這句沒法在 CLI 層驗證。
- 佐證:file: `scripts/lumos:69780`、file: `scripts/lumos:8816`。
引句:「只有這次改動碰到比對工具看的五類檔」

**F13**
severity: major
blocking: 是 ⚠
- 位置:二,放行機制與 PRIOR-ART「寬規則篩候選 → 人裁」。
- 問題:實際上沒有人裁。
  - 推送者(AI)自己跑 `lumos lint-waive <指紋> --note "…"`、把 `.lumos/lint-waivers.json` 與作弊改動放同一個提交,本機與 CI 都通過(CI 讀被推送的樹)。
  - 放行檔的 `by` 欄只是 `$USER`,分不出人或 AI。
  - 同庫先例:Android 端到端驗收否決了「只有人能放行」,改為 AI 可放行但標成 AI 放的,並在推送、開場、體檢時顯示未被人看過的 AI 放行。
  - 本 spec 的唯一覆核是三個月後的人工抽查。
  - 這是設計決策,我判斷偏弱,標 ⚠。
- 佐證:file: `scripts/lumos:38707`(`who = $USER`);`lumos rejections` 的 Android端到端驗收 兩筆。
- 判準:作弊偵測的出口沒有任何人看,閘的目的被架空。
引句:「寬規則篩候選、再由人或 LLM 去掉誤報」

**F14**
severity: minor
blocking: 否
- 位置:二,「off 與 `LUMOS_SKIP_LINT_NEW` 補寫治理帳」。
- 問題:
  - 寫了事件但沒人讀:`_lint_new_autopass_count` 只數 `fail-open`,doctor 只顯示自動放行與放行清單條數。程式碼註解寫過「沒有人去數,有記帳就是空頭支票」。
  - 事件種類字面值沒定。倉庫慣例是英文 `skipped`(room-guard、nodehome-check),spec 寫「跳過」。
  - 常駐設 off 的專案,每次 `code-loop check`(含 `--keep-going` 與 CI)都追加一筆到版控帳。
- 佐證:file: `scripts/lumos:38930`、file: `scripts/lumos:4145`、file: `scripts/lumos:47983`(`skipped` 先例)。
引句:「閘被設定 off 或 `LUMOS_SKIP_LINT_NEW` 跳過時,補寫一筆治理帳」

**F15**
severity: minor
blocking: 否
- 位置:二,「轉成它既有的鍵:`key`、`rule`、`file`、`line`、`message`」與「擋下訊息印完整原因、該確認什麼」。
- 問題:五個鍵放不下「該確認什麼」與完整原因。
  - 現行印法 `message[:70]` 與前 8 條硬截。
  - 實作者必須加新鍵並在 `_cl_say_lint_block` 判 `rule.startswith("tq/")`,spec 沒指明,`--json` 的 `blocks` 輸出也會受影響。
- 佐證:file: `scripts/lumos:68944`、file: `scripts/lumos:68950`。
引句:「併進新增告警閘時轉成它既有的鍵」

**F16**
severity: major
blocking: 是
- 位置:二「加一支配套檔要同步五處」。
- 問題:清單不完整,且現有測試會直接翻紅。
  - `t_deinit_vendored_toolkit_constant` 逐項比對 `_VENDORED_TOOLKIT` 的完整元組(8 項),加第四支檔後必紅。
  - `scripts/test_test_quality_cli.py` 寫死三支檔:`copied_bundle()`(約 10 個測試用)、`test_partial_sidecar_returns_structured_invalid`、`test_bundle_reference_guard_rejects_wrong_load_order`(三元組 `wrong` 在四支檔時會先丟「配套指紋清單或載入順序未對齊」而不是「混到未驗來源」)。
  - 這幾個測試都在 `test_lumos.py` 的全套裡跑。
  - 文件側:`03-寫回圖譜.md` 寫「入口與三份 sidecar」會過期。
  - 列舉子指令的四處也沒列:`README.md`、`README.en.md`、`docs/指令參考.md`、`docs/command-reference.md`。
  - spec 的「指令數」項在 `guard` 只是 `test-quality` 的二層動作時並不適用(頂層指令數不變);要注意的是 `t_every_subcommand_has_when` 含二層。
- 佐證:file: `scripts/test_lumos.py:12903`、file: `scripts/test_test_quality_cli.py:423`、file: `scripts/test_test_quality_cli.py:708`、file: `scripts/test_test_quality_cli.py:970`、file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:63`、file: `scripts/test_lumos.py:106793`。
- 判準:實作者照 spec 清單做完,推送前的閘仍會紅,必須自己追。
引句:「加一支配套檔要同步五處,漏一處所有專案的 `test-quality` 都會回部署不完整」

## 〈做法〉三、Semgrep 自比規則

**F17**
severity: major
blocking: 是
- 位置:三與 S11 `[test:t_test_quality_scan_truth_self_compare]`。
- 問題:這台機器沒有 Semgrep(`which semgrep` 找不到),`ci.yml` 也沒安裝。
  - 現有掃描測試全部用假 Semgrep 執行檔,假的不會判 pattern。
  - 實作者要嘛寫需要真 Semgrep 的測試(CI 與閘上不是紅就是被略過),要嘛寫只檢查 `PATTERNS` 含該字串的重述測試(專案規則禁止的空殼)。
  - S11 說「Semgrep 自比規則應列成候選;`assertThat(f()).isEqualTo(3)` 不列」,沒有說測試怎麼在沒裝 Semgrep 時成立。
- 佐證:file: `scripts/test_test_quality_scan.py:146`(假 semgrep)、file: `.github/workflows/ci.yml:73`(只裝 ruff)。
- 另:這支檔的家是 `Systems/test-quality-multilang`,該節點不在 `lands_in`(見 F20)。
引句:「Semgrep 自比規則應列成候選,`assertThat(f()).isEqualTo(3)` 不列」

## 〈做法〉四、標準改寫

**F18**
severity: minor
blocking: 否
- 位置:四,改寫清單。
- 問題:改寫清單沒有處理會跟新行為對不上的既有句子。
  - 「機器抓不到」那條仍寫「規則只有 `assertEquals(x, x)`,Truth 寫法的自比不在內」,加完第三節規則後就是假的。
  - 〈不算過的證據〉寫「專案把 `failOnNoMatchingTests` 關掉時…要數 XML」,與 `tq/build-config` 把它列為候選的新規則並存,沒有交代。
  - 「真的開了(`isReturnDefaultValues`),設定旁邊寫理由」與閘的放行方式(`lint-waive`,理由不在設定旁)是兩套出口,沒統一。
  - 〈裝置那一路〉那條描述「從第一個堆疊行起第一個 Caused by 之前」,〈五〉要把演算法改成「尾端連續堆疊區塊」,但改寫清單沒列這條。
  - `t_test_quality_standard_android_drill_lessons` 與 `t_test_quality_drill_cli_cases_present` 釘住了現有字串與 10 個測試名,改寫要避開。
- 佐證:file: `skills/lumos-project-notes/commands/test-quality-standard.md:151`、file: `scripts/test_lumos.py:120113`。
引句:「明列不採用的壞味道(寫死數字、一堆沒附說明的斷言、Eager Test、Lazy Test、Dependent Test)與理由」

**F19**
severity: minor
blocking: 否
- 位置:四(穩定與隔離、變異測試兩條)對照研讀報告。
- 問題:改寫比報告原文走樣。
  - 報告:PR 閘「原順序 1 次 + 反轉 1 次 + 隨機約 20 次」,並寫明「`RobolectricTestRunner` 能不能吃 `@OrderWith` 沒驗,要先做一次最小實驗」,裝置測試 PR 跑 3–5 次。spec 只寫「原順序、反轉、打亂都要綠」,沒有次數,也沒有把 Robolectric 未驗證的警示帶進標準;同時又寫「Robolectric 單例最該打亂順序跑」。
  - 報告:PIT 實例是「13 個套用模組只有 4 個開跑、3 個有結果」,spec 寫「13 個模組只跑了 3 個」。
  - 報告:「警告語沒用」只在 gpt-4o-mini 上測過(oracle.md §5.4);spec 寫成通則「提醒它『程式可能有錯』沒用」。
- 佐證:file: `governance/eval/results/ai-test-verification-research-20261102/flaky-pbt.md:175`、file: `governance/eval/results/ai-test-verification-research-20261102/flaky-pbt.md:183`、file: `governance/eval/results/ai-test-verification-research-20261102/mutation.md:233`、file: `governance/eval/results/ai-test-verification-research-20261102/oracle.md:87`。
- 另:研讀報告 hacking 那張對照表的 `@Config(sdk=[…])` 排除、lint 與 detekt baseline、`runCatching { assert }` 在規則表裡沒有,也沒列進「抓不到」清單。
引句:「新測試跑原順序、反轉、打亂順序(JUnit 4.13 起的 `Ordering.shuffledBy`,印出種子才能重放)都要綠」

## 〈做法〉五、上一輪延後的六條

**F20**
severity: minor
blocking: 否
- 位置:五與〈第二批〉;`lands_in`。
- 問題:
  1. 有三條機械式回頭條件掛在 `scripts/test_quality.py` 上,期限都是 2026-11-08(距今六天),本計劃改的正是歸因與該檔:`Systems/test-quality-cli.md:37`、`Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證.md:33`、`Verification/測試品質工具接線_Node與Laravel原生消費驗證.md:35`。
     - 計劃只把「其他棧重跑」放到 2026-12-15,沒說這三行怎麼處置(結案或改期)。
     - 這三行條件對已存在的檔恆成立,不會擋推送,只會被 doctor 唸。
  2. 本計劃改 `scripts/test_quality_semgrep.py`(Truth 規則),它的家是 `Systems/test-quality-multilang`,不在 `lands_in`;`Systems/pitfalls-lint-adapter` 在 `lands_in` 卻沒寫負責範圍。
  3. 上一份計劃 `REVISIT:2026-12-15 Kotlin 靜態掃描這次沒跑` 被〈六〉的 Semgrep 實跑覆蓋,但沒說要不要把那行標 `[closed:]`。
  4. `Systems/test-quality-cli` 的 `responsibility` 寫「JUnit 一致性核對,不裁決業務答案」,不包含 git 差異作弊偵測;把新檔加進 `about_code` 時 `responsibility` 要不要改沒寫。
  5. Issue 要求第一到三條「各有一支放寬就紅的測試」,S13 只綁一個測試名(安全證據閘那支),裝置歸因的五條放寬測試沒有 `[test:]`。
- 佐證:file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:37`;`lumos impact --file scripts/test_quality_semgrep.py` 顯示該檔的家是 test-quality-multilang。
引句:「上一份計劃留下的回頭條件(Gradle 包裝例外記成內層型別、裝置那路打錯類名誰擋、App 啟動的網路流量、收據重收、其他棧重跑)」

## 〈驗收條款〉
**F21**
severity: minor
blocking: 否
- 位置:S9、S10。
- 問題:單一 `[test:]` 名稱綁了六種以上行為(S9:無工具照擋、放行後不擋、off 與環境變數跳過並記帳、載入失敗擋下、沒碰五類檔不載入、超過 8 條全印)。綁定閘只看 rc,任一分支壞掉可能仍綠;全域規則要求每條路徑各一支先紅的測試。S5–S7 也是同樣的多合一。
引句:「`tq/` 候選超過 8 條時全部印出」

## 固定席逐條判

- `Systems/test-quality-cli`:
  - 該節點的 PITFALL「新增子指令或 vendored 檔時,連同這四處一起改」描述的四道守衛不是這次會翻紅的主角,真正會紅的是 F16 的測試。
  - 設計會破壞它宣稱的行為嗎?不破壞既有行為,但會讓它的「三支 bundle」敘述、責任範圍與三條 REVISIT(F20)變得不準,必須同提交更新。
- `Issues/收證歸因第三輪留下的小問題`:
  - 不破壞。
  - 第二條修好後放行面變大,Issue 原寫「都不會讓收證誤放行」的現況句會失效;spec 的反例測試(尾端區塊無 Assert 堆疊、Caused by 包著、型別名後多字仍拒收)已覆蓋,但 Issue 與標準相關句要同步改。

## 研讀結論抽查(吻合部分)
- 3.5–6.5 倍與 145 個 PR、約 8 倍(Java、11 個模型)、63% 偵測上限、唯讀擋不住特判、10 次只找到約四分之一、`failOnPassedAfterRetry` 預設 false、PIT 2022 結案、arcmutate Android 外掛仍是 beta、jqwik 1.10 反 AI 條款:報告原文對得上。
- `ViewModelScenario.recreate()` 2.9.0 不在研讀報告裡,我用官方參考頁核對過,存在。
- 研讀報告的 FrogNano 規則層精確率 5.7%,spec 的 PRIOR-ART 借用「兩段式」但第二段是人;這點見 F13。

## 〈實務隱患〉逐類
- 守衛面:見 F1、F5、F11、F13。
- 效能:見 F8。
- 併發:漏列。治理帳追加與放行檔寫入沿用既有上鎖與追加行為,新增的寫帳點在 `_lint_new_verdict` 內,與既有路徑同類,無新隱患;但同工作目錄多會談下 `docs/.governance-log.jsonl` 會被 pre-push 弄髒,是既有行為。
- 資安:漏列。比對工具讀的是 AI 可控的 Kotlin 與 YAML 內容,要的是 F2(切分規則)與 F8(深層巢狀、大量換行的輸入),spec 只量過大小,沒量過巢狀深度。
- 金流、對外送出、不可逆:同意「已排除」,理由成立(只讀 git)。

總結:最嚴重等級 major,blocking 共 10 條(F1、F2、F3、F4、F5、F10、F11、F13、F16、F17)。
