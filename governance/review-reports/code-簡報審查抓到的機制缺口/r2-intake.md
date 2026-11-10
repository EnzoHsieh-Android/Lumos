# code-簡報審查抓到的機制缺口 r2 收貨

全新架構對齊席,審 r1 修補後的整包 r2-pack-arch.patch(543 行),另附修補差異 r2-repair.patch 幫它定位。

## 機械收貨

- report-normalize:已是正規化格式。
- quote-check(對 r2-snapshot.patch):3 句引言全數錨定。
- refcheck:佐證 10 處全部對得上。
- 收貨時 repo 只有治理帳、逃逸帳與這個卷證資料夾有變動,席位沒動 repo。席位本機沒有 ast-grep,只讀檔沒實跑;逐例表由編排者實跑(下面)。

## 判讀

| id | 席位等級 | 觀察重現 | 判準 | 去向 |
|---|---|---|---|---|
| b1 | minor | HIT:計劃 S1 寫「同一支壞例檔裡另有 Service 類別時」,綁的 `t_kotlin_rulepack_security_rules` 只吃逐例表、不讀樣本 | 條款字面跟綁定測試對不上,minor 成立 | 折:S1 改照逐例表 C227~C233 的七種情況寫 |
| b2 | minor | HIT:型錄表頭沒有「情境說明」欄,實際改在名稱欄 | 計劃用了不存在的欄名,minor 成立 | 折:計劃改成「在名稱欄補一句」並照實際措辭 |
| b3 | minor ⚠ | HIT:壞例檔放了兩個不會報的 Service 類別;鄰居 kt-register-without-unregister 把被排除的 Application 放在好例檔 | 樣本慣例「壞例只放會報的寫法」;兩種情況逐例表 C227、C233 已守,樣本層不必重複 | 折:兩個 Service 類別移出壞例檔,好例檔原本就有 Service 的三種收集 |

編排者機械重現不到的:無(refuted none)。

## 修後

`-k kotlin_rulepack` 491 passed, 0 failed;計劃 lint 0 問題、spec-trace 2 條款全標。
