severity: blocker

## F1 rename 沒被 git 判成 R 時,`src.get(p, p)` 拿不到舊名,舊版真實內容漏進 seen,把「照搬另一邊」誤判成「合併自己新寫」——正好違反這支函式自己宣告的「不會多擋」

severity: blocker
blocking: yes

`_nodehome_merge_wrote_new_lines`(`scripts/lumos:21915`)用 `src.get(p, p)` 找這支檔在上一版的舊路徑:

引句:「    kept = {p for p in paths if _nodehome_merge_wrote_new_lines(repo_root, sha, parents, p, src.get(p, p))}」

`src` 只在 `_nodehome_name_status` 把 diff 判成 `R`/`C` 時才有這一筆(`scripts/lumos:21884-21886`)。但一支檔在一邊改名、另一邊改內容(modify/delete 衝突,現實裡常見的「分支改檔名,主線改內容」)時,git 對這種合併不會回報 `R`,`--name-status -M` 只印 `M <新名>`,`src` 完全沒有這支檔的項——我用 `git init` 實測重現過(兩條分支:feature 把 a.py 改名成 b.py 並小改;main 只改 a.py 的一行;合併後手動把 main 那行併進 b.py,沒有新寫任何字):

```
git show --remerge-diff --format= --name-status -M HEAD
M	b.py
```

`src` 沒有 `b.py` 這一筆,`old_path = src.get("b.py","b.py") = "b.py"`。接著找上一版內容:

引句:「        blob = _nodehome_git(repo_root, "show", "--no-textconv", f"{p}:{old_path}")」
引句:「        if blob is None and old_path != path:」

main 那個上一版沒有 `b.py`(它的內容在 `a.py` 底下),第一次查會是 `None`;而 `old_path != path` 這條件因為 `old_path` 本來就等於 `path` 而恆假,永遠不會退回去試 `path`(其實試了也沒用,因為真正該試的是 `a.py`,不是 `b.py`——這條 fallback 只能救「路徑一樣、位置不同」的狀況,救不了「舊名字根本不同又沒被判成 R」的狀況)。結果 `seen` 只有 feature 那份 `b.py` 的內容,main 那行真正存在過的內容完全沒進來源池。而 remerge-diff 對 `b.py` 這支檔的 diff 顯示的是「main 那行」被當成新增(因為 remerge-diff 拿去比對的合成合併版本裡,那行原本沒有):我實測 `added` 會抓到那一行,比對 `seen` 找不到 → 函式回 `True` → 這支檔被算成「合併自己新寫的」。但實際上這行內容是「照搬 main 既有的一行」,不是任何人在合併時新寫的——這正是這條 PITFALL 一開始要修的那種誤判(兩邊都改過、自動合起來的內容被當成合併自己寫的),只是換了個觸發方式(rename+conflict 沒被判成 R)又冒出來一次。

這跟函式自己的文件矛盾:

引句:「    新寫的行剛好跟上一版別處某一行一字不差也會漏算——兩種都偏向少擋,不會多擋。"""」

文件明講兩個天花板都「不會多擋」,但上面這條路徑會多擋(把非合併自己寫的內容判成寫了)。

**跟既有做法的落差**:同一份程式裡處理「同一件事」(改名要拿舊路徑去上一版找內容,git 失敗/找不到就當有變)的鄰居是 `_nodehome_mark_note_content`:

file: `scripts/lumos:22004`
```
olds = [b(g["src"].get(p, p)) for b in befores]
```

寫法完全一樣(`g["src"].get(p, p)`),但那支函式的文件沒有承諾「不會多擋」——它只說「讀不到一律當有變,照原本那樣查」(`scripts/lumos:21992`),這句本身就是偏保守、偏多算的自白。新函式抄了同一個 `src.get(p, p)` 寫法,卻在文件裡多開了一張「不會多擋」的保證支票,而這張支票在 rename 沒被判成 R 的情況下兌現不了。要嘛把 `_nodehome_merge_own_changes` 傳進來的 `paths`/`src` 換成更可靠的 rename 來源(例如同時對兩個上一版分別跑一次改名偵測,不只依賴這一次 remerge-diff 的 `-M` 判斷),要嘛把文件的「不會多擋」拿掉、承認這也是一個會多擋的天花板。

新加的測試 `t_nodehome_merge_conflict_union_not_blocked`(`scripts/lumos:test_lumos.py`)三個 case(union/swap/new_line)都只改同一個檔名的內容,沒有任何一個 case 牽涉改名,所以這個漏洞不會被這批新測試的翻紅釘抓到。

## 已驗過、沒問題的部分

- 新函式「判不了回 True」(`scripts/lumos:21925`:`if d is None: return True`)跟鄰居 `_nodehome_merge_own_changes`「判不了回 None 退回舊判法」(`scripts/lumos:21892` 起)乍看不一致,但兩者語意層級不同:外層 `None` 是「整支函式判不了,呼叫端要整批退回舊演算法」的控制訊號;內層 `True` 是「這一支檔判不了要不要算進合併自己改的」的布林濾網,退路是「照舊查」也就是維持原本(remerge-diff 列出來就算)的行為,跟 `_nodehome_mark_note_content` 的「讀不到一律當有變」(`scripts/lumos:21992`)是同一種保守預設。這兩種「判不了」語意不同、不需要統一寫法。
  引句:「    d = _nodehome_git(repo_root, "show", "--remerge-diff", "--no-ext-diff", "--no-textconv", "--format=",」
- 新測試 `t_nodehome_merge_conflict_union_not_blocked` 開場有 `print(...)`、docstring 裡有「出身」與「翻紅釘」段落,案例迴圈裡每個 case 先做「①現場成立」檢查(衝突確實發生、remerge-diff 確實把檔列進去)再做真正的斷言,跟既有 `t_nodehome_merge_auto_combined_not_blocked`、`t_nodehome_octopus_merge_own_violation_still_blocked` 的寫法慣例一致。
  引句:「    print("t_nodehome_merge_conflict_union_not_blocked")」
- PITFALL 筆記(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md`)講的「union/swap 不擋、new_line 照擋」跟程式在這三個測試案例裡的實際行為對得上;沒對上的是筆記與程式共同宣稱的「不會多擋」這句話,已寫進 F1。
