# r2 收貨(2026-09-17)

複核:r1 五件關上(通才席重跑;架構席對照三處折入都走既有入口)。

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| F1 | 單reviewer-r2-sonnet | major | HIT:--no-renames 讓 364 行純改名算成整支重寫被擋 | 折:回到 git 預設改名偵測,新增 _numstat_new_path 解析 {a => b}(案例⑩) |
| F2 | 單reviewer-r2-sonnet | blocker | HIT:借 _PITFALL_DIFF_SKIP_EXT 排除 .json/.html,前端大改動量不到 fail-open | 折:不按副檔名排除,只排簿記與卷證(既有 _BOOKKEEPING_DIR 擴成 _BOOKKEEPING_DIRS 含卷證目錄,三個消費者共用)(案例⑪) |
| R2 | 單reviewer-r2-sonnet(複核②) | minor | HIT:_loop_ts_key 回 None 時直接跳過該列,文件說要退回字串比對 | 折:退回字串比對 |
