severity: clean

「併發與資源」席已讀完這份 diff,沒有發現問題。實驗用的暫存目錄已刪。

所有量測都用 Python 3.14 跑,對象是 `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos`。

**`inspect.getsource` 算指紋的成本與退路:已讀,無 finding**
- 單次約 23ms,連算 20 次共 7ms。
- 實跑 `lumos spec-gate --door-rule` 能取到原始碼並印出 `inputs_sha`。
- 退路改用位元組碼,只會讓留痕裡的 `inputs_sha` 在不同 Python 版本間不一樣。我 grep 過,沒有任何程式拿它和留痕比對,所以不會誤判成過期。
- 退路本身我沒有實測,本機也找不到 python3.9。

**`_nogo_skip_lines` 在大檔與病態輸入下的時間:已讀,無 finding**
- 20 萬行清單、10 萬個「## 不做」標題、20 萬行續行,都在 0.2 秒內。
- 20 萬組連續破折號的單行 0.02 秒,30 萬個空白的單行 0.004 秒,重複破折號分隔線的正則 0.005 到 0.01 秒。沒有退化成 O(n²)。
- 內層迴圈和外層共用同一個索引,整體是線性的。

**留痕新欄位的大小上限:已讀,無 finding**
- 寫進留痕的 `nogo_skipped` 只取前 8 筆,每筆是 `[類, 詞, 16 字雜湊]`,所以留痕大小有上限。
- `_door_judge` 在記憶體裡的完整清單沒有上限,但 20 萬筆也只是短陣列,指紋計算是線性的。

**doctor 篩版本的成本:已讀,無 finding**
- 篩選是對 `_two` 做一次 O(n) 掃描,再取前 30 份,沒有新增 I/O。

**推送前重判多算的指紋:已讀,無 finding**
- `_spec_gate_push_stale` 沒有重算 `_door_rule_fingerprint`。
- 它多算的只有 `_door_judge` 裡的 `nogo` 和 `_clause_block_sha` 多加的一行。重判本來就會跑,所以不是新增成本。

**留痕寫入與鎖:已讀,無 finding**
- 寫入路徑沒變,仍是 `_vault_write_lock` 加 `_jsonl_append_verified`。新欄位沒有帶來新的鎖或 I/O。

最高等級 clean,blocking 0 條。
