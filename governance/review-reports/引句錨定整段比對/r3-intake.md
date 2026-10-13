# r3 收貨紀錄(6 席全新,上限最後一輪)

## 引句錨定狀況

quote-check:最壞時序、回滾、架構對齊三席全數錨定(載體選回滾);正確性 6/14、邊界 3/11、接手的人 1/11 句錨不到,原因同前兩輪(被審計劃含巢狀引號與示範引句字樣)。

## 機械重現表

| 群 | 涵蓋 finding | 重現命令/查證 | 結果 |
|---|---|---|---|
| unclosed 二次方 | B1 C3 | 正確性席照規則 3 字面實作量 1000/2000/4000 個標籤:0.12/0.47/1.88 秒;邊界席量 500/1000/2000:0.03/0.13/0.52 秒,每翻倍約 4 倍 | HIT(兩席獨立實測) |
| 設定壞值與壞 JSON 靜默失效 | B2 R3 | 回滾席在沙盒寫尾逗號壞 JSON 呼叫 `_bound_tests_parallel` 回 1 且 stdout/stderr 皆空;邊界席實測 `['a'] in {'legacy','full-span-v1'}` 丟 TypeError | HIT |
| 隔離閥與壞章優先序、診斷指令 | B3 R6 | 讀 r3-snapshot 讀章規則與 read_override 兩段無優先序;`--rule <章>` 對不認得的章會被 choices 拒絕 | HIT |
| 隔離閥開著時凍結 | T1 R1 R2 R4 | 讀 `scripts/lumos` `cmd_loop_replay` 凍結只擋 rc2;`governance/autonomous_loop/replay_weekly.py` 第一步自動補凍;現有 305 個 golden 有 5 個 rc1 | HIT |
| 寫側求 kind 時另一版丟例外 | T2 | 讀 r3-snapshot「由寫側同時用另一版判準算一次」未要求例外處理;`_gate_event_or_warn` 只包住寫入 | HIT |
| 截斷害 seat-check | C1 T3 | 讀 `scripts/lumos` `cmd_seat_check` 用 `q["quote"]` 經 `_quote_norm` 比材料;r3-snapshot 規則 6 的截斷套在每條 | HIT |
| 第一階段預設無測試、第二階段沒接電 | C2 H1 H2 | grep `scripts/test_lumos.py` 的 `_qfs_project` 全寫 write_rule=full-span-v1;計劃無盯第二階段的 REVISIT | HIT |
| --since 極端值與 ts 型別 | B4 | 邊界席實測 gov 的 timedelta 在 N=10**10 丟 OverflowError;`_loop_ts_key(123)` 丟 AttributeError | HIT |
| 比較指令記憶體 | B6 | 邊界席統計 952 份快照約 286MB | HIT |
| 根目錄來源 | A1 A2 T6 | `scripts/lumos` quote-check/seat-check 為 vault-free 無 --repo;severity-check 先例用 --repo 預設「.」 | HIT |
| 其餘細節 | A3 A4 A5 A6 B5 B7 C4 C5 C6 C7 C8 H3–H11 R5 R7 R8 T4 T5 T7 | 逐條讀 r3-snapshot 對應段與 `scripts/lumos`、`scripts/test_lumos.py` 對應行 | HIT(規格未定義或測試缺口) |

## 處置

- 折入 47 條(全部),寫進第四版。
- 放行:無。refuted:無。
- 第三輪是上限最後一輪且仍有 major;使用者 2026-10-13 裁破例第 4 輪(cap-decision extra-round)。
