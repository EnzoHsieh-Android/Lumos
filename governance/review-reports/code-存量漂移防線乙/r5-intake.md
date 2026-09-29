# r5 收貨紀錄(code-存量漂移防線乙;上限後第二次破例輪)

破例依據:第 4 輪(第一次破例)仍有 major,Enzo 2026-09-29 裁「再破例審一小輪」。
凍結材料:r5-snapshot.patch(第 4 輪修正差異 402b288c..5c8ee32f,只含 scripts/ 與圖譜筆記,起點是「接到新主線、清完衝突標記」那一版;484 行,sha256 3dbee877…)。5 席全新:正確性 opus;併發、資安、架構對齊 sonnet(Sonnet 5.5);外家 finder Codex(gpt-5.6-sol xhigh,唯讀沙盒)。派工詞要求「已看,無 finding」每一塊也附引句(clean 席才當得了載體)。

## 席位收貨

- 5 席全交,等完成通知、ls 確認後才讀;clone-ns 的 reflog 只有編排者自己的提交,席位沒動 repo。正確性席在編排者暫存區的報告目錄多留了一支實驗腳本 probe.py(派工詞只准寫報告檔);在 repo 外、不搬進卷證。
- report-normalize:4 份已是正規化格式;併發席總結句寫「無 blocker、無 major、無 minor」被工具判成總結句藏更高等級(字面誤判),請同一席只改那一句措辭(不改判斷)。quote-check 5 份全錨定。
- 發現 12 條(正確性 4、架構對齊 2、外家 4、資安 1、併發 0);major 5(架構對齊 F1、F2,外家 F1、F2、F3),其餘 minor。
- 同一件事被兩席報到的:SHA-256 空樹(外家 F1、正確性 F4);點名與候選不分程式檔與測試檔(外家 F3、正確性 F1);r3 回歸測試說明過時(外家 F4、正確性 F2)。
- 本輪有 major,accepted 必須是空的,12 條全折。
- 上限處置:第二次破例輪仍有 major,再問人;Enzo 同日裁「修完直接推」(這道檢查預設只提醒、不擋)。★這一輪的修正差異沒有再經審查★,每條各有翻紅測試。

## 機械重現(在審的那一版 5c8ee32f 上跑;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 架構對齊 F1(提交編號判定寫第三份) | `grep -n "^_LENS_SHA_RE" scripts/lumos` | HIT:既有常數認 40/64 碼 |
| 架構對齊 F2(條件拆法四處各寫) | 讀 prefetch、one、_drift_probe_cond_candidate、_drift_row_unread 與 _drift_probe_one 的 status 分支 | HIT:讀碼確認 |
| 外家 F1 / 正確性 F4(SHA-256 空樹) | `git init --object-format=sha256` 後以 `_drift_empty_tree` 對照:SHA-256 repo 算出 6ef19b41…、SHA-1 repo 4b825dc6… | HIT;席位附的 git diff 回 128 沒重跑 |
| 外家 F2(帶標點名稱耗光預算) | 讀 _drift_probe_cond_candidate:非 \w 名稱每條接全文再跑正則 | HIT:讀碼確認;修完以 850 條 6MB 釘測試 B1(改回舊寫法 66.8 秒) |
| 外家 F3 / 正確性 F1(點名與候選不分類) | 讀 names_in 與 _drift_row_unread:用 _drift_probe_code_path 篩,沒看 _nodehome_is_test | HIT:讀碼確認;修完照席位的兩個情境釘測試 A1、A2 |
| 外家 F4 / 正確性 F2(r3 測試說明過時) | 讀 t_drift_code_review_yi_r3_regressions docstring | HIT |
| 正確性 F3(家筆記 TEST 清單缺 r4) | 讀 Systems/存量漂移守衛 的 TEST 行 | HIT |
| 資安 F1(筆記路徑與原文沒跳脫) | 讀 _drift_print_findings、_drift_report_must、_drift_scan_print | HIT:讀碼確認(推論,席位標了未實測);修完釘測試 D1 |

## 處置

- 全部折進程式、測試與筆記:
  - 架構對齊 F1:改用 `_LENS_SHA_RE`。
  - 架構對齊 F2、外家 F3、正確性 F1:新增 `_drift_cond_split`(symbol/test 拆路徑與名稱)與 `_drift_status_target`(status 找筆記),判定、預讀、候選篩選、點名都用它們;`names_in` 依程式檔/測試檔分類建集合;樹上新增 `unread_for`,點名只算這個條件看的那一類;測試 A1、A2。
  - 外家 F1、正確性 F4:漂移的兩條 diff 路改用 `_drift_empty_tree`(這個 repo 算出的空樹,標準輸入明確給空);其他閘同一個常數沒動,開 [[Issues/SHA-256的repo其他閘仍用SHA-1空樹]](REVISIT 2026-12-29);測試 C1。
  - 外家 F2:`_DriftNames.has`:帶標點的名稱先查每個字詞在不在集合,都在才對全文跑一次正則,全文只接一次;測試 B1。
  - 外家 F4、正確性 F2:r3 回歸測試的翻紅說明改寫。
  - 正確性 F3:家筆記 TEST 清單補 r4、r5。
  - 資安 F1:三處印出(check 的判不了清單、發現清單、scan 報告)的路徑、原文、說明都經 `_esc_clean`;測試 D1。
- 翻紅驗證(每項在乾淨複本改壞一處、清快取後跑對應測試):names_in 不分類 → A1 紅;點名不分類 → A2 紅;不先查字詞 → B1 紅(66.8 秒);空樹寫死 SHA-1 → C1 紅;印出不消毒 → D1 紅。
- refuted 無;accepted 無。
