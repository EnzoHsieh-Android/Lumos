severity: minor

以下行號都是修後版本 5ce8115d 的行號。

**1. 分層與依賴方向**
- 整體跟鄰居一致。新碼放在原本就管這件事的函式旁邊,沒有跨層直呼。
- `_hooks_path_dir`(`scripts/lumos:21862`)放在 `_hooks_path_is_ours` 前面。它被 `_hooks_path_is_ours`(21884)和 `_enforcement_prepush_ungated`(25917)呼叫。這是把重複的解析收成一份,方向正確。
- `_in_ci`(`scripts/lumos:224`)把三處 CI 判斷收成一份,沒有繞過共用函式。全檔只剩這一個判斷點,`scripts/` 其他檔也沒有別的。
- `_drift_m1_note_long`(39914)改成呼叫 `_drift_m1_line_names`,跟 `_drift_m1_line_hits`(39903)用同一個先篩,傳入的 `run.check_time` 也一樣。
- 帳的截斷改走 `_gate_event_fit`(35429),跟 `_drift_m1_fit`(40100)、`_ns_relaxed_record`(33187)同一個共用函式。參數形狀一致:清單鍵 `"rows"`、`nodes_cap=20`、先 fit 再寫。
- 落盤沿用 `_note_audit_write_verdict`(34059),只加一個選用的 `max_bytes`。參數名跟 `_nodehome_cat_blobs_capped(…, max_bytes, …)`(29533)一致。
- 一處沒收乾淨的重複,見 A2。

**2. 命名與錯誤處理**
- 「擋下:…」印到標準錯誤、回 2,跟 `reread-prepare`(34980 起)和 `reread-record`(35150 附近)一樣。
- 超過上限的訊息寫成 `N KB … 上限`,跟 `_note_reread_unread_why`(34791)的 `// 1024` 寫法一致。
- 記帳欄位 `rows_truncated` 的命名跟鄰居一樣。
- `state` 字串只套到一種記帳,另一種漏了,見 A1。

**3. 第二種做法**
- 大小上限、截帳、CI 判斷、hooksPath 解析四處都沒有新做法。
- 唯一要請編排者判斷的是測試總檔的環境清除,見 A3。

## A1 判不了的記帳只在其中一條路徑記 `state`
severity: minor
blocking: 否
引句:「extra={"state": "undecidable"})      # 跟舊句檢查的帳一樣用 state 字串記」
file: `scripts/lumos:40147`(`_drift_m1_ledger`,`extra` 每筆都帶 `"check"` 和 `"state": st`)
file: `scripts/lumos:35402`(`_note_reread_ledger` 不擋時的判不了:`_gate_event_or_warn(root, "note-reread", "skipped", res["why"])`,沒有 `state`)
- 既有:舊句檢查的帳每一筆都帶 `state`。
- 這次:同一個函式裡,判不了且擋下(hard)這一支記 `state: "undecidable"`。判不了但不擋(warn,記 skipped)的另一支沒有。
- 不一致在哪:同一個狀態在回頭重讀自己的帳裡,有一半帶 `state`、另一半不帶。讀帳的人還是得認兩種寫法,「對齊舊句檢查」只做了一半。

## A2 工作目錄判定紀錄的讀取守門被抄成第二份
severity: minor
blocking: 否
引句:「if f.is_symlink() or not f.is_file() or f.stat().st_size > _NOTE_REREAD_VERDICT_MAX:」
file: `scripts/lumos:37948`(`_drift_ack_reread_verdicts`,同樣的資料夾與檔案守門:`d.is_symlink()`、`f.is_symlink() or not f.is_file() or f.stat().st_size > _NOTE_REREAD_VERDICT_MAX`)
- 既有:`_drift_ack_reread_verdicts` 已經有一份「走訪工作目錄紀錄資料夾,擋符號連結、非一般檔、超過上限」的骨架。
- 這次:`_note_reread_uncommitted`(34840)重寫了一份幾乎一樣的走訪守門。解析那一步倒是用了共用的 `_note_reread_verdict_doc`,而 `_drift_ack_reread_verdicts` 是自己 `json.loads`。
- 不一致在哪:同一個「讀工作目錄紀錄」的守門現在有兩份。這次幫 `_hooks_path_dir` 做了收斂,這裡沒有。結構還在同層、沒有跨層,所以只算 minor。

## A3 測試總檔清環境變數,多出第三種寫法 ⚠
severity: minor
blocking: 否
引句:「for k in [k for k in os.environ if k.startswith("LUMOS_SKIP_")]:」
file: `scripts/test_lumos.py:35650`(`main()` 就地用名單 `pop` 清 `GIT_*`)
file: `scripts/test_lumos.py:35536`、`scripts/test_lumos.py:35587`(`_isolate_environment` 在同一層管 `CODEX_HOME`、`CLAUDE_CONFIG_DIR`、`LUMOS_SKIP_CLAUDE_PLUGIN`)
file: `scripts/test_lumos.py:63692`、`scripts/test_lumos.py:59883`、`scripts/test_lumos.py:73572`(`_rr`、`_dr`、`_fc_lum` 各自在起子行程時清自己要的變數)
- 既有:清環境變數有兩種做法。一是 `main()` 或 `_isolate_environment` 對整個行程清,用明列名單。二是每個起子行程的 helper 各自複製環境再清。
- 這次:新增獨立函式 `_drop_inherited_skip_env`,在 `main()` 呼叫,用前綴掃描清掉所有 `LUMOS_SKIP_*`。它在 `_isolate_environment` 前面跑,而後者之後又把 `LUMOS_SKIP_CLAUDE_PLUGIN` 設回 1。
- 不一致在哪:位置(行程級、進入點)跟 `GIT_*` 的做法一致。但它沒併進已經管 lumos 相關環境的 `_isolate_environment`,清法也從名單變成前綴。`_rr`、`_dr` 的逐個 pop 現在變成重複的第二層。
- ⚠ 這算「同一做法的擴充」還是「另一套」,請編排者判。我傾向前者。

不對齊共 3 條,其中 0 條是第二種做法
