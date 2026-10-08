severity: major

Finding 1：題目超跑或結果檔重複時，M1–M4 仍把多出的列全數納入分子、分母；新逐題 `missing` 只避免超跑遮住缺題，沒有拒絕或裁掉超額樣本。預定「2 題 × 每題 1 次」可得到 `n=3`、M1=`2/3`，使各題權重失衡。

severity: major  
blocking: 是  
引句:「results = [r for r in results if r.get("id") in idset]」  
file: `governance/eval/ablation_lumos_first.py:321`  
具體輸入路徑：臨時輸出目錄內 `with-q-a.json`、`with-q-a-copy.json` 各含同一題 `a` 的通過列，`with-q-b.json` 含題 `b` 的失敗列；`expected_ids=["a","b"]`、`runs=1`。

最小重現：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import importlib.util, json, tempfile
from pathlib import Path
p=Path("governance/eval/ablation_lumos_first.py").resolve()
s=importlib.util.spec_from_file_location("a",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
with tempfile.TemporaryDirectory() as td:
    d=Path(td)
    def batch(rows): return {"arm":"with","results":rows,"fatal":False,"inconclusive":False,"skills_health_bad":[]}
    (d/"with-q-a.json").write_text(json.dumps(batch([{"id":"a","passed":True}])))
    (d/"with-q-a-copy.json").write_text(json.dumps(batch([{"id":"a","passed":True}])))
    (d/"with-q-b.json").write_text(json.dumps(batch([{"id":"b","passed":False}])))
    x=m.merge(d,["a","b"],1)["arms"]["with"]
    print(x["n"],x["m1_passed"],x["m1_rate"],x["missing"])
PY
```

觀測：`3 2 0.6667 0`；報表宣稱每題一次，但重複的 `a` 得到雙倍權重。M2、M3、M4 同樣由未裁切的 `valid` 衍生。

Finding 2：五小時額度只掃目前輸出目錄中已升格的正式 JSON。失敗候選已消耗的模型呼叫完全不計；依 marker 指示歸檔事故檔後，額度仍是零。跨午夜切換預設日期目錄或改用另一個 `--out-dir` 也會立刻清空窗口帳。

severity: major  
blocking: 是  
引句:「n += sum(1 + len(r.get("retry_attempts", [])) for r in rows if isinstance(r, dict))」  
file: `governance/eval/ablation_lumos_first.py:218`  
file: `governance/eval/ablation_lumos_first.py:512`  
具體輸入路徑：`with-q-failed.candidate` 含最後嘗試及兩次重試，對應正式 `with-q-failed.json` 是空列 fatal tombstone；另一案例把三次用量放在前一日期目錄，當前日期目錄為空。

最小重現：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import importlib.util, json, tempfile, time
from pathlib import Path
p=Path("governance/eval/ablation_lumos_first.py").resolve()
s=importlib.util.spec_from_file_location("a",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
with tempfile.TemporaryDirectory() as td:
    d=Path(td)
    tomb={"arm":"with","results":[],"fatal":True,"inconclusive":True,"skills_health_bad":[]}
    used={"arm":"with","results":[{"id":"a","passed":False,"limit_hit":True,
          "retry_attempts":[{},{}]}],"fatal":True,"inconclusive":True,"skills_health_bad":[]}
    (d/"with-q-failed.json").write_text(json.dumps(tomb))
    (d/"with-q-failed.candidate").write_text(json.dumps(used))
    (d/"with-q-failed.pending").write_text(json.dumps(tomb))
    print("before",m.runs_in_window(d,now=time.time()))
    for p in list(d.iterdir()): p.rename(p.with_name(p.name+".archived"))
    print("after",m.runs_in_window(d,now=time.time()),m.collect_skills_health(d))
PY
```

觀測：`before 0`、`after 0 []`。三次實際模型呼叫未進窗口帳，歸檔後下批可以取得完整新額度，違反 S18 的「實際呼叫消耗額度」。

Finding 3：無關 JSON 的排除規則仍以過寬的 `with-`／`without-` 前綴判斷。`with-notes.json` 會被當正式探針結果並使整批不可採信，違反 S17。

severity: major  
blocking: 是  
引句:「if p.name.startswith(("with-", "without-"))」  
file: `governance/eval/ablation_lumos_first.py:157`  
具體輸入路徑：輸出目錄旁註檔 `with-notes.json`，內容 `{"memo":"operator note"}`。

最小重現：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import importlib.util, json, tempfile
from pathlib import Path
p=Path("governance/eval/ablation_lumos_first.py").resolve()
s=importlib.util.spec_from_file_location("a",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
with tempfile.TemporaryDirectory() as td:
    d=Path(td); (d/"with-notes.json").write_text(json.dumps({"memo":"operator note"}))
    print([p.name for p in m._result_json_files(d)])
    print(m.collect_skills_health(d))
PY
```

觀測：檔案清單含 `with-notes.json`，健康掃描回報「結果檔缺少逐場資料」，純合併與 live 派工都會被阻擋。

歷史 meta：已讀，無 finding。  
錯型欄位、非物件列與逐題缺場基本拒收：已讀；除 Finding 1 的超額列問題外，無其他 finding。

總結：最嚴重 severity=major；blocking=3 條。
