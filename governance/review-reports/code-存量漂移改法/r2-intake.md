# r2 收貨紀錄(code-存量漂移改法)

凍結材料:53b6389c..429b109f 的 git diff -U10(第 1 輪的修正本身),1092 行,沒超過 1800 行,不拆;`r2-snapshot.patch`。
4 席全新:正確性 opus、外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)、架構對齊 sonnet 5.5、資安 sonnet 5.5。
偏離:派工鏡頭同第 1 輪由編排者先算好存檔當參考資料;鏡頭只信主線可達的起點,53b6389c 不在主線上,改用整批範圍 19162c1e..HEAD 算(牽連的節點同一批)。

## 席位收貨

- 4 席全交,等完成通知、ls 確認後才讀;clone-ns 的 reflog 只有編排者自己的提交,席位沒動 repo。
- report-normalize 4 份都合格(派工詞這輪寫明最後一行用「最高等級:」);quote-check 4 份對 r2-snapshot.patch 全錨定;refcheck 全對得上。
- seat-check:三席報「沒提到 r2-snapshot.patch」——報告寫的是「審材」「這份 diff」;引句全錨得回凍結 patch。只觀測不擋。
- 發現 11 條:正確性 7、外家否決 1、架構對齊 2、資安 1;major 3 條(機器數各報告的獨立 severity 行:正確性 F1 F2、外家否決 F1)。
- 多席獨立報到的同一件:c4 的 --old 連引號一起框就繞過標準 YAML 檢查(正確性 F1、外家否決 F1)。
- 同一類第二次(第 1 輪邊界 F2、外家 F1 也是 c4 的標準 YAML):照「同類兩輪換形狀」,不再推「換之前那一項有沒有引號」,改成只看換完的結果。
- 本輪有 major,accepted 必須是空的,11 條全折。

## 機械重現(在審的那一版 429b109f 上;方法同第 1 輪:折入後的新測試格,把修法還原回去就翻紅;每個改壞都在全新 clone、清掉 __pycache__ 後跑)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性 F1 / 外家否決 F1(--old 框到引號繞過) | `_drift_c4_yaml_err` 改回只看換之前 | HIT:t_drift_fix_review_r2_edges ①紅,`本工作樹(未提交)"`→`已提交 abc` 回 0;外家否決席另附 Ruby Psych 讀改後結果報 SyntaxError |
| 正確性 F1 之 3(行內清單) | 行內清單改回放行 | HIT:①Q4 那格紅 |
| 正確性 F2(「看:」那行沒加引號) | 「看:」那行拿掉 `_drift_sh` | HIT:②紅,照貼切不回同一個節點;席位另附 bash 實跑產生 PWNED 檔 |
| 正確性 F3(認不出本專案的橫幅寫法) | 橫幅正則改回只認 > 與 ** | HIT:③B1、B2 紅(疊出第二個橫幅) |
| 正確性 F4(佔位字誤擋 Map<K,V>) | 佔位字正則改回任意 <…> | HIT:④紅 |
| 正確性 F5(deps 接線沒測、⑭假綠) | c1、c5 的 deps 改成空的 | HIT(席位觀察成立):原測試全綠;補 ⑤ 與 c5 測試 ② 後兩個改壞都翻紅。⑭加前置斷言:本機(macOS)跳過並印出,Linux CI 才跑得到 |
| 正確性 F6(git 指令用 NFC 路徑) | `_drift_git_arg` 改回索引鍵 | HIT:⑦紅(替身 `_guard_raw_git_path` 回 NFD 拼法);本機檔案系統不分 NFC/NFD,真實現場跑不出來 |
| 正確性 F7(計劃清單沒過 _esc_clean) | 讀 cmd_drift_ack 預覽與成功訊息 | HIT:讀碼確認;縱深防禦,沒另寫測試 |
| 架構對齊 F1(`_drift_sh` 第三種加引號) | 讀 `_sh_quote` 與各處內聯 shlex.quote | HIT;`_drift_sh` 改成只在全是安全字元時原樣,其他交給既有 `_sh_quote` |
| 架構對齊 F2(`_drift_phys` 第三份 NFC 比對) | 讀 `_plan_file_exists` 與 `_drift_phys` | HIT;收成通用的 `_nfc_child` 與 `_phys_path`,`_plan_file_exists`、drift、結案列回頭條件共用(escape 子集 139 格、drift 子集 415 格綠) |
| 資安 F1(- 開頭的參數) | `_drift_sh` 拿掉補 ./、`_drift_fix_target` 拿掉認 ./ | HIT:⑥兩格各自翻紅 |

## 推送前檢查

- 新增告警閘對 19162c1e..e7112c53:0 條新增(第 1 輪那 5 條本機日期告警的放行照樣有效);受波及合約測試 59 支照跑。

## 處置

- 11 條全折(folded),accepted 空、refuted 空。程式與測試在 e7112c53(`wip: 代碼審 r2 折入`);家節點 Systems/存量漂移守衛 的 c4 PITFALL 改寫成「只看換完的結果」、引號與佔位字兩行補上這輪的修法,TEST 清單加 t_drift_fix_review_r2_edges。
