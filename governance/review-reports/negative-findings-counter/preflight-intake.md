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
