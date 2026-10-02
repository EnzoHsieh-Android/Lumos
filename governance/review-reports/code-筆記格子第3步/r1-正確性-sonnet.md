severity: minor

審查範圍:`/tmp/code3-r1.patch` 全部 hunk,對照 rw 工作樹(2f9cb94f)。兩支新測試實跑都綠(14 與 7 案例)。我另在 `/tmp/mut` 的 clone 做了 19 個變異實驗,沒碰 repo。找到 5 條,沒有 blocker 或 major。

**C1** `_metric_gate_off` 對 `lint-new` 永遠回 False,「閘目前 off 不判」這條對它不成立
severity: minor
blocking: 否 — 只影響 doctor 軟提醒,而且目前沒有 `lint-new` 的度量式 RULE。
引句:「return _lint_new_config(root)["gate"] == "off"」
1. `_lint_new_config` 回傳的鍵叫 `mode`,不叫 `gate`(file: `scripts/lumos:24272`、`scripts/lumos:24429`)。
2. 取 `["gate"]` 會丟 KeyError,被函式裡的 `except Exception: return False` 吞掉,等於「沒關」。
3. 重現:設定檔寫 `{"lint_new":{"gate":"off"},"node_home":{"gate":"off"},"drift_check":{"gate":"off"},"note_audit":{"gate":"off"}}`,呼叫 `m._metric_gate_off(root, gate, cfg_text)`。
4. 結果:`lint-new` 回 False(錯),`nodehome-check`、`drift-check`、`note-audit` 都回 True(對)。
5. 後果是閘已關的 `lint-new` 度量規則會被判成立,產生假提醒。
6. 這是寬泛 `except` 把筆誤吞掉的類型,建議對「讀設定失敗」另外處理,不要當成沒關。

**C2** 這次改動自己的筆記讓 S17 在本 repo 上一跑就多一條假提醒
severity: minor
blocking: 否 — 軟提醒不計入問題數,但每次 doctor 都會唸。
引句:「S17 作廢行的 [被取代:] 指到的節點或決策不在」
1. 這句散文寫在 `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:14` 的 WHY 摘要行裡,`[被取代:]` 沒包反引號、值是空的。
2. `slot_parse` 把它當成空值欄位,`_slot_replacement_dead` 回「寫法認不出」。
3. 重現:在 rw 對 `Env(docs/lumos-toolchain-knowledge)` 呼叫 `_doctor_replacement_lines`,回 1 條,正是 `Systems/lumos-cli-read.md:14:[被取代:] 寫法認不出…`。
4. 這個誤報對應的行不是作廢行,S17 卻沒有先判這行有沒有標 `[status:superseded]`。
5. 要擇一處理:S17 只看標了作廢的行,或把筆記裡那句改成反引號包住。

**C3** 新測試有 7 個變異拿掉都不紅
severity: minor
blocking: 否 — 兩支測試的主要判斷是咬住的。
引句:「_METRIC_CMP = {"<": lambda a, b: a < b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b,」
1. 實跑結果:`_slot_replacement_dead` 不查決策 valid、暖機道、`[since:]` 道、閘 off 道、FACT 不跳作廢,各讓 `t_slots_doctor_reminders` 紅。
2. 兩個測試檔案也確實會被這些變異翻紅:拿掉續行行號檢查、兜底條數記 0、`rc` 不在印之前定,都讓 `t_slots_retire_issue_followups` 紅。
3. 以下變異兩支測試全綠,等於沒測:
   - 比較符號:`>` 改成 `>=`。測試只用過 `>=` 和 `<`,`<=`、`==`、`>` 沒走過。
   - 週期單位:`"週": 7` 改成 1、`"月": 30` 改成 1。測試只用「天」。
   - S19 上限:`_FACT_RECHECK_SHOW` 20 改成 2000。測試沒造超過 20 條的情境。
   - S18 的 `--ci` 守衛:拿掉後測試仍綠。
   - 時區:`_gov_metric_events` 的 naive 時間改當 UTC 處理,測試仍綠。
   - `_gov_tail_bytes` 的檔尾截斷:`start = max(0, sz - cap)` 改成 0,測試仍綠。
4. 測試開頭的翻紅釘說明提到 S17 的 `ci` 守衛(⑥),但 S18 那段沒有對應的測試。

**C4** `[recheck:]` 的單位換算沒被任何斷言釘住,錯了不會有人知道
severity: minor
blocking: 否 — 屬 C3 同一類,單獨列是因為換算表錯了會直接讓「超過週期」判成錯。
引句:「_FACT_RECHECK_UNIT_DAYS = {"天": 1, "週": 7, "月": 30}」
1. 目前的測試只用過「天」,「週」「月」兩行沒有任何情境走到。

**C5** `[被取代:]` 值的邊角寫法被靜默放過
severity: minor
blocking: 否 — 沒有具體誤報,只是漏列;⚠ 判不準這算不算規格內。
引句:「if v.startswith("無"):」
1. 值是 `無理由`(中間沒空白)時直接放行,但規格要求的是 `無 <理由>`。
2. 路徑以「無」開頭的中文節點,例如 `無人機路徑#d1`,同樣被放行而不查。
3. 寫成 `[[Systems/Live#d9]]`(連結帶決策錨點)時,只查節點在不在,不查決策 d9。
4. 三種寫法都不會被 S17 提醒。

**資料狀態五問**
- **舊程式讀新帳**:新增的只有 `kind="retire"` 的 finding 與 null 條數的帳,舊讀者忽略未知欄位,沒問題。
- **新程式讀舊表態檔**:表態檔格式沒變,比對仍以整條原文為準,沒問題。
- **帳檔最後一行殘缺**:`_drift_jsonl_parse` 對非 JSON 的行略過,沒問題。
- **時間與時區**:帳裡 `ts` 帶 `+08:00` 時用該時區;沒帶時區的當本機時間,今天也取本機日期,一致。
- **`_gov_tail_bytes` 抽出**:與原本帳增速那段逐行比對,上限、起點、丟掉切半頭行都相同,`_from` 的語意也沒變,行為完全一樣。
- **drift scan 的 retire**:與回頭條件共用同一棵樹與同一個預算,預算用完會變成「判不了」。`[retire:when-…]` 不會被 `_probe_lines` 當成回頭條件,不會重複抽。

**圖譜鏡頭**
派工時沒有附上固定席筆記,我自己跑了 `lumos impact --diff dbb5883a..2f9cb94f`,涉及 26 個固定席加 top 8。
- **`Systems/lumos-cli-read.md` 與其他 ★INVARIANT★ 節點**:不影響。這次沒動 search 預設排除作廢節點、contracts、doctor 的原有檢查,只在 S16 後面新增三段軟提醒。
- **`Systems/reversibility-governance-ledger.md` 與其他 RISK 節點**:不影響。S17 到 S19 刻意不寫治理帳,不動 `_KNOWN_GATES`,Check R 與 H 不受影響。
- **`Systems/存量漂移守衛.md`**:新增的 WHY 與程式一致。已作廢的不抽、已表態的列在已表態、推送那支改成印完才記帳,都與程式相符。
- **`Systems/授權與歸屬.md` 等其餘固定席**:這份 diff 沒碰到它們宣稱的行為。

最高嚴重度 minor,blocking 0 條
