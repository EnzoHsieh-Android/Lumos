severity: major

## F1 改名加衝突時,`old_path == path` 讓 fallback 失效,漏掉沒改名那一邊的內容,把「純挑舊內容」的解法誤判成新寫(誤擋)

`_nodehome_merge_wrote_new_lines` 用 `old_path = src.get(p, p)` 找上一版內容,但 `src` 只在**外層**(整個合併範圍的)remerge-diff 偵測到改名時才有值。實測發現:當一支檔在其中一邊分支被改名、另一邊分支只改內容(未改名),同時兩邊衝突,git 重做合併(自動合併樹)在解衝突**之前**就已經把檔案放在新名字下——外層 remerge-diff 的 pre-image/post-image 兩邊都是新路徑,偵測不到改名,`src` 對這支檔是空的,於是 `old_path == path`。這時 `if blob is None and old_path != path:` 這行 fallback 的條件恆假,永遠不會試著用新路徑去查沒改名那一邊的上一版——而沒改名那一邊的上一版本來就沒有新路徑這個檔(它還在舊路徑下),所以那一邊的內容整個從 `seen` 漏掉。

引句:「if blob is None and old_path != path:」

severity: major
blocking: yes

實際跑出來(在 /tmp/nh-test/repo3,不在 lumos-toolchain 裡):main 把 `src/a.py` 改名成 `src/a2.py` 並把第二行改成 `line2-MAIN`;feature 沒改名、把第二行改成 `line2-FEATURE`;兩邊合併對第二行衝突,解法只是把兩行都留下、順序調換(等同這批新增測試裡的 `swap` case,唯一差別是這次多了改名)。`line2-FEATURE` 在合併前就已經存在於 feature(在它的舊路徑 `src/a.py` 底下),不是新寫的一行。直接呼叫 `_nodehome_merge_wrote_new_lines(repo, sha, [p1,p2], "src/a2.py", "src/a2.py")` 回傳 `True`——被判成「合併自己寫了新行」,但其實一個字都沒有新寫,只是把已經存在的內容換了位置。用 `git show ${sha}^1:src/a2.py` 直接驗證,parent1(feature)在新路徑下確實讀不到那個檔(`fatal: path ... exists on disk, but not in ...^1`),證實漏查的正是這一邊。

file: `scripts/lumos:21936-21938`(對應本 diff 的 `if blob is None and old_path != path:` 那三行)

這會複製本 PITFALL 鏈本來要修掉的那種誤擋:同一份 diff 的 docstring 自己宣稱「★天花板★:...兩種都偏向少擋,不會多擋」——但這個改名場景剛好相反,是會多擋。改名同時衝突在真實 repo 裡不算罕見(搬檔案到新位置、另一邊剛好也在改那支檔),命中後這個合併提交的這支檔會被算進「合併自己改的」,如果同一個合併裡湊巧有另一篇筆記寫回,就會重演 rtb 那次「兩邊都沒新寫卻被擋」的誤擋,只是換了個觸發條件。

引句:「新寫的行剛好跟上一版別處某一行一字不差也會漏算——兩種都偏向少擋,不會多擋。」

修法方向:fallback 不該只在 `old_path != path` 時才試 `path`,兩個上一版各自應該用「這個上一版自己的改名對照」去找路徑,而不是共用一個從整體 remerge-diff 推出的單一 `old_path`——目前的寫法隱含假設兩邊改名狀態一致,改名只發生在一邊時就會踩到。

## F2 大合併裡逐檔多開 git 行程,規模隨衝突檔數線性成長,壓力測沒做

`_nodehome_merge_wrote_new_lines` 對 `_nodehome_merge_own_changes` 篩出的每一支檔都再跑一次 `git show --remerge-diff -- path`,還要對每個上一版各跑一次 `git show p:old_path`(兩個上一版 = 兩次),等於每支解過衝突的檔多開 3 個 git 子行程。這批新增測試都只測 1–2 支檔,凍結 patch 裡「逐檔多跑的 git 指令在大合併(幾百支檔)上的代價」這條攻擊面完全沒有實測數字佐證——不確定幾百支檔衝突時的合併提交會不會讓推送前掛鉤明顯變慢。

severity: minor
blocking: no

file: `scripts/lumos:21924-21940`

## 已驗過、沒問題

CRLF、行尾空白:`added`/`seen` 兩邊都用 bytes `.strip()`,Python 對 bytes 的預設 strip 字元集含 `\r`,所以帶 CRLF 的檔行尾 `\r` 會被兩邊一致去掉,不會因為換行風格不同而誤判成新行。

引句:「added = [ln[1:].strip() for ln in d.split(b\"\\n\") if ln.startswith(b\"+\") and not ln.startswith(b\"+++\")]」

二進位檔:`git show --remerge-diff` 對二進位差異印 `Binary files a/... and b/... differ`,程式直接抓 `b"\nBinary files "` 這個特徵字串當「判不了、當有寫」處理,方向是保守(照舊查/照舊擋),不是漏擋。

引句:「if b\"\\nBinary files \" in b\"\\n\" + d:」

只刪不加(挑一邊、刪掉一段)這條攻擊面:實測確認走的是 `if not added: return False` 這條路(`added` 真的是空的,不是漏抓),跟 docstring 自己標的天花板一致,不是意外行為,不重複回報。
