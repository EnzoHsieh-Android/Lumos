severity: major
blocking: 是
引句:「歷史檔的非 dict 雜項沿用逐列跳過；有形狀的列若欄位錯誤則整檔拒收。」
file: `governance/eval/ablation_lumos_first.py:123`
發現：`invalid_batch_evidence` 跳過 `results` 內的非物件元素，違反 S13「舊結果欄位型別無效時拒絕計分」。混合一筆合法列與一筆字串的畸形批次不會標為失效，合法列仍抵銷缺場。
最小重現：建立 `with-q-malformed.json`，內容為 `{"arm":"with","results":[{"id":"a","passed":true},"not-a-row"],"fatal":false,"inconclusive":false,"skills_health_bad":[]}`；實跑得到 `collect_skills_health(...) == []`、`load_results(...)[with]` 含題 `a`，且 `needed(...,"with","a",1) == 0`。
影響：損壞或部分寫入的舊批次仍可進入 M1–M4 計分並阻止補跑，報表也不會顯示「整批不可採信」。

總結：最嚴重 severity major；blocking 1 條。
