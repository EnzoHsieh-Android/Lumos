---
type: system
status: done
created: 2026-07-10
updated: 2026-09-30
self_audit: sonnet/2026-07-24
about_code_stamp: batch-2026-08-23/2026-08-23/2faf3eec082c
tags:
  - type/system
  - status/done
  - risk/守衛面
  - scope/guards-gates
summary: |-
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
  WHY:[2026-10-01 同上]kill-log 每筆多 covers、recipe_id、head_sha(沙盒實際檢出的完整 sha,先取 sha 再用它建沙盒)、weak(整套一起跑、flaky 平台、配方所在筆記有未提交改動任一成立);既有 commit 欄語意不變;kill-log 現在有兩個讀者(gov 統計、寫表態算背書),都走 repo 既有的 errors=replace 逐行容錯讀(代碼審 r1 架構席:原本另寫的位元組讀法與寫入前補殘行換行是第二種做法,已拿掉);guard 層的 kill-add 因 --covers 多了一條對題目表(_stack_spec_by_id)的依賴
related:
  - "[[Projects/guard殺傷力驗證_計劃]]"
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/test-profile-multiplatform]]"
  - "[[Verification/2026-07-10_guard殺傷力驗證]]"
  - "[[Projects/併發與效能表態要合約背書_計劃]]"
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

- `lumos guard kill-add <node> "<KEY子字串>" --file F --old X --new Y [--test 名] [--platform P] [--note]`
- `lumos guard kill <node> ["<KEY子字串>"] [--platform P] [--json] [--keep-worktree]`
- rc（2026-07-29 七態後的優先序，`[test:t_guard_kill_rc_precedence]`）：任一 survived=1；drifted/abort/error 存在且無 survived=2；**全部只有弱證據（`killed_unattributed`／`timed_out_weak`）=1**（不放行——弱證據不算接住）；有強證據 killed 且無錯誤=0。舊版「全 killed（含 timed_out）=0」已作廢：把逾時當殺掉是假強殺。
- `lumos gov` 第 5 支 load 撈 kill 留痕；guard list 顯示 `[kill✓]`。

## 實作位置

`scripts/lumos`：`_kill_read_recipes`/`cmd_guard_kill_add`/`_kill_run`/`cmd_guard_kill` + INV_TAG_RE 擴 kill + KILL_REF_RE + gov/gitignore/cochange 三處同步。測試 `t_guard_kill`。

## 相關模組

- [[Projects/guard殺傷力驗證_計劃]]
- [[Systems/check-t-sentinel]]
- [[Systems/test-profile-multiplatform]]
