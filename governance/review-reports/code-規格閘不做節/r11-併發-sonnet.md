severity: minor

兩件事要報:新正則都沒有回溯,`_note_lines` 也不吃額外記憶體;治理帳一起讀確實多付成本,但不到逾時。

**新正則(壓空白、漢字間空白、切行)與 `_note_lines`**
- `_DOOR_SPACE_RUN_RE`、`_DOOR_HAN_GAP_RE`、`_LEDGER_LINE_RE` 都是單層、沒有巢狀量詞,漢字間空白那條只用固定寬度的回顧與前瞻。
- 實測 1MB 輸入,全是線性,沒有指數或二次爆炸:

| 輸入 | 耗時 |
|---|---|
| 一行 100 萬個空白 | 約 0.01 秒 |
| 交錯的「漢 」 | 約 0.6 秒 |
| 空白夾 tab | 約 0.01 秒 |
| 100 萬個 `\r`(100 萬行空行) | 約 0.8 秒 |
- 跑完整的 `_door_keyword_hits`(載入 spec-gate-nondo 的 `scripts/lumos` 實跑,只讀),結果是:

| 輸入 | 耗時 |
|---|---|
| 交錯的漢字與空白 | 0.68 秒 |
| 100 萬個 `\r` | 2.5 秒 |
| 帶 U+2028 的 100 萬字元 | 1.18 秒 |

  最壞約 2.5 秒,不到逾時;單人本機用,我判斷是可接受的天花板。
- `_note_lines` 是用 `re.split` 一次產生整份清單。1MB 計劃峰值 4 到 8MB(100 萬個空行),跟舊的 `splitlines` 同一個量級。只要讀整份文字的呼叫端,都已經先持有整份文字,所以沒有新的記憶體問題。
- 這個天花板可以接受,所以這部分我判無 finding。

severity: minor
blocking: 否 — 多付的是約 0.3 秒與 45MB 的一次性成本,不會把誠實的操作擋下
引句:「ctx["gov_events"], ctx["gov_err"] = _retro_gov_events(_vault_repo_root(env))」
問題:`_nogo_ctx` 在每次推送前檢查都會無條件讀整本版控治理帳。前提是推送範圍裡有候選計劃,沒有候選時 `_spec_gate_push_scan` 根本不會被呼叫。這一讀不看計劃有沒有走 -std,也不看有沒有不做清單被略過的行。修補前只有出口 (b),也就是完整設計審那條,才惰性去讀。現在連只走輕量審、風險低留痕、或根本沒略過行的計劃,都要讀這本帳。
具體失敗情境:治理帳目前是 20.26MB、12.2 萬行。`_retro_read_bytes(limit=None)` 把整本讀進記憶體,再用 `_ledger_lines` 切成 12 萬個位元組串。實測約 0.33 秒、峰值約 45MB,只為了撈出 103 筆 `loop-retro`。這本帳只增不減,成本跟著線性長大。每次推送前檢查多付一次這個成本,只是不到逾時,不會擋下誠實的操作。
佐證:file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:9349`、`/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:9687`、`/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:15348`

建議:讓 ctx 持有一個惰性讀取的函式或快取,第一次真的走到 (b) 時才讀,同時保留「推送前多份計劃只讀一次」的效果。

孤兒行程與訊號收尾:這輪修補沒有新增子行程,已讀,無 finding。

最高等級 minor,blocking 0 條。
