severity: blocker

severity: blocker
blocking: 是
CJK/非 ASCII 檔名未關閉 git 引號跳脫,`_git_status_entries` 呼叫 `git status --porcelain -uall` 時沒帶 `-c core.quotePath=false`(scripts/lumos 裡 `_pitfall_diff_collect` 已明文記過同一條「CJK 檔名不轉義加引號」的教訓,這裡沒抄到)。實測:在乾淨 repo 建立 `scripts/中文檔案.py` 並跑 hook,收工訊息印出的是 `scripts/\344\270\255\346\226\207\346\252\224\346\241\210.py`(git 的八進位跳脫字面文字,不是真檔名),且因為這串跟逐字稿裡的真路徑對不上,`decision:block` 的 reason 直接退化成「這一輪動到的檔算不出來,所以不列檔名」。指令:`printf 'x=1' > scripts/中文檔案.py && git status --porcelain -uall` 回 `?? "scripts/\344\270\255\346\226\207\346\252\224\346\241\210.py"`,再跑 hook 得到上述亂碼輸出(完整重現腳本見審查過程,本檔案 repo 本身滿是中文檔名,這條會天天發生)。
引句:「r = subprocess.run(["git", "-C", str(project_root), "status", "--porcelain", "-uall"],」

severity: major
blocking: 是
`_entry_is_code` 對已刪除檔案的路徑排除判斷完全失效,因為它在 relpath(git 相對路徑,如 `dist/bundle.js`)上比對 `EXCLUDE_PATH_CONTAINS` 的 `/dist/`、`/build/`、`/node_modules/`、`/docs/` 等前後都帶斜線的樣式,永遠對不上頂層目錄;未刪除檔案是靠 `is_code_file(str(project_root / relpath), …)` 重建成絕對路徑才對得上,兩條路徑不對稱。實測:建 repo、提交一支 `dist/bundle.js`,`rm dist/bundle.js` 後跑 hook,印出「工作樹上有 1 個程式碼檔還沒提交…dist/bundle.js(已刪除)」——同一支檔案存在時新增不會被列(驗證排除規則本身沒壞),刪除後卻被誤判成程式碼檔,擋停名額也可能因此被無謂用掉。
引句:「norm = relpath.replace("\\", "/")」

severity: minor
blocking: 否
STOP_BLOCK reason 的 `model_rel or rel[:0]` 是死碼:外層已經用 `if model_rel else …` 判過真假,只有 `model_rel` 為真時才會進入這個分支,`rel[:0]`(恆空列表)永遠不可能被取用,純屬可讀性瑕疵,不影響任何實際輸出。⚠ 未附翻紅重現,僅靜態讀碼判斷。
引句:「reason = stop_block_reason(model_rel or rel[:0], graph_rel, mentions) if model_rel else」

以下為已實測但判定為「未能重現/行為正常」,供編排者對照,不計入 blocking:
- 空倉庫(未提交)、index.lock 存在、同檔已暫存+未暫存改動(`MM`)、`git mv` 改名+修改(`RM … -> …`)、純空白檔名(`"hello world.txt"` 會被引號包住但 `.strip('"')` 正確還原)——逐一實測皆正常運作,未發現額外缺陷。

總結:最嚴重等級 blocker,blocking 共 2 條(CJK 檔名跳脫失真為 blocker、刪除檔誤判排除目錄為 major)。
