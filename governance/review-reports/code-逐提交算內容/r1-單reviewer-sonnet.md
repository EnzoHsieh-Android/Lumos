severity: blocker

### F1 多次改名的推送裡,「內容有沒有變」逐提交判定會誤判改名提交為「內容有變」,把無關的程式改動誤擋成寫回違規
severity: blocker
blocking: 是 — 實測會把合法推送擋下(rc1),而且正是這次修法自己要解決的「誤判內容有變」那類問題,原封不動留了一個新分支沒堵到。
引句:「讀不到(這個提交才新開、git 跑不起來)一律當有變,照原本那樣查,不因為讀不到就放過。」

1. 機制:當一篇節點在推送範圍內被改名兩次(例如 commit1 把 `B.md` 改名成 `B2.md`,commit2 才真的改內容,commit3 又把 `B2.md` 改名成 `B3.md` 這個最終名字),`here` 對 commit1 只能透過 `route_src` 的 fallback 拿到「範圍起點的原名」`B.md`;但 commit1 自己就是把 `B.md` 改名掉的那個提交,`git show {sha}:B.md` 在 `sha`(commit1)的樹裡已經找不到 `B.md`(它已被改成 `B2.md`),於是 `_nodehome_note_changed_in_commit` 的 `new` 讀不到、直接照文件說的「讀不到一律當有變」回 True。
2. 結果:commit1 只是「純改名+順手改一支早就有家、這次沒動它家的程式檔」,卻被判成「這個提交把說明寫進節點」,跟該提交裡完全無關的程式改動配對成寫回,誤擋。真正改了節點內容的 commit2 反而因為沒碰任何程式檔,`g_code` 是空的,從一開始就被規則三跳過,不會背這個鍋。
3. 實測(/tmp 自建暫存 repo,搬 scripts/ 過去跑):`_nh_base` 起點後,commit1 = `git mv Systems/B.md Systems/B2.md` + 把 `src/a.py`(已有家 `A`,`A` 這次沒動)內容從 `x = 1` 改成 `x = 2`;commit2 = 只改 `B2.md` 的內文,不碰任何程式檔;commit3 = `git mv Systems/B2.md Systems/B3.md`。跑 `lumos home check --diff <base>..HEAD`,預期 rc0(沒有任何一個提交把「跟节点无关的程式改动」和「节点内容真的有变」绑在同一个 commit),實際 rc1,訊息印「■ 這次寫了說明的節點,不是任何一支改動檔的家(1 篇):Systems/B3(這次改的檔:src/a.py)」。
4. 佐證:file: `scripts/lumos:18219` `here = vpre + rel if (vpre + rel) in g_paths else (vpre + route_src.get(rel, rel))` 這行在多跳改名時會把 `here` 落在「這個提交自己剛改掉的舊名」上。file: `scripts/lumos:18225` `repo_root, g["sha"], here, g["src"].get(here, here)):` 這裡 `g["src"]` 的 key 是這個提交自己「改名後的新路徑」,查「舊名」(`here`)查不到,預設值又退回 `here` 本身,讓 `_nodehome_note_changed_in_commit` 用同一個(已不存在的)路徑去讀 `sha` 跟 `sha^`。file: `scripts/lumos:18087` `new = _nodehome_git(repo_root, "show", f"{sha}:{path}")` 是實際失敗的那一次 git show。
5. 未覆蓋:新增測試 `t_nodehome_diff_route_counts_content_per_commit` 沒有任何改名情境(rel 名稱從頭到尾是 `B.md`),既有的 `t_nodehome_diff_route_per_commit` 也只測單次改名且改名與程式改動同一個提交(此時 `here` 直接命中 `vpre+rel`,走不到這個 fallback 分支),所以這個路徑沒有被任何綁定測試蓋到。

總結:最高 severity blocker,blocking 共 1 條
