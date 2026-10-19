severity: minor

**三問總評:新碼的分層、擋下訊息形狀、回傳碼都跟鄰居對得上。唯一的疑點是新抽出的共用函式只接了兩處,還有兩處留著原本的寫法。**

**問 1 分層與依賴方向:對齊**
- `_round_format_write_block` 回 `(事件標籤, [訊息行…])`,擺在 `cmd_canary` 正前方,由 `cmd_canary` 呼叫,呼叫端印訊息並回 rc2。這跟既有的 `_cap_retro_record_block`(`scripts/lumos:15991`)是同一套 `(原因碼, 幾行)` 契約。呼叫端寫事件的做法也一樣:`scripts/lumos:11440` 用 `_gate_event_or_warn(..., hard=True)`,新碼在 `scripts/lumos:11933` 照同形狀。
- 讀帳用的是既有的 `_loop_records_checked`(`scripts/lumos:14405`),沒有另開一套讀法。定錨分級用 `_loop_anchor_tier`(`scripts/lumos:27752`)。判編號種類用 `_roster_kind`(`scripts/lumos:14276`)。
- `_pitfall_tier_review_lines` 讀 `_TIER_ROSTER` 和 `_REQUIREMENT_LABEL`(`scripts/lumos:27747`),是唯讀常數,沒有碰帳本或圖譜。`pitfalls` 的 `_pitfall_tier` 標著不載圖譜,這個依賴方向沒有破壞它。
- 設計審 r1 提過「擴充 `_roster_dispatch_entries` 而不是另寫讀派工單」。我查了 diff,沒有動 `_roster_dispatch_entries`(`scripts/lumos:14450`),也沒有新寫讀派工單的函式。`_loop_next_hints` 只吃已算好的 `loop_id`、`eff_tier`、`n_next`,不讀派工單。沒有跨層直呼。

**問 2 命名與錯誤處理:大致對齊**
- 擋下訊息是「擋下:… / 在意的原因:… / 接下來:…」三段,指令獨立一行,回傳碼 rc2,跟 `scripts/lumos:11440` 一帶相同。
- `import shlex as _shlex` 放在函式內,跟 `scripts/lumos:15994`、`scripts/lumos:1251` 一致。
- 命名 `_loop_*`、`_disp_*`、`_SNAP_PLACEHOLDER` 都符合同檔慣例。
- 有兩處小不一致(見 finding 2、3)。

**問 3 第二種做法:發現一處「共用卻沒接完」**
- 函式沒有另造讀帳法,也沒有另一套集合解析。`_set_or_none` 重用既有的 `_ids`(`scripts/lumos:11556`)。
- finding 1 是唯一一條跟「第二種做法」沾邊的。

**Finding 1(minor,判不準,標 ⚠ 交編排者)**
severity: minor
blocking: 否
引句:「數法就是 "round" in r——loop next 開頭那道混用守衛與 canary record 寫側共用這一支」
- `_loop_round_format` 的說明寫「共用這一支」,但同一個數法還有兩處沒接上:
  - ``file: `scripts/lumos:14029` `` 的 `n_round = sum(1 for r in rounds if "round" in r)`,加上 `n_round != len(rounds)` 的 panel 混用守衛。
  - ``file: `scripts/lumos:28375` `` 的 `n_round_` 搭配 `0 < n_round_ < len(rounds)` 判混用。
- 結果是同一個「判混用」的規則現在有「共用函式」和「原地內聯」兩種寫法並存,將來改定義會漏。
- 我把它列 minor 而不是 major,有三個理由:
  - 邏輯相同,沒有引入新語意。
  - 14029 那處判的是「panel 模式下每筆都要帶輪次」,不完全等於「混用」。
  - 28375 的錯誤訊息跟 loop next 的措辭不同。
- 是否要把這兩處也改呼叫 `_loop_round_format`,交編排者決定。

**Finding 2(minor)**
severity: minor
blocking: 否
引句:「errs.append(_te.replace("(path:line 或 test:<名>)", "(path:line)").replace(";多個證據挑最直接的一個,其餘寫進 reason", ""))」
- `existing` 那段拿 `_disp_value_type_err` 產出的整句訊息,再用字串 `.replace` 改掉兩個片段。
- 同函式 `_disp_value_type_err(v, what)` 已有 `what` 參數,但提示文字寫死在函式裡,所以呼叫端只能事後替換。
- 鄰居(`scripts/lumos` 的 `_dispositions_*` 各條)都是直接組句,沒有「先產句再改字」的做法。訊息一改字,這個 `replace` 就會靜默失效。
- 屬於錯誤處理的寫法不一致,結構上還是對的。

**Finding 3(minor)**
severity: minor
blocking: 否
引句:「                out["hints"] = _hints   # cb3 s3-f1:寫側 2026-08-26 起審查席必附報告,模板同步」
- 插入 `hints` 時,把原本掛在 `record_cmd` 末行、說明「審查席必附報告」的 `cb3 s3-f1` 註解,連同 `--scope-lines` 那行換掉了。這個註解現在貼在 `out["hints"]` 這行,指不到它原本講的東西。
- `hints` 是 `out` 裡新增的 key。鄰居的提示是 `tier_hint`、`note`、`cluster_hint` 這類單句字串,`hints` 是字串清單。人讀輸出也改走專屬迴圈印「提醒:」,沒併進 `for k in (...)` 的白名單。這是新增形狀,但沒有破壞既有結構。

**不對齊共 3 條,其中 major 0 條**

(指令與範圍:我只用 Read 和 Bash 做唯讀查看,沒有跑 `pitfalls --diff`,也沒有寫檔,所以沒有暫存要清。)
