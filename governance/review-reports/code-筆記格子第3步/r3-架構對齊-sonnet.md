severity: minor

**審查範圍**:`/tmp/code3-r3.patch`,對照 repo `scratchpad/rw`。上一輪四條指出項的收斂結果如下。

| 上一輪指出項 | 判定 | 依據 |
|---|---|---|
| 第二套 stderr 處理 | 收斂。 | 小工具 `_drift_retire_quiet` 已刪,全改成直接 `print(..., file=sys.stderr)`,與 `_drift_m1_report` 同一寫法。 |
| S16 第二條讀法 | 大致收斂。S16 到 S19 都走 `_note_summary_entries`,但漂移閘那幾支另有一條讀法,見 R3A1。 | |
| S18 fail-open 寫法不同 | 收斂。 | |
| 先記後印與鄰居相反 | 收斂。 | `_drift_retire_report` 改成先印後記,與 `_drift_m1_report` 的順序相同。 |

**①分層與依賴方向**
- 依賴方向沒有新的跨層直呼。
  - `_note_summary_entries` 放在 doctor 那一層,往下呼叫既有的 `_ns_summary_logical`。這個方向與原本 S16 的寫法相同(`scripts/lumos:3505`、`scripts/lumos:27845`)。
  - `_slot_summary_entries` 改成直接取 `env.notes[rel]`(`scripts/lumos:3518`),不再繞 `env_text`。鄰居也是直取 `env.notes[rel]`(`scripts/lumos:733`、`5790`),所以方向一致。
- 讀筆記全文與欄位的分工,有一處值得標出來,即 R3A1。
  - doctor 這一側已經統一走 `n.fields` 加 `n.fm_lines`。
  - 漂移閘這一側仍用原始全文呼叫 `_ns_summary_logical`:`_retire_lines`(`scripts/lumos:30596`)和 `scripts/lumos:31433`、`31456`。這些路徑不補單行 summary。
  - 兩側的輸入不同(樹上全文對上 Note),所以不算結構錯誤。
  - 但「單行 summary 照判」這個行為只有 doctor 側有。

**②命名與錯誤處理**
- `_DOCTOR_LINE_MAX` 的命名接近既有的 `_X_LINE_MAX` 和 `_X_MAX`(`scripts/lumos:32542`、`29375`)。它取代了 doctor 各段散落的字面值 300,是收斂方向。不過常數定義在 `scripts/lumos:3497`,而第一個使用處在 `scripts/lumos:3447`,位置在使用之後。既有常數慣例是放在使用它的函式之前,這是排序上的小差異。
- S18 的 fail-open 現在與帳增速段(`scripts/lumos:2101`)和 `scripts/lumos:1932`、`2027` 同形:把 `warn_soft` 與 `ok` 放進 `try`,`except` 只印 `ok(f"…觀測跳過(fail-open:{_e18})")`。唯一的小差異是變數名 `_e18`,這是各段慣用的命名。
- `_drift_retire_report` 的外殼不同於 m1。
  - 它對印出和記帳各包一層 `try`。
  - `_drift_m1_report` 沒有這些內層 `try`,整支交給 `_drift_m1_guarded` 兜底,最後一層 `print` 也裸著。
  - 註解已說明理由:retire 的 rc 要在印出前定下來。結構上仍有兩種寫法,但新寫的註解有明講,只列為 minor。
- `_lint_new_config(text, from_snapshot)` 的參數名和語意都照 `_nodehome_config` 的同名參數(`scripts/lumos:25554`)。實作形狀略有不同:前者用巢狀條件式取 `raw`,後者用 `if/else` 分支加提早 return。另外 `from_snapshot=False` 時沒有 `_nodehome_config` 那段捷徑檔守衛,但這是改動前就有的差異,不是這次引入的。

**③第二種做法**
- `_drift_jsonl_iter` 是 `scripts/lumos` 裡既有 yield 用法之外的新 generator,但包法正確:`_drift_jsonl_parse` 直接 `return list(_drift_jsonl_iter(raw))`,只有一份解析邏輯,沒有第二套切行規則。
  - 這次只把 doctor 兩處(`scripts/lumos:2057`、`3602`)換成 iter。
  - `scripts/lumos:7900`、`12124`、`31289`、`31513` 仍用 list 版。這是合理的,因為它們需要整份清單,所以不算第二種做法。
- `scripts/lumos:2055` 的註解還寫「走 `_drift_jsonl_parse`」,實際已呼叫 `_drift_jsonl_iter`。這是註解沒跟上的小殘留,見 R3A2。
- 測試檔 `t_slots_doctor_reminders_r2` 用 `m._doctor_metric_lines = boom` 搭配 `try/finally` 還原。
  - 檔內多數 monkeypatch 用 `mock.patch.object`(`scripts/test_lumos.py:11399` 起)。
  - 也有 in-process 的 `orig = m...` 手動還原寫法(33 處),所以這一處不構成第二種做法,不列。

**R3A1**
severity: minor
blocking: 否 — 兩條讀法輸入來源不同,漂移閘不判單行 summary 只是漏判,不會誤擋。
引句:「區塊寫法(summary: |- 加縮排行)用 _ns_summary_logical 從開頭行重組;summary 寫在同一行(含引號)時,」
佐證: `scripts/lumos:3500`(新增的 `_note_summary_entries`)對照 `scripts/lumos:30596`(`_retire_lines` 仍直接呼叫 `_ns_summary_logical(text)`,不補單行)。
⚠ 判不準是否算第二種做法:輸入不同(Note 對樹上全文),但同一個概念「摘要前綴條目」現在有兩種讀法,而且對單行 summary 的行為不同。

**R3A2**
severity: minor
blocking: 否 — 只是註解跟程式不一致,不影響行為。
引句:「# 逐行解析走帳檔共用的 _drift_jsonl_parse(只在 \n 切行、壞行與非物件略過),跟度量段(S18)同一種讀法」
佐證: `scripts/lumos:2055`(此註解在 diff 中屬未改動的 context 行,而它下一行已改成呼叫 `_drift_jsonl_iter`)。

不對齊共 2 條,其中 major 0 條
