severity: minor

## 1. 分層與依賴方向

結構對,沒有跨層直呼,也沒有新的第二條路。

- **`_is_outcome_row`**
  - 它放在 `_loop_round_format` 上方,是純函式,不讀檔。
  - 它由讀帳入口呼叫,和鄰居 `d.get("kind") != "spec-gate"` 的過濾位置一致:`_canary_ledger_scan`、`_loop_status_read`、replay 的讀帳、`_spec_gate_ledger_index`。
  - 上一輪的 `_review_rows` 已整支拿掉。`_loop_round_format`、`_round_format_write_block`、`_cap_hint_scope`、`cmd_loop_next`、`_loop_status_disposal`、`cmd_loop_status` 都不再各自重濾。這是上一輪「不要另一套過濾」的收束,做到了。
  - 對照:`_canary_ledger_scan` 同時濾 spec-gate 與結局帳;`_loop_status_read` 同。
- **`_loop_records_checked_ex`**
  - `_loop_records_checked` 變成薄包裝,再呼叫它。`cmd_canary` 原本自己寫的一份 try/except 和文案併回這一支,是收斂,不是新增。
- **`_cap_retro_record_block(rows=, rows_err=)`**
  - 參數名跟鄰居 `_cap_retro_status(rows=, rows_err=)` 完全一樣,沒有新名。
- **`_jsonl_append_verified`**
  - 它改呼叫 `_ledger_tail_needs_newline`,依賴方向和 `_gate_event`、`_append_governance_log` 同向。
  - 函式註解也補了「接上」的日期,跟 `_ledger_tail_needs_newline` 的註解對得上。

## 2. 命名與錯誤處理

- **`_none_reserved_lines` 與 `_round_format_bad_lines`**
  - 兩者都回「擋下 / 在意的原因 / 接下來」三行訊息串列,由呼叫端印到 stderr 並 `return 2`。形狀跟 `_round_format_write_block` 和 `_cap_retro_record_block` 的 `(碼, [行…])` 一致。
  - `_rf_mixed_next` 改用 `_RF_RENUMBER + "(…)"`,不再自己組那句話。這條也做到了。
- **`_none_reserved_lines`** 把 `none` 在 `--folded-set` 等清單的擋法和 `_set_or_none` 對齊,`_f_ids` 例外拿掉,規則只剩一條。
- **上一輪點名的兩處**,核對結果如下。
  - `_disp_value_type_err` 已收 `fmt=` 與 `none_ok=` 參數,事後 `.replace` 沒有了。證據:``file: `scripts/lumos:55225` ``。
  - `_loop_round_format` 已統一。

不一致三處,都是 minor。

severity: minor
blocking: 否
引句:「跟規格閘留痕同一個位置濾;呼叫端不再各自重濾」
`_is_outcome_row` 的註解宣稱「讀審查列的入口」都已經濾掉結局帳,但有一個讀帳入口漏了。
- ``file: `scripts/lumos:13221` ``:`cmd_loop_verify_progress` 自己逐行讀帳,只濾 `kind != "spec-gate"`。
- 帶 `outcome` 的列會被算進它輸出的 `rounds`、`kinds` 和 `findings_trend`。這跟其他入口對結局帳的處理不同。
- 它是否該濾可以由編排者裁定,所以標 ⚠:要嘛補濾,要嘛把註解改成列舉實際範圍。

severity: minor
blocking: 否
引句:「照鄰居做法先 shell quote 再清控制字元(_esc_clean),不截斷」
新增 `_rf_qloop` 後,同一支檔案裡「印給人照貼的編號」有兩種寫法。
- `_rf_qloop` 是 quote 後用 `_esc_clean(s, len(s))`,不截斷。
- ``file: `scripts/lumos:16083` ``:`_cap_retro_record_block` 是 `_esc_clean(_shlex.quote(loop_id), 200)`,會截斷。這個函式這輪也被改過,卻沒用 `_rf_qloop`。
- ``file: `scripts/lumos:15797` ``:`_retro_cmd` 又是第三種,整行包起來再清。
- 這輪等於替 canary record 開了一條新的「quote+清」路,沒有併進既有的。結構對,所以只算 minor。

severity: minor
blocking: 否
引句:「整本帳最多讀一次、用到才讀(參數先驗):--orchestrator、--regression-set、跑滿回顧、輪次規則、載體最後記、定錨留痕共用」
`cmd_canary` 內新增 `_lcache` 加閉包 `_lread()` 的就地記憶化。
- 鄰居共用一次讀帳的做法是把 `scan=` 當參數往下傳,例如 ``file: `scripts/lumos:14477` `` 的 `_loop_records_checked_ex(..., scan=scan)`,以及 `_cap_retro_scan` 的 `cache=`。
- 這是同函式內新增的閉包快取慣用法,專案沒有同類做法。
- 它只在區域範圍,目的也單純(讀一次),所以標 ⚠ 交編排者判斷,不是 major。

## 3. 第二種做法

我搜過 `_review_rows`、`.replace(` 改句子、`_canary_ledger_rows(`、`!= "spec-gate"`,結論如下。

- 沒有引入第二套過濾。`_review_rows` 已徹底移除,過濾集中在 `_is_outcome_row` 一個謂詞。
- `_rf_mixed_next` 沒有另一套訊息組裝。
- 上一輪要求的三件事(讀側統一用 `_loop_round_format`、`_disp_value_type_err` 收格式參數、註解歸位)都做到了。
- T6 的定錨檢查由「另外整檔 `read_text`」改成 `_lread()[0]`,是把第二種讀法收回共用讀法,方向正確。
- 只剩上面三條 minor,第一條是漏網的讀帳入口,後兩條是新增了一個與既有慣用法並存的小做法。

不對齊共 3 條,其中 major 0 條
