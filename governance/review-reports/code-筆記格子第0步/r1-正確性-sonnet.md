severity: major

審查對象是 `d7314ecd..bddb664c` 的 diff。我在 `rw` 的乾淨 clone 裡驗證，沒有改 repo。

已跑且全綠的子集：`slots`、`rule_`、`note_tags`、`stale_rules`、`symbol`、`context_marker`、`lint_context`、`doctor_soft`、`note_convention`、`note_shape_`（178 案例）。`negation`、`t_gov_stats`、`spec_gate_door`、`slim_`、`lint_` 在背景跑，我交稿時還沒回報，這份報告不含它們的結果。

另外我把 base 和 tip 兩版的 `context_marker_warnings` 套在現有 453 篇筆記上比對，警告零差異，「舊行 lint 結果不變」的承諾在現有語料上成立。

**C1** 提交時的 RULE 提醒對新文法的行是瞎的，違反計劃條款 [S3]
- 輸入：暫存 `RULE:大額退費要人工核可 [依據:人]`，沒有 since、沒有 retire。`rule_lifecycle_warnings` 的 `if not new:` 分支把缺鍵檢查整段跳過，`slot_check` 又不在提醒路徑上。
- 實測輸出：不帶 `[依據:人]` 的舊寫法會印出「缺 [since:…]、[retire:…]」；帶了 `[依據:人]` 的新寫法 stderr 一個字都沒有，`rule_lifecycle_warnings("x [依據:人]")` 回 `[]`。
- 新寫法的 `[status:superseded]` 沒寫 `[被取代:]` 同樣沒提醒。
- 這是範本現在教人寫的格式。新寫法的 `[confirmed:壞日期]` 也不會被提醒。
- 範本教的格式在提交時是死角，只剩手動跑 lint 才唸得到。計劃 [S3] 寫的是「新寫的 RULE 行缺 since 或 retire，提交時應印出提醒」，沒限定舊寫法。
- 綁定的測試 `t_rule_lifecycle_warns_at_commit` 只餵舊寫法，所以全綠。
- 重現：clone 裡 `_ns_repo()` 加 `_ns_note(root, summary="KEY:x\nRULE:大額退費要人工核可 [依據:人]")`、`_ns_stage`、`_ns`，輸出為空、rc0。
引句:「if not new:      # 新文法的截斷與缺鍵由 slot_check 唸(筆記格子),這裡只管舊寫法」
佐證: file: `scripts/lumos:3423`、file: `scripts/lumos:26562`
severity: major
blocking: 是 — 條款 [S3] 的提醒在範本教的格式上整段失效，測試沒咬住

**C2** 範本、AGENTS.md、CLAUDE.md 提到一個不存在的參數 `--slots`
- 範本會注入每個消費專案，內容寫著「專案掛鉤開了格子檢查（`note-shape --staged --slots`）後提交時擋」。
- 重現：`python3.14 scripts/lumos note-shape --staged --slots` 輸出「擋下:不認得這幾個參數:--slots」。
- 程式裡只有一行註解提到 `--slots`。程式註解說明這是第 1 步，範本卻在第 0 步就寫了。
引句:「必有的格子缺了 lint 會唸，專案掛鉤開了格子檢查（`note-shape --staged --slots`）後提交時擋：」
佐證: file: `scripts/lumos:3457`
severity: minor
blocking: 否 — 只是文字提前，條件句沒說現在就擋

**C3** SEE 的 lint 把合法的別名連結和錨點連結當成句子
- `SEE:[[Systems/甲]]、[[Systems/乙|別名]]` 和 `SEE:[[Systems/甲#章]]` 都被唸「SEE 只放 [[連結]]…要寫句子」。
- 原因是 `_NS_POINTER_ONLY_RE` 的連結只收 `[^\]|#]+`。
- 同一個 diff 裡 `_plan_system_links` 刻意接受 `|` 和 `#`，`t_slots_see_prefix_and_links` 用的正是 `[[Systems/乙|別名]]`。
- 範本寫的是「至少一個 `[[連結]]`」。
引句:「if "[[" not in body or not _NS_POINTER_ONLY_RE.match(body):」
佐證: file: `scripts/lumos:26182`、file: `scripts/lumos:3586`
severity: minor
blocking: 否 — 只是誤報提醒，不擋提交

**C4** 變異測試顯示格子檢查的值判斷大半沒被測試咬住（鏡頭 4）
- 我在 clone 裡逐項把判斷拿掉，再跑上面那批子集，下列變異全部 0 failed：
  - 條件式必有（`[retire:人裁]` 另必有 `[until:]`）整段拿掉。
  - 列舉值檢查（`[依據:]`、`[來源:]` 的可選值）整段拿掉。
  - 散文 `[retire:…]` 不再報「不是機器式」。
  - PITFALL 三選一檢查拿掉。
  - `[recheck:]` 格式檢查拿掉。
  - `[status:superseded]` 缺 `[被取代:]` 的報錯拿掉。
  - 度量的未知閘檢查拿掉。
  - `_SLOT_NEW_ONLY` 少 `因`、`recheck`。
- 對照組：把必有鍵的 `missing` 清空，`t_slots_single_table` 會紅，所以測試跑得起來，是這些判斷沒有案例。
- 範本表和程式表的同步測試只比必有鍵、三選一、條件式、列舉值這四個投影。
  - 抓不到 `_SLOT_KEYS`、`_SLOT_NEW_ONLY`、`_SLOT_REPEATABLE`、機器式 retire 清單這幾處和範本的漂移。
  - 範本「常用選填」欄的鍵也沒人釘。
引句:「missing += [f"[{need}:]" for pf, k, trig, need in _SLOT_CONDITIONAL」
佐證: file: `scripts/lumos:3608`、file: `scripts/test_lumos.py:30356`
severity: minor
blocking: 否 — 現在沒有行為錯，但這些規則沒有測試保護

**C5** reference.md 說骨架空行任何前綴都不算違規，但 lint 實際會唸
- `context_marker_warnings("WHY:\nRULE:\nFACT:")` 對三行各回一條警告，base 版也一樣。
- `slot_check` 開頭那句 `if not body: return []` 從 lint 走不到，因為空行不可能被判成新文法。
- `t_slots_field_parser` 只直接呼叫 `C("FLOW","")`，沒走 lint。
引句:「冒號後什麼都沒寫的骨架行（任何前綴）不算違規。」
佐證: file: `scripts/lumos:3652`
severity: minor
blocking: 否 — 文件與行為不一致，沒有新增誤擋

**C6** 把 FLOW/DEP 改名成 `SEE:` 就能繞過提交時擋「沒寫來源的現況描述」
- 重現：`context_marker_warnings(行, rules=_NOTE_SHAPE_PREFIX_RULES)`，`FLOW:Redis 連線上限是 200` 回 1 條，`SEE:Redis 連線上限是 200` 回 0 條。
- 原因是 note-shape 的前綴表沒有 SEE，而 `_ns_check_line` 把 SEE 當成已認得的前綴放行。
- 只有 lint 會提醒「SEE 只放連結」，但 lint 不擋。
- 計劃 [S4] 把「SEE 夾句子要擋」放到第 1 步，所以這可能是已知範圍，但第 0 步範本已經教人用 SEE。
引句:「SEE", "RETIRE-IF"}」
佐證: file: `scripts/lumos:26230`、file: `scripts/lumos:26233`
severity: minor
blocking: 否 — 計劃把這個擋排在第 1 步

**無問題的查證**
- 例外隔離：`_ns_tag_hints_collect` 和 `_ns_tag_hints_emit` 各自 try/except，`rc` 不受影響，測試 `t_note_tags_hints_isolated` 咬得住。
- 衍生資料：`_plan_system_links` 讀 SEE 與 DEP 同一套抽取，沒有多算或少算。
- 治理帳去重：hinted 事件的去重鍵含 `check`，tag-hints 和 negation 不會合併。
- 時間：S16、`slot_check`、`rule_lifecycle_warnings` 都取本機日期，沒有日期不一致。`commit_time` 在此 diff 沒有任何呼叫端，未來日期檢查現在只在直接呼叫時生效。
- 新舊分流：`context_marker_warnings` 的新舊分支用 `continue` 互斥，一行不會被兩邊都唸。新專屬鍵加在 KEY、TEST 這類不在 `_SLOT_REQUIRED` 的前綴上，會兩邊都不唸，屬設計如此。
- pitfalls 鏡頭：落在新增行上的 ruff 命中只有 PLC0415（函式內 import，全檔常態）、PLR0911（回傳點太多）、PLR0913/PLR0917（測試輔助函式參數太多）、E501（一行 215 字，在 NEW_HINT 字串）。這是我自選的規則集，不是專案的 ruff 設定。沒有 C901 複雜度告警，沒有構成缺陷的命中。

**圖譜鏡頭**
- `lumos impact --diff` 列出的固定席沒有被破壞。
- 判「不影響」的有 `lumos-cli-read`（search 排除 superseded）、`lumos-cli-lifecycle`（re-inject 只改 sentinel 之間，範本內容換了但注入機制沒動）、`bound-tests-gate`、`design-loop`、`授權與歸屬`（沒碰白名單與檔頭）、`測試假綠形態`。
- `節點範圍與索引守衛`「新段必須排在 E3 之後、H 之前，不進 S 到 E1 窗口」：S16 放在合約條數段之後，`t_doctor_soft_sections_truncate_by_default` 實跑 4 passed。S16 沒新增閘名，不需登記已知閘名單，`warn_soft` 不計入 issues。
- `規格閘` 和 `筆記內容閘` 沒有合約行，新增的 WHY 與實作一致。
- 要補的一點：`Systems/筆記內容閘` 新增的 WHY 說提醒自成一套、不影響否定現況句，這句成立。但它沒說 tag-hints 對新文法的 RULE 看不到缺鍵（C1），這個限制該寫進去。

**角色鏡頭**：派工尾端沒有附前端或後端卡，略過。

最高嚴重度 major,blocking 1 條(C1)
