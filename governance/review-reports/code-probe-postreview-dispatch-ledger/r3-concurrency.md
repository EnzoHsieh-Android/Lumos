severity: major

finding: 五小時窗口帳只掃目前的輸出目錄；跨午夜切到新日期目錄，或依事故流程歸檔舊檔後，仍在窗口內的模型嘗試會歸零，下一批可再次啟動模型，突破 `--max-per-window`。

severity: major  
blocking: 是  
引句:「for p in _result_json_files(out_dir):」  
file: `governance/eval/ablation_lumos_first.py:218`  
具體輸入路徑：`.../ablation-lumos-first/2026-10-03/with-q-old.json` 在 23:59 寫入一列與兩次重試；00:01 預設輸出切到 `.../2026-10-04/`。後者的 `runs_in_window()` 回傳 0，`run_job(..., max_per_window=1)` 仍啟動一次子程序。把同一檔依人工處置改名為 `.archived` 也同樣從窗口帳消失。  
最小重現：
```bash
python3 - <<'PY'
import importlib.util, json, tempfile
from pathlib import Path
repo = Path("/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone")
s = importlib.util.spec_from_file_location("ab", repo/"governance/eval/ablation_lumos_first.py")
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
with tempfile.TemporaryDirectory() as td:
    root = Path(td); old = root/"2026-10-03"; new = root/"2026-10-04"
    old.mkdir(); new.mkdir()
    p = old/"with-q-old.json"
    p.write_text(json.dumps({"arm":"with","results":[{"id":"a","passed":True,
        "retry_attempts":[{},{}]}],"fatal":False,"inconclusive":False,
        "skills_health_bad":[]}))
    assert m.runs_in_window(old) == 3
    assert m.runs_in_window(new) == 3
PY
```
觀測：第二個 assertion 翻紅，實際值為 0。窗口帳需放在不隨日期或事故歸檔消失的來源，或掃描涵蓋窗口的相鄰日期與已歸檔嘗試。

finding: 事故紀錄內的重跑指示只要求歸檔 fatal 與 candidate，漏掉 `.pending`；照欄位操作後下一批仍被 pending 永久判為 poisoned。

severity: major  
blocking: 是  
引句:「"retry_policy": "archive-fatal-and-candidate-then-rerun"}」  
file: `governance/eval/ablation_lumos_first.py:254`  
具體輸入路徑：子程序回傳 `rc=2` 後留下同 stem 的 `.json`、`.candidate`、`.pending`；依 `retry_policy` 歸檔前兩者，再呼叫 `collect_skills_health(out_dir)`。  
最小重現：
```bash
python3 - <<'PY'
import importlib.util, json, tempfile
from pathlib import Path
repo = Path("/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone")
s = importlib.util.spec_from_file_location("ab", repo/"governance/eval/ablation_lumos_first.py")
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
with tempfile.TemporaryDirectory() as td:
    d = Path(td); stem = "with-q-x"
    marker = {"arm":"with","qid":"a","results":[],"fatal":True,
              "inconclusive":True,"skills_health_bad":[]}
    (d/f"{stem}.pending").write_text(json.dumps(marker))
    (d/f"{stem}.json").write_text(json.dumps(marker))
    (d/f"{stem}.candidate").write_text("{}")
    for p in [d/f"{stem}.json", d/f"{stem}.candidate"]:
        p.rename(p.with_suffix(p.suffix+".archived"))
    assert not m.collect_skills_health(d)
PY
```
觀測：assertion 翻紅；剩餘 `.pending` 仍回報「探針整批 fatal」。指示需明列 formal、candidate、pending 三者，並由測試走完實際恢復流程。

finding: 最後一個允許嘗試若撞用量上限，程式仍先睡 300 秒，下一圈才發現嘗試額度已耗盡並標 fatal。

severity: minor  
blocking: 否  
引句:「if a.max_attempts and attempts_started >= a.max_attempts:」  
file: `scripts/scenario_probe.py:1040`  
具體輸入路徑：`--runs 2 --wait-on-limit 300 --max-attempts 1`，第一次模型呼叫回傳 `limit_hit=True`。目前控制流在 `scripts/scenario_probe.py:1115` 仍進入等待並執行 300 秒 sleep，之後才回到額度檢查；預算已確定耗盡時應直接產生 fatal，不再等待。

父死子活的候選隔離、成功後原子升格、成功升格與 pending 清理之間的中斷、目錄鎖與舊鎖並存、一般例外的 fail-closed 路徑：已讀，無其他 finding。

總結：最嚴重 severity major，blocking 2 條。
