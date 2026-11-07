severity: major

以下逐條照最壞時序與資源耗盡的立場查過。r1 的主要改法(宣告另開檔、判誤報只留治理帳、共用一支算命中的函式)都對得上現況程式。問題集中在補進來的段落:預算怎麼分、三處重算、token 與推翻的語意、材料大小。

**逐項答覆**
- 三處各抽兩份快照:共用函式只共用程式碼,沒有共用結果。一次完整流程要重算很多次:`pass` 前機械檢查一次、`--template` 每份一次、記帳每份一次、推送 check 一次。命中超過 30 筆時份數乘上去,見 F3。
- 一般段吃光預算:覆核每次都沒跑,而且是「放行加留帳」,見 F1。
- 同一份結果檔記兩次、`rule-review` 推翻兩次:語意沒定義,見 F4。
- 記帳時工具逾時:沒寫處置,見 F2。
- 每次推送讀 22MB 治理帳:現有讀法(`_ledger_lines_having`)約 0.15 秒,扛得住。但 spec 沒要求用預篩,而且記帳寫入端有問題,見 F6。
- 上千筆命中:材料大小沒有上限,見 F5。
- 子程序殘留:`_lint_run_and_parse` 逾時會整組殺,不是問題。剩下是快照目錄,見 F7。

---

severity: major
blocking: 是
判準:預算耗盡時覆核每次靜默不跑,繞道向量剛好落在最大、最慢的推送上,而且與一般段的處置方向相反。
spec 段落:範圍 7、範圍 3、天花板 4。
問題:覆核只吃「一般段跑完剩下的預算」,沒有保留份額。現況 `_lint_new_run_one` 把「剩餘預算全部」當單條命令的逾時,所以一般段一條慢命令就能吃光 300 秒,覆核直接落入「時間預算用完」。這種情況每次推送都 fail-open,規則包的擋停形同關閉。
- 對照現況:一般段預算用盡記成 `undone kind=budget` 並擋下,覆核卻放行,spec 沒說為什麼相反。
- spec 沒說覆核命令是否套 `per_cmd_floor_sec`,也沒說兩條 sgconfig 命令各算幾份。
- `{LINT_FILES}` 版覆核命令沒有分批(只有逗號版 `{LINT_FILES_CSV}` 才分批)。大改動會撞 E2BIG,得到的不是擋,而是 fail-open。
引句:「覆核命令吃一般段跑完剩下的時間預算。」
引句:「任一種都印一行「覆核沒跑:<原因>」並寫一筆 `code-loop` 閘 fail-open 事件」
佐證:
- `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:42696`:逾時用 `max(1, int(budget_end - now))`,等於整個剩餘預算。
- `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:42677`:預算不足記 `kind=budget`,歸擋。
- `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:41789`:`budget_sec` 300、`per_cmd_floor_sec` 30。

---

severity: major
blocking: 是
判準:`--template` 與記帳兩處沒有時間預算,也沒有處置「逾時、算不出命中」。補進來的段落沒補完。
spec 段落:範圍 2、範圍 5。
問題:`_rule_review_hits(repo_root, diff_range, deadline)` 要 `deadline`,但只有推送 check 有現成預算。`--template` 與記帳誰給 deadline,spec 沒寫。情境側有獨立的 `_KT_SIT_BUDGET`(30 秒),覆核側沒有對等物。
記帳時重算逾時或回「沒跑原因」,spec 也沒寫。照字面,命中清單為空,`seg` 全部「不在」,整份被拒收。代理剛花成本判完的 30 筆全丟,而且拒收訊息講的是「seg 不在命中」,不是「覆核逾時」。
- 同樣會被誤拒的情形:`--template` 到記帳之間,有人用 `lint-waive` 放行了其中一筆。範圍 2 沒說「新增命中」是否排除已放行的,不確定時整份被拒。
- HEAD 前進(例如記帳前多了一個提交)也會讓範圍變了、整份被拒。
引句:「`rule_hits` 的每個 `seg` 要在範圍 2 那支當下算出的新增命中裡,不在就整份拒收」
引句:「新增 `_rule_review_hits(repo_root, diff_range, deadline)`,回(新增命中清單, 沒跑原因清單)」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:39021`(`_KT_SIT_BUDGET = 30.0`,情境側的獨立預算,覆核側沒有)。

---

severity: major
blocking: 否
判準:命中超過 30 筆時,重算成本隨份數線性放大,spec 沒寫快取或上限。
spec 段落:範圍 2、範圍 4、實務隱患「盲判成本」。
問題:共用函式不讀也不寫快取。命中 N 筆有 ceil(N/30) 份,每份的 `--template --part k` 與記帳各重算一次,每次是兩份快照乘覆核命令條數。
- 1000 筆是 34 份,約 68 次重算,另加 `pass` 前一次與推送 check 一次。
- 每次重算的命令集是兩條 sgconfig(62 條規則)。
- 實務隱患只談「派代理的成本」,沒談重算成本。
- 擋下後的出口只有逐筆 `lint-waive`,沒有批次放行。大量命中時唯一的整體出口是 `mode warn` 或 `LUMOS_SKIP_LINT_NEW`。
引句:「三處算出同一組身分。內部照新增告警閘的做法抽兩份快照、跑命令、比對新增」
引句:「每次推送有覆核命中就要派代理,一份最多 30 筆。」

---

severity: major
blocking: 是
判準:重試與重複推翻的語意沒定義,而 S4 只測單筆單次。
spec 段落:範圍 5、範圍 6、用詞「人複查」。
問題:
1. `token` 怎麼產生沒寫。同一份結果檔重記兩次(例如網路或工具中斷後重跑)時:token 若是檔案雜湊,兩次相同,`--batch <token> overturn` 會同時作廢原判定與重判後的新判定;token 若是隨機值,「整份都是已有的格不寫、回 2」的既有語意就和「overturn 後可再判」打架。
2. 「同一格只認第一筆」與「overturn 作廢後可再判」並存,但沒寫「有效判定」怎麼挑。序列「第一判、overturn、第二判、overturn、第三判」,或「agree 之後再 overturn」,誰算有效?
3. 同一筆被單筆 overturn 後,再被 `--batch` overturn 一次,會寫重複事件。S8 統計的「`overturn` 幾筆」會重複計數,進而扭曲「`agree` 至少九成」門檻。
4. batch 的範圍包含 `real` 與 `unsure` 判定。推翻 `real` 沒有行為意義(本來就擋),但仍會計入複查統計。
5. 結果檔頂層混有 `segments` 與 `rule_hits` 時,一邊是已有的格、另一邊是新格,回 2 還是部分寫入,沒寫。
引句:「同一格只認第一筆(照既有);`overturn` 讓那一筆作廢後,同一格可以再判(見範圍 6)。」
引句:「另帶這次記帳的 `token`。只寫治理帳一處,不碰放行檔。」

---

severity: major
blocking: 否
判準:材料大小沒有上限。份數上限是以 seg 計,但每筆 seg 的行數與處數沒封頂。
spec 段落:範圍 4(材料)。
問題:「每份最多 30 筆」計的是 seg(同檔同片段共用一個身分)。每筆卻要給「同片段的每一處」前後各 8 行。
- 同檔同片段若有 500 處(例如常見的 `.value.add`),一筆就是約 8500 行。
- 30 筆可以輕易超出代理的上下文。
- 材料的總行數沒有上限,也沒有「超過就拆分或截斷並標示」的處置。
- 材料超大時,「盲判代理看到完整語境」這個前提本身就不成立。
引句:「這支檔裡同一片段的**每一處**命中行前後各 8 行」
引句:「兩種材料各自分份、各自 `--part` 編號(每份最多 30 筆)」

---

severity: major
blocking: 否
判準:新欄位進單行治理帳,沒有寫入端的行長與並行考量。
spec 段落:範圍 5、實務隱患「治理帳長大」。
問題:spec 估一份 30 筆約 60KB,但那是單行 JSON。記帳是一次整行追加。
- 現有程式碼在別處已承認 O_APPEND 單次寫入要小於 4KB 才有原子保證(`scripts/lumos:31309` 註解)。
- 並行會談是這個 repo 的既知情境,60KB 的單行追加沒有這層保證。
- `unsure` 加仲裁會再寫一列。
- 推翻事件、`rule_hits` 判定列、一般 fail-open 事件都進同一本 22MB 版控帳。
- 讀端這一側,spec 只寫「逐筆驗形狀」,沒有要求用 `_ledger_lines_having` 預篩 token。照字面,每次推送可能對 22MB 逐行 `json.loads`。
引句:「治理帳:同一個 `code-loop` 閘、種類 `blind-judge`,新欄 `rule_hits`」
引句:「每筆判定理由最長 2000 字,一份 30 筆約 60KB 進版控治理帳」
佐證:`/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:21536`(`_ledger_lines_having` 的預篩,spec 沒要求沿用)。

---

severity: major
blocking: 否
判準:spec 內部矛盾,加上接線缺口。
spec 段落:範圍 2 對 範圍 3。
問題:
1. 範圍 2 寫共用函式「不寫任何檔」,同一段又寫它「抽兩份快照」。現況快照會寫 `.lumos/lintbase-*` 目錄與 `lumos-lint-*.sarif` 暫存。被強殺時只有超過一天才會被 `_lint_new_clean_stale` 清,重試越多殘留越多。
2. 範圍 2 要求範圍一律用 `_codeloop_disp_range`,但 `_codeloop_lint_new_step(repo_root, diff_range, tier)` 現在沒有 `marker_branch`、`marker_sha`、`merge_ledger` 參數,一般段用的是原始 `diff_range`。spec 沒寫要改簽名,也沒說覆核範圍與一般段範圍不同時怎麼辦。
3. `_codeloop_disp_range` 在分支頂端已在主線上時回 `(True, None)`、範圍是 None。spec 沒說覆核這時靜默略過,還是記「沒跑」。
4. 推送時一般段與覆核各抽一次快照,同一次推送重複解 git 與 `_lint_new_support` 複製設定檔。
引句:「它不讀治理帳、不寫任何檔。」
引句:「範圍一律用 `_codeloop_disp_range`(表態與情境題盲判共用的那一支)」
佐證:
- `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:74556`:`_codeloop_lint_new_step` 的現行簽名。
- `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:73997`:`_codeloop_disp_range` 可能回 `(True, None)`。
- `/Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj/scripts/lumos:42317`:`_lint_new_clean_stale` 只清超過一天的殘骸。

---

severity: minor
blocking: 否
判準:fail-open 事件沒有去重,工具持續不可用時每次都寫一列進版控帳。
spec 段落:範圍 7。
問題:每次 push check、每次 `code-loop pass`(`mech_only`)都寫一筆。CI 或機器沒裝 ast-grep 時,每次推送固定多一筆。這會弄髒版控的 `docs/.governance-log.jsonl`、增加合併衝突面,而且 `gov --stats` 的 fail-open 計數被灌水。spec 沒寫去重或頻率上限,而 `_gate_failopen` 的既有行為也不去重。
引句:「任一種都印一行「覆核沒跑:<原因>」並寫一筆 `code-loop` 閘 fail-open 事件」

---

severity: minor
blocking: 否
判準:判定綁「版本」的字面不明,可能讓提交壓縮或 amend 使判定失效。
spec 段落:範圍 3。
問題:範圍 3 寫「讀治理帳的規則判定(分支、版本、合併提交那一側…)」。`seg` 是內容雜湊,本來不必綁 sha。如果實作照「版本」綁 head sha,專案規定推送前把本機提交壓成一個,每次壓縮、amend 都讓全部判定失效,要重派代理。S11 與 S12 沒有覆蓋這種情形。
引句:「讀治理帳的規則判定(分支、版本、合併提交那一側照表態那一道 `_disp_bj_source` 的讀法)」

---

**對固定席節點的判斷**
- ‹Systems/kotlin規則包›:不影響。範本只新增宣告與使用說明,不改規則內容。但「提示級預設不接」那句要同步改。
- ‹Systems/pitfalls-code-loop›:會影響它的擋停合約。F1、F2 的 fail-open 方向與 F7 的簽名、範圍問題都落在它管的 `_codeloop_lint_new_step`。
- ‹Systems/linter精選目錄›:不影響行為。僅範本與說明改動。
- ‹Systems/lint-declaration-health›:不影響。覆核宣告另開檔、不動 `lint.json` 驗證器。
- ‹Systems/棧別提問表態閘›:不影響表態合約。但 F4 的 token 與重判語意要避免和「同一格只認第一筆」的既有規則衝突。

最後一行總結:r1 的方向都改對了,但覆核預算沒有保留份額(F1)、`--template` 與記帳沒定預算與逾時處置(F2)、token 與重複推翻語意缺漏(F4)三處,在最壞時序下會變成靜默繞道或整份拒收,建議折掉後再審一輪。
