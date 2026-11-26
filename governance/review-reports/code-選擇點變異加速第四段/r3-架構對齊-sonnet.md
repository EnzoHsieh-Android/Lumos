severity: minor

審查範圍是 r3-snapshot.patch 的程式碼部分(scripts/lumos 與 scripts/test_lumos.py)。我只讀了測試的函式清單與 `_CKM_GRADLE` 的位置,沒有逐行對讀測試內文。計劃與筆記的 diff 沒有逐行讀。

**1. 分層與依賴方向**

沒有跨層直呼,新碼放的位置與呼叫方向都跟鄰居一致。
- 新增的 `_choice_merge_event_line`、`_choice_merge_events`、`_choice_merge_timeout_kind`、`_choice_merge_init_path`、`_choice_merge_init_write`、`_kill_merge_base_run`、`_kill_merge_trip` 都放在既有 `_choice_merge_*` / `_kill_merge_*` 那一帶,對照 `scripts/lumos:28931`(`_kill_merge_base`)與 `scripts/lumos:29133`(`_kill_merge_base_run`)。
- 呼叫鏈沿用鄰居的方向:`_kill_merge_screen` 呼叫 `_choice_merge_events`,`_choice_merge_classify` 呼叫 `_choice_merge_timeout_kind`。`cmd_guard_kill` 只透過 `mctx.scratch` 把 `_isolated_worktree` 的 `scratch` 欄位交給合併這一側,跟既有的 `mctx` 帶參數方式相同。
- `_cmd_arg_quote` 是把原本 `_run_cmd_expand` 內重複的 `list2cmdline`/`shlex.quote` 分支收成一支,方向正確。對照 `scripts/lumos:28073`,以及既有 `_sh_quote` 在 `scripts/lumos:468`。
- `_sh_quote` 只做 `shlex.quote`、不分 Windows。`_cmd_arg_quote` 加了 Windows 分支,兩者用途不同(給人貼的指令 vs 交給 shell 執行的指令)。這不是第二種做法,而是把原本兩處的 Windows 分支併成一處。

**2. 命名與錯誤處理**

- 命名沿用鄰居:常數 `_CHOICE_MERGE_*`、函式 `_kill_merge_*` / `_choice_merge_*`,`_KillMerge` 新欄位 `hang_streak`、`init_off` 與既有 `streak`、`reopen` 同形。
- 錯誤處理與印字跟鄰居一致:
  - 新增的 `print(f"⚠ {_kill_esc(c.plat)}:…", file=sys.stderr)` 與 `_kill_merge_breaker` 既有那行相同格式。
  - 寫檔失敗用 `except OSError` 後降級、不丟例外,與 `_choice_merge_facts` 的 `OSError` 處理一致。
  - `_GOV_FIELD_TYPES`、`cmd_gov` 讀舊帳缺欄位時 `or {}` 的寫法,也與第二、三段同形。
- 發現(minor,不阻擋):`_kill_merge_breaker` 裡「累計原因」的三行(`per = mg.unclean.setdefault(…)`、`per[why] += 1`、`mg.last_unclean[plat] = why`)現在重複三次。新增的 hang 分支與試探恢復分支各複製一份,其中試探分支的條件另外寫了 `or why == _CHOICE_MERGE_HANG_WHY`,與 `counts` 語意不一致。這跟 `_kill_merge_trip` 已抽共用 helper 的作法不齊,但結構沒錯。
- 引句:「per = mg.unclean.setdefault(plat, {})」
- file: `scripts/lumos:29230`(`_kill_merge_breaker`)
severity: minor
- blocking: 否

**3. 第二種做法**

沒有引入專案原本沒有的做法。
- 引號:新增的 `_cmd_arg_quote` 是把既有兩處的 `list2cmdline`/`shlex.quote` 邏輯收成一個函式,不是平行新增。
- Windows 特殊字元:`_WIN_CMD_SPECIAL`(`scripts/lumos:6507`)已存在,新增的 `_choice_merge_init_path` 直接重用。
- 解析外部工具輸出:新增的事件行解析用 `rpartition`/`partition` 字串切,專案裡有現成用法(例如 `scripts/lumos:4509`、`scripts/lumos:5017`),不是新手法。
- 截斷標記:`_choice_merge_events` 判斷的 `...[truncated ` 與 `_kill_cap` 輸出的 `...[truncated {dropped} bytes]...`(`scripts/lumos:28274` 一帶)一致。
- 暫存目錄:`_isolated_worktree` 加 `scratch` 欄位,沿用既有 SimpleNamespace 形狀(`ok`、`err`),還是同一支共用函式。
- 測試:新增的三支 `t_choice_kill_merge_*`(events_cmd、events_order、hang_breaker)命名與既有同系列一致。

不對齊共 1 條,其中 major 0 條。
