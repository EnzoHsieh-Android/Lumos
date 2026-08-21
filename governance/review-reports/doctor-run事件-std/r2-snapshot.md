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
- ★「已清」的判讀方式★:本事件**不**列受檢節點(nodes 恆空);「某節點已清」由讀帳方推導=「該 run 有 doctor-run 標記,但該 run 內沒有該節點的 check-* 事件」。run 標記只負責把 run 的邊界畫出來(外家 r1 #1 的誤讀,明講)。
- `gov` 時間軸(非 `--full`)**明確過濾** `gate == "doctor-run"` 的列——★過濾只作用在**顯示迴圈的印出動作**(摺疊與逐行印兩處各自 `continue`),**絕不改動 `ded` 列表本身**:`ded` 與 `_render_gov_stats` 共用同一個變數,在摺疊前對 `ded` 濾會把它從 `--stats` 裡一併濾掉,正好殺掉它當棘輪分母的用途(std r1 s1 major)★;不是靠 `_is_advisory` 摺疊(該摺疊只認 `kind=="warned"`;light r1 B1);`--full` 與 `--stats` 照列(stats 要看得到它才能當棘輪分母)。`node` 縮限模式下 nodes 為空本就不命中,無需特判。
- `_KNOWN_GATES` 加 `doctor-run`;`_STATS_NODE_SEMANTICS` 不需(nodes 空,stats 印 n/a)。
- dedup 鍵含 commit,同 commit 多次 `--ci` 在 `gov` 顯示上折成一筆;★帳本原始行保留每一次★(棘輪讀原始行)。

## 範圍刀

不做棘輪本身;不回溯補歷史 run;不改 `_append_governance_log` 的零事件 early-return(由呼叫端保證非空)。

## 審計修正紀錄

- **std r1(2026-08-21,三席同門+外家 gemini)**:major 1(s1:過濾落在 `ded` 上會連 stats 一起濾掉,測試只斷 gate 名會假綠)+ minor 4;外家 4 條採 2(2 條引句不合格):#2 測試段殘留 `detail` 屬實;#1「nodes 空→看不出已清」屬誤讀,但暴露 spec 沒講清楚「已清」怎麼推導,補明。s3 消費者席順帶查出既有問題:vault 範本 `.gitignore` 列了帳檔但放錯層(`docs/<slug>-knowledge/.gitignore` vs 帳檔在 `docs/`),故帳檔實際被追蹤——非本案引入,記入 [[Issues/寫下風險當成處理風險]] 類待辦。
- **light r1(2026-08-21,1 席通才)**:blocker 1(「隱藏」無機制定義,`_is_advisory` 只折 warned)/major 1(事件鍵 `detail` 應為 `note`)。兩條存活 → ★light 誤判,依規則升 standard,開 `doctor-run事件-std`★。

## light 資格自核(★已 ratchet 升 standard,本段留作紀錄★)

不碰金流/對外送/不可逆/守衛面判定(只加一筆帳,不改任何閘的裁決);不動 ★INVARIANT★;預估 <20 行含測試;非演算法密集 → 走 light。

## 測試(TDD)

1. `t_doctor_ci_writes_run_marker`:乾淨 vault `doctor --ci` → 帳本恰一筆 `doctor-run`,`note` 含 `issues=0`(★鍵名 `note`,與設計一致;外家 r1 #2 抓到測試段殘留 `detail`★)。
2. `t_doctor_plain_still_silent`:純 `doctor` 不寫(既有 `gov-log: 純 doctor 不寫` 照樣綠)。
3. `t_gov_hides_run_marker_unless_full`:跑兩次 `doctor --ci`(不同 commit)→ `gov` 不印 `doctor-run`;`gov --full` 印兩行;★`gov --stats` 的 `doctor-run` 列去重筆數 **== 2**(斷數字,不只斷 gate 名出現——否則濾錯 `ded` 的實作會假綠)★。
4. `_KNOWN_GATES` 漂移測試自動逼 `doctor-run` 入表。

## 實務隱患

併發——append 同既有路徑。效能——每次 --ci 多一行。資源——既有 with-open。風險類:self-governance——不擋任何東西,無誤擋;★反向:多一種事件會不會汙染 `gov --stats` 的「未出現清單」邏輯?不會——它是出現的 gate,只會多一列★。已排除:金流/外送/不可逆/PII。
