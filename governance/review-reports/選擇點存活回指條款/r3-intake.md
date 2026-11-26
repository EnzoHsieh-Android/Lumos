# 選擇點存活回指條款 r3 收貨

- 派六席全新(正確性、邊界、整合、資源、回滾、架構對齊,sonnet),審 r3-snapshot.md(303 行,第 3 版)。
- 六席全部交回後一次存檔;整合席兩句、資源席一句引句內包「」、架構對齊席檔級行不在第一行,退回原席只改格式。重交後資源席第 7 條引句「最後還原。」只有 5 字低於 10 字下限:快照裡確有此句(〈用詞〉合批編譯檢查末句),編排者機械重現 HIT,不再退回。
- 編號:正確性 c1–c13、邊界 b1–b14、整合 i1–i10、資源 s1–s9、回滾 k1–k12、架構對齊 a1–a8,共 66 條;正確性、邊界、回滾三席判 blocker(同一件事:環境壞掉時全部壞法被判無效、推送閘放行)。
- 跑滿三輪。使用者 2026-11-26 裁:「折完改走原型(建議)」——把 blocker 與能確定的嚴重問題全折進計劃,記接受風險後動手實作,剩下的接法由實作與高風險代碼審以測試定案。這一輪 66 條全部折入,沒有放行。

## 依根因分組與去向

| 組 | 根因 | 發現 | 折法 |
|---|---|---|---|
| J1 | 環境壞掉、輸出截斷、錯誤歸錯人時合批編譯失效開放 | c8 c9 b1 b2 k1 s2 s3 | 先編沒套壞法的原樹當對照,紅就整段跳過不記無效;嫌疑壞法單獨再編一次確認才記;截斷或對不回一律不記;新增 S22 |
| J2 | 準備物件掛在合併快篩那條路上 | c2 b3 k6 i1 a1 | 呼叫點獨立於合併開不開、能不能合併;S5 加不合併與單支案例 |
| J3 | 另寫量基準迴圈、時間政策與收手規則不一致 | a4 s4 b5 | 把 `_kill_merge_singles` 抽成共用 `_kill_measure_singles(c, wrap)`,合併快篩與準備物件共用 |
| J4 | 合批編譯沒有時間預算、還原沒有保證、多檔套用另一套 | s1 s7 k8 a5 | 編譯預算不超過總時限四分之一、最多 3 批;泛化 `_kill_merge_apply`/`_kill_merge_restore` 成多檔版,try/finally、還原後比對內容;新增 S24 |
| J5 | 判定沒照子集、換候選後帳上身分還是候選 1、子集合併判讀、配方對回 | c1 c3 c12 a2 | 準備物件回傳後呼叫回呼更新 `_ChoiceKillRun` 的 `plan_of`(身分、order 子集)與 `rid_map`;合併判讀 names 傳子集;新增 S23 |
| J6 | 覆蓋可信與只分析改到的類別矛盾、斷路器時序做不到、零專案類別的合理測試 | c4 c5 b11 | 專案類別有紀錄數由 lumos 用 Python 讀 exec 檔、對全部專案類別算,每支跑完當場算;只對 Robolectric 測試要求大於 0;斷路器在第 5 支 Robolectric 測試跑完當場判 |
| J7 | 續跑快取鍵少了壞法行、清檔清不到子資料夾、資源無上限 | c6 c11 b4 b6 b7 s5 s8 k5 k10 a6 | 每支測試開跑前刪掉 AGP 固定位置的舊覆蓋資料檔、跑完沒新檔記覆蓋資料沒產出;快取存每支測試的覆蓋資料檔(含 init script 版本),分析每次對當下壞法重做;擴充工作目錄規則到子資料夾,`choice-cov/` 只留最近 2 個 at_sha、`choice-layer/` 14 天;分析逾時 `max(60, 支數 × 0.5)` |
| J8 | cov_sha 讀端算不出、none 行補了測試仍帶過去 | c7 b10 i3 | `cov_sha` 改由 tests_sha、檔 blob、new_sha、init script 版本算,讀端都算得出 |
| J9 | 跳過集合只看最近一次 run、exhausted 沒有出口、無效只綁單檔 blob | c10 b9 k2 k3 | 跳過集合累積、綁檔 blob;檔改就重驗;別支檔改了時把舊的無效候選放進合批編譯當探針重驗、能編就記補償;exhausted 不擋、不需要放行 |
| J10 | 回退後舊程式把 via cov 存活帶過去、整段撤回的痕跡 | k4 k9 k12 | via cov 事件的 tests_sha 寫成 `cov:` 前綴,舊程式一定重跑;抽查判錯後那個 at_sha 不再判 none;撤回時同一提交 git rm 判讀檔資料夾 |
| J11 | 抽查順序、種子、預算 | s6 i9 b12 | 抽查在記任何 via cov 事件前決定、種子用 run_id、改跑吃剩下時限、跑不完留到下次;另抽 1 行 clause |
| J12 | reach unknown 顯示與重補、補跑路徑 | b8 i2 | unknown 也算有效(印覆蓋不明),只有暫時性原因重補;`--reach-only` 走 `cmd_guard_kill(prep_only=True)` |
| J13 | 每換提交重量、旗標沒定義、init script 內容與模組變體 | i4 i5 i6 b13 k7 | 寫明換提交就重量、等於合併快篩本來每次量的基準加三成;定義 `--no-cov`、`--no-compile-check`、`--cov-audit`;init script 開 enableUnitTestCoverage、寫進 wt.scratch;模組變體從 test 任務推;`compile_check` 布林可關 |
| J14 | 記帳細節、gov、推送閘去重、計數 | c13 i7 i8 i10 a3 b14 | 拿掉 reach_more、改 reach_n 與 `_gate_event_fit` 截斷旗標;gov 另列「依覆蓋判存活後改跑」;去重一次性多記一筆寫明;exhausted 計進 exhausted_n 不佔 ran;200 × 1024 位元組、引句上下限都用實字、條款號數字序 |
| J15 | 判讀檔與帳、清單遺失、撤回欄位、落點、最壞速度 | a7 a8 k11 s9 | 判讀檔沿用 `_note_audit_write_verdict`(帳單筆 4096 上限放不下全文);清單讀不到 rc2;撤回事件帶 reason;guard-kill 那篇寫準備物件 WHY 與 responsibility;實務隱患寫三種最壞路徑的上限 |

## 重現表

全部 66 條由編排者讀程式或對照計劃確認(HIT);s7 的引句「最後還原。」短於下限,快照〈用詞〉合批編譯檢查末句確有此字樣,HIT;無 MISS。

## 先查世界

PRIOR-ART: J1 編譯檢查失效開放——mutant schemata 與 METFORD 都以「原程式能編」為前提再加壞法(https://ar5iv.labs.arxiv.org/html/2210.17215 、https://arxiv.org/html/2501.02875v2 );本 repo 合併快篩的既有做法也是先量原版基準、原版紅就不判(`scripts/lumos` 的 `_kill_merge_base`)。採用:先編原樹當對照。
方向:對 — 先確認原版再判壞法是 schemata 與本 repo 合併快篩的共同順序(上兩個來源)。
PRIOR-ART: J3 量基準迴圈——沿用本 repo `_kill_merge_singles` 既有的預估收手(Systems/guard-kill 的 PITFALL「量基準把總時限吃光」),不另寫。
PRIOR-ART: 跑滿三輪的方向——審查一直卡在「可不可行、怎麼接」而不是目標時,用有時間上限的原型或 tracer bullet 讓程式回答比再寫一輪文字有效(https://amplitude.com/blog/2018/02/26/project-planning 、https://onebigfluke.com/2016/11/rigorous-design-documents.html 、https://lucasfcosta.com/blog/design-docs 、https://www.simonwillison.net/2024/Dec/15/preferring-throwaway-code-over-design-docs );原型不能代替設計決定(同上 onebigfluke)。採用:折完進實作,以驗收條款的測試先紅後綠、高風險代碼審看真程式碼。
方向:要換 — 從「再開一輪文字設計審」換成「折完進實作、由代碼審接手」,依據上列四個來源;已攤給使用者,使用者裁「折完改走原型(建議)」。
