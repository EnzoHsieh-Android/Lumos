# r2 收貨紀錄(2026-10-14,3 席)

- 三份報告從逐字稿原樣存檔,`report-normalize --write` 只搬等級行;quote-check 全數錨定。
- 編號:正確性 正1–正7、邊界 邊1–邊5、架構對齊 架1–架6,共 18 條,全數折入,無放行、無重現不到。
- 修補因果:正1、邊1、架1(`:(literal)` 與全域旗標併用)、正2、邊2(重用函式的 splitlines)是 r1 折入的新做法帶出的;正3、正4、正5 是 r1 新寫的「雙認」與「分岔點」沒想到的路徑。

## 機械重現

| 編號 | 依據 | 判 |
|---|---|---|
| 正1 邊1 架1 | 三席各自在臨時 repo 實測 `git --literal-pathspecs diff … -- ':(literal)a.py'` 輸出空、rc0;只用其中一種都正常 | HIT |
| 正2 邊2 | 兩席實測同一行換頁符號之後內容不同,`_patch_file_changes` 回同一個雜湊;讀碼:`for ln in text.splitlines()` | HIT |
| 正4 | 讀 `_codeloop_default_base`:把本機 `refs/heads/main`、`master` 加進候選,註解寫明是刻意的 | HIT |
| 正3 | 讀計劃:`v2` 的雜湊輸入沒有任何綁檔案版本或時間的項目;紀錄合進主線後永遠在樹裡 | HIT |
