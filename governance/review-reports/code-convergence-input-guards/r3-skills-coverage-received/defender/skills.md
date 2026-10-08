severity: major  
裁決: concern

總結：F1 是 code 層假陽性；F2 保留為既有的核可來源可信度問題，但原報告主張的「受審材料自動進入執行器並放行」沒有實際資料流證據。本批沒有新增這兩個判準，也不能宣稱既有問題已修。

### skills-coverage-資安-F1

severity: major  
裁決: evidence

引句:「新增流程把自由文字直接示範成雙引號內的 shell 參數，沒有要求 argv-safe 呼叫」

- 現象「`--note` 會執行 `$()`／反引號」：MISS。
- 本批新增此判準：MISS。

實際邊界：

- 真正入口是 argparse 的 `--note` 字串，之後直接傳給 `cmd_loop_cap_decision` 或 `cmd_loop_retro`：`scripts/lumos:49134-49150`、`scripts/lumos:50167-50172`。
- `cmd_loop_cap_decision` 只驗長度、UTF-8、迴圈範圍與輪數，再把 note 當 JSON 欄位交給 `_gate_event`；沒有 `subprocess`、`eval` 或 shell：`scripts/lumos:13794-13834`。
- retro 的 `--skip --note` 同樣只驗文字後記帳：`scripts/lumos:13860-13871`、`scripts/lumos:13945-13951`。
- `_gate_event_build` 把 note 放進 `note`／`detail` 欄位，沒有執行：`scripts/lumos:1278-1306`。

最小實驗使用真 CLI，把字面值 `$(printf short)` 經 shell 變數作為單一 argv 傳入。結果進到「迴圈不在人裁範圍」檢查；若 `$()` 曾被執行，值會變成不足十字的 `short`，應先被 `--note 至少 10 字` 擋下。實際未發生替換，退出碼 2，且未寫 repo。

誰／輸入／收益：

- 只有「先把不可信文字拼成 shell 原始命令」的呼叫者，才會在 CLI 啟動前觸發 shell 展開。
- 受審 diff、報告或回顧文字沒有直接流入這條命令。本批模板也沒有要求把其內容逐字複製到 note。
- 因此透過目前 CLI 路徑的命令執行收益為零。若編排者另行把不可信內容插入 shell source，注入會成立，但那是原報告未證明的條件推論。

相鄰既有指令廣泛使用同型 placeholder，例如 `skills/lumos-code-loop/SKILL.md:24`、`:53` 與 `skills/lumos-project-notes/commands/06-代碼審與推送.md:7-14`。真正會把受審檔案送給外部程式的流程，則明訂從 stdin 讀、不可塞進 shell 引號：`skills/lumos-project-notes/commands/06-代碼審與推送.md:53`。

此外，原引句中的 `--decision … --note "<理由>"` 已存在於基線 `d9f28e…:skills/lumos-code-loop/SKILL.md:59`；候選版 `skills/lumos-code-loop/SKILL.md:60` 只新增「回顧分類核對修補因果、保留未知」。不能把整行因 diff 顯示為修改，就歸因成本批新增注入面。

### skills-coverage-資安-F2

severity: major  
裁決: concern

引句:「本材沒有把決策綁到可驗證的核可者、核可來源或不可由 agent 自填的證據」

- 現象「CLI 不驗證真人核可來源」：HIT。
- 現象「受審材料會自動進入執行器並冒充核可」：MISS／條件推論。
- 本批新增此判準：MISS。

實際邊界：

- `cap-decision` 沒有 approver、核可訊息 ID 或簽章參數；只驗固定 decision、note、迴圈種類與輪數：`scripts/lumos:13794-13834`。
- 寫入事件只有時間、commit、gate、kind、note 與額外結構欄位，沒有核可者身分：`scripts/lumos:1278-1306`。
- `completed_by` 只要求非空、不得等於 `drafted_by`；它是回顧補完者欄位，不是 `cap-decision` 的授權證據：`scripts/lumos:13429-13438`。
- 所以任何已有本機執行與 repo 寫入能力的程序，都能自報「人裁」並留下治理紀錄。若治理帳被視為真人核可證明，這是仍存在的舊可信度缺口，不能宣稱已修。

但原報告把收益說得過寬：

- `accept-risk` 不會允許新一輪；它會令新一輪 `canary record` 明確被擋，`--skip` 也不能解除：`scripts/lumos:13680-13684`。既有測試原始碼亦釘住此行為：`scripts/test_lumos.py:72486-72505`。
- `extra-round` 只有在回顧合格或記錄 skip 後才允許新輪：`scripts/lumos:13685-13693`。
- recorded／skipped 可滿足處置閘的「跑滿回顧」步驟：`scripts/lumos:13723-13733`；但不會取代其他處置條件。code-loop 只要輪內有 major，`accepted` 仍必須為空：`scripts/lumos:24574-24593`。
- 新增回顧模板只讓乾淨代理填回顧 JSON，且明訂不得填 `completed_by`：`skills/lumos-design-loop/templates.md:443-449`、`:470-474`。它還明訂報告或作者結論只是待驗主張，不作判準：`:466-468`。沒有「讀報告文字後自動呼叫 cap-decision／skip」的程式路徑。

實際攻擊者因此必須再取得一個未證明的前提：讓具有本機治理權限的編排者違反來源邊界，把受審材料當成人的當前核可並主動執行命令。原報告沒有重現這一步，故不能定為已證實的自動越權鏈；但缺乏可驗證真人來源本身仍是應保留的既有 concern。

### 基線與驗證限制

- `cmd_loop_cap_decision`、`cmd_loop_retro` 及相關 retro 判定函式在基線與候選版的抽取內容 SHA-256 完全相同；本批未改這些入口或信任邊界。
- 嘗試執行兩條既有 targeted tests 時，環境因唯讀而報 `FileNotFoundError: No usable temporary directory found`；因此沒有宣稱測試已通過。
- 未讀其他席報告，未修改指定報告或 repo。