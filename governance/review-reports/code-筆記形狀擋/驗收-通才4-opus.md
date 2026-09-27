severity: major

# 驗收輪(通才席 4,opus)——筆記形狀擋 r3 修正 delta

範圍:`驗收-delta.patch` 全部 hunk(scripts/lumos 的抽取器 exists 雙參數、`_path_at_pin`、裸寫 @ 段允許斜線、`_ns_range_added` 的 golive/max_count/改名搬移/NFC、指路行正則、`_ns_is_regen`、`_ns_pin_ok` 上提、喚醒改走 `_ns_check_line`、doctor 上限與 CI 那一步;test_lumos.py 的 r3 回歸測試)。
現場:`python3 scripts/test_lumos.py -k note_shape` → 101 passed(macOS)。以下重現都在 /tmp 或 scratchpad 的臨時 repo 裡跑,對照組用上一版 `git show 9454e66c:scripts/lumos` 存到 scratchpad 的副本(下稱「舊版」)。

## F1 推送範圍的路徑改成 NFC 之後拿去當 git 查詢鍵:合併提交裡自己寫的行在 NFD 檔名筆記整批漏查(比舊版退步),終點不是 HEAD 時一般提交也漏查
severity: major
blocking: 是 —— 會放過該擋的,而且合併那條路是這次修法自己引入的退步(舊版擋、新版放)

引句:「+        paths = [nfc(p) for p in _nodehome_split_z(names) if p.endswith(".md")]」
引句:「+    return by_path, [nfc(p) for p in _nodehome_split_z(net) if p.endswith(".md")]」

走一遍:git 樹裡存的是 NFD 檔名時,NFC 化後的 `p` 只適合當 `by_path` 的鍵,不能再拿去找 git 裡的東西——git 的「版本:路徑」與路徑篩選都是逐位元組比對。
- 合併那條路:`specs.append(f"{sha}:{p}")`(`scripts/lumos:23642`)用 NFC 路徑去 cat-file → 讀不到 → `_merge_new_lines` 回 None → 退路 `_ns_diff(repo_root, first, sha, "--", p)`(`scripts/lumos:23650`)用 NFC 當路徑篩選 → diff 是空的 → 合併自己寫的違規行一行都沒記。舊版這裡用的是 git 原樣路徑,讀得到、擋得到。
- 一般提交那條路:`net` 改成 NFC 後,評估時 `reader(p)` 讀 NFC 路徑;讀取器只有在「終點就是 HEAD、而且檔案系統不分正規化(macOS APFS)」時才從磁碟讀到,否則走 `git show {spec}:{p}`(`scripts/lumos:22565`)→ NFC 對 NFD 樹回 128 → 整篇 `continue`。所以只要終點不是 HEAD(先推舊的那個提交、doctor 拿遠端頂端、CI 以外的 --diff 手動範圍)就漏;Linux CI(ext4 逐位元組)連終點是 HEAD 也讀不到(見 F2)。

最小重現(臨時 repo,`core.precomposeunicode=false`,腳本 scratchpad/probe4/p_merge_nfd.py、p_nfd.py):
```
# 合併時在 NFD 檔名筆記裡寫 `src/a.py:7`,範圍 base..merge(終點=HEAD)
$ python3 probe4/p_merge_nfd.py
NFD new: 0  old: 1        ← 新版放行、舊版擋(退步)
NFC new: 1  old: 1        ← 對照:NFC 檔名兩版都擋
# 一般提交在 NFD 檔名筆記寫違規,同一個範圍,只差在終點是不是 HEAD
$ python3 probe4/p_nfd.py
A1 tip==HEAD: 1
A2 tip!=HEAD (same range): (0, '')      ← 漏查
A3 control NFC tip!=HEAD: 1
# 機制:git show 對 NFD 樹只認 NFD
git show HEAD:<NFC> rc = 128
git show HEAD:<NFD> rc = 0
```
改法方向:`_ns_range_added` 保留 git 原樣路徑去組 spec/路徑篩選,只在寫進 `by_path` 與回傳清單時 NFC;回傳時一併帶「NFC→原樣」對照給評估那層的讀取器用。

## F2 回歸測試 ⑤ 只在 macOS 檔案系統上成立,Linux CI 上預期翻紅
severity: minor
blocking: 否 —— 未能重現(手邊沒有 Linux/正規化敏感的檔案系統),依錨定紀律從 major 降一級;機制已由 F1 的 A2 重現

引句:「+    check("⑤NFD 檔名的筆記推送範圍照查(現場:git 裡存的是 NFD)", nfd in stored and rc == 1, out[-400:])」

走一遍:測試 ⑤ 的範圍終點是 HEAD,讀取器先試磁碟 `root / <NFC 路徑>`;macOS APFS 不分正規化,NFC 路徑讀得到 NFD 檔,所以綠。`.github/workflows/*.yml` 是 `runs-on: ubuntu-latest`,ext4 逐位元組比對:磁碟讀不到 → 退到 `git show HEAD:<NFC>` → 128(F1 已實測)→ 整篇跳過 → rc 0 → 這條 check 在 CI 上會紅。等於這條測試證明的是「macOS 上剛好讀得到」,不是修法本身對;推上去後 CI 全套分片會出一條紅。把 F1 修好(用原樣路徑讀)這條才會兩個平台都綠;另可在測試裡加一條「終點不是 HEAD」的變體(F1 的 A2),在 macOS 上就能翻紅。

## F3 「上線點不是祖先就不查」把繞過提交前檢查、在另一條也裝了檢查的分支上寫的違規整批放過(舊版擋、新版放)
severity: major
blocking: 是 —— 會放過該擋的:推送前/CI 是 --no-verify 的最後一道,這個形狀下整條分支的新增行都不看

引句:「+        live = set(ap.decode("ascii", errors="replace").split()) | {golive}」
引句:「+        if live is not None and sha not in live:」

走一遍:`golive` 取自 `git log --reverse -S<標記> tip -- scripts/hooks/pre-commit` 的第一筆(`scripts/lumos:22943`)。只要上線標記在歷史裡被**兩條分支各自加過**(消費專案在兩條分支各跑一次 lumos update、或把裝檢查那個提交 cherry-pick 到長壽分支),`log -S` 在帶路徑的歷史簡化下只會留一條(合併時掛鉤內容跟第一個上一版一樣,另一邊被剪掉),上線點就是較早那一筆。另一條分支從自己的上線提交之後寫的每個提交都不是它的後代 → `sha not in live` → 全部 `continue`。那條分支上提交前檢查其實是有在跑的,所以用 --no-verify 繞過寫的違規,到推送前/CI 也沒人看。「是不是上線點的後代」跟「寫的時候這道檢查在不在」在這個形狀下不等價。

最小重現(scratchpad/probe4/p_dual.py:分支 a 較早裝檢查、分支 bb 從上線前的提交開出來也裝檢查,之後 --no-verify 寫 `src/a.py:9`,兩條先後合進主線,範圍從上線前那個提交到頂端):
```
$ python3 probe4/p_dual.py
golive log -S: ['golive on a', '']
new: (0, '')
old: (1, '擋下:這次推送的筆記有新寫的、程式碼推得出來的形狀(筆記形狀擋)——\n  docs/kg-knowledge/Systems/B.md:17  程式行號引用 `src/a.py:9`:…')
```
改法方向:「這個提交寫的時候這道檢查在不在」直接看那個提交自己的上一版樹裡掛鉤有沒有標記(`git cat-file` 讀 `<上一版>:scripts/hooks/pre-commit` 找標記字串,批次讀),不要用「是不是某一個上線點的後代」代替;或至少把 `log -S` 改成 `--full-history` 收齊所有加標記的提交、用它們的後代聯集。

## F4 喚醒改用片段字串篩「指向新程式檔」,前綴比對比舊版的整串相等寬
severity: minor
blocking: 否 —— 只會在已經被繞過/warn 模式留下來的舊違規上重報,不會讓乾淨的提交被擋

引句:「+                        if rule == "現況描述沒寫來源" or not any(f"`{x}" in frag or f"= {x})" in frag for x in became):」

走一遍(`scripts/lumos:23848`):舊版是 `tok in became` 整串相等;新版 `` f"`{x}" in frag `` 是前綴比對。這次新增沒副檔名的 #! 腳本 `scripts/run`,同一行舊筆記裡指向既有程式檔 `scripts/run.py:5` 的片段 `` `scripts/run.py:5` `` 也含 `` `scripts/run ``,會被當成「新程式檔喚醒」報出,改法文字還說是「這支檔這次才變成程式檔」,指錯檔。要踩到得那行在上線後寫、當時就是違規卻留了下來(warn 模式或繞過),所以只標 minor。改法:比對 `` f"`{x}:" ``、`` f"`{x}@" `` 或直接讓 `_ns_check_line` 回傳解析後的路徑再做相等比對。

## 已查過、沒有問題的角落
- exists 改兩個參數:全部三個傳 exists 的呼叫端(refcheck、`_ns_check_line`、測試 ③)都已跟上;其他呼叫端不傳 pins,不會走到切 @ 那段,Check J/每支檔有家/推筆記的結果不變。
- `--ancestry-path` 在上線點本身(live 手動補上 golive)、範圍起點晚於上線點、合併提交(只要有一個上一版是後代就算 live,合併自己寫的行照查)這幾個形狀都對;測試 ⑦ 兩條(舊帳放、對照擋)都真的走到被測分支。
- `--max-count` 與 `--reverse` 併用時 git 先截再反轉,拿到的是最新 N 個;測試 ⑨ 只驗提醒字樣、沒驗掃描真的截斷,屬弱測但不假綠。
- 測試 ④ 固定了提交時間並現場驗處理順序,舊版會漏、新版擋,成立;測試 ①⑧ 都走得到喚醒那條路(那行不在 part 1 的 seen 裡、不在上線點版本裡)。
- `_ns_is_regen` 與 Check J(`scripts/lumos:4581`)判法一致。

最高 severity:major;blocking 條數:2(F1、F3)
