---
type: system
status: doing
created: 2026-08-22
updated: 2026-11-07
self_audit: sonnet/2026-08-30
aliases:
  - 圖譜同步點名
  - sync nudge
  - 同步覆蓋
tags:
  - type/system
  - status/doing
  - scope/guards-gates
summary: |-
  FLOW:改 code→(Stop hook 當輪點名)→git commit/git push 的點名 2026-09-11 起改由 [[Systems/每支檔有家]] 照家算(不再用本篇的反引號為種子那一套)→代碼審留痕前 `lumos impact --diff --sync-check` 仍照本篇算
  KEY:★2026-09-11 起提交前與推送前的點名移出本篇★:原本兩個掛鉤都呼叫 impact --sync-only,以反引號命中的節點為種子,會把人推回寫了一堆別人檔名的大雜燴節點;改由每支檔有家照 about_code 宣告的家點名(家超過 8 篇只印一句)。本篇剩 Stop hook 當輪點名與代碼審留痕前的 --sync-check [test:t_nodehome_sync_nudge_by_home]
  KEY:「動過圖譜」不等於「動對篇」——(2026-09-11 前)三個位置都用 lumos impact --sync-check 算「跟改到的 code 直接相關(固定席:合約/事故/直接相依)、這次卻沒動」的筆記,點名前 8 篇;★2026-09-05 起兩家都在改了碼沒寫回時回 block 一次讓模型續做補筆記(stop_hook_active+session 標記雙護欄;Codex 先做 [[Projects/Codex行為精修_計劃]],Claude 同日套用 [[Projects/README審視五修_計劃]] d2——舊 stderr 提醒官方文件明講模型看不到)★,逃生門仍是 --no-verify(有繞過帳)
  KEY:刻意不硬擋:單體大檔(scripts/lumos)一次牽 30+ 篇,硬擋會把人訓練成反射 --no-verify
  KEY:[2026-09-17]收工擋停的標記目錄改成逐層建逐層檢查:原本一次 mkdir 整條路徑再檢查,上層被換成指向別人目錄的連結時,別人的目錄裡已經多出一個 stop-block 資料夾,檢查才說不碰它,跟它註解的承諾矛盾。判準跟主程式 _mkdir_trusted_under_home 同一套(真目錄、屬於自己、別人不可寫;任一層不過就停手、已建的不回頭刪),這支 hook 是獨立檔不 import 主程式所以邏輯抄一份,★一邊改了另一邊要跟著改★;誠實邊界:擋不住同帳號搶跑 [test:t_stop_block_dir_does_not_touch_someone_elses_dir]
  KEY:[2026-09-18]★第一個時機(收工那一支)的清單改成問版本控制★——原本閘門 2 與閘門 3 的判準都靠列舉工具名,用 `>` 重導向/`sed -i`/heredoc 改的檔一支都不算(實測一輪改三支只報一支,全走 shell 時連響都不響;逐字稿量到 286 次走 shell 對 31 次走編輯工具)。兩處都改;(當時要帶展開旗標,否則全新目錄摺成一行;2026-11-07 起收工那支不跑 git status,新檔改用 ls-files -o 逐支列,全新目錄裡的檔也一支支列出來)。核心代價=不再宣稱切得出「這一輪」,措辭改口成工作樹語意;為了不刷屏,清單跟上次印的一樣就不印(那份紀錄壞掉只會多印一次不會少報)。★不沿用本篇原本那個查詢的理由:它看不到從未被追蹤的新檔,而 `echo > 新檔` 正是最常見的 shell 寫法★。查詢失敗一律靜默放行。單源 [[Projects/收工點名問版本控制_計劃]] [test:t_sync_nudge_lists_shell_written_files] [test:t_sync_nudge_gate3_sees_shell_written_notes] [test:t_sync_nudge_lists_untracked_dir_files_individually] [test:t_sync_nudge_suppresses_identical_repeat]
  DEP:[[Systems/lumos-cli-read]]
  TEST:t_precommit_sync_nudge_names_missing_pinned_nodes(動錯篇點名/動對篇不點名)
  WHY:家目錄標記目錄、標記目錄信任檢查、標記檔名消毒(_mark_name)與 O_EXCL 佔名額(_claim_mark)、檔名消毒、git 防護從 check-graph-sync.py 搬進共用模組 _hookshared.py,這支照名字匯入回來;★可信來源解析與逾時預算留在這支當逐字複本★ [出處:[[Projects/Android寫法回合結束檢查與改檔前推列_計劃]] 範圍 2;代碼審 r1 丁組(governance/review-reports/code-android寫法回合結束檢查/r1-intake.md)] [因:收工寫法檢查也要用同一套、兩支的擋停標記在同一個目錄;安全邊界那兩段照 [[Systems/hook信任邊界]] 走複本] [不選:新鉤子用 importlib 載這支(會帶起它的模組層狀態)] [不選:安全邊界兩段也搬進共用模組(r1 架構對齊席 F1 擋下)] [代價:替換本模組的 _stop_dir_ok 打不到共用模組裡的呼叫;匯入純度探針放寬成「真的匯入共用模組的 hook、匯入系統自己」讀 _hookshared.py、列 hook 自己的目錄] [test:t_hookshared_move_keeps_graph_sync]
  WHY:兩支收工鉤子的檔集刻意不同:這支點名工作樹上全部未提交的程式碼檔(不切回合),[[Systems/回合結束寫法檢查]] 只看修改時間不早於回合起點的檔,擋停標記也分開 [出處:[[Projects/Android寫法回合結束檢查與改檔前推列_計劃]] 決策第三條] [因:新增告警要先分出這回合碰過的,否則每個新會談第一回合都被前人的未提交改動擋;這支只是提醒寫筆記,不切回合] [不選:兩支共用同一份檔集]
  WHY:收工點名找工作樹上沒提交的檔不跑 git status,改走 _wt_changed_nofilter(主程式同名函式的逐字複本,只用不經內容過濾器的 git 指令) [出處:governance/review-reports/code-android寫法回合結束檢查/r3-資安-sonnet.md F2(鉤子自己的 git status 遇到大小不變內容改過的檔執行被打開目錄自帶的 clean 過濾器)] [因:[[Systems/hook信任邊界]]〈第二個入口〉,過濾器名字由對方決定、列不完] [代價:LFS、autocrlf 專案會多點名幾支;子模組不再列] [test:t_lwt_r3_nofilter_attack] [test:t_lwt_r3_nofilter_verbatim]
  WHY:收工點名鉤子讀 stdin 遇到深層巢狀、非 UTF-8、超長整數或不是物件一律 rc0 靜默放行(原本只接 JSONDecodeError) [出處:governance/review-reports/code-android寫法回合結束檢查/r3-邊界-sonnet.md F1] [因:rc1 是非阻擋錯誤,但同族三支處理不一致] [test:t_hook_r3_stdin_shapes]
  WHY:收工點名呼叫影響分析改帶鉤子專用的 impact --diff HEAD --sync-check --worktree-nofilter:候選清單與模式走 _wt_changed_nofilter,上一個提交那一版用 _nodehome_cat_blobs_capped 讀、工作樹那一版直接讀檔(都受 _CODELOOP_BOOKKEEPING_HEAD_CAP 管),算出 +/- 行當查詢文字(代碼審 r4 起改成數行次數相減,見下面 _impact_line_delta 那行);超過上限或讀不到的那支只用路徑、列在 query_path_only;這個選項搭別的組合 rc2(搭 --file、--node 由既有的三擇一先擋) [出處:governance/review-reports/code-android寫法回合結束檢查/r3-資安-sonnet.md F2(git diff HEAD 在 racy 檔上執行 clean 過濾器)] [因:事故的 content: 觸發比對吃改動內容,只用路徑會漏報 pinned 事故,所以內容照算、只是不經 git] [不選:改 impact --diff HEAD 對所有呼叫端的行為;查詢文字只用路徑] [代價:自己算的改動行跟 git 切出的可能略有差異(r4 起數行次數相減,見下面 _impact_line_delta 那行)] [test:t_impact_r3_hook_no_filter_exec] [test:t_impact_r3_wt_nofilter_same_pins] [test:t_impact_r3_wt_nofilter_misuse] [test:t_impact_r3_wt_nofilter_fallback]
  PITFALL:被檢查的目錄是 repo 子目錄(monorepo)時,不跑 status 的找改動把乾淨的樹報成一堆刪除與改名、子目錄裡改過的檔整次回 None [出處:governance/review-reports/code-android寫法回合結束檢查/r4-正確性-sonnet.md F1、r4-邊界-sonnet.md F1、r4-通才-sonnet.md F1] [根因:ls-tree --full-tree 與 hash-object --stdin-paths 從 repo 根算路徑,ls-files 從 -C 的目錄算,兩邊對不起來] [修法:_wt_changed_nofilter(兩份逐字複本)先取 rev-parse --show-toplevel,之後每個 git 指令帶 -C 根、ls-files 加 --full-name、paths 前面補 --show-prefix,lstat 與索引檔位置都用根接(索引檔接錯時沒動的檔也會全部算雜湊),回傳路徑從 repo 根算(同 git status --porcelain);lint-new --worktree 的 --repo 指子目錄時改在 repo 根判(r5 起取根收成 _git_toplevel);影響分析 _impact_wt_nofilter 從 repo 根讀工作樹檔] [test:t_r4wt_monorepo_subdir]
  PITFALL:檔名結尾是 CR 的已追蹤檔改過時,hash-object --stdin-paths 把結尾的 CR 當行尾吃掉、整次失敗,找改動回 None,收工檢查與收工點名在那個 repo 每回合都沒作用 [出處:governance/review-reports/code-android寫法回合結束檢查/r4-正確性-sonnet.md F2] [根因:_wt_changed_nofilter 只把含換行與開頭是引號的路徑當改過,沒想到行尾的 CR] [修法:結尾 CR 的也當改過(多查)、不送去算雜湊;同批補時間等於索引檔時間、時間同大小不同、雜湊行數對不上、兩支同內容刪除檔四個邊界案例] [test:t_r4wt_cr_name] [test:t_r4wt_racy_equal_mtime] [test:t_r4wt_same_time_size_diff] [test:t_r4wt_hash_count_mismatch] [test:t_r4wt_twin_deletes]
  WHY:收工點名的影響分析(impact --worktree-nofilter)算改動行改用 _impact_line_delta:兩版各用 collections.Counter 數每行出現幾次再相減,舊版多的當 - 行、新版多的當 + 行;讀內容前先用 _impact_diff_seed_ok 判是不是程式碼、不是的不讀,兩版合計受 _IMPACT_WT_READ_TOTAL(8MB)管、工作樹那一版逐支讀逐支放,超過的、路徑含換行或結尾是 CR 的只用路徑列進 query_path_only;刪除檔的模式取 HEAD、首行讀 HEAD 那一版;接查詢文字與模式那一格的整形抽成 _impact_hunk_query、_impact_mode_entry、_impact_wants_head,git diff 那條也呼叫 [出處:governance/review-reports/code-android寫法回合結束檢查/r4-通才-sonnet.md F2、F3,r4-資源-sonnet.md F1、F2,r4-正確性-sonnet.md F3,r4-架構對齊-sonnet.md F1] [因:difflib 最壞平方時間 https://docs.python.org/3/library/difflib.html ,重複行多的 2 萬行檔實測 57 秒、吃光收工點名約 30 秒的預算;60 支 0.9MB 的 PNG 先讀才判,記憶體約 3MB 一支線性長;查詢文字只給事故正規式比對與排名用,行序不重要] [不選:超過行數門檻就退回只用路徑(大檔的 content: 事故就漏了);留 difflib 加逾時] [代價:只移動位置的行不算改動;.png 這類 _impact_diff_seed_ok 收的副檔名照讀(受總量上限管,含 NUL 當二進位)] [test:t_r4imp_counter_speed]
  WHY:鉤子找 lumos 的 _trusted_lumos(五支鉤子各一份逐字複本)第一步拒相對路徑:PATH 有空項或 .、LUMOS_HOME 給相對路徑時都會從目前目錄、也就是被打開的資料夾解出來 [出處:governance/review-reports/code-android寫法回合結束檢查/r4-資安-sonnet.md F1(PATH 有空項時 shutil.which 回相對的 lumos,收工點名鉤子執行了 repo 根那支)] [因:_ok 只驗擁有者與可寫位元,使用者解開別人給的整個目錄後檔案本來就是自己名下;信任邊界見 [[Systems/hook信任邊界]]] [不選:比照 _lint_wt_resolve_tool 逐項解析 PATH、跳過相對項往後找(五份複本都要多一套解析;拒掉後還有 LUMOS_HOME 與預設來源可退)] [代價:PATH 第一個命中是相對項時不往後找系統裝的那支,改用 LUMOS_HOME 或預設來源,都沒有就跳過那段功能] [test:t_r4hook_relative_lumos]
  PITFALL:sparse-checkout 圈外的檔(索引有、磁碟沒有)被不跑 status 的找改動報成刪除,標了 skip-worktree 或 assume-unchanged 又改過的檔報成改過,git status 兩者都是空的;收工點名把圈外每支碼檔當已刪除擋一次 [出處:governance/review-reports/code-android寫法回合結束檢查/r5-正確性-sonnet.md F1] [根因:_wt_changed_nofilter 只看 ls-files -s 的模式與物件,沒看索引旗標,磁碟上缺檔就當刪除] [修法:ls-files 改帶 -v,標 S(skip-worktree)或小寫(assume-unchanged)的條目不比工作樹、Y 留空白,HEAD 對索引照比(同 git status:暫存過再標 skip-worktree 的照報 M 空白);兩份逐字複本一起改] [test:t_r5wt_sparse_checkout_no_delete] [test:t_r5wt_skip_worktree_unchanged]
  WHY:入口第一句呼叫 _clean_path_env(主程式同名函式的逐字複本),PATH 只留絕對項,之後裸名呼叫 git 不會解到被打開資料夾裡的同名檔 [出處:governance/review-reports/code-android寫法回合結束檢查/r5-資安-sonnet.md F1] [因:PATH 空項等於目前目錄,信任邊界見 [[Systems/hook信任邊界]]] [test:t_r5path_hooks_verbatim]
  PITFALL:專案根是 repo 子目錄(monorepo)時,收工點名鉤子把找改動回的 repo 根相對路徑接在專案根上(sub/sub/…),沒副檔名的 #! 腳本認不出是程式、筆記動過也認不出而誤點名;它呼叫的 impact --worktree-nofilter --repo 子目錄在入口因為底下沒有 .git 直接 rc2,點名靜默沒資料 [出處:governance/review-reports/code-android寫法回合結束檢查/r5-邊界-sonnet.md F1、r5-通才-sonnet.md F1、F2、r5-正確性-sonnet.md F2] [根因:r4 只改了找改動的回傳基準,消費端與命令入口沒跟著改;單元測試直接呼叫函式、沒走鉤子與命令入口] [修法:鉤子用 _repo_top 取 repo 根,狀態表路徑一律接在根上(圖譜位置與在不在專案底下照舊用專案根判);cmd_impact_diff 只在 --worktree-nofilter 時改問 git(_git_toplevel)是不是 git 專案,其他呼叫端照舊要 .git] [test:t_r5sub_hook_e2e] [test:t_r5sub_impact_cli]
  REVISIT:2027-02-07 子目錄專案(monorepo)的影響分析反查:改動路徑從 repo 根算起(sub/x.py),筆記正文寫的多半是專案相對路徑(x.py 的完整路徑寫法 scripts/x.py),而且 _refcheck_scan 會濾掉頂層目錄不在 --repo 底下的路徑,目前只有裸檔名那條比得到;要不要把改動路徑去掉 --show-prefix 再反查,交人裁(代碼審 r5 修補時實測,git diff 那條同樣)
  PITFALL:影響分析 --worktree-nofilter 三處分支原本沒有測試、改壞照綠:不開非一般檔的 S_ISREG 守衛(拿掉後已追蹤檔換成 FIFO 會卡在 open)、檔名結尾 CR 退回只用路徑、已刪除檔的模式取 HEAD [出處:governance/review-reports/code-android寫法回合結束檢查/r5-合約-sonnet.md F1、F2、F3] [根因:r4 的案例只造了含換行的檔名與 100644 的刪除檔,FIFO 沒人造] [防回歸:FIFO 案例在子程序跑、30 秒逾時,改壞時紅而不卡住整套] [test:t_r5imp_fifo_guard] [test:t_r5imp_cr_name] [test:t_r5imp_deleted_exec_mode]
  WHY:影響分析 --worktree-nofilter 的改動行 + 行在前、- 行在後;_impact_hunk_query 邊累積邊停,湊滿 4000 字就不再往下拿 [出處:governance/review-reports/code-android寫法回合結束檢查/r5-合約-sonnet.md F4、r5-通才-sonnet.md F3(刪 120 行再加 DANGER_NEW,新增的行被 4000 字上限截掉)] [因:新寫進去的內容才是事故 content: 比對要看的;git diff 那條同一支整形,截法結果不變] [不選:兩邊各配一半字數(多一套配額算法,新增少時還得把剩的字數讓回去)] [代價:查詢文字的順序跟 git diff 不同(git diff 照 hunk 先刪後加)] [test:t_r5query_plus_first] [test:t_r5query_stop_early] [test:t_r5query_help_text]
  WHY:_wt_changed_nofilter(兩份逐字複本)不重綁參數 run,在 repo 根跑的那支叫 in_top、取根那兩次以外的 git 指令都經它;影響分析讀內容的兩版合計上限自己記帳、不用 _nodehome_cat_blobs_capped 的 max_total_bytes,刪除檔的模式另跑一次 ls-tree、不重用找改動解析過的 HEAD 表 [出處:governance/review-reports/code-android寫法回合結束檢查/r5-架構對齊-sonnet.md F2、F3] [因:同一個名字前後指向兩種函式時錯誤處理看呼叫順序;既有 max_total_bytes 只算批次讀的上一個提交那一版,工作樹那一版是直接開檔讀;找改動的 HEAD 表只留一般檔物件編號、不留模式,而且是鉤子的逐字複本、改回傳形狀要兩份與所有呼叫端一起改] [代價:同一個函式裡有兩種總量上限寫法(補看首行那段照用既有參數),理由寫在常數旁] [test:t_r5arch_no_run_rebind]
  PITFALL:專案根是 repo 子目錄(monorepo)時,兄弟目錄被刪的程式碼檔被收工點名當成本專案的檔、還進擋停清單;同族連三輪在不同下游各補一處 [出處:governance/review-reports/code-android寫法回合結束檢查/r6-正確性-sonnet.md F1、r6-邊界-sonnet.md F1、r6-通才-sonnet.md F1、r6-合約-sonnet.md F1] [根因:找改動回的是整個 repo,活檔靠 is_code_file 判專案範圍,被刪的檔走另一條分支沒有那道] [修法:鉤子的 _git_status_entries 是狀態表唯一出口,回傳前用 _rel_in_project 整批濾掉專案外的條目(改名兩端任一端在專案內就留,路徑照舊從 repo 根算);刪除分支不另補第二道,範圍只在出口判一次,各道測試才各自翻得紅;依 prek 的 monorepo 做法 https://prek.j178.dev/monorepos/ ] [test:t_r6del_sibling_e2e] [test:t_r6del_status_entries_scope]
verified_by:
  - "[[Verification/2026-09-05_Codex行為精修f02後測]]"
  - "[[Verification/2026-09-05_README審視量測]]"
  - "[[Verification/2026-09-18_收工點名改問版本控制]]"
  - "[[Verification/測試品質分支第二輪修復驗證]]"
decisions:
  - content: 收工 Stop hook 擋一次兩家一致(Claude 也擋):Claude Code 官方文件明講 exit 0 的 stderr 只進除錯日誌、模型看不到,舊「軟提醒」實為零;07-06 撤的是每回合 nag,同 session 只擋一次且只在改了碼沒寫回時不算重開 nag。單源 Projects/README審視五修_計劃 d2
    id: d1
    decided: 2026-09-05
    valid: true
about_code:
  - scripts/hooks/claude/check-graph-sync.py
  - scripts/lumos
  - governance/eval/sync-nudge/probe_sync.py
plan_refs:
  - "[[Projects/收工點名問版本控制_計劃]]"
related:
  - "[[Projects/收工點名問版本控制_計劃]]"
---
# graph-sync-coverage

# graph-sync-coverage

> 白話:以前「改 code 沒動圖譜」的閘只看「有沒有任何一篇圖譜檔一起 commit」,隨便動一篇就過,真正該改的那篇沒改它看不出來——這就是 Enzo 說的「偶有沒能同步完全」。現在不加新機制,把原本只供人看的 `lumos impact --sync-check` 接到三個時機點名。

## 三個時機
| 時機 | 在哪 | 印什麼 |
|---|---|---|
| 這一輪結束時(★2026-09-18 起算的不是「這一輪改了什麼」,是「工作樹上還沒提交什麼」,見下節★) | `scripts/hooks/claude/check-graph-sync.py`(Stop hook;Codex 註冊時帶 `--harness codex`,同條件擋一次) | 即使這輪動過圖譜,仍點名「直接相關、這輪沒動」的篇(★2026-09-12 起理由變三種:是那支檔的家、帶合約、出過事故——推筆記認家上線後,固定席多了 kind=home 那一類,這支 hook 直接吃 `impact --sync-check` 的固定席,所以跟著變;見 [[Projects/推筆記認家_計劃]]★)(★2026-08-30 自足審計訂正:現況=單次 `impact --diff HEAD --sync-check --worktree-nofilter --json`(工作樹 vs HEAD,不經內容過濾器)取固定席前 8 篇——原「每檔 impact --file、最多 4 檔」是重構前舊貌,src_files 參數已是殘跡★) |
| `git commit` | `scripts/hooks/pre-commit` Gate 3 | `impact --diff staged --sync-check`,固定席優先、自由席補滿到 8 篇(pre-commit/pre-push 實際帶的旗標是 `--sync-only`,蘊含 sync-check 且只印點名) |
| `git push` | `scripts/hooks/pre-push` | 同上對整批 range——分開幾個 commit 各自過關、整批漏掉的在這裡浮出 |

## ★2026-09-18 起:第一個時機的清單改成問版本控制★

單源 [[Projects/收工點名問版本控制_計劃]]。上表第一列(收工那一支)的「改了哪些程式碼檔」不再靠列舉工具名算。

**為什麼改**:原本清單來自「這輪用了哪個工具」——只認三個編輯工具加 rm/mv/cp 那幾個命令。用 `>` 重導向、`sed -i`、heredoc 改的檔一支都不算。實測造一輪改三支程式碼檔(一支走編輯工具、兩支走 shell),它只報一支;一輪全走 shell 時連響都不響。配套量到最近 12 份逐字稿裡,改程式碼檔的動作 286 次走 shell、31 次走編輯工具——**九成走在不被計入的那條路上**。

★兩處都壞,不是只有一處★:閘門 2(算清單)與閘門 3 的分岔判準(這輪有沒有動過圖譜)都靠認名字,只修前者的話,同一種少報會換到後者活下來(用 shell 同時改程式碼和筆記時誤判「筆記沒動」)。

**改成什麼**:

| 問題 | 改成怎麼算 |
|---|---|
| 是哪幾支程式碼檔 | 問版本控制:工作樹上未提交的(不跑 git status;已追蹤的用 ls-files 加 hash-object 比,新檔用 ls-files -o 逐支列,全新目錄裡的檔也一支支列出來) |
| 這輪有沒有動過圖譜 | 同上:未提交的檔裡有沒有圖譜筆記 |
| 要不要印出來 | 跟「上次印過的清單」比,完全一樣就不印 |
| 哪幾篇筆記該動沒動 | **不動**,本來就是 `impact --diff HEAD --sync-check` |

★為什麼不沿用本篇原本那個查詢★:它底層是拿工作樹跟上次提交比,**看不到從未被追蹤的新檔**——而 `echo > 新檔.py` 正是最常見的 shell 寫法,沿用它這個病會原封不動留著。實測:改一支既有檔 + 建一支全新檔 + 建一個新目錄,那個查詢只列得出既有那一支。這是本案唯一刻意偏離既有做法之處。

**核心代價**:清單是「工作樹上未提交的」,★不再宣稱切得出這一輪★——含這輪以外的改動,共用工作目錄下還可能含別人的。所以訊息從「這一輪改了 N 個程式碼檔」改口成「工作樹上有 N 個程式碼檔還沒提交」。換來的是「用什麼工具改的都看得到」。

**兩條輸出路徑列的東西一樣,差別在措辭**:兩條都列完整清單。★初版曾讓模型那條只列「這一輪」的檔,想避免叫模型去補別人的帳——但拿來算「這一輪」的正是這次要換掉的那套工具名清單,結果用 shell 改的檔在模型那條完全不列名,少報換個位置活著(代碼審 r1 兩席獨立報)。★ 正解是承認「這一輪」算不準:列完整清單,並在送給模型那條的首句明說「不保證每支都是你這一輪改的,共用工作目錄下可能含別人的,自己判斷哪些該補」,讓模型自己判斷,而不是由我們用一把壞尺替它篩掉。

**失敗時**:版本控制查詢失敗(不是倉庫、索引被鎖、逾時)一律靜默放行(空倉庫不算失敗,照常列出工作樹上的檔),不擋不當機。代價是那種環境下這個提醒等於不存在且無人知曉;接受理由是提交前那道閘仍然會擋,最終防線不依賴本機制。

**已知限制**:被版本控制忽略的檔、子模組內的改動看不到;同一輪改完又提交(尤其用 `--no-verify` 繞過)會讓本機制與提交前那道閘同時靜默。

## 驗收儀器

`governance/eval/sync-nudge/probe_sync.py` 是本篇第一個時機(收工那一支)的情境產生器:造假的對話紀錄餵給那支 hook,比對「實際改幾支」與「它說幾支」,九個情境一次跑完。只讀 hook、不改被檢查的 repo。

用法(第一個參數是要檢查的 repo 根):

```
python3 governance/eval/sync-nudge/probe_sync.py <repo根>
```

★它為什麼在版本控制裡★:撤除條件靠它——「每季重跑一次,九個情境全部回到修前的結果就撤掉這條路徑」。之前只有它的輸出日誌在卷證目錄,三個月後沒人跑得動,等於撤除條件寫了等於沒寫。

★十一個情境裡有三個是刻意的考題★(管線寫入、一行 python 寫檔、包一層 shell):它們是設計時**沒有列舉過**的手法。補完列舉表不算修對,要這三個也過才算——因為現在的做法不看用了什麼工具,所以它們自動涵蓋。

### ★現場一定要真的改檔★(2026-09-18 實地踩到)

第一版的情境只在對話紀錄裡「宣稱」改過檔,**沒有真的動檔案**。清單來源改成問版本控制之後,工作樹是乾淨的、它就正確地回答「沒有」——於是九個情境全部 FAIL,**而每一個 FAIL 其實都是新行為的正確表現**。

這比單純沒修更糟:**它是撤除條件依賴的儀器**(「每季重跑一次,情境全部回到修前結果就撤掉這條路徑」)。壞掉的它會永遠全 FAIL,那個判準等於永遠成立——**撤除條件被自己的儀器架空**,而且會在三個月後給出一個看起來有依據的錯誤結論。

同一個形狀當天在正式測試那邊也踩過一次(既有的擋停測試造完現場就提交、工作樹乾淨),當時修了正式測試、**卻沒想到這支給人手動跑的工具帶著同樣的舊假設**。

改法:每個情境都真的改檔,各自在臨時倉庫裡跑完就丟(也不再像舊版那樣在專案裡留下測試殘檔)。修完對★實際部署的那份 hook★重跑,十一個情境全過。

### 修前修後對照(對實際部署的 hook 實測)

| | 修之前 | 修之後 |
|---|---|---|
| 用編輯工具改一支 | 說 1 支 ✓ | 說 1 支 ✓ |
| 用重導向 / 原地取代 / heredoc | **完全沒輸出** | 各說 1 支 ✓ |
| 管線寫入 / 一行 python / 包一層 shell | **完全沒輸出** | 各說 1 支 ✓ |
| 刪掉沒有副檔名的程式檔 | 判不出來 | 說 1 支 ✓ |
| 新目錄裡兩支檔 | 摺成一行 | 說 2 支、逐支列 ✓ |
| **混用(編輯工具一支 + shell 兩支)** | **說 1 支** | **說 3 支 ✓** |

## 收工那一支的已知限制

代碼審 r1 六席指出、經判斷後**不在本批處理**的邊界,逐條寫明而不是略過。每條都附「為什麼可以先不處理」,不是靜默放掉。

| 限制 | 後果 | 為什麼先不處理 |
|---|---|---|
| (已解除)改名原本用 ` -> ` 切字串,檔名含這串時會切錯;現在找改動不跑 git status,改名由結構化欄位回傳,不再切字串 | — | — |
| 空倉庫(還沒有第一個提交)時,讀「上次提交裡的內容」會失敗 | 該檔判不出是不是程式碼檔 | 失敗已被接住(當作不是程式碼檔);空倉庫本來就沒有「上次提交」可讀,這是定義問題不是缺陷 |
| 拿不到會談識別碼時,去重機制整個失效 | 退回「每輪都印」 | ★失效方向是安全的★:退化的是體驗不是正確性,不會少報。這正是那份紀錄的設計取捨——壞掉只准多印 |
| 印給人看的那條沒有消毒檔名(送給模型那條有) | 終端機可能被檔名裡的控制字元干擾 | 既有行為、非本批引入;而且那條輸出給人看,不進模型 |
| 新增又刪除、從未提交過的無副檔名程式檔仍判不出來 | 那種檔不會進清單 | 結構性的:它從未進過版本控制,讀不到「上次提交裡的內容」。既有限制、非本批引入 |

| 去重紀錄在「擋停」那條路沒存檔,所以抑制要到第三次呼叫才生效(註解寫的是第二次) | 印給人看的那條會多印一次 | 影響的只有給人看的那條——★給模型的那條另有擋停名額限制成整個會談一次★;後果是多印不是少報,跟那份紀錄的設計取捨一致(壞掉只准多印) |

★回頭條件★:上面任何一條在真實使用中造成一次實際困擾(誤報被人抱怨、或漏報害人漏寫筆記),就在下一次動這支檔時一併處理,並把該次事故記進逃逸帳。

## 為什麼不硬擋
本 repo 改 `scripts/lumos` 一次,固定席就 30+ 篇。硬擋等於每次都擋,人會養成 `--no-verify` 反射,比現在更糟。提醒要具體到篇名才有用——之前的提醒只說「筆記沒動」,現在說「這篇、這篇」。

## 怎麼用
`lumos impact --diff staged --sync-check`(commit 前自己先看)、`lumos impact --diff <range> --sync-check`(推前)。

## 程式分類補齊

PITFALL: PHP 與 Node 模組來源被附件分类誤排，日後同步點名亦需要共用完整分類 [出處:code-test-quality-native-push/r2-邊界-codex.md] [防回歸:t_code_exts_lists_agree、test_php_and_node_variants_kept_in_impact]。沿既有五份一致性控制补齊，不改 Stop 點名、阻擋次數與失敗處理。
