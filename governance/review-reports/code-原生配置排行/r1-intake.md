# 第一輪收貨

七席(正確性、資源、邊界、整合、通才、架構對齊、資安,都是 sonnet 的新代理)報告到齊後一次寫入;七份都已是正規化格式;quote-check 六份全數錨定、通才席是乾淨報告沒有引句;refcheck 全 ok;審查席沒動 repo(git status 只有編排者自己的卷證與治理帳)。材料拆三包:正式程式 r1-snapshot-prod.patch(820 行)給正確性、資源、邊界、通才、架構對齊;測試與文件 r1-snapshot-tests.patch(1172 行)給整合;資安席照規定看整份 r1-snapshot.patch(1992 行)。manifest 原始 3602 條幾乎都是 scripts/lumos 的舊告警,只留落在這次新增行上的 15 條(r1-manifest-diff.json),各席都判誤報。

## 發現編號

正確性 c1–c3、資源 z1–z3、邊界 b1–b4、整合 g1–g6、架構對齊 a1–a4、資安 s1(順序照各席報告的條目),另加編排者自己跑既有測試抓到的 o1,共 22 條。

## 重現表

| ID | 重現 | 結果 |
|---|---|---|
| b1 | 新測試 t_android_native_lumos_print 加函式名與呼叫者各 500 字的一列,在修正前的程式上跑:那一行看不到「還留著 5.0 MiB」 | HIT |
| b2、c1 | 同一支測試加 retained=10**400 的一列,修正前文字輸出 OverflowError | HIT |
| b3、c3 | t_android_native_query_caller 加「ERROR 2 在呼叫位置上面」與「ERROR 3 跟 bar 並列」兩條鏈,修正前呼叫者分別是 ERROR 2 與 ERROR 3 | HIT |
| b4 | t_android_native_budget_values 帶 nan、inf、0、-5,修正前照跑不擋 | HIT |
| g1 | 把 NATIVE_MIN_SDK 改成 31,修正前的測試照綠;補 sdk 30 照跑的案例後同一個改壞翻紅 | HIT |
| g2 | 把預估的 2 倍改成 1 倍,修正前的測試照綠;補 t_android_native_budget_rule(上限 420/419 卡線)後翻紅 | HIT |
| g3 | 把 e2e 範本傳上限那行改成 pass,修正前的測試照綠;補 t_android_native_e2e_passes_budget 後翻紅 | HIT |
| g4 | 席位在修正前的程式量到正常跑完會多送一次 kill -TERM;修正後例外處理改寫,正常路徑不再有人收那個槽,拿掉 del state["rec"] 沒有可觀測的後果,加了「恰好兩次 TERM」的斷言當回歸守衛 | HIT(現象成立、修正後不復存在) |
| g5 | t_android_native_templates_present 刪掉任一支新範本,修正前回 0、第二段才 FileNotFoundError | HIT |
| g6 | 讀程式:讀不到第二段結束紀錄、第一段 pid 讀不到、第二段 pid 兩次都讀不到這三條分支沒有測試;把各分支改壞,補的案例都翻紅;筆記正文與兩支測試的文件字串寫「兩支」、驗收計劃〈資料怎麼流〉沒有第二段 | HIT |
| c2 | 讀程式:讀不到第二段結束紀錄判 failed,規格沒有這條 | HIT |
| z1 | 讀程式:預估拿含快照與掃描的整段第一段乘三 | HIT |
| z2 | 讀程式:預估過了之後,第二段每次驅動與查詢的上限仍是 T_LONG(1800 秒),會跑過 e2e 單步上限、整步被 TERM;補的整段測試(上限 200 秒、第二段暖機睡 30 秒)在修正前會等滿 | HIT |
| z3 | 讀程式:device_dirty 只有中斷路徑讀 | HIT |
| a1–a4 | 讀程式:對照 file:line 成立 | HIT |
| s1 | 讀程式:--json 的 sites 字串只過 _macrobench_stab_scrub(控制字元),自然語言照原樣 | HIT |
| o1 | 編排者跑 -k android_e2e:t_android_e2e_preflight_stability_tools 紅,收集腳本有兩行讀 stability.test_data | HIT |

## 根因分組與處置

- 組 A 印出那一行把三段文字與數字一起截、用 float 算(b1、b2、c1、a1):函式名、.so 名、呼叫者各自過 _events_clean 各截 200、120、200 字,大小接在後面、用整數算 MiB;形狀不對改成 failed、原因「結果檔形狀不對:…」、照沒跑成那一行印,拿掉靠字串開頭分辨的 MACROBENCH_NATIVE_BAD。→ 折。
- 組 B 呼叫者沒排除回溯失敗的偽框架(b3、c3):呼叫位置往上第一個不在 libart.so 的框架是 ERROR 偽框架時記「?」;並列時有名字的排在「?」前面。計劃〈排行怎麼算〉第 1、2 條一起改。→ 折。
- 組 C 時間上限(b4、z2、g2、g3):上限值不是大於 0 的有限秒數就開跑前擋下;預估過了之後,第二段每次驅動與查詢的上限不超過「開跑時間加這一步上限、扣 180 秒」剩下的時間(driver、tp_rows、native_query 多一個 timeout 參數,預設 T_LONG);補卡線、設定值、e2e 傳遞與整段截止四支測試。→ 折。
- 組 D 版本界線沒測(g1):補 sdk 30 照跑。→ 折。
- 組 E 第二段讀不到結束紀錄與 pid(c2、g6 的分支部分):保留保守的 failed(判不出第二段期間 App 有沒有結束,寧可不採用),寫進計劃第 3 步與 S7;補三條分支的測試。→ 折。
- 組 F 例外處理的路徑(z3、a2、g4):意外例外時先從 state 拿出錄製收掉、再寫 failed 附例外類型與訊息前 200 字,收不掉就在原因後面照實寫;Terminated 不在這裡收,錄製留在 state 交給 main 的 cleanup(跟中斷在第一段時同一條路),拿掉 device_dirty 旗標與 cleanup 的那處改動。→ 折。
- 組 G 範本缺失(g5):打開時開跑前查兩支新範本在不在,少了就擋下點名。新增 S29。→ 折。
- 組 H 第二段重抄一份啟動流程(a4):抽 fresh_launch(停 App、讀結束紀錄、啟動、等、讀 pid),第一段與第二段共用;第二段的順序因此改成跟第一段一樣先讀結束紀錄再啟動,計劃第 3 步一起改。→ 折。
- 組 I 讀 test_data 兩處(o1):native_skip 改收 preflight 讀好的值,收集腳本只剩一處讀 stability.test_data。→ 折。
- 組 J 文件(g6 的文件部分):筆記正文與兩支測試的文件字串改成三支查詢;驗收計劃〈資料怎麼流〉第 1、2、3、5 步補 native_retained;skill L0 通過時把排行前幾名照抄進收據提醒(不往下);e2e 筆記那行改綁 t_android_native_e2e_passes_budget。→ 折。
- z1 預估把第一段的快照與掃描也算進去:放行。規格(設計審 r4)刻意取保守的預估,多擋只會讓只提醒的排行這次不跑、印出原因;改成只量驅動的秒數要另外計時,收益只有慢機器上多跑一次提醒。
- a3 文字欄用 hex、既有查詢用逗號重接:放行。設計審 r4 本機實測 trace_processor 的 csv 不跳脫引號與換行,重接救不回;三支查詢共用 tp_rows 一套切法,hex 只在新查詢的 SQL 裡,不是第二套解析。
- s1 --json 的外來函式名沒擋自然語言:放行。工具鏈的威脅模型是單人自用、外來文字回顯放行(控制字元與分行字元已由 _macrobench_stab_scrub 清掉、文字輸出再過 _events_clean);被量 App 的符號名本來就要原樣給人看才找得到呼叫位置。

折 19 條,放行 3 條(z1、a3、s1,都是原報 minor,記帳帶逐條來源)。

## 修補因果

第一輪,沒有上一輪的修補。

## 修完自查

- 新測試在修正前的程式上:針對缺陷的(呼叫者、印出、形狀、例外、預算、範本缺失、o1)都翻紅;補覆蓋面的(sdk 30、預算係數、e2e 傳遞、正常路徑 TERM 次數、三條分支)在修正前本來就綠,各自把程式改壞一處都翻紅(兩處第一次沒紅:pid 兩次都讀不到與主流程的截止時間,補案例後翻紅;拿掉 del state["rec"] 照綠,修正後沒有可觀測後果,見重現表 g4)。
- 效能:查詢範本由資源、正確性、通才三席各自用合成資料量過(216 萬個 callsite 約 36 秒、尖峰約 550 MB,近線性);這輪改的只有呼叫者的一個條件與排序鍵,沒有新的連接。
