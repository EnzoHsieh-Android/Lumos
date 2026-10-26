severity: minor

整體判斷:結構跟鄰居一致,沒有跨層直呼,也沒有另起一套的「第二種做法」。找到 4 條 minor 不對齊,其中 2 條判不準,標 ⚠ 交編排者。

我先查了鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/95ccb6780b8cb258cd901bc4674042037befe4b6167ffde5451cb70be66f732a.json.warming`,檔不存在,沒有要處理的鎖。

## 1. 分層與依賴方向

**對齊。**
- 判定本體 `_e2e_gate_evaluate` 的位置:file: `scripts/lumos:41703`。它對應安全證據的 `_secev_evaluate`(file: `scripts/lumos:10948`)。
- code-loop 那一道 `_codeloop_e2e_step`:file: `scripts/lumos:66156`。它對應 `_codeloop_security_step`(file: `scripts/lumos:66175`)。
- 兩邊都排在所有放行早退之前、不看 tier,並且都由 `_codeloop_guard_verdict` 呼叫(file: `scripts/lumos:65958` 起)。
- 結果都存在 `_codeloop_guard_verdict.last_*` 這類欄位,e2e 這邊是 `last_e2e`。
- 擋下類型的登記也跟著鄰居走:`_codeloop_kg_finish` 的明細鍵清單加了 `android_e2e`,pre-push 的 `pp_cl_reason` 加了 `android_e2e`。
- 判定內部呼叫的都是既有的下層工具,沒有自己繞過去直接做 git 或檔案操作:
  - `_secev_mainline`
  - `_secev_git`
  - `_secev_git_left`
  - `_secev_deadline_check`
  - `_nodehome_git`
  - `_nodehome_cat_sizes`
  - `_push_rev`
- 寫紀錄走 `_vault_write_lock` 和 `_repo_path_unsafe`,跟 lint-waive 同一套。
- 階段拆成 `_e2e_gate_resolve`、`_e2e_gate_uses`、`_e2e_gate_mainline` 等函式,跟 `_secev_stage_*` 的拆法一致。
- `_confirm_tty` 是在原函式上加 `stdin_timeout` 旗標,沿用同一個 `LUMOS_TTY_TIMEOUT`(file: `scripts/lumos:33576`)。這是重用,沒有另起一套。
- `_e2e_owner_index`、`_e2e_scope_hit`、`_e2e_scope_dirs` 把 `--changed`、算指紋、推送前判定原本各寫一份的範圍判斷收成單源。這比原本更整齊,方向正確。

## 2. 命名與錯誤處理

**大致對齊,有 3 條小差異。**
- 對齊的部分:
  - 判不清就擋,出錯和逾時都不 fail-open,代碼名沿用 `evaluation_timeout` 和 `evaluation_error`(file: `scripts/lumos:41710`、`scripts/lumos:41720`)。
  - 逾時預算 `E2E_GATE_BUDGET_SEC` 直接取自 `_SECEV_BUDGET_SEC`(file: `scripts/lumos:8527`)。
  - 治理帳事件走「`_gate_event_fit` 再 `_gate_event_or_warn`」的雙呼叫,跟 note-shape 同形(file: `scripts/lumos:46583`)。
  - 閘名 `android-e2e` 已登記在 `_KNOWN_GATES`。
  - 環境變數出口 `LUMOS_SKIP_ANDROID_E2E=1` 比照 `LUMOS_SKIP_NOTE_SHAPE=1`。
  - 擋下訊息是三段式。
  - 寫紀錄時把 `WriteBlocked` 轉成回傳錯誤字串,比照鄰居。

1. 提早結束的控制流程不同。
   - 鄰居的提早結束是「階段函式回傳 done,呼叫端判斷非空就收尾」:file: `scripts/lumos:11317-11321`。
   - 本 diff 的 `_E2eGateStop` 是用例外帶結果,連成功路徑也用(`_e2e_gate_done("pass")`、`("none")`、`("not-required")`)。
   - 全檔沒有別的「例外帶出結果」的類別,這是新的寫法。結構上仍是同一組階段拆分,所以判 minor。
   - 引句:「class _E2eGateStop(Exception):」
   - file: `scripts/lumos:41311`
severity: minor
   - blocking: 否

2. 判定結果的代碼欄位名稱跟鄰居不同。
   - 安全證據的 rep 用 `gate_code` 和 `gate_detail`(file: `scripts/lumos:10754`、`scripts/lumos:10774`)。
   - e2e 的結果 dict 用 `code`,治理帳 `extra` 也是 `code`(file: `scripts/lumos:41710`、`scripts/lumos:66156` 起的 `_codeloop_e2e_step`)。
   - 安全證據的逾時訊息會寫「判到哪一階段」,e2e 的沒有階段名。
   - 只是命名和訊息資訊量的差別,結構不變。
   - 引句:「code="evaluation_timeout")」
   - file: `scripts/lumos:41710`
severity: minor
   - blocking: 否

## 3. 第二種做法

- **`_confirm_tty` 的 `stdin_timeout`**:對齊。它是同一個函式加旗標,重用同一個環境變數 `LUMOS_TTY_TIMEOUT`,只是把 `_confirm_tty_timeout`、`_confirm_tty_stdin`、`_confirm_tty_dev` 拆成小函式。
- **`_e2e_owner_index`**:對齊。它是 `--changed`、推送前判定、涵蓋報告共用的單源,沒有另起一套。
- **`_e2e_record_files` 的 lstat 加 S_ISREG**:對齊。這跟 `_write_refusal_reason` 的 lstat 加 S_ISREG 是同一種寫法(file: `scripts/lumos:28414-28425`)。
- **`E2E_RECORD_SCAN_MAX` 與 `E2E_RECORD_FILE_MAX`**:對齊。這兩個常數放在 e2e 區塊,跟 `_SECEV_FILE_MAX`、`_VAULT_SAFE_FILE_MAX` 一樣每個領域各有自己的常數。

不對齊的 2 條:

3. ⚠ 開場掛鉤的複本做法跟 ci-status-hook 不同。
   - 鄰居的做法是同名、逐字複本,加一個比對原文相同的測試。例如 file: `scripts/hooks/claude/ci-status-hook.py:48` 寫「逐字複本」,對應測試 `t_ci_latest_attempts_copies_identical`(file: `scripts/test_lumos.py:36839`)。
   - 這份 diff 的複本改了名字:掛鉤的 `_e2e_ai_pending_rec`(file: `scripts/hooks/claude/lumos-entry-hook.py:280`)對 lumos 的 `_e2e_ai_pending_one`(file: `scripts/lumos:41788`)。
   - 內容也是改寫過的,不是逐字相同。
   - 目錄掃描(`_e2e_ai_line`,file: `scripts/hooks/claude/lumos-entry-hook.py:288`)是另外重寫的一份,不是 `_e2e_record_files` 的複本。
   - 兩邊一致只靠行為測試 `t_android_e2e_ai_count_copies_agree`(file: `scripts/test_lumos.py:19958`)。這個測試只對有限的樣本檢查筆數,檢查不到兩邊程式碼本身的漂移。
   - 判成 minor 的理由:「複本加一致性測試」這個做法本身有沿用,掛鉤不能 import lumos 也是實情。
   - ⚠ 判不準的地方:改寫過的複本算不算另一種做法,請編排者定。
   - 引句:「def _e2e_ai_pending_rec(rec, name):」
   - file: `scripts/hooks/claude/lumos-entry-hook.py:280`
severity: minor
   - blocking: 否

4. ⚠ 測試接縫環境變數 `LUMOS_E2E_GATE_BUDGET` 讓正式程式碼多讀一個環境變數。
   - 安全證據的逾時測試是在行程內改模組常數 `_SECEV_BUDGET_SEC`(S60,file: `scripts/test_lumos.py:112249-112250`),或傳 `budget=` 參數。正式程式碼本身不讀環境變數。
   - 本 diff 同時有 `budget` 參數和 `LUMOS_E2E_GATE_BUDGET`(file: `scripts/lumos:41319` 的 `_e2e_env_secs`,以及 `scripts/lumos:41703` 的 `_e2e_gate_evaluate` 內)。
   - 另外 `E2E_GATE_BUDGET_SEC = _SECEV_BUDGET_SEC` 在載入時就複製了數值,所以 S60 那種改模組常數的接縫對 e2e 不起作用。
   - 專案裡有先例:`LUMOS_TTY_TIMEOUT` 這類測試接縫,而且 `_e2e_env_secs` 的註解也寫了「同 `LUMOS_TTY_TIMEOUT` 的做法」。
   - 這個變數不是用來關掉閘門,只是調預算,所以判 minor。
   - ⚠ 判不準的地方:「閘級預算」用環境變數而不用常數或參數,算不算另一種做法,請編排者定。
   - 引句:「b = _e2e_env_secs("LUMOS_E2E_GATE_BUDGET", E2E_GATE_BUDGET_SEC) if budget is None else budget」
   - file: `scripts/lumos:41703`
severity: minor
   - blocking: 否

另外值得留意但不算不對齊:`_e2e_record_files` 只用 lstat 的大小預檢,後面 `_e2e_load_json` 仍是 `read_text`(file: `scripts/lumos:40777`)。專案有「有界讀的唯一一份」`_read_fd_capped`(file: `scripts/lumos:1682`),這邊沒用。這是邊界或資源面的議題,不是架構一致與否的議題。這個預檢只擋得住 lstat 時大小已超標的檔,不擋讀的當下才變大的檔。

不對齊共 4 條,其中擋實作的 0 條
