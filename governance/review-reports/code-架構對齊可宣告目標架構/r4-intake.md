# r4 intake(代碼審,人裁 extra-round 後的驗收輪)

## 材料
- 修補鏡頭:修前 9d6940ad → 修後 ccc92677(程式改動在 78f13a5b),r4-repair.patch 483 行必讀;r4-snapshot.patch 只當查詢參照。
- r3 修正關卡全部通過(r3-fixcheck.log);派席前重跑合約殺傷力配方 canary-audit 1ce7a8da1307:killed。人裁 extra-round 與跑滿回顧已記。

## 收貨
- 兩席:單reviewer-sonnet(4 條)、架構對齊-sonnet(5 條);正確性席報告清單式嚴重度用 report-normalize --write 純格式搬移;兩份 quote-check 對 r4-snapshot.patch 全數錨定。
- COR4-1、COR4-2 與 ARC4-1 同一族(把 git diff 文字切成行、認出檔名);兩席從不同位置各抓到一部分。

## 編排者重現(先寫紅測試,修前紅、修後綠;變異五處全部翻紅後還原並 cmp 確認)

| finding | 重現 | 修前(ccc92677) | 修後 |
|---|---|---|---|
| COR4-1 | t_pitfalls_diff_line_separator_cannot_hide_risk ③:單獨 CR 那行的 open( 漏掃(獨立提交,避免同提交其他檔的行被算到它頭上) | HIT 紅 | 綠 |
| COR4-2 | 同測試 ④:檔名含 tab、雙引號,git 檔頭包引號,整支從掃描消失 | HIT 紅 | 綠 |
| COR4-3 | t_arch_target_empty_tree_base_stays_quiet:空樹起點時沒宣告的專案多出 git 失敗警告、角色鏡頭多一行 | HIT 紅 | 綠 |
| COR4-4 | 同測試 ⑥:人讀輸出的風險位置行原樣印 U+2028 檔名 | HIT 紅 | 綠 |
| ARC4-1 | 同測試 ⑤:派工鏡頭 _lens_changed_lines 在 U+2028、CR 切斷 | HIT 紅 | 綠 |
| ARC4-2 | 讀碼:四處各寫「沒主線退回、附說明」,角色鏡頭用字串替換改說明 → 收成 _trusted_decl_ref,角色說明另立常數 | 讀碼 HIT | 已改 |
| ARC4-3 | 讀碼:merge-base 回 1 才算沒有共同祖先,與鄰居口徑不同 → docstring 寫明原因 | 讀碼 HIT | 已寫明 |
| ARC4-4 | 讀碼:docstring 補點名 _lens_push_base | 讀碼 HIT | 已改 |
| ARC4-5 | 讀碼:附加段沒內容時 JSON 沒走無損跳脫、讀最後一行用 splitlines → 有 JSON 物件就重新無損輸出、只照換行找最後一行;原輸出不是 JSON 物件時原樣交回(保留掛鉤認舊版的 rc2 加空輸出) | 讀碼 HIT | 已改 |

修 COR4-1 測試時發現:原本把 CR 檔與帶引號檔名放同一提交,帶引號檔頭認不出來,它們的 open( 被算到 cr.py 頭上,讓 CR 斷言假綠——已拆成獨立提交。測試檔裡三行原樣 U+2028(先前寫檔時被轉成真字元)改成跳脫寫法。

## 歸因(修補因果)
- 有證據的修復回歸:COR4-3(r3 修補把空樹起點的 merge-base 失敗歸成 git 失敗)、ARC4-2、ARC4-3、ARC4-4(都是 r3 修補新寫的)。
- 有證據的原有漏查:COR4-1、COR4-2(兩版結果相同)、COR4-4(兩版都原樣印)、ARC4-1(_lens_changed_lines 早就用 splitlines)、ARC4-5(附加段沒內容的分支自 r2 抽函式時就照原樣交回)。
- 未判定:無。

## 處置
9 條全數折入,無放行、無駁回。切行與檔頭改成兩支共用函式,推送前分級與派工鏡頭共用。
