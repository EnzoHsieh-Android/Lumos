# r2 架構對齊審查——主session鏡頭利用率 code-loop r1 修正

被審:`governance/review-reports/lens-stage0/r2-snapshot.patch`(對應 `governance/anchor-baseline.json` 記錄的
approved_at 2026-09-04T09:06:32、note「code-loop lens-stage0 r1:test_lumos.py 加 main 接線測試與 recount 分類測試」,commit `a39741a`)。
唯一工作:判「這份修正 delta 跟本專案既有做法一不一樣」,不找 bug、不評風格。

## 一、r1 驗收(major f1/f2 修了沒)

r1 判 major 的兩條——`recount.py` 自寫 Bash 切詞(f1)、自寫第三套圖譜目錄定位(f2)——這次都改成用 `SourceFileLoader`
載入 `scripts/hooks/claude/check-graph-sync.py` 沿用既有函式,讀 code 逐行核對過,兩條都確實修掉了:

- `classify_bash()`(file: `governance/eval/lens-utilization/recount.py:97,109`)現在呼叫 `_segment_command(cmd)` 切段、
  `_tokens_of(seg)` 切詞,不再是自己的 `re.split(r"[;|&]+", cmd)`;這兩支函式是從 `check-graph-sync.py:178,183` 原地載入
  的同一份實作(`_load_hook_helpers()`,file: `governance/eval/lens-utilization/recount.py:12-19`)。f1 消除。
- `vault_slug()`(file: `governance/eval/lens-utilization/recount.py:31-32`)改成 `g = _find_graph_root(repo); return g.name if g else None`,
  直接委派 `check-graph-sync.py:72` 的 `find_graph_root`,不再自己找 `docs/*-knowledge`。這支既有實作本身就含 r1 report
  指出「前兩份都有、recount 這份漏掉」的 legacy `docs/knowledge` fallback(file: `scripts/hooks/claude/check-graph-sync.py:80-81`),
  所以這次不只是消掉第三套,委派後連漏掉的能力都一起補回來了。f2 消除。

兩條 major 都在同一次修正裡用「載入既有實作」而不是「再修一次自己的版本」解決,符合本專案對「單一實作來源」的既定紀律
(`governance/eval/ablation_lumos_first.py` 那句「計分一律 import,兩份實作立刻漂移」)。r1 驗收:過。

## 二、三問逐答

### Q1:腳本層用 `SourceFileLoader` 載 hook 模組,在本 repo 有先例嗎?算對齊還是第二種做法?

有明確先例,而且是同一個力學(mechanics)、同一個載入對象。`scripts/test_lumos.py:9157-9163` 的 `t_impact_hook_filter_and_rc`
就是逐字同一套寫法載入 `impact-hook.py`:

```
loader = SourceFileLoader("impact_hook_mod", hook_path)
spec = importlib.util.spec_from_loader("impact_hook_mod", loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)
```

`governance/eval/lens-utilization/recount.py:21-26` 的 `_load_hook_helpers()` 用的是同一組四步(`SourceFileLoader` →
`spec_from_loader` → `module_from_spec` → `exec_module`),只是縮寫成兩行。另外同層(`governance/eval/`)的
`governance/eval/k1_stop_replay.py:11-13` 也用 `SourceFileLoader` 載入 `scripts/lumos`(同樣是無 `.py`/帶連字號檔名、
不能用一般 `import` 的腳本),證明「eval 腳本用 `SourceFileLoader` 依賴 `scripts/` 或 `hooks/` 下的既有腳本」這件事本來
就是這一層的既定做法,不是這次新開的先例。

判定:對齊。file: `governance/eval/lens-utilization/recount.py:20-26`(先例:`scripts/test_lumos.py:9157-9163`、
`governance/eval/k1_stop_replay.py:7-13`)。

### Q2:`_ttl_unmark` 命名與 `_ttl_mark`/既有慣例一致嗎?

一致。本檔既有 `_ttl_*` 家族是 `_ttl_marker_path`、`_ttl_lazy_cleanup`、`_ttl_should_inject`、(上一輪新增的)`_ttl_mark`
(file: `scripts/hooks/claude/impact-hook.py:125`)。`_ttl_unmark`(file: `scripts/hooks/claude/impact-hook.py:117`)延續
同一個字首,「mark/unmark」是標準的動作/逆動作命名對,語意(撤掉 `_ttl_mark` 寫下的標記檔)跟名字對得上,函式內容也只做
`_ttl_marker_path(...).unlink()` 一件事,沒有夾帶其他副作用。

判定:對齊,無不對齊項。

### Q3:main 裡重複的 `if session_id and not in_cooldown: _ttl_unmark(...)` 跟鄰居 hook 的錯誤處理形態一致嗎?有沒有 try/finally 慣例?

實際數出來是 5 處呼叫點(file: `scripts/hooks/claude/impact-hook.py:153-154, 175-176, 181-182, 202-203, 208-209`),
不是派工詞講的四處;三種寫法混用(獨立 `if` 區塊兩處、跟其他條件用 `and` 併一行兩處、`rc != 0` 那條額外攔在 rc==3
分支之前)。

查過本專案四支鄰居 hook(`dispatch-lens-hook.py`、`ci-status-hook.py`、`lumos-entry-hook.py`、`check-graph-sync.py`)
全部 `try:`/`except`,`finally:` 一次都沒出現——這個家族處理錯誤的既定形態是「每個失敗點各自窄範圍 try/except,配一條
`return 0` fail-open」,不是集中式清理,`impact-hook.py` 自己 `main()` 原本就已經是這種逐點 `return 0` 的散彈寫法
(未改動的 rc==3/rc!=0/lumos None 等分支都是各自獨立 `return 0`)。這次新增的 5 條 `_ttl_unmark` guard 是延著這個既有
散彈形狀長出來的,不是憑空插入一種新結構——就「本檔/本家族既有寫法」而言,結構是對的。

但往上一層看,本 repo 對「先寫入一個標記、無論哪條路徑結束都要保證對稱清理」這類問題,既定做法是 `try/finally`——
`scripts/lumos` 裡至少 7 處(如 `_ledger_append` 的 fd 寫入包 `try: ... finally: os.close(fd)`、cascade 檔案建立、
worktree keep/cleanup、CLAUDE.md 原子寫入的暫存檔 unlink)全部用 `finally` 保證釋放,一次都沒有靠「在每個 return 前手動
複製一行清理」來做。`scripts/hooks/claude/` 這個家族目前為止從沒遇過這種「寫了要嘛保留、要嘛撤銷」的資源生命週期問題
(逐一查過四支鄰居,沒有 unlink/撤銷既有標記的先例),所以嚴格說沒有「違反 hook 家族既有 try/finally 慣例」這回事——
家族裡本來就沒有這個慣例可違反。真正的落差是:這次是本家族第一次出現這種需求,而選的解法(手動複製 guard)恰好跟
本 repo 在別處(`scripts/lumos`)遇到同一類問題時採用的解法(`try/finally`)不同形狀,且 5 個呼叫點裡連寫法都不統一,
之後若再加一條新的 return 分支,很容易漏掉補這行,沒有機械測試會抓到「忘記撤標記」這件事。

判定:不對齊,見 f1(minor——命名/結構本身沒錯,是錯誤處理形態跟本 repo 對同類問題的既定解法不同,且新代碼內部三種寫法不統一)。

---

### f1

引句:「if session_id and not in_cooldown:」

file: `scripts/hooks/claude/impact-hook.py:501,523,549`(對照:`:529`、`:553` 是同一件事的 `and` 併行寫法;
既有 try/finally 慣例對照:`scripts/lumos` 的 `_ledger_append`/cascade 檔案建立/worktree cleanup 等 fd·暫存檔清理處)

severity: minor
blocking: 否

⚠ 判準不是機械可測的——沒有既有測試釘住「hooks 家族錯誤清理必須用 try/finally」,`scripts/hooks/claude/` 這個家族
本身也從未有過同類需求,所以這不是違反本家族既有慣例,而是跟 repo 更高層(`scripts/lumos`)對「保證對稱清理」這一類
問題的既定解法不同形狀;是否要收斂進 try/finally 留給 Enzo 裁,不擋。

---

不對齊共 1 條,其中 major 0 條。
