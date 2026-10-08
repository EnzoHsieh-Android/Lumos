# code r3 收貨紀錄(併發與效能表態背書,末輪)

## 收貨三道(兩席+資安席)

- report-normalize:兩份都已正規化,沒改。
- quote-check(對 r3-snapshot.patch):兩份全數錨定。
- refcheck:兩份引的 file:line 全部存在。
- 修正差異另存 r3-delta.patch(上一輪之後的修正,兩席的火力集中處)。
- 資安席:問閘指出資安席只看過 r1 材料、之後三支檔又改過,補派一席對 r3-snapshot.patch;兩席的折入差異當參考附上(r3-fold-before-security.patch,不當引句來源)。報告已正規化、引句全數錨定、file:line 全部存在。

## 編排者重現

| 席位 id | 重現 | 結果 |
|---|---|---|
| R3A1 | grep 到既有 `_git_is_shallow`(內容就是 rev-parse --is-shallow-repository、有 OSError 容錯,三個呼叫端),本案在 `_codeloop_record_valid_ex` 另寫一套 | HIT 採信 |
| R3A2 | `_drift_jsonl_rows` 讀檔前檢查 is_symlink、是連結就讀成空;gov 的 load 原本 read_text 會跟連結 | HIT 採信 |
| R3S1 | 引句錨定;`_backing_kill_rows` 只驗欄位型別與 sha 格式,kill-log 在本 repo 進版控,covers 與 note 原樣取自帳檔那一行(note 會進審查席提示) | HIT 採信 |
| R3C1 | 完整 clone 裡對 "f"*40 呼叫 `_codeloop_record_valid_ex`:回 unsure=False,但說法仍是「判不了是不是祖先」;新測試 ⑤-1b 釘住 | HIT 採信 |

refuted-set:none。本輪有 major 席(架構對齊),依規則 accepted 必空,全部折入。

## 處置

- R3A1:給 `_git_is_shallow` 加選填 timeout 參數(預設 None,既有三個呼叫端行為不變),本案改呼叫它;逾時照舊丟 TimeoutExpired 由外層接成判不了。
- R3A2:席位給兩條路(改用或註明)。改用會讓連結過來的治理帳悄悄讀成空的,改變 gov 既有行為,故選註明,在 load 內寫明不走的理由。
- R3S1:kill-log 行對回筆記現有配方(`_backing_note_recipes`),covers 與說明取筆記;node 指到知識庫外或非 .md 略過;新測試 t_contract_backing_note_recipes 四格,三個突變(covers 取帳檔、拿掉知識庫邊界、說明取帳檔)各翻紅一格。照現有配方偽造 killed 仍擋不住,記進計劃〈天花板〉第 8 條。
- R3C1:完整歷史裡找不到的提交改說「不可能是目標的祖先」;淺 clone 維持原句。預設呼叫端在完整 clone 裡看到的說法也跟著變準(判定不變)。
- 相關子集全綠:contract_backing 37、codeloop 167、gov_ 116、regen 33、provenance 18、guard_settle 38、drift_c4 26、drift_fix 146。

## 天花板

上限三輪已到,本輪的折入沒有再派新席掃:R3A1/R3A2/R3C1 改動小(一個函式加參數、一句訊息、一行註解),資安席有當參考看過;R3S1 的修正(對回筆記配方,約 40 行)沒有任何席看過,只靠新測試與突變翻紅兜底。
