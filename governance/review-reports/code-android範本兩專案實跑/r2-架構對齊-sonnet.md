severity: minor

**1. 分層與依賴方向:對齊**
- 新驗證紀錄放在 `Verification/`,並指回所驗的計劃和系統筆記。它的 `plan_refs` 和 `system_refs` 寫法與 `Verification/2026-11-08_detekt的CI型別檢查範本實跑.md:11-14` 相同。
- 範本改寫(AGP 9 的 detekt 2.0、Slack 預設關的規則、`check` 不帶 `detekt<變體>`)都寫進 `Systems/linter精選目錄.md` 的〈②CI 型別檢查範本〉和〈Android Lint 與 Compose lint 標準接法〉。這兩段是範本的家,與既有放法一致。
- 其他篇的檔案和類別只用 `[[連結]]` 或純文字帶過,沒有用反引號寫別人的檔。
- `verified_by` 加了新紀錄,`REVISIT` 用 `[closed:…]` 結案,計劃的 `status` 與 `updated` 一起改。
- 實測落差寫進 `Android現成檢查接上CI與推送前_計劃.md` 的〈審計修正紀錄〉。該節已有「實作更正」「推送閘更正」兩條非審查條目,新條沿用同一做法。
- 另外三篇計劃只改 `status`、`updated` 和標籤,沒有多寫內容,不構成層級問題。

**2. 命名與寫法:一處不一致**
- 開頭欄位 `type/status/date/valid_under/revalidate_when/tags/plan_refs/system_refs` 與 11-08、11-06 兩篇鄰居相同。
- 白話開頭是「驗 [[計劃]] 的手驗條款 S5——…**結果:…**」,與 `2026-11-08_detekt的CI型別檢查範本實跑.md:17` 同形。
- 「怎麼跑」「結果」表、「範本與實測對不上的」三節的標題和順序也和 11-08 篇一致。
- 新 `PITFALL:` 帶了 `[出處:][根因:][repro:][修法:]`,必有鍵齊全,縮排與前一行 `PITFALL:` 相同。
- `REVISIT:2027-02-09 …` 的格式與既有 `REVISIT:` 相同。
- 不一致在 B1。

**3. 第二種做法:無**
- 結案標記沿用既有的 `[closed:日期 理由]`,如 `Projects/detekt協程規則真的在跑_計劃.md:70`。
- 摘要行前綴、驗證紀錄章節、計劃的更正條目都沿用現有寫法,沒有新機制。

**B1**
severity: minor
blocking: 否
引句:「實驗複本與各步驟輸出在會談暫存區,要留的結果都寫在這一篇,收尾刪除。」
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-08_detekt的CI型別檢查範本實跑.md:40`
說明:兩篇鄰居的結尾都寫成已完成的「收尾已刪」(`Verification/2026-11-06_Android儀器測試範本與架構測試實跑.md:80` 是「;收尾已刪」)。新篇寫成未完成式「收尾刪除」。這篇是紀錄,應寫實際已發生的事,與鄰居不同調。

不對齊共 1 條,其中 major 0 條
