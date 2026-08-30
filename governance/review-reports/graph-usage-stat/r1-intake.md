# graph-usage-stat r1 前掃留痕

preflight-4: ran

- refcheck:0 壞引用(對照 repo 根)
- pitfalls --check:實務隱患節已補(payment/external-send/prod-irreversible/self-governance 逐類答)
- 前掃 agent(haiku,固定清單):命中 2 條已修真檔——①d8 分桶邊界補欄位(ts)與時刻(2026-08-29T00:00:00 本地)②「席報告引圖譜率」首現白話定義;順手釘 distinct 正規化(NFC+去 .md+stem 去重)
- 欄位實名親驗:report_path/ts 皆在帳列(grep 實測)
- 近案查證(乾淨 agent,原始問題不餵結論):兩前案裁死派工端機械強制,本切片讀側純觀測不衝突;E4 缺口正主

## 認錯更正(2026-08-30,r1 收貨後)

上面「命中 2 條已修真檔」**當時為假**:三處 python replace 因括號全半形不合靜默沒中(無 assert),連切片章節本身都沒寫進真檔——r1 席審的材料裡沒有切片規格,其 blocker 判定正確。v2 已用行錨+逐字 assert 重寫落地(L-1..L-8 全折)。本檔保留原文不改,以此節更正;教訓=改檔 replace 必 assert,已入記憶與後續紀律。
