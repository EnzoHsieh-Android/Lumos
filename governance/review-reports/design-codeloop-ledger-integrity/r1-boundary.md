severity: major

凍結稿的 SHA-256 已核對為 `f66bd1107b9fa25523d4ee9517c9b038e9e9eb8260d22a88cedfd7f9f8cc2577`。以下只按該稿、派工材料及相關程式與測試審查；未讀其他席報告，未修改檔案。

## 寫入邊界

### F1：帳檔是 symlink 或特殊檔時，足額寫入不代表帳列可讀回

severity: major  
blocking: 是  
引句:「整筆 UTF-8 JSON 與 LF 以單次 bytes 寫入並驗回報長度」  
file:line: [凍結稿:23](/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-ledger-integrity-XXXXXX.S068FMSim5/repo/governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:23)；現行寫者見 [scripts/lumos:35325](/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-ledger-integrity-XXXXXX.S068FMSim5/repo/scripts/lumos:35325)。

可重現輸入：令 `docs/.governance-log.jsonl` 指向 `/dev/null`，再寫一筆 `dispositions`。**預期**是拒絕寫入、不建立 marker；**依凍結稿字面實作的結果**可以是讀到空尾、寫入回報完整長度，因而宣稱成功並建立 marker，但帳列隨即讀不回。稿中未要求確認目標是一般檔案或拒絕 symlink；「鎖策略不可用時失敗」也未涵蓋此情況。這直接破壞本案的「寫入成功 ↔ 完整列可讀回」契約。

## 讀取邊界

### F2：外層是 JSON 物件仍可能使讀者中斷，後續好列無法使用

severity: major  
blocking: 是  
引句:「讀側共用「原始 bytes 以 LF 結尾、嚴格 UTF-8、JSON 物件」才算一列的判準；本案盤點並遷移」  
file:line: [凍結稿:25](/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-ledger-integrity-XXXXXX.S068FMSim5/repo/governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:25)；受影響讀者見 [scripts/lumos:7245](/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/lumos-ledger-integrity-XXXXXX.S068FMSim5/repo/scripts/lumos:7245)。

可重現輸入：在兩筆有效列之間放入 `{"gate":"design-loop","kind":"rewrite","nodes":42}\n`。它符合稿中完整 LF、嚴格 UTF-8、JSON 物件三項條件。**預期**是這筆欄位形狀錯誤的列不妨礙後面的好列；**現況**是 `cmd_gov` 迭代整數 `nodes` 時拋出 `TypeError`，現有逐列例外處理也接不住。只共用稿中三項判準，無法兌現「壞列前後的好列仍可用」。

## 其餘邊界

- 壞 UTF-8、外層非物件 JSON：已讀，無 finding。
- LF／CRLF／單獨 CR 與既有帳：已讀，無 finding。現有帳的 93,269 列均為 LF 結尾的 JSON 物件。
- 一般權限拒絕與鎖不可用：已讀，無另立 finding。

總結：**2 條 finding，blocking 2 條。**