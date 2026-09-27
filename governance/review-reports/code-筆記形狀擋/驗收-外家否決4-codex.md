severity: major

## F1 上線點過濾沒有套到喚醒路徑，舊分支仍會被誤擋
severity: major
blocking: 是 —— 會把上線前分支的舊帳判成新違規，直接擋住推送

引句:「★上線點不是祖先的提交不查★(golive):上線前開的分支上線後才合進來,那些提交寫的時候還沒有這道檢查,是舊帳」

具體輸入：分支在 note-shape 上線前分出，於該分支同時新增 `src/new.py` 與引用它的筆記行 ``src/new.py:2``，上線後才合回主線。

`_ns_range_added` 會正確排除不以 golive 為祖先的側分支提交；合併提交又因該筆記行已存在於側分支 parent，不算合併新寫，所以第一條檢查沒有違規。但接著 `_note_shape_eval` 直接以 `base_where..tip_where` 呼叫 `_ns_became_code`，沒有套同一個 golive ancestry 過濾；它仍把 `src/new.py` 判成新程式檔，再由喚醒路徑把同一筆舊帳擋下。file: `scripts/lumos:23817`

最小重現；stub 固定的是上述 Git 層已算出的結果：新增行集合為空、但 became-code 仍含新檔，其餘走真實 `_note_shape_eval`：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -c $'import runpy
g=runpy.run_path("scripts/lumos",run_name="review"); f=g["_note_shape_eval"]; h=f.__globals__
n=b"---\\ntype: system\\n---\\n# Old\\nsee `src/new.py:2`\\n"; fs={"docs/kg-knowledge/Systems/Old.md":"100644","src/new.py":"100644"}
h["_nodehome_reader"]=lambda r,w:(lambda p:None) if w=="GL" else (lambda p:n if p.endswith("Old.md") else b"x=1\\ny=2\\n")
h["_nodehome_list"]=lambda r,w:(fs,list(fs)); h["_ns_range_added"]=lambda *a,**k:({},["docs/kg-knowledge/Systems/Old.md"]); h["_ns_became_code"]=lambda *a,**k:["src/new.py"]; h["_nodehome_golive"]=lambda *a,**k:"GL"; h["_nodehome_cat_blobs"]=lambda *a,**k:[n]
print([(p,i,r,x) for p,i,r,x,_ in f("R",False,"BASE","TIP","docs/kg-knowledge")[0]])'
```

輸出：

```text
[('docs/kg-knowledge/Systems/Old.md', 5, '程式行號引用(新程式檔喚醒)', '`src/new.py:2`')]
```

喚醒所用的 became-code 集合也必須排除 golive 不是其祖先的提交，或直接以相同的逐提交有效範圍計算。

## F2 歷史檔所在頂層目錄已刪除時，refcheck 會靜默丟掉釘版本
severity: major
blocking: 是 —— 會讓超出歷史檔長度的引用以零 claims 通過既有 G1/refcheck 閘

引句:「exists=lambda p_, s_=None: (repo_root / p_).exists() or _path_at_pin(repo_root, p_, s_)」

`_path_at_pin` 已能證明歷史提交裡存在 `src/Foo.cs`，但抽取器切出 pin 後仍以「目前工作樹的頂層目錄」過濾 token。當整個 `src/` 已刪除，`src` 不在 `top_dirs`，程式便在 `scripts/lumos:19922` 靜默 `continue`，沒有把引用加入 `pins`。因此行號 2 明明超出該歷史檔唯一的一行，`_refcheck_scan` 卻回傳零 claims、零錯誤；`cmd_refcheck` 隨後會由 `scripts/lumos:26682` 回傳成功。

最小重現使用 repo 內實際仍受遠端追蹤分支包含的提交 `e493ca0de45e…`；該提交有一行的 `src/Foo.cs`，目前工作樹已沒有 `src/`：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import runpy,pathlib; g=runpy.run_path("scripts/lumos",run_name="review"); r=pathlib.Path("."); p="e493ca0de45e"; print("path_at_pin=",g["_path_at_pin"](r,"src/Foo.cs",p)); print("refcheck=",g["_refcheck_scan"](f"見 `src/Foo.cs@{p}:2`",r))'
```

輸出：

```text
path_at_pin= True
refcheck= ([], 0, 0, 0)
```

已由歷史 pin 證實存在的路徑不能再受目前 `top_dirs` 過濾；否則這次新增的「已刪檔歷史釘版本」支援只在頂層目錄仍存活時有效。

總結:最高 severity major；blocking 2 條。