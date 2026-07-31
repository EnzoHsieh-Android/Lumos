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
  DEP:scripts/lumos(唯一輸入源)｜scripts/test_lumos.py t_slim_gen/t_slim_gen_loop_registration/t_slim_gen_keeps_comments
  TEST:12 checks 全綠(`python3 scripts/test_lumos.py -k slim_gen`)——真檔生成(--help==保留24支/py_compile 0 SyntaxWarning/dangling handler=0)+合成fixture(驗迴圈註冊真的被砍,現行白名單下無真實對象故必須合成)+註解密度守衛(★產物註解密度不得低於原檔90%★,抓 ast.unparse 迴歸;哨兵 test_lumos.py 260→94 事故註解,2026-07-31 收尾時把原 brief 的 W4/百分比門檻哨兵換掉,見下方 DECISION)
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
---
# slim-gen-生成器

公開精簡版交付前的 AST 生成器。從 `scripts/lumos` 單檔 CLI 生成「只留 24 支保留指令」的精簡版,產物給離職接手者(或開源使用者)。核心價值主張(見〈公開精簡版計劃〉〈誠實天花板〉):Python 原始碼是可讀語言,精簡版必須是「接手者改得動」的完整原始碼,不是打包後的黑盒——因此保留原始碼裡所有事故脈絡註解,行級手術是唯一能做到這點的實作方式。詳見 [[Projects/公開精簡版_實作計畫]] Task 2。

規格/設計脈絡見 `.superpowers/sdd/公開精簡版_實作計畫/task-2-brief.md`(SDD 產出,非圖譜路徑,依計畫落地於此)。
