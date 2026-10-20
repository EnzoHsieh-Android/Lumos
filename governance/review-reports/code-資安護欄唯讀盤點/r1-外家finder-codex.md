severity: major

1. 壞型別會讓整份盤點崩潰，正常條目也無法輸出

severity: major
blocking: 是

位置：`scripts/lumos:6797`，`_sc_source`；同類問題也在 `_secinv_inventory_problems`。

`source.kind` 尚未確認是字串就拿來查字典；inventory 的 asset ID 驗成非法後，仍被放進集合。兩者都能觸發未捕捉的 `TypeError`，違反「問題累積、正常項保留、退出 2、JSON 單一物件」契約。

最小重現（repo 根執行）：

```sh
python3.14 -B -c 'import runpy; m=runpy.run_path("scripts/lumos"); print(m["_secinv_check_control"]({"source":{"kind":[]}}))'
```

輸入：登記項的 `source.kind=[]`。  
預期：回傳 schema 問題，由盤點列為 `invalid_record`，保留其他正常項。  
實際：`TypeError: cannot use 'list' as a dict key`。

另已用完整記憶體快照呼叫 `cmd_security_list(..., True)`：正常項加上述壞項時，stdout 為空並拋例外；`inventory.assets[0].id=[]` 同樣得到 `TypeError`。

引句:「"requirement": ("kind", "claim", "decision_ref")}.get(kind)」

2. 空登記塊會隱藏應列出的未登記節點

severity: major
blocking: 是

位置：`scripts/lumos:7034`、`scripts/lumos:7279`。

`block_nodes` 記的是「存在合格頂層 JSON」，不是「有登記條目」。因此帶 `flag/security-relevant` 的節點只要放 `controls: []`，就從 `unregistered_nodes` 消失，違反設計「有標籤但沒有條目者應列出」的規定。

最小重現：

```sh
python3.14 -B -c 'import runpy
from pathlib import Path
m=runpy.run_path("scripts/lumos")
t="---\ntype: system\ntags:\n  - flag/security-relevant\n---\n```lumos-security-v1\n{\"schema_version\":1,\"controls\":[]}\n```\n"
s=dict(texts=[("Systems/B.md",t)],unreadable=[],errors=[],stats={})
r=m["_secinv_build"](Path("/virtual"),s)
print(m["_secinv_exit_code"](r),r["unregistered_nodes"],r["errors"])
assert "Systems/B.md" in r["unregistered_nodes"]'
```

預期：`unregistered_nodes` 包含 `Systems/B.md`。  
實際：印出 `0 [] []`，斷言失敗。另加入一篇合法控制項後，實測還會得到 `registration_complete=true`，而 B 的缺口仍被隱藏。

引句:「if "flag/security-relevant" in as_list(n.fields.get("tags")) and rel not in block_nodes],」

3. 來源引用無效的控制項仍消除入口映射缺口

severity: major
blocking: 是

位置：`scripts/lumos:7228`，`_secinv_coverage`。

來源核對失敗只加入全域 `errors`，coverage 仍使用全部非 retired 條目。這違反設計「映射限合法控制項」；即使唯一護欄的核可決策不存在，入口仍顯示 `mapped`，從 `unmapped` 消失。

最小重現：

```sh
python3.14 -B -c 'import runpy,json
from pathlib import Path
m=runpy.run_path("scripts/lumos")
c=dict.fromkeys(m["_SECINV_CTRL_KEYS"])
c.update(id="C1",revision="r1",concerns=["security"],
 source=dict(kind="requirement",claim="Owner only",decision_ref="Systems/A#d999"),
 lifecycle="active",assets=["A"],surfaces=["S"],
 required_evidence=[],evidence_refs=[],reported_status="untested")
inv=dict(revision="r1",decision_ref="Systems/A#d1",
 assets=[dict(id="A",description="asset")],
 surfaces=[dict(id="S",asset_ids=["A"],description="surface")])
fm="---\ntype: system\nstatus: done\ndecisions:\n  - content: approve\n    id: d1\n    valid: true\n---\n"
t=fm+"```lumos-security-v1\n"+json.dumps(dict(schema_version=1,controls=[c],inventory=inv))+"\n```\n"
r=m["_secinv_build"](Path("/virtual"),dict(texts=[("Systems/A.md",t)],unreadable=[],errors=[],stats={}))
print(r["errors"],r["coverage"]["unmapped"],r["coverage"]["surfaces"])
assert "S" in r["coverage"]["unmapped"]'
```

預期：保留 C1 與來源錯誤，但 S 沒有合法 active 映射，應列 `unmapped`。  
實際：列出「找不到這個決策編號」，同時輸出 `unmapped=[]`、`state="mapped"`、`mapped_control_ids=["C1"]`。退出 2 並未修正 coverage 的錯誤結論。

引句:「live = [r for r in rows if r["lifecycle"] != "retired"]」

4. vault 選擇失敗時，JSON 模式沒有任何 JSON 輸出

severity: major
blocking: 是

位置：`scripts/lumos:60086`，security 分派入口。

選定 vault 失敗就直接返回，沒有建立錯誤報告。這是有效命令的輸入錯誤，不是 argparse 用法錯誤，不適用輸出契約的例外。

重現：

```sh
python3.14 -B scripts/lumos --vault /definitely-not-existing-seat-vault security list --json
```

預期：退出 2，stdout 為單一 JSON 物件，包含不完整狀態與錯誤。  
實際：退出 2、stdout 為空；只有 stderr 的 `擋下:--vault 指的不是目錄...`。自動消費端無法解析契約規定的錯誤結果。

引句:「print(f"擋下:{_serr}", file=sys.stderr)」

最嚴重 severity: major；blocking 共 4 條。
