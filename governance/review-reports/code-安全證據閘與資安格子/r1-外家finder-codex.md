severity: major

1. 核可鏈全部到期後，既有信任根可被整條替換
severity: major
blocking: 是

受影響：`scripts/lumos:9329`。

引句:「if any(e["status"] == "ok" for e in main_chk["entries"]):」

主線曾有合法 `approvers_init`，但所有核可都到期時，這裡把它誤認成「從未建立有效金鑰」，允許推送版刪除整條鏈。接著可以重新自簽 `approvers_init`，不必由原登記金鑰核可。這破壞主線鏈只能追加的保護；到期應取消授權效力，不應清除既有信任歷史。

最小重現（在 repo 執行；只在記憶體載入。驗章函式固定成功，隔離驗證前綴與到期邏輯，未實跑 SSH）：

```sh
python3.14 -B -c 'import runpy,datetime
m=runpy.run_path("scripts/lumos",run_name="seat_review")
f=m["_secapr_verify"]
f.__globals__["_secapr_verify_sig"]=lambda *a:True
keys=["owner ssh-ed25519 AAAA"]
e={"seq":1,"prev_sha256":"","project_id":"p","type":"approvers_init","target":"approvers","content_sha256":m["_secev_sha"](m["_secev_canon"](keys)),"approved_on":"2026-01-01","expires_on":"2026-01-31","signer":"owner","signature":"unit-test","keys":keys}
raw=m["_secev_canon"](e)+b"\n"
for day in ("2026-01-31","2026-02-01"):
 r=f(b"",raw,"p",datetime.date.fromisoformat(day))
 print(day,"diverged:",r["diverged"])
assert f(b"",raw,"p",datetime.date(2026,2,1))["diverged"], "expired mainline chain must remain append-only"'
```

實際輸出：

```text
2026-01-31 diverged: True
2026-02-01 diverged: False
AssertionError: expired mainline chain must remain append-only
```

2. 工具改名即可繞過請求數下限的放寬核可
severity: major
blocking: 是

受影響：`scripts/lumos:10313`、`scripts/lumos:10344`。

引句:「return [] if mt["category"] in cats_push else ["刪掉某工具類別的最後一個工具"]」

主線登記 `k6`、下限 1,000 次；推送版把它改名為 `k6-new`、下限改成 1 次。比較以工具名稱配對，舊名稱消失時只確認同類別仍有工具，因此不列變弱、不要求 `tool_list_change`。同一份只有 1 次請求的報告便由拒收變成合格。重新收證時保留相同 targets、更新 observed_at，也符合既有證據替換條件。

最小重現（只讀載入、記憶體執行）：

```sh
python3.14 -B -c 'import runpy,json
from types import SimpleNamespace
m=runpy.run_path("scripts/lumos",run_name="seat_review")
old={"name":"k6","category":"load_test","version":"2.3.0","allowed_targets":["localhost"],"min_requests":{"load.js":1000}}
new=dict(old,name="k6-new",min_requests={"load.js":1})
ctx=SimpleNamespace(approved=lambda *a:False,read=lambda p:(b"script",None))
tools,notes=m["_secev_tool_freeze"]({"k6-new":new},{"k6":old},ctx)
it={"targets":{"tests":["load.js"],"legit_controls":["legit"],"thresholds":["foreign count == 0"]}}
raw=json.dumps({"metadata":{"k6_version":"2.3.0"},"config":{"script":"script"},"results":{"metrics":[{"name":n,"values":{"count":v}} for n,v in (("iterations",1),("http_reqs",1),("legit",1),("foreign",0))]}}).encode()
print("old:",m["_secev_judge_k6"](it,raw,ctx,old))
result=m["_secev_judge_k6"](it,raw,ctx,tools["k6-new"])
print("renamed:",result,"freeze notes:",notes)
assert "k6_requests_below_floor" in result, "unapproved rename bypasses request floor"'
```

實際輸出：

```text
old: ['k6_requests_below_floor']
renamed: [] freeze notes: []
AssertionError: unapproved rename bypasses request floor
```

最嚴重 severity: major，blocking 共 2 條。


