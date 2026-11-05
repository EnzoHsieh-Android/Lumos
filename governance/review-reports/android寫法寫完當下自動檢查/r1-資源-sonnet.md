severity: major

資源席審查報告,針對 `r1-snapshot.md`(凍結 spec)。逐節已讀。實驗用的臨時目錄與殘留程序已清掉。

**範圍 4(改檔前推相關列)、驗收條款、回退、天花板:** 已讀,除下列 finding 外無 finding。

---

**F1. 逾時只殺 lint-new 的程序群組,殺不到真正的檢查工具,留下孤兒和快照殘骸**
severity: major
blocking: 是(判準:規劃的逾時回收法實測失效,每次逾時都會留下孤兒程序與快照目錄)
spec 段落:範圍 3「用新程序群組開、逾時整個群組一起殺」,與驗收 S3「逾時 應 連子程序一起結束」。
引句:「用新程序群組開、逾時整個群組一起殺(新增告警閘自己的快照暫存在 `.lumos/lintbase-*`,照既有規則一天後清)」
問題:
- `lint-new` 內部跑檢查工具時,又用 `start_new_session=True` 另開 session,工具不在 `lint-new` 的群組裡。
- 鉤子殺 `lint-new` 的群組,碰不到 ast-grep。ast-grep 會變成孤兒繼續跑。
- SIGKILL 殺掉 `lint-new` 時,`_lint_new_tools` 的 `finally: shutil.rmtree(work)` 也不會執行。每次逾時就留下一個 `.lumos/lintbase-*` 目錄,內含快照與設定檔副本,要等一天後才被下一次 `lint-new` 清掉。
- 這道每回合都跑,工具持續偏慢時,殘骸和孤兒會逐回合累積。
- S3 的測試條款只驗「連子程序一起結束」,抓不到這個缺口。
實驗(用 python 模擬 hook → lint-new → shell linter 兩層 `start_new_session`,對第一層 `killpg(SIGKILL)` 後 `ps`):
```
70162     1 70162 sleep 37
```
孫程序存活,ppid 變 1,自己的 pgid。
佐證:
- file: `scripts/lumos:39155-39190`,`_lint_run_and_parse` 的 `Popen(..., start_new_session=True)`。
- file: `scripts/lumos:26287`,`_kill_proc_group` 只 `killpg(proc.pid)`。
- file: `scripts/lumos:40041-40068`,`finally` 清快照。
- file: `scripts/lumos:39767`,殘骸一天後才清。

**F2. 鉤子逾時 10 秒和 `lint-new --budget 10` 同值,而且 lint-new 的預算起算點在啟動之後**
severity: major
blocking: 是(判準:正常慢機器上,鉤子的殺手一定先於 lint-new 自己收尾,F1 的殘骸變成常態)
spec 段落:範圍 1「兩種都加 `--budget 秒`,預算從指令一開始起算(含抽檔)」,範圍 3「這道用固定上限 10 秒」。
引句:「時間:這道用固定上限 10 秒;鉤子時間上限從 40 秒加到 50 秒。」
問題:
- `lint-new` 的 `--budget` 只約束命令執行期,啟動時間不在內。
- `lumos` 是無副檔名的腳本,沒有 `.pyc` 快取,每次都重新編譯。實測 `python3.14 scripts/lumos --help` 空閒機器上 0.76 秒、常駐約 362 MB。
- 預算耗盡後還有兩段不受預算控制的工作:最後一條命令跑到 `budget_end` 才回來,之後還有比對與 `rmtree`。
- 所以 `lint-new` 總耗時約 0.76 秒啟動 + 10 秒預算 + 收尾,超過鉤子 10 秒的外層殺手。正常的逾時路徑也走 SIGKILL,不是 `lint-new` 自己判成 rc3。
- spec 的 rc3 協定(「沒檢查到」印一行到 stderr)在這條路徑上到不了。
實驗:`lumos --help` 量得 0.76 秒。`_lint_new_run_one` 的逾時是 `max(1, int(budget_end - now))`,與外層沒有留白。
佐證:
- file: `scripts/lumos:40096-40112`。
- file: `scripts/lumos:39297-39298`,預設 `budget_sec` 300、`per_cmd_floor_sec` 30,spec 用 1 秒保底覆寫。

**F3. 「加 10 秒剛好抵掉」不成立:`_BUDGET_START` 是第一次呼叫 `_inner_budget` 才記的,而且 50 × 0.7 − 10 = 25,比現在的 28 少**
severity: major
blocking: 是(判準:spec 宣稱的預算守恆在程式碼現況下不成立,既有那道實際可用時間與總時間都會偏離宣稱)
spec 段落:範圍 3「時間」。
引句:「既有那道的內層預算照同一公式(時間上限 × 0.7 減掉已耗時,已耗時含這道),加 10 秒的上限剛好抵掉這道用的時間。」
問題:
- 程式現況:`_BUDGET_START = None`,註解寫「第一次用到時記」,不是鉤子開跑時。
- spec 把新道插在最前面。如果新道不呼叫 `_inner_budget` 或不先設 `_BUDGET_START`,這 10 秒(加上整份逐字稿讀取時間)都不算已耗時。
- 既有那道內層預算會是完整的 35 秒。總時間可能到 10 + 讀逐字稿 + 35,接近或超過外層 50 秒,被平台 SIGKILL。這發生在要輸出 `decision: block` 之前,擋停原因就丟了。
- 反過來,如果新道有記進已耗時,既有那道的內層預算是 35 − 10 = 25 秒,比現在的 28 秒少。
- 但 `HOOK_BUDGET` 的註解寫明該道實測需要 25 秒,並說「40×0.7=28 才真的夠」。25 秒是零餘裕,「剛好抵掉」是錯的。
- spec 沒指定要在 `main` 開頭設 `_BUDGET_START`,也沒指定新道怎麼記入耗時。
佐證:
- file: `scripts/hooks/claude/check-graph-sync.py:685`、`:712-736`,`_BUDGET_START` 惰性起算。
- file: `scripts/merge-claude-settings.py:110-121`。

**F4. 回合結束檢查寫「每次跑」的時間戳檔,與現有標記目錄「只有擋過的會談才留東西」的性質和測試矛盾;清理責任也沒寫**
severity: major
blocking: 是(判準:spec 同一份文件對同一個目錄給出兩個互斥的不變量,且現有測試釘死其中一個)
spec 段落:〈用詞〉「這一回合碰過的檔」,與範圍 3 最後一條。
引句:「回合結束鉤子每次跑都在自己的標記目錄寫一個這個會談的時間戳檔(新增)」
引句:「既有「這個目錄只有擋過的會談才留東西」不變」
問題:
- 兩句放在同一份 spec。時間戳檔每次 Stop 都寫,是每個會談一個檔;而擋停名額目錄的性質是只有擋過的會談才留標記。
- `check-graph-sync.py` 的 `_stop_block_dir()` 註解明說該目錄以此為性質,測試 `stop-block⑧` 斷言目錄內容只有擋過的 `sess-1`、`sess-4`、`sess-ascii`。
- spec 沒指定時間戳檔放哪個目錄。放進 `stop-block` 會直接讓測試紅;另開新目錄則要自己的七天惰性清理,spec 沒寫。
- 時間戳檔被七天清理刪掉後(會談隔八天再續),退回「逐字稿第一筆紀錄的時間」,整個會談歷來所有未提交檔都算這一回合碰過(見 F5)。
- `.rows` 標記也有同樣的缺口。既有改檔前的標記位於 `$TMPDIR/lumos-impact-<會談>/`,以目錄 mtime 24 小時清理。重寫檔案內容不會更新目錄 mtime,所以長會談的 `.rows` 會在 24 小時後被整個清掉,「同列同會談只推一次」就失效。spec 沒寫 `.rows` 放哪個目錄。
佐證:
- file: `scripts/hooks/claude/check-graph-sync.py:758-760`、`:763-800`。
- file: `scripts/test_lumos.py:54890`。
- file: `scripts/hooks/claude/impact-hook.py:177-190`、`:149-160`。

**F5. 「這一回合碰過的檔」沒有數量上限,首次收工的回退值會涵蓋整個會談,逐檔 `git show` 也不受預算管**
severity: major
blocking: 是(判準:會談第一次收工,清單可能是幾百支檔,實測處理成本超過 10 秒鉤子上限,每個既有會談在升級後必遇一次)
spec 段落:〈用詞〉「這一回合碰過的檔」,範圍 1「(含抽檔)」。
引句:「會談第一次收工沒有時間戳檔時,用逐字稿第一筆紀錄的時間。」
問題:
- 升級後所有進行中的會談都沒有時間戳檔。長會談(跨日)的第一次收工會把會談開始以來所有 mtime 較新的未提交檔全算進來,共用工作目錄時還包含別人的。
- 現況 `_lint_new_extract` 對每個檔、每一側各跑一次 `git show` 子程序,沒有檢查 deadline。實測 100 次 `git show` 約 2.0 秒,每次約 20 毫秒;每側一次,兩側就是每檔約 40 毫秒。300 支檔約 12 秒,超過鉤子 10 秒上限。spec 說預算「含抽檔」,但 `_lint_new_extract` 沒有逾時檢查,spec 沒寫要改它。
- `_lint_cmd_with_files` 把所有檔名展開進同一條 shell 命令,沒有批次或上限。數千支檔會撞命令列長度上限,錯誤會被歸成「這條命令跑不出可解析的結果」,rc3。
- 工作樹模式「直接讀工作樹的檔」是新程式碼,沒說是複製(而且是在預算內)還是直接指到原檔。
- spec 未規定檔數上限或分批策略。
佐證:
- file: `scripts/lumos:39626-39648`。
- file: `scripts/lumos:39325-39341`。
- 實驗指令:`for i in $(seq 1 100); do git show HEAD:scripts/hooks/claude/impact-hook.py >/dev/null; done` → 2.031 秒。

**F6. 逐字稿「只讀尾端 20 MB」與〈用詞〉的回合起點定義互相矛盾,而且 20 MB 內找不到回合開頭時沒有行為**
severity: minor
blocking: 否(判準:不直接造成資源失控,屬 spec 不一致、實作者必須自行猜)
spec 段落:範圍 3 第三點,與〈用詞〉。
引句:「逐字稿只從尾端往前讀到這一回合的開頭,最多讀 20 MB(既有那道整份讀的做法不在本案改,另記回頭條件)。」
問題:
- 〈用詞〉明說「不用『逐字稿最後一則使用者輸入』判回合開始」,回合起點靠時間戳檔或逐字稿第一筆(檔頭,不是尾端)。範圍 3 卻說從尾端往前讀到回合開頭,兩者起點的來源互斥。
- 用逐字稿最後一則使用者輸入判回合開頭,正是〈用詞〉否決的做法。
- 也沒說 20 MB 內找不到邊界時怎麼辦。含截圖 base64 的長回合很容易超過 20 MB。
- 這個「尾端讀取」到底為了什麼(算檔名?判 Codex?)spec 沒有交代,疑似可以整段刪掉。
- 另外:既有那道在新道之後仍要整份讀逐字稿,所以 spec 的 20 MB 限制對峰值記憶體沒有效果。REVISIT 已誠實承認 406 MB 常駐約 4 GB,這點不重報。
佐證:file: `scripts/hooks/claude/check-graph-sync.py:204-211`,`collect_turn_actions` 整份 `read_text`。

**F7. `delta_new` 與 Kotlin 剝註解字串沒有大小上限**
severity: minor
blocking: 否(判準:既有 `delta_text` 有 2 MB 上限,新鍵沒有,屬資源面遺漏;速度在實測範圍內可承受)
spec 段落:範圍 4。
引句:「payload 多一個鍵 `delta_new`:只放寫入的新內容(Edit 的 `new_string`、MultiEdit 每段的 `new_string`、Write 的 `content`),不含舊字串。」
問題:
- 既有 `delta_text` 有 `DELTA_TEXT_CAP = 2 MB`,spec 沒說 `delta_new` 是否同樣截斷。Write 一個大的生成檔會讓 stdin 和比對都不受限。
- 實測一個逐字元的 Python 剝註解/字串迴圈,處理 4.1 MB 約 0.55 秒;巢狀 `/* */` 與 `${}` 堆疊版會更慢。
- 單條 Edit 的鉤子預算 30 秒 × 0.7,這個成本本身不致命,但上限和超限行為(截斷並註記?略過?)要寫。
佐證:
- file: `scripts/hooks/claude/impact-hook.py:414`,`DELTA_TEXT_CAP`。
- file: `scripts/hooks/claude/impact-hook.py:417-435`,`extract_delta_text`。

**F8. 改名偵測(未追蹤檔配已刪除檔的 HEAD 內容)的比對方式與成本沒定義**
severity: minor
blocking: 否(判準:我的小規模實驗沒到超時,規模上限沒有證據)
spec 段落:範圍 2「改動清單」。
引句:「但若同一份清單裡有一支已刪除的檔、而 HEAD 那一版內容跟這支未追蹤檔逐位元組相同,就當成改名」
問題:
- 要對每個未追蹤檔拿 HEAD 的已刪除檔內容逐一比對。套件搬移(上千檔)若用逐對讀 blob 的寫法會是二次方。
- spec 沒寫用雜湊索引(例如 `git ls-tree` 的 blob id 對 `git hash-object`),也沒寫它是否在 `--budget` 內。
- 我的小實驗(3000 × 3000 位元組比較、有 early break)只花 0.19 秒,但沒測 git 子程序版本,所以只標 minor。⚠ 判不準:實作成「逐對子程序」才會爆,spec 沒鎖定做法。
- 補充量測:`git status --porcelain=v2 -z --untracked-files=all` 在 10 萬個未追蹤檔的暫存 repo 上只用 0.117 秒,這條不是問題。

---

最嚴重 severity:major;blocking 共 5 條(F1、F2、F3、F4、F5)。
