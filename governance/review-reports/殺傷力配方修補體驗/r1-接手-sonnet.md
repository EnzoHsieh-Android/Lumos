severity: major

核對範圍:實際 clone 後在臨時 git 專案跑了 guard kill(缺 old / file 是數字 / 非物件 / invariant 是數字四種壞配方)、kill-add 帶待填字樣的 --new、並讀了 `_kill_add_template`、`cmd_guard_kill_rm`、`cmd_guard_kill` 全段。

## F1 S3「格式壞的配方也一樣」在 guard kill 上大多跑不到,測試無法照寫
severity: major
blocking: 是
引句:「而且該短身分拿去 `kill-rm --id` 應對得到那一條(格式壞的配方也一樣)」
file: `scripts/lumos:13792`
1. 實測(臨時專案,兩條配方:一條好的、一條壞的)。壞配方是 file=5 時,`guard kill` 在 `os.path.join(wt, r.get("file",""))`(lumos:13859)丟 TypeError 整支崩潰,一行結果都沒印。
2. 壞配方是不可迭代元素(數字 3)時,`groups.setdefault(r.get("platform")…)`(lumos:13792)就 AttributeError,同樣崩潰。
3. invariant 是數字時,到人讀輸出 `r.get('invariant','')[:30]`(lumos:13964)才 TypeError,連好配方的結果都沒印出來。
4. 只有「缺 old」這種(判成 drifted,`count("")` 恆不為 1)能走到人讀行。所以 S3 測試要寫「格式壞的也一樣」只有缺 old 一種可驗;spec 的白話與做法段卻舉「缺 old、file 是數字」,file 是數字根本不會出現在結果行。
5. 接手人兩條路都要猜:(a)把 guard kill 對壞配方的崩潰也修掉(但範圍段寫「guard kill 的判法、回傳碼…都不改」,衝突);(b)S3 縮成只測缺 old。spec 要明寫選哪個,並把「file 是數字」的例子從做法段刪掉或改成「該情況 guard kill 本來就崩潰、不在本計劃範圍,另立 Issue」。

## F2 範本改成待填 --new 後,忘了改的人會得到假的「殺死」
severity: major
blocking: 是
引句:「`_kill_add_template` 的 `--new` 一律印 `'<照新原文改寫的壞法>'`」
file: `scripts/lumos:13484`
1. 舊範本 `--old` 是待填字樣,kill-add 寫入後會因「原文找不到」在標準錯誤提醒;但 `--new` 沒有任何檢查(`cmd_guard_kill_add` 只擋 old==new)。
2. 實測:`guard kill-add Systems/E 上限恆為5 --file prod.py --old 'LIMIT = 5' --new '<照新原文改寫的壞法>'` 回 0、寫入成功、沒有任何提醒;再跑 `guard kill` 得 killed_unattributed(run_cmd 帶 {method} 過濾時會是強殺 killed),因為把 `<照新原文改寫的壞法>` 塞進程式是語法錯誤,什麼測試都會紅。
3. 也就是照 spec 改完,rtb 那種「複製範本、只改了 --old 忘了 --new」的人會得到一條綠色勾的、毫無意義的配方。舊作法(抄舊壞法)至少是個可執行的壞法。
4. 第 1 條(重加後當場試跑)明說延後,所以這段空窗沒有任何機制擋。spec 需要:kill-add 對 `--new` 含 `<照新原文` 開頭的待填字樣一律擋或警告,或把這個風險明寫進〈實務隱患〉並附回頭條件,加一條 S 條款與測試。

## F3 S2 對格式壞配方的欄位怎麼印沒定義,照字面實作會崩潰
severity: major
blocking: 是
引句:「各欄經 `_kill_show`(會帶引號);不是物件的元素整個印 `_kill_show(json 原樣)`」
file: `scripts/lumos:13056`
1. 「原文 <old 前 30 字>」:物件缺 old、old 是數字或 null 時沒說印什麼。直接寫 `r["old"][:30]` 會 KeyError 或 TypeError,而 S2 明寫「格式壞的配方也應列出」。同理 file、test、platform 缺或型別錯(`_kill_show` 吃 str(s),缺欄位 None 會印成 "None",是否可接受沒講)。
2. 「各欄經 _kill_show(會帶引號)」是否包含第一欄短身分沒說。若短身分也被 `_kill_show` 就變成 `"ab12…"` 帶引號,「可直接拿去 --id」會被貼進引號(shell 會吃掉,但算不算「可複製」測試要怎麼斷言?)。要寫明:短身分欄原樣印、不經 _kill_show。
3. 非物件元素「整個印 _kill_show(json 原樣)」沒有長度上限,可能一整行極長(其他欄位都截 30 字),要不要截斷沒說。
4. 「前 30 字」是先截再 _kill_show 還是先 show 再截,影響會不會把跳脫序列(‮ 這種 6 字元)截斷在一半;S2 的「不應原樣印出控制字元」測試要看這點。

## F4 S1 的斷言不能照字面寫在整個標準輸出上
severity: minor
blocking: 否
引句:「印出的 kill-add 範本的 `--new` 應是待填字樣、不應出現舊配方的壞法原文;完整內容那一行仍應印出舊壞法」
file: `scripts/test_lumos.py:60544`
1. 既有 `t_guard_kill_rm` 的配方 new 是 `XX_BROKEN = 1`,而同一次輸出的「完整內容」那一行也含它。接手人若寫 `"XX_BROKEN" not in r.stdout` 必紅(寫反)。
2. 必須只對範本那一行(以「照現在的程式改寫後重新宣告:」切)斷言不含,並另斷言範本含 `--new '<照新原文改寫的壞法>'`。spec 沒講怎麼切,建議在 S1 括號補一句。
3. 翻紅驗證:還原成 `val("new", …)` 時這條要紅,spec 的寫法可以達到,但前提是 1、2 做對。

## F5 結果行加 id 要動 8 個建結果的地方,spec 只說「照 `_logged` 的做法」
severity: minor
blocking: 否
引句:「所以在組結果時用原配方算 `_kill_recipe_id`,存成底線開頭的旁路欄」
file: `scripts/lumos:13798`
1. `cmd_guard_kill` 有 8 處 `results.append({**r, …})`(13798、13836、13845、13855、13861、13868、13873、13883)加上 13896 的 `res = {**r, …}`,共 9 處;`_logged` 是在迴圈後單處加的,不是這種散落寫法。漏一處(例如平台不在 config 那條 error)就缺 id,人讀行會 KeyError 或少欄。
2. 建議 spec 指定做法:迴圈前一次建 `rid_of = {id(r): _kill_recipe_id(str(rel), r)}`,蓋章迴圈(13915 起)用結果裡保留的來源參照,或寫成一個小函式 `_with_rid(r, …)`;並加測試覆蓋每種 verdict(至少 drifted、error 圍欄、abort)都有 id。
3. 〈實務隱患〉說「『worktree 無殘留』那支要求人讀輸出維持單行」,實際該斷言(test_lumos.py:20504)讀的是 `git worktree list` 輸出,不是 guard kill 的人讀行;維持單行的真正守衛是 `t_guard_kill` 裡一堆 `r.stdout` 子字串比對。引錯測試會讓接手人以為有單行守衛。

## F6 列出模式的小缺口與回頭條件不可機械執行
severity: minor
blocking: 否
引句:「最後印一句「移除:lumos guard kill-rm <節點> --id <短身分>」。」
file: `scripts/lumos:41675`
1. `<節點>` 是字面佔位還是實際節點(`_kill_node_arg(rel)`)沒說;rtb 要的是能直接複製,應寫實際節點、`<短身分>` 才是佔位。
2. 「沒帶 `--id`」:`--id ''` 現況擋下 rc 2(格式不符)。實作者用 `if not args.gkr_id` 會把 `--id ''` 悄悄當成列出;要寫明用 `is None` 判斷、空字串仍擋。
3. 12 字元前綴在同一篇內撞到時,列出的兩行看起來一樣但 `--id` 會被擋(既有行為會列候選完整身分)。列出模式要不要偵測並提示,沒說。
4. RETIRE-IF「連續兩次 rtb 回報都沒人用到就撤掉」、REVISIT「看 rtb 回報有沒有人用到」:沒有機械來源(沒說從哪個 log 看 kill-rm 無 --id 的次數),純靠人記得;依鐵則 4 應指到入口(例如 docs/.usage-log.jsonl 若有記指令)或改成人工巡檢並寫明誰、問誰。

最高等級:major;blocking 共 3 條
