severity: major

## 第一問:分層與依賴方向

這一問沒有 major。`_doctor_cfg_bytes` 沒有找到漏改的第四份副本,這點是對齊的。`_note_shape_doctor_lines`、`_note_audit_doctor_lines`、`_drift_gate_doctor_lines` 三處的內嵌副本都已換成它。其他讀 `.lumos/config.json` 的函式(`load_symbol_profile`、`load_test_profile`、`load_platforms`、`_note_lint_config`)不是 doctor 提醒,各自走設定載入,不算不一致。

S17、S19 改用 `_dref_parse`/`_dref_norm`、`_ns_superseded`,方向是往既有函式收斂,對齊。`_lint_new_config(root)["mode"]` 我核對過,`_LINT_NEW_DEFAULTS` 的鍵確實叫 `mode`。

**R2A1**
severity: minor
blocking: 否 — S16 取全文的路徑和 S17 到 S19 不同,但結果等價,只是讀法分成兩條。
引句:「for t in _ns_summary_logical("---\n" + "\n".join(n.fm_lines) + "\n---\n").values():」
`_doctor_stale_rules(notes)` 只收 `notes`,所以用 `n.fm_lines` 假造一份 `---` 包起來的全文。S17 到 S19 走的是 `_slot_summary_entries`,內部用 `env_text(env, rel)`。整個 repo 只有這一處這樣重組全文,別處讀筆記全文都是 `env_text` 或 `_note_from_text`。⚠ 如果改成讓 S16 也收 `env`,就能走同一條路。
佐證行 file: `scripts/lumos:3439`
對照 file: `scripts/lumos:3507`、`scripts/lumos:716`

## 第二問:命名與錯誤處理

**R2A2**
severity: minor
blocking: 否 — S18 的 fail-open 寫法和帳增速段的呈現不同,不影響行為。
引句:「ok(f"度量式撤除條件這次算不出來,跳過(fail-open:{type(_e18).__name__})")」
既有的三段是整段包 try,except 裡印 `ok(f"…跳過(fail-open:{_e})")`,帶的是例外全文。S18 只帶型別名,又多了 `_met18 = None` 加 `if _met18 is None: pass` 的分支。這是這個專案 doctor 裡唯一的「try 只包計算、except 後再分支」寫法。
佐證行 file: `scripts/lumos:2530`
對照 file: `scripts/lumos:2101`、`scripts/lumos:2027`、`scripts/lumos:1932`

**R2A3**
severity: minor
blocking: 否 — 同一組 doctor 軟段,有的提醒行清控制字元,有的沒清。
引句:「out.append(_esc_clean(f"{rel}:{no}:[被取代:{v[:40]}] {why}", 300))」
這次新增的 S17 到 S19 提醒行都過 `_esc_clean(…, 300)`。S16 的 `lines.append(f"{rel}:{why}:…")` 是同一輪被碰到的函式,卻沒清。`_esc_clean` 預設上限是 200,這裡全寫 300,是新的魔術數。⚠ S16 那行是舊碼、不是這次 diff 新增的,所以只列 minor。
佐證行 file: `scripts/lumos:3559`
對照 file: `scripts/lumos:3453`、`scripts/lumos:10442`

## 第三問:第二種做法

**R2A4**
severity: major
blocking: 是 — 推送那支引入了第二套 stderr 處理,而且這個專案其他地方都沒有同一套。
引句:「"""印一句到 stderr;stderr 本身壞了(管線關掉)也不往外拋。"""」
`_drift_retire_quiet` 是 repo 裡第一個「print 到 stderr 失敗也吞掉」的小工具。同一道閘的 `_drift_m1_guarded` 最後一層兜底直接 `print(..., file=sys.stderr)`,沒包保護。`_drift_report_must` 的 print 也沒包。`_gate_event_or_warn` 失敗時也是直接 print。這次它還被用在 `_drift_retire_guarded` 的 except 開頭,以及 `_drift_retire_report` 兩處。⚠ 設計理由(stderr 關掉時不要把判定帶倒)有道理,但做法只落在 retire 一支,不是專案共通規矩。要嘛 m1 與 core 也一起收斂,要嘛 retire 退回與 m1 同一寫法。
佐證行 file: `scripts/lumos:32396`
對照 file: `scripts/lumos:33392`、`scripts/lumos:33407`、`scripts/lumos:1234`

**R2A5**
severity: minor
blocking: 否 — 記帳與印出的先後,和同一閘的 m1、core 相反。
引句:「先記帳再印(印到一半被中斷,擋下的那筆帳也已經在;r1 併發資源席),有成立或判不了才記一筆」
`_drift_m1_report` 與 `_drift_report_must` 都是先印、最後才記帳(`_drift_m1_ledger` 在函式尾端)。retire 改成先記帳再印,並且把記帳包 `try/except Exception`。m1 與 core 的記帳都沒包,因為 `_gate_event_or_warn` 自己已吞寫入失敗。m1 還有 `_drift_m1_ledger_miss` 留痕,retire 沒有。三條路徑的順序和兜底層數不一樣,讀的人要記三套。
佐證行 file: `scripts/lumos:32418`
對照 file: `scripts/lumos:33433`、`scripts/lumos:32479`、`scripts/lumos:1234`

**R2A6**
severity: minor
blocking: 否 — `_drift_retire_guarded` 的兜底層級和 m1 不同,屬於註解已承認的差異。
引句:「跟 m1 的分法不同(m1 的扣表態在 report 裡、整支一個兜底):這支的 rc 要在印之前定,所以扣表態放進判定那一半」
m1 的兜底是「例外轉成 state=error,再走一次 report」。retire 是「例外轉成一句話加一筆 null 帳,回 0」。註解已說明這是故意的,所以只列 minor。有誤報風險的是:兜底回 0 不擋,而 m1 的 block 模式遇到判不了是擋。這是既有設計(retire 計劃說判不了只列不擋),不算這次新增。
佐證行 file: `scripts/lumos:32380`
對照 file: `scripts/lumos:33392`

不對齊共 6 條,其中 major 1 條
