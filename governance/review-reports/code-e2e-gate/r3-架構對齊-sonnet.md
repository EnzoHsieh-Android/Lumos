severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/ffc2278705dcf274fe30415c639d59de1d642ac74bc0edfc9724880918638f14.json.warming` 查過,已不存在,所以沒動它。本輪只審程式與測試的對齊,文件筆記沒逐條讀。

**1. 分層與依賴方向:對齊**
- 新碼都在原本的層,沒有跨層直呼。判定本體 `_e2e_gate_evaluate` 由 `_codeloop_e2e_step` 呼叫,形狀跟 `_codeloop_security_step` 一樣,先跑判定、把結果放進 `last_e2e`、再記治理帳。對照:`scripts/lumos:66203`、`scripts/lumos:11060`。
- `_e2e_waive_commit` 放在 waive 區,呼叫的 `_nodehome_git` 和 `_esc_clean` 跟同區的 `_e2e_who`、`_e2e_head_fp` 一樣。解析提交編號的寫法跟已有的 `_e2e_head_fp` 同一種(`rev-parse ^{commit}`),不另起一套。對照:`scripts/lumos:41916`、`scripts/lumos:41973`。同一道判定裡的 `_push_rev` 要帶截止時間,放行指令沒有截止時間,所以不用它。
- `_gate_event_fit` 多一個 `ref` 參數,是為了讓「量的那一行」和「寫的那一行」相同,延續函式說明裡「★量的跟寫的是同一行★」那條。對照:`scripts/lumos:1869`。
- `_e2e_owner_index` 和 `_e2e_owners` 改成前綴查表,仍是單一函式,由 `--changed`、推送前判定和涵蓋報告三處共用。測試 `t_android_e2e_owner_index` 逐筆對照舊語意。對照:`scripts/lumos:40621`、`scripts/test_lumos.py:20569`。

**2. 命名與錯誤處理:對齊**
- `_E2eGateStop` 帶結果提早結束,有先例:`_NoteRereadStop`(`scripts/lumos:47883`)和 `_DriftM1Stop`(`scripts/lumos:54008`)都是「判不了就丟例外帶原因」。入口 `_e2e_gate_evaluate` 一律接住,轉回結果 dict,對外介面跟安全證據閘一樣。
- 本輪把 `code` 改成 `gate_code`,值 `evaluation_timeout` 和 `evaluation_error` 沿用 `_SECEV_WARN_OK` 的詞。這是把先前的不一致拉回去。對照:`scripts/lumos:41721`、`scripts/lumos:10735`。
- 預算改成呼叫時讀常數 `E2E_GATE_BUDGET_SEC`,拿掉 `_e2e_env_secs`,照 `_SECEV_BUDGET_SEC` 的做法。
- 擋下訊息裡的檔名過 `_esc_clean`,事件名 `blocked`、`skipped-env`、`waived` 都沿用既有詞,`ci` 補記帳。
- `_e2e_load_json` 多接 `RecursionError`,跟 `scripts/lumos:11785`、`scripts/lumos:17127` 一致。

**3. 第二種做法:大致是重用或比照,只有一處偏離**
- `_confirm_tty` 加 `stdin_timeout` 旗標,是擴充原函式,不是另寫一支。逾時沿用 `LUMOS_TTY_TIMEOUT`,`init` 的呼叫端不變。對照:`scripts/lumos:33578`。
- `_e2e_record_files` 先 `lstat`、檢查大小上限、再 `read_text`,跟既有做法一樣(`scripts/lumos:48989`、`scripts/lumos:35530`、`scripts/lumos:36942`)。`E2E_RECORD_SCAN_SEC` 的讀取迴圈寫法也跟 `scripts/lumos:28625` 一樣。
- `_e2e_owner_index` 前綴查表仍是同一個單源函式,不是另一套歸屬判斷。
- 開場掛鉤的 `_e2e_ai_pending_one` 做成逐字複本、拿語法樹來比,照 `ci-status-hook.py` 的複本做法。對照:`scripts/hooks/claude/ci-status-hook.py:48`。
- 偏離的一處是複本守衛本身,見下面第 1 條。

**不對齊的發現**

1. 複本一致性測試是這份 diff 自己另寫的簡化版,沒有併進既有的複本守衛 `t_ci_latest_attempts_copies_identical`(`scripts/test_lumos.py:37124`)。後者掃 `lumos` 加所有 `hooks/*.py`、有「同一檔多份」的偵測,而且特別說明「寫死清單」踩過坑。新測試寫死 `hookp` 和 `GRAPHCTL` 兩個路徑,用 `next(...)` 只取第一份同名函式,沒有重複偵測,包在別處的複本也不會被另外抓到。
   另外,掛鉤裡 `_e2e_ai_line` 的掃描迴圈只是在邏輯上對應 `_e2e_ai_pending_all`,不是逐字複本,只靠一次行為測試盯。`ci-status-hook` 的複本是整個函式逐字相同。這不算新機制,方向和先例同一個(語法樹比對),所以不判 major。
severity: minor
   blocking: 否
   引句:「def body(src, name):   # 函式去掉說明文字後的語法樹:同名、逐字相同的複本才比得過(照 ci-status-hook 的複本做法)」
   file: `scripts/test_lumos.py:20020`(快照 `r3-snapshot.patch:2922`);對照:`scripts/test_lumos.py:37124`

不對齊共 1 條,其中擋實作的 0 條
