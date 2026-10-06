severity: major

# 提交時自動更新筆記日期 — 整合與知識同步鏡頭審查(外部審稿人,Sonnet)

審查對象:`/tmp/更新日期-r1.md`。對照 repo:`/Users/enzo/harness/lumos-d4`(唯讀;實驗都在 mktemp 臨時 repo 做,沒動 repo)。

固定席說明:派工沒有附上牽連的合約或事故節點清單。我自己查了這份設計碰到的幾篇節點(`Systems/lumos-cli-write`、`Systems/每支檔有家`、`Systems/筆記內容閘`、`Systems/cochange-guard`、`Systems/delguard`),這幾篇沒有 ★INVARIANT★ / ★IRREVERSIBLE★ / ★CHECKPOINT★ 合約行。其中 `Systems/lumos-cli-write` 有一條 KEY:「8個寫入原語...是『專案層』圖譜寫入的唯一安全路徑」,這份設計繞過它,見 F3。其餘判「不影響」的有:Gate 1 污染指紋(順序在前、且只看新增行的引號日期)、Gate 3「改程式沒動圖譜」(這道只重新加入已暫存的檔,暫存清單不變)、`home check` 的 sig 比對(不含 `updated`),原因都寫在下面各條。

## F1 指定路徑提交的判斷會把最常用的 `git commit -a` 一起跳過,而且「預設索引」沒定義怎麼比
severity: major
blocking: 是——一個常見提交形態會靜默讓整個功能失效,而驗收測試用的做法看不出來。

spec 範圍第 3 條。

引句:「`GIT_INDEX_FILE` 指的不是預設索引」

實驗(臨時 repo,pre-commit 只印 `$GIT_INDEX_FILE` 再 `git add`):

| 提交形態 | hook 看到的 GIT_INDEX_FILE | 在 hook 裡 `git add` 的結果 |
|---|---|---|
| 一般 `git commit -m`(主工作樹) | `.git/index`(**相對路徑**) | 進這次提交 |
| `git commit -a` / `-am` | `<絕對路徑>/.git/index.lock` | **也進這次提交,實測沒問題** |
| `git commit <路徑>` | `<絕對路徑>/.git/next-index-<pid>.lock` | 進提交,但真正的暫存區變 `MM`(對不上) |
| `--amend` | `.git/index` | 進提交 |
| 連結的 worktree 一般提交 | `<絕對路徑>/.git/worktrees/<名>/index`(絕對) | 進提交 |
| 連結的 worktree `-a` | 同上加 `.lock` | 進提交 |

問題:
1. 只有 `next-index-*.lock` 才真的有問題。spec 的字面規則「不是預設索引就跳過」會把 `-a` / `-am`(`index.lock`)也當成指定路徑提交跳過,印「日期沒自動改」。`-a` 實測可以安全 `git add`,不該跳。
2. 「預設索引」沒有比對辦法:主工作樹是相對路徑 `.git/index`,worktree 是絕對路徑(本專案的並行會談規矩就是一人一個 worktree);macOS 的 `/var` 與 `/private/var` 同一處兩種寫法;Windows Git Bash 的 `C:/...` 與 `/c/...` 也會對不上。用字串比對,worktree 或 Windows 上一般提交也會被誤判成指定路徑而跳過。
3. 測試對不到:既有測試的 `_nh_run_hook`(`scripts/test_lumos.py:47434` 一帶)是直接執行 hook 檔,從不設 `GIT_INDEX_FILE`。若 S4/S5 沿用這個做法,「未設」會判預設、全綠,而 `-a`、worktree、相對/絕對路徑這幾條真實分歧完全沒測到。

具體例:在 `lumos-d4-wt` 這種 worktree 用 `git commit -m` 提交一篇改過正文、`updated` 已落後的筆記 → 預期:日期改成今天;實際(若用字串比對):`GIT_INDEX_FILE` 是絕對路徑、跟 `.git/index` 對不上,判成指定路徑提交,整個跳過。

修法方向:不比整串,只認 basename 是 `next-index-*` 這種模式(或讓 `git rev-parse --git-path index` 與 `realpath` 比),`index.lock` 視為預設;S5 要用真的 `git commit` 的四種形態(一般 / `-a` / `<路徑>` / `--amend`)加 worktree 各一支,不用直接呼叫 hook。

## F2 提交時改 `updated` 會讓設計審迴圈的整檔雜湊鏈在提交後失效
severity: major
blocking: 是——跟既有的設計審流程互相打架,會逼出多餘的一輪審。

spec 範圍第 1 條與做法第 3 條(改寫暫存的筆記並重新加入)。

引句:「把工作目錄那篇的 `updated:` 行改成今天,再 `git add` 那一篇」

證據:`scripts/lumos:9147`(`_sha256_file` 讀整個檔案位元組)、`scripts/lumos:9219`(`canary record` 於折入後把整檔 sha256 記成 `result_sha256`)、`scripts/lumos:10275`、`10277`(`_hash_chain_check`:當前檔的 sha256 不等於窗末 result 就回「spec 於審計後被改動(窗末 result ≠ 當前檔),需再過一輪」)。這條鏈由 `lumos loop status <編號> --disposal` 讀(`cmd_loop_status`、`_loop_status_disposal`)。對照 `scripts/lumos:6858` `_clause_block_sha` 的註解:「整檔會被 updated: 這種維護弄成過期」——規格閘的留痕當初就是為了躲 `updated` 維護才改綁條款區塊,設計審的整檔雜湊沒躲。

具體例:計劃筆記第 1 天建立(`updated: 10-01`),第 3 天設計審跑完、折入、記帳(雜湊綁第 3 天的檔),第 3 天提交 → 掛鉤見正文與 HEAD 有差、`updated` 不是今天,改成 10-03 重新加入 → 提交進去的檔位元組變了 → 之後有人問「這個編號過關了沒」(`lumos loop status 編號 --disposal --spec …`)得到「spec 於審計後被改動,需再過一輪」。審查流程裡計劃筆記幾乎都是「先寫、隔天才提交」,這個情況不是邊角。

spec 的「實務隱患」「回退」「天花板」都沒提。要解的選項:設計審的鏈改成跟規格閘一樣剝掉 `updated:` 行再算;或掛鉤對還在審的計劃(`status: doing` 且有設計審帳)不改。兩個都要在 spec 裡明寫。

## F3 自寫「只換一行」的函式繞過既有寫入原語:沒鎖、非原子、不拒 CRLF/BOM、`git add` 整檔會帶進併發改動
severity: major
blocking: 是——這是 PRIOR-ART 漏看,而且「不會把沒暫存的改動帶進提交」這句宣稱在併發下不成立。

spec 做法第 3 條與「實務隱患」第 5 條。

引句:「改的只有 `updated:` 那一行,而且那篇工作目錄與暫存一致才改,不會把沒暫存的改動帶進提交。」

證據:
- `Systems/lumos-cli-write` 的 KEY:「8個寫入原語(set/append/...)是『專案層』圖譜寫入的唯一安全路徑」,FLOW 行寫明走 `load_raw_for_edit`(`scripts/lumos:17842`,拒 BOM 與 CRLF)→ `atomic_write_verify`(`scripts/lumos:17893`)→ `_write_lf`(唯一寫入原語)。`lumos set <節點> updated <日期>` 本來就是原語(`SCALAR_KEYS` 含 `updated`,`scripts/lumos:17534`),`edit_fm_scalar`(`scripts/lumos:17648`)已經就是「換 frontmatter 一個純量」。spec 的 PRIOR-ART 沒提這些,要「自寫一支小函式」。
- `set/append/remove` 都包在 `_vault_write_lock`(`scripts/lumos:17963`)裡做讀-改-寫,註解寫的就是「沒有鎖時,回報成功的項目會被同時跑的另一個程序蓋掉」。掛鉤的版本沒鎖:使用者全域規則明講同一 repo 可能有別的會談同時動工作目錄。

具體例(併發):會談 A 在 pre-commit 內檢查完 `git diff --quiet`(一致)→ 會談 B 對同一篇正在寫的 `lumos append` 或 Edit 落地 → A 的 hook 用舊內容讀-改-寫,蓋掉 B 的修改;或 A 的 `git add -- <檔>` 把 B 剛寫到一半的內容整份加進 A 的提交。spec 宣稱「不會把沒暫存的改動帶進提交」只在沒有併發時成立。

修法方向:算出改好的位元組後,用 `git hash-object -w` + `git update-index --cacheinfo` 把「暫存版本加上改後的 updated」直接寫進索引(不碰工作目錄的別人的改動),工作目錄只在「工作目錄 == 暫存」時才同步寫;寫入走 `_vault_write_lock` 與 `_write_lf`。CRLF/BOM 的檔:既有原語會拒,掛鉤應照樣當「跳過並印一句」,不要自己另一套行為(見 F4)。

## F4 Windows Git Bash:autocrlf 會讓「正文有差」誤判成立,CRLF 檔的行尾與讀寫模式沒定義
severity: major
blocking: 是——消費專案有 Windows 使用者(本 repo 有 `get.ps1`、`slim/WINDOWS-NOTES.md`),Git for Windows 預設就是 `core.autocrlf=true`。

spec 做法第 2 條與第 3 條。

引句:「暫存版本用 `_nodehome_reader`(索引與磁碟相同直接讀磁碟),HEAD 版本用 `_nodehome_cat_blobs` 一次讀完」

證據:`_nodehome_reader`(`scripts/lumos:27409`)對「`git diff --name-only` 認為沒變」的路徑直接讀**磁碟位元組**。autocrlf 下 git 把 CRLF 正規化後比對,所以磁碟是 CRLF、索引是 LF 的筆記不在 differ 集合裡,讀到的是帶 `\r` 的位元組;HEAD 版本是 LF blob。spec 沒說正文要怎麼比。現成的 `_nodehome_parse_note`(`scripts/lumos:27531`)是逐行 `rstrip()` 再比,但 spec 沒指它;若照字面「正文有差」直接比位元組,每篇 CRLF 的筆記都會被判「正文有差」。

具體例:Windows、autocrlf=true,使用者只改了 `status`(開頭欄位)提交 → 預期:S2 不動;實際:磁碟 CRLF 對 HEAD LF,正文「不一樣」,`updated` 被改成今天。

另外:
- 既有寫入原語對 CRLF 檔一律擋(`load_raw_for_edit` 的訊息直接講「Windows 上常是 git autocrlf 造成的」);掛鉤對 CRLF 檔的行為 spec 沒定義:是跳過?是照改但保留 `\r`?「其他位元組不動」那句沒說。
- Python 在 Windows 用文字模式寫會把 `\n` 變 `\r\n`(CRLF 的檔寫出 `\r\r\n`);spec 沒規定用位元組模式。
- BOM:`split_frontmatter` 遇到 BOM 開頭回 `None`,掛鉤靜默跳過,使用者不知道為什麼日期沒改;spec 的跳過清單沒列、也沒說印不印。

## F5 UB 與 home check 對「筆記改過了」的定義不同;而且 RETIRE-IF 的量法永遠過不了
severity: major
blocking: 是——撤除條件寫成了不可能達標的量法,三個月後接手的人會得到錯的結論。

spec 範圍第 1 條與 RETIRE-IF。

引句:「正文(開頭欄位之後)或 `summary` 欄位有差,而且暫存版本的 `updated` 不是今天」

引句:「抽 20 篇最近三個月改過的筆記,`updated` 落後 git 實際改動日期的仍超過 2 篇」

證據:
- `_nodehome_parse_note`(`scripts/lumos:27531`)的 `sig` 是(摘要、**解析後的決策**、正文),另有 `sig_t`(先拿掉 `[test:]` / `[test-gone:]` 綁定);`home check` 判「有沒有寫說明」用這個,而且「只換測試綁定不算寫說明」(`_nodehome_tag_only_change`,`scripts/lumos:27490`)。UB 的定義是(摘要、正文),少了決策、又沒有 tag 豁免。
- `decision-add` 與 `append about_code` 與 `set responsibility` 都不動 `updated`(只有 `decision-supersede` 會連帶改,`scripts/lumos:18607` 到 `18615`)。這些恰恰是最載重的筆記變動,UB 不處理,`updated` 照舊落後。

具體例:
1. 一篇 Systems 只用 `lumos decision-add` 加一條決策後提交 → `home check` 認定這篇「內容有變」,UB 認定「正文與摘要沒差」不動,`updated` 落後;三個月後 RETIRE-IF 抽樣時,這篇算「`updated` 落後 git 實際改動日期」。
2. 只改 `status`(例如 doing 改 done)的提交,UB 刻意不動 `updated`,但 git 實際改動日期是那天 → 也算落後。

所以:只要正常運作,存量裡的 `status` 翻轉、決策新增、`about_code` 變動這三類都會讓抽樣的落後數量永遠壓不到 2 篇以下,撤除條件第一句會被誤觸發「掛鉤沒在跑」。要嘛量法改成「抽樣時只算正文或摘要被改過那次提交」,要嘛把決策與 `about_code` 納入 UB 的「改過」定義,與 `sig` 一致。

另外 tag 豁免:一次把大量筆記的 `[test:舊名]` 換成新名(測試改名掃描,本專案常見)提交時,`home check` 說這不算寫說明,UB 卻會把每篇的 `updated` 全部改成今天,`updated` 變成「碰過」而不是「改過說明」。

## F6 `updated` 的消費者假設它是「人確認過內容」,機械改動會讓三個既有判定變遲鈍
severity: minor
blocking: 否——現況手改也有同樣性質,這條是量級改變,不是新增壞掉的行為。

spec 沒提「updated 還有誰在讀」。

證據(都讀 `updated` 欄當時間錨):
- doctor Check S:`self_audit` 日期早於 `updated` 就算過期(`scripts/lumos:2095` 到 `2102`)——這條會因自動改日期而更常觸發,是對的方向,但存量筆記一次提交就多一筆 `check-s warned` 事件。
- E2 傳播(`scripts/lumos:2531`):鄰居的 `updated` 早於翻案的 `ended` 才標「落後」。任何一次無關的錯字修正被自動改成今天,這個鄰居就從 E2 名單消失,但它沒有因為這次翻案被複核。
- 計劃結案鏈(`scripts/lumos:1843` 到 `1847`):`status` 是 done 的計劃,`updated` 晚於驗證日期就不報「結案後有較新驗證」;計劃筆記因為改錯字被自動延後 `updated`,這條提醒被吃掉。

具體例:`Projects/X_計劃`(`status: done`,`updated: 10-01`)有一篇 10-05 的驗證指向它 → 本來報「結案後有較新驗證」;10-06 有人改了計劃正文的一個錯字提交 → `updated` 變 10-06,提醒消失,驗證仍沒被計劃吸收。

spec 要寫一句:`updated` 的語意從「作者確認過」變成「機械認為有動過」,這三處已知讀者的行為怎麼處理(接受、或改讀別的欄位)。

## F7 純改名、第一個提交、`--amend` 的基準版本
severity: minor
blocking: 否——不會壞東西,只會多寫幾個日期。

spec 範圍第 1 條。

引句:「HEAD 沒有的(新檔、改名過來的)一律照同一規則。」

問題:
1. `--no-renames` 下純改名(`git mv`,內容一位元組沒動,例如 `graph-rename.sh` 批次改名)在暫存清單是「新增」,HEAD 沒有該路徑 → 照字面「一律照同一規則」,正文與「沒有」比,必然有差 → 全部被改日期。S6 只測了「改名又改了正文」,沒有測「純改名不動」。
2. 專案第一個提交(`chore: 建立專案骨架`,見使用者專案規則)沒有 HEAD:spec 的 HEAD 版本讀取在空倉庫怎麼辦沒說(`_lens_full_sha(root,"HEAD")` 會回 None,`_nodehome_cat_blobs` 的輸入要先處理)。
3. `--amend`:spec 寫「HEAD 是被修改的那個提交,照同一規則」。但 amend 真正要提交的淨改動是對 `HEAD^`。例:第一個提交用 `--no-verify` 進了改過的正文、`updated` 沒改;amend 時沒碰那篇 → 暫存版與 HEAD 一樣 → UB 判「沒差」跳過,`updated` 永遠沒補。

## F8 判「進行中」的狀態檔位置寫死 `.git/` 會在 worktree 與子模組裡判錯
severity: minor
blocking: 否——判錯方向是多改一次日期,不擋提交。

spec 範圍第 3 條。

引句:「`rebase-merge`/`rebase-apply` 資料夾、SQUASH_MSG 任一」

問題:這些檔案住在每個工作樹自己的 git 目錄(連結的 worktree 是 `.git/worktrees/<名>/`,子模組的 `.git` 是檔案不是目錄)。spec 只說「照 note-shape 的 `rev-parse -q --verify MERGE_HEAD`」,後面幾個沒寫怎麼找。用 `root/.git/rebase-merge` 在 worktree 裡永遠不存在,rebase 進行中不會跳過。要用 `git rev-parse --git-path <名>`。測試 S4 要在 worktree 裡也跑一組。

## F9 沒寫治理帳:單次跳過不留帳,跟鄰居不一致,RETIRE-IF 沒資料可量
severity: minor
blocking: 否——功能不壞,但三個月後沒法判斷它有沒有在跑。

spec 範圍第 3 條「LUMOS_SKIP_UPDATED_BUMP=1(只認 1)」。

證據:鄰居的單次跳過都記帳(`LUMOS_SKIP_NOTE_SHAPE` 記 `skipped-env`,`scripts/lumos:30778`;`LUMOS_SKIP_NOTE_AUDIT`、`LUMOS_SKIP_REREAD_CHECK`、`LUMOS_SKIP_DRIFT_CHECK` 同);`CLAUDE.md` 對 note-shape 寫「誤擋用 ... 單次跳過、會留帳」。若 UB 也要記帳,新閘名要登記進 `_KNOWN_GATES`(`t_gov_stats_gate_drift` 掃字面值,`scripts/test_lumos.py:6537`),是否進本機帳白名單 `_GOV_LOCAL_PAIRS`(`scripts/lumos:1317` 起)也要決定,否則「每次提交一筆帳」正是 rtb 回饋抱怨過的雜訊。spec 兩邊都沒表態:不記就沒辦法回頭看「被跳過幾次、部分暫存擋了幾次」;記就要寫登記與分流。

## F10 版本錯位的雜訊、效能量法、家與說明落點
severity: minor
blocking: 否

1. 版本錯位:消費專案 `lumos update` 用 `copy2` 逐檔複製 hook 與 `scripts/lumos`(`scripts/lumos:21090`)。新 hook 配舊 `scripts/lumos` 時 `lumos updated-bump` 回 rc=2(我用 python3.14 實測:印「擋下:沒有『updated-bump』這個指令。是不是想打這個:lumos update」)。rc=2 被放行是對的,但每次提交都會在 stderr 印一段,還建議使用者去跑 `lumos update`;spec 回退節只說「要 `lumos update` 才拿到新掛鉤」,沒提這個過渡期。可以在 hook 裡先確認子指令存在再叫。
2. 效能:做法每篇一次 `git diff --quiet`、一次 `git add`。Windows Git Bash 起一個 git 行程常以十分之一秒計,100 篇逐篇叫約 20 秒,REVISIT 的門檻是 5 秒;`_nodehome_reader` 已經一次算出「工作目錄跟索引不同的路徑集合」,可以直接拿它判部分暫存、最後一次 `git add`(或 `update-index`)一批。
3. 家:`lands_in` 只寫 `Systems/lumos-cli-write`,但這個變動同時改 `scripts/hooks/pre-commit`,它的家有四篇(`Systems/每支檔有家`、`Systems/cochange-guard`、`Systems/delguard`、`Systems/筆記內容閘`)。依專案鐵則 5「改了程式要寫說明就寫進改到那支檔的家」,Gate H 在這次提交就會看。我沒有跑 `home check` 驗它擋或只提醒 ⚠(判不準),spec 要把 hook 的說明落在其中一篇(`Systems/筆記內容閘` 已管 note-shape 的 hook 段,最近)。
4. 測試:既有跑真 pre-commit 的測試約 30 處引用(`scripts/test_lumos.py` 內 `hooks/pre-commit`),夾具筆記常帶舊的 `updated:`(全檔 56 處 `updated: 20…`)。這些夾具若改了正文再走真掛鉤,位元組會被改寫、可能改變斷言;spec 沒提要檢視哪幾支。
5. slim 版 hook(`slim/hooks/pre-commit`)已凍結(`slim/FROZEN.md`),不用同步;spec 沒明講「不動 slim」,建議補一句。

## 各節結論

- frontmatter 與白話、依據、PRIOR-ART、RETIRE-IF:已讀。PRIOR-ART 漏看寫入原語,見 F3;RETIRE-IF 量法有問題,見 F5。`related` 的 `[[Projects/交接2026-10-03_計劃]]` 與 `lands_in` 的 `Systems/lumos-cli-write` 目標都存在。
- 範圍:F1、F5、F7、F8、F9。「做」第 4 條 Gate UB 放在 Gate PY 後、Gate L 前:已核對。上下游互動:
  - Gate 1 污染指紋在 UB 之前,只看新增行的引號日期;UB 寫的是不帶引號的日期,不互相影響。
  - Gate L(`lumos lint`)在 UB 之後讀的是改後的檔,`updated` 仍是合法日期;不影響。
  - Gate H(`home check`)的比對 sig 不含 `updated`(`scripts/lumos:27531`),所以 UB 改日期不會讓 home check 多算或少算「寫了說明」;「只換測試綁定不算寫說明」的判定同樣不看 `updated`,不受影響。兩者定義不同的問題見 F5。
  - Gate NS(`note-shape`):行屬哪一塊由 `_notelines_regions` 判,`updated:` 是其他欄、不在摘要與正文,不會被當成新寫的行(讀的也是索引)。不影響。
  - Gate 3「改程式沒動圖譜」:UB 只重新加入已在暫存清單的檔,`$STAGED` 與有無圖譜筆記不變;只改程式碼的提交 UB 無事可做,Gate 3 照擋。不影響。
  - `decision-supersede` 已經自己連帶改 `updated`(`scripts/lumos:18607`),UB 見到已是今天就跳過,不打架;`lumos set <節點> updated <別的日期>` 手設舊日期在改了正文的提交裡會被覆蓋成今天,spec 沒說這是設計(只能用跳過環境變數)。
- 做法:F3、F4、F7。步驟 5「掛鉤開頭算好的暫存檔名清單不會因此過期」:已核對成立(`STAGED` 在 `scripts/hooks/pre-commit:43` 算好,Gate 之間不重算,UB 只重新加入清單內已有的檔)。
- 實務隱患:對照風險類逐類——金流、對外送出、不可逆:spec 的「已排除」成立(只改要提交的筆記、無網路)。併發與共用工作目錄:不成立,見 F3。跨平台(Windows):不成立,見 F4、F1。版本錯位:見 F10。資安:無——不執行筆記內容、不拼 shell 字串(檔名走 `-z` 與 `--` 傳參),無新輸入面。守衛面:新增一道會擋的閘(部分暫存),跳過環境變數有,但不留帳,見 F9。
- 驗收條款:S1 到 S6 已讀。缺:S5 要覆蓋真的 `git commit` 四形態加 worktree(F1);缺少「純改名不動」(F7)、「CRLF 檔」(F4)、「只改決策」(F5)、「worktree 裡的 rebase 進行中」(F8)的條款。S6 排在 S5 前面只是順序,不算問題。
- 回退、天花板:已讀。回退節沒提過渡期與 F2(退回掛鉤後已被改過的 `updated` 不會還原,這點可接受);天花板第 1 條漏列「`-a` 被誤跳過」(F1 修好後就不用列)。

最嚴重 severity:major,blocking 5 條(F1、F2、F3、F4、F5)。
