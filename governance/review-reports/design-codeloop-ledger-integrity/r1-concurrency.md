severity: major

已核對凍結稿 SHA-256：`f66bd1107b9fa25523d4ee9517c9b038e9e9eb8260d22a88cedfd7f9f8cc2577`。以下兩項是凍結稿要求沿用現有鎖方法時的設計缺口；交錯依程式路徑推演，未執行會寫檔的重現測試。

## Finding 1：過期鎖接手可讓兩個寫者同時持鎖

severity: major  
blocking: 是  
引句:「沿用專案 `_excl_lock_try` 的獨佔鎖檔方法，以 `docs/.governance-log.jsonl.lock` 為同一鎖鍵，等待上限 2 秒、鎖檔過期門檻 900 秒」  
file:line: `governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:23`；`scripts/lumos:33854`、`scripts/lumos:33861`、`scripts/lumos:33868`

可重現輸入與交錯：先放一個超過 900 秒的鎖。A、B 都讀到「已過期」；A 搬走舊鎖並建立自己的新鎖；B 隨後執行已決定好的 `rename`，搬走的卻是 A 的新鎖，然後建立 B 的鎖。現有 `_excl_lock_try` 對搬走的鎖沒有再核對身分，A、B 都會收到成功。預期只有一個寫者進入鎖內；照凍結稿直接沿用此方法，兩者可同時進入，S2 的互斥前提不成立。

## Finding 2：900 秒過期接手不能阻止原持鎖者繼續寫

severity: major  
blocking: 是  
引句:「鎖內檢查既存尾端是否以 LF 結束，整筆 UTF-8 JSON 與 LF 以單次 bytes 寫入並驗回報長度，釋放時只刪自己的鎖。」  
file:line: `governance/review-reports/design-codeloop-ledger-integrity/r1-snapshot.md:23`；`scripts/lumos:33845`、`scripts/lumos:33855`

可重現輸入與交錯：A 取得鎖並確認帳尾有 LF，在寫入前暫停超過 900 秒。B 依過期規則接手，發生短寫，留下無 LF 殘尾並回報失敗。A 恢復後仍按先前檢查結果寫入完整 JSON，接在 B 的殘尾後。預期 A 失去鎖後不能再寫，後續寫者也不能接上殘尾；凍結稿只有按鎖檔年齡接手與入鎖時的一次尾端檢查，未規定如何阻止仍存活的舊持鎖者完成寫入，因此 S1、S3 可同時失守。

## 其餘鏡頭

短寫回報、讀者在寫入中間只採 LF 完整列，以及表態讀帳失敗時阻擋：已讀凍結稿、相關程式與測試，無其他 finding。

總結：鎖過期不等於原寫者已停止；現有接手方法還有搬走新鎖的交錯。**blocking 數：2。**