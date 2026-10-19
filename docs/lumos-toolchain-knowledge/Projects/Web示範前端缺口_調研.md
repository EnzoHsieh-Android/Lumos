---
type: project
status: doing
created: 2026-10-15
updated: 2026-10-15
tags:
  - type/project
  - status/doing
  - scope/ux-docs-hygiene
---
# Web示範前端缺口_調研

> 白話:一次 React 前端示範(order-web,Vite + React + Vitest + Playwright)走完整套 lumos 流程,沿路記下工具不合前端的地方。三份流水帳共 55 條(前端示範 F1–F31、後端回顧 B1–B12、Web 收尾 W1–W12),逐條到主線程式重現或讀碼確認後合併成下面 45 列,每列標出要落到哪篇計劃。這篇只是比對表與分流,不含做法;做法與驗收條款在各計劃裡。

PRIOR-ART: 沿用既有「示範回饋 → 比對表 → 分組開計劃」的做法([[Projects/示範回饋小修_計劃]] 那次是後端示範);不另建流程。
RETIRE-IF: 表上所有「仍存在」的列都在對應計劃裡結案或明講不做之後,這篇改 done,只留作歷史比對。

## 怎麼讀這張表

- 「主線現況」以 2026-10-15 主線程式為準;「重現」是在臨時的 Vite + React 骨架(跑過 `lumos init`)實跑指令得到的,「讀碼」是讀程式推得的。原始流水帳與重現用的臨時骨架不進 repo。
- 原表的程式行號引用已拿掉(行號會漂;要定位請照函式名去 `scripts/lumos` 找)。
- 「組」:A 測試名比對、B 前端技術棧、C 前端知識、D 風險關鍵字誤判、E 記帳與迴圈工具、F 筆記指令、G 健檢與家、H 規格閘、I 跨 repo、J 不改。
- 落點:A → [[Projects/測試名收自由字串_計劃]];B → [[Projects/前端框架從vue分出_計劃]](該篇 todo,開工條件「有 React 專案真的要接」這次已滿足);C、D → [[Projects/前端知識與風險詞_計劃]];E → [[Projects/記帳與迴圈工具小修_計劃]];F、G、H → [[Projects/筆記指令健檢與規格閘小修_計劃]];I、J 不改,理由寫在該列。

## 比對表(45 列)

| 編號 | 一句現象 | 既有記錄(節點、status) | 主線現況 | 組 | 落到哪篇計劃 |
|---|---|---|---|---|---|
| W1 | `[test: 中文句子]` 懸空,規格閘仍印「條款綁定 ✓」 | 多平台合約測試綁定_計劃(done)與 `Systems/test-profile-multiplatform`(done):定為「識別字名才可綁,含空白 NO MATCH」,是刻意設計 | 仍存在(部分緩解)。重現:兩條條款其中一條寫中文,印出「✓ 2 條全標(…懸空 1 只提醒不擋…)」,有顯示懸空數。逃生口 `test.method_regex` 只在單平台設定有效;`load_platforms`的多平台路徑不收,而 `init` 骨架預設就是多平台格式。2026-10-15 已由本列落點的計劃處理(句子名可綁、懸空印 ⚠、多平台逃生口) | A | [[Projects/測試名收自由字串_計劃]] |
| F1 + W7 | `init` 推測棧:vitest 沒有、eslint 沒偵測 | 消費專案接入靜默失效_計劃(doing):已做 init 寫設定骨架;沒有 vitest/eslint 專屬記錄 | `.tsx` 已算進推測,重現印「看到 3 個 .tsx 檔(TypeScript / React)」。run_cmd 仍是 `npx jest -t {method}`(`node-vitest` 只是別名)。`doctor` 仍說「沒接 linter」,不認 `eslint.config.js` | B | [[Projects/前端框架從vue分出_計劃]] |
| F2 + W2(+F10 後半) | 沒有 React 慣例 skill;`.tsx` 被當 vue,拿到 vue 效能題與 vue-idioms | 前端框架從vue分出_計劃(**todo**)。開工條件「有 React 專案真的要接」,這次示範已滿足;REVISIT 2026-12-29。代碼審前後端角色鏡頭_計劃(doing)d3 也把 React 另案 | 仍存在。`ls skills` 無 react-idioms。`_stack_key_for_file("src/App.tsx")` 回 `vue`(`_NODE_FRONTEND_MARKERS` 含 react,都歸 vue);`pitfalls` 實測列出 `[vue 效能檢核]` | B | [[Projects/前端框架從vue分出_計劃]] |
| F3 | `new project` 名稱沒有 `_計劃` 後綴,工具不提醒 | 示範回饋小修_計劃(doing)S1;測試 `t_new_project_warns_missing_plan_suffix`(`scripts/test_lumos.py`) | **已修**。重現:`lumos new project 搶購2` 印「提醒:計劃筆記的慣例是 Projects/<主題>_計劃…」與重建指令。該計劃雖 doing,程式已落地 | F | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| F4 | 需求風險面全是後端角度,前端狀態、裝置、無障礙、前端效能預算都沒有 | 示範回饋小修_計劃(doing)S2 只補後端向的 req-scale、arch-sync;`Systems/情境出題`(doing) | 仍存在。`_REQUIREMENT_FACETS`無前端面。只有代碼審角色卡有 fe-states、fe-a11y,不在需求或設計階段 | C | [[Projects/前端知識與風險詞_計劃]] |
| F5 + W3 | 「送出」「PAYMENT」被判金流、對外送出,風險高 | 雙向門放行_計劃(doing)已記「關鍵字表粗,『當送出表單』被判對外送出,不改表」;規格閘不把不做節的詞算進風險_計劃(doing)只排除「## 不做」節;`Issues/門掃描詞表沒收常見寫法`(open,反向:漏判) | 仍存在。`_door_keyword_hits`對「請求送出時刻記錄」「按鈕再按也不會送出第二個請求」都回 `對外送出`,「ORDER_PAYMENT_TIMEOUT」回 `金流`。規格閘實測判高 | D | [[Projects/前端知識與風險詞_計劃]] |
| W4 | pitfalls 不對題:e2e 腳本的 SQL 問交易包裹,fetch 當成 vue-reactive | 無專屬記錄(`Systems/效能檢核目錄` done 為題庫說明) | 仍存在。實測 `scripts/e2e.sh` 含 INSERT 被問「[併發] 寫入有沒有交易包裹?」,`src/api.ts` 的 `fetch(` 被標「這是 vue-reactive 那題的做法」。graph-rename.sh 當對照這條沒重現(判不出,屬示範專案環境) | D | [[Projects/前端知識與風險詞_計劃]] |
| F6 | `已排除:金流(理由)` 寫錯格式,lint 沒先唸 | 無 | 仍存在。重現:寫 `已排除:對外送出(只呼叫自家 API)`,`lumos lint` 完全不唸,到 `spec-gate` 才說「缺已排除行」 | H | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| F7 | 目標架構只有 DDD 範本,前端無 | DDD目標架構範本_計劃(done) | 仍存在。`skills/lumos-project-notes/commands/` 只有 `target-arch-ddd-template.md` | B | [[Projects/前端框架從vue分出_計劃]] |
| F8 + B6 + W8 | `summary-line` 不能新增摘要行,新節點樣板只四個佔位行 | 改摘要單行的指令_計劃(done)明列「不做:插行、改前綴」;`Systems/lumos-cli-write` | 仍存在(刻意不做)。`lumos summary-line --help` 只有換片段或刪片段,新片段不准含換行 | F | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| F9 | refcheck 把計劃要新建的路徑判 missing | `Systems/lumos-refcheck`(done)只核對存在 | 仍存在。重現:`refcheck` 對 `src/api/orders.ts`、`src/api/` 回 `✗ missing`,無「將新增」寫法 | G | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| F10 + F19 | 設計審五鏡頭是後端語彙,lumos 自己預先指出 0 條前端發現 | 代碼審前後端角色鏡頭_計劃(doing):角色卡只進**代碼審**正確性席 | 仍存在。`skills/lumos-design-loop/templates.md` 的角色卡在 §3 代碼審,設計審 §1 沒有;同檔設計審的席位立場段仍是後端語彙 | C | [[Projects/前端知識與風險詞_計劃]] |
| F11 | `spec-freeze` 順序(先前掃排乾再凍),`loop next` 首輪不提醒 | 無 | 仍存在。重現:`loop next` 對新編號首輪(`--tier standard`)輸出無任何順序提醒 | E | [[Projects/記帳與迴圈工具小修_計劃]] |
| F12 | hook 只看會談目錄,審別的 repo 時固定席附不上 | 派工鏡頭可指定目標repo_計劃(doing,2026-10-14);派工鏡頭跨repo不再靜默_計劃(done) | **部分已修**。同 repo 的另一工作樹已可用 `lumos spec-freeze` + `<完整sha>:<路徑>`(`spec-freeze` 指令說明、`spec_commit` 在主程式共 23 處)。完全不同的 repo 刻意不支援,仍只附說明行,本次示範情境(會談在 A、審 B)仍存在 | I | 不改:同 repo 另一工作樹已可用 spec-freeze 加完整提交編號附上固定席;完全不同的 repo 是刻意不支援(派工鏡頭可指定目標repo_計劃),示範情境(會談在 A、審 B)屬這一類 |
| F13 | 回應亂序、卸載後計時器、時鐘偏快、輪詢壓力、冪等鍵歸屬,lumos 都沒提示 | 同 F10 | 部分。`_ROLE_CARDS`有 fe-race(亂序)、fe-unmount、fe-states,但只進代碼審。時鐘偏快、輪詢退避、換使用者冪等歸屬沒有;設計審與需求面都沒有 | C | [[Projects/前端知識與風險詞_計劃]] |
| B1 + B11 | 風險低計劃實作後才跑規格閘會擋;`doctor` 規格閘欄一直顯示紅 2/綠 0 | 雙向門放行_計劃(doing)定義「新行為各自紅」 | 仍存在。`_spec_gate_print_twoway`對風險低要求至少一條紅;風險高只印不擋。`doctor` S14 取「最近一次跑的結果」(起),不重跑就停在紅 | H | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| B2 | 計劃改 done 後,推送閘不再重跑留痕測試 | 無 | 仍存在。`_spec_gate_push_scan`只對 `status == "doing"` 且有風險低留痕的走全套 | H | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| B3 | 規格閘留痕在被 gitignore 的本機帳,乾淨 clone 沒有 | `Systems/loop-convergence-recording`(done)記了 kind=spec-gate 寫進 canary 帳 | 仍存在(未做乾淨 clone 實跑)。`init` 產的 `docs/.gitignore` 忽略 `.canary-log.jsonl`(`vtest/docs/.gitignore` 實證);推送掃描「沒留痕就不跑」 | H | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| B4 + B5 | 查不到檔的家;`impact --file` 對 about_code 檔回 0 筆 | 推筆記認家_計劃(doing)、每支檔有家_計劃(doing) | **已修**(用 impact)。`lumos impact --file scripts/hooks/pre-push` 印「這支檔的家 (5)」。沒有專用「查家」子命令,`home` 只有 `check` | G | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| B7 | `set` 說明沒列可改欄位(含 responsibility) | 無 | 仍存在(輕微)。`lumos set --help` 無欄位清單;錯誤訊息才列 `SCALAR_KEYS`(含 responsibility) | F | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| B8 | 只改 about_code 或負責範圍,`home check` 仍說「家沒動」 | 每支檔有家_計劃(doing);只換測試綁定不算寫說明_計劃(done)只豁免測試綁定 | 仍存在。重現:改 `src/App.tsx` 並 `set 畫面 responsibility`,`home check --staged` 仍印「它的家 Systems/畫面 這次沒動」。「一檔兩聚合只能一個家」沒測 | G | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| B9 | `home check` 不帶參數沒預設 | 無 | 仍存在。實跑印「擋下:lumos home check 要帶 --staged 或 --diff」 | G | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| B10 | Kotlin/Spring 後端被問 Compose、Android 冷啟動題,角色「後端 0 支」 | 代碼審前後端角色鏡頭_計劃(doing):Kotlin 後端判不出為**刻意**(「寧可不附」);Java補棧_計劃(done)只處理 Java | 仍存在。實測 Spring 的 `.kt` 檔 pitfalls 列出 `[kt 效能檢核]` 的 Compose、洩漏、啟動題,角色「後端 0 支、判不出 1 支」。棧別題只看副檔名,與 W2 同根 | B | [[Projects/前端框架從vue分出_計劃]] |
| B12 | `set`/`append` 不更新 `updated` | 提交時自動更新筆記日期_計劃(done):Enzo 先裁自動改,設計審後改裁「健檢列出加一鍵修」 | 已決定不自動(`lumos updated-sync` 與 `doctor` U 段存在)。`_cmd_set_locked` 只改指定欄位 | J | 不改:已裁定不自動更新 updated(提交時自動更新筆記日期_計劃:先裁自動改,設計審後改裁健檢列出加一鍵修),lumos updated-sync 與 doctor U 段已有 |
| F14 | `append lands_in "[[Systems/x]]"` 照收 | 筆記欄位關卡補齊_計劃(done)S10 | 部分已修。重現:`append` 仍收,`lumos lint` 現在警告「lands_in 這幾項不是 Systems/<名稱> 的純字串」(warn 不擋);寫入端仍不擋 | F | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| F15 | 條款「當…時應已有…;之後…」被處置閘判缺「應」,規格閘放行 | 規格落成可驗收條件_計劃 | 判不出。兩道共用 `_clause_check`,差別只在 `grammar` 旗標。比對時造的同型句 `_clause_grammar` 全回 True,未重現 | H | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| F16 | `--accepted-set none` 被當 id「none」 | design-loop重設計_實作計畫、`Systems/finding-refute` 只描述集合語意 | 仍存在。`_ids`只把空字串當空集合;只有 `--refuted-set`與 `--regression-set`認 `none` | E | [[Projects/記帳與迴圈工具小修_計劃]] |
| F17 + W9 | 「還沒/尚未」現況句提醒把 UI 狀態句當成會過期的現況 | 筆記形狀擋_計劃(done) | 仍存在。重現:`FACT:載入中(第一次還沒回來)時…` 與 `畫面還沒重繪前…` 都被印「提醒:…新寫了 2 行『還沒有/尚未…』」(`note_shape.negation=warn`,不擋,可關) | F | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| F18 | e2e 一族(埠、程序、Vite 重用、收尾)沒有任何檢核題 | test-layers軟提醒_計劃(done)只分單元、整合、UI | 仍存在。`skills/` 與 `test-quality-standard.md` 無 e2e 起停段 | C | [[Projects/前端知識與風險詞_計劃]] |
| F20 | 設計審帶 `--regression-set none`,工具不擋也不提醒 | 代碼審修正關卡第0步_計劃(done):代碼審 2 輪起選填;`Systems/代碼審修正關卡`(doing) | 仍存在。對任何迴圈都收 `none`;設計審手冊不要求,工具也不問 | E | [[Projects/記帳與迴圈工具小修_計劃]] |
| F21 | `code-loop dispositions` 的 evidence 給清單,錯誤訊息看不出型別 | 無 | 仍存在。`str(ent.get("evidence"))` 把清單變字串,再被當 `path:line` 切,訊息是「evidence '[…]' 切不開」 | E | [[Projects/記帳與迴圈工具小修_計劃]] |
| F22 | 記帳後改 intake,指紋不符,記帳時沒提醒不能改 | `Issues/記帳後改留痕格式讓回放永久紅`(open,相鄰但不同:談格式) | 仍存在。`canary record` 收 `--intake` 時無任何「之後不能改」提醒 | E | [[Projects/記帳與迴圈工具小修_計劃]] |
| F23 + F24 | standard 代碼審的 `record_cmd` 不帶 `--round`,處置帳卻硬要,一筆無輪次帳毒到整個迴圈 | `Issues/代碼審next把新處置帳誤判舊panel`(open,同根鄰近);`Issues/輕量設計審手冊叫人記處置帳但工具不收`(done,light 版同形) | 仍存在。重現:`loop next code-X --tier standard` 的 `record_cmd` 無 `--round`;`_tpl_flags`對循序單審省略;記處置帳的那段程式要求處置帳必須綁 `--round` | E | [[Projects/記帳與迴圈工具小修_計劃]] |
| F25 | pitfalls 輸出沒講 standard 也要審 | 無 | 仍存在。實測只印「tier: standard(有程式檔改動、沒命中風險型樣)」,無「仍須一席加架構對齊」 | E | [[Projects/記帳與迴圈工具小修_計劃]] |
| F26 | macOS 沒有 `timeout` 指令,與 lumos 無關 | 不適用 | 不是 lumos 的問題;lumos 目前也沒有 e2e 範本 | J | 不改:macOS 沒有 timeout 指令,不是 lumos 的問題;lumos 也沒有 e2e 範本 |
| F27 | 資安席〈消費專案六類〉沒有網頁前端類別 | 代碼審資安席_計劃(doing)d6 定六類;工具鏈代碼審資安與資源鏡頭範圍_計劃(done)只管本 repo | 仍存在。`skills/lumos-design-loop/templates.md` 六類只有第 6 類行動端。代碼審角色卡有 fe-xss,但不進資安席 | C | [[Projects/前端知識與風險詞_計劃]] |
| F28 | 拆包審時 `--scope-lines`/`--snapshot` 填整份,八席被標 scope_oversize | 無 | 仍存在。只看自填的 `scope_lines`,不拿 dispatch.json 的 materials 比對;`record_cmd` 只寫「<這輪審了幾行>」 | E | [[Projects/記帳與迴圈工具小修_計劃]] |
| F29 | `REVISIT:[when-file:…]` 寫下就成立,推送才被擋 | 回頭條件寫下時就成立_計劃(done):推送擋新寫的、`drift scan` 標 born;回頭條件消失式與生來成立_計劃(doing) | 部分。推送擋已有;寫入端沒擋,只在提交時由 note-shape 提醒(可關) | F | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| F30 | e2e 腳本的鎖、pid、`/tmp`、symlink 沒有檢核題 | 工具鏈代碼審資安與資源鏡頭範圍_計劃(done)限工具鏈本 repo;`Issues/跑測試被中斷時子行程變孤兒`(open)只管測試 | 仍存在。消費專案六類無「本機基礎設施腳本」 | C | [[Projects/前端知識與風險詞_計劃]] |
| F31 | 資安包必須含全部改到的檔、最後一次修補後要再派,`loop next` 不提醒 | 代碼審資安席_計劃(doing);閘訊息已寫 | 仍存在。`loop next` 只列「資安 必派(問閘會擋)」(實測 1 行);事後閘才擋 | E | [[Projects/記帳與迴圈工具小修_計劃]] |
| W5 | `doctor` 路徑檢查把「`scripts/e2e.sh --cleanup`」整串當檔名,且 gitignore 的執行期檔判不存在 | 無 | 仍存在(三小項中兩項重現)。`[P]` 印「scripts/e2e.sh --cleanup(已不存在)」「e2e/.run-state(已不存在)」。另一個 repo 的路徑那項沒重現(`../other-repo/...` 未被列出,判不出) | G | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| W6 | `doctor` 每支檔有家只看已提交,提交前一直唸 | 每支檔有家_計劃(doing) | 仍存在。重現:`new system 畫面 --code src/App.tsx` 後(新節點未提交),`doctor` S8 仍列 `src/App.tsx`。另 `eslint.config.js` 這類設定檔也被列進去(雜訊) | G | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| W10 | `spec-gate` 同一句 root 不存在警告印三次 | 無 | 仍存在。重現:設平台 root 為不存在目錄,`spec-gate` 輸出三行相同 | H | [[Projects/筆記指令健檢與規格閘小修_計劃]] |
| W11 | 測試品質沒提 Vitest 假計時器與 user-event | `Systems/test-quality-cli`、`historical-test-quality`(doing) | 仍存在。`skills` 與 `commands/` 搜不到 fake timers、user-event、Testing Library | C | [[Projects/前端知識與風險詞_計劃]] |
| W12 | 設計審抓不到「只用 Tab」這類前端可執行性 gap | 無 | 設計審的天花板,靠實作才知道;不是工具缺陷 | J | 不改:設計審抓不到「只用 Tab」這類前端可執行性缺口,是設計審本身的天花板,靠實作才知道,不是工具缺陷 |

## 各組條數

括號內是「編號數 / 合併後列數」;「部分」算仍存在。

| 組 | 仍存在(編號 / 列) | 其他 | 落點 |
|---|---|---|---|
| A 測試名比對 | 0 / 0(W1 比對當時部分存在,2026-10-15 已由落點計劃處理) | 已處理 1(W1) | 測試名收自由字串_計劃 |
| B 前端技術棧 | 6 / 4(F1、W7、F2、W2、F7、B10) | | 前端框架從vue分出_計劃 |
| C 前端知識 | 8 / 7(F4、F10、F19、F13、F18、F27、F30、W11) | | 前端知識與風險詞_計劃 |
| D 風險關鍵字誤判 | 3 / 2(F5、W3、W4) | | 前端知識與風險詞_計劃 |
| E 記帳與迴圈工具 | 10 / 9(F11、F16、F20、F21、F22、F23、F24、F25、F28、F31) | | 記帳與迴圈工具小修_計劃 |
| F 筆記指令 | 8 / 5(F8、B6、W8、B7、F14 部分、F17、W9、F29 部分) | 已修 1(F3) | 筆記指令健檢與規格閘小修_計劃 |
| G 健檢與家 | 5 / 4(F9、B8、B9、W5、W6) | 已修 1 列(B4、B5) | 筆記指令健檢與規格閘小修_計劃 |
| H 規格閘 | 6 / 5(F6、B1、B11、B2、B3、W10) | 判不出 1(F15) | 筆記指令健檢與規格閘小修_計劃 |
| I 跨 repo | F12 部分(同 repo 工作樹已修;跨 repo 刻意不支援) | | 不改 |
| J 不改 | 0 | 3(F26、W12、B12) | 不改 |

## 比對時要一起看的

- **跨組要一起改的**:F5 與 W3 同一張詞表,改了要升門判定規則版本,並跟 [[Issues/門掃描詞表沒收常見寫法]](反向:漏判)一起量。
- **C 組證據只來自一次示範**:F19 顯示 96 條發現全靠手寫的前端鏡頭找到。C 組是新增知識內容,不是修 bug。
- **未重現而判不出的**:F15、W5 的跨 repo 路徑、W4 的 graph-rename.sh 對照、B3 的乾淨 clone 實跑,要實際造情境才能定。
- **W1 寫計劃時多查到的**(2026-10-15 讀碼與實跑,以下是當時的現況,已由 [[Projects/測試名收自由字串_計劃]] 處理):[test:] 名稱的切法當時有兩份不一致——note-shape 與 doctor S20 用的那支連全形逗號也切、全形冒號也當平台前綴,條款綁定與合約閘用的那支不會;標記邊界一邊「到第一個 `]`」、一邊數括號層數;推送前合約測試閘與 guard kill 的名稱白名單不收括號、冒號;歸檔「還護著存活合約的驗證紀錄」用 ASCII 的詞界包名稱,中文名稱永遠配不到。細節在 [[Projects/測試名收自由字串_計劃]] 做法 6。寫那篇計劃時跑它自己的規格閘,也當場印出「✓ — 25 條全標(…懸空 24 只提醒不擋…)」,就是 W1 本身。
