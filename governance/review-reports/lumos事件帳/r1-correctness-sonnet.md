severity: major

整體:mod 事件與讀取面大致站得住,但寫入端的狀態管理、安裝來源、與既有測試的互動各有會做壞的洞。以下 7 條,其中 4 條 blocking。

### F1 緩衝「寫完才清空」在並行子代理下丟事件或重複寫
severity: major
blocking: 是 — 不改,實作者照字面「寫成塊檔、清空緩衝」會做出並行時丟事件的系統。
- spec 段落:做法 2 寫入。
引句:「把緩衝寫成一個新塊檔(序號遞增、補零 6 位),清空緩衝。」
- 問題:`$.fs.write` 是 async。字面順序是 await 寫檔,之後清空。多個子代理並行時,另一個 hook 在這個 await 期間 push 的事件,會被寫完後的「清空」一起丟掉。兩個 hook 同時各自觸發 flush,則拿到同一個序號,後寫的覆蓋先寫的。
- 失敗場景:主代理同時派 3 個子代理,A 的 `turn.complete` 觸發 flush,await 中 B、C 的 `tool` 事件進緩衝,A 寫完清空,B、C 的事件消失,且不產生 `ledger_error`。並行子代理是這份計劃的賣點場景。
- 佐證:file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:12643` 說 subagent 的 turn.complete 是每個 hook 都看得到的獨立事件,可與主迴圈並行。
- 要補:同步取走緩衝(swap)並同步領序號,之後才 await;flush 串成一條佇列。

### F2 塊序號與緩衝存在模組變數,熱重載或重新載入後從 000001 覆蓋舊塊
severity: major
blocking: 是 — 「不重寫舊塊」這條核心承諾,在序號放模組變數時守不住。
- spec 段落:做法 2「序號遞增」「結果記在模組變數,不每次查」。
引句:「沒有就整個會談都不寫(結果記在模組變數,不每次查)。」
- 問題:spec 沒說序號從哪來。依字面是記憶體計數器。官方說明明講模組變數會在 hot reload 丟失,狀態要放 `$.state`。`$.fs.write` 的語意是「whole new content」(覆寫)。
- 失敗場景:`lumos install` 重跑後 `/reload-plugins`,或開發中存檔觸發熱重載,或 `claude --resume` 讓同一會談目錄由新行程接手。計數器歸零,下一塊寫成 `000001.jsonl`,直接覆蓋既有的第一塊,歷史靜默消失。`/clear` 讓 session id 在沒有 `session.start` 的情況下換掉,快取的 toplevel 與計數器也不會跟著重置。
- 佐證:file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/reference.md:90`(模組變數熱重載會丟,要用 `$.state`);file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:3142`;file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:4265`(`/clear` 說明)。
- 要補:序號每次 flush 前 `$.fs.list` 該會談目錄取最大值加一,或把緩衝與序號放 `$.state`;「緩衝最多 49 筆當機才遺失」的誠實界線也要改,熱重載同樣丟緩衝。

### F3 install 以「執行中的 scripts/lumos 所在 repo」當市集來源,worktree 與切分支會讓外掛來源消失或衝突
severity: major
blocking: 是 — 全域外掛綁死在一個會被刪、被切分支的路徑上,spec 沒處理「市集已存在但來源不同」。
- spec 段落:做法 4。
引句:「執行中這支 `scripts/lumos` 的上兩層(`cmd_install` 用的來源 repo)有 `.claude-plugin/marketplace.json`」
- 問題:資料夾型市集的外掛是從該資料夾「本身」讀的,不是安裝時的拷貝。使用者全域規則要求每個任務開獨立 worktree,而 `scripts/lumos` 在 worktree 裡跑 `install` 時,來源就是那個 worktree 路徑。
- 失敗場景:
  1. 在 `lumos-toolchain-event-ledger` 這種 worktree 跑 `lumos install`:市集 `lumos-toolchain` 註冊成 worktree 路徑。任務結束刪 worktree,外掛下次載入失效,enforcement 顯示 stale,使用者不知道原因。
  2. 之後在主 clone 再跑 install:`marketplace add` 同名不同來源的結果 spec 沒定義,依 spec 只印一行錯誤,外掛仍指向舊路徑。
  3. 主 clone 切到沒有 `mods/` 的分支,外掛在 reload 時失效。
- 佐證:file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/reference.md:72`(資料夾市集從該資料夾本身讀,從不讀安裝時的拷貝)。file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:17630`(`_lumos_src` 的正規來源是 `$LUMOS_HOME` 或 `~/harness/lumos-toolchain`,spec 沒用它)。
- 要補:來源固定走 `_lumos_src()`(或偵測到 worktree 就略過並提示),並規定「市集已存在且來源不同」時先 remove 再 add。

### F4 spec 說 bootstrap 不碰外掛,但 bootstrap 其實以子行程跑完整 `install --force`
severity: minor
blocking: 否 — 錯的是對現況的描述,實作者照 spec 也不會做壞,只是測試與文件寫錯。
- spec 段落:做法 4 第二點。
引句:「`lumos update`、`bootstrap` 走的 `_sync_global_hooks` 不碰外掛(要新版就重跑 `lumos install`)。」
- 問題:`cmd_bootstrap` 以 `[sys.executable, home/scripts/lumos, "install", "--force"]` 子行程執行,所以 bootstrap 會走到新增的外掛安裝,並以新 clone 當市集來源。另外,外掛從資料夾本身讀,`lumos update` 拉新版後 `/reload-plugins` 就拿到新 mod,「要新版就重跑 install」與 reference 不符,實際要做的是 reload。
- 佐證:file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:18967`。

### F5 既有 install、uninstall、enforcement 測試會在測試中真的呼叫機器上的 claude,spec 沒給隔離
severity: major
blocking: 是 — 不改,測試會改到真機的 Claude 外掛狀態,或讓測試結果依機器而變。
- spec 段落:做法 4 與 S6、S7、S8,只列 `t_install_registers_ledger_plugin` 用假 claude,範圍只含新測試。
- 問題:既有測試以假 HOME 跑 install、uninstall、enforcement。來源是本 repo,有市集檔,條件成立;`shutil.which("claude")` 又找得到真的 claude。HOME 假了,但實測驗證用的隔離機制是 `CLAUDE_CONFIG_DIR`。使用者環境若有設它,假 HOME 擋不住。
- 失敗場景:
  1. 跑全套測試時,`install --force` 的既有測試 6 處以上會對真 claude 做 `marketplace add` 與 `install`。
  2. `cmd_uninstall` 的測試(`scripts/test_lumos.py:9333`、`:35233`)會觸發 `claude plugin uninstall`,移除使用者真實裝著的 `lumos-ledger`。
  3. `enforcement_status(root, home)` 的測試注入了 home,卻無法注入 claude 的結果,在近期沒有事件的 fixture 下會跑真的 `claude plugin list`,結果依機器而變。
- 佐證:file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/test_lumos.py:540`(測試直接跑 `GRAPHCTL install --force`);file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/test_lumos.py:9333`;file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/test_lumos.py:31179`。
- 要補:加一個環境變數開關,例如 `LUMOS_SKIP_CLAUDE_PLUGIN=1`,讓測試底座預設設定它,假 claude 的測試明確取消。或 `claude` 的路徑只從可注入的位置找。

### F6 enforcement 新列的 layer 名與「Claude 列/Codex 列」是一列還是兩列沒定義
severity: minor
blocking: 否 — 影響測試與 JSON 消費端的口徑,但不會讓系統壞掉。
- spec 段落:範圍 6 與做法 5、S8。
引句:「Claude 顯示已安裝且近期有事件 / 已安裝但近期沒有 / 沒裝 / 無法判斷;Codex 顯示「不支援」」
- 問題:`enforcement_status` 的列是 `{layer, status, detail}`,layer 是英文 id,現有程式沒有「Claude 列」與「Codex 列」這種分組。spec 沒給 layer 名,也沒說是一列還是兩列。S8 寫兩列(Claude 與 Codex 各一),Codex 那列恆為 `unknown` 且永遠印在輸出,等於每次都多一層「本機測不到」的雜訊,對只用 Claude 的人也如此。
- 佐證:file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:20281` 到 `:20295`(列結構);file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:20531`(`unknown` 計入「另 N 層」)。

### F7 事件帳沒有保留期限,enforcement 與 `lumos events` 要掃的檔案無上限成長
severity: minor
blocking: 否 — 初期不會壞,但長期會拖慢進場 hook;改做法即可。
- spec 段落:做法 2、3 與回退節「要清就刪資料夾」。
- 問題:每個 `turn_end`(含每個子代理回合)寫一個新檔,永不刪除。既有的 `hook-events.jsonl` 有 512 KiB 上限砍半,這份沒有。
- 失敗場景:每日自動迭代 loop 加子代理,一年累積數萬塊檔。進場 hook 每次跑 `lumos enforcement --json`,內層預算約 7 秒,要掃 `events/` 找「最近 7 天有塊檔」,掃描變慢會讓整段 enforcement 逾時,進場 hook 對 enforcement 回 None,其他層的降級警報一併被吞。`lumos events` 列最近 10 個會談也得 stat 全部會談目錄。
- 佐證:file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/hooks/claude/_hookevent.py:49`(`MAX_BYTES` 上限的既有慣例);file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/hooks/claude/lumos-entry-hook.py:257`(enforcement 子行程逾時走 `_inner_budget`)。
- 要補:規定判「近期」用每個會談目錄最新塊檔 mtime、只看目錄層,並加保留期限(例如 mod 在開場順手刪超過 N 天的會談目錄)。

### 其他小項(併入同一輪修補,各自不必單獨成 finding)
- `turn_start`:spec 寫 `origin` 是「來源原樣字串」,但型別是物件 `{kind: ...}`,可能帶其他欄位。實作者可能序列化整個物件或寫成 `[object Object]`;應明定只取 `origin.kind`。file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:8368`。
- `turn_start` 只有主迴圈有:型別檔明說子代理的 run 不觸發 `turn.start`,S1 與共同欄位「子代理也有自己的」的 `turn` 要寫清只有 `turn_end` 與 `tool`。file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:12643`。
- `spawn` 事件的 `agent` 欄位是父還是新子代理 id,spec 沒說。`AgentSpawnResult.agentId` 才能把 spawn 連到子代理自己的事件,spec 沒記它。
- `paths` 只取 `file_path` / `path`,漏掉 NotebookEdit 的 `notebook_path` 等其他欄位名。
- `lumos uninstall` 在沒裝過外掛(或沒有 claude)的機器上,會對「沒有東西可移」印出「移除失敗」加手動指令,誤導。應先判定再移除。
- `session.end` 有約 1.5 秒的牆鐘上限,且只含 `$` 呼叫,spec 的最後一次 flush 要在上限內完成,spec 沒提這個預算。file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:10502`。

### 已讀,無 finding 的節
- 範圍、第 1 節事件表(除上列小項)、第 3 節讀取、第 5 節判定順序與三值狀態:已驗證 `_enforcement_alert` 只點名 inactive 與 degraded(`lumos-entry-hook.py:176`)、`enforcement_summary` 排除 unknown 與 stale(`scripts/lumos:20531`),與 spec 一致。
- 落點:`Systems/lumos-cli-lifecycle`、`lumos-cli-read`、`codex-harness` 皆存在。
- 與 `[[Verification/2026-10-05_Claude-mod能力實測]]` 的交叉引用:目標存在(在這個 worktree 裡,untracked)。

### 實務隱患逐類
- 並行與競態:有,見 F1、F2。
- 不可逆的使用者層狀態:有,見 F3、F5。spec 的「不可逆」段只看到移除失敗,沒看到來源路徑消失與測試誤改真機狀態。
- 資源成長:有,見 F7。
- 秘密外洩:`cmd` 記 Bash 前 500 字,spec 已承認並附 REVISIT。風險成立但已誠實列出,不另標。
- 金流、對外送出、守衛面:無,理由同 spec(只寫本機忽略資料夾、不呼叫網路、不擋不改不注入)。

最嚴重 severity:major,blocking 共 4 條(F1、F2、F3、F5)。
