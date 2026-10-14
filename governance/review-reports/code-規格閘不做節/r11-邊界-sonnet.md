severity: minor

窮舉測試沒有假綠,改壞多半會紅。`_note_lines` 的切行也沒問題。要報的是三處多字詞的比對縫隙,都不擋推送。

我在 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-Backend-improve/fe5c4f58-e7fb-477f-be55-0823b5438608/scratchpad/cr-sgn11-邊界/` 載入 `scripts/lumos` 直接呼叫 `_door_keyword_hits` 與 `_door_scan_text`,又複製一份 scripts 做破壞測試。`spec-gate-nondo` 只讀,沒寫帳。

severity: minor
blocking: 否 — 多字詞被拆開的寫法會讓門判成風險低,但是對抗性寫法,而且 `LINE推送` 的缺口在本輪之前就有,只是這輪壓空白後兩者更不一致
引句:「多字危險詞(DROP TABLE、DELETE FROM、pre-push hook、LINE 推送)寫死單一空格,兩個空格或 tab 就比不到」
問題:`_door_scan_text` 的多字詞只認「單一空格」。這輪把連續空白壓成一格,但下面三種仍然比不到:
- 看不見的空白類字元:`_is_invisible` 把 `\x0b`、`\x0c`、`\x1c`–`\x1f`、`\x85`、U+2028、U+2029 整個刪掉,`DROP\x0bTABLE` 變成 `DROPTABLE`。
- 連字號變體:NFKC 把 U+2011 折成 U+2010 而不是 `-`,`pre‑push hook` 比不到。
- 英文與漢字之間不留空白:`LINE推送` 比不到,而 `LINE　推送` 比得到。中文常這樣不留空白,`LINE 推送` 的規則反而不符合最自然的寫法。
具體失敗情境(實測 `_door_keyword_hits`):
- `DROP\x0bTABLE`、`DROP\u2028TABLE`、`DELETE\x85FROM`、`anchor\u2028verify` 都回空。
- `pre‑push hook`(U+2011)、`pre–push hook`(U+2013)都回空。
- `透過LINE推送` 回空。
- 計劃裡寫了其中一種,門會判風險低。
- 修法:刪除之外,另外比一份「把這幾個看不見的空白當空格」的版本;`LINE` 後的空格改成 `\s*`。
佐證:`scripts/lumos:8199`、`scripts/lumos:29437`

severity: minor
blocking: 否 — 只影響測試保護強度,不影響執行行為
引句:「兩個漢字中間的那一個空格(漢字範圍同 _RANK_CJK_RE)」
問題:`_DOOR_HAN_GAP_RE` 的範圍是基本區加擴充 A,日文假名、韓文、擴充 B 以後和全形標點都不算漢字,這跟 `_RANK_CJK_RE` 一致,可接受。關鍵字表的漢字全在基本區,所以目前不影響結果。但行為測試沒有蓋到擴充 A:我把正則改成只剩基本區,`-k door_scan_space` 仍是 14 passed。只有版本釘 `t_door_scan_logic_version_pin` 會紅,而它升版就能過。目前沒有關鍵字用到擴充 A,不會誤放行。
具體失敗情境:有人把範圍改窄或改寬,行為測試不會報。
佐證:`scripts/lumos:8203`、`scripts/test_lumos.py:65822`

已讀,無 finding:
- `_note_lines` 切行:只認 `\n`、`\r\n`、`\r`,`"a\rb\r\nc\n"` 切成 3 行,結尾的 `\n` 不多算一行,`\r\r\n` 切成 `['a','','b']`。
- 家族行號一致:`_door_keyword_hits`、`_h2_section_lines`、`clause_bindings`、`_clause_block_sha` 等都走 `_note_lines`。`t_note_lines_spec_gate_family` 對列出的 10 個函式做語法樹檢查。
- 英文多字詞的前後標點與行首行尾:`` `DROP TABLE`; ``、前後空格、`DROP\tTABLE`、`DELETE\u3000FROM`、全形 `ＤＲＯＰ　ＴＡＢＬＥ` 都命中。
- 漢字之間的空白:`退 款`、NBSP、全形空白、細空白、`收斂 \t 判準` 都命中。`面對 外部` 會拼出「對外」,偏向多判高,程式註解已寫明。
- `t_zero_width_strip_all_invisible` 的 `_zw_visible` 沒有呼叫 `isspace` 或被測函式,不是循環論證。窮舉含代理區,斷言「看得見的一個都不拿」和「看不見的夾進退款與 `pay…ment` 都命中」,前置斷言確認 `\x1f`、`\x0b`、`\x85`、U+2028 與 Cs 在逐一跑的那批裡。
- 破壞測試:前述把漢字範圍改窄那一次,行為測試仍綠(見上一條 finding)。窮舉測試與 `t_door_scan_break_chars_dropped` 本輪沒另外破壞,我只確認它們有蓋到相應字元。

最高等級 minor,blocking 0 條。
