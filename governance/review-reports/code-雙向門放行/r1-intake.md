# r1 收貨(2026-09-17)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| F1 | 單reviewer-sonnet | blocker | HIT:在臨時 repo 照席位步驟重現——正文塞「Stripe billing」不動條款,push-check rc0 放行;同檔 spec-gate 判單向門 | 折:推送前重判門+指紋含已排除理由 |
| F2 | 單reviewer-sonnet | major | HIT:四行已排除放進 > 引用塊仍判雙向門 | 折:引用塊行不算已排除 |
| A1 | 架構對齊-sonnet | major | HIT:_plan_all_links 與 _plan_system_links 職責重疊(讀碼即見) | 折:合成一支帶參數 |
| E2 | 編排者實測 | major | HIT:實作提交只動程式檔,push-check 不查該計劃 | 折:從被改檔的家反查計劃 |
