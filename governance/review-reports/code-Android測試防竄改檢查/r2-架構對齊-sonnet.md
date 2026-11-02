severity: major

對照基準是凍結版本 `ea1e0b8a6`,下面的行號都是這一版的。

## 一、分層與依賴方向

結論:這一輪沒有讓判定函式直接寫帳,也沒有繞過共用的 git 讀取函式。不對齊只有 A1(括號配對)和 A2(CI 區塊),都屬於第二種做法,放在第三節。

- **寫帳留在外層**:`_lint_new_verdict`、`_lint_new_off`、`_lint_new_guard_new`、`_tg_*` 都沒有呼叫 `_gate_event*`。要寫的帳放進 `out["events"]`,由 `_codeloop_lint_new_step` 寫(`scripts/lumos:69220` 附近)。
- **git 讀取走共用函式**:`_tg_retry_ok` 從 `_lens_git` 改成 `_lens_git_dl`(`scripts/lumos:49033`),`_tg_start` 把 `deadline` 傳進 `_lens_default_base`(`scripts/lumos:64197`),都是 r1 的修法。
- **新程式沒有自己開 git 子程序**,`_tg_build_cands` 的快取只是把「查過一次」記在 dict 裡。
- **工具層沒有反過來依賴印訊息層**:唯一的疑點是 `_tg_cand` 呼叫 `_esc_clean`,見 A3。`_esc_clean` 是全域字串工具,不是印訊息函式。
- **觀察,不算不對齊**:`_waive_origin_tty` 放在新增告警閘那一節(`scripts/lumos:37879`),Android 端到端驗收(`scripts/lumos:42959`)反過來呼叫它。放在 `_confirm_tty`(`scripts/lumos:33647`)旁會更中立。
- **截止時間做法有先例**:`_lint_new_verdict` 的 `tools_deadline = deadline + (monotonic() - t_guard)` 跟 `scripts/lumos:68961` 同型,不是新做法。

## 二、命名與錯誤處理

- **命名跟鄰居一致**:新函式的前綴跟各自那一區相同(`_tg_class_has_body`、`_tg_tautology`、`_tg_pair_key`、`_tg_ci_blocks`、`_rg_bracket_map`、`_strip_tok_parts`、`_strip_fill`)。`_lint_new_off`、`_lint_new_guard_new` 這輪沒有改名,跟 `_lint_new_*` 一排。
- **`_waive_origin_tty` 沒有改變 Android 端到端驗收原本的行為**:
  - 對照原版,Ctrl-C 訊息「\n沒放行(按了 Ctrl-C)。」、答 n 的訊息「沒放行(終端答的不是 y)。」、rc 1、`by = "human"/"ai"` 的判法逐字相同。
  - 三值判斷現在只剩一份。
- **訊息格式**:
  - 新增的「提醒:作弊比對沒跑完」每行都以「提醒:」開頭。
  - 放行檔壞掉那條補上了獨立一行的指令,r1 的 A3 已補。
- 其餘不一致見 A3 到 A8,都是 minor。

## 三、第二種做法

上一輪被點名的四處,結果如下:

- **yml 註解剝除:真的改成用既有的一支。** `_tg_yaml_uncomment` 刪掉,`_tg_ci_lines` 改呼叫 `_ci_strip_comment`(`scripts/lumos:48847`、`58143`)。
- **剝註解的字串判斷:真的合併。** `_strip_c_comments` 的 `_one` 現在只經過 `_strip_tok_parts` 與 `_strip_fill`,`('"""', "'''", '@"')` 的判斷只剩一份(`scripts/lumos:6765-6800`)。我逐一對過原本不等長的路徑,輸出沒有變。
- **放行三值判斷:真的收成一支。** 見上一節。
- **括號配對:沒有真的合併,只是換名字搬位置。** 見 A1。

### A1 括號配對仍是兩份各自維護的實作,只改名、搬到 `_rg_*` 前綴 ⚠
severity: major
blocking: 是 — r1 的 A5 要求「放在 `_rg_balanced` 旁並共用同一套配對邏輯」,這輪只做了改名和 docstring 互相指,配對規則在兩個函式本體裡各寫一次
引句:「剝過的文字一趟算出所有左括號的對應右括號 → {開: 關}(配對規則同 _rg_balanced:不分括號種類、只看深度)。」
file: `scripts/lumos:47632`(`_rg_balanced`:逐次掃描版;找不到回 `len(s)`)
file: `scripts/lumos:48043`(`_rg_bracket_map`:建表版,離 `_rg_balanced` 約 400 行;找不到是表裡沒有這個鍵)
說明:
- 兩支現在共用 `_RG_OPEN`、`_RG_CLOSE`,但各自維護一份深度計法。「兩者等價」只寫在 docstring 裡,沒有任何一支呼叫另一支,也沒有測試綁住。
- 「找不到」有兩種回報方式:`len(s)` 與缺鍵。呼叫端各自補預設值(例如 `bmap.get(j, n - 1)`、`br.get(opener, opener)`),以後兩邊行為分岔時不會有人發現。
- `_tg_functions`、`_tg_statements`、`_tg_catch_no_fail`、`_tg_class_at` 走建表版,`_rg_methods` 一帶走逐次版,同一條路徑仍跨兩套。
- 效能理由(避免深巢狀變平方級)成立,所以我標 ⚠ 交編排者裁。
  - 若接受建表版:讓 `_rg_balanced` 的實作直接用 `_rg_bracket_map` 的同一段配對邏輯,或把兩者放在一起並綁一支等價測試。
  - 若不接受:`_tg_*` 全改回呼叫 `_rg_balanced`。

### A2 CI 區塊的「所屬區塊開頭」有兩種算法並存
severity: minor
blocking: 否 — 兩支都在新功能內,專案裡沒有現成的可用;只是同一函式裡同一個定義算了兩次
引句:「它所屬區塊(縮排比它淺的最近一行開頭、到下一個同層)裡有沒有呼叫 Gradle 的行。用堆疊一趟算完,跟行數成正比。」
file: `scripts/lumos:48906`(`_tg_ci_head`:同一個「縮排比它淺的最近一行」,仍用逐行往回掃,同一個 `_tg_ci_hits` 迴圈裡每次命中都呼叫)
file: `scripts/lumos:58143` 一帶的 `_ci_jobs_calling_without_full_history`(專案裡另一處以縮排切 CI 區塊的做法,只認 GitHub 的 jobs 層,不能直接用)
說明:
- `_tg_ci_blocks` 內部算出的 `parent[]` 就是 `_tg_ci_head` 要的開頭索引,但沒有被共用。
- 以後縮排規則(例如 tab、續行)改一邊,另一邊會漏。

### A3 擋下訊息的外來文字用 `_esc_clean`,而且清在候選建構時,跟鄰居的單一出口不同
severity: minor
blocking: 否 — 用的是既有清洗函式,只是挑的不是專為「擋下訊息與判定結果裡的檔名」寫的那一支
引句:「file = _esc_clean(file, 500)」
file: `scripts/lumos:19408`(`_out_clean`:docstring 寫明專管「擋下訊息與判定結果裡的外來文字(…檔名)」,另清 U+2028/2029、方向標記、BOM,並拆開 pre-push 記逃逸帳的兩串字)
file: `scripts/lumos:47521`(Room 守衛在印出的當下才 `_esc_clean`,不改候選資料本身)
說明:
- `_tg_cand` 自己的 docstring 說「擋下訊息是給 AI 讀的」,這正是 `_out_clean` 的用途。
- 在資料建構時清,會連 `--json` 輸出和指紋的檔名部分一起改;Room 守衛則只在印的時候清。
- 這樣做是有意的(指紋用清過的檔名),但跟鄰居的位置不同,值得編排者確認。

### A4 新欄位 `autopass_reason` 有兩個寫入點,且沒進初始 dict 與 docstring
severity: minor
blocking: 否 — 行為可用,只是跟同一個 dict 其他欄位的宣告方式不一致
引句:「out.setdefault("autopass_reason", "%d 條命令跑不出可解析的結果(工具沒裝/逾時/拉不到規則)" % len(env_undone))」
file: `scripts/lumos:38984`(`_lint_new_verdict` 在 `_lint_new_classify` 前直接賦值 `out["autopass_reason"] = out["reason"]`)
file: `scripts/lumos:38933`(`out` 初始 dict 其他鍵都先宣告;docstring 回傳欄位清單也沒補這一鍵)
說明:
- 判定函式裡同一個鍵一處用賦值、一處用 `setdefault`,靠呼叫順序才不互蓋。
- 鄰居慣例是先在初始 dict 宣告再填。

### A5 同一筆放行紀錄裡,時間格式一帶時區、一不帶
severity: minor
blocking: 否 — 只動了 r1 點名的 `acked_at`,同筆紀錄的 `ts` 仍是舊格式
引句:「who, now = _e2e_who(repo_root), _e2e_now()      # 標看過的人與時間照 Android 端到端驗收的寫法(帶時區)」
file: `scripts/lumos:38833`(`_lint_waivers_add` 的 `"ts": _time.strftime("%Y-%m-%dT%H:%M:%S")`,不帶時區)
file: `scripts/lumos:41559`(`_e2e_now`:`astimezone().isoformat(timespec="seconds")`)
說明:同一個 JSON 項目裡 `ts` 是本地無時區字串,`acked_at` 是帶時區的 ISO 字串。

### A6 「沒宣告檢查工具」的判斷在判定函式與 `_lint_new_tools` 各寫一份
severity: minor
blocking: 否 — 只是小段重複,訊息也不同
引句:「if not (_lint_load_config(repo_root) or _lint_deps_load(repo_root)[0]):」
file: `scripts/lumos:39071`(`_lint_new_tools`:`if not lint_cfg and not _dep_probe:`,同一個條件,訊息文字不同)
說明:兩處條件靠人記得同步,可以抽成一支小函式。

### A7 放行檔路徑寫死在指令裡,沒用既有常數
severity: minor
blocking: 否 — 現在路徑一致,只是改常數時會漏
引句:「print("    python3 -m json.tool .lumos/lint-waivers.json", file=sys.stderr)」
file: `scripts/lumos:38396`(`_LINT_NEW_WAIVERS_REL`)
file: `scripts/lumos:37940`(同一組放行指令的成功訊息用 `{_LINT_NEW_WAIVERS_REL}`)
說明:同一個放行檔,別處都引用常數,這一行寫死字串。

### A8 `_tg_retry_ok` 仍用 `git grep -E` 並重寫一份 `_TG_SET` 句式(r1 A1 後半未處理)
severity: minor
blocking: 否 — 截止時間已串好;正規式方言的部分沒變
引句:「r = _lens_git_dl(root, "grep", "-l", "-E", r"failOnPassedAfterRetry([[:space:]]*=[[:space:]]*|[[:space:]]+|\.set\([[:space:]]*|\([[:space:]]*)true",」
file: `scripts/lumos:47764`(`_rg_grep`:用 `-F` 粗篩,精確比對在 Python,註明「git grep 的正規式方言各平台不同」)
file: `scripts/lumos:48750`(`_TG_BUILD_RES` 同一個 `failOnPassedAfterRetry` 句式用 Python 的 `_TG_SET`)
說明:同一個設定寫法在 Python 與 POSIX 正規式各有一份,改一邊另一邊會漏。

不對齊共 8 條,其中 major 1 條
