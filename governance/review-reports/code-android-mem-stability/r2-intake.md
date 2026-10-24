preflight-4: ran

# code-android-mem-stability r2 收貨

審材:對主線 7d17bd73 到 44d93aba 的完整改動,切四包(lumos 判定 r2-pkg-lumos.patch 608 行、收集範本 r2-pkg-templates.patch 599 行、測試 r2-pkg-tests.patch 966 行、文件與 skill r2-pkg-docs.patch 683 行),每包配同一批檔從修前 1e47929e 到修後 44d93aba 的修補差異(r2-repair-<包>.patch)。架構對齊與程式資安看程式整包 r2-snapshot-code.patch(1207 行),文件資安看測試與文件整包 r2-snapshot-tests-docs.patch(1649 行);兩席資安合起來涵蓋全部改到的檔。每席實際讀量(共同派工詞 118 行加材料)都在 1800 行內。
八席:正確性、資源、邊界、整合、通才、架構對齊、程式-資安、文件-資安(都是 sonnet)。八席都交回後才一起存檔與處理;席報告從各席的對話紀錄取最後一則回答原文存檔(完成通知會把尖括號轉成跳脫字)。
id 前綴:C 正確性、R 資源、B 邊界、I 整合、G 通才、A 架構對齊、X 程式-資安、Y 文件-資安;編號照各席報告順序(架構對齊照它三問裡的出現順序)。
引句:quote-check 對各席自己那一包跑,七席全錨;資源席兩句跨行引句錨不到(R1、R4,見下),機械重現 HIT。正確性席最後一行總結把等級與 blocking 寫在同一行,用 report-normalize --write 搬成兩行(純格式)。
圖譜鏡頭:派工掛鉤會從會談目錄(Backend_improve)的分支帶錯表態(第一輪 I11 就是這樣來的),這輪改由編排者在被審工作樹跑 lumos dispatch-lens 後貼進共同派工詞;記成 Issues/派工鏡頭附的表態取自會談目錄的分支。
記帳:--spec 與 --reviewed 每席都填四包原樣接起來的 r2-snapshot.patch(等於 r2-snapshot-code.patch 接 r2-snapshot-tests-docs.patch),--snapshot 與 --scope-lines 填該席審的那一包;用量與耗時填各席完成通知裡的數字。

## 機械重現(總表)

做法:把被審的提交 44d93aba 的 scripts/ 解到暫存目錄,換上修正後的 scripts/test_lumos.py,跑 `python3.14 scripts/test_lumos.py -k memstab`。結果 278 過、25 條斷言紅,存在 r2-repro-old-code.log。驅動逾時、快照工具逾時兩段在舊版紅,一部分是因為環境變數改了名(舊版讀 LUMOS_STABILITY_LONG_S),所以快照工具逾時另外用新舊兩個名字都給的方式重現(紀錄檔尾)。舊碼本來就對、只是缺測試的條目,用改壞實驗證明測試守得住(修後程式改壞一處、跑對應測試、還原;18 處全紅,其中「ps 不比對 pid」第一次沒紅,補斷言後紅)。

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| C1 | major | 舊碼紅:中斷落在等日誌跟上 → 日誌串流變孤兒、原始日誌留著;改壞紅:日誌先從待收清單拿掉再停 | HIT | 折:停完才從待收清單刪;t_android_memstab_collect_interrupt_windows |
| C2 | minor | 舊碼紅:串流一開就斷 → logcat.raw 留著 | HIT | 折:同 I1 |
| C3 | minor | 舊碼紅:同一個 run-id 重跑沒擋;改壞紅 | HIT | 折:run-id 已經有結果檔就回 2;t_android_memstab_collect_edges |
| R1 | major | 跨行引句錨不到;機械重現:假 java_heap_dump 底下的程序握著管線 30 秒、逾時 2 秒,44d93aba 63.1 秒、修後 6.3 秒;改壞紅:只有驅動自成群組時 26.2 秒 | HIT | 折:每個子程序都自成程序群組、逾時整組殺,殺完收屍也有上限;t_android_memstab_collect_interrupt_windows |
| R2 | major | 同 C1 | HIT | 折:同 C1 |
| R3 | major | 舊碼紅:中斷落在停錄製之前(ps 慢)→ 沒送 kill -TERM;改壞紅:錄製先拿掉再停 | HIT | 折:同 C1(錄製也停完才刪) |
| R4 | minor | 跨行引句錨不到;內容同 I1,舊碼紅 | HIT | 折:同 I1 |
| B1 | minor | 舊碼紅:unreachable 的 before 是清單 → Traceback;改壞紅 | HIT | 折:跟 heap 同一條形狀檢查;t_android_memstab_unreadable_never_passes |
| B2 | minor | 舊碼紅:violations 元素不是物件 → 列成通過;type 不是字串 → Traceback;exits 的 new 元素不是物件 → 通過;改壞各紅 | HIT | 折:元素不是 {type: 字串} 就跳過;t_android_memstab_unreadable_never_passes |
| B3 | minor | 舊碼紅:結果檔 cycles 10**400 → 不跳過;設定 cycles 10**18、warmup 10001 → 合格;改壞各紅 | HIT | 折:warmup、cycles 與結果檔 cycles 限 1 到 10000;t_android_memstab_unreadable_never_passes、t_android_memstab_check_fields_strict |
| B4 | minor | 舊碼紅:有 --stability 沒有 check 條目 → 只印沒接 Macrobenchmark;改壞紅 | HIT | 折:印出記憶體與穩定性沒有東西可判;t_android_memstab_unreadable_never_passes |
| I1 | major | 舊碼紅:串流斷了、SIGTERM、中斷落在兩個空窗時 logcat.raw 都留著;改壞紅(斷線那路、中斷那路各一) | HIT | 折:strictmode_result 用 finally 刪、cleanup 也刪;t_android_memstab_collect_logcat_scope、t_android_memstab_collect_cleanup |
| I2 | minor | 讀計劃:S18 人驗說明還寫「呼叫行」 | HIT | 折:改成「呼叫它的 App 函式」 |
| I3 | minor | 讀計劃與腳本:流程段寫其餘回 0,腳本另有六種回 2;步驟沒寫先停 App | HIT | 折:流程段列出全部回 2 的情況、補先停 App 再讀結束紀錄;腳本檔頭回傳碼同步 |
| I4 | minor | 舊碼紅:沒有 macrobench.json 時 --update-baseline 說成沒有 results_dirs | HIT | 折:沒有設定檔時改說沒有設定檔,計劃那句改成實際訊息;t_android_memstab_unreadable_never_passes |
| I5 | minor | 讀計劃:收據段說快照驗得到,又說快照只記錄不比對 | HIT | 折:改成快照那兩條只記錄、不比對,由 lumos 判定 |
| I6 | minor | 讀 skill:7 天後才會被刪、保留清單漏 record.pbtxt | HIT | 折:改成下一次跑收集腳本時才刪、不再跑不刪;保留清單補 record.pbtxt,寫明 logcat.raw 一律刪 |
| I7 | minor | 讀 skill:frozen 走 L1 時沒有逐輪 Trace 與基準 Trace | HIT | 折:L1 加一條從穩定性收集過來的走法(用 cycle.pftrace、不做 A/B、gaps 記沒有基準) |
| I8 | minor | 讀驗收紀錄:沒釘版本,修補後實機沒重跑 | HIT | 折:valid_under 寫明驗的是功能提交 1e47929e 那一版、之後的修補只用假工具驗過;加 REVISIT:2026-11-07 用實驗室重跑 |
| I9 | minor | 讀測試:沒有 Big5 語系時那段不出聲 | HIT | 折:不跑時印一行略過說明 |
| G1 | minor | 改壞紅:類別數前後對調(補不同類別數的案例後) | HIT | 折:t_android_memstab_collect_never_fakes_ok 改用前後不同的類別數 |
| G2 | minor | 改壞紅:perfetto_alive 不比對 pid(補「看原因是到了上限、不是停不下來」的斷言後才紅) | HIT | 折:假 adb 加 ps_no_grep;t_android_memstab_collect_edges |
| G3 | minor | 讀碼:測試的 git 沒隔離全域設定 | HIT | 折:假工具環境加 GIT_CONFIG_GLOBAL=os.devnull、GIT_CONFIG_NOSYSTEM=1,git init 也用它 |
| G4 | minor | 讀碼:text=True 沒人關、註解秒數錯 | HIT | 折:丟掉文字輸出的 7 處呼叫改 text=False;註解改成 40 案約 50 秒 |
| A1 | minor | 讀碼:範本依賴 lumos 本體 | HIT | 折:收集腳本家節點那條 WHY 補代價(範本層第一次依賴 lumos;scripts/lumos 不在時跑不了) |
| A2 | minor | 實測:腳本沒有版本檢查 | HIT | 折:exec 之前先確認 python3 是 3.11 以上,不是就回 2 印擋下;寫進 -P 那條 WHY(沒有 3.10 以下的直譯器可測,沒寫測試) |
| A3 | minor | 讀碼:三個環境變數用 _S 尾碼、檔頭沒列 | HIT | 折:改名 LUMOS_STABILITY_SETTLE、LUMOS_STABILITY_STOP_TIMEOUT、LUMOS_STABILITY_LONG_TIMEOUT,檔頭與 reference.md 都列出 |
| A4 | minor | 讀碼:達標也逐條印只有 frozen、exits | HIT | 折:macrobenchmark-adapter 寫成 WHY;t_android_memstab_exits 補達標逐條印的斷言(改壞紅) |
| A5 | minor | 讀碼:找工具兩道 | HIT | 折:收集腳本家節點寫成 WHY(前一道碰裝置前擋、後一道接驅動指令裡的程式) |
| X1 | major | 同 I1 | HIT | 折:同 I1 |
| X2 | major | 舊碼紅:.gitignore 只寫 *.json → 照常寫出;改壞紅 | HIT | 折:七種會寫出的檔名各問一次 git check-ignore,列出沒被忽略的;t_android_memstab_collect_edges |
| X3 | minor | 舊碼紅:原因含換行 → 多出一行;改壞紅 | HIT | 折:文字輸出過既有 _esc_clean;t_android_memstab_unreadable_never_passes |
| X4 | minor | 舊碼紅:PYTHONPATH 指到 shutil.py → 被載入;改壞紅 | HIT | 折:exec 前 env -u PYTHONPATH;t_android_memstab_collect_edges |
| Y1 | major | 同 I1 | HIT | 折:同 I1 |
| Y2 | minor | 實測:範例照抄 --check-config 回 0 | HIT | 折:範例的裁定人與日期改成佔位(照抄會被擋、填了才過,兩種都跑過),加一句要先問人 |
| Y3 | minor | 讀碼:java_heap_dump 被殺時裝置暫存可能留著(沒有實機可驗) | HIT(只讀碼) | 折:reference.md 寫明會留在哪、收集腳本只清自己的、要自己看過再刪 |

## 同族掃描

- 交接空窗(C1、R2、R3):收集腳本裡從 state 拿出來再做事的只有日誌串流與錄製兩處,都改成做完才刪;driver 與快照不經 state(run 自己的例外處理會整組殺)。
- 原始日誌(C2、R4、I1、X1、Y1):寫 logcat.raw 的只有 start_logcat,刪的地方收成 drop_raw 一支,正常、斷線、中斷三條路都走到;測試三條路各一個斷言。
- 逾時後等待(R1):所有子程序改走同一條 run,沒有例外(logcat 串流不經 run,cleanup 與 stop_logcat 各自收)。
- 讀不到不准當成沒事(B1、B2、B3):七種檢查逐一再看一次清單與數字欄位,unreachable、violations、exits.new、cycles 補齊;heap、pids、cycle_trace 上一輪已補。
- 新告警:這輪修正一度帶進一條 C901(清理測試太長),拆成 t_android_memstab_collect_interrupt_windows;推前比主線版兩支檔都沒有新增告警。

## 修補因果

上一輪修補是 1e47929e 到 9c67b337(程式、測試、文件)與 44d93aba(只加卷證)。逐條判:

| id | 歸因 | 證據 |
|---|---|---|
| R1 | 有證據的修復回歸 | 1e47929e 用 subprocess.run(逾時只 kill 加 wait、不讀管線),9c67b337 改成 Popen 加 communicate,逾時後那次 communicate 沒上限:資源席同一案例修前 12.0 秒、修後 52.2 秒;編排者對 44d93aba 重現 63.1 秒 |
| B3 | 有證據的修復回歸(結果檔那半) | 1e47929e 用 _ms_val(超大整數經 _macrobench_num 判不是有限數 → 跳過),9c67b337 改用 _secev_int(收超大整數)→ java_growth 判成通過;邊界席兩版同一份結果檔各跑一次。設定檔沒上限那半是原有漏查 |
| I3 | 有證據的修復回歸(文件) | 擋下類回傳碼(git 忽略檢查、run-id 只有點、SIGTERM)是 9c67b337 加的,計劃那句「其餘情況都寫出結果檔並回 0」沒跟著改;1e47929e 沒有 check-ignore |
| C1、R2、R3 | 有證據的原有漏查 | 1e47929e 整條中斷路徑都沒收(rc -15、孤兒、沒送 TERM),9c67b337 加了收尾但先 pop 後停留了空窗;兩版同一案例都留孤兒或沒送 TERM,行為沒有變差 |
| C2、R4、I1、X1、Y1 | 有證據的原有漏查 | 1e47929e 整份日誌寫進 logcat.txt(正常與異常路徑都留),9c67b337 正常路徑只留違規行、異常路徑留 logcat.raw;兩版異常路徑都留原始日誌 |
| X2、X4 | 有證據的原有漏查 | 1e47929e 沒有 git 忽略檢查與 -P;9c67b337 加的守衛範圍不夠,兩版同一案例都放行 |
| 其餘 | 有證據的原有漏查或未判定 | 見各席報告的歸因欄;兩版行為相同或是新文件、新測試 |

--regression-set R1,B3,I3。
