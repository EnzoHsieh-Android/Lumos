# 第二輪收貨

六席(正確性、邊界、整合、資源併發、回滾、架構對齊,都是 sonnet、沒參與第一輪的新代理)報告到齊後一次寫入;六份都已是正規化格式;quote-check 五份全數錨定,資源併發席 F4 的引句「驅動一跑完就停錄」只有 8 字、低於 10 字下限而錨不到——那句確實在快照〈打算怎麼做〉第 3 步,同一件事正確性席 F1 用足長引句報了(major),照規矩機械重現後採信;refcheck 只有回滾席一處 missing,是計劃要新建的 android-stability-heapprofd.pbtxt;審查席沒動 repo(git status 只有編排者自己的第二輪材料),席位臨時目錄沒建。這輪派工詞手列了五篇固定席筆記(第一輪掛鉤附不到),六席都逐篇判了。

## 發現編號

正確性 p1–p9、邊界 b1–b10、整合 g1–g10、資源併發 z1–z9、回滾 h1–h8、架構對齊 x1–x8(順序照各席報告的 F 編號),共 54 條。

## 重現表

| ID | 重現 | 結果 |
|---|---|---|
| z4 | 快照〈打算怎麼做〉第 3 步原文有「驅動一跑完就停錄」(引句 8 字低於下限才錨不到);同事正確性席 p1 足長引句已錨定 | HIT |
| p3、z2、g2、b8 第 5 點 | 席位引 v57.2 profile_packet_sequence_state.cc:只在 alloc_delta 或 free_delta 非 0 時寫列;實驗查詢以 distinct ts 當傾印清單 | 採信(外部原始碼,三席獨立一致) |
| z1、g1、p7 | 席位引 v57.2 stats.h:heapprofd_unwind_samples、heapprofd_unwind_time_us、heapprofd_last_profile_timestamp 等是 info 等級,成功錄製本來就非 0 | 採信(外部原始碼,兩席獨立列出同一批名字) |
| b3、g6、x4 | 讀 scripts/lumos:_macrobench_stab_optional_err(st) 只收 stability 段,stability_scenarios 在 _macrobench_stab_top_err(raw) 才拿得到 | HIT |
| b4、g5、h4 | 讀 scripts/lumos:low_iterations 只在有結果目錄的主路徑填與印;_macrobench_without_results 只 update 判定結果、印門檻 | HIT |
| b5、g4、p5 | 讀收集腳本:android_sdk 讀不到時是 None;計劃寫「Android 11 以下」與括號「要 11 以上」互斥 | HIT |
| z5、h3、g10 第 4 點 | 讀收集腳本 main():json.dump 在 measure() 回傳之後;例外走 cleanup 再 raise,不寫結果檔 | HIT |
| x1、g7 | 讀收集腳本:既有兩支查詢是 .sql 範本(android-heap-classes.sql、android-stability-cycle.sql);android-ui-attribution.sql 已用 WITH RECURSIVE | HIT |
| g3、x3 | 讀收集腳本:start_record 本機設定檔寫死 record.pbtxt、stop_record 本機錄檔寫死 cycle.pftrace;只加一個後綴做不出 heap-native.pftrace | HIT |
| p1、b2 | 用計劃自己的正常版(每輪 0 與 2 MB 來回)推算:結尾落在配置還留著的相位時,整段 2 MB、後半 2 MB → 照字面判線性增長 | HIT(推算,兩席獨立一致) |

## 根因分組與處置

- 組 A 三個時間點的做法本身站不住(p1、p2、p3、p6、b1、b2、b8、z2、z3、z4、g2):三席各自指出傾印清單取不到沒變動的那幾次、「開頭」要對主機與裝置時鐘、單點取樣碰到配了又還的來回會誤報。改法換形狀,不再補單點:開錄後立刻驅動、驅動跑完等一次傾印間隔再停錄(對 heapprofd 的收尾傾印);heapprofd 只記開錄後的配置,開頭固定是 0,不用找傾印;每個呼叫位置的累計是階梯函數,在任何時刻的值 = ts 不晚於那一刻的 size 加總,不需要傾印清單;錄製時段(trace_bounds 的起點到最後一列 ts)切四等份,取第二份裡的最小值 L1 與第四份裡的最小值 L2(最小值不受配了又還的來回影響,只要一份至少涵蓋一輪);L2 小於 1 MiB → 不增長,L2 − L1 ≥ L2 的三分之一 → 線性增長,其餘 → 停住。樣本不足改成看時段長度與輪數(N 至少 4、時段至少 4 個傾印間隔),不數傾印。實驗表裡沒有窗口最小值,新判法要在實驗室重跑才知道分得對不對,原本「重算結果相同」那句拿掉。→ 折。
- 組 B stats 篩法(z1、g1、p7):改成 stats 表裡 severity 是 error 或 data_loss、值非 0 的(會連 traced_buf 的丟資料一起抓到,b10 第 3 點)。→ 折。
- 組 C 版本邊界(p5、b5、g4 第 1 到 4 點):android_sdk 低於 30 → unsupported;讀不到(None)→ unsupported「讀不到 Android 版本」。→ 折。
- 組 D 錄失敗的原因看不到、缺鍵的語意(p4、x6、h2、g4 第 5 點):lumos 的 native_growth 固定鍵改成物件(status、reason、sites);打開了但不是 ok 時印「原生增長提示沒跑成」加原因;壞的那一列不靜默丟,計數印出;skill 讀不到這個鍵就當 lumos 太舊、照舊手動錄,不當零筆。→ 折。
- 組 E 輸出路徑(b4、g5、h4):鍵放進 macrobench 結果的初始字典,載入結果檔後就算,主路徑與只有 stability 的路徑都算、都印,印的函式獨立於門檻輸出。→ 折。
- 組 F 設定驗證的位置與保留名(b3、b9、g6、x4、x5、h8):檢查放在 _macrobench_stab_top_err(拿得到 stability_scenarios);沒指定情境那段改用不可能是情境名的 "@default"(情境名只收英數字、底線、連字號),不去改既有情境名規則(改了舊設定會被新版擋);清單元素要是非空字串、不重複;收集腳本 load_config 回傳這次的情境名給 measure 用。→ 折。
- 組 G 驅動失敗(p9、b6):第二段任何一次驅動回 ok false → failed「驅動失敗」附 why;第一段驅動失敗或 pid 讀不到 → 不跑第二段,寫 failed「第一段沒跑成,不跑第二段」。→ 折。
- 組 H 例外隔離與中斷(z5、z7、h3、g10 第 4、5 點):收集腳本先把第一段結果寫成結果檔(native_growth 段先寫 failed「第二段沒跑完」),第二段整段包在 try/except Exception,跑完再原子替換結果檔;第二段被中斷時,cleanup 另外停 App(state 記一個「第二段進行中」的旗標),本機拉到一半的錄檔照既有暫存規則處理。→ 折。
- 組 I 檔名參數(g3、x3、z8、h7 第 3 點):start_record、stop_record 的參數改成設定範本、遠端檔名前綴、本機錄檔名、本機設定檔名、上限訊息裡的設定鍵;遠端檔名改用 lumos-native-<run-id>.*(不同前綴,不會跟某個 run-id 的第一段撞名)。→ 折。
- 組 J 查詢放哪、怎麼解析(x1、x2、g7、z9、b7):查詢放新的 .sql 範本 android-stability-native.sql(照既有 .sql 範本、用標準 SQLite 與 android-ui-attribution.sql 已用過的 WITH RECURSIVE),每次 TP 呼叫一條回傳列的語句;先在 SQL 裡篩出最後累計至少 1 MiB 的 callsite、照累計取前 200 個再往上取祖先,彙總鍵是(函式,.so),呼叫者取累計最大的那個;全部框架都是配置器時記成「?」;整個輸出交給 csv.reader 解析,第一段的 split 寫法不回頭改;測試用內建 sqlite 對假表跑。→ 折。
- 組 K 系統函式庫與包裝名(p8):配置器名單補 __libc_malloc、je_malloc、tc_malloc、__wrap_malloc;所在 .so 的完整路徑在 /system/ 或 /apex/ 底下的標「系統函式庫」;同一呼叫位置多個呼叫者、SDK 自己的模板配置照實寫進〈實務隱患〉。→ 折。
- 組 L 回退與已排除(h1、h5、h6、h7):回退預設留著設定鍵(舊版忽略),刪鍵寫明會讓 e2e 指紋再變、整套重跑;「不可逆」改成不排除(後端副作用同金流);兩個新檔名只在這次情境打開時才加進 git 忽略檢查;消費專案留下的範本檔與裝置殘留給刪除指令,reference.md 那句清理說法改。→ 折。
- 組 M 落點與用詞(x7、x8、g8、g9、固定席意見):〈判法〉分成收集腳本做的(取數、往上找呼叫位置)與 lumos 做的(分類、下限、排序);結果檔鍵名寫死(sites[] 的 func、so、caller、symbol、system、low1、low2、end);新範本檔加進 Systems/android-stability-collector 的 about_code、改它的負責範圍;印出照鄰居用 _events_clean(…, 500);lands_in 不加逐層診斷計劃,但第 7 步補寫它的分層 WHY 加一條例外、驗收計劃那句「driver 跑兩次」一起改。→ 折。
- 組 N 時間成本(b10 第 1、2、4 點,z6):第二段的時長預算照 max_record_s 但要加上停錄前那一個傾印間隔;第二段約讓收集時間再多一段量測,寫進〈實務隱患〉,並提醒 e2e 的單步上限 3600 秒。→ 折。

全部 54 條折入,沒有放行。

## 修補因果

設計審第二輪;第一輪的折入讓組 A 的三個時間點、組 D 的空清單形狀、組 E 的「照 low_iterations」、組 F 的檢查位置與 "default"、組 I 的「一個後綴」這幾處是第一輪折入時新寫的句子,這輪的發現落在它們上面;其餘(stats 名單、版本邊界、例外隔離、檔名)第一輪就有對應的句子或空白。

## 折入後自查

- 新判法拿計劃自己的四種情境推算(每輪 2 MB、N=8、時段切四份,每份兩輪):①、② 每輪多留 2 MB:L1 約 4 到 6、L2 約 12 到 14,L2 − L1 約 8 ≥ L2 的三分之一 → 線性增長;③ 池在量測前兩輪補滿到 4 MB:L1 = L2 = 2 → 停住;正常版 0 與 2 MB 來回:每份裡都有回到 0 的時刻,L1 = L2 = 0 → 不增長。這只是推算,實機要重跑(S5)。
- 鏡像核對:派一個校對代理(haiku,只讀)對折入差異、計劃全文與本目錄第二輪席報告核對,找到 13 處(收集腳本取前 200 個的排序依據、舊否決段仍說新判法已分對與殘留整段後半用詞、第二段時長沒加傾印間隔、四等份切點與取整沒寫、三種 failed 原因與先寫結果檔、git 忽略檢查只在打開時、skill 缺鍵、整條都是配置器、情境名從 load_config 來這幾處沒條款、測試做法沒寫、本紀錄組 D 一句與計劃不符),當輪全改;新增 S17、S18、S19。
