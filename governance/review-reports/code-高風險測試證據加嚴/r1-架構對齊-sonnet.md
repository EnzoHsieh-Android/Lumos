severity: minor

我在工作樹讀了 `scripts/lumos` 的對照段落,也跑了 `-k high_risk_since_fresh`、`cap_world_since`、`push_scan_reads`、`bad_ledger`,全綠。沒有 major。

## 問 1:分層與依賴方向

大致對齊,有一處多讀一次帳。

- **讀帳走既有函式**:簽核讀 `_gov_vc_gate_events(rr, "signoff")`,跟 `_spec_gate_gov_index` 用的是同一支(`scripts/lumos:15721`)。
- **拆節走既有函式**:用既有的 `_h2_section_lines`(`scripts/lumos:13774`),只加一個 `heads` 參數,沒有第三套找節邏輯。
- **條款集合走既有做法**:用 stub 版 `clause_bindings`(對照 `scripts/lumos:48202`)和 `_spec_gate_keeps_rows`(`scripts/lumos:14185`)。
- **其他共用**:`_waive_origin_tty`(`scripts/lumos:38916`,docstring 已寫明共用)、`_e2e_who`(`scripts/lumos:43770`)、`_gate_event`、`nfc`、`_real_chars`、`_esc_clean`、`_out_clean` 都沿用。
- **讀計劃文字**:`(env.vault / prel).read_text(encoding="utf-8-sig")` 加 `except (OSError, UnicodeDecodeError)`,跟 `_spec_gate_push_stale` 一樣。
- **日期跟指紋**:新 `_plan_first_day` 是照 `_plan_first_commit`(`scripts/lumos:14198`)擴出來的,沒繞過既有入口,不另列。`hashlib` 加 `json.dumps(ensure_ascii=False)` 跟 `_kill_recipe_key`(`scripts/lumos:25335`)同法。
- **新鮮度測試**:把 `_cap_since_last_change_day` 加參數共用,沒另寫一套(`scripts/test_lumos.py` 的 `t_high_risk_since_fresh`)。

不對齊一處:

### 1. 推送前掃描多讀一次治理帳,而且那條錯誤分支走不到
severity: minor
blocking: 否
引句:「            ctx["exp_gov"] = _gov_vc_gate_events(rr, "signoff")」
- 對照:鄰居先讀一次放進 `ctx["sg_gov"]`(`scripts/lumos:16494` 附近),讀不到就整份回 `[帳] ` 開頭的擋下訊息。`t_spec_gate_push_scan_reads_ledger_once` 守的就是帳只讀一次的紀律(`scripts/test_lumos.py:78396`)。
- 新碼:同一次推送再用 `_gov_vc_gate_events(rr, "signoff")` 讀第二次。
- 場景:只要有候選計劃(`_live`),`sg_gov` 已經讀過同一本帳,讀不到會先擋掉,`exp_gov` 的 `gerr` 分支就走不到。patch 自己的測試也承認「上游那道先擋,整條流程走不到這裡;直接呼叫才測得到」。
- 壞在哪:萬一走到,擋下訊息帶 `_EXPECTED_PUSH_TAG`,標題會變成「N 份計劃沒過(風險低…風險高…)」,不是 `_SPEC_GATE_PUSH_LEDGER_TAG` 對應的「帳讀不到」。同一個原因出現兩種標題。
- 佐證:`scripts/lumos:15719`

## 問 2:命名與錯誤處理

大致對齊,兩處與鄰居不同。

- **命名**:`_expected_*`、`_EXPECTED_*`、`_hre_*`(測試輔助)、`t_*` 都符合現有風格。
- **錯誤回傳**:`_expected_table` 回 `(資料, 問題清單)` 且不丟例外,`_expected_push_one` 回原因字串或 None,都跟鄰居一致。
- **訊息格式**:`[spec-gate] 預期值表: ✓/✗` 沿用 `[spec-gate] 跑:` 的格式。

### 2. 規格閘新子步驟的回傳慣例跟鄰居不同
severity: minor
blocking: 否
引句:「    if _spec_gate_expected_part(env, rel, text, door) is False:」
- 對照:同函式 `_spec_gate_front` 裡,`_spec_gate_pending` 回「rc 或 None」,`if pq_rc is not None: return pq_rc`。`_spec_gate_clause_part` 回 `(rc, rows)`。
- 新碼:回 `True/False`,呼叫端用 `is False` 判斷,再自己寫 `return 1`。
- 場景:不會出錯,只是同一個函式裡有三種子步驟回傳慣例。
- 佐證:`scripts/lumos` 的 `_spec_gate_front`,即引句上方約 8 行的 `pq_rc = _spec_gate_pending(env, rel, text)`

### 3. 治理帳列的 token 與 origin 用展開覆寫,沒有接在既有條件鏈上
severity: minor
blocking: 否
引句:「         **({"token": str(d.get("token") or ""), "origin": d.get("origin")} if (d.get("gate"), d.get("kind")) == ("signoff", "expected-signed") else {}),」
- 對照:`cmd_gov` 的列字典已有 `"token": (...canary... else ...code-loop... else str(d.get("token") or "") if d.get("gate") == "fix-check" else "")` 這條鏈。
- 新碼:同一個字典先寫一次 `"token"` 鍵,再用 `**{...}` 覆寫同一個鍵。
- 場景:`fix-check` 的做法是在鏈上加一段;這裡改用另一種覆寫寫法。行為是對的,日後改 token 規則得同時看兩處。
- 佐證:`scripts/lumos:17342`

## 問 3:第二種做法

沒有 major 級的第二種做法。表格拆格、表指紋、讀帳、節段讀取、環境變數覆寫常數,新碼要不是直接重用,就是跟既有寫法一樣。

- **表格拆格**:`_expected_split_cells` 是新寫的嚴格版,docstring 說明理由是指紋要穩定。專案另外兩處(`scripts/lumos:28046`、`scripts/lumos:51850`)是寬鬆版,用途不同。
- **新日期常數**:`_HIGH_RISK_EVIDENCE_SINCE` 用純日期,跟 `_NOTE_LINT_PLAN_SINCE`(`scripts/lumos:12694`)同形;帶時區的是處置閘那一族。
- **環境變數覆寫**:`_expected_since` 對照 `LUMOS_PANEL_RETIRE_CUTOFF`(`scripts/lumos:19187`),測試端的總開關也同形(`scripts/test_lumos.py:158-159`)。

### ⚠ 交編排者:鄰居本身不一致,生效日常數該不該給環境變數覆寫
severity: minor
blocking: 否
引句:「    v = os.environ.get("LUMOS_HIGH_RISK_EVIDENCE_SINCE", "").strip()」
- 一邊:`_CAP_WORLD_CHECK_SINCE` 的註解明寫「不給環境變數覆寫(同 `_SPEC_GATE_SINCE` 那一族)」(`scripts/lumos:22474`)。
- 另一邊:`LUMOS_PANEL_RETIRE_CUTOFF` 有環境變數,新碼選了這一邊。
- 影響:新碼的覆寫值設成 `9999-12-31` 就能整道關掉預期值表簽核,而且不留帳。這取決於要不要把它當 `_CAP_WORLD_CHECK_SINCE` 那一族,我判不準,請編排者裁。

不對齊共 3 條(另 ⚠ 1 條交編排者),其中 major 0 條

總結:全份最高 minor
