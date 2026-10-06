# 同類提醒受控查證

直接載入既有CLI的實際helper；只驗repeat提醒，不表示完整fix-check通過，虛構fixture的版本與路徑不是產品缺陷證據。臨時紀錄自行清除。

```python
import copy, hashlib, json, runpy, tempfile
from pathlib import Path
repo = Path("/tmp/lumos-future-repair-regression-research")
source = repo / "scripts/lumos"
mod = runpy.run_path(str(source), run_name="category_probe")
fn = mod["_fix_item_repeat"]
previous = {"base": "0"*40, "groups": [{"id": "old-reader", "category": "boundary", "findings": ["old-F1"], "paths": [{"at": "old.py:read", "status": "fixed", "tests": ["t_old"]}]}]}
current = {"base": "1"*40, "groups": [{"id": "new-parser", "category": "boundary", "findings": ["new-F1"], "paths": [{"at": "new.py:parse", "status": "fixed", "tests": ["t_new"]}]}]}
cases = [
 ("different_ids_paths_same_category", {}, True),
 ("same_identity_same_category", {"identity": True}, True),
 ("different_category", {"category": "concurrency"}, False),
 ("other_category", {"category": "other"}, False),
 ("minor_only", {"severity": "minor"}, False),
 ("honest_different_root_prior", {"prior": {"why_failed": "上一輪修的是讀取邊界，此輪為解析錯誤，只有類別相同，根因關係未判定", "new_approach": "依此輪實際解析案例補斷言並查共用出口，仍保留原先讀取案例"}}, False),
 ("unknown_relationship_prior", {"prior": {"why_failed": "現有證據不能確認此輪與上一輪同根因，不宣稱前次修補失敗，待核對固定兩版案例", "new_approach": "固定兩版與同一案例先確認區間結果，再補具體失敗路徑與保留案例"}}, False),
]
results=[]
with tempfile.TemporaryDirectory(prefix="lumos-category-probe-") as td:
 root=Path(td); record=mod["_fix_record_path"](root,"code-probe","r1")
 record.parent.mkdir(parents=True); record.write_text(json.dumps(previous),encoding="utf-8")
 for name, change, expected in cases:
  rec=copy.deepcopy(current); g=rec["groups"][0]
  if change.get("identity"):
   g.update(id="old-reader", findings=["old-F1"], paths=copy.deepcopy(previous["groups"][0]["paths"]))
  if "category" in change: g["category"]=change["category"]
  if "prior" in change: g["prior"]=change["prior"]
  severity=change.get("severity","major")
  groups={"r1":[{"severity":"major"}],"r2":[{"severity":severity}]}
  carrier={"finding_severities":{g["findings"][0]:severity}}
  actual=fn(None,root,[{"loop":"code-probe"}],groups,"r2",rec,carrier)
  results.append({"case":name,"previous":previous,"current":rec,"rows":[{"loop":"code-probe"}],"round_groups":groups,"carrier":carrier,"expected_repeat_problem":expected,"actual_problems":actual,"matched":bool(actual)==expected})
assert all(r["matched"] for r in results)
output={"scope":"actual _fix_item_repeat helper only; no full fix-check or causal proof", "loaded_function_file":fn.__code__.co_filename,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"results":results}
print(json.dumps(output,ensure_ascii=False,indent=2))
```
