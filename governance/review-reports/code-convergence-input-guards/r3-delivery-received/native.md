severity: major

### delivery-修補驗收-codex-F1

severity: major  
blocking: 是

引句:「ok, why, unsure = _codeloop_record_valid_ex(repo_root, p2, marker_sha, timeout=left)」

file: `scripts/lumos:46871`  
file: `scripts/lumos:46977`  
file: `scripts/lumos:46993`  
file: `scripts/lumos:47068`

觀察：合併側先算出截止前剩餘時間 `left`，但 `_codeloop_record_valid_ex` 把它當成每個 Git 子程序各自的 timeout；`merge-base`、`git diff`，以及可能的 blob 讀取都能各花完整 `left`。用 Python 3.14 注入 `timeout=7` 實測，前兩個子程序收到的是 `[7, 7]`，不是第二步取得扣除後的剩餘時間。因此宣告的 20 秒截止可能膨脹成 40 秒以上，進入 blob 判定時還會更久。兩條新路徑——驗合併結果及逐筆找留痕——都有此問題；而正式 `LUMOS_SKIP_CODE_LOOP` 退路在合併側查找之後，亦可能先被拖過截止才放行。

建議把絕對 `deadline` 傳入 `_codeloop_record_valid_ex`，在每次子程序及 blob 讀取前重新計算剩餘時間；補一條假時鐘測試，證明第一階段耗盡預算後不再啟動第二階段。

是否本批新增：是；底層 helper 原本是「每次 Git 呼叫的 timeout」，本批新碼把它誤當成整段共用截止。

### 其餘驗收面

- 固定版本：HEAD 確認為 `c09d12037d1f0d5a5ce92bd09ccda1ed048a2319`，工作樹乾淨。
- 指定材料：`native-delta.patch` 996/996 行完整讀取；在固定 HEAD 執行 reverse apply check 為 rc0。
- 固定改動清單：指定 delta 只涉及 `scripts/lumos`、`scripts/test_lumos.py`。
- 每版配置：新舊快照分別讀自己的 `.lumos/config.json` 與 vendored 狀態，未發現其他 finding。
- 宣告個別所有權：超限或未完整讀到的新宣告會撤回額外路由，不能由另一篇合法宣告代替作證；舊版正式所有權仍保留，未發現其他 finding。
- 單筆／整批限制：256 KiB 單筆、8 MiB 整批的內容篩選有接入；失敗時只撤回補助證據，未發現其他 finding。
- 原正式退路：node-home 的正式判定仍在；code-loop 的 env skip 最終仍可放行，但受到 F1 的截止延遲回歸。
- 不宣稱系統原子化：新增測試含暫存 repo、索引注入與 mock clock，僅證明其受控路徑。

### 圖譜固定席

- `Issues/canary-record未落盤事件`：不影響；沒有改 canary 寫入或落盤。
- `Systems/lumos-cli-read`：不影響；search 的 stale／superseded 濾網未動。
- `Systems/design-loop`：不影響；沒有改設計審材料型別或處置閘。
- `Systems/pitfalls-code-loop`：影響；新增主線合併側留痕／表態辨識，F1 位於此路徑。
- `Systems/bound-tests-gate`：有共同入口影響，但 delta 未改綁定測試的選取、執行或 rc 規則；未發現額外 finding。
- `Systems/guard-kill`：不影響；rc 優先序及 JSON 輸出未動。
- `Systems/授權與歸屬`：不影響；沒有改 vendoring、deinit 或授權檔。
- `Systems/測試假綠形態`：影響；新增案例有現場前置斷言及翻紅釘形狀，但實際紅綠執行未完成，見限制。

### 測試與限制

- Python 3.14 對兩支檔案編譯檢查通過。
- 同版新增測試會由 runner 的 `t_` 動態收錄。
- 因沙盒禁止建立隔離實驗目錄（`Operation not permitted`），未能實跑 HEAD 綠燈及基準版翻紅；因此不宣稱完整紅綠驗證。
- 固定 repo 最終仍為乾淨狀態，未做 commit/reset/restore/checkout/stash。
- 未開啟或閱讀其他席報告內容。

行數紀錄：規則 498 個唯一行、重讀 31 行；patch 996 行；graph lens 57 行；精確符號及上下游佐證約 1,230 行。一次誤下的廣域檔名／stat 命令原始輸出達 2,397 行並被工具截斷，故可核算總量約 5,200 行，已超過 1,800 行上限，不能聲稱在行數限制內完成覆蓋。

未讀部分：影響範圍內指定 delta 以外的約 1,194 個檔案；graph lens 標成「超出上限、只列名」的 21 篇節點全文；外部碼表補選；以及實際測試紅綠結果。