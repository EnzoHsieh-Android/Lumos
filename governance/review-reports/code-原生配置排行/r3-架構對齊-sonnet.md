severity: minor

我只讀了兩份 patch 和 repo 裡對照用的鄰居檔,沒有改任何檔。python-idioms skill 沒讀到,以下只比專案內鄰居。

## 問 1:分層與依賴方向(對齊)

- **收集腳本。** 新碼放在 `scripts/templates/android-stability-collect.sh` 內嵌的 Python 裡,跟既有的 `measure()`、`heap_counts()`、`cycle_numbers()` 同一層。它呼叫的都是既有零件:`tp_rows`(`android-stability-collect.sh:260`)、`start_record`(`:315`)、`stop_record`(`:345`)、`abort_record`(`:390`)、`src()`。
  - `fresh_launch` 是從 `measure()` 抽出來的,第一段和第二段共用同一支,沒有第二份實作。
  - 清理走原有路徑:`native_phase` 用 `abort_record`,`main` 的 `cleanup(state)` 讀同一個 `state["rec"]`(`:659`)。
- **lumos 端。** 只讀 `stability.json`、驗形狀、印出,不碰裝置。`_macrobench_stab_optional_err`(`scripts/lumos:39580` 附近)加驗 `native_retained` 清單,`_macrobench_stab_top_err` 加情境名交叉檢查,跟既有的設定驗證放在同處。
  - `_macrobench_without_results` 和 `_macrobench_mode` 兩條出口都呼叫 `_macrobench_native_print`,跟 `_macrobench_print_thresholds` 的呼叫位置成對。
- **e2e 範本。** 只多傳一個環境變數 `LUMOS_STABILITY_STEP_BUDGET_S`,值是 `f"{T_LONG:g}"`。它跟 `st.step` 預設的逾時 `timeout=T_LONG`(`android-e2e-run.sh:443`)是同一個變數,同一個來源。
- **跨層直呼:** 沒有。

## 問 2:命名與錯誤處理(大致對齊,一處不對齊,見 F1)

- **擋下。** 預檢和上限檢查都走 `die()`(`android-stability-collect.sh:40`),用「擋下:」開頭、回 2,檔頭的回傳碼說明也同步補了。`preflight` 的參數從 `native_on` 改成 `native`,不再蓋掉同名函式 `native_on()`。
- **失敗與不支援。** 都用 `src(value, why, status)` 回 status 與 reason。
- **逾時。** `native_query` 拿掉以「逾時」開頭的特判後,走和 `heap_counts`(`:269`)、`cycle_numbers`(`:287`)一樣的 `rc != 0` 加「trace_processor 算不了…」寫法,這次修補反而更對齊。
- **lumos 端。**
  - 常數 `MACROBENCH_NATIVE_SHOW` 沿用 `MACROBENCH_*` 命名。
  - 設定錯誤訊息用「要是…」句式,跟 `max_record_s`、`adb_serial` 那幾行同款。
  - 印出時過 `_events_clean`,跟 `scripts/lumos:40316-40326` 同款;設定訊息裡的情境名用 `_out_clean`,跟 `:40439` 同款。

## 問 3:第二種做法

- **解析 trace_processor 輸出:** 沒有第二套。三支查詢都走 `tp_rows` 的逗號切法。文字欄改用 hex 輸出是新做法,但解碼在 `native_sites` 內,切行仍是同一套。
- **清理裝置暫存:** 沒有第二套(見問 1)。
- **驗外來 JSON 數字:** 用既有的 `_secev_int`(`scripts/lumos:8578`)。
- **逾時與截止時間:** 這次修補之後收成單一來源。
  - `end` 在 `main` 只算一次;「跑不跑」的預估和驅動截止都用 `NATIVE_TAIL`,查詢截止用 `NATIVE_FINISH`。
  - 預估式 `2 * elapsed + NATIVE_TAIL > remaining` 和驅動截止 `end - NATIVE_TAIL` 用的是同一個常數,沒有兩處各算各的。
  - 只剩下面 F2 的常數來源問題。

## 發現

1. --json 路徑提早清外來字串,和鄰居不同
severity: minor
blocking: 否
引句:「    sites = [dict(x, **{k: _events_clean(x[k], 500) for k in ("func", "so", "caller")}) for x in sec["sites"][:200]] if sec["status"] == "ok" else []」
file: `scripts/lumos:40020`(`_macrobench_stab_src` 把 reason 原樣放進結果)、`scripts/lumos:40326`(只在印出時才 `_events_clean`)
鄰居的做法是資料層保持原文、印出時才消毒。這次在資料層就清一次,印出時 `_macrobench_native_print` 又清一次,同一份資料會被清兩次。結構沒壞、用的也是同一個函式,所以只算 minor。代價是之後有人想知道「結果檔原文」時,這一段和其他來源的規矩不同,要記得多一條例外。

2. 第二段的「收尾預估」寫死 120,沒有跟停錄、拉檔的既有上限連動
severity: minor
blocking: 否
引句:「+NATIVE_TAIL = 120   # 秒:第二段驅動跑完之後停錄、拉檔、查詢的預估;「跑不跑」的預估與驅動的截止時間都用它,兩邊不會互相矛盾」
file: `scripts/templates/android-stability-collect.sh:25`(T_SHORT)、`:28`(STOP_WAIT)、`:345-360`(`stop_record` 先等 STOP_WAIT 再 pull)
`stop_record` 的實際上限由 `STOP_WAIT`(預設 30)加 `adb pull` 的 `T_SHORT`(120)決定,而 `NATIVE_TAIL` 是獨立的 120,沒有用這兩個常數組出來。上一輪的 `NATIVE_MARGIN=180` 旁至少還寫了組成;這次連組成的說明也沒了。這等於在既有逾時常數旁多了一個手調的數字,有人改 `STOP_WAIT` 時預估不會跟著動。⚠ 這條是「常數來源不一致」,不是第二套算法,交編排者決定要不要升等。

不對齊共 2 條,其中 major 0 條
