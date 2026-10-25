severity: major

**問 1 分層與依賴方向**
- 大致對齊,有一處偏離。新增的 `_macrobench_runs_count`、`_macrobench_cv`、`_macrobench_iterations` 都是放在 `_macrobench_read_one` 前面的私有函式(scripts/lumos diff 138–171)。呼叫方向跟鄰居一樣,由 `_macrobench_read_file` 往下呼叫(diff 195)。
- 比較用的 `mag_only` 判斷放在 `_macrobench_cmp_metrics` 裡(diff 224–233),不另開層,跟 `_macrobench_cmp_sampled` 的做法一致。
- 偏離處:鄰居靠 `_macrobench_read_one` 一次解析 metrics 與 sampled 並回傳 tuple。新增的 `_macrobench_iterations` 另外再走一遍同一份 `b["metrics"]` 與 `sampledMetrics`,自己做 ignore 過濾和 runs 驗證(見 A2)。
- `_macrobench_mode` 直接組 `low_iterations`,而鄰居都是呼叫 helper 填 `res`(見 A3)。

**問 2 命名與錯誤處理**
- 命名對齊:`_macrobench_*` 前綴、`MACROBENCH_MAG_ONLY_ITERS` 常數、中文 docstring,都跟 scripts/lumos:39369–39374 的 `MACROBENCH_*` 常數和既有函式一致。
- `res` 新增 `low_iterations` 鍵,沿用初始化時鍵固定的做法(`"stability_unjudged": None` 那一行,diff 306–307),`--json` 與文字輸出各印一次,對齊。
- `_macrobench_entry_ok` 用 `return False` 擋壞形狀(diff 255–260),跟既有的做法一致。
- 錯誤處理有分歧,但有意為之:`_macrobench_read_one` 遇到壞形狀丟 `ValueError`(scripts/lumos:39477–39495 一帶)。新的 `_macrobench_runs_count` 遇到壞 runs 回 `None` 並靜默略過。筆記裡已寫明這是刻意的保守設計,所以不單獨列為不對齊。
- 整數檢查的寫法跟鄰居不同(見 A1)。

**問 3 第二種做法**
- 有。整數(排除 bool)的檢查被改寫成內嵌的 `isinstance(..., int) and not isinstance(..., bool)`,出現兩處。repo 已經有 `_secev_int`(scripts/lumos:8559,`type(v) is int`,bool 不算)。`_macrobench_num` 的作法正是包裝 `_secev_num`(scripts/lumos:39387),新程式碼沒照這個模式走。
- 結果欄位組裝方式沒有第二種做法。先建立項目再補選填鍵,跟既有的 `v["source"] = src`(scripts/lumos:39585)同一模式。

## A1 整數檢查另寫一套,沒用既有的 `_secev_int`
severity: major
blocking: 是
引句:「isinstance(it, int) and not isinstance(it, bool)」
對照:新增處在 diff 224–225(`_macrobench_cmp_metrics`)與 diff 256(`_macrobench_entry_ok`),同一個判斷各寫一遍。既有的是 scripts/lumos:8559 `_secev_int`;`_macrobench_num` 包 `_secev_num` 的模式在 scripts/lumos:39387。

## A2 輪數與變異係數另走一遍解析,沒併進 `_macrobench_read_one`
severity: minor
blocking: 否
引句:「iters, cv = _macrobench_iterations(b, ignore)」
對照:diff 195(`_macrobench_read_file`)和 diff 156–171。鄰居 `_macrobench_read_one`(scripts/lumos:39477 起)是唯一解析 `metrics` 與 `sampledMetrics` 的地方,而且壞形狀丟 `ValueError`。新函式重寫了 ignore 過濾和 `isinstance(v, dict)` 檢查,壞值改回 `None`。結構上沒有跨層,但同一份輸入多了一套平行的走法。

## A3 `low_iterations` 在 `_macrobench_mode` 內嵌組裝
severity: minor
blocking: 否
引句:「res["low_iterations"] = [{"key": k, "iterations": v["iterations"]} for k, v in sorted(current.items())」
對照:diff 313–314。同一個 `_macrobench_mode` 裡的 `res` 欄位都由 helper 填:`_macrobench_stab_unjudged(res, ...)`(scripts/lumos:40199)、`_macrobench_compare`(scripts/lumos:40212)、`_macrobench_check_thresholds`。新增的這段是 mode 裡直接寫的推導式。

不對齊共 3 條,其中重大 1 條
