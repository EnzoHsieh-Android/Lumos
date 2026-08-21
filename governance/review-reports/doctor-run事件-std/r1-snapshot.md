---
type: project
status: doing
created: 2026-08-21
updated: 2026-08-21
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/檢核收緊五件_計劃]]"
---
# doctor-run事件_計劃

> 白話:巡檢(`doctor --ci`)現在**只在有警告時才記帳,乾乾淨淨跑完一次不留任何紀錄**。所以帳本永遠分不出「這問題修好了」跟「這問題還在」。本案讓每次 `--ci` 都固定寫一筆「我跑過了」——幾行程式,是 [[Projects/檢核收緊五件_計劃]] 棘輪的地基,先做。

## 緣起

[[Projects/檢核收緊五件_計劃]] r3 三席(同門 s3、外家 s6/s7)獨立抓到:`_append_governance_log` 對零事件直接 return(scripts/lumos:421-424),「run」在帳裡沒有獨立存在。棘輪案達 cap 未收斂,拆案後本件為第一步。

## 新機制準入三問

1. **真事故?** 有:2026-08-21 L4 清帳把 30 個節點的 check-s 全清零之後,帳本上**看不出「已清」**——最後一筆仍是清零前的警告,任何讀帳的人/工具都會以為它們還在被念(gov-stats 案 r2 亦把「末見 7 天內」誤當「仍在被念」,正是同一個盲點)。
2. **風格偏好?** 否——「一次執行有沒有發生」是事實,不是美感。
3. **既有小修?** 是:`run_doctor` 的 `--ci` 落帳點加一筆固定事件;`_append_governance_log` 不改(有事件就會寫)。新增=一個 gate 字面值 `doctor-run`。

PRIOR-ART: ① 最小解=落帳點加一筆;② 世界解=CI 系統的 run record / heartbeat——「執行本身是一筆紀錄,結果是它的屬性」;③ borrow-design。

## 設計

- `run_doctor(... ci=True)` 在既有 `_append_governance_log(env.vault, gov_events)` 之前,**無條件**在 `gov_events` 末尾加 `{"gate": "doctor-run", "kind": "ran", "hard": False, "nodes": [], "note": "issues=<n> gates=<本次有事件的 check-* gate 數>"}`(★欄位名 `note`——`cmd_gov` 的 governance mapper 讀 `d.get("note")`,不是 `detail`;light r1 M1★)。乾淨 run 因此恆有一筆可寫。
- **不改判定、不改 rc、不改純 `doctor`**(仍不寫帳)。
- `gov` 時間軸(非 `--full`)**明確過濾** `gate == "doctor-run"` 的列(★在去噪摺疊之前、以 gate 名直接濾,不是靠 `_is_advisory` 摺疊——該摺疊只認 `kind=="warned"`,新事件是 `ran` 不會被折;light r1 B1★);`--full` 與 `--stats` 照列(stats 要看得到它才能當棘輪分母)。`node` 縮限模式下 nodes 為空本就不命中,無需特判。
- `_KNOWN_GATES` 加 `doctor-run`;`_STATS_NODE_SEMANTICS` 不需(nodes 空,stats 印 n/a)。
- dedup 鍵含 commit,同 commit 多次 `--ci` 在 `gov` 顯示上折成一筆;★帳本原始行保留每一次★(棘輪讀原始行)。

## 範圍刀

不做棘輪本身;不回溯補歷史 run;不改 `_append_governance_log` 的零事件 early-return(由呼叫端保證非空)。

## 審計修正紀錄

- **light r1(2026-08-21,1 席通才)**:blocker 1(「隱藏」無機制定義,`_is_advisory` 只折 warned)/major 1(事件鍵 `detail` 應為 `note`)。兩條存活 → ★light 誤判,依規則升 standard,開 `doctor-run事件-std`★。

## light 資格自核(★已 ratchet 升 standard,本段留作紀錄★)

不碰金流/對外送/不可逆/守衛面判定(只加一筆帳,不改任何閘的裁決);不動 ★INVARIANT★;預估 <20 行含測試;非演算法密集 → 走 light。

## 測試(TDD)

1. `t_doctor_ci_writes_run_marker`:乾淨 vault `doctor --ci` → 帳本恰一筆 `doctor-run`,detail 含 `issues=0`。
2. `t_doctor_plain_still_silent`:純 `doctor` 不寫(既有 `gov-log: 純 doctor 不寫` 照樣綠)。
3. `t_gov_hides_run_marker_unless_full`:`gov` 不印 `doctor-run`;`gov --full` 印;`gov --stats` 列出。
4. `_KNOWN_GATES` 漂移測試自動逼 `doctor-run` 入表。

## 實務隱患

併發——append 同既有路徑。效能——每次 --ci 多一行。資源——既有 with-open。風險類:self-governance——不擋任何東西,無誤擋;★反向:多一種事件會不會汙染 `gov --stats` 的「未出現清單」邏輯?不會——它是出現的 gate,只會多一列★。已排除:金流/外送/不可逆/PII。
