severity: major  
findings: 1

ID: ARCH-1  
severity: major  
blocking: 是  
標題: 可執行的文件／JSON 檔仍被排除，impact 與角色清單會漏掉合法程式

引句:「程式副檔名、無副檔名與可執行檔保留，未知模式不排除；已刪檔用刪除前模式，staged 用索引模式。」

file: `scripts/lumos:41025`

`_impact_diff_seed_ok` 先讓 mode `100755` 通過簿記目錄判斷，卻又無條件套用後面的 `.md`、`.json`、`.jsonl` 排除。因此以下合法程式會回 `False`：

```text
governance/review-reports/case/run.md    mode 100755
governance/review-reports/case/run.json  mode 100755
governance/review-reports/case/run.jsonl mode 100755
```

這和既有 `_codeloop_bookkeeping_code` 的模式相反；後者明確把任何 `100755` 檔案視為程式，見 `scripts/lumos:44293`、`scripts/lumos:44308`。實際後果同時落到：

- `impact --diff`：檔案不進種子，家、事故與合約固定席可能漏掉，見 `scripts/lumos:41129`。
- 共享角色清單：同一檔案也被剔除，角色卡不會看到它，見 `scripts/lumos:24383`。
- 依 impact 固定席執行的 bound-tests 可能因此少跑相關合約測試。

HEAD 現場無寫入探針結果：

```text
run.md:    impact_seed=False code_loop_program=True
run.json:  impact_seed=False code_loop_program=True
run.jsonl: impact_seed=False code_loop_program=True
run.txt:   impact_seed=True  code_loop_program=True
run.patch: impact_seed=True  code_loop_program=True
```

新增測試只涵蓋 `.py`、`.sh`、可執行 `.txt`／`.patch`、無副檔名及刪檔，未覆蓋會被後段規則再次排除的三種副檔名，見 `scripts/test_lumos.py:23089`。修法應讓簿記目錄的可執行程式例外在一般文件／JSON 排除前直接成立，同時維持 `_BOOKKEEPING_FILES` 的固定帳檔排除，並補三種反例。

架構三問

1. 分層與依賴方向：部分對齊。新 helper 沿用 `_BOOKKEEPING_*`、`_nodehome_code_kind`、`_codeloop_raw_modes`，位置與依賴方向合理；但 ARCH-1 讓 impact 層和既有 code-loop 層形成兩種可執行檔語意。對照 `scripts/lumos:41015`、`scripts/lumos:44293`。
2. 命名與錯誤形狀：對齊。普通路徑不查模式；簿記 metadata 失敗回 `None`，CLI 轉 rc2，角色消費者回無角色資料，沒有新增另一種例外形狀。對照 `scripts/lumos:41032`、`scripts/lumos:41129`、`scripts/lumos:24383`。
3. 第二種做法：沒有新增目錄表或 raw parser；但 ARCH-1 形成第二套「可執行檔是否為程式」結果，屬具體跨層不一致。

不對齊共 1 條，其中 major 1 條。

資料狀態五問

1. 新舊互讀：相關。刪檔取舊 mode、非刪檔取新 mode；rename 以 `--no-renames` 拆成舊刪除／新增路徑，結構對齊。ARCH-1 在取得正確 mode 後仍錯誤排除。
2. 寫一半：不相關；本改動只讀 Git 差異與模式，不寫持久狀態。
3. 衍生資料：相關。impact manifest 與角色清單共用同一過濾入口，所以 ARCH-1 會同步污染兩份衍生結果。
4. 時間：不相關；沒有時間戳、過期或時鐘判斷。
5. 不可逆：不相關；沒有刪除、覆寫或外部送出。

固定席前 8

1. `Systems/pitfalls-code-loop.md`：未改 pitfalls 分級與留痕；只沿用其簿記分類。ARCH-1 影響 impact／role，不改原 pitfalls 消費者。
2. `Systems/lumos-cli-read.md`：未碰 search 的 superseded／stale 過濾與三路輸出。
3. `Systems/loop-convergence-recording.md`：未改 loop 帳、收斂或記錄格式。
4. `Systems/bound-tests-gate.md`：間接受影響；ARCH-1 可使合法程式及其家消失於 impact，進而少選固定席綁定測試。
5. `Systems/guard-kill.md`：未改 kill rc 優先序或 JSON stdout 規則。
6. `Systems/授權與歸屬.md`：未改 vendored 白名單、deinit 或 SPDX／LICENSE 行為。
7. `Systems/測試假綠形態.md`：`.txt`／`.patch` 有執行前置斷言，但測試期望集合未包含會被後段排除的可執行 `.md`／`.json`／`.jsonl`；ARCH-1 可在目前綠證據外存活。
8. `Systems/lumos-cli-lifecycle.md`：未改 CLAUDE.md sentinel 重注入。

其餘固定席

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

材料與證據邊界

- 完整閱讀：`r2-source.patch` 246 行、`r2-graph.patch` 181 行、`r2-delta.patch` 223 行；delta 與 source 重疊部分未重複計數。
- `r2-materials.json` 的 base、repair base、HEAD、行數及四份 SHA-256 均相符。
- `r2-snapshot.patch` 只核對 2165 行與 SHA-256，未全文閱讀。
- `r1-code-control-red.json` 的 source SHA 對應修補前 `87ec79df…`，實際邊界為單一測試、5 過 10 敗。
- `r1-repair-impact-green.json` 與 `r1-repair-role-green.json` 的 source SHA 均等於凍結 HEAD 的 `scripts/lumos`；分別只證 4 案例／50 斷言與 15 案例／59 斷言。
- `r1-repair-spec-push-check.json` 記錄 rc0 與 `ce2a961f..HEAD`，但沒有 source SHA／frozen HEAD，不能獨立釘到精確版本。
- `r1-repair-lint-new.json` 沒有來源 SHA 或 diff range，只能視為保存的 lint verdict。
- `r1-fix-check-result.json` 明載 base `87ec79df…`、head `ca6701b…`、rc0；這是編排者保存證據，不是本席現場實測。
- 現場成功探針另確認：普通路徑回 `{}` 且不查 mode；簿記 metadata 失敗回 `None`；rename raw 使用 `--no-renames -z`；staged 傳入 `--staged`。
- 未跑全套、未重新計算完整 impact／lens、未驗 Windows。第一次 here-document 探針在 Python 啟動前因唯讀環境無法建立 shell 暫存檔而失敗，改用 `python3 -c` 後完成；前者不算測試紅。
- repo 未被修改；結束時工作樹狀態與進場時相同。