severity: minor

整體判斷:這個補丁的主幹結構是對的。轉變判定沿用 `_drift_probe_check` 這一家(多帶 `extract`、`kind` 兩個參數,沒有另寫第二套)。判定另開一支放在核心之後,跟 m1 的先例一樣。種類登記和 `_drift_fix_hint` 的分支也是照原本的表加。不一致處集中在開關讀法、判不了的處理、印法與治理帳。行號以 repo 的 b3f9c874 為準。

**問一:分層與依賴方向**

沒有跨層直呼。`_retire_lines` 呼叫 `_ns_summary_logical`、`slot_parse`、`_ns_superseded`,這些是它自己的資料來源,`_probe_lines` 本來就從同一批解析器取資料。依賴方向是 `cmd_drift_check`、`_drift_retire_guarded`、`_drift_probe_check`,與 m1 的 guarded→check 同向。

**A1**
severity: minor
blocking: 否 — 結構對,只是同一份設定在一次呼叫裡被解析兩遍
引句:「rt_mode = _drift_config_text_parts(cfg_text)["retire"] if mode != "off" else "off"」
`_drift_config` 的註解寫明「從同一次解析來,不另開第二支讀同一個鍵」(`scripts/lumos:31283`)。這個補丁卻讓 `_drift_config` 的四元組不帶 retire,呼叫端再叫一次 `_drift_config_text_parts(cfg_text)` 取 retire。m1 的開關是跟 gate 一起從四元組出來的(`scripts/lumos:31404`)。`_drift_config` 的警告串了 `rt_warns`,模式值卻走另一條路。

**問二:命名與錯誤處理(治理帳、提醒字樣、開關壞值)**

**A2**
severity: minor
blocking: 否 — 壞值處理少了父層不是物件這一支,結果只是沉默地照預設
引句:「dc = cfg.get("drift_check") if isinstance(cfg, dict) else None」
`_drift_old_sentence_config` 對兩種壞法都另講一句:設定檔讀不成 JSON,以及 `drift_check` 不是物件(`scripts/lumos:31327-31341`)。`_drift_retire_config` 在 `bad` 時回 `[]`,不講;父層寫壞時也不講,直接照預設。註解說「寫法同 drift_check.old_sentence」,但提醒行為並不相同。預設是 block,跟 gate 一致,這點不算錯。

**A3**
severity: minor
blocking: 否 — 只是治理帳少了跟 m1 對得上的欄位,沒有語意錯誤
引句:「extra={"check": "retire", "unknown": len(unknown)})」
m1 的帳(`scripts/lumos:32372-32397`)每次都記,包括 passed 和 range-unavailable,並帶 `head_sha`、`base_sha`、state、handle/listed 筆數,還經 `_drift_m1_fit` 裁尺寸。retire 的 `_drift_retire_report` 只在有成立項時記 blocked 或 warned,不帶 `head_sha`。「只有判不了、沒有成立」時完全不記帳(`if not must: return 0` 在記帳之前)。事後要算 retire 的跑過次數、判不了率,查不到。同一個閘名 `drift-check` 的 `extra.check` 欄位,各 check 的記法不齊。⚠ 我沒有核實 `gov --stats` 是否依賴 `head_sha` 或 passed 事件。

**問三:第二種做法(判定、開關讀法、印法)**

**A4**
severity: minor
blocking: 否 — 有寫明理由,但跟既有「判不了算要處理」的規矩分了兩套
引句:「判不了的只列出不擋(既有回頭條件判不了照舊擋)」
`cmd_drift_check` 的 docstring(`scripts/lumos:31381`)寫「判不了的(git 失敗、逾時、預算用完)算要處理——放行等於一條繞過的路」。`_drift_unknown_hint` 也印著同一句(`scripts/lumos:32235`)。m1 的 block 模式遇到 `_DRIFT_M1_UNKNOWN` 同樣擋(`scripts/lumos:32429-32430`)。retire 是第一個把判不了降成「只列出」的判定,而且共用的 `_drift_probe_check` 同時產生 probe 與 retire 兩種判不了,probe 擋、retire 不擋。理由合理,但這是一條新的例外政策,不是既有做法。如果要留,這條例外需要寫進 `_drift_report_must` 或 `_drift_unknown_hint` 這一組共用的說明,不只是一行註解。

**A5**
severity: minor
blocking: 否 — 印法另起一套,但內容用了共用的 `_drift_print_findings`、`_drift_print_hints`
引句:「print(f"存量漂移檢查:RULE 撤除條件有 {len(unknown)} 項判不了(只列出,不擋):", file=sys.stderr)」
既有的收尾是 `_drift_report_must`(`scripts/lumos:31494`)。它用「N 處要處理、M 項判不了」一行總括,判不了走 `_drift_unknown_hint`,再印一組 `drift ack` 指令。retire 另寫了 `_drift_retire_report`:
- 判不了自己印,上限用新常數 `_DRIFT_RETIRE_SHOW`(`scripts/lumos:31423`),而 `_drift_print_findings` 的上限是寫死的 20(`scripts/lumos:31365`)。
- 沒有印「不改就留著並表態」那段 `lumos drift ack … --kind` 指令。這段是 `_drift_report_must` 的固定段落,retire 只靠 `_drift_fix_hint` 裡藏的一句 ack。
- 擋下時另加「要整個專案先只提醒」的提示。這個跟 m1 的對應段落同型(`scripts/lumos:32432-32434`),是對的。

**A6**
severity: minor
blocking: 否 — 預算是第二種配法,但註解說「同舊句檢查的先例」會讓人誤以為相同
引句:「left = min(_DRIFT_RETIRE_BUDGET_SEC, max(0.0, _DRIFT_BUDGET_SEC - (time.monotonic() - t0)))」
m1 是給自己一個獨立的截止時間(`_DRIFT_M1_BUDGET_SEC = 30`,註解「不吃 c1 到 c5 與 probe 剩下的」,`scripts/lumos:31527`)。retire 反過來,用核心判定「剩下的時間」再封頂 20 秒。兩個外掛判定各一種預算配法。核心用滿時 retire 剩 0 秒,所有 retire 條件都判不了,而 A4 又讓判不了不擋,等於核心慢的那一次推送不會檢查 retire,也不會擋。補丁的註解還宣稱「同舊句檢查的先例」,這句只對「核心之後另跑一支」成立,預算不是。

不對齊共 6 條,其中 major 0 條
