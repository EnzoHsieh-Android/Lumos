severity: major

我照字面把每個機制各走過一個具體輸入。無法確認的地方標 ⚠。本機沒有 `ast-grep`,規則實際命中沒跑,SARIF 層的行為從程式與型錄推。

## F1 工具沒裝的處理與既有新增告警閘、既有情境題相反,散文對現況的描述也不對
severity: major
blocking: 是(照字面實作,所有沒裝規則包的環境整片擋住,與同一道閘既有做法相反)
- 對應段落:範圍 2 的逾時說明、S10 與預期值表末列。
- 引句:「逾時這一點跟一般新增告警不同(一般段沒跑完是擋)」
- 問題:`_lint_new_classify` 把「工具沒裝/逾時/拉不到規則」歸 `env`,結果是自動放行並記帳。只有「預算不足沒跑到」與「參數太長」才擋。所以「一般段沒跑完是擋」不成立,命令逾時在一般閘本來就是 fail-open。
- 引句:「算不出來(工具沒裝、git 失敗)丟無法驗證」
- 預期值表 S10 也寫「ast-grep 沒裝 → 無法驗證、擋」。
- 問題:既有表態閘對「型錄或自檢程式找不到」明文選「環境不可用:提醒、記帳、不擋,消費專案 CI 沒裝工具鏈時也不會整片紅」。本案反過來選擋,而且沒給理由。
- 走一遍:消費專案 CI 沒有 ast-grep,也沒有 `$HOME/harness/lumos-toolchain`。`lint.json` 宣告了規則包後,CI 上每一次 Kotlin 推送都在「重算命中」時判無法驗證而擋下。作者沒有出口,因為本案刻意不新增放行出口。
- file: `scripts/lumos:42405` `_lint_new_classify`:`env_undone` 走 `autopass`,只有 `hard_undone` 擋。
- file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:145` 寫「照新增告警閘『工具沒裝 → 自動放行並記帳』的先例」。
- 判準:S10 的預期行為與同閘既有規則相反,且造成 CI 全擋。

## F2 命中題的適用性在 `--no-lint` 的 regex 層算,還是跑 ast-grep,spec 沒交代,兩種讀法都壞
severity: major
blocking: 是
- 對應段落:範圍 3 第一點、範圍 2、不做 5、天花板 5。
- 引句:「`lumos pitfalls --dispositions-template` 在有規則命中時多一題 `kt-rule-hits`」
- 事實一:`--dispositions-template` 固定走 `_pitfall_diff_collect(..., no_lint=True)`,程式註解寫「只跑 regex 層」。
- 事實二:`code-loop check` 取 tier 與適用題,以及 pre-push 的三處,也一律帶 `--no-lint`。
- 事實三:`_kt_situation_apply` 在 `config = None if no_lint` 那個分支之外執行,而命中題的適用性要靠跑 ast-grep 才知道。
- 讀法一,照 `_kt_situation_apply` 的位置放:每次 pre-push 的 pitfalls 呼叫、tier 判定、樣板各自觸發 4 次 ast-grep(2 份設定 × 前後 2 份快照),破壞「`--no-lint` 是快速層」的契約,也與範圍 2 想守的時間預算衝突。
- 讀法二,放在 `no_lint=False` 之內:`code-loop check` 與樣板路徑永遠是 `no_lint=True`,命中題永遠不適用。`_dispositions_verdict` 對 `applicable` 為 false 的題直接跳過,整道新閘等於沒接。
- 另一個接縫:情境題算段失敗時,程式保留 `applicable` 並寫 `situation_error`,到推送前再算一次。命中題逾時 fail-open 時,「題還在不在」沒有對應規則,可能直接不適用而漏記。⚠ 這點 spec 沒寫,走哪邊要實作者自己猜。
- file: `scripts/lumos:64986` 與 `scripts/lumos:74591`。
- file: `scripts/lumos:39397` `_kt_situation_apply`。

## F3 治理帳沒有規則 id 和程式片段,`--fp-samples` 匯出和 `gov --stats` 逐規則統計都算不出來
severity: major
blocking: 是
- 對應段落:範圍 3 答案形狀、範圍 4 結果檔、範圍 5、範圍 6、S6、S8。
- 引句:「答案形狀:`status: satisfied`,`hits: [{seg, answer: fp|risk, reason, issue?}]`」
- 引句:「結果檔 `rule_hits: [{seg, verdict: real|false|unsure, reason}]`」
- 引句:「各寫成 `<輸出目錄>/<規則 id>/review-fp-<seg>.kt`」
- 問題:帳上只有 `seg`(規則、檔名、片段的雜湊前 16 碼,無法反推),沒有 `rule`、`file`,更沒有程式片段。抽查材料只印到 stdout,沒有存起來。
- `--fp-samples` 要寫 `<規則 id>/` 目錄與檔案內容,只能重算命中。但帳只記了 head_sha,分支可能已壓縮、合併或刪除,版本不一定還在。spec 沒寫重算失敗怎麼辦。
- S8「每條規則列」要從 seg 對回規則,同樣無從對起。既有情境題統計靠 `segkey`(第一盲判事件帶 file 與 rows)才對得起來,本案沒有等價物。
- 統計的資料層也接不上:`_gov_row` 只透傳白名單欄位,不含 `branch`、`head_sha`、`rule_hits`,而範圍 6 要「同一分支只取最後一筆表態」。spec 沒列這處要改。
- 反例:`_gov_situation_collect` 現行語意是每格取最早一筆,與本案「取最後一筆」不同,兩者共用同一個帳讀取層時要分開。
- file: `scripts/lumos:17575`(`_gov_row` 的欄位清單)與 `scripts/lumos:17110` `_gov_situation_collect`。
- 判準:範圍 5、6 的輸出在資料層無法產生。

## F4 前後各 8 行的片段當誤報樣本,保不住規則依賴的外層脈絡,`--fp-regress` 的 M 會失真
severity: major
blocking: 是
- 對應段落:範圍 4 材料、範圍 5 匯出內容、S7。
- 引句:「每筆給檔名、命中處前後各 8 行」
- 引句:「內容是抽查材料裡那幾段程式」
- 事實:規則大量用 `inside:` 與 `stopBy:`,例如 `kt-livedata-setvalue-background` 要往外找 `withContext(Dispatchers.IO) { … }`。規則包 `rules-review/` 與 `rules-hints/` 共 25 份檔案計數裡有 15 份用到。
- 走一遍:真實誤報的命中行在 40 行 `withContext(IO)` 區塊深處。前 8 行不含開頭那行,截下來的片段括號不平衡,`inside` 條件不成立。
- 結果:匯出的樣本對原規則本來就不命中,`--fp-regress` 印「仍命中 0」。這會被當成「改形狀後誤報樣本不再命中」,但其實是樣本壞了。
- spec 沒要求匯出時驗證「這份樣本在當時的規則下確實還會命中」,也沒用既有情境題那種以宣告為單位的 `material`。
- ⚠ 本機沒有 ast-grep,沒能實測片段是否還命中。`inside` 依賴與括號不平衡是從規則檔讀到的。
- 判準:d6 的回測功能,依規格字面做出來的結果是錯的。

## F5 `_kt_rule_hits` 與 `_lint_new_run_cmds` 的描述對不上現況,「不讀放行檔」「只回新增」都沒有現成接口
severity: major
blocking: 是
- 對應段落:範圍 2。
- 引句:`_lint_new_run_cmds` 那一支,抽兩份快照、只回新增
- 事實:`_lint_new_run_cmds` 只負責在傳進來的 `sides` 上跑命令,回 `(base_claims, head_claims)`,既不抽快照也不比差。
- 抽快照(`_lint_new_extract`、`_lint_new_support`)、命令分派(`_lint_new_cmd_targets`)、`_lint_new_sep_split`、`_lint_new_oversize`、比差(`_lint_new_diff_claims`)和暫存目錄清理,都內嵌在 `_lint_new_tools` 一支函式裡。`_lint_new_tools` 還吃 `waivers`、`werr`,放行檔讀不了就自動放行。
- 所以「一支函式」要嘛重構 `_lint_new_tools` 抽出共用核心,要嘛抄一份。spec 沒選,也沒說。
- 抄或抽時的未定項:
  - 超過檔案大小上限的檔(`oversize`)與路徑含分隔字元的檔,一般閘是擋,本題照字面就是靜默略過。
  - 命令沒有檔案佔位符時,一般閘降級為 `report_only`,本題整個沒有命中,也沒有「沒檢查」的提示。
  - 「參數太長」被併進 fail-open。這不是逾時,是確定性的,而且作者能控制(多改檔)。一般閘明文說「參數太長不是環境問題…不歸自動放行」。{LINT_FILES} 不分批,檔多的推送恰好整題跳過。
- 另外,命中資料欄寫的是 `lines`,但 SARIF 解析出的 claim 只有 `line`、`end_line`。命中題把 `--config` 換成同目錄 `sgconfig-review.yml` 時,如何辨認「指到規則包的參數」(`--config=` 寫法、含 `$HOME`、相對路徑、使用者自己也叫 sgconfig.yml 的檔)也沒寫。
- file: `scripts/lumos:42599`(`_lint_new_tools` 內的快照與比差),`scripts/lumos:42664` `_lint_new_run_cmds`。

## F6 d5 改裁後「出處不全的 7 條只提醒」被靜默拿掉,但原則沒有被推翻
severity: major
blocking: 是
- 對應段落:Q1 文字、不做、決策 d1 與 d5。
- 引句:「建議:要擋,跟新增告警同一句擋下與同一個放行出口;出處不全的 7 條例外,只提醒」
- 引句:「不替出處不全的提示級規則補出處」
- 問題:Q1 的文字與 d1 的理由寫的原則是「依據不足的規則不准擋人」。d5 把整題改成「沒交代就擋」,沒交代的新命中一律擋,包含那 7 條出處不全的提示級規則,而且沒有任何一處說明這個例外為什麼取消。
- 還有現行 WHY:`kotlin規則包` 規定「查不到的列標(出處不全),引用它的規則只准提示級」,也就是這一級的意義就是不擋。本案把整個提示級改成擋,卻沒翻案這條 WHY。
- 抽查材料還把這些列的「標準寫法」當成判準給代理看,可是那些標準寫法依 WHY 本來就沒有官方出處。
- 走一遍:作者新增一筆其中一條出處不全規則的命中,不答就推不上去。這條規則的依據,按本專案自己的定義不夠擋人。
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:20`。
- 判準:新舊決策銜接處丟了一條仍然有效的限制,而且影響擋停範圍。

## F7 預設不掃測試檔,測試專用規則整組不會有命中
severity: minor
blocking: 否(不會做出錯誤擋停,只是與「62 條一起處理」的覆蓋宣稱不符)
- 對應段落:用詞、範圍 1。
- 引句:「語意覆核級(`rules-review/`)12 條與提示級(`rules-hints/`)50 條,共 62 條」
- 事實:命中題沿用新增告警閘的快照與檔案過濾。`_stack_changed_ok` 預設排除測試檔,`lint_new.include_test_paths` 預設為空。`rules-review/testing.yml` 與 `rules-hints/testing.yml` 共 7 條規則有 `files:` 限定在 `src/test*` 一類目錄,預設永遠沒有命中。
- 知識圖譜 `linter精選目錄` 第 199 行已經寫了要自己加 `include_test_paths`。本案範圍 7 改範本時只寫「宣告了 `sgconfig.yml` 就自動接覆核兩級」,沒要求同步設這個。
- file: `scripts/lumos:63841` `_stack_changed_ok`,`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:199`。
- ⚠ 7 這個數字是 `testing.yml` 裡 `files:` 區塊的粗數(1 + 6),沒逐條確認都是只列測試目錄。

## F8 統計門檻的分母口徑沒定,小樣本會被列成候選
severity: minor
blocking: 否
- 對應段落:範圍 6、S8。
- 引句:「答過至少 20 筆、fp 佔八成以上、而且抽查判 false 至少九成」
- 問題一:20 筆下限只管作者答案,「抽查判 false 至少九成」沒有最低抽查筆數。作者答 20 筆、fp 16 筆,只要抽查了 1 筆而且判 false,就是 100%,被列為「改形狀候選」。`unsure` 算不算分母也沒說。
- 問題二:「答過」按分支最後一筆表態算。但同一個 seg 在不同分支重答(換分支名、cherry-pick、重開分支)會被重複計入,可以把筆數灌到 20。
- 問題三:升擋候選只看 fp 少於一成,而 `risk` 與 `fp` 同樣只要寫理由就能過。`risk` 偏多的規則會被誤當成「真問題多」。spec 在天花板第 4 點承認偏保守,沒有承認這一點的偏向。

## F9 幾處小的不一致
severity: minor
blocking: 否
- 理由長度規則:
  - 引句:「`reason` 去空白後至少 10 個字、有實字、最多 500 字」
  - 既有 `_dispositions_reason_ok` 的規則是去空白標點後 CJK 至少 10 字,或總長至少 25 字。英文 `false positive`(13 字元)照本案規則可過,照既有規則不過。同一道閘內有兩套標準。
- 同一個 seg 對應多處命中:
  - `_lint_new_diff_claims` 按次數算新增,回的是排在後面的那一筆。基準有 1 處、現在有 2 處,抽查材料可能指到舊的那一處而不是作者新增的那一處。
  - 「每筆都要有答案」按 seg 還是按命中,spec 沒講。「多答 N 筆」的計法也跟著不定。
- 範圍 7 的文字落點:
  - 引句:「`skills/kotlin-idioms/checks-catalog.md` 統計節「語意覆核級要等計劃接上」那句」
  - 該檔「統計」節(第 870 行起)沒有這句。對應文字在「輸入與口徑」第 11 行,另有 7 處列的接電方式欄寫著「接上前不擋」,同樣會過期。範圍 7 只列一句,會漏掉這些列。

## 已讀,無 finding 的部分
- 用詞、不做、回退、天花板、依據來源表:已讀,無 finding(PRIOR-ART 引用的三個網址我沒外查,不列 finding)。
- 範圍 1「`.lumos/lint.json` 格式不動」:`sgconfig-review.yml`、`sgconfig-hints.yml` 實際存在,各自只載 `rules-review`、`rules-hints`,不與 `sgconfig.yml` 重複計命中。
- 範圍 4 盲判事件不帶 `role`、`blind_judge`:`_kt_bj_event_ok` 缺欄回 False,`_gov_situation_collect` 與 `_kt_bj_read` 都會略過這種事件。「舊版情境盲判照缺欄略過」成立。
- 範圍 3 用 `_codeloop_disp_range`:合併提交時用 `merge-base(主線, 版本)..版本` 把主線帶進來的碼排除,走一遍成立。
- S1 與 S7 的規則 id:`kt-livedata-setvalue-background`、`kt-mutate-state-collection` 確實在 `rules-review/state.yml`。
- 規則訊息以 `[型錄編號]` 開頭(`message_problems` 要求),所以型錄兩欄可以由訊息前綴對到主表列。
- 但主表一列對多條規則,範圍 4 的「對應型錄列」要以前綴為準,spec 沒寫,實作時要自己補。

## 實務隱患鏡頭
- 時間與資源:有 F2、F5。命中重算在 pitfalls 與 check 兩處各跑,有快取但沒說快取失效條件,也沒說 pitfalls 的 `--no-lint` 是否擋住它。
- 治理帳膨脹:spec 已列隱患,F3 另指出帳裡的資料不足以支撐匯出與統計。
- 資安與外送:沒有新增外送。`--fp-samples` 把消費專案程式寫進工具鏈,spec 已列為人工帶回。
- 偽造與繞過:作者答 `fp` 的理由只擋空答。spec 已承認(天花板 1)。F5 另列兩個確定性的略過路徑(檔太大、參數太長),作者能控制。
- 可逆性:回退一段已說明,舊版對未知題號寫側會報「不是題目表裡的 id」。不影響退回後的讀取。
- 金流、個資:無,本功能不碰。

## 固定席逐條判
- `Systems/棧別提問表態閘`:本案會破壞它宣稱的行為。該節點明文「環境不可用、不擋、CI 沒裝工具鏈不整片紅」,S10 的「沒裝就擋」與它相反(F1)。
- `Systems/pitfalls-code-loop`:本案會牽動它的 `pitfalls --diff --no-lint` 快層契約(F2)。
- `Systems/kotlin規則包`:本案會破壞它的 WHY「出處不全的列引用的規則只准提示級」(F6)。型錄自檢的 `--fp-regress` 與好例檢查擴到兩級本身不影響既有檢查,`REVIEW_FP_PREFIX` 的跳過邏輯可以直接延伸。
- `Systems/linter精選目錄`:不影響其合約。它的「提示級預設不接」與「新增告警閘預設排除測試檔」兩句會讓 F7 的覆蓋缺口浮出來。

總結:最高等級為 major,blocking 共 6 條
