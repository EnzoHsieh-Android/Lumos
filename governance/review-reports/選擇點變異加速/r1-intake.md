# 選擇點變異加速 r1 收貨

preflight-4: ran

## 前掃(派工前,便宜代理照固定清單掃;①②③與存在類命中直接修真檔、不算 findings)

- ① 未定義的詞:「下限」補成既有逾時下限環境變數 LUMOS_KILL_TIMEOUT_FLOOR(預設 20 秒);「測試任務」補判準(任務名最後一段等於 test,或以 test 開頭、UnitTest 結尾;既有 _gradle_test_module 不認 testDebugUnitTest,另寫判斷)。
- ② 壞引用:無;S12 綁的是既有測試,補註「擴充既有測試」。
- ③ 範圍矛盾,已修:判讀順序(逾時→編不過→被系統收掉→結果資料夾→乾淨才採信,前三種不檢查資料夾);預期效益表第一、二列每個壞法的分鐘數錯位;merged/fallback 歸類(編不過與被收掉算 merged、--no-merge 兩欄 0);PRIOR-ART ④ 與做法不一致(程序登記用 _KILL_RUN_LIVE、某份當掉其他份照跑的理由);S9 第三案註明「基準已綠、在壞法那次被收掉」;人裁紀錄寫明 --jobs 1 不傳 baseline_share、合併預設開會改變不帶參數的跑法。
- 額外風險(前掃順帶指出):多份跑超過一天時清殘骸可能清到別份的工作樹 → 做法 2 加「清殘骸跳過 _KILL_WT_LIVE 登記中的路徑」。

## 前掃語意類命中(修改前→後)

| # | 位置 | 修改前 | 修改後 | 程式實際 |
|---|---|---|---|---|
| 1 | 〈白話〉 | 每個壞法要把 64 支綁定測試一支一支各叫一次 Gradle,每次呼叫還要重量一次基準 | 每個壞法要把 64 支綁定測試一支一支各叫一次 Gradle(基準每支測試只量一次,但每次叫 Gradle 都要付啟動與設定的固定成本) | cmd_guard_kill 的 baselines 字典每條測試指令在一次呼叫、每個平台組內只量一次 |
| 2 | 〈實測〉 | 快取在那一次呼叫裡 | 快取在那一次呼叫的每個平台組裡 | baselines 建在每個平台組的隔離工作樹內 |

兩條都沒動到核心裁定,不升級成正式 finding。

## 收貨(6 席,全 sonnet,全新代理)

席位:正確性、邊界、整合、資源、回滾、架構對齊。材料 r1-snapshot.md(180 行,spec_commit b59878ca)。六份收齊後才一次從逐字稿存檔;收齊前沒動被審計劃。report-normalize 六份都已合格;quote-check 六份全錨定;refcheck 全對得上。

發現編號:正確性 c1–c8、邊界 b1–b10、整合 i1–i13、資源 rs1–rs8、回滾 rb1–rb8、架構對齊 a1–a5,共 52 條;原報 major 14 條(c1、b1 b2 b3 b4、i1 i2 i3、rs1 rs2、rb1 rb2 rb3、a1)。

## 重現表

| 組 | 成員 | 編排者重現 | 處置 |
|---|---|---|---|
| 平行相關(縮範圍) | rs1 rs2 rs3 rs6 rs7 rs8 i6 i8 i9 i12 a3 a4 b1 b2 b8 b10 c8 rb6 rb7 | HIT(讀碼:rs2 cmd_guard_kill 工作樹失敗走 _kill_err_all 交 error 列不丟例外;b1 floor 可得 0) | 折:使用者 2026-11-23 裁「這份只做合併,平行另開」;平行全部移出本計劃,發現逐條轉入 Projects/選擇點變異平行_計劃(todo) |
| 讀結果檔另寫一套 | a1 | HIT(scripts/test_quality.py 有 junit() 加固讀法,_secev_junit_facts 註明沿用) | 折:改用 test_quality.junit() 逐檔讀,拒收即退回逐支 |
| 退回逐支的基準在壞法上量 | i1 b3 | HIT(讀碼:cmd_guard_kill 基準在套壞法前量) | 折:退回時先還原、在乾淨樹量缺的單支基準、重套再跑 |
| 掛住成本 | c2 rs4 i5 | HIT(算術:5 倍合併基準含冷編譯) | 折:合併基準連跑兩次,逾時用第二次熱耗時 ×5;預期效益計入掛住成本 |
| 合併基準沒查每支跑到 | i2 c7 | HIT(讀計劃) | 折:每支要對到恰好一個完整名,沒對到的照現在量單支 |
| 合併前沒過名稱檢查 | b4 i4 | HIT(讀碼:_test_name_ok、_name_collision_reason 在逐支路徑) | 折:合併前先過兩道,沒過照現在記 error |
| 測試前失敗永久關合併、判讀條件 | c1 c5 rs5 c6 i13 | HIT(讀碼:_KILL_COMPILE_RE 只認 Kotlin 編譯) | 折:結果位置由合併基準證明,單一壞法找不到只退它;編不過三條件都要;補測試行程被收掉的字樣(待實測) |
| 判法通道與計數 | i3 b7 rb2 | HIT(讀碼:列欄位固定、choice-kill 收起標準輸出) | 折:列與帳加 judged(merged/single/fallback),提示印標準錯誤,計數式改三類相加 |
| 誤記殺掉無法撤回、抽查做不到、回退開關 | rb1 rb3 rb5 rb8 | HIT(讀碼:_choice_kill_pick 對 killed 不重挑) | 折:帳加 merge_ver(判法版本低於工具即作廢重跑)、--recheck、LUMOS_CHOICE_NO_MERGE;--no-merge 等同現在的條款;回退照帳本實際流向重寫 |
| 判定時機 | c3 | HIT(讀碼:on_row 第一個決定性列即判) | 折:合併模式等該壞法所有列到齊才判 |
| 對名與升級 | b6 i13 | HIT(讀計劃) | 折:完整名規則($、參數尾巴);弱證據只在完整名唯一對到時升級 |
| 指令改寫與長度 | b5 i7 a2 b9 | HIT(實測 _gradle_task_list 只回任務名) | 折:shlex 切與組、新判斷函式 _gradle_unit_test_task、超過長度上限不合併;拿掉 500 支分批 |
| 文件與落點 | i10 i11 a5 | HIT(讀碼:_gov_row ck 白名單無 ran) | 折:ran 進白名單、RETIRE-IF 改讀得到的欄位、落點與上線時要改的既有句子寫明 |
| 測試互相影響記錯人 | c4 | 讀計劃成立 | 放行:合併基準擋不住壞法造成的互相影響,寫成已知限制,S18 抽查是唯一把關;要根治得每支各起一行程,等於放棄合併 |
| 放行檔蓋過帳 | rb4 | 讀碼成立(既有行為) | 放行:既有行為;--recheck 不蓋放行檔,撤放行照現有改放行檔,寫進實務隱患 |

52 條:折 50、放行 2;沒有重現不到的。

## 先查世界

- PRIOR-ART:PIT 只跑覆蓋到被改那一行的測試、多開執行緒(https://pitest.org/faq/);Gradle 一次帶多個 --tests 都生效、JUnit XML 每類別一檔(https://docs.gradle.org/current/userguide/java_testing.html);採用合併呼叫。
- PRIOR-ART:PIT 增量分析在「類別與殺掉它的測試沒變」時沿用上次殺掉的結果,並明說依賴改變的影響是未證明的假設(https://pitest.org/quickstart/incremental_analysis);本案的帳同樣以行指紋與殺掉它的測試沿用,另加判法版本 merge_ver 讓讀法修正後舊的合併判定作廢——這是本案自訂,PIT 頁面沒寫版本作廢。
- PRIOR-ART:Google〈Practical Mutation Testing at Scale〉以測試目標(多支測試)為執行單位(https://arxiv.org/pdf/2102.11378);支持合併。
- 第 1 輪,不查方向。
