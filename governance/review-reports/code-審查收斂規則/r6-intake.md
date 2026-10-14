# code-審查收斂規則 r6 收貨紀錄

七席全回(正確性、併發、邊界、合約、通才、架構對齊、資安),report-normalize 都不用改。共 16 條:正1–4、併1、邊1–3、合1–5、通1、架1、資1。資安席在時限內沒找到能讓新殘留不經高風險審進主線的繞法(改名、改 notes、分次推送、讀不出、各 GIT_* 變數都試過),只有一條 `GIT_DIR` 的小縫。

## 機械重現(quote-check 錨不到的)

| id | 錨不到的引句 | 重現 | 判定 |
|---|---|---|---|
| 合3 | 「四個分支逐字同一段」(不到 10 字) | `grep -c '四個分支逐字同一段' r6-snapshot.patch` = 1 | HIT,採信 |
| 合4 | 「一律設 `GIT_NO_REPLACE_OBJECTS=1`(代碼審 r4 資安席」(席位加了反引號) | `git grep -n 'GIT_NO_REPLACE_OBJECTS=1' HEAD -- docs` → Systems/pitfalls-code-loop.md 第 67 行「一律設 GIT_NO_REPLACE_OBJECTS=1,本機 git replace 偽造不了起點(代碼審 r4 資安席)」 | HIT,採信 |

## 根因分組與處置

同輪有 major(併1),accepted 必空,16 條全部折入。

- G1 鏡頭排序級(併1):舊索引(沒有 notes 欄)加上改到任何圖譜檔,所有舊殘留都進 notes_unknown,跟「這次新增」同排級 0、再照節點名排,只取前 5 條;實測 5000 筆舊殘留加 1 筆新增,新增那條出現 0 次。→ 拆排序級:這次新增、合約改字排 0;改到筆記、換位置排 1;位置未知不逐條展開,彙總成一行(幾筆、哪幾篇改了)。先紅測試照併發席情境。
- G2 notes 解不出或寫錯(正1、邊1、通1):決策作廢或指標對不到時 notes 永遠缺,每次改圖譜都升 high、理由卻叫人跑 --reindex(修不好);notes 指到不存在的檔或大小寫不同時靜默判 light;舊索引升級後 doctor 報不一致。→ `--add`/`--reindex` 解不出時記明確的「解不出」與原因,理由句照實寫原因(不叫人跑 --reindex);分級讀 notes 時確認那個路徑在起點樹裡存在(大小寫照 git 的路徑比),不存在當成位置未知;doctor 對沒有 notes 欄的舊索引印「舊格式,跑 --reindex 補上」而不是當成不一致。
- G3 圖譜檔判定(正4、架1、邊2):`_residual_graph_file` 另寫一小段,`docs/<名>-knowledge/` 底下非 .md 也算、任何層級含 `Projects` 也算,圖譜根目錄的指標(`Home#d1`)算出空集合;判定分支沒有測試守(改成 return False 照綠)。→ 併進既有 `_vault_slug_of`(擴充認 `docs/knowledge/`),只認圖譜資料夾底下的 .md;根目錄指標照算;補非標準圖譜位置的測試並做變異。
- G4 鏡頭小缺口(正2、正3):沒有殘留的 repo 預算用完也印「算不出來」;一次逾時或讀不出的「算不出來」被快取下來。→ 先確認有沒有殘留索引,沒有就不出段;殘留段算不出來時那次結果不寫快取。
- G5 入口環境(資1、合3):`GIT_DIR` 能讓本機分級讀成 light;入口 WHY 沒寫代價(所有子行程繼承,含 bound-tests、fix-check 跑的使用者專案測試)、出處是過程紀錄;`GIT_EXTERNAL_DIFF` 那行沒測試。→ `GIT_DIR`/`GIT_WORK_TREE` 不清(git 跑掛鉤時本來就會設它們,清掉會讓掛鉤在工作樹裡讀錯 repo),在 WHY 寫明範圍外與理由(同一個設定也讓真正的推送推到假 repo、CI 在乾淨環境重算);WHY 補 `[代價:]`、出處改寫成可查的卷證;補一支 `GIT_EXTERNAL_DIFF` 測試(帶一支會改輸出的外部差異工具時結果照舊,拿掉那行會紅)。入口五行不動(四個分支逐字同一段)。
- G6 條款、文件與測試(合1、合2、合4、合5、邊3):條款綁定少列四支測試、`t_reference_residual_lens_docs` 沒條款認領;把關強度在 reference.md、圖譜即合約.md、templates §3、計劃 WHY 仍說得過強;兩處仍用逐呼叫帶 env 的舊說法、索引欄位沒寫 notes;圖譜即合約.md 與 06 沒寫粗粒度代價、templates 沒講只改筆記也會附段;NFC 那步沒測試釘。→ 條款補綁;各處照實寫「只保證跑一輪高風險代碼審,審查席有沒有答沒有機械核對」;舊說法改掉、補 notes;代價與附段條件補齊;補 NFD 路徑測試。

## 修補因果核對(regression)

上一輪修補範圍 6b8d81bd..03984a65(r6-repair.patch)。資1(`GIT_DIR`)是原始缺口,不是 r5 修補帶進來的;其餘 15 條都落在 r5 修補新加或改寫的程式、測試或文件(notes 欄、鏡頭排序、圖譜檔判定、快取 schema、入口與 WHY、文件與條款),判為回歸。

regression-set:正1,正2,正3,正4,併1,邊1,邊2,邊3,合1,合2,合3,合4,合5,通1,架1

refuted-set:none。

## 記帳的審查行數

正確性、併發、通才、架構對齊記 repair-lumos 加 snapshot-lumos(2971 行),邊界記 repair-lumos 加 repair-tests(1433 行),合約記 repair-docs、snapshot-docs、repair-tests(1641 行),資安記 snapshot 加 repair-lumos(5955 行)。
