severity: major

## F1 新測試沒帶同檔全部同類測試都有的 `print(函式名)` 開場行
severity: major
blocking: no

`scripts/test_lumos.py` 裡所有既有的 `t_nodehome_*` 測試(機械核對:52 支裡 51 支)都在 docstring 結束後、第一行動作前先印自己的函式名,例如同一批緊鄰的 `t_nodehome_diff_route_per_commit`(patch 內文未附這行,但檔案裡是 `print("t_nodehome_diff_route_per_commit")`)。新加的 `t_nodehome_merge_auto_combined_not_blocked` 直接跳過 docstring 進 `root = _nh_repo()`,沒有這行:

引句:「+def t_nodehome_merge_auto_combined_not_blocked():」
引句:「+    root = _nh_repo()」

兩行在 patch 裡緊鄰(docstring 結束後直接接 `root = _nh_repo()`),中間沒有其餘既有測試都有的 `print(...)` 那行。不影響測試判定結果,純粹是同檔既有寫法的一致性缺口——它讓這支測試在跑測試時少印一行自己的名字,跟鄰居的輸出習慣不一致。

file: `scripts/test_lumos.py:42782`(新函式定義處,機械核對用 grep 逐一比對 52 支 `t_nodehome_*` 是否含 `print("<函式名>")`,只有這一支缺)

## F2 `_nodehome_commit_groups` 的 docstring 沒跟著這次改法更新,還在講舊判法
severity: major
blocking: no

`_nodehome_commit_groups` 的 docstring 這次完全沒被這份 diff 動到(patch 裡那五行是純 context,沒有 `+`/`-`),但函式本體的合併分支邏輯已經整個換掉:現在先試 `_nodehome_merge_own_changes`(remerge-diff),只有拿不到才退回「跟每一個上一版都不一樣的路徑」。docstring 卻仍然這樣寫,把舊判法講成唯一/預設的算法:

引句:「只算它自己多改的——跟每一個上一版都不一樣的路徑;照搬某一邊進來的,那一邊的提交已經各自查過。」

這句話現在只描述「退路」分支,精確判法(remerge-diff)完全沒被提到。跟本次改動在筆記(`每支檔有家.md`)裡把新判法講得很清楚的程度不成比例——同一支函式的自我說明反而沒跟上自己的實作,對照這個專案一貫要求「改行為要同時寫回脈絡」的紀律,這裡漏了函式自己的 docstring 這一層,容易讓下一個改這支函式的人以為「跟每一個上一版都不一樣」還是常態路徑而不是退路,進而在改動時不小心把精確路徑跟退路的優先順序弄反。

file: `scripts/lumos:21913`(`_nodehome_commit_groups` docstring)、`scripts/lumos:21945`(退路分支實際生效處,含新加的 `# 退路(...)` 註解)

## 已驗過、沒問題

- 新函式 `_nodehome_merge_own_changes` 的命名(`_nodehome_` 前綴)、參數順序 `(repo_root, sha)`、放置位置(緊鄰在它唯一呼叫者 `_nodehome_commit_groups` 之前)都跟同檔其他 `_nodehome_*` 輔助函式(`_nodehome_git`、`_nodehome_name_status` 等,`scripts/lumos:21619`–`21892`)的排法一致。
- 呼叫 git 的方式:用 `_lens_git`(帶 `binary=True` 讀設定)與 `_nodehome_git`(包 `_lens_git` 再檢查 `returncode==0`)兩層既有共用函式,沒有另開一套 subprocess 呼叫;`_nodehome_git` 定義見 `scripts/lumos:21619`。`--no-ext-diff --no-textconv` 這組防外部驅動器旗標,同檔已有至少 6 處既有用法(如 `scripts/lumos:23345`、`scripts/lumos:26719`),新加的 `git show --remerge-diff` 呼叫沿用同一組旗標,寫法一致。
- 先查 `merge.*.driver` 設定再決定要不要跑 `--remerge-diff` 這個「查完再決定」的安全模式,雖然檔案裡沒有逐字重複的前例,但跟同檔對差異驅動器的防範原理(`scripts/test_lumos.py:46293` 一支釘全域性質的測試,docstring 自陳「性質不是行號」)同一類——查的是「會不會跑到攻擊者能命名的指令」,不是列舉哪個鍵名,判法本身沒有跟既有原則衝突。
- 退回舊判法(fallback)那段程式碼結構跟改動前一模一樣(`per = [...]`、`set.intersection` 三行),只是縮排進 `else:` 分支,邏輯本身沒被動過,也還保留原本對 octopus merge(3 個以上 parent)取交集的處理。
- 新測試 `t_nodehome_merge_auto_combined_not_blocked` 用的輔助函式(`_nh_repo`、`_nh_file`、`_nh_node`、`_nh_commit`、`_nh_git`、`_nh_check`)跟緊鄰的 `t_nodehome_diff_route_per_commit`、`t_nodehome_diff_route_counts_content_per_commit` 完全同一組,呼叫慣例(先建兩篇筆記與程式檔、`_nh_commit` 建提交、`_nh_check(root, "--diff", f"{base}..HEAD")` 取 rc/out)一致;`翻紅釘:` 這行也照同檔 275 處既有寫法的格式寫。
- `git config --get-regexp` 的回傳碼判讀(`0`=有 match、`1`=無 match、其他=錯誤)符合 git 本身行為,不是這個專案自創的慣例,寫法上跟檔案裡其他「先跑一個 git 指令、再用回傳碼分支」的模式(如 `_lens_full_sha` 在 `scripts/lumos:26565` 判 `returncode != 0`)同一種形狀。
