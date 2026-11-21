severity: minor

固定席節點沒有附上(鏡頭計算超時),所以「固定席逐條判定」沒有可判的節點。我只能照 diff 自己判:改動限於記帳新欄、gov 唯讀統計段、`loop next` 範本。我的判斷是處置閘與推送前閘不讀 `finding_seats`,不影響它們的判定。這個判斷我沒有用實驗驗證。

我逐 hunk 讀完整份 diff,追了 `cmd_canary` 的讀帳順序、`_roster_kind`、`_loop_ts_key`、`_loop_records_checked_ex` 這幾個呼叫端。實跑檢查是用真帳 `docs/.canary-log.jsonl`(6601 列)。

**Finding 1:去輪次記號的正規式會把不同模型併成同一席,也會把帶小數點的版本號切壞**

severity: minor
blocking: 否
file: `scripts/lumos:18071` 附近(diff 內 `_SEAT_ROUND_MARK_RE`,在 `_seat_noise_counts` 以 `re.sub` 套用)
引句:「_SEAT_ROUND_MARK_RE = re.compile(r"(?:-?r\d+|\d+)(?=-[A-Za-z][\w.]*$)")」
失敗場景:
- 這個正規式的 `\d+` 分支,只要「數字後面接 `-` 加英文字母收尾」就會被刪。它不分這個數字是輪次還是模型版本。
- 輸入 `外家否決-gpt-5.6-sol`:`6` 後面是 `-sol`,被刪,結果成了 `外家否決-gpt-5.-sol`。`-gpt-5.7-sol` 也會變成同一個字串,兩個不同模型被併成一席。
- 輸入 `external-veto-gemini-3-flash`:變成 `external-veto-gemini--flash`,`gemini-2-flash` 也併進來。
- 這違反計劃〈做法〉統計寫的「不同模型不合併」,以及 diff 內 `_render_seat_noise` 輸出的口徑句「同一席不同模型分開列」。
- 實跑證據:拿真帳的 auditor 跑這支正規式,`外家否決-gpt-5.6-sol` 有 20 列、`外家finder-gpt-5.6-sol` 有 4 列、`external-veto-gemini-3-flash` 有 3 列,都被切壞。
- 影響只在 `gov --stats` 這段逐席數字(只給人看,不進閘)。外家席是計劃自己要拿來評估調席位的對象,數字會失真,印出的席名也是壞的。
- 最小重現:`python3.14 -c "import re;R=re.compile(r'(?:-?r\d+|\d+)(?=-[A-Za-z][\w.]*$)');print(R.sub('','外家否決-gpt-5.6-sol'))"`,輸出 `外家否決-gpt-5.-sol`。
- 修法方向:只在角色與模型尾碼之間、且數字前面是非數字非點的字元時才去記號;或限定 `-?r\d+` 加「中文或字母緊接數字」的形式,不要裸 `\d+`。

其他我檢查過、不成立的疑點:
- `_finding_seat_parse` 用到的 `rreasons`,在同一縮排層、`_finding_seat_parse` 呼叫之前已定義。
- `_lrows` 在 `_lerr` 設了時是可讀的那一份(整本壞時是 `[]`),`_finding_seat_write_block` 不會對 `None` 迭代。
- 帳上時間讀不動而擋下的路徑:真帳 6601 列沒有一筆缺時區,不會誤擋舊迴圈。
- `_roster_kind` 對 `code` 開頭沒連字號回 `None`,在 `_finding_seat_required_block` 內被視為非設計審而必填,跟計劃的「從嚴」一致。
- `gov --stats` 的窗口起算點 `cutoff` 是 `YYYY-MM-DD` 字串,`fromisoformat` 讀得動。

最後一行總結:max severity = minor
