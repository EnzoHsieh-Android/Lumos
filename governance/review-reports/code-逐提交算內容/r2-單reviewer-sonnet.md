severity: blocker

## 第一輪修法驗收
F1:修到 — 造「一次推送裡同一篇改名兩次(B→B2→B3)」的 repo 實跑 `lumos home check --diff`,內容在沒動程式的提交改時放行(rc0)、內容在改程式的提交裡真的改又照擋(rc1),跟 `t_nodehome_diff_route_counts_content_per_commit` ①②③⑤ 一致全過。
F2:修到 — 同測試④用語法樹掃 `_nodehome_evaluate` 的呼叫圖,不含任何讀 git 的函式(含包一層的),測試通過;內容改由讀取層 `_nodehome_mark_note_content` 用既有 `_nodehome_reader` 先算好放進 `content_paths`,判定層只查表比對,架構對齊。

### F3 name_at 按扁平索引倒推名稱,合併進來的平行分支提交會拿錯「當時的節點名」,規則三的寫回違規會被靜默放行
severity: blocker
blocking: 是 — 同一個違規在線性歷史正確擋下(rc1),merge 兩條平行分支後完全不擋(rc0),且沒有任何訊息指出這篇有問題
引句:「從終點沿著改名往回推(一次推送裡可能改名好幾次;拿範圍起點的舊名去對中間的提交會對不上——代碼審 r1 單reviewer)」
引句:「for gi in range(len(groups) - 1, -1, -1):」
`name_at` 假設 `groups`(`_nodehome_commit_groups` 依 `rev-list --reverse` 產生)是單一線性序列,用扁平陣列索引由終點往回套用每個提交的改名對照;但範圍裡的提交可能來自兩條互不相干的分支(各自的非合併提交都會進 `groups`,只有合併提交本身被 `--no-merges` 排除——見 file: `scripts/lumos:18060`),彼此沒有親緣關係,倒推順序只反映提交時間先後、不反映真正的改名發生順序。當「改名的提交」時間早於「另一條分支上內容真的改了、卻碰了不相干程式檔」的提交時,`name_at` 會在還沒走到改名那一步前就把後者的索引標成改名後的新名字,對不上該提交自己 `content_paths` 記的舊名字,於是這篇節點的內容變動完全沒被記進 `routed`,[S13] 的家比對整段被跳過。

重現(在 /tmp 建的暫存 repo,`git -C <tmp>`,不動原始 repo):
1. base:節點 A(about_code: src/a.py)。
2. 分支 feature,提交 F1:`git mv A.md B.md`,同提交touch `src/a.py`,內容不變。
3. 停 1.2 秒後,從 base 另開分支 sidechange,提交 M1(比 F1 晚):不改名(路徑仍是 A.md),把 A 的內容改掉,同提交touch 一支**跟 A/B 的家無關**的 `src/unrelated.py`。
4. `git merge feature` 再 `git merge sidechange`(自動合併無衝突,B.md 最終內容 = M1 寫的新內容)。
5. `python3 scripts/lumos home check --diff base..tip --repo <tmp>` → 實測 **rc0**,只印一句不相干的提醒(`src/unrelated.py 改了,它的家 Systems/U 這次沒動`),完全沒提到 B 的寫回問題。
6. 對照組:把同一段邏輯改成線性歷史(c1 改名+touch a.py,c2 在同一分支上編輯 B 內容+touch unrelated.py,無分支無合併)→ 同一指令 **rc1**,正確印出「Systems/B(這次改的檔:src/unrelated.py)」擋下。兩者是同一種違規(寫回內容真的變了,但同提交touch的程式檔不是這篇的家),差別只在提交是否來自被合併的平行分支。

總結:最高 severity blocker,blocking 共 1 條
