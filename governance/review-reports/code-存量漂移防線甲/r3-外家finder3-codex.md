severity: major

## F1 改名對照讀取失敗未回判不了，c1 轉正事件會漏擋
severity: major
blocking: 是 — block 模式會把本應 fail-closed 的 `pending→pass` 判成沒有翻轉，讓殘留預告句通過推送閘。
引句:「        if rn is not None:」
file: `scripts/lumos:24564`
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:132`

1. 輸入：守衛紀錄在起點叫 `Old.md`、狀態為 `pending`；範圍內改名成 `New.md` 並轉成 `pass`，但仍留著 c1 預告句；改名對照的 `git diff --name-status` 讀取失敗。

2. `_note_base_status` 遇到改名對照失敗仍沿用終點路徑，讀取 `BASE:New.md` 得到不存在，於是狀態序列變成 `[None, "pass"]`。`_notes_status_flipped` 只認 `pending→pass`，回傳空清單而非判不了；`_drift_check_core` 因此丟掉已存在的 c1，`must=[]`、`unknown=[]`。

3. 最小重現：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import types,pathlib; m=types.ModuleType("lumos"); m.__dict__.update(__file__=str(pathlib.Path("scripts/lumos").resolve()),__name__="lumos"); exec(compile(pathlib.Path("scripts/lumos").read_text(),"scripts/lumos","exec"),m.__dict__); sha="a"*40; rel="Verification/G.md"; p="docs/kg-knowledge/"+rel; b=("---\ntype: verification\nstatus: pass\nguards:\n  - Systems/H\nsummary: |-\n  TEST:還沒有測試在守這條\n---\n").encode(); e=m.Env.from_texts(pathlib.Path("docs/kg-knowledge"),{rel:b.decode()}); m._drift_tree_env=lambda *a,**k:e; m._nodehome_reader=lambda *a:(lambda q:b if q==p else None); m._ns_git=lambda root,*a: ((p+"\0").encode() if a[:2]==("diff","--name-only") or a[:2]==("log","--format=") else (sha+"\0\n"+p+"\0").encode() if "--follow" in a else None); m._nodehome_cat_blobs=lambda root,specs,**kw: ([b] if specs[0].startswith(sha) else [None]); must,listed,unknown=m._drift_check_core(".","BASE","TIP","docs/kg-knowledge"); print("tip_c1=",[(f["kind"],f["path"]) for f in m._drift_state_findings(e)]); print("must=",must,"unknown=",unknown)'
```

輸出：

```text
tip_c1= [('c1', 'Verification/G.md')]
must= [] unknown= []
```

4. 改名對照的 git 呼叫回 `None` 時必須向上傳成判不了；不能把「對照讀失敗」折成「起點沒有這篇」。

guard settle 的正式行辨識、重複預告防護與兩步補救：已看,無 finding。

c3／連帶待辦、scan／doctor、status_replay／exam 與新增回歸測試：已看,無其他 finding。

Systems 筆記變更：已看,無 finding。

最嚴重等級 major，blocking 共 1 條。