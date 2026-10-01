severity: major

席名:資安-opus(代碼審第 5 輪,主審 r5-delta.patch)

看過、判定不能被利用而不報的:
- 新的正式路徑判法與建議表(`ctx["canon"]`)的成本:建議表每個 repo 只建一次、查表每條一次 normpath+nfc+casefold,都是線性。實測 Python 3.14.6 對 4 萬個組合附加符號(遞減組合類別、交錯、Hangul、被擋組合)做 NFC+casefold+normpath 都在 3 毫秒內;5000 段 `z/../` 的配方測試也照綠。造不出卡住或吃爆記憶體的輸入。
- 建議字面(「是不是 "…"」「寫成 "…"」「是連結,寫它指向的那支檔」):建議的路徑都經 `_kill_show` 加引號、跳脫;照建議改寫連結目標,如果目標在 repo 外,下一次一樣判 path,guard kill 的圍欄照樣擋。沒有能誘導人去做危險動作的字面。
- Check T 三行(平台前綴未定義、偽證據、懸空):筆記路徑、test 段、平台名、平台名清單、profile 的 attr_hint 都過了 `_kill_esc`。同一段的「裸合約」「未審」兩行照舊不跳脫,但那兩行不在這次改動裡,這個缺口是 doctor 全段既有的,不算進本輪。
- 前 4 輪補的跳脫:拿掉模擬時刪掉的只有 outside/unrestorable 兩種狀態的字面;留下的 noroot(`_kill_esc(why)`)、P2 一行(`_kill_rel`、`_kill_show`)、kill-add 提醒(`_kill_show(f)`)、修法節點(`_kill_node_arg`)都還在。

## F1 判成正式路徑之後直接讀工作目錄的 `Path(top) / file`,沒有圍欄:不可信的提交在 macOS(預設不分大小寫的檔案系統)上可以讓它讀 repo 外或 `.git` 裡的檔,doctor 會把攻擊者自訂字串在那支檔裡出現幾次印出來,而且結果跟真跑 guard kill 對不上
severity: major
blocking: 是
引句:「ctx["texts"][key] = _kill_read_text(str(Path(top) / file))」
file: `scripts/lumos:13822`(guard kill 套配方前會先過圍欄:`target = os.path.realpath(os.path.join(wt, r.get("file", "")))`,落在 wt 外就判「file 路徑逃逸 worktree(圍欄擋下)」)
file: `scripts/lumos:13060`(`_kill_read_text` 用 `os.stat` 和 `open`,兩者都會跟著連結走)

1. 這次改動的前提寫在 `_kill_path_issue` 的說明裡:引句「開檔、數原文、還原都照字面走,判得準,其他寫法一律請人改寫、不預測結果。」也就是說,判斷函式認為只要路徑在 HEAD 提交裡是一般檔,工作目錄裡的同名路徑就是那支檔。但這件事只在「HEAD 的提交」裡驗過,實際讀的卻是工作目錄,而工作目錄不一定照提交的字面長出來。不可信的提交可以同時放兩個只差大小寫的項目:一般檔 `LIB/config`(100644),和連結 `lib`(120000)指向 `.git`。git 依位元組順序檢出,`LIB/…` 先建、`lib` 後建;在不分大小寫的檔案系統上,git 會先刪掉 `LIB` 資料夾,再在原地建 `lib` 這個連結,只印一行「paths have collided」警告。結果是 HEAD 裡 `LIB/config` 確實是一般檔、判成正式路徑,但工作目錄的 `LIB/config` 會經過連結讀到 `.git/config`。把連結目標換成絕對路徑或一串 `../`,就能讀到 repo 外任何一支一般檔。
2. 可以被利用的結果有兩種:
   - **資訊外洩的探針**:P2 只列「原文不是恰好一次」的配方,而且印出次數(引句所在那一段之後的「原文出現 {n} 次」)。攻擊者在配方的 `old` 寫自己猜的字串,哪幾條沒被列出來,就知道哪幾個字串在目標檔裡恰好出現一次。如果在 macOS 的 CI 跑 doctor,公開的日誌就能拿來逐段猜出內容。kill-add 的提醒也是同一個判斷函式。下面的重現讀到的就是受害 clone 自己的 `.git/config`。
   - **判斷跟 guard kill 對不上**:同一條配方,判斷函式判 ok 或 hits,真跑 guard kill 判「file 路徑逃逸 worktree(圍欄擋下)」。這正是本輪要找的那種反例:一個判成正式路徑的輸入,guard kill 的結果卻跟判斷函式不一樣。
3. 重現(macOS,APFS 不分大小寫,git 2.39.2,repo 在 7a510e53;W 是我的臨時目錄):
   ```
   # 攻擊者的 repo:先用 _mk_kill_env 的同款檔案提交一次,再用索引直接塞兩個撞名的項目
   cd $W/atk2
   L=$(printf '.git' | git hash-object -w --stdin)
   B=$(printf '[core]\n' | git hash-object -w --stdin)
   git update-index --add --cacheinfo 100644,$B,LIB/config
   git update-index --add --cacheinfo 120000,$L,lib
   # Systems/Limit.md 的 kill_recipes 放 4 條,file 都是 "LIB/config",old 分別是
   #   [remote "origin"] / extraheader / repositoryformatversion = 0 / repositoryformatversion = 1
   git commit -qm rel
   git ls-tree -r HEAD | grep -i lib
   ```
   輸出:
   ```
   100644 blob 94b2ad54…	LIB/config
   120000 blob 191381ee…	lib
   ```
   受害端 clone 之後跑 doctor:
   ```
   git clone -q $W/atk2 $W/victim2      # 只印 "the following paths have collided" 警告
   ls -la $W/victim2 | grep -i lib      # lib -> .git
   cd $W/victim2 && python3 $W/repo/scripts/lumos --vault $W/victim2/docs/kg-knowledge doctor --verbose | grep -A4 '^\[P2\]'
   ```
   輸出:
   ```
   [P2] 殺傷力配方的原文還對不對得上程式(提醒,不擋)
     ⚠ 有 2 條殺傷力配方的原文對不上程式(guard kill 跑到會判 drifted 或擋下;不擋):
         • Systems/Limit.md → 平台 "csharp-xunit" 的 "LIB/config":原文出現 0 次(…修法:lumos guard kill-rm Systems/Limit --id 6c27657b05ab)
         • Systems/Limit.md → 平台 "csharp-xunit" 的 "LIB/config":原文出現 0 次(…修法:lumos guard kill-rm Systems/Limit --id 6606020bda19)
   ```
   用 `_kill_recipe_id` 對身分:`6c27657b05ab` 是 `extraheader`,`6606020bda19` 是 `repositoryformatversion = 1`。沒被列出的 `ac0be8a7ee74`(`[remote "origin"]`)和 `ebb727c5cfcd`(`repositoryformatversion = 0`)就是判 ok,也就是在受害端 `.git/config` 裡各出現恰好一次(那支檔第 2、8 行)。提交裡的 `LIB/config` 內容只有 `[core]`,如果真的照提交讀,4 條應該都是 0 次。
   換成絕對路徑連結 `lib -> $W/secretdir`、配方 `file: "LIB/creds.txt"`,doctor 一樣讀到 repo 外的 `creds.txt`(`GITHUB_TOKEN=ghs_s` 判 ok、`GITHUB_TOKEN=ghs_x` 判 0 次)。對同一篇真跑 `lumos guard kill Systems/Limit --json`,每一條都是 `"verdict": "error", "detail": "file 路徑逃逸 worktree(圍欄擋下)"`。
4. 另一個觸發方式:Windows(ONBOARDING 有寫支援)。在非 Windows 的機器上可以把 `..\..\Users\victim\.git-credentials`、`C:\ProgramData\secret.txt` 當成一般檔名提交進去。`_kill_path_issue` 對這兩個都回空字串,也就是判成正式路徑(實測)。但在 Windows 的路徑語意下,`Path(top) / file` 會變成 `D:\Users\victim\.git-credentials` 和 `C:\ProgramData\secret.txt`(用 `PureWindowsPath` 推算);手邊沒有 Windows,這一條未能實機重現。換句話說,「正式路徑」只比對了 HEAD 的字面,沒擋 `\` 和磁碟代號這種只在 Windows 才有意義的寫法。
5. 修法建議(一處就能兩種一起收):讀檔前做跟 guard kill 同一種「雙邊 realpath」圍欄,而且要逐字比對。`os.path.realpath(os.path.join(top, file))` 必須等於 `os.path.join(os.path.realpath(top), file)`(Windows 再加一條:file 不准含 `\` 或 `:`),不相等就判 path,原因寫「工作目錄裡這個路徑經過連結或撞名」,不讀。另一種做法是改讀 HEAD 的 blob(`git cat-file`),完全不碰工作目錄;但這樣跟 guard kill 的對應還是要靠上面那道圍欄判。防回歸可以加一格:用 `update-index --cacheinfo` 造 `LIB/x.py` 加上 `lib` 指向 `..` 的撞名提交,clone 後判斷函式要判 path,而且不能讀到 repo 外的檔。

最高等級:major
