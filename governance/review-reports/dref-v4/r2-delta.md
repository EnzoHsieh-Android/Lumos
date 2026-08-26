# dref-v4 r2 delta 席(r1 折入回歸)
sha256 已核對 = 238201a331ce10f5d985adae790682965e4cad5f82ea4f34a7156291b7147df1。

### d-f1
severity: major
引句:「★不重查迴圈★。這樣兩種振盪在批次內都不成立」
佐證:file: `governance/review-reports/dref-v4/r2-snapshot.md:116`
說明:「單次單趟」宣稱關掉兩種振盪,但通篇無機械擋——backlog 是無狀態查詢,無批次 id/快照鎖/「這節點這趟看過」記號。真正擋振盪的只有「Claude 不在同批再查 backlog」的協議紀律。spec 誠實標「重跑 backlog 明列 future」但只涵蓋「刻意週期重跑」,沒涵蓋「session 中斷/換視窗/人手動又敲 backlog 意外重查」——系統無法區分,因無東西記錄原始名單。259 節點回填大機率跨 session,非邊角。欠一句誠實話:單次單趟純靠協議紀律撐、無機械擋,中途換 session 重起手=觸發 spec 自己說要另設計的重跑情境。

### d-f2
severity: major
引句:「兩欄都移(消假清除)。冪等 no-op rc=0」
佐證:file: `governance/review-reports/dref-v4/r2-snapshot.md:124`;file: `scripts/lumos:8802`
說明:V1-V4 每處明講正規化 tuple 比對,V5 prune 卻沒提比對方式,且「移不存在→no-op rc=0」跟「移成功」同 rc、外表無別。庫唯一先例 _append_decision_ref 是逐字。最自然字面實作=prune 拿 ref 跟欄位逐字比,對不上當「本來不在」靜默回成功。若人照 candidates/promote 印的正規形輸入、欄位存的是 T1 confirm 簡寫(--from 只驗格式不驗正規),prune 回報「已沒了」其實原封不動留著——人以為剪掉、其實沒剪,下輪 candidates 正規化去重反把它濾掉不再提醒。正規化世界 vs exact-string 世界在刪除路徑打架,無一句點出。

### d-f3
severity: major
引句:「該節點指向的翻案決策中、無正欄 ref 命中的」
佐證:file: `scripts/lumos:1236`;file: `scripts/lumos:1272-1277`;file: `scripts/lumos:318`
說明:r1 s3-f1(blocker)折入修補,但掃描來源沒講清,字面最自然做法(套候選函式)兩處錯。輕的:candidates 用 verified_by/plan_refs/related,E2 typed_in(1236)只 verified_by/plan_refs 排除 related——覆蓋清單比 E2 實際抑制寬(偏安全多提醒)。危險的:E2 抑制(1272-1277)裡 did 空字串時 _hits 恆 False,只要 refs 非空一定 continue——無 id 翻案決策一旦節點 decision_refs 有任一筆(不管指哪)就無條件靜默壓掉。但 candidates 只列有 id、add-ai 因「id 真存在」驗證永遠加不進無 id 決策。若覆蓋提醒沿用候選邏輯,這批最危險(無條件被壓、T3 永遠補不了)的決策反被掃描完全漏掉——蓋章人看到乾淨清單,實際有一批更嚴重翻案落後邊已被靜默關告警且無補救。重開 s3-f1 一個子集且更難處理。spec 應明講掃描吃哪函式/哪些條件(尤其排不排 related、無 id 決策要不要單獨列成「連提醒都提不了」警訊)。

## 掃過但乾淨的面
- d-f4 s2-f3 正規化 tuple 方向正確、照抄 E2/E3 既有口徑。d-f5 add-ai 落盤逐字+外層正規化閘門兩層不衝突。d-f6 backlog/candidates 共用 build_typed_index。d-f7 巢狀 add_subparsers 照既有兩選一挑對。d-f8 五/六原語數徹底改乾淨。d-f9 promote count-check 對兩欄各自計數對齊 ext-f3、非退化「整欄空」。
- s2-f1 折 omitted_all_no_id;s1-f2 改正規化 tuple 兩種誤讀不成立;arch-f1 supersede 先例仍照走;s3-f2 minor 沒被錯誤宣稱已解;E3 聯集與不對稱信任雙欄未動;rc 0/2 一致無 rc=1。
