# code r3 收貨紀錄(code-only-test-tag-not-write-back,上限三輪的最後一輪)

八席齊了才動工作目錄(正確性席第一次派工被自動審核擋下、照原樣重發一次)。report-normalize 八份都合格;quote-check 通才、正確性、規格符合全錨,另五份有錨不到的引句,編排者逐句到實際檔案 grep 重現:
- 邊界3 #2「拿掉後只剩清單符號或空白的行整行不算」:`scripts/lumos` 說明字串在「清單符號」後換行,合起來一字不差 → HIT
- 判定路徑 #2、架構對齊3 #2 #4、資安 #1 #6 #7:`grep -cF` 在 `scripts/lumos` 都 ≥1(既有程式,不在這次差異裡)→ HIT
- 架構對齊3 #3「_SLOT_STRIP_WS = …」:檔案裡是跳脫寫法 `" \t　"`,席位印成實際字元 → HIT
- 合約3 #1 #2:`grep -cF` 在計劃筆記各 1 → HIT

| id | 席 | 嚴重 | 重現/判讀 | 結論 |
|---|---|---|---|---|
| g1 | 通才3 F1 | blocker | 席在臨時 repo 實跑兩道都 rc0;編排者寫成 [S1] ⑤b 第一、二格,修前紅 | HIT 採信,折:新名稱只收單一識別字 |
| s1 | 資安 F1 | major | 同 g1(席實跑 `_ns_tr_judge` 提交與推送都回 yes) | HIT 採信,折(同 g1) |
| d2 | 判定路徑 F2 | minor | 同 g1(不存在的類別.真測試名) | HIT 採信,折(同 g1) |
| s2 | 資安 F2 | minor | Kotlin 反引號句子測試名可藏說明(推論) | HIT 採信,折:這類名稱不再豁免(天花板 7) |
| g2 | 通才3 F2 | major | 席實跑兩道 rc0;[S1] ⑤c 修前紅 | HIT 採信,折:@ 後面只認提交編號 |
| c1 | 正確性3 F1 | major | 同 g2(席實跑 rc0 對散文 rc1) | HIT 採信,折(同 g2) |
| c2 | 正確性3 F2 | minor | test-gone 帶平台前綴、上一版沒前綴 → 多擋;[S1] ⑤d 修前紅 | HIT 採信,折:比對去平台前綴 |
| e1 | 邊界3 F1 | minor | 「中文」改「中 [test:x]文」判沒變;[S4] ⑫b 修前紅 | HIT 採信,折:後面緊接字時留前面空白 |
| e2 | 邊界3 F2 | minor | `- [ ] [test:x]` 改 `- [x]` 兩邊都丟;[S4] ⑫c 修前紅 | HIT 採信,折:核取方塊行不丟 |
| d1 | 判定路徑 F1 | minor | 席實跑:提交前 rc0、推送前 rc1(未追蹤測試) | HIT 採信,折:寫進天花板 8(推送前補得回來) |
| d3 | 判定路徑 F3 | minor | Kotlin 帶連字號、沒設 test_profile → 誤擋 | HIT 採信,折:寫進天花板 7 |
| a1 | 架構對齊3 1 | minor | `except Exception: return None` 不出聲,鄰居 `_ns_test_refs_collected` 印一句 | HIT 採信,折:印一句提醒 |
| a2 | 架構對齊3 2 | minor | `_SLOT_STRIP_WS` 在函式後 | HIT 採信,折:挪到函式前 |
| k1 | 合約3 1 | minor | RETIRE-IF 還寫已做完的收窄 | HIT 採信,折 |
| k2 | 合約3 2 | minor | 實作紀錄的翻紅描述 r2 後失效 | HIT 採信,折:標明是 r1 前 |
| k3 | 合約3 3 | minor | 「工作目錄有沒提交的測試改動就不豁免」沒測試 | HIT 採信,折:[S6] ④b(修前就綠——既有 `_ns_tr_guard` 本來就擋,只缺測試) |

規格符合3 clean。輪內有 blocker → accepted 一條都不帶;refuted 0。三輪到頂,修正沒有第四輪可審——Enzo 2026-10-05 裁:另開新編號 code-only-test-tag-not-write-back-r3fix 派全新審查員驗收。
