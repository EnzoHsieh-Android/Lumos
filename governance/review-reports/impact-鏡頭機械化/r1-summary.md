# r1 五席彙總(impact-鏡頭機械化)
severity: blocker

五席獨立審 v1 spec,一致結論=方案選錯,全部折入 v2 重寫(無放行條目)。

| 席 | 結果 |
|---|---|
| 正確性(claude/sonnet) | 1 blocker + 6 major + 5 minor;blocking 8 條 |
| 邊界可執行(claude/sonnet) | 1 blocker + 6 major + 1 minor;blocking 7 條 |
| 整合/知識同步(claude/sonnet) | 1 blocker + 8 major + 1 minor;blocking 9 條 |
| 架構對齊(claude/sonnet,不佔人數) | 3 major + 1 minor |
| 外家否決(codex/external) | 否決成立,severity blocker |

三個 blocker 同源:seat-check 只做檔名字串比對(實跑證明:列一個不存在的 manifest + 報告寫一句檔名 → 全綠 rc0),且只讀頂層 materials(逐席派工單 → vacuous),故 v1 的「自動涵蓋」核心宣稱不成立。
外家另指出根因未動:pitfalls 早在 2026-08-02 就印同類提醒,搬到 loop next 不改變 2/25。
致命提問(正確性席):提醒 2026-08-02 上線、75 份派工單全在其後,仍只有 2/25——憑什麼再加一個不硬擋的提醒有效?v2 正面答:不是加提醒,是把「要多跑一次指令」這個步驟拿掉。

處置:v1 全數作廢重寫為 v2(印結果取代印指令,落點=pitfalls 人可讀分支)。逐條去向見計劃節點〈r1 審計修正紀錄〉。
