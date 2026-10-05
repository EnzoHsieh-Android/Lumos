severity: major

### F1 `claude plugin list --json` 或 `marketplace list --json` 輸出 `null` 時,uninstall 與 install 的外掛步驟丟出未接的 TypeError
severity: major
blocking: 是 — `lumos uninstall` 在刪除任何東西之前整個崩潰,使用者的拆除被擋下。

- hunk:`_claude_json` 回傳 `json.loads(...)` 的結果,沒有檢查型別。`_teardown_claude_plugin` 與 `_sync_claude_plugin` 直接對它做 `for x in …`。except 只接 `(RuntimeError, ValueError, OSError, TimeoutExpired)`,不含 TypeError。
- 問題:`_teardown_claude_plugin()` 被放在 `cmd_uninstall` 的第一個動作(`_refuse_if_probe` 之後)。它一崩,後面的全域 symlink、skills 移除都不會跑。`_sync_claude_plugin` 在 `_sync_global_hooks` 尾端被呼叫,同樣會把 install 一併帶倒。
- 輸入→行→結果:`claude` 輸出 `null`(`json.loads("null")` 為 None)→ `_claude_json` 回 None → 迭代 None → TypeError。
- 重現:假 `claude` 只做 `echo null`,`PATH`、`HOME`、`LUMOS_HOME` 指向臨時目錄,再跑 `lumos uninstall`。輸出如下,跑的是 event-ledger 工作樹的 `scripts/lumos`。

```
File ".../scripts/lumos", line 18850, in _teardown_claude_plugin
    for x in _claude_json(claude, ["plugin", "list", "--json"])):
TypeError: 'NoneType' object is not iterable
```

  - `_sync_claude_plugin()` 在 line 18818 同樣是 TypeError。
  - 直接呼叫 `_teardown_claude_plugin()` 也是同一個 TypeError。
- 佐證:S6、S7 的假 claude 只會回 list 與錯誤碼,沒有任何一案餵 `null`、非 JSON 或物件。
引句:「return _j.loads(r.stdout or "[]")」
- file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:18850`

### F2 `--session` 沒有限制在事件帳資料夾內,`../` 與絕對路徑可讀 repo 外
severity: minor
blocking: 否 — 只讀取,只印 jsonl 的事件,不改任何檔。

- hunk:`cmd_events` 做 `d = base / session`,`_events_read` 做 `_events_root(root) / _EVENTS_REL / session`。兩處都沒擋路徑分隔字元與絕對路徑。
- 輸入→結果:`--session ../../../outside` 與 `--session <絕對路徑>` 都印出 `會談 …:1 筆事件`,內容來自 repo 外目錄的 `a.jsonl`(臨時目錄實測)。
- 空字串:`--session ""` 因 `if session:` 為假,默默變成列出所有會談,沒有報錯。
- 符號連結:`_events_read` 對符號連結會談回空,但 `cmd_events` 的 `d.is_dir()` 對它是真。結果印「0 筆事件」而不是回 2 找不到。
- 佐證:S5 只測了不存在的編號,沒有 `../`、絕對路徑、空字串、符號連結的案例。
引句:「d = _events_root(root) / _EVENTS_REL / session」
- file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:20411`

### F3 版本判斷 `ev.get("v") != 1` 把 `true` 與 `1.0` 當成版本 1
severity: minor
blocking: 否 — 只多收了格式不合的行,不影響正確資料。

- hunk:`_events_read`。
- 輸入→結果:行 `{"v":true,"ev":"tool","tool":"B"}` 在 Python 中 `True == 1`,被算成有效事件(實測 `--session S2` 印出 `tool B ✗`),而不是「版本不認得」。
- 佐證:S4 只用 `v:2` 當壞版本,沒有 `true`、`1.0`、字串 `"1"`。
引句:「elif ev.get("v") != 1:」
- file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/lumos:20432`

### F4 測試覆蓋的洞:S4、S5、S6、S7、S11 缺極端輸入案例
severity: minor
blocking: 否 — 屬測試薄弱,不是現行行為錯誤。

- S4:缺非 dict 行(陣列、數字)、空檔、非 UTF-8、`v:true` 的案例。
- S5:缺 `../`、絕對路徑、空字串、符號連結的 `--session`。
- S6、S7:假 claude 只回合法的 list JSON,缺 `null`、物件、空輸出、缺欄位。這正是 F1 沒被測到的原因。
- S11:缺 `--days " 5 "`、`+5`、`05`、`1e3`、超大數。實作對這些都保守拒絕或不刪,但沒有測試鎖住這個行為。
引句:「for bad in ("0", "-1", "1.5", "abc"):」
- file: `/Users/enzo/harness/lumos-toolchain-event-ledger/scripts/test_lumos.py`

### 圖譜鏡頭
派工時沒有附任何固定席筆記,機械反查的受影響測試、共改夥伴、呼叫者三格都是 0,所以沒有可逐條判的合約。未做的檢查:`--days` 的 prune 路徑、100000 層巢狀 JSON、`_events_root` 在子模組與裸 repo 下的行為。已實測 prune 的保守拒絕;巢狀 JSON 實測不崩(Python 3.14 把它算成壞行);`_events_root` 在子模組與裸 repo 的後備行為只讀程式碼,未實測。

severity: major
共 1 條 blocking(F1)。
