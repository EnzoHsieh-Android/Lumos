severity: major

# 代碼審 r1 資安-opus(回頭重讀守檔筆記)

實驗都在 `hcc-r1-work-資安-opus/` 底下另建的小 repo 裡跑(建法:`mk.py` 造 docs/kg-knowledge 圖譜、src/a.py 與 src/b.py 兩支程式、Systems/A 與 Systems/B 兩篇家筆記、推送前掛鉤裡放上線標記),工具用 clone 裡 94e28375 的 `scripts/lumos`,以 `/opt/homebrew/bin/python3` 執行。

## F1 攻擊者提交一個符號連結 `.lumos/note-audit`,受害者照提醒貼上 reread-prepare 就會刪掉 repo 外面的 .md 檔
severity: major
blocking: 是
引句:「wd = _note_audit_work_dir(root)」
file: `scripts/lumos:26386`(`_note_audit_work_dir`:mkdir、寫 `.gitignore`、把 `*.md` 裡超過 14 天的全刪,整段都沒有擋符號連結、也沒檢查路徑還在 repo 裡)
file: `scripts/lumos:28689`(同一份程式別處已經有「解析後必須在 repo 根底下」的守衛 `fp.resolve().is_relative_to(rootp.resolve())`,這裡沒有照做)

1. `.lumos/` 是提交進版控的資料夾(`.lumos/config.json` 就在裡面),所以協作者或惡意 PR 可以在裡面提交一個符號連結 `.lumos/note-audit -> <任意絕對路徑>`。git 會照樣把它 checkout 成連結。
2. `cmd_note_audit_reread_prepare` 只要有一篇候選(攻擊者自己在 PR 裡改一支程式、同時改它的家筆記就有),就會呼叫 `_note_audit_work_dir(root)`。這支函式會順著連結跑到目標資料夾:沒有 `.gitignore` 就寫一個 `*` 進去,再**把目標資料夾裡 mtime 超過 14 天的所有 `*.md` 刪掉**,然後把項目檔寫進去。
3. 新的推送前掛鉤與 CI 在每次有候選的推送都會印出這條 `lumos note-audit reread-prepare …` 要人(或編排的 AI)照貼。筆記內容審的 `prepare` 雖然也走同一支函式,但照技能說明它「目前還沒接線」;這次改動是第一條會在日常推送裡把人帶去跑它的路。
4. 重現(攻擊者提交連結 → 受害者跑提醒 → 照貼 prepare):
   ```
   V=$W/victim-notes; echo "我的私人筆記" > $V/diary.md; echo "另一篇" > $V/todo.md
   touch -t 202608010000 $V/diary.md $V/todo.md; echo "新的" > $V/fresh.md
   ln -s $V $R/.lumos/note-audit          # 連同改 src/a.py 與 Systems/A.md 一起提交
   git -C $R ls-tree -r $TIP .lumos
   120000 blob 32609d61…	.lumos/note-audit
   == before
   -rw-r--r--  19 Aug  1 00:00 diary.md
   -rw-r--r--   7 Oct  1 01:00 fresh.md
   -rw-r--r--  10 Aug  1 00:00 todo.md
   $ lumos note-audit reread-check …   → 印出「lumos note-audit reread-prepare --diff c3b08100…..53e2bee1… --orchestrator <claude 或 codex>」
   $ lumos note-audit reread-prepare --diff c3b08100…..53e2bee1… --orchestrator claude
   這次要回頭重讀 1 篇守檔筆記…
   rc=0
   == after
   -rw-r--r--   2 Oct  1 01:00 .gitignore        (內容是 *)
   -rw-r--r--   7 Oct  1 01:00 fresh.md
   -rw-r--r-- 2797 Oct  1 01:00 reread-d746e71728472f03-claude.md
   ```
   repo 外的 `diary.md`、`todo.md` 被刪掉,拿不回來。如果連結改指向 repo 裡的 `../docs/<圖譜>/Systems`,就會把 checkout 超過 14 天的筆記刪掉,還寫進一個 `*` 的 `.gitignore`,之後新增的筆記 `git add` 時會被靜默略過。
5. 根源在既有的 helper,但這次改動多了一個呼叫點,也多了一條提醒把人帶去跑它,所以算在這次的範圍裡。修法:`_note_audit_work_dir` 在 `.lumos` 或 `.lumos/note-audit` 是符號連結、或 resolve 後跑出 repo 根時拒絕(照 28689 那種寫法);清理只刪自己命名規則的檔(`reread-*.md` 與清單檔),而且要跳過符號連結。

## F2 筆記檔名裡的控制字元與換行沒清就印出來、也寫進項目檔頭:終端逃逸碼可以注入,項目檔的欄位也能被蓋掉(記了 E 就讓 B 算成已對照)
severity: minor
blocking: 否
引句:「f"筆記路徑: {show(note_full)}"」
file: `scripts/lumos:23689`(`_nodehome_show` 只換掉非 UTF-8 的位元組,不處理控制字元)
file: `scripts/lumos:9785`(`_esc_clean` 就是專門處理這件事的;reread-check 有用它,reread-prepare 沒用)

1. 終端注入:reread-prepare 用 `print(f"  {_nodehome_show(rel)}\n    項目檔:{f}")` 原樣印出筆記路徑(stderr 那行 `{_nodehome_show(rel)}:{why}` 也一樣)。git 檔名可以帶 ESC、BEL。重現:提交一篇 `Systems/E\x1b[31mRED\x1b[0m\x1b]0;PWNED-TITLE\x07.md`(about_code 寫 src/a.py),再跑 prepare 並用 `cat -v` 看輸出:
   ```
     Systems/E^[[31mRED^[[0m^[]0;PWNED-TITLE^G.md
   ```
   逃逸碼原樣送到終端(OSC 0 會改掉視窗標題;在允許 OSC 52 的終端,同一招可以改寫剪貼簿,而這個工具本來就是叫人複製貼上指令)。同一個 repo 跑 reread-check,印出來的是 `E [31mRED [0m ]0;PWNED-TITLE .md`,有清乾淨,所以兩個子指令的處理不一致。
2. 項目檔頭的欄位被蓋掉:`_note_reread_parse_item` 用 `dict(re.findall(^(欄位): (.+)$, re.M))` 解析檔頭,同名欄位後出現的會蓋掉前面的。檔頭裡「筆記路徑」排在「對照指紋」之後,所以檔名帶換行就能把對照指紋換成別篇的。重現:受害者這次改了 src/b.py 與 B.md(B 的對照指紋 c85e4152189bdb0e);攻擊者在同一段範圍裡提交 `Systems/E\n對照指紋: c85e4152189bdb0e\nZ.md`。prepare 產出的 E 項目檔頭:
   ```
   7:對照指紋: 385012b6512d9f32
   8:筆記路徑: docs/kg-knowledge/Systems/E
   9:對照指紋: c85e4152189bdb0e
   ```
   只 record E 那一份(報告給 `[]`),寫出來的紀錄檔名是 `c85e4152189bdb0e-…json`。提交之後跑 check,變成「有 1 篇…還沒對照(已對照 1 篇)」,只剩 E 被列出來。**B 沒有任何判定者讀過,卻被算成已對照了**。
3. 因為這道只提醒、不擋,影響只是提醒被抹掉、終端被干擾,所以定 minor。修法:印出時一律過 `_esc_clean`;寫進項目檔頭與派工詞的路徑要把控制字元與換行換掉(或整個拒收這種檔名的候選);解析檔頭時同名欄位重複就整份拒收。

## F3 `governance/reread-verdicts` 如果是提交進來的符號連結,reread-record 會把紀錄寫到 repo 外面
severity: minor
blocking: 否
引句:「d = Path(root) / _NOTE_REREAD_VERDICT_DIR」
file: `scripts/lumos:26376`(筆記內容審的 `_note_audit_write_verdict` 也是同一種寫法,同族)

1. 攻擊者提交 `governance/reread-verdicts -> ../../outside`(ls-tree 看到的是 `120000 blob … governance/reread-verdicts`)。受害者照流程跑 reread-record 時,`d.mkdir(parents=True, exist_ok=True)` 碰到指向資料夾的連結不會報錯,`_write_lf(d / name, …)` 就順著連結寫出去:
   ```
   寫了紀錄 governance/reread-verdicts/25750e0c3f7a2fa8-20260930T170018Z-2d734ad3….json:docs/kg-knowledge/Systems/A.md 點出 0 行
   == outside dir (outside repo):
   -rw-r--r--  416 Oct  1 01:00 25750e0c3f7a2fa8-20260930T170018Z-2d734ad3b4a445598a361e20dc78c698.json
   ```
2. 檔名是亂數,不會蓋掉既有檔;內容是 JSON,其中一部分由報告決定。所以危害只是「在任意資料夾多一個 .json」,另外受害者的紀錄其實沒進版控、提醒也消不掉。定 minor。修法:跟 F1 一起加「不是符號連結、resolve 後還在 repo 根底下」的守衛,筆記內容審那支一起改。

## F4 新加的簿記豁免資料夾是「路徑前綴、不看內容」:代碼審留痕之後,把程式檔改名搬進去,留痕照樣有效
severity: minor
blocking: 否
引句:「"governance/reread-verdicts/")」
file: `scripts/lumos:37822`(`_codeloop_record_valid`:`git diff --name-only rec_sha marker_sha` 沒關改名偵測,改名只會列出新路徑)

1. 重現:在留痕 sha 之後提交 `git mv src/auth.py governance/reread-verdicts/auth.json`(src/auth.py 是權限守衛):
   ```
   git diff --name-only $PASS $T1
   governance/reread-verdicts/auth.json
   _codeloop_record_valid(R, PASS, T1) → (True, '祖先 221e9a0a+簿記豁免(其後 1 檔皆簿記)')
   ```
   守衛程式在審過之後被刪掉(改名搬走),留痕仍然判有效。
2. 同一招搬進既有的 `governance/replay/` 也成立(實測同樣回 `(True, …簿記豁免…)`),所以這是既有的同族問題,這次只是多開了一個入口;小改動閘那邊已經寫了「從程式目錄搬進卷證目錄的不豁免」,代碼審留痕這一支沒跟上。定 minor。修法:判有效性時改用 `--name-status --no-renames`(或 `-M` 之後把改名的舊路徑也拿去檢查),舊路徑不是簿記就判失效;也可以把 reread-verdicts 的豁免收窄到符合 `_NOTE_REREAD_VERDICT_NAME_RE` 的 .json 檔名。

## 查過、沒有洞的部分(不算 finding)
- 指令注入:掛鉤用陣列帶參數;CI 的 BEFORE、SHA、GITHUB_REF、DEFAULT_BRANCH 都走環境變數、有加引號;`_note_reread_cmdline` 用了 shlex.quote;git 呼叫都是 argv,pathspec 帶了 `--literal-pathspecs`。
- 寫檔路徑:項目檔名是十六進位指紋加上固定選項的編排者;紀錄檔名的對照指紋先過 `[0-9a-f]{16}` 全字比對;筆記 blob 與範圍終點也驗過 sha 格式。
- reread-record 印出的報告欄位(seat、provider、model、prepared、quote、why)都經過 `_esc_clean`;dropped 用的是 repr。
- 掛鉤回傳碼:只有 130 會停下,其他都放行;標準錯誤丟掉不影響別道閘。上線標記 `note-audit reread-check` 不含筆記內容審的 `note-audit check` 這串,掛鉤與 CI 裡這兩串的次數實測都是 0。
- 未能重現、不列 finding:Codex 派法字面寫 `"<項目檔內容>"` 夾在雙引號裡。如果編排者真的把內容直接貼進 shell,diff 或筆記裡的 `$(…)` 就會被執行;但這要看編排 AI 怎麼組指令,在 clone 裡跑不出來。建議改寫成 `"$(cat <項目檔>)"`,或用 stdin 餵進去。

最高等級:major
