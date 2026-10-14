severity: minor

**finding 1**
severity: minor
blocking: 否 — 只是讀帳的寫法多了一份,行為不錯,而且跟同區鄰居一致。
引句:「rounds, gate_at, after = [], None, False」
對照:`scripts/lumos: `scripts/lumos:8884`(`_spec_gate_latest_records`,同樣的 `_ledger_lines` 加 `json.loads` 加 `isinstance(d, dict)` 迴圈,只取規格閘留痕)`;另 `scripts/lumos: `scripts/lumos:12958`(`_escape_review_rows_by_loop`,依迴圈編號分組,`except (ValueError, RecursionError)`)`、`scripts/lumos: `scripts/lumos:13170`(`loop status` 取 rounds,濾掉 kind=spec-gate)`。
判定理由:`_spec_gate_push_light` 自己寫了第三份讀審查帳的迴圈。這份是為了保留「規格閘留痕之前或之後」的 append 序,現有讀帳函式都不保留這個序,所以有它的理由。它只 `except ValueError`,跟 `_spec_gate_latest_records` 一致。但逃逸帳那幾支較新的讀法已經多接 `RecursionError`,理由是超深巢狀行(`code-逃逸帳 r3`)。這裡沒接,所以帳裡有一行超深巢狀,推送前檢查會直接丟例外。這比較像容錯缺口,不算第二種做法。因此列 minor。

**以下四項我對照過,沒有不對齊**
- **`_light_gate_fails` 抽出:** 把 `loop status --light` 的判法原樣搬出來。`loop status` 改成呼叫它,`OSError` 仍由呼叫端轉 rc2。新的推送前檢查也呼叫同一支,沒有另寫判法。這是收斂成一種做法,不是新增第二種。
- **`_spec_gate_push_light` 與留痕過期、小改動閘的接法:** 順序是先 `_spec_gate_push_stale`,再 light,再測試,再小改動閘,都回 `(原因, 綠行)`。`stale` 改回 `(原因, now)` 以便重用重判結果,沒有再判一次門,也沒有跨層直呼。
- **擋下時記治理事件、不記逃逸:** 同函式裡「測試紅」才走 `_auto_escape`,那是下游抓到洞。這裡是流程沒走完,記成 `_append_governance_log` 的 `hard: True` 事件,跟 `check-r`、`check-j` 的 blocked 寫法一致。記帳失敗時 `except` 並 stderr 提示、照樣擋,這跟「逃逸自動記 fail-open」同一精神。鄰近的留痕過期與小改動擋下沒記事件,但那是欄位語意不同,不是第二種寫法。
- **`_NOGO_NEG_PHRASES` 組正則:** `_NOGO_NEG_PREFIX_RE` 與 `_NOGO_NEG_HEADER_RE` 都由這一個字串組出,消除原本兩份複製。兩支正則的 `.pattern` 都進 `_door_rule_fingerprint` 與 `_NOGO_SKIP_LOGIC_PATS` 的釘子,所以改片語表仍會讓釘住版本的測試翻紅。`_NOGO_NEG_PHRASES` 本身不在列表裡,但它只經這兩支進來,指紋沒有漏。

不對齊共 1 條(minor),major 0 條。
