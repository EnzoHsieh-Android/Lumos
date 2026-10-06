# 實作前前掃折入

preflight-4: ran

四項真實機械檢查收據及fresh medium實際秒數保存。原major PF-1報告不改；該席觀察是未實作候選的安全控制缺口，不宣稱已上線code bug。

| ID | 觀察 | 判準 | 處置 |
| PF-1 | HIT：初版34未辨別廣泛吞Exception的壞修法；原報未實跑變異 | HIT：特定編碼拒收須保留非編碼錯誤及IO分流，不能把它們偽裝為材料編碼錯誤 | folded：增加非編碼RuntimeError注入和缺檔控制，S4綁定；原34的20/14、加Runtime後38的24/14、再加IO後42的28/14原紅各留版。隔離壞mutant對38為36/2，對42為38/4，真實殺掉普通/最佳化的廣捕捉及IO誤診 |

source53d1主線CLI52c9未改，candidate tester方法才增控制；不把初版當同一測試版本，不改任何原紅、raw preflight severity或核心處置機制。S1補明其餘參數和報告合法，保留原拒收優先序。不是設計正式R1的新增席，不借前掃代正式審。
