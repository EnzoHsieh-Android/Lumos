severity: minor

審查範圍:主審 repair patch 的 scripts/lumos 部分。對照檔為 `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos`,所在 HEAD 是 db8a7c6c。它比目標 2b3283c9 多兩個只動帳本的提交,行號以它為準。

## Finding

severity: minor
blocking: 否 — `_strip_zero_width` 在 ASCII 範圍的行為由窮舉測試釘住,目前不會判錯,只是同一個判準有兩處寫法。
引句:「if s.isascii():   # ASCII 只有控制字元會被拿掉,用一次 translate 省掉逐字查表」
對照:``/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos: `5021-5030` ``(`_INVISIBLE_CATS` 與 `_is_invisible`)
判定理由:
- `_ASCII_INVISIBLE` 另寫了一份「Cc 且非空白」,沒有經過 `_is_invisible`,而且硬寫 `"Cc"`,沒讀 `_INVISIBLE_CATS`。
- 這是同一個判準的第二份副本。哪天 `_is_invisible` 改了(例如加一個 ASCII 範圍內的類別),快路徑不會跟著變。
- 目前 `t_zero_width_strip_all_invisible` 窮舉整個碼位範圍,包含 ASCII,所以會在改壞時翻紅。但 `_DOOR_SCAN_LOGIC_PIN` 的雜湊只含 `_INVISIBLE_CATS`、`_PQ_DICP_RANGES`、`_PQ_BLANK_LOOKALIKES`,沒含 `_ASCII_INVISIBLE`。
- 建議:在 `_is_invisible` 定義之後,用 `_is_invisible` 推導這張表(`{c: None for c in range(128) if _is_invisible(chr(c))}`)。

severity: minor
blocking: 否 — 其他幾處「看不見」判法各自用途不同,但 `_is_invisible` 的註解寫「唯一一份」,沒交代跟它們怎麼分開,後人可能再合併或再抄一份。
引句:「一個字元在比對時算不算看不見(_strip_zero_width 的判準,唯一一份)」
對照:
- ``/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos: `7221` ``(`_pq_blank`):手寫 isspace、預設可忽略碼位、空白圖形、Mn/Me/Sk 的聯集,與 `_is_invisible` 幾乎相同,只多 Sk 與空白。
- ``/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos: `19556` ``(`_residual_claim_fp`):另有一份 Cf/Cc 剝除,屬指紋用途,改了會讓既有指紋全變。
- ``/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos: `37512` ``(`_PATH_SPECIAL_CATS`):跳脫用的類別組。
- ``/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos: `12981` ``(`_esc_clean`):有註解寫明為什麼不併進 `_PATH_SPECIAL_CATS`。
判定理由:
- `_pq_bad_char`、`_kill_esc`、`_lens_visible`、`_json_text_escaped` 是「擋掉/跳脫」,`_residual_claim_fp` 是「指紋穩定」,跟「比對時拿掉」確實是不同用途,不算第二種做法。
- 只有 `_pq_blank` 是同一個問題「這串是不是看不見」。它沒改用 `_is_invisible`,也沒在註解說明差在 Sk 與空白。
- `_INVISIBLE_CATS` 旁也沒說跟 `_PATH_SPECIAL_CATS` 的分工。`_esc_clean` 的註解有寫自己那一邊,新常數沒有對應的交代。
- 建議二選一:把 `_pq_blank` 改成 `ch.isspace() or _is_invisible(ch) or category == "Sk"`;或在 `_INVISIBLE_CATS` 與 `_is_invisible` 補一句分工說明,並把「唯一一份」限縮成「比對時拿掉」這一種用途。

severity: minor
blocking: 否 — 只在邊角輸入上跟既有判法不同,方向都是多擋;問題在註解與實作不一致。
引句:「這個編號帳上每一筆審查紀錄都帶輪次(非空字串),而且分級(第一筆帶 tier 的定錨)」
對照:``/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos: `27285` ``(`_loop_anchor_tier`:帳上第一筆 tier 為真值者;註解寫明它是 loop next 與處置閘共用的唯一定錨),以及 `10870`、`13484`、`14152` 都走它。
判定理由:
- `_nogo_full_review_shape` 的註解說「第一筆帶 tier 的定錨」,實作卻自己掃全部列,用 `is not None` 收集,再要求每一個都是 standard/high。這既不是 `_loop_anchor_tier`,也跟註解的說法不同。
- 邊角差異:某一列 tier 是空字串時,`_loop_anchor_tier` 會略過它,這裡卻算「有記」,然後報「分級是 ,不是…」。
- 「每筆有輪次」在既有各處是看鍵是否存在(`_cap_hint_scope`、(a) 的 `any("round" in d …)`、(b) 呼叫端 `any("round" in r …)`),這裡改成要非空字串。這是刻意更嚴,但同一個 `-std` 判斷現在有兩種寫法。
- 建議:定錨一步直接呼叫 `_loop_anchor_tier(rows)`,「沒有任何一筆是 light」另列一條並照實寫在註解。

severity: minor
blocking: 否 — 傳遞方式功能正確,`_cap_retro_status` 會自己照編號篩 `loop == loop_id`;只是參數形狀跟既有慣例不一致。
引句:「治理帳的人裁紀錄:推送前只讀一次、多份計劃共用(代碼審 r9 併2;跑滿回顧那一步自己會照編號篩)」
對照:
- ``/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos: `15498` ``(`_cap_retro_status(..., events=None, ..., gov_err=None)`)
- ``/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos: `15617-15637` ``(`_cap_retro_scan` 先讀一次、依編號分好,再用 `events=` 傳入)
- ``/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos: `9308` ``(`_nogo_ctx` 一開始就把審查帳讀好放進 ctx)
判定理由:
- 既有的「讀一次再傳」是 `events=` 加 `gov_err=` 兩個具名參數。新寫法多了一個元組參數 `gov`,在 `_disposal_judge`、`_loop_status_disposal`、`_disposal_retro_step` 三層轉手,最後才在 `_disposal_retro_step` 拆成 `gov[0]`、`gov[1]`,並多一個 `if gov is None` 分支重複呼叫 `_cap_retro_status`。
- 同一份 ctx 裡,審查帳在 `_nogo_ctx` 預先讀好,治理帳卻在 `_nogo_full_review_gate` 裡用 `"gov" not in ctx` 惰性填入。兩種填法並存。
- 建議:`_nogo_ctx` 一併讀進治理帳,並沿用 `events=`/`gov_err=` 的傳法。

## 已讀,無 finding

- `_under_root` 收齊後的同形寫法:全檔 `os.path.isabs` 與 `is_absolute` 出現處共 9 個,逐一讀過。
  - 唯一還在「判絕對再接根」的是 `_under_root` 自己。
  - 其餘是 `relpath` 轉換(28142、47681、48393、30690)、拒絕絕對路徑(22389、1157)、解析比對(15275)、Python 路徑驗證(206、187)。
  - 這些形狀都不是接根,`t_nogo_shared_helpers_used` 的語法樹守衛涵蓋兩種拼法,沒有漏網。
- `_nogo_full_review_shape` 與 `_roster_kind`:兩者各管一件事,`_roster_kind` 只看編號前綴,`-std` 編號不會被誤判成 code,沒有重複。
- `_nogo_has_named_seat` 與 `loop status --light` 的席位計法:
  - `_light_gate_fails` 與 `_panel_extra_checks` 的 `min_seats` 是計相異非空 `auditor`,不去空白,也不排除架構席。
  - 推送前這邊另外排除架構對齊席並做 strip,屬 (a) 文件已寫明的「推送前另加綁定」(r4 G4)。
  - 現在 (a)(b) 兩條出口共用同一支 `_nogo_has_named_seat`,`t_nogo_shared_helpers_used` 的 ⑤ 釘住 `_nogo_is_arch_seat` 只在這裡被呼叫。
  - 沒有新的第二種席位判法。
- `_door_scan_text` 的「先拿、NFKC、再拿」順序:有註解說明原因,且只用於比對,不改行雜湊用的原文。
- 其他改動:`_ledger_physical_lines` 的 `bytearray` 緩衝、`_DOOR_RULE_VERSION` 與 `_DOOR_SCAN_LOGIC_VERSION` 的升版,都沿用既有寫法。沒有跨層直呼。

最高等級 minor,blocking 0 條。
