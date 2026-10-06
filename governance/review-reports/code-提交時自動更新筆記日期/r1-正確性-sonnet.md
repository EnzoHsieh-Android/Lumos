severity: major

## F1 淺 clone 下整張日期表變成同一天,doctor 會把大量筆記誤列落後,並勸人一鍵蓋掉真日期
severity: major
blocking: 是 — 建議的指令會大批覆寫人工維護的 updated,且 CI 常用淺 clone。
file: `scripts/lumos:40860`(git_last_change_dates)、`scripts/lumos:18035`(_updated_stale_notes)
場景:`actions/checkout` 預設 depth 1(或本機 `git clone --depth 1`)。淺 clone 只有一個提交,git log --name-only 把 vault 全部檔案都當成「這個提交新增」,每篇的 git 日期都等於 tip 日期。所有 updated 早於 tip 日期的筆記一律被判落後。advice 又寫 `lumos updated-sync --stale` 一次改成今天,等於把真實 updated 全蓋成今天。
重現:r2 有兩個提交,P.md 的 updated 是 2026-09-11 且只在第一個提交(committer date 2026-09-11)改過,第二個提交只動 README。在 r2 跑 `lumos updated-sync --stale --dry-run` 得「沒有要改的筆記」;`git clone --depth 1 file://…/r2 sh` 後在 sh 的 vault 跑同一條指令,得「會改 Systems/P:updated 2026-09-11 → 2026-10-06」。
引句:「updated 落後 git 最後改動的筆記 {len(_us)} 篇(例:{_ex})」
佐證:函式內只在 returncode 非 0 時回空,淺 clone 回 0 所以沒有 fail-open。可補 `git rev-parse --is-shallow-repository` 為 true 就回 {},或讓 U 段在淺 clone 不印、`--stale` 在淺 clone 擋下。

## F2 updated 是空字串時,訊息講「沒有 updated 欄」不準確
severity: minor
blocking: 否 — 只有訊息誤導,行為(不改)與設計一致。
file: `scripts/lumos:18065`
場景:筆記寫 `updated: ''`(欄位存在但空)。指定節點跑 updated-sync,印「跳過 Systems/E:開頭沒有 updated 欄(不加)」,實際欄位在。已實測。
引句:「print(f"跳過 {rel[:-3]}:開頭沒有 updated 欄(不加)")」
佐證:`_drift_str` 對空值與缺欄都回 "",分不出來。

## F3 次日提交同步結果後會再度落後(循環)
severity: minor
blocking: 否 — 屬設計取捨,doctor 只提醒不擋。
file: `scripts/lumos:18040`
場景:今天 updated-sync 後立刻提交,updated 是今天、git 日期也是今天,不落後。若提交跨日(updated 寫今天、commit 在明天),git 日期大於 updated,下次 doctor 又列這篇;再 sync 再提交又重複。日期比較用 `u < g`,跨午夜或之後任何一次動到該檔的提交都會觸發。
引句:「if g and re.fullmatch(r"\d{4}-\d{2}-\d{2}", u) and u < g:」

## 其他走過、未發現問題
- 帶引號的 updated(`"2026-09-11"`):解析後是純字串,--stale 會列;指定節點時 cmd_set 改寫成不帶引號的今天,只動該行。實測。
- 帶時間(`2026-09-11T10:00`)或非日期:fullmatch 不過,--stale 不列,doctor 不報;指定節點仍會被改成今天。可接受。
- 快取:cmd_set 改的是未提交內容,git 日期不變,同行程再讀不會過期。`git_last_change_dates` 目前只有新呼叫點與測試呼叫,resolve 兩邊對其他呼叫者無影響。
- 重複:`dict.fromkeys(rels)` 去重,--stale 與節點名重疊只改一次。找不到節點 rc 取 max,其他照改。
- 測試:3 支的翻紅釘大致成立;t_updated_sync_stale ④只檢查 rc,沒檢查內容,偏弱但不算假綠。沒有測淺 clone、跨資料夾 NFC/NFD、vault 不在 repo 根的情形。

總結:max severity major,blocking 1 條(F1)。
