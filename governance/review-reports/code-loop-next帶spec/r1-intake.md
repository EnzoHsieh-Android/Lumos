# r1 收貨(code-loop-next帶spec)

standard 分級:一位通才(正確性-sonnet)加架構對齊席(sonnet),收齊才動工作目錄。兩份報告第一次交都格式不合(架構對齊 clean 但沒有引句、正確性的引句用反引號且敘述夾了 severity 冒號字樣),退回各席自己改格式,內容沒動;改完 quote-check 全數錨定、report-normalize 不用改。

## 發現

| id | 來源席 | 一句話 |
|---|---|---|
| Z1 | 正確性 F1 | loop next 改問處置閘後,這個唯讀指針會順手追加寫席位異常紀錄 roster-alerts.log,重跑一次多一行 |

架構對齊席:三問皆對齊,clean。

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| Z1 | t_loop_next_spec_uses_disposal_gate_for_new_loops 新增一段:報告改得比帳面高,連跑兩次 loop next,看有沒有 roster-alerts.log | HIT:舊程式寫出那個檔 |

## 處置

- Z1 折入:cmd_loop_status 加 readonly 參數轉給處置閘,loop next 代問時帶 readonly=True。
