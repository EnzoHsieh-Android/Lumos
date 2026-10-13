severity: minor

只有 1 條不對齊,方向是結構對、錯誤處理略少一種情況。

## 1. `bound_tests` 區塊型別錯時靜默用 1,跟既有的「設定型別錯就出聲」不一致
severity: minor
blocking: 否
引句:「if not isinstance(bt, dict) or "parallel" not in bt or bt["parallel"] is None:」
file: `scripts/lumos:5804`(`test` 欄位不是物件就印「⚠ config.json 的 test 欄位應為物件,忽略」);另一處同做法在 `scripts/lumos:43476`(`ci` 非物件就印「⚠ …非物件」)。
- 新函式 `_bound_tests_parallel` 的文件字串與計劃的「做法」一節都說「有寫但不合法時印一句提醒」。
- 但 `"bound_tests": 4` 或 `"bound_tests": "x"` 這類區塊本身不是物件的情形,會走到上面那行,直接 `return 1`,不出聲。
- 同檔既有寫法是區塊型別錯就印一句,例如 `test` 欄位和 `ci`。
- 修補差異(`/tmp/code-btpar-r2-repair.patch`)只補了 `parallel` 值不合法的警告,沒有補區塊型別。這是修補後仍留著的缺口,不是新引入的。
- 測試 `t_bound_tests_parallel_config_values` 也沒有涵蓋「區塊不是物件」。
- 這條不算 major,因為警告的措辭、`提醒:` 前綴和 stderr 管道都對齊既有寫法。

## 三問

**1. 分層與依賴方向:對齊。**
- 並行設定是在 `_run_bound_tests` 內讀的(`scripts/lumos:48149` 起)。
- 同一函式本來就讀 `LUMOS_TEST_TIMEOUT` 環境變數和 `load_platforms`,執行層自己決定執行策略,跟既有分工一致。
- 實際跑測試仍走既有的 `_kill_run`(`scripts/lumos:17175`),沒有跨層直呼。
- 記帳仍只經 `_bound_tests_log`(`scripts/lumos:47887`)。
- ⚠ `_run_bound_tests` 還被 `_spec_gate_judge_items`(`scripts/lumos:7661`)共用,所以規格閘也會跟著並行。計劃與 `bound-tests-gate.md` 只寫到合約測試閘,沒提規格閘。這是範圍描述的落差,不是做法分歧,所以不列為 finding。

**2. 命名與錯誤處理:大致對齊。**
- 警告用 `提醒:` 開頭、`file=sys.stderr`,跟 `scripts/lumos:5842` 和 `scripts/lumos:8224` 同。
- 設定讀不了時回預設值,跟 `_config_has_top_run_cmd`(`scripts/lumos:48258` 起)的 `except Exception` 寫法同。
- 修補把 `import json as _json` 改成用模組層的 `json`,更貼近該檔既有寫法。
- 記帳欄位 `secs_kind` 是 snake_case,跟 `calc_secs` 同風格。
- `_GOV_FIELD_TYPES`(`scripts/lumos:8623`)只登記讀帳 mapper 會用到的欄位。`calc_secs` 也沒登記,`secs_kind` 沒有 mapper 用到,所以不必登記。
- `_time.time()` 計時並 `round(...,1)`,跟同函式的 `_calc` 寫法同。
- 函式內 `from concurrent.futures import ...` 的區域匯入,跟該檔 `import os as _os` 的風格同。
- 唯一缺口就是上面的 finding 1。
- 另外警告會隨每次呼叫 `_run_bound_tests` 重印(規格閘會多次呼叫)。`load_platforms` 的「讀不了」警告(`scripts/lumos:5842`)也是每次呼叫都印,所以不列。

**3. 第二種做法(Grep 實查):沒有。**
- 我 grep 了整個 `scripts/lumos`:`ThreadPoolExecutor` 只出現在新程式(`scripts/lumos:48193`)。其他命中是審查題庫的字串(`scripts/lumos:26608`)。
- 專案原本沒有第二套 Python 內部並行機制,並行只在測試跑者的 `--shard` 做(`scripts/test_lumos.py:18891` 起),不是 lumos 內部。
- 所以這是「第一種」做法,不是「第二種」。
- ⚠ 這是 lumos 內第一次引入執行緒池,沒有既有先例可比。計劃的 `PRIOR-ART` 已說明借用外層多工作者的想法。
- 讀 `.lumos/config.json` 的方式:既有就有多份各自的載入函式(`_lint_load_config`、`_impact_load_config`、`_cochange_load_config` 等)。新增 `_bound_tests_parallel` 再多一份,跟 `_config_has_top_run_cmd` 同類,不算新做法。
- 測試:`_bt_parallel_fixture` 加上 `_load_lumos_inproc()`、`redirect_stderr`(`scripts/test_lumos.py:1260`)、結尾 `print("  ✓ t_…")`,跟既有 `t_bound_tests_*` 一致。S4 沿用 `_mk_bound_tests_repo`(`scripts/test_lumos.py:9274`)。

不對齊共 1 條,其中 major 0 條
