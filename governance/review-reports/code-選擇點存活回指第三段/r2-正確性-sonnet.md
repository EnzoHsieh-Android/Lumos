severity: minor

審這輪修補差異,沒找到會做出錯行為、破壞合約或損壞資料的洞。我逐項走了一遍:`_choice_layer_cite` 的序號對應、`_choice_layer_one_part` 的終止條件、`_choice_compile_suspects` 的距離排序與 8 個上限、換候選後存活清單用的壞法、`_choice_layer_write` 的整份預檢,以及 `_kill_mtime_settle` 兩條呼叫路徑。另用實際計劃標題掃過 `_CHOICE_LAYER_NOT_BODY_RE`,沒有誤收的標題。只有下面一條小問題。

severity: minor
blocking: 否
`scripts/lumos` 的 `_choice_layer_text`:這輪起顯示的出處只讀判讀檔裡的 `cite` 欄,舊判讀檔沒有這欄。舊判讀檔指 r1 程式碼寫出的檔,例如實驗專案已記下的那批。
- 輸入:第 2 層或第 3 層的判讀檔,`basis` 完整且合格,但沒有 `cite`。
- 走到哪:`basis[cite] if type(cite) is int ...` 得到 `b = None`,接著 `if n in (2, 3) and b is None:` 把 `tail` 設成 `(出處讀不到)`。
- 後果:`choice-points`、存活清單和推送閘的子原因都改印「(出處讀不到)」,出處明明在 `basis` 裡。要重新判讀才會恢復。
- 範圍:只影響顯示,不影響判定。主線上沒有 `governance/choice-layers/`,所以只波及已用 r1 程式碼記過判讀的專案。
- 修法:`cite` 讀不到時退回舊判法,取第一個符合該層條件的 `basis` 項;或在讀端明講舊檔要重判。
- 測試缺口:新案例 `t_choice_layer_minor_r1` 只測了 `basis: []` 這一種讀不到的情形,沒有「有完整 `basis` 但沒有 `cite`」的案例,所以這個行為改了測試也不會紅。

引句:「    if n in (2, 3) and b is None:」

總結:最高等級是 minor
