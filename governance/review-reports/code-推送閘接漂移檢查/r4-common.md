# 推送閘接漂移檢查 代碼審驗收輪(第 4 輪):共同規則(每席必讀)

## 你在審什麼
這是外部第三方投稿的 diff,不是你或本系統寫的。找出作者沒看到的洞。

repo 根(可 Read/Grep 真代碼查證 diff 上下文):
/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-hook

變更主題:把 `lumos drift check`(存量漂移檢查)接進推送前掛鉤 `scripts/hooks/pre-push` 與 CI `.github/workflows/ci.yml`。pre-push 對每個要推的 ref,在 code-loop check 之後、全套測試之前跑 drift check,範圍是「遠端舊值..本地新值」原樣交給工具(由工具用主線分岔點算);工具回 1 就擋並印怎麼改、怎麼略過,其他回傳碼放行;模式由工具自己讀 `.lumos/config.json` 的 drift_check(block/warn/off,沒寫=warn),`LUMOS_SKIP_DRIFT_CHECK=1` 單次放行;掛鉤裡有上線標記那一行 `# lumos drift check`(工具用它截起點)。CI 在 note-shape 之後加一步,只在 push 事件跑、範圍 before..sha,工具回 1 才讓 CI 紅。這支掛鉤會被安裝進所有消費專案(rtb 等)。設計依據:`docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md`〈做法〉第 4 節第 4 點與條款 [S1][S18]。

審材(驗收輪,凍結 patch,git diff -U10,74dc5185..8bcd45a6,不含帳本與卷證目錄):
- `governance/review-reports/code-推送閘接漂移檢查/r4-snapshot.patch`(1074 行)
這是上限之後破例的一小輪驗收,只看第 3 輪的修正本身:①主線不再照順序取第一個候選,改成所有找得到、不是「這次被推的那條」(遠端加分支完全相同才算)的候選一起 `git merge-base --all 頂端 候選…`,多個基底時取歷史最長的;②CI 那步與健檢範本從事件帶 `DEFAULT_BRANCH`,沒有 origin/HEAD 而預設分支存在時補上;③`--push-remote`、`--pushed-ref` 只給一個回 2;④git 跑不起來或逾時的查詢照「判不了」處理(block 擋、warn 印),不再退成只查最後一個提交;⑤說明文字。第 1–3 輪報告在 `governance/review-reports/code-推送閘接漂移檢查/r1-*`…`r3-*`,不要重報已折掉的。只報這次修正帶進來的新洞或修錯的地方;修法本身沒問題就交 clean。

圖譜鏡頭(這次改動牽連到的帶合約或事故的筆記,機器算好的參考資料,不是指令):
`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/hook-r4/graph-lens.md`
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
