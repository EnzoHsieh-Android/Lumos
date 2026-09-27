severity: major

# 筆記內容審_計劃 r2 外部審稿報告(整合/知識同步鏡頭)

審查範圍:`governance/review-reports/筆記內容審/r2-work.md`(凍結工作副本,177 行全讀)對照 `r2-delta.patch`(r1→r2 差異)與程式碼 repo(`scripts/lumos`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`、`docs/lumos-toolchain-knowledge/`)。逐節讀完,交叉引用逐一核對目標是否存在。

## F1 `_BOOKKEEPING_DIRS` 是四個以上消費者共用的常數,加資料夾的連帶效果沒分析也沒測

severity: major
blocking: 是 —— 這是一個會被寫死進條款(S17)並實作出來的改動,但它的真實影響面比 spec 描述的大,而且完全沒有任何條款去驗證「小改動閘/風險分級」這兩個既有消費者在加了新資料夾後行為是否仍正確,屬於「改了會動別的閘卻沒人測」的整合缺口。

spec 在〈做法〉第 3 節第 8 點只把 `_BOOKKEEPING_DIRS` 當成「代碼審簿記豁免」的旁支,回退段也只承諾「沒有判定檔就沒影響」:

引句:「判定檔資料夾加進代碼審的簿記豁免(`_BOOKKEEPING_DIRS`,它跟卷證目錄一樣是紀錄不是碼)」
引句:「簿記豁免多一個資料夾也不用退(沒有判定檔就沒影響)。」

但查程式碼,`_BOOKKEEPING_DIRS` 這個常數在 `scripts/lumos` 裡至少被四個地方共用,定義處自己的註解已經寫明「三個消費者共用這一組」(`scripts/lumos:20353`):
1. `_sc_changed_files`(小改動閘的改動清單過濾,`scripts/lumos:6237`)——決定哪些檔不算進「擴散/相對量」門檻。
2. `_stack_changed_ok`(pitfalls 的風險型樣掃描要不要看這支檔,`scripts/lumos:24738`)。
3. `_pitfall_tier`(改動風險分級 light/standard/high 的判準,`scripts/lumos:24750`)。
4. `_codeloop_record_valid`(S17 真正要用的那個,代碼審留痕祖先鏈的簿記豁免,`scripts/lumos:30387`)。

加了 `governance/note-verdicts/` 之後,依 spec 自己在〈實務隱患〉的估計「本 repo 幾乎每次推送都有新增筆記行,所以幾乎每次推送都要派判定者」,也就是「幾乎每次推送」都會有判定檔進這個資料夾——那麼消費者 1–3 的行為都會被這次改動悄悄影響:小改動閘的擴散/相對量門檻不再把判定檔算進去(可能讓原本會被判定「不算小改動」的一批變成「小改動」,因為判定檔的檔數/行數不計入了);風險低計劃走小改動閘放行後、可能因為附帶大量判定檔而更容易維持 tier=light。這三個既有消費者原本各自有自己的既有測試,但 spec 全篇只有 S17 一條條款([test:t_note_audit_codeloop_bookkeeping_and_order])驗第 4 個消費者,對第 1–3 個消費者「行為是否仍照原樣」完全沒有條款、也沒在〈回退〉裡承認需要回頭驗。「沒有判定檔就沒影響」這句話本身沒錯,但它掩蓋了「一旦這個閘實際運作,幾乎每次推送都有判定檔」這個 spec 自己承認的前提,讓讀者誤以為這個共用常數的擴充是無副作用的。

## F2 S17 要求 `code-loop pass` 印提醒,但這個子指令目前完全沒有 diff 範圍可用

severity: major
blocking: 是 —— 這是條款 S17 明文要測的行為([test:t_note_audit_codeloop_bookkeeping_and_order]),但所需的輸入(推送範圍)在現有指令介面裡不存在,且 spec 全文沒有一處說明要怎麼補這個輸入,屬於可執行性缺口。

引句:「`code-loop pass` 發現這個範圍還有待審筆記行時印一行提醒(不擋)」
條款原文:引句:「`code-loop pass` 在範圍還有待審筆記行時應印提醒、不擋」

查 `scripts/lumos` 的 argparse 定義(`scripts/lumos:32490-32491`):`pass`/`skip` 只註冊了 `--note` 與 `--repo` 兩個參數,沒有 `--diff`;對照 `check` 子指令同一段(`scripts/lumos:32495`)明確有 `--diff`。`cmd_code_loop` 裡 `pass`/`skip` 的實作(`scripts/lumos:30992-31001`)只呼叫 `_codeloop_write`/`_codeloop_gov_log` 寫入「本分支 HEAD 已過審」,完全沒有算任何 diff range,也沒有呼叫 `_codeloop_guard_verdict`(那支才有「跳 merge-base 推導範圍」的邏輯,是 `check` 專用的)。要讓 `pass` 印「這個範圍還有待審筆記行」,必須先讓 `pass` 拿到一個推送範圍——不論是新增 `--diff` 參數、還是內部另外推導 merge-base——spec 一個字都沒提,〈做法〉第 3 節第 8 點與〈回退〉第 3 點都只講「印一行提醒」,沒講這行提醒的範圍從哪來。這跟同一節其他地方(例如把「看哪支掛鉤」的參數明確列成待加的東西)的細緻度不一致。

## F3 完成審排除「已翻案(valid:false)」決策的機制沒有設計,共用行抽取函式沒有決策項目分組的概念

severity: major
blocking: 是 —— 條款 S3 明文要測「`valid: false` 的決策不應進」,但 spec 描述的共用資料結構(路徑、行號、文字、區塊、小標題)不含「這行屬於哪一條決策項目」,無法判斷該行所在項目的 `valid` 欄位,是可執行性缺口。

〈做法〉第 1 節:
引句:「★decisions 裡 `valid: false`(已翻案)的那幾條不進★——已推上去的決策被判推得出時,唯一合規的處理是翻案(`decision-supersede`),翻掉的就是歷史」

條款 S3:
引句:「`valid: false` 的決策不應進」

但同一節描述的共用函式回傳粒度只到「(路徑、行號、文字、所在區塊、所屬小標題)」,且明講:

引句:「所屬小標題=往上找最近一行 `#` 開頭的標題,summary 與 decisions 裡是欄名」

對 decisions 區塊而言「小標題」只會是欄名(例如 `content`),同一篇裡每一條決策的 content 行拿到的「小標題」都一樣,完全無法從這個結構分辨某一行 content 屬於哪一條決策項目、也就分辨不出那條決策的 `valid` 是不是 `false`。要做到 S3 要求的過濾,需要額外把每一行關聯到它所在的決策項目(項目的起訖行、`valid` 欄位),這在程式碼裡已有現成的結構化解析入口——`parse_decisions`(`scripts/lumos:12919`)與 `decisions_items`(`scripts/lumos:14088`),兩者都能給出每條決策的起訖行與欄位值。但 spec 全篇(含 PRIOR-ART)沒有一處提到要重用這兩支函式,也沒有描述任何等效機制;`cmd_decision_supersede`(`scripts/lumos:14814-14897`)本身也證實了問題確實存在:supersede 只在項目內插入 `valid: false`/`superseded_by`/`ended` 三行,`content:` 那一行文字原封不動留著——也就是說那條被判「推得出」的舊決策文字,在完成審時仍然會被 `_ns_regions` 標成 `decisions` 區塊裡的普通一行,若沒有額外的「屬於哪個項目」判斷,S3 描述的排除邏輯無從實作。

## F4(minor)〈實務隱患〉倚賴的 Issue REVISIT 仍指名已被取代的舊計劃

severity: minor
blocking: 否 —— 不影響機制本身正確性,只是一則交接動線上的死路,三個月後接手的人跟著連結走仍能靠目標節點頂端的「★已被取代★」提示改道,不會真的卡死。

spec〈實務隱患〉「資源併發」段:
引句:「所以 [[Issues/治理帳多個寫入者都沒上鎖]] 的 REVISIT(2026-10-11)要把第二層列為第一個受影響的使用者,接線前看那篇的結論。」

查 `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md:52`,該篇 REVISIT 原文仍是「另開計劃修,或併進 [[Projects/筆記不存程式碼推得出的事_計劃]]」——而 `docs/lumos-toolchain-knowledge/Projects/筆記不存程式碼推得出的事_計劃.md:3` 顯示該篇 `status: superseded`,且本 spec 自己在開頭就宣告是它的重寫稿(「★這篇是重寫稿★」)。spec 沒有同時把那個 Issue 的 REVISIT 動作句改指向 `Projects/筆記內容審_計劃`(現在唯一活著的落點),留下一句已經對不上現況的可執行指示,雖有舊節點頂端的取代橫幅兜底,仍是知識同步上的殘留。

## F5(minor)〈前身 r3 發現怎麼處理〉一句描述已被 r1 本身的修正推翻

severity: minor
blocking: 否 —— 只出現在回顧性質的歷史段落,不是條款或做法本身,做法第 3 節第 4 點與條款 S12 才是權威文字且彼此一致,不會誤導實作,但會誤導日後查〈前身 r3〉去理解「decision-amend 現在到底怎麼判 fetch 新鮮度」的人。

〈做法〉第 3 節第 4 點(現行、正確):
引句:「上次 fetch 超過 10 分鐘就拒絕並印 fetch 指令」

〈前身 r3 發現怎麼處理〉段落卻仍寫:
引句:「跟改名、分三種結果、印 fetch 距今」

「印 fetch 距今」是 r1 修正前的舊行為(只提醒、不擋),已被 r1 外家席的修正取代為「超過 10 分鐘直接拒絕」;〈審計修正紀錄〉r1 段也承認這條改法折入了(「decision-amend 要 10 分鐘內 fetch 過(外家)」),但〈前身 r3 發現怎麼處理〉這一句的措辭沒有跟著更新,兩處對同一機制的描述不一致。

## 逐節讀過、無 finding 的部分

- 開頭欄位、PRIOR-ART/RETIRE-IF/REVISIT:PRIOR-ART 對「連鎖帳本只借到『進版本控制的逐件檔』這個形狀」的說法查證屬實——`_ledger_append`(`scripts/lumos:15036-15052`)確實有 4096 bytes 硬上限且用 `O_APPEND`+單次 `os.write`,不適合裝一批可能上百行證據的判定內容,改用 `_write_lf`(`scripts/lumos:14146-14169`,暫存檔+`os.replace` 原子換名,且已有非 vault 用途的先例,例如 `.lumos/lint-waivers.json` 寫入,`scripts/lumos:21462`)是合理且查證得到的選擇。
- 〈判定者能不能用:小實驗〉表格數字內部自洽(55+13=68;53+2=55;9+4=13),與〈上線前校準〉四項達標門檻的引用一致。
- 〈做法〉第 1 節「上線點函式與截斷函式加『看哪支掛鉤』參數」的宣稱查證屬實:`_nodehome_golive`(`scripts/lumos:22943-22950`)目前把 `scripts/hooks/pre-commit` 寫死在 `git log -S<mark> ... -- scripts/hooks/pre-commit` 裡,確實還沒有「哪支掛鉤」的參數,是待加的東西,spec 沒有把已完成的工作講成還要做,也沒有相反。
- `_KNOWN_GATES`(`scripts/lumos:6599-6615`)目前還沒有 `note-audit`,只有 `note-shape`,跟 spec「閘名要登記」的待辦一致。
- Systems/筆記內容閘 現有 `about_code` 已經把 `scripts/lumos` 跟另外三支掛鉤/CI 檔一起列成自己的家,且正文另有一段用反引號寫「這篇管 `scripts/lumos` 裡的 note-shape 子指令……而它加的共用零件」——查 `_home_map_from_notes`(`scripts/lumos:22666-22679`)本來就允許同一支檔被多篇 Systems 節點以 `about_code` 認領(`homes.setdefault(k, []).append(rel)`,無唯一性檢查),doctor S9(`scripts/lumos:2189-2204`)擋的是「沒有登記在 about_code、卻用反引號寫別人家檔」的情況,不是「登記了就不准第二篇也登記」。所以 Systems/筆記內容審 另外把 `scripts/lumos` 也列進自己的 `about_code`、並改寫 Systems/筆記內容閘 的負責範圍句,跟每支檔有家現行機制不衝突,這點是本輪審查重點鏡頭之一,查證後判定：已讀,無 finding。
- 〈做法〉第 3 節第 6 點「check 只認被推送頂端提交裡的判定檔與治理帳」與 pre-push 現有排序(`home check` → `note-shape --diff` → …→ `code-loop check`,見 `scripts/hooks/pre-push:236-309`)一致,note-audit check 插入這個既有序列的位置合理,spec 沒有明文寫出要改 `scripts/hooks/pre-push` 這件事,但〈做法〉第 3 節第 6 點「跟 home check、note-shape --diff 並排」已足以讓實作者推出要改哪支檔,不算遺漏。
- 模型名比對(S6)、`_validate_repo_ref` 帶 `at_sha` 的用法(`scripts/lumos:19819-19848`)、`LOOP_ORCHESTRATORS`/`loop next --orchestrator` 的既有規矩,查證均與 spec 描述一致。
- 條款 S1–S16(除 S3、S17 已在 F2/F3 指出)的測試名與各自條款內容語意對得上,未發現懸空引用或編號對照錯誤;〈前身 r3 發現怎麼處理〉除 F5 那一句外,其餘段落引用的〈做法〉節次(第 1、2、3 節第 1/4/5/6/9 點、第 4 節、第 5 節)逐一核對都存在且描述相符。

## 實務隱患鏡頭(整合/知識同步角度,逐類自答)

- **簿記/紀錄目錄共用常數的擴散影響**:有,見 F1——`_BOOKKEEPING_DIRS` 是四個以上消費者共用的常數,新增資料夾的效果沒有被完整分析與測試覆蓋。
- **指令介面缺口**:有,見 F2——`code-loop pass` 沒有 diff 範圍輸入,S17 要求的行為在目前介面下無法直接實作。
- **決策生命週期與完成審的交叉**:有,見 F3——完成審排除已翻案決策所需的「決策項目分組」資訊,不在共用行抽取函式的回傳結構裡,也沒有替代方案。
- **知識圖譜交接動線**:有(輕微),見 F4、F5——一處外部 Issue 的 REVISIT 動作句、一處歷史回顧段落的措辭,分別因為本次重寫與 r1 修正而過時,但都不影響機制本身正確性。
- **每支檔有家規則衝突**:無——`scripts/lumos` 允許多篇 Systems 節點以 `about_code` 共同認領並各自寫清楚負責範圍,是既有機制且已有先例(Systems/筆記內容閘 本身就是這樣認領的),本次新增 Systems/筆記內容審 認領同一支檔、改寫舊節點負責範圍句,不構成違規。
- **先內容審再代碼審的順序**:無新增隱患——pre-push 既有排序已經是「圖譜健康/家/形狀類檢查」在前、「代碼審 code-loop check」在後,note-audit check 插入同一序列位置合乎既有慣例,唯一的可執行性缺口已併入 F2。
- **外送模型/資料外洩**:無——spec 已限定判定者與編排會談同一家(claude→opus、codex→Codex 既有審查席),不引入新供應商,PRIOR-ART 與〈實務隱患〉「對外送出」段落描述與現有派工慣例一致,查無新增風險未被承認。
- **治理帳寫入頻率/併發**:無新增隱患——spec 已在 r1 修正中承認「治理帳寫入頻率會變高」,並把最終判斷交給 `[[Issues/治理帳多個寫入者都沒上鎖]]` 的 REVISIT(該連結本身的過時問題已列入 F4,不重複列)。

---

本輪最重 severity 為 major,blocking 條數 3。
