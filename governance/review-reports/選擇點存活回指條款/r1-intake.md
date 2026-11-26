# 選擇點存活回指條款 r1 收貨

preflight-4: ran

## 首輪前掃(2026-11-26,sonnet 一席,只讀)

前掃命中:① 未定義 2、② 壞引用 3、③ 自相矛盾 5、④ 語意不符 3、部分符合 10。①②③ 與存在類直接修真檔;語意類修真檔並逐條記在下面(修改前 → 後);碰到核心裁定的兩條不自行改,升成正式發現交席位審。

### 語意類修改(前 → 後)

- ④1 覆蓋階段跑在哪:前「在同一個隔離工作樹的原版程式上跑」;程式裡判壞法的隔離工作樹由 `cmd_guard_kill` 建、返回時已收掉 → 後「覆蓋階段自己用 `_isolated_worktree` 從 HEAD 另建一棵樹」,S5 改成驗「不在使用者工作目錄跑」與「另建的樹不是原版就不跑」,預期值表 S5 拆兩列。
- ④2 choice-kill 存活列:前「choice-kill 結尾的存活列後面加一段」;choice-kill 的存活列是判壞法時逐個當場印、結尾只印統計 → 後「覆蓋階段跑完另印一份存活與分類清單」。
- ②2/④3 推送閘提示:前第 1 層 `situation-rule … --clause <條款>`、第 3 層範例帶 `--clause S3`;`--clause` 收新條款文字、`--test` 必填 → 後第 1、2 層範例補 `--test`、`--clause "<新條款文字>"`,第 3 層改成「補測試綁到那一條的 [test:]」、不用 situation-rule;預期值表 S9 改成「提示句含 `P#S3`」。
- ④4 換候選:前「照 `_choice_pick` 取下一個候選」;它只回第一個 → 後「加排除已試壞法身分的參數」。
- ④5 `{tests}`:前「照 `_choice_merge_cmd` 組多個 `--tests`」;那支吃 `{method}` 段並要求形狀 → 後「`run` 恰好一個 `{tests}`,代換成整串 ` --tests <名>`(含字面),名稱過 `_run_cmd_expand`、依名排序,不經 `_choice_merge_shape`」。
- ④6 中斷:前「第一個訊號照既有收法」;判壞法那段的訊號處理在覆蓋階段前已還原 → 後「覆蓋階段自己再包一層 `_situation_rule_signals`」,刪掉「已跑完的群照用」那句(反正這次不寫事件)。
- ④7 排序:前「依 choice-kill 的測試排序(同一個家的計劃優先)」;那份是每支被改檔一份 → 後「依計劃路徑、條款號排序」,預期值表 S1 第二列跟著改。
- ④8 條款群組:補「清單只收進行中計劃、kotlin-junit、已扣 manual 與 keeps」。
- ④9 讀帳:補「reach/layer 事件自帶 `token`」與「gov 讀取欄位白名單與型別表要補新欄位」。
- ④10 attempt 與上限:前「`attempt` 逐次加 1」「算進 `--max-mutants`」;`attempt` 是帳上累計筆數、`--max-mutants` 是跑前切行數 → 後「另加 `candidate` 欄位 1–3」「`--max-mutants` 只數行、換候選不另佔名額」,S17 與預期值表 S17 跟著改。
- ④11 材料取法:補 `_kt_sit_material` 的實際行為(可能是整個類別)。
- ④12 分份:註明 200KB 上限與減半再切是新寫(盲判只按段數分份)。
- ④14 常數:寫出 `_CHOICE_MERGE_FILE_MAX`(8 MiB)。

### 機械類直接修

- ①1 `reach_why` 補固定字串表(範圍 4),〈用詞〉覆蓋設定改用表裡的「沒設定覆蓋」。
- ①2 〈用詞〉補「對得上」:「現在」在 choice-points/choice-layer/choice-kill 讀被分析版本、推送閘讀 B 版。
- ②1 REVISIT 的事件名改成 gate choice-kill、kind reach 與 layer。
- ②3 Android 骨架「註解」改成 `_ANDROID_SKELETON_NOTE`(設定檔是 JSON)。
- ③2 判讀材料加附〈預期值表〉。
- ③3 「不改哪些存活要擋」改成「不改擋的判定規則」並承認換候選改變結果分布(〈白話〉與〈不做〉兩處)。
- ③4 PRIOR-ART 改成「只沿用材料形狀,記帳語意不沿用(這裡取最新一筆)」。
- ③5 `--reach-only` 與 `--no-reach`、`--only`、`--max-mutants`、`--no-merge` 同給 rc2。

### 升成正式發現、交席位審(前掃不改裁定)

- p1(③1)編不過的最終去向:〈白話〉與 WHY 寫「不留成跑不出結果」並把「記成跑不出結果」列為不選;範圍 11 卻在 3 個候選都編不過或沒有候選時記 `no_result`;〈用詞〉說「第 4 層只有編譯不過是工具自己判的」,但工具不寫層事件。要嘛工具寫第 4 層(無效壞法)事件,要嘛改 WHY 為「優先換候選、換光才記 no_result」。
- p2(④10 後半)換光候選的行每次重跑都再試同樣 3 個:`no_result` 下次一律重跑(choice-kill 既有規則),3 個都編不過的行在測試沒變時每次都白跑 3 次編譯。

## 席位收貨(2026-11-26,六席 sonnet)

六席(正確性、邊界、整合、資源、回滾、架構對齊)全部交回後一次存檔;正確性、資源兩席有引句錨不到、整合席等級行縮排,退回原席重交(只改引句與格式)。重交後六份都過 report-normalize 與 quote-check(全數錨定)。

編號:正確性 c1–c10、邊界 b1–b16、整合 i1–i17、資源 s1–s16、回滾 k1–k13、架構對齊 a1–a5,共 77 條;major 以上 45 條。全部折入(輪內有 major,minor 不放行)。前掃升上來的 p1、p2 由正確性席判成 c6、c10,一併折。

使用者 2026-11-26 對這一輪的裁定:「我不想對整個功能願景做偏離的妥協,所以如果有重大block,請你都做網路調研,找出可以兩全、或是更聰明的辦法」「不要懼怕改動,改動大沒有關係」「但是速度這件事,也是要保證好,不要又變回十幾個小時」。所以不縮範圍,改設計。

### 依根因分組與去向(全部折入改版計劃)

| 組 | 根因 | 發現 | 折法 |
|---|---|---|---|
| G1 | 覆蓋另開階段:另建樹、版本、時間預估、逾時、殘骸、中斷、聯集長度、報告大小、斷路 | b2 b3 b7 b11 b12 s1 s2 s3 s4 s5 s6 s7 s13 s14 c8 i7 i12 i15 s11 k10 b1 k1 | 拿掉獨立覆蓋階段;覆蓋掛在既有單支基準上(範圍 1),在 at_sha 的 lumos-kill- 隔離樹、同一套逾時與訊號;報告只產改到的類別、上限 32 MiB;斷路器;unknown 不算有效、會再補(範圍 7) |
| G2 | 覆蓋全 0 靜默誤判成 none | b4 | 〈用詞〉覆蓋可信要全模組行覆蓋 > 0;有一支不明其餘沒經過記 unknown;實測重現寫成 PITFALL |
| G3 | 判讀新鮮度鍵太粗、碰到的計劃集合會變 | c1 c5 b5 k13 i13 | 判讀只綁依據(範圍 9 有效表);覆蓋綁逐行 cov_sha |
| G4 | 引句驗證太弱、層驗證缺口 | c4 b6 s10 k5 i16 | 引句 10–200 實字、正規化、要落在標的條款或段;第 3 層排除 manual/keeps;plan 要是碰到的計劃 |
| G5 | 判讀記錯撤不回、鍵沒綁壞法、記錄與範圍脫節、分份位移、最新一筆的順序 | k2 k3 s9 b9 s16 k12 | --withdraw 補償事件、--redo;判讀記 new_sha;清單檔固定分份、記錄帶 --list;不合時逐筆印 |
| G6 | 事件大小與 gov 讀取 | i5 k4 k11 i4 k7 a4 | 判讀全文存檔、帳只記指紋與依據(≤4096);新 kind 自帶 token;(gate,kind) 白名單、欄位白名單與型別表補新 kind 與 candidate |
| G7 | 換候選接不上現有結構、統計失真、無限重跑、終態矛盾 | c2 c3 c6 c10 i2 i3 s8 s15 k6 k8 b10 b13 | 改成無效壞法記憶(範圍 4–6):invalid 事件、_choice_pick 的 skip 全路徑共用、同一次再跑一批不重量基準、exhausted 比照乾節點不擋且不重跑、編譯錯誤要指到被改檔;回退 3 保留 skip 讀帳 |
| G8 | 推送閘提示結構 | i6 i10 b16 c7 i11 | 存活拆子原因(範圍 11),行數加總不變;第 3 層不用 situation-rule;輸出截字與跳脫 |
| G9 | 設定讀不進來、多平台 | i1 a3 | coverage 穿過 load_platforms、單平台 test 節也讀、各平台各自;不再有 {tests} 佔位符(由 init script 處理) |
| G10 | 第二套 XML DTD 規則 | a1 c9 | 改用 test_quality.py 既有 NoDtdTreeBuilder,只先拿掉固定那一行 JaCoCo DOCTYPE;內文的 `[` 不受影響 |
| G11 | 材料大小、分份另一套 | b8 s12 a2 | 同一份計劃一份、正文過大時另存檔由材料指路;大小以 UTF-8 位元組計 |
| G12 | 讀者清單、文件落點、舊否決、條款對不上、回退漏文件端 | i9 i17 a5 i8 i14 b14 b15 k9 | _choice_ledger_aux 新讀者、其餘不動;現況落 Systems/規格閘,guard-kill 只一句;choice-layer 登記說明表與 INDEX;舊否決補母計劃「不接覆蓋率」與一行一個壞法;S12 註明只比那 20 行;package 用語法樹取;多筆 <line> 任一 >0;驗收條款補邊界 |

### 先查世界

PRIOR-ART: G1/G2 覆蓋怎麼取才不另開階段又夠快——PIT 先跑覆蓋階段記下每支測試經過的行,每個壞法只跑經過的測試(https://pitest.org/quickstart/basic_concepts );Google 差異式變異只對有覆蓋的行產生壞法(https://arxiv.org/pdf/2102.11378 );JaCoCo 維護者說逐測試分析成本與測試數成正比、要縮小類別(https://groups.google.com/g/jacoco/c/BGxeozd9ciI/m/X_Acj6rjAQAJ );JTeC(https://github.com/tum-i4/JTeC )與 Teamscale(https://docs.teamscale.com/howto/providing-testwise-coverage )做逐測試覆蓋,Teamscale 寫明並行跑分不出。採用:掛在本來就逐支跑的單支基準上。排除:同 JVM 監聽器逐支歸零(Android 單元測試是 JUnit4,Gradle 不能註冊全域 RunListener,GRADLE-2895 討論串;https://issues.gradle.org/browse/GRADLE-2895 )。
方向:要換 — 從「判完壞法後另跑覆蓋群組」換成「覆蓋階段在前、拿來選測試」,PIT 與 Google 都是這個順序(https://pitest.org/quickstart/basic_concepts 、https://arxiv.org/pdf/2102.11378 );使用者已裁「不偏離願景、速度要保證」,方向改動照使用者這句做。
實測(2026-11-26,實驗專案批 4a 複本):兩支測試(一支 Robolectric)各單獨跑並掛 JaCoCo,一次 Gradle 呼叫 5 秒產兩份報告:金額那支 Money.kt 8 行、分錄那支 EntryRepositoryImpl.kt 29 行;init script 在 afterEvaluate 設 includeNoLocationClasses 時分錄那支 0 行(重現 b4 的靜默全 0),改到 pluginManager.withPlugin('jacoco') 才生效;同一支 Robolectric 測試開關覆蓋各跑 3 次,4.7/4.6/4.7 秒對 6.1/6.1/6.3 秒。
PRIOR-ART: G3/G5 判讀有效期——建置系統的驗證追蹤:記下結果讀過的輸入,輸入沒變就不重算(Build Systems à la Carte,https://www.microsoft.com/en-us/research/uploads/prod/2018/03/build-systems-a-la-carte.pdf );只追加帳的更正用補償事件(https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing )。採用兩者。
方向:對 — 判讀是「依輸入算出的結果」,用驗證追蹤正是建置系統處理同一問題的形狀(上兩個來源)。
PRIOR-ART: G4 引句驗證——引句查核業界做法是正規化後(空白、引號)做子字串比對,找不到就判不可驗(https://aijourn.com/a-citation-verification-framework-for-llms-in-sensitive-domains/ );沒查到最短長度的公認值,沿用本工具放行理由的 10 實字門檻。
PRIOR-ART: G7 編不過的壞法——Google 論文 3.2.1 用規則事前擋;mutant schemata 把全部壞法編進一個程式只編一次(https://ar5iv.labs.arxiv.org/html/2210.17215 ),Android 有 METFORD 實證(https://arxiv.org/html/2501.02875v2 )。採用:無效壞法記憶(事前擋的帳上版);排除:schemata 這次不做(要改套壞法的方式),REVISIT 看量。
方向:對 — 把編不過當成「不是壞法」而不是「跑不出結果」,跟 Google 與 schemata 兩邊都一致(https://arxiv.org/pdf/2102.11378 、https://ar5iv.labs.arxiv.org/html/2210.17215 )。
PRIOR-ART: G10 XML 安全——本 repo 已有唯一的拒收 DTD 解析器(`scripts/test_quality.py` 的 NoDtdTreeBuilder),沿用,不另寫。
