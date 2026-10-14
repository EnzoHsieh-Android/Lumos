severity: major

材料已讀,暫存目錄已刪。實驗只在臨時 repo 內做,沒碰真的 index 或 ref。

## Finding 1:spec-freeze 的「一般檔」判斷沒排除符號連結,會把 repo 外的檔案讀進物件庫和 `--out`
severity: major
blocking: 是 — 沿用既有的 `is_file()` 寫法就會跟隨符號連結。第三方投稿的 repo 放一個指到 repo 外的計劃連結,就能把 repo 外的內容寫進共用物件庫和交給審查席的快照。
引句:「而且要是工作樹上的一般檔」
問題:第 9 條只寫「要是工作樹上的一般檔」和「第 2 條的路徑規則」。第 2 條是純字串檢查,不看檔案本身。程式裡「是不是檔案」的慣用判法是 `Path.is_file()`(`cmd_dispatch_lens_spec` 就這樣寫),它跟隨符號連結。`git hash-object -w --no-filters <path>` 也跟隨符號連結。這一步發生在 `ls-tree` 的 120000 檢查之前,檢查擋不到它。
失敗情境:`docs/x-knowledge/Projects/a_計劃.md` 在工作樹上是指到 repo 外檔案的符號連結。
- 輸入:`lumos spec-freeze docs/x-knowledge/Projects/a_計劃.md --out s.md`
- 實測:`git hash-object -w --no-filters` 對符號連結路徑,印出的是被指到檔案的內容(實測讀到 SECRET)。
- 結果:該內容進了物件庫的 blob,`mode` 又因 stat 跟隨而變成 100644。`--out` 寫出 repo 外檔案的內容。印出的 `LUMOS-SPEC:` 一行看起來完全正常,讀取端的 120000 檢查也不會觸發,因為提交裡存的是普通 blob。
- 路徑中間的目錄是符號連結時同理(例如 `docs` 指到別處)。
- 建議條款:用 lstat 判一般檔,且 `resolve()` 後要在 repo 根底下。S18 補一條符號連結的夾具。
佐證:``file: `scripts/lumos:48999` `` 的 `cmd_dispatch_lens_spec` 用 `sp.is_file()` 判檔。

## Finding 2:「只在提交裡」那一行用一次 `ls-tree` 帶多個路徑,會被一個壞候選毀掉或對不上
severity: minor
blocking: 否 — 只影響那一行附加說明,不影響其他節點的內容。
引句:「會談目錄沒有、只在那個提交裡有的檔(一次 `ls-tree` 帶多個路徑判」
問題:候選檔來自 `_LENS_SPEC_CODE_RE`,字元集允許 `.` 和 `/`,所以會抓到 `scripts/../../x`。實測三件事:
1. `ls-tree <sha> -- scripts/lumos scripts/../../x` 整批 rc=128(`outside repository`)。一個壞候選讓整批判不出來。
2. 非 ASCII 路徑(圖譜節點名是中文)預設被引號跳脫成 `"docs/.../\346..."`。不加 `core.quotePath=false` 或 `-z`,輸出列對不回輸入路徑。
3. 輸出順序是 tree 排序,不是輸入順序。
失敗情境:計劃文字裡有 `scripts/../../x` 之類的字串,同時有一個只在提交裡的檔 `scripts/new.py`。
- 結果:ls-tree 整批失敗,「只在提交 … 沒算牽連」那行消失。
- 結果:席位看到的是「沒牽到任何家、合約或事故的節點」,以為已算過。這正是第 5 條要避免的誤導。
- 條款沒規定整批失敗時怎麼辦,也沒規定用 `-z`/`quote=True` 還是逐檔呼叫。
佐證:``file: `scripts/lumos:48952` `` 的 `_LENS_SPEC_CODE_RE`;``file: `scripts/lumos:47386` `` 的 `_lens_git(quote=True)` 是現成的選項。

## Finding 3:spec-freeze 的提交只含 HEAD 加計劃,草稿階段新寫的節點被標成「錯字連結」,新增檔的說法也不成立
severity: minor
blocking: 否 — 不會出錯結果,但標籤是假話,會誤導審查席。
引句:「計劃要新增或改名的檔就是這種,不再落到「沒牽到任何家、合約或事故的節點」那句」
問題:凍結提交的 tree 只比 HEAD 多這份計劃。工作樹上同時寫的、還沒提交的新 Systems/Issues 節點和新程式檔,既不在會談目錄也不在凍結提交裡。
- 第 6 條把這種連結標成「連結指到不存在的節點」,並註明「分得出是錯字連結」。這句話在 spec-freeze 的主要用法(不先提交草稿)下是錯的。
- 第 5 條說新增或改名的檔會被列出。但新增的檔在兩邊都不存在,根本進不了候選(候選本來就要 `is_file()`)。
- 「只在提交裡」只會命中「計劃所在分支已提交、會談目錄分支沒有」的檔,跟第 5 條講的情境不同。
失敗情境:計劃連結 `[[Systems/新模組]]`,該節點同一個工作樹裡剛寫好、未提交。
- 結果:標成「連結指到不存在的節點」,而不是「在凍結時尚未提交」。
- 條款:S6 和 S7 的夾具都用已提交的物件,測不到這種情況。

## Finding 4:成功但沒有任何固定席內容時,掛鉤直接放行,不記 `spec_commit` note
severity: minor
blocking: 否 — 只影響撤除條件的計數。
引句:「提交寫法成功 `spec_commit`、失敗 `spec_commit <代碼>`、工作樹寫法失敗 `spec_worktree <代碼>`」
問題:現行掛鉤在 rc 0 且 `text` 為空時就 `return 0`,在讀 `spec_source` 之前。計劃沒提到程式檔、沒連結節點、也沒寫 `lands_in` 時,`text` 為空,lumos 也不印「計劃來源:提交…」那行。
失敗情境:一份只有文字的計劃,用提交寫法成功讀到。
- 結果:掛鉤不記 note。RETIRE-IF「連續 8 週都沒有 `spec_commit` 字首」和 REVISIT 的次數會低估,席位也看不到是哪個提交。
- S12 只規定成功列有文字的情況。
佐證:``file: `scripts/hooks/claude/dispatch-lens-hook.py:545` `` 附近 `if not text: return 0`。

## Finding 5:`no_knowledge` 一律記 error,但提交寫法下它多半是使用者打錯 slug
severity: minor
blocking: 否 — 只影響統計,前後矛盾。
引句:「`no_knowledge` 與範圍類代碼照現在記 `error`」
問題:同一段的理由是「使用者輸入錯不是掛鉤壞掉,記成 error 會蓋過真的掛鉤錯誤」。第 2 條規定提交寫法的 slug 在會談目錄沒有同名目錄就回 `no_knowledge`。這比工作樹寫法更常是輸入或分支錯位,跟理由自相矛盾。
失敗情境:計劃在新開的 `y-knowledge`,會談分支還沒有。
- 結果:記 `error`,拉高 enforcement 的錯誤數。
- 建議:提交寫法下的 `no_knowledge` 也記 `ok`,或在條款裡寫明為什麼例外。

## Finding 6:大小上限的 None 無法分辨「超過上限」和「讀不到」
severity: minor
blocking: 否 — 只在物件被 gc 清掉或 replace 的邊角情況才錯。
引句:「單項回 None(超過上限)回新代碼 `spec_too_large`」
問題:`_nodehome_cat_blobs_capped` 的單項 None 有兩個來源:大小超過上限,或 `cat-file --batch-check` 回 missing(`_nodehome_cat_sizes` 把 missing 也轉成 None,之後被 `continue` 略過)。條款把單項 None 一律當 `spec_too_large`。
失敗情境:`ls-tree` 通過後、讀取前 blob 被清(或有 `refs/replace` 干擾)。
- 結果:回 `spec_too_large`,說明講檔案太大,實際是物件不見了,正確代碼是 `spec_missing`。
- `spec_blob` 取自 `ls-tree`,內容卻是另一次 `<sha>:<path>` 讀出,條款也沒要求兩者一致。
- 建議:先用 `ls-tree -l` 的 size 欄位判上限,或讀回來再核對 blob 編號。
佐證:``file: `scripts/lumos:31133` `` 的 `_nodehome_cat_sizes`。

## Finding 7:目標架構段的 vault 沿用「排序第一個」,第 4 條沒寫要改
severity: minor
blocking: 否 — 有兩個 vault 時才會錯。
引句:「目標架構段(`_dispatch_lens_spec_arch_text`)吃的計劃文字就是這一份;宣告與節點照現在從會談 repo 的 HEAD 讀」
問題:第 2 條和 S5 都說目標架構段也要到計劃自己的 vault 找。但第 4 條只說傳「計劃文字」。現行 `_dispatch_lens_spec_with_arch` 的 vault 來自 `_arch_target_vault_rel(root, "HEAD")`,取排序第一個。照字面實作,多 vault 時目標架構段會到 `a-knowledge` 找,與 S5 矛盾。
失敗情境:計劃在 `b-knowledge`,加 `--arch-target`。
- 結果:目標架構的節點讀自 `a-knowledge`。
- 建議:第 4 條明寫把路徑得出的 vault 傳給 arch 段。
佐證:``file: `scripts/lumos:43538` `` 的 `_arch_target_vault_rel`;``file: `scripts/lumos:49137` `` 的 `_dispatch_lens_spec_with_arch`。

## 已讀,無 finding 的節
- **暫存 index 與 commit-tree:** 用 `GIT_INDEX_FILE` 指暫存檔,不碰真的 index、ref 和掛鉤。實測設 `commit.gpgsign=true` 加壞掉的 `gpg.program` 時,`commit-tree` 仍成功、未觸發簽名。
- **HEAD 分離與沒有提交:** HEAD 分離時 `read-tree HEAD` 和 `-p HEAD` 正常。沒有提交時條款已拒絕。
- **計劃是新檔:** 用 `update-index --add --cacheinfo` 處理,沒問題。
- **完整編號語意:** `_lens_full_sha` 的 `^{commit}` 會把 tag 剝成 commit,再要求解出值等於輸入,能擋掉 tag 編號和縮寫。大小寫轉換、64 碼在 SHA-1 repo 失敗,行為符合條款。
- **`ls-tree` 判一般檔:** 單一路徑時是字面比對,目錄、符號連結和子模組都能分出來。
- **第一個冒號切開、路徑規則:** 與工作樹寫法互不干擾。
- **三種連結節點的分類邏輯:** 分類邏輯本身自洽,錯在 Finding 3 的前提。
- **資料狀態五問:** 除 Finding 3 的未提交草稿和 Finding 6 的物件被清,其餘未發現新問題。

最高等級 major,共 7 條 finding,其中 blocking 1 條(Finding 1)。
