severity: blocker

### F4 推送前逐提交判定用 `--no-merges` 整個排除合併提交,合併提交自己樹狀態帶進來的內容/程式變動完全不受檢查
severity: blocker
blocking: 是 — 同一組「節點寫進不相干程式的說明、同提交改掉那支程式(家在別篇)」的違規,包在一般提交會被擋,原封不動搬進合併提交就放行,兩條分支合併是完全平常的工作流程。
1. `_nodehome_commit_groups` 用 `git rev-list --reverse --no-merges` 列提交,合併提交整個不出現在 `groups` 裡——不是「查不到它的舊名」,是它自己相對親代多改了什麼從沒被 `diff-tree` 讀過。
2. `_nodehome_evaluate` 逐提交迴圈只走 `for g in groups`,合併提交不是任何 `g`;它自己在合併當下多寫的節點內容與多動的程式檔既不會進 `content_notes`/`per_commit`,舊版 `routed` fallback 也用不到同一個 `sha`,三條路徑全繞過。
3. 實測(`git -C /tmp 下` 建的兩分支專案):B 節點在合併提交裡順手寫入跟 `c.py`(家是 C,B 不管)有關的散文、同提交改掉 `c.py`——包成一般提交時 `lumos home check --diff` 印「這次寫了說明的節點,不是任何一支改動檔的家:Systems/B」且 rc1;把完全相同的兩處編輯改成夾在 `git merge --no-ff` 產生的合併提交裡提交,變成只印「提醒」、rc0。
引句:「不跨提交追名字(2026-09-11 平板 POS 第一次真推送踩到的誤擋、代碼審兩輪抓到的改名與合併)」
file: `scripts/lumos:18060` `_nodehome_commit_groups` 的 `git rev-list --reverse --no-merges` 把合併提交整支排除,不只排除跨分支追名字那個場景
file: `scripts/lumos:18234` `_nodehome_evaluate` 的 `for g in groups:` 只走得到非合併提交,合併提交本身沒有對應的 `g`

### F5 節點狀態在同一次推送裡「這個提交降成 planned 順便寫內容、下一個提交只把狀態打回 doing」可完全繞過規則三
severity: blocker
blocking: 是 — 兩個普通提交(不需要合併、不需要反引號)就能讓違規內容躲過 `lumos home check --diff`;同一段編輯包在一個提交裡會被擋,拆成這兩步就放行。
1. `_nodehome_mark_note_content` 只用「這個提交之後(after)的 status」判斷要不要收進 `content_notes`,而 `sig` 只比對摘要/決策/正文、不含 status——「這個提交把狀態從 doing 降成 planned,順便在摘要寫進跟另一支不相干程式有關的散文」因為 after-status 是 planned,被整條跳過不查。
2. 下一個提交把 status 從 planned 打回 doing、內容(摘要/決策/正文)一字不動:`sig` 沒變,`_nodehome_mark_note_content` 判「只補簿記欄位」整條不收進 `content_notes`,這個提交也不會被查——status 升格或降格本身完全沒有另外補查。
3. 實測:X 的摘要新增一段跟 `y.py`(家是 Y)行為有關的散文(不寫反引號、不會觸發規則二)、同提交改掉 `y.py`,包在單一提交(status 全程 doing)時 `lumos home check --diff` 擋下(rc1,點名 Systems/X 不是 `y.py` 的家);拆成「這個提交把 X 降成 planned 並寫進內容、下一個提交把 X 打回 doing」兩步後,結果變成只剩提醒、rc0。
引句:「只補簿記欄位:不算這個提交寫回」
file: `scripts/lumos:18243` `info["status"] not in _NODEHOME_HOME_STATUSES` 用的是這個提交的 after 狀態,沒有另外處理「這個提交本身在降格/升格」的邊界
file: `scripts/lumos:17925` `_nodehome_parse_note` 的 `sig` 只有 `(summary, dec, body)` 三元組,不含 status,純狀態切換永遠判不到「內容有變」

## 前一輪修法驗收

F3:修到 — `t_nodehome_diff_route_counts_content_per_commit` 的 ⑥(平行分支合併、另一條在改不相干程式的提交裡改了 A 的內容)在 sandbox 實跑 rc1 且訊息點名 Systems/A,改成完全單一提交內判定後不再跨提交追名字。

總結:最高 severity blocker,blocking 共 2 條
