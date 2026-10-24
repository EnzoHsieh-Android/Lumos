severity: major

1. 只做穩定性、沒有 Macrobenchmark 的專案接不上
severity: major
blocking: 是,這會讓 spec 要服務的專案直接回 2,屬 major
引句:「專案沒有 `.lumos/macrobench.json` 也照判」
佐證 file: `scripts/lumos:39402-39405`
- `stability` 段放在 `.lumos/macrobench.json`。`_macrobench_config` 在沒有非空的 `results_dirs` 時回錯誤,`_macrobench_mode` 隨即印「擋下:」回 2。
- 沒有 `results_dirs` 的專案(例如沒有 Macrobenchmark 的專案)只要寫了 `stability.test_data` 或 `stability.strictmode`,就整個回 2。
- 沒有該檔的專案,`test_data` 與 `strictmode` 無處宣告,S7、S15 只能恆跳過。
- `_macrobench_mode` 目前在 `cfg is None` 時提早 return,spec 的 S14 靠改這裡就繞得過去。
- 但 spec 沒寫 `results_dirs` 要改成選填,也沒寫 `stability` 要拆到別的檔。S14 的測試涵蓋不到「有檔但沒有 results_dirs」。

2. 範例驅動指令會殺掉行程,暖機與量測兩次呼叫之間記憶體不累積
severity: major
blocking: 是,核心前提(同一行程、不殺行程)在範例指令下不成立
引句:「`adb shell am instrument -w -e class <測試類別>#<方法> -e cycles $CYCLES <測試套件>/androidx.test.runner.AndroidJUnitRunner`」
佐證 file: `r2-snapshot.md:62`
- Android 測試文件寫明,instrumentation 啟動時 target package 會被重啟。AOSP 另為此加了 `--no-restart` 旗標(來源 source.android.com 與 android.googlesource.com 的 commit)。
- 收集腳本先跑一次暖機呼叫、記下 pid,再跑一次量測呼叫。第二次 `am instrument` 若指向被測 App,行程會被重啟。
- 後果是第一份快照對應的行程已死,JVM 與原生記憶體歸零,`pid_changed` 恆為 true,`exits` 恆不過。
- 只有當測試 APK 的 targetPackage 是自己、而不是被測 App 時,才不會殺行程。
- spec 沒要求驅動指令加 `--no-restart`,也沒要求腳本檢查暖機後與量測前 pid 相同。
⚠ 我沒有在實機上驗過 UI Automator 在 targetPackage=自己時的行為。實驗室 spike 可能走的就是這條路。

3. 子案二「只要換驅動指令」站不住
severity: major
blocking: 是,spec 對子案二的承諾與 Maestro 實際行為不符,屬 major
引句:「子案二換成 `maestro test <flow>`」
佐證 file: `r2-snapshot.md:62`
- 輪數傳法不通:Maestro 的環境變數要用 `maestro test -e CYCLES=5 flow.yaml` 傳入。spec 的「收集腳本把輪數用環境變數 CYCLES 傳給它」只在 UI Automator 範例裡靠字串內插才成立。
- `repeat: times:` 能不能吃 `${CYCLES}` 沒有文件依據。文件只說 `times` 是整數,只有 `while` 示範了表達式。⚠ 我沒有實測。
- `launchApp` 預設 `stopApp: true`,會停掉執行中的 App 再重啟。flow 必須寫 `stopApp: false`,或完全不用 `launchApp`,否則同樣殺行程。
- 暖機與量測是兩次獨立的 `maestro test`。兩次之間 App 停在哪個畫面、flow 要從哪個畫面開始,spec 沒有約定。
- 所以子案二至少要改:flow 的寫法規範、`-e` 傳參、`stopApp:false`、起點畫面約定。
- 這與「收集與判定不動」的說法衝突。

4. 查詢範本的測試在 CI 跑不起來
severity: major
blocking: 是,S9、S10 的綁定測試做不出來,屬 major
引句:「應輸出一列,第一欄是字串 cycle,其後是匿名常駐記憶體加 swap 的最大值」
佐證 file: `scripts/templates/android-ui-attribution.sql:22`、`scripts/test_lumos.py:18006`
- 既有範本只用標準 SQLite 語法與四張表,測試靠 Python 內建的 sqlite3 跑同一支檔。
- 新範本用 trace_processor 的 stdlib 表,例如 `actual_frame_timeline_slice`、process counter 與 `heap_graph_*`。plain sqlite3 沒有這些表。
- `test_lumos.py` 只有一個假的 trace_processor,CI 上也沒有真的。S9、S10 要嘛需要 CI 裝 trace_processor 加追蹤檔 fixture,要嘛得改成 `[manual:]`。
- 統計化計劃的待辦 5 已把「CI 不能再用 sqlite3 跑範本測試」列為代價,這份 spec 卻直接預設可行。
- 另外,範本的 `__PROCESS__` 取代機制與「註解不以分號結尾」的既有坑(範本檔頭有寫),spec 都沒提到。

5. 收集腳本是 sh,卻要求每個呼叫都有逾時並解析 JSON
severity: minor
blocking: 否,有替代做法,屬 minor
引句:「每個 adb 與 trace_processor 呼叫都有逾時,中途失敗也刪暫存檔」
佐證 file: `scripts/templates/android-receipt-rerun.sh:1-14`
- 工具鏈作者在 macOS,系統沒有 `timeout` 指令。既有的重跑範本是 `sh` 外殼加 python3 heredoc。
- 腳本還要讀 `.lumos/macrobench.json`(JSON)、執行 `driver_cycles` 字串、解析 `exit-info`,純 sh 做不了。
- 建議明寫「sh 外殼加 python3」,逾時用 `subprocess.run(timeout=)`。

6. 檢查型條目沒有套用 NaN 與有限數守衛
severity: minor
blocking: 否,補一句條款即可,屬 minor
引句:「當結果檔某個來源的 status 不是 ok、或欄位缺、或值是 -1 時」
佐證 file: `scripts/lumos:39365-39372`、`docs/lumos-toolchain-knowledge/Projects/Macrobenchmark驗收門檻_計劃.md` 的 S10
- S11 只涵蓋 status、缺欄位與 -1。結果檔的 `bytes` 為 NaN 時,「大於門檻」恆假而判通過。
- 這正是 Macrobenchmark驗收門檻 S10 與 adapter 節點 PITFALL 記過的坑。
- 新增的 `check` 欄位(門檻上限、實例上限、阻塞上限)與結果檔數字都該走 `_macrobench_num`。spec 沒有這條條款。

7. 實例上限宣告在兩個地方
severity: minor
blocking: 否,補一句定義即可,屬 minor
引句:「門檻檔可以宣告 SDK 類別的實例上限,用第二份 Java 快照數」
佐證 file: `r2-snapshot.md:26`、`r2-snapshot.md:62`
- 類別清單同時出現在門檻檔的 `instances` 條目,以及設定的 `stability.declared_classes`。
- spec 沒說哪個是準,兩者不一致時怎麼辦也沒說。
- `scenario` 在門檻檔是「類別#方法」。穩定性結果檔只有單一 `scenario`,spec 沒說它對應什麼值。
- `--stability` 只收一個結果檔,多情境專案怎麼辦也沒說。
- `check` 條目是否遵守 `device_model`(驗收門檻 S3)沒寫。

8. 〈這次要改到的地方〉漏列統計化計劃
severity: minor
blocking: 否,只是漏列,屬 minor
引句:「抓退步用自己的基準那層移到 [[Projects/Android效能判定統計化_計劃]]」
佐證 file: `docs/lumos-toolchain-knowledge/Projects/Android效能判定統計化_計劃.md:38-44`
- 統計化計劃的五條待辦全是計時指標,沒有穩定性基準或記憶體單位容差那一條。
- spec 說「跟統計化計劃的第一條是同一件事」,但第一條是對計時用 Mann-Whitney 檢定。
- 〈這次要改到的地方〉也沒列要去補那一條。三個月後這個承諾會無人認領。

逐節判定(不影響的各附一句理由):
- 前言與詞彙、WHY 各條、七種檢查表、資料怎麼流:風險已列在上面第 1 到 7 項,其餘已讀,無 finding。
- 實務隱患、條款、回退:已讀,無 finding。
- 固定席 `Systems/macrobenchmark-adapter`:該節點沒有登記合約。把 `scripts/lumos` 與範本掛進 `about_code` 不會破壞宣稱的行為。「不接裝置」的負責範圍改寫已列在 spec 裡,順帶需要修改。
- `Macrobenchmark驗收門檻` S5、S10:門檻驗證只對沒寫 `check` 的條目套用,不破壞既有行為,但第 6 項的有限數守衛要補。
- `Android逐層診斷` S6、「L3 預設關閉」:spec 已明寫要標成被取代,不衝突。
- `_VENDORED_TREE_FILES`:新範本要登記並帶 SPDX 檔頭,S12 已涵蓋,不影響。收據重跑腳本只認第一欄當鍵,新查詢符合,不影響。

總結:最高嚴重度 major,blocking 共 4 條
