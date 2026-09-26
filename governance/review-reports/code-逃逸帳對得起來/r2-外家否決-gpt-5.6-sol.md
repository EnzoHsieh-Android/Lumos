severity: major

## F1 plan 類舊列會污染歸因比對，掩掉真正漏網
severity: major
blocking: yes
引句:「        if lid in released:」
file: `scripts/lumos:9887` `_escape_shared_evidence` 只判迴圈目前是否已放行，沒有按該列已落帳的 `loop_kind` 排除 `plan`；但 `scripts/lumos:9937` 稍後又把同一列視為 plan。結果是：某計劃先留下 plan 逃逸、後來才完成審查時，該舊列會參與佐證碰撞，令另一個真正受審迴圈的逃逸變成「歸因不明」，違反 [S1] 的落帳種類優先與 [S20] 的分母母體限制，並把漏網率低估。

重現步驟（已實跑，rc=1）：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import importlib.machinery,importlib.util
ldr=importlib.machinery.SourceFileLoader("lumos_review","scripts/lumos"); s=importlib.util.spec_from_loader(ldr.name,ldr); m=importlib.util.module_from_spec(s); ldr.exec_module(m)
class E: pass
e=E(); e.notes={}
rows=[{"loop":"A","loop_kind":"plan","sha":"same","stage":"CI"},{"loop":"B","loop_kind":"design","sha":"same","stage":"CI"}]
m._escape_rows_for=lambda env:rows; m._review_loop_ids=lambda env:{"A","B"}; m._escape_review_rows_by_loop=lambda env:{"A":[{"tier":"standard"}],"B":[{"tier":"standard"}]}; m._escape_released_loops=lambda env,ids:{"A","B"}; m._escape_plan_scopes=lambda env,lid:["x"]; m._escape_raw_rows=lambda env:rows
st=m._escape_stats(e); print(st); assert st["totals"]["unattributed"]==0 and st["categories"][0]["leaked"]==1, "plan 列不應污染分母母體的佐證比對"'
```

實際得到 `unattributed: 1`、`leaked: 0`，斷言紅；B 的真漏網被 A 的 plan 列消掉。

## F2 NFD 檔名找到計劃後仍會丟失 scope 分類
severity: major
blocking: yes
引句:「    n = env.notes.get(rel) if rel else None」
file: `scripts/lumos:323` `load_vault` 將索引鍵正規化成 NFC；但 `scripts/lumos:9481` 的 NFD 後備分支回傳磁碟原始檔名。新增的 `env.notes.get(rel)` 因字串正規形不同而找不到已存在的筆記，將帶 `scope/evals` 的計劃錯分為「未分類」。這破壞 [S9] 的範圍分類，亦使 [S10] 宣稱的 NFC 查找只完成一半。

重現步驟（已實跑，rc=1）：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import importlib.machinery,importlib.util,unicodedata
ldr=importlib.machinery.SourceFileLoader("lumos_review","scripts/lumos"); s=importlib.util.spec_from_loader(ldr.name,ldr); m=importlib.util.module_from_spec(s); ldr.exec_module(m)
class N: pass
n=N(); n.fields={"tags":["type/project","scope/evals"]}
class E: pass
e=E(); rel=unicodedata.normalize("NFD","Projects/café_計劃.md"); e.notes={unicodedata.normalize("NFC",rel):n}; m._plan_for_loop=lambda env,lid:rel
sc=m._escape_plan_scopes(e,"code-café"); print(sc); assert sc==["evals"], "NFD 計劃已找到卻被錯分未分類"'
```

實際輸出 `['未分類']`，斷言紅。

已看,無: `--withdrawn-by` 路由、撤回與 `--repo` 混用、重複 token 拒絕、清單印 token、`nodes`/`gate` 放行形狀、sha 與 defect_ref 分鍵、控制字元清洗，未再找到可實跑證成的 blocker/major。指定測試 runner 在唯讀沙箱因無可寫暫存目錄而未能啟動；上述兩個反例改以不落盤方式直接載入凍結實作並實跑。
