severity: major

審查範圍:逐節讀完 r3-snapshot.md 全文,並對 `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj` 逐項開檔查證。以下整合席的主要結論是:spec 對「接進表態閘」只講了形狀,沒列出必須動的註冊面,照寫會讓 `t_stack_question_triggers` 翻紅,`gov --stats` 的統計也算不出來。

## F1 `_kt_rule_hits` 呼叫的函式認錯,算新增命中的接線不成立
severity: major
blocking: 是。判準:照 spec 字面實作不出來,必須先重構新增告警閘。
範圍 2 說 `_lint_new_run_cmds` 會「抽兩份快照、只回新增」。實際上它只在已解好的快照上跑命令,回傳 (base_claims, head_claims) 兩份原始告警。抽快照、算差集、套放行檔都在 `_lint_new_tools` 裡,而且它直接讀 `.lumos/lint.json` 組出 cmd_targets,沒有留給「換掉 `--config` 參數」的插入點。
- `_lint_new_tools` 的簽名需要 `base_ref`、`head_ref`、`cfg`、`out`、`waivers`、`werr`。所以「不讀放行檔」要傳空 waivers,spec 沒講。
- 「seg 是 `_lint_new_key` 取 sha256 前 16 碼」也不準:`_lint_new_key` 只回組合字串,sha256 在 `_lint_new_diff_claims` 才算。
- spec 要的是「同一條命令、把 `--config` 換成 review 與 hints」,所以得把 cmd_targets 改寫後再傳進去。這要重構 `_lint_new_tools`,spec 沒列。
- 命令沒有 `{LINT_FILES}` 佔位符時,`_lint_gate_covers` 會讓它落進 `report_only`。spec 沒說這種宣告怎麼辦。
- `--config` 的辨認(`--config=`、`-c`、`$HOME` 展開)沒定義。既有的嚴格切詞在 `_lint_wt_argv` 一帶(約 40575 行),spec 沒指名要不要重用。
- 預算只寫「時間預算」,沒指名常數。`_KT_SIT_BUDGET` 是情境題的,沒有說這題共用還是另設。

引句:「內部呼叫新增告警閘跑命令與比對新增的那一組函式(`_lint_new_run_cmds` 那一支,抽兩份快照、只回新增)」
file: `scripts/lumos:42664` `_lint_new_run_cmds` 的 docstring 與回傳是兩份告警清單,內部只呼叫 `_lint_new_run_one`。
file: `scripts/lumos:42590` `_lint_new_tools` 才做快照抽取、`_lint_new_diff_claims` 差集與 waivers 過濾(約 42640–42660 行)。
file: `scripts/lumos:42261` sha256 前 16 碼是 `_lint_new_diff_claims` 裡才算的 `c["key"]`。

## F2 `kt-rule-hits` 沒有註冊面清單,照做會讓既有守衛測試翻紅
severity: major
blocking: 是。判準:照 spec 做,既有測試必紅,而且接線站點沒寫全。
範圍 3 說「新增一題,題號 `kt-rule-hits`,形狀照情境題」。但題目表 `_STACK_QUESTION_SPECS` 才是全部機制(適用性、樣板、核對、`_stack_spec_by_id`)的入口,spec 沒寫要登記它。
- `t_stack_question_triggers` 把全表 id 集合釘死,`kt-rule-hits` 一進表就紅。
- 同一支測試還釘 id 格式 `^[a-z]+-[a-z0-9]+$`,而 `kt-rule-hits` 有兩個連字號,格式檢查也會紅。spec 要嘛改題號,要嘛列出改測試與放寬格式。
- 該測試同時要求每題 `when` 非空。這題的適用性來自「跑 ast-grep 算出命中」,不是觸發字,所以要像 `kt-situation` 一樣另有收集函式(`_kt_situation_apply` 一類)改寫 meta 的 applicable,spec 沒有。
- 情境題在 5 處有特殊分支:
  - `_dispositions_validate` 的形狀檢查(約 73001 行)。
  - `_dispositions_verdict` 的 `_pick`(約 74387 行)。
  - `_dispositions_template` 的 applicable 分支(約 74465 行)。
  - 逾時分支 `_over`。
  - `--carry` 的 `carried` 處理。
  spec 只寫「照既有規則」,沒列要新增哪幾處。
- `_ClkgFakes.disp` 手抄 `_dispositions_verdict` 的簽名,圖譜另有 PITFALL 記過替身簽名漂移。若為 `kt-rule-hits` 加參數,替身要同步,spec 沒提。
- 題表登記後,`code-loop recall-miss kt-rule-hits` 會被接受。`gov --stats` 的「觸發太窄候選」對這種非觸發字題沒有意義。

引句:「`lumos pitfalls --dispositions-template` 在有規則命中時多一題 `kt-rule-hits`」
file: `scripts/test_lumos.py:66060` `t_stack_question_triggers` 釘 id 集合;`scripts/test_lumos.py:66086` 釘 id 格式 `^[a-z]+-[a-z0-9]+$`,`kt-rule-hits` 不符。
file: `scripts/lumos:38393` `kt-situation` 是以 `_STACK_QUESTION_SPECS["kt"].append(...)` 登記;`scripts/lumos:39392` 之後由 `_kt_situation_apply` 改寫 meta。

## F3 治理帳欄位與統計接線漏列:mapper 沒有 `branch` 和 `rule_hits`
severity: major
blocking: 是。判準:S8「同一分支只取最後一筆」在現有統計管線上做不出來。
範圍 4 新增 ledger 欄 `rule_hits`。範圍 6 要 `gov --stats` 逐規則統計,而且「同一分支只取最後一筆表態」。
- `cmd_gov` 的 `_gov_row` mapper 是欄位白名單,只列了 `dispositions`、`blind_judge`、`role` 等,沒有 `branch`、`rule_hits`、`head_sha`。統計列拿不到分支名,也拿不到抽查結果。
- `_GOV_FIELD_TYPES` 明寫「新增 mapper 用到的欄位時一起補進來」,否則型別錯會讓整個 gov 當掉。`rule_hits` 不在表裡,所以 `_gov_event_types_ok` 不會擋型別錯的事件。
- spec 另寫「舊版讀情境盲判的 `_kt_bj_event_ok` 照缺欄略過」。`_kt_bj_event_ok` 對缺 `role` 回 False,這點成立。但 `_gov_situation_collect` 另有分支處理 `kind == "blind-judge"` 的事件,規則命中的抽查事件走進去會被當成壞形狀略過,spec 沒說新統計怎麼取這類事件。
- 「覆核規則」段在沒有資料時要不要印,spec 沒定義。既有 `gov --stats` 輸出測試可能受影響,⚠ 未逐一核對。

引句:「同一分支只取最後一筆表態,避免一個分支推多次被數多次」
file: `scripts/lumos:17577` `_gov_row` 回傳的欄位白名單沒有 `branch`、`rule_hits`。
file: `scripts/lumos:17499` `_GOV_FIELD_TYPES` 沒有 `rule_hits`。

## F4 `blind-judge --rule-hits` 與現有 `blind-judge` 入口衝突,記帳端的路由沒寫
severity: major
blocking: 是。判準:spec 兩處宣稱和現有入口的行為互相矛盾,而且記帳指令沒有定義。
範圍 4 說「型錄讀不到就那兩欄寫『型錄讀不到』,抽查照判」,又說結果檔「只收 `rule_hits` 一個鍵,不跟情境題的 `segments` 同檔」。
- `_cmd_codeloop_blind_judge` 一進來就先判 `_KT_DT_ERR`:型錄決策表讀不到直接 rc2「沒有情境題可以盲判」。這與「型錄讀不到、抽查照判」直接矛盾。
- 接著它呼叫 `_kt_bj_segments`,先算情境段。算不出來(`_KtSitUnverifiable`)就回 None、rc2。沒有情境改動時,規則命中抽查也被這條路攔住。
- 記帳端把結果檔交給 `_kt_bj_validate(data, segs, role, cells)`,它只認 `segments`。spec 沒定義記帳要靠旗標(例如 `--rule-hits`)還是靠偵測 `rule_hits` 鍵來分流。
- 旗標互動沒定義:`--rule-hits` 與 `--missing`、`--disagreements`、`--arbiter` 並用時怎麼處理。
- 新增旗標要有說明,`t_skill_mentions_resolve` 才會讓文件裡的 `--rule-hits` 解得開。範圍 7 只列了文件改寫,沒有 parser 與 `--help` 的改動。

引句:「結果檔只收 `rule_hits` 一個鍵,不跟情境題的 `segments` 同檔」
file: `scripts/lumos:74172` `_cmd_codeloop_blind_judge` 先 `if _KT_DT_ERR:` rc2,再呼叫 `_kt_bj_segments`。
file: `scripts/lumos:77657` blind-judge 的 parser 目前沒有 `--rule-hits`。

## F5 文件改寫清單漏項,且「統計節」指錯地方
severity: minor
blocking: 否。判準:內容過期,沒有機械測試會紅,但消費專案會讀到錯的說明。
範圍 7 只列了一句「統計節『語意覆核級要等計劃接上』那句」。
- 型錄裡 `checks-catalog.md` 第 11 行是通電批次欄定義,寫「要等 …計劃接上盲判才有作用」。統計節(第 881 行)沒有這句,位置寫錯。
- 另有 7 列的「告警帶寫法」格子寫著「接上前不擋」,這是批次欄的格值,spec 沒列。
- 41 處「預設不接」是提示級批次格值(例如「批一(只有提示級規則,預設不接)」)。計劃接上後這些全部變成不實,spec 沒覆蓋。
- `check.py` 第 22–24 行的註解 spec 有列。

引句:「`skills/kotlin-idioms/checks-catalog.md` 統計節「語意覆核級要等計劃接上」那句」
file: `skills/kotlin-idioms/checks-catalog.md:11` 實際位置在這裡;`grep -c "接上前不擋"` 是 7 筆;`grep -c "預設不接"` 是 41 筆。

## F6 改形狀候選門檻與既有 RULE 的一成線之間有未涵蓋的區間
severity: minor
blocking: 否。判準:只出候選、不自動改,沒有破壞既有合約。
圖譜 `Systems/kotlin規則包` 有一條齊欄且 2026-11-05 確認過的 RULE:「規則在真專案誤報超過命中的一成就降提示級或改形狀」。範圍 6 的「改形狀候選」要求 fp 佔八成以上、而且抽查判 false 至少九成。fp 在一成到八成之間的規則,既不列改形狀候選、也不列升擋候選,而 RULE 已經要求處理。這與 RULE 不是矛盾,但門檻比 RULE 寬很多,spec 沒有解釋。

引句:「答過至少 20 筆、fp 佔八成以上、而且抽查判 false 至少九成 → 列「改形狀候選」」
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:24` 該 RULE 行。

## F7 S9 的兩個場景在現況下沒有東西能判紅
severity: minor
blocking: 否。判準:測試形同空殼,不影響功能。
S9 要求「收工鉤子或 `lint-new --worktree` 跑工作樹模式時,覆核命令不被執行」。工作樹模式是白名單重組單條 ast-grep 命令(`_lint_wt_argv`),本來就不會執行 `kt-rule-hits` 的呼叫路徑。⚠ 收工鉤子是否會跑 `pitfalls --diff`(進而觸發收集函式)我沒查到。如果會,要把這點寫進測試;如果不會,S9 要換成能對症狀翻紅的指令。

引句:「當收工鉤子或 `lint-new --worktree` 跑工作樹模式時,覆核命令 應 不被執行」
file: `scripts/lumos:40575` 工作樹模式只自動執行寫死的 ast-grep 白名單命令。

---

固定席判定(這份設計會不會破壞該節點宣稱的行為或合約):
- `Systems/棧別提問表態閘` 第 31 行(`code-loop check` 逐題核對:缺 id、適用題卻 auto:true 等都擋):不影響。`kt-rule-hits` 只是多一個適用題,規則不變。
- 同節點第 34 行(適用性靠 `when` 逐行比對、未觸發題自動 na):這題的適用性來自工具輸出,不是觸發字。這是對該行宣稱的例外,但 F2 的註冊面一補齊就不破壞它。
- 同節點第 33 行(讀側只讀分支最後一筆 dispositions):不影響,spec 沿用同一讀法。
- `Systems/kotlin規則包` 的 RULE:見 F6,不破壞。
- `Systems/pitfalls-code-loop` 與 `Systems/linter精選目錄`:本席沒找到宣稱被這份設計破壞的合約。

消費專案(只有安裝版工具)能不能跑:
- 命中題用 `$HOME/harness/lumos-toolchain/configs/...` 同目錄的 `sgconfig-review.yml` 與 `sgconfig-hints.yml`,安裝版有這兩個檔,可跑。
- `check.py` 的 `main_rows` 與 `--fp-regress` 只在來源 repo 跑,這點 spec 已寫明。

實務隱患鏡頭:
- 守衛面:spec 自己已列為高風險,且走完整設計審。
- 效能:每次 `pitfalls --diff` 收集會多跑「兩份快照 × 兩份設定」的 ast-grep。spec 有快取,但沒給預算常數與數值(見 F1)。
- 資安:無,spec 已排除(只讀本機檔、不連網);範圍外。
- 不可逆:新增帳欄與題號,退提交回原狀。F3 的欄位補進 `_GOV_FIELD_TYPES` 後,舊帳不受影響。

總結:最高等級為 major,blocking 共 4 條
