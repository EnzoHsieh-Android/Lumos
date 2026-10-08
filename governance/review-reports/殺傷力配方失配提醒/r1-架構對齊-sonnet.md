severity: major

## F1 判斷函式的檔案路徑基準跟 guard kill 實際用的不是同一個
severity: major
blocking: 是
引句:「`os.path.realpath(平台根/file)` 不在平台根的 realpath 底下 → `outside`(不讀檔)。這跟 `cmd_guard_kill` 的圍欄同一種判法」
file: `scripts/lumos:13214`
1. `cmd_guard_kill` 的 `proot = Path(pentry["root"])` 只拿來跑 `git -C proot worktree add`;git 的 worktree 是整個 repo 的檢出,根是 git 頂層,不是 proot。之後 `target = os.path.realpath(os.path.join(wt, r.get("file")))` 的圍欄與讀檔都以 wt(git 頂層)為基準(`scripts/lumos:13271` 一帶)。所以 guard kill 的 `file` 是「相對 git 頂層」。
2. spec 的新函式改以「平台根」為基準。平台根是 `load_platforms` 的 `(repo_root/root_str).resolve()`(`scripts/lumos:4545`),可以是 repo 的子目錄(例如 `root: "android"`)。這種設定下同一條配方 `file` 在兩邊解析到不同檔:guard kill 找得到、doctor/kill-add 報 missing 或 outside(假警報),或反過來該報失配卻讀到別的同名檔(漏報)。
3. 這正是「同一件事引入第二套做法」:spec 的 PRIOR-ART 與 S5 都宣稱「同一種圍欄」,但錨點不同,spec 自己的前置掃描(④1「驗專案根改驗平台根」)只對 kill-add 的舊假設做了修正,沒有對照 guard kill 實際的錨。平台根剛好等於 git 頂層的設定(本 repo、legacy 單平台)才一致。
4. 修法方向:二選一寫進 spec——(a) 錨改成「平台根所在 git 頂層」(`git -C proot rev-parse --show-toplevel`,與 worktree 內容一致),並在 S5 加子目錄平台根的測試案例;(b) 明寫這是刻意的第二種語意並把「平台根為子目錄時兩邊可能不同」放進〈誠實界線〉。

## F2 doctor 新段取專案根的來源沒定,既有就有兩套
severity: minor
blocking: 否
引句:「專案根照 `_repo_root_from_env`,跟 guard kill 同一套」
file: `scripts/lumos:1583`
1. doctor 內 P 段用的 `repo_root` 是 Check C 起手從 vault 往上找名為 `docs` 的資料夾,找不到是 `None`,P 段遇 None 印「沒有 docs/ 資料夾,跳過」;doctor 其他段也大量用 `_vault_repo_root(env)`(往上找 `.git`,`scripts/lumos:8099`,全檔 38 處)。`_repo_root_from_env` 只有 8 處,doctor 內不用它。
2. spec 要 P2「放在 P 段之後」又「照 P 段的形狀」,卻指定 `_repo_root_from_env`。實作者可能(a)沿用 doctor 區域變數 `repo_root`,在無 docs 的專案出現 None 後 `load_platforms(None)` 例外(雖有整段例外保護,但被吞成「算不出來」而非明確跳過),(b)用 `_repo_root_from_env`,與 P 段在無 docs/ 專案行為不同。
3. 建議 spec 明寫 doctor 段用哪一個,以及 repo_root 為 None 時比照 P 段印跳過句。

## F3 「不抽共用、自己寫一份」站得住,但缺防止兩份判準日後分家的機制
severity: minor
blocking: 否
引句:「不改 guard kill 本身(它的圍欄、錯誤說明與回傳碼有既有合約與測試,抽共用會改到它的行為,前置掃描逐項證實)」
file: `scripts/lumos:12864`
1. 取捨本身成立:guard kill 的讀檔在隔離工作樹內、帶 `drifted` 專屬說明與 `OSError` 才降級,硬抽會動到既有合約;而且 `_kill_read_recipes` 這個讀配方的入口新函式有沿用,沒有第二套解析。
2. 但專案對同類情形有明確慣例:`_kill_recipe_key` 的說明寫「三處都用這一支(別各寫一份比對)」,也有「刻意複製、不共用」時在註解互相點名的做法(`scripts/lumos:34119`)。spec 新增的是同一個「原文恰好一次」條件的第二份實作,卻沒要求兩邊互相標註,也沒有一條測試用同一組輸入同時驗兩邊結論一致(S6 只驗 guard kill 沒變)。日後 guard kill 改讀法(例如換成二進位或改次數條件),doctor 會默默說對得上、guard kill 卻判 drifted。
3. 建議:實作時在新函式與 `cmd_guard_kill` 該段互相加註解指名,並加一條對照測試(同一批配方,新函式 `ok` 與 guard kill 的非 drifted 一致)。
4. 其餘對齊面已讀,無 finding:P2 的跳過條件與 P 段逐字相同;`warn_soft` 的上限與 `--ci`=verbose 行為(`scripts/lumos:1349`)與 spec 描述一致;「這一段算不出來,先跳過」措辭與既有 `warn_soft([], "這一段算不出來(…),先跳過")` 同形;kill-add 提醒走標準錯誤的 `⚠` 前綴與檔內既有 stderr 提醒同路,成功訊息仍在標準輸出,管道沒有新增第二種;kill-add 其他訊息用「擋下:」而本案用「⚠ 提醒:」,語意不同(不擋)用詞合理。

最高等級:major;blocking 共 1 條
