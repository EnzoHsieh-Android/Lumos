# 選擇點存活回指條款 r2 收貨

- 派六席全新(正確性、邊界、整合、資源、回滾、架構對齊,sonnet),審 r2-snapshot.md(286 行,整份重寫後的第 2 版)。
- 六席全部交回後一次存檔;架構對齊席一句引句內又包「」被截斷,退回原席只改那句。六份都過 report-normalize 與 quote-check(全數錨定)。
- 編號:正確性 c1–c17、邊界 b1–b14、整合 i1–i11、資源 s1–s9、回滾 k1–k6、架構對齊 a1–a8,共 65 條;全部折入(輪內有 major)。
- 使用者這輪的方向同 r1:「不要懼怕改動,改動大沒有關係,我要的是完美符合願景,能實際幫上code review的功能」「但是速度這件事,也是要保證好」。

## 依根因分組與去向(全部折入第 3 版)

| 組 | 根因 | 發現 | 折法 |
|---|---|---|---|
| H1 | 覆蓋基準在另一棵樹、上層越過 guard-kill、基準快取鍵與不確定欄位、多平台 | c1 c2 s1 i3 a1 | 改成準備物件 `_KillPrep` 交給 `cmd_guard_kill`(形狀同 `_KillMerge`),在 guard-kill 那棵樹、合併快篩先量齊基準的同一處做;結果寫進 guard-kill 自己的快取與 mstate;每平台組一份 |
| H2 | 掛覆蓋才紅的測試讓壞法全中止 | s3 | 掛覆蓋紅就不掛重跑一次,綠就用那次、覆蓋算不明 |
| H3 | 覆蓋可信與「只收改到的類別」矛盾、斷路誤跳 | c3 b1 s4 | 改用「覆蓋資料裡專案類別有執行紀錄數 > 0」(實測:失效 0、正常 345);斷路少於 5 支時就是全部 |
| H4 | 有一支不明仍只交經過的測試、行內函式與常數、多行壞法 | c4 b2 c5 b3 c15 b14 | 有任一支不明就跑全部;〈用詞〉覆蓋例外(inline fun、const val、屬性初始值、沒有指令紀錄);經過看壞法改的行範圍 |
| H5 | 沒有測試經過的行從沒編譯過 | c6 i2 | 合批編譯檢查在測試前把全部壞法編一次、換掉編不過的 |
| H6 | 時間、中斷、續跑、批次建新樹、殘骸說法 | s2 s5 s6 s8 b6 | 合批編譯與覆蓋在同一棵暖樹、測試前完成,不再有第二批 guard-kill;每支前看剩餘時間、分析剩 30 秒以下不做;續跑快取同一個 at_sha 接著跑;呼叫帶當場收標記;拿掉殘骸那句(不再另建樹) |
| H7 | 判讀依據一變就消失、n² 重判 | c7 i1 | 依據變了標「待複核」照樣顯示,一批處置完再重判 |
| H8 | gov 第一次判定口徑、via cov 欄位與統計 | c8 i4 i8 k5 a2 | 照現在 `attempt == 1 and via == "run"`;via cov 另列一行;via cov 事件欄位寫明(judged cov、tests_sha、cov_sha);invalid 不是壞法事件、不佔 attempt |
| H9 | 判讀材料分組沒定義未歸計劃與跨計劃、單一存活超限、零存活、段名重名 | c9 b9 b13 | 依第一條經過條款的計劃分組、其餘放未歸計劃組;減到 1 個仍超限就正文另存;零存活印一行 rc0;段名用標題路徑、重名加序號、前言段 |
| H10 | exhausted 走不到、三個候選上限、無效記憶只綁單檔 blob | c10 b4 b10 c11 i7 | exhausted 改成挑壞法時的行狀態(同 arid),不進處置判定;合批編譯換到候選用完;無效記憶記 at_sha、每次 run 合批編譯都重新驗,skip 取最近一次 run 的 |
| H11 | 合併快篩跟子集 | c12 b7 | 子集用經過的測試組合併指令,合併基準仍是整組那條;子集合併有失敗就轉逐支確認 |
| H12 | reach 有效沒定義、cov_sha 沒讀者 | c13 b11 i9 | 〈範圍〉6 定義 reach 有效:cov_sha 相同且不是 unknown;帶過去規則讀 cov_sha |
| H13 | 報告與 XML(類別對應、多模組、DOCTYPE、大小、test_quality 載入、XML 第二套) | c14 c16 b8 b12 a7 s7 | 不產 XML:在 Gradle 程序裡用 JaCoCo 分析 API 讀覆蓋資料,只輸出壞法行;類別依套件資料夾挑再依 JaCoCo 記的原始檔名過濾;每個模組收類別資料夾;覆蓋資料檔用序號命名 |
| H14 | 事件大小與欄位型別 | b5 i10 k6 | reach_clauses 最多 20 條加 reach_more、超限照 `_gate_event_fit`;layer 只存 deps_sha 一個雜湊;每個新欄位寫型別;`LOOP_NOT_CLOSE_EVENTS` 一併分類 |
| H15 | 推送閘讀 B 版 aux 與判讀檔、簿記白名單 | i5 i6 k4 | `_choice_push_read` 多回傳 aux、判讀檔從 B 版樹讀、讀不到當沒有判讀;`governance/choice-layers/` 加進 `_BOOKKEEPING_DIRS`(同 reread-verdicts 先例) |
| H16 | 覆蓋判錯沒有發現與更正、via cov 回退回不去、回退互相矛盾 | k1 k2 k3 | 每次 run 抽查 2 行 none 照跑(殺掉就斷路並改記);via cov 存活只在開覆蓋且 cov_sha 相同時帶過去;回退重寫,保留 skip 那段的理由寫明 |
| H17 | 清單檔第三種做法、引句正規化第三套、init script 產法、設定形狀 | a5 a6 a4 a3 | 清單檔與續跑快取放 `_note_audit_work_dir` 同一套工作目錄規則;引句沿用 `_kt_sit_quote_norm`;init script 寫進 `wt.scratch`(同合併快篩);`coverage` 改成布林,型別不對照既有丟 ValueError |
| H18 | 文件與小錯 | a8 i11 c17 s9 | 規格閘 responsibility 補上;REVISIT 事件名改對;守衛面改引 S9、S10、S16;判讀狀態的雜湊一次呼叫內共用 |

## 先查世界

PRIOR-ART: H1/H6 覆蓋該在哪一層做才不冷編譯、不多建樹——合併快篩的既有做法就是 choice-kill 建 `_KillMerge` 交給 guard-kill,在 guard-kill 那棵樹先量齊單支基準(`scripts/lumos` 的 `_kill_merge_iter`);PIT 的覆蓋階段也跟壞法在同一個工作環境(https://pitest.org/quickstart/basic_concepts )。採用:準備物件同形狀。
方向:對 — 覆蓋在前、同一處先量齊,PIT(https://pitest.org/quickstart/basic_concepts )與本 repo 合併快篩都是這個位置;r2 的問題是「另一棵樹」與「上層越層」,不是方向。
PRIOR-ART: H3/H13 覆蓋怎麼讀才可信又快——JaCoCo 維護者建議逐測試分析、縮小類別(https://groups.google.com/g/jacoco/c/BGxeozd9ciI/m/X_Acj6rjAQAJ ),JaCoCo 有分析 API(https://www.jacoco.org/jacoco/trunk/doc/api/org/jacoco/agent/rt/IAgent.html 一帶的 org.jacoco.core)。實測 2026-11-26(實驗專案批 4a 複本):12 支測試逐支掛覆蓋後,一次 Gradle 呼叫在程序內用 JaCoCo 分析 API 讀完,整次 5.4 秒、分析 0.66 秒、166 個類別;同一支 Robolectric 測試在設定失效時專案類別有紀錄數 0、正確時 345;AGP 的覆蓋資料檔位置不吃 init script 的 destinationFile 也不吃 -D/-P(12 支都沒寫到指定路徑),要從固定位置複製。採用。
方向:對 — 逐測試分析是 JaCoCo 維護者給的做法(上連結),PIT 也是逐測試(https://pitest.org/quickstart/basic_concepts )。
PRIOR-ART: H5/H10 沒經過的行從沒編譯過——mutant schemata 把全部壞法放進一次編譯(https://ar5iv.labs.arxiv.org/html/2210.17215 ),Android 有 METFORD(https://arxiv.org/html/2501.02875v2 );Google 以規則事前擋(https://arxiv.org/pdf/2102.11378 3.2.1)。採用輕量版:全部壞法同時套上編一次、依錯誤行號對回;不採完整 schemata(要改成執行期開關)。
方向:對 — 先編譯再測試是 schemata 與 Google 的共同順序(上兩個來源)。
PRIOR-ART: H7 依據變了怎麼辦——建置系統的驗證追蹤只決定要不要重算(Build Systems à la Carte);這裡重算的成本是代理判讀,所以標「待複核」延後批次重算,同建置系統「先用舊結果、批次重建」的取捨。
PRIOR-ART: H16 覆蓋判錯怎麼發現——抽查是本工具既有的回退抽查做法(合併快篩的 `merged` 判存活回退與抽查,[[Projects/選擇點變異加速_計劃]]〈回退〉);照同一個形狀每次抽 2 行。

## 重現表

全部 65 條由編排者讀程式或對照實驗結果確認(HIT);無 MISS。
