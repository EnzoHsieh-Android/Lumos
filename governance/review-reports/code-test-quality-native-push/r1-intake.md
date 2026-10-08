# r1 根因重現與處置

凍結起點5d8f0ec7045638dcc9c9f21e7fc9e0aff562eca7；所有七席交回後才修改程式。同門審查視角，未對未審部分聲稱全知。

| ID | 現象 | 判準 | 根因／處置 | 原問題控制 | 既有行為保留 |
|---|---|---|---|---|---|
| F1 | HIT | HIT | XML aggregate矛盾卻綠；核對總數，修復 | suite/root failure summary兩控制先紅後綠 | consistent summary及原生報告五棧重放 |
| b1 | HIT | HIT | 遞移部署缺檔；a1重複同根因，精確白名單preflight | partial_sidecar/missing_all控制先紅後綠 | legacy_help、完整CLI及五消費copy |
| b2 | HIT | HIT | vendor bytecode殘留；只清已知模組，不刪使用者／symlink外側 | deinit_removes_only_vendored_bytecode | user cache與symlink外側保留 |
| r1 | HIT | HIT | 中斷未清理process group；finally與SIGTERM通道 | cancelled_capture子程序已進入後終止，先紅後綠 | 正常capture及timeout控制 |
| r2 | HIT | HIT | claude逾時留下worker；新session群組清理 | fake claude PATH前置和worker停止，先紅後綠 | 不作付費重採樣；historical controls |
| r3 | HIT | HIT | 输出上限事後檢查；live bounded pipes | 30MiB writer completion marker不存在，先紅後綠 | 正常XMLcapture |
| r4 | HIT | HIT | 773附件作種子；只擴impact record分類 | eval附件分類及原真實branch種子核對 | py/executable/shebang/unknown仍種子，marker豁免未擴大 |
| i1 | HIT | HIT | SPDX加入後五消費副本過期、hash主張失效 | 重同步15模組hash及五報告重放 | 原始729/142附件不覆寫，區分stored replay與native execution |
| i2 | HIT | HIT | whitelist數量現況漂移；a2同根因，改為單源精確名單說明 | 現況文字移除固定舊數量 | 歷史決策原樣保留 |
| a3 | HIT | HIT | scan parser與argv有第二套契約；共用namespace／參數定義 | standalone/CLI共旗標且候選一致 | 21 scanner控制及33 CLI控制 |
| g1 | HIT | MISS | trusted local capture保留原始輸出，不自動publish；攻擊判準需要使用者另注入真secret並發布。獨立辯方以程式與可信命令合約反駁major；不引入不完整mask破壞卷證 | r1-defender-security.md原文與r1-資安-codex.md保留 | 原始來源與report hash契約保留 |

a1合併b1；a2合併i2；不把重複席數當不同bug。真發現全部折入；無major風險接受。資安原報告仍忠實記major，存活findings為0，refuted g1。

修復候選先由原問題與既有22項CLI行為選定；新增主要控制在修復前30項8敗，修後30項全綠，再增加分類、卸載、雙入口保留控制共33項綠。重構另保留scanner21控制、historical grammar/lock controls；未宣稱所有Python模型提交語法或所有平台已窮盡。

輸出、取消與套件preflight修復在同一工作副本；5d8起點與紅綠控制檔保留。新的複雜度告警分責任抽函式後精確lint全綠，未關閉閘或豁免。
