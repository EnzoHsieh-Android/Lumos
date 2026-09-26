severity: clean

已看,無:第 2 輪差異(r2-snapshot.patch)在「回滾與相容」這個鏡頭下逐項核對,沒找到能實際重現的洞。逐項記錄查了什麼、怎麼查的:

1. **`--by` 改名成 `--withdrawn-by` 有沒有漏改**:`grep -rn` 全 repo(scripts/lumos、scripts/test_lumos.py、四份 skill 文件、計劃筆記、loop-convergence-recording.md)裡所有跟 `escape --withdraw` 相關的位置(錯誤訊息、argparse help、內部欄位存取、測試呼叫),全部已經是 `--withdrawn-by`。唯一還留著舊字串 `--by "「誰」"` 的是 `governance/review-reports/逃逸帳對得起來/r1-snapshot.md`、`r2-snapshot.md`、`r3-snapshot.md` 這幾份——但那是照專案紀律「審查一輪只凍一份材料」凍結的歷史卷證,本來就不該回頭改,不算漏改。另外驗證了改名後***真的擋下***舊呼叫方式而不是靜默吃掉:
   ```
   python3 scripts/lumos --vault <v> loop escape --withdraw ESC-A --reason "理由夠長了" --by someone
   → 擋下:不認得這幾個參數:--by。 rc=2
   ```
   （argparse 直接擋,不會被舊腳本無聲誤用成別的語意。）內部撤回紀錄的儲存欄位仍叫 `"by"`(`rec = {"kind": "withdraw", ..., "by": by.strip(), ...}`,scripts/lumos:9625),讀側 `_list`/`_escape_withdraw` 都用同一個內部欄名,這是刻意的(CLI 旗標名跟 JSON schema 欄名分開),不是漏改。

2. **`_plan_for_loop` 擋路徑字元、`_escape_plan_scopes` 改用 `env.notes` 對既有呼叫者的影響**:`_plan_for_loop` 只有兩個呼叫者(scripts/lumos:8180 的代碼審自動記逃逸、scripts/lumos:9833 的 `_escape_plan_scopes`);前者呼叫前已經自己去掉 `code-` 前綴,不受這次改動影響(計劃回退段第 115 行也這樣寫,實跑核對一致)。新加的路徑字元擋(`/`、`\`、`..`)只會讓原本就查不到計劃的輸入提早回 `None`,對 repo 現有 `.escape-log.jsonl` 的所有 `loop` 欄位做過掃描,沒有一筆帶路徑字元,不會造成現有資料的分類倒退。`_escape_plan_scopes` 改讀 `env.notes` 而非重新讀檔:因為 `load_vault` 是 `vault.rglob("*.md")` 全掃且讀檔失敗也會把 Note(fields={})塞進 `notes` dict,`_plan_for_loop` 回的 `rel` 保證在同一個 `env.vault` 底下,`env.notes.get(rel)` 不會落空;又因為每次 CLI 呼叫都是全新 process、`Env.__init__` 才建一次 `load_vault`,不存在「同一次呼叫內先寫檔後讀 stale cache」的機會。實際端到端測過 `code-` 前綴 + env.notes 路徑一起生效:
   ```
   loop="code-回滾範例" → escape-stats --json
   → {"categories":[{"kind":"code","tier":"standard","scope":"retrieval",...}]}
   ```
   scope 正確解析出來,跟改動前用直接讀檔的版本行為一致。也核對了測試裡兩處用假 env(`type("E",(),{"vault":v})()`,只有 `.vault` 沒有 `.notes`)呼叫的函式(`_plan_for_loop`、`_review_loop_ids`、`_auto_escape`、`_escape_rows_for`)都不觸碰 `env.notes`,不會因為缺這個屬性而炸——會用到 `env.notes` 的只有 `_escape_stats`/`cmd_loop_escape_stats`,而這兩個永遠是透過 `run()` 走 subprocess 用真正的 `Env(vault)` 建的,測試裡沒有用殘缺 env 直接呼叫它們。

3. **舊版提醒文字有沒有出現在所有該出現的地方**:提醒只需要出現在「寫入一筆新格式(撤回)紀錄之後」這一個點,因為只有撤回紀錄缺 `loop`/`stage`/`severity` 這幾個舊版必讀欄位,才會被舊版誤讀;其餘新增欄位(如 `loop_kind`)是舊版本來就會忽略的多餘欄位,不需要提醒。實際切到這次改動之前一版(`40fcad7b^`)重現舊版讀新帳的行為,證實訊息內容屬實:
   ```
   （新版寫入含一筆 withdraw 紀錄的帳,拿舊版 lumos 讀)
   loop escape --list → 逃逸帳:2 筆(...)
     ?:1 筆(最重 非標準值 None(手改帳?))
   ```
   確實把撤回紀錄印成「?」分組、「非標準值(手改帳?)」的可疑列,且總筆數從 1 灌水成 2 ——跟訊息「會把它印成可疑列、治理帳統計多算」一致。目前 repo 裡只有這一處在寫入撤回紀錄(`_escape_withdraw`,scripts/lumos:9634),沒有第二個寫入口需要補提醒。

跑過 `python3 scripts/test_lumos.py -k escape`(121 passed)、`-k rule_gap`(6 passed)、`-k plan_for_loop`(1 passed),全綠,没有另外改動任何檔案(唯讀複本在 exp2-回滾/repo 底下跑)。
