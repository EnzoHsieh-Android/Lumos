severity: minor

# 代碼審第 1 輪 正確性席(正確性-opus)

## 總結

**主修法成立**:派工詞列的每種情境我都拿基底 d8b02331 和 5fc409a5 實跑對照過,基底會判錯的,新版全部判對;不會出錯的路徑(還原失敗、drifted、逃逸、baseline 非綠)判定與回傳碼都跟基底一樣;`--json` 與 kill-log 的欄位集合沒變(只差在判定變了以後,survived 那筆本來就會帶 tail)。正常環境不會出現假的弱證據。只找到 1 條 minor:寫後確認失敗時,弱證據標錯了是哪一條配方。

引句:「mstate["r"] = int(time.time())   # 每個測試指令的 baseline 都記(夾在配方之間)」

實測對照(本機 macOS,run_cmd 用系統的 python3 3.9 / make 3.81,清掉 PYTHONDONTWRITEBYTECODE;lumos 用 /opt/homebrew/bin/python3;腳本在 `pcc-r1-work-正確性-opus/s1.py`–`s5.py`)

| 情境 | 期望 | 基底 d8b02331 | 新版 5fc409a5 |
|---|---|---|---|
| A 同一支檔兩條、改完一樣大(傷害在前、無害在後) | killed, survived | killed, killed ×3 | killed, survived ×3 |
| B 傷害壞法改完跟原檔一樣大(LIMIT = 5→6) | killed | survived ×3 | killed ×3 |
| C 先改 a(傷害、同大小)再改 b(無害),測試兩支都 import | killed, survived | survived, survived ×3 | killed, survived ×3 |
| D1 make,指令帶 {method}:TestA 傷害 → TestB 無害(中間跑新的 baseline)→ TestA 傷害 | killed, survived, killed | survived ×3 ×3 | 對 ×3 |
| D2 make:TestA 無害 → TestB 傷害(TestB 有自己的 baseline) | survived, killed | survived, survived ×3 | 對 ×3 |
| E 兩個平台(p1 整套一起跑、p2 帶 {method}),各兩條 | p1: killed, survived;p2: killed, survived | p1 killed, killed;p2 survived, survived | 對;weak 只有 p1(整套一起跑)為 true,跟基底同 |
| F 還原失敗(測試跑完把工作樹的 index 鎖住) | error、整組停 | error, rc2 | error, rc2(一樣) |
| G drifted、路徑逃逸、檔不存在 | drifted/error/drifted、不等待 | rc2,0.9–1.1 秒 | 一樣,沒有多等 |
| H baseline 非綠 | abort | abort rc2 | abort rc2 |
| I `--json` 鍵、kill-log 鍵 | 不變 | — | 鍵集合一樣;沒有 `_mtime_unsure`;正常跑沒有時間提醒 |

條款測試三支在 clone 裡跑都綠(`-k no_stale_build_cache` 13.5 秒、`-k mtime_unsure`、`-k no_future_mtime`)。

推想上也查過、沒找到問題的:
- 一組裡每次寫檔讀回的秒數嚴格遞增(w 只在讀回成功時更新,每次寫前都要求晚於 w),同一支檔不同版本的修改時間一定不同秒;第一次寫一定晚於 baseline 結束,所以也不會跟建工作樹時的原檔同秒。
- Linux 這類檔案時間戳比牆鐘落後幾毫秒的系統:讀回會撞到 floor、多等 1 秒補碰一次,判定還是對的,只是慢。
- 只到 2 秒的檔案系統:最多重試兩次就能跨過去。
- 時鐘往回撥:往回 6 秒以內的,等待 + 重試吸收得掉;撥更多的話,還原跟下一條寫檔都會被標弱證據,而且撥回之後寫出的修改時間不會跟壞法撞同一秒,不會真的吃到舊快取。
- 多平台每組各自一份工作樹、各自一份狀態,不會互相干擾。
- weak 的消費端(算背書時要求「killed 而且 weak 不是 true」)讀到的是收尾重算後的值,`_mtime_unsure` 有算進去。

## F1 還原後的寫後確認失敗時,弱證據標在已經跑完的這一條,真正可能吃到舊快取的下一條反而沒標

severity: minor
blocking: 否
引句:「mt_ok = _kill_after_write(target, mstate) and mt_ok」
file: `scripts/lumos:13996`
file: `scripts/lumos:14046`

1. 還原這次寫檔是在這條配方的測試**跑完之後**才發生的。還原後修改時間沒錯開,影響的是**下一條**配方的測試:例如下一條改的是別支檔,測試卻 import 這支,可能吃到壞法留下的快取。但程式把這次失敗併進這一條的 `mt_ok`,所以被標成弱證據的是這一條(它的測試在還原前就跑完了,不受影響),下一條如果自己的寫檔讀回都正常,weak 就是 false。結果是:「時間沒錯開,這些結果記成弱證據」這句提醒,標的是錯的那一列。
2. 模擬重現(行程內呼叫新版,只讓「第 1 條的還原」那一次寫前不等、寫後確認回 False,用來模擬還原的時間沒錯開;配方:a.py `A = 1`→`A = 2` 會傷到、b.py `B = 1`→`B =1 ` 無害,run_cmd 帶 {method}):
   ```
   /opt/homebrew/bin/python3 s5.py   (×3)
   [('a.py', 'killed', True), ('b.py', 'killed', False)]
   ⚠ 有配方寫檔後修改時間沒能跟上一次錯開(…)這些結果記成弱證據
   ```
   無害的 b 吃到 a 壞法的快取,被判成 killed,而且 weak=false,背書會把它當強證據;反而判對的 a 被標成 weak。
3. 為什麼只給 minor:在真實環境裡,我造不出「只有還原那次讀回失敗、下一條寫檔讀回卻成功,而且還原時間剛好跟壞法同秒」的情況。造成讀回失敗的原因(時間精度太粗、時鐘異常)通常整組都會碰到,下一條自己也會被標;時鐘往回撥的情況也算過了,不會真的撞秒。上面的重現是模擬出來的,所以照規則不升 major。
4. 修法建議(擇一):還原後讀回失敗時,把「下一條要標弱證據」記在 mstate(例:`mstate["taint"]=True`),下一條結果再帶上 `_mtime_unsure`;或者兩邊都標。同一組最後一條的還原讀回失敗時,其實沒有下一條會受影響。計劃〈做法〉寫的是「這條結果」,所以這是計劃本身的語意漏洞,要改的話計劃要跟著改。

最高等級:minor
