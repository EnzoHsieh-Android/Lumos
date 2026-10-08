severity: major

### F1 巢狀深度落在「解析得過、印不出來」的窗口時,列表與逐筆文字輸出都 Traceback
severity: major
blocking: 是 — 一行約 140KB 的事件就讓 `lumos events` 與 `lumos events --session` 兩種文字輸出未接例外退出,同目錄其他會談也一起看不到。

- hunk:`_events_read` 與 `cmd_events`。r2 修了解析端:`except (ValueError, RecursionError)` 把 200000 層巢狀算壞行。沒修的是 `json.loads` 成功、但之後 `str()` / `repr()` 同一個物件時才超出遞迴上限的深度。事件裡的 `ts`、`tool` 等欄位會被 f-string 轉成字串再進 `_events_clean`,而這一步沒有任何保護。
- 具體輸入→結果(python3.14,臨時 repo,scripts/lumos 取自該 repo 的 HEAD 51f3a76e):
  - `S1/1.jsonl` 只有一行,內容為 `{"v":1,"ev":"turn_end","ts":` 加 70000 個 `[` 加 70000 個 `]` 再加 `}`。
  - `lumos events` 印 `RecursionError: Stack overflow (used 16352 kB) while getting the repr of an object`,位置在列表印行的 `r['last'] or '?'`,rc=1。
  - `lumos events --session S1` 同樣的 RecursionError,rc=1。
  - 深度 100000 一樣崩。深度 50000 與 120000 都不崩,所以是一段窗口(約 70000 到 100000 層);120000 層在解析端就被算成壞行。
  - 把同樣巢狀放進 `tool` 欄位(`{"v":1,"ev":"tool","tool":[[...]],"ok":false}`),`--session S1` 也崩。
  - `--json` 兩種輸出不崩(`json.dumps` 在這個深度還撐得住)。
- 佐證:`t_events_reader_hostile_lines` 用的是 200000 層,落在解析就失敗的那一側,測不到這段窗口。這是 r2 邊界 F1 同族的剩餘形狀:修在 loads 的例外,而不是「進入輸出前的值型別與大小」。
引句:「# 極深巢狀的一行會把解析器的遞迴吃光」
- file: `scripts/lumos`(`cmd_events` 列表印行與逐筆印行;diff 內第 509 到 521 行一帶)

### F2 `_events_clean` 對整行截斷 2000 字元,長欄位會把結尾的 ✓ / ✗ 切掉
severity: minor
blocking: 否 — 失敗工具呼叫被印成沒有狀態標記,是顯示錯誤,不崩、不刪、列表的 failed 計數仍正確。
- hunk:`cmd_events` 逐筆輸出的 `_events_clean(f"...{detail}{ok}")`,`_events_clean` 先呼叫 `_esc_clean(text, 2000)`。
- 輸入→結果:`{"v":1,"ts":"t","ev":"tool","tool":"A"×3000,"ok":false}` → `events --session S1` 輸出一行長 2003、以 `…` 結尾,沒有 ✗。`ok` 標記接在 `detail` 後面,超長就被截掉;tool 很短時同一筆有 ✗。
- 佐證:`t_events_reader_edge_lines` 沒有超長欄位案例。截斷發生在碼點層,沒有切在多位元組中間(驗過)。
引句:「事件帳內容可能被人強制提交進 repo」
- file: `scripts/lumos`(`_events_clean`,diff 內第 344 行)

### F3 讀取端沒有大小上限,單一超長行讓記憶體與時間爆量
severity: minor
blocking: 否 — 只在有人把巨檔強制提交進 repo 時發生,是資源耗盡而非錯結論。
- hunk:`_events_read` 的 `f.read_text(...)` 整檔讀入、再 `text.split("\n")`。
- 輸入→結果:`S1/1.jsonl` 單行約 300MB(合法 JSON,`tool` 欄位是 3 億個 a)。`lumos events` 列表 1.99 秒、峰值約 1.1GB;`lumos events --session S1` 32.83 秒、峰值約 2.6GB(慢在 `_esc_clean` 逐字跑)。列表模式最多讀 10 個會談,每個都是這個量級。
- 佐證:`_events_sessions` 只限制讀幾個會談,沒限制單檔或單行大小。
引句:「塊檔依檔名排序、塊內照行序;壞行與版本不是 1 的行各自計數後略過。」
- file: `scripts/lumos`(`_events_read`,diff 內第 348 行)

### F4 `_events_main_trusted` 對 gitdir 檔內容處理過窄:相對路徑誤擋、壞位元組丟 Traceback
severity: minor
blocking: 否 — 兩種都落在「不刪」這一側,沒有刪錯,只是誤擋與未接例外。
- hunk:`_events_main_trusted`,逐一讀 `main_root/.git/worktrees/*/gitdir`,只接 OSError。
- 輸入→結果(在登記過的 worktree 裡跑 `events --prune --days 30`):
  - 結尾帶空白 → 可信,正常刪除(strip 有效)。
  - 相對路徑:gitdir 內容 `../../../../wt2/.git`(新版 git 相對路徑 worktree 格式。⚠ 本機 git 2.39 不會自己寫出,我手改檔案模擬)→ 印「擋下:事件帳路徑 … 不可信」,什麼都沒刪。`Path(...).resolve()` 對目前工作目錄解析,不是對 gitdir 檔所在目錄;把 cwd 換成 `.git/worktrees/wt2` 同一個 worktree 就變可信,結論取決於 cwd。擋下訊息的原因欄也講錯原因。
  - 任何一個 worktree 項目的 gitdir 含非 UTF-8 位元組(如 0xFF 0xFE)或 NUL:在 worktree 裡跑 prune 丟 `UnicodeDecodeError` / `ValueError: lstat: embedded null character in path`,Traceback 退出;別的 worktree 的壞項目會連帶擋住合法的那個。這兩種都不是 `OSError`。從主 checkout 跑不受影響(`root == main_root` 提前返回)。
- 佐證:`t_events_prune_hardening` 只有一個絕對路徑且完好的 gitdir 案例。
引句:「才算可信——.git 檔可以被人改成指到別的 repo,不驗就會把清理導到別人的事件帳」
- file: `scripts/lumos`(`_events_main_trusted`,diff 內第 434 到 446 行)

### F5 讀取路徑沒做 `_events_path_safe`,上層連結可讀到 repo 外
severity: minor
blocking: 否 — 只讀且只印符合事件格式的欄位,但與 prune 端的路徑守衛不一致。
- hunk:`cmd_events` 的列表與 `--session` 路徑。`_events_path_safe` 只在 `--prune` 分支呼叫;讀取端只檢查會談資料夾與塊檔本身是不是連結。
- 輸入→結果:repo 內 `governance/runtime` 是指向 repo 外 `out/runtime` 的符號連結,`out/runtime/events/OUTS/1.jsonl` 內容 `{"v":1,"ev":"tool","ts":"OUTSIDE-REPO","tool":"leak","ok":true}` → `lumos events` 列出 `OUTS  最後 OUTSIDE-REPO …`,`lumos events --session OUTS` 印出 `OUTSIDE-REPO  tool  leak ✓`。
- 佐證:r2 邊界 F6 修了塊檔連結,同族的「上層目錄連結」只補在清理那邊。
引句:「事件帳路徑從 repo 根往下每一層都不能是符號連結:陌生 repo 可以把 governance 或 runtime 做成連結,」
- file: `scripts/lumos`(`_events_path_safe` 與 `cmd_events`,diff 內第 449 與 489 行)

### F6 ⚠ 修復測試只驗「拒絕」這一側,信任判斷永遠回假也會全綠
severity: minor
blocking: 否 — ⚠ 我沒有真的對測試檔做變異,只依測試內容推論;實測確認真實行為正確,所以只是測試強度問題。
- hunk:`t_events_prune_hardening`。
- 觀察:對 `_events_main_trusted` 只有一個案例(竄改的 `.git` 指到別的 repo,期望 `v_old.exists()`),沒有「登記過的真 worktree 可以清理」的正向案例(全檔 worktree add 只出現在 `t_events_reader_from_worktree` 與 `t_enforcement_ledger_row`,都不跑 prune)。把 `_events_main_trusted` 改成永遠回 False、或讓 prune 一律拒絕,這個案例照樣綠。F4 的相對路徑誤擋就是這個缺口的實例;F1 的窗口深度同樣沒有測試。
- 實測:臨時 repo 手動驗過,登記過的 worktree(絕對路徑 gitdir)執行 prune 確實刪得到主 checkout 的舊會談,現行行為正確,缺的是被測分支沒被釘住。
引句:「.git 檔被竄改:看起來像 worktree,實際指到另一個 repo」
- file: `scripts/test_lumos.py`(`t_events_prune_hardening`,diff 內第 1337 行起)

### 前輪修復驗收(r2 邊界席 F1 到 F7)
- F1 極深巢狀(200000 層):已修。算壞行、其他事件照讀、列表與逐筆都 rc=0。但同族的「解析得過、印不出來」窗口(約 70000 到 100000 層)未修,見本輪 F1。
- F2 孤立代理字元:已修。`ts` 與 `tool` 放 U+D800 時,文字、列表、`--json` 都 rc=0;JSON 內為跳脫形式。
- F3 `ok` 是列表:已修。印 `?`、不崩。
- F4 `--days` 上標數字:已修。上標、圈號、`+5`、`05` 都回 2、訊息在標準錯誤、無 Traceback。
- F5 雙向覆寫與零寬字元:已修。文字輸出實測沒有 U+202E、U+200B 的位元組;JSON 為 ASCII。
- F6 塊檔符號連結:已修。連結塊檔不被讀;同族的上層目錄連結見本輪 F5。
- F7 teardown 範圍:已修(讀碼確認與 `_ledger_user_plugin` 一致的 `--scope user`)。⚠ 本環境不准跑會改設定的 claude 子指令,只靠讀碼,未實跑真 claude。

固定席圖譜鏡頭:這次沒附固定席節點,未判。

總結:最嚴重 major,blocking 1 條
