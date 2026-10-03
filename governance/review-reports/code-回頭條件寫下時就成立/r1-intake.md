# r1 收貨(code-回頭條件寫下時就成立)

收齊兩席(正確性-sonnet、架構對齊-sonnet)才動工作目錄;席位沒動 repo(reflog 只有編排者自己的提交)。
正確性席報告末行總結格式不合(report-normalize 第 50 行),退回該席自改成「總結:最高等級 major」,其餘未動。
三道機械:兩份 quote-check 全數錨定;refcheck 正確性 1/1、架構對齊 13/13 對得上;seat-check vacuous。

## 重現表

| id | 怎麼試 | 結果 |
|---|---|---|
| F1 | 席位留的 scratchpad/probe1.py「disk dup」:已提交一行、工作目錄加同條件第二行未提交,scan --json | HIT:第 16、17 行 born 都是 state=true、同一個提交(e2e3d28) |
| F2 | probe1.py「gap」:寫下時 a.py 不在 → 改壞成解析不到 → 加 a.py → 修回 | HIT:born=修回那一版(3bd1ee2,即 HEAD)、state=true,訊息說「第一次出現在這篇時就成立」比查到的強 |
| Z1 | grep `_git_is_shallow`:scripts/lumos 有既有 helper,另兩處行內 | HIT:採用既有 helper |
| Z2 | 讀 `_DriftBornHistory._text`:None=沒有、False=讀不了 | HIT:改成回 (狀態, 文字) |
| Z3 | 讀 `_drift_born_annotate`:依「不在第一版」「歷史查不到這篇」字面值改寫原因 | HIT:改成 birth 回旗標,不比字串 |
| Z4 | `_drift_list` 裡寫死 8、`_DRIFT_BORN_MAX_COMMITS = 6` 只靠註解連動 | HIT:抽 `_DRIFT_LS_CACHE_MAX`,上限由它算 |
| Z5 | grep `partialClone|promisor`:專案沒有既有判法 | MISS:沒有不一致可重現(專案裡沒有鄰居可對,席位自己標 ⚠);只看 extensions.partialClone 記進計劃天花板 8 |

## 依根因分組

- 甲「現在這份文字沒進比對」(F1):工作目錄或 --at 終點那份文字裡,同組條件也要恰好一行;不是就判不了「不只一行」。統一規則=終點文字算第 0 版,跟歷史每一版同一條檢查。
- 乙「訊息說得比查到的強」(F2):訊息改成「從 <編號> 起連續出現在這篇,那一版條件就已成立」,不講「第一次出現」「寫下」;計劃天花板補「改壞再修好算重新出現」。
- 丙 架構對齊(Z1–Z4)。
