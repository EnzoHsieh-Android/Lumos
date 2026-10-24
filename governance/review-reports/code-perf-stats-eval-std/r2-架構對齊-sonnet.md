severity: minor

**1. 結構與位置:跟鄰居一樣。**
- 新增的 Verification 放在 `Verification/` 底下,檔名是 `2026-10-24_<主題>.md`,跟 `2026-10-24_Android記憶體與穩定性實驗室驗收.md` 同一個格式。
- 前置欄位 `type/status/date/valid_under/revalidate_when/tags/plan_refs` 跟 `2026-10-23_macrobench實機端到端.md:1-17` 一致。`valid_under` 用清單寫法,對照 `2026-10-23_macrobench實機端到端.md:5-7`;記憶體驗收那篇的 `valid_under` 用字串寫法(同檔第 5 行),兩種寫法鄰居都有。
- 原始資料放在 `governance/research/macrobench/2026-10-24-perf-stats/`,已被 git 追蹤。跟 `2026-10-23-lab-tablet/` 同樣是「日期-主題」資料夾,對照 `2026-10-23_macrobench實機端到端.md:27`。
- `Systems/macrobenchmark-adapter` 的 `verified_by` 只在清單尾端多一條連結,做法跟既有四條相同。
- 計劃的 `RETIRE-IF`、`REVISIT` 維持「獨立一行」的位置。同一份計劃裡有多條 `RETIRE-IF` 和多條 `REVISIT`,在 repo 裡很常見,例如 `Projects/審查席唯讀隔離_計劃.md` 有 7 條 RETIRE-IF,`Projects/Android記憶體與穩定性驗收_計劃.md:45-49` 有 5 條 REVISIT。

**2. 寫法:大致一樣,有一處不一致。**
- 事件式回頭條件寫在 Verification 裡,跟 `Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證.md:33` 同形。`[when-status:Projects/…=done][by:…]` 的語法跟 `Projects/安全主張驗收閘_計劃.md:380` 一致,節點沒有加 `[[ ]]`。
- 內文用 `##` 小節(怎麼量、結果、沒驗的),`## 沒驗` 這類小節在 `Verification/2026-08-22_受波及合約測試真跑閘落地.md` 等檔也出現過。
- 唯一不對齊是下面 A1。

**3. 有沒有第二種做法:沒有。**
- 研究資料沿用 `governance/research/macrobench/`,沒有另開位置。
- 回頭條件沿用 `REVISIT:` 和 `RETIRE-IF:`,沒有發明新欄位。
- 證據連結沿用 `verified_by` 和 `plan_refs`。

## A1 計劃的 REVISIT 用日期開頭,卻描述事件條件
severity: minor
blocking: 否
引句:「REVISIT:2027-03-31 第 1、2、3、5 條上線後,真實專案若出現同場 20 輪仍誤報」
對照:
- `Projects/Android效能判定統計化_計劃.md` 新增的那條 `REVISIT:2027-03-31`,觸發條件是「第 1、2、3、5 條上線」這個事件。
- repo 的 `CLAUDE.md` 鐵則 4 說「綁事件的寫 `REVISIT:[when-file:路徑][by:日期]`」。
- 同一次 diff 的新 Verification 已經用了 `[when-status:…][by:…]`,另有 `Projects/安全主張驗收閘_計劃.md:380` 的先例。
- 同計劃的另一條 `REVISIT:2026-11-30` 是純日期,而且屬於舊有內容。
- 這是格式不一致,不是結構問題。計劃在 `Projects/安全主張驗收閘_計劃.md:380` 那種寫法可以用,但這份計劃只有一個整份計劃的 `=done` 狀態,沒有「第 N 條上線」的節點。純日期加散文事件在 `Projects/Android記憶體與穩定性驗收_計劃.md:47-48` 也有,所以只列 minor。

不對齊共 1 條,其中重大 0 條
