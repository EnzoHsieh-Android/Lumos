severity: major
findings: 1

ID: COR-1
severity: major
blocking: 是
引句:「if f in _BOOKKEEPING_FILES or f.startswith(_BOOKKEEPING_DIRS):」
file: `scripts/lumos:41018`

新條件把簿記目錄內的真正程式也無條件排除。具體輸入 `governance/review-reports/x/run.sh` 依既有 `_nodehome_code_kind` 判為程式 `ext`，但 `_impact_diff_seed_ok` 回傳 `False`；它會在 `cmd_impact_diff` 的 `scripts/lumos:41114` 被跳過，也會經 `scripts/lumos:24382` 從角色鏡頭消失，導致該程式的家、事故與後端角色卡全部漏掉。

這違反既有簿記定義：`scripts/lumos:44272` 明定簿記目錄內仍要辨認程式檔，`scripts/test_lumos.py:58973` 也已用同一路徑下的 `run.sh` 釘住「不算簿記」。新增測試反而把 `governance/code-loop/case/example.py` 當附件並期待全部種子為空，沒有加入 `.py`／`.sh` 真程式保留的對照組。

最小現場探針：

```text
counterexample=governance/review-reports/x/run.sh
code_kind= ext
impact_seed_ok= False
adjacent_seed_ok= True
deleted_seed_ok= True
```

應讓 `.patch/.txt/.diff` 等卷證被排除，同時沿既有程式辨識保留簿記目錄內的真程式，並補 `.py`／`.sh` 正向控制。相鄰 `review-reports-other`、一般刪檔與附件追蹤本身均正常。

固定席逐條答覆：

- `Systems/pitfalls-code-loop.md`：受影響；簿記目錄內真程式的既有例外被新入口吞掉，即 COR-1。
- `Systems/lumos-cli-lifecycle.md`：不影響 sentinel 外內容保存。
- `Systems/lumos-cli-read.md`：不影響 search 的 superseded/stale 過濾。
- `Systems/bound-tests-gate.md`：未改合約測試執行或結果判讀。
- `Systems/guard-kill.md`：未改 rc 優先序或 JSON stdout。
- `Systems/授權與歸屬.md`：未改 vendored 白名單、授權檔或檔頭。
- `Systems/測試假綠形態.md`：真 CLI 紅綠確實跑到入口，但測試把 `.py` 預設成附件，缺少證明「被排除者不是正式程式」的反例，因此沒有守住語意邊界。
- `Systems/design-loop.md`：未改處置閘或審材判定。

其餘固定席只列名：`loop-convergence-recording.md`、`lumos-deinit.md`、`check-t-sentinel.md`、`reversibility-governance-ledger.md`、`check-r-guard.md`、`cochange-guard.md`、`doctor-irreversible-hint.md`、`節點範圍與索引守衛.md`、`lumos-refcheck.md`、`slim-uninstall-一行卸載.md`、`canary-audit.md`、`slim-get-一行安裝.md`、`slim-install-安裝器.md`、`雙向門放行_計劃.md`、`規格落成可驗收條件_計劃.md`、`逃逸自動記_計劃.md`、`judge-severity-gate.md`、`core-invariant-baseline.md`。

資料狀態五問：

- 新舊互讀：沒有新增持久格式，不適用。
- 半完成輸入：沒有寫入流程；但程式改名或新增到簿記目錄仍會被 COR-1 漏掉。
- 衍生資料：impact manifest 與角色卡可重算，但目前會從錯誤的缺檔種子重算。
- 時間：未新增時間語意。
- 不可逆：未新增刪除或覆寫；附件仍由 Git 追蹤。

實讀與驗證邊界：

- 完整讀完 `r1-source.patch` 103 行、`r1-graph.patch` 162 行。
- 核對 base/HEAD 與兩份 patch SHA-256；`r1-snapshot.patch` 僅核對 463 行及指紋，未冒稱讀完正文。
- 讀取保存卷證：紅 6/4、impact 綠 35/0、role 綠 59/0，且 source SHA 分別吻合 base 與目前 `scripts/lumos`。
- `r1-pitfalls.json` 只有 Ruff claims；新增 hunk 命中 0，無 stack questions。
- 現場只跑無寫入分類探針與 `git diff --check`；未重跑需暫存 Git repo 的測試、全套、完整 impact/lens 或 Windows。
- 未讀其他席報告、混合分支報告、派工或 intake；未寫 repo。