severity: major

## operator-F1

severity: major
blocking: 是

引句:「if groups is None or any(not g.get("sha") for g in groups):」

觀察：推送的逐提交清單讀取失敗回None時，新增routeN/B把分屬兩個提交的測試變更當成同次證據，錯放行。
判準：已宣告測試只能證明同一提交實際變更；保留舊正式程式退路不等於可主動借不確定的跨提交測試證據。

同一兩提交fixture：正常current rc1；故障current rc0；基線53d1 CLI在同一故障rc1。故障為private wrapper使_nodehome_commit_groups回None，非產品開关，也不改受審根。group-failure-counter.json留argv/base/tip/raw与来源。新持續測試t_nodehome_optional_test_group_failure先核對測試只在前一提交變更，並印故障入口标記；普通/-O兩方向故障原版皆翻紅。

file: `scripts/lumos:27635`
file: `scripts/lumos:28005`

此報為編排者機械補充，不算第八位獨立找問題席，不拿它冒稱多席一致；獨立resources-defender後續實跑同意major。

已讀材料：
- `governance/review-reports/code-convergence-input-guards/r1-source.patch`
- `governance/review-reports/code-convergence-input-guards/group-failure-counter.json`
