# code-回頭條件消失式與生來成立 r1 收貨

審材:r1-snapshot.patch(f369e9c7..功能提交,不含卷證與帳本,1135 行)。分級 standard:正確性一席加架構對齊一席。共 10 條,major 2(C1、Z1)。正確性席引句全錨;架構對齊席 #2(Z2)引句跨了多行程式、diff 行首的 `+` 讓它錨不到——不改席位引句,編排者機械重現(見重現表),照採。本輪有 major,全部折、不放行。

## 依根因分組(全部折)

1. 反引號誤擋(C1,major):原本找行裡任何 `when-gone:`,說明文字提到它、後面有行內程式碼就誤報 → 只看 `[when-gone:` 或 `[retire:when-gone:` 開頭、找得到結尾 `]` 的真標記;撤除條件的值(不帶方括號)另一種寫法。
2. 讀原始位元組沒有事前上限(Z1 major、C3):git 模式整份讀進來才判太大 → 改走 `_nodehome_cat_blobs_capped`(先問大小);工作目錄模式每支檔看預算(Z2)。
3. 字串被截斷(C2):`x[1]y` 在第一個 `]` 截掉 → 字串含 `[` 報錯。
4. 介面與共用(Z3、Z4、Z5):反引號檢查為什麼不放值驗證寫進計劃(值已剝過反引號);「是不是資料夾」收成 `is_dir`、when-file 的提示共用;`_drift_cond_split` 的鍵參數改必填、所有呼叫端傳鍵。
5. 測試沒走到(C4):讀不出、超過上限、工作目錄模式補進 `t_drift_when_gone_review_r1`;when-file 指到資料夾的既有提示順手補測試。
6. 量測(C5):RETIRE-IF 與 REVISIT 改成用 `_probe_lines`、`_retire_lines` 數解析出的 gone 條件(含還在等的)。

## 重現表

| id | 怎麼查 | 結果 | 去向 |
|---|---|---|---|
| C1 | `_ns_revisit_violations("REVISIT:[when-file:src/a.py][by:2099-01-01] 寫法見 when-gone: 用 \`[when-gone:路徑]\` 那種","body",True)` 報條件寫錯 | HIT | 折(第 1 組) |
| C2 | `_slot_retire_err("when-gone:a.py::x[1")` 回 None | HIT | 折(第 3 組) |
| C3 | 同 Z1(席位 200 MB 實測) | HIT | 折(第 2 組) |
| C4 | 讀測試:讀不出、超過上限、disk 模式沒有斷言 | HIT | 折(第 5 組) |
| C5 | 讀 `cmd_drift_scan --json` 只輸出成立與判不了的 | HIT | 折(第 6 組) |
| Z1 | `t_drift_when_gone_review_r1` ③:3 MB 檔在 git 模式整份留在 `_raw`(改回原寫法翻紅) | HIT | 折(第 2 組) |
| Z2 | 引句錨不到;機械重現:讀 `_DriftProbeTree._read_raw` 的 disk 分支,迴圈內沒有 `_over()` | HIT | 折(第 2 組) |
| Z3 | 讀 `_probe_check_value` 拿到的是剝過反引號的值 | HIT | 折(第 4 組,寫進計劃) |
| Z4 | 讀 `_drift_probe_row_problems` 的 when-file 資料夾判斷 | HIT | 折(第 4 組) |
| Z5 | `grep -n '_drift_cond_split(v)'` 三處沒傳鍵 | HIT | 折(第 4 組) |
