severity: clean

沒有發現架構對齊上的問題。這份 diff 的寫法跟 `scripts/scenario_probe.py` 既有的做法一致,沒有引入第二種做法,也沒有跨層直呼。

**對齊的地方(對照到哪裡)**

1. **解析 stream-json**
   - 新函式 `_env_scan` 用的是 `tool_calls_from_stream` 同一套骨架:逐行 `strip`、`startswith("{")` 才解析、`json.loads` 失敗就 `continue`。對照 `file: `scripts/scenario_probe.py:184``,`run_one` 取 result 事件的迴圈 `file: `scripts/scenario_probe.py:1124`` 也是同一型。
   - 既有程式本來就是每個用途各掃一遍(`calls`、`final/result_ev`、`source_evidence`),所以 `env_fingerprint(out.splitlines())` 再掃一遍屬於既有慣例。
   - `source_evidence` 的 `except (ValueError, TypeError)` 和 `tool_calls_from_stream` 的 `except Exception` 兩種寫法並存,`_env_scan` 的 `except ValueError` 落在這個範圍內。

2. **「取不到」的表示法**
   - 新做法是 `env_fp: None` 加 `env_missing` 原因。對照既有結果欄位:`first_tool: None`、`first_lumos_idx: None`、`answer_content_ok: None`、`result_subtype: None`,取不到都用 None。
   - 提早返回點補欄位的方式,跟既有的 `"limit_hit": False, "result_subtype": None` 在同一個字典字面值裡擴充一致。
   - Codex 執行器寫死 None 加原因,對照它既有的 `"result_subtype": "codex"`、`limit_hit` 恆 False 的寫法 `file: `scripts/scenario_probe.py:1004``。

3. **歷史紀錄欄位**
   - `history_record` 新增的 `if summary.get("env_fps"): rec["env_fps"] = ...` 是選填欄位追加法,跟既有的 `if arm != "with" or runs > 1: rec.update({"arm": ..., "runs": ...})` 同型 `file: `scripts/scenario_probe.py:1200``。
   - 舊呼叫者沒帶 env_fps 時不寫欄位,所以舊紀錄形狀不變。
   - `env_fp_counts` 對「沒有任何結果帶 env_fp 欄位」回 None,跟 `summary.get("valid_total", ...)` 這種向後相容的寫法一致。
   - 分母只用 `valid`,跟 `summarize_results` 既有的有效場次口徑一致。

4. **判準版本常數**
   - `GRADER_VERSION` 和 `SANDBOX_VERSION` 沒改。這份 diff 只記錄、不改判分,也不改沙盒,所以不改是對的。常數註解說的是「判準換過,前後通過率不可直接比」`file: `scripts/scenario_probe.py:216``。

5. **模組層 import 與函式位置**
   - `hashlib` 加進頂部單行的 import 串 `file: `scripts/scenario_probe.py:21``,沒有在函式內才 import。
   - 新函式放在 `grade` 之後、`judge` 之前,屬於判分與資料整理這一區。
   - 命名用底線前綴的私有小函式,公開入口是 `env_fingerprint`、`env_fp_counts`,跟 `grade`、`judge`、`lumos_stats` 一致。
   - 常數 `_ENV_MISSING_INIT` 放在使用處旁邊,不放在檔頭。

6. **測試檔**
   - 新測試沿用既有 `t_probe_*` 的寫法:`_load_probe_module("sp_xxx")`(`file: `scripts/test_lumos.py:42154``)、區域類別 `R` 加假 `subprocess.run`、`try/finally` 還原 `mod.subprocess.run`、逾時用 `raise_to` 丟 `TimeoutExpired`。這些都出自 `t_probe_truncated_run_not_scored`(`file: `scripts/test_lumos.py:42170``)。
   - 結果用 `_probe_res` 組(`file: `scripts/test_lumos.py:42214``)。
   - 測試 docstring 前綴 `[探針設定指紋 S1]` 對應計劃條款,跟既有的 `[S1]`、`[S2]` 一致。
   - `t_probe_env_fingerprint_stable_fields` 有「前置:取得到指紋與摘要」的斷言,符合 `Systems/測試假綠形態` 的 INVARIANT。
   - 新測試末尾的 `print("  ✓ ...")` 在別處也有先例(`file: `scripts/test_lumos.py:8888``),但相鄰的 `t_probe_summary_excludes_instrument_runs` 沒有。這是風格偏好,不列為 finding。

**不影響結論的小差異(沒有失敗場景)**

- 取不到 init 的原因,`env_fingerprint` 用常數 `_ENV_MISSING_INIT`,兩個提早返回點與 Codex 路徑直接寫字串字面值。字面值各自出現一次,沒有第二種做法。
- `--out` 的 JSON 報告不帶 `env_fps` 彙總,只有逐筆 `results` 裡有 `env_fp`。這份報告本來就把摘要欄位分散放(`excluded`、`valid_total`、`inconclusive`),計劃主題也只要求歷史紀錄,所以不算不對齊。

總結:最高等級 clean
