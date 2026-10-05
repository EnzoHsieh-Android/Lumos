severity: major

DESIGN-ARCHITECTURE-1 — 特殊字元路徑在共用 raw 解析器前已被文字化，保留的是錯誤路徑

severity: major  
blocking: 是

引句:「路徑特殊字元使首行不可安全批次讀取；這些狀態不當作排除證據，保守保留。」

觀察：`_codeloop_raw_changes` 採 `--raw -z` 與無損解碼，本身符合設計；但 `cmd_impact_diff` 更早以前仍以文字模式執行 `git diff --name-only`，再用 `splitlines()` 建立候選。含換行等控制字元的 Git 路徑會被引用／跳脫，候選因此不再是原始路徑。

具體錯行為：

- 被引用後的路徑不再以 `governance/review-reports/` 等簿記前綴開頭，`_impact_diff_modes` 會認為範圍沒有簿記檔，直接回空模式表。
- `_impact_diff_seed_ok` 隨後把這個帶引號的假路徑當普通來源保留。
- 下游以假路徑取得 hunk、查家與事故，無法命中真正檔案。因此正式程式雖表面上「未排除」，實際會漏掉正確種子、家與事故；普通附件則可能成為偽種子。
- 角色鏡頭已用 `--name-status -z` 正確處理此類路徑，造成兩個共享分類消費者在路徑語意上分裂。

佐證：

- file: `scripts/lumos:41146`
- file: `scripts/lumos:41151`
- file: `scripts/lumos:41043`
- file: `scripts/lumos:41178`
- file: `scripts/lumos:44305`
- file: `scripts/test_lumos.py:23051`
- file: `scripts/test_lumos.py:23201`
- file: `scripts/test_lumos.py:38693`

判準：影響分析的候選枚舉也應採 NUL 分隔與既有無損解碼口徑；驗收需用簿記目錄內含換行／控制字元的真正程式，斷言輸出的 `files` 是原始精確路徑，且家與事故仍命中。這是對齊既有 raw 路徑語意，不需新增另一套分類機制。

臨時 Git 重現因唯讀 sandbox 禁止在 `/tmp` 建目錄而未能執行（`mktemp: Operation not permitted`）；不把這次實驗算作通過。上述 finding 依已開碼的文字拆行資料流判定。

各節核對：

- 開場、PRIOR-ART、RETIRE-IF：無其他 finding。沿用 `_BOOKKEEPING_FILES`、`_BOOKKEEPING_DIRS`、`_nodehome_code_kind` 與既有 raw parser，沒有另建目錄或副檔名單源。
- 最小改法：除 DESIGN-ARCHITECTURE-1 外，模式、物件、刪檔舊側、staged 索引側及未知保守保留的主幹一致。
- 證據與範圍：無其他 finding。三個 `lands_in` 分別覆蓋檢索入口、測試可信度、共享 raw／角色預算，與實際修改相符。
- 實務隱患：無 finding。守衛面升為高風險，沒有再以「不改閘判準」錯誤排除。
- 回退：無 finding。回退動作與程式控制測試均有明確落點。
- 終審揭露的分類例外：無其他 finding。可執行文件副檔名、無副檔名腳本及刪檔均有對照測試。
- 第二輪完整例外核對：共享 `_codeloop_raw_changes` 沒有形成第二個 raw parser；問題只在 impact 入口較早的候選列舉。
- 修復驗證的時間前提：無 finding。功能正面段與正式三秒／零預算降級分開驗證，零預算提前返回也位於所有 Git 讀取之前。

已完整閱讀：

- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-snapshot.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-lens.txt`
- `/private/tmp/lumos-review-artifact-impact-inputs/CLAUDE.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/MOC/index.md`

另核對：

- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/lumos`
- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/test_lumos.py`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`

未讀取其他輪的審查報告或結果內容。

最嚴重 severity：major  
blocking 總數：1