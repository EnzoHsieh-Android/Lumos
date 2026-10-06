severity: minor

白話:第 3 版新加的「外掛自己跑 git 做事後查」沒有跟既有做法衝突。事件帳外掛本來就會用 `$.process.run` 跑 git,這份設計走同一個模式,只是這次是逐席多跑幾支。整份沒有新的 major,下面兩條 minor 都不擋。

### F1 條款 S10 與〈做法〉三的事後查自相矛盾:S10 說外掛不改寫工具呼叫的結果,事後查卻要在回傳文字後面附警告
severity: minor
blocking: 否 — 只是條款文字與做法對不上,不引入第二種做法,也不影響跨層邊界
引句:「外掛原始碼不改寫任何工具呼叫的輸入或結果」
引句:「在 `next(e)` 回來的 `text` 後面附一段固定開頭 `⚠ lumos-guard:這席審查期間 repo 有變動` 的警告」
佐證:事件帳 S9 禁的是「拒絕、改寫輸入、注入」這類會改變行為的 API,見 file: `docs/lumos-toolchain-knowledge/Projects/Lumos事件帳_計劃.md:130`。guard 要擋人,所以事件帳那條禁令不能直接搬來用,S10 已改寫成較窄的版本。但改窄後仍寫「結果」,而 `turn.complete` 的附文字就是改寫結果。若 `t_guard_plugin_files_valid` 照字面去掃「不改寫結果」,事後查那段會被判違規,條款和實作對不上。建議把 S10 改成「不改寫 `tool.call` 的輸入與結果;`turn.complete` 只准附警告文字」。⚠ `t_guard_plugin_files_valid` 實際掃什麼我沒看(測試尚未寫)。

### F2 事後查的 repo 根與 `.git` 路徑沒沿用事件帳「解主 checkout」的做法,本 repo 慣用的 worktree 會讓設定檔與掛鉤比對失效
severity: minor
blocking: 否 — 只會讓事後查在 worktree 內少看或誤報幾類,不是結構分歧,也有「事後查沒做成」的出口可走
引句:「在會談 cwd 跑 `git rev-parse --show-toplevel` 找 repo 根」
引句:「`.git/config`、`.git/hooks/` 底下每個檔的大小與修改時間」
佐證:事件帳外掛解主 checkout 的做法是「`git-common-dir` 是 `.git` 資料夾就取上一層,否則就是 `show-toplevel`」,讀取端與 enforcement 共用同一條規則。file: `mods/claude/lumos-ledger/hooks/register.ts:43`。全域規則也要求每個任務開獨立 worktree。linked worktree 的 `.git` 是檔案、不是資料夾,所以 `.git/config`、`.git/hooks/` 這兩個路徑在 worktree 裡不存在;設計裡「`.git`」的路徑要改用 `git rev-parse --git-common-dir`(或 `git config --local --list`)。另外,事件帳外掛已有注入式的 `Io.run`(`register.ts:263-266`,逾時 3 秒),guard 的 git 也該走同形的可注入介面。設計寫了「核心邏輯可注入」,但沒明說這支 git 呼叫介面。

### 前輪修復驗收

- F1(報告存放位置只有兩處說法):已改。範圍第 6 點明寫「使用者記憶『報告存 repo 外』那條改指這個位置」,並把設計審與代碼審手冊「先存檔放著」那句指到席報告暫存處。`$CLAUDE_JOB_DIR` 的落點沒驗(`skills/` 底下查不到 `lumos-seat-staging` 或 `CLAUDE_JOB_DIR` 的舊句),但設計已把位置固定在暫存根底下,新舊位置分歧的風險已收掉。
- F2(Bash 斷詞要在 TS 自寫第二份):已消除。這版不再逐詞解析 shell(決策 d3 否決),只做「以非單詞字元切詞、比對 `gh`、`hub`、`git` 配 `push`」的粗擋,不再需要跟 Python `shlex` 做對齊,也就沒有跨語言重複規則。S3 的測試案例寫在 TS 測試裡,只在 TS 這一側。這條已收掉。
- F3(安裝流程的 marketplace update 與名稱通用化):大部分已改。`_LEDGER_PLUGIN` 改成 `_LUMOS_PLUGINS` 清單、`_ledger_*` 改 `_lumos_plugin_*`、對應測試名跟著改、`t_ledger_plugin_files_valid` 的斷言改成「恰好是清單那幾支」、各支獨立結果並取最差。`marketplace update` 的「沒驗證」也改成「實作前先在隔離的 Claude 設定資料夾實測,不需要就拿掉」,有了回頭條件。唯一剩的小缺口:`_ledger_fail_hint` 的提示文字(「事件帳暫時停寫」)怎麼通用化沒寫。這屬實作細節,不另列。

沒有問題、不列為 F 的項目:
- 「只觀察、不跑外部指令」的定位:事件帳外掛本來就用 `$.process.run` 跑 git(`register.ts:265`),`Lumos事件帳.md:24` 那條 RULE 管的是 `lumos` 命令列的 enforcement 函式,不是外掛。guard 事後查跑唯讀 git,跟這個既有做法同形。guard 是第一支會 deny 的外掛,決策 d1 的否決理由(放進事件帳會破壞它的只觀察合約)成立,分兩支外掛是對的。
- 標記解析:只認第一個非空行,和 `dispatch-lens-hook.py:25` 與 `:147` 的逐行找法不同。這是刻意差異(避免內文範例被誤認),計劃有寫理由。兩者標記名稱不同(`LUMOS-SEAT` 與 `LUMOS-IMPACT`),不衝突。
- 擋下理由三段式、測試綁法(TS 測試標題以條款編號開頭加 `[manual:]`)、市集檔與安裝流程的家都沿用既有做法。

總結:最嚴重 minor,blocking 0 條
