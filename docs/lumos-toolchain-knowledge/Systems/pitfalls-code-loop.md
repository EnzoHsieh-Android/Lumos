---
type: system
status: done
created: 2026-07-04
updated: 2026-10-01
self_audit: sonnet/2026-08-21
about_code_stamp: batch-2026-08-23/2026-08-23/a57f70871fa9
tags:
  - type/system
  - status/done
  - risk/守衛面
  - scope/loop-engineering
verified_by:
  - "[[Verification/2026-07-04_pitfalls-code-loop]]"
  - "[[Verification/2026-07-05_code-loop必用守衛]]"
  - "[[Verification/2026-07-10_合約鏈補強234]]"
  - "[[Verification/2026-08-05_panel-K2與抽查落地]]"
  - "[[Verification/2026-08-14_canary協議停用none制落地]]"
  - "[[Verification/2026-08-21_L4交叉審計30節點清帳]]"
  - "[[Verification/2026-09-11_代碼審資安席落地]]"
  - "[[Verification/2026-09-11_全報vs抑噪試點]]"
  - "[[Verification/2026-09-29_代碼審資料狀態鏡頭]]"
  - "[[Verification/2026-09-29_前端卡小實驗]]"
  - "[[Verification/2026-10-04_治理帳寫讀設計遭鎖競態擋下]]"
  - "[[Verification/2026-10-06_附件種子修復獨立驗收]]"
  - "[[Verification/2026-10-06_審查附件影響修復主線CI]]"
  - "[[Verification/2026-10-06_引用座標依實際換行_驗證]]"
summary: |-
  PITFALL:[2026-09-28 筆記形狀擋全零修正的代碼審通才席]code-loop check --diff 的起點是 40 個 0(新分支首推)或本機找不到(force-push 後)時,原本原樣交給 pitfalls、它回 rc2、這裡走 fail-open 不擋;現在先照筆記形狀擋與每支檔有家共用的判法換成真的起點(頂端落後或等於主線頂端就沒有新東西;找不到主線時照它原本拿到空樹的做法、不截上線點);工具鏈 CI 的代碼審那步也改成原樣交前一版 [test:t_push_base_zero_or_missing]
  PITFALL:[2026-09-22 rtb-production-agent-demo 回報]★代碼審記帳漏帶凍結快照,原本要到問處置閘才爆★:既有規則只在「這條迴圈已經有一筆帶發現清單」之後才強制留痕,而代碼審的慣例是先記非載體席、再記載體席,第一席記帳時還沒定錨,漏帶 --snapshot 會安靜通過,之後以「資安席留痕對不上」這種看不出原因的訊息擋下,帳本又不能撤銷,只能整輪換編號重記。現在代碼審從第一筆起就寫側當場擋,訊息直接講缺哪個;設計審照舊用定錨規則。★「code 開頭卻不是 code-」這種看不出是哪一種審查的,照最嚴的當代碼審★——代碼審 r1 說這會誤擋 codestage 這類真的設計審,r2 說同檔三處既有呼叫點對這個灰色地帶一律從嚴、就是為了擋「取個 codeX 的編號就繞過」;兩輪方向相反,照既有慣例裁從嚴,而 r1 真正的傷(訊息硬說它是代碼審、誤導人去找不存在的凍結 patch)改用既有那幾處的說法老實講來解。從嚴的代價:走新處置閘的設計審本來也要帶這兩個所以沒差;★舊的 panel 型設計審從沒要求過★(codestage 那九筆就是),目前打不到只是因為更早那條「審查席一定要附 --report」先擋了,以後動那條規則或開補記舊帳的旁路時要重新想 [test:t_code_loop_record_requires_provenance_from_first_row]
  PITFALL:[2026-09-22 同上]★把本機提交壓成一個或 rebase 之後,表態與審查留痕都會失效,內容沒變也一樣★:兩者都只認「同一個提交、或是它的祖先且中間只動簿記檔」,壓過之後原本記的提交不再是祖先。原本擋下訊息只丟兩個 sha,看不出是自己剛壓的提交造成的;現在訊息會點出這個原因並給重來的兩條指令。順序上要先壓、再表態與留痕 [test:t_codeloop_record_invalid_after_squash_says_why]
  KEY:[代碼審 r1 折入 2026-09-16]★對不齊就不算分級,範圍原本訂太寬★——當初的理由是「真正擋新帶進來的告警的是推送前那道閘」,而那道閘★不跑★沒有帶檔清單佔位符的宣告(把它降級成只報不擋)。那種宣告如果分級這邊也放掉就兩邊都漏。現在每條發現會記下它是哪種宣告報的,降級只套在推送閘真的接得住的那種 [test:t_pitfalls_lint_gets_the_changed_files]
  KEY:[linter 那隻手 2026-09-16]算風險有兩隻手:自己的規則、和專案宣告的 linter。★linter 那隻手在 2026-09-16 之前從來沒真的檢查過任何一行★——指令裡「要檢查哪些檔」的佔位符沒被換成真檔名,原樣送給工具,工具回報「找不到檔」;而那條錯誤自己被當成一條發現、把分級撐成最高級。修法:換佔位符走共用那支、執行入口對沒換掉的佔位符 fail-closed(記成「這條沒跑」不是「乾淨」)、棧別辨識改用會看第一行 shebang 的那支(主程式沒有副檔名,在此之前對整道檢查隱形)。★修完量到的副作用與處置★:linter 真的讀檔之後,對不齊座標時(工作目錄不乾淨、或審比目前版本舊的範圍)會把改到的檔裡所有舊有問題全收進來——本 repo 實測 1446 條、分級必定最高級;對齊時只有 3 條且都落在新增行上。★對不齊時 linter 的發現照樣列出來但不參與分級★:分級問的是「這次改動有多危險」,對不齊時分不出哪條是這次帶進來的;真正擋「新帶進來的告警」的是推送前那道閘(比對兩份快照,跟對齊無關)。出身見 [[Issues/風險掃描的linter那隻手沒送檔進去]] [test:t_pitfalls_lint_gets_the_changed_files]
  KEY:★[2026-08-14]canary 協議停用(單源=[[Systems/canary-audit]] d5)★——植入/三道防污染/判定/missed 懲罰全停;輪記帳改 `canary record none`;panel 輪有效=記帳席≥2(Landmark r5「單席 caught<2 白跑」型不再發生);repro triage 觸發改「可疑席(引句錨不到/通用回應)」;落地驗證=[[Verification/2026-08-14_canary協議停用none制落地]]
  KEY:[2026-08-05]UI 層驗收慣例(MCP 接驗證層,Enzo 靈感;立慣例不綁案)——test-layers 宣告 layer 含「UI 驗收」的棧被 diff 命中時,終審驗收=agent 以 Playwright MCP(乾淨瀏覽器)/claude-in-chrome(真登入態)真開頁執行驗收條款,截圖+console 證據存 governance/review-reports/<loop-id>/ui-evidence/ 由 Verification 引用(哲學同 quote-check:證據可重放非口頭);起不了環境=明記未驗+原因不得靜默跳;Landmark .lumos/test-layers.json 已宣告 vue/html/js→UI 驗收、cs→dotnet test;首用=下一個天然帶 UI 面的工作(RSNO 暫緩,人裁);★Android 通道(2026-08-11,[[Projects/Android側UI測試綁圖譜工作流_計劃]])★=maestro MCP list_devices→inspect_screen→run,與 Playwright/chrome 並列;★前置:只准對「已標可自動且測試門店已確認」的 flow 自動跑★(否則會在真裝置真後端開真單),未達條件的 flow 一律僅手動、終審走 lumos code-loop skip --note 留痕;★截圖基準通道(2026-09-10,[[Projects/截圖基準驗收流程_計劃]])★=專案 .maestro/ 有 visual-check.sh 的畫面,終審跑 `.maestro/visual-check.sh <畫面> <證據目錄>` 代替「開頁看一眼」,退出 1 照抄它印的「相符率/門檻/diff 路徑」那行回報;agent 不動基準圖、不降門檻;沒有基準圖的畫面照舊
  KEY:[2026-08-05]pitfalls --diff 排除 governance/review-reports/ 路徑——歸檔證物(席報告/canary 快照 .patch)★故意★含 bug,當代碼掃=push 被自己的留痕擋下(C 慣例落地首推實錄);排除不外溢(收緊釘:同內容在該路徑外照掃) [test:t_pitfalls_diff_skips_review_report_artifacts]
  KEY:[2026-08-11]同型第二例——簿記帳也排除(_BOOKKEEPING_FILES/_DIR:治理帳/usage-log/ci-log/anchor-baseline/code-loop 留痕)。★自我餵食迴圈★:治理帳裡記的 skip 理由本身在描述「命中 open(...)」→掃自己的紀錄再次命中→再 skip→再寫一行理由進治理帳,實測誤觸發 9 次(3978732、837bbff 等皆此形態)。白名單與 code-loop 留痕失效豁免★共用同一組常數★(原本 code-loop 端寫成區域變數,兩處會漂移) [test:t_pitfalls_diff_skips_bookkeeping_ledgers]
  KEY:[2026-08-05]missed 席 findings 改★機械 repro triage★(取代直接丟)——canary 硬閘不動(該席判決仍作廢),但 findings 逐條試真碼/真跑證實;證實走通道 a 折入(note 記「機械證實非席信用」)、repro 不出才丟。實證=T8 r1 missed 席兩條真 major 靠 repro 撈回,原「撈」是編排者裁量現為硬步驟(結構性誤殺的機制化補丁;與 design-loop d4 分流不變:代碼有真 oracle 故走 repro 不走「不作廢」)
  KEY:[2026-08-05]席報告留痕慣例+收貨 quote-check(advisory)——報告落 governance/review-reports/<loop-id>/(原躺 scratchpad 蒸發,帳上 note 指空;T8 實錄);record 帶 --report/--snapshot 讓 sha 落帳(不帶 findings_set 不觸 T6 定錨);逐席 quote-check 對工作副本驗引句(§3 錨定紀律的機械收貨端;不進 gate,panel 判準一字不動)
  KEY:[2026-08-04]pass/skip 留痕的簿記白名單豁免([[Issues/code-loop-pass自失效追尾]])——留痕 sha 之後的 commit 只動簿記檔(治理帳/usage-log/anchor-baseline/code-loop 留痕)且留痕 sha 為目標祖先 → 留痕仍有效;其他檔一動照樣失效、改寫史拒認。「HEAD 移動→作廢」原意=pass 不得蓋到新代碼,此為精化非放寬(原嚴格等值下 pass 自己 append 的治理帳行被 commit 即自失效→追尾) [test:t_codeloop_pass_survives_bookkeeping_commits]
  KEY:[2026-07-18]codestage S1/S5 落地(設計[[Projects/code階段強化_計劃]],4輪審計30條折入+實質收斂人裁)——S1 真跑優先(綁約合約 pass 前必真跑綁定測試,解析三順位不得靜默跳過;紀律層)+確定性驗證器三通道參與(不佔canary席;M2帳下capture advisory裁決歸機械證實通道)/S5 辯方預設Codex+tier-high雙Codex角色(帶餌finder佔W+無餌否決席外掛,落閘=M2記disputed-major)+家族否決保護+fail分級(high外家缺席不得收斂攤人)
  KEY:[2026-07-10]panel 追加 spec-conformance slot(tier=high 且有收斂 spec→對答案審查員,四類:已實作/縮水/多做/未實作;templates §7.5)
  FLOW:pitfalls spec 模式(剝除對齊 assess_spec+防呆→掃 PITFALL_CLASSES 四類→印通用 4 問(3 固定+1 風險類反問,2026-08-08 追加;★原記 3(2026-08-21 程式碼實證)★)+命中類追問)｜--check(命中類且無「## 實務隱患」節→rc1)｜--diff(掃新增行 Check H 骨架+代碼形態 pattern→manifest(★(2026-08-21 程式碼實證)欄位依來源而異:內建 regex 類={file,line,class,pattern,question};lint 來源={file,line,source,rule,message}★)+stack_questions(命中 kt/cs/vue/sql 附該棧效能問,源=[[效能檢核目錄]])+尾行 tier;line 由 @@ 推導;rc 恆0)→ 尾行 tier 分流:trivial 跳(commit 註明)/standard 走單 reviewer 終審/high 觸發 lumos-code-loop 終審對抗審(bug canary 四型+辯方+K-streak∧G2 收斂,loop status --gate 無 --spec G1 skip);★2026-09-09 起另一條不看 tier 的分支:stack_questions_applicable(增刪行觸發到的棧題)有題 → 推送前每題表態(code-loop dispositions),check 擋;見[[Systems/棧別提問表態閘]]★
  KEY:兩層隱患兩錨點——設計決策級(冪等鍵/重試策略)錨 spec 層 pitfalls --check;代碼級(N+1/race/資源洩漏)錨終審 --diff+code-loop。補審計火力頭重腳輕(spec 有整套對抗機器、代碼原只兩道普通眼)
  KEY:三道防污染(不可違反)——真代碼永不含(fix 錨真 diff file:line、canary hunk 不在真 diff)｜低耦合植入(canary 座標在真改動集外=pillar-1 機械前提)｜溯源排除(含間接聯想幻影,未顯式引用亦排;偏多排)
  KEY:PITFALL_CLASSES 四類名 ≡ difficulty.RISK_CLASSES、_PITFALL_BLACKLIST ≡ difficulty._BLACKLIST——漂移守衛落 test_autonomous_loop.py(toolchain-only、非 vendored);詞表/pattern 表自帶 scripts/lumos(difficulty.py 不 vendored)
  KEY:diff class 用代碼形態類軸(併發/效能/資源)非四業務類;pattern 去重疊(SELECT→效能 N+1、INSERT/UPDATE/DELETE→併發交易);過濾繼承 Check H 全套(skip .md/.txt/.rst+測試檔+註解行)
  KEY:★[2026-09-11 d6 取代 d5]高風險代碼審一律必派一席「資安」★(Enzo 裁;所有專案,工具鏈自己也算;只在 tier high,不改風險掃描觸發)——處置閘加「資安席」一步(第六步,第五步是條款綁定):整個迴圈要有資安席帳列、報告 sha 對、看過的檔涵蓋最後一版;編制表新值 required-gated;生效日 2026-09-12(2026-09-11 落地,驗證 [[Verification/2026-09-11_代碼審資安席落地]];代碼審待跑) [test:t_disposal_security_seat_required] [test:t_roster_code_high_has_security_seat];單源 [[Projects/代碼審資安席_計劃]]。舊 d5(2026-08-27 刻意排除,理由單人私有 repo)前提已不成立:repo 公開、一行安裝、09-06 hook 信任邊界事件
  KEY:誠實天花板——pattern 提示器非偵測器(單行掃描,跨行語境小行窗啟發為限)｜canary 校準+溯源排除靠自律｜--check 只驗節存在不驗內容｜mutation 冒煙抽樣非覆蓋｜code-loop 少一道 G1(--spec 可選、G1 skip)｜事故語料進圖譜留 v2
  KEY:[2026-09-18 Enzo 裁]改動風險分級單一算法 _pitfall_tier(★維持 vault-free★,代碼審 r1 兩席):命中風險型樣/新告警 → high;改動裡沒有「需要有家的程式檔」(_is_code_file:副檔名清單或首行 #!)→ light;其餘 standard,審查帳有全靠人驗留痕時多印一句「跑 spec-gate --push-check 看是不是 light」;「計劃風險低且全靠人驗且小改動閘過 → light」由 spec-gate --push-check 印(只有它有圖譜、本來就在 pre-push 跑,不重跑測試)。JSON 多 tier_reason [test:t_pitfalls_tier_light_sources]
  KEY:[2026-09-17 小改動閘 r2]簿記目錄單一源 _BOOKKEEPING_DIR 擴成 _BOOKKEEPING_DIRS(governance/code-loop、review-reports、replay):三個消費者(pitfalls --diff 掃描排除、code-loop 留痕失效豁免、小改動閘的擴散量)共用;效果=卷證/凍結判定的提交不再讓 pass 留痕失效 [test:t_prepush_small_change_gate]
  KEY:[2026-09-18 純文件推送不跑全套]`pitfalls --diff --json` 多五欄:`suite`(docs|full)、`suite_reason`、`affected_keys`、`light_ok`、`suite_graph`(docs 且範圍碰到 docs/<名>-knowledge/ → 執行器加 --graph 跑讀真圖譜的測試)。docs=改到的每一支都過兩層白名單:路徑(README/根目錄 .md/LICENSE/docs/assets/diagrams/governance)★且★副檔名在文件清單 _DOCS_ONLY_EXTS(不分大小寫);沒副檔名、.rb/.PY 這種一律不算文件(代碼審 r1 邊界席 blocker+正確性席:第一版「路徑對且不在程式清單」被繞兩次,改成反過來列文件)。scripts/skills/.github 任一支、從 scripts/ 搬進 docs/(--no-renames 看成刪程式檔)都 full;★守衛本身★(governance/anchor-baseline.json、governance/code-loop/)碰到就 full(r3 資安席:只推基準線會跳過 t_anchor);其餘簿記帳不算;範圍算不出 → full。affected_keys=改到的程式檔裡動到的★頂層★函式名(cmd_x 也給子命令 x;縮排的 def 不算,check 會選中全部)與檔名,只留 [A-Za-z0-9_.-]{3,}。light_ok=非文件檔全是程式檔(資安席:測試檔/skills 這種既非文件也非程式的不准跟著 light 少跑全套)。三點範圍起點用 merge-base(_range_base)。執行器 `--suite docs` 直接讀 _DOCS_ONLY_PATHS,不抄第二份
  DEP:[[risk-tiered-review]](分級哲學延伸到 diff 層)｜[[convergence-evidence-gate]](gate --spec 改可選)｜[[lumos-refcheck]]｜doctor Check H(diff 掃描骨架)
  TEST:t_pitfalls_spec(9)+t_pitfalls_diff(截至 2026-08-21 為 12;★原記 11(2026-08-21 程式碼實證)★,含行號值+併發寫入)+TestPitfallsDrift(2,類名+黑名單)+t_loop_gate 案14翻契約+t_loop_gate_no_spec;當時 374 passed(★全量數字已漂,以 CI 為準★)
  VERIFY:[[2026-07-04_pitfalls-code-loop]]
  WHY:[2026-09-29 [[Projects/代碼審資料狀態鏡頭_計劃]]]代碼審派工詞正確性鏡頭加 DDIA 資料狀態五問(新舊互讀/寫一半/衍生資料/時間/不可逆),冪等與併發擴寫同次讀兩次與對外送出重試;只寫進審查員鏡頭、不做推送前表態閘——推送前表態版經設計審 r1 撤案(會在 60–85% 推送上亮、放大無圖譜死結),小實驗只量到鏡頭形式多抓一次已知 bug([[Projects/代碼審鏡頭對照DDIA_調研]]);多席時五問只留給正確性席(靠編排者照做);範本內容由 t_data_state_lens_in_code_template 等三支測試釘住
  WHY:[2026-09-29 [[Projects/代碼審前後端角色鏡頭_計劃]]]代碼審正確性席派工詞加 `LUMOS-ROLE-CARDS: on` 時,依改到前端或後端附角色鏡頭卡(前端 6 題、後端 2 題,題號 fe-/be- 不得改:撤除條件靠它計數);判定建立在既有題組鍵上不另造分類,宣告讀起點版本(被審分支不能自己關卡);推送前分級只在人讀輸出多一行角色統計、不進 JSON。只接 Claude 通道,Codex 領席每席同一份文字做不到只給正確性席(d4)
  PITFALL:[2026-09-29 代碼審角色鏡頭 r1 正確性席與外家席各自重現]角色段放在「參考資料」框外(框外=審查員照做的指令區),壞宣告的警告若回填專案寫的 role/path 值,被審專案就能往指令區塞字;警告只准寫第幾條與固定原因 [test:t_review_role_warning_never_echoes_config_values]
decisions:
  - content: 共用層(手動 pipeline + 自主 loop 都吃);checklist=通用3問+類專屬追問;載體=lumos 新指令;--check 機械擋;code-loop 風險分級觸發;醒著訊號=reviewer bug-canary+mutation 冒煙
    id: d1
    context: 效能/併發主戰場在業務專案、治理面在 loop,擇一都缺半;純 prompt 違反 mechanical-not-motivational;全分支跑 code-loop 日常太貴
    why_chosen: 每軸都選機械可驗+分級控總量;bug canary 驗審查層醒著、mutation 驗測試層守著,兩者正交
    decided: 2026-07-04
    valid: true
  - content: 代碼 canary 用三道防污染(真代碼永不含+低耦合植入+溯源排除),不採純 mutation
    id: d2
    context: 使用者質疑代碼 canary 污染風險比 spec 嚴重(假 hunk 改變語意、reviewer 推導衍生幻影 findings)
    why_chosen: 需醒著訊號(無則蓋章 reviewer 連 2 LGTM 空轉收斂,r9 opus 都漏抓);mutation 只驗測試層抓不到審查層敷衍;三道防污染把污染封到「必留可見痕跡」
    decided: 2026-07-04
    valid: true
  - content: code-loop check 在 marker 檔不在時退讀 tracked 的治理帳(docs/.governance-log.jsonl 最後一筆該分支 code-loop 事件)。起因:governance/code-loop/ 被 gitignore,CI 後盾(#5)的乾淨 checkout 永遠沒有 marker,上線後第一筆 tier=high 推送(6097b85)假紅。放行/封鎖規則不變(同 sha 或純簿記增量才放行),只是來源多一個;reason 會標「來源 marker/治理帳」。
    id: d3
    decided: 2026-08-22
    valid: true
  - content: code-loop 擋推鏈(pre-push 與 CI 的 code-loop gate)恆以 --no-lint 跑 pitfalls——lint SARIF 發現在整條擋推鏈結構上不可見,兩側同跳(--no-lint 寫死在共用判定函式 _codeloop_guard_verdict,不是 pre-push 單邊省時間、CI 兜底——那個敘事對 lint 不成立)
    id: d4
    context: lint接線收口 [S2]:原裁定只存在 hook 註解;設計審 s2-f3 抓到「CI 兜底」誤導面後如實明文化
    why_chosen: 速度(pre-push 已 11 分鐘)+lint 告警屬審查品質面非擋推面;[F] 檢守宣告健康、pitfalls 帶 lint 屬手動加跑
    decided: 2026-08-26
    valid: false
    superseded_by: 擋推鏈改成會跑檢查工具:代碼審那一關多一道獨立判定(新增告警閘),對每一次推送都跑、不看風險分級,只擋這次改動新增的告警。既有的風險分級計算維持原樣(照舊帶 --no-lint 快算),兩件事分開
    ended: 2026-09-13
  - content: 安全缺陷型審查鏡頭★刻意排除★(Enzo 2026-08-27 D2 裁):類軸只留代碼形態(併發/效能/資源),不加對抗性安全鏡頭。理由=單人私有 repo、非對抗威脅模型(IssueTrojanBench 66.5% 對抗基準不適用);真正的威脅=幻覺 agent 寫錯圖譜/碼,由既有正確性鏡頭+測試+人 signoff 覆蓋,非安全鏡頭。邊界/回頭條件=當工具鏈真的吃不可信外部輸入(日報吸收管線是已標的 future 不可信面)上線時,重新拉進安全鏡頭
    id: d5
    context: 調研 D2:兩家 skill 全文零 security、regex 類軸註解明寫排除安全、效能 2026-08-21 降建議級=無席能因安全缺陷判 major
    why_chosen: 明文宣告排除比空白留著好——空白讓人以為漏了,明文+邊界讓下一個 session 知道是刻意的、何時該重新評估
    decided: 2026-08-27
    valid: false
    superseded_by: d6
    ended: 2026-09-11
  - content: 高風險代碼審一律必派一席「資安」(Enzo 2026-09-11 裁;所有專案,工具鏈自己也算):只在代碼審本來就跑的 tier high 加席、不改風險掃描觸發;機械擋=處置閘加「資安席」一步(整個迴圈要有資安席帳列、報告 sha 對、看過的檔涵蓋最後一版;細節以計劃為準),生效日 2026-09-12;看什麼/不報什麼/每條必附攻擊路徑見 templates.md §7.8;單源 Projects/代碼審資安席_計劃
    id: d6
    context: 2026-09-11 治理日報(agent 設定倉庫 16% 帶安全缺陷、判定該擋在動手那一刻)觸發重查:d5 排除的前提「單人私有 repo」已不成立——repo 在 GitHub 公開、README 教一行 curl|bash 安裝、2026-09-06 hook 信任邊界事件=吃不可信輸入(d5 自己的回頭條件),且消費專案(會員/金流後端、App)照樣繼承了排除;兩個獨立來源查到代碼審全無資安席、9 個消費專案派工單零資安鏡頭
    why_chosen: 消費專案與公開分發的工具鏈都有真實攻擊面;資安席照 Anthropic claude-code-security-review+OWASP 借清單,不自己發明;只在 high 加是人裁的成本取捨(限制與 REVISIT 記在計劃)
    decided: 2026-09-11
    valid: true
  - content: 擋推鏈改成會跑檢查工具:代碼審那一關多一道獨立判定(新增告警閘),對每一次推送都跑、不看風險分級,只擋這次改動新增的告警;既有的風險分級計算維持原樣(照舊帶 --no-lint 快算),兩件事分開。翻掉 d4
    id: d7
    context: 翻掉 2026-08-26 的 d4(擋推鏈恆以 --no-lint 跑 pitfalls)。當時理由兩條:①推送前已經十一分鐘,再加檢查工具太慢 ②lint 告警屬審查品質面、不屬擋推面。2026-09-12 Enzo 立了「用自然語言寫任何程式語言,但要社群經驗覆蓋每一次提交」這個方向,前提就變了——不擋就不叫覆蓋。單源 [[Projects/新增告警閘_計劃]]
    alternatives_considered:
      - "維持不跑:完全不動既有裁定,但「覆蓋每一次提交」這個方向就不成立"
      - "只在高風險跑:成本低,但低風險改動根本不派席,覆蓋率等於看運氣"
      - "跑但只報告不擋:摩擦最小,但歷史上預設不擋的東西很少有人回頭看"
    why_chosen: 速度那條用機制回應而不是無視:只跑改動檔、只解那幾支檔的兩份快照、整條閘有時間預算、單檔有行數與位元組雙門檻,數字是實測訂的(843 行 1.8 秒、26718 行 105 秒)。品質面那條是前提變了——這道閘只擋「這次新增的」,舊債一概不管,所以它擋的不是品質分數,是你這次帶進來的新問題
    trade_offs: "檢查工具太慢會直接擋人(預算用完、沒跑到的命令判擋不判放行);環境不可用(工具沒裝、逾時、拉不到規則)走自動放行,所以它防疏忽不防惡意——把工具移掉或弄慢就能繞過,配套是健檢會數自動放行次數。零真專案實證,這個 repo 自己也還沒宣告檢查工具"
    decided: 2026-09-13
    valid: true
related:
  - "[[Projects/impact-diff橋接_計劃]]"
  - "[[Projects/新增告警閘_計劃]]"
about_code:
  - scripts/lumos
aliases:
  - lumos pitfalls
  - tier: high 代碼審
  - pitfalls --diff
  - 資安席
---
# pitfalls-code-loop

`lumos pitfalls` 三模式 + `lumos-code-loop` skill——**實務隱患意識 + 代碼審計對齊**。

## 動機
AI 開發仰賴模型自決實作方式、只需通過最終驗證,但實作選型的實務隱患(效能/冪等/併發/資源)沒人逼它回答;且審計火力頭重腳輕——spec 有 canary/辯方/跨家族/證據閘一整套對抗機器,代碼只有 task reviewer + 終審兩道普通眼睛。

## 組件
- `scripts/lumos` `cmd_pitfalls`:三模式(spec 提問 / --check 缺節擋 / --diff 代碼風險 manifest+tier),vault-free、詞表自帶。
- `cmd_loop_status --gate` 的 `--spec` 改可選(缺 → G1 skip;供 code-loop 吃 G2 枯竭錨)。
- `skills/lumos-code-loop/SKILL.md`:對抗代碼審(bug canary 四型+三道防污染+辯方+證據閘+mutation 冒煙),tier high 觸發。
- 接線:orchestrator-prompt(步驟1節名+2.8 pitfalls --check)/graph-discipline(終審前 --diff→code-loop)/design-loop skill(審前 --check)/project-notes(指令表+gate 契約)。

## 代碼審留痕的簿記豁免不只看路徑前綴(2026-10-01)

留痕之後「中間只動簿記檔」才算有效。原本只比路徑前綴,而且用 git 預設的改名偵測:把程式檔改名搬進簿記資料夾(順便換成 .json)時只看到新路徑,「程式檔被刪」整個看不見,留痕照算有效;在簿記資料夾裡新增一支 .py 也照算簿記。回頭重讀代碼審 r1 資安席實測重現。現在這一個消費者改成:關掉改名偵測(搬家看成「刪程式檔+加新檔」)、簿記資料夾底下副檔名是程式檔的不算簿記。另外四個共用簿記名單的消費者(風險掃描、小改動閘、推送前測試範圍、來源髒檔合併)沒動——它們誤判的後果是多掃或多跑,不是放過沒審的碼。順手修掉一個舊病:git 預設把中文檔名加引號印出,簿記資料夾裡中文命名的卷證比不到前綴、會讓留痕無故失效,改用 -z 照原樣比。改之前查過:當時版控裡五個簿記資料夾共 4275 支檔,沒有一支是程式副檔名;本機未追蹤的 `governance/review-reports/maestro-visual-baseline-2026-09-10/` 有一支 .kt,若在留痕之後提交它,留痕會失效(照新規矩這是對的)。測試 `t_code_loop_bookkeeping_rejects_code_moved_in`;設計與取捨在 [[Projects/守檔筆記對照改動_計劃]] 的〈實作紀錄〉。

第二輪(回頭重讀代碼審 r2 架構對齊席,major):第一版只接了「副檔名是程式」那一半,沒副檔名、首行 `#!` 的腳本放進簿記資料夾照樣豁免(席位重現:`governance/replay/run` 內容 `#!/bin/sh`)。現在判法跟每支檔有家同一套:副檔名在清單裡,或沒副檔名、首行是 `#!`;★首行用 git 讀目標提交裡那一版,不讀磁碟★(判的是那個版本),那一版刪掉了讀留痕那一版,兩邊都讀不到保守當程式檔(跟 `_is_code_file` 一樣)。戳記、游標這類沒副檔名的簿記檔首行不是 `#!`,照舊豁免。副檔名大小寫照舊敏感(大寫 `.PY` 不算程式,跟另外四份副檔名清單同口徑)。測試 `t_code_loop_bookkeeping_shebang_script_not_exempt`。

第三輪(回頭重讀代碼審 r3,2026-10-01;上限輪,修完經使用者裁定不再派席,只經測試與翻紅核對):
- **檔名結尾的 \r 會讀到別支檔**(資安席,major):git 的批次讀取把每行結尾的 `\r` 當換行的一部分吃掉,查「run\r」拿回的是同目錄另一支「run」的內容。攻擊做法是放一支結尾帶 \r 的 `#!` 腳本、再放一支同名不帶 \r 的戳記當誘餌,第二輪的首行判法就讀到誘餌、整批算簿記。現在沒副檔名、要讀首行的路徑只要帶控制字元(跟回頭重讀同一組 Unicode 類別,不含非 UTF-8 的替身字元),就當判不了、保守算程式檔。共用的批次讀取函式沒改:它有十幾個呼叫端,有的把「整批讀不了」當空清單接著用,改它的行為要逐一確認,這次只修這一個消費者。測試 `t_code_loop_bookkeeping_ctrl_char_path_not_exempt`。
- **可執行的一律算程式、首行先去 BOM 與行首空白**(資安席):BOM 開頭、行首空白的 `#!` 腳本,以及有執行權限但沒寫 `#!` 的檔,bash 都照樣跑得起來(沒有可用 `#!` 的可執行檔,bash 會改用 sh 直接跑內容)。現在改用 `git diff --raw` 連檔案模式一起拿:簿記資料夾底下目標那一版(刪掉了就看留痕那一版)是 100755 的一律算程式,有副檔名也一樣;首行判 `#!` 前先去掉 UTF-8 BOM 與行首空白(只有這個消費者這樣去;每支檔有家維持嚴格口徑)。改之前查過:版控裡五個簿記資料夾(4295 支檔)沒有一支是可執行的。測試 `t_code_loop_bookkeeping_exec_mode_and_bom`。
- **`#!` 在第二行不算**:核心只認檔案最開頭兩個位元組的 `#!`,第二行的 `#!` 不會讓檔案變成那個直譯器的腳本。這種檔要嘛有執行權限(上一條的模式判法已經算它是程式),要嘛得有人明寫 `sh 檔名` 去跑——那樣任何文字檔都跑得起來,跟一般紀錄分不出來;把「任一行有 `#!`」都算進來,只會讓內文引用到 `#!` 的卷證與紀錄被誤判。跟每支檔有家同口徑。
- **讀首行走帶上限的批次讀取**(架構對齊席):改用同檔既有的 `_nodehome_cat_blobs_capped`,單支上限 1 MB,超過就讀不到、保守算程式。現在簿記資料夾裡沒副檔名的只有 .weekly-stamp(9 位元組)與 .rotation-cursor(約 5.6 KB,每輪加一行),離上限很遠。目標那一版在不在改由 diff 的模式判(000000 就是刪掉了),不再用「讀不到」來猜——不然超過上限的會被誤當成刪掉、改讀留痕那一版。測試 `t_code_loop_bookkeeping_head_read_capped_and_deleted_stamp`(也守「刪掉的是一般戳記 → 退回讀留痕那一版、照舊豁免」那個分支,通才席指出原本拿掉它沒有測試會紅)。

## 相關
- 設計稿:`docs/design/2026-07-04-pitfalls-code-loop.md`(design-loop 8 輪 K=3 收斂;qwen major 機械反證後 endorsed-after-refute)。
- 實作計畫:`docs/superpowers/plans/2026-07-04-pitfalls-code-loop.md`。

## 新增告警閘怎麼判（2026-09-13，[[Projects/新增告警閘_計劃]]，翻案 d4→d7）

> 白話：推送前多一道判定——這次改動有沒有帶進新的告警。舊債一概不管。

- **位置**：判定序列裡排在表態之後、留痕之前。**跟表態一樣不看風險分級**——「覆蓋每一次提交」是這件事的目的，只在高風險跑就不成立。既有的風險分級計算維持原樣（照舊快算、不跑檢查工具），這是獨立的一條路。算的部分在 [[Systems/pitfalls-lint-adapter]]。
- **兩類失敗分開，對齊既有的兩套慣例**：
  - **環境不可用**（工具沒裝、命令逾時、拉不到規則、版本代號解析不出、放行檔讀不了）→ 自動放行並自動記一筆帳，不要求人手寫說明。跟既有合約測試遇到環境問題的做法一致。
  - **真的有未放行的新增告警、檔太大沒被檢查、預算不足沒跑到的命令** → 擋，逃生門是人手動放行並寫理由。
  - **檔太大不走自動放行**：那會變成「把檔案撐大就能繞過」的可重現繞道。大檔有自己的指紋（綁路徑不綁內容），登記過就不再擋、但照樣列出來讓人知道那支沒被檢查。**上限不是時間防線**（時間防線是預算）——實測同一支兩萬八千行的檔，ruff 0.05 秒、社群規則掃描器 105 秒，掃不掃得動是工具的性質不是檔案的性質。
  - **放行檔讀不了不可以當成「沒有放行紀錄」**：那會讓所有既有放行瞬間復活、整批擋人。
- **放行**：`lumos lint-waive <指紋> --note "<理由>"`，寫進 `.lumos/lint-waivers.json`（**這個檔要進版本控制**，只活在本機的話換台機器整批復活）。讀改寫要上鎖——只做原子換名的話，兩個工作階段同時放行不同指紋，後寫的會整份蓋掉先寫的。
- **關得掉**：環境變數 `LUMOS_SKIP_LINT_NEW` 整道關；設定檔 `.lumos/config.json` 的 `lint_new` 區塊有三態（擋／只報告／關閉）與各項門檻。**設定不可以放 `.lumos/lint.json`**——那個檔的每個頂層鍵都被當成「副檔名→命令清單」嚴格驗證。
- **自動放行要被數**：健檢會唸「最近 30 天自動放行幾次、放行清單幾條」。自動放行是已知的繞道向量（把工具移掉或弄慢就能過），沒有人去數就等於沒有守衛。
- **誠實邊界**：它防疏忽不防惡意；整批重新縮排的提交會產生一批假新增（刻意選誤報不選漏擋）；零真專案實證。

WHY:[2026-10-06 附件種子第二輪]模式與首行必須同出凍結版本；共用 raw 解析器提供模式及物件，舊留痕消費者仍只取原模式對，避免影響分析另建解析器漂移。既有簿記程式例外測試子集已驗 5 案例25條全綠，不代表整個分支放行。[出處:[[Verification/2026-10-06_附件種子修復獨立驗收]]] [因:只共享目錄或副檔名仍有跨層分類不一致] [test:t_code_loop_bookkeeping_exec_mode_and_bom] [test:t_code_loop_bookkeeping_shebang_script_not_exempt]

WHY:[2026-10-06 角色功能驗收時間控制]凍結內容正確性不應同時承諾機器負載下三秒必讀完；兩個真 Git 功能案例顯式給30秒測試預算，正式3秒與期限降級仍由原專門案例驗。原斷言不改，不用自動重試掩盖紅燈。[出處:[[Verification/2026-10-06_附件種子修復獨立驗收]]] [因:可控3.1秒觀測使原內容案例必紅、充足測試預算使原內容斷言全綠] [test:t_review_role_changed_files_population] [test:t_review_role_reads_head_content_base_config] [test:t_review_role_file_cap_and_budget]

WHY:[2026-10-06 零角色預算先做讀取反例]budget=0 的真時間斷言曾紅，禁止 Git／選檔的探針也先0過2敗；沒有時間可用應先回超時空結果，不先耗設定與 metadata 查詢。此修復保留原零預算三秒斷言，沒有放寬正式預設時間。[出處:[[Verification/2026-10-06_附件種子修復獨立驗收]]] [因:耗盡預算後才檢查讓派工仍做無用讀取] [test:t_review_role_zero_budget_no_git] [test:t_review_role_file_cap_and_budget]

WHY:角色新增簿記查詢承接剩餘預算，不再自開固定timeout；一般角色改名仍取新路徑，只有被終點附件排除遮住的舊程式要保留 [出處:審查附件不作程式影響種子設計審r1] [因:小幅正預算會被新增查詢穿透，跨簿記改名也曾令角色輸入全空] [test:t_review_role_bookkeeping_remaining_budget,t_impact_diff_bookkeeping_boundary_rename]

WHY:[2026-10-06 第三輪角色統計補強]固定帳檔與未知首行終點也需要舊側角色證據；只對確定排除的目錄補償，不能兌現完整跨簿記改名承諾。採同一分類入口的「已確認」口徑，不另建簿記表、不改一般改名只取新側。[出處:code-review-artifact-impact-inputs/r3-correctness.md、r3-architecture.md] [因:避免角色消費者與影響分析消費者分岔，降低同類修復再次漏邊界] 防回歸：t_review_role_bookkeeping_rename_uncertainty，含三種真 R100、超限／逾期未知與角色不重複計數。

WHY:表態的來源座標必須共用引用驗證入口，避免同一個不存在的第三行在不同證據閘得到相反結果；本次只修座標計數，不把存在性檢查升格為語意正確性 [出處:source-coordinates 最小重現、r1設計審與countercontrol] 防回歸：t_refcheck_physical_dispositions。 [因:避免表態證據與引用檢查對同一來源座標矛盾]
