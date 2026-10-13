severity: minor

三條 finding 都是 minor。沒有 blocker 或 major,也沒有碰到後端 API 相容或授權問題:be-api-compat 和 be-authz 兩張卡對這份 diff 不適用。這份 diff 沒有端點。結果 dict 與歷史列只新增欄位,沒有改名或刪欄位。下面有逐項走過的相鄰路徑。

1. init 欄位型別不對時 `env_fingerprint` 丟 TypeError,整場被記成儀器例外
severity: minor
blocking: 否
引句:「"mcp_servers": _env_names(init.get("mcp_servers")), "agents": _env_names(init.get("agents")),」
file: `scripts/scenario_probe.py:1071`(`_env_names` 內 `for x in items or []`)
1. 輸入:init 事件的 `skills`、`plugins` 或 `mcp_servers` 是非空且不可迭代的值,例如 `5` 或 `true`。
2. 走到:`run_one` 回傳時才呼叫 `env_fingerprint(out.splitlines())`,此時模型已經跑完。
3. 壞在:`items or []` 對 `5` 不會回空清單,`for x in 5` 丟 TypeError。例外一路傳到 main 的 `except Exception`,這場變成「儀器例外」而不計分。模型額度已花,判分結果丟掉,但這份改動標榜只記錄、不改判分。
4. 其他壞型別都不會例外,這是我實際跑過的結果。`None`、字串 `"abc"`、`dict`、混著清單或數字的 list 都安全。
5. 最小重現(不呼叫 claude):`env_fingerprint(['{"type":"system","subtype":"init","plugins":5}'])` 丟 `TypeError: 'int' object is not iterable`。`skills: 5` 與 `mcp_servers: true` 同樣丟。
6. 修法:在 `run_one` 用 try/except 包住 `env_fingerprint`,失敗時回 `env_fp: None` 加 `env_missing`。
7. 四支新測試沒有任何一支餵壞型別,這條沒被守住。

2. SessionStart 掛鉤不去重、不限第一次,中途再觸發的掛鉤會讓同一環境的指紋變動
severity: minor
blocking: 否
引句:「elif ev.get("subtype") == "hook_started" and ev.get("hook_event") == "SessionStart":」
file: `scripts/scenario_probe.py:360`
1. 輸入:同一環境下,一場會談在 init 之後又多出一筆 `SessionStart:compact` 或 `resume` 的 `hook_started`。
2. 走到:`_env_scan` 掃全部行,凡是 SessionStart 的 `hook_started` 都 append。不看是否在 init 之前,也不去重。
3. 壞在:指紋只該反映啟動時載入了什麼,卻被會談中途的事件影響。實測如下:
   - 只有 `SessionStart:startup` 時指紋是 `96f536f57edb`。
   - 多一筆 `SessionStart:compact` 變成 `f1571852e55f`。
   - 同一筆 startup 重複出現,指紋變成 `b68e925e1077`。
4. 後果:`env_mixed` 會被誤標成 true,「規矩變了還是環境變了」的訊號被污染。
5. 觸發機率:`--max-turns 18` 下自動壓縮很少發生,所以標 minor。另有一點我驗不到:run_one 沒傳 `--include-hook-events`,真實 2.1.296 的 `-p --verbose` 是否一定吐 SessionStart 的 `hook_started`,我沒辦法驗(不准呼叫 claude),計劃稱已實測。若不吐,`session_start_hooks` 恆為空,測試用的假資料仍會綠。⚠

3. 指紋測試只涵蓋五個欄位,拿掉其餘欄位的實作測試不會翻紅
severity: minor
blocking: 否
引句:「"SessionStart 掛鉤不同": dict(_hooks=[]),」
1. `variants` 只測外掛、外掛版本、output_style、skills、SessionStart 掛鉤五項。
2. 沒測的欄位有 `mcp_servers`、`model`、`claude_code_version`、`permissionMode`、`tools`、`agents`、`slash_commands`。把任何一項從 `stable` 拿掉,四支測試仍全綠。MCP 伺服器是這份指紋最主要的目的,卻沒有守住。
3. 其餘三支測試的判斷:
   - `t_probe_history_records_env_fps` 的「被排除場次不算」與「null 那一格」可以翻紅。
   - `t_probe_run_one_records_env_fp` 與 `missing_init` 在 `run_one` 拿掉併入時會翻紅。
   - 沒有發現空集合下恆成立的假綠。
4. 補法:在 `variants` 加一條 `mcp_servers=[{"name":"x"}]` 即可。

相鄰路徑檢查(無問題):
- `run_one` 兩個返回點與 `run_one_codex` 兩個返回點都帶 `env_fp`。main 的例外兜底 dict 沒有 `env_fp`,但它的 reason 以「儀器例外」開頭,不進有效場次,所以不影響。
- `summarize_results` 的 `line` 沒動,`governance/autonomous-loop.sh` 解析總結行不受影響。
- 歷史檔舊列沒有新欄位,新增鍵不會讓舊讀者壞。`autonomous-loop.sh` 只用字串 grep `"seed"`。
- `governance/eval/ablation_lumos_first.py` 只讀 `results` 列的既有欄位,多的 `env` 與 `env_fp` 不會讓它出錯。
- `env_fp_counts` 在沒有任何結果帶 `env_fp` 時回 None,舊呼叫者不會多出欄位。Codex 批次的 `env_fps` 會是 `{"null": N}`,單一種所以不標 mixed,無害。
- 指紋裡的 `"null"` 計入種類數:有效場次裡混入一場取不到 init 的 Claude 場,就會標 `env_mixed: true`。語意可接受,但是否算「環境混合」要由使用者自己決定。

總結:最高等級 minor
