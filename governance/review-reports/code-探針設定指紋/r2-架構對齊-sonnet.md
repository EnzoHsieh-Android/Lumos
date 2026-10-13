severity: minor

## 1. 檔頂已匯入 hashlib,main() 裡還留著舊的區域匯入
severity: minor
blocking: 否
引句:「import argparse, ast, errno, hashlib, json, os, re, secrets, shutil, stat, subprocess, sys, tempfile, time」
file: `scripts/scenario_probe.py:1301`

- 既有寫法在 `scripts/scenario_probe.py:1301`:`main()` 抽樣段落裡自己 `import hashlib`。這份 diff 在檔頂(第 21 行)加了 hashlib,卻沒動那一行。
- 現在同一個模組有兩處匯入同一個東西,一處在檔頂、一處在函式裡。
- 影響:執行行為沒有差別。這是 diff 遺漏的順手清理,不是第二種做法。
- 歸因:有證據的修復回歸(本輪之前就已加了檔頂匯入)。
- 查證命令:`grep -n "hashlib" scripts/scenario_probe.py`。結果是第 21、389、1301 行。

## 與既有寫法對齊的部分(不列為 finding)
- **stream-json 逐行解析**:`_env_scan` 的寫法是 `strip`、`startswith("{")`、`json.loads` 失敗就 `continue`。`tool_calls_from_stream`(約第 187 行)、`run_one` 的 result 迴圈(第 1139 行)和 codex 解析器(第 155 行)都是這個形狀。
  - 唯一的小差異是例外型別:`_env_scan` 寫 `except ValueError`,前三處寫 `except Exception`,`source_evidence`(第 230 行)寫 `(ValueError, TypeError)`。
  - 這裡的輸入一定是 str,三種寫法的結果相同,所以只提一句。
- **「取不到」的表示法**:既有程式用 `None` 加原因文字(例如 `first_tool: None`、`source_evidence: "unknown"`)。新欄位 `env_fp: None` 加 `env_missing` 沿用這個慣例。計數表的 `"null"` 字串鍵是 JSON 字典不能用 None 當鍵的必要折衷。
- **只記錄欄位的意外處理**:`env_fingerprint` 外層包 `except Exception` 退成「取不到」,跟第 898 行「載不進就退回預設,不把整場判成儀器例外」是同一種做法。內層另拆一支 `_env_fingerprint`,在這個檔裡是新的寫法,但不算第二種做法。
- **提早返回點**:`run_one` 和 `run_one_codex` 的 `_validate_scenario` 失敗分支都補了 `env_fp: None` 加原因。
  - `main()` 迴圈裡兩個例外分支(第 1398、1429 行)沒補這兩欄,但它們的 reason 以「儀器例外」開頭,會被 `summarize_results` 的 `valid` 排除。
  - `env_fp_counts` 用 `any("env_fp" in r ...)` 判斷,所以不受影響。
- **小函式位置**:新函式放在 `grade` 和 `judge` 之間,不在檔前段其他 stream 解析器旁。這是偏好問題,不列。
- **測試寫法**:新增的四支測試用 `_load_probe_module`、`_probe_res`、`check(...)`,用 `mod.subprocess.run` 替換成假的再還原,結尾印 `✓`(全檔共 259 處)。這跟 `t_probe_truncated_run_not_scored` 的寫法一致。
- **新欄位的讀取端**:新欄位目前只有 `summarize_results` 和 `history_record` 讀,`governance/*.sh` 和其他腳本沒有人讀,沒有跨層直呼。

沒有第二種做法,也沒有跨層直呼。

總結:最高等級 minor
