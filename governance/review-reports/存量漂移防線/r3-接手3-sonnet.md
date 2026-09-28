severity: major

## F1 c4 的「不含工作樹」排除規則會漏掉考卷自己的 E3 正例

severity: major
blocking: 是 — 照做法第 1 節字面實作 c4(單純字串排除「工作樹」),考卷甲組 6 題裡的 E3(唯一測 valid_under/c4 的題)會被自己的排除規則吞掉,永遠判不成立,直接做出「c4 系統性漏抓最常見寫法」的錯系統。
引句:「c4 前提寫「還沒提交」**:`valid_under` 含「未提交」「還沒提交」「uncommitted」任一詞(不含「工作樹」——「釘在某提交的乾淨工作樹」是合法的可重現寫法)。只列出。」

1. 做法第 1 節第 4 點把 c4 寫成:valid_under 含「未提交/還沒提交/uncommitted」任一詞才算成立,但**只要整句裡出現「工作樹」三個字就整句排除**(逐字讀法:排除條件是「不含『工作樹』」這個子字串,不是「排除『乾淨工作樔』這個特定片語」)。
2. 考卷 `governance/eval/drift-exam/rtb-2026-09-28.json` 的 E3 是甲組(mechanism=3)唯一走 c4/valid_under 這條線的題(其餘 A4–A6、E1、E2 都是守衛紀錄/狀態欄位,不碰 valid_under)。我在唯讀複本 `rtb-exam` 上用 `git -C rtb-exam show b2fc512:docs/rtb-production-agent-demo-knowledge/Verification/Phase14增量2b驗證紀錄.md` 取出原文第 5 行,一字不差是:「valid_under: 僅 Phase 14 增量 2b 本工作樔(未提交、未過代碼審);全套測試、宣稱驗證器、ruff、mypy 與 Phase 13 評估 72 筆錄製離線重播;入庫展示錄製因政策升版有 8 筆模型說明找不到錄製」——同一句裡「未提交」跟「工作樹」同時出現,是很自然、很常見的寫法(講「這結論只在這個還沒提交的工作樹上成立」本來就會兩個詞一起講)。
3. 我另外查了 plan_refs 指的計劃 `Projects/RTB_Phase14正式規則照九條判斷_計劃.md` 在 b2fc512 當時的 status,是 `doing`(`git -C rtb-exam show b2fc512:docs/rtb-production-agent-demo-knowledge/Projects/RTB_Phase14正式規則照九條判斷_計劃.md` 第 3 行),不是 done/superseded,所以 c3(計劃收尾了、驗證紀錄還待定)也接不住這一題——E3 真正能被設計接住的入口只有 c4。照做法第 1 節第 4 點字面實作,這一句因為含「工作樹」而整句被排除,c4 判不成立,E3 這一題會漏(考卷甲組的正例直接漏一題)。
4. 條款 [S7](`governance/review-reports/存量漂移防線/r3-snapshot.md:132`)寫的排除範圍其實比做法窄:「c4 不應把「乾淨工作樹」當成還沒提交」——是針對「乾淨工作樹」這個特定片語(意指「釘住某個提交的乾淨工作樹」這種合法、可重現的講法本身根本不含「未提交」等三個詞,不會誤觸發,所以其實不需要另外排除),不是「valid_under 只要出現『工作樹』兩個字就整句放過」。做法第 1 節第 4 點的寫法比 S7 的意圖寬太多,兩處對「排除什麼」的描述不一致;一個沒有上下文、只照做法字面實作的人會做出 S7 沒有要求、而且會弄丟考卷正例的排除規則。
5. 這條排除規則本身要防的案例(「釘在某提交的乾淨工作樔」)其實從來不會觸發「含未提交/還沒提交/uncommitted 任一詞」這個前提——因為那句話根本沒有那三個詞——所以這條排除對它要保護的案例是多餘的;唯一會被它動到的,是像 E3 這種「未提交」與「工作樔」同句出現的真實漂移句,而那正是要抓的。

## 其餘章節

已讀,無 finding:frontmatter(`lands_in`/`related`)、〈範圍〉、做法第 0 節(條件文法、REVISIT 共用判定、`lumos drift` 指令族、開關與逾時語意)、做法第 1 節其餘各點(guard settle 改寫、補救路徑、`lumos set` 連帶待辦、c1/c2/c3/c5)、做法第 2 節(when 鍵判定、評估規則、擋新寫散文回頭條件、跟筆記內容審的分工)、做法第 3 節(考卷與考法)、做法第 4 節(掃圖譜與修復、接線門檻)、〈落點〉、〈回退〉、〈實務隱患〉、〈誠實界線〉、〈審計修正紀錄〉、〈考試結果〉/〈修復結果〉占位段。

逐項查證重點(supporting evidence,非另立 finding):
- `lands_in`/`related`/〈落點〉點名的節點(`Systems/筆記內容閘`、`Systems/筆記內容審`、`Systems/guard-kill`、`Systems/reversibility-governance-ledger`、`Issues/治理帳多個寫入者都沒上鎖`、`Issues/存量筆記漂移三種機制_rtb根因回饋`、`Projects/舊句偵測實驗_計劃`、`Projects/筆記內容審_計劃`、`Projects/筆記形狀擋_計劃`、`Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋`、`Projects/先問世界_存量掃描裁定`)在 `docs/lumos-toolchain-knowledge/` 裡全部存在;唯一「新開」的 `Systems/存量漂移守衛` 確認目前不存在,跟宣稱一致。about_code 要指 `scripts/lumos` 這支單檔巨石,查了現有 44 篇節點已經這樣做(如 `Systems/筆記內容審.md`、`Systems/reversibility-governance-ledger.md`),不是新問題。
- PRIOR-ART 列的借用函式(`_lens_push_base`、`_nodehome_clamp_base`、`_nodehome_reader`、`_nodehome_list`、`_nodehome_is_test`+`_nodehome_layout`、`edit_fm_sync_status_tag`、`atomic_write_verify`、`_vault_write_lock`(可重入,已讀 `scripts/lumos:14251-14276`)、`_visible_lines`(只剝圍欄,不剝表格/行內程式碼——條件標記的可見行判定屬於自建的「條件語法與評估」,不是靠 `_visible_lines` 單獨做到)、`_nodehome_code_kind`、`_lens_git`(20 秒逾時,`scripts/lumos:29257-29259` 核對過))全部存在且語意跟 PRIOR-ART 的敘述吻合。
- `guard plan`/`guard settle`/`guard abandon`/`guard audit` 現況(`scripts/lumos:11500-11940,12464-`)核對過:四種固定句型逐字比對、`guards` 欄位在守衛紀錄本身(不在家筆記)、`_guard_home_of` 只取清單第一項(對應〈誠實界線〉「settle 只處理第一篇家筆記」),`cmd_set`/`_vault_write_lock` 的巢狀行為與 S4/S5 的寫入順序敘述一致。
- 考卷與改寫檔:33 題、`exam_event` 五種分布(current_state 12、mechanism1_experiment 9、probe 6、commit 4、status_replay 2)、`mechanism` 分布(1→9、2→5、3→6、None→13)、README 的「漂移 20(①9/②5/③6)、屬實非漂移 10、不成立 3」都跟 JSON 逐項核對一致;`rtb-2026-09-28-probes.json` 6 題(A7/B1/B2/B3/B4/B5)跟做法第 3 節描述一致。在唯讀複本 `rtb-exam`(頂端 067f005,跟 README 宣稱一致)上重驗多筆失效提交:`ef10bc7` 把 Phase12 計劃 status 從 doing 改成 done(對應 E1)、`f183cd8` 新建 Phase12 計劃且 status 就是 doing(對應 B3)、`0ffba7d` 在 `src/rtb/executor/execution.py`(不是稽核原寫的 guardrails.py)新增 `MAX_INCREASE_NUMERATOR`(對應 A7/B4,佐證 README 更正紀錄)、`8ff8c95` 新增 `src/rtb/analyzer/runner.py`(對應 B1/B2/B5)、`e8ea7d0` 把七篇事故驗證筆記從長檔名改短名(佐證 A4/A5 的 `note_at_event`)。全部命中,沒有跟原始碼或 README 對不上的數字或分類。
- 〈審計修正紀錄〉r2 折入清單逐條核對:條件標記正式文法、只在正文/摘要可見行生效、REVISIT 共用判定認得列表/引用記號、「同一行」判法、check 只評估這次推送可能改變結果的條件、判不了算要處理、表態綁路徑加原文加種類、c1 加 WHY 與第四句、c3 排除空/壞 plan_refs、新增 c5、when-status 筆記不存在算不成立、when-test 先算版面、第二層排除條件式回頭條件、E5 一律印條數、`lumos set` 只給檢視指令、回退節改寫(手改撤銷 settle、不准單獨還原守衛紀錄、還原順序、用 scan 清點)、考卷 B3 改成 f183cd8、exam_event 對齊四種考法、lands_in 加 guard-kill、〈落點〉新增、併發段改寫、多分支時間改寫——都已落進正文對應段落,沒有發現「口頭折入但正文沒改」的漏網。判錯項(邊界 F7,家筆記 vs 守衛紀錄)也已正確寫進〈誠實界線〉,標成既有限制而非要修的 bug,跟 r2 說明一致。
- 跟既有節點宣稱是否衝突:`Systems/guard-kill` 的 RULE([since:2026-09-22])只講「威脅模型防忘記不防繞過」,跟本計劃改寫預告句/加補救路徑不衝突,是同一機制的加強,不影響原 RULE 的判準。`Systems/reversibility-governance-ledger` 的決策 d3(「doctor 是治理帳唯一新寫者」)跟現況(`_gate_event` 已有多支呼叫端)確實不一致,但這是既有落差,`Issues/治理帳多個寫入者都沒上鎖` 已經記錄且本計劃的〈實務隱患〉已明講表態檔與 drift-check 事件會在那篇 2026-10-11 回頭看時一併算入——屬於已知且已排定處理,不算本計劃新引入或新破壞的衝突。

最嚴重 major,blocking 共 1 條。
