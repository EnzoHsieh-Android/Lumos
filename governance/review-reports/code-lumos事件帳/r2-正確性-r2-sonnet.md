severity: major

### F1 事件讀取端遇到一行怪內容就整支崩潰,`_events_clean` 擋不到
severity: major
blocking: 是 — 單行資料就讓 `lumos events --session` 以回溯結束,r1 修的「邊界行」同一族還剩兩個洞。

hunk:`_events_clean`、`cmd_events` 的 `--session` 輸出段(diff 約第 280–284、415–419 行)。

問題:r1 補了斷行、版本、控制字元,但兩處仍會崩。
- 孤立代理對(JSON 寫成 `\ud800`)會通過 `_events_clean`,因為它只剝控制字元。`print` 到 UTF-8 時丟 `UnicodeEncodeError`。`--json` 用 `ensure_ascii=False`,一樣崩。
- `ok` 欄位是 list 或 dict 時,`{True:…, False:…}.get(e.get("ok"))` 丟 `TypeError: unhashable`。

輸入→行→結果,以下在我自己的臨時 repo 重現:
1. `governance/runtime/events/S1/1.jsonl` 內容為 `{"v":1,"ev":"tool","ts":"t","tool":"\ud800","ok":true}`。
   - `lumos events --session S1`:回溯停在 `print(_events_clean(f"  {e.get('ts'...`,`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' ... surrogates not allowed`。
   - `lumos events --session S1 --json`:同一個錯誤。
2. 內容為 `{"v":1,"ev":"tool","ts":"t","tool":"Bash","ok":[1]}`,執行 `lumos events --session S1`,回溯停在 `ok = "" if e.get("ev") != "tool" else {...}.get(e.get("ok"), " ?")`,`TypeError: cannot use 'list' as a dict key (unhashable type: 'list')`。

JS 端的 `JSON.stringify` 遇到被截斷的字串會正規地輸出 `\udXXX`,所以孤立代理對不只是惡意輸入。列表模式(`_events_sessions`)的 `last` 欄位若含孤立代理對,印出時同樣崩,一個壞會談拖垮整份列表。

引句:「印到終端前剝掉控制字元:事件帳內容可能被人強制提交進 repo,ESC / BEL 會改寫終端畫面或視窗標題。」

### F2 `--days` 用 `isdigit()` 擋,遇到上標數字崩潰
severity: minor
blocking: 否 — 只是參數錯誤時給回溯而不是「擋下」訊息,沒有誤刪(`int()` 在刪除前就丟錯)。

hunk:`cmd_events` 的 `--prune` 天數驗證。

輸入→結果:`lumos events --prune --days '²'`。`'²'.isdigit()` 為 True、長度 ≤ 6,所以進到 `int(txt)`,丟 `ValueError: invalid literal for int() with base 10: '²'`(已重現)。r1 修補時宣稱天數不合法一律回 2 並印三段式訊息,這個輸入繞過了。

引句:「為什麼在意:天數不合法時寧可不動,免得一次刪光。例如保留 30 天:」

### F3 teardown 不把來源路徑傳給外掛移除,市集殘留且不出聲
severity: minor
blocking: 否 — 只留下一筆無害的市集登記,外掛本身已移除。

hunk:`cmd_uninstall` 新增的呼叫(`_teardown_claude_plugin()`),與 `_teardown_claude_plugin(source=None)` 的簽名。

輸入→結果:市集 `lumos-toolchain` 以 `--lumos-home A` 註冊(bootstrap 現在會這樣傳),事後在沒設 `LUMOS_HOME` 的環境跑 `lumos teardown --source A`。`cmd_teardown` 手上有 `source`,卻只呼叫無參數的 `cmd_uninstall()`。teardown 內 `_lumos_src(None)` 解析成預設路徑,和市集路徑 A 不相等,所以不移除市集。
- 假 claude 重現:日誌只有 `plugin list`、`plugin uninstall lumos-ledger@lumos-toolchain`、`plugin marketplace list`,沒有 `marketplace remove`。
- 輸出只印「已移除 … 外掛」,完全沒提市集還在,也沒印手動指令。

引句:「移除 lumos-ledger 外掛與我們的市集。沒有 claude、兩者都沒有就安靜略過;成功說移掉了什麼;失敗附兩個手動指令。」

### F4 安裝失敗的救援訊息在「新市集已加上、外掛沒裝上」時說錯
severity: minor
blocking: 否 — 救法(重跑 `lumos install --force`)仍然有效,只是敘述不實。

hunk:`_sync_claude_plugin` 的 `hint`。

輸入→結果:現有市集路徑與 `src` 不同,`remove` 成功、`add` 成功,`plugin install` 失敗。假 claude 重現,輸出是「舊的市集登記已移除、新的沒加上,事件帳暫時停寫」。實際日誌有 `marketplace add …/B --scope user`,新的已加上。`removed_old` 一旦為 True 就套用同一句,不分是哪一步失敗。

引句:「舊的市集登記已移除、新的沒加上,事件帳暫時停寫——修好原因後重跑 lumos install --force」

### F5 enforcement 新列的註解宣稱不呼叫外部指令,實際會跑 git
severity: minor
blocking: 否 — 只是註解與行為不符,有 20 秒逾時並退回 root,不會卡死。

hunk:`enforcement_status` ⑪。該列呼叫 `_events_root(root)`,內部是 `_lens_git` 子行程 `git rev-parse --git-common-dir`。註解寫「不呼叫任何外部指令」,與實作矛盾。`enforcement_status` 被儀表板與開場路徑讀取,這是每次多一個 git 子行程。

引句:「只看主 checkout 的事件帳資料夾修改時間,不呼叫任何外部指令。」

### 前輪修復驗收
- c1/e1(`claude` 列表吐 null 或非陣列):`_claude_json` 現在拒絕非 list 與元素非 dict 的輸出,拋 `RuntimeError`,外層有接。修好。我用假 claude 走過 install 路徑,沒有 TypeError。
- k1(bootstrap 沒傳 `LUMOS_HOME`):`env=dict(os.environ, LUMOS_HOME=str(home))` 已加。修好。相對路徑由 `_sync_claude_plugin` 內 `.resolve()` 處理。
- a1/e2/s2/k4(`--session` 跳出資料夾、空字串、連結):`fullmatch` 加 `is_symlink()` 與 `is_dir()` 修好,`..`、絕對路徑、空字串都被拒。
- c2/c3/e3/s1(斷行、缺 ok、v:true、控制字元):前四項修好。控制字元只剝 C0 與 C1,孤立代理對與不可雜湊的 `ok` 沒擋到,見 F1。
- c4/k7/p1/s3(超大 `--days`、刪失敗、上層連結):上限 36500 與位數限制修好。`isdigit()` 漏網,見 F2。逐層連結檢查與 `failed` 計數正確。
- k5(專案範圍裝過就不裝使用者層):`_ledger_user_plugin` 看 scope,修好。
- p2/p3(救援訊息、同時安裝的競態):競態的最終狀態判斷修好。救援訊息加了,但句子與實況不符,見 F4。
- 修出的新問題:F3、F4。

### 固定席與角色鏡頭
- `lumos-cli-read` 的 ★INVARIANT★(search 預設排除 superseded):本 diff 沒碰 search,不影響。
- `lumos-cli-lifecycle` 的 ★INVARIANT★(re-inject 只覆蓋 sentinel 之間):`cmd_uninstall` 與 `_sync_global_hooks` 只新增外掛子行程呼叫,沒碰 CLAUDE.md 注入,不影響。
- `design-loop` 處置閘 ★INVARIANT★:diff 沒涉及,不影響。
- 其餘固定席節點(`每支檔有家`、`bound-tests-gate` 等):`events` 與新函式需要有家,這是圖譜層的待辦,不是行為破壞。
- 另外:`.claude-plugin/marketplace.json` 與 `mods/claude/lumos-ledger` 目前不在這個分支,`_sync_claude_plugin` 在此分支恆回 `no-source`。我只確認了子行程邏輯,真實端到端沒驗到,後續提交補上後需要再驗一次。
- be-api-compat:`events --json` 是新增輸出,`--session --json` 沒有欄位改名,沒有相容問題。
- be-authz:`--prune` 的路徑安全逐層檢查正確。`_events_root` 在 worktree 裡改刪主 checkout 的事件帳是計劃內設計。我沒找到可重現的越權路徑。

總結:最嚴重 major,blocking 1 條
