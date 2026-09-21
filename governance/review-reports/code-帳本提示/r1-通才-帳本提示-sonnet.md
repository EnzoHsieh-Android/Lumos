severity: minor

## F1 `-uall` 對改名/複製(R/C)輸出的續行條目誤套「XY+空白」前綴,`ent[3:]` 切錯位置

severity: minor
blocking: no

**觀察到什麼**:`_codeloop_print_dirty_bookkeeping` 對 `git status --porcelain -z -uall` 的每個 NUL 分隔片段一律假設格式是「兩碼狀態 + 一個空白 + 路徑」,直接切 `ent[3:]` 當路徑:

引句:「rel = ent[3:]」

但 porcelain -z 對「改名/複製」是把新路徑(帶 `XY ` 前綴)與舊路徑(**不帶任何前綴,就是裸路徑**)拆成兩個相鄰的 NUL 片段。迴圈把第二個片段也當成「帶前綴」去切 `ent[3:]`,等於把舊路徑開頭砍掉 3 個字元,得到一串垃圾字串。

**怎麼重現**(在 /tmp 臨時 repo,沒有動到 /Users/enzo/harness/lumos-toolchain):
```
git init -q repo && cd repo
mkdir -p docs && printf '{}' > docs/.governance-log.jsonl
git add -A && git -c user.name=t -c user.email=t@t commit -qm init
git mv docs/.governance-log.jsonl docs/renamed-log.jsonl
git status --porcelain -z -uall | python3 -c "
import sys
for i,p in enumerate(sys.stdin.buffer.read().split(b'\x00')): print(i, repr(p))"
```
輸出:
```
0 b'R  docs/renamed-log.jsonl'
1 b'docs/.governance-log.jsonl'
```
第 1 條是裸路徑(沒有 `R ` 前綴)。套用 `ent[3:]` 後變成 `'s/.governance-log.jsonl'`(砍掉了 `doc`),既不等於 `docs/.governance-log.jsonl`,也不等於清單裡任何一個固定字串。實測跑過(python 重現同一組字串),結果一致。

**為什麼是問題而不是風格**:這是解析邏輯本身的錯誤前提(「每個切片都帶 2 碼狀態+空白」對 R/C 的第二個切片不成立),不是覆蓋率取捨。以目前 `_BOOKKEEPING_FILES` 只有 9 個固定字面路徑(見 `scripts/lumos:18720`)而言,砍壞後的字串幾乎不可能巧合等於其中之一,所以**目前**不會造成錯誤提示或漏提示——我也實測過:如果有人真的把某個簿記檔改名(例如上面的 `docs/.governance-log.jsonl` → `docs/renamed-log.jsonl`),新路徑不在白名單裡、舊路徑又被切壞不會比對到,兩邊都不會被列出來,行為上等同於「這個簿記檔悄悄消失,完全沒被提醒」——但因為簿記檔在正常工作流裡不會被改名(都是工具自己固定路徑寫入),這是一個潛伏但目前打不到的邊界情形。如果未來 `_BOOKKEEPING_FILES` 擴充到路徑更容易被工具/人改名的檔案,這條解析錯誤就會變成真正的漏列。

**建議**(不擋,提醒修法):解析 -z 輸出時要處理 R/C 狀態的雙 NUL 片段(第二片段是純路徑,不切前綴),或至少對「切出來的字串不在任何已知路徑格式」的片段做防呆,不要無條件假設固定偏移量。

---

## 已查但沒發現問題(逐項覆蓋任務指定的檢查點)

- **`--note` 注入**:新函式印出的 `git commit -m '{msg}'` 裡 `msg` 是依 `status` 決定的固定字面字串(`"chore(lumos): 記錄代碼審通過"` / `"...跳過"`),完全不含使用者 `--note` 的內容(引句:「msg = "chore(lumos): 記錄代碼審通過" if status == "passed" else "chore(lumos): 記錄代碼審跳過"」)。核對過整段函式,`note` 沒有被接進這個列印的指令字串,所以沒有 `--note` 注入這條路。
- **路徑含空白/中文/引號/開頭 `-`**:`_sh_quote` 用 `shlex.quote`,實測對空白、中文、單引號、開頭 `-` 都能安全還原(`python3 -c "import shlex; print(shlex.quote(...))"` 逐一測過);開頭 `-` 那個案例雖然 shlex 不會額外加引號,但指令模板固定帶 `git commit -m '...' -- <paths>`,`--` 之後 git 一律當 pathspec 處理,不會被誤判成選項。不過目前 `_BOOKKEEPING_FILES` 全部是工具寫死的固定字面路徑(`scripts/lumos:18720-18724`),不會出現空白/中文/奇怪字元,這層防呆目前用不到,是面向未來擴充的防禦。
- **漏列**:比對過 `_codeloop_record_valid`(`scripts/lumos:27982-28002`,推送前判留痕有沒有失效用的是 `_BOOKKEEPING_FILES` **加上** `_BOOKKEEPING_DIRS`)與新函式(只查 `_BOOKKEEPING_FILES`)。查過 `_codeloop_gov_log`(`scripts/lumos:27086-27105`)只會弄髒 `docs/.governance-log.jsonl`;背景故事另一個踩雷點 `governance/anchor-baseline.json` 本來就在 `_BOOKKEEPING_FILES` 裡。`_BOOKKEEPING_DIRS` 裡的 `governance/code-loop/` 整層在 `governance/.gitignore:10` 被 gitignore(不會、也不該被提交),`governance/review-reports/`、`governance/replay/` 是有版控的目錄(`git ls-files` 分別數到 2916、138 個檔),不列進提示是 patch 自己說明過的刻意取捨(避免把別的 session 的卷證一起貼上去)。這條路沒找到作者沒看到的漏列。
- **多列**:`_BOOKKEEPING_FILES` 九個都是工具自己專用的帳本檔(治理帳、各種 -log.jsonl、簽名檔),沒有找到不該進帳本提交的項目。
- **`git status` 解析的其它面向**:一般 M/D/`??`/staged+unstaged 混合(如 `MM`)都是單一 NUL 片段、`ent[3:]` 切法正確,拿真實 repo 現在的髒檔驗證過(`docs/.governance-log.jsonl`、`docs/.usage-log.jsonl`、`governance/anchor-baseline.json` 都被正確切出來,見 F1 之外的驗證紀錄)。改名/複製那個坑就是上面 F1。
- **不該印的時候印 / 效能**:`repo_root` 在進到 pass/skip 分支前已經先驗證是目錄(`scripts/lumos:28563`)且 `head_sha` 必須拿到(`scripts/lumos:28578-28580`,拿不到直接 rc2 提早 return),所以走到新函式時 repo 一定是能跑 git 的合法 repo,`git status` 失敗的分支(`r.returncode != 0: return`)實務上幾乎不會被觸發、觸發了也是安靜跳過不印,不會誤印。效能上直接在真 repo(/Users/enzo/harness/lumos-toolchain,目前有 148 個 status 條目)跑 `git status --porcelain -z -uall` 計時只要 0.04 秒,不是問題。
- **as_json 汙染**:確認 `cmd_code_loop` 的 `as_json` 參數只在 `check` 子指令分支被讀,pass/skip 沒有 JSON 輸出模式,新的一行提示不會混進任何機讀輸出。
- **翻紅釘(新測試是不是假綠)**:把 `_codeloop_print_dirty_bookkeeping(repo_root, status)` 這行呼叫從一份 `/tmp` 複本裡拿掉,直接呼叫 `t_codeloop_pass_lists_dirty_bookkeeping()`,7 個 `check()` 裡有 5 個從 ✓ 變 ✗(「留痕寫了治理帳,就要列出它還沒提交」「簽名檔也列進去」「列成可直接貼的提交指令」「帳本檔照樣列」等);沒拿掉時原樣跑(含用官方指令 `python3 scripts/test_lumos.py -k t_codeloop_pass_lists_dirty_bookkeeping`,在真 repo 執行,唯讀不改動任何東西)是 `7 passed, 0 failed`。翻紅釘成立,不是假綠。

sha256 核對:`governance/review-reports/code-帳本提示/r1-snapshot.patch` 算出來是 `11724a5a6b16fb74afcebc640bde01b481c2f76ce20598eae83ce4aef97fe3a0`,跟派工詞給的一致,187 行也對得上。
