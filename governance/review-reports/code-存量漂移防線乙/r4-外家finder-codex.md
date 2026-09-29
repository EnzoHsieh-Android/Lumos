severity: major

## F1 邏輯行計數把大量註解累積成深運算式，進而誤認 docstring 內的定義

severity: major

blocking: 是 — Python 3.9 會把合法檔案中的範例函式判成真實 symbol，導致 drift check 錯擋。

引句:「+            run = 0 if t.type == _tok.NEWLINE else run + 1」

file: `scripts/lumos:25905`

1. `tokenize` 對註解／空白行產生 `COMMENT`、`NL`，不是 `NEWLINE`；目前兩者都讓 `run` 持續累加。超過 20,000 後 `_drift_py_names` 放棄 AST，退回會掃到三引號字串的正則。

2. 輸入為 20,001 行註解，加上一段包含 `def phantom()` 的 docstring。AST 明確認為沒有此函式，drift 卻回傳存在。若該範例在這次推送新增，block 模式會把條件誤判為剛成立。

3. 最小重現：

   `/usr/bin/python3 -c 'import ast,runpy; m=runpy.run_path("scripts/lumos",run_name="review_probe"); txt=("# padding line\n"*20001)+"\"\"\"\ndef phantom():\n    pass\n\"\"\"\n"; tr=m["_DriftProbeTree"](".","deadbeef",{"big.py"},({},{})); tr._text["big.py"]=txt; ast_has=any(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="phantom" for n in ast.walk(ast.parse(txt))); got=tr.one("symbol","phantom"); print("ast_has_phantom={} drift_symbol_phantom={}".format(ast_has,got)); assert got is False'`

   輸出：`rc=1`，`ast_has_phantom=False drift_symbol_phantom=True`，接著 `AssertionError`。

## F2 SHA-256 提交不會填內容編號，怪檔名修補在該類 repo 失效

severity: major

blocking: 是 — 工具接受 64 碼提交，但 drift 只替 40 碼提交建立 OID cache，最終退回已知會讀錯怪檔名的 `版本:路徑`。

引句:「if not (isinstance(where, str) and re.fullmatch(r"[0-9a-f]{40}", where)):」

file: `scripts/lumos:25942`

file: `scripts/lumos:31276`

1. `_lens_full_sha` 明確認得 40、64 碼 SHA；但 64 碼值在 `_drift_list` 直接走 `_nodehome_list(root, where)`，沒有傳入 `oids`。

2. `_drift_oids` 因此固定得到空 dict，`_drift_cat` 對 NFD／混合正規化／相容表意字／換行檔名退回 `64碼SHA:正規化路徑`。這正是本次改用內容編號要消除的失敗形狀，會令 check 判不了並阻擋。

3. 最小重現：

   `/opt/homebrew/bin/python3 -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="review_probe"); g=m["_drift_oids"].__globals__; calls=[]; fake=lambda root,where,oids=None: (calls.append((len(where),oids is not None)), oids.update({"café.py":"b"*len(where)}) if oids is not None else None, ({"café.py":"100644"},["café.py"]))[-1]; g["_nodehome_list"]=fake; g["_DRIFT_LS_CACHE"].clear(); g["_DRIFT_OID_CACHE"].clear(); one=g["_drift_oids"]("/repo","a"*40); two=g["_drift_oids"]("/repo","a"*64); print("sha1_has_oid={} sha256_has_oid={} calls={}".format(bool(one),bool(two),calls)); assert two'`

   輸出：`rc=1`，`sha1_has_oid=True sha256_has_oid=False calls=[(40, True), (64, False)]`，接著 `AssertionError`。

## F3 一支改動檔讀不到時，另一支已確定命中仍被候選層降成判不了

severity: major

blocking: 是 — 已能確定名稱受這次推送影響，候選層仍回傳 unknown，block 模式會錯擋。

引句:「+            if not self._read(list(key)) or any(self._text[p] is None for p in key):」

file: `scripts/lumos:26041`

file: `scripts/lumos:26256`

1. 輸入為兩支 `M` 狀態的程式檔：`good.py` 可讀且定義 `target`，`bad.py` 讀不到；圖譜已有不帶路徑的 `[when-symbol:target]`。

2. `names_in` 因任一檔是 `None` 就丟掉 `good.py` 的確定命中，候選結果變成 `None`。同一棵樹的正式條件判定 `one("symbol", "target")` 卻是 `True`；這也違反新增 F2 測試宣告的「找到定義照成立，找不到才判不了」。

3. 最小重現：

   `/opt/homebrew/bin/python3 -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="review_probe"); t=m["_DriftProbeTree"](".","tip",{"good.py","bad.py"},({},{})); t._text={"good.py":"def target():\n    pass\n","bad.py":None}; ch={"touched":{"good.py","bad.py"},"renames":{},"code_shape":False,"code_touched":["good.py","bad.py"]}; cand=m["_drift_probe_is_candidate"]([("symbol","target")],ch,"docs/kg-knowledge/",None,lambda:t.names_in(ch["code_touched"])); tip=t.one("symbol","target"); print("candidate={} tip_condition={} bad_paths={}".format(cand,tip,t.bad_paths())); assert cand is True'`

   輸出：`rc=1`，`candidate=None tip_condition=True bad_paths=['bad.py']`，接著 `AssertionError`。

圖譜同步、`_NotelinesNet` 即時失敗、解析 bad 旗標、版面比較、scan budget、shebang 搬移及其餘測試 hunk：已看，無 finding。

最嚴重等級 major，blocking 共 3 條。