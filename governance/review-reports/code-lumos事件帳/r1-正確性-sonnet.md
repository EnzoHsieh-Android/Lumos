severity: major

圖譜鏡頭:派工只附機械反查(受影響測試、共改夥伴、呼叫者三格皆空),沒有釘到固定席節點,沒有節點可逐條答。補一句判斷:這份 diff 沒有動既有合約。`enforcement_status` 新增的 `stale` 值已被 `enforcement_summary`(`scripts/lumos:20813`)排除在分母外,也已有圖示對應(`scripts/lumos:20831`)。測試隔離這塊,`_isolate_environment` 確實設了 `LUMOS_SKIP_CLAUDE_PLUGIN=1` 並清掉 `CLAUDE_CONFIG_DIR`。子行程繼承 `os.environ`,HOME 也是假的,所以既有 install/uninstall 測試碰不到真的 claude。角色卡沒有附,略過。

### F1 claude 回 JSON `null`(或任何非可迭代值)時 install 與 uninstall 會直接崩潰
severity: major
blocking: 是 — 違反本案核心承諾「外掛步驟失敗不影響 install 回傳碼」,還讓 uninstall 在移除 symlink 之前中止。

hunk:`_claude_json`、`_sync_claude_plugin`、`_teardown_claude_plugin`。

問題:`_claude_json` 回傳 `json.loads(r.stdout or "[]")`,沒有檢查型別。`null` 解成 `None`,數字解成 int,呼叫端直接 `for x in <None>`。`except (RuntimeError, ValueError, OSError, subprocess.TimeoutExpired)` 接不住 `TypeError`,例外一路冒到 `cmd_install` 與 `cmd_uninstall` 外面。

引句:「raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[0] if (r.stderr or r.stdout).strip() else f"rc={r.returncode}")」

重現(臨時目錄,假 HOME,假 claude 一律 `echo null`):
- 路徑:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ad81457d-7225-41ab-9224-1045d74d59f1/scratchpad/y1`
- `lumos install --force` 結果是 rc=1,輸出 `TypeError: 'NoneType' object is not iterable`,停在 `_sync_claude_plugin` 的 `scripts/lumos:18818`。
- 崩潰發生在 `cmd_install` 的 `for _h in ("claude","codex")` 迴圈裡,所以 codex 側的 hook 同步、PATH 檢查、`merge-failed` 判斷全被跳過。
- `lumos uninstall` 同樣 `TypeError`,停在 `_teardown_claude_plugin` 的 `scripts/lumos:18850`。
- `_teardown_claude_plugin()` 排在 symlink 移除之前,所以 `home/.local/bin/lumos` 還留著,uninstall 是半拆狀態。
- `lumos update` 與 `init` 經 `_sync_global_from_project` 也會走同一處,沒有外層 try。

file: `scripts/lumos:16954` 的 `cmd_install` 迴圈沒有任何 try 包住 `_sync_global_hooks`。

### F2 事件含 U+2028、U+2029、U+0085 時,`splitlines()` 把一筆事件切成兩行壞行
severity: minor
blocking: 否 — 事件被靜默改記成壞行,但只影響統計與顯示,不損資料。

hunk:`_events_read`。

引句:「for line in f.read_text(encoding="utf-8", errors="replace").splitlines():」

輸入:寫入端是 TypeScript mod,JSON.stringify 不會跳脫 U+2028、U+2029、U+0085。計劃 `Lumos事件帳_計劃.md:71` 說 `cmd` 欄位記 Bash 指令前 500 字,這些字元可能出現在裡面。

結果:Python `str.splitlines()` 會在這些字元處斷行。我造了一筆 `cmd` 含 U+2028(編排者註:原稿此處是那個字元本身,傳遞時被顯示成換行,存檔改寫成字元代號)的 `tool` 事件(`ok:false`),`lumos events --session S1` 印「1 筆事件(略過:壞行 2…)」。那筆失敗的事件被丟掉,列表裡的「失敗」計數少算。改用 `split("\n")` 即可避免。

### F3 `tool` 事件缺 `ok` 欄位時,逐筆輸出標 ✗,但列表視圖不算失敗
severity: minor
blocking: 否 — 只是兩個視圖的判準不一致。

hunk:`cmd_events` 逐筆輸出。

引句:「ok = "" if e.get("ev") != "tool" else (" ✓" if e.get("ok") else " ✗")」

輸入:`{"v":1,"ev":"tool","tool":"X"}`(沒有 `ok`)。逐筆印出 `tool  X ✗`,而 `_events_sessions` 用 `e.get("ok") is False`,列表印「失敗 0」,實測兩邊矛盾。

### F4 `--prune --days` 給極大整數(約 309 位數以上)時崩潰成 OverflowError
severity: minor
blocking: 否 — 崩潰時什麼都沒刪,不會誤刪資料,只是錯誤處理不一致。

hunk:`_events_prune`。

引句:「cutoff = now - days * 86400」

輸入:`--days 1` 後面接 400 個 0。`int("1000…")` 在 4300 位數上限內可解析,也通過 `str(n) == str(days).strip()` 檢查。`float - 巨大 int` 丟出 `OverflowError: int too large to convert to float`,沒人接,輸出 traceback 而不是三段式的擋下訊息。實測如此。

最嚴重 severity:major,blocking 共 1 條。
