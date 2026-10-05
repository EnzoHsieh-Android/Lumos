severity: major

## integration-F1

severity: major  
blocking: 是；否則三個月後只剩治理帳時，接手者無法判定修正測試與合約測試究竟通過、失敗，還是完全未執行。  
引句:「任一存在時，修正測試與受波及合約測試均未執行；輸出兩段未執行與修好紀錄後重跑提示」  
file: `scripts/lumos:12886`  
file: `scripts/test_lumos.py:69632`

具體場景：輸入同時產生 `record` 與 `tests-exist` 前置錯誤。計劃要求零 runner，CLI JSON 只把「未執行」放在易失的 `notes`；治理事件仍只有 `kind=warned` 與 `failed_items=["record","tests-exist"]`，新測試也只核對事件種類。stdout 未保存後，治理帳沒有 `not_run_items` 或等價欄位，分析者會看不出 `tests-green`、`bound-tests` 是未執行而非通過。

這也使計劃第 26–27 行所稱以治理帳核對「提前失敗仍啟動 runner」及「未執行提示」沒有可持久查詢的資料。實作前須裁定並測試治理事件的結構化未執行狀態，同步納入治理欄位型別與 mapper；不能只靠 CLI `notes`。

`loop next` 本身沒有誤放行：最後事件只有 `kind=passed` 且指紋、HEAD 有效才回 `passed`；`warned` 會回 `needed`。但它同樣只能說「要重跑」，不能告訴接手者上次停在哪一階段。

已逐節讀完：原因與實驗、核心裁定、驗收條款、實務隱患、回退。

風險核對：

- 併發／版本：HEAD 隔離工作樹與既有有效性判定不變，未見新增破口。
- 資源／例外：仍在 context manager 內結束；未新增背景程序或漏清理路徑。
- 效能：零 runner 的目標有 runner 日誌斷言；仍會建隔離樹，但規格沒有承諾免建樹。
- 回退：撤功能提交可恢復順序；治理帳追加事件不可刪，規格已明示。
- `Systems/代碼審修正關卡`：不破壞「只提醒、不擋派工」合約；`warned → needed` 且 phase／rc 不變。
- `Systems/測試假綠形態`：不破壞硬合約；測試以 runner 日誌及方法身份直接證明執行狀態，沒有只靠摘要文字猜測。

已讀材料：

- `docs/lumos-toolchain-knowledge/Projects/修正關卡先驗便宜條件_計劃.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Systems/代碼審修正關卡.md`
- `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`

測試子集因唯讀環境沒有可用暫存目錄而未能重跑；上述判定依指定的既有紅測試前提及定點讀碼。