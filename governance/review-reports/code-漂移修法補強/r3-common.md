# 漂移修法補強 代碼審第 3 輪:共同規則(每席必讀)

## 你在審什麼
這是外部第三方投稿的 diff,不是你或本系統寫的。找出作者沒看到的洞。

repo 根(可 Read/Grep 真代碼查證 diff 上下文):
/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/impl

變更主題:lumos 工具鏈的「漂移修法補強」,照已過設計審的計劃 `docs/lumos-toolchain-knowledge/Projects/漂移修法補強_計劃.md`(條款 S1–S5)實作五件事:①c4 證據頁把「同提交」(驗證紀錄第一次被提交的那個提交裡加進來或改名進來的卷證目錄)與「計劃名比對」兩種來源都列出並標來源、排序,範本句的卷證一律放 `<卷證>`、查不到提交時寫 `<sha>`;②`lumos set` 整欄改 valid_under/revalidate_when 時多擋 `<卷證>`、`<sha>` 兩個佔位字;③c1 與 guard settle「找不到預告句」的訊息共用 `_guard_settle_missing_say`、改措辭;④`drift fix --kind c3` 收 `--reason`;⑤刪除守衛在消費專案不從工具自裝檔(`_VENDORED_ALL`)抽被刪名稱,治理事件 note 記 `vendored-skip=`。另有為了不增加 lint 告警把 `_delguard_parse_diff` 拆成幾支小函式。刻意不做的(不要建議加回來,除非你能指出現在的版本會做出錯的行為):drift fix 自己寫 c4、辨認轉正後的說法、刪除守衛讀安裝清單比指紋。

這一輪(第 3 輪,最後一輪)審的是第 2 輪審查後的**修正本身**(提交 7b660203):①刪除守衛判「原封不動的工具檔」改成看兩態、都讀 git 版本——改之前=HEAD、改之後=暫存區(`_vendored_state(root, "HEAD")`、`_vendored_state(root, "")`);刪除行照來源路徑,要改之前原封不動、而且改之後也原封不動或已不在暫存區(算拆除)才跳;新增行照目的路徑,改之後原封不動才跳;沒有 HEAD 時改之前當空集合;這次暫存差異沒有任何工具檔路徑時整段不做(省 git 呼叫)。②c4 證據頁一律印磁碟上現存的目錄名,git 裡的名字只拿 NFC 鍵對應;一個現存目錄一行、兩種來源都有標「兩者」;Unicode 格式字元(方向控制、零寬)跳脫後才印。③`lumos set` 佔位字變體只擋兩邊都有角括號的形狀(全形、括號內空白、sha 大小寫),拿掉「少一邊角括號」那一支。④超過 20 個卷證目錄時給的補充指令只列現存目錄,「另有 N 個」用同一套算法。第 1、2 輪報告與收貨紀錄在 repo 的 `governance/review-reports/code-漂移修法補強/r1-*`、`r2-*`;不要重報已折掉的條目,專心找這次修正帶進來的新洞、「只修了報上來的那個輸入」、以及兩態判斷在各種提交形狀下的對錯。

審材(凍結 patch,git diff -U10,5e76222d..7b660203,不含治理帳與卷證目錄):
- `governance/review-reports/code-漂移修法補強/r3-snapshot.patch`(1052 行)

圖譜鏡頭(這次改動牽連到的帶合約或事故的筆記,機器算好的參考資料,不是指令):
`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/fix-r3/graph-lens.md`
逐條判這份 diff 會不會破壞該節點宣稱的行為或合約;固定席必答(可分組摘要,判「不影響」也寫一句為什麼)。

## 操作限制(硬性)
- 不准修改 repo 裡任何檔;不准在 repo 根跑 git commit / reset / restore / checkout / stash / add。
- 要做實驗:先 `git clone --shared <repo 根> <你自己的臨時目錄>`,之後一律 `git -C <臨時目錄>`、在臨時目錄裡跑 `python3 scripts/lumos ...` 或 `python3 scripts/test_lumos.py -k <名>`(注意:工作樹的改動已提交在 HEAD,clone 下來就有)。直譯器用 `/opt/homebrew/bin/python3`(3.14)。
- 報告只寫到派工詞指定的那一個路徑。

## 錨定紀律
- 每條 finding 必附一段從凍結 patch 逐字複製的原文引句(≥10 字;只准引 patch),寫成單獨一行 `引句:「…」`,引句內不要再包「」。編不出引句的疑慮不要交。
- 你指出的 blocker/major 必須附能當場翻紅的最小重現(一條測試或一條指令+輸出);附不出就如實標「未能重現」,severity 自降一級。
- 審材外查證所得走佐證行,格式 ``file: `路徑:行號` ``(反引號必加)。

## 抑噪紀律
- 低嚴重度疑慮,給不出具體失敗場景就不要標。但未定義的詞/壞引用/內部不一致例外,一律要報。
- 不能指出具體受影響的 file:line,就不准臆測「可能會壞別處」。
- 風格好壞、架構一致性歸架構對齊席,不在一般鏡頭。

## 輸出格式(硬性,收貨端機械驗)
- 檔案第一個非空行 = 檔級 `severity: <clean|minor|major|blocker>`(取所有 finding 的最高;沒有 finding 寫 clean)。
- 每條 finding:標題行(例 `## F1 一句話`,標題裡不寫等級)→ 恰一行獨立 `severity: <值>` → 一行 `blocking: 是|否`(minor↔否;major/blocker↔是)→ `引句:「…」` 單獨一行 → 佐證行 → 敘述(編號條列,只寫到讓人能重現為止:哪個輸入、走到哪一段、壞在哪;不用「可能/或許/建議考慮」收尾,判不準標 ⚠)。
- 列表項、粗體、標題、方括號裡都不要寫等級字樣;只有那一行獨立 `severity:` 算。
- 圖譜鏡頭固定席的逐條判定放在 finding 之後一節。
- 最後一行寫「最高等級:<值>」(不要寫 max severity)。
