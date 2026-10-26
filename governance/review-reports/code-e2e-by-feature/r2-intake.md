# code-e2e-by-feature r2 收貨紀錄

七席全交回(2026-10-26),git reflog 核過席位沒動 repo(HEAD 仍在 787dd51b)。引句:六席對自己的審材全數錨定;合約席兩句引的是程式碼(不在它的文件包),對完整快照 r2-snapshot.patch 全數錨定,記帳以完整快照為比對對象。

編號:正確性 C1–C7、資源 R1–R3、邊界 B1–B5、合約 K1–K8、通才 G1–G2、資安 S1–S3、架構 A1–A2,共 30 條,blocking 7 條(C1 C2 C3 C4 K1 G1 G2;K2 標 major 但席位寫 blocking 否,照 major 處理、一律折)。

## 修補因果(regression)

上一輪修補造成、有兩版證據的:C1(沒有會判項目時三處矛盾,修後才出現)、C2 G1 K1 S1(方法名收 $,修前擋、修後跑成別支)、G2(保留規則把真失敗蓋掉,修前無條件覆蓋)、S2(LUMOS_E2E_COLLECT 修後才有)、R3(整套多跑每個情境,修補刻意的代價)、K2(S28 整套各判一次是修補新增、沒有測試守住)。

原有漏查(兩版行為相同):C4 C5 C6 C7 R1 R2 B1 B3 B4 S3 A1 A2 K3 K5 K6;C3 裡判讀時髒、HEAD 換了兩處是原有,保留規則那處未判定。未判定:B5 K4 K7 K8。

## 根因分組與重現

重現方式:新測試放進修補前的版本(787dd51b 的乾淨副本,換上修後測試檔)跑;另對修後版本故意改壞判讀時的工作目錄檢查與 HEAD 檢查各一次。結果見本檔末尾。

| 組 | 編號 | 重現 | 去向 |
|---|---|---|---|
| 方法名收 $ 被 sh 展開 | C2 G1 K1 B2 S1 | HIT:四席各自在修後跑出 Outer#test | 折:兩邊規則都不收 $,設定檢查就擋 |
| 沒有會判項目時整次結果矛盾 | C1 | HIT:修後 rc 0、總表 pass、feature_runs unjudged | 折:整次結果跟著最差的情境;原因文字照實寫略過了哪塊 |
| 保留規則把真失敗蓋掉、重判舊的蓋掉新的 | G2 C6 | HIT:修後 --no-perf 真失敗被舊 pass 蓋掉 | 折:_e2e_keep_old:沒過一律蓋;只有沒判完或不完整但通過才留;既有那筆更晚結束也留 |
| 紀錄前提、分岔點、整套各判一次沒有測試 | C3 C4 K2 | HIT:席位改壞後全綠 | 折:t_android_e2e_feature_record_rules、t_android_e2e_changed_edges、t_android_e2e_full_scenarios_judged |
| --changed 邊角 | R2 B1 B4 B5 R1 | HIT:git 讀不到當沒改動、未提交改名漏舊路徑、混合命中不提醒、--case 被連累、清單內重複 | 折:讀不到就擋;diff HEAD --no-renames;.maestro 與驗收設定列進提醒;指名的照跑;清單內去重 |
| 設定檢查 | B3 C5 | HIT:app//src、. 照收;macrobench_cmd 是數字時噴錯誤堆疊 | 折:paths 要正規寫法;macrobench_cmd 要是字串 |
| 環境變數殘留 | S2 S3 | HIT:讀碼;S3 席位兩版實測 | 折:用了替身收集腳本整套與按功能都不寫紀錄;stability 段本身拿掉殘留的情境變數 |
| 總表 | C7 A2 | HIT:history --case 列別的情境的失敗;路徑寫兩次 | 折:按功能跑另記 case_results、照情境篩只列自己的;路徑常數 E2E_HISTORY_REL |
| 整套跑時間與磁碟倍增 | R3 | HIT:修補刻意的行為 | 折:README 與 skill 寫明每個情境各留一份錄製、不自動清 |
| 文件 | K3 K4 K5 K6 K7 K8 | HIT:讀文件對照程式 | 折:README 路徑與小節名、手冊與系統筆記回傳碼、圖產生器筆記、計劃三處、{{TEST}} 只跑列到的方法與 history 預設 20 筆 |
| 分派函式 | A1 | HIT:guard 分派的說明寫只有它例外 | 折:那段說明加列 _android_e2e_dispatch |

沒有機械重現不到的條目(refuted 為 none)。同輪有 major,minor 全折、沒有放行。

## 重現結果

- 修補前 787dd51b 換上修後測試檔跑 -k android_e2e:345 過、14 紅,紅的全在這輪新加或改的斷言(方法名 $、paths 正規、macrobench_cmd 字串、沒有會判項目回 1、共用 flow 提醒、--case 加 --changed、清單內重複、讀 git 失敗、沒過一律蓋掉、重判舊的不蓋新的、替身收集腳本、殘留情境變數、history 按情境)。
- 修後版本拿掉判讀時的 _e2e_precheck:t_android_e2e_feature_record_rules 紅 2 條(判讀時髒、HEAD 換了)。
- 修後版本拿掉 start_head == head:同一支紅 1 條(HEAD 換了)。
