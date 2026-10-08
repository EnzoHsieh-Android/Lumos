severity: major

## Finding 1 — 實際載入的 skill 會靜默跳過試行

severity: major  
blocking: 是

引句:「本 repo 的 `skills/lumos-code-loop/SKILL.md` 已有入口。第2案啟動前核對實際載入的 skill 版本，未同步時由編排者直接讀本計劃，開工與收尾依本表執行；第五次收尾觸發回顧。」

具體場景：

1. `review-repair-pilot-decouple-slim` 日後通過並記為生效。
2. 新程式工作觸發實際安裝於 `/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md` 的 code-loop skill。
3. 該版本沒有五案試行入口，也沒有計劃指標；只有 repo 內版本在 `skills/lumos-code-loop/SKILL.md:16` 有入口。
4. 編排者因此不知道要「直接讀本計劃」，不會檢查第2案資格、登記五格表或在 2026-11-03 觸發到期回顧。這個 fallback 是循環依賴：必須先知道本計劃，才會知道實際載入的 skill 缺本計劃。
5. 若只移除 repo 內入口作回退，也沒有明定如何處置之後可能同步出去的實際載入版本。

這個漂移不是推測：圖譜已明載 repo 版有入口、使用者層版本未同步，見 `docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:22`；我也直接核對過兩份 skill，SHA 不同，安裝版全文沒有「修復穩定性試行」或「五次修復試行」。目前改道仍未生效，因此尚未造成錯誤；同一 Verification 保持 pending，見 `docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:3`、`:16`、`:24`。

最小修正：

把「實際生效入口已接線」列為改道生效的前置條件，而不是第2案執行者的自律步驟。正式 PASS 後、寫入生效時間前，必須二選一：

- 同步實際載入的 skill，並驗證它包含計劃指標；或
- 在 repo 必讀入口建立不依賴 skill 的強制指標。

生效驗證需記錄實際載入檔案的雜湊。回退則同時處理該生效入口，或保留入口但讓它讀到明確的 stopped 狀態。未完成前不得把 Verification 改成 pass，也不得登記第2案。

## 逐節檢查結果

- Frontmatter、開場說明、第一組 PRIOR-ART／RETIRE-IF：無其他 finding。
- S1：除上述入口／登記失聯外，工作資格、重開仍占原序號、中止仍計數及樣本邊界無 finding。
- S2：根因合併、改變／保持行為、紅綠配對、失敗路徑及未驗處置無 finding；與 `skills/lumos-code-loop/reference.md:126`、`:127` 一致。
- S3：前後版本同例分類及「分類不改處置」無 finding；與 `skills/lumos-code-loop/reference.md:129` 一致。
- S4：原席驗原問題、新席驗完整差異、三輪上限及禁止換號洗輪次無 finding；現行 reference 已明文禁止重開編號洗輪次，見 `skills/lumos-code-loop/reference.md:128`、`:129`。
- S5：證據不覆寫、缺值記未知、觀測窗及耗時口徑無其他 finding；到期通知的可達性併入 Finding 1。
- 「收斂性診斷與下次試行的最小調整」、第二組 PRIOR-ART／RETIRE-IF：無 finding。
- 「落點」：無 finding。
- 「試行登記與回顧入口」：除 Finding 1 外，未發現可重現的登記失敗；並行會談先交人裁、不先造鎖，與精簡方向一致。
- 歷史 FAIL 與樣本外儀器修補：無 finding。第四輪仍是 FAIL 且未放行的外部證據見 `docs/lumos-toolchain-knowledge/Verification/2026-10-04_修復穩定性試行第1案例外續修.md:18`、`:35`、`:37`、`:39`。
- 改道 pending design gate：無 finding。實跑 `lumos loop status review-repair-pilot-decouple-slim --disposal …` 顯示目前零筆記錄；圖譜也要求正式處置帳與 PASS 後才生效，見 `docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:24`。
- 比較口徑、證據接線、時間事件、14 天觀測窗與 REVISIT：無其他 finding。
- 「實務隱患」：無 finding。
- 「回退」：停止後保留證據、未結案工作仍占名額、普通 code-loop 照常完成的語意無 finding；生效入口如何同步回退併入 Finding 1。
- 「審計修正紀錄」：無 finding。
- 「第1案逐案紀錄」：停手、交接、三輪上限、FAIL 與未知耗時均未被洗掉，無 finding。
- 「第1案例外續修授權」：例外限一輪、沒有 r5、最終 FAIL 及後續需重新人裁均清楚，無 finding。

已完整讀取 151 行 frozen snapshot；SHA-256 與指定值一致。未讀取其他 reviewer 報告，未修改任何檔案。

最高等級：major  
blocking count: 1
