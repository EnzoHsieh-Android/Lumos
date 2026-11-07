---
type: project
status: doing
created: 2026-11-08
updated: 2026-11-08
tags:
  - type/project
  - status/doing
  - scope/platform
lands_in:
  - Systems/測試執行器
related:
  - "[[Systems/測試執行器]]"
  - "[[Projects/測試總檔預設切片_計劃]]"
decisions:
  - content: 在 Claude Code 對話裡(CLAUDECODE=1)、不是推送前閘也不是切片子程序、又沒帶 -k、--suite、--list 時,測試總檔拒跑並回 2;LUMOS_ALLOW_FULL_SUITE=1 是印提醒的逃生門;不選工具前掛鉤比對指令字樣(python3 -m、別名、cd 後相對路徑都繞得過)、不選只靠記憶與規則(已實證擋不住)
    id: d1
    context: 對話裡一再跑全套:寫進記憶與 CLAUDE.md 都沒擋住(2026-11-07 又兩次),全套約 8 分鐘、超過對話工具上限、還吃記憶體
    why_chosen: 使用者 2026-11-07 原話「你可以不斷繞過這個規則，代表這個功能根本沒做好吧」「推完戊線就去做擋全套的機制」;擋在執行器唯一進入點,不管指令怎麼寫都會經過
    decided: 2026-11-08
    valid: true
---
# 對話裡不准跑全套測試_計劃

> 白話:在 Claude Code 的對話裡直接打 `python3.14 scripts/test_lumos.py`(沒帶 `-k`、`--suite`、`--list`)會跑滿約 8 分鐘的全套,超過對話工具的時間上限、還會吃掉大量記憶體。規則寫在 CLAUDE.md 與記憶裡已經一再被繞過(2026-11-07 又兩次)。這份計劃讓測試執行器自己認出「在對話裡、又不是推送前閘」的全套呼叫,當場拒跑並印出該怎麼跑子集。使用者原話(2026-11-07):「又在跑全套，要講幾次」「你可以不斷繞過這個規則，代表這個功能根本沒做好吧」「推完戊線就去做擋全套的機制」。

PRIOR-ART: 同一個執行器入口已經有兩個「在唯一進入點清掉外部注入」的先例(清 `GIT_*` 變數、關掉子程序上色),理由是對現有與未來的呼叫一律成立、不靠每個呼叫點自己記得;`scripts/scenario_probe.py` 開巢狀 Claude 子程序前也拿掉 `CLAUDECODE`。Claude Code 會在它開的殼裡設 `CLAUDECODE=1`(本機實測 2026-11-08);推送前閘在跑測試前 export `LUMOS_PUSH_ATTEMPT`(`scripts/hooks/pre-push`)。借用這兩個既有標記判斷,不另造。不選 Claude Code 工具前掛鉤比對指令字樣:只認得到字面寫法,`python3.14 -m`、shell 別名、先 cd 再相對路徑都繞得過。
RETIRE-IF: 計數檔(`~/.cache/lumos/full-suite-guard.jsonl`)八週內逃生門放行次數超過擋下次數(擋錯多於擋對)→ 撤掉改回只提醒;擋下一直有、逃生門很少 → 留著當守衛。

## 狀態

設計第二版(2026-11-08,折入設計審 r1 四席)。

## 跟舊決定的關係

[[Projects/測試總檔預設切片_計劃]] d1(2026-11-05)在「預設切片 / Claude Code 工具前掛鉤擋 / 兩個都做」裡選了預設切片,解的是「全套被單一程序跑、慢到三小時」。本案解的是另一件事:全套根本不該在對話裡跑(就算切片也要約 4 分鐘、超過對話工具的兩分鐘預設上限、還占住使用者機器)。使用者在 2026-11-07(那個決定之後)明確要求做這個擋,所以不算翻案;擋的位置也不是那次不選的「工具前掛鉤」,是執行器本身。

## 範圍

### 做

1. **判斷函式**:`scripts/test_lumos.py` 新增 `_chat_full_suite_block(args, env)`,回擋下訊息或 None。在對話裡(`env.get("CLAUDECODE") == "1"`),而且不是推送前閘(沒有 `LUMOS_PUSH_ATTEMPT`)、不是切片子程序(沒有 `LUMOS_FANOUT_CHILD`)、沒帶逃生門時,下面任一成立就擋:
   - 沒帶條件:`args.keyword`(合併位置參數後)、`args.suite`、`args.list`、`args.lf` 全是假值(用真值判斷,跟 `_fanout_wanted` 同一口徑,所以 `-k ""` 也算沒帶)。`--shard`、`--serial`、`-x`、`--ff`、`--seed` 都不算條件(它們不縮小範圍,只改怎麼跑)。
2. **選完之後再判一次**(解 r1 繞過 F1、F6,正確性 F7):在對話裡、同樣的豁免都不成立時,關鍵字篩選或 `--suite keys` 選完之後,選中支數超過全部測試的三成就擋,訊息印選中幾支、全部幾支。三成沿用 `_keys_suite_select` 既有的「太泛」門檻。`--suite docs`(文件子集,約兩百支、約四分鐘)不套這條,因為它是推送前閘對純文件推送用的正式子集。
3. **接在 main 的位置**(解 r1 四席獨立指出的插入點):第 1 條接在位置參數併進 `-k` 之後、`if _fanout_wanted(_args):` 之前;第 2 條接在測試清單篩選完、開始跑之前。擋下時印訊息到 stderr、回 2,不建暫存目錄、不開子程序。判斷時讀的是當下的環境變數;判斷完(不論擋不擋)才把 `CLAUDECODE` 從 `os.environ` 拿掉,這一步也在 `_fanout_wanted` 之前,讓切片子程序與測試開的沙盒執行器都不繼承(解 r1 正確性 F1:不跟清 `GIT_*` 放同一段,那一段在參數解析之前)。
4. **擋下訊息**(解 r1 通才 F4、繞過 F3、架構對齊 F3):第一行照鄰居寫「擋下:在對話裡不准跑全套測試(或選中太多:N/M 支)」;第二行講為什麼(約 8 分鐘、超過對話工具上限、推送前閘會自己跑);第三行起指令各自獨立一行:`python3.14 scripts/test_lumos.py -k <關鍵字>`、`--suite docs`、`--lf`(只重跑上次紅的)、全套交給推送前閘或請使用者在一般終端機跑。**訊息不印逃生門的變數名**,逃生門只寫在 [[Systems/測試執行器]]。
5. **只重跑上次紅的 `--lf`**(解 r1 正確性 F4、繞過 F8:推送前閘紅了之後印的 `--ff -x` 在對話裡會被反擋):新增 `--lf`,照 pytest 的 `--last-failed`,只跑執行器既有「上次紅過」紀錄裡的測試;沒有紀錄時印一行並回 2,不退成全套。`scripts/hooks/pre-push` 兩處「下一步」提示從 `--ff -x` 改成 `--lf -x`。`--ff` 照舊(先跑紅的、再跑其餘),在對話裡沒帶條件就擋。
6. **逃生門要帶理由**(解 r1 繞過 F3、架構對齊 F2):`LUMOS_ALLOW_FULL_SUITE=<理由>`,理由去空白後至少 10 個字才算數(不夠照擋並講要寫理由);算數時只在「本來會擋」的情況印一行「對話裡放行跑全套,理由:<理由>」(解 r1 正確性 F6),帶條件的呼叫不印。命名用 ALLOW 不用鄰居的 SKIP:它放行的是一個動作、不是略過一道檢查。
7. **計數**(解 r1 通才 F3、繞過 F4:RETIRE-IF 與 REVISIT 要的數字原本量不到):擋下與逃生門放行各追加一行 JSON 到 `~/.cache/lumos/full-suite-guard.jsonl`(時間、種類、argv、理由),在工作目錄之外、不改 repo;寫不進去就略過、不影響判斷。不寫治理帳:執行器跑在測試的隔離環境前段,治理帳在 repo 裡,寫了會讓「工作目錄乾淨」的測試與提交前檢查看到改動(跟鄰居逃生門寫 `skipped-env` 是刻意不同)。
8. **手冊**:[[Systems/測試執行器]] 補 WHY 與逃生門寫法、`CLAUDECODE` 被拿掉的副作用(執行器之後開的子程序都看不到它;現在只有 `scripts/scenario_probe.py` 讀它而且本來就拿掉);`--lf` 寫進說明。

### 不做

- 不在 CI 擋:CI 沒有 `CLAUDECODE`。
- 不擋人在一般終端機跑全套:沒有 `CLAUDECODE` 就不判。
- 不寫治理帳(理由見做 7)。
- 不管其他 AI 工具(Codex 等沒設 `CLAUDECODE` 的):另案。
- 不擋對話裡 `git push` 觸發的推送前閘全套:那是規定的跑法(CLAUDE.md「全套留給推送前的閘」),推送要放背景跑。

## 實務隱患

- **人在 Claude Code 的終端分頁裡手跑**:那個殼也有 `CLAUDECODE=1`,會被擋;要帶逃生門加理由。
- **Claude Code 改了變數名**:擋不到但不會擋錯;寫成回頭條件。
- **測試沙盒繼承環境**:做 3 處理;驗收的子程序測試從頭組環境(只給 `PATH`、`HOME`、`CLAUDECODE=1` 與私有 `TMPDIR`),不繼承外層的 `LUMOS_PUSH_ATTEMPT`、`LUMOS_FANOUT_CHILD`、`LUMOS_ALLOW_FULL_SUITE`,免得在推送前閘裡真的開出全套。
- **消費專案**:測試總檔會被安裝進消費專案(工具自裝檔),那邊在對話裡不帶條件跑也會被擋,跟本 repo 一致。
- **自動迭代迴圈**:headless 的 Claude 也設 `CLAUDECODE`;它跑全套同樣被擋,要改走推送前閘。
- 已排除:金流:不碰付款
- 已排除:對外送出:不連網、不呼叫外部服務
- 已排除:不可逆:只改執行器入口兩段判斷、一個旗標與推送前閘的兩行提示,計數檔在工作目錄外;退提交即回原狀
- 守衛面:不排除——這是一道新的擋停(擋 AI 在對話裡跑全套),判風險高

REVISIT:2026-12-08 讀 `~/.cache/lumos/full-suite-guard.jsonl` 看這一個月擋下幾次、逃生門放行幾次與理由;Claude Code 的 `CLAUDECODE` 變數還在不在

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 對話裡不准跑全套 | 使用者要求 | 使用者 2026-11-07:「又在跑全套，要講幾次」「你可以不斷繞過這個規則，代表這個功能根本沒做好吧」「推完戊線就去做擋全套的機制」 |
| 用 `CLAUDECODE=1` 認對話 | 本機實測 | 2026-11-08 在 Claude Code 殼裡 `echo $CLAUDECODE` 印 1;`bash -lc` 新殼仍是 1(r1 繞過席實測) |
| 推送前閘的標記 | 既有程式 | `scripts/hooks/pre-push` 在起測試前 export `LUMOS_PUSH_ATTEMPT` |
| 判斷放在執行器入口、拿掉外部注入 | 既有先例 | `scripts/test_lumos.py` 的 main 清 `GIT_*` 與關子程序上色;`scripts/scenario_probe.py` 開子程序前拿掉 `CLAUDECODE` |
| 選中超過三成算太泛 | 既有門檻 | `scripts/test_lumos.py` 的 `_keys_suite_select` |
| 只重跑上次紅的 `--lf` | pytest 的 `--lf, --last-failed` | https://docs.pytest.org/en/stable/how-to/cache.html |

## 驗收條款

- [S1] 當 `CLAUDECODE=1`、沒有推送前閘與切片子程序標記、也沒帶逃生門時,不帶條件、只帶 `--shard`、`--serial`、`-x`、`--ff`、`--seed` 或 `-k ""` 呼叫判斷函式 應 擋;帶 `-k foo`、位置關鍵字、`--suite docs`、`--list`、`--lf` 任一 應 不擋 [test:t_runner_chat_full_suite_block]
- [S2] 當沒有 `CLAUDECODE`、`CLAUDECODE=0`、有 `LUMOS_PUSH_ATTEMPT`、有 `LUMOS_FANOUT_CHILD`、或逃生門帶了 10 字以上理由時,判斷 應 不擋;逃生門理由不到 10 字 應 照擋;擋下訊息 應 不含逃生門的變數名 [test:t_runner_chat_full_suite_block]
- [S3] 當在對話裡關鍵字選中超過全部測試的三成時,執行器 應 擋並印選中與全部支數;三成以內 應 不擋 [test:t_runner_chat_full_suite_block_broad]
- [S4] 當用從頭組的環境(`CLAUDECODE=1`、私有 `TMPDIR`)真的起一個執行器子程序、不帶條件時,它 應 以 2 結束、私有 `TMPDIR` 裡 應 沒有 `gctl-run-` 目錄、計數檔 應 多一行擋下;前置:同樣環境拿掉 `CLAUDECODE` 時判斷函式 應 回 None(證明擋是 `CLAUDECODE` 造成的) [test:t_runner_chat_full_suite_block_process]
- [S5] 當帶 `--lf` 時,執行器 應 只跑上次紅的測試;沒有紀錄時 應 回 2、不跑任何測試;推送前閘的兩處提示 應 印 `--lf -x` [test:t_runner_last_failed_only]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | CLAUDECODE=1,無參數 | 擋 | 做 1 |
| S1 | CLAUDECODE=1,`--shard 2/4` | 擋 | 做 1 |
| S1 | CLAUDECODE=1,`--ff -x` | 擋 | 做 1 |
| S1 | CLAUDECODE=1,`-k ""` | 擋 | 做 1;r1 正確性 F3 |
| S1 | CLAUDECODE=1,`-k foo` / 位置 `foo` / `--suite docs` / `--list` / `--lf` | 不擋 | 做 1 |
| S2 | 沒有 CLAUDECODE / CLAUDECODE=0,無參數 | 不擋 | 不做 2 |
| S2 | CLAUDECODE=1 + LUMOS_PUSH_ATTEMPT 或 LUMOS_FANOUT_CHILD | 不擋 | 做 1 |
| S2 | CLAUDECODE=1 + 逃生門理由「重現 CI 第三片紅燈要整套」 | 不擋,印放行與理由 | 做 6 |
| S2 | CLAUDECODE=1 + 逃生門 `1` | 擋,講要寫理由 | 做 6 |
| S3 | CLAUDECODE=1,`-k t_`(選中全部) | 擋,印 N/M | 做 2 |
| S3 | CLAUDECODE=1,`-k runner`(選中不到三成) | 不擋 | 做 2 |
| S4 | 真子程序,從頭組環境,無參數 | rc 2、沒有 gctl-run-、計數 +1 | 做 3、7 |
| S5 | 上次紅 2 支,`--lf` | 只跑那 2 支 | 做 5 |
| S5 | 沒有紅的紀錄,`--lf` | rc 2、0 支 | 做 5 |

## 回退

退回本計劃的提交:執行器少了兩段判斷、`--lf` 與清變數,推送前閘提示回到 `--ff -x`,行為回到改動前;計數檔在 `~/.cache/lumos/`,留著無害、可手刪;沒有寫任何 repo 檔或帳。

## 天花板

1. 只認 Claude Code 設的 `CLAUDECODE`;別的 AI 工具不受限。
2. 逃生門與兩個豁免標記(`LUMOS_PUSH_ATTEMPT`、`LUMOS_FANOUT_CHILD`)都是環境變數,AI 自己也能設;逃生門至少留下理由與計數,手設豁免標記沒有紀錄(屬刻意偽造,不防)。
3. `env -u CLAUDECODE`、`CLAUDECODE=0`、tmux 或 cron 這類不繼承環境的新程序都繞得過(r1 繞過席實測 `env -u` 有效)。
4. 選中三成以內但很大的子集(例:多個關鍵字各跑一次)擋不到。
5. 對話裡 `git push` 讓推送前閘跑全套是規定的跑法,不擋;推送要放背景跑。

## 審計修正紀錄

- r1(2026-11-08,四席 sonnet:通才、正確性、繞過、架構對齊):24 條/blocking 12/插入點落在預設切片之後(四席獨立)、清變數早於判斷、`-k t_` 與空字串繞過、推送前閘提示被反擋、訊息印出逃生門、計數量不到、子程序測試環境沒清會遞迴;全部折入做 1–8 與條款 S1–S5,分組在 r1-intake.md。卷證:governance/review-reports/對話裡不准跑全套測試/。
