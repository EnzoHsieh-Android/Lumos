severity: major

## F1 符號連結迴圈判 outside,但 guard kill 實際判 drifted
severity: major
blocking: 是
引句:「跟隨連結超過 40 次 → `outside`(迴圈)」
file: `scripts/lumos:13264`
1. guard kill 用 `os.path.realpath`(非 strict)取目標;遇到連結迴圈它不丟錯,回傳停在迴圈上的路徑,仍在工作樹內,所以圍欄通過。接著 `open` 丟 `OSError`(ELOOP),被 `except OSError` 接住,判 drifted,說明是「file 開不了」(scripts/lumos:13264-13271 一帶)。我在臨時目錄造 a->b、b->a 實測:realpath 結果以根開頭、open 丟 Errno 62。
2. spec 把迴圈歸 outside,kill-add 提醒字面是「guard kill 會擋在圍欄外(判 error)」。照做的話,迴圈連結的配方會被印上錯的狀態與說明,跟 S5「outside ↔ error」的對應衝突。S5 的題目清單沒有迴圈這一格,對照測試抓不到。
3. 折法:迴圈改歸 `missing`(細節寫「連結迴圈」),並在 S5 與對照測試補一格迴圈連結,斷言 ↔ drifted。這正是「第二套解析器」要靠對照測試守的地方。

## F2 解析結果等於 repo 頂本身,guard kill 判 outside,spec 歸 missing
severity: minor
blocking: 否
引句:「不是一般檔(目錄、具名管線、裝置檔)→ `missing`,細節寫「不是一般檔」」
file: `scripts/lumos:13261`
1. guard kill 的圍欄是 `target.startswith(wt_real + os.sep)`:`file` 為空字串、`.`、或解析後正好落在根的路徑,realpath 等於工作樹根本身,不以「根加分隔字元」開頭,判 error(逃逸)。spec 的小解析器走完還在根內,再因為是目錄歸 `missing`。
2. `file` 是字串但為空或 `.` 的配方(型別檢查擋不掉)會得到 missing/「不是一般檔」,guard kill 實際是 error。兩邊都非 ok,只有分類與說明不同,所以只是 minor。折法:解析結果等於根時歸 outside。

## 其餘節
- 與既有做法對齊:`_repo_path_unsafe` 是「寫入前逐層禁連結」的語意,跟本案要模擬的「guard kill 工作樹內 realpath 前綴」語意不同,不能直接重用;自寫解析器加對照測試釘住兩邊,站得住,不算引入第二種做法(PRIOR-ART 一句「同一種圍欄 realpath 前綴判法」與 §1 的手寫解析器字面不一致,屬措辭 minor,放行)。
- 身分共用函式:`_kill_recipe_key`(scripts/lumos:12870)三處呼叫點都傳 `str(rel)`,spec 的節點字串寫法一致;格式壞的另走雜湊,不衝突。
- 接走 stderr:專案已有 `contextlib.redirect_stderr` 先例(scripts/lumos:11558 一帶),`load_platforms(cfg=)` 的 `cfg` 參數也確實存在且不讀磁碟;已讀,無 finding。
- 其他節已讀,無 finding。

最高等級:major;blocking 共 1 條
