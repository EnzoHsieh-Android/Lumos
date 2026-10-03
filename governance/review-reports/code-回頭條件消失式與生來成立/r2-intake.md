# code-回頭條件消失式與生來成立 r2 收貨

審材:r2-snapshot.patch(r1 修正那一段,390 行)。正確性一席、架構對齊一席,全新派、引句全錨。共 6 條,major 1(C1)。本輪有 major,全部折。

## 依根因分組(全部折)

1. 標記在第一個 `]` 截斷(C1,major):r1 只擋字串含 `[`,路徑含 `[`(Next.js 的 `app/[id]/page.tsx`)照樣被截成 `app/[id`、對還在的檔誤判;既有 when-file/symbol/test 同一個洞 → `_probe_bad_path` 一律擋方括號,四種帶路徑的鍵與撤除條件都報錯。兩邊圖譜目前沒有路徑含方括號的條件(grep 確認),上線不會把舊條件判成寫錯。
2. 反引號檢查(C2、Z1):行內程式碼裡提到 `[when-gone:` 也被當標記 → 前面反引號奇數個(在行內程式碼裡)跳過;撤除條件的值不再走同一支,改共用訊息 `_PROBE_GONE_BACKTICK_MSG`。
3. 讀不出的原因(Z2):git 模式「讀不出或超過 2 MB」混在一起 → 帶上限批次讀回 None 的只對那幾支再問一次大小,分開講。
4. 重複的查法(Z3):內容編號查找抽成 `_drift_specs`,`_drift_cat` 與 `_read_raw` 共用。
5. 測試沒咬到(C3):工作目錄模式每支檔看預算,補 `t_drift_when_gone_review_r2` ③(拿掉那兩行會紅)。

## 重現表

| id | 怎麼查 | 結果 | 去向 |
|---|---|---|---|
| C1 | `_slot_retire_err("when-gone:app/[id/page.tsx")` 回 None(席位實測);`_probe_check_value("file","app/[id")` 回 None | HIT | 折(第 1 組) |
| C2 | `_ns_revisit_violations("REVISIT:[when-file:src/a.py][by:2099-01-01] 寫法是 \`[when-gone:路徑\` 開頭,見 [[Projects/X]]","body",True)` 報條件寫錯 | HIT | 折(第 2 組) |
| C3 | 席位在副本刪掉那兩行、`-k when_gone_review` 仍全綠 | HIT | 折(第 5 組) |
| Z1 | 讀 `_probe_gone_backtick_err` 的 startswith 分流 | HIT | 折(第 2 組) |
| Z2 | `t_drift_when_gone_review_r2` ④ 改前兩種都印「讀不出或超過 2 MB」 | HIT | 折(第 3 組) |
| Z3 | 讀 `_read_raw` 內聯 `_drift_oids` 查找 | HIT | 折(第 4 組) |
