severity: minor

## F1 手動記帳這次也動了寫入,但仍不比照撤回上鎖
severity: minor
blocking: 否
引句:「手動記帳今天只把 `--defect-ref` 寫進列、`--sha` 沒寫進去(r2 正確性席重現),這次一起補上」
現況(既有做法):`cmd_loop_escape` 的手動記帳分支(`file: scripts/lumos:9472-9533`)目前完全不呼叫 `_vault_write_lock`,直接走 `_jsonl_append_verified` 落盤;而 `_auto_escape`(`file: scripts/lumos:9316-9321`)已經把「讀 existing→判重複→append」整段包進 `_vault_write_lock`,理由是「兩個 hook 同時寫,各自讀到『還沒包含對方那筆』的 existing,去重會被繞過」。本次設計第三節明講撤回要補鎖(「手動記帳今天沒上鎖,這裡要明確加」),但只針對撤回這條新指令;同一節第二節卻明確要改動手動記帳分支本身(補寫 `--sha`、驗證 `defect_ref`/`missing-defect-ref`),沒有一併把這條既有寫入路徑納入 `_vault_write_lock`。結果是同一支 `loop escape` 底下三種寫入模式(auto/withdraw/手動)只有兩種上鎖,手動記帳仍留著跟 `_auto_escape` 當初修的同一類競態(兩個人同時手動記,或手動記與自動記同時觸發,讀 `existing` 去重會被繞過)。這不是本案新引入的做法,但本案這輪已經觸碰這支函式、也已經為撤回把鎖語意講清楚,若不順手補齊,會在同一個子指令族裡留下「有的分支上鎖、有的不上鎖」兩種寫入紀律並存。

## 已看,無:
- 分層與依賴方向:`escape-stats`、撤回、規則缺口統計都經同一組既有讀寫原語(`_escape_rows_for`、`_vault_write_lock`、`_jsonl_append_verified`),沒有新開一條繞過既有函式的路徑;`_escape_rows_for` 的四個既有呼叫點(`scripts/lumos:2301,6303,7082,18551`)都會自動吃到本案加的「非物件跳過」與 `include_withdrawn` 過濾,不必逐處手改。`rule-gap`(`scripts/lumos:20215`)本來就獨立找檔(支援 standalone 佈局),設計只要求它套「同一支判斷函式」而非改成呼叫 `_escape_rows_for`,跟它現有結構一致。
- 命名與錯誤處理:`--by` 明講、不讀 git config,與 `decision-supersede --by required=True`(`scripts/lumos:31035`)同款;理由旗標改名為 `--missing-defect-ref` 避開 `--no-` 前綴,查過全檔 `--no-*` 旗標(`--no-run`、`--no-lint`、`--no-pull`…)確認都是「關掉 X」語意,設計避開這個坑是對的;理由「≥4 字含實字」與 `_MANUAL_MIN_CHARS`(`scripts/lumos:5739,7713,30760`)既有門檻一致;`_plan_for_loop` 加 `code-` 前綴剝除與 NFC 前,已核對它目前唯一呼叫者(`scripts/lumos:8010`)本來就自己先剝了前綴才呼叫,回退段「單獨回退 `_plan_for_loop` 不影響既有呼叫者,但會讓 escape-stats 靜默歸成未分類」這個判斷跟程式碼一致。
- 第二種做法:撤回紀錄用獨立 `token` + `target` 欄位指回被撤列,不直接改動原列——這跟既有「只追加,不改舊列」的帳本哲學(`kind=rewrite` 用 `note` 存 `prev=/successor=` 血緣、不改舊 canary 列,`scripts/lumos:813-843`)同一路數,只是欄位從字串編碼換成結構化欄位(既有 escape 列本來就已是結構化欄位,不是新引入的做法)。`kind=spec-gate` 留痕不算審查紀錄這條排除規則,在既有程式碼裡已有三處先例(`scripts/lumos:9088,9604,9912`),設計照搬同一判準,不是另立一套。
- 落點:`Systems/loop-convergence-recording` 目前管 `_escape_rows_for` 所在的那支檔,0 份計劃掛著、沒寫負責範圍,是這次唯一會落地新函式/新旗標說明的既有節點,落點合理,不需要另開。

不對齊共 1 條,其中 major 0 條。
