severity: major

審查鏡頭:邊界與可執行(第 2 版)。實驗全在 mktemp 臨時 repo 內做,對照碼 repo 唯讀;用 python3.14 直接 import scripts/lumos 呼叫 `_push_range_start`,並用現有指令餵 `X..X`、sha1 空樹..sha256 頂端。派工時 hook 沒有附計劃牽連的合約/事故節點,固定席判斷部分無對象:已讀,無 finding。

## F1 SHA-256 repo 在「找不到主線、全新首推」會印出 SHA-1 空樹,會擋的閘整批無聲放行
severity: major
blocking: 是 判準:修改後比修改前更鬆(今天掛鉤自己算的空樹在 SHA-256 是對的,會擋;改後會擋的閘變成 fail-open)。
spec 段落:範圍第一條與做法第 1 點。
引句:「其他印 `起點..頂端`。」
問題:做法第 1 點只讓 `_PUSH_START_UNKNOWN` 走 `_drift_empty_tree`(本 repo 的雜湊算法);但 `_push_range_start` 在最常見的「全新 repo 首推 main、沒有任何遠端追蹤分支」會直接回傳寫死的 SHA-1 空樹常數(`scripts/lumos` 的 `_push_no_mainline`,回 `_EMPTY_TREE_SHA`,值 4b825dc6…)。spec 把它當「其他」原樣印出。這個 40 位十六進位字串通過掛鉤那條 `^[0-9a-f]{40,64}\.\.[0-9a-f]{40,64}$` 檢查,所以掛鉤會採用。
具體例:`git init --object-format=sha256`,三個提交、無遠端,對 `_push_range_start(".", "0"*64, tip, "origin", "refs/heads/main")` 實測回 `('4b825dc642cb6eb9a060e54bf8d69288fbee4904', '…新分支首推:從空樹算…')`,頂端 64 位。`git diff 4b825dc6…..HEAD` 實測報 unknown revision。接著 `pitfalls --diff <該範圍> --no-lint --json` 實測 rc2、無 JSON;`code-loop check --diff <該範圍> --at-sha …` 實測 rc0 並印「OK——可以推(tier=unknown):pitfalls 失敗(fail-open)」。掛鉤 `scripts/hooks/pre-push:371-372` 的 `pitfalls` 是 `2>/dev/null || true`,JSON 空 → `_tier_high=0`;code-loop check 回 0。預期:跟今天一樣整個 repo 當新改動、照擋。實際:會擋的那幾步全部無聲放行。
另:S1–S7 沒有 SHA-256 案例,測試抓不到。
同一段還有一個相鄰問題:`push-range` 的 UNKNOWN 分支與正常分支各用一套空樹來源,spec 沒有要求「凡是空樹一律用 `_drift_empty_tree`」這條統一規則。

## F2 推 main 且舊值本機找不到時,只查最後一個提交(S7 把今天的「全掃」變成「只掃頂端那一個」)
severity: major
blocking: 是 判準:修改後比修改前更鬆,且與 spec 自己宣稱「不會更鬆」相反。
spec 段落:實務隱患「舊版 lumos」與守衛面、驗收 S7。
引句:「不會更鬆。」
引句:「起點由存量漂移檢查已在用的那支算,失敗一律退回空樹(多擋)」
問題:S7 要求舊值找不到時「不再從空樹」。`_push_range_start` 的 `_push_no_mainline` 在「找不到主線 + 舊值找不到」時退到頂端的第一個父提交,函式自己的說明就寫「只查最後一個提交」。而被推的那條分支本身永遠被 `_push_mainlines` 跳過(候選指到 refs/remotes/<遠端>/<被推分支> 與目標完全相同才跳,見該函式),所以「推 main、別人 force-push 過、本機沒 fetch」這個 S7 的典型情形,遠端 HEAD、main@{upstream}、遠端 main 三個候選全被跳過,必走這條路。
具體例:本機 main 比舊遠端多 5 個提交,遠端被別人 force-push 後本機沒 fetch(舊值本機無此物件),`git push origin main`。實測 `_push_range_start(".", "a"*64, tip, "origin", "refs/heads/main")` 回「從頂端的第一個父提交 127f686f557c 算,只查最後一個提交」。預期(spec 第 56 行字面):範圍涵蓋這次要推的提交,或至少不比今天鬆。實際:前 4 個提交完全不進會擋的閘(風險分級、code-loop check、doctor 的碰到清單)。這等於把「force-push 之後再推」變成繞過會擋的閘的穩定做法。
spec 的說法互相矛盾:守衛面說「失敗一律退回空樹(多擋)」,但這條不是失敗,是正常成功路徑,不會退空樹。

## F3 舊版 lumos 或呼叫失敗時,錯誤文字原樣噴到終端,而且沒有任何「這次沒用真起點」的說明
severity: minor
blocking: 否 判準:只影響訊息,放行/擋的結果與今天相同。
spec 段落:範圍第二條、實務隱患「舊版 lumos」。
引句:「舊版 lumos 沒有這個指令、失敗、印出怪東西)退回 `空樹..頂端`(同今天)。」
問題:spec 沒規定 `push-range` 的 stderr 怎麼處理。實測舊版行為:`lumos push-range` 回 rc2 並印「擋下:沒有「push-range」這個指令。…」到 stderr。掛鉤若不 `2>/dev/null`,每個新分支首推、每個 ref 兩次(`pp_touched_file` 與迴圈各一次)印出以「擋下:」開頭的字,但推送並沒被擋(同檔漂移那段專門加了一句註解解釋同樣的誤導)。反過來若丟掉 stderr,退回空樹時使用者看不到為什麼又被 715 條擋,看不出是 lumos 太舊。
具體例:消費專案新掛鉤配舊 lumos,推新分支 → 看到「擋下:沒有 push-range」加上原本的誤擋,兩者的關係無從判斷。
規則:退回空樹時掛鉤自己印一行固定句(含「lumos 太舊/起點算不出,這次照舊用空樹」),stderr 的細節另處理;spec 沒有這條,測試 S5 也只驗退回、不驗訊息。

## F4 參數規格內部不一致:「必帶」「少一個 rc2」與「遠端名空的」「參數錯 rc2」對不上
severity: minor
blocking: 否 判準:掛鉤端怎樣都退回空樹,不影響放行結果;只影響手動跑與測試怎麼寫。
spec 段落:範圍第一條、做法第 1 點、實務隱患「遠端名是網址或空的」。
引句:「`--push-remote` 與 `--pushed-ref` 必帶(少一個 rc2),同 `drift check` 的參數規矩。」
問題:`drift check` 的規矩實際是「兩個要一起給,都不給也行,只給一個 rc2」(`scripts/lumos` 的 `cmd_drift_check`:`(push_remote is None) != (pushed_ref is None)`),不是「必帶」。spec 兩句互相矛盾。另外手動跑掛鉤時 `$_PP_REMOTE` 是空字串,掛鉤會傳 `--push-remote ""`(argparse 收成空字串、不是 None);spec 實務隱患寫「找不到主線時全零起點回空樹」暗示照常算,但 S6 的「少帶 rc2」是否把空字串算成少帶沒講。另外頂端解不出提交(`_lens_full_sha` 回 None)時 rc 與輸出 spec 沒定義。
具體例:`lumos push-range --diff 000…0..HEAD --push-remote "" --pushed-ref refs/heads/x` 是 rc2 還是印範圍?照字面兩讀都成立。

## F5 每個新 ref 兩次 lumos 啟動、內部 git 查詢各 20 秒逾時,掛鉤沒有整體時限
severity: minor
blocking: 否 判準:逾時最終走 `_PUSH_START_UNKNOWN` → 空樹,結果與今天相同,只是慢。
spec 段落:實務隱患「時間」。
引句:「跟存量漂移檢查同量級。」
問題:實測 `lumos` 空跑一次約 0.57 秒(啟動 python3.14 載入單檔),不含 git。`pp_touched_file`(`scripts/hooks/pre-push:289`)與迴圈各呼叫一次,所以 `git push --all` 首推 30 個分支至少 60 次啟動(約 35 秒起跳)。每次 `push-range` 內有 `rev-parse`、`merge-base --is-ancestor`(每個主線候選一次)、`merge-base --all`,各自 `_lens_git` 預設 20 秒逾時;大 repo、淺層 clone 最壞每次數十秒到分鐘,掛鉤層沒有 `timeout` 包它。drift 那段是「每個 ref 一次」,本案是兩倍。可行的收斂:`pp_touched_file` 與迴圈共用同一個 ref 的結果(迴圈前先算一次存進陣列),把呼叫數砍半。

## F6 `_EMPTY_TREE` 算不出時 `pp_block_range_for` 的最後退路是壞字串,且與迴圈那句 continue 的先後沒定
severity: minor
blocking: 否 判準:git 環境壞到連空樹都算不出,其他閘也同樣跑不起來,今天已是 advisory 放行。
spec 段落:做法第 2、3 點。
引句:「印出的那一行要符合 `^[0-9a-f]{40,64}\.\.[0-9a-f]{40,64}$` 才用,否則退回空樹。」
問題:退回空樹時用 `$_EMPTY_TREE`,而它在 `git hash-object` 失敗時是空字串,結果是 `..tip`。今天迴圈在 `_range` 後有 `[[ -z "$_EMPTY_TREE" ]] && continue`,spec 說 `_brange` 在「迴圈開頭」算,沒講算在這句 continue 之前還是之後;若在之前,`push-range` 白跑一次 lumos 才被丟掉。`pp_touched_file` 已有自己的 `[[ -n "$_EMPTY_TREE" ]] || return 0`,所以那頭沒事。

## 逐節與逐情境結果(已讀,無 finding 的部分)
- 標頭/summary/白話/依據/PRIOR-ART/RETIRE-IF:已讀,無 finding(連結目標與 `_lens_push_base`、`_push_range_start` 皆存在)。
- 範圍:F1、F2、F4 見上。其餘句:已讀,無 finding。
- 做法 4–6:已讀,無 finding。
- 驗收條款/回退/天花板/審計修正紀錄:除 F1(缺 SHA-256 測試)、F3(缺訊息測試)外,已讀,無 finding。
- push-range 印多行或空行:bash 3.2 與 5.x 實測 `[[ x =~ ^…$ ]]` 在含換行字串上不匹配(無行錨),多行輸出必退回空樹;結尾多空行被 `$(...)` 吃掉仍可用。無 finding。
- python 啟動失敗:`PY` 在 `scripts/hooks/pre-push:226` 決定,`pp_touched_file` 在 289 呼叫,順序沒問題;PY 為空時 `$PY …` 失敗 → 退回空樹。無 finding。
- 推刪除 ref:迴圈與 `pp_touched_file` 都在本地頂端全零時 continue,`push-range` 不會被叫到。無 finding。
- 頂端是合併提交:`merge-base --all` 與範圍 diff 對合併提交正常;無 finding。
- 標籤/頂端已在主線(`X..X`):實測 `pitfalls --diff X..X` 回 tier=light、suite=docs;`code-loop check` 回 0;範圍可被各指令吃下(`impact` 在無圖譜 repo 回 3 屬無關環境);spec 已把這寫進天花板。無 finding。附註:新增遠端(如 backup)首推時,頂端已在 origin 的 main 上也會得到空範圍,屬同一個「已推過」語意,接受。
- 遠端名是網址:候選 `refs/remotes/<網址>/HEAD` 的 `rev-parse` 回非 0 被當「沒有」跳過,其餘靠 main@{upstream};不崩。無 finding。
- 同推多分支:迴圈逐 ref 各算一次,`_IMPACT_JSON` 逐 ref 覆蓋同今天;時間成本見 F5。
- 全新 repo 首推 main(sha1):回空樹,同今天。SHA-256 見 F1。
- 實務隱患逐類:金流(無:只改範圍推導,spec 已排除,同意)、對外送出(無:push-range 唯讀不連網)、不可逆(無:退回提交即恢復)、守衛面(有:F1、F2 兩處放鬆)、時間(有:F5)、舊版相容(有:F3)。

總結:最嚴重 severity 為 major,blocking 共 2 條(F1、F2);minor 4 條(F3–F6)。
