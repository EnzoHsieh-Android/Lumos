severity: clean

我沒有建立 worktree 或臨時目錄,也沒有跑測試。這個鏡頭只比對寫法,我用 `git show f14bd5881…:scripts/test_lumos.py` 取出凍結版逐項對照鄰居測試,結果如下。對照用的暫存檔已刪。

## 架構對齊三問

**1. 分層與依賴方向:對齊。**
- 修補只動測試檔 `scripts/test_lumos.py`、筆記 `Systems/guard-kill.md` 和 `anchor-baseline.json`,沒有新增跨層呼叫。
- 測試照鄰居慣例走 `_load_lumos_inproc()`、`_ckm_repo`、`_ckm_inproc(... cmd_guard_kill ...)`、`_ck_cleanup`。
- 鄰居:`scripts/test_lumos.py:146781`(同樣用 `_ckm_inproc` 包 `cmd_guard_kill`)。

**2. 命名與錯誤處理:對齊。**
- check 訊息開頭沿用「r4 通才 #1」「r4 邊界 #3」這種標註審查輪次的前綴,跟既有 `r1 邊界 #4`、`r3 邊界 #2` 一樣。
- 解析失敗用 `except (ValueError, IndexError, KeyError)` 退成 `rows = []`,斷言再接手,跟鄰居「讀不到就給空值」的寫法同一類。
- 鄰居:`scripts/test_lumos.py:147222`、`:147415`。

**3. 第二種做法:四項都沒有引入。**

| 被問到的寫法 | 修補的做法 | 鄰居的既有做法 | 判定 |
|---|---|---|---|
| 函式內 `import json` | `t_choice_kill_merge_cap_wiring` 開頭一行 | 全檔 45 處縮排 `    import json`,如 `scripts/test_lumos.py:14224`;choice-kill 區塊內還有 `scripts/test_lumos.py:146870` 的 `import json as _j` | 同一種(只差別名) |
| 解析 `--json` 輸出 | `json.loads(out.strip().splitlines()[-1])["results"]` | 全檔 `json.loads(r.stdout.strip().splitlines()[-1])` 一個固定用法,如 `scripts/test_lumos.py:1500`、`:1652` | 逐字同一種 |
| 換掉 `_KillMerge.remaining` | `mg.remaining = lambda: 60.0 if singles[0] < 3 else -5.0` | 同檔既有直接指定 lambda,如 `scripts/test_lumos.py:147222`、`:147234`、`:147415` | 同一機制 |
| 一個測試內部 `run()` 跑兩個情境 | 內部 `def run(mg, as_json=False)`,其中 try/finally 還原 `_kill_run` 並呼叫 `_ck_cleanup` | 全檔內部 `def run(...)` 有 10 處以上,如 `scripts/test_lumos.py:17895`、`:18626` | 同一種 |

- `remaining` 改成依呼叫次數切換:用的還是直接指定 lambda,只是條件多了計數器。
- 計數器 `singles[0] += 1` 用單元素 list,檔內 `calls[0] += 1` 等多處同款(`scripts/test_lumos.py:82938`、`:83059`)。

## 已驗主張
引句:「mg.remaining = lambda: 60.0 if singles[0] < 3 else -5.0」
引句:「rows = json.loads(out.strip().splitlines()[-1])["results"]」
引句:「_rc, out, _err = run(m._KillMerge(_ckm_time.monotonic() + 60, 2), as_json=True)」

- 這三段分別對應「換掉 remaining」「解析 --json」「內部 run() 跑兩情境」。
- 同一測試新增的 `import json` 一行與上面的 `run()` 也一併核過,對照結果都在上表。
- 本席只比寫法,不判行為是否正確。
- 鄰居慣例以凍結版 `f14bd5881` 的 `scripts/test_lumos.py` 為準。

不對齊共 0 條,其中 major 0 條。

總結:最高嚴重度 clean
