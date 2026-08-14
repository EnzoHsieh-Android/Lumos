# r1 s3 邊界席(sonnet) findings 摘錄
F1 major: capture_counts 非 list(字串)時 _estimate_remaining_defects 靜默回 0.0(實跑證實),既有壞行防禦只擋壞 JSON;現況帳 100% list 乾淨,風險在未來/人工編修。
F2 minor: 超門檻 fixture(1,1,1,1→殘餘6.0)不會印 ⚠低殘餘句,斷言字面錯會當場紅(自糾型)。逐 fixture 推演:兩條反轉後 rc 確實 1→0,非換湯不換藥。
F3 major: S2 未規範 quiet(K=2 前一輪)路徑;K2 cutoff 已過=新 loop 預設吃 K=2,照 if not quiet 慣例前一輪觀測整段消音。
F4 clean: 驗收 rel-mainnet 可執行,實跑現況=唯「殘餘超門檻」FAIL rc1,為落地後乾淨對照。
