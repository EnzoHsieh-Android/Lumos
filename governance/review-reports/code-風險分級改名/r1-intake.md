# r1 收貨(2026-09-18)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| A1 | 架構對齊-sonnet | major | HIT:pitfalls 宣告 vault-free(CLI help 與節點都寫),我在裡面 Env 載整份圖譜,無降級 | 折:pitfalls 只留字串前置提示;耦合搬到 spec-gate --push-check(唯一有圖譜、本來就在 pre-push 跑) |
| A2 | 架構對齊-sonnet | minor | HIT:每支檔有家節點沒登記 _nodehome_code_kind 的新消費者 | 折:KEY 登記 |
| F1 | 單reviewer-sonnet | major | HIT:report 模式對有綁測試的候選會 _run_bound_tests,pre-push 跑第二次 | 折:report 只看全靠人驗(manual_only=True),有測試的不跑;與 A1 同解 |
| F2 | 單reviewer-sonnet | major | HIT:_nodehome_code_kind 對無副檔名回 shebang? 不是「確定是程式檔」,.gitignore/Makefile 被當程式檔 | 折:_is_code_file 補首行 #! 檢查(案例①) |
