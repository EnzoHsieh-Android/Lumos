severity: major

總評:四個舊的「第二種做法」裡,跑滿判定(共用 `_cap_hint_scope`/`_cap_hint`)、卷證資料夾(`governance/review-reports/<編號>/` 加 `cmd_loop_replay` 的編號檢查)、`escape-stats` 式獨立子指令、`fix-check --record-template` 式 stdout/stderr 分流、`warn_soft`、`LOOP_NOT_CLOSE_EVENTS`,都已改回既有做法。指紋留痕還沒真正改成既有做法,見 F1。另有三條較小的不一致。

## 四問

1. 分層與依賴方向:一致。
   - 擋點放在 `cmd_canary` 寫側、處置閘第八步、`loop next` 提示三處。這跟 `fix-check`(已經擋在 `cmd_canary` 寫側)、`_disposal_landing_step` 的接法同層,沒有跨層直呼。
   - `_disposal_landing_step` 的簽名本來就帶 `spec_sha_override`,「凍結第二趟與回放印 — 不重判」可以直接照接。
   - file: `scripts/lumos:22646`(`_disposal_landing_step`)、`scripts/lumos:8828`(`_cap_hint`)、`scripts/lumos:8851`(`_cap_hint_scope`)、`scripts/lumos:13105`(`loop next` 附 `cap_hint`)。
2. 命名與錯誤處理:大致一致,有兩處不齊,見 F3、F4。
   - `--template`/`--check`/`--record`:`--record-template` 在 `scripts/lumos:46124`,另有 `--check` 在 `scripts/lumos:46519`。
   - `--skip` 在 `scripts/lumos:46807`(`bt.add_argument("--skip", ...)`)。
   - 這四個旗標形狀都有先例,不另列。
   - 回傳碼 0/1/2 與三段式擋下訊息,跟 `cmd_canary` 的寫法一致。
   - 編號檢查:file: `scripts/lumos:1041`。
   - `retro-stats` 對照:file: `scripts/lumos:46165`(`escape-stats`)、`scripts/lumos:11426`(`cmd_loop_escape_stats`)。
3. 第二種做法:有一條 major(F1),一條 minor(F2)。
   - 「事件帶檔案 sha」已有先例,是 `_gate_event_or_warn(..., extra={"record_sha256": rsha, ...})` 這種結構化欄位。
   - 先例位置:file: `scripts/lumos:12844`(`fix-check` 落帳),`scripts/lumos:8265` 與 `scripts/lumos:8343` 是欄位型別登記與讀取。
   - 跳過的先例是 `_gate_event_or_warn(..., "skipped"/"waived", ...)`。
   - 這兩條先例見 F1、F4。
4. 落點:合理。
   - `loop-convergence-recording` 的 `about_code` 只列 `scripts/lumos`,新開 `Systems/loop-retro` 也掛同一支檔。
   - 共用 `scripts/lumos` 的 Systems 節點有 44 篇,所以這樣掛沒有先例衝突。
   - 把 `canary record` 擋點與兩支共用函式的重構寫進 `loop-convergence-recording`,新指令與統計寫進 `loop-retro`,分工合理。
   - file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:81`。

### F1 指紋留痕還是寫成 note 字串,不是既有的結構化欄位
severity: major
blocking: 是 — 引入第二種做法:既有「事件帶檔案 sha」走 `extra` 結構化欄位,這裡改成塞進 note 字串,閘要自己解析。
引句:「在治理帳寫一筆 `kind=cap-retro`(nodes 帶編號,note 帶檔案路徑與 sha256)」
- `_loop_gov_mark` 只收 `note`,沒有 `extra`,所以快照寫的「用 `_loop_gov_mark` 帶指紋」只能把 sha 塞進 note。
- 處置閘第八步比對指紋時,就得從自由文字裡解析 sha。
- 既有先例:`fix-check` 用 `extra` 欄位帶 `record_sha256`;`canary` 的 `report_sha256` 也是欄位。
- 建議二選一:改走 `_gate_event_or_warn(..., extra={"loop","retro_sha256","path"})`;或擴充 `_loop_gov_mark` 加 `extra` 參數。
file: `scripts/lumos:12844`
file: `scripts/lumos:971`
file: `scripts/lumos:8265`

### F2 寫側擋下沒有留 blocked 事件
severity: minor
blocking: 否 — 結構對,但漏了既有「寫側擋下也落帳」的慣例。
引句:「回 2、不寫帳,三段式印原因與 `--template` 指令」
- `cmd_canary` 的每一種寫側擋下都落一筆 `_gate_event_or_warn("canary","blocked",...,hard=True)`。
- 該行附帶 `id=uuid` 防同秒去重折疊,註解明寫「被擋也要留痕」。
- S1 的擋點完全沒提這件事。
- 快照〈守衛面〉只說跳過會被統計,沒說被擋的次數。要量「擋了幾次」就沒資料。
- 建議補一筆 `canary blocked cap-retro-missing loop=… id=<uuid>`。
file: `scripts/lumos:9503`
file: `scripts/lumos:9513`

### F3 回顧與跳過的落帳用 fail-open 的 `_loop_gov_mark`,而閘會倚賴這筆帳
severity: minor
blocking: 否 — 事件種類歸 `_loop_gov_mark` 是對的,但錯誤處理與既有「閘倚賴的帳」不齊。
引句:「治理帳寫入照 `_loop_gov_mark` 既有做法(失敗不擋)」
- `_loop_gov_mark` 是 `except Exception: pass`,沒有回傳值。
- `--record` 與 `--skip` 的存在意義就是產生閘要驗的帳,寫失敗卻回 0,使用者會以為已記,下次問閘才看到 ✗。
- `fix-check` 對同樣情境的做法是看 `_gate_event_or_warn` 的回傳,`ok is not True` 就提示「沒記到帳」。
- `_loop_gov_mark` 目前只用在 `converged`、`rewrite`、`replay-refreeze` 這些「結案標記」。回顧與跳過是「閘要比對的證據」,性質不同。
- 建議 `--record`/`--skip` 至少要在寫不進去時印警告並回非 0。
file: `scripts/lumos:971`
file: `scripts/lumos:12844`

### F4 新事件名與 gate 名的歸屬跟既有不齊(⚠ 部分判不準)
severity: minor
blocking: 否 — 命名不一致,結構沒壞。
引句:「新事件種類 `cap-retro`、`cap-retro-skipped` 登記進 `LOOP_NOT_CLOSE_EVENTS`」
- 既有跳過類 kind 都是 `skipped`、`skipped-env`、`waived`,形狀是 `<動作>-<修飾>`。`cap-retro-skipped` 是反過來的。
- `LOOP_NOT_CLOSE_EVENTS` 的元素是 `(gate, kind)` 二元組,快照只寫「事件種類」。
- `_loop_gov_mark` 把 gate 寫死成 `design-loop`。但快照〈適用範圍〉寫「設計審與代碼審都算」,而代碼審的事件既有慣例是 `code-loop` gate。
- ⚠ 我判不準:是否要讓代碼審的回顧事件走 `code-loop` gate。這要快照指定,現在是空白。
- 建議指明 gate,並把 kind 改成 `cap-retro` 與 `cap-retro` 搭配 `skipped`/`waived`。
file: `scripts/lumos:10295`
file: `scripts/lumos:971`
file: `scripts/lumos:24866`

不對齊共 4 條,其中 major 1 條
總結:最嚴重 major,blocking 1 條
