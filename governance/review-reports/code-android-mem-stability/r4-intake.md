preflight-4: ran

# code-android-mem-stability r4 收貨

這輪是前三輪跑滿上限後人裁破例加的一輪(2026-10-24 Enzo,cap-decision extra-round,跑滿回顧已記)。
審材:對主線 7d17bd73 到 5fc4e715 的完整改動,切四包(r4-pkg-lumos.patch 659 行、r4-pkg-templates.patch 645 行、r4-pkg-tests.patch 1245 行、r4-pkg-docs.patch 754 行),每包配同一批檔從修前 f0d41453 到修後 5fc4e715 的修補差異。測試那包加修補差異超過 1800 行,通才席改以 r4-repair-tests.patch(720 行)當引句來源、需要時讀工作樹的完整函式;測試整包由測試資安席完整讀過。架構對齊與程式資安看程式整包 r4-snapshot-code.patch(1304 行)。三席資安合起來涵蓋全部改到的檔。
九席:正確性、資源、邊界、整合、通才、架構對齊、程式-資安、測試-資安、文件-資安(都是 sonnet),都交回後才一起存檔;席報告從各席對話紀錄取最後一則回答原文。
id 前綴:C 正確性、R 資源、B 邊界、I 整合、G 通才、A 架構對齊、X 程式-資安、T 測試-資安、Y 文件-資安;編號照 report-normalize --items 列的序號(邊界席的 F1/F3/F4/F5 依序記成 B1 到 B4)。
引句:八席全錨;通才席第 5 條引句取自完整測試檔而不是它那一包修補差異,錨不到,內容機械重現 HIT(見下)。三份報告格式不合記帳工具,請該席自己只改那一行重出,存成 -格式更正.md(原檔保留):邊界席把「這不是缺陷」那段的 F2 編號拿掉(第 31 行)、通才席檔級從 minor 改 major(第 1 行)、測試資安席「- 嚴重度:」改「- 影響評估:」(第 16 行)。
人裁(2026-10-24 Enzo,這輪交回後):「修完 major 就收」——major 全折、便宜的 minor 一起折,剩下不划算的 minor 逐條指回原報放行(--finding-source),記成 cap-decision accept-risk、補跑滿回顧,不再派第五輪。

## 機械重現(總表)

做法:把被審的提交 5fc4e715 的 scripts/ 解到暫存目錄,換上修正後的測試檔,跑 `-k memstab`,存在 r4-repro-old-code.log(367 過、12 紅);只缺測試的條目用改壞實驗(15 處,檔尾)。

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| C1 | major | 舊碼紅:ps 連三次失敗加錄製已到上限 → cycle_trace 照記 ok | HIT | 折:ps 失敗連問三次,還是不知道就停錄製但追蹤檔不採用;t_android_memstab_collect_record_alive |
| C2 | minor | 讀碼加席位兩版實跑:最後一次確認剛好 ps 失敗 → 好檔被補 KILL | HIT | 折:同 C1(每次存活判斷都連問三次) |
| C3 | minor | 舊碼紅:裝置離線時失敗原因看不出 device offline | HIT | 折:不帶標準輸出,留回傳碼與標準錯誤最後一行;t_android_memstab_collect_never_fakes_ok |
| R1 | minor | 席位實跑:兩個不同訊號同一毫秒到 → 收尾被打斷 | HIT | 折:訊號處理本身先把所有中斷設成忽略再丟例外;改壞實驗見檔尾 |
| R2 | minor | 舊碼紅:收尾期間沒有任何提示 | HIT | 折:收尾開始印「收尾中、最久約 4 分鐘、按 Ctrl-C 沒有用」;t_android_memstab_collect_signals |
| R3 | minor | 讀碼:unreachable 整份輸出進記憶體 | HIT | 放行:要改成串流讀、改動大;只有洩漏極大的 App 才會到數百 MB,實驗室與一般 App 的傾印遠小於此 |
| R4 | minor | 舊碼紅:錄製回報失敗時沒補送停止 | HIT | 折:失敗分支也 pkill;t_android_memstab_collect_record_alive |
| B1 | minor | 舊碼紅:全形角括號、中間換行的佔位放行 | HIT | 折:佔位判法加全形與跨行(只寫一邊角括號的不擋:合法人名可能含 <,機器分不出);t_android_memstab_check_fields_strict |
| B2 | minor | 舊碼紅:負數跳過原因寫「是 -1」 | HIT | 折:三處原因改成「負數(-1 是量不到)」;t_android_memstab_unreadable_never_passes |
| B3 | minor | 席位實跑:scenario 含 tab 時清洗後對不上 | HIT | 放行:真實情境名與機型名不含控制字元;清洗是為了擋孤立代理字元讓 --json 崩,兩害取輕 |
| B4 | minor | 席位實跑:門檻檔字串含孤立代理字元時 --json 崩 | HIT | 放行:門檻檔是人寫的,要手寫 \ud800 這種跳脫才會出現,在單人、AI 依序操作、只用中英文的威脅模型外 |
| I1 | major | 席位改壞實驗:S23 綁的五支測試守不到 ps 失敗那句 | HIT | 折:S23 加綁 t_android_memstab_collect_record_alive |
| I2 | minor | 讀碼:事故筆記的函式名不對、省略了 marker_only | HIT | 折:改成 _dispatch_lens_graph 與 marker_only=True |
| I3 | minor | 讀計劃:設計正文只寫 SIGTERM 與 Ctrl-C、第 5 點沒寫 test_data 門 | HIT | 折:兩處都補 |
| I4 | minor | 讀 skill:L0 第 8 步與限制句沒寫 value 要是 true | HIT | 折:兩處改成 value 是 true 才往下、沒寫或 false 都不錄 |
| I5 | minor | 讀計劃:逐層診斷 S6 的人驗證據沒涵蓋 L0 停下那條 | HIT | 折:逐層診斷計劃加 REVISIT:2026-11-07 實驗室拿掉 test_data 跑一次 |
| I6 | minor | 讀驗收紀錄:有效範圍沒涵蓋 r3、r4 的裝置端新指令 | HIT | 折:valid_under 寫明到 r4 只用假工具驗、列出 pkill 與 ps;REVISIT 加實機確認這兩項 |
| I7 | minor | 讀計劃:驗收門檻計劃 S5 沒記舊條目也擋佔位 | HIT | 折:S5 補一句並指到 S25 的測試 |
| G1 | major | 改壞實驗:訊號處理與收尾兩處的忽略都拿掉 → 收尾中再按 Ctrl-C 那兩條紅(補測試前沒有任何測試送 SIGINT) | HIT | 折:t_android_memstab_collect_signals 加 Ctrl-C 第一次中斷、收尾中再按一次 Ctrl-C |
| G2 | minor | 讀碼:ps 失敗那條的前置斷言在沒注入故障時也成立 | HIT | 折:假 adb 失敗時留標記,前置斷言看標記;改壞(ps 不重問)紅 |
| G3 | minor | 讀碼:假 ps 的誘餌跟 4321 沒有重疊 | HIT | 折:誘餌加 43210、perfetto4321;改壞(pid in line)紅 |
| G4 | minor | 讀碼:XDG 隔離沒有測試 | HIT | 折:t_android_memstab_collect_edges 造帶 ~/.config/git/ignore 的 HOME;改壞(拿掉 XDG)紅 |
| G5 | minor | 讀碼:ps_no_grep 案例與 record_dies_early 重複、假 ps 的 grep 分支是死碼 | HIT | 折:刪掉旗標與死碼,那段改成驗誘餌 |
| G6 | minor | 讀碼:等待的回傳值被丟掉、清理測試手寫收孤兒 | HIT | 折:每個等待都包成前置斷言;清理測試改用 _ms_orphans |
| A1 | minor | 讀碼:pbtxt 的 __DURATION_MS__ 用程式替換卻用 __ 寫法 | HIT | 放行:同一批範本(SQL 的 __PROCESS__)都用 __ 寫法,收據也照這個寫法貼;只改 pbtxt 一處反而是第二種寫法 |
| A2 | minor | 讀碼:stability_unjudged 只在觸發時出現 | HIT | 折:結果一開始就放這一欄(值 null);t_android_memstab_unreadable_never_passes |
| A3 | major | 讀碼:kill_group 與 _kill_proc_group 同功能、少了退路 | HIT | 折:補上沒有 killpg 時只殺這一個的退路;收集腳本家節點那條 WHY 寫明拿不到 lumos 的函式、兩份各自維護的代價(POSIX 上 killpg 一定在,退路分支測不到) |
| X1 | minor | 舊碼紅:git 回 128(safe.directory)時當成不是 repo、照寫產物 | HIT | 折:128 而且不是「不是 git repo」就回 2;t_android_memstab_collect_edges |
| X2 | minor | 舊碼紅:原因含 U+2028 時印出來多出一行 | HIT | 折:印出改用既有的 _events_clean(連分行字元一起清);t_android_memstab_unreadable_never_passes |
| X3 | minor | 舊碼紅:裝置刪不到暫存時訊息照說已刪 | HIT | 折:abort_record 回傳裝置有沒有回應,訊息照實寫;t_android_memstab_collect_signals |
| T1 | minor | 讀碼:sleep 30 的命令列不帶假工具目錄 | HIT | 折:sleeper 改成自己睡的 python,命令列一直帶假工具目錄 |
| Y1 | minor | 讀 skill:heap_profile 的 -o 沒限定位置 | HIT | 折:L3 第 1 步改成放在產物目錄底下、寫明 7 天自動刪不管它 |
| Y2 | minor | 同 I4 | HIT | 折:同 I4 |
| Y3 | minor | 實測:拿掉角括號的假名字照過 | HIT | 折:reference.md 改成「只擋得住原樣照抄的佔位,真正的防線是先問人」 |

## 同族掃描

- 錄製存活判斷:perfetto_alive 的三個呼叫點(停之前、等待迴圈、最後確認)都改走連問三次;回 None 的意義在 stop_record 一處決定。
- 中斷:SIGTERM、SIGHUP、SIGQUIT、SIGINT 四種都在訊號處理本身先忽略後續中斷,收尾開頭再設一次(等價、保險);四種都有測試。
- 失敗原因帶輸出:這輪把 unreachable 的標準錯誤留回來;其他工具的失敗原因照留尾巴,印出時一律過 _events_clean。
- 佔位:門檻條目兩種寫法與 test_data 共用一支 _macrobench_signed_err。

## 修補因果

上一輪修補是 f0d41453 到 98cd9d8d(程式、測試、文件)與 5fc4e715(修正紀錄、跑滿回顧與帳本)。

| id | 歸因 | 證據 |
|---|---|---|
| C1、C2 | 有證據的修復回歸 | 98cd9d8d 把 ps 失敗改成回 None 並當成還在跑;正確性席同一案例 f0d41453 標提早結束、5fc4e715 照收截斷的追蹤檔或丟好檔 |
| C3 | 有證據的修復回歸 | 98cd9d8d 拿掉輸出尾巴時連標準錯誤一起拿掉;同一案例 f0d41453 看得到 device offline,5fc4e715 只剩回傳碼 |
| B2、B3 | 有證據的修復回歸 | 98cd9d8d 新加負數判法沒改原因文字、新加的清洗改變了含控制字元的身分字串;邊界席兩版各跑一次 |
| I1、I2、I4 | 有證據的修復回歸(文件) | 98cd9d8d 新寫的 S23 句子沒綁測試、函式名改錯、skill 兩處條件寫法不一 |
| G3、G5 | 有證據的修復回歸(測試) | 98cd9d8d 把 grep 搬到主機端,假 ps 的誘餌沒跟著補、留下死碼 |
| A2 | 有證據的修復回歸 | 98cd9d8d 新加的欄位只在觸發時出現 |
| 其餘 | 有證據的原有漏查或未判定 | 見各席報告的歸因欄 |

--regression-set C1,C2,C3,B2,B3,I1,I2,I4,G3,G5,A2。
