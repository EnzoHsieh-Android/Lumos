severity: major

ID: DESIGN-COMPATIBILITY-1  
severity: major  
blocking: 是  
引句:「正式 _review_roles 預設3秒、零預算與期限降級案例均另验」  
佐證:

- file: `scripts/lumos:24391`
- file: `scripts/lumos:24402`
- file: `scripts/lumos:41041`
- file: `scripts/lumos:41059`
- file: `scripts/lumos:41529`
- file: `scripts/test_lumos.py:38531`
- file: `scripts/test_lumos.py:38546`

觀察：共享分類接入 `_review_role_changed_files` 後，只要差異含簿記路徑，就會在角色剩餘預算計算之前執行 `_impact_diff_modes`。該入口的 raw diff 最長可等 20 秒；需要讀首行時，大小查詢及內容查詢又各自使用固定 Git timeout。這些耗時都沒有接收 `_review_roles` 的剩餘 `budget`。因此正值 `budget=1` 或正式預設 3 秒時，角色鏡頭仍可能阻塞遠超預算，且回來後若沒有待讀內容，甚至不一定標成 `timed_out`。這是本次為簿記分類新增的讀取，不只是凍結副本末段所稱的「既有正預算兩趟讀取」。

現有測試只驗：

- `budget=0` 完全不讀 Git。
- 正面功能案例使用 `budget=30`。
- 零預算在三秒內返回。

沒有覆蓋「小幅正預算＋含簿記檔＋raw／首行讀取變慢」的正式路徑。

判準：共享分類在角色消費者中必須使用角色剩餘預算，或在每個新增 Git 階段前後檢查截止時間；驗收應以小幅正預算控制 raw diff／物件讀取延遲，證明總耗時受限並誠實回報超時。這不需要另建分類機制。

逐節結果：

- 前言、PRIOR-ART、RETIRE-IF：沿用簿記單源且不以 gitignore 代替分類，與程式一致，無 finding。
- 最小改法與 S1：副檔名、可執行模式、無副檔名首行、刪檔舊模式及 staged 索引模式均有對應實作；未知狀態保守保留，無其他 finding。
- 證據與範圍：清楚承認補設計審發生在實作後，也未重設獨立代碼審輪次，無 finding。
- 實務隱患：有揭露共享 raw parser 的守衛面；但正預算穿透落在上述 finding。
- 回退：分類入口可撤回，並指定既有程式例外控制組，無 finding。
- 終審揭露與第二輪例外：可執行 `.md/.json/.jsonl`、普通無副檔名卷證及既有 `_codeloop_raw_modes` 相容包裝均與源碼一致，無 finding。
- 修復驗證時間前提：零預算提前返回正確；正值預算缺口即 DESIGN-COMPATIBILITY-1。
- 實際鏡頭三個落點：三篇 Systems 均存在；`retrieval-ranking` 管兩支檔、`測試假綠形態` 管測試檔且有一條合約、`pitfalls-code-loop` 管主 CLI。落點與本次分類、測試鑑別力、code-loop 相容性相符，無 finding。
- 共享 raw parser 相容性：`_codeloop_raw_modes` 仍只回舊／新模式對，既有留痕消費者的資料形狀未變；未發現模式 API 破壞。
- 全域原排除：`docs/`、golden、固定帳檔及一般目錄的舊 `.md/.jsonl/governance .json` 排除順序保持原範圍；程式例外只在既有簿記目錄內生效，無 finding。
- 併發與資源釋放：未新增共享可變狀態或長存資源；子程序有單次 timeout。總預算聚合問題已列為 finding。

已讀材料：

- `/Users/enzo/.agents/skills/lumos-project-notes/SKILL.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/CLAUDE.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-snapshot.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-lens.txt`
- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/lumos`（派工指定函式、所有呼叫點及相鄰 helper）
- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/test_lumos.py`（對應 impact、角色、raw parser／code-loop 測試）
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`
- 上述三篇 Systems 的 `lumos contracts` 輸出

未讀任何其他輪審查報告或結果。計劃與凍結副本逐字相同。

執行限制：嘗試執行三組針對測試，但唯讀 sandbox 沒有可用臨時目錄，測試在建立 fixture 前即由 `tempfile.gettempdir()` 終止；因此本席不把既有測試紀錄當成本次實跑通過，也沒有進行 Git 臨時實驗。

最嚴重 severity：major  
blocking 總數：1