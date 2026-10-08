# 回顧分類受控查證

合成三輪與報告，直接載入既有helper；不是實際人裁、不是完整retro CLI通過。臨時資料自行清除。driver SHA256 a06b8a8667ef2fd0d8f28a1c5122562d47e3e430a2f71be3dad1b4684e6d3655。

```python
import copy, hashlib, json, runpy, tempfile
from pathlib import Path
source=Path("/tmp/lumos-future-repair-regression-research/scripts/lumos")
mod=runpy.run_path(str(source),run_name="retro_family_probe")
report_content="severity: major\n\n新發現：修後輸入失敗；修前未跑，測試來源也未核對。因果未判定。\n"
results=[]
with tempfile.TemporaryDirectory(prefix="lumos-retro-family-") as td:
 root=Path(td); loop="code-fixture"; report="governance/review-reports/code-fixture/r3-seat.md"
 rp=root/report;rp.parent.mkdir(parents=True);rp.write_text(report_content,encoding="utf-8")
 rows=[{"auditor":"original-seat","report_path":report,"round":"r3"}]
 decision={"rounds":["r1","r2","r3"]}
 data={"version":1,"loop":loop,"rounds":decision["rounds"],"drafted_by":"fresh-drafter","completed_by":"orchestrator", "families":[{"family":"fix-induced","rounds":["r3"],"evidence":[report],"note":"只有修後失敗，沒有修前結果，因果未判定"}], "why_cap":"原有案例不足以證明兩版行為與原因，因此此輪需要保留待核對事項", "avoid":"應在原修補之前固定案例與版本證據，再沿需求核對既有路徑是否保留", "changes":[{"target":"dispatch","ref":"existing repair lens","change":"沿原有兩版案例紀錄補待核對材料與未知原因"}]}
 cases=[("unsupported_fix_induced","fix-induced",False),("unknown_as_other","other",False),("new_enum_rejected","attribution-undetermined",True),("same_family_is_not_causality","same-family-unswept",False)]
 for name,family,expect_problem in cases:
  d=copy.deepcopy(data);d["families"][0]["family"]=family
  if family=="other":d["families"][0]["note"]="attribution-undetermined: 缺修前可比案例與實際載入證據，不能歸因修補"
  raw=json.dumps(d,ensure_ascii=False).encode("utf-8")
  probs,parsed=mod["_cap_retro_check"](root,loop,decision,rows,"",raw=raw)
  results.append({"case":name,"input":d,"report_content":report_content,"decision":decision,"rows":rows,"expected_problem":expect_problem,"actual_problems":probs,"accepted_object_returned":parsed is not None,"matched":bool(probs)==expect_problem})
assert all(r["matched"] for r in results)
print(json.dumps({"scope":"actual existing checker helper only; synthetic decisions and reports; no real cap-decision or full CLI pass; acceptance is structural not causal proof", "loaded_source":mod["_cap_retro_check"].__code__.co_filename,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"results":results},ensure_ascii=False,indent=2))
```
