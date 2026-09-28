severity: minor

## F1 明寫為 null 的 gate 被當成完全沒寫

severity: minor

blocking: 否 — 只漏掉 doctor 的軟提醒；drift check 仍按預設 warn 執行。

引句:「既有慣例);多回一個 explicit=專案有沒有自己寫 drift_check(寫壞了也算寫了)——doctor 的開關提醒要用,」

file: `scripts/lumos:25685`

1. 輸入 `{"drift_check":{"gate":null}}` 已明寫 `gate`，且值不在合法集合中，符合「寫壞了也算 explicit」。
2. `_drift_config` 以 `dc.get("gate")` 讀值；`null` 變成 `None` 後走「沒寫」分支，回傳 `explicit=False` 且不產生警告。未接線時，doctor 的 `(wired or explicit)` 因而為假，整項設定錯誤完全靜默。
3. 最小重現：

```text
$ python3 -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="review"); mode,_,explicit=m["_drift_config"]("{\"drift_check\":{\"gate\":null}}"); print(mode,explicit,mode!="block" and explicit)'
warn False False
```

4. 新測試只涵蓋 `drift_check` 整體不是物件，沒有涵蓋「物件內確實存在 `gate`、但值是 null」這條回歸。

file: `scripts/test_lumos.py:50887`

逐提交狀態讀取、嚴格／不嚴格失敗語意與批次讀取期限：已看，無 finding。

完全相同測試名、空連結與考試重放：已看，無 finding。

計劃、Systems 筆記及新增測試：已看，除 F1 的內部不一致外無 finding。

rtb 考卷唯讀重放：擋到 3、點到 3、漏 0，與計劃記錄一致，無 finding。

驗證限制：新增 r4 測試未進入案例；唯讀沙盒沒有可寫暫存目錄，測試框架在隔離環境初始化時中止。

最嚴重 minor，blocking 共 0 條。