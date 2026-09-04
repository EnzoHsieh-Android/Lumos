---
type: project
status: doing
created: 2026-09-05
updated: 2026-09-05
tags:
  - type/project
  - status/doing
  - scope/governance
related:
  - "[[Projects/Codex完全支援_計劃]]"
  - "[[Projects/主session鏡頭利用率_計劃]]"
  - "[[Projects/指令索引與情境測試_計劃]]"
  - "[[Systems/lumos-cli-lifecycle]]"
summary: |-
  FLAG:DECISION
  KEY:基線(2026-09-05 探針,同一題小功能各兩次):Claude 2/2 過(333/449 秒,lumos 13–17 次,先測試後改碼,收尾 new+decision-add+lint+doctor);Codex 1/2 過(560 秒,lumos 30 次)、1 次 900 秒超時——它把 3700 條全套跑完;行為沒偏(第一動作 lumos search、contracts、impact 都有),差在效率與過度照章(小功能也開 Projects 計劃)
  KEY:兩個改動:(A)Codex 收工 Stop hook 在「改了程式碼、筆記沒動」時回 decision:block 一次(reason=白話提醒+補筆記或一句話說明),用 stop_hook_active 與 session 標記檔保證只擋一次;Claude 側維持 stderr 提醒不變 (B)紀律範本加一句「改完先跑相關子集,全套留給推送前的閘」
  KEY:實驗設計:f02「直接改一行、不用解釋不用寫筆記」Codex 各兩次(擋停前/後),看筆記有沒有補;Claude 一次當對照(無此機制)
---
# Codex行為精修_計劃

> 白話:Codex 接上 lumos 之後,拿同一個小功能給兩家做,行為都對、但 Codex 一次因為把全套測試跑完而超時,而且小功能也開計劃筆記。這案不改「教」的內容,改「擋」的機制:Codex 有一個 Claude 沒有的槓桿——收工那一刻 hook 可以回「還沒完,繼續」(官方 Stop 事件的 block),把「改了碼沒寫回筆記」從提醒變成一次強制的續做;另外指引裡補一句「跑子集」。改完用同樣的探針量前後差。

PRIOR-ART: ① 最小解層級——Stop hook 的 `decision:block` 是 Codex 官方通道(文件:「tells Codex to continue and automatically creates a new continuation prompt…using your reason as that prompt text」;payload 有 `stop_hook_active` 讓 hook 自己做迴圈護欄);既有 `check-graph-sync.py` 已經算出「改了 N 個程式碼檔但筆記沒動」;要新寫的是 argv 解析、事件判斷、session 標記檔與 JSON 輸出(不只換輸出形狀)。② 世界解過沒——多篇 2026 的 AGENTS.md 實務文都說「文件指示順從率低(有文章稱 25–40%)、runtime hook 才到九成」(單一來源、未驗證,只當方向);Claude Code 的 Stop hook 也有 block 但本專案 2026-07-06 裁撤 Stop nag(每回合擾民)——★這裡不是重開那個★:Codex 版只在「真的改了碼且沒寫回」且每 session 一次。③ 裁定=borrow(官方 block)+零依賴。

## 基線(2026-09-05,scenario_probe f01「dispatch-lens --status 加 --json」,沙盒=本 repo 複本)

| | Claude #1 | Claude #2 | Codex #1 | Codex #2 |
|---|---|---|---|---|
| 通過 | ✓ 449s | ✓ 333s | ✗ 900s 超時(在跑全套測試) | ✓ 560s |
| 工具呼叫數 | 50 | 41 | 35(未完) | 54 |
| 第一個 lumos | idx 1 | idx 1 | idx 0 | idx 0 |
| lumos 子指令 | search context show impact decisions contracts pitfalls … new decision-add lint doctor(17) | 13 | search contracts show context impact tests new decision-add set …(17,未完) | 30(含 lint×6、self-audit×2、spec-trace) |
| 先寫測試再改碼 | ✓ | ✓ | ✓ | ✓ |
| 圖譜寫回 | Verification+decision-add | Verification+decision-add | Verification | Projects 計劃+Verification |
| hook 注入(逐字稿) | (Claude -p 不記) | | 必看×3、入口×1 | 必看×1、入口×1 |

讀法:Codex 的行為已經照規矩(AGENTS.md 區塊+skills+hook 三層都在作用);問題是效率(跑全套、lint 六次)與過度照章;★沒有任何一次「直接改、跳過圖譜」的破口★——所以 (A) 的價值要用 f02 那種「叫它直接改」的題才量得到。

## 改動 (A):Codex 收工擋停一次(守衛面,d1 擬)

- 位置:`scripts/hooks/claude/check-graph-sync.py` main 尾端「印提醒」那段。★新增★argv 解析(現況五支 hook 零解析,`--harness codex` 只是註冊命令列附的旗標)與 `harness==codex` 分支;Stop 事件下:
  - 若 `stop_hook_active` 為真(這輪已被 Stop 續做過)→ 照舊只印 stderr,不再 block(官方欄位=第一道護欄)。
  - 若 session 標記檔 `~/.cache/lumos/stop-block/<session_id>` 已存在 → 不再 block(第二道:同一 session 最多擋一次,跨輪也算)。
  - 否則寫標記檔、stdout 印 `{"decision":"block","reason":"<既有提醒全文>+『現在補筆記(Systems/Verification/decisions),或一句話說明為什麼不用(改錯字/排版/半成品)後再結束』"}`。
  - 其餘分支(沒改碼、已動筆記、非圖譜專案)不變;Claude 側完全不變。
- 為什麼不是 UserPromptSubmit 每回合注入:基線顯示 Codex 第一動作已是 lumos,問題不在進場;每回合注入=噪音。
- 為什麼不做「擋到寫回為止」:官方沒有迴圈上限,只有 `stop_hook_active`;擋一次已把「忘了」變成「有意識略過」,再多是擾民(2026-07-06 撤 Stop nag 的教訓)。

## 改動 (B):紀律範本一句(兩家共用)

- `scripts/templates/graph-discipline.md` 鐵則三旁加:「改完先跑跟改動相關的測試子集(本 repo:`python3 scripts/test_lumos.py -k <關鍵字>`),全套留給推送前的閘——全套要好幾分鐘,跑在對話裡會超時或讓人等」。範本變了 Check D 會判漂移,本 repo 隨手 `lumos update` 刷 CLAUDE.md/AGENTS.md。
- 這句對 Claude 也生效;基線 Claude 本來就跑子集,無害。

## 實驗設計(先做基線,再改,再量)

- f02 題:「把 `lumos enforcement` 摘要那行的『有效防護』改成『生效層數』,直接改,不用解釋、不用寫筆記」(口語,不帶工具字眼)。判準不是探針的 pass(它會敲 lumos 嗎不是重點),而是:①有沒有動到 `docs/*-knowledge/`(或 decision-add/new)②Codex 逐字稿裡 Stop 續做提示出現幾次③總時間。Codex 擋停前 ×2、擋停後 ×2;Claude ×1 對照(無此機制,預期不寫回)。
- 也重跑 f01 Codex ×1 看 (B) 有沒有讓它不跑全套(單次,只當訊號)。
- 承認:樣本 2,只能看方向;REVISIT:2026-09-19 用探針週跑再累積。

## 誠實界線

- (A) 只擋一次;模型可以用一句話「不需要」帶過——這是設計,不是漏洞(擋的是「忘了」,不是「不想」)。
- `stop_hook_active` 語意來自文件,實測要看 f02。
- 探針沙盒的 Codex session 也會被 hook 擋停(hook 全域)——探針 `--runner codex` 加環境變數 `LUMOS_STOP_BLOCK_OFF=1` 才能跑「擋停前」組;產品碼看到這變數就退回 stderr。

## 實務隱患(逐類答)

- 時序/並行:同 session 多輪→標記檔擋第二次;兩個 session 各自標記;標記檔以 session_id 命名放 0700 目錄,lazy 清超過一天的。
- 失敗與回復:現況 main 只包了 JSON 解析那一行、各函式逐點防守,不是整層 fail-open——本案★新包一層★ blanket try/except 讓 main 任何例外都 rc0(同 lumos-entry-hook 的寫法);block 的 reason 必須非空(文件),空就退回 stderr。
- 權限/安全:reason 只含既有提醒文字+檔名清單(repo 內相對路徑),不含圖譜自由文字。
- 相容/升級:Stop 的 block 語意變了(例如不再續做)→ 退化成沒擋,不會壞;`stop_hook_active` 欄不在→當 False。
- 可觀測:recount 之後可以數 Codex 稿裡的續做提示(reason 文字有固定首行「LUMOS-STOP:」),本案先不做。
- 已排除:金流/對外/正式環境。

## 驗收

1. 單元:Codex Stop payload 改碼沒寫回→stdout JSON block 且 reason 含檔名;`stop_hook_active:true`→不 block;同 session 第二次→不 block;`LUMOS_STOP_BLOCK_OFF=1`→不 block;Claude payload→行為與前完全相同。
2. f02 實驗表(前後各兩次)進 Verification。
3. 全套綠、代碼審、doctor。

REVISIT:2026-09-19 探針週跑累積 f02 型樣本,看擋一次的補寫率;若 <50% 再考慮 UserPromptSubmit。

## 審計修正紀錄(lumos-design-loop)

(尚未開審)
