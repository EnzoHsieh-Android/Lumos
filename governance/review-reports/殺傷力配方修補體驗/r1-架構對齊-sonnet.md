severity: minor

# 架構對齊-sonnet 第 1 輪報告

## F1 「不帶 --id 就列出」是專案裡沒有先例的第三種列出寫法,spec 沒交代為何不走既有兩種
severity: minor
blocking: 否
引句:「kill-rm 不帶 --id 時列出這篇所有配方的短身分」
file: `scripts/lumos:40733`
1. 專案既有的「列出」有兩種做法:(a) 獨立動詞,如 `loop list`(40645,help 直接寫「這支先給你編號」)、`guard list`(40677)、`guard required`、`rel-cascade list`;(b) 選填「位置參數」省略=全部/摘要,如 `guard trace` 的 node(40720)、`loop` 摘要的 loop_id(40658,「省略=全 loop 摘要」)。反方向的先例是 `decision-reindex`:缺參數時拒絕而不是切換模式,要顯式 `--all`(40874)。
2. spec 讓「必填的寫入旗標 `--id` 一省略,同一個動詞從寫入變唯讀列出」,既有程式碼裡沒有這種「省略選項旗標切模式」的寫法;spec 的 PRIOR-ART 只講了範本與身分演算法,沒對「列出」這件事說明為何不用 `guard kill-ls` 之類獨立動詞或既有慣例。
3. 風險低:省略 --id 只會走唯讀分支(不拿寫入鎖),不會誤刪;且這是 Enzo 裁定的方向、RETIRE-IF 也寫了撤除條件。建議只在 spec 補一句「為何不用獨立 list 動詞(例:rtb 修法行已經是 kill-rm 開頭、少一個動詞好記)」,或在 argparse help 明寫「省略 --id=列出」。這不阻擋實作。
4. 另:既有 `_kill_fix_hint`、kill-add 提醒、P2 都是以 `--id <前12字元>` 嵌在修法指令裡印短身分(13224);spec 列出行用獨立欄位 `<短身分前 12 字元>  平台…` 且結尾補「移除:lumos guard kill-rm <節點> --id <短身分>」,取 12 字元的算法一致,沒有第二套身分,已核對無問題。

## F2 旁路欄的過濾與算入位置,沒對齊既有「單點蓋章」「硬寫 k != "_logged"」的做法
severity: minor
blocking: 否
引句:「所以在組結果時用原配方算 `_kill_recipe_id`,存成底線開頭的旁路欄(照 `_logged` 的做法在 `--json` 輸出前濾掉)」
file: `scripts/lumos:13955`
1. 既有 `_logged` 是在寫 kill-log 的迴圈裡才設(13941-13943),`--json` 前用硬寫 `k != "_logged"` 的字典推導濾掉(13955)。照 spec 字面「照 `_logged` 的做法」,實作者很可能再補一個 `and k != "_rid"` 之類的第二個硬寫名字;若漏改,新旁路欄會洩進 `--json`,違反 [S3]「各筆結果的欄位跟改動前相同」。較貼近既有精神的做法:過濾改成「濾掉所有底線開頭的鍵」一次涵蓋,spec 應明講要濾哪些鍵。
2. 結果是在 9 個 `results.append({**r, ...})` / `results.append(res)` 站點(13798、13836、13845、13855、13861、13868、13873、13883、13908)分散組出來的;既有的 recipe_id、covers、weak 是在迴圈後的「背書欄位蓋章」單點處理(13923 起),但那一步已拿不到原配方(spec 自己說明了)。spec 只說「組結果時」,沒指定位置。若在 9 個站點各算一次會是散落同族寫法;較整齊的做法是在分組迴圈(`for r in recipes: groups.setdefault`,13790)把原配方先換成帶旁路欄的副本,之後各站點既有的 `{**r, …}` 展開自然帶上。建議 spec 點明這個單點位置。
3. kill-log 寫入用明列欄位(13945-13953),不會被旁路欄污染,已核對無問題。

## 其他節
- 範本節:已讀,無 finding。核對「現在是把舊壞法原樣抄進去」對應 `_kill_add_template` 的 `val("new", "'<壞法>'")`(13484 起),`--old` 既有 `'<照現在的程式填原文>'` 寫法,spec 的 `'<照新原文改寫的壞法>'` 與之同一種待填佔位字風格。
- 跳脫節:已讀,無 finding。引句:「各欄經 `_kill_show`(會帶引號);不是物件的元素整個印 `_kill_show(json 原樣)`」。既有慣例:提醒/P2 行裡人寫的欄位用 `_kill_show`(13239、13312-13313,含 `inv[:30]` 截斷),完整 JSON 傾印用 `_kill_esc`(`_kill_rm_show`,13574),spec 兩者的分工與既有一致,未引入第二種跳脫。
- 分流節:已讀,無 finding。列出分支早於寫入鎖與 id 驗證,與既有 `cmd_guard_kill_rm` 開頭驗證順序相容;找不到筆記、整欄解析失敗回 2 同既有 `cmd_guard_kill`/kill-rm 措辭。
- 條款、回退、實務隱患節:已讀,無 finding。

最高等級:minor;blocking 共 0 條
