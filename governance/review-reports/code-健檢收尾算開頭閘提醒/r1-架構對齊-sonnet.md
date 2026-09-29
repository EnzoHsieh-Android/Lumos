severity: minor

## F1 開頭閘提醒逐行算一段,跟既有「一個 warn/warn_soft 呼叫算一段」的口徑不同
severity: minor
blocking: 否
引句:「_top_soft.append("筆記形狀擋")」
佐證行 file: `scripts/lumos:1331`、`scripts/lumos:1347`
1. 既有做法:收尾計數只有一本帳 `_soft`,由 `warn`(空清單分支,1331-1333)與 `warn_soft`(1347-1349)在呼叫時 `segs += 1`、`lines += len(lines)`、`heads.append(head)`。一次呼叫=一段。
2. 這次沒有引入第二本帳:`_top_soft` 只是暫存,最後灌進同一個 `_soft` 當初始值(patch 的 `_soft = {"segs": len(_top_soft), ...}`),收尾讀取端(3185、3190)不變,所以不算第二種計數做法,不到 major。
3. 但口徑有細微差:`_note_shape_doctor_lines` 等回傳多行時,每一行都 append 一次,segs 會等於行數;既有 warn_soft 是一個標題算一段、行數另計。同一道閘吐 3 行,收尾會講「3 段、共 3 條」,而既有口徑是「1 段、共 3 條」。
4. 更貼既有的寫法:開頭的迴圈裡每道閘只在「有任何一行」時 append 一次標題並把 lines 另加行數(例如 `_top_soft.append((head, n_lines))`),或把 `_soft` 與 warn_soft 定義前移,開頭改走 warn_soft(但會吃到 3 條上限收斂,行為要另評)。屬口徑一致性,不擋。
5. 無跨層直呼:全在 run_doctor 內。

最高等級:minor
