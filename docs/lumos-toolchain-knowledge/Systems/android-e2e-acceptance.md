---
type: system
status: doing
created: 2026-10-25
updated: 2026-10-26
responsibility: 負責 Android 端到端驗收:範本腳本在主機端依序建 APK、裝上、跑 Maestro flow、截圖比對、記憶體與穩定性、效能並寫 steps.json,lumos android-e2e judge 判四塊、算內容指紋、寫 .lumos/e2e-records/ 的查證紀錄,以及 macrobench.json 的 e2e 段格式;之後 code-loop check 那一道與放行也歸這裡。不負責記憶體收集本身(Systems/android-stability-collector)、效能判定與 --results-dir 以外的 macrobench 行為(Systems/macrobenchmark-adapter)、截圖比對的實作(使用者的 maestro-visual-toolkit)
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
  SEE:[[Projects/Android端到端驗收_計劃]] [[Systems/android-stability-collector]] [[Systems/macrobenchmark-adapter]]
verified_by:
  - "[[Verification/2026-10-25_端到端驗收實機初跑]]"
  - "[[Verification/2026-10-25_端到端驗收四塊實跑與情境實驗]]"
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

REVISIT:2026-11-30 計劃第二批(code-loop check 那一道、放行與 AI 放行通知)上線時,把推送檢查怎麼讀紀錄、怎麼放行寫進這篇
