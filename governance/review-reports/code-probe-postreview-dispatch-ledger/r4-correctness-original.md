severity: major

## Finding COR4-001

severity: major

blocking: 是

引句:「if len(meta) != 1 or type(meta[0][0]) is not float or not math.isfinite(meta[0][0]):」

file: `scripts/scenario_probe.py:753`

具體輸入：既有一般 SQLite 檔，`user_version=1`、表與欄位皆可查，但唯一的 `ledger_meta.initialized_at=-1.0`，無 launch-intent；`now=20000.0`、limit=1。

預期路徑：負 Unix epoch 是邏輯壞帳，應拋 `ProbeAttemptLedgerError`；父派工器留下 `attempt-ledger` 事故、設定 stop，模型零啟動。

實際路徑：第 753 行只驗型別與 finite，`-1.0` 通過；第 759 行不構成回撥；第 762 行視為冷卻早已結束，回傳剩餘 1；claim 隨後寫入意圖，runner 可繼續啟動模型。

本席唯讀等價重現使用固定版 helper、in-memory SQLite，僅替換不可寫的檔案系統介面，實際輸出：

```text
remaining= 1
claim= True
stored= -1.0 1
```

最小驗證命令（需可寫 `/tmp`）：

```sh
PYTHONDONTWRITEBYTECODE=1 python3.14 -c 'import sqlite3,tempfile; from pathlib import Path; import scripts.scenario_probe as p; d=Path(tempfile.mkdtemp())/"u.sqlite3"; c=sqlite3.connect(d); c.executescript("CREATE TABLE ledger_meta (id INTEGER PRIMARY KEY CHECK(id=1), initialized_at REAL NOT NULL); CREATE TABLE launch_intents (claimed_at REAL NOT NULL CHECK(typeof(claimed_at)='\''real'\'' AND claimed_at>=0)); CREATE INDEX intents_time ON launch_intents(claimed_at); PRAGMA user_version=1;"); c.execute("INSERT INTO ledger_meta VALUES (1,?)",(-1.0,)); c.commit(); c.close(); print(p.attempt_ledger_remaining(d,1,now=20000.0),p.claim_model_attempt(d,1,now=20000.0))'
```

預期應拋帳本錯誤；現碼輸出 `1 True`。

最小修法：建立表時替 `initialized_at` 加 `typeof(...)='real' AND initialized_at>=0` 約束，並在讀取既有帳時顯式拒絕負值；只改 DDL 無法處理已存在的壞帳。測試須先斷言 fixture 確實存有 REAL 負值，再斷言父派工器不呼叫子程序且保留事故證據。

同案例前後歸因：未判定。`532f5a15` 沒有持久 SQLite 帳或此輸入介面，無法對同一壞帳案例做兩版行為比較；不因它出現在修後就稱為修補回歸。

## 四檔覆蓋

- `governance/eval/ablation_lumos_first.py`：完整讀完全部 hunks；核對父程序查帳、子程序參數、結果檔篩選、每題權重、報表轉義及 meta 不覆寫。除上游帳本驗證缺口外無新增 finding。
- `scripts/scenario_probe.py`：完整讀完全部 hunks；核對 SQLite 交易、兩種 runner、重試、fatal、時間窗與 CLI。COR4-001 位於此檔。
- `scripts/test_autonomous_loop.py`：完整讀完全部 hunks；涵蓋冷啟、競爭、啟動失敗、跨日、程序死亡、父程序競爭及舊 shard。
- `scripts/test_lumos.py`：完整讀完全部 hunks；既有案例以零模式保持舊路徑，新案例涵蓋停派、超額列、錯型 calls、恢復清單及報表來源。沒有負 `initialized_at` 或等價壞 schema 案例。

四檔均可在記憶體中 `compile()`；`git diff --check` 無輸出。

## 原問題、既有行為與回歸

- 原問題「失敗結果歸檔或換日期後額度歸零」：新權威來源已移至輸出目錄外的 SQLite，意圖 commit 後不因歸檔退款；靜態路徑符合修法。因唯讀環境不能建立 file-backed fixture，本席獨立同案例實跑未驗，不能把作者 log 冒稱本席驗證。
- 相鄰衍生資料問題：已獨立比較兩版。100 筆題 A 成功加一筆題 B 失敗，before=`n=101, rate=.9901`，after=`n=2, rate=.5, excluded_surplus=99`，修好。
- 錯型 calls：同一資料 before 接受，after 回報「逐場工具呼叫內容型別錯誤」，修好。
- 正常統計保持：一成功一失敗在兩版皆為 `n=2, rate=.5`。
- 零模式保持：實跑 `remaining=None`、`claim=True`，指定不可寫路徑仍未建立檔案。
- 新修補回歸：沒有取得可比兩版證據。COR4-001 歸因維持未判定。

## 五問

- 新舊互讀：舊 shard 命名仍收；舊版執行器不納入帳本是明訂邊界，須人工先停。版本 1 邏輯壞帳的互讀存在 COR4-001。
- 半寫入：claim 在 `BEGIN IMMEDIATE` 交易內 commit 後才啟動；程序死在 commit 後會保守占額，不退款。file-backed 中斷未由本席實跑。
- 衍生資料：結果檔只供計分；帳本才是額度權威。超額有效列留在原始資料但不加權，正常案例保持。
- 時間：`claimed_at <= now-18000` 過期，恰五小時可用；時鐘回撥至初始化或最新意圖之前會停止。跨機不在保證範圍。
- 不可逆：帳本只追加意圖；失敗、取消、歸檔均不刪。純合併不再覆寫壞 meta 原始 bytes；恢復採歸檔三個可能路徑。

## 固定圖譜鏡頭

| 節點 | 判定 |
|---|---|
| Systems/ablation-lumos-first | 無登記合約；主要責任路徑已讀，COR4-001 是計劃 S3 的壞帳邊界。 |
| Systems/codex-harness | 無登記合約；兩種 runner 都在 subprocess 前 claim。 |
| Systems/測試假綠形態 | 未改兩支綁定 slim 測試；新增帳本測試未覆蓋 COR4-001。 |
| Systems/autonomous-iteration-loop | 無登記合約；只增加相關測試，未改 loop runtime。 |
| Systems/lumos-cli-read | search 合約路徑未觸及。 |
| Systems/lumos-cli-lifecycle | re-inject 合約路徑未觸及。 |
| Systems/bound-tests-gate | bound-tests 合約路徑未觸及。 |
| Systems/canary-audit | 兩條落盤／telemetry 合約未觸及。 |
| Systems/design-loop | 處置閘第五步未觸及。 |
| Systems/guard-kill | rc 優先序與 JSON 純度未觸及。 |
| Systems/slim-get-一行安裝 | PowerShell 兩條合約未觸及。 |
| Systems/slim-install-安裝器 | 七條安裝合約未觸及。 |
| Systems/slim-uninstall-一行卸載 | 六條卸載合約未觸及。 |
| Systems/授權與歸屬 | vendoring／授權檔合約未觸及。 |
| Projects/規格落成可驗收條件_計劃 | 無登記合約；未觸及。 |
| Systems/lumos-deinit | 無登記合約；未觸及。 |
| Projects/逃逸自動記_計劃 | 無登記合約；未觸及。 |
| Systems/cochange-guard | 僅技術債；未觸及。 |
| Systems/check-r-guard | 無登記合約；未觸及。 |
| Systems/節點範圍與索引守衛 | 雖共用 `scripts/test_lumos.py`，本次 hunks 僅在探針測試區；九條合約及綁定測試未改。 |

## 實際執行、未驗與閱讀界線

- 已核對 snapshot SHA256=`15816452e6d94bcc59ccec186ff3ccdaf69c71221c91f23cdbe6efce26cbf53f`、1455 行，逐 hunk 全讀；before/after 與 ancestry 均吻合。
- 9 個 file-backed 目標測試嘗試執行，但全部在 `TemporaryDirectory()` 前置因唯讀沙盒無可寫暫存目錄而失敗；未進產品邏輯，不算程式紅燈。
- 作者 raw log 的尾端顯示 corrected suites 為 32、30、138、3 項通過；僅記為作者測量，不算本席獨立執行。
- 未發真模型、付費 API、push、圖譜寫入；未讀其他審查員報告、作者處置清單或 staging。
- 閱讀量已超過單席 1800 行預算：依派工要求仍完整讀完凍結 patch，額外上下文限於固定版本相關函式、完整持久帳計劃及第二計劃相關條款。未重審四個完整大檔的非 hunk 區域，也未全文讀第二計劃與 raw logs；因此不是全 repo 通過。

總結：max severity major，blocking 1。