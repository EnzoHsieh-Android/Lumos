# 首輪前掃判讀

preflight-1: ran — refcheck rc0，零壞引用。
preflight-2: ran — prose-lint修正為檔案路徑後rc0，保守詞表無命中；不能據此宣稱語意正確。
preflight-3: ran — pitfalls --check真檔rc0，六類風險逐項作答；守衛面不排除，規格閘判風險高，3條句式綁定及回退通過，新行為紅2/既有綠1、相依4支全綠。
preflight-4: ran — 全新唯讀gpt-5.6-sol medium實際140.68秒，四項清單語意查證；原報不改。

|ID|觀察|判準|處置|
|PF1|HIT：S2真的少綁執行兩席record與gate的現有方法|HIT：驗收引用不完整，不是核心數量裁定錯|S2補回t_canary_negative_findings_rejected，既有兩綁定保留；測試和核心裁定未改|

修改前：有效零發現兩席應仍通過處置閘。 [test:t_canary_findings] [test:t_canary_carrier_quote_positive_controls]
修改後：有效零發現兩席應仍通過處置閘。 [test:t_canary_negative_findings_rejected] [test:t_canary_findings] [test:t_canary_carrier_quote_positive_controls]

此方法原碼14pass20fail的紅來自負數期待，合法對照全通過；條款S2引用同一方法可能跟著整體紅，不能把它說成合法控制失敗。前掃沒有動核心裁定，語意修正逐條保存。首次prose-lint/pitfalls用了節點而非檔案導致rc2，spec-lens非CLI命令導致rc2，皆操作者輸入更正，不當產品缺陷或綠燈。正式語意鏡頭已用dispatch-lens --spec的真檔生成。


正式首輪六席收齊後才改材料：五席clean、一席minor resources-F1，blocking0。

|ID|觀察|判準|處置|
|resources-F1|HIT：源碼及真CLI負數配不正規報告先報格式並寫治理blocked，沒有canary追加|HIT限於phase未明；MISS為泛化到治理拒收事件一律禁寫，既有程式明訂被擋須留痕|folded：明訂負數在報告驗證前、canary成功帳不追加；加普通/O雙錯輸入診斷及canary逐位元不變對照；不禁治理拒收telemetry|

原規格：只在findings顯式給負數時、追加前回rc2。
折入後：只在findings顯式給負數時、既有欄位分支內且任何報告驗證與canary追加之前回rc2。
S1的「帳列」明確為成功canary列，不是治理blocked事件；全治理帳不得變的額外直覺未採。其他核心條款不改，不放寬負數域、不加集合大小等式、不改舊帳讀側、沒R2或重置cap。

鏡像席155.77秒判clean，讀完全部原報、折入及具體反例；fold-check rc1空summary啟發告警不是abort，原樣留存。自動spec鏡頭只列落點計數，未宣稱自動附全文；各席報告皆核對相鄰Systems/design-loop實際合約，規格閘相依4支已實跑綠。
