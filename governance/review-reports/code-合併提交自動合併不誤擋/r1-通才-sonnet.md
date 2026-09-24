severity: blocker

## F1 八爪魚合併(3 個以上上一版)時,remerge-diff 靜默回報「這個提交沒改任何東西」,原本該擋的寫回違規變成放行

severity: blocker
blocking: yes

`_nodehome_merge_own_changes` 判斷要不要用 remerge-diff 的方式,是看 `_nodehome_git` 有沒有回 `None`(git 指令跑失敗才退回舊判法):

引句:「r = _nodehome_git(repo_root, "show", "--remerge-diff", "--no-ext-diff", "--no-textconv", "--format=",」

但 `git show --remerge-diff` 遇到八爪魚合併(3 個以上 parent)時,行為是:印一行警告、**照樣以 exit code 0 收尾**,而且這行警告是印在 **stdout**(不是 stderr)。我在 `/tmp` 用真的 git(2.39.2)實測:

```
$ git show --remerge-diff --no-ext-diff --no-textconv --format= --name-status -z -M <八爪魚合併sha>
diff: warning: Skipping remerge-diff for octopus merges.
$ echo $?
0
```

`_nodehome_git` 只在 `r.returncode != 0` 時才回 `None`;這裡 rc=0,所以它把這串警告文字原封不動當成「git show 的合法輸出」回傳給 `_nodehome_name_status`。`_nodehome_name_status` 用 `\0` 切 token,這段警告文字裡沒有 `\0`,整段變成一個 token、開頭字元是 `d`(不是任何一種狀態碼),於是三個回傳值(改到的路徑、改名對照、刪除的路徑)全部是空集合——**跟「這個合併提交自己什麼都沒改」是同一個結果,而且不會觸發退回舊判法的 `None` 分支**。

實測影響(用 `lumos home check --diff`,不是我自己編的推論):
- 建一個 4-parent(3 條分支)的八爪魚合併,合併本身乾淨自動完成;之後 `git commit --amend` 在合併提交裡順手多做一件事——改一支沒有家的舊檔 `ui/Screen.vue`,同時把節點 A 的正文改成用散文(不加反引號)提到 `ui/Screen.vue`。這在**真的 2-parent 合併**做同樣的事,`lumos home check --diff` 會擋(`EXIT=1`,列出「這次寫了說明的節點,不是任何一支改動檔的家」)。
- 換成 4-parent 八爪魚合併,一模一樣的違規,`lumos home check --diff` 變成 `EXIT=0`,只印一句不擋的提醒(「這次改到 1 支還沒有家的舊檔……只提醒」)。

也就是說:這批改動聲稱的目標「① remerge-diff 對真違規要跟舊判法一樣擋」在 3 個以上 parent 的合併提交上是不成立的——不是變寬鬆一點,是**整個合併提交自己多改的部分,S13(節點寫進不是家的節點)跟 S13b(有寫回的提交裡每支改動檔都要有家)兩道檢查全部失效**,因為它們都是照 `groups[i]["paths"]` 這個空集合去比對。這正是派工單「特別攻擊②」點名的情境(八爪魚合併),也正是這批修法自己要解決的問題(合併提交誤放行/誤擋)在另一個方向上重新出現。

補充:這不是我掰出來的邊角案例——`_nodehome_commit_groups` 原本(修法前)就是逐一對每個 parent 做 `diff-tree` 再取交集,那段迴圈本來就沒有限定只能 2 個 parent,代表這支程式本來就承認、也處理過 3 個以上 parent 的合併;新判法用 remerge-diff 取代之後,反而在這個本來就有考慮到的情境上失效了,而且沒有任何新測試涵蓋(patch 唯一新增的測試 `t_nodehome_merge_auto_combined_not_blocked` 只建了 2-parent 的合併)。

引句:「if drv is None or drv.returncode != 1:     # 0=有自訂驅動器;其他=判不了。兩種都不冒險」

這行本身邏輯沒錯(驗證過:找不到自訂驅動器時 `git config --get-regexp` 回 exit 1,找到時回 0),不是這條發現的成因;成因在於 `_nodehome_merge_own_changes` 沒有另外檢查 git 的 stdout 是不是真的「像 name-status 輸出」,只信任 exit code。

修法方向(僅供參考,不代寫):remerge-diff 拿到 rc=0 之後,先確認輸出真的能被 `_nodehome_name_status` 正確解析(例如檢查前幾個位元組不是 `diff: warning:`,或者乾脆判斷 parent 數 > 2 就直接不用 remerge-diff、走舊判法),或是改用 `capture_output` 分開讀 stdout/stderr 並檢查 stderr 是否非空來偵測這種「rc=0 但其實被跳過」的情況。

## 已驗過、沒問題的路徑

在 `/tmp` 自建的臨時 repo(真的 git 2.39.2)裡實測以下情境,都跟作者的說法一致:

- **①真違規對照組(2-parent)**:兩條分支各改同一篇筆記的不同段、同一支程式的不同行,合併自動完成,remerge-diff 輸出空、`lumos home check --diff` 放行(rc0)——跟 patch 自帶的新測試 `t_nodehome_merge_auto_combined_not_blocked` 一致,我另外用 `python3 scripts/test_lumos.py -k t_nodehome_merge_auto_combined_not_blocked` 在正式 repo 跑過,5 個 check 全過。
- **①真違規會擋(2-parent)**:合併時手動解衝突、順手多改不相干檔案,`git show --remerge-diff ... --name-status -z` 正確列出手動改到的檔(含新增檔案 `A d.py`);`modify/delete conflict`(一邊刪、一邊改,以刪為結論)也正確輸出 `D f.py`,能被 `_nodehome_name_status` 解析成刪除。
- **③改名偵測(-M,2-parent)**:一邊改名、一邊改內容,git 自動合併乾淨完成(git 自己的改名偵測接手),remerge-diff 輸出為空(跟自動合併結果一致、沒有「自己多改」的部分)——格式驗證另外用手動衝突的例子確認過:remerge-diff 的 `R`/`M`/`D`/`A` 這幾種狀態碼、`-z` 分隔、`-M` 觸發的 `Rxxx <舊路徑> <新路徑>` token 順序,跟 `_nodehome_name_status` 期望的格式(`diff-tree --name-status -z -M` 的輸出)一致,能正確解析。
- **④自訂合併驅動器判斷**:`git config --get-regexp '^merge\..*\.driver$'` 在真的沒有註冊驅動器時回 exit 1(→ 用 remerge-diff)、我沒有另外注入全域 `~/.gitconfig` 驅動器去測「全域驅動器也會被抓到」這件事,但邏輯上 `git config`(不加 `--local`)本來就會併讀 system/global/local,所以這裡偏保守(全域有裝一個不相干的驅動器也會讓全部合併提交退回舊判法)不是安全方向的漏洞,只是精確度打折,不算違規放行,沒有另開一條發現。
- patch 自帶的測試 `t_nodehome_merge_auto_combined_not_blocked` 裡「③有自訂合併驅動器時,那個驅動器的指令完全沒被執行」我讀過測試邏輯,跟我自己在 `/tmp` 驗過的 `--get-regexp` 行為互相印證,沒有另外重跑(派工單只要求唯讀,這段不涉及會寫入本體 repo 的動作,用讀 patch + 單獨跑該測試已足夠佐證)。
