severity: major

已讀程式與計劃全文。實驗只做一個:確認 `filter.clean` 在 `-c core.fsmonitor=false` 下仍會執行。實驗目錄已刪。

## Finding 1:被拒時「仍用會談目錄取角色卡」做不到,做得到的版本會帶出錯的內容
severity: major
blocking: 是 — 做法 4 禁止退回會談目錄算,可是 lumos 沒有「只算角色卡、不算圖譜」的入口。照字面實作,錯樹的內容會被附上卻不講。
引句:「但仍用會談目錄叫一次 lumos 只取角色卡與架構段」
問題:
- `cmd_dispatch_lens` 帶 `role_cards` 時,角色段與架構段都由 `diff_range` 在 `repo` 解析出的樹算出,算完一定接著跑 `_dispatch_lens_graph`。
- 計劃的 lumos 端改動清單(三個 spec 代碼、`_lens_git` 的保險)沒有「跳過圖譜段」的旗標。
- `_dispatch_lens_role_text` 與 `_dispatch_lens_arch_text` 對 `diff_range` 解析不到時回空字串,所以 S8 要的角色卡不會出現。
失敗情境:
- 輸入:`LUMOS-IMPACT: main..HEAD`、`LUMOS-ROLE-CARDS: on`、`LUMOS-REPO: /不在登記的路徑`。
- 結果一:`main..HEAD` 在會談 repo 解得出來,角色卡與目標架構段就是會談 repo 那條分支的內容,被當成目標 repo 的審查材料附上。
- 結果二:圖譜段 rc0,會談樹的牽連節點整段併進 `text`,正好是計劃禁止的退回會談目錄。
- 結果三:範圍是完整 sha 時在會談 repo 找不到,角色卡是空的,S8 的測試與預期不符。
- 建議:lumos 加獨立模式(例如 `--cards-only`,不跑圖譜、範圍不在會談 repo 時不附任何東西),或被拒時一律不附卡並明講。
佐證:``file: `scripts/lumos:48640-48700` ``(`_cmd_dispatch_lens_impl`)、``file: `scripts/lumos:48734-48750` ``(`_dispatch_lens_role_text`)。

## Finding 2:只有 `LUMOS-REPO:` 會略過圍欄與引用行,圍欄裡的標記被靜默忽略後退回會談目錄
severity: major
blocking: 是 — 會把「錯 repo 的節點不說明」帶回來,而且做法 1 的「寫歪也不退回」沒有涵蓋這一格。
引句:「派工詞常貼進計劃或範本全文,裡面的範例行不算」
問題:
- 現有的 `find_marker`、`find_spec_marker`、`wants_role_cards` 對每一行 `strip()` 後比對,圍欄、引用裡的行照樣算。
- 新規則只對 `LUMOS-REPO:` 略過圍欄與 `>` 行,而且略過不報,不算 `repo_malformed`。
- 計劃沒定義圍欄語法:`~~~`、四個反引號、縮排程式碼區塊、沒收尾的圍欄,各是什麼處理。
失敗情境:
- 輸入:編排者把整段派工範本貼成圍欄塊,或前面有一個沒收尾的 ``` 夾帶 diff 片段,圍欄裡有 `LUMOS-IMPACT: abc..def` 和 `LUMOS-REPO: /wt2`。
- 結果:`LUMOS-IMPACT` 照常生效,`LUMOS-REPO` 被當成沒寫。
- 後果:範圍在會談目錄算。若範圍是 `main..HEAD`,會算出另一個 repo 的牽連節點,成功時沒有來源行以外的警示;這正是計劃要消滅的 2026-10-14 那一晚的失敗。
- 建議:
  - 兩個標記用同一套比對規則。
  - 或只要有任何一行含 `LUMOS-REPO`(圍欄裡的也算)而最後沒生效,就一律附說明行,不退回會談目錄。
佐證:``file: `scripts/hooks/claude/dispatch-lens-hook.py:165-180` ``、``file: `scripts/hooks/claude/dispatch-lens-hook.py:274-279` ``。

## Finding 3:被拒時的說明教人跑 `lumos update`,審查材料可以用它誘導編排者把惡意 repo 登記進去
severity: major
blocking: 是 — 登記制是整份設計唯一的信任閘,而閘的「開門」動作被寫進了每一則拒絕說明。
引句:「說明行附一句怎麼登記」
問題:
- 派工詞的 `LUMOS-REPO:` 值(攻擊者可控)被拒時,說明行把路徑(只經消毒)連同「在那個專案跑一次 `lumos update`」放進子代理與編排者讀得到的文字。
- `cmd_update` 與 `cmd_init` 不問這個目錄是誰的:只要 cwd 底下有 `docs/*-knowledge` 目錄,`find_vault` 就找得到,登記就發生。
- 計劃沒寫「只在成功時登記」,沒寫「`--dry-run` 不登記」,也沒寫 `install.sh` 登記哪個專案。`install.sh` 本身沒有專案的概念,實作者會登記 cwd。
- `update` 自己還會在該目錄跑 git(`cmd_init` 的 `git rev-parse --show-toplevel` 就是在 cwd 跑)並把 hooks 裝進去。
失敗情境:
- 輸入:被審的材料(下載來的 repo 或 PR 描述)寫 `LUMOS-REPO: /Users/x/evil`。
- 流程:掛鉤附「未登記,請在該專案跑一次 lumos update」,編排者或審查席照做,`/Users/x/evil` 進入 `projects.txt`。
- 結果:之後該路徑的任何 `LUMOS-REPO:` 都通過,lumos 在 evil repo 跑 git(`core.fsmonitor` 擋住了,但見 Finding 5)。
- 建議:
  - 說明只講「請使用者確認後自行登記」,不給可被機器照抄的指令。
  - 登記改成獨立指令(例如 `lumos trust`),拿掉 `update`、`init` 的副作用。
  - 至少 `--dry-run` 與失敗時不登記,並規定 `install.sh` 登記什麼。
佐證:``file: `scripts/lumos:24307-24335` ``(`cmd_update` 以 `find_vault(cwd)` 決定專案)、``file: `scripts/lumos:25631-25650` ``(`cmd_init`)。

## Finding 4:會談目錄本身是連結工作樹時,工作樹清單沒有算法
severity: major
blocking: 是 — 這是計劃要解決的主場景(三個工作樹),規格沒覆蓋,S1 的測試很可能只從主工作樹出發。
引句:「會談 repo 的 git 共用資料夾底下 `worktrees/*/gitdir` 檔」
問題:
- `_events_main_trusted` 把 `main_root / ".git" / "worktrees"` 寫死,`main_root` 由呼叫端先算好(`_events_root`,用 git)。
- 計劃同時要求「不在目標路徑跑任何 git」又沒說會談目錄是連結工作樹時怎麼找共用 git 資料夾:`<會談>/.git` 是檔案,要讀 `gitdir:` 再讀 `commondir`。
- 「主工作樹本身」靠 `commondir` 的上一層推,遇到 `--separate-git-dir`、裸 repo 加工作樹會推錯。
- `worktrees/*/gitdir` 只比對單向。已刪除但沒 prune 的條目,路徑被別的 repo 佔用後仍會對上,計劃沒要求檢查 `<工作樹>/.git` 是檔案、而且 `gitdir:` 指回同一條目。
失敗情境:
- 輸入:會談開在 `/wt/a`(連結工作樹),`LUMOS-REPO: /wt/b`(同 repo 的另一個工作樹)。
- 結果:照字面讀 `/wt/a/.git/worktrees` 不存在,清單是空的,合法工作樹全被拒為 `repo_not_registered`。實作者很可能因此改成跑 git,破壞「一次 git 都不跑」。
- 若讓 `/wt/b/.git` 被換成獨立 repo 目錄(條目沒 prune),`/wt/b` 照樣通過,並用那個 repo 自己的 config 跑 git。
佐證:``file: `scripts/lumos:27051-27068` ``(`_events_main_trusted`)。

## Finding 5:`-c core.fsmonitor=false` 擋不住別的會執行指令的設定,計劃的說法偏滿
severity: minor
blocking: 否 — 只對已登記的專案才有影響;但配合 Finding 3 的誘導登記,這一條會被連起來用。
引句:「即使登記清單裡的專案設定被改,讀取時也不會因此執行指令」
問題:
- 實測:`filter.x.clean` 加上 `.gitattributes` 的 `* filter=x`,在 `git -c core.fsmonitor=false diff HEAD --name-only` 下仍會執行(產生了 PWNED 檔)。
- 派工鏡頭路徑上有幾處直接用 `subprocess.run(["git", ...])`,不經 `_lens_git`:`_git_commit_exists`、`_codeloop_git_branch`。所以「一律帶 `-c`」不成立。
- 這幾處是 `rev-parse` 與 `cat-file`,不讀 index,實際不觸發 fsmonitor 或 filter。但說「讀取時不會執行指令」是過強的宣稱。
- 派工鏡頭本身用到的 `rev-parse`、`merge-base`、`ls-tree`、`show <ref>:<path>`、range 內的 `diff` 都不跑 clean filter,現況沒有已知的觸發點。
- 建議:把宣稱改成「目前已知只有 fsmonitor 會被 index 類指令觸發,派工鏡頭路徑上沒有 index 類指令」,並加一條守衛測試:派工路徑不得出現 `diff HEAD` 或 `status`。
佐證:``file: `scripts/lumos:6221-6229` ``、``file: `scripts/lumos:47129-47135` ``、``file: `scripts/lumos:47386-47397` ``(`_lens_git`)。

## Finding 6:登記清單不會過期,同一路徑換了內容仍受信任
severity: minor
blocking: 否 — 屬於做法 2 自己列在「先查後用」的威脅模型外,但沒有清理機制是另一件事。
引句:「把那個專案的根(realpath)追加進使用者層的」
問題:
- `projects.txt` 只追加、不修剪。刪掉的專案、`/tmp` 底下測試用 repo 的路徑會永遠留著。
- 之後有人在同一路徑 `git clone` 別的 repo,`samefile` 對得上,就直接被信任。
- 測試也會把暫存 repo 寫進去,除非 `HOME` 隔離;計劃的〈測試怎麼搭〉有寫隔離,但沒要求 `lumos update` 測試以外的路徑都不能寫真的 `HOME`。
- 建議:讀清單時順便略過不存在的路徑,並要求條目所指目錄現在仍含 `docs/*-knowledge`;或登記時記下該目錄的 inode,讀取時核對。

## 已讀,無 finding
- `samefile` 語意:符號連結、大小寫、Unicode 正規化寫法不同都會對上;做法 3 要傳清單裡對到的那一條 realpath 而不是 `LUMOS-REPO:` 原值,這個決定是對的。路徑含 NUL、讀不到、丟例外一律當不在清單,合理。
- 重複值的處理:兩個不同寫法指向同一目錄會被算成 `repo_duplicate`,這是安全方向的誤擋,可接受。
- `_trusted_lumos` 的 `_ok` 另寫新函式不改逐字複本:設計合理。

最高等級 major;4 條 blocking(Finding 1 至 4)。
