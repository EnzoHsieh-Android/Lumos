preflight-4: ran

# code-android-mem-stability r3 收貨

審材:對主線 7d17bd73 到 f0d41453 的完整改動,切四包(r3-pkg-lumos.patch 618 行、r3-pkg-templates.patch 632 行、r3-pkg-tests.patch 1086 行、r3-pkg-docs.patch 741 行),每包配同一批檔從修前 44d93aba 到修後 f0d41453 的修補差異(r3-repair-<包>.patch)。架構對齊與程式資安看程式整包 r3-snapshot-code.patch(1250 行);測試與文件整包 1827 行超過 1800,資安改成三席(程式、測試、文件各一包),合起來涵蓋全部改到的檔。
九席:正確性、資源、邊界、整合、通才、架構對齊、程式-資安、測試-資安、文件-資安(都是 sonnet)。九席都交回後才一起存檔;席報告從各席對話紀錄取最後一則回答原文。
id 前綴:C 正確性、R 資源、B 邊界、I 整合、G 通才、A 架構對齊、X 程式-資安、T 測試-資安、Y 文件-資安;編號照各席報告順序。
引句:quote-check 對各席自己那一包跑,九席全錨。架構對齊席的總結句寫了「請編排者裁是否升 major」,記帳工具把它當成總結句藏了比檔級高的等級;請該席自己只改那一行重出一份,存成 r3-架構對齊-sonnet-格式更正.md 當記帳用的報告(原檔保留,兩份只差第 82 行)。圖譜鏡頭照第二輪的做法由編排者在被審工作樹產出後貼進共同派工詞。
這輪是上限(3/3),有 major;人裁(2026-10-24 Enzo):破例加一輪,折完記帳後記 cap-decision、寫跑滿回顧,再派第四輪。
記帳:--spec 與 --reviewed 每席都填 r3-snapshot.patch(r3-snapshot-code.patch 接 r3-snapshot-tests-docs.patch),--snapshot 與 --scope-lines 填該席審的那一包;用量與耗時照各席完成通知。

## 機械重現(總表)

做法:把被審的提交 f0d41453 的 scripts/ 解到暫存目錄,換上修正後的 scripts/test_lumos.py,跑 `-k memstab`,存在 r3-repro-old-code.log。只缺測試的條目用改壞實驗(修後程式改壞一處、跑對應測試、還原),結果附在同一份紀錄檔尾。

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| C1 | minor | 讀碼加席位實跑:連按兩次 Ctrl-C,第二次落在收尾的裝置呼叫時 logcat.raw 留著 | HIT | 折:收尾一開始先忽略後面的中斷、最先刪原始日誌;t_android_memstab_collect_signals |
| C2 | minor | 舊碼紅:錄製開起來、pid 還沒回來時被中斷 → 沒有停錄製也沒刪裝置暫存 | HIT | 折:推設定之前先登記待收,pid 還沒回來時照追蹤檔名 pkill;日誌暫存檔也在開檔前登記;t_android_memstab_collect_start_window |
| C3 | minor | 舊碼紅:第一次 ps 失敗 → cycle_trace 記成提早結束 | HIT | 折:不在裝置上 grep,ps 失敗回不知道、當成還在跑;t_android_memstab_collect_record_alive |
| R1 | minor | 舊碼紅:SIGHUP、SIGQUIT → 直接結束、孤兒、原始日誌留著 | HIT | 折:SIGTERM、SIGHUP、SIGQUIT 都走收尾;t_android_memstab_collect_signals |
| R2 | minor | 舊碼紅:收尾中再收到 SIGTERM → traceback、裝置暫存與原始日誌留著 | HIT | 折:同 C1 |
| R3 | minor | 同 C2 | HIT | 折:同 C2 |
| R4 | minor | 讀碼:中斷訊息說暫存已收掉,主機上快照與追蹤檔還在 | HIT | 折:訊息改成照實寫:錄製已停、暫存與原始日誌已刪,run 目錄裡已錄到的快照與追蹤檔留著要自己刪 |
| B1 | minor | 舊碼紅:40 個類別增長、沒給 mapping → 截長後看不到警語 | HIT | 折:警語與類別數放在清單前面;strictmode 也先印筆數;t_android_memstab_unreadable_never_passes |
| B2 | minor | 舊碼紅:原因含孤立代理字元 → --json 印到 UTF-8 時崩 | HIT | 折:讀結果檔時先用既有 _events_depth_ok 限深、字串過既有 _esc_clean;t_android_memstab_unreadable_never_passes |
| B3 | minor | 舊碼紅:凍結幀 -5、unreachable 位元組負數 → 不跳過 | HIT | 折:數字欄位負數一律當量不到;t_android_memstab_unreadable_never_passes。classes_seen 跟前後兩份內容對不對照那個小點:結果檔只存有增減的類別,前後兩份的類別數本來就小於 classes_seen,對照不了,不改 |
| I1 | major | 舊碼紅:給了結果檔、門檻檔沒有 check 條目時 --json 沒有任何欄位 | HIT | 折:--json 帶 stability_unjudged,skill L0 遇到這欄記 GAP、不得記 L0 通過;t_android_memstab_unreadable_never_passes |
| I2 | minor | 讀計劃:S7 收集那半綁的測試只測 lumos 端 | HIT | 折:S7 加綁 t_android_memstab_collect_logcat_scope |
| I3 | minor | 讀測試:沒有 Big5 語系時那句驗不到 | HIT | 折:計劃加 REVISIT:2026-12-31 看 CI 有沒有這個語系,沒有就裝或改用不靠系統語系的方式 |
| I4 | minor | 實測:check 條目寫 device_model 合格,reference.md 說表格以外會回 2 | HIT | 折:reference.md 寫明每一種都另外可以寫 device_model |
| I5 | minor | 實測:decided_by 留佔位、只改日期 → --check-config 回 0 | HIT | 折:共用署名檢查擋 <…> 佔位(門檻條目兩種寫法與 test_data);t_android_memstab_check_fields_strict |
| I6 | minor | 讀計劃:逐層診斷 S6 停在 L2,記憶體類 check 走 L0 直達 L3;skill 寫「有宣告才做」 | HIT | 折:S6 改成停在當時那一層(從 L2 往下停在 L2、記憶體類停在 L0),沒寫或 value 是 false 都算沒授權;skill L3 標題改成 value 是 true 才做 |
| I7 | minor | 讀筆記:統計化計劃指向的 REVISIT 不在那篇 | HIT | 折:改指 Projects/Macrobenchmark退步提醒_計劃 與 Verification/2026-10-23_macrobench實機端到端 |
| G1 | major | 改壞紅:cycle_trace 欄位互換(補新測試後) | HIT | 折:新測試 t_android_memstab_collect_result_fields,期望值從假工具輸出另外算(7386728 // 1024 = 7213 等);新條款 S27 |
| G2 | major | 改壞紅:正常結束不刪原始日誌(補斷言後) | HIT | 折:t_android_memstab_collect_logcat_scope 正常路徑加 logcat.raw 不存在的斷言 |
| G3 | major | 改壞紅:擋下之前先碰裝置(補斷言後) | HIT | 折:run-id 不合法、run-id 用過、產物沒被忽略、只忽略 *.json、test_data 格式錯都斷言假 adb 沒被叫(用過那條比對前後呼叫次數);t_android_memstab_collect_edges、t_android_memstab_collect_test_data_gate、t_android_memstab_check_fields_strict |
| G4 | minor | 讀碼:清理測試只收最後一組孤兒 | HIT | 折:兩組都收;新拆的幾支用共用的 _ms_orphans 收 |
| G5 | minor | 席位實測:XDG_CONFIG_HOME 的全域 ignore 讓兩條誤紅 | HIT | 折:假工具環境另把 XDG_CONFIG_HOME 指到不存在的目錄,註解寫明擋得住的範圍 |
| G6 | minor | 讀碼:三支表格式測試每案多起一次 lumos | HIT | 折:java_growth、instance_limit、exits 的輔助預設不跑文字輸出,要看的案例才開 |
| G7 | minor | 同 I3 | HIT | 折:同 I3 |
| G8 | minor | 讀碼:"5" in rt.stdout 太鬆 | HIT | 折:斷言整句「com.sdk.Player 有 5 個(上限 1)」 |
| G9 | minor | 讀碼:多餘的 NaN 分支、_ms_collect 重抄參數、空窗迴圈的 marker 沒用到 | HIT | 折:拿掉 NaN 分支;_ms_collect 改成 **kw 轉給 _ms_prepare;等待與收孤兒抽成 _ms_wait_for、_ms_log、_ms_orphans,marker 改成 None 表示不用 |
| A1 | minor | 讀碼:範本叫 lumos、又自己讀設定檔 | HIT | 折:收集腳本家節點那條 WHY 補「驗過之後再讀的是 lumos 驗過的那份」 |
| A2 | minor | 讀碼:_macrobench_stability_* 與 _macrobench_stab_* 混用 | HIT | 折:三支改名成 _macrobench_stab_* |
| A3 | minor | 讀碼:常數定義在用到之後 | HIT | 折:分級表與輪數上限移到 _macrobench_stab_cfg_err 之前 |
| A4 | minor | 讀碼:decided_at、device_model 檢查寫兩份 | HIT | 折:抽成 _macrobench_signed_err,兩種門檻條目與 test_data 共用 |
| A5 | minor | 讀碼:另一套版本檢查(席位標判不準) | HIT | 折:維持 minor(範本拿不到 lumos 的函式,3.11 是 -P 的需求);收集腳本家節點寫成 WHY |
| A6 | minor | 讀碼:kill_group 與 _kill_proc_group 同功能(席位標判不準) | HIT | 折:同 A5,同一條 WHY |
| X1 | major | 舊碼紅:unreachable 讀不到總量那行時失敗原因帶傾印(假輸出裡的 Bearer、Authoriz 進了結果檔) | HIT | 折:這支失敗原因只寫回傳碼與固定說明;t_android_memstab_collect_never_fakes_ok |
| X2 | minor | 同 R1 | HIT | 折:同 R1 |
| X3 | minor | 席位實跑:類別名帶一般文字照原樣印 | HIT | 折:收集腳本家節點寫成 WHY(合法類別名可以是任何語言的字,只清控制字元;換行已清、偽造不出一行) |
| T1 | minor | 讀碼:清理控制字元只有 strictmode 原因那條有測試 | HIT | 折:加類別名帶換行走 [沒達驗收門檻] 那條的案例;t_android_memstab_unreadable_never_passes |
| Y1 | minor | 同 I5 | HIT | 折:同 I5 |

## 同族掃描

- 交接空窗:第二輪補了停的那兩個空窗,這輪補啟動的兩個(錄製、日誌),四個都在登記之後才做事;收尾自己被打斷(C1、R2)另外用「先忽略中斷、先刪本機檔」處理。
- 訊號:收集腳本會收到的中斷訊號是 SIGTERM、SIGINT、SIGHUP、SIGQUIT,四種都走收尾;其他訊號(SIGKILL)收不到,不處理。
- 失敗原因帶裝置輸出:收集腳本裡帶輸出尾巴的還有驅動、java_heap_dump、trace_processor、perfetto 四處,都是工具自己的錯誤訊息,不是 App 記憶體或日誌內容,照留(診斷用);只有 unreachable 的輸出本身是記憶體傾印。
- 讀不到不准當成沒事:負數(B3)補完後,七種檢查用到的數字欄位都走 _macrobench_stab_val。
- 新告警:這輪一度帶進兩條 C901 與一條 RUF059,拆函式與改名後兩支檔都沒有新增告警。

## 修補因果

上一輪修補是 44d93aba 到 8144207a(程式、測試、文件)與 f0d41453(只加修正紀錄與帳本)。

| id | 歸因 | 證據 |
|---|---|---|
| R1 | 有證據的修復回歸 | 8144207a 讓所有子程序 start_new_session,java_heap_dump 與 trace_processor 從此收不到終端機的 SIGHUP;資源席同一案例修前沒有孤兒、修後殘留 jhd 與 sleeper |
| B1 | 有證據的修復回歸 | 8144207a 在印出時加 _esc_clean(…, 500),警語接在清單最後被截掉;邊界席同一份結果檔修前看得到警語、修後看不到 |
| X1、I1、C2、C3、R2 | 有證據的原有漏查 | 兩版程式在這幾處逐字相同或行為相同(席位兩版對照或 git show 比對) |
| G1、G2、G3 | 有證據的原有漏查 | 修前的測試對這幾個欄位、這條路、這個時機就沒有斷言 |
| G5 | 未判定 | 修前完全沒隔離,修後隔離了 ~/.gitconfig 那種、沒隔離 XDG 那種;比修前好,不算回歸,但修補宣稱的範圍不完整 |
| 其餘 | 有證據的原有漏查或未判定 | 見各席報告的歸因欄 |

--regression-set R1,B1。
