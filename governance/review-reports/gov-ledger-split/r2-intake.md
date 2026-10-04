# r2 收貨與重現

## 引句截斷(quote-check 未錨定 5 句)

正確性 #1 #4、邊界 #2 #5 等 5 句 quote-check 判未錨定,原因都是被審稿本身含「」、席位引句內再包「」被收貨截斷成不到 10 字(工具印 <10 字下限)。依規則這幾句引句不採信;所屬 finding 的內容由下表的機械重現或他席獨立一致支撐,照常處置。

## 編排者機械重現

| finding | 重現指令 | 結果 |
|---|---|---|
| 種類黑名單漏 skipped-flag(c1、k1、b2、i1) | `sed -n 42838,42846p scripts/lumos` | HIT:`kind = "skipped-env" if … else "skipped-flag"`,`_bound_tests_log(repo_root, kind, …)` |
| unfilterable 擋人但 hard 為假(c2、k1、b2) | `grep -n '_bound_tests_log(repo_root, "unfilterable"' scripts/lumos`;`sed -n 42460,42466p` | HIT:42945 寫 unfilterable;hard 只在 kind == red-blocked 為真 |
| 提醒模式 warned(b1) | `sed -n 27366p;35713p scripts/lumos` | HIT:nodehome-check、drift-check 在 warn 模式寫 warned |
| 舊 vault 沒有 docs/.gitignore(b3、i2、c 小) | `sed -n 20865,20881p scripts/lumos` | HIT:註解記 2026-06-26 起忽略檔寫在 vault 內,2026-08-21 改到 docs/ |
| 停止追蹤後別台機器 pull 刪檔(rb1、b5、k2) | git 行為:上游刪除追蹤、下游乾淨時 pull 會刪工作樹檔,下游有改動時 pull 中止 | 採信(回滾、邊界兩席各自在 /tmp 實測一致) |
| 使用紀錄帳只寫不讀(i 小、c 小) | `grep -n 'usage-log' scripts/lumos scripts/*.py` | HIT:只有 `_usage_log` 寫入點 |
| 淺層副本(c ⚠) | `git rev-parse --is-shallow-repository` | false;寫進〈天花板〉3 |
