severity: major

本審查只判「這份 diff 跟 scripts/lumos 既有做法一不一樣」,不找 bug、不評風格。逐問作答,每問先列 file:line 對照,再列 finding。

## 問一:分層與依賴方向

對照:`_drift_check_core`/`_drift_probe_check` 呼叫 `_ns_git`(既有先例,`_drift_range_events` scripts/lumos:25586 在這次改動前就已這樣用)、`_ProbeTree` 呼叫 `_nodehome_list`/`_nodehome_layout`/`_nodehome_is_test`/`_nodehome_code_kind`/`_nodehome_cat_blobs`(計劃〈做法〉借用清單第③④項明寫借這些)、`_probe_is_candidate`/`_ProbeTree.one` 的 status 條件用 `tenv.resolve(link_target(...))`(跟 `_drift_plan_followups` 既有寫法一致,不是另開連結解析)。這幾條依賴方向都跟計劃裡登記的借用清單對得上,沒有違規。

只有一處呈現層(presentation)跟指令層(orchestration)的既有分工被打破:

## F1 cmd_drift_scan 把 probe 問題清單的印表邏輯直接寫在指令函式裡,沒有併入既有的 _drift_scan_print
severity: minor
blocking: 否 — 結構仍對(印的東西沒錯),只是同一份輸出邏輯現在分裂成兩處
引句:「    _drift_scan_print(at, left, done, bad)」
1. `cmd_drift_scan` 既有寫法是把全部文字輸出邏輯收在 `_drift_scan_print(at, left, done, bad)`(scripts/lumos:26247)裡,指令函式只算資料、呼叫一次印表函式。
2. 這次新增的 `probs`(乙的問題清單)沒有傳進 `_drift_scan_print`,而是緊接著在 `cmd_drift_scan` 本體另外寫一段 `if probs: print(...)`(scripts/lumos:26239-26243)。
3. file: `scripts/lumos:26238`(呼叫既有印表函式)對照 `scripts/lumos:26239-26243`(新增的內聯印表)——同一個指令現在有兩份印表邏輯,一份走既有的分工、一份沒有。改法是把 `probs` 當參數傳給 `_drift_scan_print`,由它統一印。

## 問二:命名與錯誤處理

## F2 _ProbeTree、_probe_changes、_probe_is_candidate、_probe_judge、_probe_prepare 只被 drift 呼叫,卻不像同組的 _drift_probe_check/_drift_probe_scan 一樣掛 _drift_ 前綴
severity: minor
blocking: 否 — 命名不一致但呼叫關係與行為都對
引句:「def _probe_prepare(root, base, tip, vault_rel, deadline, override_base):」
1. 全檔既有慣例是「同一支功能的私有函式共用同一個前綴」:`_drift_*`(`_drift_check_core`、`_drift_state_findings`、`_drift_tree_env`…)全部只服務 drift 功能;`_ns_*`、`_nodehome_*`、`_lens_*` 同理。
2. 這次新增的 `_revisit_split`/`_probe_parse`/`_probe_lines`/`_probe_value_err`/`_probe_bad_path`/`_probe_named_err` 確實被 E5(doctor)、`_ns_revisit_violations`(第一層)、`_note_audit_items`(第二層)、drift 四處共用(scripts/lumos:2017、24191、24196、24730、25760),不掛任何單一功能前綴合理,跟 `_notelines_*` 這種「共用領域」前綴的既有做法一致。
3. 但 `_ProbeTree`(scripts/lumos:25776)、`_probe_changes`(25851)、`_probe_is_candidate`(25887)、`_probe_judge`(25956)、`_probe_prepare`(25940)經查只有 `_drift_probe_check`(25906)/`_drift_probe_scan`(25974)/`cmd_drift_scan` 呼叫(全域搜尋 `_ProbeTree(`、`_probe_changes(`、`_probe_is_candidate(`、`_probe_judge(`、`_probe_prepare(` 只在這三處出現),呼叫範圍跟 `_drift_probe_check`、`_drift_probe_scan` 一模一樣,卻沒有掛 `_drift_` 前綴——同一段「乙」程式碼裡,呼叫範圍相同的姊妹函式一半有前綴(`_drift_probe_check`、`_drift_probe_scan`)一半沒有(`_probe_prepare`、`_probe_judge`、`_probe_is_candidate`、`_ProbeTree`)。

## F3 _ProbeTree 用物件內的 self.ok 旗標編碼「這一版讀不到」,既有同類抽象(建某一版快照)一律讓建構函式回 None
severity: minor
blocking: 否 — 呼叫端 `.one()` 一律先檢查 `self.ok`,行為上不會漏判,只是失敗編碼方式跟鄰居不同
引句:「        self.ok = lst is not None」
1. 既有「建某一個版本的快照,供後續重複查詢」這個角色,原本的做法是工廠函式在讀不到時直接回 `None`,物件只在成功時才被建出來:`_nodehome_side(...)` 讀不到 `_nodehome_list` 就 `return None`(scripts/lumos:22889-22892),物件 `_NodehomeSide()` 只在確定讀得到之後才建;`_drift_tree_env(root, where, vault_rel, ...)` 一樣是「git 失敗回 None」(scripts/lumos:25535-25541 docstring 明寫)。
2. `_ProbeTree.__init__`(scripts/lumos:25776 起)反過來——不管讀不讀得到都把物件建出來,失敗與否改記在 `self.ok` 這個旗標上,呼叫端要記得每次先查 `.ok`。
3. file: `scripts/lumos:22886-22894`(`_nodehome_side`,同角色、回 None 的既有寫法)對照 `scripts/lumos:25776-25784`(`_ProbeTree.__init__`,新的 ok 旗標寫法)。功能上不算錯(`.one()` 內部有擋),但同一個「一版快照物件」的角色在同一支檔案裡有兩種失敗編碼形狀。

## 問三:第二種做法(有沒有又寫一套已有的工具)

## F4 _probe_changes 手刻一份 git diff --name-status -z -M 的 token 解析,跟同一支 diff 裡 _probe_prepare 已經在用的 _nodehome_name_status 是兩份實作
severity: major
blocking: 是 — 引入第二種做法,而且同一份 diff 裡兩個姊妹函式各用一套,行為分岔的風險是真的(見下方重現)
引句:「        if code in ("R", "C") and i + 2 < len(toks):」
1. `_nodehome_name_status(raw, norm=True)`(scripts/lumos:23021)已經是全檔唯一、既有的 `git diff --name-status -z [-M]` 輸出解析器,`_nodehome_commit_groups`、`_nodehome_merge_own_changes` 都在用,回 `(改到的路徑, 改名新→舊, 刪掉或改名掉的舊路徑)`。
2. 這次新增的 `_probe_changes`(scripts/lumos:25851-25884)自己重新寫一份幾乎一樣的 R/C token-walk(`toks[i][:1]`、`i += 3`/`i += 2` 那段,scripts/lumos:25860-25874),用來算 `touched` 集合與 `shape` 旗標,而不是呼叫 `_nodehome_name_status(raw)` 拿 `paths` 再自己疊一層算 `shape`。
3. 更明顯的是同一份 diff 裡的姊妹函式 `_probe_prepare`(scripts/lumos:25940-25953)在做幾乎一樣的事(對同一種輸出格式抽路徑)時,正確地呼叫了 `_nodehome_name_status(rn)[1]`(scripts/lumos:25953)。同一支 diff、同一個「乙」區塊,一個呼叫既有解析器、一個手刻同款解析器,不是「不知道有這支」的問題。
4. file: `scripts/lumos:23021-23041`(`_nodehome_name_status` 既有實作)對照 `scripts/lumos:25860-25874`(`_probe_changes` 手刻的第二份)與 `scripts/lumos:25953`(同一份 diff 裡正確呼叫既有函式的對照組)。
5. 重現(結構性,不是輸入造出來的邊界案例):`_nodehome_name_status` 對改名(`R`)只把新路徑併入 `gone - src`,如果之後有人要在 `_probe_changes` 加同一種「改名要不要算刪除」的邏輯,兩份 R/C 解析各自維護,任何一邊修 bug(例如改名大小寫正規化、章魚合併的退路)都要記得改兩處——這正是「第二種做法」要擋的那類分岔風險。

## F5 _probe_py_def_re 用行首寬鬆正則掃 Python def/class,跟既有「在某個提交/某段文字裡找 Python 符號定義」的做法(ast.parse)是兩套,而且重現了那套正則做法過去被判過 blocker 的同一種假陽性
severity: major
blocking: 是 — 引入第二種做法;且可具體重現假陽性(見下方)
引句:「        return re.compile(rf"^[ \t]*(?:async[ \t]+)?def[ \t]+{n}\b", re.M)」
1. 全檔既有找「Python 原始碼文字裡的頂層 def/class」的做法是標準庫 `ast.parse`,不是正則:`_lens_py_defs(text)`(scripts/lumos:31073-31087)"標準庫 ast,沿 slim-gen/slim-scan 先例"、`_py_declared_methods`(scripts/lumos:4489-4516)更明寫"★不要用放寬的正則去掃★(代碼審 r2 通才席 blocker):…docstring 裡縮排的程式範例會被當成真宣告——實測本 repo 自己的測試檔就多算 148 個"。
2. `_probe_py_def_re(name, test)`(scripts/lumos:25769-25774)反過來就是那支被判過 blocker 的做法:`^[ \t]*(?:async[ \t]+)?def[ \t]+{n}\b`,行首允許任意縮排,而且 `_ProbeTree.corpus()`(scripts/lumos:25805-25814)讀進來的是整份原始檔文字(不含 docstring/字串的任何剝離,`b.decode("utf-8", errors="replace")` 原樣保留),直接拿去給 `pydef.search(txt)` 比對(`_ProbeTree.one`,呼叫在 corpus 之後同一支方法裡)。
3. file: `scripts/lumos:4492-4496`(`_py_declared_methods` docstring,明寫這個假陽性的實測後果與 148 個誤算的前科)對照 `scripts/lumos:25769-25774`(`_probe_py_def_re`)與 `scripts/lumos:25805-25814`(`corpus()` 讀進未剝離的原始文字)。
4. 重現(可當場推導,不需要跑測試):一支被 `when-symbol:` 指到的 Python 檔裡如果有這種 docstring:
   ```python
   def helper():
       """範例:
       def helper():
           pass
       """
   ```
   `_probe_py_def_re("helper", False)` 的正則 `^[ \t]*(?:async[ \t]+)?def[ \t]+helper\b` 對 docstring 縮排那行 `    def helper():` 一樣會比對成功(它不檢查是不是在字串裡),`_ProbeTree.one(("symbol", "helper"))` 回 True 不會因為只有 docstring 裡有假的一份而改變結果——但如果條件寫的是一支「還沒實作、只在 docstring 範例裡提到函式名」的檔,回頭條件會被判成「已經成立」而擋下推送,這正是 `_py_declared_methods` 當初升級成 ast 解析要擋的那種誤判,現在在 `_probe_py_def_re` 這條新路徑又重新出現。

## 總結
最嚴重等級:major。blocking 共 2 條(F4、F5)。
