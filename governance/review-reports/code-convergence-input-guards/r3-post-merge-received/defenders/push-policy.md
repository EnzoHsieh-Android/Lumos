severity: major  
裁決: concern

F1 裁決：現象 HIT，本批新增判準 MISS。

引句：「所有提交共用最终 tip 的 `cfg` 与 `vendored_skip`。」

- 現象成立：`cmd_home_check` 從 push 終點讀一次 `cfg` 與 `skip`，再交給所有歷史 group。[scripts/lumos](/private/tmp/lumos-future-repair-regression-research/scripts/lumos:30053)、[scripts/lumos](/private/tmp/lumos-future-repair-regression-research/scripts/lumos:30073)
- 但這是既有明確政策：正式計劃指定新增路由使用「推送終點快照讀出的同份設定與排除清單」。[已宣告測試家的同次寫回_計劃.md](/private/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/已宣告測試家的同次寫回_計劃.md:38)
- 系統筆記更直接排除原報告判準：「這不是重定義推送終點設定對歷史分組的既有政策」。[每支檔有家.md](/private/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:115)
- main 基線早已用同一份終點 `cfg` 同時計算 B/N；不是 `_nodehome_group_route_tests` 新增的政策。

引句：「不属于该生产代码的 Systems 笔记……因此通过。」

這混淆了兩種家：

- 本批刻意允許「不是生產檔的家、但確實是同提交改動測試的家」接受寫回。[已宣告測試家的同次寫回_計劃.md](/private/tmp/lumos-future-repair-regression-research/docs/lumos-toolchain-knowledge/Projects/已宣告測試家的同次寫回_計劃.md:27)
- 候選測試必須同時出現在該 group 的改動路徑與節點 `own`。[scripts/lumos](/private/tmp/lumos-future-repair-regression-research/scripts/lumos:29518)
- 判定時仍要求該篇自己的 `info["own"]` 與路由集合相交；真正無關的節點仍會形成 route block。[scripts/lumos](/private/tmp/lumos-future-repair-regression-research/scripts/lumos:29727)

因此，A→B 的終點設定重分類是有意行為；「必須按每個提交自己的設定分類」只能算政策變更提案，不能證明候選違反現有合約。F1 是 code 層假陽性，但不宣稱任何舊問題已修或整體 clean。

未執行寫入式 Git fixture：目前 sandbox 為 read-only。指定報告檔也因相同限制無法寫入，仍保持原內容；repo 未修改。