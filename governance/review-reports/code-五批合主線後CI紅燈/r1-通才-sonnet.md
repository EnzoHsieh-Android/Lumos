severity: minor

我只讀了 patch 和 repo 現況(`fix-ci-batches` 的 24c703b57),沒有跑測試。blocker 和 major 都找不到講得出具體失敗輸入的,只有下面兩條 minor。

**① 行為等價:沒有問題**
- `_under_root(root, p)` 就是 `Path(p)`,再加上「相對路徑接 root、絕對路徑照用」,跟被取代的兩段寫法一樣。
- 空字串兩邊都得到 `root/.`,也就是 repo 根。
- `root` 為 None 時行為有差:原本 `Path(None)` 會丟 TypeError,現在回相對路徑。這兩個呼叫端都擋不到這個差異。
  - `_android_plugin_missing` 唯一的呼叫端 `_lint_android_ci_advisories`(`scripts/lumos:40568`)前面已經先擋掉 `repo_root is None`。
  - `_lint_wt_unready` 在這之前已經用 `repo_root` 跑過 git,沒有 None 的路。
- bytes 輸入:第二處先用 `os.fsdecode` 轉成字串才傳進去,第一處本來就是字串,沒有新差異。

**② 呼叫端:沒有問題**
- 兩處的後續處理(`is_file()`、`exists()`)都沒動。
- `_under_root` 不做 resolve,原本也沒有 resolve。

**③ 守衛放寬:有一點鬆,但可接受**
- `t_lint_files_substitution_has_one_implementation` 的允許名單加了 `_lint_placeholder_words`。名單是兩邊對等檢查:名單裡的函式必須還在碰佔位符,名單外的碰到就紅。
- `_lint_placeholder_words` 真的有碰佔位符(`scripts/lumos:42491` 起),`ALLOWED <= set(touchers)` 成立,所以不是死項。
- 它只回傳「佔位符→詞」的對照,不做字串替換。名單旁邊的註解也這樣寫,所以放寬是有理由的。

**⑥ 拆測試:前置現場都成立**
- 拆出來的三支都自己呼叫 `_fp_repo()`,`tip`、`zero`、`d`、`g` 都在各自函式內定義。
- `⑥` 的 wrapper 裡 `d, g = _fp_repo(lumos_wrapper=wrap)`、`feat` 分支、`notes.md` 提交、`tip` 都在函式裡重建,`⑦` 沿用同一個現場。
- ①到⑦的斷言一條都沒漏。

severity: minor
blocking: 否
引句:「推分支的新分支首推(遠端舊值全零)改用 lumos push-range 算的起點:主線上的舊高風險寫法不算這次的;」
這是 `t_prepush_new_branch_block_range` 的 docstring,拆完沒改。它還寫著「S1 到 S6」和翻紅釘「①③④紅、⑥紅、⑦紅」,但函式現在只剩 ①②。③到⑦已搬走。之後有人只看這支的 docstring,會誤以為它還守 S3 到 S6。
file: `scripts/test_lumos.py:30096-30098`

severity: minor
blocking: 否
引句:「[S3] 當新分支先合過主線(主線在分岔後又多了會被當成告警的提交)再首推時,推送前掛鉤 應 只算分支自己的提交、放行 [test:t_prepush_newbranch_merged_tip]」
- 這條計劃條款綁定本身是對的。
- 但 `governance/test-durations.json` 只有舊名 `t_prepush_new_branch_block_range`(約 101 秒,見 1451 行),三支新名字沒有紀錄。這個檔看起來是分片排程用的耗時表,新測試會被當成「沒有耗時資料」。分片排程怎麼處理沒有紀錄的測試,我沒追到。
- 舊名的 101 秒也不再對應拆分後的實際耗時。這會讓切片排程變得不準,不會讓測試紅,所以只列 minor。
file: `governance/test-durations.json:1451`

⑦(文件同步)的另一個觀察:`存量漂移守衛.md` 的 `[test:…]` 補了三個新名字,計劃的 S3 到 S6 也改綁新名字,兩邊對得上。S1、S2 仍綁舊名,而舊名裡確實還有 ①②,所以沒問題。

⑧(命名與重複):三支拆出來的測試函式名一致(`t_prepush_newbranch_*`),跟舊名 `t_prepush_new_branch_block_range` 的寫法(`new_branch` 加底線)不同,是小的命名不一致,不列為 finding。

總結:這個 diff 沒有講得出具體失敗輸入的 bug,只有一條過期 docstring 和一條測試耗時表沒更新,兩條都是 minor、不擋。
