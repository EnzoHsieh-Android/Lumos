severity: major

# 代碼審第 3 輪 資安席(資安-opus)

範圍:r3-delta.patch(73bc8aff..d219e935),站攻擊者那邊看。威脅模型照派工:筆記(含 kill_recipes)、筆記檔名、設定檔都可能來自不可信的提交;doctor 在 CI 與推送前自動跑。
實驗都在 `kcc-r3-work-資安-opus/` 底下自己 clone 的 repo 與自己造的暫存 repo 裡跑,沒動主 repo。

先講查過、**不能被利用、不報**的(給收貨端知道這幾塊看過了):
- `_kill_restorable` 把 file 當 pathspec 交給 `git ls-files --error-unmatch -- <file>`:`--` 擋住了 `-` 開頭;實測 `:(top)../../etc/passwd`、`:(attr:foo)b`、`-x` 都只回「did not match」,`:!x` 只是比對結果不同。ls-files 預設模式只查索引、不讀工作目錄、不跑任何外部程式,讀不到 repo 外的東西。萬用字元做成的病態樣式(三層各 120 個 `*` 的路徑對 300 條 700 多字長的索引)實測 0.017 秒,git 的比對器有剪枝,而且每次呼叫還有 10 秒上限。超長參數在 Linux 會丟 E2BIG(OSError),程式接住當「問不出來」。
- GIT_INDEX_FILE 的暫存索引:`tempfile.mkdtemp` 開的資料夾權限 0700、名字隨機,別人沒辦法先放檔或搶先建;用的是絕對路徑,也不會碰到使用者真正的索引(pre-commit 勾子裡原本設好的 GIT_INDEX_FILE 也被蓋掉)。程式被 SIGKILL 時會留下一份 HEAD 的索引,但只在 0700 的資料夾裡,算不上洞。
- `_kill_fs_fold` 同樣在 mkdtemp 開的私有資料夾建檔,沒有能被別的使用者利用的競態。
- 第 2 輪補的跳脫:我把 `\x1b[2K\r‮\x85` 塞進每一個人寫或設定來的欄位做模糊測試,包括筆記檔名、invariant、file、old、new、note、covers、test、platform、設定檔的 default_platform、平台名、root、profile、run_cmd,另外也試了不是物件的元素。doctor P2 段、kill-rm 的每一行輸出、kill-add 的提醒行都**沒有**原樣印出控制字元。kill-rm 的 `✓ 從 {rel} 移除了` 雖然沒跳脫,但 `env.find` 只認完整路徑或完整檔名,要用到它得自己打出控制字元,攻擊者沒辦法引誘使用者走到這裡。所以不報。

## F1 別名比對改成每段都把整棵提交掃一遍,一條特製配方就能讓 macOS 上的 doctor/推送前檢查卡住幾十秒到幾分鐘(第 3 輪新引進)
severity: major
blocking: 是
引句:「hits = {c[len(pre):] for c in (*modes, *dirs)」
file: `scripts/lumos:13084`(`_kill_alias`)
file: `scripts/lumos:13202`(`_kill_resolve` 遇到每一段不存在的名字都呼叫它)
file: `scripts/lumos:2940`(doctor P2 呼叫判斷,這一段沒有時間上限)

1. 第 2 輪的 `_kill_alias` 開頭先拿 `os.path.lexists` 問工作目錄,名字根本不存在就直接回 None,一段只花一次系統呼叫。第 3 輪換成先問暫存資料夾的 `_kill_fs_fold`,macOS 預設會回 (True, True),於是**每一段不存在的名字**都要把提交裡所有檔案和資料夾(`modes` 加 `dirs`)逐條比一遍。
2. 攻擊者只要在筆記裡放一條 file 寫成 `"z/../" * N + "prod.py"` 的配方。`_kill_resolve` 每遇到一個 `z` 就掃一次全表,代價是 N 乘上提交裡的條數。這條路徑解析完還是 `prod.py`,判定結果是 ok,doctor 什麼都不會列出來,使用者也看不出是哪一條在拖時間。
3. 重現,同一台 macOS、同一份輸入,比第 2 輪(73bc8aff)與第 3 輪(d219e935):
   ```
   # dos.py:造一個有 5000 支檔的 repo,呼叫 _kill_recipe_judge 判一條 file="z/../"*N+"prod.py" 的配方
   $ python3 dos.py lumos_r2.py 100000 5000   → ok 0.34 s
   $ python3 dos.py repo/scripts/lumos 100000 5000 → ok 31.39 s
   # 完整跑 doctor:一篇筆記放兩條這種配方(筆記約 1MB),repo 有 5000 支檔
   $ time python3 lumos_r2.py --vault …/docs/kg-knowledge doctor   → real 2.12
   $ time python3 repo/scripts/lumos --vault …/docs/kg-knowledge doctor → real 63.56
   ```
   兩版的 P2 都印「✓ 殺傷力配方的原文都對得上」。花的時間跟配方條數、repo 大小成正比:這個 repo 自己的 HEAD 就有 5757 支檔,放 10 條這種配方大約要 5 分鐘。P2 這段是純 Python 迴圈,沒有任何時間上限,`_KILL_GIT_TIMEOUT` 只管得到 git 子程序。
4. 影響:不可信的提交被拉下來之後,macOS 開發機每次推送前的 doctor 都會卡住,實際上就是擋住推送。Linux 的 CI 因為 `_kill_fs_fold` 回 (False, False) 會提早返回,不受影響;用 macOS 跑的 CI 一樣會中。這是第 3 輪「改量暫存資料夾」造成的退步,第 2 輪同樣的輸入只要 0.3 秒。
5. 修法建議:同一次判定裡,每個 (repo 頂, 上層路徑) 只建一次「折疊後的名字 → 提交裡的名字」對照表,放進 ctx 快取,之後每段查一次就好,代價回到跟段數成正比。別用「file 太長就判格式不對」來擋:guard kill 的 realpath 吃得下這種路徑,這樣做判斷會跟它對不上。對照測試建議加一格「很多段不存在的名字加上 `..`」,並且限定時間。

## F2 kill-add 的成功行把筆記裡的 test 名與既有 covers 原樣印出,能在終端機上把新加的失配提醒擦掉,或寫入剪貼簿(既有的行,第 2 輪「全面跳脫」沒涵蓋到)
severity: minor
blocking: 否
引句:「def ok(v):   # 帶控制字元的欄位不放進可貼的範本(代碼審第 2 輪資安席:引號擋不住終端把整行蓋掉),改印佔位字」
file: `scripts/lumos:13577`(`✓ kill 配方寫入 … test={test}`,沒帶 --test 時 test 取自 KEY 行的 `[test:…]`)
file: `scripts/lumos:13574`(`✓ 只更新了既有配方的 covers(…):{', '.join(updated[0])}`,updated[0] 是筆記裡既有那條的 covers)
file: `scripts/lumos:13523`(新加的 `_kill_add_warn` 在這兩行之前印到標準錯誤)

1. 第 2 輪把 kill-add 提醒行、kill-rm 的完整內容和範本都跳脫了,但同一支 kill-add 最後那行成功訊息還是把筆記來的字原樣印出。這兩行在這個功能之前就有,這次只是搬進 `_guard_kill_add_locked`,不過它們跟新提醒印在同一個終端畫面上。
2. 重現一:擦掉新提醒。KEY 行寫成 `[test:T\x1b[1A\x1b[2K\x1b[1A\x1b[2KOK]`,使用者照常 `lumos guard kill-add Systems/Limit 上限恆為5 --file prod.py --old 'LIMIT = 42' --new 'LIMIT = 99'`(不帶 --test):
   ```
   stderr '⚠ 提醒:配方欄位格式不對(test 名 "T\\u001b[1A…" 不合法,guard kill 會拒跑)。修法:lumos guard kill-rm Systems/Limit --id c92030e0e6a7,…\n'
   stdout '✓ kill 配方寫入 Systems/Limit.md(invariant『上限恆為5…』, test=T\x1b[1A\x1b[2K\x1b[1A\x1b[2KOK)\n…'
   ```
   在終端機上,標準錯誤那行提醒會先印,接著被標準輸出裡的「游標上移、清整行」蓋掉。這個功能本來就是要讓人在寫入當下看到提醒,這樣就被抵銷了。
3. 重現二:寫剪貼簿。在既有配方的 covers 放 `"\x1b]52;c;cm0gLXJmIH4=\x07\x1b[1A\x1b[2K"`(OSC 52,base64 解開是 `rm -rf ~`)。使用者對同一條配方補 `--covers java-concurrency`:
   ```
   rc 0
   stdout '✓ 只更新了既有配方的 covers(Systems/Limit.md):\x1b]52;c;cm0gLXJmIH4=\x07\x1b[1A\x1b[2K → java-concurrency\n…'
   ```
   kitty、WezTerm、Alacritty、tmux 這類預設允許 OSC 52 寫入的終端機,會把剪貼簿換成攻擊者指定的字。
4. 修法:這兩行裡從筆記來的字(test、updated[0]、updated[1])跟 rel 一樣過 `_kill_esc`/`_kill_rel`。另外補一個測試:KEY 行的 `[test:]` 和既有 covers 夾控制字元時,kill-add 的標準輸出不能出現原始控制字元。

## F3 doctor Check T 同一段裡「平台前綴未定義」那行把設定檔的平台名原樣印出(第 2 輪只修了隔壁那行)
severity: minor
blocking: 否
引句:「print(f"  {C['Y']}—{C['X']} 設定檔讀不了({_kill_esc(_te)}),跳過 test_ref 存在性檢查(裸合約仍檢)")」
file: `scripts/lumos:1669`(`bad_platform` 那行:`{seg}`、`{plat}`、`', '.join(split)` 都沒處理)

1. 第 2 輪把 Check T 裡「設定檔讀不了」那行改成走 `_kill_esc`,理由是「例外訊息帶著設定檔裡的字」。可是同一個 try 區塊後面的 `bad_platform` 那行,直接印出設定檔的平台名(split)和 KEY 行的 `[test:…]` 片段,來源一樣,卻沒處理。
2. 重現:設定檔寫 `{"default_platform":"a\x1b[2K\rX","platforms":{"a\x1b[2K\rX":{…},"b":{…}}}`,筆記的 KEY 行寫 `[test:zz:TestLimitFive]`,再跑 `lumos doctor --verbose`:
   ```
   "      • Systems/Limit.md: [test:zz:TestLimitFive] 平台前綴 'zz' 未定義於 platforms(a\x1b[2K"
   ```
   結果原始的 ESC 和回行首印進 doctor 的輸出(推送前與 CI 日誌都會出現),能把同一行或前面的行蓋掉。
3. 這行在這次改動之前就有,不是新的錯。之所以報,是因為第 2 輪宣稱這一段已經處理過設定檔來的字,其實只處理了一半。修法照隔壁那行套 `_kill_esc` 即可,不擋推送。

最高等級:major
