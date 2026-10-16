# r1 收貨與修補判讀

固定修前 e3f92904ba93c37fcd417e14fce70148f7855e3e；兩席全收齊後才改工作樹。
獨立辯方 brief_defense 對 C1–C4 均 agree，引用固定版 S1/S4、S5、U4 共同任務及 AGENTS 每檔有家。C3 共同任務當時僅在探索 trial，正式兩臂仍須凍結共同任務，不以 trial 當正式評測。

| ID | 重現 | 判準與處置 |
|---|---|---|
| C1 | HIT | S1 metadata、共同材料與 grader-only 邊界；補 metadata 驗證、凍結角色清單及精確兩臂核對 |
| C2 | HIT | 字串 false 不等於布林；拒絕畸形數值，不把 invalid 列放進合計；保留 raw_receipts |
| C3 | HIT | worker [1,2] 乘二應得 [2,4]，原 fixed 得 undefined；保留 v1 歷史檔，v2 補 oracle 與結果保留 |
| C4 | HIT | Dart 機檢 profile 未涵蓋不取消人工要求；兩支來源掛到既有評測主節點，計劃與驗證已連此家 |
| A1 | HIT | MOC 評測入口補全部五案與儀器連結 |

修前測試：新 receipt/preflight 斷言跑原實作，Ran 3 tests, FAILED (failures=9, errors=3)。
斷言包括 incomplete != proceed-to-historical（valid、primary_hit、evidence_grounded 字串；負 tokens；非法 elapsed）；false_positives 字串 TypeError；case_id/arm 非雜湊值 TypeError。C1 缺 oracle 的 assertRaises 未拋出。
U4 獨立 probe：AssertionError actual undefined, expected [2,4]，Node v24.16.0，退出 1。
修後：原生 unfamiliar_stack_brief 子集通過；U4 v2 四格 1/0/0/0，內含結果、亂序及空輸入斷言。
沒有資料庫／網路／外部服務；純本機合成材料。
修補與必要測試一起提交，無非必要重構。歷史 v1 與 Gemini 原始 receipt 不改寫。
保留案例與未覆蓋範圍見 r1-behavior-cases.json；正式十場、語意洩題審及真人陌生度成效未驗。
