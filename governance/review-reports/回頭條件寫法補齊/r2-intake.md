# 回頭條件寫法補齊 r2 收貨

席位:通才 8(U1–U8)、正確性 8(C1–C8)、邊界輸入 6(B1–B6)、架構對齊 5(Z1–Z5);共 27 條,blocking 6(C1、C2、C3、B1、B2、U3)。四席引句全數錨定。架構對齊席 Z4 原報 `severity: minor` 配 `blocking: 是`,兩欄矛盾,退回該席重判,該席改成 minor/否(檔首不變);編排者沒動報告。四席交齊才動計劃。

## 依根因分組

1. 結案標記位置限死、寫在行尾靜默失效(C3、B5、C6、B4、C7、U3、Z2)→ REVISIT 行上任何位置都認;一支 `_revisit_closed` 掃整行(一行兩個不論位置都算錯;日期先比形狀再 fromisoformat);`_probe_parse` 只跳過、`_PROBE_LEAD_RE` 同步;還原後夾在中間的標記寫進回滾。
2. 句中清單併進「不評估」清單的副作用(C1、U2、Z3、B1)→ 另一支 `_revisit_misplaced_lines` 只給 Z 段。
3. Z 段也受 3 條上限(U1、C4)→ 接在 Z 段第一行。
4. 同一行第二個 REVISIT 漏看(B2)→ 一行逐處看,行首正牌那處不算。
5. RETIRE-IF 量不到(C2、Z4)→ 擋下與提醒事件多記 `rules`,撤除條件改成量得到的形狀,新增 [S12]。
6. 引號判定(U7、B3)→ 在一對引號裡面才算範例。
7. 提示與既有測試(U5、U4、C5、Z5)→ 日期式與條件式同一句;`t_doctor_revisit_reminder` 同步改;已結案不進 E5 件數。
8. 重新打開(U6)→ 寫明會被點名「這次新寫…已經成立」。
9. 呼叫順序(U8)→ 每個區塊都先算 `_revisit_split`。
10. `drift fix` 平行路徑(C8、B6)→ 寫進相容。
11. 條件式兩個入口(Z1,minor)→ 附理由放行:r1 已寫明 drift ack 與結案標記的分工判準,drift ack 拒收已結案的行;兩者是不同意圖(留著提醒 vs 不用回頭),機械上分不出意圖,判準留給作者。

## 重現表

| id | 怎麼查 | 結果 | 去向 |
|---|---|---|---|
| C1 | 讀 `_drift_doctor_lines` 的 `n_dead`、`_drift_probe_scan` 把 dead 併進 probs | HIT | 折(第 2 組) |
| C2 | 讀筆記形狀擋擋下事件的 note 只有總數 | HIT | 折(第 5 組) |
| C3 | 讀 r1 稿〈做法〉2.1「其他位置不認、當普通文字」與第 4 點只報 errs | HIT | 折(第 1 組) |
| C4 | 讀 `warn_soft` 的 `_SOFT_CAP` 對 Z 段同樣適用 | HIT | 折(第 3 組) |
| C5 | `grep` 到 `t_doctor_revisit_reminder` 比對「日期改下一次或刪行」 | HIT | 折(第 7 組) |
| C6 | 讀 r1 稿「一行最多一個」與「其他位置不認」 | HIT | 折(第 1 組) |
| C7 | 讀 `_PROBE_LEAD_RE` 只列 when-/by | HIT | 折(第 1 組) |
| C8 | 讀 `drift fix` 寫入前跑第一層回頭條件檢查 | HIT | 折(第 10 組) |
| B1 | 同 C1 | HIT | 折(第 2 組) |
| B2 | 讀 `_revisit_split` 只解析第一個 `REVISIT:`,date 分支直接回 | HIT | 折(第 4 組) |
| B3 | 讀 r1 稿「前面緊鄰的字元」 | HIT | 折(第 6 組) |
| B4 | `fromisoformat('20261003')` 在 3.14 合法(席位實跑) | HIT | 折(第 1 組) |
| B5 | 同 C3 | HIT | 折(第 1 組) |
| B6 | 同 C8 | HIT | 折(第 10 組) |
| U1 | 同 C4 | HIT | 折(第 3 組) |
| U2 | 同 C1 | HIT | 折(第 2 組) |
| U3 | 讀 r1 稿 `_probe_parse` 多認鍵與 `_revisit_closed` 兩處解析 | HIT | 折(第 1 組) |
| U4 | 同 C5 | HIT | 折(第 7 組) |
| U5 | 讀 r1 稿提示只寫日期式範本 | HIT | 折(第 7 組) |
| U6 | 讀 `_drift_probe_old` 起點用 `_probe_lines` 抽同一條 | HIT | 折(第 8 組) |
| U7 | 同 B3 | HIT | 折(第 6 組) |
| U8 | 讀 `_ns_revisit_violations` 非正文區塊不呼叫 `_revisit_split` | HIT | 折(第 9 組) |
| Z1 | 讀計劃〈做法〉2.6 分工判準 | HIT | 放行(第 11 組) |
| Z2 | 同 U3 | HIT | 折(第 1 組) |
| Z3 | 同 C1 | HIT | 折(第 2 組) |
| Z4 | 同 C2 | HIT | 折(第 5 組) |
| Z5 | 讀 E5 件數與開段條件 | HIT | 折(第 7 組) |
