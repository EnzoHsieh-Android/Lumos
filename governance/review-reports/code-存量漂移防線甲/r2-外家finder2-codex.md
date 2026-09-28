severity: major

## F1 批次讀取失敗被當成「沒有狀態翻轉」

severity: major  
blocking: 是 — git 讀取失敗時，drift check 與筆記內容審都會把應判不了的事件當成沒有事件而放行。  
引句:「states = [_note_audit_status_of(b)[1] for b in (blobs or [])]」  
file: `scripts/lumos:24519`

1. `_nodehome_cat_blobs` 以 `None` 表示失敗；新拆出的 `_note_status_seq` 卻用 `(blobs or [])` 把它轉成空序列，最後回傳 `[base_state]`，沒有依函式契約回 `None`。
2. `_notes_status_flipped` 因此得到空結果：守衛的 `pending→pass` 不進 `passed`，c1 不擋；計劃收尾也不進筆記內容完成審。
3. 最小重現：

```sh
python3 -c 'import runpy;m=runpy.run_path("scripts/lumos",run_name="lumos");f=m["_notes_status_flipped"];g=f.__globals__;p="docs/kg-knowledge/Verification/G.md";a="a"*40;b="b"*40;pending=b"---\ntype: verification\nstatus: pending\nguards: H\n---\n";passed=pending.replace(b"pending",b"pass");g["_ns_git"]=lambda root,*args:((a+"\0\n"+p+"\0"+b+"\0\n"+p+"\0").encode() if "--follow" in args else (p+"\0").encode());kw=(".",None,"tip","docs/kg-knowledge",lambda q:passed,lambda t,s:t=="verification" and s=="pass",lambda x,y:x=="pending" and y=="pass");g["_nodehome_cat_blobs"]=lambda root,specs,**k:[passed,pending];print("batch_ok =",f(*kw,only={p}));g["_nodehome_cat_blobs"]=lambda *a,**k:None;print("batch_git_failure =",f(*kw,only={p}))'
```

輸出：

```text
batch_ok = ['docs/kg-knowledge/Verification/G.md']
batch_git_failure = []
```

## F2 狀態歷史讀取沒有接上剩餘預算

severity: major  
blocking: 是 — 一個候選可連續跑兩次 60 秒批次讀取，推送閘承諾的 60 秒總預算失效。  
引句:「blobs = _nodehome_cat_blobs(repo_root, specs) if specs else []」  
file: `scripts/lumos:24518`

1. `_nodehome_cat_blobs` 新增了 `timeout` 參數，但 `_note_status_seq` 的歷史與 base 兩次呼叫都沒傳它，也沒收到 `_notes_status_flipped` 的 `deadline`。
2. 兩次呼叫各沿用預設 60 秒；第一批逾時後仍會繼續讀 base。這也放大 F1：逾時最多拖到約 120 秒，最後仍能被當成沒有翻轉。
3. 最小重現：

```sh
python3 -c 'import runpy,inspect;m=runpy.run_path("scripts/lumos",run_name="lumos");f=m["_note_status_seq"];g=f.__globals__;default=inspect.signature(m["_nodehome_cat_blobs"]).parameters["timeout"].default;p="docs/kg-knowledge/Verification/G.md";a="a"*40;g["_ns_git"]=lambda root,*args:((a+"\0\n"+p+"\0").encode() if "--follow" in args else b"");calls=[];blob=b"---\ntype: verification\nstatus: pass\n---\n";g["_nodehome_cat_blobs"]=lambda root,specs,**kw:(calls.append(kw) or [blob for _ in specs]);f(".","BASE","TIP","docs/kg-knowledge",p);print("cat_file_default =",default);print("timeouts_forwarded =",calls)'
```

輸出：

```text
cat_file_default = 60
timeouts_forwarded = [{}, {}]
```

## F3 已有正式合約但測試名不同時 settle 會寫出重複合約

severity: major  
blocking: 是 — `guard settle` 成功後，家筆記會留下兩條文字相同、測試不同的正式合約行。  
引句:「if _guard_formal_line(hlines, he, claim, method) is not None:」  
file: `scripts/lumos:11995`

1. 新增的「正式行與預告行並存時只刪預告」分支要求正式行含本次 `--test` 方法。
2. 若原有正式行是 `[test:t_old]`，本次 settle 使用 `t_new`，比對回 `None`，程式走一般替換路徑，把預告行改成第二條 `[test:t_new]` 正式合約。
3. 最小重現：

```sh
python3 -c 'import runpy,pathlib,types;m=runpy.run_path("scripts/lumos",run_name="lumos");f=m["_guard_settle_home"];g=f.__globals__;c="大額退費要人工核可";ls=["---","summary: |-",f"  KEY:★INVARIANT★ {c} [test:t_old]",f"  KEY:★INVARIANT-PLANNED★ {c} [watch:Verification/G] [due:2099-12-31]","---"];cap={};g["load_raw_for_edit"]=lambda p:(ls,1,4);g["_guard_planned_line"]=lambda e,r,c:(ls,3,4,None);g["atomic_write_verify"]=lambda p,new,key,check:cap.setdefault("lines",new);print("settle_ok =",f(types.SimpleNamespace(vault=pathlib.Path(".")),"Systems/H.md",c,"t_new"));print("formal_claim_count =",sum("KEY:★INVARIANT★ "+c in x for x in cap["lines"]));print("\n".join(cap["lines"][2:4]))'
```

輸出：

```text
settle_ok = True
formal_claim_count = 2
  KEY:★INVARIANT★ 大額退費要人工核可 [test:t_old]
  KEY:★INVARIANT★ 大額退費要人工核可 [test:t_new]
```

## F4 status_replay 仍用失效提交而非上一版的圖譜位置

severity: major  
blocking: 是 — 圖譜資料夾在失效提交改名時，考試會把本來能點到的題判成漏。  
引句:「fu = _drift_exam_replay(root, par, vault_rel, q.get("status_targets") or [])」  
file: `scripts/lumos:25772`

1. `_drift_exam_one` 先把 `vault_rel` 改成失效提交 `c` 的圖譜位置，再把同一位置交給 `_drift_exam_replay` 讀父提交 `par`。
2. 若提交把 `docs/old-knowledge` 改成 `docs/new-knowledge`，父提交在新路徑下會被讀成空 Env，而不是失敗；所有 `status_targets` 都消失，題目回「漏」。
3. 最小重現：

```sh
python3 -c 'import runpy,pathlib;m=runpy.run_path("scripts/lumos",run_name="lumos");f=m["_drift_exam_one"];g=f.__globals__;plan="---\ntype: project\nstatus: doing\n---\n# P\n[[Issues/I]]\n";issue="---\ntype: issue\nstatus: open\n---\n# I\n";base={"Projects/P.md":plan,"Issues/I.md":issue};g["_lens_full_sha"]=lambda root,ref:{"x":"C","x^":"P"}.get(ref);g["_drift_vault_rel"]=lambda root,w:"docs/new-knowledge" if w=="C" else "docs/old-knowledge";g["_drift_check_core"]=lambda *a,**k:([],[],[]);g["_drift_tree_env"]=lambda root,w,v,override=None,timeout=60:m["Env"].from_texts(pathlib.Path(v),({**base,**(override or {})} if w=="P" and v=="docs/old-knowledge" else {**(override or {})}));q={"exam_event":"status_replay","note":"Issues/I.md","line":3,"invalidating_commits":["x"],"status_targets":["Projects/P"]};print("exam_one =",f(pathlib.Path("."),"docs/current-knowledge",q,"HEAD")[0]);print("parent_own_vault =",m["_drift_exam_replay"](pathlib.Path("."),"P","docs/old-knowledge",q["status_targets"]))'
```

輸出：

```text
exam_one = 漏
parent_own_vault = {'Issues/I.md'}
```

## F5 scan 仍把解不開的筆記報成零發現

severity: major  
blocking: 是 — 修復清單會漏掉無法解碼的筆記，與「判不了要列出」的規格相反。  
引句:「left, done = _drift_split_acked(_drift_state_findings(tenv), _drift_load_acks(root, sha), vault_rel)」  
file: `scripts/lumos:25667`

1. `_drift_tree_env` 已把非 UTF-8 路徑記進 `env.undecodable`，但 `cmd_drift_scan` 只取 `_drift_state_findings`，完全不消費該清單。
2. 同一個無法解碼案例在 check 會成為「判不了」，在 scan 卻回 0 並印 c1–c5 全零；也沒有規格要求的 degraded 結果。
3. 最小重現：

```sh
python3 -c 'import runpy,pathlib,contextlib,io;m=runpy.run_path("scripts/lumos",run_name="lumos");f=m["cmd_drift_scan"];g=f.__globals__;e=m["Env"].from_texts(pathlib.Path("docs/kg-knowledge"),{});e.undecodable=["Verification/G.md"];g["_drift_vault_of"]=lambda env:(pathlib.Path("."),"docs/current-knowledge");g["_lens_full_sha"]=lambda *a:"C";g["_drift_vault_rel"]=lambda *a:"docs/kg-knowledge";g["_drift_tree_env"]=lambda *a,**k:e;g["_drift_load_acks"]=lambda *a,**k:[];o=io.StringIO();exec("with contextlib.redirect_stdout(o):\n rc=f(e,at=\"C\")");print("rc =",rc);print(o.getvalue().strip())'
```

輸出：

```text
rc = 0
存量漂移健檢(C):c1 0、c2 0、c3 0、c4 0、c5 0
```

## F6 同一計劃的兩種合法連結寫法會讓 c3 消失

severity: minor  
blocking: 否 — c3 與 `lumos set` 的連帶待辦只列出不擋，但合法資料會被漏報。  
引句:「if len(plans) != len({link_target(x) for x in refs}):」  
file: `scripts/lumos:25217`

1. 輸入 `plan_refs: [[Projects/P]], [[P]]`；兩項都明確解到唯一的 `Projects/P.md`。
2. typed index 得到兩次同一 target，程式先 `set` 成一個 plan，卻拿它跟兩個不同字面 target 比數量，回 `None`。
3. 重現結果：

```text
typed_targets = ['Projects/P.md', 'Projects/P.md']
c3 = None
```

## F7 同名猜不準分支重新把守衛紀錄列進連帶待辦

severity: minor  
blocking: 否 — 收尾計劃時會列出規格明確排除的 pending 守衛紀錄。  
引句:「and _drift_str(env.notes.get(src), "status") == "pending":」  
file: `scripts/lumos:25330`

1. 一篇 pending verification 同時有 `guards` 鍵與含糊的 `plan_refs: [[P]]`，而圖譜裡有兩篇同名 P。
2. 正常 c3 路徑會以「有 guards 鍵」排除；新增的 ambiguous 路徑只檢查 type/status，直接追加。
3. `_drift_plan_followups(..., "Projects/P.md", "done")` 實際輸出：

```text
[('驗證紀錄', 'Verification/G.md', 'plan_refs 寫 [[P]] 同名猜不準(可能指這份計劃),看一下')]
```

已看,無 finding：lint waiver 與 Systems 筆記更新、`Env.from_texts` 排序、欄位實際文字與 c4 行定位、表態寫入鎖與舊理由過濾、doctor 閘提醒、移除 `--probes`、rtb 指定考卷結果。

最嚴重等級 major，blocking 共 5 條。