severity: major

### F1 相對 `--out-dir` 使鎖與子程序輸出落在不同目錄

severity: major  
blocking: 是  
引句:「out_dir = Path(a.out_dir) if a.out_dir else ROOT / "governance" / "eval" / "ablation-lumos-first" / date」  
file: `governance/eval/ablation_lumos_first.py:422`

`out_dir` 保留相對路徑，因此主程序在呼叫者 cwd 建立並鎖定目錄；`run_job` 卻用 `cwd=ROOT` 啟動探針，令同一相對結果路徑改從 repo 根解析。鎖保護的目錄不是探針實際寫入的目錄。兩個不同 cwd 的程序可各自成功取鎖，卻同時把原始結果寫進 `ROOT/<out-dir>`，破壞 S10 的互斥與資料隔離；單一程序也會留下不在摘要目錄中的孤兒結果。

最小翻紅重現（已執行，退出 1）：

```sh
cd /tmp
python3 -c 'from pathlib import Path; root=Path("/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone"); rel=Path("relative-out")/"probe.json"; print("parent=", (Path.cwd()/rel).resolve()); print("child =", (root/rel).resolve()); assert (Path.cwd()/rel).resolve() == (root/rel).resolve()'
```

實際顯示 `/private/tmp/relative-out/probe.json` 與 repo 下的 `relative-out/probe.json`。應在入口把 `out_dir` 絕對化，再取得鎖及派給子程序。

### F2 空 `qid` 會關掉探針篩選，一個工作可展開成整份題庫

severity: major  
blocking: 是  
引句:「"--only", qid, "--runs", str(n), "--arm", arm, "--out", str(out),」  
file: `governance/eval/ablation_lumos_first.py:196`

`load_ids` 接受空字串；下游 `scenario_probe` 對空的 `--only` 視為「未指定篩選」，因此該工作會執行整份題庫。惡意題庫只需加入空 id，就能讓一次已通過 `max_per_window` 事前檢查的工作啟動所有有效情境，超出場數上限並消耗模型配額。含逗號或恰為共同前綴的 id 也會擴大選取集合。

最小翻紅重現（已執行）：

```sh
printf '%s\n' '{"id":"","prompt":"x"}' |
python3 -c 'import importlib.util; s=importlib.util.spec_from_file_location("a","governance/eval/ablation_lumos_first.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(repr(m.load_ids(["/dev/stdin"])))'
# ['']

python3 scripts/scenario_probe.py \
  --scenarios governance/scenarios/commands.jsonl \
  --only '' --dry-list |
awk -F, '{print "selected=" NF}'
# selected=25
```

入口應拒絕空 id，且消融呼叫需要「完全相等」的單題選取介面，不能沿用支援逗號及前綴的互動式 `--only` 語意。

### F3 `arm` 可把 log 路徑導出 `out-dir`

severity: minor  
blocking: 否  
引句:「out = Path(out_dir) / f"{arm}-q-{qid_key}-{stamp}.json"」  
file: `governance/eval/ablation_lumos_first.py:193`

外層 `--arms` 沒有限定為 `with`／`without`。例如 `--arms /tmp/attacker/probe` 會使 `Path(out_dir) / filename` 變成絕對的 `/tmp/attacker/probe-q-…`；程式先開啟 `.log`，內層探針才因非法 arm 拒絕。這可在鎖定目錄外建立診斷檔。奈秒後綴使精確覆寫既有檔不實際，因此降為 minor。應驗證、去重 arm 後才建立工作。

### F4 `qid` 未轉義即進 log、終端與 Markdown

severity: minor  
blocking: 否  
引句:「lf.write("$ " + " ".join(cmd) + "\n")」  
file: `governance/eval/ablation_lumos_first.py:202`

題庫可用 `{"id":"ok\nFORGED: batch healthy\n\u001b]0;spoofed\u0007", ...}` 注入額外 log 行及終端控制序列；同一 qid 又在 `render_md` 中直接插入表格，可用換行、管線符號或原始 HTML 偽造摘要內容。檔名雜湊只修復路徑長度，沒有處理呈現端注入。應拒絕控制字元，並分別對單行 log、終端與 Markdown 做編碼。

### 信任邊界判定

在圖譜明定的「同擁有者、合作進程、輸出目錄不被對手改名」範圍內，目錄 inode 鎖、舊鎖相容及 summary/meta 的符號連結替換成立；fatal summary 未帶未清洗例外訊息或完整命令，這部分無 finding。

不受信任共用目錄不在現行驗證範圍：共同寫入者可植入合法 `*.json` 偽造統計，或在取得目錄鎖後改名目錄並替換路徑，使後續以 pathname 執行的讀寫脫離已鎖 inode。這與 `Systems/ablation-lumos-first` 及 Verification 的限制一致，因此未另列本輪 blocking；若部署到共用目錄，需重新視為 major 威脅模型。

### 固定席圖譜逐條判定

- 表態 `py-eventloop na`：已讀，無 finding。
- 表態 `py-parallel satisfied`：外層確為串行；F2 是單一子程序的選取展開，並非平行派工。已讀，無另項 finding。
- `Systems/codex-harness`：F2 命中 `--only` 選取邊界。
- `Systems/測試假綠形態`：新增測試均有現場成立斷言；已讀，無 finding。
- `Systems/lumos-cli-read`：已讀，無 finding。
- `Systems/canary-audit` 兩條 invariant：已讀，無 finding。
- `Systems/design-loop`：已讀，無 finding。
- `Systems/bound-tests-gate`：已讀，無 finding。
- `Systems/guard-kill` 兩條 invariant：已讀，無 finding。
- `Systems/lumos-cli-lifecycle`：已讀，無 finding。
- `Systems/ablation-lumos-first`：F1 使相對 out-dir 下鎖身分與實際結果路徑不一致。
- 計劃 S8：已讀，無 finding。
- 計劃 S9：字面停派與單路成立；F2 會繞過其「一個工作對應一題」的資源假設。
- 計劃 S10：F1 違反實際輸出位置的互斥。
- `Verification/2026-10-04_探針停派與失敗留痕`：既有測試全用絕對 out-dir，未覆蓋 F1；未覆蓋空／逗號／前綴 qid。

總結：最嚴重 severity major；blocking 2 條。
