# 「怎麼確保 AI 寫的測試沒問題」論文全文研讀(2026-11-02)

六組研讀代理各讀一組論文與官方文件的**全文**,交回實驗設計、原文數字與出處、作者建議與限制,以及「這個實驗已經回答了什麼、我們不必重做」;另派一個沒看過結論的代理核對標準缺口。報告是代理交回的原文,只把本機路徑換成 `<研讀暫存>` 或刪掉;英文引句是代理從論文逐字抄的,引用前照報告裡的出處再核一次(報告自己也標了哪些只讀到摘要、哪些數字論文內部不一致)。

| 檔 | 主題 | 讀了什麼 |
|---|---|---|
| `oracle.md` | AI 看得到實作時會把錯寫成預期值 | 六篇(2610.11835、2410.21136、2607.22883、2607.10277、ASE 2025 oracle、2501.17461) |
| `hacking.md` | AI 為了讓測試過而作弊與偵測 | ImpossibleBench、SpecBench、FrogNano、Verification Horizon、Handshake DeepSWE、Specification Self-Correction、TRACE |
| `mutation.md` | 變異測試在業界與 AI 測試生成的用法 | Google 兩篇、Meta TestGen-LLM 與 ACH、AdverTest、MutGen、Kotlin 工具現況與一個 Android 實例的 CI 日誌 |
| `smells.md` | 測試壞味道與偵測工具準確度 | 八篇,含 tsDetect 誤判的人工標註研究與代理過度 mock 的原始出處;另查 detekt、Konsist、Android Lint、Sonar 有沒有現成規則 |
| `flaky-pbt.md` | 不穩測試、順序依賴、AI 寫屬性測試 | iDFlakies、Wei TACAS 2021、FlakeFlagger、Gruber、Android 官方穩定性與 Orchestrator、test-retry 外掛、四篇屬性測試研究、Kotest 與 jqwik |
| `latest.md` | 2026 下半年新研究 | 2610.36584、2606.18168、2607.05139、2608.05917、Meta JiT、2608.29460、Android Bench 2.0 等 |
| `gap-check.md` | 標準缺口核對 | 只讀標準,17 類逐項引原句 |
| `manifest.json` | 本目錄每個檔的 sha256 | |

這些結論怎麼落到工具與標準,見工具鏈圖譜的 `Projects/Android測試防竄改檢查_計劃`。
