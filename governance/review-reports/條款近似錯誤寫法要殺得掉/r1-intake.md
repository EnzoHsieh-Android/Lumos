preflight-4: ran

# r1 收貨紀錄(條款近似錯誤寫法要殺得掉)

## 前掃(首輪,2026-11-13,sonnet 一席,只讀)

命中:①4 ②1 ③5 ④7。①②③ 直接修真檔、不算 findings;④ 語意類逐條修並留前後對照:

| # | 類 | 計劃原說 | 程式實際 | 修成 |
|---|---|---|---|---|
| p1 | ④ | `_clause_body_of` 多剝 `[near:]`;回退節說「已剝掉」 | 剝的名單在 `INV_TAG_RE`,不含 near | 範圍 1 改成「`INV_TAG_RE` 名單加 near」;回退節改成「範圍 1 剝掉之後」 |
| p2 | ④ | `[near:]` 一句話只限實字數 | `INV_TAG_RE` 的值遇 `]` 截斷 | 〈用詞〉加「不得含 `]`」,形狀檢查也擋 |
| p3 | ④ | 殺傷力帳本那筆 source 寫 clause-kill | `cmd_guard_kill` 給了 recipes_override 就寫死 situation-rule | 範圍 2 加:`cmd_guard_kill` 多選用參數 source;讀帳只跳過人裁的讀者一併跳過 clause-kill |
| p4 | ④ | 有效紀錄在 `docs/.kill-log.jsonl` | 消費專案 init 把 `.kill-log.jsonl` 寫進 gitignore,推送閘與 CI 讀不到 | 有效紀錄改成版控治理帳的 clause-kill 事件(照人裁的寫法);殺傷力帳本照記但推送閘不讀 |
| p5 | ④ | 生效日比「首筆設計審帳」 | 預期值表那道改用 `_plan_effective_day`,因審查帳在消費專案不進版控 | 〈用詞〉生效日改用 `_plan_effective_day` 與 `LUMOS_NEAR_SINCE` 覆寫 |
| p6 | ④ | 推送前「只看風險高」沒說判法 | `_spec_gate_push_scan` 只對風險低走全套,風險高由預期值表那圈重判門 | 〈用詞〉風險高 = 預期值表那道同一判法 |
| p7 | ④ | 讀帳失敗沒說 | 預期值表那道讀治理帳失敗是擋 | 範圍 3 補「治理帳讀不到 → 擋」 |
| p8 | ③ | 範圍 1 要求綁測試的條款宣告、範圍 2 要求綁恰一支 | — | clause-kill 加 `--test`,綁多支時必給 |
| p9 | ③ | 預期值表 S6、S7 缺範圍列出的情境 | — | S6 補三列、S7 補兩列、S9 補風險低一列 |
| p10 | ② | 依賴另一條分支的 `--import`、`also`、`fail_excerpt` | 主線還沒有 | 〈用詞〉加「前置」一條 |

沒有動到核心裁定(做正向、宣告式、推送只讀帳、不自動產生),不升級成正式 finding。

## 席報告收貨(六席全到,皆 sonnet;收齊後一次寫進卷證)

正確性 c1–c11、邊界 b1–b9、整合 i1–i11、資源 z1–z8、通才 t1–t9、架構對齊 a1–a4,共 52 條、blocking 24。引句除邊界席外全數錨定;邊界席錨不到的引句,其發現由編排者對照計劃與程式重現(下表)。

## 分組(依根因)

| 組 | 根因 | 發現 | 處置 |
|---|---|---|---|
| G1 | 宣告與實際壞法脫鉤:`--file/--old/--new` 作者自填、可打測試檔、`new` 不入帳 | t1、c10、b4、i6 | 折(方向改):壞法由工具依型錄同列兄弟寫法產生,`--file` 禁測試檔,帳記 old/new |
| G2 | 沒殺掉可改寫宣告或寫「無」逃掉;RETIRE-IF 量不到 | t2、t4、b8 | 折:免宣告與存活後改寫要人核可、留帳;gov --stats 印三個數;RETIRE-IF 加③ |
| G3 | 有效紀錄沒比現在綁的測試、--test 可亂指 | c1、b3、i1、t3 | 折:--test 要在綁的清單;紀錄 test_name 要在現在綁的清單 |
| G4 | 弱證據與 rc 對應、哪些判定入帳 | c2、c8、a1、b9、i8 | 折:從 result_out 讀 weak;只記 killed/survived,其餘 rc 2 不記帳、訊息分流 |
| G5 | 新閘名與測試總開關沒登記 | c3、z6、t5、b6、i2、i7、a2 | 折:範圍 4 列 _KNOWN_GATES、LOOP_NOT_CLOSE_EVENTS、token;測試總檔預設 9999 |
| G6 | 標記掃描器:`]` 截斷、反引號、全形、共用 INV_TAG_RE 牽動合約指紋、行中剝除留空白 | c4、c7、b1、b2、i5、t9 | 折:條款專用正規式、先遮反引號、整個標記要對上形狀、剝前導空白 |
| G7 | 適用範圍:todo 計劃、人裁條款、keeps | b5、i3、i4、c9、t6 | 折:只看 _live、扣人裁與 keeps |
| G8 | 推送版本與讀帳次數 | z1、z4、t7、i10 | 折:跟預期值表同圈共用 ctx;取範圍右端;按(提交,檔)快取 |
| G9 | 中斷收尾、重用人裁零件、讀者跳過 | z3、a3、a4、i9、i11 | 折:參數化 _situation_rule_kill 共用;讀者改「source 非空就跳過」 |
| G10 | 其他邊界 | c5、c6、c11、b7、z5、z7 | 折:天花板 2 擴寫、取篩完最後一筆、--file 基準、生效日隔日與 scope=note、計劃檔要乾淨、old 長度上限 |
| — | 連結候選計劃也被要求(z2) | z2 | 放行:跟預期值表那道既有範圍一致(_live 的 doing 計劃就是正在實作的);單人使用;改範圍會跟預期值表那道分歧 |
| — | 一次只跑一個宣告(z8) | z8 | 放行:寫進〈不做〉,單人依序操作,成本問題不影響正確性 |
| — | near 句子進門判定的關鍵字(t8) | t8 | 放行:新形狀只收列號與識別字,不會含門判定的風險詞 |

## 先查世界

- G1/G2 PRIOR-ART:Meta ACH 壞法由代理產生、人只審測試(https://arxiv.org/html/2501.12862);MutApi API 誤用寫成改寫運算子(https://bohrium.dp.tech/paper/arxiv/5cf934b85ced2477cb3c1843);Google 差異式變異測試、存活在代碼審處置、無用的壓掉(https://arxiv.org/pdf/2102.11378v1、https://testing.googleblog.com/2021/04、https://arxiv.org/html/2306.09130v1、https://homes.cs.washington.edu/~rjust/publ/mutation_testing_resolution_icse_2023.pdf)。排除:作者自填壞法(三家都沒有)。
  方向:要換 — 作者自填壞法換成工具依型錄兄弟寫法產生;來源 https://arxiv.org/html/2501.12862 、https://bohrium.dp.tech/paper/arxiv/5cf934b85ced2477cb3c1843 。已攤人裁:使用者 2026-11-13「你調研一下? 記住我們的大方向」→ 調研後「照方向,計畫連結到這些sources,日後好說明」。
- G6 PRIOR-ART:專案既有 `_inline_visible_mask` 遮反引號、`_slot_scan` 認成對括號;採前者遮反引號、整標記用條款專用正規式,不改合約共用的 INV_TAG_RE。
- 其餘組:內部一致性,照預期值表那道與人裁既有做法(`_expected_requirement`、`_spec_gate_ruled_ids`、`_situation_rule_kill`)。

## 重現

| id | 重現 | 結果 |
|---|---|---|
| t1、i6、b4 | 讀計劃 r1 範圍 2:`--file/--old/--new` 由參數直給、無任何與 near 的比對 | HIT |
| c1、b3、i1 | 讀 `_clause_sha` 說明「不含綁的測試」與人裁 `_spec_gate_ruled_events` 另比 test_name | HIT |
| c3、i2 | `_gate_event` 對不在 `_KNOWN_GATES` 的閘名不寫 | HIT(讀碼) |
| c4、b1、i5 | 席位實測把 near 加進 INV_TAG_RE 後 `[near:用 a[0] …]` 截斷 | HIT(整合席附腳本) |
