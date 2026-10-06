severity: major

### F1 `--session --json` 遇到極深巢狀事件行會 Traceback 退出碼 1(r2 修了讀、沒修寫出)
severity: major
blocking: 是 — 讀取端會對 repo 內一個約 230KB 的 jsonl 檔崩潰,而 r2 的修正明明宣稱已處理極深巢狀。
hunk: `_events_read` 加了 RecursionError 的 except,但 `cmd_events` 的 `--json` 分支在解析之後才做序列化。
引句:「print(_j.dumps(dict(r, session=session)))   # ensure_ascii:控制、格式、孤立代理字元一律跳脫」
問題:解析端剛好能吃下的巢狀深度,放進 `{"events":[…]}` 外殼後多了兩層,序列化端就超限。深度落在這個縫隙的行,解析成功並進了 events,輸出時丟出未捕捉的 RecursionError。
具體輸入→結果:建一個 repo(git init 加一次空提交),在 `governance/runtime/events/Z/a.jsonl` 寫一行 `{"v":1,"ev":"tool","x":[[[…]]]}`,其中 x 是 116190 層的 `[`…`]`。
- `lumos events --session Z --json` 的輸出是 Traceback,退出碼 1。
- 同一份檔跑不帶 `--json` 的 `lumos events --session Z` 正常,印出「1 筆事件」。
- 深度二分實測:116201 層(含)以下都崩,116202 層以上被當壞行計數(`"bad": 1`)、退出碼 0。
- 一行約 232KB,可以被人強制提交進 repo。
佐證:這是 r2 修過的「極深巢狀」同一族。r2 的 t_events_reader_hostile_lines 只測了讓解析器遞迴耗盡的那一端,沒測「解析成功、序列化失敗」的縫隙。
修法方向(僅供參考):序列化包 `try/except RecursionError`,或讀取時對 events 先做深度上限,超過就算壞行。

### F2 讀取路徑沒做 prune 那套「路徑上層不得是符號連結」檢查
severity: minor
blocking: 否 — 只洩漏唯讀內容,且需要有人能在 repo 裡放符號連結,又恰好有人去讀。
hunk: `cmd_events` 的 `--session` 與列表分支只檢查 session 資料夾本身是不是連結,沒呼叫 `_events_path_safe`。
引句:「if not _EVENTS_SESSION_RE.fullmatch(session) or d.is_symlink() or not d.is_dir():」
具體輸入→結果:把 `governance/runtime` 做成指向 repo 外某資料夾的連結。`lumos events` 列出外部資料夾下的會談,`lumos events --session SX` 印出 `SECRET-FROM-OUTSIDE ✓`,退出碼 0。
佐證:同一個 repo 下,prune 會擋這種路徑(退出碼 2),讀取卻照讀,兩邊信任邊界不一致。

### F3 `--prune --repo <子目錄>` 會被擋,訊息說的原因不對
severity: minor
blocking: 否 — 失敗方向是安全的(什麼都沒刪),只是訊息誤導。
hunk: `_events_main_trusted` 要求 root 等於主 checkout,或 root 是登記過的 worktree。
引句:「if not (_events_main_trusted(root, main_root) and _events_path_safe(main_root, base)):」
具體輸入→結果:`lumos events --prune --days 30 --repo docs/sub`(docs/sub 是 repo 內的子目錄)印「擋下:事件帳路徑 … 不可信(上層有符號連結,或 .git 指到的主 checkout 沒登記過這個 worktree)」,退出碼 2。實際上沒有任何符號連結,只是 `--repo` 給的不是 toplevel。使用者被導去 `ls -la governance` 查符號連結,查不到問題。
⚠ 另一個沒驗證的推測:git 2.48 以上、啟用 `worktree.useRelativePaths` 時,`gitdir` 檔內容是相對路徑,`Path(...).resolve()` 照目前目錄解讀,合法 worktree 也會被擋。本機 git 是 2.39,不支援該設定,所以重現不了。

### 前輪修復驗收(r2)
- 讀取端極深巢狀、孤立代理字元:解析端與文字輸出已修好。實測 900 到 100000 層都不崩。`--json` 輸出端的縫隙另見 F1,沒修乾淨。
- ok 欄位是列表:已修。實測文字與列表模式都不崩。
- 清理函式統一為 `_events_clean`:`_esc_clean` 加 `_PATH_SPECIAL_CATS`。路徑與 Path 物件傳入都正常,未見問題。
- 塊檔連結不跟:已修。`_events_read` 已跳過連結檔。
- 上標數字天數:已修。`_EVENTS_DAYS_RE` 只收 ASCII 數字、`str(n)` 比對擋前導零。
- `.git` 改指別的 repo 導致清理刪到別人的帳:`_events_main_trusted` 有效。
  - 真 worktree 內 `--prune` 正常刪掉主 checkout 的舊會談,實測退出碼 0、舊資料夾消失。
  - 相對路徑 gitdir 的情況重現不了(見 F3 的 ⚠)。
- git 卡住拖垮 enforcement:`_lens_git` 帶 timeout=3,逾時回 None 後退回原根,邏輯正確。
- teardown 的 `--source` 傳遞、只有專案範圍那份時的誤報:程式路徑正確。
  - `_ledger_user_plugin` 以 scope 過濾,市集移除獨立於外掛那步。
  - 外掛與市集的 `--scope user` 旗標,我只用 `--help` 對照,參數存在,語意相符。
  - 真實的 `claude plugin` 變更類指令依規定沒有跑,所以只做了程式推演。
- 競態重查(`_ledger_wait`):邏輯成立。副作用是真失敗時固定多等 3 秒,屬可接受。
- 來源非預設位置時顯示市集來源:有輸出。
- 擋下訊息改走標準錯誤:已修。實測 stderr 與退出碼 2。

### 其他已檢視、判定不成問題
- `bootstrap` 傳 `LUMOS_HOME`:子行程 `_lumos_src()` 指向本次來源,正確。
- 新增的 `claude-event-ledger` 列用 stale/unknown/active:`enforcement_summary` 已把 stale 排出分母,不會讓摘要偏紅。`cmd_enforcement` 的示意圖示已有 stale 項。
- 測試執行器 `LUMOS_SKIP_CLAUDE_PLUGIN=1` 與 pop 掉 `CLAUDE_CONFIG_DIR`:不影響正式路徑。
- 事件帳是路徑讀寫,沒有 API 欄位、沒有端點授權面:be-api-compat 與 be-authz 兩題對這份 diff 無對應輸入。唯一接近的是 F2(讀取路徑缺信任檢查,算資料存取邊界)。
- LUMOS-IMPACT:派工說這次沒附固定席節點,我照派工詞審,沒有補算。

重現環境:全程在 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ad81457d-7225-41ab-9224-1045d74d59f1/scratchpad/r3b` 底下的臨時 git repo,沒有改 `/Users/enzo/harness/lumos-toolchain-event-ledger` 的任何檔。我曾下過一條 `rm` 被安全檢查擋下、沒有執行。

總結:最嚴重 major,blocking 1 條
