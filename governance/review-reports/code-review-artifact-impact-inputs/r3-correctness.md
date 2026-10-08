severity: major
findings: 1

ID: R3-COR-1  
severity: major  
blocking: 是  
引句:「一般改名仍取新路徑；只有簿記終點被排除時，不能把舊程式刪除一起藏掉。」  
file: `scripts/lumos:24432`  
file: `scripts/lumos:24433`

跨簿記改名的舊側補回只檢查 `new.startswith(_BOOKKEEPING_DIRS)`，沒有涵蓋同一分類來源中的 `_BOOKKEEPING_FILES`。因此把 `src/api.py` 以 R100 改名成 `governance/anchor-baseline.json` 時：

1. 新路徑先進入 `out`。
2. 因終點不在 `_BOOKKEEPING_DIRS`，舊路徑不會補回。
3. 最後的新路徑又因屬 `_BOOKKEEPING_FILES` 被排除。
4. 共享角色選檔結果成為空清單，真實後端程式的刪除不會計入角色統計，也不會附後端角色卡。

`impact --diff` 因使用 `--no-renames` 仍能保留舊路徑，所以這是兩個正式消費者間的分類漂移。修正不必把固定帳檔本身當程式；只要舊側補回條件同時辨識 `new in _BOOKKEEPING_FILES`，並增加固定帳檔終點的改名控制。

現場無寫入探針：

```text
輸入：
R100  src/api.py -> governance/anchor-baseline.json
old/new mode 都是 100644

_review_role_changed_files(...) 輸出：
[]

對照：
R100  src/api.py -> governance/review-reports/case/report.txt

輸出：
[('src/api.py', '<base>')]
```

## 固定席前 8

1. `Systems/pitfalls-code-loop.md`：有影響。凍結 mode/OID、共用 raw parser、零預算及剩餘時間路徑未見回歸；但固定帳檔終點仍會讓共享角色入口漏掉舊程式，見 R3-COR-1。
2. `Systems/lumos-cli-read.md`：未破壞 search 排除 superseded、保留 stale 的合約；本次沒有改 search 分岔。
3. `Systems/bound-tests-gate.md`：未改 bound-tests 的執行、懸空／偽證據／unfilterable 判準。
4. `Systems/guard-kill.md`：未改 rc 優先序或 JSON stdout 純度。
5. `Systems/授權與歸屬.md`：未改 `_VENDORED_TOOLKIT`、deinit 授權檔保留或 `scripts/lumos` 檔頭。
6. `Systems/測試假綠形態.md`：可執行 `.txt/.patch` 控制具有實際執行前置斷言；但新增跨邊界測試沒有涵蓋 `_BOOKKEEPING_FILES` 終點。
7. `Systems/lumos-cli-lifecycle.md`：未碰 re-inject 或 sentinel 外內容保留。
8. `Systems/design-loop.md`：未碰處置閘第五步、條款綁定或設計審材料格式判定。

其餘固定席：

- `Systems/loop-convergence-recording.md`
- `Systems/reversibility-governance-ledger.md`
- `Systems/lumos-deinit.md`
- `Systems/check-t-sentinel.md`
- `Systems/doctor-irreversible-hint.md`
- `Systems/cochange-guard.md`
- `Systems/節點範圍與索引守衛.md`
- `Systems/check-r-guard.md`
- `Systems/lumos-refcheck.md`
- `Systems/canary-audit.md`
- `Systems/slim-get-一行安裝.md`
- `Systems/slim-install-安裝器.md`
- `Systems/slim-uninstall-一行卸載.md`
- `Projects/雙向門放行_計劃.md`
- `Projects/規格落成可驗收條件_計劃.md`
- `Projects/逃逸自動記_計劃.md`
- `Systems/core-invariant-baseline.md`
- `Systems/judge-severity-gate.md`

## 實讀與核對

- 已完整閱讀 `r3-source.patch` 708 行及 `r3-graph.patch` 358 行。
- `r3-materials.json` 的 base、HEAD、行數與三份 SHA-256 均核對相符。
- `r3-source.patch` 與指定範圍的兩支程式 diff 位元相符；`r3-graph.patch` 與 `core.quotePath=false` 的圖譜 diff 位元相符。
- `r3-snapshot.patch` 僅核對 24,441 行及 SHA-256，未冒稱全文閱讀。
- 已讀四份允許的機械證據。`r2-delivery-fix-check.json` 綁目前 HEAD；舊 HEAD 46ec9e7d、77ad08f3 的兩支程式 blob 與目前 HEAD 相同。`r2-integrated-subsets.json` 本身未帶 HEAD／來源雜湊，因此只作既有執行紀錄，不當本席現場實測。
- 現場只做無寫入分類矩陣、共享角色改名探針、AST 解析與 `git diff --check`；沒有執行測試套件或重算完整鏡頭。

## 未驗界線

- Windows 依指示排除。
- 未涵蓋原混合分支的 Python 測試結果判讀。
- 沒有宣稱封住既有設定讀取、name-status 或角色內容兩趟讀取的全部正預算成本；只核查本次新增 raw／首行分類的剩餘時間傳遞。
- 換行 basename 的既有限制未擴 parser；本次只核對已登記且能由單檔入口成立的 tab 完整路徑與換行目錄控制。
- 未讀其他席、歷史 raw 報告、intake、dispatch 或混合分支。