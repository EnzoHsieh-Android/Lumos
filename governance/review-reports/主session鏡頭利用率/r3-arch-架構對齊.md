# r3 架構對齊審(主session鏡頭利用率_計劃,第 3 版上限輪)

審材(凍結):`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/26a6b57a-9efc-4073-b845-c27e42a2fbb1/scratchpad/主session鏡頭利用率-r3.md`
第 2→3 版差異:`governance/review-reports/主session鏡頭利用率/r3-delta.diff`
只判「跟本 repo 既有做法不一樣」;不找 bug、不評風格。編號從 f17 起(f1–f8 是 r1,f9–f16 是 r2)。

## 零、前輪 8 條(f9–f16)驗收:元件是否真的拆了

r2 那席判的 8 條全部釘在「hook 寫帳/gov 第八源/`lens` 子命令命名/timeout 配對/gitignore 登記/`collect_turn_touches` 共用 helper 落點」這些**元件本身**上。r3 把 `lumos lens push/tally`、`docs/.lens-log.jsonl`、`lens-tally-hook.py`、gov 第八源、SubagentStop 註冊整批砍掉(`主session鏡頭利用率-r3.md:37`「r2 儀器歸零……不加帳、不加 hook、不加子命令」、`:75`「r1 版的推送記帳、獨立帳、gov 第八源、lens 子命令、tally hook、SubagentStop、gitignore、timeout、撞名——整批不需要」)。逐條核對:

| r2 | 判 | 依據 |
|---|---|---|
| f9 gov 第八源缺 gate/token | **已拆** | 「同步清單」只剩圖譜+README+test_lumos 三項,無 gov 登記(`:96-98`) |
| f10 hook 註冊順序假合約 | **已拆** | 無新 hook,tally hook 不存在 |
| f11 `lens`/`dispatch-lens` 命名撞 | **已拆** | 無 `lumos lens` 子命令、無 `_lens_*` helper |
| f12 `kind` 值域非動詞 | **已拆** | 無 `kind` 欄位、無 ledger schema |
| f13 timeout 配對/`LUMOS_HOOK_DEBUG` | **已拆** | 無新 hook,「不印進任何 hook」(`:86`) |
| f14(major)`collect_turn_touches` 共用 helper 沒落點 | **已拆,且原問題不復現** | 見下方問三——腳本自己讀逐字稿,不宣稱共用 `check-graph-sync` 的 helper,f14 的「共用但沒機制」張力消失 |
| f15 帳檔定位函式沒指名 | **已拆** | 無 ledger,不需要定位函式 |
| f16 gitignore 登記錯誤來源 | **已拆** | 無新帳檔要忽略;「文件……命令數與登記點★全部不動★」(`:101`) |

八條結構性都已隨元件拆除消失,判斷正確。但「元件真的拆了」不等於「文字全部跟著改」——`誠實界線`與`實務隱患`兩段裡各留了一句還在講「獨立帳」「帳裡記」,這是 r2→r3 diff 沒有動到的既有行(見 `r3-delta.diff` context line,不在 `+`/`-` 裡),屬於殘留,列 f17/f18。

### f17 「實務隱患」的 self-governance 緩解清單仍列著已經拆掉的獨立帳

`:117` 的「緩解」四項裡還有「獨立帳」,但本版正文(儀器 1-8、同步清單)已經沒有任何獨立帳——d3 明寫「不加帳」(`:37`)。這句沒跟著改,照字面實作的人會以為還要開一本 ledger,等於在文件裡留了一條「第二做法」的活路。
引句:「緩解=零義務、不印給模型、獨立帳、fail-open。」
severity: major
blocking: 是

### f18 「安全」段仍用「帳裡記」描述輸出,跟本版「輸出只落報表檔」的說法不一致

`:121` 說「帳裡記節點名與檔名」,但本版的輸出物是 governance/eval/…/ 下的報表檔(`:86`「腳本輸出只落檔案」),不是帳(ledger)。兩處對同一件事用兩種語彙且語意不同(帳=持續 append 的 ledger;報表=每次重算覆寫的檔案),讀的人分不清這支腳本到底寫不寫一本累積帳。
引句:「帳裡記節點名與檔名(repo 內部路徑),不記 diff 內容」
severity: major
blocking: 是

## 一、分層(governance/eval/ 唯讀腳本 vs lumos 子命令)

新結構把腳本放 `governance/eval/lens-utilization/`,明寫「同席間覆蓋率那支 recount.py 慣例」(`:77`)。核對 `governance/eval/seat-coverage/recount.py`:唯讀、`sys.argv` 取輸入路徑、直接 `print` 到 stdout、零 lumos/subprocess 依賴、未進 `scripts/test_lumos.py`(全檔搜尋 "recount"/"seat-coverage" 零命中)file: `governance/eval/seat-coverage/recount.py:1-10`。r3 對「不進測試」這條確實照抄(`:102`「腳本本身照席間覆蓋率那支慣例不進測試(唯讀、可重跑)」),對「放哪」也照抄(governance/eval/<主題>/,不是 lumos 子命令——這正好是 r2 f8 已經判過對的地方,也是本輪唯一沒被拆掉又保留正確的舊結構)。README 的部分,`seat-coverage/` 本身沒有 README,但 `governance/eval/hook-intercept/README.md` 是同資料夾家族裡「怎麼重跑」文件的先例 file: `governance/eval/hook-intercept/README.md:1-5`,r3 計劃「該目錄的 README(將建)寫重跑步驟」(`:101`)跟這個先例對得上,不算新做法。

### f19 輸出物「落檔案」跟被引用的 recount.py 先例本身(印 stdout)不一致

recount.py 的自我定位是「唯讀、零配額、零副作用。輸出直接印,數字要進圖譜就自己抄」file: `governance/eval/seat-coverage/recount.py:6`——這支腳本從來不寫檔,人讀 stdout 後自己抄進圖譜。r3 卻在 Hawthorne 段寫「腳本輸出只落檔案(governance/eval/…/ 下的報表)」(`:86`),同一份文件既引用 recount.py 當慣例依據,又在輸出型態上跟它不同。兩者要達成的「不印給模型」目的其實靠 print-to-stdout 就已經滿足(執行者是人不是模型),看不出為什麼這支要多一層「寫檔」——如果理由沒寫清楚,之後維護的人會不知道該學 recount.py 印,還是學這支寫檔。
引句:「腳本輸出只落檔案(governance/eval/…/ 下的報表)」
severity: minor
blocking: 否

## 二、命名與錯誤處理

### f20 推送記錄的欄位叫 `session`,但整條鏈(hook payload、逐字稿、r2 舊 ledger schema)上都是 `session_id`

`impact-hook.py` 的 hook payload 欄位是 `session_id`(`payload.get("session_id", "")`)file: `scripts/hooks/claude/impact-hook.py:447`;逐字稿子代理那份本身的欄位是 `sessionId`(`:79`「`sessionId` 是主 session 的」);連 r2 已刪掉的舊 ledger schema 都寫的是 `session_id`(`r3-delta.diff:10`「`session_id`, file, mode, pinned」)。到了 r3 這支腳本的每筆推送記錄卻縮寫成 `session`(`:82`),跟上下游三處都對不上,是本輪新出現的命名不一致,不是延續舊有做法。
引句:「**每筆推送記**:{session, is_subagent(★判法」
severity: minor
blocking: 否

### f21 ⚠ 沒有說腳本遇到壞資料/空資料時怎麼收尾,recount.py 這條先例是有明確約定的

recount.py 對「這批資料根本算不出東西」有清楚且吵的處理:`if not cc: print("帳上沒有 capture_counts 欄——這支算不出東西。"); return 1` file: `governance/eval/seat-coverage/recount.py:26-28`——印一句人話、回傳非 0。r3 只處理了「樣本太少」這一種退化情形(`:89`「推送若 <20 → 樣本不存在,改題」),沒提逐字稿整份缺 `hook_additional_context`、subagent 目錄不存在、或某行 JSON 壞掉時腳本要印什麼、回什麼碼——這是唯讀重算腳本這個類別裡,recount.py 已經定下但 r3 沒接住的一角。標 ⚠ 是因為這更可能是這個設計高度本來就不寫到的實作細節,不一定是刻意的做法分歧;若已經有共識「照 recount.py 的『印一句+非 0』模式做」,這條可以直接消。
引句:「先跑歷史:主 session 非空固定席、非 scratch 的推送若 <20 → 樣本不存在,改題」
severity: minor
blocking: 否

## 三、第二種做法(自寫逐字稿解析 vs 復用 check-graph-sync;前置修正是改既有函式還是繞路)

**逐字稿解析自己寫,不從 `check-graph-sync.py` import——判對齊。** 三個理由都在審材與鄰居檔案裡有實據:①本 repo 六支 hook 之間零跨檔 import,沒有共用模組(`impact-hook.py`/`check-graph-sync.py` 連 `CODE_EXTS`、`EXCLUDE_PATH_CONTAINS` 這種小表格都是各自複製一份、用「同源」註解互指,不是真的共用)file: `scripts/hooks/claude/impact-hook.py:26`「同源:check-graph-sync.py(20 副檔名版)」、file: `scripts/hooks/claude/impact-hook.py:42`「同源:check-graph-sync.py EXCLUDE_PATH_CONTAINS / EXCLUDE_FILENAMES」——自己寫一份是延續既有慣例,不是新做法。②`collect_turn_actions` 語意跟這支腳本要的東西本來就不同:只掃「到最近一次真實 user 輸入為止」的本回合、回兩個無序扁平 list、不收 Read、不管子代理檔案 file: `scripts/hooks/claude/check-graph-sync.py:107-146`;r3 要的是跨全部逐字稿(主+子代理多檔)、有序、含 Read、含 hook 附件的歷史掃描(`:79-82`)——語意差距大到「復用」在這裡等於整個重寫，跟 import 沒有實質差別。③審材自己的歷史記錄裡已經有「試過復用、發現不夠、才自寫」的實據,不是沒想過就跳過:`extract_bash_file_paths`(check-graph-sync 既有的 Bash 路徑抽取函式)被 r1/r2 明確點名「不認 cat/sed」而放棄沿用(`:13`「extract_bash_file_paths 不認 cat/sed」、`:33` 同句於 d2 context)。三條合起來,這不是「懶得查鄰居」的分歧,是查過、試過、留了理由的借用判斷,跟 CLAUDE.md 要求的「PRIOR-ART」精神一致。

**前置修正是改既有函式,不是繞路——判對齊。** 兩處都指名既有函式:①`hook_decide` 現況只看副檔名(`p.suffix.lower() not in CODE_EXTS`)file: `scripts/hooks/claude/impact-hook.py:84-102`,且 `main()` 現況確實是先呼叫 `hook_decide(payload)`(`:430`)才在後面拼 `file_path_abs`(`:441-444`)——審材對這個順序缺陷的描述(「現況 main 先 hook_decide 再拼絕對路徑」,`:85`)跟原始碼逐字對得上,不是憑空猜的。修法是讓 `hook_decide` 認得到 shebang,而不是在旁邊另開一支「影子過濾器」。②TTL 標記現況是「判定+寫」耦合在 `_ttl_should_inject` 一支函式裡(讀標記→比對→必要時清理+更新標記,一次做完)file: `scripts/hooks/claude/impact-hook.py:127-171`;`:85`「TTL 標記改在★真的注入之後★才寫」講的是移動同一個標記的寫入時機,不是另開一個標記系統。審材沒有寫到「怎麼拆」(要不要把 `_ttl_should_inject` 拆成唯讀判定 + 另一支寫入)這一層實作細節,但這是同一個函式責任怎麼分,不構成「第二做法」——沒有任何一句話提到要新增第二個標記檔、第二個判定路徑。

不對齊共 5 條,其中 major 2 條。
