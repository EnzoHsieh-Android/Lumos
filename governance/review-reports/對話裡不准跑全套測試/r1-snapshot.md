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
RETIRE-IF: 連續八週治理帳與終端都沒有任何一次被擋下、而且記憶裡「對話裡跑全套」的事故也沒再發生 → 留著當守衛,不撤;若逃生門被用的次數超過被擋的次數(擋錯多於擋對)→ 撤掉改回只提醒。

## 狀態

設計中(2026-11-08)。

## 跟舊決定的關係

[[Projects/測試總檔預設切片_計劃]] d1(2026-11-05)在「預設切片 / Claude Code 工具前掛鉤擋 / 兩個都做」裡選了預設切片,解的是「全套被單一程序跑、慢到三小時」。本案解的是另一件事:全套根本不該在對話裡跑(就算切片也要約 4 分鐘、超過對話工具的兩分鐘預設上限、還占住使用者機器)。使用者在 2026-11-07(那個決定之後)明確要求做這個擋,所以不算翻案;擋的位置也不是那次不選的「工具前掛鉤」,是執行器本身。

## 範圍

### 做

1. **判斷函式**:`scripts/test_lumos.py` 新增 `_chat_full_suite_block(args, env)`,回擋下訊息或 None。擋的條件同時成立:`env["CLAUDECODE"] == "1"`;沒有 `LUMOS_PUSH_ATTEMPT`(推送前閘)、沒有 `LUMOS_FANOUT_CHILD`(預設切片開的子程序)、沒有 `LUMOS_ALLOW_FULL_SUITE=1`(逃生門);而且沒帶 `-k` 或位置關鍵字、沒帶 `--suite`、沒帶 `--list`。只帶 `--shard` 沒帶關鍵字也擋(那還是全套的一片)。
2. **接在 main**:參數解析完、`_isolate_environment()` 之前呼叫;擋下時印訊息到 stderr、回 2,不建暫存目錄、不載入任何測試。訊息三段:發生什麼(對話裡不准跑全套)、為什麼(約 8 分鐘、超過工具上限、推送前閘會自己跑)、怎麼辦(指令獨立一行:`python3.14 scripts/test_lumos.py -k <關鍵字>`;文件子集 `--suite docs`;真的要跑全套就 `LUMOS_ALLOW_FULL_SUITE=1`)。
3. **逃生門**:`LUMOS_ALLOW_FULL_SUITE=1` 時照跑,開頭印一行「對話裡放行跑全套(LUMOS_ALLOW_FULL_SUITE=1)」;不寫任何檔(執行器不准改工作目錄,測試本身會驗工作目錄乾淨)。
4. **不汙染子執行器**:判斷完(不論擋不擋)把 `CLAUDECODE` 從 `os.environ` 拿掉,跟清 `GIT_*` 同一段;理由:不少測試會在沙盒裡另開一個執行器跑全套(例:預設切片的測試),環境繼承自外層,不拿掉的話在對話裡跑那些測試的子集時,沙盒裡的子執行器會被誤擋。
5. **手冊與記憶指路**:`Systems/測試執行器` 補一行 WHY;CLAUDE.md 紀律區塊與專案〈測試子集怎麼跑〉那段不改字(規則照舊,現在多了機械擋)。

### 不做

- 不在 CI 擋:CI 沒有 `CLAUDECODE`。
- 不擋人在一般終端機跑全套:沒有 `CLAUDECODE` 就不判。
- 不寫治理帳:執行器不改工作目錄。
- 不管其他 AI 工具(Codex 等沒設 `CLAUDECODE` 的):另案。

## 實務隱患

- **人在 Claude Code 的終端分頁裡手跑**:那個殼也有 `CLAUDECODE=1`,會被擋;訊息裡印逃生門。
- **Claude Code 改了變數名**:擋不到但不會擋錯;寫成回頭條件。
- **測試沙盒繼承環境**:範圍 4 處理;測試另驗「判斷完 `CLAUDECODE` 已不在環境裡」。
- 已排除:金流:不碰付款
- 已排除:對外送出:不連網、不呼叫外部服務
- 已排除:不可逆:只改執行器入口的一段判斷,退提交即回原狀
- 守衛面:不排除——這是一道新的擋停(擋 AI 在對話裡跑全套),判風險高

REVISIT:2026-12-08 看這一個月對話裡有沒有再跑全套(記憶事故、終端紀錄)、逃生門被用了幾次;Claude Code 的 `CLAUDECODE` 變數還在不在

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 對話裡不准跑全套 | 使用者要求 | 使用者 2026-11-07:「又在跑全套，要講幾次」「你可以不斷繞過這個規則，代表這個功能根本沒做好吧」「推完戊線就去做擋全套的機制」 |
| 用 `CLAUDECODE=1` 認對話 | 本機實測 | 2026-11-08 在 Claude Code 殼裡 `echo $CLAUDECODE` 印 1 |
| 推送前閘的標記 | 既有程式 | `scripts/hooks/pre-push` export `LUMOS_PUSH_ATTEMPT` |
| 判斷放在執行器唯一進入點、清掉外部注入 | 既有先例 | `scripts/test_lumos.py` 的 main 清 `GIT_*` 與關子程序上色兩段;`scripts/scenario_probe.py` 開子程序前拿掉 `CLAUDECODE` |

## 驗收條款

- [S1] 當 `CLAUDECODE=1`、沒有推送前閘與切片子程序標記、也沒帶逃生門時,不帶條件或只帶 `--shard` 跑執行器 應 回 2 並印出子集與逃生門的指令;帶 `-k`、位置關鍵字、`--suite docs`、`--list` 任一 應 不擋 [test:t_runner_chat_full_suite_block]
- [S2] 當沒有 `CLAUDECODE`、或有 `LUMOS_PUSH_ATTEMPT`、或有 `LUMOS_FANOUT_CHILD`、或 `LUMOS_ALLOW_FULL_SUITE=1` 時,判斷 應 不擋;逃生門 應 印放行那一行 [test:t_runner_chat_full_suite_block]
- [S3] 當在 `CLAUDECODE=1` 的殼裡真的起一個執行器子程序、不帶條件時,它 應 在 5 秒內以 2 結束、應 沒有建任何 `gctl-run-` 暫存目錄 [test:t_runner_chat_full_suite_block_process]
- [S4] 當執行器判斷完之後,`CLAUDECODE` 應 不在它自己的環境裡(沙盒子執行器不會被誤擋) [test:t_runner_chat_full_suite_block_process]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | CLAUDECODE=1,無參數 | 擋 | 範圍 1 |
| S1 | CLAUDECODE=1,`--shard 2/4` | 擋 | 範圍 1 |
| S1 | CLAUDECODE=1,`-k foo` | 不擋 | 範圍 1 |
| S1 | CLAUDECODE=1,位置參數 `foo` | 不擋 | 範圍 1 |
| S1 | CLAUDECODE=1,`--suite docs` | 不擋 | 範圍 1 |
| S1 | CLAUDECODE=1,`--list` | 不擋 | 範圍 1 |
| S2 | 沒有 CLAUDECODE,無參數 | 不擋 | 不做 2 |
| S2 | CLAUDECODE=1 + LUMOS_PUSH_ATTEMPT,無參數 | 不擋 | 範圍 1 |
| S2 | CLAUDECODE=1 + LUMOS_FANOUT_CHILD,無參數 | 不擋 | 範圍 1 |
| S2 | CLAUDECODE=1 + LUMOS_ALLOW_FULL_SUITE=1 | 不擋,印放行 | 範圍 3 |
| S2 | CLAUDECODE=0 | 不擋 | 範圍 1 |
| S3 | 真子程序,CLAUDECODE=1,無參數 | rc 2、5 秒內、沒有暫存目錄 | 範圍 2 |

## 回退

退回本計劃的提交:執行器少了那段判斷與清變數,行為回到改動前;沒有寫任何檔或帳,不用收拾。

## 天花板

1. 只認 Claude Code 設的 `CLAUDECODE`;別的 AI 工具不受限。
2. 逃生門是環境變數,AI 自己也能設;只印一行、不留帳。

## 審計修正紀錄

