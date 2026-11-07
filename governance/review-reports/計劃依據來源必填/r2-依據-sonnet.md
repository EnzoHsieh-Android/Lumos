severity: major

第一輪依據席 10 條的核對結果:F1(推送前重查)、F2(三處分工)、F3(機制定義)文字上有補,但 F1 的補法有洞,見下方 F1 與 F5。F10(lands_in 補家)沒有真的修好,見 F4。型錄計數我重跑指令,473/140/29/324 對得上。計劃筆記提到的 `check.py` 的 `catalog_problems`、`_MAIN_ROW_RE`、`_cells` 都存在,185 篇計劃的數字也對。

我實際打開了 6 個網址:Rust RFC、ADR、ozimmer、Tricorder PDF、git-rebase、Wikipedia 都打得開,支持度見 F6。

F1
severity: major
blocking: 是
引句:「對這次範圍碰到的每一份新計劃,用範圍 1 同一支判定函式再查一次〈依據來源〉」
問題:計劃說推送前重查跟預期值表簽核「同一個出口」,但那個出口有狀態過濾。
- `_spec_gate_push_scan` 的 `_live` 只放行 `doing`,或「這次推送改到的 `done`」。
- 預期值表那道 `_expected_push_one` 只對 `_live` 的計劃跑。`status: todo` 的新計劃(本計劃自己就是 todo)整個被略過。
- 規格閘過後把〈依據來源〉整節刪掉,只要計劃還是 todo,推送前不擋。
- 另外,`_spec_gate_push_candidates` 挑「連到被碰 Systems 節點」的計劃時也只收 `doing`。
- 計劃範圍 2 與 S3 都沒寫要查哪些狀態,範圍 3 的健檢卻列 todo 與 doing,兩處不一致。照字面「同一個出口」實作會漏掉這一類。
file: `scripts/lumos:16509`(`_live` 定義在 `_spec_gate_push_scan` 裡)、`scripts/lumos:15788`(只收 doing)

F2
severity: major
blocking: 是
引句:「舊計劃 → 印一行提醒,不擋。」
問題:計劃要求別人「一個機制一行」,自己的〈依據來源〉表卻漏了正文裡幾個可被單獨質疑的選擇,對照〈用詞〉的「機制」定義(判法、門檻、預設值、擋或不擋、插入位置、格式、刻意不選)。漏的有:
- 舊計劃只提醒不擋(而不是回溯補寫或照擋)。
- 範圍 4、5:為什麼改紀律範本與兩本手冊、加在哪一段。
- 三處依據紀錄的分工。
- 表頭固定為「機制|依據|出處」三欄。
- 擋下留帳帶格子原文前 200 字。
- 健檢不算進問題數、不改退出碼。
- 型錄只印前 20 個編號、「只有網址沒有〔查證〕也算未查證」。
- 〈不做〉裡「不回頭改已結案的計劃」。
這跟第一輪「機制定義」那組是同一類洞。計劃自己宣稱機器判不出,要靠審查席點名,所以這裡要點名。

F3
severity: major
blocking: 是
引句:「網址會變、連網會讓規格閘離線跑不了,也讓同一份計劃今天過明天擋」
問題:這一列(網址只驗格式不連網)的「出處」欄引了使用者原話「你的標準、最佳寫法來源要有依據,不要你自己寫」。
- 那句話講的是型錄來源要有依據,不支持「不連網」這個設計選擇。依據欄自己也承認,算是出處不支持說法。
- 「網址會變、離線跑不了」沒有任何出處。
- 日期也對不上:同一句話,計劃範圍 6 與 `Systems/kotlin規則包` 的 WHY 都記 2026-11-05,這一列寫 2026-11-06。〈用詞〉要求的是出處讓人查得到,日期錯了就查不到。
file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:19`(WHY 的 `[出處:2026-11-05 使用者…]`)

F4
severity: minor
blocking: 否
引句:「Systems/convergence-evidence-gate」
問題:第一輪 F10 沒有真的修好。r1-intake 說 `skills/lumos-design-loop/SKILL.md` 與 `scripts/templates/graph-discipline.md` 的家分別是 `convergence-evidence-gate`、`lumos-refcheck` 與 `lumos-cli-lifecycle`,但這三篇的 `about_code` 都沒列這兩支檔。
- 我跑了 `lumos impact --file`:`graph-discipline.md` 與 `design-loop/SKILL.md` 都沒有「這支檔的家」,只有 `code-loop/SKILL.md` 有家(`每輪修補差異派工`)。
- `lands_in` 的 `convergence-evidence-gate` 與 `lumos-cli-lifecycle` 因此不是範圍 4、5 任何檔的家。
- `.md` 不在「需要有家的程式檔」副檔名清單裡,所以不違反鐵則 5。
- 但計劃沒交代這兩篇各自要寫什麼,接手的人不知道要寫哪一篇。
- 兩篇各帶 ★INVARIANT★(`lumos-cli-lifecycle` 的「re-inject 只覆蓋 sentinel 之間」、`Systems/design-loop` 的處置閘第五步),`Systems/design-loop` 沒列進 `lands_in`,計劃也沒說範本改動跟它們的關係。
file: `docs/lumos-toolchain-knowledge/Systems/convergence-evidence-gate.md:8`、`docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:8`

F5
severity: minor
blocking: 否
引句:「審查迴圈收貨紀錄(rN-intake.md)裡的〈先查世界〉是每一輪修補前查證的過程紀錄(照留,屬卷證)」
問題:新的「三處分工」跟現行手冊只對得上一半。
- 設計審手冊寫的是「在 rN-intake.md(或計劃的審計修正紀錄) 寫〈先查世界〉」,計劃只講 rN-intake.md,漏了後一個位置。
- 照做的人若把〈先查世界〉寫在計劃的審計修正紀錄裡,同一份計劃就有 `PRIOR-ART:` 行、〈先查世界〉、〈依據來源〉三處同內容。
- 紀律範本的 `PRIOR-ART:` 原意是「設計動筆前先問世界(最小解在哪一層、世界解過沒)」,計劃改稱它是「整份設計查世界的摘要」。
- 本計劃自己就重複寫:`PRIOR-ART:` 行裡的 Rust RFC、ADR、Wikipedia、Tricorder 四個網址,在〈依據來源〉表又各寫一遍。分工沒說這種重疊該不該有。
- 範圍 5 要求「同一次在計劃〈依據來源〉補」,但代碼審迴圈審的是分支程式,不一定有計劃筆記,計劃沒講這種情況。
file: `skills/lumos-design-loop/SKILL.md:41`、`skills/lumos-code-loop/SKILL.md:50`

F6
severity: minor
blocking: 否
引句:「架構決策紀錄一份只記一個決定;重大決策的定義(改起來代價高)不拿來當門檻」
問題:有三處出處與說法略有出入,都是措辭精度。
- 這一列(「機制」的粒度)引 ozimmer 說「一份只記一個決定」,但那頁沒有明寫這句。
  - ozimmer 只引了 Fowler、Booch 的「重大決策」定義。
  - 「一份 ADR 只描述一個重大決策」是 Nygard 那頁原文。
- PRIOR-ART ② 說 Nygard 把 Context「列為必填」,原文沒有 required 字樣,只說它是 ADR 的一個部分。
- 依據來源表說可查證性「支持與否只有人判得出來」。Wikipedia 其實給了「明確寫在來源裡」的測試,並用共識處理爭議。計劃「機器不判」的設計不受影響,但這句話不是政策原文。
Rust RFC、Tricorder(not useful 低於 10%)、git-rebase(rebase 保留作者日、提交日變當下)的說法與原文相符。
file: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions 、 https://ozimmer.ch/practices/2021/04/23/AnyDecisionRecords.html 、 https://en.wikipedia.org/wiki/Wikipedia:Verifiability

F7
severity: minor
blocking: 否
引句:「注入到消費專案的 CLAUDE.md 照既有的重新注入流程。」
問題:範圍 4 要往每回合注入的紀律範本再加一句。
- 範本現在 13416 bytes,已超過瘦身基準 5256 的 150%(門檻 7884),`lumos doctor` 已在警告。
- `Systems/lumos-cli-lifecycle` 的 WHY 寫「細節搬進 skill 的 reference.md、範本只放表與一個例子」。
- 計劃沒交代為什麼這句要放進常駐範本、不放 skill,也沒說會不會讓警告更嚴重。
file: `scripts/lumos:3790`、`scripts/test_lumos.py:32681`

總結:最嚴重是推送前重查會漏掉 todo 與未被碰到的計劃,加上自己的〈依據來源〉表漏列機制、一列出處不支持還寫錯日期,會擋 3 條。
