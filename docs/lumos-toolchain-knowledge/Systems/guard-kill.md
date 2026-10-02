---
type: system
status: done
created: 2026-07-10
updated: 2026-10-02
self_audit: sonnet/2026-07-24
about_code_stamp: batch-2026-08-23/2026-08-23/2faf3eec082c
tags:
  - type/system
  - status/done
  - risk/守衛面
  - scope/guards-gates
summary: |-
  WHY:[2026-10-02 Projects/代碼審修正關卡第0步_計劃]建、收隔離工作樹那段抽成共用的 `_isolated_worktree`(with 區塊,寫法照 _vault_write_lock;修正關卡也用);guard kill 照舊在平台根下 `git -C` 建樹、測試在樹的最上層跑、建樹失敗記 error 繼續下一個平台、--keep-worktree 的「現場保留」由 guard kill 自己印(--json 時印到標準錯誤),行為不變 [test:t_isolated_worktree_shared]
  RULE:[since:2026-09-22][confirmed:2026-09-22][retire:連續兩季沒有任何專案用 guard plan,或誤擋多過真擋]合約可以「預告」:`lumos guard plan … --name <短名>` 一次寫好預告標記(`★INVARIANT-PLANNED★`,既有合約抓取撈不到它)與一個待完成的守衛驗證節點並雙向連好;查那篇功能節點時預告會另起一段印出來(還沒有測試在守、最遲哪天);逾期讓自檢出 issue(推送與 CI 靠它擋)、七天內先唸不擋、**到期當天不算過期**、**不准延期**;★本機推送只擋「這次改動碰到的」那幾條★(靠守衛節點→家節點→about_code 兩跳算交集;算不出來本機放行、CI 仍擋),別人的逾期會列出來但不擋你的推送;做完 `guard settle` 就地轉正,不做了 `guard abandon` 立墓碑(要先 `signoff --ref`)。★威脅模型是防忘記不防繞過★:改日期、改型別、刪節點檔都繞得過,刻意不補,寫在計劃的誠實界線。單源 [[Projects/必要合約清單_計劃]] [test:t_guard_plan_creates_marker_and_node]
  PITFALL:[2026-09-22 代碼審 r2 blocker]預告行是「合約文字 + 指令接在行尾的 `[watch:…] [due:…]`」,轉正與棄置要靠還原出原始合約文字才找得到那一行。★只能剝行尾那一對,不能把整行同樣字樣都剝掉★:合約文字自己寫到那兩個字樣時(這個 repo 滿篇都是方括號標籤寫法)就還原不出原文,那條預告從此轉不了正也棄置不掉、逾期還一直擋推送,只剩手改檔案一條路 [test:t_guard_claim_with_bracket_tags_still_settles]
  RULE:[since:2026-09-23][confirmed:2026-09-23][retire:有專案反映必填短名擋掉了正常流程(例如批次腳本登記大量預告)]★守衛節點的檔名要人給短名★:`--name` 必填、24 字內、只收中英數字底線連字號,檔名 = 日期_短名。原本拿合約原文前 40 字當檔名,斷在句子中間(rtb-production-agent-demo 回報)。舊規則截斷出來的檔名,自檢會在不擋的那一層點出來——判法是精確比對(檔名等於原文被截斷的樣子、而且原文真的比截斷長度長),手取的名字不會被點到。單源 [[Projects/必要合約清單_計劃]] 〈守衛節點的檔名〉 [test:t_guard_plan_requires_short_name]
  WHY:[2026-09-22 提交 eca5f218 合約預告]規則只認「節點身上有 guards 欄位」的守衛節點,不看 status 字面值——手寫 `status: pending` 的人不該被拖進整套規則;判準跟著節點走,改名搬家都對得上
  WHY:[2026-09-28 Projects/存量漂移防線_計劃]settle 轉正時把 guard plan 寫的四種預告句改成歷史說法(TEST 句改成哪天轉正、由家筆記的正式行守,不寫測試名;WHY 行尾加已轉正;正文兩句改寫),status、標籤與句子同一次寫入。原本轉正後守衛紀錄照樣寫著「還沒有測試在守」(rtb 考卷 A4–A6)。句型比對跟 [[Systems/存量漂移守衛]] 的 c1 共用同一支,從行首比、第四句含反引號
  PITFALL:[2026-09-28 設計審 r3 外家席]plan、settle、abandon 原本改家筆記都在寫入鎖外,兩個指令同時改同一篇家筆記,後寫的會用舊內容蓋掉先寫的(例:settle 蓋掉同時 plan 寫的預告行,留下 pending 守衛紀錄卻沒有預告行);現在三支各自從讀到寫整段拿鎖。settle 第一步做完、第二步失敗時重跑只補第二步,守衛紀錄已是 pass 就回 0 [test:t_guard_commands_hold_vault_lock] [test:t_guard_settle_recovers_half_done]
  KEY:★INVARIANT★ guard kill rc 優先序:survived→rc1、drifted/abort/error→rc2、弱證據(unattributed/timeout)不放行執行錯誤 [test:t_guard_kill_rc_precedence] [audit:sonnet/2026-07-29]
  KEY:★INVARIANT★ guard kill --json 模式**成功跑完時(rc 0/1)** stdout 恰一行合法 JSON(所有診斷走 stderr;rc2 早退路徑不印 JSON=範圍外,明文收窄) [test:t_guard_kill_json_purity] [audit:sonnet/2026-07-29]
  FLOW:kill-add(配方進kill_recipes+KEY行[kill:recipes],同檔原子寫)→kill(依platform分組→worktree於系統temp→baseline綠→套壞法(圍欄+唯一命中)→綁定測試必翻紅→七態verdict→docs/.kill-log.jsonl留痕)
  KEY:宣告式壞法(人寫,從業務行為推導非實作反轉;繞開等價變異不可判定)｜run_cmd由config宣告(platforms.X.run_cmd/legacy test.run_cmd,{method}佔位+shlex.quote+killpg)｜**七態**(2026-07-29 oracle品質包升級,取代舊六態):killed(強證據,歸因到綁定測試)/killed_unattributed(紅了但歸不到該測試)/timed_out_weak(**不再計為 killed**,舊版歸 killed 是假強殺)/survived(稻草人rc1)/drifted/abort/error
  KEY:baseline前置(cargo-mutants)防假殺;timeout=baseline×5下限20s(LUMOS_KILL_TIMEOUT_FLOOR可覆寫);worktree只隔離原始碼不隔離DB(hermetic警語);HEAD基準(dirty大聲警告)
  KEY:★DEBT★ hydration(未提交帶入)與lockfile v1砍(否決位裁);E2E maestro {method}不適用;冷build成本;submodule不init
  KEY:★誠實界線[2026-07-23 日報吸收]★——殺傷率有天花板:「殺得掉」≠「殺得準」。研究(arXiv 2606.10417)實測突變殺傷率 7-9 成的測試仍漏一大片未真正驗到的行為,且很多「殺掉」是程式碰巧崩(rc≠0)、非斷言真的檢查了被改壞的行為。**對 lumos 兩重意義**:①guard-kill 的 survived(rc1)只證「綁定測試對這個壞法翻紅」,不證斷言指到被改的業務欄位——高風險合約可加一句「準殺」檢查(失敗測試斷言須提及被弄壞的欄位/行為,非只看 rc)②**打臉 2026-07-22 日報 inspiration「把 Check K 健康指標從『數測試』換成『殺傷率』」**(該 inspiration 未落地)——別把可鑽的『數量』換成另一個可鑽的『殺傷率』;真要換,健康指標得是『準殺』(斷言驗到規則),不是裸殺傷率。載重合約留「這條到底驗了哪些行為」比留一個殺傷率數字誠實
  DEP:[[Systems/check-t-sentinel]][[Systems/test-profile-multiplatform]]
  TEST:t_guard_kill(七態+M1/M2殺手測試)+t_guard_kill_attribution+t_guard_kill_rc_precedence+t_guard_kill_json_purity+全套923綠 | VERIFY:[[Verification/2026-07-10_guard殺傷力驗證]]
  WHY:[2026-09-29 Projects/存量漂移改法_計劃]guard settle 對「已 pass 但預告句還在」補改句(以前一律回 0 印已轉正),前提不符回 2——把 settle 當重跑無害在腳本裡呼叫的地方會看到新的失敗;--test 只在待完成時要、--date 只給補改句用。轉正日期依序取 --date、那篇已寫的日期、守衛紀錄第一次變成 pass 的提交(那筆也是檔案第一次出現就不算、shallow 擋),★不拿今天充數★;不用 git log -S 合約文字:settle 是原地換行、出現次數不變,找不到轉正那次(設計審 r1 四席報到)
  WHY:[2026-09-30 [[Projects/漂移修法補強_計劃]] 第 3 節]settle 找不到某種預告句時的提醒改成「找不到<名稱>——可能已經是轉正後的說法(不用改),或被手改過(看一下)」:rtb 用 drift fix --kind c1 修時,已經手改成轉正說法的句子被講得像出錯。不區分兩種情形(前兩版要工具自己辨認轉正後的說法,設計審 r2 整類拿掉),由人看;drift fix c1 的結果訊息接同一支函式的同一句,不改判定與回傳值 [test:t_drift_fix_c1_missing_message]
  WHY:[2026-09-29 Projects/存量漂移改法_計劃]改句、前提、轉正日期推導放 guard 這邊,drift fix 往下呼叫、guard 不呼叫 drift;settle 句下一個非空行已經是人手補的「已轉正」段時刪掉 settle 句、不再疊一行,待完成的轉正與補改走同一支——同一種句子不因入口不同而結果不同
  WHY:[2026-10-01 [[Projects/併發與效能表態要合約背書_計劃]]]kill-add 多 --covers(驗過的題目 id,只收標了 needs_backing 的題;同一條配方只多帶 covers 就只更新 covers);配方身分改由共用函式 _kill_recipe_key 判(同筆記、invariant、file、old 的 json 序列化雜湊)——kill-add 判重、kill-log 的 recipe_id、寫表態分組三處共用
  WHY:[2026-10-01 同上]kill-log 每筆多 covers、recipe_id、head_sha(沙盒實際檢出的完整 sha,先取 sha 再用它建沙盒)、weak(整套一起跑、flaky 平台、配方所在筆記有未提交改動、寫檔後修改時間沒能錯開任一成立;最後一項 2026-10-02 加,見 [[Projects/殺傷力驗證編譯快取誤判_計劃]]);既有 commit 欄語意不變;kill-log 現在有兩個讀者(gov 統計、寫表態算背書),都走 repo 既有的 errors=replace 逐行容錯讀(代碼審 r1 架構席:原本另寫的位元組讀法與寫入前補殘行換行是第二種做法,已拿掉);guard 層的 kill-add 因 --covers 多了一條對題目表(_stack_spec_by_id)的依賴
  WHY:[2026-10-01 [[Projects/殺傷力配方失配提醒_計劃]]]配方失配(程式重構後原文找不到或出現好幾次)原本只有手動跑 guard kill 才看得到(rtb 2026-10-01 巡檢一次 10 條)。現在三處補上:kill-add 寫入時驗「這次要寫進去的那一條」,不是恰好一次就在標準錯誤多印一行提醒、照舊寫入(保留「宣告不擋、跑時擋」,既有測試刻意用失配配方測 guard kill);doctor P2 每次逐條數(只提醒,--ci 記 check-p2);kill-rm 給失配配方一條修法(身分含原文,不先移掉舊的就改不了)。guard kill 的判法不改,判斷函式重演它的走法(2026-10-02 [[Projects/殺傷力配方當場試跑_計劃]] 只給它加了挑配方與交回結果的選用參數) [test:t_guard_kill_add_warns_drifted_recipe] [test:t_doctor_kill_recipe_drift] [test:t_guard_kill_rm]
  WHY:[2026-10-02 [[Projects/殺傷力配方當場試跑_計劃]]]rtb 修配方時重加一條要跑整篇才知道殺不殺得掉,P2 也看不出「原文對得上卻殺不掉」。guard kill 加 --id(對整篇比對、規則跟 kill-rm 同一支,在合約片段過濾之前;對到格式壞的回 2 叫人先 kill-rm,判法跟 P2 同一支 _kill_recipe_judge,不讓人照列表抄短身分踩進既有的崩潰;代碼審 r1 抓到原本只擋不是物件、r2 抓到另寫一支判法跟 P2 結論不同);kill-add --try 寫完只跑那一條,回傳碼照 guard kill、★不看 weak★(筆記剛寫沒提交、weak 一定是 true,看它的話回傳碼分不出殺不殺得掉),另印背書不採信;doctor P2 另列最近一次真跑判 survived 的配方,閘名另開 check-p2s(照 check-s/check-s2 先例,kind 用 warned 治理帳的多日沒人理與折疊才算得到) [test:t_guard_kill_only_ids] [test:t_guard_kill_add_try] [test:t_doctor_p2_lists_survived]
  WHY:[2026-10-02 同上 設計審 r1 正確性席]P2 的 survived 清單取每條配方「最近一筆」比 ts、不比檔內順序:本 repo 的 kill-log 進版控,多個會談各自追加再合併後檔內順序可能倒。跟合約背書刻意不同——背書判 survived 看這版任何一筆、跟順序無關;同 ts 取先出現的,跟背書取最新那筆同一個規則。ts 是當地時間不帶時區,guard kill 寫 ts 那句改成帶時區時一起改
  PITFALL:[2026-10-02 同上 代碼審 r1–r3]guard kill --id 擋格式壞的配方,同一類問題連三輪:r1 只擋不是物件、r2 另寫一套判法跟 P2 結論不同、r3 改用 P2 判法但它在 file 不是正式寫法時停在 path、不看 old/new。第三次換形狀:guard kill 在當掉的兩步原地擋(數原文前、原文恰好一次之後,記 error「配方欄位格式不對」),第四輪(另開一輪)發現原地擋只抄了判法的一部分,改成判法與 guard kill 共用 _kill_old_issue/_kill_new_issue 兩支——同一個判斷只寫一次;落單替身字元那一類試過讓寫 kill-log 與印 --json 經 _kill_esc,上限輪發現壞字元會寫進進版控的帳、讓 lumos gov 當掉,撤回、整類留在 [[Issues/guard kill遇到格式壞的配方整支崩潰]];--id 只擋判法說的 malformed;對照測試把「配方欄位格式不對」也算 malformed ↔ error [test:t_guard_kill_only_ids] [test:t_kill_recipe_check_matches_guard_kill]
  PITFALL:[2026-10-02 同上 設計審 r1 三席實測]「原文那段已列過的不重複列」原本收所有不是 ok 的配方,設定檔壞時每條都判「設定讀不了」→ survived 清單整段變空;只收真的逐條列出的狀態碼,cfg 與 noroot 不收 [test:t_doctor_p2_lists_survived]
  PITFALL:[2026-10-01 設計審 r2–r3 正確性席實跑]在工作目錄用 realpath 前綴判圍欄,跟 guard kill 判得不一樣:它的工作樹是「暫存資料夾/wt」、從 HEAD 檢出,所以 `../wt/x` 爬回來算在內、解析到 repo 頂本身算逃逸、連結迴圈是開檔失敗不是逃逸、沒提交/被忽略/子模組裡的檔它沒有。判斷函式原本照這些重演,代碼審四輪都被抓到新的對不上(大小寫、Unicode 寫法、檔案連結還原、記憶體),2026-10-01 改成規定 `file` 必須是提交裡的正式路徑、其他一律提醒改寫不預測;對照測試每一格用獨立 repo 真跑 guard kill(同一組的格子會被 guard kill 的還原互相污染) [test:t_kill_recipe_check_matches_guard_kill]
related:
  - "[[Projects/guard殺傷力驗證_計劃]]"
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/test-profile-multiplatform]]"
  - "[[Verification/2026-07-10_guard殺傷力驗證]]"
  - "[[Projects/併發與效能表態要合約背書_計劃]]"
  - "[[Projects/殺傷力配方失配提醒_計劃]]"
aliases:
  - 殺傷力驗證
decisions:
  - content: 拿掉 2026-07-10 那份已 stale 的驗證背書(態數升級後前提不成立,E1 連喊 24 天 207 次沒人理——機制空轉週報首批)。目前 guard kill 沒有有效驗證紀錄;重驗要在有 kill 配方的消費端專案跑一輪,排進下一批。
    id: d1
    decided: 2026-08-22
    valid: true
  - content: 歸因需要測試輸出把「失敗標記」和「測試名」放同一行或 5 行內:test_lumos.py 的 runner 在每支失敗測試後印「✗ FAILED <名>(N 條斷言)」。2026-08-22 第一次真跑 kill(canary-audit 落盤自驗配方)判 killed_unattributed 就是因為這個。
    id: d2
    decided: 2026-08-22
    valid: true
verified_by:
  - "[[Verification/2026-08-22_guard-kill首次真跑]]"
  - "[[Verification/2026-09-22_預告合約首個真專案]]"
about_code:
  - scripts/lumos
---
# guard-kill（殺傷力驗證）

## 概述

合約鏈最後一哩：`★INVARIANT★→[test:]` 只證「保鑣存在」，`guard kill` 真的打一拳——隔離 worktree 裡故意弄壞被守護的行為，綁定測試必須翻紅；全綠＝稻草人證據（rc 1）。設計三輪 panel 收斂見 [[Projects/guard殺傷力驗證_計劃]]，golden 凍結 `governance/golden/guard-kill/`。

## CLI

- `lumos guard kill-add <node> "<KEY子字串>" --file F --old X --new Y [--test 名] [--platform P] [--note] [--covers 題目id,…] [--try]`:寫入成功時「下一步」印只跑這一條的 `guard kill --id`。`--try` 寫完(含只更新 covers)當場只跑這一條,回傳碼照 guard kill;試跑那筆一定是弱證據(筆記剛寫沒提交),另印一句合約背書不採信、提交後跑哪一行;試跑回 2(drifted/abort/error)時標準錯誤印「配方已寫進筆記,試跑沒跑成」,跟寫入失敗的「擋下」分得開。
- `lumos guard kill <node> ["<KEY子字串>"] [--platform P] [--json] [--keep-worktree] [--id <短身分> …]`:`--id` 可重複,只跑對到的那幾條;比對規則跟 kill-rm 同一支(對整篇、8 碼以上前段、零條或多條擋),在合約片段過濾之前;對不到時標準錯誤列出這篇每條配方、結尾印「只跑某一條」;對到格式壞的配方(跟 P2 同一套判法:guard kill 會拒跑或程式出錯的那幾種)回 2 叫人先 kill-rm。
- `lumos guard kill-rm <node> --id <短身分>`:移除一條配方(短身分是共用身分函式算出的前 12 字元,kill-add 提醒與 doctor P2 逐條列出的修法裡都有、guard kill 每條結果行 `id=` 也有;平台根找不到那種整個平台合併成一行的不附;給 8 到 64 個十六進位字元,從頭比對)。不帶 `--id` → 唯讀列出這篇每條配方的短身分、合約片段、檔、原文前 30 字、test、平台(原文對得上的也列;[[Projects/殺傷力配方修補體驗_計劃]])。
- kill-add 的 `--file` 從配方平台根**所在 repo 的最上層**算起(guard kill 在那個 repo 開工作樹,實際就是這樣算;平台根是子資料夾時要把子資料夾寫進路徑)。
- guard kill 每次寫檔(套壞法、還原)之前,等到跟同一組上一次寫檔、上一次跑測試結束都不同秒(最多等 3 秒),寫完讀回修改時間確認錯開(只到 2 秒的檔案系統會再碰一次,最多 3 次;還是不行就把那條結果記成弱證據、標準錯誤整次印一行)。理由:測試工具靠「修改時間到秒 + 大小」判斷要不要重編(Python 編譯快取、macOS 內建 make),同一秒寫出同大小的檔會沿用上一次的編譯結果,誤判雙向——無害壞法被判 killed、傷害壞法被判 survived。不把時間設到未來(綁定測試拿修改時間跟現在比時會造出新的假 killed)。代價每條配方多約 1.4–1.9 秒([[Projects/殺傷力驗證編譯快取誤判_計劃]])。還原沒錯開的檔在被成功重寫之前、以及在那期間跑出來的 baseline,同組後面沿用到的結果都記弱證據。
- 還原(`git checkout`)用的是解開連結後實際被改的那支檔、照字面認路徑(`:(literal)`);原本用配方寫的字串,`file` 是連結時只還原連結本身、真檔一直壞著,同組後面的配方被判成強證據的 killed(2026-10-02 代碼審第 3 輪抓到,改動前就有)。
- guard kill 人讀輸出每條結果行在判定之後附 `id=<短身分>`(放在人寫的合約片段與 test 名前面,偽造的 id 只會出現在真的後面);`--json` 不變(旁路欄 `_rid` 與 `_logged` 一起濾掉,既有 `recipe_id` 照舊)。
- rc（2026-07-29 七態後的優先序，`[test:t_guard_kill_rc_precedence]`）：任一 survived=1；drifted/abort/error 存在且無 survived=2；**全部只有弱證據（`killed_unattributed`／`timed_out_weak`）=1**(這裡的弱證據指這兩種判定;`weak` 欄是另一件事,不影響 rc——修改時間沒錯開只讓 `weak` 為 true)（不放行——弱證據不算接住）；有強證據 killed 且無錯誤=0。舊版「全 killed（含 timed_out）=0」已作廢：把逾時當殺掉是假強殺。
- `lumos gov` 第 5 支 load 撈 kill 留痕；guard list 顯示 `[kill✓]`。

## 配方失配提醒(kill-add 提醒、doctor P2、kill-rm)

設計與三輪審計見 [[Projects/殺傷力配方失配提醒_計劃]]。三處共用 `scripts/lumos` 的 `_kill_recipe_judge`(判一條)與 `_kill_recipe_id`(身分)。

**規定正式路徑**(Enzo 2026-10-01 裁,代碼審第 4 輪後):配方的 `file` 必須是提交裡的正式路徑——`git ls-tree` 列出的寫法、一般檔(不是連結或子模組)、組合寫法、不以冒號開頭(git 還原時會當成特殊語法)、這條路徑與任一層上層不分大小寫與寫法後不跟提交裡別的路徑撞名(macOS 上檢出會互蓋、可能繞連結跑到 repo 外)、Windows 上不含反斜線或冒號。判成正式路徑後讀的是提交裡的內容(`git cat-file blob HEAD:<file>`),不讀工作目錄(代碼審第 5 輪資安席:讀工作目錄會被撞名繞到 .git 或 repo 外)。不是的一律判「不是提交裡的正式路徑」並請人改寫(提交裡有去掉 `./` 與多餘斜線、不分大小寫與寫法後相同的正式路徑就點名;含 `..` 的不建議),★不預測 guard kill 會怎樣★——前四輪代碼審一路模擬它怎麼解析怪路徑,每輪都被抓到修正自己引進的 major。

**正式路徑時,判斷函式跟 guard kill 的對照**(兩邊不分家靠 `t_kill_recipe_check_matches_guard_kill`,一格一格真跑 guard kill):

| 判斷函式的結果 | guard kill 跑到同一條 | 什麼情況 |
|---|---|---|
| ok | 套上壞法、還原得回去,照常判殺得掉或沒殺掉 | 原文恰好一次 |
| hits | drifted「old 命中 N 次」 | 原文 0 次或好幾次 |
| undecodable | 讀檔時程式出錯、回傳碼 1 | 讀不成 UTF-8 |
| malformed | error「test 名不合法」或程式出錯 | 不是物件、platform 是清單或物件、test 轉成字串後過不了白名單、file 不是字串或含 NUL(平台與 test 都過了才判);old 不是字串(讀得到檔時)、old 或 new 沒寫、new 不是字串或含寫不成 UTF-8 的替身字元(原文恰好一次時) |
| path | 不預測 | 不是提交裡的正式路徑 |

**判的順序照 guard kill 走到哪一步**:分平台 → test 名白名單 → file 型別 → 正式路徑 → 讀檔 → 數原文 → 套壞法(new);欄位讀法也照它(old/file/test 沒寫當空字串、test 先轉字串)。

判不了的:設定檔讀不了(壞 JSON、不是物件、`load_platforms` 丟例外)、平台不在設定裡、平台根找不到、不在 git repo 或提交讀不了——kill-add 印一行「沒驗原文」照舊寫入,P2 各自列出(平台根找不到每個平台只列一條)。設定檔讀不了時 P2 照樣逐條走,不用讀設定就判得出的格式不對照列。

**kill-add**:判重之後、寫入成功並放掉鎖之後驗「這次實際寫進去的那一條」(只補 `--covers` 時驗既有那條、用它自己的平台);不是恰好一次就在標準錯誤多印恰好一行(含可直接貼的 kill-rm 修法),標準輸出與回傳碼不變。`--old` 或 `--new` 整欄等於 kill-rm 範本的待填字樣就擋下回 2(待填字樣原樣寫進去,guard kill 會把程式換成這串字、語法錯誤讓測試變紅而判成殺得掉;只是含有這串字的照寫)。讀—改—寫整段拿筆記庫寫入鎖;驗原文(要跑 git,每支最多等 10 秒)放在寫入成功、鎖放掉之後(鎖 30 秒沒放會被別人接手)。

**人寫的字怎麼印**:配方的檔名、平台、合約片段印進提醒前一律加引號、跳脫引號與控制字元(類別走共用的 `_PATH_SPECIAL_CATS`);設定檔來的字(平台根、讀不了的原因)、例外訊息、筆記路徑、kill-add 成功行的 test 名與舊 covers、Check T 那段的筆記路徑與平台名也跳脫;可以照貼的修法與 kill-rm 範本裡,帶控制字元的筆記名與欄位改印佔位字(引號擋得住 shell 斷字、擋不住終端把整行蓋掉)——筆記與設定可能來自不可信的提交(代碼審第 1、2 輪資安席)。

**doctor P2**:放在 P 段之後,跳過的節點照 P 段(verification 型、superseded、stale),再多跳沒有配方的。用 warn_soft 印(回傳碼不變,一般與 `--strict` 一樣),預設每段最多 3 條、`--verbose`/`--ci` 全列;`--ci` 跑時記 `check-p2` 事件。每條、每篇、整段各自包例外保護。

同一段第二個提醒(2026-10-02):殺傷力帳本裡現有配方最近一次真跑判 survived 的,列短身分(從筆記那條配方算)、合約前段、那次日期與版本、重跑與 kill-rm 兩個指令;原文那段已逐條列過的不重複列,設定檔讀不了時照列。行尾提示:那次證據弱、配方指的檔之後改過(單一檔 `diff --quiet`,檔名照字面、標準錯誤收掉,整段 20 秒上限)。綁定測試改過不觸發行尾那句(配方不記測試檔),所以標題寫「之後補強過測試的先重跑」。自己一個例外保護;`--ci` 記 `check-p2s`。帳本只在跑過 guard kill 的機器有。

**kill-rm**:對到零條、對到不同完整身分的多條、短身分太短都擋下回 2;對到的全是同一完整身分(手改造成的重複)一起移除。移除前印每一條的完整內容與 kill-add 範本(`--old` 與 `--new` 都是待填字樣、不抄舊壞法——程式改過之後舊壞法常常也套不上,rtb 上線回饋;舊壞法在完整內容那一行對照);剩下的配方都對不到的 KEY 行拿掉 `[kill:recipes]`;寫後自驗用自己的一支(kill-add 那支遇到格式壞的元素會崩潰)。kill-log 舊紀錄不刪。

**誠實界線**:只驗「原文還找得到、而且只有一處」,不驗套用壞法之後測試還會不會翻紅;讀的是提交(HEAD)裡的內容,跟 guard kill 的工作樹同一份(沒提交的改動不算、檢出時的 eol/smudge/LFS 轉換不涵蓋)——照提醒改寫後先提交,再跑 `lumos guard kill <節點>` 確認。

## 實作位置

`scripts/lumos`：`_kill_read_recipes`/`cmd_guard_kill_add`/`_kill_run`/`cmd_guard_kill` + INV_TAG_RE 擴 kill + KILL_REF_RE + gov/gitignore/cochange 三處同步。測試 `t_guard_kill`。挑配方 `_guard_kill_pick`(共用 `_kill_norm_prefix`、`_kill_match_prefix`、`_guard_kill_rm_rows`)、試跑 `_kill_add_try`、P2 第二個提醒 `_kill_p2_survived`/`_kill_log_latest`/`_kill_file_changed_since`、跳過規則 `_kill_note_skipped`。

## 相關模組

- [[Projects/guard殺傷力驗證_計劃]]
- [[Systems/check-t-sentinel]]
- [[Systems/test-profile-multiplatform]]
