# r3 收貨、重現與處置(末輪)

## 收貨

六席(正確性3、邊界3、接手3、併發3、回滾3、架構對齊3,皆 sonnet,全新代理)全部交回後才一次寫進卷證,報告取自逐字稿,六份都一次通過正規化與引用路徑檢查。引句錨定:五份全錨;邊界3 有兩句不採信——「判定紀錄只增不減」不足 10 字(該條 F5 另一句錨定成功)、F8 那句中間用「…」節錄。F8 的事實編排者自己重現:`cmd_note_audit_reread_record` 寫 `text` 時不截斷(只截 `quote` 與 `why`),讀端 `_nodehome_cat_blobs_capped` 對超過上限的檔回 None,HIT。repo 沒被席位動過(git status 只有本編排者的卷證檔;reflog 最新一筆是本編排者的提交)。邊界3、正確性3、併發3、回滾3 在 /tmp 做了實驗並附輸出。

## 處置(46 條;折 43、放行 3、駁回 0)

編號:C3=正確性3、B3=邊界3、H3=接手3、N3=併發3、R3=回滾3、A3=架構對齊3,後接各報告 F 序號。

| finding | 重現 | 根因組 | 去向 |
|---|---|---|---|
| C3-3、B3-1 | HIT(B3-1 實驗:`text` 空白行時比中第 3、4、5 行) | G-NEEDLE 空比對字串 | 折:最後選定的比對字串少於 6 字一律略過 |
| B3-4 | HIT | G-NEEDLE 非字串欄位 | 折:不是字串的 quote/text 當空字串 |
| C3-2、B3-2、R3-7 | HIT(實驗:`_ns_summary_logical` 對單行 summary 回 `{}`) | G-ENTRY 單行 summary 表態不了 | 折:`_reread_summary_entries(text)` 共用,`_drift_ack_line_err`/`_drift_ack_text` 對 reread 走它 |
| C3-6、B3-6、A3-4 | HIT(實驗:摘要雜行不屬任何條目) | G-ENTRY 條目歸屬 | 折:同上,用 `cont` 對照,雜行不歸任何條目 |
| C3-1、H3-1、N3-1、R3-6 | HIT(N3-1 實驗:已提交、provenance 假的紀錄落進 wip) | G-COVER wip 口徑與訊息 | 折:wip 改成頂端樹沒有的檔;擋下訊息分列;record 的照收改說不算對照 |
| N3-2 | HIT(實驗:掛鉤取自主工作目錄、工具取自工作樹) | G-HOOKVER 舊掛鉤搭新工具靜默不擋 | 折:沒帶 --gate 時印一句;enforcement 查生效掛鉤 |
| R3-1 | HIT(實驗:別人只動 scripts/lumos 後同範圍同筆記指紋變) | G-COST 本機也會因 rebase 重判 | 折:改正理由說法,算進第一層成本與 RETIRE-IF |
| N3-7 | HIT(推論,依指紋定義) | G-COST 非快轉重試 | 折:隱患節寫明 |
| C3-5、B3-9、N3-6、R3-5 | HIT | G-UNDEC `_NoteRereadStop` 來源 | 折:參數錯以外一律判不了;最大五份改用 `_nodehome_cat_sizes` |
| A3-2 | HIT | G-UNDEC 工作目錄設定退路 | 折:拿掉退路,照預設 block |
| C3-4、H3-6 | HIT | G-CLAUSE 條款前提 | 折:S16、S18 加 --gate 前提,S6 排除 off |
| C3-7、H3-4 | HIT(設定從被推頂端讀) | G-OUT 改設定要提交 | 折:掛鉤逃生段寫明 |
| A3-5 | HIT | G-OUT 逃生段誰印 | 折:照存量漂移分工,工具印改法、掛鉤印通用逃生 |
| N3-5、H3-5 | HIT(`_drift_load_acks` 預設讀工作目錄) | G-ACK 表態讀哪棵樹 | 折:頂端樹 |
| B3-5、N3-8 | HIT | G-ACK 條目編輯讓表態失效、表態檔合併衝突 | 折:寫明刻意與既有性質 |
| N3-4 | HIT | G-ENTRY superseded 只排除 RULE | 折:三類都排除 |
| B3-7 | HIT(實驗:兩個非 UTF-8 路徑轉換後相同) | G-PATH 顯示轉換撞名 | 折:比對用原始字串 |
| N3-3、R3-3 | HIT(CI drift 步驟受指紋釘住) | G-DOCS 自相矛盾 | 折:CI 那句不改,只改掛鉤那句 |
| H3-3 | HIT | G-DOCS 漏改清單 | 折:補名稱消失那列圖、手冊 94 行、掛鉤執行時句、note-audit 命令表、路線圖 REVISIT、手冊字樣測試 |
| H3-2 | HIT(實跑 `_slot_replacement_dead` 認不出) | G-DOCS superseded 寫法 | 折:改成 `[[…]]` |
| R3-4 | HIT | G-DOCS 升版要重注入戳記 | 折:列入 |
| H3-7 | HIT(放行有四支) | G-DOCS 複雜度放行 | 折:只處理 `_note_reread_check`,其餘三支照舊放行 |
| H3-8 | HIT(推論;看不到 rtb 紀錄) | G-CONSUMER 消費專案舊紀錄 | 折:CHANGELOG 寫明 |
| H3-9 | HIT | G-HOOK 128 以上都停 | 折:寫明刻意推翻、進 CHANGELOG |
| R3-2 | HIT | G-ROLLBACK 新測試與計劃收尾 | 折:回退節列明 |
| A3-3 | HIT(`_note_reread_config` 字面值散落) | G-CONST 預設常數 | 折:`_NOTE_REREAD_DEFAULT_GATE` |
| A3-6 | HIT | G-LANDS 落點漏 README 圖產生器 | 折:補進 lands_in |
| A3-1 | HIT | 設定 block 還要旗標才擋,這一族第一次 | 放行:人裁「只在本機擋」的直接結果,較近的先例是 `bound-tests --advisory`、`doctor --ci`;minor |
| B3-3 | HIT(實驗:共用測試綁定字串出現在 7 條) | 泛引句連帶擋同篇其他條目 | 放行:每條可表態,比對字串至少 6 字,不另用行號錨定(行號在筆記改動後會漂);minor |
| B3-8 | HIT | 寫入端不限紀錄大小 | 放行:要很多列或超長行才會超過 256 KB,恢復路徑是 git rm 重判;minor |

`refuted-set`:none。

## 停止資格

這是 high 分級的第 3 輪(上限)。本輪全部處置後問閘;本輪修補沒有再派全新席審,實作後的代碼審照高風險走、會再審一次實作與設計是否一致。
