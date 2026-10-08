severity: clean

seat: code-probe-postreview-dispatch-ledger/r4/邊界4-codex  
blocking: 否  
findings: 0

凍結 patch 引句錨點（非 finding）：

引句:「本機共用帳五小時內最多記幾次模型啟動意圖(含失敗與重試)；0=停用記帳，不管其他工具或帳號總量」  
file: `governance/eval/ablation_lumos_first.py:521`

引句:「持久窗口額度已滿或初始化冷卻中，未啟動子程序」  
file: `governance/eval/ablation_lumos_first.py:264`

材料核對：

- before：`532f5a15c05ce547c8305e0d30492e5d3c8845a0`
- after：`05e87b5476cf161a203382a50ef008b374e60a31`
- 凍結 patch：SHA256 `15816452e6d94bcc59ccec186ff3ccdaf69c71221c91f23cdbe6efce26cbf53f`
- 凍結 patch：1455 行，已逐 hunk 讀完。
- 四個固定檔案均與 after 提交 byte-level diff 相符；`git diff --check` rc0，四檔 AST 解析成功。
- 未讀其他審查員報告、作者處置清單及本輪 staging 內容。

四檔覆蓋：

- `governance/eval/ablation_lumos_first.py:136`
  - 原問題：同題超額結果、錯型 calls、跨目錄額度歸零、事故恢復漏列 pending、報表原始 HTML／來源 meta 改寫均有對應修補。
  - before/after 同案例實跑：
    - 一百筆題 A 成功加一筆題 B 失敗、`runs=1`：before 為 `n=101, rate=0.9901`；after 為 `n=2, rate=0.5, excluded_surplus=99`。
    - `calls=[42]`：before 未拒收；after 回「逐場工具呼叫內容型別錯誤」。
    - `<img …>` 題號、來源與事故檔名：before 保留原始 HTML；after 全部轉成文字。
  - 父派工傳參獨立驗證：剩餘額度 7、窗口 9、要求 3 場時，實際子命令帶 `--runs 3 --max-attempts 7 --max-per-window 9 --attempt-ledger /dev/null`；model 參數亦保留。
  - 帳本查詢 fatal 獨立驗證：父程序未呼叫子程序、設置 stop、回傳批次失效。
  - 自訂帳路徑由 `_run_locked_batch` 傳至 `run_job`，未被替換成預設值。
  - 既有 merge、workers、arms、結果升格與鎖定相鄰路徑未見回歸。

- `scripts/scenario_probe.py:711`
  - 原問題：新增 SQLite `BEGIN IMMEDIATE` 持久 launch-intent、五小時冷卻、時鐘回撥與壞帳 fail-closed；Claude/Codex runner 均在 scenario 預驗及沙盒驗收後、模型 subprocess 前 claim。
  - 獨立 runner 驗證：
    - 缺 `expect` 的非法 scenario 在 claim 前返回，模型呼叫數 0。
    - `/dev/null` 作為非一般檔帳本時，Claude 與 Codex runner 均拋 `ProbeAttemptLedgerError`，模型呼叫數 0。
    - `max-per-window=0` 時兩個 runner 均完全略過帳本並各呼叫一次假模型；`claim_model_attempt(..., 0)` 不開帳。
  - 真 CLI 相鄰輸入：
    - `scenario_probe.py --max-per-window -1` → rc2。
    - `scenario_probe.py --max-per-window 0 --dry-list` → rc0。
    - help 明列本機同帳、五小時、首次冷卻與 0 停用邊界。
  - 供應商 limit 後先核對本批與持久額度、額度盡時不 sleep 的控制路徑完整；未見重試繞過帳本。

- `scripts/test_autonomous_loop.py:1852`
  - 已讀全部新增／修改 hunk。
  - 競爭最後一格、父程序死亡、壞帳、鎖逾時、跨日期、歸檔、非法 scenario、冷啟與零值均有測試。
  - 測試包含現場成立證據：ready marker、兩進程輸出、一個 `.launched`、實際模型假呼叫計數、持久剩餘量與事故檔欄位；未違反「測試假綠形態」合約。
  - 舊 `runs_in_window` 測試已明確降為診斷視圖，硬額度改驗持久帳，沒有把舊算法繼續冒充守衛。

- `scripts/test_lumos.py:37587`
  - 已讀全部新增／修改 hunk。
  - 舊 probe 測試顯式使用 `--max-per-window 0`，保留原本無帳本的相鄰測試語意。
  - 新測試由真 `main`／merge／父派工入口驗 fatal、零等待、超額計分、錯型 calls、恢復三路徑及報表轉義。
  - 每組修補測試都有前置現場斷言，例如 101 筆原始列、三份事故產物、題號確實進入不一致清單；未見只驗替身算法的假綠。

獨立執行：

- `git diff --check before after -- <四檔>`：rc0。
- 四檔 after 版本 AST 解析：4/4 成功。
- ablation 負窗口真 CLI：rc2。
- scenario probe 負窗口真 CLI：rc2。
- scenario probe 零值 dry-list：rc0。
- Claude/Codex runner：非法題、帳本拒收與零值相鄰輸入均以假 subprocess 獨立執行，未發出真模型。
- 父派工 command vector、fatal stop 與自訂帳路徑傳遞：獨立執行通過。

未驗：

- 唯讀沙箱禁止 `mktemp`，錯誤為 `Operation not permitted`；因此實體 SQLite 建帳、兩進程真鎖競爭、程序死亡後持久性、跨日期、檔案歸檔恢復及 meta byte-preservation 未能由本席獨立執行。這是環境限制，不列程式故障。
- 作者 raw 顯示 `implementation-ablation-corrected.log` 為 32 tests OK、`implementation-probe-boundary-corrected.log` 為 138 passed、`implementation-parent-race.log` 為 1 test OK；僅列為作者測量，不冒稱本席執行。
- 未發出真模型、付費 API、push，亦未修改工作樹或圖譜。
- 未讀凍結 delta 以外的大量不相干 unchanged 實作；相關 caller、runner、CLI、計分、恢復與測試上下文已讀。閱讀預算未耗盡。

固定圖譜鏡頭：

- `Systems/ablation-lumos-first.md`：無登記合約；持久帳、結果拒收及計分修補符合責任範圍。
- `Systems/codex-harness.md`：無登記合約；Codex runner 只增加模型前 claim，既有 command/env/result 路徑保持。
- `Systems/測試假綠形態.md`：未破壞；新增測試均有前置現場成立或實際呼叫計數。
- `Systems/autonomous-iteration-loop.md`：無登記合約；未改 loop 實作。
- `Systems/lumos-cli-read.md`：search superseded 合約未觸及。
- `Systems/lumos-cli-lifecycle.md`：re-inject byte-equal 合約未觸及。
- `Systems/bound-tests-gate.md`：固定席綁測試 gate 合約未觸及。
- `Systems/canary-audit.md`：record readback 與 second telemetry 兩合約未觸及。
- `Systems/design-loop.md`：處置閘第五步合約未觸及。
- `Systems/guard-kill.md`：rc 優先序與 JSON purity 合約未觸及。
- `Systems/slim-get-一行安裝.md`：PowerShell ASCII/BOM 與 `$Args` 合約未觸及。
- `Systems/slim-install-安裝器.md`：七條安裝／注入／manifest／Windows 合約均未觸及。
- `Systems/slim-uninstall-一行卸載.md`：六條獨立清理、備份、還原、shim、manifest 合約均未觸及。
- `Systems/授權與歸屬.md`：vendored 授權檔與 SPDX 合約未觸及。
- `Projects/規格落成可驗收條件_計劃.md`：無登記合約；未觸及。
- `Systems/lumos-deinit.md`：無登記合約；未觸及。
- `Projects/逃逸自動記_計劃.md`：無登記合約；未觸及。
- `Systems/cochange-guard.md`：僅技術債鏡頭；未觸及。
- `Systems/check-r-guard.md`：無登記合約；未觸及。
- `Systems/節點範圍與索引守衛.md`：九條抽取、索引、排序、閘名與治理帳合約均未觸及。

原問題判定：修補後的可獨立執行部分已修好；實體持久 SQLite 部分由程式路徑與作者 raw 支持，但因唯讀環境標為本席未驗。  
既有行為判定：零值停用、非法輸入拒收、兩個 runner 及父派工相鄰路徑保持。  
回歸判定：凍結 delta 與可執行範圍內未發現具體回歸；沒有未判定 finding。

總結：最嚴重 severity=clean；blocking=0。