severity: major
scope-lines: 1625（審材 1013；skill／CLI／評測實作精準核對 612）
材料: `governance/review-reports/code-readme-manual-push/r1-snapshot.patch`

finding: 更新後的共用手冊正確寫明 `ci-wait` 的 rc0 不代表成功，但 CLI `--help` 仍宣稱「綠 rc0／紅 rc1」，形成兩套互斥判讀；使用者依 CLI 單源操作時，會把 timeout、no-run、unavailable 或 undetermined 誤認為 CI 綠燈。
severity: major
blocking: 是
引句:「只有結論 green 才算過;red 要處理;timeout/no-run/unavailable/undetermined 都不算綠,rc0 不等於 CI 成功」
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:32`
file: `scripts/lumos:49530`
最小重現: `! python3 scripts/lumos ci-wait --help | rg -q '綠 rc0/紅 rc1'`；目前翻紅，因 help 仍包含錯誤判讀。

其餘核對: 中英文 README 能力與邊界一致；slots 的掛鉤啟用、子開關回退與 `note_shape.gate` 總開關符合實作；離線 eval 路徑、未知值、指紋僅驗宣告一致及不重跑模型／驗收的界線符合實作；261 筆固定 main 清單與 Git 範圍逐筆集合一致，release 指向及 installer 預設 release 亦相符；圖譜同步與固定席 0 的補充結果已納入，無 finding。

總結: 最嚴重 severity=major，blocking=1
