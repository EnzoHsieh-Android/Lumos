# r1 收貨紀錄(前掃)

preflight-4: ran

首輪前掃以固定四類清單掃完(9 條:語意命中 7、存在命中 1、①一條、③兩條,有重疊)。核心裁定「指紋改認分支自己的改動、分岔點跟推送參數無關、算不出退回舊指紋」沒被推翻;下列修正逐條折入,審查席可覆核推翻。前掃的實驗倉庫在編排者 scratchpad,收貨後已刪。

| 編號 | 類 | 修改前 | 修改後 | 證據 |
|---|---|---|---|---|
| p1 | ④語意 | 選項寫死 `--no-ext-diff --no-textconv --no-color --no-renames --diff-algorithm=myers -U3` | 沿用 `_NOTE_REREAD_DIFF_ARGS`(已釘前綴)再加 `--literal-pathspecs --no-renames --diff-algorithm=myers --inter-hunk-context=0 -U3`;S5 補 `diff.interHunkContext`、`diff.mnemonicPrefix` | 實驗:`diff.noprefix=true` 沒釘前綴時 patch-id 由 e5cfd26d103e 變 1eecf51ab50c;`diff.interHunkContext=10` 由 9552303b042e 變 28ff4e8f4acf |
| p2 | ④語意 | 照 `patch-id --stable` 規則正規化(去 index、行號,忽略空白) | 只去 `index` 行與 `@@` 數字,空白照算,在 Python 裡做;PRIOR-ART 寫明不借「忽略空白」;新增 S7 | 實驗:Python 檔兩種只差縮排、語意不同的改動 patch-id 同為 18779e053216 |
| p3 | ④語意 | 抽成吃「頂端」參數 | 簽名 `(repo_root, tip)`,「這條分支」改成指向頂端的本機分支,零或多條退回簽出分支;唯一呼叫點傳 HEAD | `_codeloop_default_base` 用 `symbolic-ref HEAD` 找分支、`merge-base --all HEAD` |
| p4 | ④語意 | 同一個 repo、同一個頂端必然相同 | 同一份 refs 狀態下必然相同;補 CI 一段(只印、多列不漏) | 函式讀本機 main/master |
| p5 | ③ | `v1` 標版本 vs S4 等於現行 | `v1`=現行雜湊一字不改;`v2` 加一行版本;補第二層表態要重做 | 現行雜湊輸入沒有版本字樣 |
| p6 | ④語意 | prepare 用 `_lens_push_base`、check 用 `_push_range_start` | 兩者都經 `_note_audit_start`,帶不帶推送參數決定走哪支 | `_note_audit_start` |
| p7 | ④存在 | 照 patch-id 規則 | 併入 p2(Python 內正規化,不跑 `git patch-id`,不需 stdin helper) | `_lens_git` 沒有 stdin 參數 |
| p8 | ① | 候選、主線候選、頂端、對照紀錄未定義 | 緣起後加詞彙一行 | — |
| p9 | ③ | 約數百毫秒到一兩秒 | 沒量過,實作時量;逾時退回 `v1` | `_lens_git` 預設 20 秒 |

## r1 席報告收貨(2026-10-14,6 席)

- 六份報告從逐字稿原樣存檔;quote-check 五份全數錨定,併發席 5 句有 1 句錨不到(引的是收貨紀錄裡的句子,不是計劃本文)——那條(本機 diff 設定還有漏)由邊界席獨立實測 `diff.suppressBlankEmpty` 重現,照採。
- 編號:正確性 正1–正4、邊界 邊1–邊9、整合 整1–整9、併發 併1–併5、回滾 回1–回4、架構對齊 架1–架4,共 35 條,全數折入,無放行、無重現不到。

## 機械重現

| 編號 | 依據 | 判 |
|---|---|---|
| 正2 邊2 整3 | 席位實測:主線改封閉函式 `def` 行後 hunk 標頭尾巴變、指紋變;編排者讀 `_patch_file_changes` 說明確認它也算段落標頭 | HIT |
| 併1 邊3 | 席位實測:兩種二進位改動去掉 index 後雜湊相同 | HIT |
| 正1 邊5 | 席位實測:precompose 下 NFD 檔名用 NFC/NFD pathspec 都查不到;程式註解已記同一坑 | HIT |
| 併2 邊1 | 席位實測 `git diff --literal-pathspecs` 回 129、`git --literal-pathspecs diff` 回 0 | HIT |
| 邊4 | 讀 `_note_reread_scan`:候選用範圍起點的家,指紋用分岔點 | HIT |
| 架1 | 讀 `_patch_file_changes`:已有逐檔、去行號、處理二進位與引號路徑的改動指紋 | HIT |
| 回1 整7 | 席位讀治理帳 101 筆 note-reread 事件無 branch 欄 | HIT |
