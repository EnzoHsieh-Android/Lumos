# r3 收貨紀錄(code-android資安靜態檢查補齊第三批)

## 修補鏡頭準備(§3.1)

- 兩端:修前 b3561e61aecffb923faa3b3716a778bb7c0c922b(r2 派工單 base_commit;重產 r2 材料指紋一致)→ 修後 7ca3c134057f969bbd9b499b5c6d15b2d0bca457;祖先關係 rc0。差異 `r3-repair.patch`,審查用 `r3-repair-review.patch`(測試與計劃兩支),來源 `r3-repair-binding.json`,fix-check 結果 `r2-fix-check.txt`(通過)。新完整快照 `r3-snapshot.patch`。

### 先列出處清單(r2 各組)

- t1 錨點:呼叫名的兩個 ^(C121 自訂元件名、C122 完整套件名);`^visualTransformation`、`^keyboardOptions` 兩處講不出失敗場景,不補例。
- t2 天花板:計劃〈天花板〉一處,預期值表 C123 一列。

### 修補驗證(修前紅、修後綠)

- t1:修後拿掉呼叫名 ^ 錨點 → C121、C122 紅(192 passed 2 failed),還原 194 passed。
- t2:C123(`KeyboardOptions(…, imeAction = if (x) … else …)`)現行規則不報,釘住天花板。
- 保留行為:C95~C120 與 S4 在修後全綠。

## 收貨

- 兩席(審查三、架構對齊三)全部交回後一次從逐字稿存檔;兩份已是正規化格式,架構對齊三引句全數錨定,審查三 0 條。收貨時 git status 沒有 repo 改動,臨時目錄 /tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/ 收貨後刪。
- 審查三獨立重驗:拿掉呼叫名 ^ 錨點 C121、C122 會報(變異翻紅),C123 現行 0 筆;30 個表外寫法都跟預期值表與〈天花板〉一致。修前紅它沒重跑,標未判定。

## 編號與處置

編號:架構對齊三 u1。

| id | 一句 | 重現 | 處置 |
|---|---|---|---|
| u1 | 第三批型錄測試少了第二批的「逐列查證 0 列」那道檢查 | HIT:t_kt_catalog_security_lint_batch3 只有 ①、②;全域 t_kt_catalog_unverified_rows 對整份真型錄已驗同一件事 | 放行:實際沒有漏守(全域測試涵蓋三列),S4 條款也沒承諾這項;這是 standard 第 3 輪(上限),折入要再開一輪全新席,代價大於價值 |

--refuted-set none。--regression-set none:u1 歸因原有漏查(初版就是這個形狀,r2 修補沒碰這段)。
