severity: major  
findings: 2

ID: COR-1  
severity: major  
blocking: 是  
引句:「簿記目錄也可能有真程式；沿每支檔有家與留痕的既有例外，未知模式不排除。」  
file: `scripts/lumos:41021`

可執行檔先通過簿記目錄判斷，隨後仍會被全域副檔名規則排除。具體輸入是 Git mode `100755` 的可執行 `.md`、`.jsonl` 或 governance `.json`；它們在 `scripts/lumos:41025` 被回傳 `False`。現有 code-loop 定義卻明定 `100755` 不分副檔名一律是程式，且已有可執行 `.md` 控制案例。

file: `scripts/lumos:44293`  
file: `scripts/test_lumos.py:59330`

現場無寫入探針：

```text
governance/review-reports/case/run.md    100755 -> False
governance/review-reports/case/run.jsonl 100755 -> False
governance/review-reports/case/run.json  100755 -> False
對照 run.txt / run.patch / tool.py       100755 -> True
```

同一過濾器同時供 impact 與共享角色清單使用，因此這類合法程式會同時漏掉家、事故節點及角色鏡頭，而不只是附件降噪不完整。

file: `scripts/lumos:24383`  
file: `scripts/lumos:41135`

ID: COR-2  
severity: major  
blocking: 是  
引句:「簿記分類沿用 _BOOKKEEPING_FILES/_BOOKKEEPING_DIRS,卷證不是程式;」  
file: `scripts/lumos:41016`

普通模式、無副檔名的卷證會全部被誤納。`_nodehome_code_kind` 對任何無副檔名路徑只回傳待查的 `shebang?`，但新過濾器把「不是 None」直接當程式，沒有像既有 code-loop 判法那樣讀凍結版本首行確認 `#!`。

file: `scripts/lumos:26731`  
file: `scripts/lumos:44293`

現場無寫入探針：

```text
governance/replay/.weekly-stamp       100644 -> shebang? -> True
governance/replay/.rotation-cursor    100644 -> shebang? -> True
governance/review-reports/case/report 100644 -> shebang? -> True
```

前兩支是 HEAD 中真實存在的普通簿記檔；既有測試也明定正常上限內的游標與非 shebang 戳記應視為簿記。

file: `governance/replay/.weekly-stamp:1`  
file: `scripts/test_lumos.py:59349`

因此只要無副檔名報告含歷史程式片段，它仍會進 impact 種子並誤觸事故；這直接漏掉本修補要排除的一類歷史附件。

固定席前 8：

1. `Systems/pitfalls-code-loop.md`：受影響；兩項 finding 都是既有簿記程式例外沒有完整沿用。
2. `Systems/lumos-cli-read.md`：不影響 search 的 superseded/stale 合約。
3. `Systems/loop-convergence-recording.md`：記帳語意未改，但無副檔名卷證仍會被當程式輸入。
4. `Systems/bound-tests-gate.md`：閘本身未改；COR-1 可能先漏掉程式的家，使後續固定席與綁定測試輸入不完整。
5. `Systems/guard-kill.md`：未碰 rc 優先序或 JSON 純度。
6. `Systems/授權與歸屬.md`：未碰 vendored toolkit 或授權檔。
7. `Systems/測試假綠形態.md`：受影響；新增綠測試沒有涵蓋可執行 `.md` 與普通無副檔名卷證。
8. `Systems/lumos-cli-lifecycle.md`：未碰 reinject 邊界。

其餘固定席：

- `Systems/reversibility-governance-ledger.md`
- `Systems/design-loop.md`
- `Systems/doctor-irreversible-hint.md`
- `Systems/lumos-deinit.md`
- `Systems/check-t-sentinel.md`
- `Systems/lumos-refcheck.md`
- `Systems/check-r-guard.md`
- `Systems/cochange-guard.md`
- `Systems/節點範圍與索引守衛.md`
- `Systems/canary-audit.md`
- `Systems/slim-get-一行安裝.md`
- `Systems/slim-install-安裝器.md`
- `Systems/slim-uninstall-一行卸載.md`
- `Projects/雙向門放行_計劃.md`
- `Projects/規格落成可驗收條件_計劃.md`
- `Projects/逃逸自動記_計劃.md`
- `Systems/core-invariant-baseline.md`
- `Systems/judge-severity-gate.md`

資料狀態五問：

- 新舊互讀：COR-2 會把舊卷證重新當成新程式輸入。
- 寫一半：本改動只讀 Git metadata，未見部分寫入狀態。
- 衍生資料：模式來源使用凍結 Git 差異；失敗會回 `None`，普通路徑維持快速入口，這兩點正確。
- 時間：沒有時間戳判斷。
- 不可逆：沒有刪除、覆寫或外部送出。

材料與證據邊界：

- 完整讀完 `r2-source.patch` 246 行、`r2-graph.patch` 181 行及 `r2-delta.patch` 223 行。
- `r2-materials.json` 的 HEAD/base/repair-base、行數及四份 SHA-256 均相符。
- `r2-snapshot.patch` 只核對 2165 行及 SHA-256，未全文閱讀。
- `r1-code-control-red.json` 的來源 SHA 對應修補前 `87ec79df`，只跑單一控制案例。
- 兩份 repair green 的來源 SHA 均對應凍結 HEAD 的 `scripts/lumos`；範圍分別是 4 個 impact_diff 案例與 15 個 review_role 案例，不涵蓋上述反例。
- spec push-check 與 lint artifact 沒有可綁定的來源 SHA；只採信各自記錄的命令邊界。
- fix-check 的 base/head 與材料相符，但屬編排者保存證據，不冒稱本席現場實測。
- 本席只執行純函式與 Git 唯讀探針，沒有重跑測試子集或完整 impact/lens。一次 heredoc 在 shell 建立暫存前即因無可寫暫存目錄被拒，未執行程式，不計測試紅綠。
- 舊 name-only 改名舊路徑缺口、Windows 及 Python 結果判讀均未驗，亦未宣稱 `--raw --no-renames` 已解完整 rename 問題。