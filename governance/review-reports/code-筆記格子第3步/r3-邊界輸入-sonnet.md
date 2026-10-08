severity: minor

整體判斷:blocking 級的問題我沒找到,修正都成立。我在已套用 diff 的 repo 裡實跑了最壞輸入。`-k slots_doctor_reminders` 的 36 個、`-k slots_retire_issue` 的 8 個測試都通過。

**逐項驗證修正**
- **單行 summary 寫法**:`summary: KEY:x`、單引號包 `RULE:`、尾端 `# 註解`、`summary:RULE:` 沒空白、`|+`、`>`、單行與區塊混用,`_note_summary_entries` 都沒丟例外。
  - 值不是前綴開頭的(如 `這是一句話 RULE:甲`)回 `{}`。
  - 空字串、空值回 `{}`。
  - `|+` 走區塊路徑,得到正確條目。
- **`_lint_new_config(from_snapshot=True)`**:
  - 帶 BOM 的 bytes 去掉 BOM 後正常讀到 `off`。
  - bytearray 和 str 都正常。
  - None 回預設且沒有警告。
  - 空 bytes 和非 UTF-8 回預設,附一句 `JSONDecodeError` 警告。
  - 都沒丟例外,讀法跟 `_nodehome_config` 一致。
- **S16 的 `_esc_clean`**:rel 帶 ESC、BEL、C1 時都被換成空格,輸出為單行。
- **`_drift_jsonl_iter`**:`None`、壞行、10 萬層巢狀 `[` 都不崩,只跳那一行。

R3B1
severity: minor
blocking: 否 — 重複 `summary:` 鍵本身是壞 YAML,只造成行號錯位,判定內容沒錯。
- 同一篇有兩個 `summary:` 鍵時,值取最後一個,行號卻取第一個。實測 `summary: RULE:甲` 加 `summary: RULE:乙` 得到 `{4: 'RULE:乙'}`,行號 4 是甲那行。
- 影響:S17 到 S19 提醒的 `rel:行號` 會指到不是這條內容的行。
引句:「no = next((i for i, ln in enumerate(n.fm_lines, 2) if re.match(r"summary\s*:\s*\S", ln)), None)」
file: `scripts/lumos:3506`

R3B2
severity: minor
blocking: 否 — 只影響提醒行的可讀性,條目判定不受影響。
- rel 很長(目錄深或檔名長)時,300 字截斷吃掉尾端的「原因:句子」。
- 實測 350 字元的 rel 輸出只剩路徑加 `…`,S16 看不出是 `[until:]` 過期還是別的原因。
- `_DOCTOR_LINE_MAX` 的註解承認截的是尾端。
引句:「_DOCTOR_LINE_MAX = 300       # doctor 提醒行印出前清控制字元,最多這麼長(路徑與行號在最前面,截的是尾端)」
file: `scripts/lumos:3497`

R3B3 ⚠
severity: minor
blocking: 否 — 只在 stderr 管線壞掉時發生,鄰居 m1 與 c1 到 c5 也是同樣取捨。
- 拿掉 `_drift_retire_quiet` 後,「清單印到一半出錯」這支 except 裡的 `print(..., file=sys.stderr)` 沒有再包保護。
- 實測 stderr 是會丟 `BrokenPipeError` 的物件、有 must 項時,`_drift_retire_report` 直接把 `BrokenPipeError` 丟出去。
  - 這一筆帳沒寫。
  - rc 沒回傳;warn 模式也一樣。
  - 例外會穿過 `cmd_drift_check`,是否擋推送取決於呼叫端。
- 以前的包裝吞掉了這個情境。這是 r2 架構對齊席要求的取捨,筆記也寫明了,所以不升級。若要保留,建議在記帳挪到印出之前,或把 except 內的 print 包 try。
引句:「print(f"存量漂移檢查:RULE 撤除條件的清單印到一半出錯({type(ex).__name__}),判定照舊", file=sys.stderr)」
file: `scripts/lumos:32473`

R3B4
severity: minor
blocking: 否 — `_esc_clean` 是共用的既有消毒函式,不是這次 diff 引入的。
- `_esc_clean` 只換掉 C0 與 `\x7f` 到 `\x9f`,U+2028、U+2029 會原樣通過。
- 實測 S16 的 rel 帶 U+2028 時,輸出仍含該字元。多數終端不換行,風險低,但跟「一行一筆」的目的不完全一致。
引句:「out = "".join(ch if ch >= " " and not ("\x7f" <= ch <= "\x9f") else " " for ch in str(v))」
file: `scripts/lumos:10457`

**圖譜鏡頭**
- `Systems/lumos-cli-read`:S16 到 S19 共用 `_note_summary_entries`、S17 與 S18 在 `--ci` 不跑、印出前清控制字元、用 `_doctor_cfg_bytes` 讀設定,都跟程式一致,合約沒破。
- `Systems/存量漂移守衛`:筆記改成「先印後記」,與 `_drift_retire_report` 現況相符。沒有 `★INVARIANT★` 或合約行被動到。
- `Issues/撤除條件檢查末輪遺留四項` 與 `Projects/筆記格子寫法與過期檢查_計劃`:文字與程式一致。
  - S13 加掛的兩支測試都存在且通過。
  - S12 未動。
  - 計劃第 13 條限制改成「doctor 不評估 `when-*`、度量式由 S18 判」,與程式一致。
- 我沒有逐一核對「m1 與 c1 到 c5 也是先印後記」這句,只確認了 `_drift_report_must` 與 `_drift_m1_report` 存在。

最高嚴重度 minor,blocking 0 條
