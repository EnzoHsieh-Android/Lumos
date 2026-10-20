preflight-4: ran

## 前掃語意修正

前掃一席唯讀掃 `Projects/安全主張驗收閘_計劃`(2026-10-19),作者逐條開檔重驗後修真檔。下面只記「④機械宣稱驗語意」類(某機制現在會做 X 但不成立);①未定義詞、②壞引用、③自相矛盾與存在類命中直接修真檔,不在這裡逐條記。佐證行號以修改當下的 `scripts/lumos`、`scripts/test_lumos.py`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml` 為準(分支 EnzoHsieh-Android/security-gate,基底 301b0916)。

### P4-1 安全判定的位置跑不到放行早退那幾條路

- 修改前:「**位置**:`code-loop check` 的判定函式裡,排在新增告警閘之後、看風險分級之前,跟表態閘、新增告警閘並列;不看 tier(d9 要求所有專案都擋)。」
- 修改後:「**位置**:`code-loop check` 的判定函式(`_codeloop_guard_verdict`)裡,跟表態閘、新增告警閘並列、不看 tier(母計劃 d9 要求所有專案都擋),但**排在所有放行早退之前**:取到要推的提交(marker_sha)之後、推導 diff 範圍之前就判。」另補「取不到要推的提交時:工作目錄有資安登記痕跡就擋,原因代碼 `commit_unavailable`」,條款加 S30。
- 佐證:`scripts/lumos:57341-57343` 取不到 HEAD 直接 `_fin` 放行;`scripts/lumos:57349-57350` merge-base 等於 HEAD 放行;`scripts/lumos:57351-57353` 無 merge-base 放行;`scripts/lumos:57365-57366` 全零起點找不到真起點放行;`scripts/lumos:57397-57399` pitfalls 失敗 `return _fin(pf_fail)`;新增告警閘那一步在 `scripts/lumos:57466`,tier 早退在 `scripts/lumos:57470`。

### P4-2 「要跟著改的地方」漏了三處

- 修改前:「**要跟著改的地方**(避免漏接):合併各道明細的鍵清單、擋下訊息的分派、放行時的小結、每次判定開頭清掉的暫存屬性、pre-push 的擋下原因對照表 `pp_cl_reason`(有測試雙向比對)、pre-push 放行時只顯示特定字樣那一行的過濾條件、pitfalls 失敗時那條分支要不要照跑。」
- 修改後:拆成條列,新增三項:`_cl_say_block` 預設分支會印「這次高風險改動還不能推」,要加 `security_evidence` 專用句;`scripts/test_lumos.py` 的 `_PPC_KIND_SENTENCES` 加第五句;`t_prepush_cl_reason_sentences_match_plan` 讀的 [[Projects/推送前一次列出全部擋下原因_計劃]]「對照表四句的正本在這裡」那一行要先改成五句正本,測試的「四句」判準同步改。pitfalls 失敗那條改寫成「不用另外處理:安全判定已在它之前跑完」。
- 佐證:`scripts/lumos:57259` `_codeloop_kg_finish` 的鍵清單只有 bound_tests、dispositions、lint_new;`scripts/lumos:57928` `_cl_say_block` 的 else 分支印「這次高風險改動還不能推」;`scripts/test_lumos.py:75207-75208` `_PPC_KIND_SENTENCES` 四句;`scripts/test_lumos.py:75972-75987` 讀計劃那一行並檢查 `len(got) == 4`;`docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:68` 是正本那一行;`scripts/hooks/pre-push:136` `pp_cl_reason`。

### P4-3 bound-tests-gate 不是「每次推送當場真跑」

- 修改前:「- **behavior,來源是 Invariant**:沿用 bound-tests-gate。合約綁的 `[test:]` 在每次推送當場真跑,結果直接拿來用;這是唯一不怕舊報告的證據,因為它就在這次推送跑。」
- 修改後:「- **behavior,來源是 Invariant**:bound-tests-gate 的推送當場真跑不能當資安證據來源(…):它只跑這次改動波及到的合約,沒被波及的合約不跑;CI 那一步設了 `LUMOS_SKIP_BOUND_TESTS=1` 整道跳過;低風險推送帶 `--bound-tests-advisory`,紅了只提醒不擋。所以資安的 behavior 證據不分來源,一律要有自己的執行收據(…),閘門讀收據判;…」;〈機械做不到的判斷〉末條同步改成「閘門不執行任何工具,所有證據(含來源是 Invariant 的 behavior)都有這個限制」。
- 佐證:`scripts/lumos:55637` `_bound_tests_for_diff` 只取受波及合約;`scripts/lumos:56150-56154` 環境變數跳過;`.github/workflows/ci.yml:187` CI 設 `LUMOS_SKIP_BOUND_TESTS: "1"`;`scripts/hooks/pre-push:572` 低風險帶 `--bound-tests-advisory`;`scripts/lumos:57383` 只有 red 與 unfilterable 且非 advisory 才擋。

### P4-4 guard kill:配方不涵蓋 Invariant、kill-log CI 讀不到

- 修改前:「① guard kill:讀 `.kill-log.jsonl`,沿用表態閘合約背書那套判法(…)」;表格 guard kill 列 qualified 條件「…、配方涵蓋這條 Invariant」。
- 修改後:改成照表態閘的做法——本機寫入時算好資安背書、存進會被提交的治理帳 `docs/.governance-log.jsonl`,閘門(本機與 CI)只讀治理帳那一筆;另寫「**配方對到哪條護欄是新增的對應方式**」:證據圍欄的 fault_sensitivity 項寫明 `recipe_ids` 與它對的護欄 id,背書只認圍欄列名的配方,不沿用 `covers`。表格 qualified 條件改成「治理帳裡有本機算好的資安背書…配方 id 列在證據圍欄的 `recipe_ids` 且圍欄的 `control_id` 是這條護欄」。
- 佐證:`scripts/lumos:57603` `_backing_judge_groups` 用棧別題號 qid 比 `covers`;`scripts/lumos:57686` `covers` 從配方讀出、是題號字串;`scripts/lumos:27133` scaffold 把 `.kill-log.jsonl` 寫進 `.gitignore`;`scripts/lumos:57762` 註解「kill-log 不進消費專案版控,推送前與 CI 讀不到,只能在這裡算」。

### P4-5 SARIF 不能共用 `_lint_run_and_parse`

- 修改前:表格 SARIF 列讀法「把新增告警閘 `_lint_run_and_parse` 裡的 SARIF 解析抽成只吃資料的共用函式,兩邊共用,不另寫第二套」;PRIOR-ART「SARIF(抽出新增告警閘既有讀法共用)」。
- 修改後:「新寫一支只吃資料的嚴格解析(見下〈SARIF 另寫嚴格解析〉),不共用新增告警閘的寬鬆解析」,新增〈SARIF 另寫嚴格解析,不共用新增告警閘的讀法〉一段寫明取捨:新增告警閘既有行為一字不改,只可能共用 uri 正規化那一小段(現在內嵌、沒有獨立函式)。
- 佐證:`scripts/lumos:32586` 函式內 `subprocess.Popen` 執行指令;`scripts/lumos:32615` 接受 SARIF 1.0;`scripts/lumos:32621` 缺 driver 名 `continue`;`scripts/lumos:32623` `results` 用 `or []`,null 當空陣列。

### P4-6 teardown 不是「逐字輸入確認句」

- 修改前:「① 新增 `lumos security exception-approve`,要求從終端機逐字輸入確認句(沿用 teardown 的終端確認寫法),…」(整段三案比較)。
- 修改後:整段刪除(d1 已選 PR 核准,三案比較是歷史);改成「**核可方式依 d1**:…」一段與〈例外核准的可行性(待使用者裁)〉一節。
- 佐證:`scripts/lumos:25846` `cmd_teardown` 只問 `確定? [y/N]`;`scripts/lumos:59857` 有 `--yes` 略過。

### P4-7 d1 的「CI 核對 PR 核准」現況做不到 — 升級為正式 finding 交席位審

- 修改前:d1 content「…閘門在 CI 端核對該例外列是由使用者核准的 PR 帶進來的;…」(決策本身不改);正文「本機推送前與 CI 呼叫的是同一個指令,所以兩邊判定相同」;S28「…安全證據判定應相同」。
- 修改後:先照第一版裁定寫成待人題 Q9 與〈例外核准的可行性(待使用者裁)〉;同日使用者裁「不然就用金鑰吧」,於是改成:`decision-add` 新決策 d6(例外列只認使用者手上、需實體觸碰或密碼的金鑰簽的提交帶進來;公鑰釘在 `.lumos/security-approvers`;本機與 CI 都用 `git verify-commit` 與 `%G?`/`%GF` 核對最後改到例外列的提交、以母提交版清單驗;清單本身的修改也要現有金鑰簽;第一次釘金鑰由使用者手動),`decision-supersede` 把 d1 標成被 d6 取代,Q9 記成已決指向 d6,Q1 決策連結改指 d6。正文那節改寫成〈例外核准用簽章金鑰〉,第二帳號記為不選與理由,天花板(觸碰與密碼驗不到、第一次釘金鑰無從驗)各附 REVISIT。位置一段改成「本機與 CI 判定完全相同」;S28 改成「安全證據判定應完全相同,包括例外的簽章核對結果」;S26 改成簽章核對的四種樣本。
- 佐證:`.github/workflows/ci.yml:4-7` 觸發是 push 與 pull_request;`.github/workflows/ci.yml:185` code-loop gate 只在 `github.event_name == 'push'` 跑;`.github/workflows/ci.yml:12-13` `permissions: contents: read`;`scripts/lumos` 唯一的 GitHub API 呼叫在 `scripts/lumos:33517`(lint-watch 查 releases/latest),沒有讀 PR 核准的程式;GitHub 不准 PR 作者核准自己的 PR 是平台規則。
- **升級為正式 finding 交席位審**:這條動到已決的 d1 能不能實作。使用者已在 2026-10-19 裁成簽章金鑰(d6 取代 d1),席位審的是金鑰做法本身:找出要驗的提交的方法、用母提交版清單驗章、換公鑰與第一次釘金鑰的防線、本機與 CI 判定是否真的相同。

## 前掃判錯、沒改的

- 無。前掃各條重驗都成立;③10「沒登記專案每次寫治理帳」照裁定改成不寫治理帳、只在 `--json` 多一鍵。

## r1 處置

r1 七席共 60 條(blocking 37 條,數法:各席報告裡 `blocking: 是` 的行數)。組別照編排者裁定 G1–G13;G11、G12 使用者 2026-10-19 已裁,記成 d8、d9,沒有開待決題。架構對齊席的發現沒有編號,這裡依報告出現順序記成 F1–F8。

| 席位發現 | 組 | 處置 | 一句 |
|---|---|---|---|
| 正確性-sonnet#F1 | G2 | folded | controls 加 `threat_categories` 進〈一〉v2 唯一清單;缺了判護欄層 `threat_categories_missing` |
| 正確性-sonnet#F2 | G2 | folded | 判定輸入(required_evidence、threat_categories、assets、surfaces、evidence_refs)也跟 merge-base 比,變弱沒簽章紀錄就用新舊聯集判 |
| 正確性-sonnet#F3 | G3 | folded | 加種類 × format 允許表,不合判 kind_format_mismatch;工具類別產生不了該種類判 tool_kind_mismatch |
| 正確性-sonnet#F4 | G3 | folded | 同種類多筆取最差、不准好的蓋壞的,S17 改寫;targets 空陣列判 targets_empty |
| 正確性-sonnet#F5 | G3 | folded | 校準檔要命中每條宣告規則(calibration_rule_missing),校準夾具進綁定 |
| 正確性-sonnet#F6 | G4 | folded | 新增 `_secinv_snapshot_tree` 從提交樹產快照,起點與要推的版都用它;`security list --commit` |
| 正確性-sonnet#F7 | G1 | folded | 改內容簽章,壓提交、rebase、合併提交不影響;〈為什麼五種問題不再發生〉逐條寫 |
| 正確性-sonnet#F8 | G2 | folded | 修訂紀錄搬到 `.lumos/security-revisions.json`,綁 before/after 雜湊,節點刪了也讀得到 |
| 正確性-sonnet#F9 | G3 | folded | 一筆 review_record 只算它宣告的一個 kind;deployment 另要人審 |
| 邊界-sonnet#F1 | G3 | folded | targets 該種類要的鍵是空陣列判 invalid:targets_empty(S33) |
| 邊界-sonnet#F2 | G3 | folded | 補 S34–S40 涵蓋 review_not_independent、review_expired、evidence_fence_invalid、vulndb_stale、unsupported_format、backing_missing 與背書寫讀失效;S29 加未簽紀錄樣本 |
| 邊界-sonnet#F3 | G1 | folded | 內容簽章不看提交,合併提交與 squash 不影響;多提交推送一律對 merge-base 判 |
| 邊界-sonnet#F4 | G9 | folded | 30 天整有效、31 天無效;到期日當天有效隔天擋;日期一律 UTC;S23/S25 補樣本 |
| 邊界-sonnet#F5 | G7 | folded | `vulndb_fetched_at` 只收 ISO 8601;門檻仍待 Q5,寫明第 14 天有效第 15 天 stale 的邊界寫法 |
| 邊界-sonnet#F6 | G11 | folded | review expires_on 上限 observed_at+90 天、比對前正規化;紀錄由 d8 處理(reviewer_kind,人審要簽章) |
| 邊界-sonnet#F7 | G7 | folded | 證據檔 16 MiB/總量 256 MiB/10000 項,超限只判該項 evidence_too_large |
| 邊界-sonnet#F8 | G10 | folded | 安全指標腳本先 add(0);請求下限由工具清單登記;REVISIT 實測 k6 v2.3.0 |
| 邊界-sonnet#F9 | G2 | folded | 起點一律 merge-base(對預設分支推送前的位置),不用遠端舊值 |
| 整合-sonnet#F1 | G5 | folded | 只有 lumos-security-v1 圍欄算痕跡;本工作樹實跑確認只帶標籤的兩篇不會擋工具鏈(見下 M1) |
| 整合-sonnet#F2 | G3 | folded | 加 report_sha256 從要推的提交讀報告核雜湊;改綁定不重跑擋不住,寫進 limitations |
| 整合-sonnet#F3 | G1 | folded | 簽章在物件裡,壓提交不洗掉;例外提交不必排最後,也不會讓其他證據 stale(簽章不看提交) |
| 整合-sonnet#F4 | G1 | folded | 整個物件規範化後簽,沒有「那幾行」的問題,改任一欄都驗不過 |
| 整合-sonnet#F5 | G2/G6 | folded | v2 欄位彙整成〈一〉唯一清單、insufficient_required_evidence 單一擁有者在閘門、v1/v2 雙讀與預設寫清楚 |
| 整合-sonnet#F6 | G3 | folded | 圍欄項 kind 要等 evidence_refs 的 kind;Verification 節點 superseded/stale 判 verification_node_stale |
| 整合-sonnet#F7 | G3 | folded | 配方改到的檔要在 bindings(kill_recipe_unbound);新子命令 `security backing` 列進要跟著改的地方;S37、S38 |
| 整合-sonnet#F8 | G13 | folded | considerations 用同一個核可物件與同一支檢查、同樣要內容簽章 |
| 資源-sonnet#F1 | G7 | folded | 寫死上限與超限只判該項;S41 |
| 資源-sonnet#F2 | G7 | folded | 同一判定以(path, blob)快取解析;S43 |
| 資源-sonnet#F3 | G7/G1 | folded | git 讀取批次化(ls-tree + cat-file --batch);不再 blame;修訂紀錄可直接刪(只會少核可不會放寬) |
| 資源-sonnet#F4 | G1 | folded | 內容簽章不受重寫影響;格式化動到行也不影響(簽規範化 JSON) |
| 資源-sonnet#F5 | G4 | folded | 先 git grep 圍欄字樣當廉價預檢,沒有就不建快照 |
| 資源-sonnet#F6 | G7 | folded | 治理帳冪等鍵(護欄、種類、head_sha),多筆取 head_sha 相符最新;例外使用帳同鍵 |
| 資源-sonnet#F7 | G7/G9 | folded | 日期 UTC;observed_at 晚於提交時間判 observed_in_future;vulndb 只收 ISO 8601 |
| 資源-sonnet#F8 | G7 | folded | 未預期例外 fail-closed 判 evaluation_error;JSON/XML 深度上限;S42 |
| 回滾-sonnet#F1 | G6 | folded | 加 `security_evidence.gate: block|warn`,warn 要簽章;上線順序加「先釘金鑰」一步 |
| 回滾-sonnet#F2 | G6 | folded | 淺層 clone 擋並給 unshallow;根提交以空樹為起點;其餘由簽章的 warn 設定當出路 |
| 回滾-sonnet#F3 | G1 | folded | 建議至少兩把金鑰;清單修改含刪檔要 merge-base 金鑰簽新清單;全遺失寫成天花板加 REVISIT |
| 回滾-sonnet#F4 | G1 | folded | 同 F3 組,內容簽章不被壓縮、格式化、squash 洗掉 |
| 回滾-sonnet#F5 | G2 | folded | 修訂紀錄搬到受版控獨立檔,整篇節點刪掉也讀得到;S29 加樣本 |
| 回滾-sonnet#F6 | G6 | folded | 新工具雙讀 v1/v2、雙讀版先上線;回退舊工具前先降圍欄,寫進〈回退〉 |
| 回滾-sonnet#F7 | G6 | folded | 寫明 ② 依賴 ①、先撤 ②;四句改五句那行歸 ② |
| 回滾-sonnet#F8 | G9 | accepted | minor;到期就擋是設計本意,本機與 CI 跨日不同步已用 UTC 消掉;合進主線後才過期的照擋,出路是續簽例外或簽 warn 設定,不另加機制 |
| 回滾-sonnet#F9 | G8 | folded | test_quality 抽純函式寫明抽出前後 CLI 輸出與既有測試照綠、更新 bundle 雜湊 |
| 架構對齊-sonnet#F1 | G8 | folded | `_secinv_blocks` 參數化(圍欄標記、准放節點類型),共用 `_fence_regions` |
| 架構對齊-sonnet#F2 | G8 | folded | 純函式放 test_quality.py、更新 `_TEST_QUALITY_BUNDLE_DIGESTS`、配套缺檔判 toolchain_incomplete 擋 |
| 架構對齊-sonnet#F3 | G4 | folded | `_secinv_snapshot_tree` 沿用同組容量常數與錯誤代碼,不沿用 `_drift_tree_env` |
| 架構對齊-sonnet#F4 | G8 | folded | 另開 `_cl_say_sec_block`,三段式 |
| 架構對齊-sonnet#F5 | G8 | folded | JSON 用 `_secinv_json_loads`、git 用既有包裝並帶 log.showSignature=false、治理帳用 `_ledger_lines`、工具清單嚴格讀不回 None |
| 架構對齊-sonnet#F6 | G8 | folded | uri 正規化現在就決定不抽、各寫,寫明理由 |
| 架構對齊-sonnet#F7 | G8 | folded | question_refs 與 decision_ref 解析走 `_pq_*` 同一組 |
| 架構對齊-sonnet#F8 | G8 | folded | 新開 Systems/安全證據閘 當家;lands_in 補它與 Systems/棧別提問表態閘;推送前一次列出全部擋下原因_計劃 不是 Systems,lint 只准 Systems,改放 related |
| 外家finder-codex#F1 | G12 | folded | 使用者裁 d9 維持現狀:承接對照與〈實務隱患〉寫成工具天花板,加 REVISIT:2027-01-31 回看繞過 |
| 外家finder-codex#F2 | G4 | folded | 從提交樹產快照,checkout 跟推送的 ref 不同也判對版本;S4 改寫 |
| 外家finder-codex#F3 | G11 | folded | 使用者裁 d8:reviewer_kind 必填、ai 放行不了要人的判斷、human 要簽章;天花板寫明 |
| 外家finder-codex#F4 | G3 | folded | environment_ref 指 tracked 環境描述檔並進綁定;S18 改成描述檔改了就 stale |
| 外家finder-codex#F5 | G3 | folded | JUnit/SARIF/k6 必填 report_sha256;S10 改寫 |
| 外家finder-codex#F6 | G1 | folded | 簽章內容含 control revision 與判定輸入雜湊,外層一改就 exception_content_changed |
| 外家finder-codex#F7 | G3 | folded | 加 test_sources 必填並須在 bindings,漏列判 binding_incomplete |
| 外家finder-codex#F8 | G3 | folded | 加 coverage_path 鍵 |
| 外家finder-codex#F9 | G6 | folded | 新增 `code-loop check --security-only`,pre-push 非分支路徑也叫、CI 加 tag 觸發;S32 |

## r1 機械重現

工作樹 /Users/enzo/orca/workspaces/lumos-toolchain/security-gate,基底 e56c7234,2026-10-19 至 10-20 跑;合成 vault 放 /private/tmp/claude-501/sec-fold2/,做完已刪。

- M1(G5):`python3.14 scripts/lumos security list` → rc 0,`read_complete: true  registration_complete: false`,「沒有任何登記條目」,`errors: []`。`grep -rl flag/security-relevant docs/lumos-toolchain-knowledge` 有 `Projects/跨session傳訊用途調研.md`、`Verification/2026-08-14_跨session傳訊互動視窗實測.md` 兩篇只帶標籤(另三篇只在正文提到這個字)。`grep -rn '^```lumos-security-v1' docs/lumos-toolchain-knowledge` 0 筆:全庫沒有真的圍欄,提到字樣的五篇都是散文。結論:照 G5「只有圍欄算痕跡」,工具鏈自己判 no_registration、不擋;照舊寫法(標籤也算)會被判「有痕跡又登記不完整」擋下。
- M2(H3,@repo):合成 vault 一條護欄 `surfaces:["@repo"], assets:["@repo"]` 跑 `security list --json` → rc 2,errors `reference_error`(field assets,「assets 指到 inventory 沒有的 ID」)與 `reference_error`(field surfaces);同 vault 改回 `S1/A1` 對照 rc 0、errors 空。HIT:不改 `_secinv_check_links` 三類永遠登記不上。
- M3(G6/H2,schema_version):同一塊改成 `schema_version: 2` → rc 2,`unknown_schema_version`「schema_version 只支援 1」,整塊不採用。HIT:舊工具遇到 v2 圍欄整塊拒收,所以雙讀版要先上線、回退前要先降圍欄。
- M4(G6,tag):`sed -n 565,580p scripts/hooks/pre-push` 只有 `refs/heads/*` 那條路叫 `code-loop check`;`sed -n 618,630p` 的 else 分支註解「非分支 remote_ref(tag/其他 namespace):無 branch marker 通道,一律 advisory」、只印提醒。`.github/workflows/ci.yml` 開頭 `on: push: branches: [main]` 加 `pull_request`,沒有 tags。HIT:tag 推送現在完全不經安全判定。
- M5(blocking 數):`grep -cE 'blocking: ?是'` 逐席:正確性 4、邊界 5、整合 7、資源 4、回滾 6、架構對齊 2、外家 9,共 37;發現數用 `grep -cE '^(- )?severity: '` 扣掉報告開頭那一行:9、9、8、8、9、8、9,共 60。
- M6(G8 名稱存在):`grep -n` 確認 `scripts/lumos` 有 `_secinv_blocks`、`_fence_regions`、`_secinv_json_loads`、`_ledger_lines`、`_pq_decision_target`、`_pq_decision_state`、`_secinv_check_exception`、`_cl_say_disp_block`、`_cl_say_lint_block`、`_lens_git`、`_nodehome_git`、`_drift_tree_env`、`_TEST_QUALITY_BUNDLE_DIGESTS`、`_test_quality_load_bundle`;`_secinv_snapshot` 只吃工作目錄。

## 帳上 id 對照

帳上發現 id = 席名縮寫 + 席報告內編號:正=正確性-sonnet、邊=邊界-sonnet、整=整合-sonnet、資=資源-sonnet、回=回滾-sonnet、架=架構對齊-sonnet、外=外家finder-codex(例:正3 = 正確性-sonnet#F3)。發現種類一律 spec(被審文件缺陷)。
