severity: major

## F1 SHA-256 首推仍使用 SHA-1 空樹

severity: major

blocking: 是 — 無主線與上線標記時，SHA-256 repo 會把不存在的 SHA-1 空樹交給 `git diff`，最後以判不了硬擋。

引句:「if not (isinstance(where, str) and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", where)):」

1. 這份修正只讓快取接受 64 碼提交；共用 `_EMPTY_TREE_SHA` 仍固定為 40 碼 SHA-1。SHA-256 repo 首推且找不到主線時，`_lens_push_base` 回傳此常數，之後 `_drift_probe_changes` 用它作為 diff 起點。

file: `scripts/lumos:31971`

file: `scripts/lumos:33775`

file: `scripts/lumos:26735`

2. SHA-256 的空樹是 `sha256(b"tree 0\0")`，不是現有常數。Git 找不到錯誤物件後，條件檢查回判不了；block 模式會錯擋首推。

3. 最小重現：

    ```sh
    /opt/homebrew/bin/python3 -c 'import hashlib,runpy; m=runpy.run_path("scripts/lumos",run_name="review"); f=m["_lens_push_base"]; f.__globals__["_mainline_ref"]=lambda *a,**k:None; base,why=f("/sha256","0"*64,"a"*64); want=hashlib.sha256(b"tree 0\0").hexdigest(); print("resolved_base",base,len(base)); print("sha256_empty",want,len(want)); print("reason",why); assert base==want'
    ```

    輸出：

    ```text
    resolved_base 4b825dc642cb6eb9a060e54bf8d69288fbee4904 40
    sha256_empty 6ef19b41225c5369f1c104d45d8d85efa9b057b53b14b4b9b939dd74decc5321 64
    reason 新分支首推:找不到主線,從空樹算(截到上線點)
    AssertionError
    ```

## F2 含標點的合法名稱仍逐列掃描全文並耗盡閘門預算

severity: major

blocking: 是 — 合法條件耗盡固定 60 秒預算後被改判為判不了，block 模式因此不該擋卻擋。

引句:「return "\n".join(self.texts)」

1. 名稱只有完全符合 `\w+` 才走集合；文法允許的 `missing-1`、`foo-bar` 等名稱會讀取 `names.text`。新增的 property 每次把全文串起來，再跑一次全篇正則。

file: `scripts/lumos:26387`

file: `scripts/lumos:26582`

file: `scripts/lumos:26779`

2. 6 MB 的改動全文配 850 條既有條件時，前 783 條查找花滿 60 秒，剩下 67 條被記為判不了。`cmd_drift_check` 會將這些 unknown 當作阻擋項。

file: `scripts/lumos:26852`

file: `scripts/lumos:27178`

3. 最小重現：

    ```sh
    /opt/homebrew/bin/python3 - <<'PY'
    import runpy, time
    m = runpy.run_path("scripts/lumos", run_name="review")
    f, g = m["_drift_probe_candidates"], m["_drift_probe_candidates"].__globals__
    names = m["_DriftNames"](["x_1 " * 1500000])
    tree = type("T", (), {
        "names_in": lambda self, paths: names,
        "bad_paths": lambda self: [],
    })()
    ch = {"renames": {}, "touched": set(), "code_shape": False, "code_touched": ["a.py"]}
    lines = [
        ("Systems/P.md", i, "x", {
            "conds": [("symbol", f"missing-{i}")],
            "by": "2099-12-31",
            "bad": False,
        })
        for i in range(850)
    ]
    old = g["_drift_probe_old"]
    g["_drift_probe_old"] = lambda *a, **k: True
    start = time.monotonic()
    todo, unknown = f(
        lines, ch, "docs/kg-knowledge/", None, None, tree,
        lambda: time.monotonic() - start >= 60,
    )
    g["_drift_probe_old"] = old
    print("elapsed", round(time.monotonic() - start, 2),
          "todo", len(todo), "unknown", len(unknown))
    assert not unknown
    PY
    ```

    輸出：

    ```text
    elapsed 60.04 todo 0 unknown 67
    AssertionError
    ```

## F3 判不了的檔名會被前一列留下的快取污染

severity: major

blocking: 是 — 錯誤清單會在五筆上限內只顯示這一列未讀取的測試檔，真正造成判不了的程式檔反而被隱藏。

引句:「out.update(q for q in t.bad_paths() if (q == path if path else _drift_probe_code_path(q)))」

1. `bad_paths()` 是整棵 tree 累積讀取失敗的集合。無路徑 `symbol` 與 `test` 現在只用 `_drift_probe_code_path` 過濾，沒有依 `_nodehome_is_test(..., layout)` 分開兩種語料。

file: `scripts/lumos:26645`

file: `scripts/lumos:26865`

2. `drift scan` 先評估一條 `when-test` 後，再評估 `when-symbol`；第二列只讀取 `zz/a.py`，卻沿用前列六支測試檔的失敗。排序加五筆顯示上限讓真正的 `zz/a.py` 完全不出現在訊息中。

3. 最小重現：

    ```sh
    /opt/homebrew/bin/python3 - <<'PY'
    import pathlib, runpy, types
    m = runpy.run_path("scripts/lumos", run_name="review")
    files = {"zz/a.py", *[f"tests/t{i}.py" for i in range(6)]}
    tree = m["_DriftProbeTree"](".", "tip", files, m["_nodehome_layout"](files))
    tree._read = types.MethodType(
        lambda self, paths: self._text.update({p: None for p in paths}) is None,
        tree,
    )
    def note(cond):
        return ("---\ntype: system\nstatus: doing\nsummary: x\n---\n"
                f"REVISIT:{cond}[by:2099-12-31] x\n")
    env = m["Env"].from_texts(pathlib.Path("/unused"), {
        "Systems/A.md": note("[when-test:missing]"),
        "Systems/B.md": note("[when-symbol:missing]"),
    })
    _, problems = m["_drift_probe_scan"](env, tree)
    print(*[p[0] + ":" + p[3] for p in problems], sep="\n")
    PY
    ```

    輸出：

    ```text
    Systems/A.md:判不了(git 讀不出程式檔或筆記:tests/t0.py、tests/t1.py、tests/t2.py、tests/t3.py、tests/t4.py 等 6 支)
    Systems/B.md:判不了(git 讀不出程式檔或筆記:tests/t0.py、tests/t1.py、tests/t2.py、tests/t3.py、tests/t4.py 等 7 支)
    ```

## F4 C1 的翻紅說明仍描述已刪除的預量機制

severity: minor

blocking: 否 — 目前判定不受影響，但回歸測試的 mutation 說明已與測試內容相反。

引句:「名稱改回對全文跑正則 → B2 紅;候選遇到判不了就停 → B3 紅;3.12 以前不先量最長邏輯行 → C1 紅;」

1. C1 已改成在 Python 3.14 直接呼叫 `_drift_py_names`，而 `_drift_py_too_deep` 已刪除；「3.12 以前不先量最長邏輯行」不再是能讓 C1 翻紅的 mutation。

file: `scripts/test_lumos.py:52917`

file: `scripts/test_lumos.py:52974`

2. 後續照這段說明做 mutation 時，會測一個已不存在的防線，與同一 hunk 新寫的 C1 目的不一致。

## 已看,無 finding：Python 3.14 解析退回

引句:「except (SyntaxError, ValueError, MemoryError, RecursionError):」

1. 直接以 Python 3.14.6 執行 30 萬個負號與 17 萬段 `elif`，兩者都快速回傳 `None`，沒有未接住例外或程序崩潰。

## 已看,無 finding：partial 的命中分流

引句:「return True if hit else (None if names.partial else False)」

1. 可讀檔命中時回 `True`、未命中且另有讀取失敗時回 `None`，這部分符合修正規格；問題限於 F2 的非識別字效能路徑。

總結:最高 major，blocking 共 3 條。