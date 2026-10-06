severity: major

簡化鏡頭。已實測:對 HEAD..HEAD 跑 pitfalls / spec-gate --push-check / code-loop check 都正常(suite=docs、OK),所以「空範圍照常跑」可行。固定席附的合約/事故節點:派工訊息未附,無法逐條判,標 ⚠ 不影響判定。

## F1 抽新函式 pp_block_range_for 與新變數 _brange 都不需要:_hrange 已在同一個迴圈裡、同一個位置算好
severity: major
blocking: 是——spec 要求的改法比必要多一個函式加一個變數,且把已通過審查的 _hrange 段落搬動,違反最小改動;判準:有更小的等價改法。
spec 段落:「做法」第 1、2 點。
引句:「新增 `pp_block_range_for`:跟現在 `_hrange` 那段逐字同一套判斷」
問題:file: `scripts/hooks/pre-push:332-344` 的 _hrange 在迴圈內、`impact_once "$_range"`(file: `scripts/hooks/pre-push:371`)之前就已算好,而且無條件算(if 外面)。spec 要新增函式、搬走這段、再算 _brange,結果 _brange 就是 _hrange 加一行空字串補值。
更小的改法(零新函式、零搬動):
  _brange="${_hrange:-$_lsha..$_lsha}"   # 一行,放在 _hrange 那段 fi 之後
  然後把 371、372、384、396、423、432、438 行的 _range 換成 _brange。
抽函式的唯一理由是「_hrange 與別處兩處各寫一份」,但本案之後 _hrange 只有一個寫處,沒有第二個使用者,抽函式是為了抽而抽。註解(file: `scripts/hooks/pre-push:318-319`)還警告過兩處各寫一份會漂移——那是針對 pp_range_for 與 pp_touched_file 共用,與 _hrange 無關。
具體例:新分支首推、遠端沒有、本地兩個新提交 → 實際 _hrange=`<第一個新提交的父>..<頂端>`,小改動版與 spec 版輸出同一字串,S1~S4 測試兩種寫法都綠。

## F2 兩套範圍並存之外還有第三個名字:_range、_hrange、_brange 其實只有兩種值,應收成兩個名字
severity: minor
blocking: 否——只是可讀性與後續維護成本,不影響正確性。
spec 段落:「做法」第 3、4 點。
問題:做完後 _hrange(空字串=不查)與 _brange(空字串=空範圍)兩個變數內容幾乎相同,下一個讀者必問「為什麼兩個」。照 F1 小改法,保留 _hrange 的語意不動(用於每支檔有家的「空就不查」),_brange 只是它的「空→空範圍」版,一行別名即可,不用再寫一段註解解釋「不同的兩套」(第 4 點的註解重寫也縮成一句)。

## F3 更小的方向:讓 pp_range_for 本身改用新起點(一套取代兩套)——spec 沒有比較,需交代為何不選
severity: major
blocking: 是——spec 的「不選」只列了兩個方案,沒列這個最小方案,也沒說明兩套並存的代價值得;判準:設計遺漏了顯而易見的更簡選項。
spec 段落:「範圍」的「不做」第一條、「不選」欄。
引句:「照舊用 `pp_range_for` 寧可多掃。受波及合約測試提醒」
問題:pp_range_for(file: `scripts/hooks/pre-push:39-45`)與 _hrange 的差別只剩兩點:(a)沒有遠端舊值時走空樹 vs 找最早新提交;(b)全在遠端時 _hrange 空、pp_range_for 不會空。把 pp_range_for 改成 _hrange 的邏輯後,三個只提醒的使用者(pp_touched_file、標籤路徑的 pitfalls --diff、test-layers)只會「範圍變小」:
  - pp_touched_file(file: `scripts/hooks/pre-push:69-77`):註解自己寫「別人的逾期不該擋掉你的推送」,範圍變小更符合原意。
  - 標籤推送 pitfalls:只印提醒;test-layers:只印建議。
  - 代價:標籤推送、頂端全在遠端分支上時這三處不再提醒。這是可論述的取捨,但 spec 現在把它當成「為了保守而刻意保留空樹」卻沒給具體失敗場景;file: `scripts/hooks/pre-push:36-38` 註解「放行會讓推個新分支變成穩定繞法」針對的是會擋的閘,不是只提醒的三處。
  - 但要注意:pp_range_for 在 pp_touched_file 要求回傳非空(git diff "" 會報錯被 `|| true` 吞掉);改函式就得處理空輸出。這也是 F1 小改法比「改 pp_range_for」好的地方:不碰既有函式,零風險。
結論:若要比 spec 更徹底簡化,選「改 pp_range_for」(一套取代兩套,刪掉 file: `scripts/hooks/pre-push:330-331` 那句『別把兩套合併成一套』);若求最小改動,選 F1 的一行別名。spec 現在兩者都不是:新增函式又保留兩套。至少要在「不選」欄寫明為什麼不採這兩者。使用者「修工具」的方向不受影響。

## F4 另一條路「改傳全零給 lumos 讓它算」:spec 的理由只對 impact_once 成立,對其餘四道不成立
severity: minor
blocking: 否——可行性有別條路能達成,spec 的理由略過頭;判準:不涉及正確性,屬設計取捨說明不足。
spec 段落:PRIOR-ART。
引句:「但它對「明寫的空樹」照字面從空樹比——掛鉤傳的正是明寫的空樹,所以改在掛鉤這一層。」
問題:這句說明為何不改傳全零,但事實是:改傳 `$_ZERO..$_lsha` 給 pitfalls --diff / spec-gate --push-check / code-loop check --diff(這三道在 lumos 內走 _lens_push_base,file: `scripts/lumos:41772-41801`)就能得到跟 CI 完全相同的算法(跟主線分岔點),掛鉤零新邏輯。反對理由有兩個且 spec 沒寫:(1)impact_once 要真範圍字串;(2)_lens_push_base 在合過主線、沒 upstream 時會算錯(file: `scripts/lumos:41783-41785` 明文說這是已知洞),所以才不採。若 spec 要說服人,應把這兩條寫進「不選」。目前讀者只會得到「掛鉤傳空樹所以只能改掛鉤」的假二分。
