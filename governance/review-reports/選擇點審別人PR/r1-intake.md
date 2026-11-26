# 選擇點審別人PR r1 收貨紀錄

preflight-4: ran

## 前掃(凍結前,sonnet 一席,固定四項清單;29 條命中)

存在類與用詞類直接修真檔,不算 findings:〈用詞〉補模組、測試類別、審查樹、被抓到、回指、PR 頭提交;`baseRepository` 不是 gh 欄位 → 改用 `isCrossRepository`(實測 `gh pr view --json baseRepository` 回 Unknown JSON field);`RULE_LINE_RE` 不存在 → 改指既有 `_slot_summary_entries`;D1 輸入拿掉「遠端分支」(跟 PR 描述、同 repo 判斷、留言接不起來)。

語意類命中動到核心裁定,攤人裁(使用者 2026-11-26):
1. choice-kill 要求範圍右端是 HEAD、工作目錄乾淨、cwd 有圖譜,治理帳沒有旗標可關(`_choice_record`、`_choice_kill_report` 的 run 事件),而且會讀帳略過已處置的行 → 人裁「給核心加參數」;實際做法改成判定另寫小執行器重用合併快篩那幾支函式,不經 `cmd_guard_kill` 與 `_ChoiceKillRun`,掃描那兩支加 `repo`/`at_sha`。
2. 別人的 repo 多半沒有圖譜與 `.lumos` 設定(會退成 csharp-xunit、沒有 run_cmd)→ 人裁「連沒裝的也要能跑」:加 `--run-cmd`,第一版只支援 Gradle JVM 單元測試。
3. 第四層(模組全部測試)要先量每支單支基準,N 支就 N 次 Gradle → 人裁「審別人時可以」每個壞法只跑一次合併、不量單支基準、不歸因;碰到舊否決「合併直接判殺掉」,計劃寫〈舊否決比對〉。
4. 測試地圖是本機檔、審查樹裡沒有、輸出是測試檔不是方法 → 拿掉這一層、寫進〈不做〉。
5. 回指第一層原寫「impact --diff 的牽連檔」:那個欄位幾乎恆真、也沒有合約行 → 改成讀節點內文取 ★INVARIANT★ 與 `RULE:` 行、用反引號路徑或 about_code 對存活點所在檔。
6. D5「改動行數多的檔先」程式裡沒有這個排序 → 拿掉,照既有挑行順序。
7. 「唯一防線」與同 repo PR 不設防矛盾 → 改寫實務隱患照實寫同 repo 不設防。
8. S5「.git 一個位元組都沒變」做不到(worktree 登記、fetch 物件)→ S6 改成只比帳、工作目錄檔案與目前分支,實務隱患寫明。

核心裁定由使用者裁過才改,這份是重寫後的版本。

## 收貨(四席齊了才落地;報告從逐字稿原樣存)與暫停

- 四席最高:通才 blocker、正確性 blocker、邊界 blocker、架構對齊 major;四席獨立點到同一組:第三層類別名對不到方法名(classify 判 unclean)、`_kill_merge_*` 吃 `cmd_guard_kill` 內部現場 `c`(讀單支基準)與 D6、D7 矛盾、掃描只收 `.kt`(Java 正式碼沒掃)、基底提交沒 fetch、同 repo PR 讀 PR 頭的 `run_cmd`(可塞任意殼層指令)、多模組任務不對、回指第一二層會對到不相干的句子;架構對齊另指 guard-kill「唯一判法」與既有否決「另抽一支共用的殺傷力函式」,`JAVA_TEST_RE` 已存在、gh 呼叫沿用 `_ci_gh`、落點要補規格閘或另開一篇。
- 使用者 2026-11-26 裁:先做「選擇點存活回指條款」,審別人 PR 暫停在這一輪;還沒記帳、還沒折。回來時照這份收貨紀錄與四份席報告折入,再記帳。
