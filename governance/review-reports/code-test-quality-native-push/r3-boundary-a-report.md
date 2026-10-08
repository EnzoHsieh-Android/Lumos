severity: blocker

blocking: 是

本輪已超過閱讀上限，不能冒稱完成審查，也未對程式品質作 clean/有缺陷判定。

引句:「总阅读包含提示规则固定镜头搜索重读不超过一千八百行」

可確認的最低閱讀量已達 1,918 行：

- 指定兩份 patch：1,196 行
- 三份必要 skill 規則：399 行
- binding source：26 行
- 固定鏡頭：66 行
- CLAUDE.md：105 行
- 測試方法索引搜尋：62 行
- `commands/03` 規則：64 行

這還未計入對話提示、行數盤點與其他短搜尋。尚未執行 before/after 實驗，也未讀固定版本產品函式，因此沒有產品紅燈或無回歸結論；repo 未修改。

請拆成兩席，例如：

- A：`copied_bundle` 至 `test_results_rename_preserves_original_role_source`
- B：`test_mixed_scanner_retains_legacy_help` 至檔尾

或明確提高本席閱讀上限後再續審。