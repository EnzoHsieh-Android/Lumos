severity: minor

## F1 序號超長防護放在使用點,鄰居是把位數寫進正規式
severity: minor
blocking: 否
引句:「elif len(no) > 9 or int(no) > len(decls[path]) - 1:」
file: `scripts/lumos:41680`(`_COUNT_NUM_RE = re.compile(r"[0-9]{1,9}")`,註解寫明九位數以內)
file: `scripts/lumos:28915`(`_EVENTS_DAYS_RE = re.compile(r"[0-9]{1,5}")`)
file: `scripts/lumos:35143`(`_NS_WD_NUM`,`[0-9]{1,9}`)
file: `scripts/lumos:27875`(`_FINDING_SOURCE_NO_RE = re.compile(r"[1-9][0-9]*")`,本輪沒動)
- 鄰居處理「超長數字轉整數會丟例外」的做法一致:把位數上限寫進正規式,讓不合格的字串在格式檢查就被擋掉。
- 本輪在 `_mr_refs` 的使用點另外加 `len(no) > 9`,正規式仍不限長度。
- 這等於在同一個專案裡出現第二種防護位置,而且使用點只改了 `_mr_refs` 一處。
- `scripts/lumos:11622` 的寫側解析同樣用 `_FINDING_SOURCE_NO_RE.fullmatch(no)`,正規式本身沒有位數上限。
- 超長序號走到錯誤分支時,訊息會說「序號超出」而不是「格式不對」,與鄰居的分類也略有不同。
- 結構上沒有第二套工具,所以只列 minor。

## 三問回答
1. 分層與依賴方向:一致,沒有跨層直呼。
   - `report-normalize --items` 範本的路徑那段現在直接過 `_drift_sh`(`scripts/lumos:10954`),與同檔 `scripts/lumos:28361`、`scripts/lumos:43185` 的呼叫方式相同。
   - 原本自己判斷是否加引號再呼叫 `_sh_quote` 的寫法已拿掉(`_sh_quote` 在 `scripts/lumos:450`)。
   - `cmd_report_normalize` 仍是不碰圖譜的指令。
   - 拿掉「單一字串轉清單」是對的:`scripts/lumos:57433` 的 argparse 是 `nargs="+"`,`scripts/lumos:58316` 傳進來的一定是清單。
2. 命名與錯誤處理:大致一致。
   - 手改帳的怪值改成先判型別再用:`isinstance(mine, str) and mine in _SEV_ORDER` 在 `scripts/lumos:28027`,`sevs` 由集合改成清單在 `scripts/lumos:27939`。
   - 這與鄰居「讀帳時遇到壞型別就判不過、不噴例外」的方向一致。
   - 區域變數 `path_`、`_sep` 沿用同檔 `scripts/lumos:11622` 的 `path_` 命名。
   - 錯誤訊息裡的 `no` 改過 `_esc_clean(no, 12)`,符合同函式對 `fid`、`path` 的處理。
   - 唯一差異就是上面的 F1。
   - 附帶一點:`scripts/lumos:11050` 的 `r.get("severity") in _SEV_ORDER` 若遇到清單值也會丟 TypeError。它不在本次差異內,只是同類手改帳型別問題的鄰居,不列為發現。
3. 第二種做法:沒有自寫一套而鄰居已有的功能。
   - 修補本身是移除自寫的「判斷是否要引號再 `_sh_quote`」邏輯,回到既有的 `_drift_sh`,方向正確。
   - 唯一的新做法是 F1 的使用點長度判斷,屬於同一個防護目的的不同位置。
   - 測試端的改動也一致:`t_disposal_code_minor_release` 和 `t_canary_record_finding_source` 用 `enumerate` 取代 `hash` 當迴圈 id,避免 id 撞名,測試結構沒有出現新做法。

不對齊共 1 條,其中 major 0 條。
