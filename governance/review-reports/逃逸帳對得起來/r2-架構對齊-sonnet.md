severity: major

## F1 撤回紀錄的「by」用自動讀 git 設定,跟專案既有的「由旗標明講是誰」做法不一樣
severity: major
blocking: 是
引句:「有自己的 token,不跟目標共用。」
引句:「"by":"<git user.name>","ts":"…","token":"<新的 ESC- 編號>"」

專案裡所有需要記「誰做的」的寫入指令,都是靠呼叫端明講的旗標值(`--by`/`--who`),不是工具自己去讀 `git config user.name`:
- file: `scripts/lumos:6539`(`cmd_signoff(env, node, note, by=None, ref=None)`,`by` 來自 `--by` 旗標,line 31602 `by=args.by`)
- file: `scripts/lumos:6558`(`_lint_waivers_add(..., who)`,`who` 同樣是呼叫端傳入,不是自動偵測)
- file: `scripts/lumos:31035`(`decision-supersede --by`,必填旗標,語意雖是「被誰取代」但也是「講清楚是誰/什麼」的旗標模式)
- file: `scripts/lumos:31048`(`rel-cascade --by`,值域 `ai|human`,同樣是明講的旗標)

全檔搜尋 `git config` / `user.name` 沒有任何一處會自動讀本機 git 身份寫進帳本(`grep -n "user\.name" scripts/lumos` 只命中 decision 的 `rollback` 欄與帳本 key 名,不是身份讀取)。這份設計在撤回紀錄的 `by` 欄改成自動讀 `git user.name`,是在既有「屬性用旗標明講」之外另開一條「自動偵測」的路——單人 repo 下兩者結果通常一樣,但跟本機 git 設定值可能不是這台機器在跑 CLI 的那個人(CI、共用帳號、多人共用同一顆 repo clone 都會誤記),而且是專案裡目前唯一一處這樣做的地方,屬於引入第二種做法。改成 `--by`(仿 signoff/rel-cascade,可留空預設回退某個值)會跟既有做法一致。

## F2 `--no-defect-ref` 的旗標語意跟專案裡其他 `--no-X` 旗標不同,容易讀錯
severity: minor
blocking: 否
引句:「跟既有旗標慣例一致),否則擋下。」
引句:「手動記帳兩個都沒有時,要另給 `--no-defect-ref "<為什麼沒有>"`」

專案裡目前所有 `--no-X` 旗標,語意都是「停用/排除 X」,不是「X 沒有時給個理由」:
- file: `scripts/lumos:31166`(`--no-lint`,`action="store_true"`,語意=不跑 lint)
- file: `scripts/lumos:31095`(`--no-hooks`,`action="store_true"`,語意=不裝 hooks)
- file: `scripts/lumos:30975`(`--no-tag`,`action="append"`,語意=排除帶這個 tag 的節點,值是「要排除的東西」)
- file: `scripts/lumos:30943`(`--no-any`,語意有獨立合約釘住,連自己都特別註明不共用)

這份設計的 `--no-defect-ref "<為什麼沒有>"` 拿的是一句必填的自由文字理由,語意其實是「defect-ref 沒有的理由」,跟上面幾支「不要 X / 排除 X」完全不同類。這不是引入第二種寫入路徑(仍是同一支 `cmd_loop_escape` 內的獨立驗證),只是命名讓人第一眼會以為它是布林開關;結構沒有問題,屬於命名層級的不一致(對應計劃裡自己說的「理由用獨立旗標,跟既有旗標慣例一致」——旗標確實獨立了,但「慣例一致」只做到一半,語意跟現有 `--no-X` 家族對不上)。改個名字(例如 `--defect-ref-reason`)就能解掉。

## 已看,無

- **分層與依賴方向(問1)**:新指令 `loop escape-stats`、`loop escape --withdraw` 都乖乖疊在既有讀寫原語上,沒有跨層直呼:讀帳一律經 `_escape_rows_for`(`scripts/lumos:7397`,計劃加 `include_withdrawn` 參數是既有函式的自然擴充,不是另開一套讀法);寫入一律包在 `_vault_write_lock`(`scripts/lumos:13757`,計劃裡「讀帳確認目標→寫入」整段上鎖,跟 `cmd_set`/`_auto_escape` 現有的「讀-改-寫包在同一把鎖裡」是同一形狀,`scripts/lumos:9342` `_auto_escape` 已示範過);分級沿用 `_loop_anchor_tier`(`scripts/lumos:17905`,取「帳上第一筆帶 tier 的值」,計劃第 67 行原樣照抄同一支函式的語意——這是 r1 架構席指出的第一點,已照做);範圍類沿用 `_plan_for_loop`(`scripts/lumos:9293`)並直接修在它裡面而不是另開一份平行邏輯,查計劃的呼叫者會一起受惠,是正確的「改共用函式」而非「新增一支繞過它」。
- **兩本帳分開讀、沒有混用(問1的延伸)**:計劃裡「治理帳有 `kind=converged`」對應 `_loop_gov_mark` 寫進 `.governance-log.jsonl` 的事件(`scripts/lumos:8392` 等多處 `_loop_gov_mark(env, loop_id, "converged", …)`),「審查帳裡有它的列」對應 `.canary-log.jsonl` 的逐輪紀錄——這兩本帳在專案裡本來就是分開的兩支檔案、各自有寫者,計劃沒有把它們的欄位混在一起判斷,對齊現況。
- **命名:撤回紀錄的 `kind` 欄(問2)**:用 `"kind"` 當事件判別欄位,跟治理帳既有的 `kind: converged|cap-reached|rewrite`(`scripts/lumos:551`)、`.canary-log.jsonl` 的 `kind: "spec-gate"` 同一種用法,沒有另創一套判別欄名字。
- **鎖與擋下訊息(問2)**:計劃要求「拿不到鎖印擋下,不讓例外冒出來」,對照現有 dispatch 層對 `_vault_write_lock` 逾時拋出的 `RuntimeError` 一律在 `main()` 用 `except (ValueError, RuntimeError) as e: print("擋下:…")` 接住(例如 `scripts/lumos:1185`、`1262`),方向一致;計劃沒有明講要在哪一層接,但既有慣例是留給 dispatch 層,不是 cmd 內部自己 try/except——這點計劃沒寫清楚,但沒有跟現況衝突,標 ⚠ 不升成 finding。
- **第二種做法對照(問3)**:計劃明講撤回走「稽核帳只追加、撤回也是追加一筆」而不是仿 `decision-supersede` 原地改欄位(`scripts/lumos:14327`,`valid:false`+`superseded_by` 是改寫單一 frontmatter 節點,不是 append-only jsonl)。這兩種資料形狀本來就不同:`decision-supersede` 動的是筆記節點的欄位,逃逸帳是純追加的 jsonl 帳本,專案裡所有 jsonl 帳本(canary-log、governance-log、signoff-log、kill-log、rel-cascade)一律只追加、沒有原地改列的先例,全檔搜尋不到任何一處會回頭改寫 jsonl 舊列。撤回選擇「另開一筆反向紀錄」是延續這條既有的 append-only 原則,不是另立新做法。
- **落點(問4)**:`Systems/loop-convergence-recording` 目前管 1 支檔(`scripts/lumos`)、掛 0 份計劃,計劃改動的函式(`_escape_rows_for`/`_auto_escape`/`cmd_loop_escape`/`_plan_for_loop`)全部落在同一支檔案裡,落進這篇既有節點是合理的,不需要另開一篇;唯一要指出的是這篇節點目前「沒寫負責範圍」(不合鐵則5),但這是既有缺口,不是這份計劃造成或需要解的,不列進不對齊清單。

不對齊共 2 條,其中 major 1 條。
