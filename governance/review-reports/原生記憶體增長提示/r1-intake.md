preflight-4: ran

# 前掃(首輪派審前)

前掃由編排分出的分身自己做,沒有另派子代理(分身規則不准再派子代理);固定清單四項:①未定義的詞 ②壞引用 ③範圍自相矛盾 ④機械宣稱驗語意。排乾先跑過:refcheck 0 處宣稱、0 壞引用;prose-lint 1 處「一段時間」已量化成 dump_phase_ms、dump_interval_ms;pitfalls --check 有節、命中四類都在〈實務隱患〉。

## ①未定義的詞(直接修)

- 「skill 的 L3」:補成「skill lumos-android-evidence 的 L3(逐層診斷的第四層「誰配置、誰留住」,要宣告測試資料才做)」。
- 「heapprofd」在白話段第一次出現:補「掛在 malloc/free 上記每個呼叫位置配了多少、還了多少」。

## ②壞引用

- 沒有:related 三篇、lands_in 一篇都存在(lint 0 問題);正文沒有反引號路徑宣稱(refcheck 0 處)。

## ③範圍自相矛盾(直接修)

- 白話段寫「在 N 輪量測期間另開一段」、〈打算怎麼做〉第 2 步寫「另錄一份(或另跑一段 N 輪,見待決問題)」,與已裁的 d1(另跑一段 N 輪)不一致:兩處改成「在既有量測之後另跑一段 N 輪(d1)」。
- 〈實務隱患〉量測干擾那條寫「跟追蹤檔同時錄可能讓那幾項變差」,d1 已排除同時錄:改成照 d1 另跑不受影響;原句的「這次實驗沒量開銷」搬成獨立一行 REVISIT。

## ④機械宣稱驗語意(開檔讀碼)

| 計劃原句 | 讀到的程式 | 結果 | 修改前 → 後 |
|---|---|---|---|
| 收集腳本已經有「暖機 W 輪 → 量測 N 輪」兩次驅動呼叫,量測期間本來就錄一份 Perfetto 追蹤檔 | android-stability-collect.sh 的 measure():driver(warmup) → start_record → driver(cycles) → stop_record | 成立 | 不改 |
| skill 的 L3 已經在用 heapprofd(--heaps libc.malloc)事後診斷原生漏法 | skill SKILL.md〈L3〉第 3 步 | 成立 | 只補詞義(見①) |
| Native Heap 前後兩個數字(只回報、不判) | 收集腳本 measure() 把 native_heap_kb 寫進結果檔;scripts/lumos 整支沒有 native_heap 字樣 | 不成立:lumos 不讀也不印,只在結果檔 | 「只回報、不判」→「只寫在收集腳本的結果檔,lumos 判定不讀也不印」 |
| 錄檔放 run 目錄、檔名 heap-*.pftrace(沿用 7 天自動刪的樣式) | prune_old_snapshots() 只刪 .lumos/artifacts/android/<各 run 目錄> 第一層、檔名 fullmatch heap-.*\.pftrace;開跑前的 git 忽略檢查照 ARTIFACTS 常數逐檔查 | 部分成立:7 天刪對得上;但 git 忽略檢查不會自動涵蓋新檔 | 第 2 步改成「直接放 run 目錄第一層、檔名 heap-*.pftrace(既有 7 天自動刪只看各 run 目錄第一層、這個檔名樣式),並加進開跑前『產物有沒有被 git 忽略』那份逐檔清單」 |
| heapprofd 只記開始記帳之後的配置,暖機期間配的不算進來 | 外部:perfetto.dev native-heap-profiler「all allocations done between when profiling is enabled, and the end of the profiling session」;實驗室 pool 情境暖機已配 2 塊、量測只見 +2 MB | 成立 | 不改 |

# 第一輪收貨

六席(正確性、邊界、整合、資源併發、回滾、架構對齊,都是 sonnet、沒參與過這個計劃的新代理)報告到齊後一次寫入;六份都已是正規化格式、quote-check 全數錨定、refcheck 全 ok;審查席沒動 repo(git status 只有編排者自己的第一輪材料)。seat-check 有三席沒提到派工單列的 Systems/android-stability-collector 筆記(只觀測)。

收貨時另查到兩件流程上的事:
- 派工詞的 LUMOS-SPEC 標記沒附上任何固定席節點:掛鉤在會談目錄(Backend_improve 工作樹,分支比 20e1a255 舊)讀圖譜,那裡還沒有 Systems/android-stability-collector,計劃直接連結的三篇也就沒被附上。回滾、邊界、整合三席自己去工作樹讀了那篇與連結的計劃並逐條判;其餘三席寫了「沒附到」。下一輪改從開在本工作樹的會談派、或手貼固定席。
- 架構對齊席開頭說「工作樹裡的計劃比 r1-snapshot 舊」:編排者核對 `git show 5bf55ca2:<計劃>` 與工作樹檔逐字相同,是席位誤讀;不影響它的發現(它說只用快照判)。

## 發現編號

正確性 c1–c7、邊界 e1–e6、整合 i1–i12、資源併發 s1–s11、回滾 k1–k8、架構對齊 a1–a7(順序照各席報告的 F 編號),共 51 條。

## 重現表

| ID | 重現 | 結果 |
|---|---|---|
| c1、e2、s6 | 照計劃字面「依時間切成前後兩半」加實驗流程「量測後等 3 秒停錄」,以計劃自己的數字推算 N=3、每輪約 1.5 秒、每輪 2 MB:傾印 1 到 7 秒,未釋放 2,4,4,6,6,6,6 → 中間第 4 次 6、前半增 4、後半增 0 → 照字面判「停住」 | HIT(推算,三席獨立一致) |
| c3、i8 | 列出判法三條的條件組合:f≤0 且 b>0 落「其他→不增長」;0<b<f/2 同時可讀成「停住」與「其他」 | HIT(讀計劃) |
| c4、e3、s8 | 讀實驗室 fakesdk.c:JNI 函式直接呼叫 malloc;計劃的查詢只取 malloc 上一層 | HIT(讀碼;C++ operator new 那層為外部知識,三席獨立一致) |
| s1、e4、i3、k3 | 讀收集腳本:state["rec"] 只有一格、cleanup 只收 state.get("rec");start_record 的遠端與本機檔名寫死 lumos-stability-{run_id}、record.pbtxt、cycle.pftrace | HIT |
| s2、e4、i1、k6 | 讀 measure():第一段之後依序 pidof、unreachable、native_heap_kb、快照、read_exits;lumos 的 _macrobench_stab_pids 要求剛好 3 個 | HIT |
| s4、i2 | 計劃錄製設定 duration_ms: 120000 寫死;既有錄製用 max_record_s(stop_record 的「到了上限」訊息) | HIT |
| e1、s3、i7 | `grep -rn profileable scripts`(不含測試)零命中:收集腳本沒有任何 profileable 偵測 | HIT |
| k2、i12 | 讀 _e2e_scenarios_err:情境欄位不在 E2E_SCENARIO_KEYS 就回「不認得的欄位」;_macrobench_stab_optional_err 沒有未知鍵檢查 | HIT |
| a1 | 讀收集腳本檔頭「不判過不過(判定在 lumos macrobench --stability)」 | HIT |
| s5 | perfetto --background 不等資料源啟動(席位引 v57.2 perfetto_cmd.cc 說明) | 採信(外部原始碼,未另跑) |
| s3 | 同一行程同時只能有一個 heapprofd 工作階段(席位引 v57.2 heapprofd_producer.cc「Rejecting concurrent session」) | 採信(外部原始碼,未另跑) |

## 根因分組與處置

- 組 A 判法沒定義完整(c1、c2、c3、c5、c6、e2、s6、s11、i8):改成只取三個時間點(第一次傾印、量測驅動跑完那一刻停錄時的最後一次傾印、時間上最接近兩者正中的那次),停錄緊接在驅動跑完之後(不再等 3 秒);少於 3 次傾印由收集腳本寫成 failed「樣本不足」;某呼叫位置在某時間點沒有列當 0;判法改成一條互斥又涵蓋全部的規則:整段增量 = 結尾 − 開頭,小於 1 MiB(1048576 位元組)不增長、否則後半增量 ≥ 整段增量的三分之一是線性增長、其餘是停住(f、b 都非負時等同原本「後半至少前半的一半」,實驗室四種情境照舊分對);排序與列出下限統一成整段增量。→ 折。
- 組 B 呼叫位置歸屬(c4、c5、e3、s8):從 malloc 往上走,跳過配置器那幾層(libc、libc++、libc++_shared、libstdc++ 的 malloc 家族與 operator new),取第一個不是配置器的框架當呼叫位置,再往上一層記成呼叫者;沒有符號時寫成「.so 檔名+相對位址」並標符號缺失;.so 只記檔名。→ 折。
- 組 C 錄不到被當成沒事(e1、e6、s3、s5、i7):結果檔那段只有 ok、failed、unsupported 三種狀態;傾印少於 3 次、trace_processor 的 stats 表有 heapprofd 開頭的錯誤計數非 0、第二段前後 pid 不同,都是 failed 附原因;Android 11 以下列 unsupported;事前不偵測 profileable(沒有可靠的事前判法),沒錄到時的原因寫出可能的三種;只量主行程並寫進結果;開錄後等第一次傾印再開始驅動。→ 折。
- 組 D 第二段的位置、錄製與清理(s1、s2、s4、e4、i1、i2、i3、i4、k3、k6、a5):第二段放在既有量測全部讀完(含第二次 read_exits)之後;自己重新停 App、啟動、暖機 W 輪、量測 N 輪;自己的 pid 與前後結束紀錄記在新段落、不碰既有 pids、exits;錄製沿用 start_record、stop_record(加參數:設定範本、檔名後綴),設定範本另開一支 pbtxt、時長照 max_record_s,遠端檔名加 -native 後綴,本機 heap-native.pftrace、record-native.pbtxt 列進 ARTIFACTS;第一段從 state 拿掉之後才開第二段,沿用同一個 state["rec"] 槽,cleanup 不用改;第二段結束後停 App。→ 折。
- 組 E 分層與輸出(a1、a2、a4、i6、i7、k7):收集腳本只存每個呼叫位置三個時間點的未釋放量與傾印數,分類、下限、排序都在 lumos;lumos 輸出固定鍵 native_growth(照 low_iterations 的形狀),文字與 --json 都有、不看門檻檔有沒有寫;印前過 _out_clean、最多列 20 個;結果檔沒有這段(舊收集腳本)時不印;數字照 _macrobench_stab_val 的規矩驗。→ 折。
- 組 F 設定鍵與相容、退回(k1、k2、k7、i10、i12、a3、e5、c7):開關改成寫在 stability 段的清單 `native_growth: ["<情境名>", …]`(預設那段寫 "default"),不進 stability_scenarios、不動 E2E_SCENARIO_KEYS:舊版 lumos 不驗 stability 段的未知鍵,退回不會擋下整份設定,同時保留 d4 的「按情境開」;判斷順序寫死(沒打開 → 沒宣告測試資料 → 版本不支援 → 錄製);寫進設定會讓 e2e 的記憶體設定指紋變、要重跑整套,寫進〈實務隱患〉。〈回退〉逐項列出每個寫出物。→ 折。
- 組 G 已排除理由(k3、k4、k5、k8;邊界、整合兩席判金流與不可逆站得住,與回滾席相反):編排者讀過 measure() 與 d4 的結帳例子後判回滾席對:第二段就是再驅動情境 W+N 次,情境含下單時會在測試後端多下單,「不碰交易」不成立;錄檔先寫在裝置上、拉回才在本機,「只在本機 run 目錄」字面不成立;7 天刪靠還有人跑收集腳本。改寫:金流改成不排除、寫明前提;對外送出、不可逆照實改理由並補回頭條件;守衛面改成以組 D 的位置規定為前提。→ 折。
- 組 H 落點與文件(i5、i11、a7、e5 第 4 點):lands_in 加 Systems/macrobenchmark-adapter;skill 的 L0 往下條件加一條「native_growth 有列出位置」;reference.md 的設定表、driver 跑幾次、保留清單一起改;新範本檔登記進 _VENDORED_TREE_FILES;Android記憶體與穩定性驗收_計劃那句「只剩 Native Heap 前後數字當線索」實作後改。→ 折。
- 組 I 查詢效能與解析(s7、i9、e6 第 2 點):不做每次傾印 × 每列的連接,只算三個時間點的累計(一次掃描);輸出用 csv 模組解析,不用逗號切;收集腳本最多存 200 個呼叫位置(照整段增量排)。→ 折。
- 組 J 分析工具版本(s9):收集腳本照第一段用同一個 TP;計劃寫明這次用到的表與欄位(heap_profile_allocation 的 ts、size、callsite_id、heap_name,stack_profile_callsite、stack_profile_frame、stack_profile_mapping)整合席在 v57.2 與 v58.2 都查到;版本釘法照舊留 REVISIT。→ 折(寫明,不新增機制)。
- 組 K 撤除條件(s10):「多花的時間超過量測本身的一倍」照 d1 本來就會成立,改成兩倍。→ 折。
- a6 判法數字寫死在程式、不走門檻檔:放行。理由:提示永遠只提醒(d2),門檻檔的欄位是給會判過不過的檢查用的;為一個不擋的提示在門檻檔加欄位等於多一個新機制,REVISIT 已排定拿真實專案重定這兩個數字。

## 修補因果

首輪,沒有前一輪修補。

## 折入後自查

- 新判法拿實驗室四種情境的數字重算(結尾、前半、後半 → 整段增量、後半):①16、8、6 → 14、6,6 ≥ 14/3 線性;②同①;③4、2、0 → 2、0,停住;正常版 → 0,不增長。四種都跟原判法同結果。
- 新增機制逐項寫了「不加的最小解為什麼不夠」(見計劃〈審計修正紀錄〉)。
- 鏡像核對:派一個校對代理(haiku,只讀)對折入差異、計劃全文與本目錄席報告核對,找到 14 處不一致(狀態名「樣本不足」對 failed、開頭指哪次傾印、白話與 PRIOR-ART 仍寫每輪都漲與前後兩半、排序用詞、MB 與 MiB、S3 配置器清單、可能原因只寫兩種、驗收計劃那句沒排進步驟、審計紀錄類別少列、查詢逾時與總表與收據寫法沒寫、S7 漏 App 結束、輸出上限與清理沒條款),當輪全改;新增條款 S9。pending_questions 的 Q3 與 d2 的 context 是當時的問句與決策脈絡,照原文留著。
