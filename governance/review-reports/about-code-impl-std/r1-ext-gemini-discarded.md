e1
**severity**: major
**spec 逐字引句**: 「目標檔命中 ≥ LUMOS_IMPACT_ABOUT_MAX(預設 8)→ 本次關閉 about 加分(仍三軸照舊)。」
**問題說明**: 邏輯自相矛盾且損害高負載場景下的 UX。本案目標是透過排序解決「噪音過多」問題，而「巨檔」（命中 ≥ 8 篇）正是噪音最嚴重、最需要將「關於」類筆記排到前排的場景。規格卻規定在這種最需要排序的情況下「關閉加分」（退回無序狀態），導致功能在關鍵時刻失效，使用者仍需在大量噪音中手動翻找。

e2
**severity**: major
**spec 逐字引句**: 「找 stamp 第一段 = batch-<日期> 的節點、對每篇把 about_code 清單逐值 cmd_remove 並刪 stamp。」
**問題說明**: 導致「髒回滾」或數據遺失。若某節點在批次寫入後，人工又增補了標記，其 stamp 會按慣例更新為 `claude/...`。此時 revert 指令會因 stamp 不匹配而跳過該節點，導致該節點內殘留的「批次舊數據」無法被清除。若 revert 邏輯改為強制清除，則會連同人工增補的正確數據一併刪除。

e3
**severity**: major
**spec 逐字引句**: 「範本加 about_code: 空欄與一句提示 ... about_code: [] 會被 fm_structure 判成 scalar → append 必敗」
**問題說明**: 實作流程阻塞。規格要求在範本中預設 `about_code: []`，但同時承認既有解析器會將空清單誤判為純量（scalar）導致 `append` 指令失敗。這意味著所有基於新範本建立的節點，在解析器 bug 修復前，都無法透過規格建議的 `lumos append` 方式增加標記，增量流程在字面實作上是斷裂的。

e4
**severity**: major
**spec 逐字引句**: 「過期判準改成 git 最後改動日期 ... git 缺席時退回 updated ... 用 updated 當過期判準會沉默放過這些節點」
**問題說明**: 安全機制存在沉默失敗（Silent Failure）。#4 節規定讀側在 git 缺席時 fallback 到 `updated` 欄位，但文中已明確指出 `updated` 有 33% 的資料落後於真實改動。這會導致讀側誤信了已過期但 `updated` 尚未更新的錯誤標記，而 #6 節的檢查側（doctor）在 git 缺席時卻選擇「略過」，導致系統性地放過三分之一的潛在錯誤資料且不予報警。

e5
**severity**: major
**spec 逐字引句**: 「A 席 Codex、B 席 Gemini(或反之), merge → 不一致人裁 → apply 寫入 ... apply 那半未做」
**問題說明**: 關鍵工具鏈缺失。規格強調存量與增量必須走「雙評審」流程以保證寫入品質，但負責將評審結果寫回 frontmatter 的 `apply` 工具卻標註為「未做」。在缺乏自動化寫入工具的情況下，雙評審產出的數據無法有效落地，導致規格宣稱的品質保證流程成為空談。

最嚴重 severity: major