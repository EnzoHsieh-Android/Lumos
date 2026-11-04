severity: major

我對照的是 HEAD `ce5256bdd`(含本 patch)。行號引的是這個版本。

## 一、分層與依賴方向

判定函式沒有寫帳,這點跟既有慣例一致。`_lint_new_verdict`、`_lint_new_guard`、`_lint_new_off`、`_lint_new_relax`、`cmd_test_guard` 全都不呼叫 `_gate_event*`。要寫的帳放進 `out["events"]`,由 `_codeloop_lint_new_step`(`scripts/lumos:69059`)寫,種類字串也和 Room 守衛一致(skipped / skipped-env / warned,見 `scripts/lumos:48266`)。`_lint_new_verdict` 只有這一個呼叫者,沒有別的路徑會漏寫帳。

讀 git 沒有自己開子程序。新碼用的都是共用函式:`_lens_git_dl`、`_lens_git`、`_nodehome_cat_sizes`、`_nodehome_cat_blobs_capped(sizes=)`、`_nodehome_reader(from_git=True)`、`_lens_default_base`、`_lens_full_sha`。這跟 Room 守衛的依賴方向相同。

AI 放行的「還沒看過」只有一個判斷函式 `_lint_waiver_ai_unacked`,健檢、`--list`、`--ack` 和推送前提醒都用它。這跟 e2e 的 `_e2e_ai_pending_one` 一樣是單源。

### A1 git 讀取沒串截止時間,另寫一支 git grep 與起點包裝
severity: minor
blocking: 否 — 結構是對的(走共用的 `_lens_git`),只是沒用 `_lens_git_dl` 把截止時間串進去,也沒用鄰居已有的寫法
引句:「r = _lens_git(root, "grep", "-l", "-E", r"failOnPassedAfterRetry([[:space:]]*=[[:space:]]*|[[:space:]]+|\.set\([[:space:]]*|\([[:space:]]*)true",」
file: `scripts/lumos:47750`(`_rg_grep`:鄰居的 git grep 包裝,註明「git grep 的正規式方言各平台不同」所以用 `-F` 粗篩,精確比對放在 Python)
file: `scripts/lumos:63622`(`_lens_git_dl`:同一份 diff 裡的 `_tg_changes` 已經用它)
說明:
- `_tg_retry_ok` 用 `-E` 加 POSIX 字元類,跟鄰居的 `-F` 粗篩加 Python 精比做法不同。
- `_tg_build_cands` 到 `_tg_retry_ok` 這一路沒有傳 `deadline`。同一個 `_tg_analyze` 上面卻是帶 deadline 的,所以預算用完時這一步還是可以多跑 20 秒。
- `_tg_start` 的 `_lens_default_base(root, tip=head, include_local=True)` 也沒傳 deadline。它跟 `_rg_fork_point` 沒有 push 時的分支(`scripts/lumos:47816`)是同一個呼叫,另包了一層。
- 起點改由主線分岔點算,而不是用 `_note_audit_start` / `_push_range_start` 的共用算法。這跟 Room 的 `fork or start` 同型,計劃也明寫了。我只提醒,不算違規。

## 二、命名與錯誤處理

這些跟鄰居一致:
- 函式前綴 `_tg_` / `_TG_` 沒有跟既有名字撞。
- 指令入口 `cmd_test_guard`、旗標 `--diff` / `--repo` / `--json`、參數錯誤的「擋下:」文字和 rc 2,都照 Room 守衛。
- 放行提醒行都以「提醒:」開頭,符合 pre-push 只轉印含「提醒」字樣的行的規則。
- 單次出口 `LUMOS_SKIP_LINT_NEW=1 git push` 獨立成一行。

### A2 ⚠ 判不了時的處理跟鄰居不一致,但鄰居本身就分兩派
severity: minor
blocking: 否 — 錯誤處理方式跟某些鄰居不同,結構沒壞
引句:「g["error"] = f"比對工具出錯({e.__class__.__name__}:{str(e)[:80]})"」
file: `scripts/lumos:69059`(`_codeloop_lint_new_step`:同一道閘的工具那一半,例外走 `_gate_failopen` 放行,見 `scripts/lumos:69067`)
file: `scripts/lumos:48294`(`cmd_room_guard`:git 算不出來 rc0 加記 skipped)
file: `scripts/lumos:42702`(e2e:判定內部出錯就擋)
說明:
- 新的作弊比對例外記成沒跑完並擋,跟 e2e 一致,但跟同一道閘工具那一半的 fail-open 不同。現在同一道 lint-new 閘裡有兩種出錯策略。
- `cmd_test_guard` 在 git 算不出改動時回 rc 2(`if cands is None: ... return 2`)。Room 守衛和筆記形狀擋是「判不了一律講一句、rc0」。
- 計劃和 docstring 已說明是刻意的(Android 端到端驗收否決過「出錯就放行」)。兩派都有既有先例,我不硬判,請編排者裁。

### A3 放行檔壞掉時的擋下訊息缺「指令獨立一行」
severity: minor
blocking: 否 — 擋下訊息的三段式缺了最後一段,不影響判定
引句:「print(f"接下來:{_lv['waiver_err']}——先修好它(現在放行一定失敗),再重推。", file=sys.stderr)」
file: `scripts/lumos:48266`(`_rg_report`:發生什麼、為何在意、`LUMOS_SKIP_ROOM_GUARD=1 git push` 獨立一行)
說明:
- 這個分支寫完就 `return`,沒有指令行。別的擋下路徑都有。
- 其他分支(一般新增告警、作弊比對本身壞掉)都有獨立指令行,只有這一條沒有。
- 建議補一行檢視放行檔的指令。

## 三、第二種做法

計劃要求「擴充原處」的三處都確實在原處改:`_strip_c_comments` 加 `keep_length`、`_rg_methods`(原有 `kinds` 參數)、`_rg_split_args` 加 `angle`,掃描本體 `_C_STRIP_PAT` 仍只有一份。`_rg_method_end` 和 `_rg_annotations` 也是改原函式。`_lint_new_kind_counts` 是把 `_lint_new_autopass_count` 原處擴充,舊函式留成包裝。讀 git、確認終端分別用了 `_lens_git_dl` / `_nodehome_cat_blobs_capped` 和 `_confirm_tty`,沒有另寫。

### A4 另寫一套 YAML 行尾註解剝除,既有的 `_ci_strip_comment` 就是同功能
severity: major
blocking: 是 — 專案裡已有同功能的函式,新碼另寫了一份(引入第二種做法)
引句:「yml 一行 → 拿掉行尾註解(前面有空白的 #,而且不在單、雙引號裡)。」
file: `scripts/lumos:57992`(`_ci_strip_comment`:切掉不在引號裡的行尾註解,邏輯逐行相同)
說明:
- `_tg_yaml_uncomment` 的邏輯跟 `_ci_strip_comment` 幾乎逐行相同,只差 `i == 0 or ...` 與沒有 `.rstrip()`。
- `_ci_workflow_texts` 的 docstring 寫明「哪些算註解只有一份」,那是之前審查要求收斂過的。
- 新增這份等於重開兩份。
- 建議 `_tg_ci_lines` 直接呼叫 `_ci_strip_comment`,必要時在呼叫端補 `i == 0` 或 rstrip。

### A5 另寫一套括號配對,既有的 `_rg_balanced` 就是同功能
severity: major
blocking: 是 — 專案已有 `_rg_balanced`,新碼另寫了一支同用途的配對(引入第二種做法)
引句:「剝過的文字一趟算出所有 ( [ { 的對應位置 → {開: 關}。」
file: `scripts/lumos:47619`(`_rg_balanced`:`s[i]` 是左括號就回對應右括號,找不到回 `len(s)`)
說明:
- `_tg_brackets` 的字元集和深度計法跟 `_rg_balanced` 相同,是另一個實作。理由是效能:一趟建表,避免深巢狀時平方級。
- 同一條 `_tg_functions` 路徑會同時走兩套配對:`_rg_methods` 內部用 `_rg_balanced`,後面用 `_tg_brackets`。
- 這理由成立,但按錨點判法仍是第二種做法。
- 若編排者接受「建表版」,建議把它放在 `_rg_balanced` 旁,並讓兩者共用同一套配對邏輯,而不是兩份各自維護。

### A6 剝註解的逐字元處理另開一支函式,跟 `_one` 內的判斷平行
severity: minor
blocking: 否 — 掃描本體(`_C_STRIP_PAT`)仍只有一份,重複的是逐 token 的分支判斷
引句:「def _strip_same_length(tok, blank_strings):」
file: `scripts/lumos:6782`(`_strip_c_comments` 的 `_one`:同一組 `('"""', "'''", '@"')` 判斷與 `tok[0]` 分支)
說明:
- `_strip_same_length` 重做了一次「這個 token 是註解、哪一種字串、引號怎麼留」的判斷,包括 `@"` 的特例。
- 以後 `_C_STRIP_PAT` 若新增字串語法,要改兩處。
- 可以把「換成等長空白」做成 `_one` 裡的一個小分支。

### A7 放行與標看過照搬 e2e,但沒共用,細節也有出入
severity: minor
blocking: 否 — 計劃本來就寫「照搬判法」,結構是對的(用 `_confirm_tty`、`_vault_write_lock`、`_write_lf`、`_e2e_who`),只是細節和鄰居不一致
引句:「if len(re.sub(r"\s", "", note or "")) < 10 or not re.search(r"[^\W_]", note or ""):」
file: `scripts/lumos:42923`(`_e2e_waive_cmd`:理由只要求去空白後至少 10 字)
file: `scripts/lumos:42878`(`_e2e_ack_write`:`acked_at` 用 `_e2e_now()`,有時區)
file: `scripts/lumos:41543`(`_e2e_now`)
說明:
- 三值判斷(True 為 human、None 為 ai、False 為不放行)在 `_lint_waive_origin` 與 `_e2e_waive_cmd` 各寫了一份,`_lint_waive_ack` 又複製一次確認流程。
- 同樣是放行指令,理由規則卻不同:lint 多了「要有實字」,e2e 沒有。
- 標看過時 `acked_at` 在 lint 側用不帶時區的 `strftime`,e2e 側是帶時區的 isoformat。`acked_by` 取 git `user.name`,而同一指令的 `by` 取環境變數 `USER`。
- 欄位名也不同:e2e 用 `by` 當 human/ai,lint 因為 `by` 已經是使用者名,另加 `origin`。這個差異是被迫的,但兩邊的資料格式要分開處理。
- 建議把三值判斷抽成共用小函式,並統一理由規則與時間格式。

不對齊共 7 條,其中 major 2 條
