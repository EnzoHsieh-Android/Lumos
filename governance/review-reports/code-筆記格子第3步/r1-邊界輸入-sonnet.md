severity: major

這份 diff 在邊界輸入上有一個會讓整個 `lumos doctor` 崩潰的洞(B1),另有四個較輕的問題。我實跑了 S17、S18、S19 和 `_metric_gate_off`。`t_slots_doctor_reminders` 與 `t_slots_retire_issue_followups` 兩組測試在現況下都綠,所以這些洞測試都沒碰到。

**B1** S18 讀進來的週數與門檻完全沒有範圍保護,一條 RULE 就能讓整個 doctor 以 traceback 退出
引句:「cutoff = now - _dt.timedelta(weeks=weeks)」
severity: major
blocking: 是 — `近99999999999週` 讓 doctor 在 S18 以 OverflowError 退出,後面 S19 和其餘段落都不跑。
1. 週數 1 到 8 只在提交時的 `_slot_retire_err` 檢查,doctor 沒有重驗。`_SLOT_METRIC_RE` 的 `近(\d+)週` 和門檻 `(\d+)` 吃任意位數。舊筆記或 `--no-verify` 進來的筆記都不經過那道檢查。
2. 重現:vault 放 `RULE:x [依據:人] [since:2026-06-01] [retire:度量 note-shape.blocked < 1 近99999999999週]`,再放任一筆治理帳,跑 `python3.14 scripts/lumos --vault <vault> doctor`。
3. 結果是 `OverflowError: Python int too large to convert to C int`,出在 `scripts/lumos:3620`,rc=1。
4. 超過 4300 位數的週數或門檻會在 `int()` 拋 ValueError,同樣崩潰。
5. S18 呼叫端沒有 try 保護,而 S16 到 S19 是新插進 doctor 主流程的。
6. 建議在 `_doctor_metric_lines` 內逐條包 try,並重驗 1 到 8 週,範圍外的改成「寫法不合」提醒。
7. 同一個根因會讓 `近0週` 的 `< 1` 立即成立,等於沒有暖機。

**B2** 治理帳的 ts 沒有時區且接近年份上下限時,`astimezone()` 在 try 之外拋 ValueError
引句:「t = t.astimezone()」
severity: minor
blocking: 否 — 帳是機器寫的,真實機率低,但一行壞帳就讓 S18 崩潰。
1. `_gov_metric_events` 的 try 只包 `fromisoformat`,`astimezone()` 在它外面。
2. 重現:治理帳放一行 `{"ts":"9999-12-31T23:59:59","gate":"a","kind":"b"}`,呼叫 `_gov_metric_events`,得到 `ValueError: year must be in 1..9999, not 10000`。在東八區 `0001-01-01T00:00:00` 同樣會炸。
3. 程式檔位置是 `scripts/lumos:3586`。
4. 同一份 `_drift_jsonl_parse` 對壞行的原則是「只跳那一行」,這裡沒有做到。
5. 建議把 `astimezone` 納入 try,失敗時 continue。

**B3** `_metric_gate_off` 認不得 `lint-new` 關掉的狀態,錯誤被吞掉,而 Systems 筆記宣稱「閘目前 off 不判」
引句:「return _lint_new_config(root)["gate"] == "off"」
severity: minor
blocking: 否 — 只會多唸一條不該唸的提醒。
1. `_lint_new_config` 回傳的 dict 鍵是 `mode`,沒有 `gate`(`scripts/lumos:24452` 寫的是 `cfg["mode"] = g`)。
2. 取 `["gate"]` 會 KeyError,被外層 `except Exception: return False` 吞掉。
3. 重現:設定檔放 `{"lint_new":{"gate":"off"}}`,呼叫 `_metric_gate_off(root, "lint-new", cfg_text)` 得到 False。
4. 其餘五個閘我都驗過,關掉時回 True。
5. 測試只覆蓋 `note-shape`,所以沒紅。
6. 這同時違反 `Systems/lumos-cli-read` 新增 WHY 行的說法。

**B4** S18 不驗閘名、種類是否存在,`==` 或 `<` 對拼錯的名字永遠成立
引句:「if _METRIC_CMP[op](cnt, thr):」
severity: minor
blocking: 否 — 只是多出誤導性提醒,不影響 rc。
1. 重現:`[retire:度量 nosuchgate.blocked == 0 近4週]` 與 `度量 note-shape.blokced < 1 近4週`,都輸出「近 4 週 … 0 筆(… 成立),這條限制該撤」。
2. 原因是名單和種類的檢查只在提交時做(`_KNOWN_GATES`、`_SLOT_METRIC_KINDS`),沒經過提交檢查的舊筆記會被 doctor 當成「沒事件所以成立」。
3. 建議 doctor 也驗閘名與種類,不在名單就略過或改唸「閘名不認得」。

**B5** S17、S18、S19 把筆記裡的原文直接塞進輸出,沒清控制字元
引句:「out.append(f"{rel}:{no}:[被取代:{v[:40]}] {why}")」
severity: minor
blocking: 否 — 輸出是終端提醒,但筆記原文可帶 ESC 序列。
1. 驗證:`[被取代:` 後面放一個 ESC 字元,doctor 輸出的 S17 行裡出現原始 ESC(`cat -v` 顯示 `^[`)。
2. `sp['core'][:40]`(S18、S19)和 `rc[:20]`(S19)同樣直接進 `warn_soft`。S18 的實測回傳值是 `…該撤:\x1b[2Jevil\x07`,ESC 和 BEL 都沒清。
3. 同一份 diff 的 `_drift_scan_print` 與 `_drift_retire_print` 都用了 `_esc_clean`,這三段沒有。
4. 建議在組字串處統一包 `_esc_clean`。

**固定席筆記判定**:派工訊息尾端沒有附 LUMOS-IMPACT 的固定席筆記,所以只能按 diff 動到的節點判。
- `Systems/存量漂移守衛`:不影響。新 WHY 行說的 scan 兜底、表態行號限制、印完才記帳,與我讀到的程式和兩支測試一致。續行行號擋下和 `_retire_lines` 的行號口徑相同,`>-` 與 CRLF 情境我都對過。
- `Systems/lumos-cli-read`:新 WHY 行宣稱「閘目前 off 不判」與 B3 不符,其餘不影響。
- `Issues/撤除條件檢查末輪遺留四項`:四項結案內容與程式相符。

**未發現問題的項目**:
- 筆記讀不了或非 UTF-8:略過,不崩。
- `[[X|顯示]]` 與 `[[X#標題]]`:正確解析。
- 路徑含 `..` 或空白的 `節點路徑#dN`:正確回報找不到或寫法認不出,沒有路徑逃逸。
- 日期 `2026-02-30`、`0000-01-01`、未來日期:不判,不崩。
- 治理帳為空檔、只有壞行、中段非 UTF-8、`gate` 是 null 或 list:都不崩。
- ack 行號 0、負數、超過行數、指到 frontmatter:被擋。
- 重複的 `[retire:]`:不判。
- 單行字串的 `summary:`:整條被略過,與其他檢查一致。

最高嚴重度 major,blocking 1 條
