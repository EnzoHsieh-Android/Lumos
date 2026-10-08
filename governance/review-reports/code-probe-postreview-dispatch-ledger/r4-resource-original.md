severity: major

## Finding R4-RES-01

severity: major  
blocking: 是  
引句:「remaining = 0 if now < initialized + 18000 else max(0, limit - used)」  
file: `scripts/scenario_probe.py:762`

同一 SQLite 帳沒有保存或核對唯一的窗口上限；每次交易直接採用當次 caller 傳入的 `limit`。

具體輸入：

1. 同帳冷卻完成。
2. 第一個程序以 `--max-per-window 1` 成功 claim；此時按上限 1 查詢，剩餘量為 0。
3. 五小時尚未過，另一程序對同一帳使用 `--max-per-window 50`。

預期：共用帳應有單一權威上限，或在上限不一致時 fail-closed；第二個 claim 不應靜默突破先前的一場上限。

實際路徑：第二個程序用 `50 - used` 重算，仍可插入意圖。以實際 `_attempt_ledger_transaction` 搭配不落檔的共享記憶體 SQLite 執行結果：

```text
claim-cap-1 True
remaining-cap-1 0
claim-cap-50 True
rows 2
```

正常可寫環境的最小驗證命令：

```sh
PYTHONPATH=scripts python3 -c 'import tempfile; from pathlib import Path; import scenario_probe as p; d=tempfile.TemporaryDirectory(); x=Path(d.name)/"u.sqlite3"; print(p.attempt_ledger_remaining(x,1,now=1000), p.claim_model_attempt(x,1,now=20000), p.claim_model_attempt(x,50,now=20001))'
```

目前會印出 `0 True True`；最後一個值應為 `False`，或應拋出「同帳上限不一致」的專用 fatal。

原問題／既有行為／回歸判斷：

- 原先「失敗、歸檔、跨日期會退還額度」的問題，在相同上限前提下已改由持久帳處理。
- 這是共用額度域的相鄰設定衝突，不等同原本的歸檔問題。
- before 沒有 SQLite 帳及同案例入口，無法取得同案例兩版輸出；修補歸因標為未判定，不宣稱是本修補造成的回歸。
- 建議把有效上限寫進 `ledger_meta`，遇到不同值時拒絕；若允許調額，應使用明確遷移操作，不能由任一程序單方面放寬。

## Finding R4-RES-02

severity: minor  
blocking: 否  
引句:「time.sleep(300); waited += 300」  
file: `scripts/scenario_probe.py:1223`

`--wait-on-limit` 宣稱是「最多等幾秒」，但等待固定為 300 秒，沒有取剩餘預算。

具體輸入：`--wait-on-limit 1 --max-per-window 0`，第一次 runner 回 `limit_hit=True`，第二次成功。

預期：總等待不超過 1 秒，例如 `sleep(min(300, wait_on_limit - waited))`。

實際路徑：條件只檢查 `waited < 1`，隨後仍呼叫 `sleep(300)`。不落檔 stub 實跑得到：

```text
rc 0 runner_calls 2 sleeps [300]
```

同一 harness 對固定兩版的輸出：

```text
before {'rc': 0, 'calls': 2, 'sleeps': [300]}
after  {'rc': 0, 'calls': 2, 'sleeps': [300]}
```

最小靜態核對命令：

```sh
git show 05e87b5476cf161a203382a50ef008b374e60a31:scripts/scenario_probe.py |
  nl -ba | sed -n '1207,1224p'
```

原問題／既有行為／回歸判斷：

- 持久帳修補新增的「額度已盡就不先等待」路徑有效，不受此項否定。
- 同案例 before/after 都等待 300 秒，因此是既有相鄰行為，不是本修補回歸。
- 它會讓小於 300 秒的等待預算失真，並額外保留批次基線資源。

## 四檔覆蓋

- `governance/eval/ablation_lumos_first.py`：完整讀過所有 patch hunk，另讀 `run_job`、`_run_locked_batch`、`main`。父程序先留 pending／log、查帳失敗停批、額度為零不啟動子程序、子程序最終仍原子 claim 的順序成立；但它把 caller 的原始上限直接傳入共用帳，受 R4-RES-01 影響。
- `scripts/scenario_probe.py`：完整讀過帳本交易、Claude/Codex runner、主迴圈、清理與重試。`BEGIN IMMEDIATE`、commit 後才進 `subprocess.run`、程序死亡後已提交意圖不退款、鎖錯誤 fail-closed、冷啟動五小時及每次重試重新 claim 的主路徑成立。發現 R4-RES-01、R4-RES-02。
- `scripts/test_autonomous_loop.py`：精準讀過八支新增 ledger 測試。涵蓋同上限末席競爭、鎖逾時、commit 後程序死亡、冷啟動、零值模式、失敗與跨日期、非法題目不耗額度、兩父程序敗方證據；未涵蓋同帳不同上限與小於 300 秒的等待上限。
- `scripts/test_lumos.py`：精準讀過本 patch 所涉測試函式。持久額度停止、結果權重、恢復路徑及報表來源測試未發現額外問題；同樣未覆蓋兩項 finding。

四檔均以固定 after `05e87b5476cf161a203382a50ef008b374e60a31` 查證；凍結 patch 為 1455 行，SHA256 確認為 `15816452e6d94bcc59ccec186ff3ccdaf69c71221c91f23cdbe6efce26cbf53f`。

## 實際執行與未驗

實際完成：

- 四檔以 `compile()` 做不落檔語法檢查，全部 `syntax-ok`。
- 記憶體 SQLite 執行不同上限案例，重現 R4-RES-01。
- stub runner／sleep spy 執行重試案例，重現 R4-RES-02。
- R4-RES-02 另以 before/after 同案例執行，確認兩版皆為 `sleeps [300]`。

因唯讀環境未完成：

- `python3 scripts/test_autonomous_loop.py -k attempt_ledger`：8 支都在 `TemporaryDirectory()` 前置階段失敗，原因為沒有任何可寫 temp 目錄，未進入被測邏輯。
- `python3 scripts/test_lumos.py -k persistent_ledger`
- `python3 scripts/test_lumos.py -k fourth_round`

後兩者均在 `_isolate_environment()` 取得 temp 目錄時以相同環境錯誤停止。這些不是程式故障，也不能冒稱本席獨立測試通過。作者的 `implementation-*.log` 未作為本席執行證據。

## 固定圖譜鏡頭判斷

- `Systems/ablation-lumos-first.md`：責任邊界正中本次改動；候選／pending／fatal、單路派工與目錄鎖事故邊界保持。共用帳上限不一致由 R4-RES-01 阻擋完整放行。
- `Systems/codex-harness.md`：Claude 與 Codex 均在 subprocess 前走同一 claim helper；未破壞 hook 責任邊界，兩者同受 R4-RES-01 影響。
- `Systems/測試假綠形態.md`：既有綁定測試未改；新增鎖與程序死亡測試有 ready／持鎖／啟動次數等現場前置證據。沒有覆蓋 R4-RES-01、R4-RES-02。
- `Systems/autonomous-iteration-loop.md`：預設 `max_per_window=0` 的既有直跑仍保留；無登記合約破壞。
- `Systems/lumos-cli-read.md`：search 合約及綁定測試未觸及。
- `Systems/lumos-cli-lifecycle.md`：re-inject 合約未觸及。
- `Systems/bound-tests-gate.md`：固定席合約測試執行語意未觸及。
- `Systems/canary-audit.md`：record／second 的落盤與 gate 語意未觸及。
- `Systems/design-loop.md`：處置閘第五步及條款解析未觸及。
- `Systems/guard-kill.md`：rc 優先序與 JSON 純度未觸及。
- `Systems/slim-get-一行安裝.md`：PowerShell 兩項合約未觸及。
- `Systems/slim-install-安裝器.md`：七項安裝合約未觸及。
- `Systems/slim-uninstall-一行卸載.md`：六項卸載合約未觸及。
- `Systems/授權與歸屬.md`：vendored 白名單未增加授權檔；`scripts/test_lumos.py` 既有 SPDX/MIT 檔頭保持。
- `Projects/規格落成可驗收條件_計劃.md`：無合約，相關規格閘責任邊界未觸及。
- `Systems/lumos-deinit.md`：無合約；vendored/deinit 清單未改。
- `Projects/逃逸自動記_計劃.md`：無合約；只新增測試函式，未改自動記帳入口。
- `Systems/cochange-guard.md`：僅登記技術債，未觸及。
- `Systems/check-r-guard.md`：不可逆／guard 解析責任未觸及。
- `Systems/節點範圍與索引守衛.md`：九項 doctor／索引合約及其綁定測試未改。

未讀其他審查員報告、作者處置清單、staging、無關測試函式及真模型紀錄；閱讀預算未耗盡。因 R4-RES-01 為 blocking major，這不是部分 clean 或完整通過。