# 第三輪收貨(使用者 2026-10-28 裁:只審新判法)

三席(正確性、邊界、架構對齊,都是 sonnet、沒參與前兩輪的新代理)報告到齊後一次寫入;三份都已是正規化格式、quote-check 全數錨定、refcheck 全 ok;審查席沒動 repo(git status 只有編排者自己的第三輪材料);邊界席建過臨時目錄,已刪。

## 發現編號

正確性 m1–m5、邊界 n1–n8、架構對齊 y1–y5(順序照各席報告的 F 編號),共 18 條。

## 重現表

| ID | 重現 | 結果 |
|---|---|---|
| m1 | 編排者自寫模擬(上限 4 塊的池、量測第 1、2 輪各配 2 MB、每秒傾印、N=8,gap 0.5–2.0 秒 × 每輪 1.2–2.2 秒 × 傾印相位 4 種 = 64 組):64 組全判線性增長(席位報約一半) | HIT |
| m2 | 同一支模擬跑「第 3 輪一次配 6 MB」:判不增長(不是席位說的線性);原因是 t4 取最後一列的 ts,一次跳升時 t4 就落在跳升上,後段窗口取到跳升前的 0——跟 n1 第 3 點同一個洞;判法對一次性跳升的結果隨 t4 的取法翻轉 | HIT(現象不同、根因成立) |
| m4、n3 | 讀〈打算怎麼做〉第 4 步:1 MiB 與前 200 在 callsite 層、〈判法〉的 L1/L2 在歸併後的呼叫位置層 | HIT |
| y1 | 讀收集腳本:heap_counts、cycle_numbers 都用 split(",") | HIT |

## 上網查證(使用者 2026-10-28 要求:結果不確定就上網搜)

- 停錄時有沒有最後一次傾印:有。官方文件寫「the dump at the end of the profile that is always produced」;v57.2 heapprofd_producer.cc 的 StopDataSource → ShutdownDataSource → PostDisconnectSocket → HandleSocketDisconnected → DumpProcessState,上限 stop_timeout_ms(預設 5000),逾時記「Final dump timed out.」不補。來源:https://perfetto.dev/docs/data-sources/native-heap-profiler、https://raw.githubusercontent.com/google/perfetto/v57.2/src/profiling/memory/heapprofd_producer.cc
- stats 的等級(v57.2 stats.h):heapprofd_buffer_corrupted、hit_guardrail、client_error、malformed_packet、missing_packet、rejected_concurrent、non_finalized_profile 是 kError,heapprofd_buffer_overran 是 kDataLoss;client_disconnected、sampling_interval_adjusted、unwind_time_us、unwind_samples、client_spinlock_blocked、last_profile_timestamp 是 kInfo;traced_buf_* 的資料遺失有 13 項 kDataLoss。第二輪折入的「severity 是 error 或 data_loss」成立。來源:https://raw.githubusercontent.com/google/perfetto/v57.2/src/trace_processor/storage/stats.h
- 接上已在跑的行程:官方文件說行程被送訊號後「a few hundred milliseconds after the next allocation」才開始記,閒置後突然大量配置可能漏記。來源同上官方文件。
- 錄製結束後 App 的負擔:v57.2 client_api.cc 在下一次記錄失敗時呼叫 ShutdownLazy → DisableAllHeaps 並清掉 client,之後的 hook 先看 enabled 就返回;之後的工作階段可以用 AHeapProfile_initSession 重新接上。所以中斷時不停 App,負擔也只剩每次配置一個判斷;停 App 仍保留(讓下一次量測從乾淨行程開始)。來源:https://raw.githubusercontent.com/google/perfetto/v57.2/src/profiling/memory/client_api.cc
- 沒有符號的框架 name 是 NULL 還是空字串:沒查到明確說法;Perfetto 自己的符號化工具判「沒有符號」看的是 symbol_set_id IS NULL,不是 name。計劃改成 name 是 NULL 或空字串都當沒有符號。
- 沒有變動的傾印會不會寫列:官方文件沒寫;前一輪三席引的 profile_packet_sequence_state.cc 是只在差額非 0 時寫。拆分後的排行只用最後累計,不受影響。

## 到頂裁定

這是 high 分級上限內的最後一輪,仍有 major(m1、m2、m4、n1、n2、n3、n4、y1)。m1、m2 與 n2 指出判法換了兩次形狀(三個時間點 → 窗口最小值)仍受時間對齊左右,而且分不出一次性跳升;攤給使用者裁,使用者 2026-10-28 選「拆兩份:先做排行」:這份縮成「錄製 + 找呼叫位置 + 列出量測結束時還留著最多的原生配置」,只提醒、不分漲或停;「在漲還是停住」的判法另開計劃,先在實驗室用每輪記號切窗實驗。縮小後的這份要再過一輪設計審。

## 根因分組與處置

- 組 A 判法受時間對齊左右、分不出一次性跳升(m1、m2、m3、n1、n2、n6、y2、y3、y5 的分類部分):整套分類(L1、L2、線性增長、停住、樣本不足的時段條件)從這份拿掉,搬到新計劃 Projects/原生記憶體增長判法_計劃;這份只列結尾累計。→ 折(拆出)。
- 組 B 篩選與前 200 的層次(m4、m5、n3、n5、y5 的門檻部分):先歸併到呼叫位置(函式,.so,系統旗標),再套 1 MiB、再取前 200;決勝鍵是結尾累計降冪、函式名升冪、.so 升冪;呼叫者取「從它進來的那些 callsite 結尾累計加總」最大的那個,並列照呼叫者名字升冪;沒有上一框時 caller 寫「?」。1 MiB 只在收集腳本篩一次(lumos 不再重套)。→ 折。
- 組 C 沒有符號與 mapping 缺名(n4):name 是 NULL 或空字串都當沒有符號,寫成「.so 檔名+0x相對位址」;mapping 沒名字時 so 寫「?」、system 是 false;.so 檔名用 SQLite 字串函式取最後一段;系統旗標照完整路徑判,歸併鍵帶系統旗標,所以不同路徑的同名 .so 不會混在一起。→ 折。
- 組 D 配置器名單的比對方式(n8):函式名精確比對,外加 operator new 的 demangle 名(以「operator new」開頭)與 mangle 名(_Znwm、_Znam、_ZnwmRKSt9nothrow_t、_ZnamRKSt9nothrow_t 這類以 _Znw、_Zna 開頭);檔名那條跳過這幾支 .so 裡的全部框架(歸責給呼叫它們的 SDK)。→ 折。
- 組 E 失敗原因的順序(n7):跑完之後的檢查順序寫死:查詢逾時 → stats 有 error 或 data_loss → heap_profile_allocation 沒有任何一列 → 其餘 ok。→ 折。
- 組 F 解析寫法(y1):把「讀範本、換佔位、寫暫存檔、跑 TP、解析成列」抽成一支共用函式,裡面用 csv.reader;heap_counts、cycle_numbers 一起改用它(既有行為不變,用既有測試守),同一支檔只剩一種解析。→ 折。
- 組 G 數字驗證(y4):lumos 讀 sites 時,end 用 _secev_int 驗整數、再擋負數;讀來源段沿用 _macrobench_stab_src。→ 折。
- 組 H 視窗累計的同 ts 陷阱(n6):拆分後排行不用視窗累計(只用整段 sum),這條隨組 A 移到新計劃。→ 折(拆出)。
- 組 I 樣本不足提早判(y3):拆分後沒有樣本不足這一類;N 不再影響排行。→ 折(拆出)。

全部 18 條折入(其中組 A、H、I 是拆到新計劃),沒有放行。

## 修補因果

m1、m2、n1、n2、n3、y1–y5 都落在第二輪折入時新寫的句子上(窗口最小值、四等份、csv.reader、low1/low2、前 200 的位置);第二輪那套是為了修第一輪「三個時間點」的洞而換的形狀,這輪顯示換了形狀仍有同一族(時間對齊)的洞。

## 縮小後自查

- 鏡像核對:派一個校對代理(haiku,只讀)對縮小後的計劃、新計劃、r3 快照與本紀錄核對,找到 16 處(PRIOR-ART ③ 仍寫判法依據、RETIRE-IF 與 REVISIT 對同一結果結論相反、「一定會傾印」與 5 秒上限矛盾、指向不存在的查證段、本紀錄組 D 多寫 operator delete、S7 漏 App 結束、呼叫者規則與 mapping 缺名與 main_process_only 與錄檔位置與「沒寫等於空清單」與 L0 不變沒條款、縮小後的計劃沒指到已知失效形狀、related 不對稱、步驟 7 與 RETIRE-IF 還叫「提示」),15 處當輪改掉,新增 S21、S22;d5 的 context 寫了舊判法名字,那是決策脈絡,照留。
