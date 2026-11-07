# r1 收貨(2026-11-07,標準級:審查-sonnet + 架構對齊-sonnet)

兩席報告全數錨定(quote-check 全中),格式已正規化。全輪 4 條,全部 minor,無 major/blocker。

| id | 席 | 一句 | 去向 | 重現 |
|---|---|---|---|---|
| a1 | 審查 | 規則包節點 WHY 寫「逐列查完後是 0」,實際自檢印 2 列 | 折:改成剩 API-14、TEST-31 兩列待人裁 | HIT:`check.py --catalog-only` 印「還沒逐列查證 2 列:API-14、TEST-31」 |
| a2 | 審查 | 完整檢查路徑另印那一行沒測試;⑤ 只驗字樣不驗數字 | 折:加 ⑦(假 check 走完整路徑)、⑤ 改比對真型錄算出的數字 | HIT:刪完整路徑的 `_print_unverified()` → ⑦紅;數字加一 → ⑤紅 |
| b1 | 架構 | 新函式認「出處不全」四字,鄰居 catalog_problems 認「(出處不全)」 | 折:改認「(出處不全)」,加 ④b(名稱只提到四個字的列照算) | HIT:改回四字比對 → ④b紅 |
| b2 | 架構 | 新常數與函式放在 check() 後;正規式用 〔 跳脫而鄰居寫字面 | 位置折(搬到 main_rows 後);跳脫放行 | HIT:字面寫法時 pitfalls 列 RUF001 新告警把分級升到高 |

## 先查世界

- PRIOR-ART: b2 跳脫——查 ruff RUF001(ambiguous-unicode-character-string)規則說明 https://docs.astral.sh/ruff/rules/ambiguous-unicode-character-string/ :字串裡出現跟 ASCII 相像的字元就告警,設定 `lint.allowed-confusables` 可放行。本 repo 的告警閘只算「這次新增」的告警;鄰居 `_src_expand` 的字面〕是舊碼,不算新增。採用跳脫(行為相同、不新增告警);不採改 allowed-confusables(那是推送閘的共用設定,動它等於放寬所有檔,超出本批範圍)。
- PRIOR-ART: a2 測試完整路徑——沒有 ast-grep 時用替身取代外部依賴,只驗輸出段;做法同 Python 標準庫 unittest.mock 的 patch 概念(https://docs.python.org/3/library/unittest.mock.html),本 repo 零依賴,手動換屬性後 finally 還原。
- a1、b1 是文件與口徑一致性,不涉外部做法。

## 改壞驗證

④b、⑤、⑦ 三條各自改壞一次、各自翻紅,還原後 `-k kt_catalog` 37 通過。
