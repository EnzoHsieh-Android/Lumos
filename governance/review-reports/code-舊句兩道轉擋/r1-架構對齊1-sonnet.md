severity: minor

審查時 Bash 在後半段因磁碟滿(ENOSPC)不能用,最後兩個點只能靠 Read 對照,沒能 grep 全檔。這兩點在下面標了「未驗」。

## 三問

**1. 分層與依賴方向**
- 結構與鄰居一致。`_note_reread_judge`、`_note_reread_guarded`、`_note_reread_report`、`_note_reread_print`、`_note_reread_ledger` 這個拆法,照的是 `_drift_retire_guarded`、`_drift_retire_report`、`_drift_m1_guarded`(`scripts/lumos:39132`、`39165`、`40129`)。
- 讀判定紀錄走既有的 `_nodehome_cat_blobs_capped`(`scripts/lumos:29520`);單份超限時多問一次大小,走既有的 `_nodehome_cat_sizes`(`scripts/lumos:29501`)。沒有另寫 git 讀取。
- 判不了的提示重用 `_drift_unknown_hint`,只加了 `skip` 參數(`scripts/lumos:40422` 一帶),沒有複製一份。
- 回頭重讀呼叫漂移那邊的 `_drift_load_acks`、`_drift_reread_split_acked`,漂移的 ack 呼叫回頭重讀的 `_reread_*`。這個方向舊碼本來就有:`_note_reread_scan` 已經用 `_drift_empty_tree`。不算新的跨層。
- 有兩處是新寫的而且各自再做一遍:
  - 「讀掛鉤檔」那份(見 A5)。
  - 治理帳整行大小的處理(見 A4)。
- 未驗:`_reread_summary_entries` 的 docstring 說「再補 `_note_summary_entries` 那個單行 summary 的寫法」,看起來是把那段解析抄了一份,沒有呼叫它。沒能 grep 到 `_note_summary_entries` 的簽名,不確定回傳形狀能不能直接用,⚠ 交編排者。

**2. 命名與錯誤處理**
- 例外類別 `_NoteRereadArgErr(_NoteRereadStop)` 延續舊的 `_NoteRereadStop` 做法。`_note_reread_config` 的預設值常數 `_NOTE_REREAD_DEFAULT_GATE` 照 `_DRIFT_DEFAULT_GATE`(`scripts/lumos:35445`)。這兩處一致。
- 記帳的種類詞(`blocked` 且 `hard=True`、`skipped`、`none`、`covered`、`reminded`)沿用既有的,走 `_gate_event_or_warn`,沒有新增記帳格式。
- 不一致的有三處:函式名前綴(A1)、參數錯誤的措辭(A2)、判斷 CI 的方式(A3)。

**3. 第二種做法**
- `--gate` 是由呼叫端(掛鉤)決定要不要擋的旗標。專案裡已有同款先例:note-shape 的 `--slots`,說明寫「掛鉤帶這個參數才開擋」(`scripts/lumos:50754` 一帶)。所以這不是第二種做法。
- ⚠ 交編排者:專案裡「由呼叫端調鬆嚴」其實有兩個方向。`--slots`、`--gate` 是預設不擋、帶了才擋。`code-loop check --bound-tests-advisory` 與 `bound-tests --advisory` 是預設擋、帶了才放寬(`scripts/lumos:50896`、`50907`)。鄰居本身就不一致,我不硬判。
- ⚠ 交編排者:CI 的 reread-check 不帶 `--gate`,又接 `|| true`(`.github/workflows/ci.yml:264`),所以 CI 從不擋。同一份 CI 裡 `drift check` 那步是擋的(`.github/workflows/ci.yml:239`)。這是計劃裡 Enzo 2026-10-09 的裁定,不算引入新做法,但兩道閘的 CI 行為不同。
- `_DRIFT_FIX_HINT_TAIL` 把 c4、c6 兩個分支改成查表,其餘種類還是 if 串。這是同一個函式裡兩種寫法並存,但範圍很小,我只記在這裡,不列 finding。

## A1 新增的規則類輔助函式沒有 `_note_` 前綴
severity: minor
blocking: 否
引句:「def _reread_summary_entries(text):」
file: `scripts/lumos:34393`(同一段的 `_note_reread_show`)
file: `scripts/lumos:34665`(`_note_reread_config`)
- 既有:這一段的函式一律叫 `_note_reread_*`,漂移那邊的叫 `_drift_*`。
- 這次:新增 `_reread_summary_entries`、`_reread_rule_entry`、`_reread_row_match`、`_reread_note_hits` 四支。它們放在筆記內容審那一段,被漂移的 ack 共用。
- 不一致:前綴規則被打破,grep `_note_reread_` 找不到它們。docstring 說是照 `_path_special_chars` 的先例而去掉前綴,但那是通用字元工具,這四支是回頭重讀專用的。

## A2 參數錯誤(回傳碼 2)的措辭與流向跟 drift check、reread-prepare 不同
severity: minor
blocking: 否
引句:「print(f"回頭重讀提醒:這次沒提醒:{res['why']}", file=sys.stderr if gate else sys.stdout)」
file: `scripts/lumos:39102`(`cmd_drift_check` 的 `--push-remote` 與 `--pushed-ref` 檢查,印「擋下:…」回 2)
file: `scripts/lumos:34990`(`cmd_note_audit_reread_prepare` 同一個檢查,印「擋下:…」)
- 既有:參數錯一律「擋下:…」到標準錯誤、回 2。
- 這次:帶 `--gate` 時回 2,但印的是「這次沒提醒:…」。`_NoteRereadArgErr` 的 docstring 說「跟 drift check 對同一件事的處理一樣」,措辭其實不同。
- 不一致:回傳碼 2、文字卻說「沒提醒」。掛鉤端再補一句「上面如果印了擋下…」去圓。

## A3 同一個子指令裡判斷「是不是 CI」用了兩套條件
severity: minor
blocking: 否
引句:「and not (os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"))):」
file: `scripts/lumos:35263`(新加的判斷)
file: `scripts/lumos:35383`(同一支 reread-check 的帳 `src = "ci" if os.environ.get("CI") else "hook"`)
- 既有:帳裡用 `CI` 一個變數判斷來源。
- 這次:印「掛鉤沒帶 --gate」那段另外加了 `GITHUB_ACTIONS`。測試的 `_rr` 也跟著多清一個 `GITHUB_ACTIONS`。
- 不一致:同一支指令兩個 CI 判斷,日後行為會分岔。應收成一個小函式,或兩處用同一個條件。

## A4 回頭重讀「有東西」的那筆帳沒走 `_gate_event_fit`,rows 與 nodes 筆數也大很多
severity: minor
blocking: 否
引句:「nodes = list(dict.fromkeys([_note_reread_show(pre + r) for r in left] + [r["path"] for r in rows]))[:50]」
file: `scripts/lumos:40065`(`_drift_m1_fit`,轉呼叫共用的 `_gate_event_fit`)
file: `scripts/lumos:1560`(`_gate_event_fit` 的 docstring,說是舊句檢查帳與筆記形狀擋放寬帳共用)
- 既有:帶 rows 清單的帳先量整行,超過 4096 位元組就從尾端丟 rows 並記 `*_truncated`。m1 的 rows 只留 10 加 3 筆。
- 這次:第二層最多 50 筆 rows,每筆含路徑、80 字原文、紀錄指紋清單,再加最多 50 個 nodes,整筆直接寫,不量也不截。另外判不了的那筆帳用 `extra={"undecidable": True}` 這個布林,m1 的做法是 `state` 字串。
- 不一致:同類帳,鄰居有共用的截斷函式,這裡沒接。未驗:讀帳那一側碰到超過 4096 位元組的行會怎樣。

## A5 讀掛鉤檔的方式在 `enforcement_status` 一側又寫了一份,hooksPath 解析也複製了
severity: minor
blocking: 否
引句:「v = os.path.expanduser(hp) if hp else str(Path(".git") / "hooks")」
file: `scripts/lumos:21856`(`_hooks_path_is_ours`,docstring 寫「抽成共用,別留第二份實作」)
file: `scripts/lumos:40366`(doctor 用 `_lens_git show HEAD:scripts/hooks/pre-push` 加標記字串判有沒有接線)
- 既有:判斷 `core.hooksPath` 指向哪裡,集中在 `_hooks_path_is_ours`(expanduser、絕對或相對 root)。doctor 判「掛鉤有沒有接」是讀提交裡的檔,比對標記字串。
- 這次:`_enforcement_prepush_ungated` 自己把 expanduser、絕對或相對 root 的解析再寫一遍,直接讀工作目錄的檔,用「--gate 不在呼叫行」判斷。
- 不一致:「實際生效的那份」和「提交裡的那份」兩種讀法本身有理由(docstring 有講),但路徑解析應該從 `_hooks_path_is_ours` 抽出一支回目錄的共用函式。呼叫端只在 `ok` 為真時才進來,而 `ok` 已要求 `hp` 非空,所以 `.git/hooks` 那條退路走不到。

不對齊共 5 條,其中 major 0 條
