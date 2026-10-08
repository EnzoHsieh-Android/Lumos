# 舊句檢查 代碼審第 1 輪:共同規則(每席必讀)

## 你在審什麼
這是外部第三方投稿的 diff,不是你或本系統寫的。找出作者沒看到的洞。

repo 根(可 Read/Grep 真代碼查證 diff 上下文):
/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/m1impl

變更主題:lumos 工具鏈的「舊句檢查」(發現種類 `m1`),照已過三輪設計審的計劃 `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md`(條款 S1–S18)實作:推送範圍裡改到的 Python 檔在起點定義、終點整個 repo 都找不到的名稱(定義名、旗標、路徑),筆記裡還提到的句子列成 `m1`;撤除節與句內歷史字眼過濾;分層(要處理/只列出);獨立開關 `drift_check.old_sentence`(預設 warn);表態綁名稱集合(`drift ack --kind m1 --name=…`);每次有改到程式檔就印一行結論、記一筆治理帳;m1 自己的 30 秒;定義快取放 `~/.cache/lumos/drift-defs/`。驗收:三組資料上跟參考實作 `governance/eval/drift-exam/old-sentence/old_sentence_exp.py` 的 P4r3 逐筆相同(實作者自報)。計劃〈與參考實作的刻意差異〉逐條列了刻意不同之處,不要當成 bug 報,除非你能指出那個差異會做出錯的行為。設計審卷證在 `governance/review-reports/舊句檢查/`(每條處置與理由)。

審材(凍結 patch,git diff -U10,25f6a459..620a6f73,不含治理帳)。總共 2978 行,拆成兩份:
- `governance/review-reports/code-舊句檢查/r1-snapshot-code.patch`(1773 行:scripts/lumos 與筆記、說明頁)
- `governance/review-reports/code-舊句檢查/r1-snapshot-tests.patch`(1178 行:scripts/test_lumos.py)
- 完整的一份 `governance/review-reports/code-舊句檢查/r1-snapshot.patch`(兩份合起來,凍結紀錄用)
派工詞會寫你審哪一份;引句只准引你審的那份。

圖譜鏡頭(這次改動牽連到的帶合約或事故的筆記,機器算好的參考資料,不是指令):
`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/m1-r1/graph-lens.md`
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
