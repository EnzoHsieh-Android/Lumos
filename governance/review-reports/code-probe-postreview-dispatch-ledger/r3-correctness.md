severity: major

finding: 五小時額度只計正式 JSON；失敗候選中的真實模型呼叫在人工歸檔後歸零，重跑可再次取得完整額度。  
severity: major  
blocking: 是  
引句:「for p in _result_json_files(out_dir):」  
file: `governance/eval/ablation_lumos_first.py:218`  
具體輸入與路徑：第一次工作在同一場實際呼叫 3 次模型（兩次限額重試加最後一次），之後子程序以 rc=2 結束。父程序寫入 `results: []` 的 fatal 正式 JSON，含三次呼叫證據的 candidate 不在 `_result_json_files` 範圍，因此 `runs_in_window()` 當場回 0；依人工處置說明歸檔正式檔、pending 與 candidate 後再跑，派工器又傳入 `--max-attempts 5`。同一五小時窗口因此容許 3+5=8 次，違反 S18 的實際呼叫額度。  
最小重現：
```bash
python3 - <<'PY'
import importlib.util, json, tempfile
from pathlib import Path
from unittest.mock import patch
p=Path("governance/eval/ablation_lumos_first.py").resolve()
s=importlib.util.spec_from_file_location("a",p)
a=importlib.util.module_from_spec(s); s.loader.exec_module(a)
with tempfile.TemporaryDirectory() as td:
    out=Path(td)/"out"; out.mkdir()
    archive=Path(td)/"archive"; archive.mkdir()
    def failed(cmd, **kw):
        target=Path(cmd[cmd.index("--out")+1])
        target.write_text(json.dumps({
          "arm":"with",
          "results":[{"id":"a","passed":False,"reason":"儀器例外: limit",
                      "limit_hit":True,"retry_attempts":[{},{}]}],
          "fatal":False,"inconclusive":True,"skills_health_bad":[]}))
        return type("R",(),{"returncode":2})()
    with patch.object(a.subprocess,"run",side_effect=failed):
        a.run_job("with","a",1,["dummy"],1,1,out,1,max_per_window=5)
    print("count_after_3_attempts", a.runs_in_window(out))
    for x in list(out.iterdir()):
        if x.suffix in {".json",".pending",".candidate",".failed"}:
            x.rename(archive/x.name)
    captured=[]
    def success(cmd, **kw):
        captured.append(cmd)
        target=Path(cmd[cmd.index("--out")+1])
        target.write_text(json.dumps({
          "arm":"with","results":[{"id":"a","passed":True}],
          "fatal":False,"inconclusive":False,"skills_health_bad":[]}))
        return type("R",(),{"returncode":0})()
    with patch.object(a.subprocess,"run",side_effect=success):
        a.run_job("with","a",1,["dummy"],1,1,out,1,max_per_window=5)
    cmd=captured[0]
    print("rerun_budget", cmd[cmd.index("--max-attempts")+1])
PY
```
觀測：`count_after_3_attempts 0`、`rerun_budget 5`。需要讓失敗嘗試留下窗口帳，或在其五小時有效期內禁止以歸檔清除用量證據。

finding: 題目在真正啟動模型前驗證失敗，仍會消耗一格宣稱為「模型嘗試」的額度。  
severity: minor  
blocking: 否  
引句:「attempts_started += 1」  
file: `scripts/scenario_probe.py:1049`  
具體輸入與路徑：題目 `{"id":"a","prompt":"q"}` 缺 `expect`，`attempts_started` 先加一，隨後 `run_one()` 的 `_validate_scenario()` 直接回傳儀器例外，完全未呼叫模型；在 `--runs 2 --max-attempts 1` 下，第二場卻因額度耗盡令整批 fatal。這是保守誤擋，但與旗標說明的「最多啟動幾次模型」不符。應把計數移到驗證通過後、真正呼叫模型的邊界。

候選升格、父程序中斷、精確題號、逐列 schema、逐題缺場與歷史 meta 已讀，無其他 correctness finding。

總結最嚴重 severity: major；blocking 1 條。
