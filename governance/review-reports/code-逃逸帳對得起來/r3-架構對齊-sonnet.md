severity: clean

已看,無:前兩輪架構席指出的四點都照做,r3 新增的修正也都沿用既有寫法,沒有另開第二種做法或跨層直呼。

- r1 F1(掃帳只寫一份)、r1 F2(計劃欄位走 env.notes)、r1 F3(`--by` 改名)、r1 F4(fixture 命名)四點,r2 架構席已核對過全部照做(見 `governance` 外的 r2-架構對齊 報告),r3 patch 裡沒有任何一處把這四點寫法退回去。

- r3 把 `_escape_log_guard` 的呼叫從「先讀帳、再檢查符號連結」搬到「先檢查符號連結、再讀帳」,現在跟手動記帳路徑（`cmd_loop_escape` 記帳分支）同一種順序：兩處都是進了 `_vault_write_lock` 之後第一件事就是 `rc_g = _escape_log_guard(log); if rc_g: return rc_g`。
引句:「rc_g = _escape_log_guard(log)   # 先確認帳檔不是符號連結再讀(r2 外家找洞席)」
file: `scripts/lumos:9605`(撤回路徑)對照 `scripts/lumos:9797`(手動記帳路徑),兩處寫法完全一致,不是各寫一套。

- r3 把「落帳時已決定的種類為準」那段邏輯從內聯在 `_escape_row_bucket` 裡抽成獨立函式 `_escape_row_kind`,跟本檔既有「共同判斷抽成一支具名函式再被多處呼叫」的慣例一致（對照 `_escape_evidence_keys`、`_escape_stage_class` 這類同檔案裡已有的小型純函式,職責單一、有 docstring)。`_escape_stats` 與 `_escape_row_bucket` 都改呼叫這支新函式,沒有兩邊各寫一次判斷。
file: `scripts/lumos:9924`(`ev_loops = _escape_shared_evidence([r for r in rows if _escape_row_kind(r, review_ids) != "plan"], released)`)、`scripts/lumos:9955`(`_escape_row_kind` 定義)、`scripts/lumos:9962`(`_escape_row_bucket` 呼叫同一支)。

- r3 新增的 `_esc_clean` 套用範圍(doctor 按階段那行、`--list` 的日期欄、撤回紀錄裡的日期)全部沿用同一支既有消毒函式,沒有另外寫一套字元過濾。
引句:「out = "".join(ch if ch >= " " and not ("\x7f" <= ch <= "\x9f") else " " for ch in str(v))」
file: `scripts/lumos:9418`(`_esc_clean` 定義,擴大控制字元範圍到 C1,函式簽名與呼叫端不變)。

- r3 新增的 `--repo` 併入撤回互斥檢查(`others=(..., repo)`)跟既有「混記帳參數即擋」的互斥檢查是同一組 tuple、同一段判斷式,不是為 `--repo` 另開一條路。file: `scripts/lumos:9642`(`others=(loop_id, stage, severity, desc, defect_ref, rule, git_range, sha, missing_ref, repo)`)。

- r3 新增的測試 `t_escape_review_r2_fixes` 沿用 `_mk_escape_fixture`/`_esc_row`/`check` 既有測試 idiom,沒有引入新的斷言風格或 fixture 搭法。
