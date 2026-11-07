severity: major

第一輪資源席三條的狀況如下。
- F1(健檢批次 git log):已改成整 repo 一次加程序內快取。新問題見下面 F2。
- F2(逐份計劃花 git):新舊判斷已改成吃預取的快取。但出處判定這輪改成每個路徑出處都開 git,見下面 F1。
- F3(擋下不去重):已用指紋去重。我量讀整份 21.7MB 帳(124557 行)掃一次約 0.08 秒,可接受。`pp_record_block` 的另記一筆這輪沒動,我不另標。

**F1:路徑出處改走版控樹後,每個路徑引用要開 2 到 3 個 git 子程序,合格的計劃也照付**
引句:「if _validate_repo_ref(Path(rr), path, line, at_sha="HEAD")[0] != "ok":」
- 這輪的出處判定,每個反引號路徑都要開 `cat-file -e`(`_git_tree_has`)和 `ls-tree`。帶行號的再加一次 `git show`,符號連結再加一次 `git show`。上一輪只用 `Path.exists()` 和 `is_file()`,不開 git。
- 我在 clone 上實跑 `_plan_sources_problems`,對象是本案計劃(約 37 列、42 個反引號)。結果 0.81 秒、34 次 `subprocess.run`。上一輪同一支是毫秒級。
- 這個 0.81 秒就是作者說的「健檢那段 0.18 到 0.81 秒」。目前 repo 裡只有 1 份計劃有〈依據來源〉節,所以看起來快。
- 作者量的「408 份計劃推送前那圈 1.1 秒」,絕大多數是沒有這一節的計劃,根本沒進到出處判定。這個數字不代表之後的狀況。
- 健檢 S22 對每份 todo/doing 的新計劃都跑一次 `_plan_sources_problems`,不管合不合格。規格閘生效日 2026-11-08 之後,新計劃都會有這一節。
- 以每份約 0.8 秒推算,20 份 todo/doing 計劃的健檢約 16 秒,一次推送改到 20 份計劃約 16 秒。
- 這支函式沒有把 HEAD 樹的檔案清單快取起來。一次 `git ls-tree -r -z HEAD`(或 `cat-file --batch-check`)加按 HEAD 快取就能把次數壓成常數,效果跟 first-days 那份快取一樣。
- `_disp_git_timeout()`(預設 8 秒)逾時會被 `except (OSError, subprocess.TimeoutExpired)` 吞成 False。git 變慢時,合法出處會被判成不合格,擋下訊息看不出是逾時。
- file: `scripts/lumos:71398`、`scripts/lumos:71413`
severity: major
blocking: 是

**F2:整 repo 不限路徑的 `git log -M` 在大歷史下,單篇規格閘也要付全史成本,逾時沒有降級**
引句:「r = subprocess.run(["git", "-C", root, "-c", "core.quotePath=false", "log", "--reverse", "-M", "--diff-filter=AR",」
- 我造了 10 萬提交、每提交加 3 檔、每 10 個提交改名一檔的 repo(約 31 萬路徑)。實測數字如下:

  | 項目 | 數字 |
  |---|---|
  | `_plan_first_days` 首次 | 10.5 秒 |
  | `git log` 輸出 | 10.3MB |
  | `git log` 峰值常駐記憶體 | 約 484MB(`--reverse` 要把整段歷史收齊) |
  | Python 端新增 | 約 115MB(31 萬筆字典,含所有曾經存在的路徑) |
  | 快取命中 | 18 毫秒(其實是那次 `rev-parse` 子程序) |

- 本 repo(3302 提交)只要 0.21 秒、63MB,沒問題。
- 快取按 (repo 根, HEAD) 留 8 份。真實使用只有一個 repo,實際上限約一份,不是問題。
- 退化點一:快取只活在程序內。規格閘單篇和每次 pre-push 都是新程序。只要計劃有出處問題,而且 `created` 缺或早於生效日,就付整史 10 秒以上。上一輪是單篇 3 次 git,約 0.2 秒。
- 退化點二:歷史再大就撞 `_PLAN_FIRST_DAYS_TIMEOUT`(60 秒)。撞到後每次推送白等 60 秒才退回只看 `created`。快取存的是 None,但程序一結束就沒了,下一個程序要再等一次。
- 建議是把結果落成帶 HEAD 的磁碟快取,或對單篇查詢保留一條單路徑退路。
- 我把它列 minor,因為要到 10 萬提交量級才超過預算;本 repo 現況不受影響。
- file: `scripts/lumos:14255`
severity: minor
blocking: 否

總結:最嚴重是 major(F1:出處判定每個路徑引用開 2 到 3 次 git,單份計劃 0.8 秒、隨 todo/doing 計劃數線性放大),會擋 1 條
