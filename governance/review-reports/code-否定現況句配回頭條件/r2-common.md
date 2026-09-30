# 否定現況句配回頭條件 代碼審第 2 輪:共同規則(每席必讀)

## 你在審什麼
這是外部第三方投稿的 diff,不是你或本系統寫的。找出作者沒看到的洞。

repo 根(可 Read/Grep 真代碼查證 diff 上下文):
/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard

變更主題:照已過三輪設計審的計劃 `docs/lumos-toolchain-knowledge/Projects/否定現況句配回頭條件_計劃.md`(條款 S1–S10)實作:提交時筆記形狀擋(note-shape)對新寫的正文與摘要行判「還沒有/尚未/目前沒有…」這類會過期的否定現況句,只印提醒(全部印出)、不進違規清單、不改任何既有回傳碼;提醒教人把那一句搬成獨立一行回頭條件;子開關 `note_shape.negation`;治理帳記精簡 `hinted` 事件(幾行、幾篇);全域紀律範本鐵則 4 與 skill 主檔那句改寫、`LUMOS_VERSION` 升到 1.1、CHANGELOG 補 v1.1;新增一條 lint 放行(`_note_shape_eval` 函式簽名多一個參數)。參考實作 `governance/eval/negation-revisit/neg_revisit_measure.py`(字眼表與過濾以它為準,計劃〈與參考實作的刻意差異〉列了不同處,不要當成 bug 報,除非你能指出它會做出錯的行為)。設計審卷證在 `governance/review-reports/否定現況句配回頭條件/`。

審材(凍結 patch,git diff -U10,1ca70d4f..0984c966,不含治理帳與錨點基準):
- `governance/review-reports/code-否定現況句配回頭條件/r2-snapshot.patch`(第 1 輪修正本身)

## 操作限制(硬性)
- ★第一個動作先 cd 到你自己的臨時目錄★;任何 git 指令都帶 `-C <路徑>`;絕不在 /Users/enzo/harness/lumos-toolchain 跑任何 git 或改任何檔。
- 不准修改 repo 裡任何檔;要做實驗先 `git clone --shared <repo 根> <你自己的臨時目錄>`,在臨時目錄裡跑 `/opt/homebrew/bin/python3 scripts/lumos ...` 或 `/opt/homebrew/bin/python3 scripts/test_lumos.py -k <名>`。
- 報告只寫到派工詞指定的那一個路徑。

## 錨定紀律
- 每條 finding 必附一段從凍結 patch 逐字複製的原文引句(≥10 字,括號與反引號裡的字也照抄),寫成單獨一行 `引句:「…」`,引句內不要再包「」。
- 你指出的 blocker/major 必須附能當場翻紅的最小重現;附不出就標「未能重現」,severity 自降一級。
- 審材外查證走佐證行,格式 ``file: `路徑:行號` ``。

## 抑噪紀律
- 低嚴重度疑慮給不出具體失敗場景就不要標;未定義的詞/壞引用/內部不一致例外,一律要報。

## 輸出格式(硬性,收貨端機械驗)
- 檔案第一個非空行 = 檔級 `severity: <clean|minor|major|blocker>`。
- 每條 finding:`## F1 一句話`(標題不寫等級)→ 恰一行獨立 `severity: <值>` → 一行 `blocking: 是|否` → `引句:「…」` → 佐證行 → 編號敘述。每個 `## F` 段都要有自己那一行 severity。
- 沒問題就交 `severity: clean`,不要湊數。
- 最後一行寫「最高等級:<值>」。

## 這一輪
第 2 輪只審第 1 輪的修正本身:測試拆成來源專用與消費專案都跑的兩支、新增模擬消費專案的測試、判定相符例句多五句、設定寫錯提醒的時機測試、doctor 那行改看結構化欄位(新函式 `_note_shape_negation_parse`)。第 1 輪報告在 `governance/review-reports/code-否定現況句配回頭條件/r1-*`,不要重報已修的;只報修正帶進來的新洞或修錯的;沒問題就交 clean。
