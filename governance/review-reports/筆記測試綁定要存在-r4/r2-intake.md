# 筆記測試綁定要存在-r4 r2 收貨紀錄(2026-10-03,4 席)

preflight-4: ran(本迴圈 r1 已跑;本輪材料是 r1 折入後的同一份計劃,前掃不重跑)

機械:四份 report-normalize 都已是正規格式;quote-check --spec r2-snapshot.md 四份全錨定;refcheck 四份全 ok(正確性 20、整合 26、架構對齊 21、邊界 20)。

編號:c1–c9 = r2-正確性-opus.md F1–F9;b1–b8 = r2-邊界-sonnet.md F1–F8;i1–i13 = r2-整合-sonnet.md F1–F13;a1–a4 = r2-架構對齊-sonnet.md F1–F4。共 34 條,blocking 17(c 5、b 6、i 5、a 1)。

| id | 怎麼試 | 結果 |
|---|---|---|
| a1 / i11 | 編排者讀碼:`_note_shape_eval` 對 `slots` 只轉 `mark2`(沒有就 None)、跑完放回 `notes` 與 `old_by`;格子違規由 `cmd_note_shape` 之後呼叫 `_ns_slots_violations` 另判;`_ns_skip_slot_extra` 已傳 `slots = {}` 只取筆記 | HIT(r1 折入「傳容器會連帶開格子」的前提是錯的) |
| c1 / b4 / i5 | 三席實驗:`_notelines_new` 的 notes 含 rows 為空的篇(合進來的主線、只刪行、純改名、新增後又刪) | HIT(三席獨立一致) |
| c6 / b3 / i5 | 三席實驗:只改 `updated:`/`status:` 的提交,rows 有 `other` 區的行 | HIT(三席獨立一致) |
| c2 / b1 / i3 | 三席實驗:`_classify_test_refs("[test:FooTests.Bar]")` 判 real;`git grep -w -F -e FooTests.Bar` rc 1、`-e Bar` rc 0 | HIT(三席獨立一致) |
| c3 / b2 / i2 / a4 / i8 | 讀碼+實驗:表態閘根在 repo 外放行、rc 其他值擋、逾時丟例外各自不同;子模組裡的根 `git grep` 回 rc 1 | HIT(四席一致) |
| c7 / b5 / i4 | 讀碼:`_visible_lines`、`_strip_inline_markup`、`clause_bindings` 都明寫不偵測 HTML 註解;實驗註解裡的名稱照抽到 | HIT(三席獨立一致) |
| i1 | 整合席探針:單行寫法 summary 的鍵行判 other、`_ns_summary_logical` 回空;編排者讀碼:`_note_summary_entries` 有單行寫法處理(吃筆記物件,`_note_from_text` 可從全文建) | HIT |
| c4 | 讀碼:Check T 不跳過作廢的合約行,沒 `[test:]` 就算裸合約,`doctor --ci` 擋 | 採信(讀碼) |
| c5 / i9 | 讀碼:`extra.test_refs` 會跟別的規則的擋一起寫進帳;nodes 只收 viol/errs/sviol | 採信(讀碼) |
| b6 | 編排者查 rtb 量測報告 rtb-cmp-B 第 3 節:「58 筆全部是非 ★INVARIANT★ 的 [test:],所以 doctor [T] 與 S5(只驗 [S###] 條款)都沒看」 | MISS(主張「動機證據大半在條款行、擋不到」不成立);但「各有檢查」措辭太滿屬實,照折 |
| i7 | 編排者讀 bound-tests-gate 摘要:WHY 行「[test:] → resolve_test_refs」、FLOW 行「合約行 [test:] 解平台」沒包反引號 | HIT |
| c8 / b7 / i12 | 讀碼:保險沒寫偵測指令;本 repo 測試都在已追蹤的 test_lumos.py;第①道讀工作目錄設定 | 採信(讀碼) |
| c9 | 讀 scripts/hooks/pre-push 與 .github/workflows/ci.yml:擋下句寫死形狀規則、逃生句叫人關整道 gate | HIT |
| a2 / a3 / i6 / i10 / i13 / b8 | 讀碼核對 | 採信 |

處置:34 條全折,無放行、無駁回(b6 的主張不成立部分不改設計,措辭部分折入)。
- 碰到的判法(c1 c6 b3 b4 i5 a1 i11):只算正文或摘要有新寫行的篇(含單行 summary 鍵行);改用既有 `slots` 容器,不加 `rows_out`;S2 擴成三種不算碰到、S3 夾具改已推過的起點、S25 改走 CLI 的 S26。
- 第②道(c2 c3 b1 b2 i2 i3 i8 a4):類別.方法找最後一段;`_test_in_tree` 回 found/notfound/outside/error、逾時丟例外、逾時秒數由呼叫端傳;子模組判法留在 note-shape 側;表態閘照原樣對回(S25 列四種);名稱以(平台, 名稱)去重、固定順序、預算從建索引起算。
- 註解(c7 b5 i4):照算,不偵測。
- 摘要抽取與名稱(i1 i6 a3 i10):`_note_summary_entries`、`_test_names_of` 共用切分、去反引號、全形冒號前綴;條款定義行取 `clause_bindings` 的 defined 行號、名稱一律 `slot_parse`。
- 合約行與條款行(c4 b6 i13):作廢合約行改法、作廢 PITFALL 補防回歸無;條款行不驗的理由改寫成已知缺口+REVISIT。
- 保險(c8 b7 i12):三個條件寫成指令與檔名規則,S15 改新開未追蹤檔、S16 加不觸發的反例。
- 帳本(c5 i9):mode/blocked/new、nodes、count,單次跳過不看格子開關(S21、S22),RETIRE-IF ② 改寫成量得到。
- 同步與上線(c9 a2 i7):掛鉤與 CI 的擋下句、說明字串進同步清單;〈做法〉12 上線順序。
