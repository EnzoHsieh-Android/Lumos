# r1 收貨(2026-09-18;standard:通才 + 架構對齊)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| G1 | 單reviewer-sonnet | major | HIT:只改圖譜筆記的推送判成 docs;t_slim_gate / 其反事實測試(檢索品質、slim 與完整版搜尋等價)不在收緊後的子集;run_doctor 沒有搜尋相關檢查 | 折:pitfalls 多 suite_graph(範圍碰到 docs/<名>-knowledge/);執行器 --suite docs --graph 把「讀真圖譜」的測試加回(46 支,合計 109 支、四片 67 秒);掛鉤與 CI 都接;斷言 ⑦a、--graph 子集含 t_slim_gate、只改圖譜筆記的推送兩片帶 --graph |
| A1 | 架構對齊-sonnet | major | HIT:CI 自主迴圈步驟 if/else 各寫一次整條指令,同檔上一步是 extra 變數寫法 | 折:改 extra="-k real_claude_md" + 單一指令;接線斷言改對 |

附帶:掛鉤真跑測試的假執行器記錄檔原本放在 repo 裡,被 fixture 的 git add -A 帶進提交,讓推送範圍多一支非文件檔;移到 repo 外(新斷言當場抓到)。
