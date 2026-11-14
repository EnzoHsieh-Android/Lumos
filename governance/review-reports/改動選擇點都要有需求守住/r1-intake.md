preflight-4: ran

# r1 收貨紀錄(改動選擇點都要有需求守住)

## 前掃(2026-11-13,sonnet 一席,固定清單四項)

報告原文:編排者 scratchpad 的 choice-preflight.md(派工詞與報告內容摘錄如下;報告引的行號是前掃當時的 scripts/lumos)。四類:① 未定義詞 5、② 壞引用 2、③ 範圍矛盾 6、④ 語意 12。全部直接修進計劃真檔;④ 沒有一條推翻核心裁定(選擇點全數各換一個壞法、存活交人裁、無規格照擋),不升正式 finding。

### ④ 語意類逐條(修改前 → 後)

| id | 修改前 | 修改後 |
|---|---|---|
| ④-1 | 推送那一道「在 _spec_gate_push_check 裡、跟預期值表那道同一圈」;_live 當成可直接呼叫 | 在 _spec_gate_push_scan 之後另起一圈(沒有候選計劃也跑);_live 抽成頂層函式;_spec_gate_push_bad_head 補新標籤;「進行中」寫明 doing 或改到計劃檔的 done |
| ④-2 | 選擇點範圍「同人裁的 --diff,_codeloop_disp_range」,推送閘也照它 | 推送閘用主線與 B 的分岔點..B(算不出退回推送範圍);choice-points 不帶 --diff 時算同一個範圍 |
| ④-3 | 「都從這個版本讀(git show)」 | 指名重用 _kt_sit_read_many 與 _gov_rows_at;計劃(決定守的測試)也從 B 讀;預期值表那圈照舊讀工作目錄 |
| ④-4 | 型錄「從工作目錄讀」 | 照 _kt_catalog_path()(工具鏈來源);測試用 LUMOS_KT_CATALOG |
| ④-5 | 天花板 2:字串樣板裡的運算子會漏 | 樣板裡的程式碼照算;剝除用 keep_length=True 在等長文字上定位 |
| ④-6 | _situation_rule_kill「參數化」 | 改成只回 (結果列, 狀態),判定與訊息由呼叫端做;人裁拒絕訊息搬回 cmd_situation_rule |
| ④-7 | 平台「照 _kill_method_name 判」 | 照 resolve_test_refs/_split_test_ref_ex 取平台;臨時配方帶 platform 欄 |
| ④-8 | 「一支一支跑、殺掉就停」+「基準只跑一次」(互斥) | 每點一次 cmd_guard_kill、全部守的測試一次丟入;killing_test 取條款順序第一支強 killed |
| ④-9 | 同意記 ai-with-consent、欄位 by | 照 _waive_origin_tty 記 origin human/ai + consent |
| ④-10 | situation-rule --point「其餘照原本流程」 | 獨立的選擇點檢查路徑;seg/row/file/old/new 改選用並互斥;冪等鍵換 (file, old, new) |
| ④-11 | _GOV_FIELD_TYPES「int 排除 bool」 | 表只驗 isinstance;讀者自己 type(x) is int |
| ④-12 | 測試檔判法(語意正確) | 預期值表補 androidTest 一列 |

### ①②③ 直接修

- ①-1 過期 → 〈用詞〉新增「過期」定義、blocked reason 加入。①-2 有效紀錄 → 統一用「有效處置」並定義。①-3 預期值表組名改寫、種類只三種。①-4 blocked 的 gate 寫明 choice-kill,LOOP_NOT_CLOSE_EVENTS 寫成 (gate, kind) 配對。①-5 只收 .kt。
- ②-1 前置計劃節點:前置已合進主線(PR #202),本分支 rebase 後存在。②-2 Offutt 網址 404 → 換 dblp 書目頁;ldra 網址 curl 403、WebFetch 讀得到,內容列「changes to requirements」「removal of dead code」兩種處置,保留。
- ③-1 同行多點 → 定位 <檔>:<行>#<n>。③-2 型錄缺檔只提醒、檔在但讀不了或表壞才擋。③-3 混合結果判法與 rc 取最大。③-4 新增 reason 無測試。③-5 choice-kill 事件加 via 欄。③-6 choice-kill 跑與判拆兩行語法,判不套用跑前檢查。

## 席報告收貨(r1,6 席,皆 sonnet)

六席全到後才一次從逐字稿存進卷證;收貨前沒動被審材料。quote-check:正確性 14 句錨 13(c11 引句不到 10 字)、架構對齊 8 句錨 6(第 2 句在四問段非 finding;a4 的 lands_in 引句是把 frontmatter 的 YAML 清單寫成一行),其餘四席全錨。共 53 條(c 13、b 11、i 10、z 6、t 9、a 4),blocking 22。

## 分組(依根因)

| 組 | 根因 | 發現 | 最高 | 處置 |
|---|---|---|---|---|
| G1 | 每個選擇點各開一次殺傷力:每點一棵工作樹、基準重跑、結果列對不回測試 | z1、z2、z3、t2、c13、c1、z6、i7 | major | 折:同平台同計劃一次 cmd_guard_kill 批次;配方 invariant 寫成「定位\|測試名」讓 recipe_id 各自唯一;node 填那份計劃;基準 abort 整批 no_result 不重跑;放棄提前停(選批次,z3 要求二選一) |
| G2 | 壞法編不過、弱證據沒有處置出口 | t4、b3、i2、c7 | major | 折:--judge 加 not-applicable、存活與 no_result 都能判;run_cmd 要含 {method};編不過的形狀累計給人改表(論文 3.2.1) |
| G3 | 選擇點比對太寬或邊界沒定 | b2、c7、b4、t7、c6、b7、b8、c8、b1、t5 | major | 折:API 成員只認呼叫形、運算子兩側含換行、BOM、反引號識別字不算、沿用 _kt_sit_hits 縮排過濾與 _kt_sit_path_ok、測試判法帶 layout 加 testFixtures/sharedTest;單元測試分不出的寫法移出表;照論文加乾節點規則(附錄 A) |
| G4 | 需求脈絡組與樣式推廣:函式邊界取不到、組鍵歧義、一條條款殺不了整組、推廣範圍過大 | t1、b5、c4、c9、b6、c5、b10、c11、t6 | major | 折:照論文撤掉分組處置與樣式自動推廣,只留按外層宣告排版;乾節點規則人工增補;身分改雜湊並要求唯一 |
| G5 | 推送閘接線:主線 ref 傳不進、「碰到」沒定義、計劃讀工作目錄、算不出來沒結果 | i1、c3、c10、b9、z4 | major | 折:--push-check 加 --push-remote/--pushed-ref(同 pitfalls);主線照 _push_mainlines、推主線用推送範圍;碰到=_spec_gate_push_candidates;B 版計劃 git show;預算與讀不到各自 reason |
| G6 | situation-rule 選擇點路徑:冪等、統計污染、既有測試 | c2、i3、i8 | major | 折:既有條款記給新壞法;事件帶 point 欄、情境題統計排除;不改 _situation_rule_kill 回傳形狀 |
| G7 | 帳:量、提交、token、度量欄位 | i6、i4、i5、t3、c12 | major | 折:只存雜湊;每次呼叫記 run(行數、耗時);blocked 帶 token、同 B 不重記;提示提交帳;S19 數字照 attempt 定義重寫 |
| G8 | 架構對齊與舊裁定 | a1、a2、a3、a4、t9、i9、i10、t8、b11 | major | 折:兩節共用 check.py 表讀法並寫明為什麼不併進決策表;沿用 _kt_sit_hits;生效日不沿用 _kt_sit_spec_since 的理由;lands_in 加 Systems/kotlin規則包;d1 用 decision-add 翻案;manual-only 計劃只提醒(規格閘裁定);環境變數關閉時印一行 |

另:使用者同日裁「照那份論文來實作」「有什麼問題,優先參考」——與 G1–G8 一起折:一行一個壞法(論文 4.1)、五個運算子加 SBR(表 1)、回報上限檔數 × 7(2.3)、固定種子穩定回報(3.2.4)。

## 先查世界

- G1 PRIOR-ART:論文 2.3「一次產生全部壞法、批次執行」與 4.1「每行只一個壞法」(https://arxiv.org/pdf/2102.11378);採用批次與一行一個,不採逐點呼叫。
- G2 PRIOR-ART:論文 3.2.1「無法編譯的壞法要用規則擋」(https://arxiv.org/pdf/2102.11378);Google 讓開發者按「沒用」回報(https://research.google/pubs/state-of-mutation-testing-at-google/)。採用:人可判不適用、累計給人改表。
- G3 PRIOR-ART:論文附錄 A 的乾節點規則與 A.1.23(== 只換 !=)(https://arxiv.org/pdf/2102.11378);論文用語法樹,我們沒有 Kotlin 語法樹,改用呼叫形與邊界近似並寫進天花板。排除:純字串整字比對(本輪 b2、c7、i2 三席打穿)。
- G4 PRIOR-ART:論文逐行回報、無分組,回饋由人寫成規則(3.1,有用比例 15% 到 89%)(https://arxiv.org/pdf/2102.11378);MuRS 依樣式自動排序(https://homes.cs.washington.edu/~rjust/publ/murs_fse_2023.pdf)是後續研究,不採(使用者裁優先照論文)。
- G5、G6、G7、G8:內部接線與一致性,沿用 repo 既有零件(pitfalls 的 --pushed-ref、_push_mainlines、_spec_gate_push_candidates、_kt_sit_* 系列、check.py 的 dt_table),不涉外部規格。

## 重現

| id | 重現 | 結果 |
|---|---|---|
| c11 | 引句不足 10 字;讀快照〈用詞〉選擇點身分:身分是 (file, old, new) 不含位置、不唯一的點標不唯一 | HIT(複製貼上的兩段 old 相同時身分相同;改寫後身分含那一行雜湊且要求唯一) |
| a4 | 快照 frontmatter lands_in 只列 Systems/規格閘、Systems/guard-kill;grep 型錄的家是 Systems/kotlin規則包 | HIT |
| z1、t2、c13 | 讀 cmd_guard_kill:baselines 是呼叫內區域變數、每次呼叫一棵 _isolated_worktree | HIT |
| c1 | 讀 _kill_recipe_key 與 result_out 列欄位:不含 test | HIT |
| b1 | 席附 _nodehome_is_test 不帶 layout 對 androidTest 回 False 的實跑 | HIT |
| i1 | 讀 pre-push 呼叫 spec-gate --push-check 只帶範圍;pitfalls 那行帶 --pushed-ref | HIT |
