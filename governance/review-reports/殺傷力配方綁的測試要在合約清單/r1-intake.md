preflight-4: ran

# 殺傷力配方綁的測試要在合約清單 r1 前掃

前掃一席(sonnet):①無 ②1 條(rtb 庫的節點寫得像本庫)③無 ④6 條語意命中。不動核心裁定,直接修真檔。

| 類 | 修改前 | 修改後 |
|---|---|---|
| ④ | 照 guard bind 組完整 ref 再比字串 | 配方 test 有三種存法、清單預設平台有前綴與沒前綴兩種,字串比兩邊誤報;改成兩邊都轉 (平台, 方法) 再比(`resolve_test_refs`、`_kill_method_name`) |
| ④ | 沒提解析失敗 | 合約行未定義平台前綴時 resolve_test_refs 丟 ValueError;不比、不提醒、不失敗 |
| ④ | 提醒一律講「推送前跑清單那幾支」 | 帶 --test 且清單空時不擋、走到提醒;措辭另分支。沒帶 --test 不會觸發;比的是實際寫入那條(含只更新 covers) |
| ④ | 對回合約行照 kill-add 掃整個開頭欄位 | doctor 用 extract_contracts(只認摘要 KEY 行)加去標記含片段 |
| ④ | 對不回合約行「既有檢查管」 | 沒有任何檢查管;改成同一則提醒開頭印筆數 |
| ④ | 放 Check T 的提醒區 | Check T 沒有提醒區、用的是會計入問題數的 warn;改併進 P2 段當第三個提醒,照它的寫法 |
| ② | Systems/執行迴圈:25 | 標明是 rtb 庫的筆記 |

# r1 收貨

席報告 6 份(正確性 6、邊界 10、整合 8、回滾 7、簡化 4、架構對齊 3,共 38 條)。quote-check:正確性席 1 句錨不到(該句不採信,所屬 c3 另有邊界 e4、整合 i4、回滾 rb2 錨定同一問題);其餘全錨。refcheck 全 ok。

彙整 id:正確性 c1–c6、邊界 e1–e10、整合 i1–i8、回滾 rb1–rb7、簡化 s1–s4、架構對齊 a1–a3。

## 機械重現(命令:python3.14 scratchpad/d3repro.py,SourceFileLoader 載入 scripts/lumos)

| id | 重現 | 輸出 | 判 |
|---|---|---|---|
| e2 | resolve_test_refs 反引號 vs _kill_method_name | `[('kotlin', '`foo bar`')] vs 'foo bar'` | HIT |
| c2 e3 | 單平台傳整張平台表 vs 傳 {} | 整表 → ValueError 前綴 't_a' 未定義;{} → `[('python', 't_a:b')]` | HIT |
| c1 e5 i2 | 不帶 --test 取前綴 ref | invariant_test_refs → `['ios:Foo']`;kill 跑 (預設平台, Foo);kill 分組 `r.get("platform") or platform_override or default_plat` | HIT |
| e1 i1 rb3 a1 s4 | check-p2t 登記 | `_KNOWN_GATES` 無;`_GOV_LOCAL_PAIRS` 只有 check-p2、check-p2s | HIT |
| rb1 e6 c5 i6 a2 | 鎖外拿不到合約行 | 讀碼:warn_box 只 append(recipe),line/refs 在 _guard_kill_add_locked 內 | HIT |

## 處置

全折,除 s1(放行:rtb 點名要寫入當下的提醒)、s4(放行:撤除條件要單獨數這一則,另開閘名;登記兩處已折)。
