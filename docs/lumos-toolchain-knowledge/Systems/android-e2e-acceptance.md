---
type: system
status: doing
created: 2026-10-25
updated: 2026-10-27
responsibility: 負責 Android 端到端驗收:範本腳本在主機端依序建 APK、裝上、跑 Maestro flow、截圖比對、記憶體與穩定性、效能並寫 steps.json,lumos android-e2e judge 判四塊、算內容指紋、寫 .lumos/e2e-records/ 的查證紀錄,macrobench.json 的 e2e 段格式,以及 code-loop check 的 Android E2E 那一道(推送前判定、按功能放行)、android-e2e waive 放行與 AI 放行待看的通知。不負責記憶體收集本身(Systems/android-stability-collector)、效能判定與 --results-dir 以外的 macrobench 行為(Systems/macrobenchmark-adapter)、截圖比對的實作(使用者的 maestro-visual-toolkit)、pre-push 的擋下原因表(Systems/bound-tests-gate)
aliases: []
about_code:
  - scripts/lumos
  - scripts/templates/android-e2e-run.sh
tags:
  - type/system
  - status/doing
  - scope/stack-knowledge
summary: |-
  WHY:指紋用那個提交自己的 e2e 段選檔,接 e2e 段的正規化雜湊、不接整份 macrobench.json(例外:e2e 段開了記憶體時,stability 段與 stability_scenarios 也另算一段雜湊接進去,見計劃決策 d1) [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r2 正確性、守衛、整合三席] [因:分支加了 flow 要認得自己的紀錄;改效能基準或 results_dirs 不該讓 E2E 紀錄失效] [test:t_android_e2e_fingerprint]
  WHY:judge 遇到 HEAD 跟開跑時不同、工作目錄有簿記檔以外的改動或沒追蹤的新檔、steps.json 格式不認得,就不寫紀錄、回 2 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r2 邊界席、正確性席] [因:驗的不是這一版時,紀錄會把沒驗過的程式記成通過] [test:t_android_e2e_judge_dirty_tree]
  WHY:建置或安裝失敗、裝置上的 APK 跟建出的不同或中途被換、這次被中斷,那一塊記成 unjudged 而不是 fail(整份結果只要有一塊 fail 就是 fail,沒有 fail 才看 unjudged) [出處:2026-10-25 實作] [因:那是環境沒跑成,不是程式本身的結論;紀錄要分得出是程式壞還是環境壞,推送檢查兩種都擋] [不選:一律記 fail(看紀錄的人會以為程式壞了)] [test:t_android_e2e_judge_tool_failure]
  WHY:裝置鎖放在 ~/.cache/lumos/android-e2e-lock/<序號>、寫程序編號,記的程序已經不在就清掉接手 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r2 守衛席、邊界席] [因:兩個工作樹會對同一台裝置跑;被 kill -9 或斷電時鎖會留下] [test:t_android_e2e_run_script]
  WHY:範本腳本把效能排最後,裝置上 APK 的第二次 sha256 在它之前讀 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r2 正確性席] [因:Macrobenchmark 的 Gradle 指令常會自己裝上、跑完再移除測試用的 App,排前面會讓記憶體那塊沒有 App 可跑]
  WHY:範本腳本的開跑前檢查呼叫 lumos android-e2e judge --precheck,不自己列簿記檔 [出處:2026-10-25 實作] [因:哪些檔不算改動只該有 lumos 那一份清單,腳本自己列就是第二份、會漂] [test:t_android_e2e_run_script]
  PITFALL:新範本沒登記進工具組複製清單,lumos update 不會把它裝進消費專案,接入的專案拿不到驗收腳本 [出處:2026-10-25 實驗室接入] [根因:複製清單是手寫的,加新範本時要同時加一行] [修法:登記進清單並補檔頭檢查] [test:t_android_e2e_vendored]
  WHY:裝置鎖記的程序已經不在就清掉接手,跟 lumos 本體 _excl_lock_try 不自動接手的做法相反 [出處:2026-10-25 代碼審 code-android-e2e-batch1 r1 架構對齊席] [因:範本腳本是獨立的 Python、拿不到 lumos 的鎖;被 kill -9 或斷電後不接手,每次都要人手動刪鎖] [不選:照本體不自動接手(無人看顧時卡死)] [代價:兩次驗收幾乎同時發現同一把殘鎖時可能兩邊都拿到;照 Lumos 的威脅模型(單人、AI 依序操作)不另外防]
  WHY:中斷時先對子程序群組送 TERM、等 LUMOS_E2E_STOP_GRACE 秒(預設 60)再 KILL [出處:2026-10-25 代碼審 code-android-e2e-batch1 r1 單審席] [因:收集腳本靠 TERM 才停裝置上的錄製、刪原始日誌,它自己的子程序各自成組只能由它收;toolkit 靠 trap 清鎖與展示模式;一開始就 KILL 這些收尾都不會跑] [不選:直接 KILL(裝置上的錄製一直錄、驅動變孤兒)] [代價:Ctrl-C 之後最久要等 60 秒] [test:t_android_e2e_run_script]
  PITFALL:關掉終端(HUP)時,中斷路徑上那一行印到錯誤輸出的訊息丟出 EIO 或 EPIPE,例外跳過後面的存檔與 judge,steps.json 沒標中斷、也沒寫紀錄 [出處:2026-10-25 代碼審 code-android-e2e-batch1 r1 單審席] [根因:收尾路徑上的 print 沒保護] [修法:收尾與擋下訊息一律走 say(),印不出來就算了] [test:t_android_e2e_run_script]
  PITFALL:門檻檔裡同一個 check 另有別的情境或別的裝置的條目時,它們落在 threshold_skipped,記憶體這塊永遠判成沒判完 [出處:2026-10-25 代碼審 code-android-e2e-batch1 r1 單審席] [根因:判定只看 check 名、沒分這條適不適用這次的結果] [修法:lumos macrobench --stability 對情境或裝置不符的跳過條目標 applies=false,端到端驗收不把它們算進來] [test:t_android_e2e_stab_applies_flag]
  WHY:JUnit 報告用 test_quality.junit() 讀(安全證據閘同一套),判定用的 JSON 讀檔限深並清孤立代理字元,git 呼叫走 _nodehome_git [出處:2026-10-25 代碼審 code-android-e2e-batch1 r1 架構對齊席] [因:自己寫的讀法會漏掉既有讀法擋的情況(帶 DTD、宣告的案例數對不上;孤立代理字元讓寫紀錄時整支崩)] [test:t_android_e2e_judge_ui]
  PITFALL:改成先 TERM 再等寬限之後,逾時路徑在寬限中又被中斷時,例外從 except 區塊丟出、子程序已從待收清單拿掉,不理 TERM 的子程序變孤兒;領頭程序在寬限內退了也不再補 KILL,同組裡不理 TERM 的成員留著 [出處:2026-10-25 代碼審 code-android-e2e-batch1 r2 單審席(上一輪修補帶進來的)] [根因:等寬限那一段沒接中斷,KILL 只在寬限到期時送] [修法:寬限中被中斷先補 KILL 再往上丟;寬限結束一律對整組補 KILL] [test:t_android_e2e_run_script]
  PITFALL:紀錄讀回改成完全不清洗之後,紀錄裡要是有孤立代理字元(手改或舊版寫的),寫回時編碼失敗、judge 整支崩,回傳碼 1 看起來像「寫了紀錄但沒過」 [出處:2026-10-25 代碼審 code-android-e2e-batch1 r3 單審席(上一輪修補帶進來的)] [根因:為了保住換行與 tab 把清洗整個關掉,孤立代理字元那一類又放回來] [修法:紀錄讀回只把孤立代理字元換成 U+FFFD,其他照原樣] [test:t_android_e2e_judge_dirty_tree]
  PITFALL:讀紀錄時套了清洗(換行、tab、孤立代理字元換成空白),讀改寫一次就把人寫的放行理由壓扁再寫回 [出處:2026-10-25 代碼審 code-android-e2e-batch1 r2 單審席(上一輪修補帶進來的)] [根因:同一支讀檔函式同時給只讀的判定輸出與要整份寫回的紀錄用] [修法:紀錄讀回只限深、不清洗換行與 tab;孤立代理字元後來仍換成 U+FFFD,見上一條 r3 那行] [test:t_android_e2e_judge_dirty_tree]
  PITFALL:錯誤輸出斷了之後,say() 吞掉例外、但緩衝區還留著字,程式結束清緩衝區時失敗,回傳碼變成 120 [出處:2026-10-25 代碼審 code-android-e2e-batch1 r2 單審席] [根因:只吞了這一次的例外,沒換掉壞掉的錯誤輸出] [修法:第一次寫不出去就把錯誤輸出換成 /dev/null] [test:t_android_e2e_run_script]
  PITFALL:紀錄或 lumos 本體裡用 "diff" 當欄位名,推送前全套測試的「取差異內容的 git 呼叫要帶防護旗標」守衛會把它當成 git 呼叫而翻紅 [出處:2026-10-25 首次推送被擋] [根因:那道守衛靠字面上的引號 diff 找呼叫點] [修法:截圖比對的差異圖欄位叫 diff_image] [test:t_lumos_content_diffs_all_disable_external_drivers]
  PITFALL:新加頂層子指令只寫了 add_parser,推送前全套測試另有兩支會紅:說明沒有「什麼時候用」、架構說明與手冊參考檔寫的指令總數沒跟著加 [出處:2026-10-25 第四次推送被擋] [根因:「什麼時候用」集中寫在 HELP_WHEN 表、指令總數散在兩份文件,加指令時不會被提醒] [修法:android-e2e 與 android-e2e judge 補進 HELP_WHEN,總數改 95] [test:t_every_subcommand_has_when]
  WHY:這次真的要收記憶體時(整套跑看 e2e 段開了沒;按功能跑看挑到的情境有沒有列記憶體、沒帶 --no-memory;都不看最外層給單獨 macrobench --stability 用的那段),範本腳本的開跑前檢查先查 trace_processor,宣告了測試資料再查 java_heap_dump,跟收集腳本同兩個環境變數、讀 test_data 的那一行逐字相同(測試各抽出那一行比相等) [出處:2026-10-25 實驗室四塊實跑] [因:收集腳本自己也查,但輪到它時建置、安裝、UI、截圖都已跑完,實驗室兩次都白跑一趟才記成沒判完] [不選:只靠收集腳本自己查(慢)] [test:t_android_e2e_preflight_stability_tools]
  WHY:範本腳本 --changed、--feature、--case 按 e2e.features 對照表只跑挑到的情境,交給 judge --no-record 判;開跑時與判讀時工作目錄都乾淨、HEAD 沒換時把每個情境的結果寫進這一版查證紀錄的 feature_runs(略過效能或記憶體、或沒有會判的項目時標 complete=false),不碰整套的 runs;judge 沒帶 --no-record 卻讀到 steps.json 有 selection 欄就拒寫、回 2 [出處:2026-10-26 Enzo 要按功能與使用情境跑,並說「只針對功能開發寫正式檢驗紀錄也算合理」(開發是按功能分派的)] [因:整套的 runs 代表「這一版整套驗過」,按功能的結果另存一欄,推送前檢查(下一批)才分得出改動碰到的功能各有沒有驗過] [不選:按大類挑的 --only(粒度不對,同日改掉);按功能跑只記總表(開發按功能分派,每次逼整套跑不實際)] [test:t_android_e2e_by_feature]
  WHY:每次跑(整套或按功能)都由 judge --history 在 .lumos/artifacts/android/history.jsonl 加一行,有沒有沒提交的改動照開跑前檢查同一套規則判 [出處:同上,Enzo 要完善的檢測紀錄] [因:按功能跑不寫整套的紀錄、開跑時有改動就什麼紀錄都不寫,開發中的檢測歷史要另有地方查;簿記檔不算改動,不然整套跑後沒提交的紀錄檔會讓下一筆都記成有改動] [test:t_android_e2e_history]
  WHY:--changed 的分岔點照安全證據那套挑主線(_secev_mainline),挑不到只看工作目錄的改動並說明;一個功能都對不到回 2,不靜默放過 [出處:同上] [因:主線挑法只該有一份;對不到時什麼都不跑卻回通過,會被當成驗過] [test:t_android_e2e_by_feature]
  PITFALL:按功能跑開跑時工作目錄有改動、跑到一半收掉,判讀時乾淨、HEAD 沒換,結果被記成這一版驗過,但建出來的 App 含那些改動 [出處:2026-10-26 代碼審 code-e2e-by-feature r1 資安、通才席] [根因:寫 feature_runs 只看判讀當下的工作目錄,開跑時記下的 dirty 沒拿來擋] [修法:steps 的 dirty 不是 false 就只記總表] [test:t_android_e2e_feature_record_trust]
  PITFALL:--changed 漏挑:整個沒追蹤的新目錄被 git status 收成一筆「目錄/」,對不到寫在更深一層的 paths;只改 flow 檔時對不到任何功能 [出處:2026-10-26 代碼審 code-e2e-by-feature r1 邊界席] [根因:沒追蹤的檔沒逐檔展開;只用程式路徑對功能] [修法:沒追蹤的檔用 ls-files --others 逐檔列;改到某情境列的 flow 也算那個功能] [test:t_android_e2e_changed_pick]
  PITFALL:效能測試方法名為了收 Kotlin 巢狀類別而放行 $,但名字原樣換進 sh -c,Outer$Inner#test 被展開成 Outer#test,設定檢查與驗收都過、跑的卻是別支 [出處:2026-10-26 代碼審 code-e2e-by-feature r2 通才、合約、正確性席(上一輪修補帶進來的)] [根因:放寬白名單時只想到設定檢查,沒追到值換進 shell 之後] [修法:E2E_BENCH_NAME_RE 與範本腳本同一條都不收 $] [test:t_android_e2e_args_and_names]
  WHY:效能測試方法名不收 $(Kotlin 巢狀類別 Outer$Inner 因此不能用 {{TEST}} 指名),不改成換進指令時加 shell 引號 [出處:2026-10-26 代碼審 code-e2e-by-feature r3 通才席] [因:macrobench_cmd 是專案自己寫的指令,有人已經把 {{TEST}} 包在引號裡,再加一層引號會壞;白名單擋掉會被展開的字元,兩種寫法都安全] [不選:shlex.quote 換進指令(跟使用者自己的引號打架)] [代價:巢狀類別要另寫一支不帶 $ 的包裝方法] [test:t_android_e2e_args_and_names]
  PITFALL:陌生專案提交一個捷徑 .lumos/e2e-records 指向專案外,寫查證紀錄時就跟過去把檔寫到外面 [出處:2026-10-26 代碼審 code-e2e-by-feature r3 資安席] [根因:寫紀錄前沒檢查路徑上有沒有捷徑] [修法:_e2e_record_update 與 _e2e_history_append 寫之前過共用的 _repo_path_unsafe(逐層擋捷徑、解析後要在專案裡),擋下訊息用 _repo_path_unsafe_why] [test:t_android_e2e_run_edges]
  PITFALL:路徑規則合成一支之後,功能 paths 寫 ./. 又收得進來:根本身的判斷看的是只去掉頭尾空白與結尾斜線的字串,沒先去掉開頭的 ./ [出處:2026-10-26 代碼審 code-e2e-by-feature r4 通才、邊界席(上一輪修補帶進來的)] [根因:合併時兩道檢查用了不同的正規化] [修法:_e2e_relpath_err 根本身也看 _e2e_norm 之後的值] [test:t_android_e2e_r4_edges]
  PITFALL:直接在 main 上開發時,--changed 看不到已提交沒推的改動:本機 main 本身也是主線候選、等於 HEAD,分岔點變成 HEAD 自己 [出處:2026-10-26 代碼審 code-e2e-by-feature r4 邊界席] [根因:主線候選把現在所在的分支也算進去] [修法:分岔點等於 HEAD 而且在 main/master 上時,改拿這條分支的 upstream(沒設就 origin/<分支>)當起點] [test:t_android_e2e_r4_edges]
  PITFALL:「完整的結果不被不完整的蓋掉」條件只看完不完整,同一版先完整通過、再略過效能跑出真失敗時,失敗被丟掉、紀錄仍寫通過,跟總表矛盾 [出處:2026-10-26 代碼審 code-e2e-by-feature r2 通才席(上一輪修補帶進來的)] [根因:保留規則沒先排除這次沒過] [修法:_e2e_keep_old:這次沒過一律蓋掉;只有沒判完、或不完整但通過才留舊的;既有那筆更晚結束也留] [test:t_android_e2e_feature_record_rules]
  WHY:整套跑的記憶體收 stability 段本身加 stability_scenarios 每個情境、各判一次;多個效能方法每跑完一個就收進自己的子目錄 [出處:2026-10-26 代碼審 code-e2e-by-feature r1 正確性、通才席] [因:整套代表「這一版全部驗過」,只跑 stability 段本身會讓按功能列的記憶體情境從沒在整套裡判過;Macrobenchmark 結果檔名常固定,一起收會只剩最後一個] [test:t_android_e2e_memory_by_case] [test:t_android_e2e_perf_per_method]
  WHY:本機總表追加走 _local_ledger_append、帳尾缺換行先補,讀取走 _canary_ledger_rows 只留最後 N 筆;judge 擋下沒寫紀錄的那次也記一行、附原因 [出處:2026-10-26 代碼審 code-e2e-by-feature r1 架構對齊、正確性席] [因:本機帳的追加與讀法專案已有一套(擋捷徑、短寫、半行黏行、U+2028 劈行);擋下的那次正是最需要回頭查的] [不選:裸 open 追加、splitlines 讀全檔] [test:t_android_e2e_history_edges]
  WHY:推送前判定(code-loop check 的 Android E2E 那一道)跟安全證據一樣排在所有放行早退之前、不看分級、判不清就擋,整道 60 秒預算、每次 git 拿剩下的時間 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r2 整合席、r3 資源席] [因:出錯時默默放行等於整道關掉;推送前掛鉤沒有外層逾時] [不選:照新增告警閘出錯就放行(那類閘本來就不擋)] [test:t_android_e2e_gate_unclear_blocks] [test:t_android_e2e_gate_budget]
  WHY:推送前判定先看被推送提交與主線候選有沒有 e2e 段,都沒有就不跑、一字不印;讀不到不算沒有:先用 ls-tree 看路徑在不在樹裡,在卻讀不出就擋 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r3 邊界席、資源席] [因:這道接進每個專案共用的 code-loop check,沒用 E2E 的專案不能因為主線找不到被擋;物件缺時當成沒有會默默放行] [test:t_android_e2e_gate_unclear_blocks]
  WHY:沒有可用的整套結果時按功能判:改到的檔都歸屬到功能、每個要驗的情境有通過的 feature_runs 就放行;碰到 shared_paths、對不到功能、驗收設定或記憶體設定改了要整套 [出處:2026-10-26 Enzo 裁「只針對功能開發寫正式檢驗紀錄也算合理」;[[Projects/Android端到端驗收_計劃]]〈推送前怎麼按功能判〉] [因:開發按功能分派,每次逼整套跑不實際] [不選:只認整套] [代價:沒標成共用、其實別的功能也在用的程式改壞別的功能時擋不住,回頭條件在計劃〈實務隱患〉] [test:t_android_e2e_gate_by_feature] [test:t_android_e2e_gate_needs_full]
  WHY:整套 pass 之後,只有結束時間不早於它的 fail(同一秒算較新)才推翻;沒判完、略過效能的開發中途跑不算 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r3 正確性席] [因:中途跑的沒判完不是「沒過」,拿它推翻完整的整套通過會擋下而且解不開] [test:t_android_e2e_gate_newest_wins]
  WHY:查證紀錄的讀改寫鎖照用 _vault_write_lock(照 lint-waive),殘留鎖不自動接手,搶不到時說出鎖檔位置與人工清鎖的前提 [出處:代碼審 code-e2e-gate r1 架構對齊席,推翻設計審 r3 資源席的「程序不在就接手」] [因:靠鎖裡的程序編號接手有競態,專案的 _excl_lock_try 明文不這樣做;另寫一把鎖是第二種做法;推送本身不拿這把鎖,出口 LUMOS_SKIP_ANDROID_E2E=1 照樣有效] [不選:自寫會接手的鎖] [test:t_android_e2e_record_lock_blocked]
  WHY:放行先在鎖外問終端、問完才拿鎖重讀寫回;waive 與 --ack 用 _confirm_tty 的 stdin_timeout,標準輸入是終端時也等 LUMOS_TTY_TIMEOUT 秒 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r3 資源席、整合席] [因:持鎖等人會讓另一個寫入逾時;掛著虛擬終端、沒有人在的流程原本會永遠等] [不選:改 _confirm_tty 的全部呼叫端(init 的互動行為會跟著變)] [test:t_android_e2e_waive]
  WHY:還沒人看過的 AI 放行列在推送那一行、doctor 的 AE 段與開場提示,不進 lumos enforcement [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r3 整合席] [因:enforcement 查的是防護有沒有裝上、沒生效時叫人重裝;待看的放行是資料狀態] [test:t_android_e2e_ai_waiver_notice]
  WHY:指紋範圍判斷(_e2e_scope_hit)與功能歸屬(_e2e_owners)抽成共用,算指紋、--changed 與推送前判定三處同一支 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r3 架構對齊席] [因:三處各寫一套範圍,接手的人要猜哪一套準] [test:t_android_e2e_scope_shared]
  WHY:e2e.shared_paths 的設定檢查(_e2e_shared_paths_err)跟 features 的 paths 用同一套寫法規則(_e2e_relpath_err)、一樣不驗路徑存不存在;另外多兩條只屬於它的:要在 app_dirs 底下(推送前判定只看 app_dirs 裡的改動,寫在外面等於沒寫)、最多 E2E_PATH_LIST_MAX 項 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r3 架構對齊席] [因:同一份設定裡兩個路徑欄位規則不同會讓人猜;寫了還不存在的共用目錄(先列再建)不該擋] [test:t_android_e2e_shared_paths_config]
  PITFALL:推送前判定的提醒行不以「提醒」開頭時,真的 git push 看不到 [出處:[[Projects/Android端到端驗收_計劃]] 設計審 r3 整合席] [根因:pre-push 在放行路徑只轉印含「提醒」等幾個字的行] [修法:按功能放行與 AI 放行待看兩行都以「提醒:」開頭] [test:t_android_e2e_gate_wiring]
  PITFALL:預算用完時 git 呼叫回失敗,擋下原因被講成「讀不到要推的提交」 [出處:2026-10-26 實作時測試翻紅] [根因:沒時間時 _lens_git_dl 不跑、回 None,跟 git 失敗分不出] [修法:擋下時預算已經用完就一律報成逾時與怎麼關掉一次] [test:t_android_e2e_gate_budget]
  PITFALL:推送前判定一開始就把要推的提交解成完整編號、解不出來就擋,搶在「這個專案用不用 E2E」之前,沒用 E2E 的專案被誤擋(推送前掛鉤的測試傳假的提交編號) [出處:2026-10-27 推送前全套測試翻紅 4 支] [根因:前置判斷要讀被推送提交的樹,讀不到時沒有別的線索可看] [修法:讀不到要推的提交時照安全證據閘先看工作目錄的設定,沒有 e2e 段就整道不跑、一字不印] [test:t_android_e2e_gate_unclear_blocks]
  PITFALL:只改 .lumos/macrobench.json(拿掉 flow、關掉記憶體、整段刪掉 e2e)、App 程式沒動的提交,推送前判定說不用驗就放行 [出處:2026-10-27 代碼審 code-e2e-gate r1 資安、正確性席] [根因:兩端用同一份設定算指紋,設定本身的改動不會讓兩端指紋不同] [修法:指紋相同時另比分岔點與被推送提交自己的 e2e 段與記憶體設定,不同就要驗;被推送提交拿掉了 e2e 段就擋] [test:t_android_e2e_gate_reads_mainline_config]
  PITFALL:被推送提交的設定讀不懂或判定逾時時,照擋下訊息設 LUMOS_SKIP_ANDROID_E2E=1 照樣被擋,CI 裡也被擋 [出處:2026-10-27 代碼審 code-e2e-gate r1 通才、邊界、正確性、合約席] [根因:兩個出口排在讀設定之後才看] [修法:判定結果是擋下時最後再看一次這兩個出口] [test:t_android_e2e_gate_unclear_blocks]
  PITFALL:陌生專案在 .lumos/e2e-records/ 放一個捷徑指到 /dev/zero,開場掛鉤與 doctor 讀它讀不完、吃光記憶體 [出處:2026-10-27 代碼審 code-e2e-gate r1 邊界席] [根因:用 stat 跟著捷徑走,裝置的大小是 0、過得了大小上限] [修法:兩邊都用 lstat 只讀一般檔,份數與單份大小同一組上限,一份讀不懂只跳過那一份] [test:t_android_e2e_ai_count_copies_agree]
  PITFALL:doctor、waive --ack 與開場掛鉤數 AI 放行待看的結果各說各話,深層巢狀的紀錄讓 waive --list 崩潰,500 份 2MB 的大清單讓開場掛鉤超過外層 10 秒 [出處:2026-10-27 代碼審 code-e2e-gate r2 邊界、資源、合約席] [根因:三處讀紀錄各寫一套(lumos 先限深再數、掛鉤直接數;太大的檔一邊佔名額一邊不佔),只限份數與單份大小、沒限總時間,json 解析遞迴爆掉的 RecursionError 沒接] [修法:同一套寬鬆讀法(只 json.loads、太大的佔名額不讀、總時間 3 秒、沒讀到的份數講出來),掛鉤的 _e2e_ai_pending_one 跟 lumos 逐字相同、測試比原文] [test:t_android_e2e_record_scan]
  WHY:e2e 的外來文字兩層看門:源頭——設定的路徑(_e2e_relpath_err,類別用共用的 _path_special_chars)與從 git 取來的改到的檔名都拒收控制字元與看不見的字元;出口——底層的 _out_clean 與 _say_block(macrobench 也用),e2e 區不准自己印「擋下:」,有一支掃語法樹的測試守 [出處:2026-10-27 代碼審 code-e2e-gate r4 資安、邊界、架構對齊席,r5 資安、正確性、邊界、通才、合約、架構對齊席] [因:r1–r5 每輪都在一個沒經過出口的輸出點找到原樣回顯;清單式地補出口每輪都漏一處,所以改成源頭擋加一條會自動抓新漏網的規則] [不選:逐個印出點補(每輪漏一處)、e2e 專屬的清理函式(macrobench 往上呼叫,跨層)] [test:t_android_e2e_say_single_exit]
  WHY:寫入端驗紀錄跟判定端同一套(含結束時間),所以結束時間讀不懂的舊紀錄連 judge 重跑都不覆蓋,只能修好或刪掉 [出處:2026-10-27 代碼審 code-e2e-gate r3 合約席、r4 正確性席] [因:寫得進去卻照樣被擋的放行、重跑之後照樣讀不懂的紀錄都比明著擋更糟;擋下訊息講明「修好或刪掉」] [不選:重跑時整份換掉 runs(其他欄位的壞資料照留,還是讀不懂)] [test:t_android_e2e_record_unreadable]
  WHY:主線在分岔後改了驗收設定時,另用主線設定算一次兩端指紋(多兩次 ls-tree),只在兩邊設定不同時才算 [出處:2026-10-27 代碼審 code-e2e-gate r3 資安席、r4 資源席] [因:照這一版的範圍看沒改到、照主線的範圍看可能改到;兩邊設定一樣時不多花] [代價:設定不同的推送多吃一點 60 秒預算] [test:t_android_e2e_gate_mainline_wider]
  PITFALL:擋下訊息的外來文字逐點清,每輪漏一處:r2 清了檔名,r3 又找到設定值回顯與紀錄鍵名 [出處:2026-10-27 代碼審 code-e2e-gate r2 資安席、r3 資安、合約、通才席] [根因:清理寫在組字串的每一處,新的回顯點沒人記得] [修法:結果出口 _e2e_gate_out 統一清原因與清單裡的字串] [test:t_android_e2e_gate_output_clean]
  PITFALL:開場提示與 doctor 說「另有幾份沒讀,看 waive --list、標 --ack --all」,那兩個指令卻跟它們用同一個 500 份名額,名額外那份永遠看不到也標不掉 [出處:2026-10-27 代碼審 code-e2e-gate r3 正確性、邊界、合約、通才、資源席] [根因:把給「看一眼」用的份數上限套到人明著下的指令上] [修法:--list 與 --ack 讀全部、只留時間上限] [test:t_android_e2e_waive_all_records]
  PITFALL:歸屬查表逐層 join 前綴,路徑深一萬層時一百多支檔就吃掉 60 秒預算 [出處:2026-10-27 代碼審 code-e2e-gate r3 資源席(r2 修補引入)] [根因:修平方工作量時只看了檔數乘路徑數,沒看單一路徑的長度] [修法:只查到功能路徑最深那一層] [test:t_android_e2e_scope_perf]
  PITFALL:主線採用 E2E 之前分出去的舊分支只改文件也被推送前判定擋下,訊息還說 App 不一樣 [出處:2026-10-27 代碼審 code-e2e-gate r2 正確性、通才席] [根因:r1 為了「只改設定也要驗」加的設定比較要求兩端都有 e2e 段,兩端都沒有時永遠算不一樣] [修法:兩端都沒有 e2e 段也算設定一樣] [test:t_android_e2e_gate_cfg_sides]
  WHY:推送前判定的各段用例外(_E2eGateStop)帶結果提早結束,不照安全證據閘「階段回傳 done、呼叫端判非空」的寫法 [出處:2026-10-27 代碼審 code-e2e-gate r2 架構對齊席] [因:判定有十來個會提早結束的點(出口、沒用 E2E、不要求、放行、各種判不清),分散在被拆小的階段函式裡,逐層回傳要每層多一個判斷;例外只在這一道內部用,入口 _e2e_gate_evaluate 一律接住轉成結果,對外介面跟鄰居一樣是結果 dict] [不選:逐層回傳 done(每個階段函式多一層判斷,拆函式時降的複雜度又加回去)] [代價:讀程式的人要知道 _e2e_gate_done 不會回來]
  SEE:[[Projects/Android端到端驗收_計劃]] [[Systems/android-stability-collector]] [[Systems/macrobenchmark-adapter]]
  WHY:lumos android-e2e coverage 只報告功能對照表的缺口、不擋,範圍判斷與逐檔歸屬跟推送前判定共用同一支(_e2e_scope_hit、_e2e_file_owner),沒歸屬的程式檔按所在資料夾彙總、共用程式另列支數;設定讀工作目錄,補完對照表不用先提交就看得到 [出處:[[Projects/端到端驗收對照表涵蓋報告_計劃]] 2026-10-27 Enzo 照「只報告、預設按目錄分組」開工] [因:缺歸屬的後果推送前檢查已經會擋(要求整套跑);事先列出來是讓人在推送前補對照表] [不選:擋推送(重複擋同一件事);從程式的 import 猜歸屬(猜錯比列出來更糟)] [test:t_android_e2e_coverage_unowned] [test:t_android_e2e_coverage_doctor_line] [test:t_android_e2e_coverage_same_as_gate] [test:t_android_e2e_coverage_worktree_cfg]
  WHY:涵蓋報告另列情境與筆記對不上的兩種(列了流程檔卻沒有筆記綁到或正文提到的情境、筆記合約綁了卻沒有情境列到的流程),只報告不擋;綁定照合約測試綁定那一套解、只認 maestro 平台,正文寫流程檔路徑也算提到 [出處:[[Projects/端到端情境對照筆記_計劃]] 2026-10-27 Enzo 回「我覺得可以補」] [因:對照表管跑什麼、筆記管為什麼要成立,兩邊靠同一支流程檔對上,沒有機器看會悄悄分岔] [不選:擋推送(合約照不確定就不標的鐵則,不能逼每個情境都有合約);只認合約行(README 教不確定就寫在正文)] [test:t_android_e2e_coverage_cases_without_notes] [test:t_android_e2e_coverage_note_flows_not_in_cases] [test:t_android_e2e_coverage_notes_absent]
  WHY:涵蓋報告的情境與筆記對照用 load_vault_safe 讀整個圖譜、不沿用 doctor 手上的 env,流程檔名字從 maestro 平台的測試名索引(_platform_name_files)反查 [出處:[[Projects/端到端情境對照筆記_計劃]] 2026-10-27 代碼審架構對齊席] [因:要全文找流程檔路徑,load_vault 的筆記物件不留正文;名字索引跟殘留索引共用一支,測試檔篩選改了兩邊一起變] [不選:自己讀流程檔的 name:(第二套走訪);doctor 傳 env 進來(筆記物件沒有正文,還是要重讀)]
verified_by:
  - "[[Verification/2026-10-25_端到端驗收實機初跑]]"
  - "[[Verification/2026-10-25_端到端驗收四塊實跑與情境實驗]]"
  - "[[Verification/2026-10-26_AI自己選分塊跑法探針]]"
  - "[[Verification/端到端情境對照筆記_實驗室實測]]"
---
# android-e2e-acceptance

白話:Android App 推送前在實機上跑一次端到端驗收的那一套。範本腳本負責碰裝置、把每一步的結果寫成 steps.json;lumos 只讀這些結果判過不過,再寫一份綁在「App 程式與驗收素材內容」上的查證紀錄。設計與條款的單源在 [[Projects/Android端到端驗收_計劃]],這裡只記現在怎麼運作、程式碼看不出來的理由。

## 怎麼跑

在專案根目錄:

```
sh scripts/templates/android-e2e-run.sh --preflight
sh scripts/templates/android-e2e-run.sh
```

第一行只做開跑前檢查(工作目錄乾淨、裝置連著沒鎖屏、工具與截圖素材在、產物目錄被忽略、同一台裝置沒有另一次驗收在跑),不碰 App;第二行照順序跑完,最後交給 `lumos android-e2e judge` 判並寫紀錄,結尾印要提交的紀錄檔。

開發中按功能跑:加 `--changed`(看改到的檔挑 `e2e.features` 的功能)、`--feature <功能>` 或 `--case <功能.情境>`,可再加 `--no-perf`、`--no-memory`。不要求工作目錄乾淨、不寫整套的紀錄;從開跑到判讀都乾淨、HEAD 沒換時,按情境的結果寫進這一版紀錄的 `feature_runs`。每次都記進本機總表,`lumos android-e2e history` 看。

## 回傳碼

以下是整套跑;按功能跑是 0=挑到的都過、1=有沒過或沒判完(一個會判的項目都沒有也算)、2=挑不到、設定不合格、steps.json 讀不懂或被中斷,寫沒寫進紀錄看終端最後那行。

- 0:寫了紀錄,而且這次通過。
- 1:寫了紀錄,但沒通過(某塊沒過,或環境沒跑成而沒判完)。
- 2:開跑前檢查沒過、版本中途換了、工作目錄有改動、設定不合格(這幾種都不寫紀錄);或這次被中斷(judge 照樣寫紀錄:中斷前已有一塊沒過就是「沒過」,否則是「沒判完」,腳本回 2 讓呼叫的人知道沒跑完)。

## 推送前檢查

`code-loop check`(推送前掛鉤每個分支 ref 都叫它)裡的 Android E2E 那一道;單獨看會不會擋:

```
lumos android-e2e check
```

印成 JSON,不寫任何東西;回 0 不擋(包括沒用 E2E 的專案)、1 會擋。判定順序與按功能那段的規則在 [[Projects/Android端到端驗收_計劃]]〈資料怎麼流〉第 4 步與〈推送前怎麼按功能判〉,這裡不複述。紀錄從被推送提交的樹讀,不讀工作目錄:跑完驗收要先提交紀錄再推。

擋下時訊息照實際需要給指令:要整套的印整套跑,只要按功能的印 `--case <功能.情境>`,紀錄沒提交的印提交指令,被推送提交沒有 e2e 段(分岔點也沒有)、或主線的驗收要求比這一版新的叫人先合主線,這次拿掉了 e2e 段(分岔點還有)的只給環境變數那條路(合主線補不回被刪的段);能放行時另印一行帶完整指紋與 `--commit` 的放行指令。

放行與看過:

```
lumos android-e2e waive <完整指紋> --commit <提交> --note "<理由>"
lumos android-e2e waive --list
lumos android-e2e waive --ack --all
```

終端答 y 記成人放的;沒有互動終端(或沒人答)記成 AI 放的,推送、`lumos doctor` 的 AE 段與開場提示會一直列出來,直到人用 `--ack` 看過。這一次整道先關掉:`LUMOS_SKIP_ANDROID_E2E=1 git push`(會記一筆治理帳 skipped-env)。

REVISIT:2026-11-30 計劃第二批(code-loop check 那一道、放行與 AI 放行通知)上線時,把推送檢查怎麼讀紀錄、怎麼放行寫進這篇 [closed:2026-10-26 寫進〈推送前檢查〉一節與摘要]
