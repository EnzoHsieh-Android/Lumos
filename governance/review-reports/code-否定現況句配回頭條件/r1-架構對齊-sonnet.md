severity: minor

整體:note-shape 掛法(拆出小函式、違規段 → 尾句與帳 → 提醒段)、子開關獨立讀取(不擴充 `_note_shape_config`)、hinted 走既有 `_gate_event_or_warn`、字眼表常數貼著首個使用處、doctor 那行放 ci 返回之前、lint 放行條目格式,都跟既有做法對得上,沒有引入第二種做法或跨層直呼。已逐項對過的既有做法(不算 finding):
- 常數貼近使用處:file: `scripts/lumos:25113`(`_NS_POINTER_ONLY_RE` 貼著 `_ns_check_line`)
- 記帳走 `_gate_event_or_warn`、自由欄位放 extra:file: `scripts/lumos:8546`、`scripts/lumos:37912`;kind 是自由字串,沒有名單要登記:file: `scripts/lumos:1234`(只有 gate 名要進 `_KNOWN_GATES`,`note-shape` 早已在)
- 各閘各自一支設定讀取、預設不同不共用:file: `scripts/lumos:28762`(`_drift_old_sentence_config`)
- 輸出參數先例:file: `scripts/lumos:19671`(`result_out=None`)
- 放行條目欄位與寫法(key/rule 空/file 空/reason/by/ts):file: `.lumos/lint-waivers.json` 前 39 筆

## F1 doctor 那行靠訊息文字裡有沒有「看不懂」來挑提醒,跟鄰居用結構化旗標不同
severity: minor
blocking: 否
引句:「return out + [w for w in warns if "看不懂" in w]」
佐證行:file: `scripts/lumos:29962`(`_drift_old_sentence_doctor_lines` 用 `parts["os_warns"]` 結構化欄位與 `parts["old_sentence"] == "off"` 判斷,不比對訊息內文)
1. 既有鄰居的 doctor 開關行是從解析結果的結構化欄位判斷要不要唸;這裡是對 `_note_shape_negation_config` 回的提醒字串做子字串比對,兩支函式的訊息文字被隱性綁在一起。
2. 具體失敗場景:有人把 `_note_shape_negation_config` 裡「看不懂」那句改個說法(例如「無法辨識」),doctor 那行就靜默不再講寫錯值的專案,推送前與 CI 都看不到;沒有跨函式的釘住(diff 內未見對應測試)。
3. 改法方向:讓設定讀取多回一個「值不合法」旗標,或分開兩類提醒,doctor 不比對內文。

最高等級:minor
