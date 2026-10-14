# r3 收貨紀錄(2026-10-14,2 席,上限輪)

- 兩份從逐字稿原樣存檔,`report-normalize --write` 只搬等級行;quote-check 全數錨定。
- 編號:正確性 正1–正6、邊界 邊1–邊6,共 12 條,全數折入,無放行、無重現不到。
- 修補因果:正1 正2 正3 邊2 邊3(推送前規格閘那一步的輸入、提前返回、主線版、改名)是 r2 把升高風險改放規格閘帶出的;正4(不准重問沒痕跡)、邊1(checker 放不進多行)是 r2 新寫的留痕要求沒想到的路徑。

## 機械重現

| 編號 | 依據 | 判 |
|---|---|---|
| 邊2 正1 | 讀 `scripts/hooks/pre-push`:`spec-gate --push-check` 只帶範圍與 `--repo` | HIT |
| 邊3 | 讀 `_spec_gate_push_check`:`if not plans: return 0` 在前;`.github/workflows/ci.yml` 不跑 push-check | HIT |
| 正3 | 讀 push-check 的 `git diff --name-only` 沒有 `--no-renames` | HIT |
| 邊1 | 讀 `_fmt_decision_value`:決策欄位遇換行丟例外 | HIT |
