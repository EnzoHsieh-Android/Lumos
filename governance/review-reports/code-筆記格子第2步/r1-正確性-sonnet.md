severity: major

我讀完整份 diff,並在 repo 裡用 `_retire_lines` 實跑了 C1。測試 `t_slots_retire_when_push` 我沒有拿掉判斷重跑,3 的結論只來自讀程式。`lumos impact --diff cbbdd46a..b3f9c874` 實際列出 26 篇固定席加 8 篇其他節點,下面第 2 項分組回答。

## 1. 正確性

**C1** 有續行的 RULE 一旦撤除條件成立,`drift ack` 表態對它無效,推送永遠被擋,只剩把那行標作廢或 `LUMOS_SKIP_DRIFT_CHECK=1` 兩條出路。
severity: major
blocking: 是 — 改法提示叫人用 `drift ack --kind retire`,但對這類行這條指令記下的表態永遠對不上。
引句:「must, _acked = _drift_split_acked(must, acks, vault_rel)」
- `_retire_lines` 回傳的原文是 `_ns_summary_logical` 接回續行後的整行。
- `cmd_drift_ack` 記下的是第 N 行的實體行(`"text": lines[line - 1].strip()`),見 file: `scripts/lumos:30497`。
- `_drift_split_acked` 比的是「路徑 + 一字不差的原文 + 種類」。
- 回頭條件不會中這個洞,因為 `_probe_lines` 回的是實體行 `ln.strip()`。
- 最小重現(已實跑):摘要寫成下面兩行,`_retire_lines` 回的原文是 `RULE:要人簽 [since:2026-09-01] [retire:when-file:src/new.py]`。ack 記的卻是 `RULE:要人簽 [since:2026-09-01]`,兩者永遠不等。
  ```
  RULE:要人簽 [since:2026-09-01]
    [retire:when-file:src/new.py]
  ```
- 欄位寫在續行的 RULE 在摘要裡很常見。
- 修法:`_retire_lines` 另外回實體第一行當 ack 比對用的 text,或讓 ack 對 retire 種類改用同一個接回續行的函式。
引句:「out.append((no, line, _probe_parse("[" + vals[0] + "]")))」

**C2** 已設 `drift_check.gate=warn` 的專案,升級後 retire 沒寫設定仍預設 block,等於這個專案的「只提醒」被新檢查繞過。
severity: minor
blocking: 否 — 預設 block 是設計給的,影響面是舊專案的升級驚喜。⚠ 是否該讓 retire 預設跟 gate 走,我判不準。
引句:「rt_mode = _drift_config_text_parts(cfg_text)["retire"] if mode != "off" else "off"」
- 對照組 `old_sentence` 預設是 warn,不是 block。
- doctor 的 `_drift_doctor_lines` 在 `explicit and mode != "block"` 時說「推送不會被擋」,對 retire 不成立。
- `retire=off` 或 `warn` 時 doctor 也沒有任何一句話講到。

**C3** 核心判定吃滿 60 秒時,retire 實際上一條都沒判,而且訊息講錯原因。
severity: minor
blocking: 否 — 設計接受判不了只列出,問題在原因寫錯、使用者以為是 git 壞了。
引句:「left = min(_DRIFT_RETIRE_BUDGET_SEC, max(0.0, _DRIFT_BUDGET_SEC - (time.monotonic() - t0)))」
- `left` 為 0 時,`_drift_tree_env` 內部 `max(1, …)` 只給 1 秒。
- 讀不到就走 `must, unknown = [], ["git 讀不出被推送頂端的筆記(撤除條件)"]`,實際是預算用完。
- 就算讀到了,`_drift_probe_check` 內的 `over` 文字也寫成「超過 60 秒預算(條件式回頭條件)」,對 retire 是錯名。
- 大推送(核心最慢)正好是 retire 整段被跳過的情境,只在 stderr 有一行。
引句:「must, unknown = [], ["git 讀不出被推送頂端的筆記(撤除條件)"]」

**C4** 我走過的其他輸入,沒找到具體失敗。
- 同篇有 REVISIT 與 RULE 兩種條件:各自呼叫、各自新建 `base_lines` 快取,不會混。`[retire:when-…]` 不會被 `_PROBE_ANY_RE` 的 `\[when-` 吃到,也不會重複判。
- 改名:`_drift_probe_old` 沿用同一個改名對照,行為不變。
- 一行兩個 retire:實跑確認不抽。
- 起點沒作廢、終點作廢:終點不抽,所以不擋;反過來(復活)當新條件判。
- `by` 缺漏:retire 不需期限,`bad` 不含缺期限,照評估。
- 例外兜底:`except Exception` 只吞一般例外,合理。
- 新舊互讀:舊程式讀新帳時 `_drift_load_acks` 會濾掉 `retire` 種類,無害。
- `_esc_clean` 有套在判不了的清單上。

## 2. 圖譜鏡頭(固定席與直接節點)

- 家節點 `Systems/存量漂移守衛` 是這次改動的家:新增的 WHY 行有出處和 `[test:]`,內容與程式一致。
  - 其「判定另開、不放進 `_drift_check_core`、不改考試與歷史重放基準」的合約,這次有守住,見第 3 項。
  - 它的「判不了算要處理」是針對核心 probe 的;retire 判不了只列出,新 WHY 行已明講差別,不衝突。
- `Projects/筆記格子寫法與過期檢查_計劃` 第 2 步的敘述與程式吻合。
  - 「drift scan 種類第 3 步才加」對應 `_DRIFT_SCAN_KINDS` 排除 retire,一致。
  - 進度行寫「第 2 步實作中」,合理。
- `Projects/舊句檢查_計劃`、`Projects/存量漂移防線_計劃`、`Projects/否定現況句配回頭條件_計劃`:共用 `_drift_probe_*`。
  - 沒傳 `extract/kind` 時預設值與原程式逐字等價,所以它們宣稱的行為不變。
- 固定席的 INVARIANT 與 RISK 節點(`lumos-cli-read`、`bound-tests-gate`、`guard-kill`、`授權與歸屬`、`測試假綠形態`、`lumos-cli-lifecycle`、`design-loop`、`節點範圍與索引守衛`、`canary-audit`、slim 系列等):
  - 不影響:這份 diff 只在 `cmd_drift_check` 尾端加一段、擴充 `_drift_probe_*` 的可選參數,並新增設定鍵與帳目欄位。
  - 沒碰到它們各自守的流程(授權、安裝器、節點範圍索引、guard 殺傷、錨點、可逆性帳)。
  - `reversibility-governance-ledger` 與逃逸自動記:`_gate_event_or_warn` 的 `extra={"check":"retire"}` 是既有參數,不改帳的結構。
- 一個圖譜缺口:C1 的 ack 路徑是 `存量漂移守衛` 描述的「照留要表態」合約,這次實作讓它對續行 RULE 失效,應修程式,不是改筆記。

## 3. 本案特定鏡頭

**C5** `t_slots_retire_when_push` 的 ①到⑥ 咬得住,⑦ 沒咬住它自稱的東西。
severity: minor
blocking: 否 — 核心斷言有咬,缺口在宣稱的預算語意與 C1 這類互動沒覆蓋。
引句:「check("⑦撤除條件在回頭條件之後另跑一次(不吃它的時間)", calls == ["probe", "retire"], str(calls))」
- ⑦ 只驗呼叫順序,不驗「不吃回頭條件的時間」。把 `left` 寫死成 0 或 `_DRIFT_BUDGET_SEC`,這個測試都不紅。
- 其餘幾項我只用讀程式推演,沒拿掉判斷重跑:
  - ①③ 靠拿掉 `_drift_retire_guarded` 會紅。
  - ② 靠 `_drift_probe_old` 沒傳 `extract`,基準 set 為空,`old` 變 False,轉成擋,所以會紅。
  - ④ 靠拿掉作廢跳過,終點行重新被抽出而擋。
  - ⑥ 靠把判不了算擋,rc 變 1。
- 完全沒覆蓋的:
  - ack 流程,所以 C1 漏掉。
  - 續行與欄位在續行。
  - 改名。
  - 例外兜底。
  - `gate=off` 加 retire 預設。
  - `gate=warn` 時 retire 預設行為(C2)。
  - 預算用完的路徑(C3)。

既有回頭條件基準方面,`_drift_probe_check`、`_drift_probe_candidates`、`_drift_probe_old` 的新參數預設值等價於原邏輯(`extract or _probe_lines`、`kind="probe"`)。`must` 的 kind 預設仍是 "probe",考試與歷史重放走的 `_drift_check_core` 沒被動,所以基準不變。`_DRIFT_KINDS` 多一個 retire,只影響 `--kind` 的 choices 與 ack 載入,不影響 scan 計數。

最高嚴重度 major,blocking 1 條
