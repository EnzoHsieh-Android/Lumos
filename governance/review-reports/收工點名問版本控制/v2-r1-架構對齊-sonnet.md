severity: major

# 架構對齊審查:收工點名問版本控制(第二版)

## 問一:這一版真的沿用既有做法了嗎?

**沒有——它把「沿用第三種」寫在 PRIOR-ART,但技術描述其實選了第四種查詢。**

先核對既有三處實際各自問的是哪一種:

- pre-commit(提交前那道閘):`file: \`scripts/hooks/pre-commit:43\`` —— `STAGED="$(git -c core.quotePath=off diff --cached --name-only)"`,問的是「已暫存(staged/index)清單」。
- pre-push(推送前那道閘):`file: \`scripts/hooks/pre-push:51\`` —— `"$PY" "$GRAPHCTL" impact --diff "$1" --sync-check --json`,而 `_range` 在 `file: \`scripts/hooks/pre-push:167-173\`` 是 `$_rsha..$_lsha`(兩端 commit 的範圍),問的是「提交範圍」。
- 這支 hook 閘門 3 那條路(唯一沒被這次改動碰的分支):`file: \`scripts/hooks/claude/check-graph-sync.py:600\`` —— `subprocess.run([sys.executable, lumos, "impact", "--diff", "HEAD", "--sync-check", "--json", ...])`,而 `cmd_impact_diff` 內部在 `file: \`scripts/lumos:25233-25234\`` 實際執行的是 `git diff --name-only HEAD`,問的是「工作樹(含已暫存)對上次提交 HEAD 的差異」——**不含從未 `git add` 過的全新檔案**,因為 `git diff` 本來就不列未追蹤檔。

三種都是「diff」家族的不同範圍(staged / commit-range / working-tree-vs-HEAD),沒有一種是 `git status --porcelain`。而這一版的 PRIOR-ART 節明講要用的是:

引句:「零依賴家規下不引入新套件:`git status --porcelain` 即可,本 repo 4074 個追蹤檔實測跑一次約 30 至 40 毫秒」

`git status --porcelain` 跟前三種在語意上不是同一件事——它會多列出「從未提交過、也從未 `git add` 過」的全新檔案(`??` 項目),這是 `git diff`(不管對 staged / 對某個 commit range / 對 HEAD)結構上都看不到的一類。所以「本方案沿用第三種」這句話,跟它自己在同一篇裡寫下的技術選型(`git status --porcelain`)對不上:

引句:「本 repo 已經有三處在做同一件事,全部直接問版本控制」

引句:「本方案是沿用第三種,不新增第四種」

但緊接著在下一段給的可執行細節卻是另一條命令、另一種查詢語意,而且沒有一行提到會呼叫既有的 `lumos impact --diff HEAD --sync-check`(閘門 3 分支本來就在用、本計劃也承認它「本來就對、不用動」)。換句話說,**S1/S2 要用的查詢跟閘門 3 分支現成在用的查詢是兩套不同的東西,只是都貼著「問版本控制」這個標籤**,而 PRIOR-ART 的措辭把兩者說成同一種。這正是第一版被判 major 的同一種毛病(自稱沿用既有、實際上另開一種),只是這次換了個更隱蔽的位置——不是自建快照,而是自選一條全 repo 都還沒人用過的 git 查詢語法來做「這一支 hook 現成有函式可以直接重用」的事。

引句:「工作樹上有哪些程式碼檔還沒提交」

這句話本身作為需求描述沒有錯,但拿它去論證「這就是第三種、不是第四種」,查證下來是假的。第三種問的是「對 HEAD 的 diff」,這一版要的是「status(含未追蹤檔)」,兩者只在「都不自己存狀態、都問 git」這一點上一樣,在查詢範圍上不一樣。

severity: major
blocking: 是

## 問二:委派方式一不一致

這支 hook 現有三種呼叫外部的方式並存,不是題目講的兩種:①純 Python 邏輯(`is_code_file`、路徑排除);②不經 `_trusted_lumos` 信任檢查、直接 subprocess 呼叫外部 CLI(`file: \`scripts/hooks/claude/check-graph-sync.py:404-406\``,`obsidian` 那一段);③經 `_trusted_lumos()` 信任檢查後 subprocess 呼叫主程式(`file: \`scripts/hooks/claude/check-graph-sync.py:596-600\``,`_impact_missing`)。**這一版要新增的 git 查詢,走哪一種,計劃沒講。**

FLOW 與條款都只寫「問版本控制」,沒有任何一行說是「直接在 hook 內 `subprocess.run(["git", ...])`」還是「新開一個 lumos 子命令、照③那樣經 `_trusted_lumos` 呼叫」。PRIOR-ART 的效能量測(`git status --porcelain` 跑 30–40 毫秒)聽起來像是在替「直接呼叫 git」鋪陳,但這件事從未被計劃正面講出來。

引句:「開口之後說哪幾支檔,一律問版本控制」

若真走「直接呼叫 git」,那會是這支檔案第一次不經 `_trusted_lumos()` 信任檢查就 subprocess 呼叫一個從 PATH 找到的執行檔並拿它的輸出做判斷依據(`obsidian` 那一段雖然也不經信任檢查,但它的輸出只拿來加值提示,不是本案這種「拿它的輸出直接決定清單/決定閘門走向」的權重)。這不必然是錯誤方向,但既有兩種既有委派模式(③現成有 `_impact_missing` 可以重用)並存的情況下,計劃完全沒表態要沿用哪一種、要不要重用現成函式,這是未交代。

severity: minor
blocking: 否

## 問三:錯誤處理一不一致

鄰居的既有慣例是「算不出來就 fail-open,多半靜默,少數會印一行 stderr 說明降級原因」——例如 `_impact_missing` 在 `file: \`scripts/hooks/claude/check-graph-sync.py:596-609\`` 找不到可信 lumos 或 subprocess 出錯一律回 `[]`,不印任何訊息;`find_notes_mentioning` 在 `file: \`scripts/hooks/claude/check-graph-sync.py:412-413\`` 遇到 `FileNotFoundError`/`TimeoutExpired`/`OSError` 也是靜默回 `{}`;而 `_stop_block_dir`/`_stop_dir_ok` 在信任檢查沒過時則會印一行 stderr 說明「為什麼停用」(`file: \`scripts/hooks/claude/check-graph-sync.py:630-634\``)。這兩種都是「不擋、繼續往下走」,差別只在要不要留一句話。

這一版拿掉了第一版的「降級模式」,但拿掉的理由只針對「沒有自存的基準快照,所以不會有『取不到基準』這件事」:

引句:「降級模式常態化、警語該走哪條輸出路徑(接手席 blocker、回滾席 major) | 沒有基準,就沒有「取不到基準」的降級模式」

這個推論只處理了「v1 特有的快照基準缺失」這一種失敗模式,沒有處理「v2 這條新查詢本身執行失敗」這個新的失敗面——例如 `git status --porcelain` 逾時、`git` 執行檔不存在、`.git` 損毀、worktree 非常規狀態。整份文件(條款 S1–S6、驗收條件、撤除條件)找不到任何一句話講這種情況下 hook 要閉嘴、要印訊息、還是要照舊印「查不到就當沒有」。既有慣例是有的(上面兩種都存在),但這一版沒表態要跟隨哪一種,也沒有新開一種並講清楚——是單純沒交代。

severity: minor
blocking: 否

## 問四:落點合不合理

`Systems/graph-sync-coverage.md` 現有 52 行,summary 只圍繞「三個時機的點名內容、為什麼不硬擋、擋停標記目錄的信任檢查」這幾件事,已經掛了 8 篇計劃(含本篇與被重寫的前身)。它的 about_code 確實列了 `scripts/hooks/claude/check-graph-sync.py` 與 `scripts/lumos`(後者在本 repo 是多節點依規模分工共同認領的巨型檔案,不算違規)。

但條款 [S5] 與〈回退〉節談的是另一件事——「repo 裡的 hook 檔改了要跑安裝指令才會同步到 `~/.claude/hooks` 與各接入專案的複本」:

引句:「當 repo 裡的 hook 檔被改動後,安裝器應把它同步到所有已部署的位置,否則實際生效的仍是舊版」

這是「安裝器 / vendor 同步機制」的通用行為,不是「圖譜同步點名」這個功能本身的行為——查證下來,這件事現成有專門的節點在管:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md` 已經記著「全域 lumos 與 skills 走 symlink/junction 指向來源 clone」「vendor 結尾 diff 自癒(逐檔 filecmp 比對 src↔target 差異即 shutil.copy2 覆補)」「`_sync_global_claude` 把 hooks 複製到 `~/.claude/hooks`」這些機制本身的細節(`scripts/lumos:14429`、`16049` 一帶)。S5 說的正是這套既有機制要不要涵蓋這次改的檔案,屬於 lumos-cli-lifecycle 的範圍,不是 graph-sync-coverage 的範圍——後者的 summary 從沒提過「安裝/部署同步」這件事。把 S5 與整段〈回退〉的三類部署位置細節塞進 graph-sync-coverage,會讓這篇節點的職責從「點名機制」擴大成「順便管部署同步」,而部署同步本身另有專門節點在管、且已經記了很多細節(symlink vs copy、diff 自癒等),這裡重寫一份容易跟那邊的既有敘述不同步。

比較合理的落點:S5 本身的「安裝器要同步」這個事實鏈進 `[[Systems/lumos-cli-lifecycle]]`(或至少用連結指過去,而不是在 graph-sync-coverage 裡重新描述部署機制),graph-sync-coverage 只保留「這次改的檔屬於需要跑安裝指令才生效的那一類」這句提醒。

severity: minor
blocking: 否

---

不對齊共 4 條,其中 major 1 條。
