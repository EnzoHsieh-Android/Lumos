severity: major

鎖 `/Users/enzo/.cache/lumos/dispatch-lens/e61b41df6a49fa6a794b899f5e9c47060c0cd6c5296569ff9408a79467085225.json.warming` 檢查時不存在,沒有要處理的鎖。

## F1 刪掉 DAO 方法最上面一行註記(例如 @Transaction)後,守衛不再要求測試
severity: major
blocking: 是 修補讓一條原本會擋的真實改動變成放行,違反 [S26]「方法裡刪一行要測試」。

引句:「s.update(range(c, c + cnt) if cnt else (c + 0.5,))」

失敗場景:
- main 上有 `@Transaction` 加 `@Query` 疊在 `suspend fun getTx()` 上,feat 分支只刪掉 `@Transaction` 那一行。
- 這是 `-U0` 的純刪除區段,新檔裡 c 是被刪行的上一行。
- 修前記成 (c, c+1),c+1 正好是方法起行,方法被點名。
- 修後記成 c+0.5。`_rg_methods` 的起行是第一個註記行,c+0.5 小於起行,也大於上一個方法的迄行,所以沒有任何方法含它。
- `_rg_dao_changes` 的 `s <= x <= e` 判不到,守衛放行。
- 失去交易註記是行為改變,卻不要求任何測試。同樣會漏的還有刪掉 `@RewriteQueriesToDropUnusedColumns` 這類最上面的單行註記。

重現(兩版同一支腳本,main 有 getAll、getTx(@Transaction + @Query),feat 刪 `@Transaction`,測試只呼叫 getAll):
- 修前 2327a527:`rc 1`,輸出「OrderDao.getTx 這次改了,沒有測試以 .getTx( 呼叫它」
- 修後 680b7870:`rc 0`,沒有輸出

歸因:有證據的修復回歸。新測試 `t_room_dao_whole_method_deletion_no_neighbor` 只測整段刪掉方法和連空行刪,沒有測方法最上面一行被刪。把 `(c + 0.5,)` 改回 `(c, c+1)` 會讓它紅,但上述場景它抓不到。

## F2 整個專案沒有結構檔時,[S17]「exportSchema = false 只提醒」被一併吞掉
severity: minor
blocking: 否 只少一則提醒,rc 不變。

引句:「if any(not d["export_false"] for d in db_src.values()):」

失敗場景:
- 專案從沒匯出過結構檔,`AppDb` 寫 `exportSchema = false`,這次把 version 從 2 升到 3。
- 進入新加的 `if db_src and not tip_s:` 分支。所有資料庫都是 export_false,不產生警告,直接 `return`。
- 迴圈裡原本的「寫了 exportSchema = false,沒匯出結構檔」提醒走不到。

重現(兩版同一支腳本):
- 修前:`rc 0`,印出「提醒:Room 守衛——p.AppDb 寫了 exportSchema = false,沒匯出結構檔,這道判不了它的升級」。
- 修後:`rc 0`,什麼都沒印。

歸因:有證據的修復回歸。`t_room_mig_export_schema_false_warns` 綠,是因為它的專案裡有別的結構檔。

## 驗證過的正向主張(同一案例,修前與修後)
- **mock 認法(G1)已修好。**
  - `t_room_dao_mock_forms_all_count` 的 10 種寫法修後擋下。
  - 另外附對照:mock 別的型別、DAO 用真的,修後放行。
  - 未對修前版跑這組測試,修前行為只靠 r1 程式內的舊正則推斷,所以修復效果標未判定。
  - 我另外檢查 `@MockK` 跨行規則:`lateinit var api: OrderApi` 後面接 `val dao: OrderDao` 不會被吃成 mock。冒號只能被吃一次,所以不誤判。
- **沒匯出結構檔(G2)已修好。**
  - `t_room_mig_never_exported_warns_not_blocks` 和 `t_room_mig_untouched_db_old_gap_not_blocked` 在修後綠。
  - 主線上舊缺口、這次沒碰的資料庫不擋,碰到才擋。
- **常數版本(G4)已修好。**
  - 只改常數檔升版會觸發並擋。
  - 同名常數有兩個值時不擋。
  - 我檢查拿掉任一半(觸發端或 `_rg_check_sources` 的 const_files)測試都會紅。
- **共用函式(G5–G7)正常路徑仍成立。**
  - `-k t_room_` 在修後全套 109 passed, 0 failed。
  - `_rg_fork_point` 問 `_push_range_start(舊值全 0)` 的語意,我對照過程式:全 0 時走 `_push_pick_base(..., "新分支首推")`,和修前同一個起點。
  - `_rg_root` 與 `_note_audit_start` 在有 `--repo`、沒有 `--repo`、有無 push 三種輸入下,語意與舊程式相同。
  - 沒有另外跑修前版的完整測試,所以「與修前逐字相同」標未判定。
- **效能。**
  - `_rg_triggered` 現在在沒碰 Room 的推送也呼叫 `_rg_db_sources`(git grep 加讀檔加剝註解)。
  - 我用 1500 個含 "Database" 字樣的 java 檔、只改 README 的推送量測:修前 63.04 秒,修後 64.45 秒,多出約 1.4 秒。
  - 整體耗時主要來自修前就存在的其他部分(約 40 毫秒每檔)。
  - 增量是每檔約 1 毫秒,上萬檔約多 10 秒。這不構成具體失敗場景,所以不當 finding。

## 三問
1. 原問題的修復效果:G1、G2(提醒與舊缺口那半)、G3、G4 都有測試行為證據。我自己重現了 F1、F2,它們是新的回歸。
2. 修補處的正常、錯誤與相鄰路徑:
   - 整段刪方法、方法中間刪行、新增行仍成立。
   - 方法最上面一行被刪(相鄰路徑)壞了,見 F1。
   - 全專案無結構檔且全是 export_false(相鄰路徑)壞了,見 F2。
3. 新發現同一案例在修前與修後的結果:F1 修前 rc 1、修後 rc 0。F2 修前有提醒、修後沒有。

## 圖譜固定席判定
- 派工詞寫明這次沒附固定席節點,也沒有「這次新增的殘留」段,所以殘留逐條題不適用。
- `Systems/room-guard` 和 `Projects/Room資料庫測試守衛_計劃` 的新增偏離紀錄與程式實作一致。
- 有一點要註明:實作偏離紀錄第三條寫「純刪除只在前後兩行落在同一方法裡才算」,F1 的場景下被刪的那行本來就屬於該方法,卻不算,這和 [S26] 衝突。這是程式的問題,不是筆記寫錯。
- `scripts/hooks/pre-push` 與 `INDEX.md` 的改動只是註解與文字,不影響合約。

## 未驗範圍與案例來源
- `r2-behavior-cases.json` 的 G1–G7 我逐組對過;缺修前證據的是 G1 的修前實跑,標未判定。
- 角色卡:派工詞寫 `ROLE-CARDS: on`,但沒附任何卡,略過。
- 未驗:`_rg_const_value` 在 `VERSION` 這種常見名字、全庫另有不同定義時的誤算。我只看出可能,沒造出具體輸入。

最嚴重 severity 是 major,blocking 共 1 條(F1)。
