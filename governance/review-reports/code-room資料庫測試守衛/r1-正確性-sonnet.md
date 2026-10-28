severity: major

## F1 DAO 的 mock 辨識漏掉常見寫法,只有 mock 的測試被當成真 Room 測試放行
severity: major
blocking: 是 判準:守衛宣稱要擋的錯(DAO 只用 mock 測)在常見寫法下照樣放行。

引句:「mock_re = re.compile(rf"mockk\s*<\s*{dao}\s*>|mockk\s*\(\s*{dao}\b|mock\s*\(\s*{dao}\s*(?:::|\.)class"」

1. 輸入:main 上有真 Room 測試和 `OrderDao.getAll`。分支新增 `OrderDao.getUnpaid`,唯一呼叫它的測試是 `src/test/.../RepoTest.kt`,內容為 `val dao: OrderDao = mockk(relaxed = true)` 加 `dao.getUnpaid()`。
2. 走到 `_rg_dao_need_tests`:`hits` 有 RepoTest,`mock_re` 對這一行不匹配,`not mock_re.search(...)` 為真,於是 `continue`,不記缺口。
3. 實測 rc=0。S24 的測試只用 `mockk<OrderDao>()` 這一種寫法,所以抓不到。
4. 另外實測三種寫法也都 rc=0:
   - `val dao = mock<OrderDao>()`(mockito-kotlin)
   - `@RelaxedMockK lateinit var dao: OrderDao`
   - `val dao: OrderDao = mockk()`
5. 只有 `mockk<OrderDao>()` 這種寫法 rc=1。

file: `/Users/enzo/harness/lumos-room-test/scripts/lumos` 的 `_rg_dao_need_tests`

## F2 專案從沒提交過結構檔時,任何碰到 Room 的推送都被擋,而且訊息教的救法做不到
severity: major
blocking: 是 判準:正常專案被誤擋,訊息指的補法無法操作。

引句:「top = max(tip_s.get(tq, {}) or [0])」

1. 輸入:專案沒設 `room.schemaLocation`,全 repo 沒有任何 `schemas/**.json`。`@Database(version = 3)` 沒有寫 `exportSchema = false`(預設是匯出)。
2. 分支只往 `OrderDao` 加一個有測試的方法。
3. `_rg_triggered` 因 `@Dao` 命中而觸發,`_rg_migration_half` 呼叫 `_rg_check_sources`。`tip_s` 是空的,所以 `tq=None`、`top=0`,`3 > 0` 且不在 allow 清單,就擋。
4. 實測 rc=1,訊息是「p.AppDb 的 @Database 寫 version = 3,結構檔最大只到 0……把 p.AppDb/3.json 加進提交」。
5. 沒設匯出路徑時重新編譯產不出這個檔。此外這個資料庫根本沒被改,也被擋。
6. 唯一出路是 `allow_destructive`、改成 `exportSchema=false`,或單次跳過,而這些訊息都沒教。

引句:「if d["version"] is not None and d["version"] > top and fq not in allow:」

## F3 整個刪掉一個 DAO 方法,會要求相鄰、沒改過的方法補測試
severity: minor
blocking: 否 判準:純刪除的誤擋,有單次跳過可以脫身。

引句:「s.update(range(c, c + cnt) if cnt else (c, c + 1))」

1. 輸入:`OrderDao` 依序有 getAll、alpha、old、beta,分支整段刪掉 `old`,什麼都沒新增。
2. 純刪除的區段 `cnt=0`,算 `c` 與 `c+1` 兩行。`c+1` 落在 beta 的 `@Query` 註記行,於是 beta 被當成「這次改了」。
3. 實測 rc=1,點名 `OrderDao.beta 這次改了,沒有測試以 .beta( 呼叫它`。
4. beta 一個字都沒動。

## F4 `version` 寫成常數、只改常數檔而忘了提交結構檔時,守衛完全不觸發
severity: minor
blocking: 否 判準:漏擋,但前提是版本號用常數,且同時沒有結構檔異動。

引句:「ver = int(vm.group(1).strip()) if vm and re.fullmatch(r"\d{1,9}", vm.group(1).strip()) else None」

1. 輸入:`@Database(version = DB_VERSION)`,分支只把 `Consts.kt` 的 `DB_VERSION` 從 1 改成 2,沒提交 `2.json`,也沒寫 Migration。
2. `Consts.kt` 不含 `@Database` / `@Dao` / `Migration(`,`_rg_triggered` 不命中,`cmd_room_guard` 直接 rc=0,沒有任何輸出。
3. 實測 rc=0。S12 只涵蓋「有新增 2.json」的情況。

## 圖譜鏡頭與本案特定鏡頭(不帶 severity)

- 圖譜固定席:派工詞寫明這次沒附固定席節點(鏡頭計算超時),也沒有「這次新增的殘留」段,所以沒有逐條要答的合約。
- (a) 掛鉤整合:
  - 位置在存量漂移檢查之後、回頭重讀之前,三個變數(遠端舊值、本地頂端、遠端 ref)與漂移那段一致。
  - rc 處理:1 擋,128 以上整支停下,其他非零講一句再放行。
  - 擋下時走 `pp_record_block`,會進彙總。
  - 我跑了 `-k prepush_interrupt`(50 個全過)與 `-k room`(100 個全過)。
- (b) 誤擋與漏擋:誤擋見 F2、F3;漏擋見 F1、F4。
  - 多個資料庫共用同一組 Migration 邊,這是計劃〈誠實界線〉已寫明的限制,實測也如此:CacheDb 沒有自己的 1→2 路徑,但 AppDb 的 `Migration(1, 2)` 讓它過關(rc=0)。我不另開一條。
- (c) 帳本:
  - `room-guard` 已加進 `_KNOWN_GATES`。
  - `("room-guard","passed")` 進本機帳,`blocked`、`warned`、`skipped`、`skipped-env` 進版控帳,與 `drift-check` 的既有規矩一致。
  - 我跑了 `t_gov_stats_gate_drift`,通過。
  - 小瑕疵:gate=block 時只有提醒、沒有擋下的推送,會記成「passed / 有碰到 Room、全部通過」,提醒不進帳。
- (d) 效能:3000 個 kt 檔加 2000 個測試檔、一次新增 3 個名為 insert/delete/update 的 DAO 方法,實測 4.8 秒。成本與「方法數乘上粗篩命中的測試檔數」成正比,沒有快取。我沒有找到會超時的具體輸入,所以不立 finding。
- 測試品質:S24 只覆蓋 `mockk<OrderDao>()` 一種 mock 寫法,這正是 F1 的測試缺口。
- 臨時目錄:`/tmp/lumos-seat-work/code-room資料庫測試守衛/正確性-sonnet` 已用字面絕對路徑刪除。

最嚴重 severity 是 major,blocking 共 2 條(F1、F2)。
