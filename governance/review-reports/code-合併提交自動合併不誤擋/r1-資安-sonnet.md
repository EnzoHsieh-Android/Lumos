severity: clean

## 審查範圍與方法
鏡頭:資安-合併-sonnet,站攻擊者那邊看「別人給的資料夾」情境——`.git/config`、`.gitattributes`、`.git/info/attributes` 皆視為攻擊者可寫。針對 patch 新增的 `_nodehome_merge_own_changes`(自訂合併驅動器守門 + `git show --remerge-diff`)做三件事的實測:① 守門擋不擋得住各種自訂合併驅動器的寫法;② remerge-diff 本身會不會觸發合併驅動器以外可執行的東西;③ 守門與執行之間有沒有時間差。

全部在 `/tmp/mgtest` 自己 `git init` 的臨時 repo 裡做(兩條分支各改 `b.py` 不同行、git 自動合併不衝突,模擬 patch 描述的現場),沒有動到 `/Users/enzo/harness/lumos-toolchain` 或 `/Users/enzo/rtb-mainwt`,也沒有跑 `lumos home check`/`canary record`/`code-loop pass`。

## 已驗過、沒問題:自訂合併驅動器守門(①)
守門指令是 `git config --get-regexp '^merge\..*\.driver$'`,只在確定 `returncode == 1`(完全沒匹配)才用精確判法,`drv is None` 或其他 returncode 一律回 `None` 退回舊判法(見 `scripts/lumos:21903-21906`,對應本 patch 引句「有就不用、退回舊判法。」)。實測以下寫法皆被抓到(`--get-regexp` 回 `rc=0`,守門正確擋下):
- 一般寫法 `merge.evil.driver`。
- 子區段名含點:`[merge "Evil.Sub"] driver = ...` → 鍵名為 `merge.Evil.Sub.driver`,regex 的 `.*` 照樣吃得到中間的點。
- 大小寫變化:`[Merge "case-test"] Driver = ...`——git 一律把 section 名與變數名正規化成小寫,子區段名大小寫保留,鍵名輸出仍是 `merge.case-test.driver`,守門吃得到。
- 透過 `[include] path = ...` 引入的外部設定檔(相對路徑要相對 `.git/` 目錄,不是 repo 根目錄——一開始試錯路徑時守門吃不到,修正相對路徑後即抓到,確認 `--get-regexp` 本來就會解出 include)。
- 透過 `[includeIf "gitdir:<path>/"] path = ...` 條件式引入。
- 子區段名含正則特殊字元(`merge.a+b(c).driver`)——因為 pattern 是丟給 git 自己的 regex 引擎比對鍵名字面,不是拿子區段名去組 pattern,不會被利用來繞過。
- 只放 `.gitattributes` / `.git/info/attributes` 宣告 `merge=<name>` 但**沒有**在 config 裡定義對應 `merge.<name>.driver`:git 退回內建三方合併,不會執行任何外部指令(本來就沒有可執行的東西可守)。
- git 內建指令(`config`、`show`)不能被 `[alias]` 覆蓋——即使設了 `alias.config`/`alias.show` 指向會 `touch` 標記檔的指令,兩次呼叫都不會被劫持(git 對 builtin 子指令的別名優先權低於 builtin 本身)。

## 已驗過、沒問題:remerge-diff 本身不會觸發合併驅動器以外可執行的東西(②)
在同一顆臨時 repo 上,對 `git show --remerge-diff --no-ext-diff --no-textconv --format= --name-status -z <merge-sha>`(即 patch 用的確切指令,見 `scripts/lumos:21906-21907`)逐一注入以下可執行點,全部沒有被觸發(以 `touch DRIVER_RAN` 當試爆點,實測後檔案都不存在):
- `diff.<name>.textconv` + `.gitattributes` 宣告 `diff=<name>`。
- `diff.<name>.command`(外部差異驅動器)+ 同上宣告——這兩項本來就有 `--no-ext-diff --no-textconv` 明擋,而且 `--name-status` 本身根本不印內容/hunk,連驅動器的呼叫點都摸不到,雙重安全。
- `filter.<name>.clean` / `filter.<name>.smudge` + `.gitattributes` 宣告 `filter=<name>`:remerge 是在記憶體裡拿 blob 做三方合併,不涉及檢出到工作目錄,clean/smudge 完全不會被呼叫。
- `core.pager` 搭配 `pager.show = true`(強制開 pager 而非只看 tty):因為呼叫方式是 `subprocess.run(capture_output=True)`,stdout 是管線不是 tty,git 沒有觸發 pager。
- hooks(`pre-merge-commit`、`post-merge`、`post-checkout`、`pre-commit`):remerge-diff 只是模擬合併算差異、不建立提交也不檢出,四種 hook 都沒被呼叫。

## 時間差(③)——僅推論,未能構造真實攻擊
守門呼叫(`git config --get-regexp`)與實際執行(`git show --remerge-diff`)是兩次獨立的 `subprocess.run`,理論上兩次呼叫之間存在窗口。但在本鏡頭設定的威脅模型裡(攻擊者只是「給一個資料夾」,資料夾本身是靜態檔案,不是常駐行程),要在這個窗口內把 `.git/config` 從「無驅動器」換成「有驅動器」,需要攻擊者已經有另一個同時執行的行程在監看檔案存取並即時改寫——這超出「被動資料夾」的攻擊面,沒有辦法只靠資料夾內容本身構造出來,所以沒有實測,只記錄推論在此,不算發現。

## 結論
①②③三個重點都實測過,沒有找到可利用的洞。這批改動看起來把「合併提交自己改了什麼」判得更準的同時,守門(先確認沒有自訂合併驅動器才用 remerge-diff)也真的擋住了測過的所有寫法,remerge-diff 本身在 `--name-status` + `--no-ext-diff --no-textconv` 的用法下沒有其他可執行面。
