---
type: project
status: doing
created: 2026-09-05
updated: 2026-09-05
tags:
  - type/project
  - status/doing
---
# README審視五修_計劃

> 白話:2026-09-05 拿 README 逐條對回程式碼、帳本、量測(我+一位乾淨稽核員各做一份,兩份結論一致),抓到五處「寫的比做到的多」。Enzo 裁「依序優化」。這篇記五件事各自為什麼這樣修、改到哪、還剩什麼沒補。

KEY:稽核來源=`governance/review-reports/readme-audit-2026-09-05.md`(乾淨稽核員)+本 session 實測(pre-commit 對只改 scripts/lumos 放行、對 .py 擋;Claude Code 官方文件 exit 0 的 stderr 模型看不到;自主迴圈週報連續七週收斂 0)。
KEY:d1 pre-commit/post-commit 補 shebang 判定——沒副檔名但首行是 `#!` 的 staged 檔算程式碼(讀 staged blob 不讀工作樹);四份清單守衛加「都認 shebang」;實證:五月起 26 個只改 scripts/lumos 的 commit 從沒被擋。
KEY:d2 收工擋一次改為兩家一致——check-graph-sync 的 block 不再看 harness;Claude 側 exit 0 + stderr 官方文件明講模型看不到,「軟提醒」實為零;07-06 撤 nag 的理由(每回合刷屏)被「同 session 只擋一次+只在改了碼沒寫回時」化解,是有意識重開但不是重開 nag;stop_hook_active 兩家語意相同(已續做過=不再擋)。LUMOS_STOP_BLOCK_OFF=1 仍可關。
KEY:d3 自主迴圈暫停派工——daily-governance 不再每天派 orchestrator(七週週報收斂 0/待放行 0、每週 210–330 美元;dry-run 永遠不會走到開 PR);便宜的日常段(治理日報、lint-watch、doctor --ci、回放週跑、探針週抽)照跑;`LUMOS_AUTOLOOP_OFF=0` 可臨時開回;REVISIT:2026-10-05 決定給它真產出路徑或正式退場。
KEY:d4 README 補「成本與界線」一節(中英)——代碼審 7 天 930 萬 token、自主迴圈成本與零產出、pre-commit 任一篇即過、憑證自發只擋忘記不擋敷衍、附節點利用率低、處置閘驗帳目不驗內容。
KEY:d5 enforcement 字句——Codex 五層「等你審過」改為「信任狀態本機測不到」;強制力表 Stop 列改兩家一致。
KEY:設計審跳過:d1 是 bug 修+既有守衛延伸;d2 是把已審過三輪的 Codex 機制套到 Claude(邏輯同一份碼);d3 是關開關;d4/d5 是文件。代碼審依 pitfalls tier 決定。

## 代碼審 r1 折入(2026-09-05,standard 3 席:通才 / 架構對齊 / 外家 Codex;卷證 `governance/review-reports/code-readme-five/`)

- **三席同題的 major**:「什麼算程式碼」的 shebang 判定寫成直譯器清單,而且 bash 兩支、check-graph-sync、impact-hook 三份清單彼此不同(bash 漏 `#!/bin/dash`,impact-hook 漏 ruby/perl/node);測試又只查函式名字串,漂移照樣綠。改成★首行是 `#!` 就算程式碼★,四處同一條規則、不再有清單;測試真的餵 dash / env -S / fish / 純文字 / 二進位 / 空檔驗語意,pre-commit 實測加 dash、env -S、`.pythonrc`。
- **minor 三條都折**:dotfile 去掉開頭的點再判副檔名;死別名 `codex_stop_decision` 刪除;暫停開關改成 repo 慣例的 `LUMOS_AUTOLOOP_OFF`(預設 1=暫停,開回設 0),log 寫法對齊其他段。
- **開放風險(通才 ⚠,未計分)**:Claude Code 在 bypass / dontAsk 權限模式下會不會忽略 Stop 的 block、讓那一次名額白燒——本 session 查不到官方明文。REVISIT:2026-10-05 對照 `~/.cache/lumos/stop-block` 標記數與逐字稿裡 `LUMOS-STOP` 出現數,差太多就是白燒。

## 代碼審 r2 折入(2026-09-05,delta 兩席)

- **major(兩席同題)**:檔名含雙引號或反斜線時 git 會印成 C 式引號,直接拿去 `git show` 找不到,含 shebang 的程式碼就放行、post-commit 也不記。修=`is_shebang_code` 先解引號(`"`、`\`、`\t`);含換行的檔名仍解不到——那是整支 hook 用逐行讀檔名的既有限制,不在本案。測試加含引號檔名。
- **minor**:`..foo` 只剝一個點 → 剝掉所有開頭的點;impact-hook 刪清單後多出的空行收掉。

## 代碼審 r3 折入(2026-09-05,末輪;外家 Codex 先到)

- **外家 major**:含控制字元的檔名 git 印成八進位跳脫(`"bin/weird\001tool"`),上一輪的解引號只處理了 `\"`、`\\`、`\t`,八進位沒解 → `git show` 找不到 → shebang 檔放行。修=`\"` 手解後整串交給 `printf '%b'`(它會解 `\\`、`\t`、`\0nn` 這種控制字元);臨時 repo 實測五種怪檔名(雙引號、反斜線、tab、`\x01`、反斜線接引號)全部擋下;測試加一案。殘留限制:`\177`(DEL)這種不以 0 開頭的八進位 `%b` 不解、檔名含換行則整支 hook 逐行讀檔名本來就對不上——兩者都極罕見,寫明不修。
- **第一次真實觸發**:這條修法寫完、筆記還沒補時,本 session 的 Claude Stop hook 當場擋了一次要我補筆記——這是 d2 套到 Claude 之後第一次在真實對話中生效(之前的 stderr 提醒從沒到過模型面前)。
- **sonnet delta 席**(快照已落後,結論與外家同題):另一條 minor——單一個引號的假輸入在 `set -u` 下子字串會吐錯(真 git 輸出到不了),加長度守衛。
- **★達上限★**:standard 3 輪到頂,r3 仍出 major(已折);r3 之後這幾行修法沒有再派席。REVISIT:2026-09-08 Enzo 併 Codex行為精修 那條一起裁要不要補一輪 delta 審。
