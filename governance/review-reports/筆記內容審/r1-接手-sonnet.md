severity: blocker
# 筆記內容審_計劃 r1 審查(接手鏡頭/整合·知識同步)

severity: blocker

審查範圍:逐節讀完 `r1-work.md`(155 行),核對程式碼 repo(clone-ns)裡 `scripts/lumos`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`、`scripts/templates/graph-discipline.md`、`skills/lumos-project-notes/commands/06-代碼審與推送.md`、`skills/lumos-code-loop/`、`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md` 及前身 r3 卷證(`governance/review-reports/筆記不存程式碼推得出的事/r3-*`)。審查鏡頭:三個月後接手的人照這份做,會在哪裡撞牆——重點是抽共用函式牽連的呼叫端、代碼審帳本提交/判定檔提交/第一層檢查三者在同一次推送裡的先後、skill 路由表能不能讓人照做、條款測試名與內容是否對得上、新家該管哪些檔。

---

## F1 判定檔提交會讓已記錄的代碼審留痕(code-loop pass)自我失效,規格全篇沒處理這個互動

severity: blocker
blocking: 是 —— 這會讓「tier=high 且這次推送有新筆記待判」的正常路徑反覆觸發不必要的全套代碼審重跑,直接違背 CLAUDE.md「過代碼審的功能多一個帳本提交」與 lumos-code-loop 既有設計的預期行為;沒有任何條款(S1–S16)測到這個互動,回退段也沒提到

**現象(可重現,不是臆測)**

1. 開發者照 `skills/lumos-project-notes/commands/06-代碼審與推送.md` 既定流程(這是**推送前的準備動作**,不是被擋之後才做):寫完程式+筆記 → `lumos pitfalls --diff` 判 tier=high → 走完對抗代碼審 → `lumos code-loop pass --note "…"`。這一刻的留痕綁在當時的 HEAD(設為 SHA_A)。
2. 這批改動裡照例會有新寫的筆記行(spec 自己在〈誠實界線〉第 5 點承認:「本 repo 幾乎每次推送都有新增筆記行」)。`git push` → pre-push 依序跑 `home check` → `note-shape --diff` → **note-audit check**(spec 做法第 3 節第 6 點:「跟 `home check`、`note-shape --diff` 並排」,即排在 code-loop check 之前)→ 這是 note-audit 第一次跑(spec 明講「只在推送前與 CI 跑,提交前不跑」,本機完全沒有事先信號),擋下:有新筆記行待判。
3. 開發者只好照做:`prepare` → 派判定者 → 刪掉判成「推得出」的整行 → `record` → 寫出 `governance/note-verdicts/<時間>-<亂數>.json`。spec 做法第 3 節第 6 點原句:

引句:「涵蓋它們的判定檔只在工作目錄、還沒提交時,另外印提交指令」

   照這句話,開發者把「刪掉的筆記行」+「新的判定檔」提交成新的一個或多個本機提交(HEAD 前進到 SHA_B),再推。

4. `git push` 第二次:note-audit check 過了,往下跑到 `code-loop check`。code-loop check 的有效性判定走 `_codeloop_record_valid(rec_sha=SHA_A, marker_sha=SHA_B)`(`scripts/lumos:30805`),這支函式在 `scripts/lumos:30382-30389`:
   ```
   df = _sp.run(["git", "diff", "--name-only", rec_sha, marker_sha], ...)
   ...
   if df.returncode == 0 and all(f in _BOOKKEEPING_FILES or f.startswith(_BOOKKEEPING_DIRS) for f in files):
       return True, f"祖先 {rec_sha[:8]}+簿記豁免(其後 {len(files)} 檔皆簿記)"
   return False, f"記錄 sha {rec_sha[:8]} 之後動了代碼(非純簿記增量)"
   ```
   `_BOOKKEEPING_DIRS = ("governance/code-loop/", "governance/review-reports/", "governance/replay/")`(`scripts/lumos:20353`);`_BOOKKEEPING_FILES` 只列 `docs/.*-log.jsonl` 與 `governance/anchor-baseline.json`(`scripts/lumos:20340-20344`)。**這兩份清單都不含 `governance/note-verdicts/`**(spec 新開的資料夾,做法第 2 節「新資料夾」),而 SHA_A→SHA_B 之間又真的改了筆記檔本身(刪掉判成推得出的行)——筆記檔同樣不在這兩份清單裡。
   `_codeloop_record_valid` 判定「非純簿記增量」,回 `False`。`_codeloop_guard_verdict`(`scripts/lumos:30798-30818`)把它讀成「tier=high 且留痕過時:記錄 sha … 之後動了代碼」,擋下推送,要求整批重跑 `dispositions` + `code-loop pass`——即使實際被審過的程式碼一行都沒變。

**這不是「圖譜筆記本來就該讓留痕失效」的既有規則,是既有規則本身就有這個洞,這份 spec 剛好踩進去**

`_codeloop_record_valid` 只認 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS`,**沒有**像 `scripts/lumos:6237` 的小改動閘 `_bk()` 那樣多一條 `(vrel and x.startswith(vrel + "/"))`(圖譜筆記路徑豁免)。`scripts/lumos:5411` 的說明明講「哪些檔不算程式改動」的單一源是「簿記檔…+圖譜筆記」,但這條單一源沒有被 `_codeloop_record_valid` 引用——它是另一個各自維護的判準,漏了圖譜筆記那一半。這是 codebase 既有的潛在不一致,先前因為「程式、圖譜筆記放同一個提交」的紀律(CLAUDE.md 提交鐵則)幾乎不會在 code-loop pass 記錄**之後**單獨再改筆記,所以沒被踩到。這份 spec 的設計(prepare/judge/record 只能在推送前跑、且往往在 `code-loop pass` 已經記錄之後才第一次觸發)第一次系統性地製造出「pass 記錄之後、push 之前,只動筆記+新判定檔」的提交,把這個潛伏的洞變成必然路徑。

**spec 完全沒有處理這個互動**:全篇找不到 `_BOOKKEEPING_DIRS`、`_codeloop_record_valid`、`code-loop` 留痕失效等字樣;S1–S16 沒有一條測「record 寫入判定檔後,既有的 code-loop pass/skip 留痕應仍然有效」;〈回退〉第 5 點只講判定檔目錄本身可以留著不擋東西,沒提到它會不會讓別的閘的留痕跟著死。

**要補的**:至少把 `governance/note-verdicts/` 併入 `_BOOKKEEPING_DIRS`(或等價地讓 `_codeloop_record_valid` 也吃 `vrel` 豁免),並且明講「note-audit 造成的筆記行刪除」算不算簿記增量(它改的是筆記正文,不是純粹的记录檔,語意上要不要豁免需要 Enzo 裁,不是工程細節)。這條裁決目前完全沒有出現在 spec 裡。

---

## F2 判定檔的寫入語意含糊:引用的「連鎖帳本那支」寫法其實是兩支互斥的函式

severity: minor
blocking: 否 —— 不會讓現有路徑壞掉,是實作起手時就會卡住、但幾分鐘內能自己查清楚的規格缺口,不影響設計是否成立

spec 做法第 2 節:

引句:「寫法照連鎖帳本那支(整檔一次寫、拒絕捷徑)」

查證:`governance/rel-cascade/` 實際由兩支不同語意的函式寫:
- `rel_cascade_create`(`scripts/lumos:15055-15079`)★建新檔★:`os.open(..., O_WRONLY|O_CREAT|O_EXCL)`,同秒撞名就在檔名尾巴加 `-1..-99` 重試,**沒有** `O_NOFOLLOW`。
- `_ledger_append`(`scripts/lumos:15036-15054`)★對已存在的檔案追加一行★:`os.open(..., O_WRONLY|O_APPEND|O_NOFOLLOW)`,**沒有** `O_CREAT`(檔案必須已存在,否則開檔失敗),單次 `os.write` 驗滿寫、超過 4KB 直接拒絕不截斷。

spec 描述的判定檔語意是「一次判定一個新檔」(做法第 2 節:「每次 record 或 skip 寫一個新檔」),這在建檔動作上比較接近 `rel_cascade_create`(需要 O_CREAT 才能建出新檔),但 spec 括號裡強調的「拒絕捷徑」(即擋 symlink 終點)這個安全屬性只存在於 `_ledger_append` 的 `O_NOFOLLOW`,`rel_cascade_create` 並沒有這個保護;而 `_ledger_append` 又依賴檔案已存在(不能拿來建新檔)。兩支函式的 open flags 不能簡單拼在一起沿用,spec 沒有講清楚判定檔寫入器要用哪一套語意(要不要 O_EXCL 撞名重試、要不要 O_NOFOLLOW、"亂數" 要多少位元才能讓撞名機率可以忽略且不需要重試迴圈)。這件事不影響設計本身能不能成立,但會讓實作者在動手那一刻卡住,判準只有「查另一份程式」,不算規格缺口以外的功能性問題。

---

## 逐節讀完記錄(其餘皆已讀,無 finding)

- 標頭與 frontmatter(1–18 行):`lands_in: Systems/筆記內容審` 指向的節點目前確實不存在,但這是計劃節點慣用的「落點宣告」(forward-declare),不是 `[[wikilink]]`,不算壞連結。`related:` 五個連結全部核對存在:`Projects/筆記不存程式碼推得出的事_計劃.md`、`Projects/筆記形狀擋_計劃.md`、`Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md`、`Systems/筆記內容閘.md`、`Issues/治理帳多個寫入者都沒上鎖.md` 皆存在(clone-ns 的 `docs/lumos-toolchain-knowledge/`)。
- PRIOR-ART/RETIRE-IF/REVISIT(19–29 行):PRIOR-ART 提到「借第一層已上線的算法,但先把它從第一層內部抽成兩層共用的函式」——查證 `_ns_range_added`(`scripts/lumos:23579-23664`)與 `_note_shape_eval`(`scripts/lumos:23763-23859`)確認:前者只回「範圍裡每個提交加過的行文字」集合(不帶行號、加了又刪的仍在),終點版本裡還在哪一塊、第幾行是 `_note_shape_eval` 自己在迴圈裡算的(`23799-23819` 的 `for p, linenos in sorted(cand.items())` 迴圈配 `_ns_regions`)——spec 這段對現況的描述精確對得上程式碼。`Systems/外部對照-code衍生wiki.md` 存在。`RETIRE-IF`/`REVISIT` 寫齊條件與日期,符合 CLAUDE.md 鐵則 4。
- 〈判定者能不能用:小實驗〉(31–43 行):逐字核對 `governance/audits/2026-09-27-rtb-notes/judge-experiment/` 底下 `judge_key.json`(68 筆,`src` 欄 audit 55/why_chosen 13)、`judge_opus.md`、`judge_sonnet.md` 的統計行——opus「55(53 推得出、2 一半一半)」「0(9 脈絡、4 一半一半)」與 sonnet「54(漏 1 句…)」「3」兩欄數字,逐筆用 `n` 編號比對 CONTEXT/MIXED/CODE 分類與 `src` 欄位,**全部精確吻合**,包括 sonnet 漏判的那一句(n=27,對應 `judge_key.json` 裡 `"src":"audit","note_clean":"Projects/RTB_Phase13"`)確實是在講已被移除的 `renew_lease` 機制、sonnet 判成 CONTEXT 的理由也確實是「機制已整支刪除」——跟 spec 寫的「在講已刪掉的程式,它判成歷史」一字不差對得上。`judge_prompt.md` 確實把 rtb 專案路徑與「Python」寫死在句子裡(非佔位符),支持 S13 要求「換路徑」的可行性。
- 做法第 1 節(46–54 行):驗過 `_ns_range_added`/`_note_shape_eval` 現況描述準確(見上)。三處寫死看 `scripts/hooks/pre-commit` 的地方核對存在:`_nodehome_golive`(`scripts/lumos:22943-22951`)、`_nodehome_clamp_base`(`22954-22966`,內部呼叫前者)、`_ns_range_added` 裡逐提交判上線那段(`23602-23606`,`f"{c[0]}:scripts/hooks/pre-commit"`)——三處都硬編路徑字串,「三處都加參數」的說法屬實,且目前確實只有 `mark`(標記字串)可換、hook 檔案路徑不可換,跟 spec 的落差描述一致。`_NOTE_SHAPE_GOLIVE_MARK = "note-shape --staged"`(`23455`)證實「標記=子指令呼叫文字」這個既有慣例,支持「note-audit 用 `note-audit check` 當自己的標記」的設計合理。
- 做法第 2 節(56–63 行):內容編號(NFC 路徑+區塊+去空白文字)、完成審另編號、取最重只申訴能調輕——邏輯自洽;`_ns_regions`(`23500-23523`)證實區塊判定(body/summary/decisions/other)確實存在且照 `TOP_KEY_RE`/`_NS_STRUCT_KEY_RE` 算,不靠解析欄位值,跟 spec「借法寫死」的說法相符。F2 已列於上。
- 做法第 3 節 1–4 點(66–70 行):`--orchestrator claude|codex` 核對 `LOOP_ORCHESTRATORS`/`cmd_loop_next(..., orchestrator=None)`(`scripts/lumos:10813` 等)確有此慣例。`.gitignore` 疑慮已查清——不是問題:`lumos init` 確實會在 `governance/`、`docs/` 底下寫巢狀 `.gitignore`(`scripts/lumos:17339-17370`、`18190-18258`),根目錄的 `.gitignore` 才是人手維護(clone-ns 根 `.gitignore` 裡 `.lumos/test-cache*.json` 等條目找不到對應的自動寫入呼叫),所以 spec「消費專案的根 .gitignore 沒有工具會去改」以及「在 `.lumos/note-audit/` 自帶 `.gitignore`」的設計跟既有慣例(巢狀 `.gitignore`、不碰根目錄)一致,不是新花樣。`_validate_repo_ref` 核對確實拒絕絕對路徑與 `..`(`scripts/lumos:19819-19832`),S7 條款描述準確。
- 做法第 3 節 5–8 點(71–83 行):`check` 的「涵蓋它們的判定檔只在工作目錄、還沒提交時,另外印提交指令」正是 F1 觸發點,已詳述。doctor 段(83 行)沿用 `_note_shape_doctor_lines`(`23862-23935`)同款「掃 CI yml 有沒有呼叫、遠端頂端讀判定檔」模式,`.github/workflows/ci.yml` 確有 `note-shape gate` 步驟(`ci.yml:121-139`)與 `fetch-depth: 0`(`ci.yml:16`)可供比對,設計上可平行複製,無矛盾。
- 做法第 4 節(85–87 行):「推送前掛鉤全 repo 只有一份,分不出這次推送是哪一家在編排」——查 `scripts/hooks/pre-push` 的 code-loop check 呼叫段(`_rbranch`/`marker_branch` 邏輯,無 orchestrator 分流)支持這個限制描述屬實,兩家都要校準達標才能接線的設計合理對應這個限制。
- 做法第 5 節(89–93 行):`scripts/templates/graph-discipline.md` 核對:第 44 行已有 `FACT:`/`FLOW:`/`DEP:` 表格列(含 `LUMOS_SKIP_NOTE_SHAPE` 提醒),第 71/75 行已有「遇到這些情境就調用對應 skill」表且首列就是 `lumos-project-notes`——spec 說「第一層已改好」「加一列」都對得上現況,插入點明確。`skills/lumos-project-notes/commands/06-代碼審與推送.md` 已存在同款「情境→指令→結果→不用會怎樣」表格式,新子檔可以照樣式插入,可執行性沒問題(但其內容——會不會真的講清楚 Claude 與 Codex 各自怎麼派——要等實際寫出來才能驗,目前只有意圖,不算 gap)。
- 條款 S1–S16(95–112 行):逐條核對測試名與內容語意相符(S1 shared_new_lines↔抽共用函式langs、S2 hook_param_all_three_sites↔三處掛鉤參數、S3 done_plan_rejudged↔完成審另判、S4 content_ids↔內容編號含區塊、S5 prepare↔清單/gitignore/上下文、S6 provenance↔來源錨點拒絕、S7 evidence_confined↔證據關在 repo 裡、S8 heaviest_wins_dispute_only↔取最重僅申訴調輕、S9 verdict_files_concurrent_merge↔並行寫檔不衝突、S10 check_reads_tip_verdicts↔只認頂端提交、S11 modes_and_event_kinds↔開關與事件種類、S12 decision_amend_remote_rename_and_collision↔決策改名撞號、S13 prompt_rendered_for_repo↔派工詞換路徑、S14/S15 manual↔人工義務、S16 doctor_note_audit_ci_and_bypass_scan↔doctor 檢查)。沒有一條測到 F1 描述的 code-loop 留痕互動,這件事已併入 F1 陳述,不重複另開一條。
- 〈回退〉(114–121 行):五步順序(先改 CI→專案開關 off→拿掉掛鉤呼叫→共用函式不用退→判定檔留著)本身邏輯自洽,「note-audit 指令改成只印『已撤除』並回 0」跟第一層既有慣例一致(`_note_shape_config`/gate off 放行模式已有前例)。沒有發現新洞。
- 〈實務隱患〉(123–131 行):四類鏡頭(守衛面/對外送出/資源併發/可用性/容量)逐項有答;「已排除:不可逆」「已排除:金流」寫法符合 `_EXCLUDED_RE`/`_DOOR_CLASS_ZH` 認得的格式(`scripts/lumos:5411` 一帶,`已排除:<類>:<理由>`)。資源併發段「兩條分支各自寫判定檔 → 檔名不同,合併不衝突」跟 F2 提到的撞名疑慮不衝突——只要亂數位元夠,這句話仍然成立,F2 只是說規格沒寫清楚要多少位元/要不要重試。
- 〈誠實界線〉(133–141 行):第 5 點「本機新分支的起點是…CI 從空樹截到上線點、只排除主線」跟 `_ns_mainline_refs`/`_ns_exclusions`(`scripts/lumos:23560-23576`)及 `_note_shape_doctor_lines` 的 CI 步驟文字(`23885-23889`,`git fetch`+`git branch --track main`)描述的既有落差一致,誠實反映既有限制,沒有新增問題。
- 〈前身 r3 發現怎麼處理〉(143–151 行):核對卷證 `governance/review-reports/筆記不存程式碼推得出的事/r3-*` 六席報告全部存在(正確性-opus、邊界-sonnet、接手-sonnet、併發-sonnet、架構對齊-sonnet、外家否決-codex)。「駁回」那條——邊界席 F5 說〈擋什麼的初步實測〉查無此篇——查證 `Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:127` 確實只是一個粗體段落標題,不是獨立筆記,而 `〈…〉` 在本庫（含這份 spec 自己,例如「見〈做法〉第 1 節」)是通用的「段落標題引用」寫法而非 `[[wikilink]]`,駁回理由站得住,不是遺漏。

---

## 總結

檔級 severity 為 **blocker**,共 1 條 blocking(F1);另有 1 條 minor 不計入 blocking。F1 是這份重寫稿最大的洞:它把「note-audit 的判定檔提交」這個新增的必經步驟,放進了既有 `_codeloop_record_valid`(`scripts/lumos:30359-30389`)判準的死角——那支函式的簿記豁免清單沒有圖譜筆記路徑,也不包含 spec 新開的 `governance/note-verdicts/`,導致每一次「tier=high 且推送前才第一次觸發 note-audit」的正常路徑,都會讓已經做完的代碼審留痕在下一次 push 時被判成過期,逼人重跑一輪本來已經審完的審查。這正是任務要求的整合/知識同步鏡頭要抓的東西:三個月後接手的人會在這裡撞牆,而且撞的不是一次性邊角案例,是「幾乎每次 tier=high 推送」的主幹路徑。
