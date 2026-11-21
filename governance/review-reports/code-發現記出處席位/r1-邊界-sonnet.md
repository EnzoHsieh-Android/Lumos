severity: major

審查範圍:只讀 diff 加上在 `/tmp/lumos-seat-work/code-發現記出處席位/邊界-sonnet/w` 的複本上實跑。沒改 repo 裡的檔,也沒跑 `-k` 測試。固定席筆記這次沒附,見最後一段。

### Finding 1:沒帶 `--loop` 的載體會繞過席名核對,壞席名直接進帳
severity: major
blocking: 是
file: `scripts/lumos:20197`(diff 內是 cmd_canary 尾端的 `_fsb = ...` 那行)
引句:「    _fsb = _finding_seat_write_block(env, loop, round_id, auditor, rec, _lrows, _lerr) if (loop and outcome is None and "findings_set" in rec) else None」

具體失敗場景:
- 輸入:`canary record none --auditor 載體-sonnet … --findings-set c1 --folded-set c1 --refuted-set none --finding-seat c1=亂寫`,不帶 `--loop`。
- 路徑:形式檢查 `_finding_seat_parse` 通過,`rec["finding_seats"]` 設好。`_finding_seat_write_block` 因為 `loop` 是假值而整支跳過,席名核對、NFC 正規化、必填判定都沒走。
- 重現:實跑 rc=0,`.canary-log.jsonl` 末列是 `"finding_seats": {"c1": ["亂寫"]}`。同一個複本裡,帶 `--loop` 的同一筆會被擋下(「不是這一輪帳上任何一席的 --auditor」)。
- 連帶:`_seat_noise_carriers` 用 `(loop, round)` 當鍵。兩筆沒有迴圈的載體都是 `(None, None)`,只留最後一筆。實跑記兩筆沒有迴圈的載體,逐席段只印 `Y:1 條`,第一筆的 X 整個消失。
- 影響:合約是「席名要是同輪帳上的 auditor」,這條路徑違反它。亂寫的席名會進逐席沒用率,又因為帳不能撤銷而撤不掉。
- 建議:有 `finding_seats` 卻沒有 `loop` 時直接擋下;或把核對條件改成只看 `"findings_set" in rec`,`loop` 為空時擋。

### Finding 2:去輪次記號的正則會吃掉模型名裡的版本數字,不同模型被併成同一席
severity: minor
blocking: 否
file: `scripts/lumos:288`(`_SEAT_ROUND_MARK_RE`)
引句:「_SEAT_ROUND_MARK_RE = re.compile(r"(?:-?r\d+|\d+)(?=-[A-Za-z][\w.]*$)")」

具體失敗場景:
- 實跑結果:`邊界-claude-3-opus` 和 `邊界-claude-4-opus` 都變成 `邊界-claude--opus`;`gemini-2.5-pro` 和 `gemini-2.0-pro` 都變成 `gemini-2.-pro`;`opus-4-7-xhigh` 變成 `opus-4--xhigh`。
- 影響:這跟統計段尾「同一席不同模型分開列」互相矛盾。版本 3 和 4 的沒用率被混在一起,而且印出的席名是壞的。
- 反面:`邊界r2-sonnet` 和 `邊界-r2-sonnet` 都正確收成 `邊界-sonnet`。`r2-邊界-外家` 這類輪次記號在前面、尾碼是中文的,不會被去掉,同一席會分開列。
- 建議:只去 `r\d+`,不去純數字。

### Finding 3:時間讀不動的擋下訊息教的脫困法做不到
severity: minor
blocking: 否
file: `scripts/lumos:19451`(`_finding_seat_required_block`)
引句:「壞資料不放行(修好那一筆再記)」

具體失敗場景:
- 輸入:一個 2020 年開的舊迴圈,帳上另有一列 ts 壞掉,載體沒帶 `--finding-seat`。
- 路徑:`any(k is None for k in keys)` 對整個迴圈的所有列都成立。即使首筆早於生效日、本來不必填,也被擋成 rc2。
- 問題:訊息叫人「修好那一筆」,但審查帳是只增不改(專案慣例「帳不能撤銷」)。真正的脫困法是補帶 `--finding-seat`,訊息沒講,擋下的原因也跟「必填」無關。
- 建議:訊息加一句「或補帶 --finding-seat」,或舊迴圈(帳上存在可解析且早於生效日的列)不因壞列擋。

### Finding 4:生效日覆寫值寫成日期格式會被安靜忽略
severity: minor
blocking: 否
file: `scripts/lumos:19436`(`_finding_seat_since_key`)
引句:「    return k if k is not None else _loop_ts_key(_FINDING_SEAT_SINCE)」

具體失敗場景:
- 輸入:`LUMOS_FINDING_SEAT_SINCE=9999-12-31`。同檔其他旗標(`LUMOS_HIGH_RISK_EVIDENCE_SINCE` 等)都用這種寫法。
- 路徑:`_loop_ts_key` 對沒帶時區的值回 None,於是退回 2026-11-22 的常數。覆寫沒生效,也沒有警告。
- 影響:想把必填關掉的人會在生效日後被擋,卻不知道為什麼。只有測試總檔預設值用了完整時區格式才沒踩到。
- 建議:設了環境變數卻解析不了時印一句警告,或接受日期格式。

### 統計段在各種帳形狀下實跑的結果

| 帳形狀 | 結果 |
|---|---|
| 空 `finding_seats`(`{}`) | 整段不印 |
| 只有一筆載體 | 印一行,標「樣本少」 |
| `--since 0`、負數 | 整段不印,不炸 |
| `--since 3` | 標題寫「近 3 天」 |
| 全部是沒用的條(沒有折入) | 印 100%,沒有除以零 |
| 同一 id 同時在折入和重現不到 | 算有用 |
| `folded_set` 型別壞掉(dict) | 整列被 gov 載入層丟掉,不噴例外 |
| 沒帶時區的 ts | 整段不印 |

另外,「沒有迴圈的載體互相覆蓋」見 Finding 1。

### 其他鏡頭的判定
- 席名大小寫或全半形只差一點(`正確性-SONNET`、`正確性－sonnet`):rc2。訊息列出帳上現有的席名,照抄可脫困。
- id 叫 `none`:被既有的保留字擋(`--findings-set` 裡 `none` 是保留字),不是新程式碼的問題。
- 生效日當下:`first < since` 才免填,剛好等於生效日要填,方向正確。
- `loop next` 範本:`<id=席名>` 是單一佔位符,多條發現要重複寫。測試只替換成 `z1=s2-sonnet`,沒走重現不到的涵蓋規則。範本本身 `--refuted-set none`,所以不會因此跑不過。

### 固定席節點
這次沒附(派工詞寫明鏡頭計算超時),所以逐條判定無從做。從 diff 本身看,Finding 1 的改法會落在 `Systems/canary-audit` 與 `Systems/loop-convergence-recording` 宣稱的「載體記帳涵蓋與同輪席名核對」合約上。

severity: major
(最高等級,共 1 條 major、3 條 minor)
