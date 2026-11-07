severity: major

審查範圍:依據來源、既有決策、跨案相依、新鉤子檔的家。我讀完快照 258 行,逐條核對了官方鉤子文件(https://code.claude.com/docs/en/hooks.md 打得開,Stop 與 UserPromptSubmit 段已讀)、`android-write-check` 與 `android-situation-evidence` 兩個工作樹的程式。我沒有改任何東西。

核對結果摘要:
- **官方文件支持的部分**:
  - 同事件鉤子並行跑,文件有寫。
  - `Stop` 帶 `stop_hook_active`、`decision:"block"` 的格式,文件有寫。
  - 8 次連續續做上限,文件有寫。
  - `UserPromptSubmit` 屬共通欄位 `prompt_id`,文件有寫。
- **文件沒寫的部分**:逾時送 SIGTERM。文件只寫「canceled、output discarded」,計劃靠實驗 E3 而不是文件,這一點它已自己標明,不另報。

F1
severity: major
blocking: 是
引句:「`UserPromptSubmit` 在每次送出提示(含 Claude Code 自己起的回合)時觸發、帶 `prompt_id`」
- 文件對 `prompt_id` 的定義是「UUID identifying the user prompt currently being processed… Absent until the first user input」。
- 文件沒有任何一句說 `UserPromptSubmit` 會在 Claude Code 自己起的回合觸發。實驗 E1 只測了 `claude -p` 與 `--resume`。
- 同一份文件的 Stop 段說明,`background_tasks` 與 `session_crons` 是用來分辨「被背景工作或排程喚醒」的回合。
- 失敗場景:cron 或背景任務喚醒的回合沒有送出提示事件。這時 Stop 的 `prompt_id` 若是舊的,會與記錄相同。回合起點就退回上一個使用者提示的時刻,把前一回合碰過的檔也算進來。若 `prompt_id` 缺或不同,則整個回合靜默不檢查。
- 〈依據來源〉第一列把「含自己起的回合」當成官方行為寫進決定設計的前提,實際只有 `-p` 的證據。

F2
severity: major
blocking: 是
引句:「範圍 3 與白名單的工具鏈根要等那條線合進主線再動,先做範圍 1(工具鏈根以外)與範圍 2。」
- 範圍 1 第 5 條的白名單,比對時一定要用 `_kt_toolchain_root()` 算出 `<工具鏈根>/configs/ast-grep/`。
- 這個函式只存在於 `android-situation-evidence` 的 `scripts/lumos:38267`,本工作樹沒有(我用 grep 確認)。
- 沒有工具鏈根,任何 ast-grep 命令都過不了白名單,結果只有三種:
  - 實作者先做範圍 1,結果 S1 的正例(新增告警應 rc1)與 S6 的整條鏈永遠只能 rc3。
  - 實作者自己補一份 `_kt_toolchain_root`,與盲判那條線撞名。
  - 或必須等盲判線合併才能開工。
- 句子說「工具鏈根以外」可先做,但 S1、S3、S6、S7、S12 都依賴白名單通過。

F3
severity: major
blocking: 是
引句:「檔名加進 `_GLOBAL_CLAUDE_HOOKS`(否則 `_prune_dangling` 會剪掉註冊)」
- 新增一支鉤子還有三個登記點,計劃只提了第一個。照計劃做會讓另兩處出錯:
  1. `_VENDORED_TREE_FILES`(`scripts/lumos:33043` 附近)。註解寫明有一支測試逐檔比對 `scripts/hooks` 底下受版控的檔,少登記會翻紅,而且消費專案裡的工具檔會被推送閘當成產品碼。
  2. 存活事件層清單(`scripts/lumos:36905` 與 `36952` 的兩份,Claude 與 Codex 各一)。註解寫「這份清單是寫死列舉的,加 hook 一定要回來加一行」。沒加的話,這支逾時、出錯或靜默失效,`enforcement` 都不會有感知。計劃也沒說新鉤子要不要用 `_hookevent.guard` 包 `main`,`check-graph-sync.py:1126` 就是這樣包的。
  3. 同一份註解提過前例(記憶清掃那支漏登記)。
- 計劃的〈驗收條款〉S8 只驗註冊與 `_GLOBAL_CLAUDE_HOOKS`,上面兩處沒有條款守。

F4
severity: minor
blocking: 否
引句:「官方說 `stop_hook_active` 為真時要「檢查它,或自己判斷條件,避免擋在永遠解不了的條件上」」
- 官方原文是「Check this value or process the transcript to avoid blocking on a condition that will never resolve」,選項是「看逐字稿」,不是「自己判斷條件」。把改寫放進引號當官方說法,措辭不精確。
- 另有一個相關疑慮。引句:「外層還有 Claude Code 連續八次續做的硬上限(官方文件)」
- 文件說這個計數「resets each time Claude calls a tool」。續做時只要模型有呼叫工具(修檔必然會),八次上限就不會累積,所以不能當兜底。真正的防線只有計劃自己的「三批」上限,文字應改正。

F5
severity: minor
blocking: 否
引句:「既有決策是同會談只擋一次(收工點名);寫法檢查修完一批可能又寫出新的一批」
- d1 沒寫出舊決策的出處。出處在 `docs/lumos-toolchain-knowledge/Projects/README審視五修_計劃.md` 的 d2(第 17 行)。d2 明確寫「stop_hook_active 兩家語意相同(已續做過=不再擋)」。
- 本案的新鉤子刻意在 `stop_hook_active` 為真時照查,與這句衝突。計劃只在〈實務隱患〉對照了 07-06 撤 nag 那條,沒有指名 d2 的這一句。
- 〈待解問題〉第 10 組的「只管收工點名那道」是結論,不是理由。
- 另外 d1 是編排者在使用者睡著時代裁。計劃有註明「使用者在場可改」,這點已誠實交代。

F6
severity: minor
blocking: 否
引句:「也就是這支檔不是全判伺服端」
- `_stack_platform_excluded` 回的是「要拿掉的題號集合」(`scripts/lumos:38194`)。「集合裡沒有 android_only 的題號」要比對哪個題號,計劃沒寫。
- 盲判線新增的 `kt-situation` 題才是 `android_only` 且 `shape_only`,而且只在決策表讀得到時才被加進題表。
- 實作者容易寫成「集合為空」或「不含 `kt-situation`」。兩種寫法在表壞掉或另一條線還沒合併時,結果不同。
- 建議明寫判斷用哪個 id,或另提一個「這支檔是否判為伺服端」的單點函式。

F7
severity: minor
blocking: 否
引句:「用 `importlib` 載入同目錄的 `check-graph-sync.py` 取用,不抄第二份;載入失敗整支靜默結束(rc0)」
- Q3 的自答說「沒宣告 ast-grep 的專案讀一個檔就結束」,依據是 E10。
- E10 量的是 `python3.14 -c 'import json,sys,os,time,pathlib'`,沒有量載入一千多行的 `check-graph-sync.py`。
- 範圍 2 的順序是先載入共用模組、後找專案根並預篩。這支鉤子又是全域註冊,每個專案的每次送出提示都會付這筆載入成本。
- Q3 的成本結論與設計順序不一致。要嘛先預篩再載入,要嘛重量一次。

總結:最嚴重是 major(依賴先後順序自相矛盾、新鉤子少兩處必要登記、回合起點的官方行為無依據),會擋 3 條(F1、F2、F3)。

我只改了 F1 的 `blocking`,從「否」改成「是」。這樣兩欄一致:它的前提是官方文件沒寫的行為,而且這個前提決定了回合起點的設計。總結行的條數從 2 改成 3,檔首最高等級不變。
