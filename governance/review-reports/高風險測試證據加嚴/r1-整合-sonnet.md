severity: major

審稿立場:三個月後接手的人。以下 finding 都附了重現條件或程式位置;全文逐節讀完。

## 逐條 finding

### 1. 報告在整批測試跑完後才讀,同一個測試類別的 XML 已被後一次執行蓋掉
severity: major
blocking: 是 — 實作者照這段寫,同類別第二支以後的測試會一律判成「找不到報告」的弱證據,低風險計劃也過不了規格閘。
- 段落:做法 1「紅的原因」;實務隱患「誤擋二」。
- 問題:規格閘不是跑一支判一支。`_run_bound_tests` 先跑完所有測試才回傳結果,`_spec_gate_judge_items` 才逐支判定,期間沒有每支的開跑時間。Gradle 對每個測試類別寫一個 `TEST-<類別>.xml`,而每支測試是各自一次 `--tests X` 執行。
- 重現:同一個類別 `FooTest` 綁了 `a`、`b` 兩支,規格閘依序跑 `--tests FooTest.a`、`--tests FooTest.b`。判定時 `TEST-FooTest.xml` 只剩 b 的內容,a 走到 d 款「哪裡都找不到」,判弱證據。
- 其他類別的報告是否被 Gradle 清掉,⚠ 交編排者,我沒實測。
- 誤擋二只談「兩個規格閘同時跑」,沒談單次規格閘自己的多支測試。`bound_tests.parallel` 開了以後(`scripts/lumos:73xxx` 的 `_bound_tests_parallel`)同一目錄會併發寫,更糟。
- S1、S2 寫的是「風險高低都算」,所以低風險 Kotlin 計劃也受影響。`_spec_gate_twoway_run_verdict` 規定弱證據不算紅,結果是規格閘 rc1。
- 引句:「只讀修改時間晚於這次開跑、檔名是 XML 的檔」
- file: `scripts/lumos:69029`(`_run_bound_tests` 全部跑完才組 results)
- file: `scripts/lumos:15105`(`_spec_gate_judge_items` 在其後判定)
- file: `scripts/lumos:14338`(`_redbase_collect` 的註解寫明「判完當下就取內容」,現有程式已知道要立刻取)
- 需要補:報告要在每支測試的那一次執行結束時立刻讀,並指定「開跑」是哪個時間。

### 2. 借用 `_secev_junit_facts` 讀不到判法 a/b/c 需要的資訊
severity: major
blocking: 是 — 不改被指紋釘住的 test_quality.py,a/b/c 三款就分不出來,實作者必然自己發明判法。
- 段落:做法 1 判法 a、b、c;S2、S4。
- 問題一:`_secev_junit_facts` 只回 `{身份: (狀態, bool 斷言失敗)}`。它拿不到「失敗內文」,也分不出「報告沒有失敗型別(c 款,未判)」和「有型別但不是斷言(b 款,弱證據)」。兩者在 facts 裡都是 `(failure, False)`。
- 問題二:`tq.junit()` 的案例只有 `id/status/assertion_failure/reason`。`reason` 是型別加訊息加全文,並截在 4000 字。
  - JUnit5 的 `assertThrows` 包 `NotImplementedError` 時,`Caused by:` 排在整串 stack 之後,常超過 4000 字,例外鏈檢查會漏。
  - 計劃寫「只借不改」test_quality.py(有部署指紋釘住),所以這個上限改不了。
- 問題三:S4 說「跑在手機上的測試報告就是沒有型別」,不完全對。AGP 無型別路徑在首行是 `java.lang.AssertionError` 且有 `org.junit.Assert` frame 時,`assertion_failure` 會是 True,走 a 款而不是 c。
- 問題四:Truth 或 Hamcrest 在手機上是 False,照 facts 的 bool 會被 b 款當成「非斷言」判弱證據,每支都要補空殼,但那其實是「未歸因」該判未判。
- 問題五:`_secev_tq()` 在配套不完整時回 None。計劃沒寫這時 a/b/c/d 走哪款;若落到 d,部署不全的消費專案所有 Kotlin 計劃都不能做。
- 引句:「再讀那一筆 testcase 的失敗內文」
- 引句:「跑在手機上的測試報告就是這樣」
- file: `scripts/lumos:8883`(`_secev_junit_facts` 只回 `(status, bool)`)
- file: `scripts/test_quality.py:129`(`if not kind:` 分支,手機報告可判斷言)
- file: `scripts/test_quality.py:238`(`reason[:4000]`)
- file: `scripts/lumos:8871`(`_secev_tq()` 可回 None)

### 3. 風險高計劃把新行為條款標 `[keeps]` 就能整套繞過,而且沒有防繞的機械檢查
severity: major
blocking: 是 — 這是整個功能唯一不需要偽造任何東西就能繞過的洞,而且正好在「先紅補不出來」時最誘人。
- 段落:名詞「新行為條款」;做法 3「查什麼」;S7。
- 問題:風險低靠兩道檢查擋 keeps 濫用:`_spec_gate_twoway_static` 規定至少一條不標 keeps,且標 keeps 的測試必須在計劃建立前的提交樹裡已存在。計劃對風險高只借了 `_spec_gate_keeps_rows`(解析標記),沒借這兩道。
- 重現:風險高計劃的每條條款都加 `[keeps]`。
  - 「新行為條款」集合為空,先紅檢查空轉通過。
  - 預期值表「每條新行為條款至少一列」也空轉,簽核同樣不要求。
  - 「至少一條新行為」也沒要求。
- 引句:「風險高也叫 `_spec_gate_keeps_rows` 算 keeps」
- file: `scripts/lumos:14218`(`_spec_gate_twoway_static`)
- file: `scripts/lumos:14235`(`_test_exists_before` 檢查)
- file: `scripts/lumos:15278`(前段只對 `door == "low"` 才跑這兩道)
- 需要補:風險高也要「至少一條不標 keeps」和「keeps 的測試在計劃建立前存在」,否則加進天花板並附回頭條件。

### 4. 首筆留痕與紅證據只讀審查帳,與既有「兩本帳合併讀」設計與腳手架預設相反
severity: major
blocking: 是 — 換一台機器或乾淨 clone 後,所有已有紅證據的風險高計劃都會被擋,而且補不了。
- 段落:名詞「首筆規格閘留痕」;做法 3;實務隱患「效能」;天花板二。
- 問題:腳手架預設忽略的是審查帳 `.canary-log.jsonl`,治理帳刻意不忽略。現有推送前檢查因此用 `_spec_gate_latest_merged` 合併兩本讀(B3 設計)。計劃卻寫「在審查帳這份計劃的所有規格閘留痕裡」找紅,首筆也定義在審查帳。
- 天花板二寫「治理帳被 git 忽略的消費專案」,與腳手架預設相反。
- 重現:消費專案或第二台機器的乾淨 clone 沒有審查帳。
  - 在途的、生效日前的風險高計劃會被當成「沒有留痕=新計劃」(名詞末句),溯及既往地被擋。
  - 已實作完的計劃擋下後要求「先跑規格閘」,但實作完成後規格閘拿不到紅(`_spec_gate_low_not_red` 現有同款訊息),只剩把實作換回空殼的補法。
- 引句:「在審查帳這份計劃的所有規格閘留痕裡」
- 引句:「治理帳被 git 忽略的消費專案」
- file: `scripts/lumos:33136`(腳手架 `.gitignore` 內容,第 33140 行起列 `.canary-log.jsonl`,註解說治理帳刻意不忽略)
- file: `scripts/lumos:15519`(`_spec_gate_latest_merged` 合併兩本帳)
- 另外:現有函式只回「最後一筆」,「所有留痕」和「最早一筆」要新寫,計劃沒說。

### 5. 「程式檔」沒有定義,照現有候選函式的算法,設計階段的推送就會被擋
severity: major
blocking: 是 — 計劃自己宣稱要避免的「設計審階段誤擋」,照現有算法會直接發生。
- 段落:做法 3「哪些計劃要查」;S7、S9;天花板四。
- 問題:名詞表沒有「程式檔」。`_spec_gate_push_candidates` 的 `code` 是「不在圖譜目錄底下的所有檔」。
- 重現:規格閘每跑一次就寫 `docs/.governance-log.jsonl` 與 `docs/.canary-log.jsonl`(本 repo 兩本都進版控),卷證在 `governance/review-reports/…`。這些都不在圖譜目錄下,也不在 `_is_code_file` 的排除層以外的豁免裡。
  - 一次「計劃檔加兩本帳」的設計階段推送,依 `code` 的算法算作「也改到程式檔」,觸發先紅檢查。
  - 若實作者改用 `_is_code_file`,則 `_nodehome_is_test` 會把測試檔排除,「計劃加測試加空殼」之外只提交測試的 TDD 推送又查不到。
- 引句:「這次推送範圍改到那份計劃檔、同時也改到程式檔」
- file: `scripts/lumos:15543`(`code = [t for t in touched if not t.startswith(vrel + "/")]`)
- file: `scripts/lumos:15578`(`_is_code_file` 豁免層排除測試檔與 glob)

### 6. `clause_verdicts` 的形狀撐不住「一條多支測試」與多平台,推送前比對無從定義
severity: major
blocking: 是 — 一條綁兩支測試的條款,會變成永遠擋或形同不查;兩個平台同名測試則互相頂替紅證據。
- 段落:做法 2;做法 3「查什麼」。
- 問題:格式是每條條款一筆 `{判定, 紅因, 測試名}`,資料來源 `verdicts` 把一條多支測試壓成一個值。
  - 壓縮規則是「第一個非綠勝出」(`prev[0] == "green" and v != "green"`),所以先紅後弱與先弱後紅記出來不同。
  - 只留一個測試名。
- 推送前卻要「同一條款編號、同一測試名、紅」。多測試條款該每支都要紅還是任一支,沒寫;若要每支都紅,格式就留不住第二支。
- 多平台專案的留痕早就把測試名寫成「平台:名字」(`_spec_gate_record` 註解「紅燈版實跑三缺口」做法 2),`clause_verdicts` 沒帶平台,android 與 ios 同名測試會互相頂替紅。
- 引句:「每條條款記 `{判定, 紅因, 測試名}`」
- file: `scripts/lumos:15137`(`verdicts` 合併規則)
- file: `scripts/lumos:14263`(`_spec_gate_record` 的 refs 與平台前綴處理)

### 7. 已完成(done)計劃沒有比照風險低的「起點已 done 寬待」
severity: major
blocking: 是 — 舊問題重現:已完成的計劃只要改個字就被擋,補紅的唯一辦法是回頭換空殼。
- 段落:做法 3「哪些計劃要查」;天花板四。
- 問題:計劃規定「status 已經是 done」的風險高計劃一律查先紅與簽核。
- 重現:生效日後完成的風險高計劃,之後測試改名或刪除、或重編條款號,再編輯計劃檔(補回顧、改 `updated:`)。紅證據是用測試名比的,改名後找不到同名紅。實作早已完成,規格閘跑不出新紅,只能把已上線的實作換回空殼。
- 風險低這一側已有寬待:起點已是 done 時,條款指紋對不上與測試找不到只提醒不擋(`_spec_gate_push_one(done=True)`,決策 d3,`Systems/規格閘` WHY 2026-10-15)。計劃沒說風險高要不要比照,也沒說為什麼不比照。
- 引句:「或那份計劃的 status 已經是 done」
- file: `scripts/lumos:16128`(`_spec_gate_push_one` 的 `done` 寬待)

### 8. 被翻掉的舊規則散在 lands_in 與〈回退〉沒列到的地方,三個月後讀的人會得到相反指示
severity: major
blocking: 是 — 計劃的核心是「風險高也要先紅、要簽」,但最先被 AI 讀到的指引全都說「風險高只印不擋」,而且文件不在計劃要寫回的清單裡。
- 段落:frontmatter `lands_in`;〈回退〉末句。
- 計劃只列 `Systems/規格閘`、`Systems/reversibility-governance-ledger` 與「lumos-project-notes 的寫法說明」。還在講舊說法的地方:
  - `Systems/規格閘`(note)的第 19 行 KEY「風險高(半套)只印不擋紅綠」、第 82 行風險高流程(設計審→實作→代碼審→推,沒提推送前先紅與預期值表)、第 161 行「跟『風險高紅綠只印不擋』是兩回事」。計劃只點了第 39 行那一條。
  - `skills/lumos-design-loop/SKILL.md` 第 13 行「先判門」:「判風險高 → 照本 skill 走」,完全沒提預期值表或推送前要紅過。
  - `skills/lumos-project-notes/commands/03-寫回圖譜.md` 第 26 行 signoff 列、`skills/lumos-project-notes/reference.md` 第 71 行「工具只記留痕…」沒有 `--expected`。
  - 注入模板:`CLAUDE.md` 第 90 行與 `AGENTS.md` 第 91 行「風險高再進實作前的審查迴圈」(每個消費專案會被重新注入)。
  - `Systems/test-guard`:`_TG_LIMITS` 紅燈版那條沒說「非斷言紅判弱證據、不存紅燈版」。
  - `Projects/規格閘紅燈測試快照_計劃`〈四、不做〉:「不改風險高計劃『不強制先紅』的規則」,被翻掉了卻沒標記。
  - `Projects/業務簽核留痕_計劃`:這篇沒有 `decisions`,無法 `supersede`。
  - 程式字串:`scripts/lumos:15397` docstring、`:15428` 印出的行、`:72163`(`HELP_WHEN["spec-gate"]`)、`:72888` 與 `:72891`(argparse help)、`:3515`(doctor S12「半套」)。計劃只提「印紅綠那行」和 pre-push 與 `_spec_gate_push_check` 各一處,實際不只兩處:`scripts/hooks/pre-push:581-582` 有兩個字串,`_spec_gate_push_check` 還有 `份風險低計劃沒過` 與 `風險低不派審`。
- 一個細節:d3 引的舊規則字面是「何時該簽由人判,工具不擋」,原文是「何時該簽由人/流程判,工具不擋」,不是逐字。
- 規格閘印紅綠那行改成「推送前會要每條新行為都紅過一次」,也沒說首筆早於生效日的在途計劃要不要照舊印。
- 引句:「寫回的筆記(Systems/規格閘、Systems/reversibility-governance-ledger、lumos-project-notes 的寫法說明)跟著改回」
- 引句:「pre-push 掛鉤與 `_spec_gate_push_check` 各一處」
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:19`
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:82`
- file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:161`
- file: `skills/lumos-design-loop/SKILL.md:13`
- file: `CLAUDE.md:90`

### 9. 既有測試會紅的清單(計劃沒列)
severity: minor
blocking: 否 — 跑測試就會發現,不會做出壞系統,但工作量與預期應事先寫明。
- `_rb_sg_repo`(`scripts/test_lumos.py:123616`)用「python 假執行器、不產生 JUnit 報告」的 Kotlin fixture,被 7 處使用。
  - 這些計劃是新計劃,首筆留痕晚於生效日,依 S2/S3 該判弱證據,不再判紅。
  - 受影響:`t_spec_gate_redbase_written_on_red`、`_skips_after_green`、`_green_other_branch`、`_green_tracked_unfiltered`,以及同批用 `_rb_sg_repo` 的 `_ledger_ignored`、`_bookkeeping` 與 `t_tq_guard_redbase_*` 中走真規格閘的那幾支。
  - 要改成產生報告的 fixture,或在 fixture 裡設舊的生效日。
- `t_spec_gate_help_says_low_risk_blocks`(`scripts/test_lumos.py:76785`)釘「風險高只印不擋」,說明文字一改就紅。
- doctor S12、S14 的字串測試(`scripts/test_lumos.py:109900`)若動到「紅=新行為還沒做」會紅。
- 86 處 `--push-check` 測試裡,風險高計劃且同時改計劃檔與程式檔的案例,會被新檢查影響;全部掃一遍屬實作工作,我只抽查了 `t_prepush_small_change_gate`,其餘未逐支確認。

### 10. S9 的條件互相矛盾
severity: minor
blocking: 否 — 〈不做〉與做法 3 已經足以還原意圖,但綁定測試的人會寫反。
- 段落:S9。
- S9 把三種情況併成一句「不因先紅與簽核擋下」:早於生效日、每條都紅過、只因連到同一系統節點。
  - 「每條都紅過」仍受 S13 管:表沒簽照樣擋,與 S13 衝突。
  - 「早於生效日、每條都紅過」可被讀成要兩個條件同時成立才豁免,與〈不做〉「不回頭擋首筆早於生效日」矛盾。
- 引句:「每條新行為條款都紅過,或推送範圍只因連到同一個系統節點而碰到它」

### 11. 「紅在斷言上」的名詞定義與判法清單不一致
severity: minor
blocking: 否 — 只影響邊緣案例的歸類。
- 段落:名詞「紅在斷言上」;判法 a。
- 名詞說空指標這類例外不算紅在斷言上。判法 a 的例外鏈黑名單卻只有 `NotImplementedError` 與 `UnsupportedOperationException`。
- 重現:`assertThrows(IllegalStateException)` 抓到被測程式丟的 NPE,JUnit5 丟的是 `AssertionFailedError`(型別是斷言類),cause 是 NPE。照判法 a 判紅,紅因記斷言,與名詞定義相反。
- 名詞同一段還提到 `assertThrows` 會包例外,所以作者知道這個形狀,但判法沒收。
- 引句:「測試失敗是因為斷言不成立(預期值跟實際值不同),不是編譯錯」

### 12. RETIRE-IF 要的數字沒有任何記帳來源
severity: minor
blocking: 否 — 不影響功能,但撤除條件寫成了永遠量不到。
- 段落:RETIRE-IF;做法 3、5。
- 條件靠「風險高計劃在推送前因沒有先紅或預期值沒簽被擋的次數」。計劃沒有定義新的治理帳事件,只提到擋下訊息要照計劃風險講。
- pre-push 掛鉤記擋下用 `pp_record_block spec-gate`,同一個閘名、同一個原因字串,低風險的擋與高風險的擋分不開(`scripts/hooks/pre-push:582`)。
- 引句:「生效日後連續 90 天,風險高計劃在推送前因」

### 13. `lumos gov --stats` 的去重會折掉同一提交上的多筆簽核事件
severity: minor
blocking: 否 — 人簽與 AI 簽的列數會少算,而這組數字是計劃唯一拿來衡量「人抽離多少」的指標。
- 段落:做法 5 末句;天花板三。
- 去重鍵是 `(commit, nodes, gate, kind, token, check)`,新閘 `expected-signoff` 事件若不帶 `token`,同一個 HEAD 提交下對同一份計劃簽兩次(例如人簽幾列、AI 簽幾列)會折成一筆。
- 計劃只說「`_gov_row` 只取白名單欄位,要把這兩個數加進去」,沒提去重。
- 引句:「`_gov_row` 只取白名單欄位,要把這兩個數加進去」
- file: `scripts/lumos:17056`

### 14. 失效方向不一致:找不到報告判弱證據,走目錄逾時卻判未判(算紅);也沒有單檔大小上限
severity: minor
blocking: 否 — 逾時退化成「放過」,屬 fail-open;且讀超大報告會吃記憶體。
- 段落:實務隱患「誤擋一」「效能」。
- 找不到報告→弱證據(擋),走目錄逾時→未判(紅證據成立,放行),方向相反。計劃沒說為什麼逾時可以放過。
- 只限制走目錄時間,沒限制單檔位元組數或檔數。`junit()` 要整個 raw 餵進去,手機端測試的 system-out 或 logcat 可能很大。
- 引句:「走目錄的時間另設上限,逾時就把沒判完的當未判、印一句」

### 15. 預期值表的解析規則不足
severity: minor
blocking: 否 — 實作者要自己補細節,補錯的代價是誤擋。
- 段落:做法 4。
- 沒說:格內含 `|`(例如輸入欄寫 `a || b`)怎麼辦、欄數不是四欄、同一份計劃有兩個 `## 預期值表`、條款欄寫成 `S3` 不帶括號或同時列兩條、表格在程式碼圍欄裡。
- 列指紋把格內容做 NFKC 並壓空白,但上述解析歧義會讓同一列算出不同指紋,造成重簽。
- 引句:「格式:計劃裡一節 `## 預期值表`,底下一張表,表頭固定四欄」

### 16. ⚠ 交編排者:Gradle 的 JUnit5 測試名稱比對規則未定義
severity: minor
blocking: 否 — 我沒有在本 repo 找到佐證,只標出缺口。
- 段落:做法 1「找名字對得上這支測試的那一筆」。
- 比對規則只說比方法那一段。我記得 JUnit5 在 Gradle 報告裡的 `testcase name` 可能帶括號簽名(如 `method()`),參數化測試帶 `[1]` 序號,Kotlin 反引號名帶空白。計劃沒定義去括號或前綴比對。
- 若真的帶括號,精確比對會讓每支 JUnit5 測試走 d 款判弱證據。repo 內沒有現成處理(`scripts/test_quality.py` 與 `scripts/lumos` 都沒有去括號的邏輯)。
- 引句:「找名字對得上這支測試的那一筆」

## 各節狀態
- 名詞:見 11、10(S9 屬驗收條款)。
- 問題與最小解:已讀,無 finding。我用審查帳重算了數字,為 459 筆、134 份計劃、風險高 103、跑出過紅 13、最新一筆是紅 7;計劃寫的是 458 / 133 / 102 / 13 / 7,差一筆是計劃寫完後新增的留痕,不算錯。
- 調研結論:已讀,無 finding(外部文獻,我沒去核對原文)。
- 做法第一批:見 1 至 8、12 至 15。
- 做法第二批:已讀,無 finding。它引用 `Systems/guard-kill` 的舊否決並說明差異,這是計劃自己的處理方式,不影響本批。
- 不做:已讀,無 finding。
- 驗收條款:S9 見 10;其餘每條的測試名在目前的 `scripts/test_lumos.py` 都不存在(實作前正常),spec-trace 全部懸空。
- 回退:見 8。
- 實務隱患:見 14,誤擋二見 1。

## 固定席節點判定
- `Systems/test-quality-cli`:不影響其合約。計劃宣稱只借用 `scripts/test_quality.py` 不改,第一批不動它;但 finding 2 顯示若要補失敗內文,就會逼出改動並牽動部署指紋,實作時要停下回報。
- `Systems/test-quality-evidence`:不影響。計劃只讀它的 JUnit 解析,不改拒收型別或證據規則。
- `Systems/guard-kill`:不影響。兩條 ★INVARIANT★(`guard kill` 的 rc 優先序、`--json` 純度)都在 guard kill 路徑上,第一批只動規格閘、推送前檢查、`signoff`。第二批提的變異測試明說另開計劃,且與 guard-kill 的「不自動產生變異」用不同機制。
- `Systems/lumos-cli-lifecycle`(★INVARIANT★ re-inject 只覆蓋 sentinel 之間):不影響其合約。若依 finding 8 要改 `CLAUDE.md` 與 `AGENTS.md` 的注入模板,改動只落在 sentinel 內,不碰「sentinel 外 byte-equal 保留」。
- `Verification/測試品質第四輪修補驗證`:不影響,計劃不改它驗過的行為。

## 紅燈版(redbase)與 test-guard 的後果
- 非斷言紅改判弱證據以後,`_redbase_row_reason` 對 `v != "red"` 一律回「弱證據」,不存紅燈版。前提是弱證據的判定要寫在 `_spec_gate_judge_items` 這一層。若只改在 `verdicts` 或留痕那邊,`_redbase_collect(jrows)` 拿到的仍是 red 列,`TODO()` 階段的骨架檔照樣被存成紅燈版,和計劃最後一句相反。計劃沒指定改在哪一層。
- `tq/redbase-unmatched` 與 `tq/redbase-weakened` 的邏輯本身不受影響,它們只讀已存的紅燈版。但紅燈版會變多(風險高計劃現在都要先紅),測試改名時會同時觸發 `tq/redbase-unmatched` 與先紅證據找不到(見 7 的同一機制)。

## 實務隱患鏡頭:這個功能碰到的風險類
- 併發:有隱患。`bound_tests.parallel` 開啟時同一 Gradle 目錄併發寫報告,與單次規格閘內多支同類別測試互蓋(finding 1);計劃只談了兩個規格閘同時跑。
- 效能:有隱患。治理帳目前 21MB,推送前檢查每次整本讀兩次(留痕一次、簽核一次),約數十毫秒,可接受。真正的隱患是報告單檔大小沒上限(finding 14)。
- 資源:有隱患。同上,`junit()` 要整個報告進記憶體。
- 回滾路徑:有隱患。三個生效日常數可退,但被翻掉的規則散在 finding 8 列的文件裡,回退清單沒涵蓋;紅燈版與先紅證據一旦存了不會因回退消失,無害。
- 資料相容:有隱患。`clause_verdicts` 欄舊讀側當沒記這點成立;但 finding 4 的「沒有留痕=新計劃」會溯及既往地把在途計劃算進去。
- 可觀測性:有隱患。finding 12、13。
- 安全與路徑:無隱患。計劃自己的來源是本機報告與本機帳,沒有新的外部輸入路徑;finding 3 的繞過屬單人信賴模型之外的刻意偽造以外的無心路徑,已報。
- 使用者互動:無隱患。簽核的 30 秒逾時與現有 `_waive_origin_tty` 一致(`scripts/lumos:34220` 預設 30 秒),無新問題。

最嚴重 severity 是 major,blocking 共 8 條(1 至 8),minor 共 8 條(9 至 16)。
