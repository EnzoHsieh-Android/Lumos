severity: clean

本輪需拆範圍，不能誠稱完成審查。工具首次合併讀取遭截斷後發生重讀，實際回傳／重讀已超過 1,800 行上限；依派工規則在此停止，不提出未完整驗證的 finding。

已覆蓋：

- `r3-resource-full.patch`
- `r3-resource-repair.patch`
- `r3-repair-binding.json`
- 修後 `model_command`、`run_model` 與必要呼叫者
- 測試入口：`scripts/test_lumos.py`、測試材料 README
- 圖譜鏡頭：
  - handbook 程序清理與歷史 trial：已靜態檢視
  - 錯誤／逾時／取消：逾時修復測試已檢視；取消路徑尚未完成動態判定
  - 測試入口歸屬：獨立 unittest 與總入口接線已定位

未驗範圍：

- before/after 同案例動態執行與真實行為比較
- SIGTERM 取消路徑的程序群清理
- 相鄰錯誤路徑回歸
- Windows，依派工排除

執行受阻：指定實驗目錄建立命令回傳 `rc=1`，真實行為為 `Operation not permitted`；唯讀環境下未改用其他目錄，因此沒有編造測試結果。repo 未修改，也未開啟 r1/r2 席報告或作者 intake。

建議拆成兩輪：

1. 固定版本 before/after 動態案例、逾時與取消路徑。
2. 圖譜鏡頭、測試入口歸屬與相鄰路徑靜態審查。