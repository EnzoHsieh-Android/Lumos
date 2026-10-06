severity: major

## DESIGN-BOUNDARY-1 — 特殊字元檔名被轉成假路徑，真正程式的家與事故會漏推

severity: major

blocking: 是

引句:「路徑特殊字元使首行不可安全批次讀取；這些狀態不當作排除證據，保守保留。」

觀察：設計承諾遇到特殊路徑時保守保留，但 `impact --diff` 最前面的檔名清單仍使用非 NUL 的文字輸出，再以 `splitlines()` 拆解。Git 對換行、tab 等檔名會輸出帶引號的轉義名稱；非 UTF-8 位元組還會被 `errors="replace"` 改寫。之後 raw parser 雖然無損取得真正路徑，兩份名稱卻無法相配。

具體錯行為：例如簿記目錄內真正的 `run\nscript.py`，會以包含引號與 `\n` 字面的假路徑進入 `files`；模式查詢落空，逐檔 diff 也找不到該假路徑，因此真正檔案的 hunk、Systems 家與事故節點都不會被推出。這破壞 S1 的「保留其種子、家與事故」，不是只有顯示問題。角色鏡頭已使用 `-z`，所以兩個共享消費者在此邊界也會產生不同結果。

佐證：

- file: `scripts/lumos:41145`：檔名入口只有 `core.quotePath=false`，沒有 `-z`。
- file: `scripts/lumos:41146`
- file: `scripts/lumos:41151`：以文字 `splitlines()` 建立 candidates。
- file: `scripts/lumos:41152`：再拿 candidates 與無損 raw 結果配對。
- file: `scripts/lumos:44293`：raw parser 使用 NUL 分隔與 `os.fsdecode`，路徑表示和上述入口不同。
- file: `scripts/lumos:24370`：角色清單則使用 `--name-status -z`，沒有相同問題。
- file: `scripts/test_lumos.py:23037`：S1 驗收未包含特殊字元檔名。
- file: `scripts/test_lumos.py:23087`：程式控制組同樣只使用一般檔名。

判準：檔名入口須以 NUL 分隔並無損解碼，或直接沿用已解析的 raw changes；驗收至少要證明特殊字元命名的真正程式以原始完整路徑出現在 `files`，且其家與事故均被推出。普通特殊字元附件仍應依設計保守處理。

## 逐節核對

- 最小改法：普通附件、程式副檔名、普通無副檔名、shebang、可執行模式、刪檔舊物件及 staged 索引物件的核心分類均可實作；特殊路徑入口有上述阻擋問題。
- 證據與範圍：已清楚揭露這是實作後補設計審，未冒稱事前授權；未重設代碼審輪次。
- 實務隱患：守衛面已改列高風險，沒有以「不改閘判準」排除風險。
- 回退：撤回分類修補及恢復既有誤觸的後果均有交代。
- 終審分類例外：副檔名、可執行 `.txt/.patch/.md/.json/.jsonl`、無副檔名腳本及已刪可執行檔，源碼路徑皆有對應處理。
- 第二輪完整例外：模式與物件共用 `_codeloop_raw_changes`，刪除選舊物件、其他選新物件；大小超限、缺物件及批次失敗均保守保留。
- 時間前提：`budget <= 0` 在設定和選檔前直接返回；30 秒只用於內容型功能驗收，正式預設仍為三秒。未發現新的併發、資源釋放或正預算承諾錯置。
- 合約：三個 lands_in 中僅 `Systems/測試假綠形態` 有一條既有合約；本設計未破壞該合約。

## 已讀材料

完整閱讀：

- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-snapshot.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-lens.txt`
- `/private/tmp/lumos-review-artifact-impact-inputs/CLAUDE.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/MOC/index.md`

核對指定符號、測試及相關落點／合約：

- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/lumos`
- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/test_lumos.py`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`

未讀取其他 `governance/review-reports/` 輪次報告或結果內容。臨時 Git 重現及測試子集因唯讀 sandbox 無可用暫存目錄而無法執行，未將其算作通過。

最嚴重 severity：major；blocking 總數：1。