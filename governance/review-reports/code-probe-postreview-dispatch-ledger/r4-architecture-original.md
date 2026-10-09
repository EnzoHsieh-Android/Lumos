severity: minor

## Finding ARCH4-01

severity: minor  
blocking: 否  
引句:「"--max-attempts", "1", "--out", str(out)]」  
file: `scripts/test_lumos.py:38396`

具體輸入：以 `--max-per-window 1 --wait-on-limit 300` 直跑探針，不設 `--max-attempts`；第一場 claim 最後一格後收到供應商 limit。

預期路徑：測試應走 `scripts/scenario_probe.py:1210` 的持久帳重新查額度，證明直接停止、不 sleep。

實際測試路徑：fixture 沒有啟用 `--max-per-window`，而以 `--max-attempts 1` 讓 `scripts/scenario_probe.py:1209` 先判定額度耗盡。因此即使刪除持久帳的重試前檢查，這條測試仍會得到「零等待、零重試」。

具體影響：持久帳重試停止線沒有還原翻紅釘；未來該接線被移除時，探針會先白等 300 秒，再於下一次 claim 才停止，而測試仍可能全綠。這違反 `Systems/測試假綠形態` 的「前置斷言證明現場成立」合約。

最小驗證命令：

```sh
sed -n '38394,38405p' scripts/test_lumos.py
```

本席另以唯讀靜態檢查確認該案例區塊含 `--max-attempts`、不含 `--max-per-window`。

同案例前後歸因：未判定；沒有可執行的 before/after 同案例輸出。來源差異顯示 after 新增持久分支與測試，但本席不把「在修後發現」直接歸因為修補造成。

原問題：正式碼已修好。  
既有行為：批次 `--max-attempts` 通道有保留。  
回歸：未發現目前 runtime 回歸；問題是持久通道缺少有效防回歸證據。

## Finding ARCH4-02

severity: minor  
blocking: 否  
引句:「self.assertEqual(self.rn.run_job("with", "zz", 1, [], 1, 1, d, 0, "", max_per_window=3)[2][:4], "skip")」  
file: `scripts/test_autonomous_loop.py:2165`

具體輸入：輸出目錄有三筆最近結果，但持久帳已度過五小時冷卻且沒有 launch-intent，窗口上限為三。

預期路徑：派工只依 SQLite 帳，應有三格可用；舊 `runs_in_window()` 不得參與硬額度。

實際測試路徑：fixture 建立的是全新帳，冷卻規則本來就回零，所以新帳與舊結果檔算法都會得到 `skip`。即使重新把 `runs_in_window()` 接回派工判斷，測試仍會通過。

具體影響：測試沒有守住「結果檔只供診斷、SQLite 是唯一硬額度來源」的分層；未來另造第二套結果檔閘時，仍可能假綠並錯誤阻止尚有帳本額度的工作。

最小驗證命令：

```sh
sed -n '2153,2165p' scripts/test_autonomous_loop.py
```

本席唯讀檢查確認 fixture 有三筆近期結果、帳本未預先越過冷卻，且只斷言 `skip`。

同案例前後歸因：未判定；沒有同案例兩版執行輸出。after 正式碼已移除 `runs_in_window()` 的派工依賴，但測試無法區分新舊做法。

原問題：正式碼已修好；`run_job` 目前不呼叫 `runs_in_window()`。  
既有行為：`runs_in_window()` 作為診斷函式仍保留。  
回歸：未發現目前 runtime 第二套帳；缺口只在架構邊界的測試證據。

## 四檔覆蓋

| 檔案 | 判斷 |
|---|---|
| `governance/eval/ablation_lumos_first.py` | 父層只 import 共用帳本 helper；預查、子程序參數轉送、逐題權重上限、錯型拒收、meta 唯讀與 Markdown 轉義均核對。沒有目前的第二套硬額度。 |
| `scripts/scenario_probe.py` | SQLite `BEGIN IMMEDIATE`、專用錯誤型別、claim-before-launch、冷卻、回撥、重試前查額度及 fatal/inconclusive/rc3 通道均核對。介面新增參數放在尾端且預設停用，舊呼叫相容。 |
| `scripts/test_autonomous_loop.py` | 逐段看完新增帳本、競爭、跨日、死亡與父層事故測試；發現 ARCH4-02。 |
| `scripts/test_lumos.py` | 精準讀完本修補新增／調整函式；結果、恢復、報表測試有現場前置斷言，持久重試案例發現 ARCH4-01。 |

## 固定圖譜鏡頭

| 節點 | 合約判斷 |
|---|---|
| `Systems/ablation-lumos-first.md` | 無登記合約；責任仍在父派工／合併層。 |
| `Systems/codex-harness.md` | 無登記合約；Codex runner 仍由同一 claim helper 控制。 |
| `Systems/測試假綠形態.md` | 未完全滿足：ARCH4-01、ARCH4-02。 |
| `Systems/autonomous-iteration-loop.md` | 無登記合約；只增測試，未改迴圈實作。 |
| `Systems/lumos-cli-read.md` | search superseded 合約未受影響。 |
| `Systems/lumos-cli-lifecycle.md` | re-inject 合約未受影響。 |
| `Systems/bound-tests-gate.md` | 固定席測試執行通道未變。 |
| `Systems/canary-audit.md` | record/readback 與 second telemetry 未變。 |
| `Systems/design-loop.md` | 處置閘第五步未變。 |
| `Systems/guard-kill.md` | rc 優先序與 JSON 純度未變。 |
| `Systems/slim-get-一行安裝.md` | PowerShell 合約未變。 |
| `Systems/slim-install-安裝器.md` | 安裝與 CLAUDE.md 合約未變。 |
| `Systems/slim-uninstall-一行卸載.md` | 卸載及 manifest 合約未變。 |
| `Systems/授權與歸屬.md` | vendored 授權集合未變。 |
| `Projects/規格落成可驗收條件_計劃.md` | 無登記合約。 |
| `Systems/lumos-deinit.md` | 無登記合約。 |
| `Projects/逃逸自動記_計劃.md` | 無登記合約。 |
| `Systems/cochange-guard.md` | 僅技術債，未受影響。 |
| `Systems/check-r-guard.md` | 無登記合約。 |
| `Systems/節點範圍與索引守衛.md` | 抽取器、索引範圍及 doctor 段落均未變。 |

## 實際驗證

- 凍結 patch 1,455 行已逐 hunk 閱讀；SHA256 符合 `15816452e6d94bcc59ccec186ff3ccdaf69c71221c91f23cdbe6efce26cbf53f`。
- `git diff -U10 before after -- 四檔` 的 SHA256 同樣吻合。
- `git diff --check` 通過。
- 四檔 AST 解析通過。
- 唯讀純函式驗證通過：100 筆同題超額資料被限成每題一場，結果為 `n=2`、M1 `0.5`、超額 `99`；錯型 calls 被拒收；零模式不碰帳本路徑。
- 使用記憶體 SQLite 獨立驗證冷卻、窗口過期、兩次 claim、回撥拒絕及兩執行緒競爭最後一格，結果只有一個 claim 成功。
- `TestScenarioProbeAblation` 共 32 案：15 案通過；17 案因唯讀環境沒有可用暫存目錄而在 fixture 建立前報錯，未視為程式故障。
- 未啟動真模型、付費 API、push 或圖譜寫入。

## 未驗與範圍

未能實跑需檔案寫入的 SQLite、多 OS 程序死亡、五秒鎖逾時、跨日期歸檔及完整 CLI 暫存 repo 案例。未讀其他審查員報告、作者處置清單、staging 與作者 raw logs；未把作者測量當本席證據。未讀凍結 patch 外的無關大型測試段落。閱讀預算未耗盡；本報告涵蓋完整指定 patch，但不是整個 63 檔提交的全面重審。