---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/guards-gates
related:
  - "[[Projects/世界解重新註解2026-10_總覽_調研]]"
  - "[[Projects/世界解重新註解2026-10_守衛閘門_調研]]"
  - "[[Projects/enforcement可觀測性_計劃]]"
lands_in:
  - Systems/代理繞閘問人
  - Systems/lumos-cli-lifecycle
---
# 代理繞閘字樣問人

> 白話:代理在推送被擋、使用者又在催的時候,會順手在指令上加 `--no-verify` 或用環境變數把檢查關掉,而 Lumos 目前在執行前完全不攔、不問人。這篇在 Claude Code 的「Bash 執行前」掛一道檢查:指令真的在對一個非拋棄式的 repo 做繞過(推送或提交帶 `--no-verify`、提交帶 `-n`、用 `-c core.hooksPath=` 或 `git config core.hooksPath` 關掉掛鉤、指令前設 `LUMOS_SKIP_*`),就回「問人」,讓使用者按允許才執行。只是字面提到這些字樣(搜尋、說明文字、heredoc 內容)或在拋棄式暫存目錄裡做實驗,一律放行不問。來源是世界解總覽〈跨類優先順序〉第 7 名。

PRIOR-ART: 世界解 W09 spec-gates(代理邊界的 Bash 指令遇到 `--no-verify`、`git commit -n`、`core.hooksPath`、`HUSKY=0` 就問人)與 TDD Guard 同形;Claude Code 官方的 PreToolUse 掛鉤 `permissionDecision: "ask"`。本 repo 既有的兩支工具前掛鉤(`scripts/hooks/claude/impact-hook.py`、`dispatch-lens-hook.py`)由 `scripts/merge-claude-settings.py` 註冊、讀 stdin 事件、印 JSON;這支照同一種做法,共用 `_hookevent.py` 記「跑過/逾時/失敗」。與總覽第 7 名原句的差異:只做 Claude Code(Codex 另見 REVISIT);不新增寫治理帳的入口(`Projects/enforcement可觀測性_計劃` 已決定記帳不另開端點,事後量測掃 Claude 事件帳與掛鉤自己的存活事件);不列 `LUMOS_STOP_BLOCK_OFF` 與 `HUSKY=0`(理由見〈範圍〉)。審查席的推送已由 `mods/claude/lumos-guard` 擋下,那支外掛依 `Projects/審查席唯讀隔離_計劃` d4 不跑外部指令、只對審查席生效,所以不放進它。對照該計劃 d3、d4(d4 取代 d3 的事後查部分,保留審查席 Bash 粗擋、不逐詞解析 git 指令、寧可誤擋):那條管審查席、動作是擋,誤擋只讓審查席少做一個實驗;這條管主會談、動作是問人,誤問的代價是把使用者訓練成反射按允許(〈量測〉照字面比對一天要問十幾次),所以這裡選逐段解析、寧可漏問——兩條不衝突。這個取捨以 `lumos decision-add` 記進本篇 decisions。
RETIRE-IF: 上線滿 8 週,掛鉤記下的「問了」事件裡,事後在 Claude 事件帳找到同一條指令有執行紀錄(=使用者按了允許)、且人工抽看判定為正當用途的比例超過八成(問了也只是被反射性按掉),就改成只記錄不問;或 Claude Code 原生提供同等的「繞閘指令確認」,就拆掉這支、改用原生。

REVISIT:2026-11-14 上線後一個月:用 scratchpad 一次性腳本讀掛鉤的「問了」事件(存活事件 note 以 `ask:` 開頭)並對照 Claude 事件帳同指令前 500 字有沒有執行紀錄,數問了幾次、幾次被允許、其中真正繞閘幾次,寫回〈量測〉;同時對照使用者有沒有回報「在互動加略過權限模式下沒跳出提示」
REVISIT:2026-12-14 決定要不要接 Codex 適配(Codex 的 Bash 前事件與回覆形狀不同,本篇第一版只做 Claude Code)

## 量測(2026-10-14,拿 Claude 事件帳用一次性腳本量)

- 範圍:`/Users/enzo/harness/lumos-toolchain/governance/runtime/events` 近 30 天(實際最早 2026-10-07)2363 個檔、27689 條 Bash 指令原文(事件帳每條只存前 500 字)。
- 只比對字面(`--no-verify`、`git commit … -n`、`core.hooksPath`、`LUMOS_SKIP_*`、`LUMOS_STOP_BLOCK_OFF`、`HUSKY=0` 出現在指令裡):命中 175 次。抽看前 20 筆幾乎全是用 `grep` 搜尋這些字樣,或審查席在 `/tmp/lumos-seat-work/` 的拋棄式 repo 做實驗——照字面比對會每天問十幾次,把人訓練成反射按允許。
- 照指令結構判(只看 git 的推送或提交帶 `--no-verify`、`-c core.hooksPath=` 接推送或提交、`git config core.hooksPath <值>`、`LUMOS_SKIP_*` 或 `HUSKY=0` 設在 git 推送或提交前):標記 38 次。
- 再排除拋棄式目標(`cd` 或 `git -C` 指到 `/tmp/`、`/private/tmp/`、`/var/folders/`,或指令裡用 `mktemp`):剩 4 次,4 次都是真的在工作樹裡繞閘——一次對 Lumos 遠端推送加 `--no-verify`,三次 wip 提交加 `--no-verify`。一週約 4 次,一天不到 1 次。
- 事件帳沒有「確認框按了允許或拒絕」的欄位(`denied` 欄由事件帳外掛在工具執行層記,確認框被拒時會不會寫進來未驗),所以 RETIRE-IF 改用「掛鉤自記問了」加「同指令事後有沒有執行紀錄」兩個量得到的訊號。

## 範圍

- 只做 Claude Code 的 Bash 工具前事件;Codex 適配另見 REVISIT,安裝 Codex 時這條註冊要跳過(見〈做法〉)。
- 只看指令文字;變數拼接(`F=--no-verify; git push $F`)、shell 別名、自寫腳本裡藏繞過、`bash -c "…"` 與 `sh -c` 包起來的字串、`$(…)` 與反引號指令替換、`eval`,攔不到——這篇防「代理順手繞」,不防有心改寫(spec-gates 與 TDD Guard 都同樣自承)。
- `LUMOS_STOP_BLOCK_OFF` 不列:它關的是 Claude Code 自己的收工掛鉤,在 Bash 指令裡 export 只影響那條指令的子程序,關不到掛鉤。
- `HUSKY=0` 不列:它是 W09 針對 husky 的通用字樣,Lumos 的推送前閘與提交前閘走 `core.hooksPath` 指向的 `scripts/hooks/`,`HUSKY=0` 關不到;本 repo 不用 husky,列了只會在消費專案對無關的閘問人。

## 做法

- 新增 `scripts/hooks/claude/bypass-ask-hook.py`:
  - 讀 stdin 的 PreToolUse 事件,取 `tool_input.command`。命令列參數(安裝時附的 `--budget 5`)一律忽略、不報錯。
  - **便宜的預篩(在 `_hookevent.guard` 之外)**:指令裡沒有 `--no-verify`、`hookspath`(不分大小寫)、`LUMOS_SKIP_`,也沒有「`commit` 之後同一行出現以 `-` 開頭且含 `n` 的短旗標」,直接結束、不輸出、**不記任何事件、不跑任何子程序**。絕大多數 Bash 呼叫走這條。理由:`guard` 每次都會跑一次 `git rev-parse` 並寫一筆存活事件,存活事件檔滿 512KB 會砍到剩最後 2000 行;每條 Bash 都記會一天灌數千筆,把其他掛鉤的存活紀錄擠出去,讓 `lumos enforcement` 對它們假紅。
  - 過了預篩才進 `guard("bypass-ask-hook", __file__, main, swallow=True)`;`swallow=True` 讓任何例外都放行(這道是問人層,不是安全邊界),例外由 `guard` 記成 error。`main` 內部若自己吞了例外,要 `mark("error", …)`,不能記成 ok。
  - **剝掉 heredoc**:切段之前,把 `<<WORD`、`<<-WORD`、`<<'WORD'`、`<<"WORD"` 之後到結束字那一行的內容整段拿掉(heredoc 運算子本身留著),否則 `cat <<EOF … git push --no-verify … EOF` 會被當成要執行的指令。
  - **結構分類**(`bypass_reasons(command, cwd)` → 理由清單):用 `shlex`(posix、把 `; & | 換行` 當分隔)切成一段段指令;每段跳過開頭的 `VAR=值`,看程式名:
    - `git`:跳過全域選項(`-c 鍵=值`、`-C 目錄`、`--git-dir`、`--work-tree`)找到子指令;子指令是 commit/push/merge 且後面有 `--no-verify` → 命中;commit 的短旗標組逐字看,遇到吃值的旗標(`-m -F -C -c -t`,值可黏著也可在下一個詞;`-S -u` 的值只會黏著)就停,停之前出現 `n` → 命中(`-n`、`-qn` 命中;`-mnote`、`-m -n`(`-n` 是訊息)不命中);全域 `-c core.hooksPath=…` 且子指令是 commit/push/merge/rebase/am/cherry-pick/revert → 命中;`config` 子指令設定 `core.hooksPath`(有值、不是 `--get`/`--list`/`--unset`)→ 命中;同段開頭有 `LUMOS_SKIP_*=` 且子指令是 commit/push/merge → 命中。
    - `export LUMOS_SKIP_*=`,且同一條指令後面有 git 的 commit/push/merge → 命中。
  - **拋棄式目標放行**:追蹤段落中的 `cd <目錄>` 與 `git -C <目錄>`(展開同一條指令裡先賦值的變數),目標落在 `/tmp/`、`/private/tmp/`、`/var/folders/`、`/private/var/folders/`、`$TMPDIR` 底下,或指令裡用了 `mktemp`,該段命中不算。沒有任何 `cd`/`-C` 時用事件的 `cwd` 判。
  - **切不動**(引號不成對等 `shlex` 失敗):退回字面判——同時含 `git`、`push` 或 `commit`、`--no-verify` 就算命中,其他放行。
  - **命中**:印 `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": "<三段式>"}}`,並用 `mark("ok", "ask:<理由代號>")` 讓存活事件帶上「問了」(RETIRE-IF 的量測來源)。三段式:發生什麼(這條指令會跳過 Lumos 的閘:<命中理由>)、為什麼在意(閘被跳過就沒人檢查這次推送或提交,代理順手繞過是已知模式)、怎麼做(確定要跳過就按允許;不確定就拒絕,讓代理改成修好被擋的原因)。
  - 決策邏輯放在 `decide(event) -> dict | None`(回要印的 JSON 物件或 None),`main` 只負責讀 stdin、叫 `decide`、印出——測試直接呼叫 `decide`。
- `scripts/merge-claude-settings.py`:
  - PreToolUse 加一條 `matcher: "Bash"` 指向這支;`HOOK_BUDGET` 加 `"bypass-ask-hook.py": 5`(實際應在幾十毫秒內)。
  - `_codex_entries` 遇到 `matcher: "Bash"` 的 PreToolUse 一律跳過、不寫進 Codex 註冊表:Codex 的 Bash 前事件回覆形狀不同,原樣寫過去會讓 Codex 收到它看不懂的 ask。
- `scripts/lumos`:
  - `_GLOBAL_CLAUDE_HOOKS` 加 `bypass-ask-hook.py`:沒加的話安裝不會把檔複製到 `~/.claude/hooks/`,`_prune_dangling` 還會把註冊當懸空剪掉——測試照綠、實際整支不生效。`_own_hook_scripts` 由它推出,不必另改。
  - `enforcement_status` 的 Claude 掛鉤列舉加 `("pretooluse-bypass-ask-hook", "bypass-ask-hook.py")`;釘住列數的測試(現為 24 列)同步改成 25。Codex 側不加列(本篇不註冊 Codex)。近期沒命中過時它照既有規則顯示 unknown(「七天內沒被觸發」不標失效),不會假紅。
  - `_VENDORED_TREE_FILES` 與 `ANCHOR_FILES` 加 `scripts/hooks/claude/bypass-ask-hook.py`(前者有逐檔比對測試;後者讓自動執行的掛鉤內容受錨點盯著)。
- 新 Systems 節點 `Systems/代理繞閘問人` 管這支掛鉤檔(每支檔有家);`scripts/lumos` 與 `merge-claude-settings.py` 的改動寫進 [[Systems/lumos-cli-lifecycle]]。
- 實測(2026-10-14,**非互動模式**):`claude -p --dangerously-skip-permissions` 加一支回 ask 的測試掛鉤,`echo` 指令沒有執行,模型收到說明後表示要等使用者核准——非互動的略過權限模式不會跳過掛鉤的問人。互動加略過權限模式會不會真的跳出確認框,官方文件沒寫,由下面人工條款驗。

## 驗收條款

- [S1] 當指令在非拋棄式目錄對 git 做 push/commit/merge 並帶 `--no-verify`、commit 帶含 `n` 的短旗標組(`-n`、`-qn`)、用全域 `-c core.hooksPath=` 接 commit/push、用 `git config core.hooksPath <值>` 設定、或在 git commit/push 前設 `LUMOS_SKIP_*=`(含 `export` 後接 git commit/push)時,掛鉤 應 回 `permissionDecision: "ask"` 並附三段式理由 [test:t_bypass_ask_flags_real_bypass]
- [S2] 當指令只是字面提到這些字樣(`grep`/`echo`/`sed` 的參數、引號裡的說明文字、heredoc 內容)、commit 的吃值旗標帶含 `n` 的值(`-mnote`、`-m -n`)、`git config --get core.hooksPath`、`HUSKY=0 git commit`、或 `LUMOS_SKIP_*` 設在 git 以外的程式前(例如跑測試)時,掛鉤 應 不輸出、放行 [test:t_bypass_ask_ignores_mentions]
- [S3] 當繞過的目標是拋棄式目錄(`cd` 或 `git -C` 指到暫存目錄、經同指令變數賦值展開後指到暫存目錄、或指令用 `mktemp`)時,掛鉤 應 放行;同一條指令裡另一段對非拋棄式目錄繞過時 應 照樣問人 [test:t_bypass_ask_throwaway_targets]
- [S4] 當指令引號不成對而切不動時,含 git、push 或 commit、`--no-verify` 三者 應 問人,其他 應 放行;掛鉤內部丟例外時 應 放行並記一筆 error 事件;沒過預篩的指令 應 不寫任何存活事件;命中時存活事件 應 帶 `ask:` 開頭的 note;10 萬字的指令 應 在 0.5 秒內判完;帶 `--budget 5` 參數執行 應 正常運作 [test:t_bypass_ask_fallbacks_and_budget]
- [S5] 當執行 `merge-claude-settings.py` 時,PreToolUse 應 有一條 `matcher: "Bash"` 指向 `bypass-ask-hook.py`,逾時 應 是 5 秒;以 Codex 為目標安裝時 應 沒有任何指向 `bypass-ask-hook.py` 的註冊;`_GLOBAL_CLAUDE_HOOKS` 應 含這支、`enforcement_status` 應 有 `pretooluse-bypass-ask-hook` 一列 [test:t_bypass_ask_registered]
- [S6] 當使用者在互動加略過權限模式的會談裡遇到第一次命中時,Claude Code 應 跳出確認框讓使用者按允許或拒絕 [manual:使用者第一次遇到時回報有沒有跳出確認框,沒跳就改成回 deny 並在理由裡要求代理先問人]

## 回退

- 拿掉 `merge-claude-settings.py` 那條 Bash matcher 並重跑安裝,掛鉤就不再被呼叫;掛鉤檔留著不影響任何事。
- 誤問太多:先調分類函式(加拋棄式目錄、收窄命中形狀),不必整條拿掉。
- 不可逆的部分:無。掛鉤只回「問人」、不改指令、不寫治理帳(只在過了預篩時寫 `_hookevent` 的存活事件)。

## 實務隱患

- 每條 Bash 指令都多一次 Python 啟動(約幾十毫秒):過去「每次 Bash 都觸發」的掛鉤被撤,是因為每次付高成本且核心邏輯跑不到;這支預篩在掛鉤內、`guard` 之外完成,不叫主程式、不跑 git 子程序,命中預篩才做結構分類與記事件。
- 存活事件檔共用:只有過了預篩才寫,量測裡過預篩的指令一週約 175 次量級,不會擠掉其他掛鉤的紀錄。
- 誤問:量測一週 4 次全是真繞閘;但新的寫法(例如別的拋棄式路徑)可能誤問,RETIRE-IF 與第一條 REVISIT 盯著。
- 問人只擋「順手繞」:有心改寫攔不到(見〈範圍〉)。
- 已排除:正式環境不可逆:掛鉤只回「問人」、不改指令也不寫治理帳,拿掉註冊即完全還原(見〈回退〉)
- 已排除:金流:不碰任何金流或扣款相關程式
- 已排除:對外送出:只讀本機 Bash 事件,不送任何東西到外部服務
- 自我治理:這是守衛本身;掛鉤壞掉時放行(問人層不是安全邊界),但會記 error 事件讓 `lumos enforcement` 看得到。
