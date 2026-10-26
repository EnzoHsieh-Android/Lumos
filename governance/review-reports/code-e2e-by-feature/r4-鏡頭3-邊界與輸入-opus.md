severity: major

## F1 在主線上直接開發時,--changed 看不到已提交但還沒推的改動,會靜默少挑功能
severity: major
blocking: 是
file: `scripts/lumos:40855`(`_e2e_changed_files` 呼叫 `_secev_mainline(root, head)`,沒帶 pushed_branch)
失敗場景:repo 有 origin、`refs/remotes/origin/main` 指向初始提交,本機在 main 上多提交一次改 `app/src/login/L.kt`(`origin/main..HEAD` 有 1 個提交)。程式把本機 main 也算進主線候選,而它就等於 HEAD,於是 `_secev_mainline_pick` 挑出的主線頂端是 HEAD 本身,分岔點也變成 HEAD,`diff base head` 是空的。
- 只有這一個提交時:`android-e2e select --changed` 回 2,訊息是「改到的檔 (沒有改動)」。
- 再在工作目錄改 `app/src/main/A.kt`(屬 home 功能):回 0,只挑到 `home.ok`,`login.ok` 被漏掉。`note` 是空的,`unmatched` 也是空的,使用者完全看不出有東西被漏掉。
- 從同一點開 feat 分支(本機 main 仍等於 HEAD)時也一樣是「沒有改動」。

S23 寫的是「HEAD 加工作目錄改動……對分岔點的差異」。計劃〈資料怎麼流〉對「推的就是主線本身」另有規則(用推送前的主線位置),但 --changed 沒有比照,`file: \`docs/lumos-toolchain-knowledge/Projects/Android端到端驗收_計劃.md:91\``。
引句:「ml, why, _code = _secev_mainline(root, head) if head else (None, "讀不到 HEAD", None)」
最小重現:用 git init -b main 建暫存專案,`remote add origin <任意路徑>`,`update-ref refs/remotes/origin/main HEAD`,`symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main`;提交一次對 login paths 的改動;再改 home paths 的檔不提交;跑 `python3.14 scripts/lumos android-e2e select --repo <專案> --changed`。
歸因:有證據的原有漏查。修前 4b056532、修後 7988107c 各自的臨時 clone(`git -C <clone> rev-parse HEAD` 印出兩個完整 sha 確認版本)跑同一支探針,結果逐字相同:三種情況分別是 rc2「(沒有改動)」、rc0 只挑 home.ok、rc2「(沒有改動)」。

## F2 功能 paths 寫成 ./. 修前會擋,修後放行,而且永遠對不到任何檔
severity: minor
blocking: 否
file: `scripts/lumos:40287`、`scripts/lumos:40289`、`scripts/lumos:40457`
失敗場景:`features.all.paths=["./."]`,另有 `home.paths=["app/src/main"]`;在 feat 分支提交 `app/src/main/A.kt` 的改動。
- 修後:`--check-config` 合格;`select --changed` 回 0,只挑到 `home.smoke`。原意是「改什麼都算」的 `all` 功能被靜默略過,因為 `_e2e_under(f, ".")` 永遠不成立。
- 修前:舊的功能路徑檢查有 `_e2e_norm(x) in ("", ".")` 這一條,會回 2「'./.' 要寫成正規的相對路徑」。

原因:修補把功能路徑併進 `_e2e_relpath_err`。新函式判「只寫 .」時看的是 `q`(只去掉頭尾空白與結尾斜線,還是 `./.`),判正規寫法時看的是 `_e2e_norm(p)`(去掉 `./` 後是 `.`,normpath 之後還是 `.`)。兩道都漏過,S26 寫明「只寫 `.`」要回 2。app_dirs 寫 `./.` 修前修後都放行。
引句:「if posixpath.normpath(_e2e_norm(p)) != _e2e_norm(p) or any(c in q for c in "*?["):」
引句:「if q in ("", ".") or ".." in q.split("/"):」
歸因:有證據的修復回歸。同一份設定:修前 check-config 回 2,select 也是 rc2 並點名 './.';修後 check-config 回 0,select 回 0 只挑 home.smoke。兩版都在臨時 clone 上用 python3.14 跑,版本照 rev-parse 確認。

## F3 run-id 不能叫 history.jsonl 那道擋只比對全小寫,macOS 上寫成 History.jsonl 照樣佔掉總表
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh:321`、`scripts/templates/android-e2e-run.sh:526`、`scripts/lumos:40389`
失敗場景:macOS 預設的 APFS 不分大小寫。跑 `--case login.ok History.jsonl` 會建出 `.lumos/artifacts/android/History.jsonl/` 目錄,它跟總表 `history.jsonl` 是同一個路徑。這次與之後每一次的總表寫入都失敗,只印「提醒:檢測總表……寫不進去」,回傳碼仍是 0,S25「每一次都記」就此長期失效。下一次用正常 run-id `next1` 跑,同樣寫不進去,`history.jsonl` 仍是目錄。
引句:「if run_id == "history.jsonl":   # 本機總表 .lumos/artifacts/android/history.jsonl 跟 run 目錄在同一層」
最小重現:載入該版 `test_lumos.py`,用 `_e2e_feat_env`,呼叫 `_e2e_script(root, script, env, "--case", "login.ok", "History.jsonl")`,接著看 `root/.lumos/artifacts/android/history.jsonl` 的 `is_dir()`。
歸因:有證據的原有漏查(修補沒蓋到同一族)。修前與修後都是 rc0、`is_dir True`,第二次跑 `next1` 也仍是 `is_dir True`。

## F4 --feature 後面用空白接第二個功能時,第二個字被當成 run-id,其餘的參數直接丟掉
severity: minor
blocking: 否
file: `scripts/templates/android-e2e-run.sh:1058`(diff 行號,`run_id = rest[0]`)
失敗場景:`sh android-e2e-run.sh --feature login home extra` 的解析結果是 `PICK={'--feature':['login']}`、`rest=['home','extra']`、`run_id='home'`、`BAD=[]`。只跑 login,run-id 變成 home,extra 被靜默丟掉,沒有任何提示。說明寫的是 `--feature <功能>[,…]`,但用空白分隔是常見的誤用。
引句:「run_id = rest[0] if rest else time.strftime("e2e-%Y%m%d-%H%M%S")」
歸因:未判定。這是程式碼抽出來直接執行的結果:從兩版範本腳本各自抽出參數解析迴圈,用同一組 argv 執行,結果相同。這段解析在 8f613342 之後才新增,修補範圍內沒動過,所以不屬於修復回歸。

## 鏡頭一:其他已走過、沒發現問題的輸入
兩版各用臨時 clone 跑 `android-e2e select` 或 `macrobench --check-config`,結果相同。
- **--case 寫法**:`--case login`(沒有點)與 `--case a.b.c` 回 2,並列出對照表裡有的情境。`--case=-x` 回 2,報「不認得」,沒有噴出 argparse 的英文錯誤。
- **--feature 寫法**:`--feature ""` 回 2「沒挑到任何情境」。`--feature=login,`、`--feature " login "`、重複的 `--case` 都會去重或去掉頭尾空白,最後只跑一次。
- **路徑寫法**:`app/`、`./app/src/login`、`app/src/login/`、`" app "` 都合格,而且比對前會先正規化;`app/src/../x` 與 `app//src` 都擋。
- **對照表外的檔**:只改共用 flow `.maestro/shared.yaml` 時回 2,並點名那支檔;同時改到 login 時,共用 flow 列在 `unmatched` 提醒。這和 S23 一致。
- **只看程式碼的部分**:效能測試方法名的規則(第一個字是英數字、`_` 或 `.`,後面可以接 `#`)擋掉了所有會被 sh 展開的字元(`$`、空白、萬用字元、`~`、引號、分號);兩個 `{{TEST}}` 會一起被替換。記憶體情境名只收 `[A-Za-z0-9_-]`,拼成 `<run-id>.<情境>` 後跳不出產物目錄。cycles 是 0、字串或 bool 時會擋。

## 修補三問
① **修復效果有沒有行為證據**:修前 clone 換上修後的測試檔,和修後各跑一次。
- G1:args_and_names 在修前紅 5 條(反斜線、萬用字元、app_dirs 的 //、run-id history.jsonl,外加一條「只寫 .」的訊息用字),修後 16/16 綠。
- G3:修前 run_edges 裡「替身收集腳本有設但這次沒收記憶體時照寫紀錄」是紅的,修後 7/7 綠。
- G4:修前紅「run-id 不能佔本機總表的檔名」,修後綠,但大小寫變體沒擋到(見 F3)。
- G2:feature_record_rules 在修前就是 15/15 綠,修補差異裡也沒有改 `_e2e_keep_old`,所以這組只是補測試,沒有修前是紅的證據,修復效果未判定。
- G5:修前 run_edges 在跑到逾時那條之前就噴例外(找不到 e2e-records 目錄),修前結果未判定;修後綠。
- G6:輪數上限那條在修前就沒紅,屬於等價改寫,未判定。

② **正常、錯誤與相鄰路徑是否仍成立**:以下保留案例在兩版都綠。
- feature_record_trust 5/5
- full_scenarios_judged 4/4
- history_edges 7/7
- run_script 40/40
- perf_per_method 1/1
- t_android_memstab_collect_scenario 2/2
- config_strict 56/56

features_config 在修前紅 1 條,原因是錯誤訊息用字改了,行為本身一樣。相鄰路徑上有一處新的不一致,就是 F2 的 `./.`。

③ **新發現在修前、修後各是什麼結果**:F1 兩版相同,都失敗;F2 修前會擋、修後放行;F3 兩版相同,都失敗;F4 兩版相同,都失敗。

未驗範圍:monorepo(專案根不是 git 頂層)時 diff 與 ls-files 的路徑基準不同、淺 clone、檔名有空白或中文以及改名。這幾項只讀了程式碼(用了 `-z` 與 `--no-renames`),沒有實跑。兩個 run-id 互撞的情形(例如 `r1` 加情境 `login`,對上另一次的 `r1.login`)也只讀了程式碼,沒有實跑。我只跑了上面列出的測試子集,沒有跑全套。

## pitfalls manifest 判定
內建的 open( handle 題判為誤報。diff 裡沒有用 with 的 open( 有兩處,都是沒改動的上下文行:範本腳本 `gradle_modules` 的 `open(...).read()`,以及收集腳本的 `json.load(open(...))`。兩支都是跑完就結束的短命腳本,CPython 用完就回收,檔案控制代碼會立刻關掉。新寫的 `Steps.save` 有用 with。ruff 的舊帳照派工詞略過;併發類題目在這個 repo 判範圍外。

## 圖譜鏡頭
這次的 hook 沒附固定席節點(LUMOS-LENS 那段寫「這次沒附固定席節點」),依派工詞,備援段不逐條答。我另外核對了兩篇:
- 計劃 S23、S26 與〈資料怎麼流〉第 91 行:F1、F2 是程式違反這兩條條款。
- `Systems/android-stability-collector` 的 WHY 行(LUMOS_STABILITY_SCENARIO 蓋過的欄位與 E2E_SCENARIO_KEYS 相同):和程式一致。

鎖檔 `08273ea6….json.warming` 在檢查時已經不存在,所以沒有動它。臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/鏡頭3-邊界與輸入-opus` 與我產生的 6 個 gctl-run 現場已經用字面絕對路徑刪掉;其他會談留下的 gctl-run 目錄沒有碰。

在主線上開發時,--changed 會靜默漏挑已提交的功能,這一條要先修;另外修補把 `./.` 這種路徑寫法放行了,history.jsonl 的擋法也可以用大小寫繞過。
