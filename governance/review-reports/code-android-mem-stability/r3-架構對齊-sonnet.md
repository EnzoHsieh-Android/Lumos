severity: minor

本席只比對「一不一致」,不找 bug。判定依據是 `r3-snapshot-code.patch` 與工作樹 f0d41453 的對照檔。

## 問 1:分層與依賴方向

lumos 這側的分層對齊鄰居。數字、整數、日期、輸出清理都沿用既有共用函式,沒有跨層直呼或另寫一套。
- 數字驗證用 `_macrobench_num`,整數用 `_secev_int`,日期用 `DATE_RE` 加 `_rule_date`(`scripts/lumos:4296`、`8559`、`28099`、`39369`)。舊的 `datetime.date.fromisoformat` 自寫判法也被拿掉,改成同一支 `_macrobench_date_ok`。
- 文字輸出用 `_esc_clean`(`scripts/lumos:19331`)。
- 新的 check 判定掛在既有的 `_macrobench_threshold_item_err`、`_macrobench_check_thresholds`、`_macrobench_print_thresholds`、`_macrobench_mode` 底下,沒有繞過它們。

不一致的是收集腳本(sh 外殼包 python3)的依賴方向。鄰居 `android-receipt-rerun.sh` 只靠 manifest 與 TP,不回頭呼叫 lumos。新腳本做了兩件鄰居沒有的事:
- 用 `$here/../lumos` 呼叫 `lumos macrobench --check-config`。
- 自己再用 `json.load` 讀一次 `macrobench.json`。`macrobench-thresholds.json` 也由 `declared_classes()` 另讀一次,而且沒經過 lumos 的驗證函式。

兩份設定各有兩個讀取者,是結構上可再收斂的地方,但不構成跨層直呼。

severity: minor
blocking: 否
引句:「rc, out, err = run([sys.executable, lumos, "macrobench", "--repo", root, "--check-config"])」
佐證 file: `scripts/templates/android-stability-collect.sh:94`。另見 `scripts/templates/android-stability-collect.sh:98` 與 `:320` 的第二次讀檔,鄰居對照 `scripts/templates/android-receipt-rerun.sh` 沒有呼叫 lumos。

## 問 2:命名與錯誤處理

這些對齊,不列 finding:
- 回傳碼:收集腳本只用 0 和 2,沒有 1。鄰居的 1 是「比對不符」,收集腳本不比對,所以沒有對應。
- 擋下訊息:`die()` 一律印 `擋下:` 到 stderr 並回 2。`--check-config` 與 `_macrobench_mode` 同樣是 `擋下:` 加 rc 2。
- 環境變數:`ADB`、`TP`、`JAVA_HEAP_DUMP` 沿用鄰居的 `TP` 無前綴寫法。三個測試用旋鈕是 `LUMOS_STABILITY_SETTLE`、`LUMOS_STABILITY_STOP_TIMEOUT`、`LUMOS_STABILITY_LONG_TIMEOUT`,形式 `LUMOS_<領域>_<名>` 與既有 `LUMOS_PANEL_K2_CUTOFF`、`LUMOS_RANK_*` 一致(`scripts/lumos:18224`、`5149`)。
- 佔位:`__PROCESS__` 與鄰居一樣。`__DURATION_MS__` 是新增的第二個,但只在 pbtxt 裡用,寫法形式一致。
- SQL 註解:新增的兩支 SQL 註解都不以分號結尾,用標準 SQLite、第一欄當鍵、有 SPDX 檔頭,與 `android-ui-attribution.sql` 一致。
- 設定欄位:`decided_by`、`decided_at`、`_pct` 這類後綴沿用既有欄位;`max_record_s` 的 `_s` 後綴與 `tolerance_pct` 同一寫法。

有三處不一致:

1. 同一批新函式的前綴混用兩種縮寫。有 `_macrobench_stability_*`,也有 `_macrobench_stab_*`。既有 `_macrobench_*` 全用完整詞。

severity: minor
blocking: 否
引句:「def _macrobench_stability_load(path):」
佐證 file: `scripts/lumos:39819`(對照同批的 `_macrobench_stab_src` 在 `scripts/lumos:39833`、`_macrobench_stab_heap` 在 `:39862`)。

2. 常數放得比使用處晚。`MACROBENCH_MAX_CYCLES` 與 `MACROBENCH_VITALS_FG` 定義在 `_macrobench_check_item_err` 一帶,但 `_macrobench_stability_cfg_err` 更早就用到它們。既有常數(例如 `MACROBENCH_METRIC_STATS`)都定義在使用它的函式之前。

severity: minor
blocking: 否
引句:「MACROBENCH_MAX_CYCLES = 10000   # 暖機與量測輪數上限:驅動真的會跑這麼多輪,超過多半是寫錯」
佐證 file: `scripts/lumos:39774`(使用處 `scripts/lumos:39429` 起,對照 `scripts/lumos:39681`)。

3. 同一組欄位檢查寫了兩份。`decided_at` 與 `device_model` 的檢查,在 `_macrobench_check_item_err` 裡原樣再寫一份,沒有抽出共用。兩份訊息字串目前相同。

severity: minor
blocking: 否
引句:「return "decided_at 要是真的日期,寫成 YYYY-MM-DD"」
佐證 file: `scripts/lumos:39698`、`scripts/lumos:39798`。

## 問 3:第二種做法

lumos 側沒有引入第二種做法:整數、數字、日期與輸出清理都重用既有函式。

收集腳本這側有兩處,都是 sh 範本自成一個執行環境、不能 import lumos 造成的。我拿不準算不算 major,各標 ⚠ 交編排者。

1. 另一套版本檢查,下限不同。專案的 Python 下限是 `_PY_FLOOR = (3, 14)`,並有 `_py_floor_gate` 與統一的「需要 Python 3.14 以上」訊息。收集腳本自己寫了一段 `>= (3, 11)` 的判斷與另一句訊息。
- 該腳本隨後用 `sys.executable` 呼叫 lumos,而 lumos 會自己重跑到 3.14。
- 所以這段版本判斷的下限與專案下限不一致,理由只是「用了 `-P`」。

severity: minor
blocking: 否
⚠ 判不準:結構上是第二套版本檢查(依錨可算 major);但範本無法 import lumos,且 3.11 是 `-P` 旗標的需求,不是專案下限的替代。
引句:「python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null」
佐證 file: `scripts/lumos:72`(`_PY_FLOOR`)、`scripts/lumos:248`(`_py_floor_gate`)。

2. 另一套子程序收尾與訊號處理。收集腳本的 `kill_group` 是 `os.killpg(p.pid, SIGKILL)` 加 `except OSError`,與 `_kill_proc_group` 同功能。
- 兩者差在 `_kill_proc_group` 多一層 `AttributeError` 和 `proc.kill()` 的退路。
- `on_term` 把 SIGTERM 轉成例外,這在 lumos 內沒有先例;我 grep `scripts/lumos` 沒找到 `signal.signal`。這是新增能力,不是重做既有功能。

severity: minor
blocking: 否
⚠ 判不準:`kill_group` 與既有 `_kill_proc_group` 重複(依錨可算 major),但 sh 範本無法共用 lumos 的函式。
引句:「os.killpg(p.pid, signal.SIGKILL)」
佐證 file: `scripts/lumos:25519`(`_kill_proc_group`)、`scripts/templates/android-stability-collect.sh:44`。

不對齊共 6 條,其中 major 0 條。另有 2 個 ⚠(即第 4、5 條,版本檢查與 `kill_group`)已列在上面,請編排者裁是否升 major。
