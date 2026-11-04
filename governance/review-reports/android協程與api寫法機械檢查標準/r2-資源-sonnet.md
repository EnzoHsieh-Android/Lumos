severity: major

審稿立場:機器資源。依規定只用繁體中文。實驗暫存(`/tmp/lumos-seat-work/android協程與api寫法機械檢查標準/資源-sonnet/`)已用字面絕對路徑刪除。

**對 r1 的處理**:r1-intake 已折入「預設預算小於單條保底」(範圍 7 保底降成 1 秒)和「共用工作目錄」。下面都是 r1 沒碰到的新問題。

**逐類回答**
- 孤兒子程序、暫存殘留:有 finding(F1、F2)。
- 時間預算:有 finding(F2、F3、F5、F6)。
- 記憶體與二次方:有 finding(F4)。型錄本身無問題,見下方。
- 型錄一次讀進記憶體:無。`skills/kotlin-idioms/checks-catalog.md` 實測 254120 位元組、844 行,讀一遍毫秒級。改檔前推列每次花的時間,幾乎都是 `python3.14 scripts/lumos --help` 實測的 0.74 秒啟動成本(三次都是 0.73~0.75 秒),不是解析型錄。

**合約與事故節點**:附在派工尾端的節點(`Systems/linter精選目錄`、`棧別提問表態閘`、`pitfalls-code-loop`、`graph-sync-coverage`、`改檔前推播`)都標 0 條合約。所以本案沒有破壞哪條宣稱行為的合約。事故類(例如 `impact-hook.py` 註解提的「單檔固定 30 秒讓 fail-open 分支跑不到」)與 F6 有關,見該條。

## Finding 1:鉤子逾時只殺到 lumos 本身,掃描子程序、掃描暫存檔、暫時索引全部殘留
引句:「鉤子被平台強制結束時,新增告警閘的快照暫存照既有規則一天後清」
severity: major
blocking: 是
判準:預設子程序會殘留成孤兒,而 spec 宣稱的清理只涵蓋其中一項。

- **孤兒子程序**
  - 鉤子端若沿用 `check-graph-sync.py:751` 的 `subprocess.run(..., timeout=)` 去叫 `lumos lint-new --worktree`,逾時只會 SIGKILL 直接子程序(lumos),lumos 沒機會執行 `_kill_proc_group`。
  - lumos 內部用 `start_new_session=True` 開 ast-grep 等命令(file: `scripts/lumos:38392`),它們在另一個程序群組,不會被一起殺。
  - 實驗:父程序 `subprocess.run([python, child.py], timeout=2)`,child 用 `Popen("sleep 47", shell=True, start_new_session=True)`。逾時後 `ps` 看到 `sleep 47` 的 PPID=1,孤兒存活。
- **暫存檔**
  - `_lint_run_and_parse` 的 `finally: os.unlink(temp_path)`(file: `scripts/lumos:38479`)在 SIGKILL 下不跑,`/tmp/lumos-lint-*.sarif` 殘留。這類檔沒有任何一天後清掃。
  - 一天後清掃只掃 `.lumos/lintbase-*`(file: `scripts/lumos:38957`)。
- **暫時索引**
  - 範圍 7 的「複製目前索引到暫時檔」沒寫放在哪、也沒寫例外或強殺時怎麼收。我複製 2 萬檔 repo 的索引是 1.8MB,大型 monorepo 會更大。
  - 此外,逾時後 spec 沒要求鉤子回頭收尾,孤兒又在 `.lumos/lintbase-*` 外的路徑寫東西。

## Finding 2:暫時索引上的 `git add -A` 掃整棵樹,不受 `--only` 限制,在時間預算之外,還會寫進真正的物件庫
引句:「改動清單用暫時索引算:複製目前索引到暫時檔、在暫時索引上」
severity: major
blocking: 是
判準:回合結束鉤子每輪都付一筆與「這輪寫過幾支檔」無關、且不計入 15 秒預算的整樹成本。

- 範圍 7 說 `--only` 只過濾結果,但改動清單是整樹 `git add -A` 算的。
- 實驗(2 萬個 kt 檔的 repo,多一個未被忽略的 300MB 未追蹤檔 `app/big.hprof`、一個已修改檔):
  - 暫時索引上的 `git add -A` 加 `git diff --cached --name-status HEAD` 共 6.4 秒。
  - `.git` 從 81M 漲到 292M。暫時索引只換了索引檔,blob 仍寫進真的 `.git/objects`。
  - 同一檔第二次跑 0.22 秒(物件已存在),所以首輪最痛。
- 預算起點:`budget_end` 在抽快照之後才算(file: `scripts/lumos:39118`),所以這 6.4 秒不在「上限 15 秒」裡。
- 另外 `.lumos/lintbase-*` 快照如果消費專案沒忽略,也會在 `git add -A` 時被 hash 進物件庫(範圍 7 自己承認「消費專案不一定忽略它」),而排除它要等 diff 算完之後。

## Finding 3:`--budget` 的起算點在抽檔之後,所以鉤子外層逾時與內層預算沒對上
引句:「兩種都加 `--budget 秒`」
severity: major
blocking: 是
判準:大輸入下前置階段不受預算管,實際耗時超過鉤子或使用者設的上限。

- 前置階段(lumos 啟動 0.74 秒、暫時索引、`_lint_new_changed_files`、`_lint_new_extract`)都在 `budget_end` 計算之前。
- `_lint_new_extract` 對每個檔、每邊各開一個 `git show` 子程序(file: `scripts/lumos:38816`)。實測 3000 次 `git show` 約 57 秒(shell 迴圈,每次約 19 毫秒)。
- 範圍 10 把 `code-loop pass` 的範圍明講拉寬到「跟主線的分岔點到 HEAD」。一條 3000 個 kt 檔的大重構分支,抽 base 與 head 兩邊約 100 秒以上,預算還沒開始算。
- 後果:
  - 呼叫者用內層預算或對話的指令逾時(預設 2 分鐘)當外層時,在預算起算前就被殺,同 F1 留下孤兒與 `lintbase-*`。
  - spec 沒寫鉤子叫 lumos 時的逾時要比 `--budget` 多留前置成本。
  - 若鉤子把「切一半、上限 15 秒」同時當 `--budget` 和 `subprocess` 逾時,F1 的殺法在正常大專案下就是常態而不是例外。

## Finding 4:回合結束新增的一道把「整份逐字稿讀進記憶體」帶到沒有圖譜的專案,且可能多讀一次
引句:「插在既有那道的所有提早離開(找不到圖譜、動過筆記、同批檔已講過)之前,所以沒有圖譜的專案」
severity: major
blocking: 是
判準:大逐字稿下記憶體尖峰約為檔案大小的 10 倍,而且擴大到原本在讀逐字稿之前就退出的專案。

- 檢查範圍靠「只限這一輪逐字稿裡寫過的程式碼檔」,只能走 `collect_turn_actions`,它是 `transcript_path.read_text().splitlines()` 整份讀入(file: `scripts/hooks/claude/check-graph-sync.py:211`)。
- 實測本機最大逐字稿 406323943 位元組:耗時 2.09 秒,最大常駐記憶體約 3.96GB。
- 現況在 `find_graph_root` 為 None 時就 `return 0`(file: `scripts/hooks/claude/check-graph-sync.py:1000`),沒圖譜專案不碰逐字稿。spec 改成沒圖譜也跑,所以消費端的 Android 專案(只有 `.lumos/lint.json`)每個 Stop 都付這筆。
- 長時間自動執行的會談,逐字稿一路增大,每回合都要整份重讀,總成本是回合數乘檔案大小,即二次方。
- spec 沒寫新一道與既有一道共用同一次讀取。若各自呼叫,圖譜專案每個 Stop 讀兩遍。

## Finding 5:「切一半、另一半留給既有那道」與內層預算的實際公式不符,既有那道的保證只剩 13 秒
引句:「從鉤子既有的內層預算(外層天花板乘 0.7 扣掉已用)切一半給這道、上限 15 秒,另一半留給既有那道」
severity: minor
blocking: 否
判準:只會讓一則提醒靜默變少,不擋正常操作。

- `_inner_budget` 回的是「還剩多少」,不是配額(file: `scripts/hooks/claude/check-graph-sync.py:712`)。這道若用到 15 秒,既有那道拿到 28−15=13 秒。
- `scripts/merge-claude-settings.py` 的註解寫 `check-graph-sync.py` 的圖譜同步檢查「實測需要 25 秒」,所以天花板才訂 40。13 秒不夠它。
- `_impact_missing` 逾時後的例外被吞掉、回 `[]`(file: `scripts/hooks/claude/check-graph-sync.py:751`),「動了筆記卻漏動相關筆記」的提醒靜默消失。
- 觸發情境就是 F2 的首輪(6.4 秒加啟動 0.74 秒),花掉近一半,圖譜那道不夠。

## Finding 6:改檔前推相關列的第二次 lumos 子程序沒有預算規則,每個 kt 寫入多 0.74 秒
引句:「鉤子把寫入內容交給 `lumos impact --file <檔> --delta-stdin`(新增旗標)」
severity: minor
blocking: 否
判準:每次 Edit/Write 對 `.kt` 多付一次啟動成本,逾時處置沒寫。

- 既有路徑已經把寫入內容走 `--stdin-payload` 交給 `lumos impact --file`(file: `scripts/hooks/claude/impact-hook.py:1001`)。spec 另加一個新旗標,若是第二次呼叫,每個 `.kt` 寫入多 0.74 秒。對 100 次 Edit 的重構是 74 秒。
- spec 沒寫第二次呼叫的逾時。`impact-hook.py:920` 的註解記載過「單檔固定 30 秒」讓內層永遠沒機會跑 fail-open、外層 30 秒 SIGKILL 整支鉤子並留下 20 分鐘冷卻標記。第二次呼叫若用預設 30 秒,會在既有那次吃掉內層預算後重演。
- ⚠ spec 沒說新旗標是併進既有呼叫還是另開一次,我判不準。

## 其他節
已讀,無 finding:用詞、分批、驗收條款、回退、天花板、裁決紀錄、舊版初稿的去向。

總結:最嚴重 severity: major,blocking 共 4 條(F1、F2、F3、F4)。
