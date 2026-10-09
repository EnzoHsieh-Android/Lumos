preflight-4: ran

# 首輪前掃

唯讀 evidence_preflight 核對未定義詞、引用、範圍、現有機制語意；非正式席。

| 項 | 重現 | 修改前 → 修改後 |
|---|---|---|
| PF1 | HIT：main 在limit_hit直接continue，checkout只還原索引 | 使用既有git清理移除標記 → 每次attempt finally直接還原原文；重验安全及失敗停批 |
| PF2 | HIT：run_one無結果完整性判定 | 缺原始結果一概排除 → 完整零呼叫/Glob/已知失敗為有效失敗；支援呼叫缺結果才unknown |
| PF3 | HIT：既有probe fixture不含完整結果 | 依既有fixture驗證 → 新adapter驗證待實作，不冒稱已驗 |
| PF4 | HIT：runner保留calls/answer/stderr | 不保存標記範圍含糊 → 所有結果字串欄位遮罩當場標記 |

前掃語意修正均未更改以成功目標片段為證據的核心判準；交正式席續審。

## 正式席處置

| ID | 席 | 重現/判讀 | 去向 |
|---|---|---|---|
| B1 | boundary第一條 | HIT：父代理以subprocess stub與GIT_DIR=/outside/repo/.git、GIT_WORK_TREE=/outside/repo呼叫兩runner，兩者env均仍含這兩值；沒有真模型或Git寫入 | folded S5；使用既有_git_env，不造新清洗表 |
| B2 | boundary第二條 | HIT：main的except Exception把一般清理錯誤變成單場排除再續跑；將來路徑尚未實作，非已發生事故 | folded S4 明確fatal返回/回3/停止下一場 |
| M1 | measurement第一條 | HIT：check-graph-sync.main在_git_status_entries後看到code_entries就檢查圖譜；快照後注入確實造成code dirty | folded S1 標記在獨立副本初次快照前注入，finally只刪專用副本 |
| M2 | measurement第二條 | HIT：同B2，保留雙席觀察但同一根因 | folded S4 |
| M3 | measurement第三條 | HIT：run_probe以seed每週一次去重；這是配額界線，沒有聲稱當週立即執行新版 | folded 部署驗證入口直接--only v04核grader，legacy不當新版證據；不擴案改週抽配額 |

所有席已收齊才折。general與arch clean；B1由父代理機械重現，B2/M2兩席一致，M1父代理查讀實際hook邏輯，因此免辯方。無refuted/accepted。
基線：python3.14 scripts/test_lumos.py -k probe，124 passed, 0 failed；尚未新增測試/實作。
