severity: minor

我只讀了 `r2-repair-lumos.patch` 與原始碼,沒讀 r1 文件。pitfalls 只列出 `scripts/lumos` 既有的 ruff 舊帳,沒有這次改動才有的項目。`scripts/lumos` 目前在 `69ee6d76`,`f791d8ba` 是它的祖先,我讀的是工作樹內容。

**上一輪架構席三項要求:全數做到**
- 讀側另外兩處已改用 `_loop_round_format`。`cmd_loop_next`(`scripts/lumos:16467-16473`)、`loop status --panel`(`:14058-14061`)、處置閘(`:28397-28407`)、`_cap_hint_scope`(`:11057-11058`)都不再自己數 `"round" in r`。全檔已搜不到 `n_round` 殘留。
- `_disp_value_type_err` 改收 `fmt`、`none_ok` 參數,`existing` 那處(`:55248`)不再 `.replace`。`.replace("(path:line` 全檔 0 筆。
- 註解已歸位。「代碼審minor解綁」那行回到載體段前(`:11966` 上方),`cb3 s3-f1` 那行回到 `record_cmd` 上。

**1. 分層與依賴方向:一致,沒有跨層直呼**
- `_review_rows`(`:11347`)與 `_loop_round_format`(`:11353`)是純函式,放在 `_ledger_rel_path` 與 `_round_format_write_block` 之間,跟 `_loop_anchor_tier`(`:27783`)這類「吃列清單」的 helper 同一層。
- 呼叫方向是 cmd 層(`cmd_canary`、`cmd_loop_next`、`cmd_loop_status`、`_loop_status_disposal`)呼叫 helper,helper 不回頭呼叫 cmd。
- `_rf_mixed_next` 只被 `_round_format_write_block`(`:11400`)呼叫,`_RF_RENUMBER` 兩處共用(`:11374`、`:11416`)。訊息組裝只有這一套。
- `_review_rows` 沒有第二套過濾:全檔只有 `:11350` 一處寫 `"outcome" not in`,它跟 `_escape_review_rows_by_loop`(`:13794`,按 kind 過濾)是不同判準,沒有重複。
- 過濾位置有兩種做法。既有的規格閘留痕在讀帳層 `_canary_ledger_scan`(`:14407`)就濾掉,新的結局帳卻在六個使用端各自過 `_review_rows`。寫側本來就有逐處判 `outcome is None` 的先例(`:11958`、`:11966`),而結局帳也要留給讀 `usd` 的使用端,所以我判成結構可接受。
- 使用端先呼叫 `_review_rows` 再呼叫 `_loop_round_format`,後者內部又濾一次(`:11357`),等於重複過濾。這點標 ⚠ 交編排者,我不判成 major。

**2. 命名與錯誤處理:有兩處小不一致**

severity: minor
blocking: 否
引句:「q = _shlex.quote(_esc_clean(str(loop), 80))」
- 鄰居是先 quote 再 `_esc_clean`,上限 200(file: `scripts/lumos:16036`)。另外 `:16135`、`:1255`、`:28037` 都是只 `shlex.quote(loop_id)`,不截斷。
- 新碼順序相反(先清洗、截成 80 字再 quote)。同一個函式裡 `:11407` 又用上限 60。
- 印出去給人照抄的指令因此會用被截短的編號,跟鄰居「指令保持完整編號」的做法不同,同函式內的上限也不一致。

severity: minor
blocking: 否
引句:「_lscan, _lerr, _lwhole = None, f"審查帳讀不到({e.__class__.__name__})", True」
- `_loop_records_checked` 在 `scan=None` 時本來就有這段 `OSError` 處理,回的是同一句「審查帳讀不到(…)」(file: `scripts/lumos:14447`)。
- `cmd_canary` 開頭另寫了一份同樣的 try/except 與同一句文案,為的是拿到「整本壞」旗標,這是第二份訊息字串。
- 結構(先 scan 再傳 `scan=`)符合 `_loop_records_checked` 的設計。建議這個旗標由 helper 回傳,或至少共用同一句文案。

`_rf_mixed_next` 的 `mixed` 分支(`:11369`)重寫了一遍 `_RF_RENUMBER` 的指令字串。文案略有不同,我不列為獨立條。

**3. 第二種做法:沒有 major**
- 搜過 `"outcome" not in`、`shlex.quote`、`_esc_clean`、`.replace(` 錯誤句改寫、輪次格式計數,沒有新的並行機制。
- `_ids(regression_set)` 與 `_set_or_none(regression_set)`(`:11586-11604`)是 `cmd_canary` 內既有閉包,`--folded-set`、`--accepted-set` 已在用,這次是收斂到同一支,方向一致。
- `fmt=(格式說明, 句尾補充)` 這種兩元素 tuple 參數在檔內沒有先例,但只在一個函式內使用,結構上不算第二種做法,不列。

不對齊共 2 條,其中 major 0 條(另有 1 條標 ⚠ 交編排者:使用端先過 `_review_rows` 再進 `_loop_round_format` 會重複過濾,以及結局帳與規格閘留痕的過濾位置不同)。
