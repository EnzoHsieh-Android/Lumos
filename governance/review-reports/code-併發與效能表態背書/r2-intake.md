# code r2 收貨紀錄(併發與效能表態背書)

## 收貨三道(三席)

- report-normalize:三份都已是正規化格式,沒改。
- quote-check(對 r2-snapshot.patch):架構對齊、資安全數錨定;正確性席三句中第 1、2 句錨不到(第 1 句引的是 diff 外既有的 `_codeloop_bookkeeping_code` 兩行,第 2 句跨兩行而快照每行帶 `+` 前綴),見下表機械重現。
- refcheck:正確性席 `governance/replay/readme` 不存在——那是席位重現用的假想檔名(簿記資料夾內沒副檔名的檔),不是引用;其餘全部存在。

## id 對照

正確性席報告沒有編號,依出現順序編:R2C1=簿記檔讀不到內容被當確定無效、R2C2=找不到的舊提交連帶否決同題強證據、R2C3=殘行吃掉下一筆。架構對齊席:R2A1=另寫讀帳 helper、R2A2=`_ex` 三元組命名沒先例。

## 編排者重現

| 席位 id | 重現 | 結果 |
|---|---|---|
| R2C1 | 修前版本(2c8bd5ef)配上新測試 t_contract_backing_bookkeeping_unsure:② 讀不到內容 → 判不了 紅(2 passed, 1 failed);修後綠 | HIT 採信 |
| R2C2 | 修前版本配上 t_contract_backing_cases:⑤-1 完整歷史裡找不到的提交不連帶否決 紅,原因印「版本驗證逾時或出錯:記錄 sha ffffffff…找不到」;修後綠 | HIT 採信 |
| R2C3 | 引句錨定;行為即計劃〈天花板〉第 6 條已承認的情況 | HIT 採信 |
| R2A1 R2A2 | 引句錨定;`_drift_jsonl_rows` 存在且語意同席位所述 | HIT 採信 |

refuted-set:none。三席最高 minor,可附理由放行。

## 處置

- 折入:R2C1、R2C2、R2A1(已修進功能提交,測試見上表)。
- 放行:R2C3——計劃〈天花板〉第 6 條已承認;補換行的修法在代碼審 r1 被架構席判為第二種做法而拿掉,只提醒的背書最壞是少算一筆 survived。R2A2——保住兩個既有呼叫端的二元組簽名,架構席自己判結構合理。
