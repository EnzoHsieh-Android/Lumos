# 第一輪三項折入

preflight-4: ran

六席原報、收貨normalize/quote/ref/seat四道全部保存。三席clean的quote-check rc2只表示沒有引句可驗，不冒稱全錨。兩major一minor忠實保留，不降級。

| ID | 觀察 | 判準 | 處置 |
| logic-F1 | HIT：CLI52，載體首次驗句read_bytes拋一次OSError、後续hash成功，普通/-O非法UTF8及不錨快照都rc0追加，處置閘quote FAIL | HIT：未知材料不能以rawhash代替解碼和驗句；直接違反S1的非法材料不追加 | folded：S5加IO讀取當場rc2及不追加，獨立24控制舊碼2/22；診斷仍是IO，不改非載體或吞Runtime |
| resources-F1 | HIT：內層只包decode/_quote_rows廣捕捉的隔離mutant對46控制44/2，原42全部通過，唯新兩個解析Runtime逸出控制翻紅 | HIT：特定編碼捕捉不能把未知解析故障改成材料編碼錯誤 | folded：S4覆蓋讀入及解析兩階段，新46舊碼32/14；不新增生產helper |
| receipt-F1 | HIT：拒收不產成功帳，原REVISIT未指定獨立配對收據格式 | HIT：十份真實恢復必須有來源、命令、材料、rc和帳變化證據 | folded：計劃指定real-input-receipts每案例JSON、配對成功token及獨立Verification；測試/注入不計入真實十份 |

父編排者獨立實驗與logic席相同形狀，不冒稱席位實跑。最初counter漏--spec時gate rc2只驗參數；改以spec同路徑注入首次read時被更早spec入口擋，為負對照；獨立spec路徑的正式counter才證實驗句IO漏驗與quote FAIL。所有前序收據保存不覆寫。未知例外原樣逸出；無辯方，兩major均有父方可執行證據。生產CLI未改；46/24測試來源2eee5fd8，舊34/38/42各保存。

輔助鏡像收貨：mirror-F1觀察HIT（fold-check rc1，兩條reverse-omission、无value-drift）；判準MISS（「三項均折入」不宣稱summary完整；skill reference明定rc1是訊號非abort，Projects也無Systems/Issues的必摘要規則），接受提示並明載限制，不重複程式現況。mirror-F2觀察/判準HIT，Systems重驗入口補編碼/I/O與人工格式，folded。原鏡像報告保留，不把兩條minor洗成clean，不冒充正式6席卷證。append summary rc2並明說檔未動；不手改開頭或繞過寫入政策。
