preflight-4: ran

# code-android-evidence r2 收貨

審材:r2-snapshot.patch(1372 行,1c6c0add..49283648,排除卷證與兩份帳本);修補差異 r2-repair-review.patch(583 行,3461928852b20eb0e216f9b15fa649c982444b48 → 1c3df999);來源 r2-repair-binding.json;案例 r2-behavior-cases.json。
兩席全新:單審-sonnet(3 條)、架構對齊-sonnet(2 條)。兩席都交回後才一起存檔與處理。
架構對齊席第一次交回時第 1 條寫 major 卻標 blocking:否,退回該席自己重判,改為 blocking:是(其餘一字未改);存的是重判後的版本。
單審席報告最後一行「max severity: major」被收貨端當成格式不對的嚴重度宣告,請該席只改那一行,存成 r2-單審-sonnet-格式更正.md 當載體(原檔保留,只差那一行)。
圖譜鏡頭:派工時會談專案算不出這個工作樹的範圍,兩席照備援只就 diff 碰到的節點判定。

## 逐條重現與去向

| id | 嚴重度 | 歸因 | 重現 | 結果 | 去向 |
|---|---|---|---|---|---|
| R1 | major | 修補回歸(r1 新增的測試護不住它自己新增的檢查) | 範本裡「標頭數與解析條數不同」那道改成 if False → `-k android_evidence_rerun` 4 passed 0 failed | HIT | 折:範本搬成 scripts/templates/android-receipt-rerun.sh 真實檔;測試每個案例只踩一道檢查(其他條件合格、查詢帶 expect),收據寫錯回 2、比對不符回 1 分開判,另加一個格式全對用假分析工具回 0 的案例;三道檢查各拿掉一道,各有一個案例紅 |
| R2 | major | 修補回歸(r1 的非有限數測試只造了啟動類) | `_macrobench_read_one` 滑動類與 `_macrobench_entry_ok` 滑動類改回 `_secev_num` → `-k macrobench` 158 passed 0 failed | HIT | 折:t_macrobench_rejects_nonfinite 補基準與結果檔的滑動類 P90 三種非有限數;同改壞重跑 6 條紅 |
| R3 | minor | 修補回歸(r1 新加的 `math.isfinite` 對超大整數丟 OverflowError) | 門檻 `max` 寫 1 後接 400 個 0 → rc1 加 traceback | HIT | 折:`_macrobench_num` 接住 OverflowError 回 False;同族的設定容差超大整數(原本也是 traceback)一起變成 rc2;測試補兩個案例 |
| RA1 | major | 修補回歸(r1 新增的測試從 reference.md 抽 ```sh 區塊來執行) | 讀 scripts/test_lumos.py 既有測試:圍欄抽取只做文字斷言、執行的都是 repo 裡的真檔案 | HIT | 折:範本改成 scripts/templates/ 底下的真檔(那個目錄本來就放範本、會整個複製進消費專案),reference.md 改成指示複製;測試直接跑那支檔;計劃 WHY 行跟著改寫 |
| RA2 | minor | 修補回歸(同 RA1 那支測試) | 讀 t_data_state_lens_doc_sync 等鄰居:讀 skills/ 的測試在消費端沒有 skills/ 時 raise _SrcOnly | HIT | 折:測試改讀 scripts/templates/(工具鏈與消費端都有),不再依賴 skills/ 存在 |

## 三問(席位回答的核對)

- 單審席已驗:門檻與設定容差的非有限數被擋、範本三案例回非 0、`-k macrobench` 158 綠;未驗:基準檔滑動類 NaN、來源雜湊競態、資安證據閘測試、SKILL 的裝置指令。本輪已補基準與結果檔滑動類案例;競態與裝置指令維持未驗(r2-behavior-cases.json 的 uncovered 欄)。

## 修補因果

regression_set:R1、R2、R3、RA1、RA2(五條都由 r1 的修補直接造成:R1、R2、RA1、RA2 是 r1 新增的測試本身的缺口,R3 是 r1 新加的有限數檢查引入的例外)。
