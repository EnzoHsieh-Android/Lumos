# code-過期鎖安全接手 r1 收貨與處置

凍結審材：`r1-snapshot.patch`，SHA-256 `43e265ffd8b4a01aa7655160216cd07b4952e0af5bb4ac4c1d8add80d5b19302`，1588 行。兩席獨立唯讀讀同一份快照，收齊後才改碼。代碼席最高 major 三條；架構席最高 minor 一條。外家席這輪不可用，故結論只稱同家族視角。逐字引句與原始報告在同目錄，`quote-check`、`refcheck`、`report-normalize` 均核對。

| id | 現象重現 | 處置 |
|---|---|---|
| C1 | HIT：`lock_error` 被 hook 吞下後未 `mark`，事件帳回 `ok`。新增測試先紅，修後 `mark("error", …)`，測試綠。 | folded |
| A1 | HIT：架構席獨立找到與 C1 相同的 telemetry 缺口。 | folded，同 C1 |
| C2 | HIT：fake object 在 `lstat` 和 `unlink` 間替換名稱可刪新鎖；但這個 fake 不是同版鎖協議的直接路徑。辯方核對：同版 vault 未取得者不刪舊鎖；lens 原本有「非持有者見快取便刪鎖」的同版入口，已以先紅後綠測試改成只由本次取得者在快取命中時清鎖。舊版程序或人工換檔仍可製造理論窗口，本計劃 S6 明定混版未保證，實際切換前須停舊版。 | folded，同版可達刪鎖入口已收緊；跨版本殘餘列為進場條件 |
| C3 | HIT：S1 原斷言只拒絕雙 True，未核對雙 False 與原鎖內容。已強化同一跨程序測試。 | folded |

額外機械閘：`code-loop check` 的 59 支受影響合約測試全綠，但新增 C901 `_lens_wait_or_warm` 複雜度 15>10；抽出背景啟動與超時說明兩支同層 helper 後，差異告警須重跑確認為零。這是本輪修補帶來的回歸風險，下一輪看新 patch 的 delta，不只重看原問題。
