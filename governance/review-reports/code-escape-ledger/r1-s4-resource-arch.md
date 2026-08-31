# esc r1 資源+架構席
R-1|major|blocking:是:裸 open('a') 繞過既有 _jsonl_append_verified(2026-07-28 未落盤事故後的硬化原語,canary/ci 帳已用)——ground truth 帳用最弱寫法。
引句:「f.write(_je3.dumps(rec, ensure_ascii=False) + "\n")」
R-2|major|blocking:是:全檔唯一把單一子指令必填驗證拆進 dispatch 層;函式自身不驗 severity,繞過呼叫點可寫 null。
引句:「if not args.esc_list and not (args.esc_severity and args.esc_desc):」
R-3|minor:記帳全掃 canary 帳(819 行/588KB)=既有全掃模式延續,留追蹤票不擋。
抑噪:append 家族形一致;ts 對齊;stderr 慣例;錯誤訊息家規;佈線位置無違例。
severity: major
