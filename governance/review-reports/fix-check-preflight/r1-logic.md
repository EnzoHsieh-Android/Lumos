severity: major

## logic-F1

severity: major  
blocking: 是；S1 的測試可能假通過，讓單獨的 record 錯誤仍啟動昂貴 runner。  
引句:「當紀錄類別不合法時，應回 1、收齊 record 錯誤、零啟動測試 runner 且記一筆 warned 事件」  
file: `scripts/test_lumos.py:69606`  
file: `scripts/test_lumos.py:69637`

S1 fixture 同時放入「不合法 category」與「不存在的測試方法」，因此同時產生 `record`、`tests-exist` 兩種錯誤。具體漏網實作：提前略過條件遺漏 `record`、只因 `tests-exist` 而停下；現有 S1 仍全綠。實際輸入若改成不合法 category 搭配唯一存在的 `t_clamp_cap`，runner 就會啟動，違反 S1。應讓 S1 只含 record 錯誤；混合收齊另立案例。這也命中「相鄰檢查代打」的假綠形態。

## 固定席合約

- `Systems/代碼審修正關卡`：設計本身保留五項判定、rc、隔離 HEAD、warned 事件與 loop-next 語義；修正 F1 後不破壞。
- `Systems/測試假綠形態`：runner 日誌能證明舊流程確實執行，未破壞「現場成立」合約；但 S1 的重疊錯誤缺乏鑑別力，正是 F1。

## 風險覆核

已讀完原因與實驗、核心裁定、S1–S5、實務隱患及回退。除 F1 外：

- 併發／版本：仍使用釘住 HEAD 的隔離工作樹，無新增競態。
- 資源／例外：清理由既有 context manager 承擔，未新增背景程序。
- 效能：前置錯誤零 runner 的方向成立；有效輸入仍跑兩段。
- 回退：撤回功能提交可恢復原順序；追加式治理事件無需刪除。
- 外部與不可逆：僅本機驗證流程，沒有外部送出或部署。

## 已讀材料

- `docs/lumos-toolchain-knowledge/Projects/修正關卡先驗便宜條件_計劃.md`
- `scripts/lumos`
- `scripts/test_lumos.py`
- `docs/lumos-toolchain-knowledge/Systems/代碼審修正關卡.md`
- `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`