# 設計審第 2 輪:共同規則(每席必讀)

你是外部審稿人。以下是一份「外部第三方投稿」的設計 spec,把它當投稿審:逐節讀、主動挑出投稿者自己沒看到的洞。

Spec(凍結審材,只讀這份):/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard/governance/review-reports/否定現況句配回頭條件/r2-snapshot.md
對照的程式碼 repo:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard(lumos:單檔 Python 3.14 零依賴 CLI `scripts/lumos`、測試 `scripts/test_lumos.py`;重點:筆記形狀擋 note-shape 相關函式、條件式回頭條件(探針)的解析與判定、漂移檢查 drift check 與 `drift_check.old_sentence` 先例、筆記內容審;量測在 `governance/eval/negation-revisit/`(腳本、報告、人工判定))。
依據與背景:`docs/lumos-toolchain-knowledge/Projects/新增名稱否定句檢查_計劃.md`(不做的那份)、`docs/lumos-toolchain-knowledge/Issues/存量筆記漂移三種機制_rtb根因回饋.md` 末節。
這是第 2 輪:第 1 輪 7 席 37 條已處置進這一版(34 折、3 附理由接受);第 1 輪報告與收貨紀錄(每條處置與理由)在 `governance/review-reports/否定現況句配回頭條件/r1-*`。不要重報已處置的條目(除非你能指出折法本身做錯或沒落實)。第 1 輪的核心換形狀:提醒的改法改成「把那句本身改寫成一行條件式回頭條件」,「已配」只認那一行本身是條件式;過濾收窄(字眼只看否定字眼所在的那一小段,引號與 RULE 欄位裡的字不算);新增上線門檻(準度點估計 ≥40%,重量得 12/30=40%,剛好達標);升級門檻改成寫明資料來源、分母與最小樣本。重點驗:這些新規則照字面實作會不會做錯、上線門檻與升級門檻是不是真的算得出來、提醒字樣照做會不會踩到別的閘。

## 審查要求
1. 逐節讀完整份 spec,不要跳段;內部交叉引用都核對。
2. spec 對程式碼現況的每個假設,用 Grep/Read/Bash 實際查證。
3. 要做實驗:★第一個動作先 cd 到你自己的臨時目錄★,`git clone --shared <repo> <你自己的臨時目錄>`,之後一律 `git -C <臨時目錄>`;不准改 repo 任何檔;絕不在 /Users/enzo/harness/lumos-toolchain 跑任何 git。直譯器 /opt/homebrew/bin/python3。

## 嚴重度
- major/blocker = 照 spec 字面實作會做出錯的行為或漏掉合約;minor = 措辭、文件精度。
- blocking:否 ↔ minor;blocking:是 ↔ major/blocker。
- 低嚴重度疑慮給不出具體失敗場景就不要標;但未定義/壞引用/內部不一致一律要報。

## 輸出格式(硬性,收貨端機械驗)
- 檔案第一個非空行 = 檔級 `severity: <clean|minor|major|blocker>`。
- 每條 finding:`## F1 一句話`(標題不寫等級)→ 恰一行獨立 `severity: <值>` → 一行 `blocking: 是|否` → `引句:「…」` 單獨一行(只准逐字引凍結 spec,≥10 字,引句內不要再包「」)→ 佐證行 ``file: `路徑:行號` ``→ 編號敘述(照 spec 做會在哪個輸入、哪一步出錯)。
- 沒問題的節寫「已讀,無 finding」;整份沒問題就交 `severity: clean`。
- 最後一行寫「最高等級:<值>;blocking 共 N 條」。
