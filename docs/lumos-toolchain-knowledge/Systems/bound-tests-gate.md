---
type: system
status: done
created: 2026-08-22
updated: 2026-10-31
about_code_stamp: batch-2026-08-23/2026-08-23/5461ed371d06
self_audit: sonnet/2026-08-30
aliases:
  - 受波及合約測試真跑閘
  - bound tests
  - 合約測試閘
tags:
  - type/system
  - status/done
  - scope/guards-gates
summary: |-
  WHY:全套分片改照耗時分:執行器讀 `governance/test-durations.json`,權重由大到小丟給總耗時最少的一份(下限 0.05 秒、平手比支數);沒有表照名字輪流分,表格式不對每一份都擋;同一個 PR 有新推送就取消舊 CI,推到 main 每個提交各自一組不被取代 [出處:[[Projects/推送與CI提速_計劃]]] [因:照名字輪流分時 CI 各台 6.1–14.3 分不等,最慢那台決定整次時間] [不選:主線同一提交略過全套與快轉合併(設計審 r1 三席指出 PR 與主線環境對不齊、排隊中的主線 CI 會被取代,只省機器時間不省人的等待,使用者裁定拿掉);讀表失敗各份自行退回輪流分(各份可能混用兩種分法、聯集出錯)] [test:t_runner_shard_by_duration] [test:t_ci_yml_speed_shape]
  WHY:耗時表的刷新做成 `lumos test-durations refresh` 子指令、不放進測試執行器的旗標,耗時表列進簿記檔清單 [出處:2026-10-14 [[Projects/推送與CI提速_計劃]]] [因:它改寫進版控的檔,屬於主程式的工作;表錯只影響分得平不平均、不影響跑了哪些,所以只改它的提交不讓代碼審留痕失效、推送判成文件改動] [不選:執行器跑完自動改表(每次推送都會帶一個表的改動)] [test:t_test_durations_refresh] [test:t_codeloop_pass_survives_bookkeeping_commits]
  PITFALL:CI 分片那一步的子殼層繼承 Actions 預設的 bash -e,測試一紅子殼層就直接結束,紅的那份印不出耗時(離開碼照樣保留,判定不受影響) [出處:2026-10-14 推送與CI提速 代碼審 r1 通才席、合約圖譜席] [根因:errexit 會被子殼層繼承,rc=$? 與之後的 echo 沒機會跑] [修法:子殼層開頭 set +e] [test:t_ci_yml_speed_shape]
  PITFALL:包子程序跑整檔的測試自己另設的超時比單支上限 180 秒緊很多時,同一台 CI 機器的另一份一變重就連續超時(本機與主線照綠) [出處:2026-10-21 安全證據閘合併請求 CI 連兩次紅] [根因:CI 一台同時跑兩份、互搶 CPU,t_test_quality_cli 在主線 CI 已要 40 秒卻只給 60 秒] [修法:內層超時放寬到 150 秒,仍在單支上限之內] [test:t_test_quality_cli]
  WHY:[2026-10-06 [[Projects/CI加速_計劃]]]分支與合併請求的 CI 拆成三個工作(推 tag 另有一個只跑安全證據判定的工作,見 [[Systems/安全證據閘]]):prep(編譯類檢查、決定範圍、純文件子集)→ shards(全套用 matrix 分給多台機器、每台背景跑自己那幾份 `--shard i/$SHARD_TOTAL`)與 gates(自主迴圈測試、健檢、代碼審留痕閘、筆記形狀閘、存量漂移檢查、回頭重讀提醒、錨點驗證)同時跑;每個工作各自抓完整歷史、補本機 main、裝 Python;後盾步驟的指令逐字照搬(`t_ci_yml_matrix_and_gates_shape` 用拆分前的指紋守),全套跟後盾不再有先後——全套紅了後盾照跑 [出處:Enzo 2026-10-06「CI 好慢,拖慢整個開發速度」] [因:一台機器切 4 片已跑到 32–38.5 分、離 45 分上限只剩約 7 分] [不選:主線推送在同一棵檔案樹已於合併請求跑綠時不重跑全套(看提交歷史的測試在合併請求與主線結果會不同,見 [[Systems/測試假綠形態]] 鏡頭逾時暖快取那條;Enzo 改裁不做);本機全綠就不等 CI(要改全域規則)] [test:t_ci_yml_matrix_and_gates_shape]
  WHY:CI 在 pull_request 事件多一步建出追蹤 origin/main 的本機 main(git branch --track main origin/main),讓 PR 跟推到 main 時是同一種環境 [出處:2026-10-03 第一個 PR(EnzoHsieh-Android/Lumos#1)CI 紅] [因:PR 取出的是不在分支上的合併提交、本機沒有 main,t_lens_timeout_keeps_warming_cache 與 t_codex_s1_lens_arm_claim 以 main@{upstream} 找主線而整支紅;容器重現:沒本機 main 紅、補上就綠] [不選:改兩支測試各自退回 origin/main(dispatch-lens 認主線的規則也要跟著改,範圍更大)]
  WHY:_classify_test_refs 多一個呼叫者:note-shape 的筆記測試綁定第①道,名稱逐一重包成 `[test:名]` 再交(同修正關卡),判 real 才算指得到 [出處:2026-10-03 [[Projects/筆記測試綁定要存在_計劃]]] [因:判存在不另寫第二套] [test:t_note_shape_test_refs_touched_note]
  WHY:[2026-10-02 Projects/代碼審修正關卡第0步_計劃]「`[test:]` → resolve_test_refs → 名稱規則(2026-10-15 起是 _test_name_ok,原本是白名單)→ real/fake/dangling/bad-name」抽成 `_classify_test_refs`(修正關卡第 3 項也用),判定不變;修正關卡在自己建的隔離工作樹裡呼叫 `_bound_tests_check`(帳與測試快取落在樹裡、跟著刪) [出處:Projects/代碼審修正關卡第0步_計劃] [因:推送前合約測試閘與修正關卡第 3 項要用同一套判法,分開寫會漂]
  KEY:★INVARIANT★ code-loop check 對 impact 固定席上合約綁的測試逐支真跑,任一紅/懸空(dangling/fake)/方法名不合法/★證不出跑過(unfilterable)★ → blocked=True rc1;沒 run_cmd/diff 算不出/無固定席/沒綁 → 不擋但寫 gate=bound-tests 帳 [test:t_bound_tests_gate] [audit:sonnet/2026-08-22]
  KEY:★閘不得把「指令回成功」當「測試跑過」★(2026-09-09 消費專案接入靜默失效 [F];r1 代碼審把判準整條換掉):主力證據是★逐支看測試工具自己的輸出有沒有說「執行了 N 支(N≥1)」★(_RAN_EVIDENCE,只填實測過「跑 1 支」與「跑 0 支」兩種輸出的 profile:swift-xctest/csharp-xunit/node-jest(node-vitest 共用同一條)/playwright/python);沒有樣式可比的 profile 才退回過濾能力冒煙測試(拿不存在的測試名跑一次看回不回 0)。任一支證不出來 → 狀態 unfilterable、不報綠,擋的路徑上跟紅一樣擋 [test:t_bound_tests_unproven_blocks_push]
  KEY:為什麼不是只用冒煙測試(同上,r1 實測推翻第一版):★大多數測試工具都分不出「測試不存在」與「測試通過」★——xcodebuild 三段 -only-testing 但方法名打錯回 0、dotnet test --filter 對不到回 0、jest -t 對不到回 0;只有 pytest(回 5)分得出來。只靠冒煙測試等於把最常見的幾種棧全判成不可信,不是擋錯人就是等於沒擋 [test:t_bound_tests_rejects_unfilterable_cmd]
  KEY:★xcodebuild 帶 -quiet 時跑 1 支跟跑 0 支的輸出一模一樣★(2026-09-09 在 calc-ios 實測,逐字比對過兩份輸出):所以 swift 骨架指令刻意不帶 -quiet,unfilterable 的訊息也直接點名這件事;dotnet 的解法是尾巴加 `-- RunConfiguration.TreatNoTestsAsError=true`(實測對不到回 1、對到回 0),已寫進骨架
  KEY:★「擋」跟「講」是兩個地方★(2026-09-09 代碼審 r2 blocker):判定在 _codeloop_guard_verdict、但印給人看的在 cmd_code_loop,後者原本只認 green/red——低風險推送因此在假綠上一個字都不印就放行,高風險擋下時也看不到逃生指令。動判定一定要回頭看列印分流 [test:t_code_loop_check_speaks_about_unproven]
  KEY:證據行不得被輸出截斷砍掉(同上 r2):輸出超過 256KB 取頭尾各半時,符合證據樣式的行要從中段撈回來(_kill_cap 的 keep_re);★審查席舉的 jest 實例實測不成立(jest 29 摘要仍在最後一行),這是防禦性修法★——沒有它等於押注「所有測試工具都把摘要印在最後」
  KEY:整套跑(run_cmd 沒有 {method})那條路也驗證據(同上 r2):整套跑但一支都沒執行、退出碼仍為 0 的情況不得報綠;★天花板:整套跑只證得出「有測試跑過」,證不出「你綁的那一支跑過」★
  KEY:★這一層不驗「跑的是不是正確那一支」★(同上 r2 訂正):它只數輸出裡有沒有「N passed」,不比對測試名。「合約綁的名字對到別支測試」是更早的存在性靜態檢查(resolve_test_refs 判 real/dangling/fake)擋下的,別把既有防線的功勞算到新機制頭上
  KEY:零覆蓋不再靜默(同上 [E]):四種來源各自出聲(找不到知識庫/沒節點引用/沒綁測試/算不出範圍),訊息帶「受波及合約測試」關鍵字以通過 pre-push 對 check 輸出的 grep 過濾 [test:t_bound_tests_explains_no_pins]
  KEY:(2026-09-09 表態閘起)pre-push 對每個分支 ref 都叫 check,低風險那一路帶 `--bound-tests-advisory`:紅了只印、寫帳、不擋(2026-09-07 人裁「低風險只提醒」搬進 check 內部執行,不再另呼叫 bound-tests --advisory);高風險不帶旗標,上面那條合約照擋;tag 推送仍走獨立的 bound-tests --advisory [test:t_prepush_computes_impact_once]
  KEY:掛在 check(擋的路徑)不掛 pass——design-loop bound-tests-gate-c r1 架構席抓到的;去重鍵=解析後完整指令(同 kill);超時用 runner 同名 LUMOS_TEST_TIMEOUT,whole-suite 600s(同 kill)
  KEY:[2026-09-17 風險低放行]pre-push 在 code-loop check 之前多一段:對每個 ref 的範圍叫 `lumos spec-gate --push-check <範圍> --repo <根>`(2026-10-06 起用 _brange:新分支首推時是跟主線的分岔點,其他形狀同 _range,見 [[Projects/新分支首推會擋的閘改用真起點_計劃]]),rc1 就擋(風險低計劃留痕裡的測試沒全綠、或留痕過期);rc≠1 放行(fail-open;回傳碼 128 以上是被中斷,掛鉤停下,見下面 pp_stop_if_signaled 那行)。判定與訊息都在 [[Systems/規格閘]],這裡只管掛接 [test:t_prepush_hook_calls_spec_gate_push_check]
  WHY:[2026-09-30 Projects/存量漂移防線_計劃 [S18]]推送前掛鉤在 code-loop check 之後、test-layers 與全套測試之前多一段 drift check(每個 ref,分支與 tag 都查;code-loop 約 0.6 秒、它最壞每個 ref 60 秒預算加前置的 git 呼叫、全套 8 分鐘,便宜的先擋)。回傳碼:1 擋;128 以上(被訊號殺掉)整支掛鉤停下、不跑全套;其他非零(工具錯誤、git 太慢逾時、舊版工具沒有 drift)講一句「這次沒檢查」再放行。CI 那步回 1 印擋下原因並紅,其他非零照原碼紅(工具出錯寧可紅,同 code-loop gate、note-shape 兩步)——掛鉤與 CI 對「其他非零」刻意不同,CI 是最後一道後盾。掛鉤裡的上線標記註解是 lumos 截範圍起點用的,不能改寫。CI 的全套測試仍在它前面(CI 是後盾,順序只影響全套紅時這步有沒有跑到)。模式、判定與訊息都在 [[Systems/存量漂移守衛]],這裡只管掛接 [test:t_prepush_and_ci_wire_drift_check]
  WHY:[2026-09-30 推送閘接漂移檢查代碼審 r2 架構對齊席 F3]推送前掛鉤裡「rc1 擋、其他非零放行」的七道閘(每支檔有家、筆記形狀擋、spec-gate --push-check、code-loop check、drift check、2026-10-28 起的 Room 守衛 room-guard,以及 2026-10-09 起帶 --gate 的回頭重讀 note-audit reread-check)都先過 pp_stop_if_signaled:回傳碼 128 以上(被訊號殺掉,多半是 Ctrl-C)就印「<閘名>被中斷(rc=…),推送停下,後面的檢查不跑。」並以那個回傳碼離開、不跑全套——被中斷不是工具錯誤,當成放行等於按一下 Ctrl-C 就繞過那道閘;原本只有 drift 那道會停。anchor verify、doctor 那兩道是任何非零都擋(2026-10-14 起也先過 pp_stop_if_signaled;要接的呼叫列在掛鉤的「中斷就停」註解區塊、刻意不接的附理由),advisory 的(test-layers、bound-tests --advisory、pitfalls)恆放行,不接 [test:t_prepush_interrupt_stops_every_gate]
  PITFALL:[2026-09-30 推送閘接漂移檢查代碼審 r1 正確性席、併發回滾席、外家席實測;r2 正確性席、邊界席、架構對齊席、外家否決席]範圍起點的坑:①把 遠端舊值..本地新值 原樣當範圍,功能分支合過主線、或重定基底後 force push 時,git log 舊..新 會把合進來的主線提交(別人的轉正)算成這次的;②共用起點判法(_lens_push_base)只在舊值是全 0 或找不到時才算分岔點,主線只認 main/master 的 upstream;③CI 裡前一步 fetch 過,main 的 upstream 就是這次頂端,before 是全 0 或找不到時會判「頂端已在主線、沒有新東西」整步跳過。r1 折入時在掛鉤的 bash 與 CI 的 shell 各補一份起點算法,r2 查出兩份各有洞:CI 補法只在 before 找不到時換起點(合過主線照樣算進別人的轉正)、新分支首推退到頂端的父提交(一次推多個提交時前面的不查,頂端是合主線的合併提交時反而查進主線那一側);掛鉤的主線候選 upstream 排在遠端預設分支前面(git-flow、主線叫 trunk 時用到過期的 main/master)、交叉合併只看 git 挑的第一個合併基底。★現在起點只在 lumos 的 _push_range_start 算一處★:掛鉤原樣交 遠端舊值..本地頂端 加 --push-remote <遠端名> --pushed-ref <遠端 ref>,CI 交 before..sha(空的換成 40 個 0)加 --push-remote origin --pushed-ref "$GITHUB_REF";主線候選是遠端 HEAD、main/master 的 upstream、遠端 main/master,跳過指到 refs/remotes/<推送遠端>/<被推分支> 的那個(遠端與分支都比;推主線本身時用遠端舊值),其餘全部一起算分岔點(merge-base --all 頂端 加 所有候選),取離頂端最近的——r3 查出照順序取第一個候選時 git-flow 與 fork 兩頭顧不到、只比分支短名會把正本的 main 當成被推的那條跳過;每一個分岔點都是舊值的祖先才用舊值,否則用不是舊值祖先的分岔點裡歷史最長的那個;舊值或主線候選的 git 查詢本身失敗(逾時、跑不起來)算判不了,不退成只查最後一個提交。CI 裡 actions/checkout 不建 origin/HEAD,那步先照 github.event.repository.default_branch 補上,預設分支叫 develop/trunk 也找得到主線 [test:t_prepush_drift_range_ref_shapes,t_prepush_drift_start_mainline_shapes,t_ci_drift_start_shapes,t_ci_drift_default_branch_shapes,t_drift_check_push_start_edges,t_prepush_and_ci_wire_drift_check]
  KEY:逃生門 `code-loop check --skip-bound-tests --note` 或 `bound-tests --skip --note`(留痕 kind=skipped);CI 設 LUMOS_SKIP_BOUND_TESTS=1(CI 的全套在另一個工作同時跑當後盾)
  KEY:★2026-09-12 這道閘的核心保證被實際打穿過一次(Java 補棧代碼審 r1 資安席)★——閘驗的是「合約綁的名字有沒有出現在 discover_test_methods 掃出來的集合裡」,所以★掃描器認錯名字=閘直接失效★:當時 Java 的方法正則太鬆,一支「掛註解但不是 void 的誘餌方法」後面接一支完全沒掛註解的空方法,那支空方法就被收成真證據,健檢一聲不吭。教訓:新增任何語言的測試掃描時,除了「收得到真測試」還要有「收不到假測試」的斷言,兩邊都要 [test:t_java_profile_discovery]
  DEP:[[Systems/pitfalls-code-loop]]
  DEP:[[Systems/guard-kill]]
  KEY:[2026-09-11 多平台缺指令,Issues/多平台設定下測試指令被默默略過]沒設 run_cmd 改成★逐平台★——有指令的平台照跑,沒指令的平台那幾支列成 not_run(平台點名);全部沒指令才 no-config;原本碰到第一支沒指令就整批 no-config,連前面已判的懸空紅都被吞掉(違反上一行合約「任一懸空 → 擋」的原意)。訊息改由 _no_run_cmd_reason 給:多平台點名平台,最上層還留著 test.run_cmd 就照 2026-07-10 並存優先序講明它不生效、要搬;code-loop check 與 bound-tests 兩條路共用 [test:t_bound_tests_multiplatform_missing_cmd]
  KEY:[2026-09-12,2026-10-06 起改成多台機器,見上面那行 WHY]CI 的全套測試改成切 4 片同時跑(`--shard i/4`,跟推送前掛鉤同一支旗標);單行程版本已經從 25–27 分鐘漲到撞 job 上限 30 分被砍(8a45751b 那次),不是測試紅、是跑不完。上限同時拉到 45 分留餘裕;任一片紅就整步紅,四片的尾端都會印出來
  KEY:[2026-09-17]推送閘擋下時的逃逸自動記:code-loop check 回 rc1 那個分支多兩個 grep——「受波及合約的測試沒過」→ lumos loop escape --auto --stage push-gate;「tier=high 且」開頭的缺留痕句 → --stage push-gate-unreviewed(lumos 端查有風險低留痕才記);兩者都 || true,記帳失敗不能變成擋推送的第二個理由。單源:[[Projects/逃逸自動記_計劃]]
  KEY:[2026-09-18]推送前與 CI 的全套測試,純文件改動只跑文件子集(Enzo 裁「像這種改動 CI 可以跳過吧」「判成 light 的也不用」):掛鉤每個 ref 讀 pitfalls 的 suite,全部 docs → 分片改帶 `--suite docs`(執行器挑「讀真 repo 根、而且讀 README/根目錄文件/assets/docs 底下非圖譜文件」的測試,連看它呼叫的本檔輔助函式一跳;2026-09-18 實推量到舊挑法 209 支四片跑 234 秒、跟全套一樣慢——假環境裡順手寫 CLAUDE.md 的重測試全被挑進來;收緊後 63/1021 支、四片 21 秒,測試釘 ≤10% 且不含 t_ci_wait/t_slim_gate;讀真圖譜的測試平常不算;★推送碰到圖譜筆記時★(pitfalls 的 suite_graph)加 `--graph` 把讀★真★圖譜(lumos 找到的那個目錄名,不是任何 -knowledge 字樣:假環境 x-knowledge 會把 34 支評測 fixture 帶回來)的 12 支加回——圖譜健檢只驗結構、驗不到檢索品質(代碼審 code-文件子集收緊 r1/r2 通才席),合計 75 支、四片 55 秒;掛鉤先讀檔探執行器認不認得 `--graph`,不認得退全套;先挑子集再切片);改到程式但 spec-gate --push-check 判 light ★且 pitfalls light_ok★ 的,文件子集之外再跑 `--suite keys --keys <affected_keys>`(原始碼整字提到改到的頂層函式/檔名的測試;一個關鍵字選中 >30% 就丟),兩組各自分片、真的同時跑(2026-09-18 實測前一版是一組跑完才跑下一組,註解卻寫平行);keys 每片都 rc3(沒對到)不擋、講明 CI 會跑全套當後盾,有紅照擋;其餘全套。CI 只認 docs(push 事件用 before..sha 問 lumos;首推/force-push 對不到起點/pull_request 一律全套)。純文件推送的自主迴圈測試(整支 68 秒)兩邊都只跑讀真 CLAUDE.md 那一條(`-k real_claude_md`,接線測試真跑確認選得到 1 支);★light 推送前也一樣★,除非 pitfalls 的 `autoloop_full` 為真:affected_keys 有任一個整字出現在那支測試的原始碼裡(它測自主迴圈模組、主程式常數、兩支探針腳本),或抽不出任何關鍵字(不知道改了什麼就整支跑);整字比對只有 lumos `_keys_mentioned` 一份,執行器 `--suite keys` 也用它(代碼審 code-light自主迴圈 r1)——2026-09-18 在隔離工作樹造真 light 情境實測 108 秒 → 40 秒。CI 對 light 照跑全套當後盾。執行器不認得 --suite(讀檔探旗標)就退全套。push-check 輸出用 tee 即時印(r1 併發席:先存檔再印人會以為卡住);暫存檔全收 _PP_TMP 掛 trap。★誠實界線★:文件子集是「原始碼字樣」挑的,不是真的追蹤誰讀了哪個檔——第一版單看字樣挑到 254 支跑 9 分半比全套分片還慢,現在 docs/、governance/ 要跟真 repo 根寫法同現才算
  TEST:t_bound_tests_gate(綠/紅/懸空/逃生門/env/no-config/壞設定檔/新分支首推 12 斷言(2026-08-30 機械重數訂正,原記十));本 repo 實跑 42 支 29s
  WHY:[2026-09-29 [[Projects/最低Python版本改3.14_計劃]]]測試指令用 {python} 佔位符,由 lumos 代入自己那支直譯器並依平台加引號;原本吃 PATH 上的 python3,3.14 只以 python3.14 存在的機器會把每一支綁定測試跑紅、被當成「證不出跑過」擋推送。三處代入點(guard kill、合約測試閘本體、過濾探針)都經同一支函式 [test:t_test_run_cmd_uses_running_python]
  WHY:[2026-09-29 [[Projects/最低Python版本改3.14_計劃]]]pre-push 有 scripts/lumos 卻找不到 Python 3.14 就擋下,不再像以前「找不到 python 就放行、找到 3.9 就拿 3.9 跑」;沒有 scripts/lumos 的 repo 照舊放行 [test:t_hooks_block_without_python314]
  WHY:pp_cl_reason 加第六種 android_e2e,逃生路文字補 Android 端到端驗收那條(跑驗收、提交紀錄、waive 放行、LUMOS_SKIP_ANDROID_E2E=1);ci.yml 的擋下說明不加這一種 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r3 整合席] [因:CI 不跑這道,列進 ci.yml 是永遠不會出現的死條目;種類名帶數字,兩支守衛測試抽種類名的樣式改成收數字] [test:t_prepush_cl_reason_table_matches_lumos] [test:t_prepush_cl_reason_sentences_match_plan]
  WHY:[2026-10-30 Enzo 裁]推送被擋時掛鉤輸出的最後一行改成第一筆擋下那道閘實際跑的指令(`下一步:…`),全套測試紅與自主迴圈紅兩條不經彙總的路也各補一行重跑指令;重查會印該道修法,所以不把修法再抄一份;指令由各閘交給 `pp_record_block`,掛鉤自己印、不經 lumos,所以配舊版 lumos 走簡版彙總時也有 [出處:2026-10-30 研究報告現況核對抽 5 道閘] [因:原本最後一行是散文或 git push --no-verify,而受控實驗顯示訊息指名下一個做得到的呼叫才恢復得好(2609.35381 v2,OpenAI 模型與無終端情境,套到 Claude 是推論)] [不選:lumos 依閘名查表再填一個共用範圍(各閘範圍不同,新分支首推與推標籤會重查到別的東西,2026-10-30 代碼審抓到);只調換各閘順序(全套前的閘最後印的是彙總,換了也看不到);印預演指令(預演沒落地)] [test:t_prepush_next_step_is_the_call_the_gate_ran] [test:t_prepush_blocked_last_line_is_next_step]
  PITFALL:被擋時「最後一行是重查指令」只到掛鉤輸出為止,真的 git push 之後還會印自己的 error: failed to push some refs 那行 [出處:2026-10-30 代碼審實測] [根因:那行由 git 在掛鉤回非零後印,掛鉤管不到] [防回歸:量代理被擋後的行為時,要把這行算進它讀到的最後一句]
verified_by:
  - "[[Verification/2026-09-09_接入靜默失效七項落地]]"
  - "[[Verification/2026-09-11_多平台缺指令逐平台處理]]"
  - "[[Verification/2026-10-15_order-web實地跑vitest合約測試]]"
about_code:
  - .github/workflows/ci.yml
  - scripts/hooks/pre-push
  - scripts/lumos
---
# bound-tests-gate

# bound-tests-gate

> 白話:改到相依功能,以前工具只會「點名」那些功能綁的測試,跑不跑靠自律。現在 pre-push 每次呼叫的 `code-loop check` 會把被點名的測試當場跑完:紅的、綁了不存在測試的、名字不合法的,一律擋推送。

本機的掛接點在 `scripts/hooks/pre-push`(推送前呼叫 `code-loop check`,tag 推送另走 `bound-tests --advisory`);CI 那一側在 `.github/workflows/ci.yml`,全套與後盾閘分成平行的工作跑。

## 怎麼跑

★2026-09-07 起有兩條路★([[Projects/合約測試閘什麼時候跑_計劃]],人裁):
- **高風險推送**:照舊藏在 `code-loop check` 裡,紅了**擋**。
- **低風險推送**:pre-push 同一次 `code-loop check` 帶 `--bound-tests-advisory`(2026-09-09 表態閘起;之前是另外呼叫 `lumos bound-tests --advisory`,現在只有 tag 推送還走那條),紅了**印出來、記帳,但不擋**。
  不選「低風險也擋」的理由:擋下去最可能的結果不是人去修測試,是人改走 `--no-verify`
  ——而 pre-push 自己在別的地方就把那條當第三選項在教,那條零留痕。

★而且波及計算一次推送只算一次★:pre-push 算一份寫進暫存檔給這道閘(`bound-tests --from-json`)讀。
以前同步點名(`impact --sync-only --from-json`)也讀這一份;2026-09-11 起推送前的點名改由 [[Systems/每支檔有家]] 照家算,不再讀它。
算不出來時這道閘記 `range-unavailable` 放行,不拖垮別的檢查。

1. `impact --diff <range>` 取固定席(合約/事故/直接相依)裡帶合約的節點。
   ★新分支首推★:起點是空樹時改用主線 tip(`_mainline_ref`),不是放棄計算、也不是跑滿全部;
   連主線都問不到才記 `range-unavailable`。
2. 每個節點的 ★INVARIANT★ 行 `[test:…]` 用 `resolve_test_refs` 解平台前綴,再用 Check T 同一套平台真測試索引判存在(real/dangling/fake)。
3. real 的逐支用 `.lumos/config.json` 的 run_cmd 真跑(`_kill_run`,同 kill);去重鍵=完整指令。超時:單支 `LUMOS_TEST_TIMEOUT`(預設 180s,同測試 runner),整套(run_cmd 無 {method})600s。(2026-10-13 補:設了 `bound_tests.parallel` 就同時跑,見本篇〈同時跑幾支與 secs 的意思〉)
4. 任一紅 → check 回 BLOCKED(rc1),訊息列合約、測試、尾段輸出,並給 `--skip-bound-tests --note` 範本。

## 帳的類別(2026-09-07 拆細,不擋的都寫帳讓零觸發看得見)

`green` / `red-advisory`(低風險,只提醒) / `red-blocked`(高風險,擋) /
`skipped-flag`(人給了理由) / `skipped-env`(CI 環境變數) /
`no-config`(沒 run_cmd) / `no-pins`(沒固定席) / `no-bound`(固定席沒綁測試) /
`range-unavailable`(範圍算不出,含首推連主線都問不到) /
`whole-suite-deferred`(測試指令不可過濾、而且這次是低風險 → 不跑)。

★為什麼要拆這麼細★:紅了擋跟紅了只提醒,後果完全不同;人給理由跳過跟 CI 常態跳過,
意義也完全不同。混成同一個 kind 就回答不了人裁時掛的那條回頭條件(「只提醒到底夠不夠」)。
★耗時也拆成兩個獨立欄位★(`secs` 跑測試、`calc_secs` 算波及)(2026-10-13 補:secs 自此是牆上時間並帶 `secs_kind: wall`,沒帶的舊帳是逐項相加):
以前塞在自由文字的備註裡,回頭條件量不到。

`gov --stats` 看 bound-tests 那列就知道這道閘在這個專案有沒有真的開。

## 設計迴圈紀錄
`bound-tests-gate-c` r1 四席(通才/正確性邊界/可執行性成本/架構對齊)20 條:19 折 1 放行(hermetic:run_cmd 是專案自宣告指令,與 CI 同信任邊界)。我自己記帳走歪兩次(處置帳一輪只能一筆;每席都要留痕)才過閘,編號 -b/-c 是這樣來的。

## 回頭看條件
- 30 天後 `gov --stats` 若 bound-tests 只有 no-config/no-pins、零 green/red → 入口 hook 加「本專案沒設 run_cmd,合約測試閘沒開」提醒;再 30 天仍零 → 列入只退場不痛的機制檢討。
- 三次 check 超過 3 分鐘 → 加只跑 direct 相依的縮圈選項。(2026-10-13 補:只算帶 `secs_kind: wall` 的帳;本 repo 打開同時跑後實測約 1 分鐘)
- gov --stats 出現 red 且原因是外部資源 → 加單支白名單跳過。

## 鏡頭側呈現(2026-09-03 v1.1)

`lumos dispatch-lens` 對每條 ★INVARIANT★ 合約行用同一個 `_classify_one` 標「綁定測試:有/懸空/偽證據」或「★裸合約★」,並在段尾固定寫「有=方法存在,不代表跑過或有殺傷力(閘只看 rc)」。鏡頭是參考、本閘是判決:鏡頭讀 base 版合約行、閘讀工作樹版節點,分支改了合約行時兩邊可能不同。單源 [[Projects/派工鏡頭注入_計劃]] v1.1 節。

## 推送前掛鉤的回頭重讀那一段(2026-10-01 接上,2026-10-09 轉擋)

drift check 那段之後(2026-10-28 起中間隔一道 Room 守衛,見 [[Systems/room-guard]])、test-layers 之前,多一段 `note-audit reread-check`(回頭重讀守檔筆記,[[Projects/守檔筆記對照改動_計劃]]〈做法〉4;判定歸 [[Systems/筆記內容審]],呼叫那段歸 [[Systems/存量漂移守衛]])。2026-10-01 接上時只提醒:工具恆回 0,掛鉤只在 130(Ctrl-C)停、其他非零照推。2026-10-09 起([[Projects/舊句兩道轉擋_計劃]]〈掛鉤與 CI〉)掛鉤那段帶 `--gate`,改成跟上面「rc1 擋、其他非零放行」的幾道同一種形狀:回 1 擋下並印通用逃生段(2026-10-14 起擋下改成記下、跑完其他閘才在全套之前統一擋),128 以上原樣交給 pp_stop_if_signaled(刻意推翻「只有 130 停」——這道會擋人之後,被外部砍掉也不該當作放行),其他非零(含舊版工具不認得 `--gate` 回 2)講一句放行;標準錯誤不再丟。要接 pp_stop_if_signaled 的呼叫 2026-10-14 起列在掛鉤的「中斷就停」註解區塊,守衛照清單逐支驗被殺掉會停(原本那支數行數的測試併進去了,見下面〈推送前一次列出全部擋下原因〉)。★CI 那步不帶 `--gate`、照舊 continue-on-error 並吞掉回傳碼★,跟上面「CI 是最後一道後盾、工具出錯寧可紅」的慣例刻意不同:合併後主線 CI 用整個 PR 的累計範圍重算,候選與指紋跟作者本機看到的不同,擋在 CI 會誤擋;代價是 `--no-verify` 跳過本機掛鉤時這一道沒有兜底(人裁接受)。

## 同時跑幾支與 secs 的意思(2026-10-13)

WHY:`.lumos/config.json` 的 `bound_tests.parallel`(2–16 的整數)打開後,`_run_bound_tests` 先照原順序收集去重後要跑的指令,再用自建的 daemon 工作執行緒同時跑、最後照原順序組結果;一支出錯或被中斷就不再派新的,同批已開跑的子程序整個程序群組收掉;沒寫或不合法一律循序。本 repo 設 4 [出處:[[Projects/合約測試閘並行執行_計劃]]] [因:同一批 51 支循序 176.5 秒、同時 4 支約 56 秒,時間花在循序本身] [不選:預設就同時跑——消費專案的測試工具可能互搶建置目錄;縮小綁定範圍或因後面跑全套而跳過這道閘——改的是該守什麼或判定語意;ThreadPoolExecutor——工作者不是 daemon,程式結束與 Ctrl-C 都要等已開跑的測試跑完,map 依提交順序取結果讓排在後面的例外晚浮上來;主流程只 join 第一條執行緒——它先收工後變滿速空轉] [test:t_bound_tests_parallel_matches_sequential] [test:t_bound_tests_parallel_config_values]
PITFALL:閘回報與記帳的 secs 原本是每個綁定項目秒數相加,同一支被幾篇綁就加幾次,同時跑時又被重疊放大 [出處:2026-10-13 實測同時跑 CLI 報 215 秒、實際約 60 秒] [根因:sum(每項秒數) 不是牆上時間] [修法:改量跑測試那段的牆上時間,記帳多帶 secs_kind=wall;沒帶這欄的舊帳 secs 是相加值,不跟之後比] [test:t_bound_tests_secs_is_wall_time]
PITFALL:測同時跑被中斷的測試,在推送前掛鉤裡永遠收不到中斷、8 支照跑完 [出處:2026-10-13 推送閘實測紅] [根因:掛鉤在背景開測試分片,非互動 shell 的背景程序繼承「忽略 SIGINT」,Python 看到已忽略就不裝 KeyboardInterrupt] [修法:送中斷的子程序開頭先把 SIGINT 裝回預設處理] [test:t_bound_tests_parallel_interrupt_stops_dispatch]
WHY:同時跑時子程序一律經由 `_BtProcs.launch` 開:開之前看收尾標記、數一支「正在開」,收尾立標記後等正在開的都開完(最多 30 秒;期限在第一次收尾時定下,中途再按 Ctrl-C 重叫收尾也沿用同一個期限,不會越按越久)再整組收掉;收尾中途再按 Ctrl-C 也收完再走 [出處:2026-10-13 高風險代碼審第三輪併發席,[[Issues/合約測試閘並行收尾小問題]]] [因:舊版開完才登記、收尾最多等 2 秒,開程序卡更久或收尾中再按一次 Ctrl-C 都會在程式結束後留下孤兒] [不選:開程序與登記整段包在同一把鎖——同時跑的開頭會退化成一支一支開] [test:t_bound_tests_parallel_slow_spawn_reaped] [test:t_bound_tests_parallel_interrupt_reaps] [test:t_bound_tests_reap_deadline_not_reset]

## 推送前一次列出全部擋下原因(2026-10-14)

白話:推送被擋時,原本一次只看得到第一個原因,修好重推(每次掛鉤要跑幾分鐘)才看到下一個;現在全套測試之前那幾道便宜的閘全部跑完,一次列出全部原因,有任何一道擋下就在全套之前結束。

WHY:全套測試之前的 10 道閘(裁判簽名、簽名檔沒提交、圖譜健檢、每支檔有家、筆記形狀、雙向門放行、代碼審判定、存量漂移、Room 守衛(2026-10-28 起)、回頭重讀)擋下時不再立刻結束,改成記下、照原樣印那一道的說明、繼續下一道;跑到建測試 log 暫存檔之前有任何一筆,就叫 `lumos push-summary` 印「這次推送共有 N 筆擋下(M 道閘)」逐筆一行、記一筆 `prepush-summary` 治理帳,然後一律 exit 1,自主迴圈與全套都不跑。同一道被多個 ref 擋各記一筆,ref 欄在非刪除的推送行多於一行時才印 [出處:[[Projects/推送前一次列出全部擋下原因_計劃]]] [因:2026-10-13、10-14 兩批推送被依序擋了四次與兩次,每次修完重推才看到下一道] [不選:維持遇錯就停——那是 2026-09-06 全 repo 審視 #12 只調順序時的裁定,沒評估過一次列出;pre-commit 的幾道一起改——那幾道合計幾秒,重提交的代價不是要解的痛] [test:t_prepush_collects_all_blocks] [test:t_prepush_each_gate_blocks_alone] [test:t_prepush_multi_ref_blocks]

WHY:擋不擋只看記憶體裡的兩個純量(`_PP_BLOCKED`、`_PP_NBLK`),記一筆時先設它們、才追加暫存檔;彙總照 `--count` 算筆數,暫存檔讀不到或少幾行時講明有幾筆沒寫進去。`push-summary` 回非零或不存在(舊版 lumos)時掛鉤自己印簡版彙總,照樣 exit 1 [出處:[[Projects/推送前一次列出全部擋下原因_計劃]] 第二輪設計審] [因:暫存檔寫不進去(磁碟滿、暫存目錄被刪)或觀測那支壞掉,都不能把擋下變成放行;bash 3.2 搭 set -u 展開空陣列會出錯,所以不用陣列] [test:t_prepush_block_survives_lost_record] [test:t_prepush_summary_records_event]

WHY:`push-summary` 讀暫存檔只照換行字元切,不用 `splitlines`;找 repo 根跟 `push-range` 同一支 `_note_audit_root`(沒帶 `--repo` 又不在 git 專案裡就回 2)。掛鉤寫暫存檔(含雙向門放行那份留底檔)失敗時,錯誤訊息整組丟掉 [出處:第一輪代碼審邊界席、架構對齊席] [因:`splitlines` 也會在 U+2028、U+2029、U+0085 這類字元斷行,而 git 允許 ref 名帶它們(git 2.39.2 的 `git check-ref-format` 實測可過;跳頁與 0x1c–0x1e 是控制字元,會被拒,推不出來),那一筆會被切成兩段丟掉,跟掛鉤照換行讀的簡版彙總對不上;`2>/dev/null` 寫在 `>>` 後面時,bash 先開檔,開檔失敗的訊息在導走之前就印出來了,所以掛鉤裡寫進檔案又丟掉 stderr 的重導向一律包成一組] [test:t_push_summary_anchor_note_and_separators] [test:t_push_summary_repo_root_like_push_range] [test:t_prepush_block_survives_lost_record] [test:t_prepush_touched_file_write_fails_quietly]

WHY:代碼審判定那一道,掛鉤在逐 ref 迴圈之前讀一次 `scripts/lumos` 的原始碼,看有沒有 `"--keep-going"` 字樣。有就帶上這個旗標,讀它最後印的 `LUMOS-BLOCKS:` 行,每個種類記一筆;有多行時只取最後一行。原因用掛鉤寫死的對照表,查不到用通用句。沒有那個字樣就不帶旗標,照舊只看回傳碼。不論那一行在不在、解析出幾筆,回 1 時至少記一筆,那一行也不印給人看 [出處:[[Projects/推送前一次列出全部擋下原因_計劃]]〈做法〉5、6;第一輪代碼審架構對齊席] [因:掛鉤與 scripts/lumos 分開複製到消費專案,core.hooksPath 又讓好幾個工作樹共用一份掛鉤,版本一定會錯開;舊版不認得旗標回 2,而 2 在掛鉤裡是放行] [不選:執行 `code-loop check --help` 看輸出——同一支掛鉤探 `--shard`、`--suite`、`--graph` 都是讀檔找字樣,而且註解寫明不執行對方,多一種做法還要多一條中斷條目;掛鉤改讀 `--json`——要呼叫兩次或另外組文字,逃逸自動記帳又靠文字裡的兩句擋下句] [test:t_prepush_mixed_versions] [test:t_prepush_block_kinds_each_recorded]

WHY:每種擋下的一句話原因只存在掛鉤 `pp_cl_reason` 那一份;它的種類要跟 `scripts/lumos` 判定會產生的 `reason_kind` 一樣多、一樣名(雙向),而產生 `reason_kind` 的地方一律寫字面字串 [出處:第一輪代碼審架構對齊席、邊界席;第二輪代碼審通才席、架構對齊席、合約席] [因:掛鉤要能配舊版 lumos 跑,不能向 lumos 要這份表;新加一種擋下卻沒補掛鉤的表,彙總會退成通用句;種類若經變數產生,守衛從原始碼抽不到、會照綠] [不選:`scripts/lumos` 也存一份句子表、`--json` 的 blocks 每筆帶 `summary`——第一輪折入時加的,沒有任何程式讀,只為了給漂移測試一個比對對象,第二輪拿掉] [test:t_prepush_cl_reason_table_matches_lumos]

WHY:同一個 ref 的代碼審判定同時印出「受波及合約的測試沒過」與「tier=high 且…缺留痕」兩句時,逃逸自動記帳只記一筆,而且是合約測試紅那一筆 [出處:第一輪代碼審通才席] [因:原本遇錯就停時只會印第一句;收集模式兩句都印,兩筆都記的話,修好測試重推時缺留痕那筆又記一次,`push-gate-unreviewed` 的筆數會比實際抓到的漏多] [test:t_prepush_escape_records_once]

WHY:裁判簽名也改成收集:它管的是測試檔與掛鉤,不管 `scripts/lumos`;被改的若是掛鉤本身,它這一刻已經在跑,提早結束換不到可信度。這次推送反正已經因它被擋,不會變成放行;彙總裡有它時最前面多一行講明代碼審與雙向門放行這次跑的測試用的是沒簽名的測試檔;`push-summary` 印的與掛鉤簡版彙總印的都有這一行 [出處:[[Projects/推送前一次列出全部擋下原因_計劃]]〈做法〉1] [因:兩道會在全套之前跑 scripts/test_lumos.py 裡的測試,它們的綠燈這次不算數] [test:t_prepush_each_gate_blocks_alone] [test:t_prepush_plain_summary_anchor_note] [test:t_push_summary_anchor_note_and_separators]

WHY:中斷一律結束:清單上的每一支呼叫被訊號殺掉(128 以上)就以那個回傳碼停下;陷阱拆開,EXIT 只收拾,INT/TERM/HUP 先收掉自己的背景工作再以 130/143/129 結束 [出處:[[Projects/推送前一次列出全部擋下原因_計劃]]〈做法〉2] [因:原本 EXIT、INT、TERM 共用一支陷阱、裡面不結束,掛鉤自己被中斷時刪掉暫存目錄後照樣往下跑(/bin/bash 3.2.57 實測),收集模式會更常踩到;bash 要等手上那支前景子程序結束才跑陷阱,所以「立刻」是那支結束之後不再開始下一道] [test:t_prepush_interrupt_stops_every_gate]

PITFALL:掛鉤被砍或按 Ctrl-C 之後,全套測試的各片變成 ppid=1 的孤兒繼續跑(最多八分鐘,輸出寫進已刪的資料夾),兩個測試 log 也留在 TMPDIR [出處:第一輪代碼審併發席,/bin/bash 3.2.57 實測四片全成孤兒;第二輪代碼審併發席、架構對齊席:只對掛鉤送 HUP 時 8 片全活著;第三輪代碼審併發席、邊界席:片的子行程沒收、子殼的 HUP 陷阱沒測試守] [根因:掛鉤的陷阱只對 `jobs -p` 列出的直接子行程(跑測試的子殼)送 TERM,各片是孫行程;非互動 bash 用 & 起的背景命令又忽略 SIGINT,Ctrl-C 對整個行程群組送的 INT 也殺不到;主殼與子殼原本都沒接 HUP;兩個 log 用 mktemp 建在 `$_PP_TMP` 外] [修法:跑測試的子殼 `run_group` 自己接 TERM 與 HUP,用主殼同一支 `_pp_kill_jobs`(`jobs -p`)收掉它起的各片——不自己記 pid 收,「& 起片」與「記下 pid」之間有空窗,訊號落在中間會漏收剛起的那片;各片起的時候先換到自己的行程群組,`_pp_kill_jobs` 對每個工作整組送 TERM(不是組長才退回只送本人),連片自己起的子行程一起收(第三輪代碼審併發席:只收片本人時,片的子行程全成孤兒,起片後幾毫秒內收到訊號時連片也會漏);主殼也接 HUP(129);測試看那一片的 pid 在掛鉤結束後有沒有消失,不靠「睡幾秒再看有沒有寫下結束標記」的計時窗口(負載下會假綠);兩個 log 改放 `$_PP_TMP` 內,紅時要給人看的那份先複製到外面再印路徑;測試起掛鉤時先把 SIGINT 裝回預設,不然測試跑在推送前閘的背景分片裡、繼承「忽略 SIGINT」,bash 的 INT 陷阱裝不上,測 Ctrl-C 的斷言會假紅] [test:t_prepush_interrupt_stops_every_gate] [test:t_prepush_test_logs_inside_tmp]

PITFALL:整組只送一發 TERM 時,送的那一刻正在 fork 的片(或它的子行程)生出來的孩子變成 ppid=1 的孤兒 [出處:第四輪代碼審併發席,/bin/bash 3.2.57 模擬掛鉤啟動後 20–45 毫秒送 TERM] [根因:訊號是逐一投遞給群組當下的成員,剛生出來的孩子已經在群組裡、卻沒收到那一發;之後沒人再送] [修法:`_pp_kill_jobs` 送完第一發後短等 0.2 秒,再對每個群組送第二發,群組已空的錯誤吞掉;測試用「收到 TERM 才生孫行程」的假片讓這個情形每次都成立] [test:t_prepush_interrupt_stops_every_gate]

PITFALL:在原生 Windows 的 Python 上推送時,全套測試每一片一起跑就 AttributeError、被判成有紅,推送永遠被擋,「紅的是這幾支」又是空的 [出處:第四輪代碼審正確性席、併發席、通才席] [根因:換群組那段無條件呼叫 `os.setpgid`,Windows 的 Python 沒有它;就算繞過,Windows 的 `os.execv` 是起新行程後讓舊的立刻回 0,測試沒跑完就判綠] [修法:有 `setpgid` 才換群組再 `exec`(`setpgid` 失敗就不換、照樣 `exec`);沒有就在同一個行程裡用 `runpy` 跑測試檔,離開碼照實傳出] [test:t_prepush_interrupt_launcher_without_setpgid]

WHY:推送行程的環境帶一個放了 sitecustomize 的 PYTHONPATH,就能讓換群組那段與其他每個 `$PY` 閘一啟動就回 0;掛鉤不為這件事加機制 [出處:第四輪代碼審資安席] [因:要先刻意放一支 sitecustomize、再讓推送行程的環境指過去才成立,屬刻意設定環境的手法,在工具鏈的資安範圍外(工具鏈本身的資安只看提示注入、讀寫與執行越界、非刻意的一步繞過;見 Systems/pitfalls-code-loop 工具鏈資安範圍 RULE);非刻意殘留、別的程序帶進來的 PYTHONPATH 屬那條 RULE 的第 ③ 類、照審;而且每個 `$PY` 閘都一樣,不是換群組那段獨有、修補前就有] [不選:整支掛鉤統一給 `$PY` 加 `-I` 或清掉 PYTHONPATH——改動面是每一支閘,換到的只是「已經能改環境的人」多走一步]

找不到 Python 3.14、暫存目錄建不起來、使用者中斷這幾種前提壞掉的,照舊立刻結束、不收集;找不到 `scripts/lumos` 照舊提醒後放行 [test:t_prepush_stops_without_python]。代碼審判定內部的六道(含有資安登記時的安全證據、有 e2e 段時的 Android 端到端驗收)怎麼一次判完見 [[Systems/pitfalls-code-loop]]〈code-loop check --keep-going〉。

## 名稱篩選的跳脫與撞名(2026-10-15)

- `_run_cmd_expand` 依平台 `name_filter` 跳脫:regex(Jest/Vitest -t)跳脫正規式字元與斜線再加 shell 引號;regex_tail(Playwright -g)跳脫後錨在結尾 `\s<名字>(?:\s@\S+)*$`(容許 Playwright 接在標題後面的 tag)(-g 比專案名、檔名、describe、標題整串);plain(dart)與 ident 只加引號。Windows 上名稱含 `& | < > ^ % " !` 判不合法(cmd.exe 不認單引號)。 [test:t_run_cmd_name_filter_escape]
- `_run_bound_tests` 對名稱篩選型平台先做靜態撞名檢查(`_name_collision_reason`,guard kill 也用):數「篩選選得到的全部標題」(含 it.skip、帶 ${ 的樣板、.each、含逗號的標題),拿實際會用的篩選式比每個標題(regex 含這個名字、不分大小寫;regex_tail 用錨定式 search、只看測試;plain 含這個名字、分大小寫;describe 加測試的拼名只在同一支檔裡配對),撞名就不跑、記證不出(不是綠)。Windows 上 {method} 改用 list2cmdline(cmd.exe 不認單引號),規格閘與推送前閘一致。跑過的證據補了 playwright 一筆實測樣式(vitest 跟 jest 共用 node-jest 那一條,見下一節)。單源 [[Projects/測試名收自由字串_計劃]]。 [test:t_name_filter_collision_not_green]
- 推送前合約測試閘的名稱合法性改用 `_test_name_ok`;`類別.方法` 拿最後一段比,只在點號兩邊都是識別字時才用。 [test:t_test_name_ok_rules] [test:t_clause_binds_free_string]

## 跑過證據認得 vitest(2026-10-15,[[Projects/前端框架從vue分出_計劃]] F1)

`node-jest` 那條「跑過的證據」樣式改成同時吃 jest(`Tests:       1 passed, 1 total`)與 vitest(`      Tests  1 passed | 33 skipped (34)`),`node-vitest` 指向同一條;所以設定寫 `node-jest` 卻用 vitest 跑的專案也認得。中段限長 200 字(舊樣式遇到超長一行會二次方回溯,4 萬字實測 11 秒);數字前只要求「前一個字不是數字」(色碼結尾的 m 緊貼數字,字詞邊界不成立),空白只收同一行的、不跨行;`Tests:` 與 `Tests` 兩支都要在行首或行首前綴之後(前綴只收空白、色碼與游標控制碼、方括號或 ISO 時間戳、以冒號結尾的工作區前綴,如 turbo 的 `@org/web:test:`、pnpm -r 的 `packages/app test:`),測試標題裡出現「Tests: 2 passed」或「Tests 2 passed」都不算(代碼審 r3 折入,測試 t_ran_evidence_workspace_prefixes、t_ran_evidence_title_lines_rejected、t_ran_evidence_prefix_regex_linear;r2 折入,測試 t_ran_evidence_anchored_to_summary_line、t_ran_evidence_bounded_middle_fast;r1 折入,測試 t_ran_evidence_colored_per_line_reader、t_ran_evidence_no_cross_line_match)。全部 skipped 照舊判沒跑過。vitest 對不存在的測試名同樣回 0(5.0.4 實測),所以這條摘要行是唯一的證據。成本:每支綁定測試各起一次 vitest、預設依序跑,綁得多時用 `bound_tests.parallel`。測試 t_ran_evidence_vitest_one_passed、t_ran_evidence_vitest_all_skipped、t_ran_evidence_node_jest_accepts_vitest、t_ran_evidence_jest_summary_kept、t_ran_evidence_long_line_fast。

實地驗收(order-web 綁合約後推送拿到綠燈)要等測試名能收中文句子,見計劃的 S30。(2026-10-15 補:測試名已能收中文句子,見 [[Projects/測試名收自由字串_計劃]];實地驗收拿到綠燈與否以那份計劃的 S30 為準)

- 2026-10-20 pre-push 的 code-loop 那段與 ci.yml 多了安全證據那一道:非分支 ref(tag)改叫 `code-loop check --security-only`、任何非 0 都擋;CI 加 tag 觸發與只在 tag 跑的 security_tag 工作,其他工作限分支或 PR。說明的家在 [[Systems/安全證據閘]]。
- 2026-10-28 pre-push 在存量漂移那段之後、回頭重讀之前多一道 Room 守衛(`room-guard`):全套之前的閘變成 10 道,先過 pp_stop_if_signaled 的「rc1 擋、其他非零放行」閘變成 7 道,擋下一樣記進推送前彙總;CI 不接(回頭條件在家那篇)。判定與說明的家在 [[Systems/room-guard]]。
