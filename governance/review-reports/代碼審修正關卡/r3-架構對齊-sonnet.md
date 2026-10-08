severity: major

# 代碼審修正關卡 第 3 輪:架構對齊-sonnet

對照的程式碼:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard 的 `scripts/lumos`(以下行號都是該檔)。

## F1 「一支測試的判法」沒有抽共用,而是第三次手抄規格閘的四步接線,還直呼規格閘四支私有函式
severity: major
blocking: 是
引句:「每支結果用 `_ran_count`、`_spec_gate_declared`(宣告集照規格閘拿放寬那份)、`_spec_gate_verdict` 判」
file: `scripts/lumos:6625`
file: `scripts/lumos:6672`
file: `scripts/lumos:38606`
1. 規格閘裡「`_run_bound_tests` 跑 → `_ran_count` 讀支數 → `_spec_gate_declared(放寬宣告集)` → `_spec_gate_verdict` 判」這段接線,現在已經有兩份:`_spec_gate_run_clauses`(6625-6648)與 `_spec_gate_regress`(6672-6690 附近的迴圈)。修正關卡要在綠樹、紅樹各接一次,等於第三、四份。
2. 這份計劃對 guard kill 的隔離工作樹有「先抽共用函式、兩邊都改用」的處理,對這段接線卻沒有:它是從 fix-check 直呼 `_spec_gate_declared`、`_spec_gate_verdict`、`_ran_count`、`_platform_test_index` 這幾支規格閘內部零件,自己重組一遍。〈PRIOR-ART〉寫「全部沿用 lumos 既有零件」,但沿用的是零件、不是那條接線,接線這份會跟規格閘漂移(正是計劃自己點名的「第 2 版自己重寫一份又把規格閘修過的誤擋帶回來」)。
3. 另一個接不上的點:計劃要求「每支測試的逾時取自己的逾時與剩下的時間較小的」,但 `_run_bound_tests` 的逾時只從環境變數 `LUMOS_TEST_TIMEOUT` 讀(38618),沒有參數。計劃沒寫要改 `_run_bound_tests` 簽名,也沒寫用改環境變數硬塞;不抽共用函式就沒有落腳處,最後多半是第二套「逾時從哪來」的做法。
4. 同層鄰居的做法對照:鄰居(`_spec_gate_regress`)是手抄,但那是既有債;新增第三份不是「跟鄰居一樣」,是在加重第二種做法。修法方向:抽一支「在某棵樹跑一批測試並逐支判紅綠弱」的共用函式(帶逾時參數),規格閘兩處與 fix-check 共用。
未實測,依據是讀碼。

## F2 「之後有沒有改程式」另寫一套比對,沒用代碼審留痕現成的判法,連定義都跟留痕對不上
severity: major
blocking: 是
引句:「事件的 `head_sha` 跟現在的 `HEAD` 之間沒有簿記檔以外的檔案改動(`git diff --no-renames --name-only -z`」
file: `scripts/lumos:39232`
file: `scripts/lumos:39269`
file: `scripts/lumos:6896`
1. 專案裡「記錄那版到現在,是不是只多了簿記」已經有現成的一支:`_codeloop_record_valid_ex(repo_root, rec_sha, marker_sha)`(39232-39276)。它處理了祖先關係、找不到提交(`_codeloop_missing_commit`)、`--raw` 看檔案模式,而且★簿記資料夾底下的程式檔不算簿記★(`_codeloop_bookkeeping_code`)。
2. 計劃在 `loop next` 提醒這裡自己寫 `git diff --no-renames --name-only -z` 加前綴比對,沒有這幾層。結果:改到 `governance/replay/` 或 `governance/review-reports/` 底下的程式(S8 條款明寫「含 `governance/` 底下的程式」要算改了),前綴比對會把它們當簿記,條款自己就做不出來。
3. 〈名詞〉說簿記檔是「代碼審留痕認定「改了不算改程式」的檔」,又「加圖譜筆記資料夾」。留痕那支(39269)只認 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS`,不豁免圖譜筆記;加筆記資料夾的是小改動閘的 `_bk`(6896)。所以計劃的定義是「小改動閘那套」,卻掛在留痕名下,S8 的「只改了圖譜筆記時不印」跟留痕的判法也不一致。
4. 現況是各處把 `f in _BOOKKEEPING_FILES or f.startswith(_BOOKKEEPING_DIRS)` 內聯(6896、28151、33326、33413),新增這一處又是一份內聯。至少要指明「提醒用 `_codeloop_record_valid_ex` 或抽出的共用判斷」,否則是第二種做法。
5. 次要:fix-check 的「主工作目錄有未提交改動」提醒要求 `git status --porcelain -z`、改名兩個路徑都看,專案已有 `_porcelain_z_paths`(38296 用到),計劃沒說沿用。
未實測,依據是讀碼。

## F3 `fix_check.link_dirs` 寫「照 `_lint_link_deps`」,但那支寫死目錄清單、沒有參數,等於另寫第二支連結函式
severity: major
blocking: 是
引句:「寫法照新增告警閘的 `_lint_link_deps`」
file: `scripts/lumos:23590`
file: `scripts/lumos:23630`
1. `_lint_link_deps(real_dir, snap_dir)` 內部迴圈走常數 `_LINT_DEP_DIRS = ("node_modules", ".venv", "venv")`(23590、23632),不收目錄清單;而且是「預設就連」。
2. 計劃要的是相反語意:預設不連、只連專案宣告的清單。直接呼叫它會多連 `node_modules`、`.venv`,正是計劃要避開的紅樹失真;所以只能「照它的寫法」另寫一支,等於同功能(把依賴資料夾用符號連結指回主工作目錄)兩套。
3. 沒有一句說明為什麼不給 `_lint_link_deps` 加一個目錄清單參數(新增告警閘傳 `_LINT_DEP_DIRS`、fix-check 傳 `link_dirs`)。計劃對隔離工作樹是抽共用,對這個卻沒有,同一份計劃內處理方式不一致。
未實測,依據是讀碼。

## F4 殘骸清理另起一套(標記檔+行程編號+`git worktree list` 比實際路徑+24 小時),沒提既有的 `_lint_new_clean_stale`
severity: major
blocking: 是
引句:「沒有標記檔的,資料夾修改時間超過 24 小時才清」
file: `scripts/lumos:23798`
file: `scripts/lumos:14202`
1. 專案已有一支同需求的殘骸清理:`_lint_new_clean_stale`(23798-23811)——開跑前掃同前綴、修改時間超過一天(`_LINT_NEW_STALE_SEC`)的暫存資料夾,理由寫的也是「強殺時收尾不會執行」。
2. 計劃的清理是新的一套:位置不同(系統暫存資料夾而非 `.lumos/`)、判準不同(標記檔+行程存活)、清法不同(`worktree remove`+`prune`)。其中「沒標記檔就看修改時間 24 小時」這條跟既有的是同一個判準、卻重寫了一個新常數。
3. 差異有部分正當理由(worktree 的登記要 prune、guard kill 目前根本沒有清理),但計劃整份沒提到既有那支,〈PRIOR-ART〉還寫「全部沿用」。⚠ 判不準:若編排者認為 worktree 登記讓它必須另寫,這條可降為 minor,條件是計劃要寫一句「為什麼不能擴充 `_lint_new_clean_stale`/共用它的時間常數」。
未實測,依據是讀碼。

## F5 設定讀取:類比對象選錯,`stress` 的 `timeout` 欄位沒帶單位後綴
severity: minor
blocking: 否
引句:「照 `_drift_config` 那類寫法:沒設定用預設、單一欄位讀不懂用預設並警告」
file: `scripts/lumos:23507`
file: `scripts/lumos:30808`
file: `scripts/lumos:23959`
1. `_drift_config` 吃的是「被檢查那一版的設定檔文字」、回 tuple;最像的鄰居是 `_lint_new_config(repo_root)`(23507-23539):直讀 `.lumos/config.json` 一個區塊、回 dict 帶 `warnings`、`budget_sec` 同名同單位(用在 23959、39750),驗法是「布林/非整數/小於 1 → 預設+警告」。計劃對 `budget_sec` 的規則大致同,但要明講「是否收浮點」,現在「不是數字」含糊。
2. 同一份計劃裡 `budget_sec` 帶 `_sec`、壓力指令卻寫 `{"cmd": "…", "timeout": 秒}`;鄰居 `_lint_new_config` 的單位後綴一律 `_sec`。結構對、命名小不一致。
3. `--record-template`(對照 41525 `--dispositions-template`)、kind `warned`/`passed`/`skipped-env`(對照 27018、9575、26889)、`secs` 欄名(38377)、`_KNOWN_GATES` 登記,都對得上鄰居,不列。
未實測,依據是讀碼。

## F6 `base_commit` 加進派工單,但沒說放在哪種形狀、哪一個檔,也沒沿用既有的派工單讀法
severity: minor
blocking: 否
引句:「派工單多一個欄位 `base_commit`(派工當下 `git rev-parse HEAD` 的 40 碼」
file: `scripts/lumos:11144`
file: `scripts/lumos:11541`
1. 派工單 `rN-dispatch*.json` 現有三種形狀(單席 dict、帶 `seats` 的 dict、頂層 list),且一輪常有多個檔;既有讀法 `_roster_dispatch_entries`(11144-11170)對形狀有容錯。計劃只說「多一個欄位」,`--record-template` 要從哪個檔、哪個形狀拿 `base_commit` 沒定,又會長出第二支讀派工單的函式。
2. 同份計劃裡修正紀錄用 `base`、派工單用 `base_commit`,治理帳用 `head_sha`,命名不統一(結構沒錯)。
3. 審查帳這邊也沒指名用 `_loop_records(env, loop_id, strict=True)`(11541,註解「單一讀法」)取載體席與「前一輪」,fix-check 與 `loop next` 若各自讀帳會分叉。
未實測,依據是讀碼。

## F7 整次執行改行程環境 `TMPDIR`、裝 SIGTERM 處理,專案裡沒有先例,也沒給既有的 `_kill_run` 傳環境的管道
severity: minor
blocking: 否
引句:「整次執行期間把行程環境的 `TMPDIR` 指到修正關卡自己的暫存資料夾」
file: `scripts/lumos:13976`
file: `scripts/lumos:37733`
1. 全檔只有一處寫 `os.environ`(253,重新執行用的 `LUMOS_REEXEC_PYTHON`);其他地方要給子行程環境是在 Popen 傳 `env=`(37733)。`_kill_run`(13976)沒有 `env` 參數,計劃卻用改整個行程環境的方式讓測試工具的暫存現場落在自己的資料夾。這是新做法,且影響同行程內其他呼叫(例如 `_bound_tests_check` 內部),計劃沒說會不會牽連。
2. SIGTERM 處理計劃自己承認是專案第一個,不算違規;但是它跟 `finally` 收工作樹的組合要跟 guard kill 共用函式同一處做,不要 fix-check 單獨裝。⚠ 判不準,交編排者。
未實測,依據是讀碼。

## F8 `lands_in` 少兩篇:改 `_kill_run` 行為會動到的合約測試閘與規格閘,沒列
severity: minor
blocking: 否
引句:「新開 [[Systems/代碼審修正關卡]] 寫指令本體、[[Systems/guard-kill]] 補共用工作樹函式」
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`
file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md`
1. 〈要同步的文件〉自己列了 [[Systems/bound-tests-gate]] 要補一句,但前言的 `lands_in` 只有四篇,沒有它;計劃還要改 `_kill_run` 的中斷行為,而 `_kill_run`/`_run_bound_tests` 出現在 `Systems/bound-tests-gate.md`、`Systems/規格閘.md`、`Systems/guard-kill.md` 三篇(grep 可見),`規格閘` 完全沒被提。
2. 其餘四篇的落點合理:`guard-kill`(共用工作樹函式)、`loop-convergence-recording`(`loop next` 提醒與 `gov` 讀端)、`finding-refute`(`regression_set` 欄位)、新開 `代碼審修正關卡`(指令本體)。
未實測,依據是讀碼。

---

**四問答覆(對應派工單)**
1. 分層與依賴方向:fix-check(指令層)往下呼叫 `_bound_tests_check`、`_run_bound_tests`、`_gate_event_or_warn`,方向跟鄰居一致;不一致在 F1(直呼規格閘私有零件而不抽共用)、F2(簿記/改程式判法不沿用留痕)、F3(連結函式不能直用)。
2. 命名與錯誤處理:`--record-template`、`budget_sec`、kind `warned`、`secs` 對得上鄰居;`link_dirs` 只在語意上跟 `_LINT_DEP_DIRS` 相反(F3);`base_commit` 與紀錄的 `base`、帳上的 `head_sha` 不統一(F6);`timeout` 缺單位後綴(F5)。`no_red_reason` 為專屬欄位,無鄰居可比。
3. 第二種做法:殘骸清理(F4)、「之後有沒有改程式」(F2)、依賴資料夾連結(F3)、一支測試的判法(F1)。設定讀取與樣板產生沒有第二種做法(新函式一道閘一支是既有慣例,`--record-template` 照 `--dispositions-template`)。SIGTERM 處理沒有先例可比。
4. 落點:四篇合理,但少 `bound-tests-gate`、`規格閘`(F8)。

不對齊共 8 條,其中 major 4 條。

最高等級:major,blocking 共 4 條
