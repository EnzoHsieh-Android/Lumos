---
type: system
status: done
created: 2026-07-31
updated: 2026-07-31
tags:
  - type/system
  - status/done
summary: |-
  FLOW:讀 `scripts/lumos` 原始碼 → AST parse → 算 root 集合(保留指令 dispatch 分支呼叫的函式 + module-level 語句/class body 呼叫的函式,★root 不可只算 dispatch,否則模組層賦值如 `_SKILLS = _skills_list()` 的 helper 會被誤砍★)→ 從 root 做可達性閉包(BFS)→ 補集=移除函式清單 → 收集刪除的行號範圍(整函式/dangling subparser 註冊/dispatch if 分支)+ 少量重排插入(混合保留移除的迴圈註冊,唯一允許重排的小塊)→ 對原始文字做行級刪除套用(不重建保留部分的任何字元)→ 自我 `ast.parse` 驗證產物語法完整
  KEY:★正解是行級手術,不是 ast.unparse★——語法樹無註解,`ast.unparse` 實測把 686 行事故脈絡註解全剝光、格式全重排,直接違背〈公開精簡版計劃〉「接手者改得動」的核心價值主張;唯一允許重排的例外是混合保留/移除的迴圈註冊小塊(2-3 行)
  KEY:移除謂詞=「保留指令 dispatch 的 AST 可達性閉包之補集」,不是 `cmd_` 前綴字面比對(lint-watch 實作叫 `_lint_watch_mode`、保留的 doctor 叫 `run_doctor`,前綴法會誤判)
  KEY:removed_cmds 真值來源=掃全部 subparser 註冊(Assign/Expr/迴圈三種形態)得到的指令全集減 DEFAULT_KEEP(24 支),不硬編移除清單
  KEY:產物自我驗證雙保險——① `ast.parse(new_text)` 失敗即 rc1 中止(行級刪除最容易刪出語法洞的地方)② `--emit-manifest` 印 `keep_funcs`/`drop_funcs`/`removed_cmds`/`kept_comment_lines` 供測試/人工核對
  KEY:★迴圈註冊刪除須 top_var receiver 限定★(2026-07-31 審查揪出、已修復,不是「超出範圍」)——`_is_registration_loop` 原本只看 for 迴圈 body 有沒有 `X.add_parser(迴圈變數,...)`,完全沒查 receiver `X` 是不是頂層 subparsers 變數(`top_var`)。後果:一個被保留的指令,若用迴圈註冊「自己的」巢狀子指令(如 `osub = p2.add_subparsers(...)` 後 `for n,h in (...): osub.add_parser(n,help=h)`,receiver 是 `osub` 不是 `top_var`),整段迴圈會被誤判成頂層指令迴圈、拿巢狀子指令名去跟頂層 keep 名單比對(當然比不中)、整段砍空——即使外層指令本身在保留清單裡。審查用合成 fixture(`otherkeep` 巢狀註冊 `removeme`/`x2`)實地示範重現;現行 `scripts/lumos` 沒被咬到純屬巧合(全檔唯二匹配的巢狀迴圈——`links`/`backlinks`兩者皆保留不觸發混合刪除、`code-loop` 底下的 `pass`/`skip`/`check` 因 `code-loop` 本身就是移除指令整塊本來就要砍——潛伏缺陷不是已發生的錯誤)。修法:`_is_registration_loop(n, top_var=...)` 加 receiver 檢查,`collect_edits()` 與 `main()` 印診斷用的 `allc` 掃描兩處呼叫點都傳入 `top_var`(★兩邊是同一段未防護邏輯,不是各自獨立的問題★);連帶修正 `collect_edits()` 的 main.body 區塊追蹤——nested for 迴圈(receiver≠top_var)不再被無條件剝離去單獨處理,而是併入所在區塊(隨區塊留/隨區塊砍),否則「巢狀迴圈屬於已移除群組指令(如 code-loop)」的情況會反向退化成漏刪、產出 NameError。
  DEP:scripts/lumos(唯一輸入源)｜scripts/test_lumos.py t_slim_gen/t_slim_gen_loop_registration/t_slim_gen_nested_loop_registration/t_slim_gen_keeps_comments
  TEST:24 checks 全綠(`python3 scripts/test_lumos.py -k slim_gen`)——真檔生成(--help==保留24支/py_compile 0 SyntaxWarning/dangling handler=0)+合成fixture(驗迴圈註冊真的被砍,現行白名單下無真實對象故必須合成)+巢狀迴圈合成fixture(`t_slim_gen_nested_loop_registration`,驗保留指令自己的巢狀註冊迴圈不被誤砍、頂層迴圈砍法不退化)+註解密度守衛(★產物註解密度不得低於原檔90%★,抓 ast.unparse 迴歸;哨兵 test_lumos.py 260→94 事故註解,2026-07-31 收尾時把原 brief 的 W4/百分比門檻哨兵換掉,見下方 DECISION)
verified_by:
  - "[[Verification/2026-07-31_slim-gen生成器落地]]"
  - "[[Verification/2026-07-31_公開精簡版交付]]"
decisions:
  - content: t_slim_gen_keeps_comments 的斷言二次修正:原哨兵 W4 位於 _link_or_copy(scripts/lumos:7238),只被 _install_skills 呼叫、後者只從 cmd_install/cmd_uninstall 可達——兩支都在移除清單,W4 被砍是正當汰換,是 brief 挑錯哨兵,不是生成器漏砍。改用 test_lumos.py 260→94 那條事故註解(出現兩處:module-level TEST_PROFILES dict 字面值 + 保留指令閉包內的 discover_test_methods(),兩處都保證留在產物中)。門檻同時從「保住 N% 註解」(N=60→50,前手依實測 55% 下修過一次)改成「產物註解密度不得低於原檔的 90%」。
    id: d1
    context: 任意保留率門檻無意義(砍多砍少都會動它),真正該鎖的是密度沒有下降——那才是行級手術相對 ast.unparse 的實質保證
    why_chosen: 密度守衛照樣抓得住 ast.unparse 迴歸(密度歸零);實測原檔 11999行/686行註解=5.7%,產物 6203行/379行註解=6.1%,未下降
    decided: 2026-07-31
    valid: true
  - content: 迴圈註冊刪除加 top_var receiver 限定:2026-07-31 審查(Task 5 複審)以合成 fixture 實地示範重現「保留指令巢狀自建註冊迴圈被誤砍空」——修 _is_registration_loop 加 receiver 檢查、collect_edits()與main()診斷用allc掃描兩處呼叫點統一傳入top_var,並修正collect_edits()的main.body區塊追蹤(nested迴圈併入所在區塊隨去留,不再無條件剝離單獨處理)。前一位實作者曾把此現象定調為「main()印診斷用allc掃描沒限定receiver、collect_edits()是安全的、純診斷雜訊、超出範圍」——經審查追碼確認兩邊是同一段未防護邏輯,那個定調錯誤,已不採用。
    id: d2
    context: 審查用合成fixture(otherkeep巢狀註冊removeme/x2)demonstrate:一個被保留的指令若用迴圈註冊自己的巢狀子指令,那段迴圈會被整個砍空,即使該指令本身在保留清單。現行scripts/lumos沒被咬到純屬巧合(links/backlinks都保留不觸發、code-loop底下pass/skip/check本來就該整塊砍),是潛伏缺陷不是已發生的錯誤。
    why_chosen: receiver檢查是最小且對稱的修法——與_add_parser_name既有的top_var限定同一套設計語言;順帶修main.body區塊追蹤讓nested迴圈跟隨所屬群組指令去留,避免只修『不該砍』又反向破壞『該砍』(code-loop案例的NameError回歸,已用t_slim_gen_nested_loop_registration+既有真檔測試雙重鎖死)
    decided: 2026-07-31
    valid: true
---
# slim-gen-生成器

公開精簡版交付前的 AST 生成器。從 `scripts/lumos` 單檔 CLI 生成「只留 24 支保留指令」的精簡版,產物給離職接手者(或開源使用者)。核心價值主張(見〈公開精簡版計劃〉〈誠實天花板〉):Python 原始碼是可讀語言,精簡版必須是「接手者改得動」的完整原始碼,不是打包後的黑盒——因此保留原始碼裡所有事故脈絡註解,行級手術是唯一能做到這點的實作方式。詳見 [[Projects/公開精簡版_實作計畫]] Task 2。

規格/設計脈絡見 `.superpowers/sdd/公開精簡版_實作計畫/task-2-brief.md`(SDD 產出,非圖譜路徑,依計畫落地於此)。
