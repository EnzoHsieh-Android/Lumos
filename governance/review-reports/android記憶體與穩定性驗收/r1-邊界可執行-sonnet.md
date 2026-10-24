severity: major

我讀完整份 spec,並對照 `scripts/lumos` 的門檻檢查、實驗室追蹤檔和 SM-X710(Android 16、API 36)。已修過的四項沒重報。

**此功能碰到的風險類**
- 極端輸入:輪數、null、超大追蹤檔。
- 平台版本:Android 16 與 17。
- 時間與時區。
- 量不到與沒有的區別。
- 單位。
- 守衛面:只提醒、回 0。
- 個資:快照。

**逐節結論**
- 一份驗收看什麼(六種檢查):見 finding 5、7。
- 資料怎麼流:見 finding 3、4、5、8、9、10。
- 實務隱患:已讀,補充已併入 5 與 3。
- 回退:已讀,無 finding。
- 這次要改到的地方:已讀,無 finding。
- 條款 S12、S14–S16:已讀,無 finding。
- S1–S11、S13:見各 finding。

**固定席(macrobenchmark-adapter)判定**
- 不影響:「只提醒、有退步也回 0」、「不接裝置、不從量測產生門檻」、「門檻檔壞了回 2」都維持。
  - 裝置只在範本腳本碰。
  - 峰值基準若新寫一份,要小心碰「不從量測產生門檻」(見 7)。
- 會影響:節點的容差規則「取基準絕對值×容差百分比與 `abs_tolerance` 兩者較大的」,預設 `abs_tolerance` 是 1(毫秒類指標用),見 2。
- 會影響:門檻驗證「每條必有 metric、stat 與 max 或 min 其一」,見 7。
  - 未寫 `kind` 的舊條目不變,但新 `kind` 條目要走另一套驗證。

1. 趨勢規則在真實抖動下抓不到洩漏
severity: major
blocking: 是(洩漏檢查會對有洩漏的 App 判通過,功能目的落空)
- spec 段落:WHY 洩漏用趨勢判,S1–S3。
- 輸入:實驗室正常版 `scrollCompose` 五輪追蹤檔,各取最後一個 `Heap size (KB)` 樣本。
- 走到:五輪結束值是 15584、13084、28292、21400、12368 KB(同一個沒洩漏的情境,忽高忽低兩倍以上)。
- 壞在:「每一輪都不低於前一輪」在這種鋸齒下幾乎不成立。
  - 真的每輪漏 1 MB,只要有一輪因回收時間點多掉 1 KB,第一個條件就不成立,判通過。
  - 這是漏判(假陰性),不是誤報。
  - REVISIT 只說「校準數字」,沒有改規則形狀。
- 佐證:`/Users/enzo/orca/workspaces/macrobench-lab/.lumos/artifacts/android/ui-c1-unstable-ft-v3/ComposeScrollBenchmark_scrollCompose_iter000_2026-10-23-13-52-52.perfetto-trace` 到 iter004。
  - 該追蹤檔裡 `Heap size (KB)` 是 atrace_counter,單輪就有 22547 個樣本。
- 引句:「N 輪結束時的值一路往上(每一輪都不低於前一輪),而且最後一輪比第一輪多出超過容差」

2. 容差「照既有規則」會把毫秒單位的絕對容差套到 KB,基準參照也換了
severity: major
blocking: 是(S3 的「第一輪值接近 0」情境在預設設定下做不出來)
- 輸入:未設 `abs_tolerance` 的專案(預設 1),Java 堆積以 KB 為單位。
- 走到:既有 `abs_tolerance` 是單一全域設定,預設 1,為毫秒類指標設計。
  - 套到 KB 上絕對下限只有 1 KB,「取較大者」等於只剩百分比。
  - 百分比的基準,既有規則是「基準值」,spec 改成「第一輪值」,而第一輪含類別載入與暖機。
- 壞在:spec 沒說記憶體類是否有獨立的容差欄位與單位。
  - 實作者照字面沿用,S3 第三種輸入(只超過百分比沒超過絕對值)在預設設定下不會出現。
  - 第一輪暖機成長通常大於 10%,會誤報。
- 佐證:`scripts/lumos:39358`(`MACROBENCH_DEFAULTS`)、`scripts/lumos:39488`(`tol = max(abs(base) * cfg["tolerance_pct"] / 100.0, cfg["abs_tolerance"])`)。
- 引句:「容差照 [[Systems/macrobenchmark-adapter]] 既有的規則取」

3. 輪數太少、缺輪或某輪 null 沒有規則
severity: major
blocking: 是(實作者得自己決定,結果會因人而異)
- spec 段落:`rounds`、S1–S3、S11、「App 中途被殺掉」。
- 輸入一:N=1。第一輪等於最後一輪,「多出超過容差」恆假,判通過,應該是沒判。
- 輸入二:N=2。只要第二輪比第一輪多出容差就判「一路往上」不過,這等於比對暖機漲幅。
- 輸入三:App 在第 3 輪被殺掉,只有 2 份追蹤檔。spec 沒說這時 `rounds` 少於 N 要怎麼判,也沒說收集腳本是否還會跑(測試失敗時)。
- 輸入四:5 輪中第 3 輪 `java_heap_end_kb` 是 null。S11 是「欄位值是 null 就跳過」,但整條線跳過,還是丟掉那一輪、用剩下四輪判,沒定義。
  - 後者會把「一路往上」的相鄰關係接錯。
- 壞在:沒有「最少幾輪才判、少於時列成跳過」的條款,也沒有預設輪數寫進條款(輪數 5 只出現在 REVISIT)。
- 引句:「量不到的欄位寫 null,不寫 0」

4. 結束紀錄的時間窗:時區與時鐘來源沒定,也沒限定被測 App
severity: major
blocking: 是(時間窗錯一個時區,舊紀錄會混進來或新紀錄全被丟掉)
- 輸入:SM-X710,裝置時區 Asia/Taipei。
- 走到:`dumpsys activity exit-info` 的 `timestamp=2026-10-23 19:09:23.945` 是裝置本地時間、不帶時區,也不是 epoch。
  - spec 的 `started_utc` 是 UTC;沒說 `started_utc` 取自主機時鐘還是裝置時鐘。
- 壞在:收集腳本用 UTC 去比本地時間字串,台灣時區差 8 小時。
  - 開始時間前 8 小時內的舊崩潰全算進來,害這次不過(spec 想避免的情況)。
  - 或者反過來:若實作者誤把本地時間當 UTC,真崩潰被判成舊紀錄、漏判。
  - 主機和裝置時鐘本身也可能差好幾秒。
- 另一個漏洞:spec 沒說只看被測 App 的套件。
  - 全機 `dumpsys activity exit-info` 有 351 個套件,任何其他 App 在測試期間崩潰,都會讓這個專案的驗收不過。
- 佐證:`adb shell dumpsys activity exit-info`(上述輸出)。
- 引句:「用測試開始的時間點過濾系統結束紀錄」

5. 「空」被當成「沒事」:exits、strictmode、instances 量不到時分不出來
severity: major
blocking: 是(守衛在失效時仍顯示通過)
- spec 段落:`exits`、`strictmode`、S4、S7、S8、S11。
- 輸入一:`dumpsys` 或 `logcat` 執行失敗或被截斷,收集腳本寫出空陣列。
  - 只有 `rounds` 的欄位有「量不到寫 null」的規則,`exits` 與 `strictmode` 沒有。
  - 空陣列就判通過;S11 只管 null,管不到空陣列。
- 輸入二:消費專案的 StrictMode 只在 debug 建置開(Macrobenchmark 跑的是非 debuggable 建置),違規數恆為零,判通過。
  - spec 沒要求確認 StrictMode 真的有開。
  - logcat 預設緩衝區有限,長測試會把早期違規擠掉。
  - `LeakedClosableViolation` 要等物件被回收才印,測試結束前沒回收就不會有紀錄。
- 輸入三:Android 16 以下的裝置(實驗室的 SM-X710 就是 API 36)沒有 MemoryLimiter。
  - 這一項在這些裝置上永遠是零筆、判通過,但從沒有被量過。
  - Android 17 的描述字串含 `MemoryLimiter:AnonSwap` 已用官方資料確認(substring 比對,見網址)。
- 壞在:S14 要求「六種檢查應全過」,實驗室現有裝置會把三種不可能觸發的檢查也算成過。
- 佐證:https://developer.android.com/about/versions/17/behavior-changes-all
- 引句:「`strictmode`:每筆 `kind`」

6. 宣告類別的實例數:缺席算 0 還是算沒量到,以及混淆後的類別名
severity: major
blocking: 是(實例數這一項在乾淨 App 上必然判跳過,或在混淆建置上必然判通過)
- spec 段落:`instances`、S4、S11。
- 輸入一:類別在關畫面後已被正常釋放。
  - 查詢「類別名對實例數」自然只列出至少有 1 個實例的類別,0 個的類別不出現。
  - 門檻檔宣告了該類別時,S11 規定「缺了欄位要跳過、不得通過」。
  - 結果是健康的 App 永遠是「跳過」,沒有任何情況會是「通過」。
  - 收集腳本不讀門檻檔,spec 也沒讓它補 0。
- 輸入二:Macrobenchmark 的建置是 R8 縮減過的,第三方 SDK 類別名常被混淆。
  - 門檻檔寫原類別名,快照裡是 `a.b.c`,實例數恆為不存在,若改成補 0 則判通過。
  - spec 沒要求用 mapping 檔還原或要求 keep 規則。
- 引句:「`instances`:類別名對實例數(沒錄快照時整欄不出現)」

7. 六種 `kind` 的必填欄位、主執行緒阻塞、峰值基準都沒定義,實作者做不出來
severity: major
blocking: 是(S13 要測「缺了那種的必填欄位時擋下」,但 spec 沒列出是哪些欄位)
- 輸入:實作者要寫 `leak`、`instances`、`peak`、`exits`、`strictmode`、`frozen` 的驗證函式。
- 走到:
  - 必填欄位只有「每種有自己的必填欄位」一句,沒有任何一種的欄位清單。
  - 既有 `_macrobench_threshold_item_err` 要求每條有 `metric`、`stat`,且 `max` 與 `min` 恰好一個。
    - `exits`、`strictmode` 沒有這些概念,新驗證要不要放寬沒說。
  - 「單次阻塞的門檻由人在門檻檔自訂」,但六個 `kind` 裡沒有 `block`。
    - 要塞進 `frozen` 還是要加第七個 `kind` 沒說。
    - 「主執行緒阻塞」也沒有定義:最長的最上層區段?執行緒狀態睡眠?
    - 取最長區段會把整個 `activityStart` 當成阻塞。
  - 「峰值」兩層:
    - 「基準加容差」的基準存在哪、第一次沒有基準時怎麼辦、怎麼更新,spec 都沒寫。
    - 既有基準檔只存 Macrobenchmark 的指標,沒有 `--stability` 的基準。
    - 另開一份基準又碰節點的「不從量測產生門檻」。
  - 峰值判定吃的是每輪一個 `rss_anon_swap_peak_kb`,要取各輪最大值、平均還是每輪都要過,S6 沒說。
  - `--stability` 與既有流程的關係:專案沒有 `.lumos/macrobench.json` 時,現行 `_macrobench_mode` 在 `cfg is None` 就提早回 0,`--stability` 會被一起略過。
  - 不帶 `--stability` 時,有 `kind` 的條目是跳過還是被舊驗證擋下,也沒說。
  - `--stability` 指定的結果檔壞掉或讀不了,spec 只講「回 0」,沒講回 2。
- 佐證:`scripts/lumos:39632`(`_macrobench_threshold_item_err`)、`scripts/lumos:39724`(`_macrobench_mode`)。
- 引句:「每種有自己的必填欄位,`scenario`、`contract`、`decided_by`、`decided_at` 照舊必填」

8. 官方記憶體分級表:WHY 與 S5 互相矛盾,也沒給 MB 區間
severity: major
blocking: 是(裝置落在哪一級由實作者猜,同一台裝置可能被判成不同級)
- spec 段落:WHY 記憶體峰值分兩層、S5、`total_mem_mb`。
- 輸入:SM-X710,`MemTotal` 為 7386728 kB(約 7213 MB,行銷規格 8 GB)。
- 走到:官方表依「可用記憶體」分級,4 GB 級是 3200–4800 MB,6 GB 級是 4800–6800 MB,8 GB 級是 6800–9216 MB。
  - 0–3200 MB 與 18432 MB 以上沒有數字。
  - spec 沒寫這些區間。
- 壞在:
  - 實作者最容易拿行銷數字當切點,例如 `< 8192` 當 6 GB。
    - 這台 8 GB 裝置會被判成 6 GB 級,上限變 2.25 而不是 2.25(巧合相同);4 GB 裝置(約 3.6 GB 可用)會落到「4 GB 以下」被跳過。
    - 12 GB 裝置(約 11 GB 可用)也會落錯。
  - WHY 把 4 GB 與 16 GB 兩級列了數字,S5 卻說「4 GB 以下或 16 GB 以上沒有官方數字」。
    - 「以下」「以上」是否含 4 GB 本身、16 GB 本身無法判斷。
    - 前掃修的是門檻格式,這個矛盾在修完後留下來。
  - 官方表另有遊戲欄,spec 只用 App 欄,沒說明遊戲類專案要不要換。
- 佐證:https://developer.android.com/google/play/vitals(2026-10-24 讀到的表與分級定義)。
- 引句:「4 GB 以下或 16 GB 以上沒有官方數字時列成跳過並說原因」

9. 單位、峰值取樣與 S10 輸出沒定義(查詢範本一做就會錯)
severity: minor
blocking: 否(寫測試時才會發現,不會讓判定悄悄做錯)
- 輸入:實驗室追蹤檔。
- 走到:
  - `mem.rss.anon` 的單位是位元組,`Heap size (KB)` 的單位是 KB。
    - spec 的「原生記憶體 = 匿名常駐扣掉 Java 堆積」沒寫換算。
    - 實作者直接相減會得到負值或錯 1024 倍。
  - `mem.swap` 在同一追蹤檔只有 19~23 個樣本,而 `mem.rss.anon` 有 33340 個。
    - 「匿名加 swap 的最大值」若用同一時間戳 JOIN,幾乎沒有列。
    - 取兩個最大值相加則高估。
    - 正確做法是兩條時間序列對齊(取最近前一個 swap 值),spec 沒說。
  - 行程重啟或死亡時 `mem.rss.anon` 會有 0 值(此追蹤檔該欄最小值 0)。
    - 「結束值」若取最後一個樣本,可能取到 0,而且 S10 又規定計數空的欄位輸出空值,0 與空值怎麼分沒說。
- 佐證:追蹤檔 iter003 的 `counter` 與 `process_counter_track` 查詢結果(`mem.rss.anon` 單位位元組、`Heap size (KB)` 為 atrace_counter)。
- 引句:「計數是空的欄位輸出空值而不是 0」

10. 輪次字串的來源與排序
severity: minor
blocking: 否(影響限於輪次 10 以上或查詢範本寫法,不改判定結果)
- 走到:S10 要求輸出第一欄是輪次字串。追蹤檔內沒有輪次資訊,查詢範本必須有 `__ROUND__` 這類佔位符。
  - 現行 `android-ui-attribution.sql` 的作法是 `__PROCESS__` 佔位符,spec 沒有提到。
  - 輪數超過 9 時,若有人按 `round` 字串排序,`r10` 排在 `r2` 前面,趨勢順序就錯了。
  - spec 只說 `rounds` 是陣列,但沒說判定以陣列順序為準。
- 佐證:`scripts/templates/android-ui-attribution.sql:1-20`。
- 引句:「`round`(字串,例 r1)」

11. ⚠ Macrobenchmark 的啟動模式沒限定,冷啟動會讓洩漏趨勢無意義
severity: minor
blocking: 否(要看消費專案怎麼寫測試,判不準所以標 ⚠)
- 走到:`measureRepeated` 若用 `StartupMode.COLD`,每輪都會殺掉行程重來,N 輪的記憶體都是同一個冷啟動後的值,趨勢永遠是平的,洩漏看不到。
  - 應該要求 `startupMode = null`(或 WARM / HOT),同一個行程跑完 N 輪。
- spec 段落:資料怎麼流第 1 步沒提這個前提;S14 的實驗室情境也沒寫。
- 引句:「Macrobenchmark 的洩漏情境掛 MemoryUsageMetric,讓每輪追蹤檔都錄到記憶體計數」

總結:最高嚴重度 major,blocking 共 8 條
