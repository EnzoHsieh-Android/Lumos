severity: major

審查範圍與方法:逐節讀完 r4-snapshot.md,對照 `scripts/templates/android-stability-collect.sh`、`scripts/lumos`、Perfetto v57.2 原始碼、AOSP libunwindstack 和實驗室分支。我沒讀 r1 到 r3 的席報告。

白話:這份排行像「按停錄那一刻的帳,把每筆還沒還的記憶體記到最近一個非配置器的函式」。我查到的問題集中在三處。一是現代 App 預設把 .so 直接放在 APK 裡,檔名比對會失效。二是 lumos 沒有欄位能分辨「沒打開」和「打開了但失敗」。三是函式名在 Perfetto 資料裡其實是 mangle 名。

## 各節

- 前置欄位、決策 d1 到 d5:有 1 條 minor(F11)。其餘已讀,無 finding。
- 白話、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding。我核對過 `heapprofd_config.proto` 的欄位、`heap_profile_allocation` 的 delta 寫法(`profile_packet_sequence_state.cc`),以及官方 `summary_tree.sql` 用 `sum(size)`,三項都成立。
- 實驗室實測:有 F6、F8。
- 〈排行怎麼算〉第 1 到 3 條:有 F1、F3、F4、F5、F7、F10。
- 〈打算怎麼做〉第 1 到 7 步:有 F2、F9。第 1 步 `_macrobench_stab_top_err(raw)` 拿得到 `stability_scenarios`,情境名 regex 與 `_e2e_scenarios_err` 一致,`@` 不會跟情境名撞。`_secev_int`、`_events_clean(text, limit)`、`_macrobench_stab_src`、`_VENDORED_TREE_FILES` 都存在,簽名也對得上。
- 跟舊否決的差別:已讀,無 finding。
- 實務隱患:見後面逐類答覆。
- 條款 S1 到 S22:已逐條對照〈排行怎麼算〉與〈打算怎麼做〉。S1、S2、S3、S11、S12、S21、S6、S7、S13、S14、S17 的字面一致,S15 與第 6 步的衝突見 F2。
- 回退、審計修正紀錄:已讀,無 finding。

### F1 .so 檔名比對在「.so 直接從 APK 載入」時整個失效
severity: major
blocking: 是
引句:「所在 .so 檔名是 libc.so、libc++.so、libc++_shared.so、libstdc++.so」

1. 〈排行怎麼算〉第 1 條用 mapping 名的最後一段比對檔名,並說「這幾支裡的全部框架都跳過」。
2. heapprofd 的 mapping 名來自 `map_info->GetFullName()` 再按 `/` 切開(`src/profiling/common/callstack_trie.cc` 的 `InternCodeLocation`)。
3. libunwindstack 的 `GetFullName`(`MapInfo.cpp`)在 `elf_start_offset() != 0` 時回傳 `name() + '!' + soname`,也就是 .so 被未壓縮直接放在 APK 裡載入的情況。AGP 在 minSdk 23 以上預設 `extractNativeLibs=false`,所以這是現代 App 的常態。
4. 具體例:SDK 的 `libfakesdk.so` 和 `libc++_shared.so` 都放在 APK 裡。mapping 最後一段會是 `base.apk!libc++_shared.so`,與名單的 `libc++_shared.so` 不相等。
   - 照字面實作,`std::__ndk1::basic_string::__grow_by` 這類落在 libc++_shared 的框架不會被跳過,會當成呼叫位置。
   - 排行會列 `__grow_by @ base.apk!libc++_shared.so`,而不是歸給 SDK。
   - 顯示的 `.so` 也全是 `base.apk!…`。
5. 名單只有 libc.so 與 libc++.so 在系統路徑,不受影響。
6. 實驗室的假 SDK 只在 C 裡直接呼叫 malloc(`fakesdk.c`),從沒走過這條規則,測不出來。
7. 修法方向:比對前先去掉 `…!` 前綴,或比對 `!` 後面的 soname,並補一條 APK 內嵌 .so 的測試。

### F2 lumos 無法分辨「沒打開」與「打開了但失敗」,第 6 步和 S6/S15 互相卡住
severity: major
blocking: 是
引句:「打開了但 status 不是 ok → 印一行「原生配置排行沒跑成:<原因>」」

1. S6 與第 2 步規定:沒打開、沒宣告測試資料、Android 版本不夠,收集腳本都要寫 `unsupported` 並附原因。第 2 步第一種原因就是「設定沒替這個情境打開 native_retained」。
2. 第 6 步只說「結果檔沒有這段 → unsupported、不印;打開了但 status 不是 ok → 印一行」。但 lumos 只讀結果檔,結果檔裡沒有「這個情境有沒有打開」的欄位。
3. 具體例:一個沒打開 `native_retained` 的專案,新收集腳本寫出 `{status: unsupported, reason: "設定沒替這個情境打開 native_retained"}`。
   - 照字面讀,「段存在且不是 ok」就印一行,預設關閉的專案每次都被唸。
   - 若實作者改成「unsupported 一律不印」,又會吃掉「沒宣告測試資料」「Android 版本不支援」這兩種打開了卻跑不了的情況,S15 沒了意義。
4. 兩種讀法都是實作者臨場決定,這是實作者會做錯決定的缺口。需要在結果檔多一個欄位(例如 `enabled: true/false`),或規定哪幾種 reason 要印。

### F3 函式名是 mangle 名,「demangle 名」這一支沒有資料來源,輸出也沒說怎麼顯示
severity: minor
blocking: 否
引句:「demangle 名以「operator new」開頭」
file: `src/profiling/memory/unwinding.cc`(v57.2)、libunwindstack `Unwinder.cpp`

1. 第 1 條把配置器判斷寫成兩種名字:demangle 名和 mangle 名。
2. 實際上 `stack_profile_frame.name` 只有一個欄位。
3. 我查到的程式路徑如下,每步都有原始碼為證:
   - heapprofd 把 `unwindstack::FrameData.function_name` 原樣送出。
   - libunwindstack 只在 `FormatFrame` 顯示時才呼叫 `DemangleNameIfNeeded`。
   - `VirtualMemoryMapping::InternFrameImpl` 原樣 intern 這個名字。
4. 所以真實資料是 `_Znwm`、`_ZN6fakesdk5Cache3putEv` 這種 mangle 名。
5. 後果有三個:
   - 「operator new 開頭」那條永遠不會命中,真正起作用的是 `_Znw`/`_Zna`。
   - 用 Python sqlite 對假表測試時,若 fixture 寫成 demangle 名,測試綠、真資料卻不同。
   - 排行裡所有 C++ SDK 的「函式」欄都是 mangle 名,spec 沒說要不要還原、在哪一層還原。
6. 另外,SQL 的 `LIKE '_Znw%'` 裡 `_` 是萬用字元,要用 `GLOB` 或 `ESCAPE`。
7. ⚠ PerfettoSQL 是否有 `demangle()` 函式,我沒查到官方位置,未驗證。

### F4 「不同路徑的同名 .so 不會混在一起」寫過頭,系統函式庫的定義漏了 vendor 等路徑
severity: minor
blocking: 否
引句:「所以不同路徑的同名 .so 不會混在一起」

1. 歸併鍵是「函式、.so 檔名、是否系統」。「系統」只看 `/system/` 與 `/apex/`。
2. 這會同時多出兩個問題:
   - `/system/lib64/libicuuc.so` 與 `/apex/com.android.i18n/lib64/libicuuc.so` 都是系統庫,同名會被併成一個呼叫位置。
   - `/vendor/`、`/product/`、`/system_ext/`、`/odm/` 底下的庫(例如 `/vendor/lib64/egl/` 的 GPU 驅動)會被標成「不是系統函式庫」,看起來像 App 自己的 .so。
3. 實務隱患那條又說「系統函式庫(例如 Bitmap 的原生記憶體)也可能被列出,標系統函式庫讓人分辨」。把驅動標錯,這個分辨功能就誤導人。
4. ⚠ 最多印 20 筆,系統庫是否會把第三方 SDK 擠出前 20,沒有真實專案數字可驗,我只能標未驗證。

### F5 沒有符號的框架以 rel_pc 當函式名,會讓同一個函式裂成多個呼叫位置
severity: minor
blocking: 否
引句:「寫成「.so 檔名+0x相對位址」並標沒有符號」

1. `stack_profile_frame` 以 `(rel_pc, name)` 為唯一鍵(`virtual_memory_mapping.cc`)。非葉框架的 `rel_pc` 是回傳位址。
2. 第三方 .so 通常 strip 過,內部函式沒有名字,所以「函式」欄就是 `.so+0x…`。
3. 具體例:未命名的內部函式 H 裡有兩個 malloc 呼叫點,各留 0.6 MiB。
   - 因為鍵是 `.so+0xA` 與 `.so+0xB`,兩個各 0.6 MiB,都低於 1 MiB。
   - 在呼叫位置層被篩掉,H 實際留了 1.2 MiB,卻不上榜。
   - S12(同一函式不同呼叫鏈加總)只對有名字的函式成立,這裡與它不一致。
4. 這條也會把不同邏輯擁有者合併:一個沒有名字的共用輔助函式被很多 JNI 函式呼叫,全併成一列。
5. spec 該明寫「沒符號時是按呼叫點而不是按函式歸併」,並把 S12 限定在有符號的情況。

### F6 回溯失敗時會附加一個 `ERROR …` 偽框架,第 1 條沒處理
severity: minor
blocking: 否
引句:「整條都是配置器時呼叫位置記成「?」,沒有上一框時呼叫者記成「?」」
file: `src/profiling/memory/unwinding.cc`(v57.2,`DoUnwind` 在 `error_code != ERROR_NONE` 時追加)

1. 回溯出錯時,heapprofd 會在 frames 尾端追加一個 `function_name = "ERROR " + …`、`build_id = ""` 的框架。
2. 具體例:堆疊是 `[malloc, operator new, ERROR ERROR_INVALID_MAP]`(回溯在配置器之後就失敗)。
   - 第 1 條的跳過規則沒有涵蓋這個偽框架。
   - 它會變成「第一個不是配置器的框架」,呼叫位置成了 `ERROR ERROR_INVALID_MAP @ ?`,被標成有符號、非系統。
   - 這跟「整條都是配置器時記成 ?」本質上是同一種「歸不到人」,卻出現兩種寫法。
3. 這種偽框架可能在排行裡佔位,應規定歸成同一個「?」。

### F7 排行抬頭說「結束時還留著」,實際只算 heapprofd 開錄之後的配置
severity: minor
blocking: 否
引句:「量測結束時還留著的原生配置,含快取與池,不代表漏」

1. 〈實驗室實測〉明寫「heapprofd 只記開始記帳之後的配置,所以暖機期間配的…本來就不算進來」。實務隱患也承認「量測一開始那一下的配置可能漏記」。
2. 但第 3 條規定 lumos 印出的抬頭沒有提這個範圍。
3. 具體例:SDK 在暖機輪就配了 80 MB 的快取,N 輪量測期間不再配置。排行完全看不到它。使用者讀到「結束時還留著」,會以為排行涵蓋全部。
4. 抬頭應補一句,例如「只含開錄之後配的」。

### F8 S5 的「正常版不列」與實驗表的觀察互相打架,正式流程也拿掉了實驗的 3 秒等待
severity: minor
blocking: 否
引句:「池照實列出(含快取與池),正常版不列」

1. 實驗表的正常版 `nativeCreate` 是「開關之間在 0 與 2 MB 來回」。
2. 實驗做法含「等 3 秒停錄」。〈打算怎麼做〉第 3 步的流程寫的是「驅動量測 N 輪 → 停錄」,沒有等待。
3. 若停錄時恰好有一塊 2 MB 還沒被下一個 onDestroy 釋放,結束累計 = 2 MB,大於 1 MiB。
   - 正常版會被列出,[manual] 驗收偶爾判失敗。
   - 這是 App 的非同步釋放造成的,不是設計意圖。
4. 該把等待寫回第 3 步,或讓 S5 容許這種波動。

### F9 「呼叫者 = 緊鄰的上一框」沒有被實驗查詢驗證過
severity: minor
blocking: 否
引句:「第一個不是配置器的框架就是呼叫位置,再往上一框是呼叫者」

1. 實驗的 SQL 只取 malloc 的上一層當呼叫位置(`c.parent_id`),沒有算呼叫者。表格第②列的 `← PlayerActivity.onCreate` 不是這條 SQL 產生的。
2. 照第 1 條字面,JNI 函式的上一框通常是 ART 的 JNI 跳板(例如 `art_quick_generic_jni_trampoline`,在 libart.so)。
3. 而 Java 框架可能要再往上一兩框才出現。
4. ⚠ 我沒有實驗當時的堆疊資料(spec 說錄檔已刪),不能確定上一框在這個裝置上是什麼。
5. 規則和表格不一致的風險在於:S5 驗收若只看呼叫位置不看呼叫者,測不到;使用者看到的呼叫者卻可能每個 JNI 函式都是同一個跳板。

### F10 靜態連結 libc++ 或 SDK 自己實例化的模板時,呼叫位置落在 std:: 內部
severity: minor
blocking: 否
引句:「SDK 自己包一層配置器(不在〈排行怎麼算〉第 1 條名單裡)」

1. 實務隱患把這件事列成已知限制,「要人往上看呼叫者」。我審的是這個理由夠不夠。
2. NDK 的 CMake 預設 `ANDROID_STL=c++_static`,libc++ 會編進 SDK 自己的 .so。此時:
   - `operator new` 靠名字(`_Znw`)還能被跳過。
   - 但 `std::__ndk1::vector<T>::__push_back_slow_path` 這類框架就在 SDK 的 .so 裡,不在名單上,會成為呼叫位置。
3. 結果是一個 SDK 內所有同型別容器的成長都併成同一列,「呼叫者」欄只記加總最大的那一個。
4. 使用者想往上看,但排行只給一層呼叫者,看不到更上面的真正擁有者。
5. 要嘛加一條「函式名以 `std::` 或 `_ZNSt` 開頭也跳過」的規則,要嘛承認這會讓靜態 STL 的 SDK 排行失真,並在 L3 說明裡要人用手動錄製補。

### F11 d2 的 context 留著已拿掉的判法描述
severity: minor
blocking: 否
引句:「判法(前後兩半增量)只在實驗室一台裝置驗過」

1. 這是縮範圍(d5)留下的殘句。
2. d2 的決定是「永遠只提醒」,理由是「判法只在一台裝置驗過、快取上限大於輪數會誤判」。
3. 但這份計劃已經不做判法,這句理由現在指向另一份計劃,不再是這份提醒的前提。
4. 這份提醒不擋推送的真正理由,是排行會列出快取與池,所以不能擋。

### F12 lumos 讀 `sites` 只驗 retained,形狀不對會崩潰並改變回傳碼
severity: minor
blocking: 否
引句:「retained 用 `_secev_int` 驗整數、再擋負數,不合格的呼叫位置不採用」

1. 結果檔可能被手改或壞掉。現有慣例是「形狀不對列成跳過,不噴例外」(`_macrobench_stab_native_unreachable` 的註解就是這樣寫)。
2. 這份 spec 只規定 `retained` 不合格怎麼處理。
3. `sites` 不是清單、某一項不是物件、缺 `func`/`so`/`caller` 時該怎麼辦,沒寫。
4. 照字面實作,這些情況會丟 `TypeError` 或 `KeyError`,改變 lumos 的回傳碼,直接違反 S4 和 d2。
5. 同一點,多筆 `retained` 相同時 lumos 的排序規則沒寫,輸出順序依賴實作。

### F13 單一 TP 語句要同時帶回排行、stats 和「有沒有任何一列」,spec 沒說怎麼做到
severity: minor
blocking: 否
引句:「每次 TP 呼叫只跑一條回傳列的語句」

1. 第 4 步要判三件事:排行列、stats 的 error/data_loss、`heap_profile_allocation` 有沒有任何一列。
2. 「排行為空」不等於「沒有任何一列」:所有呼叫位置都小於 1 MiB 時,排行是空的,資料表卻有列。
3. spec 沒說這是三次 TP 呼叫、還是一條帶標籤的 UNION ALL。
4. 另外,`ok` 但 `sites` 是空清單時,lumos 該印什麼也沒寫。
5. 這會造成實作者各寫各的,測試也難以對齊。

## 實務隱患逐類

- 併發:
  - 同一行程已有別的 heapprofd 工作階段,會得到 `heapprofd_rejected_concurrent`(error 等級),已涵蓋。
  - 兩個收集腳本同時跑,run-id 不同、遠端檔名不同,不衝突。
  - 無新增隱患。
- 效能:
  - 遞迴 CTE 只對 distinct 葉 callsite 走,且只在配置器框架上繼續,成本小。
  - 若實作成走到根,成本是葉數乘深度(最多 500),可到數百萬列。spec 沒要求對大型輸入做量測,建議實作時補一個效能測試。
- 資源:
  - 錄檔大小有上限(65536 KB,DISCARD),且 `heapprofd_buffer_overran` 已列入 failed。
  - 無新增隱患。
- 回滾:
  - 與遷移一起查過,spec 寫得完整,無 finding。
- 遷移:
  - `native_retained` 進指紋的說法與 `android-e2e-acceptance` 的指紋 WHY 一致。無 finding。
- 已排除:對外送出:
  - 理由成立,錄檔只在裝置與本機 run 目錄,無 finding。
- 已排除:守衛面:
  - 前提是 S4 的測試連第二段出事都驗,但 F12 顯示 lumos 讀端沒有保護,這個前提在讀端目前不成立。見 F12。
- 不可逆(不排除)、金流(不排除):
  - 理由本身站得住,無 finding。

## 固定席逐篇

- `Systems/android-stability-collector.md`:不破壞。既有的 PITFALL 要求「停完才從待收清單刪」,第 3 步的「第一段錄製拿掉才開第二段」遵守它。「不帶標準輸出尾巴」也遵守,第二段失敗原因只帶 stats 名稱與例外類型。落點需要補 about_code 與負責範圍,spec 已列。
- `Systems/macrobenchmark-adapter.md`:不破壞。「有退步也回 0,只提醒」與「`stability_unjudged` 一開始放好、鍵固定」兩條 WHY,第 6 步都照做。唯一缺口是 F12:讀端對 `sites` 形狀沒防護,會讓「只提醒、回 0」不成立。
- `Systems/android-e2e-acceptance.md`:不破壞。e2e 開記憶體時,stability 段與 `stability_scenarios` 另算雜湊接進指紋,所以 `native_retained` 會改指紋。spec 的遷移那條已正確寫明,單步 3600 秒上限也已列入。
- `Projects/Android記憶體與穩定性驗收_計劃.md`:不破壞,但要補寫。WHY「Native Heap 前後兩個數字只回報」與「同一條驅動指令呼叫兩次」兩句會被改,第 7 步已列出要改。
- `Projects/Android逐層診斷_計劃.md`:不破壞。它否決「每次都錄」,d4 的預設關、按情境開維持了這個否決。分層 WHY 要補一條例外,第 7 步已列出。
- `Projects/原生記憶體增長判法_計劃.md`:不影響。它承接分漲停,明寫「不改排行本身」。它的實驗 2 需要重讀每次傾印的資料,這份保留的 `heap-native.pftrace` 7 天內夠用。

總結:整份最高嚴重度為 major,blocking 共 2 條
