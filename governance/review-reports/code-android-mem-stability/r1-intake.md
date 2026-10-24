preflight-4: ran

# code-android-mem-stability r1 收貨

審材:r1-snapshot-code.patch(程式,1052 行)與 r1-snapshot-tests-docs.patch(測試與文件,1298 行),從功能提交 1e47929e 對主線 7d17bd73 凍結;超過 1800 行所以拆兩包。
七席:正確性、資源、邊界、整合、通才、架構對齊、資安(都是 sonnet)。七席都交回後才一起存檔與處理。
id 前綴:C 正確性、R 資源、B 邊界、I 整合、G 通才、A 架構對齊、X 資安;編號照各席報告的順序。
引句:quote-check 對兩包合併的凍結材料跑,六席全錨;資安席第 1 條引句錨不到(見下表),其餘全錨。seat-check:派工單沒列材料清單,vacuous。
記帳:--spec 與 --reviewed 每席都填兩包原樣接起來的 r1-snapshot.patch(同輪指紋要一致),--snapshot 與 --scope-lines 填該席審的那一包;各席用量與耗時在對話壓縮後對不回是哪一席,不填(選填欄)。

## 機械重現(總表)

做法:把被審的提交 1e47929e 的 scripts/ 整份解到暫存目錄,換上修正後的 scripts/test_lumos.py,跑 `python3.14 scripts/test_lumos.py -k memstab`。結果 222 過、41 條斷言紅,全文存在 r1-repro-old-code.log。下表「舊碼紅」指那份紀錄裡紅的斷言;「改壞紅」指舊碼本來就對、只是缺測試的條目,改用「把修正後的程式改壞一處、看新測試會不會紅」證明測試守得住(每次只改一處、跑完還原)。

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| C1 | major | 舊碼紅:崩潰後沒被重啟(第三次讀不到 pid、驅動也失敗)→ exits 沒過 | HIT | 折:exits 有崩潰類紀錄時不依賴 pid 照判;t_android_memstab_unreadable_never_passes |
| C2 | major | 舊碼紅:驅動輸出 INSTRUMENTATION_FAILED / INSTRUMENTATION_ABORTED / 短格式 RESULT 而回 0 → driver ok | HIT | 折:輸出有任何 INSTRUMENTATION_ 行就要看到 CODE -1 且沒有 FAILURES!!!;t_android_memstab_collect_never_fakes_ok |
| C3 | major | 舊碼紅:快照查詢一列都沒有 → heap 仍是 ok;java_growth 兩份快照都是空的 → 不跳過 | HIT | 折:空快照記 failed、正常時帶 classes_seen,判定端沒有它就跳過;t_android_memstab_collect_never_fakes_ok、t_android_memstab_unreadable_never_passes |
| C4 | minor | 舊碼紅:類別物件尖括號裡的混淆名沒還原 | HIT | 折:deobfuscate 連 java.lang.Class<…> 一起還原;t_android_memstab_collect_edges |
| C5 | minor | 舊碼紅:exits 缺 new 欄、strictmode 缺 violations 欄 → 不跳過 | HIT | 折:每種來源欄位缺或型別錯一律跳過附原因;t_android_memstab_unreadable_never_passes |
| C6 | minor | 舊碼紅:category 是清單或物件 → Traceback | HIT | 折:category 必須是字串,否則回 2;t_android_memstab_check_fields_strict |
| B1 | major | 同 C3(舊碼紅) | HIT | 折:同 C3 |
| B2 | major | 同 C1(舊碼紅) | HIT | 折:同 C1 |
| B3 | major | 舊碼紅:frozen 設了阻塞上限但阻塞量不到(-1)→ 不跳過 | HIT | 折:設了 max_block_ms 卻量不到就跳過附原因;t_android_memstab_unreadable_never_passes |
| B4 | minor | 同 C6(舊碼紅) | HIT | 折:同 C6 |
| B5 | minor | 舊碼紅:max_byte、max_block 拼錯 → 設定檢查照樣合格 | HIT | 折:check 條目有不認得的欄位回 2;t_android_memstab_check_fields_strict |
| B6 | minor | 舊碼紅:exits 的 new 是 null、pids 的 values 是巢狀清單 → Traceback | HIT | 折:同 C5 的統一規則;t_android_memstab_unreadable_never_passes |
| B7 | minor | 舊碼紅:run-id 是 . 或 .. 不擋;max_record_s 超大或不到 1 秒照樣合格 | HIT | 折:run-id 不能只有點、max_record_s 限 1 到 86400;t_android_memstab_check_fields_strict |
| B8 | minor | 舊碼紅:有 mapping 時類別物件的混淆名沒還原,宣告類別沒實例就被當成名字拼錯 | HIT | 折:同 C4 |
| R1 | major | 舊碼紅:SIGTERM 時沒停裝置錄製、沒刪裝置暫存、日誌串流與驅動變孤兒 | HIT | 折:收到 SIGTERM 先停錄製刪暫存、整組收掉子程序;t_android_memstab_collect_cleanup |
| R2 | minor | 改壞紅:把逾時那支的整組殺換回只殺最外層,新測試量到要 32.3 秒才結束(底下的程序握著輸出管線) | HIT | 折:驅動自成程序群組,逾時與中斷都整組殺;t_android_memstab_collect_cleanup(長逾時可用環境變數縮短,只給測試用) |
| R3 | minor | 實驗室真追蹤檔量測:峰值子查詢 73.8 秒 | HIT | 折:改用 LEAD 算區間,同一份追蹤檔 0.26 秒、結果相同;t_android_memstab_cycle_query |
| R4 | minor | 舊碼紅:錄製收到 TERM 不停 → 沒補 KILL、追蹤檔照記 ok | HIT | 折:等滿 STOP_WAIT 還在就 KILL 並記 failed,刪檔放 finally;t_android_memstab_collect_cleanup |
| G1 | major | 舊碼紅:日誌串流一開就斷 → strictmode 照記 ok | HIT | 折:關串流前確認還活著,一開就斷記 failed;t_android_memstab_collect_never_fakes_ok |
| G2 | major | 改壞紅:拿掉 -T 量測開始時間,新測試 2 條紅 | HIT | 折:假 adb 依 -T 過濾、放一筆更早的違規並斷言不計入;t_android_memstab_collect_logcat_scope |
| G3 | major | 改壞紅:拿掉產物目錄捷徑守衛,新測試紅 | HIT | 折:補測試;t_android_memstab_collect_edges |
| G4 | minor | 改壞紅:app 最高一級 4.25 改 4.5,新測試 2 條紅 | HIT | 折:每一級、含上界都對「剛好等於過、多 1 KB 沒過」;改成直接呼叫判定函式(28 秒降到約 1 秒),命令列路徑由 t_android_memstab_peak_vitals_floor 走;t_android_memstab_vitals_every_tier |
| G5 | minor | 讀碼:迴圈裡 max_main_block_ms 那條被 continue 掉 | HIT | 折:刪掉死條目,阻塞量不到的情境改在 t_android_memstab_unreadable_never_passes 測 |
| G6 | minor | 改壞紅:結束紀錄只看 pid,新測試紅 | HIT | 折:補同一個 pid、不同時間的案例;t_android_memstab_collect_edges |
| G7 | minor | 讀碼:假 adb 的 ps 不看 pid | HIT | 折:假 adb 的 ps 依 pid 過濾;t_android_memstab_collect_edges |
| G8 | minor | 讀碼:收集腳本兩段固定睡兩秒、每案多跑一次文字輸出 | HIT | 折:睡眠秒數可用環境變數縮短(測試 0.1 秒)、文字輸出按需才跑;一次收集現在約 2 秒。這輪新增 7 支測試,子集約 3 分鐘(全套切 4 片跑,攤到每片) |
| G9 | minor | 讀碼:JAVA_HEAD_DUMP 拼錯、為了拿假工具目錄先跑一次完整收集 | HIT | 折:拼字改正;兩處改成只備環境不跑收集(_ms_prepare 補預設值) |
| I1 | major | 同 C1(舊碼紅) | HIT | 折:同 C1 |
| I2 | major | 實驗室收據:App 那層只到函式 PlayerActivity.onCreate | HIT | 折:計劃 S18、驗收紀錄、skill L3 第 3 步改成「App 哪個函式」 |
| I3 | major | 舊碼紅:沒給 mapping 時結果檔沒標明、文字輸出也沒標明類別名未還原 | HIT | 折:heap.class_names 記 raw / mapping,java_growth 輸出標明;t_android_memstab_collect_edges、t_android_memstab_java_growth |
| I4 | minor | 讀計劃:S7 收集那半綁的是只測 lumos 端的測試 | HIT | 折:新條款 S22 綁 t_android_memstab_collect_logcat_scope |
| I5 | minor | 同 G4 | HIT | 折:新條款 S26 綁 t_android_memstab_vitals_every_tier |
| I6 | minor | 讀碼與計劃:S16 寫法與實作不同 | HIT | 折:計劃改寫驅動成功的判法(有 INSTRUMENTATION_ 行才看 CODE),新條款 S21 |
| I7 | minor | 讀計劃:S15 寫「不是帶署名與日期的 true」,實作是格式錯回 2 | HIT | 折:S15 改寫 |
| I8 | minor | 讀文件:家節點 results_dirs 必填、統計化計劃說五條、驗收紀錄四條人驗、排除清單寫法 | HIT | 折:四處都改;家節點 updated 改 2026-10-24 |
| I9 | minor | 讀文件:逐層診斷表格沒寫 L0 直接到 L3、WHY 沒指例外、S6/S9 佐證早於新寫法、沒授權時沒說怎麼辦 | HIT | 折:表格與 WHY 補上;S6/S9 註明當時驗的是舊寫法;沒宣告時停在 L0 記 [GAP] L3 未授權(逐層診斷計劃與 skill 都寫) |
| I10 | minor | 讀文件:run 目錄沒有「結束紀錄」檔、peak_vitals → L3 計劃沒寫、保留規則、Python 版本、run-id 字元、門檻範例 | HIT | 折:skill 改指 exits.new 與 logcat.txt;計劃補 peak_vitals 進 L3;reference.md 補版本、run-id、gitignore、保留規則與門檻 JSON 範例(範例用 --check-config 跑過合格) |
| I11 | minor | 見下方「重現不到」 | MISS | 列進 refuted-set |
| A1 | minor | 讀碼:範本叫 lumos --check-config、另讀門檻檔的 class | HIT | 折:收集腳本家節點寫成 WHY(只用公開子命令與回傳碼、門檻檔只在 lumos 驗過後讀 instances 的 class;不選完全不碰 lumos 的理由) |
| A2 | minor | 讀碼:新函式前綴 _ms_ | HIT | 折:改名成 _macrobench_stab_(只在 scripts/lumos 內部用,42 處) |
| A3 | minor | 實測:LC_ALL=zh_TW.BIG5 時 `python3 -I` 的 utf8_mode 是 0、輸出編碼 big5,`-P` 是 1、utf-8;C 語系下兩者都是 1 | HIT | 折:改用 -P(同時擋專案目錄的同名模組);改壞紅:-P 換回 -I,新測試 Big5 那條紅(機器沒有 Big5 語系時那段不跑);t_android_memstab_collect_edges |
| A4 | minor | 實測:在沒有 .lumos/macrobench.json 的目錄跑收集腳本 → 回 2 擋下 | HIT | 折:家節點寫成 WHY(收集腳本留在 scripts/templates 原地跑、使用方式是在專案根跑;不選從腳本位置往上推的理由) |
| A5 | major | 讀碼:_macrobench_date_ok 自寫 regex 加 fromisoformat,門檻函式另有一份行內版 | HIT | 折:改成 DATE_RE 加既有 _rule_date,行內版改呼叫它 |
| A6 | minor | 讀碼:整數驗證自寫 isinstance | HIT | 折:改用既有 _secev_int |
| X1 | major | 引句錨不到(引句與凍結材料差在 pid 讀不到那段的寫法);內容同 C1,舊碼紅 | HIT | 折:同 C1 |
| X2 | major | 舊碼紅:沒宣告 strictmode 照開日誌串流、落地日誌留全文;git repo 裡產物目錄沒被忽略照樣寫 | HIT | 折:只在宣告時開、只收這個 pid 與量測之後、落地只留違規行;開跑前查 gitignore;t_android_memstab_collect_logcat_scope、t_android_memstab_collect_edges |

## 重現不到

| id | 席位說的 | 怎麼試的 | 結果 |
|---|---|---|---|
| I11 | 表態記錄寫的是待決問題解析、受測場次(指到 scripts/scenario_probe.py),不是這次改動 | 在這個工作樹跑 `lumos pitfalls --diff 7d17bd73..HEAD --dispositions-template --carry`:記下的表態是 sql-nplus1、infra-signal、infra-timeout 這些,證據都指到 android-stability-collect.sh。席位看到的表態是派工時掛鉤從會談目錄(Backend_improve,另一個分支)帶進來的 | MISS:這個分支的表態對得上這次改動,席位看到的是派工工具帶錯分支 |

## 同族掃描

- 讀不到不准當成沒事(C1、C3、C5、B1–B3、B6、X1):整理成一條統一規則寫在 _macrobench_stab_skip_reason,七種 check 都走它;每種來源缺欄、型別錯、空的、量不到各一個案例。
- 子程序收尾(R1、R2、R4):中斷、逾時、錄製停不下來三條路都整組殺,各一條測試。
- 不會造假的 ok(C2、C3、G1):驅動、快照、日誌三種來源都檢查「真的拿到東西」才記 ok。
- 新告警:這輪修正一度帶進一條 C901 與 11 條 F401/RUF003/RUF059,推前比主線版逐條清掉,現在兩支檔都沒有新增告警。

## 修補因果

r1 是首輪,沒有上一輪修補,regression_set 不適用。
