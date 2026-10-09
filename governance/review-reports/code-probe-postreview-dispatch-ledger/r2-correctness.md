severity: major

finding C1: `reason` 漏驗型別，畸形儀器例外可被當成成功樣本計入 M1
severity: major
blocking: 是
引句:「or (row.get("answer") is not None and not isinstance(row["answer"], str))」
file: `governance/eval/ablation_lumos_first.py:133`
最小重現:
```bash
python3.14 - <<'PY'
import importlib.util
from pathlib import Path
p=Path("governance/eval/ablation_lumos_first.py").resolve()
s=importlib.util.spec_from_file_location("a",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
r={"id":"a","passed":True,"reason":["儀器例外: timeout"],"calls":[],"n_calls":0}
d={"arm":"with","results":[r],"fatal":False,"inconclusive":False,"skills_health_bad":[]}
print(m.invalid_batch_evidence(d,"with"))
r=m.backfill_limit(r)
print(m.is_valid(r), m._arm_stats([r],["a"],1)["m1_passed"])
PY
```
實際輸出 `[]`、`True 1`；列表型 `reason` 避開 `startswith("儀器例外")`，S13 的錯型拒收仍未封閉。

finding C2: falsey 錯型 `skills_health_bad` 在純合併路徑被當成健康，舊檔可抵掉缺場
severity: major
blocking: 是
引句:「bad = d.get("skills_health_bad")」
file: `governance/eval/ablation_lumos_first.py:111`
最小重現:
```bash
python3.14 - <<'PY'
import importlib.util,json,tempfile
from pathlib import Path
p=Path("governance/eval/ablation_lumos_first.py").resolve()
s=importlib.util.spec_from_file_location("a",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
d={"arm":"with","results":[{"id":"a","passed":True,"reason":"ok"}],
   "fatal":False,"inconclusive":False,"skills_health_bad":""}
with tempfile.TemporaryDirectory() as td:
    Path(td,"with-q-bad.json").write_text(json.dumps(d))
    print(m.collect_skills_health(td))
    rows=m.load_results(td)["with"]
    print(len(rows),m.needed({"with":rows},"with","a",1))
PY
```
實際輸出 `[]`、`1 0`。live 路徑另有精確 `list` 檢查，merge-only 卻只看 truthiness，造成舊新互讀判準分裂。

finding C3: 空白題號未被拒絕，仍可進入精確選題並啟動模型
severity: major
blocking: 是
引句:「if (not isinstance(qid, str) or not qid or "," in qid」
file: `governance/eval/ablation_lumos_first.py:68`
最小重現:
```bash
q=$(mktemp)
printf '{"id":"   ","prompt":"x","expect":["x"]}\n' > "$q"
python3.14 scripts/scenario_probe.py --scenarios "$q" --exact-id '   ' --dry-list
printf 'rc=%s\n' "$?"
```
實際印出空白題號且 `rc=0`；正式執行時 `_validate_scenario` 也以 truthiness 驗證，會燒模型配額並把視覺上無題號的列納入計分，違反 S12 的空白題號前置拒絕。

S11 未完成標記、父死子活與異常回傳碼：已讀,無 finding  
S14 純合併保留來源 meta：已讀,無 finding  
新增父死子活與歸檔注入測試：已讀,無 finding

總結：最嚴重 severity: major；blocking: 3 條。
