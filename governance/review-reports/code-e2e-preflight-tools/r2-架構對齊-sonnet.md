severity: minor

## A1 兩支範本的判斷式一致守衛,是「寫死字面再各查一次含不含」,不是檔內既有的「兩邊各抽出來、直接比相等」
severity: minor
blocking: 否

對照:
- ``file: `scripts/test_lumos.py:4006-4012` `` 的 post-commit 對 pre-commit 漂移守衛,做法是從兩個檔各抽出那一行,再比 `pre_case.strip() == post_case.strip()`。
- ``file: `scripts/test_lumos.py:12760-12780` `` 的 `t_code_exts_lists_agree`,做法是各檔解析成集合,再逐份比 `v == ref`。
- 新守衛是把判斷式字面寫死在測試裡(`cond`),再分別檢查兩支範本「含不含這串」。
- 這樣只釘住兩邊都含這串字面,沒有比兩邊抽出來的東西相不相等。
- 收集腳本實際寫的是 `bool((st.get("test_data") or {}).get("value"))` 的片段,範本 run.sh 寫的是 `((cfg.get("stability") or {}).get("test_data") or {}).get("value")` 的片段。測試截取的子句是兩者的共同尾巴。
- 守衛的結構還是「讀兩個檔」,所以不算第二種做法。
- 只是比既有守衛弱:共同尾巴以外的部分(例如前面的 `or {}` 層)漂了不會紅。
- 因此判 minor,不判 major。如果編排者認為「改成寫死字面」本身就是另起一種寫法,請自行升級,這點我不確定,標 ⚠。

引句:「    cond = '.get("test_data") or {}).get("value")'」

## A2 沒有其他不對齊
本節不單獨計條。下面各項我逐一對照過,與鄰居一致。
- 新環境變數名 `TP`、`JAVA_HEAP_DUMP` 與常數 `TP, JHD`,與收集腳本同名同寫法。
  - ``file: `scripts/templates/android-stability-collect.sh:20` ``
  - 收集腳本的宣告為 `ADB, TP, JHD = os.environ.get("ADB", "adb"), os.environ.get("TP", "trace_processor"), os.environ.get("JAVA_HEAP_DUMP", "java_heap_dump")`
- 缺工具的訊息句式是「找不到 X;用環境變數 Y= 指定」,與 ``file: `scripts/templates/android-stability-collect.sh:378` `` 的 `找不到 {tool};用環境變數 ADB=、TP= 指定` 一致。上一輪修補正是把句式對齊到這一種。
- 錯誤處理走本檔既有的 `die()`,回傳碼 2。
  - 對照 ``file: `scripts/templates/android-e2e-run.sh:48` `` 與同函式裡其他 `die` 呼叫,例如 `:157`。
- 測試側沿用 `_e2e_script_env`、`_e2e_script`、`check(...)` 與測試末尾的 `print("  ✓ ...")`。
  - `**proj` 只是把參數轉傳給既有的 `_e2e_proj`(``file: `scripts/test_lumos.py:18488` ``),沒有另起一套輔助。
  - 檔內 335 支測試都有這種尾端 print。

## 三問

1. **分層與依賴方向。**
   - 新碼放在 run.sh 的 `preflight()`(``file: `scripts/templates/android-e2e-run.sh:244-262` ``),與同函式裡既有的 ADB、MAESTRO 工具檢查同層、同風格。
   - 它只呼叫 `shutil.which` 與 `die`,沒有跨層直呼 lumos 內部。
   - 「兩支範本各寫一份」是檔頭註明的既有設計:各自是獨立的 `python3 -` 腳本,照抄進消費專案。
   - 結論:一致。

2. **命名與錯誤處理。** 見 A2,環境變數名、常數名、`die` 與訊息句式都與收集腳本一致,只有 A1 一條 minor。

3. **第二種做法。**
   - 兩處文字一致的守衛沿用「讀兩個檔再斷言」的做法,但比較方式較弱,見 A1。
   - 測試輔助(`_e2e_script_env`)只擴充參數,沒有新增一套。
   - 沒有發現全新的機制。
   - 圖譜筆記那一行 WHY 與 README 的改動屬文件,不涉及程式結構。

不對齊共 1 條,其中 major 0 條
