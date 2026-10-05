severity: clean

已逐節讀完凍結 spec，無 finding。

風險覆核：

- 極端輸入：空值、混合有效／無效測試會先形成前置錯誤；任一錯誤均阻止兩段 runner。
- 未釘住平台：既有 `tests-exist` 會判失敗，不會落入可執行清單，符合零啟動要求。
- 併發：仍使用釘住 HEAD 的隔離工作樹，順序調整未新增共享狀態。
- 資源／例外：結果與事件在 context manager 外統一收束，設計明禁提早 return，未破壞清理。
- 效能：只略過昂貴的修正與合約測試；前置解析仍完整執行。
- 回退：撤回功能提交即可恢復原順序；追加式治理事件無須刪除。
- `代碼審修正關卡`：通過標準、回傳碼與一筆 warned 事件不變，未破壞現有職責。
- `測試假綠形態`：probe 以真實 CLI、runner 日誌及實際方法身分證明路徑；精確失敗項與未執行提示共同避免鄰近檢查代打，未破壞「現場成立」合約。

已讀材料：

- `docs/lumos-toolchain-knowledge/Projects/修正關卡先驗便宜條件_計劃.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Systems/代碼審修正關卡.md`
- `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`