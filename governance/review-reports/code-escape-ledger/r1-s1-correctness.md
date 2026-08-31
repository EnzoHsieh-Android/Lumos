# esc r1 正確性席
C-1|major|blocking:是:記帳指令多帶 --list → rc0 靜默吞資料像成功(dispatch 守衛+list 分支疊加)。
引句:「if not args.esc_list and not (args.esc_severity and args.esc_desc):」
C-2|minor:真空字串 desc 被 dispatch 層訊息蓋掉,函式內準確訊息成死碼。
C-3|minor:手改帳的怪 severity(critical/null)被權重 .get 歸 0 誤判最輕、None 原樣印出。
引句:「key=lambda v: {"minor": 0, "major": 1, "blocker": 2}.get(v, 0))」
抑噪:known 混 None 不影響(前置擋);ts 格式與 canary 帳同款。
severity: major
