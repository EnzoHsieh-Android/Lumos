severity: minor

# 架構對齊審查 r1(回頭條件寫法補齊)

審查範圍:/tmp/code-revA-r1.patch 全部 hunk(scripts/lumos、scripts/test_lumos.py、兩份技能手冊、四篇圖譜筆記)。repo 佐證在 rw 工作樹,行號以該樹為準。我對 `_ns_revisit_violations`、`_revisit_closed`、`_revisit_misplaced` 各跑了一次 in-proc 實驗(/tmp/codeRevA/exp_arch.py)。

## 三問

### 1. 分層與依賴方向:對齊,沒有跨層直呼

- 新函式都留在 scripts/lumos 既有的 REVISIT 一帶,依賴方向跟鄰居一樣由上往下:第一層 `_ns_revisit_violations` → `_revisit_split` / `_revisit_closed` / `_revisit_misplaced`;讀取端 `_revisit_lines`、`_probe_lines`、`_drift_ack_line_err` 都呼叫同一支 `_revisit_closed`,結案判定只有一處。對照:file: `scripts/lumos:31757`(`_revisit_closed`)、file: `scripts/lumos:31736`(`_revisit_split`)。
- 「跳過已處理的行」放在抽取層,跟 `_retire_lines` 跳過 superseded 同一手法:file: `scripts/lumos:31981`(`_retire_lines`)對照 file: `scripts/lumos:31974`(`_probe_lines` 的新分支)。
- `_probe_parse` 只跳過 closed、不驗,驗與判留在 `_revisit_closed`,沒有兩支各解析一次同一標記。
- `_real_chars` 抽出後 `_excluded_line` 改呼叫它,沒有抄第二份實字計數:file: `scripts/lumos:6395` 附近。
- `_note_shape_report` 加 `rules` 欄的口子,跟鄰居 `_ns_slot_extra` / `_ns_tr_extra_merged` 一樣只往 `extra` 加鍵、用 `dict(ex, ...)` 不改傳進來的字典:file: `scripts/lumos:29359`。行內 `import collections` 跟同檔 27581、27708、28835 的寫法一致。
- 違規元組 `(節點, 行號, 規則, 片段, 改法)` 的 `v[2]` 確是規則名(file: `scripts/lumos:28782`),計數鍵對得上。

### 2. 命名與錯誤處理:大致對齊,有兩處不一致(都是 minor)

- 命名:`_ns_revisit_cond_viol`、`_ns_revisit_closed_viol` 跟 `_ns_revisit_violations` 同前綴;`_drift_ack_line_err` 跟鄰居 `_drift_ack_args_err`(file: `scripts/lumos:32789`)同樣回「原因字串或 None」,呼叫端同樣印「擋下:」再 `return 2`。`_revisit_closed` 回 `{"closed", "errs"}` 的形狀照 `_probe_parse` 的 dict 加 `errs`。
- 錯誤處理不一致見 Z1、Z2。

### 3. 第二種做法:沒有「新工具函式而鄰居已有同功能」,有一處判定被複製成第三份(Z3,⚠ 判不準)

- 新函式沒有跟既有函式重複:`_revisit_misplaced_lines` 的行走法是 `_probe_lines` 那套(`_visible_lines` + `_notelines_regions` + `_strip_inline_markup`),計劃〈做法〉1.3 已明寫為什麼不併進 `_probe_lines`(它另有 drift scan 與 doctor Z 既有那行兩個讀者)。
- 結案寫法跟 RULE 行的 `[status:superseded]` 是兩個「處理完了」記號,計劃〈做法〉2.6 有分工理由,不算未說明的第二套。

## Findings

**Z1 第一層裡 `bad` 分支提早 return,其餘分支累加,同一函式兩種流程**
severity: minor
blocking: 否 — 結構方向對,只是控制流跟自己新加的累加寫法不一致,後果是同一行要分兩次提交才報完。
引句:「+    if not dead and _revisit_misplaced(probe):」
1. 輸入:`REVISIT:2026-9-1 壞 REVISIT:2026-10-05 後面`(body 區、新寫)。
2. 走到 `_ns_revisit_violations`:`kind == "bad"` 這支是原本就有的 `return [...]`(file: `scripts/lumos:27931`,diff 裡是未改的上下文行),在 diff 新加的 `out`/`dead` 累加(`if kind in ("date", "cond")`、`if not dead and _revisit_misplaced(probe)`)之前就回了。
3. 實測輸出:`'REVISIT:2026-9-1 壞 REVISIT:2026-10-05 後面' -> ['回頭條件格式不合']`,沒有「回頭條件寫在句中」。作者照改法把第一處日期改對後再提交,第二處才被擋,等於同一行被擋兩輪。同函式 `cond` 分支已改成 `out +=`,只有 `bad` 留著 early return。
4. 修法方向:`bad` 也 `out.append(...)` 而不是 return,讓三種報告對同一行一次報完。

**Z2 開頭欄位區:結案標記的文法會擋,日期與條件文法不擋,同一類行三種待遇**
severity: minor
blocking: 否 — 沒有新增第二套判定,是新規則的適用區塊跟鄰居規則不一致,後果是只擋了一半。
引句:「+    if kind in ("date", "cond"):」
1. 輸入:開頭欄位清單項(reg=`extra`)`- REVISIT:2026-10-05 x [closed:2026-13-45 好好好好]`。
2. diff 把 `_revisit_split` 提到所有區塊都算,`if kind in ("date", "cond"): out += _ns_revisit_closed_viol(...)` 於是在 `extra` 區也跑;但同函式的 `bad` 檢查與 `_ns_revisit_cond_viol` 仍只在 `reg in ("body", "summary") and not table` 的分支裡。
3. 實測:`'- REVISIT:2026-10-05 x [closed:2026-13-45 好好好好]'`(extra)→ `['結案標記寫錯']`;`'- REVISIT:2026-9-1 壞日期'`(extra)→ `[]`;`'- REVISIT:[when-file:a.py] 沒期限'`(extra)→ 只有 `['條件寫在不評估的地方']`。同一個區塊裡,結案標記被查、日期壞損不被查。計劃〈做法〉1.2 只說「每個區塊都算 `_revisit_split`」是為了認得行首形狀,沒有說結案文法也要延到 `extra`;E5 讀不讀 `extra` 區的 REVISIT 行取決於 `_search_visible_lines`,這裡沒有對齊說明。
4. 要嘛把結案文法也限在 body/summary(跟鄰居規則同範圍),要嘛在計劃與 WHY 寫明 `extra` 區的結案文法是刻意查的。⚠ 我沒確認 E5 是否真的會讀 `extra` 區的 REVISIT 行,若會讀,則 `extra` 區缺的反而是日期壞損的檢查,屬既有缺口、非本案引入。

**Z3 「寫在不評估的地方」的判定現在有三份各自成立的條件式 ⚠**
severity: minor
blocking: 否 — 目前三份結論一致(我逐區塊對過),沒有可重現的分歧,只是同一條件寫了三次。
引句:「+            continue        # 已經算進 _probe_lines 的「寫在不評估的地方」,不重算(同第一層 _ns_revisit_violations 的不重報)」
1. 三處:file: `scripts/lumos:31967`(`_probe_lines` 的 `if _PROBE_ANY_RE.search(probe): dead.append`)、`_ns_revisit_violations` 新加的 `dead = True` 分支(file: `scripts/lumos:27935`)、`_revisit_misplaced_lines` 新加的 `(table or regs[no - 1] not in ("body", "summary")) and _PROBE_ANY_RE.search(probe)`。
2. 計劃〈審計修正紀錄〉自己記了這個條件漏抄過一次(「Z 段同一列算了兩次」),實作時才補。此後有人改「不評估」的範圍(例如新增一種區塊),要同時改三處,漏一處就是 Z 段重複計數或第一層重報。目前沒有測試把三處綁在一起(`t_doctor_revisit_lists_misplaced` ③ 只釘表格那一種)。
3. 判不準它算不算「第二種做法」:條件本身是同一個,但各自活在不同函式、沒有共用判定函式。依錨定規則不升 major。

## 沒問題的項目

- 新規則的擋/提醒走既有 `_gate_event_or_warn` 與 `kw = {"extra": ex}`,blocked 與 warned 兩條路徑共用同一個 `kw`,所以兩種事件都帶 `rules`;`rules` 只有規則名種類數的鍵,體積小,寫入器本身另有 4096 位元組保護(file: `scripts/lumos:18345` 附近)。
- 帳本欄名 `rules` 跟放寬帳(file: `scripts/lumos:28839`)同名同形(規則名 → 條數)。
- `drift ack` 的前置檢查抽成 `_drift_ack_line_err`,原有的兩條擋下訊息字句沒變,只是搬位置;新增的 probe 結案檢查放在 retire 檢查之後、不影響既有行為。
- 說明與圖譜:技能手冊 SKILL.md 與 commands/03 兩處補句、系統筆記各補一行 WHY,跟計劃〈做法〉第 3 節一致。
- `_drift_doctor_lines` 的位置字串用 `p[:-3]` 去 `.md`,跟同函式 c1–c5 的 `f['path'][:-3]` 同口徑(兩邊路徑都是不含 vault 前綴的相對路徑)。
- python-idioms:沒有新的阻塞呼叫、秘密或資源釋放問題;`_revisit_quote_states` 整行一遍掃,不是平方;`_revisit_closed` 用 `raise ValueError` 轉 `errs` 的寫法跟 `_probe_parse` 的 try/except 同風格。

## 固定席節點(參考,/tmp/codeRevA/lens.txt)

- 本次改動牽連的 ★INVARIANT★ 節點(bound-tests-gate、guard-kill 等)都在 scripts/lumos 與 test_lumos.py 範圍內;diff 沒有動它們的綁定測試名,也沒有動 `_VENDORED_TOOLKIT` 或主程式檔頭,我沒有看到跟這些合約衝突的改動。⚠ 未逐條重跑綁定測試。

最高 severity:minor
