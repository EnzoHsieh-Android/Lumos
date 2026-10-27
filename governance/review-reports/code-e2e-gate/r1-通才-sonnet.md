severity: major

1. 判定的前段在 `LUMOS_SKIP_ANDROID_E2E=1` 檢查之前就會擋人,環境變數逃生口對這幾種擋下無效。
severity: major
   blocking: 是
   file: `scripts/lumos`,位置在 `_e2e_gate_body` 約 diff 第 1544–1549 行。順序是 `_e2e_gate_resolve`、`_e2e_gate_uses`、`_in_ci()`,最後才是 `os.environ.get("LUMOS_SKIP_ANDROID_E2E") == "1"`。
   引句:「        return _e2e_gate_out("skipped-env", "LUMOS_SKIP_ANDROID_E2E=1:這一次整道不跑")」
   場景:被推送提交的 `.lumos/macrobench.json` 讀不懂(壞 JSON、BOM、非物件)時,`_e2e_gate_uses` 會 `_e2e_gate_block`。主線候選的 macrobench.json 讀不懂、`_push_rev` 讀不到提交、或這兩階段 git 逾時,也一樣會擋。擋下訊息由 `_cl_say_e2e_block` 固定印「這一次整道先關掉(會留帳):LUMOS_SKIP_ANDROID_E2E=1 git push」。使用者照做仍然被擋,只剩 `--no-verify`。這同時違反計劃 S17 與第 102 行寫的「出口是 `LUMOS_SKIP_ANDROID_E2E=1`」,也違反「沒有 e2e 段的專案輸出一字不變」:一個根本不用 E2E、但 macrobench.json 有 BOM 或壞掉的專案,每次推送都被這道擋。
   重現:
   - 在乾淨的 git repo 裡寫一份 `.lumos/macrobench.json`,內容是 `not json`,提交。
   - 跑 `LUMOS_SKIP_ANDROID_E2E=1 python3.14 scripts/lumos android-e2e check --repo .`。
   - 實測輸出:`{"status": "blocked", "reason": "被推送提交的 macrobench.json b69fe527 的 .lumos/macrobench.json 讀不懂(不是合格的 UTF-8 JSON 物件)"}`,rc=1。不設環境變數時輸出完全相同。
   - 修法方向:`LUMOS_SKIP_ANDROID_E2E` 與 `_in_ci` 提到 `_e2e_gate_resolve` 之前先判,或讓 `_e2e_gate_uses` 的錯誤在 skip 時降成放行。
   - 測試缺口:沒有測試把 skip 與「壞 macrobench」組合起來,拿掉順序依賴測試照綠。

2. 開場掛鉤的 `_e2e_ai_line` 沒有逐檔隔離例外,一份壞紀錄會讓所有 AI 放行提醒一起消失。
severity: minor
   blocking: 否
   file: `scripts/hooks/claude/lumos-entry-hook.py`,位置在 `_e2e_ai_line` 的 for 迴圈。
   引句:「            rec = json.loads(p.read_text(encoding="utf-8"))」
   場景:`.lumos/e2e-records/` 裡有一份檔名合格、內容是 `[]` 或字串的 JSON(手改或合併衝突殘留)。下一行 `rec.get("waivers")` 會丟 `AttributeError`,被最外層 `except Exception` 吞掉,整個函式回 None。其他紀錄裡未被人看過的 AI 放行就一直不會在開場出現。同一批資料在 doctor 端走 `_e2e_records_all`,有 `_e2e_record_err` 過濾,行為不一致。
   重現:在 `.lumos/e2e-records/<64 位 hex>.json` 放 `[]`,同目錄再放一份帶 `by:"ai"`、note 非空的合法放行紀錄。跑 `_e2e_ai_line(root)` 會回 None,預期是列出 1 筆。
   修法方向:迴圈內先判 `isinstance(rec, dict)`,或把 try 包到單檔層級。未能在掛鉤上實際跑出輸出,此條只憑讀碼。

逐角度的其餘候選都沒有可講出的失敗情境,不列:
- `_confirm_tty` 拆三支:其他呼叫端 `scripts/lumos:33754` 預設 `stdin_timeout=False`,路徑不變。
- `_e2e_fingerprint` 加 pathspec:`seen_app` 與 `gone` 的語意不變,`--literal-pathspecs` 與 `_e2e_scope_hit` 的篩選一致。
- `_e2e_changed_features` 的 unmatched 範圍:舊判斷是「`.maestro` 整個目錄、app_dirs 全部、flows」。新判斷在 scope_hit 內,只少了預設排除的單元測試目錄,屬於刻意改動。
- `_E2eRecordLock` 的 stale 接手有 TOCTOU,屬併發題,判範圍外、標誤報。
- 表態記錄:`py-eventloop`、`py-parallel`、`py-memory`、`py-hotpath` 與這份 diff 一致。

固定席節點判定:
- `Issues/code-loop守衛main-direct盲區`:不影響。新道排在放行早退之前,沒有改動 main-direct 路徑的守衛判斷。
- `Systems/lumos-cli-lifecycle` 的 ★INVARIANT★:不影響。`_confirm_tty` 只在 `stdin_timeout=True` 時改行為,沒碰 sentinel 與 CLAUDE.md 注入。
- `Systems/lumos-cli-read` 的 ★INVARIANT★:不影響。diff 沒碰 search 的 superseded 過濾。
- `Systems/guard-kill` 的 ★INVARIANT★:不影響。沒碰 guard kill 的 rc 與 JSON 輸出。
- `Systems/pitfalls-code-loop`、`Systems/存量漂移守衛`、`Systems/每支檔有家`、`Systems/筆記內容閘`:不影響。這份 diff 只新增一道判定,沒改這些節點宣稱的行為。唯一的行為落差就是第 1 條,對照的是 `Projects/Android端到端驗收_計劃` 的 S17。

總結:max severity 是 major,blocking 1 條(第 1 條),minor 1 條(第 2 條)。第 1 條已實測重現,第 2 條只憑讀碼。
