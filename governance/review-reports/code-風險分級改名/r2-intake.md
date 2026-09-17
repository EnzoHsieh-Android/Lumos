# r2 收貨(2026-09-18)

複核:r1 四件關上(通才席)。

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| F1 | 單reviewer-r2-sonnet | blocker | HIT:刪掉無副檔名的 #! 檔(hook 本身),磁碟讀不到 → 不算程式檔 → light 漏派審 | 折:_is_code_file 磁碟讀不到就從範圍起點 git show 讀首行,兩邊都沒有保守當程式檔(案例①b) |
| F2 | 單reviewer-r2-sonnet | major | HIT:_spec_gate_push_report 沒人呼叫,規格閘 KEY 卻說分級靠它「不跑測試」 | 折:拆掉函式與 manual_only 分支;KEY 改成描述真實路徑(分級是 push-check 掃描的副產物) |
| A1 | 架構對齊-r2-sonnet | major | HIT:_is_code_file 首行 #! 判斷與 _nodehome_required 逐字相同的第二份 | 折:抽 _head_is_shebang 兩處共用 |
| A2 | 架構對齊-r2-sonnet | major | HIT:_spec_gate_push_report 整段複製 _spec_gate_push_check 的前段 | 折:同 F2,拆掉 |
