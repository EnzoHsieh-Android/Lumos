severity: clean

第 3 輪沒有新的不對齊。r2 的 major(用 `_SrcOnly` 表示缺外部工具)已改回 detekt 鄰居的寫法。r1、r2 報過的項目我沒有重報。

## 問 1:分層與依賴方向

對齊。
- 這輪的改動都在原函式內,沒開新入口,也沒跨層直呼:
  - `configs/ast-grep/kotlin-android/check.py` 仍是零依賴獨立檔,沒有 import `scripts/lumos`。
  - `scripts/test_lumos.py` 照舊用 `_ktpack()` 載入它。
- `.lumos/config.json` 的 `node_home.ignore` 從一條 `samples/*` 改成 `*.kt` 與 `*.kts` 兩條,還是同一個機制。
  - 判定在 `scripts/lumos:59776` 的 `_cochange_excluded`,用 `fnmatch`。
  - 呼叫端在 `scripts/lumos:44812`、`scripts/lumos:15596`,都是把 `ignore` 清單原樣傳進去,沒有另寫第二套 glob。
  - fnmatch 的 `*` 會跨斜線,所以 `samples/*.kt` 仍涵蓋樣本子目錄。

## 問 2:命名與錯誤處理

對齊。
- **缺工具的處理(r2 major 已修)。** `_ktpack_sg` 缺工具時回 `None`,不再丟 `_SrcOnly`。
  - 呼叫端 `t_kotlin_rulepack_samples` 與 `t_lint_new_astgrep_kotlin_two_files` 先跑靜態那半,再印「本機沒有 ast-grep,只跑了靜態那半;CI 裝了 0.51.1 會跑…」。
  - 這跟 detekt 鄰居一致:file: `scripts/test_lumos.py:37440` 印「本機沒有 detekt,只跑了靜態那半」。
  - file: `scripts/test_lumos.py:66224` 的 docstring 寫明「_SrcOnly 專指缺來源 repo 的產物,不拿來表示缺外部工具」,新碼的註解也引用了這句。
  - 這輪不會再多出 `SKIP` 計數,不碰 `EXPECTED_SKIP_MAX`(`scripts/test_lumos.py:126`)。
- **shell 引號。** 新增的 `_shlex.quote(sg)` 與 `_shlex.quote(str(pack))` 沿用測試檔內已有的寫法,例如 `scripts/test_lumos.py:27749` 與 `scripts/test_lumos.py:84435`。
- **逾時與 OSError 的處理。** `scan` 與 `loaded_count` 把 `TimeoutExpired` 和 `OSError` 分開處理,仍然回 `None`,上層報「跑不起來」。這跟 r2 確認過的方式相同。
- **訊息與命名。** 新增的測試用 `★改壞★` 前綴,常數與函式的命名與同檔其他項一致。

## 問 3:第二種做法

沒有。
- `_TIMED_OUT = [False]` 是 `check.py` 內部的逾時旗標,沒有第二套逾時機制。⚠ 專案其他地方沒有同形狀的先例,但它只在這支獨立檔內,不判不對齊。
- 這輪新增的 `review-fp-` 豁免條件(限定在語意覆核級規則)和 `info` 級目錄檢查,沿用 r2 已確認的 `_DIR_SEVERITY` 與 `REVIEW_FP_PREFIX` 管道,不是新做法。

不對齊共 0 條
