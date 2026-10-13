severity: minor

我只對照寫法,沒有真跑 `claude -p` 或 `codex`。這份 diff 沒有引入第二種做法,也沒有跨層直呼,所以沒有 major。找到兩條小的不對齊。

1. 兩個提早返回點只補了一半,`main` 裡兩個儀器例外結果沒帶 `env_fp`
severity: minor
blocking: 否
引句:「"limit_hit": False, "result_subtype": "codex", "harness": "codex",」
file: `scripts/scenario_probe.py:1400-1407`
file: `scripts/scenario_probe.py:1432-1438`
1. 既有寫法:`main` 裡有兩個 `res = {...}` 儀器例外結果,欄位集合要和 `run_one` 的結果保持一致。上一次加 `source_evidence` 時,這兩處都跟著補了 `"source_evidence": "unknown" if ... else None`。
2. 這份 diff:只在 `run_one` 和 `run_one_codex` 的提早返回、`run_one_codex` 的正常返回補了 `env_fp: None` 加 `env_missing`。`main` 那兩個 fallback 字典一律沒補,結果就缺 `env_fp` 這個鍵。
3. 差在哪:同一種「儀器例外結果」現在有帶鍵和不帶鍵兩種形狀。
4. 目前沒有實際壞處:這兩處的 `reason` 都以「儀器例外」開頭,`summarize_results` 的 `valid` 不會收它們,所以 `env_fps` 不受影響。
5. 計劃寫的是「兩個提早返回點」,指的是 `run_one` 和 `run_one_codex` 那兩處,和 `main` 這兩處無關。這條是欄位集合的慣例,不是 bug。
6. 歸因:有證據的原有漏查。修前修後都一樣。查證命令:`grep -n '"result_subtype": None' scripts/scenario_probe.py`。結果:`main` 內兩處(1406 和 1432-1438)都沒有 `env_fp`。
7. 三問②:正常、錯誤、相鄰路徑裡,只有這兩處形狀不同,而且不影響統計。

2. 「取不到」用了第二套字眼:`"null"` 字串鍵加獨立的 `env_missing`
severity: minor
blocking: 否
引句:「k = r.get("env_fp") or "null"」
file: `scripts/scenario_probe.py:1405-1412`
file: `scripts/scenario_probe.py:1406`
1. 既有寫法:同一批結果和歷史列裡,「無法判定」寫成 `"unknown"` 字串(`source_evidence`,`main` 的 fallback 字典用 `"unknown"`)。沒有就是 `None`(`first_tool`、`first_lumos_idx`、`result_subtype`)。
2. 這份 diff:結果裡 `env_fp` 是 `None`,原因另放新鍵 `env_missing`。計數統計又把它寫成字串 `"null"`。
3. 差在哪:同一個「取不到」概念在同一個結果檔和歷史列裡有 `"unknown"` 和 `"null"` 兩個詞。`None` 轉成 `"null"` 是為了 JSON 鍵的需要,這個理由成立,但詞可以沿用 `"unknown"`。
4. 沒有功能影響,風格上的詞彙不一致,所以標 minor。
5. 歸因:有證據的修復回歸。上一輪就是這樣寫的,不是這輪新引入的。查證命令:`grep -n '"unknown"' scripts/scenario_probe.py`。
6. 三問③:這個不一致修前修後相同。

已對照過、與既有寫法一致,不列為 finding:
- 逐行解析的 `strip`、`startswith("{")`、`json.loads` 加 `except Exception: continue`,與 `tool_calls_from_stream`(`scripts/scenario_probe.py:169`)和 `run_one` 的 `result_ev` 迴圈(`scripts/scenario_probe.py:1151`)相同。
- `hashlib` 由 `main` 內搬到頂層 import,與第 21 行其他標準庫的寫法一致。
- 小函式放在 `grade` 和 `judge` 之間、`summarize_results` 之前,位置與既有分區一致。
- 外層 `try/except Exception` 退成「取不到」的做法,與 `scripts/scenario_probe.py:907`(載不進就退回預設)同型。
- 測試沿用 `_load_probe_module`、`check()`、`import json as _j`、猴補 `mod.subprocess.run`、`raise_to`、`R` 類別,與既有截斷測試(`scripts/test_lumos.py:42180-42212`)的結構相同。

三問回答:
1. 修復效果的行為證據:我只讀了 diff 和既有檔,沒有重跑測試。修補方向(欄位型別不對當空的、`null` 不算一種環境、移除重複匯入)在程式裡都看得到。
2. 修補處的正常、錯誤、相鄰路徑:`run_one` 的正常和逾時路徑,以及 `run_one_codex` 兩個返回點,都有帶 `env_fp`。只有 `main` 兩個 fallback 字典沒帶,見第 1 條。
3. 新發現同一案例在修前、修後:兩條都是修前修後相同。

總結:最高等級 minor
