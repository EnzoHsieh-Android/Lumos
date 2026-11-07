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

設計第三版(2026-11-08,折入設計審 r2 四席:判斷改看估計耗時)。

## 跟舊決定的關係

[[Projects/測試總檔預設切片_計劃]] d1(2026-11-05)在「預設切片 / Claude Code 工具前掛鉤擋 / 兩個都做」裡選了預設切片,解的是「全套被單一程序跑、慢到三小時」。本案解的是另一件事:全套根本不該在對話裡跑(就算切片也要約 4 分鐘、超過對話工具的兩分鐘預設上限、還占住使用者機器)。使用者在 2026-11-07(那個決定之後)明確要求做這個擋,所以不算翻案;擋的位置也不是那次不選的「工具前掛鉤」,是執行器本身。

## 範圍

### 做

1. **在對話裡一律不切片**:`_fanout_wanted` 多一個條件——在對話裡(`CLAUDECODE` 是 `1`)而且不是推送前閘(沒有 `LUMOS_PUSH_ATTEMPT`)時回 False,讓選測試、算耗時都在本程序做完才決定跑不跑(解 r2 兩席 blocker:放行的旗標後面接著預設切片、照樣開出全套)。判斷讀的是當下環境變數;判斷完才把 `CLAUDECODE` 從 `os.environ` 拿掉,讓測試開的沙盒執行器不繼承(這一步在參數解析之後、`_fanout_wanted` 之前,不跟清 `GIT_*` 同段,那段在參數解析之前)。
2. **選完照耗時判,不照旗標判**(r1、r2 同類兩輪打穿:`-k t_`、分片輪流、紀錄過大、文件子集都是「拿旗標或支數猜會跑多久」;換成看估計耗時):新增 `_chat_full_suite_block(selected, all_tests, args, env)`,回擋下訊息或 None。在對話裡、不是推送前閘、不是切片子程序(沒有 `LUMOS_FANOUT_CHILD`)、沒帶逃生門時,這次要跑的測試(分片、`-k`、`--suite keys` 都套完之後的清單)估計耗時佔全部測試估計耗時超過 `_CHAT_SUITE_SHARE = 0.2` 就擋。估法重用 `_shard_by_duration` 的權重:耗時表秒數,表裡沒有的用全表中位數,下限 `_DURATION_FLOOR`;耗時表讀不到時改用支數比例。`--suite docs` 不判(使用者允許對話裡跑的文件子集);`--list` 不判(只列不跑)。
3. **接在 main 的位置**:第 1 條在 `_fanout_wanted` 裡;第 2 條接在 `--list` 分支之後、開始跑測試之前,此時清單已經套完所有篩選。全部測試的分母在分片與篩選之前記下。擋下時印訊息到 stderr、回 2,在 `_isolate_environment()` 之前不開任何子程序。⚠ 因為選測試要先載入測試清單,這一條在 `_isolate_environment()` 之後才判得了;所以擋下時要照既有收尾把這一輪的暫存根目錄清掉(實作時確認既有 `finally` 收尾涵蓋這條路)。
4. **擋下訊息**:第一行「擋下:在對話裡這次要跑的測試約佔全套 N%(超過兩成),不准跑」;第二行講為什麼(全套約 8 分鐘、超過對話工具上限、推送前閘會自己跑);第三行起指令各自獨立一行:`python3.14 scripts/test_lumos.py -k <關鍵字>`、`--suite docs`、全套交給推送前閘(`git push` 放背景)或請使用者在一般終端機跑。**訊息不印逃生門的變數名**,逃生門只寫在 [[Systems/測試執行器]]。
5. **推送前閘的補救提示**(解 r1 正確性 F4、繞過 F8:原提示 `--ff -x` 在對話裡會被擋):`scripts/hooks/pre-push` 兩處「下一步」從 `--ff -x` 改成「用 `-k <紅的那支測試名>` 逐支重跑」,紅的名字掛鉤上面已印出。不新增 `--lf`(r2 指出它自帶紀錄過期、消費專案沒有紀錄、選中 0 支回綠、選中太多等於全套四個新洞;拿掉它的最小解就是逐支 `-k`)。
6. **逃生門要帶理由**:`LUMOS_ALLOW_FULL_SUITE=<理由>`,理由照 `lint-waive --note` 既有判法(去空白後至少 10 字、至少一個文字或數字字元)才算數;不算數照擋並講要寫理由。只在「本來會擋」時印一行「對話裡放行,理由:<理由>」。命名用 ALLOW:它放行的是一個動作、不是略過一道檢查。
7. **計數**:擋下與逃生門放行各追加一行到 `~/.cache/lumos/full-suite-guard/events.jsonl`(時間、種類、估計佔比、理由),寫法照 `scripts/lumos` 既有的家目錄快取寫入那一套(子目錄、驗目錄可信、只攔 OSError,單次寫入一行);寫不進去就略過、不影響判斷。不寫治理帳:治理帳在 repo 裡,執行器寫了會讓「工作目錄乾淨」的測試與提交前檢查看到改動。
8. **手冊**:[[Systems/測試執行器]] 補 WHY、逃生門寫法、`CLAUDECODE` 被拿掉的副作用(之後開的子程序看不到它;現在只有 `scripts/scenario_probe.py` 讀它而且本來就拿掉)。

### 不做

- 不在 CI 擋:CI 沒有 `CLAUDECODE`。
- 不擋人在一般終端機跑全套:沒有 `CLAUDECODE` 就不判。
- 不寫治理帳(理由見做 7)。
- 不管其他 AI 工具(Codex 等沒設 `CLAUDECODE` 的):另案。
- 不擋對話裡 `git push` 觸發的推送前閘全套:那是規定的跑法,推送要放背景跑。
- 不新增 `--lf`(理由見做 5)。

## 實務隱患

- **人在 Claude Code 的終端分頁裡手跑**:那個殼也有 `CLAUDECODE=1`,會被擋;要帶逃生門加理由。
- **Claude Code 改了變數名**:擋不到但不會擋錯;寫成回頭條件。
- **耗時表過期或不齊**:表裡沒有的測試照中位數估;表讀不到時照支數;估計不準只影響「兩成」那條線落在哪,不會讓全套溜過(全套永遠是 100%)。
- **測試沙盒繼承環境**:做 1 處理;驗收的子程序測試從頭組環境(只給 `PATH`、`HOME`、`CLAUDECODE=1` 與私有 `TMPDIR`),不繼承外層的推送前閘、切片子程序與逃生門標記,免得在推送前閘裡真的開出全套。
- **消費專案**:測試總檔會被安裝進消費專案,那邊在對話裡跑全套也會被擋,跟本 repo 一致;那邊沒有耗時表時照支數比例。
- **自動迭代迴圈**:headless 的 Claude 也設 `CLAUDECODE`;它跑全套同樣被擋,要改走推送前閘。
- 已排除:金流:不碰付款
- 已排除:對外送出:不連網、不呼叫外部服務
- 已排除:不可逆:只改執行器入口一段判斷、切片條件一行與推送前閘兩行提示,計數檔在工作目錄外;退提交即回原狀
- 守衛面:不排除——這是一道新的擋停(擋 AI 在對話裡跑全套),判風險高

REVISIT:2026-12-08 讀 `~/.cache/lumos/full-suite-guard/events.jsonl` 看這一個月擋下幾次、逃生門放行幾次與理由是不是正當情境(例:重現 CI 某一片);Claude Code 的 `CLAUDECODE` 變數還在不在

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 對話裡不准跑全套 | 使用者要求 | 使用者 2026-11-07:「又在跑全套，要講幾次」「你可以不斷繞過這個規則，代表這個功能根本沒做好吧」「推完戊線就去做擋全套的機制」 |
| 對話裡可跑文件子集 | 使用者先前允許 | 對話裡只准跑關鍵字子集或 `--suite docs`(2026-11-07 起的使用者規則,記在記憶 dont-rerun-verified-work) |
| 用 `CLAUDECODE=1` 認對話 | 本機實測 | 2026-11-08 在 Claude Code 殼裡 `echo $CLAUDECODE` 印 1;`bash -lc` 新殼仍是 1(r1 繞過席實測) |
| 推送前閘的標記 | 既有程式 | `scripts/hooks/pre-push` 在起測試前 export `LUMOS_PUSH_ATTEMPT` |
| 照耗時估、表裡沒有的用中位數 | 既有程式 | `scripts/test_lumos.py` 的 `_shard_by_duration` |
| 判斷不靠字面、改看結構量 | 手冊「同類兩輪換形狀」 | r1 `-k t_`、r2 分片輪流與紀錄過大同類兩輪打穿 |
| 逃生門理由判法 | 既有程式 | `scripts/lumos` 的 `lint-waive --note` 檢查 |

## 驗收條款

- [S1] 當 `CLAUDECODE=1`、沒有推送前閘與切片子程序標記、也沒帶逃生門時,這次要跑的測試估計耗時超過全部的兩成(不帶條件、只帶 `--shard 1/4`、`-k t_`),判斷函式 應 擋;兩成以內(例:`-k runner`)、`--suite docs`、`--list` 應 不擋 [test:t_runner_chat_full_suite_block]
- [S2] 當沒有 `CLAUDECODE`、`CLAUDECODE=0`、有 `LUMOS_PUSH_ATTEMPT`、有 `LUMOS_FANOUT_CHILD`、或逃生門帶了合格理由時,判斷 應 不擋;逃生門理由不合格 應 照擋;擋下訊息 應 不含逃生門的變數名;耗時表讀不到時 應 改用支數比例判 [test:t_runner_chat_full_suite_block]
- [S3] 當在對話裡呼叫切片判斷時,預設切片 應 不啟用;推送前閘裡 應 照舊啟用 [test:t_runner_chat_full_suite_block]
- [S4] 當用從頭組的環境(`CLAUDECODE=1`、私有 `TMPDIR` 與 `HOME`)真的起一個執行器子程序、不帶條件時,它 應 以 2 結束、私有 `TMPDIR` 裡 應 沒有留下 `gctl-run-` 目錄、私有 `HOME` 的計數檔 應 多一行擋下;前置:同樣環境拿掉 `CLAUDECODE` 時判斷函式 應 回 None(證明擋是 `CLAUDECODE` 造成的) [test:t_runner_chat_full_suite_block_process]
- [S5] 當推送前閘測試紅時,它的「下一步」提示 應 教用 `-k <紅的那支>` 重跑、應 不再印 `--ff -x` [test:t_prepush_red_hint_uses_k]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | CLAUDECODE=1,無參數(100%) | 擋 | 做 2 |
| S1 | CLAUDECODE=1,`--shard 1/4`(約 25%) | 擋 | 做 2 |
| S1 | CLAUDECODE=1,`-k t_`(100%) | 擋 | 做 2 |
| S1 | CLAUDECODE=1,`-k t_ --shard 1/16`(約 6%) | 不擋(天花板 4) | 做 2 |
| S1 | CLAUDECODE=1,`-k runner`(低於 20%) | 不擋 | 做 2 |
| S1 | CLAUDECODE=1,`--suite docs` / `--list` | 不擋 | 做 2 |
| S2 | 沒有 CLAUDECODE / CLAUDECODE=0,無參數 | 不擋 | 不做 2 |
| S2 | CLAUDECODE=1 + LUMOS_PUSH_ATTEMPT 或 LUMOS_FANOUT_CHILD | 不擋 | 做 2 |
| S2 | CLAUDECODE=1 + 逃生門理由「重現 CI 第三片紅燈要整套」 | 不擋,印放行與理由 | 做 6 |
| S2 | CLAUDECODE=1 + 逃生門 `1` 或十個句點 | 擋,講要寫理由 | 做 6 |
| S2 | 耗時表讀不到,選中 25% 的支數 | 擋 | 做 2 |
| S3 | CLAUDECODE=1,無參數 | `_fanout_wanted` 回 False | 做 1 |
| S3 | CLAUDECODE=1 + LUMOS_PUSH_ATTEMPT,無參數 | 照舊切片 | 做 1 |
| S4 | 真子程序,從頭組環境,無參數 | rc 2、沒有留下 gctl-run-、計數 +1 | 做 3、7 |
| S5 | 推送前閘一支紅 | 提示 `-k <那支>`,沒有 `--ff -x` | 做 5 |

## 回退

退回本計劃的提交:執行器少了判斷、切片條件與清變數,推送前閘提示回到 `--ff -x`,行為回到改動前;計數檔在 `~/.cache/lumos/full-suite-guard/`,留著無害、可手刪;沒有寫任何 repo 檔或帳。

## 天花板

1. 只認 Claude Code 設的 `CLAUDECODE`;別的 AI 工具不受限。
2. 逃生門與兩個豁免標記(`LUMOS_PUSH_ATTEMPT`、`LUMOS_FANOUT_CHILD`)都是環境變數,AI 讀原始碼就知道;逃生門至少留理由與計數,手設豁免標記沒有紀錄(屬刻意偽造,不防)。直接手跑 `scripts/hooks/pre-push` 腳本也會帶出 `LUMOS_PUSH_ATTEMPT`(r2 繞過 F5),同屬這一類。
3. `env -u CLAUDECODE`、`CLAUDECODE=0`、tmux 或 cron 這類不繼承環境的新程序都繞得過(r1 繞過席實測 `env -u` 有效)。
4. 兩成以內的子集一次次分開跑擋不到(例:`-k t_ --shard i/16` 跑 16 次)。
5. 對話裡 `git push` 讓推送前閘跑全套是規定的跑法,不擋;推送要放背景跑。
6. 估計耗時用的是過去量到的秒數,機器變慢或測試變慢時估計會偏低。

## 審計修正紀錄

- r1(2026-11-08,四席 sonnet:通才、正確性、繞過、架構對齊):24 條/blocking 12/插入點落在預設切片之後(四席獨立)、清變數早於判斷、`-k t_` 與空字串繞過、推送前閘提示被反擋、訊息印出逃生門、計數量不到、子程序測試環境沒清會遞迴;全部折入做 1–8 與條款 S1–S5,分組在 r1-intake.md。卷證:governance/review-reports/對話裡不准跑全套測試/。
- r2(2026-11-08,四席 sonnet 新席):20 條/blocking 8(blocker 2)/`--lf` 被預設切片開成全套(兩席獨立)、`--lf` 紀錄過期與過大、三成門檻分母不明、分片輪流繞過、文件子集其實四分鐘、計數寫法不照既有、直接手跑掛鉤帶出豁免;同類「照旗標或支數猜耗時」第二輪打穿,換形狀成對話裡不切片、選完照耗時表估佔比,拿掉 `--lf`;分組在 r2-intake.md。
