severity: major

先講結論:有兩條是「同一件事出現第二種做法」(F1、F2),其餘是結構對、細節沒對齊。沒有鉤子直呼 lumos 內部函式的跨層:鉤子都走 `lint-new --worktree --json`(最後一行 JSON,同 `check-graph-sync.py:635` 讀 `impact --json` 的做法)與 `lint-new --record-stop-block` 這兩個 CLI 入口。

## ① 模組邊界

收工鉤子、工作樹模式、決策列、共用模組各落在對的層:

- 鉤子只做預篩、起點、擋停名額與子程序收尾。
- 判定與白名單都在主程式,帳也由主程式寫(鉤子不能匯入主程式,所以給了記帳入口)。
- 決策列放在 `cmd_impact` 的 `stack_questions_applicable` 那段(`scripts/lumos:66660`)之後,讀表、觸發字正規式、剝註解都用第三批的 `_kt_decision_table`、`_kt_trigger_re`、`_strip_c_comments(kotlin=True)`。這一點是對的。
- 帶狀態碼的 porcelain 解析收成 `_porcelain_v1_entries` 一份,三處舊解析改走它,這是在收斂,不是新增。

只有一條邊界細節不齊:

F5
引句:「if "kt-compose" in _stack_platform_excluded([rel_file], repo_root):」
severity: minor
blocking: 否
- 「這支檔是不是伺服端 Kotlin」改用題號 `kt-compose` 當代理去查排除集合。
- 同一組 Android 專屬判斷,既有常數 `_KT_SIT_QID`(`scripts/lumos:38277`)是直接用情境題自己的題號。
- 這裡把另一題的題號寫死一次。結構沒錯,但多了一個要跟題表同步的字面值。

## ② 命名與錯誤處理

退出碼與擋下格式都跟既有一致:

- 鉤子一律 rc0。
- 擋下用 `{"decision":"block","reason":…}`,與 `check-graph-sync.py:835` 同形。
- 標頭 `LUMOS-STOP-LINT:` 與既有 `LUMOS-STOP:`(`check-graph-sync.py:647`)同系。
- `lint-new` 的 rc 沿用 1/0/3/2,新旗標組合錯誤走 rc2。
- 登記點與 `bypass-ask-hook.py` 那批對得上:`HOOK_BUDGET`、`_GLOBAL_CLAUDE_HOOKS`、`_VENDORED_TREE_FILES`、`ANCHOR_FILES`、`enforcement_status` 的 Claude 與 Codex 兩列、`_KNOWN_GATES`。

不齊的一條:

F4
引句:「p.add_argument("--record-stop-block", dest="ln_record", help="只記帳:收工鉤子真的擋下後記一筆 stop-lint(配 --count、--prompt)")」
severity: minor
blocking: 否
- `lint-new` 的子指令說明還寫「不寫治理帳」(`scripts/lumos:76381` 一帶的 `add_parser("lint-new", …)`),`_LINT_NEW_CLI_RC` 上方註解也有同一句「★不寫治理帳★」。
- 這批在同一個指令下加了一個會寫帳的模式,說明文字沒改。
- 記帳入口掛在唯讀檢查指令的旗標下,命名上也和既有「寫帳的事用獨立動詞」不同,例如 `code-loop pass`、`canary record`。
- 結構可接受,只是文字與慣例不一致。

## ③ 第二種做法

F1
引句:「可信來源與逾時預算那兩段在別支鉤子(impact-hook 等)還有逐字相同的複本,漂移守衛逐字比對(t_trusted_lumos_rejects_untrusted_locations、」
severity: major
blocking: 是
- `_trusted_lumos` 與 `_outer_budget`、`_inner_budget` 現在有兩種共用做法並存。
  - 方式一:`impact-hook.py:294`、`lumos-entry-hook.py:214`、`dispatch-lens-hook.py:424`、`bypass-ask-hook.py:46` 等仍是「逐字複本加守衛」。
  - 方式二:`check-graph-sync.py:46` 與 `stop-lint-hook.py` 改成從 `_hookshared.py` 匯入。
- `_hookshared.py` 裡搬過去的註解還寫著「所以用複製加守衛而不是抽共用模組」,和它自己的存在互相矛盾。
- 守衛測試 `t_trusted_lumos_rejects_untrusted_locations`(`scripts/test_lumos.py:28795`)被放寬成「複本或匯入共用模組」兩種都過,等於把第二種做法正式化。
- 計劃說底線模組是既有唯一做法,但 `_hookevent.py` 共用的是事件寫入器,這批要共用的函式,既有決策正是「複本加守衛」。
- 要嘛全鉤子一起改成共用模組,要嘛新鉤子照舊用複本加守衛。

F2
引句:「n = re.sub(r"[^A-Za-z0-9_.-]", "_", str(s))[:120]」
severity: major
blocking: 是
- `stop-lint-hook.py` 的 `_name` 與 `_claim` 把 `check-graph-sync.py:677` 的 `_stop_mark_path` 消毒和 `_stop_mark_write` 的 O_EXCL 佔名額又寫了一份,而且放在 `stop-block` 同一個目錄、同一批標記檔。
- 這兩段沒被搬進 `_hookshared.py`,所以搬共用模組要避免的「邏輯抄一份、一邊改另一邊沒跟上」,在這裡原樣重現。
- 兩邊的消毒規則或長度上限一旦分家,同一會談的標記檔名會對不上。
- 該搬進 `_hookshared.py` 的是「標記檔名消毒」與「O_EXCL 佔名額」。

F3
引句:「return subprocess.run(["git", "--no-optional-locks", "-C", str(repo_root), "-c", "core.quotePath=false", *args],」
severity: minor
blocking: 否
- 主程式已有 `_lens_git`(`scripts/lumos:67614`,支援 `quote`、`binary`、`timeout`、`env`),相鄰的 `_tg_rb_pending`、`_handoff_files` 都走它。
- 新增的 `_lint_wt_git` 是同類的第三個 git 包裝。
- 它唯一多的是 stdin(`cat-file --batch` 用)與 `--no-optional-locks`;後者其實 `_lint_new_cli_worktree` 已設 `GIT_OPTIONAL_LOCKS=0` 涵蓋。

F6
引句:「n = sum(1 for tr in dict.fromkeys(r["triggers"]) if re.search(_kt_trigger_re(tr), body))」
severity: minor
blocking: 否
- `_kt_decision_rows` 自己逐列逐觸發字跑 `re.search`。
- 同一批觸發字比對在 `_kt_sit_rows_rx`(`scripts/lumos:39123`,每列合成一條預編譯樣式加首字預篩,註記是代碼審 r1 D9 的效能修正)已有現成做法。
- 沒重用它,等於另起一套比對。
- 單檔寫入內容通常很小,所以只算 minor。

F7
引句:「signal.signal(signal.SIGTERM, _lint_wt_on_term)」
severity: minor
blocking: 否
- ⚠ 交編排者判斷。
- 這是主程式第一個訊號處理器,patch 自己宣告是新慣例,說明記在 `Systems/hook逾時預算`。
- 收尾梯度在兩層各有一套:鉤子側 SIGTERM、寬限、再 SIGKILL;主程式側直接 SIGKILL。
- 主程式側有重用 `_kill_proc_group`(`scripts/lumos:26861`),方向對。
- 鉤子側的殺群組寫法與 `memory-sweep.py:936` 又是各寫一份,但鉤子不能匯入主程式,屬於「鉤子之間複本」那一類。
- 若採 F1 的任一方向,這條要連帶處理。

F8
引句:「out = {"status": "clean", "blocked": False, "mode": "block", "new": [], "waived": 0, "weak": 0, "oversize": [],」
severity: minor
blocking: 否
- `_lint_new_wt_verdict` 把 `_lint_new_verdict` 的整個結果 dict 骨架複製了一份,另外加 `skipped`、`wt_rejected`。
- 之後 `_lint_new_verdict` 加鍵時,這份要手動跟上。
- 較穩的做法是抽共用的骨架建構函式。

不對齊共 8 條,其中會擋的 2 條
