severity: minor

我讀了主審 patch,也跑了 `python3.14 scripts/test_lumos.py -k light`,結果 204 passed、0 failed。以下是找到的問題。

severity: minor
blocking: 否 — 只在手改審查帳、塞入含 NUL 字元的路徑時才會觸發,正常記帳寫不出這種路徑,而且崩潰是擋下而不是放行。
引句:「return (q if q.is_absolute() else root / q).resolve()」
問題:`_nogo_review_unbound` 對帳上的 `spec_path` 和 `snapshot_path` 只擋了非字串,沒擋含 NUL 字元的字串。`_at(sp)` 在 try 外面呼叫,`Path.resolve()` 碰到 NUL 會丟 `ValueError`。`_at(snp).read_bytes()` 雖然在 try 裡,但 except 只接 `OSError`,`ValueError` 一樣漏出去。這跟本輪已經處理過的「超深巢狀行會讓推送前檢查崩潰」是同一族。
具體失敗情境:帳上有一行手改的 `"spec_path": "a\u0000b"`,推送前整支崩成 traceback,而不是印出「沒綁到」的原因。我用 python3.14 實測確認 `resolve()` 和 `read_bytes()` 對 NUL 都丟 `ValueError`;長路徑只丟 `OSError`,已被接住。
佐證:file: `scripts/lumos:9150`(`_nogo_review_unbound` 內的 `_at`)和 `scripts/lumos:9163`(`read_bytes` 的 try)。

severity: minor
blocking: 否 — 擋的對象很窄(只有判成風險低、又略過危險詞的計劃),逃生路是在計劃加 `plan_risk: high`;而且這是 r4 G2 刻意的決定,測試 `t_prepush_nogo_plan_not_skipped` 有釘。
引句:「if prel in touched_plans or full:」
問題:推送範圍只要碰到任何 `Projects/*.md`(狀態是 done 或 superseded 也算),就會用新規則重判門。凡是判風險低、不做清單又略過危險詞、而且帳上沒有「風險低的規格閘留痕」的,一律擋,要求先跑 `lumos spec-gate` 再走一席綁快照的輕量審。
具體失敗情境:舊規則下,不做節裡寫「不做退款」的計劃會被判風險高,所以這類歷史計劃帳上本來就沒有風險低的留痕。新規則下它們變成風險低,但留痕仍沒有。只要這種已結案或撤案的計劃被推送碰到(批次改名、`lumos set`、修連結),整個推送就被擋。逃生路是去改歷史計劃,補規格閘、補輕量審,或加 `plan_risk: high`。
佐證:file: `scripts/lumos:9309`(`_spec_gate_push_scan` 迴圈)和 `scripts/lumos:9255`(`_spec_gate_push_nogo_only`)。

severity: minor
blocking: 否 — 席名由編排者自己填,單人依序操作的威脅模型下,這道檢查本來就只是防呆。
引句:「isinstance(a, str) and a.strip() and not nfc(a.strip()).startswith」
問題:判斷「不是架構對齊席」只看席名開頭是不是中文的「架構對齊」。英文名如 `arch-alignment-sonnet`,或加了輪次前綴如 `r5-架構對齊`,都會被當成通才席。結果是只有架構對齊席的審查也能放行,這和 G4 要擋的情境一樣。
具體失敗情境:窗口裡只有一筆 auditor 為 `arch-align-opus` 的乾淨審查,`_seat_ok` 判真,推送前放行。
佐證:file: `scripts/lumos:9234`。

已讀,無 finding:
- `loop status --light` 新增的 `bad` 結論:欄位型別壞掉時回 rc2,印在 stderr,位置在 ratchet 和 empty 之後。這個函式只有兩個呼叫端,另一個是推送前檢查,也有處理 `bad`。正常記帳寫入的 `findings` 一定是整數、雜湊一定是字串,所以不會讓合法紀錄多出 rc2。原本 rc1 的路徑沒變。
- `_door_keyword_hits` 和 `_nogo_skipped_rows` 抽出後,結果跟原本逐行相同:行號跳過條件、每行每類取第一個命中、去空白後雜湊前 16 字、排序都一致。`_door_judge` 把已算好的 `hits` 傳下去,沒有重算;快照和現況也用同一套算法。
- 平台設定讀不動的路徑:`idx=False` 後,有風險低留痕的計劃只做不做清單的檢查,其餘放行,最後回 `(None, [])`,和原本「整個放行」一致。非風險低的計劃不會被誤要求跑測試。
- 小改動閘的 `oks` 只收走完整路徑的計劃,輕量審的檢查不會干擾它。
- 讀規格閘留痕時多接 `RecursionError`,和 `_nogo_light_window` 的讀法一致。
- `_nogo_light_cmd` 加 shell 引號:只改指令的呈現,測試也釘了引號。
- 窗口在每筆規格閘留痕重開,舊的 major 和帶輪次的紀錄不再算。這和 `loop status --light` 的永久 ratchet 語意不同,但是 r4 G3 明講的設計,所以只記一筆備註,不當 finding。

最高等級 minor,blocking 0 條。
