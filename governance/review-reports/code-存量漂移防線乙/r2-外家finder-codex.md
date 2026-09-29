severity: major

## F1 單一 blob 讀取失敗被當成條件不成立，block 閘會放行

severity: major

blocking: 是 — 判不了本應阻擋，但目前會產生空 verdict 並放行

引句:「self._text[p] = None if b is None else b.decode("utf-8", errors="replace")」

1. `_nodehome_cat_blobs` 合法回傳 `bytes|None` 清單；新 `_read` 遇到單一 `None` 仍回 `True`，隨後 `_defines` 把它判成 `False`。`_drift_probe_judge` 因而回空字串，而不是 `None` 的判不了路徑。
2. NFD 路徑會實際走到這裡：樹清單先轉 NFC，之後卻用 NFC 路徑讀仍以 NFD 儲存的 Git blob。status 筆記也有同形狀：`_drift_tree_env` 直接跳過單一 `None`，使新 `_note_unreadable` 判定無從生效。
3. 新測試只注入「整批回 `None`」，沒有覆蓋「整批成功但單一元素為 `None`」。
4. 最小重現：

```sh
python3 -c 'import runpy; m=runpy.run_path("scripts/lumos"); g=m["_DriftProbeTree"].__init__.__globals__; g["_nodehome_cat_blobs"]=lambda *a,**k:[None]; t=m["_DriftProbeTree"](".","0"*40,{"src/a.py"},({},{})); cond=(("symbol","src/a.py::start"),); one=m["_drift_probe_line"](t,None,cond); verdict=m["_drift_probe_judge"](lambda c:one,lambda c:False,{"conds":cond,"by":"2099-01-01"},False); print(f"line={one!r}, check_verdict={verdict!r}")'
```

輸出：

```text
line=False, check_verdict=''
```

file: `scripts/lumos:25920`

file: `scripts/lumos:25587`

file: `scripts/test_lumos.py:50458`

## F2 `--budget inf` 讓唯讀 scan 直接 traceback

severity: minor

blocking: 否 — 只影響顯式傳入非有限預算的 scan 呼叫

引句:「if budget <= 0:」

1. `argparse` 的 `float` 接受 `inf` 與 `nan`；目前只檢查 `<= 0`。`inf` 被傳給 `subprocess.run(timeout=...)` 後拋出 `OverflowError`，沒有依 CLI 慣例回 rc2；`nan` 則讓所有 deadline 比較為假，實際停用總預算。
2. 最小重現：

```sh
python3 scripts/lumos drift scan --at HEAD --json --budget inf >/dev/null; echo rc=$?
```

輸出末尾：

```text
OverflowError: cannot convert float infinity to integer
rc=1
```

file: `scripts/lumos:26403`

file: `scripts/lumos:25581`

## F3 混合 c1 與 probe 時印出的 ack 指令會被 shell 解讀成管線

severity: minor

blocking: 否 — 閘本身仍能阻擋，但提供的處置指令不可執行

引句:「"|".join(sorted(kinds)) if len(kinds) > 1 else next(iter(kinds))」

1. 同一次推送可同時產生 `c1` 與 `probe`；此時提示印成 `--kind c1|probe`。`--kind` 只接受單一 choice，而且未引用的 `|` 會被 shell 當成管線運算子。
2. 對 `_drift_report_must` 餵入一筆 `c1` 與一筆 `probe`，輸出為：

```text
lumos drift ack <節點> <行號> --kind c1|probe --reason "<為什麼照留>"
```

file: `scripts/lumos:26376`

## 已看,無 finding

- 圖譜計劃、Systems 節點與考卷期限改寫：已看,無 finding。
- E5 雙反引號、範圍淨差異行號、status 收尾判定：已看,無 finding。
- AST 定義、候選共用、工作目錄快照與提交清單快取：除 F1 外，已看,無 finding。
- Python 3.9 grammar：`scripts/lumos` 與 `scripts/test_lumos.py` 均通過解析，無 finding。
- 新增測試子集因唯讀沙盒無可寫臨時目錄而未能啟動；上述 findings 均另有不寫檔的當場重現。

最嚴重等級 major，blocking 共 1 條。