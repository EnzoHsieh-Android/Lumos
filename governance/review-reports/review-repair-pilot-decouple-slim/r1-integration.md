severity: major

已完整讀取 151 行凍結快照，SHA-256 符合指定值；未讀其他 reviewer 報告，未修改檔案。

## Finding 1：實際載入的 skill 沒有試行入口，啟用流程無法自行起動

severity: major

blocking: 是

引句:「這是人工試行，現有機械閘不檢查新增欄位；本 repo 的 `skills/lumos-code-loop/SKILL.md` 已有入口。第2案啟動前核對實際載入的 skill 版本，未同步時由編排者直接讀本計劃，開工與收尾依本表執行；第五次收尾觸發回顧。」

情境：下一個 session 依系統實際提供的 `lumos-code-loop` skill 開始第2案。實際載入的是使用者層副本；它沒有五案試行入口，也沒有指向本計劃或「修復穩定性試行」章節。編排者因此根本不知道要先核對同步狀態，「未同步時直接讀計劃」這個備援本身無法被發現。結果會照普通 code-loop 執行，不登記第2案，也不做 S2–S5 的證據蒐集。

證據：

- repo 版入口已存在：`skills/lumos-code-loop/SKILL.md:16`、`skills/lumos-code-loop/SKILL.md:46`
- repo 版 reference 有完整試行章節：`skills/lumos-code-loop/reference.md:122`
- 實際載入版在一般入口後直接進普通流程，缺少試行入口：`/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md:11`
- 實際載入版 reference 從測試說明直接進「記錄」，缺少該章：`/Users/enzo/.agents/skills/lumos-code-loop/reference.md:114`、`:122`
- 圖譜已承認此漂移仍存在：`docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:22`
- 目前生效條件只要求設計閘 PASS 與記錄版本、時間，沒有要求發布或驗證實際載入版：`docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md:72`

最小修正：把「實際載入的 SKILL.md/reference.md 與本輪核准 repo 版本一致」列為改道生效前置條件；至少記錄兩份檔案雜湊並以一個全新 session 證明載入後可看見試行入口。回退也必須同步撤下實際載入版，不能只改 repo 副本。

## Finding 2：圖譜仍把舊 PASS 掛成目前驗證，與待審狀態衝突

severity: major

blocking: 是

引句:「舊 `review-repair-pilot` 的 PASS 不移用。」

情境：接手者先執行 `lumos context Projects/代碼審修復穩定性試行_計劃 --brief`。圖譜目前只在 `verified_by` 顯示 2026-10-03 的舊 PASS；新的改道驗證仍是 pending。若接手者或自動流程以結構欄位判斷是否已驗證，就可能把尚未通過的改道當成已放行，提前登記第2案。

證據：

- 計劃目前的唯一 `verified_by` 是舊驗證：`docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md:15`
- 舊驗證明定修改試行入口、取樣、分類、計量或交接時要重驗：`docs/lumos-toolchain-knowledge/Verification/2026-10-03_代碼審修復穩定性試行落地.md:6`、`:9`
- 目前改道驗證仍是 pending，明說未生效：`docs/lumos-toolchain-knowledge/Verification/2026-10-04_代碼審改道生效驗證.md:2`、`:16`

最小修正：正式 PASS 前，不再讓舊驗證以現行 `verified_by` 身分代表目前版本；保留為歷史證據即可。正式閘通過後，把核准快照雜湊、生效時間及 skill 同步結果寫入新的改道驗證，將其轉成 pass，並同步回計劃的 `verified_by`。

## Finding 3：第2案只在 intake 領號，崩潰交接後可能重複占用同一格

severity: major

blocking: 是

引句:「第2案之前須核對本表仍為待登記、該工作沒有既有試行序號，並在首輪 intake 記工作來源、接手時間、基準提交及是否依賴未放行探針。」

情境：會談 A 在自己的首輪 intake 登記「第2案」後，尚未更新五格表便中斷。會談 B 接手時依規格讀五格表，仍看到第2格是「待登記」，於是把另一個工作也登記成第2案。單一編排者限制能避免已知的同時操作，卻不能處理崩潰或未完成交接；兩個 intake 最終都聲稱第2案，後續樣本、耗時及 finding 歸因無法可靠合併。

證據：

- S1 明確把序號與 loop id 登記位置指定為首輪 intake：`docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md:30`
- 啟動前只要求讀表並確認「待登記」，沒有要求先占用該列：同檔 `:52`
- 第2至5格目前只有「待登記」，沒有 claim 狀態：同檔 `:56`
- S5 只明確要求收尾時補表中結果：同檔 `:34`

最小修正：首次派工前先在五格表同一列寫入工作、loop id、intake 路徑、接手時間與 `claimed` 狀態，再寫 intake；該列成為崩潰恢復的權威入口。接手者選新案前先核對已 claim 的列及其 intake，claim 後即使中止也不得重用。

## Finding 4：第1案最新交接提到三篇 Issue，但圖譜只連到一篇

severity: minor

blocking: 否

引句:「下次仍限aspidochelone，先讀本計劃、最新Verification與三篇open Issue（讀碼、Git隔離、共用沙盒清理），確認無另一協調者。」

情境：未來若重新界定第1案，接手者從計劃執行 `lumos context --brief`，只會得到「探針讀碼證據不足」的直接 Issue；Git 隔離與共用沙盒清理兩項 blocking 歷史沒有圖譜邊。若接手者只沿圖譜連結而沒有再用三個同義詞搜尋，就可能漏掉兩個仍 open 的放行阻擋。

證據：

- 計劃 `related` 只列讀碼 Issue：`docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md:17`
- Git 隔離 Issue 仍為 open：`docs/lumos-toolchain-knowledge/Issues/探針Git隔離的設定與絕對路徑缺口.md:1`、`:15`
- 共用沙盒 Issue 仍為 open：`docs/lumos-toolchain-knowledge/Issues/探針共用沙盒清理失敗仍繼續評分.md:1`、`:14`
- 最新 Verification 也要求從三篇 open Issue 重驗：`docs/lumos-toolchain-knowledge/Verification/2026-10-04_修復穩定性試行第1案例外續修.md:39`

最小修正：在最新交接段及 `related` 中加入兩篇缺失 Issue 的正式 `[[Issues/...]]` 連結，讓 `lumos context` 能完整推出三個阻擋入口。

## 已讀且沒有其他 finding 的部分

- 開頭目的、PRIOR-ART、總體 RETIRE-IF：無 finding。
- S1：除 Finding 3 的領號持久性外，樣本資格、重開與中止計數無 finding。
- S2：根因分組、改變／保持行為、壞例與好例、失敗路徑無 finding。
- S3：以同例前後版分類，且不以來源分類降低嚴重度，無 finding。
- S4：原席驗原問題、新席看完整差異、三輪上限與停止疊補丁，無 finding。
- S5：未知值、觀測窗、escape、已入帳證據不覆寫，無 finding。
- 收斂性診斷與多入口小表：和 pending 根因盤點一致，沒有把診斷冒充成效果證明；無 finding。
- 試行表中的第1案、樣本外儀器修補、歷史四輪 FAIL：與 Verification 的 abandoned／pending 狀態一致；無 finding。
- 改道的樣本資格、探針工作排除、歷史與新工作分列：除 Findings 1–2 外無 finding。
- 耗時、根因組、缺陷去重、14 天曝光窗與未知值口徑：無 finding。
- intake 證據接線及不可追加规则：無 finding。
- 實務隱患：四類均有明確處置；無 finding。
- 回退：停止後不再執行試行、在途工作仍按原 code-loop 完成、歷史證據保留，語意無 finding；只有 Finding 1 所述發布副本同步缺口。
- 審計修正紀錄、第1案逐案紀錄及例外續修：FAIL、未推送、未宣稱收斂或因果效果均保持；除 Finding 4 的圖譜連結外無 finding。

最高等級：major  
blocking count: 3
