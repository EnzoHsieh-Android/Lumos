# r1 intake

preflight-4: ran

兩席（單審、架構對齊，Claude sonnet，standard）收齊後才寫入卷證；被審 repo 未被動。兩份引句全數錨定。

| id | source | severity | reproduce | disposal | evidence |
|---|---|---|---|---|---|
| LO-1 | 單審 | major | HIT | folded | 編排者以 stray=None 變異重現四支新測試照綠；補 test_bundle_reference_guard_rejects_wrong_load_order（錯誤順序下守衛單獨回「混到未驗來源」），變異 M1 紅在 unexpectedly None |
| LO-2 | 單審 | minor | HIT | folded | 判斷式改以物件身分反查，不靠 __name__；test_bundle_reference_guard_judges_by_identity 修前紅在 user.wrapped 誤報、修後綠，變異 M2 紅 |
| LO-3 | 單審 | minor | HIT | folded | 補模組物件身分檢查（同一測試，變異 M3 紅）；常數看不到寫進 PITFALL 與函式說明，縮小宣稱 |
| LOA-1 | 架構對齊 | minor | HIT | folded | 改用既有 `_regular_own_fd`（O_NONBLOCK 開檔後 fstat 判一般檔），不再先 stat 後 open；變異 M4 改回直接開檔時 FIFO 測試逾時紅 |
| LOA-2 | 架構對齊 | minor | HIT | folded | 對齊檢查涵蓋 _TEST_QUALITY_LOAD_ORDER，與指紋表、vendored 清單三者集合不等即判不完整 |
| LOA-3 | 架構對齊 | minor | HIT | folded | 兩支舊 bytecode 測試共用 plant_stale_bytecode，不再各抄一份 |

regression_set：none（本迴圈第一輪；六條皆為被審修補本身的寫法與缺測）。
