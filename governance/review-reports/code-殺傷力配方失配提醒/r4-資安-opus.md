severity: major

# 代碼審第 4 輪(破例輪)資安席(資安-opus)

範圍:主審 r4-delta.patch(d219e935..0f1e68ea),全貌只拿來對照。站攻擊者那邊看。威脅模型照派工:筆記(含 kill_recipes、KEY 行)、筆記檔名、設定檔都可能來自不可信的提交;doctor 在 CI 與推送前自動跑。
實驗都在 `kcc-r4-work-資安-opus/` 底下:`repo/` 是 `git clone --shared` 出來的,`lumos_r3.py` 是 `git show d219e935:scripts/lumos` 抽出的第 3 輪版本,`lumos_r4.py` 是 0f1e68ea 的版本,另外造了一次性的暫存 repo。主 repo 和審材 repo 根都沒動。

先列出**查過、不能被利用、所以不報**的部分(讓收貨端知道這幾塊有人看過):
- **很多只差大小寫的檔、很長的名字**:`tree_kids` 每個 repo 只建一次,`fmaps` 每個真實存在的資料夾只建一次,代價跟提交大小成正比。`_kill_fold_key`(NFD → casefold → NFC)拿病態字串測過:8 萬個組合符號倒序排、交錯排、被擋住的組合、諺文、會展開的 casefold 字,每種 16~32 萬字都在 0.012 秒內做完,沒有平方級的情況。
- **`git ls-files -z` 的輸出變成路徑集合**:`-z` 會關掉引號跳脫,換行、跳脫碼這類檔名都原樣切開。`os.fsdecode` 跟 `_kill_tree` 用的是同一種解碼(surrogateescape),兩邊比得起來。集合的大小最多就是整個 repo 的檔案數,用完就丟、不進快取。每條配方各叫一次 git 的成本在第 2、3 輪就有了,不是這次才加的。只拿 pathspec(例如提交一支名字就叫 `*` 的檔)能做到的,也只是讓判斷「還原會不會成功」失準。那是正確性問題,而且提醒本來就只提醒、不擋,攻擊者拿不到任何好處。
- **kill-add 把驗原文移到鎖外**:`warn_box` 裡放的是記憶體裡那條配方本身,鎖外不會再讀筆記;驗原文只讀設定檔、工作目錄的檔和 HEAD。暫存索引放在 `mkdtemp` 開的 0700 資料夾裡,每次都是新的。兩支程序同時跑沒有共用的可寫狀態,別人插不進來。提示裡的 `kill-rm --id` 是照配方內容算的短身分,中途有人改了筆記,它也只會對到同一條,或因為對到多條而被擋下。提醒現在改在成功行之後才印,第 3 輪 F2「用成功行的跳脫碼把提醒擦掉」那條路反而更難走了。
- **kill-add 成功行的兩處跳脫**:`test` 和舊 covers 都過了 `_kill_esc`;拿第 3 輪 F2 的兩個重現(游標上移清行、OSC 52)重跑,標準輸出都沒有原始控制字元。`rel` 和 `invariant_substr` 是使用者自己打的字,不報。

## F1 `_kill_alias` 新加的快取會把每一段「不存在的上層路徑」整串存起來,一條很深的配方就能讓 macOS 上的 doctor 和推送前檢查吃掉好幾 GB 記憶體(第 4 輪修正引進)
severity: major
blocking: 是
引句:「for base in tree_kids.get(par, ()):」
file: `scripts/lumos:13112`(`_kill_alias`:par 不在提交裡也照樣建一張空表,存進 `fmaps[par]`)
file: `scripts/lumos:13218`(`_kill_resolve`:每一段不存在的名字都照字面接上,下一段的 par 就多一層)
file: `scripts/lumos:13173`(`_kill_readlink`:工作目錄裡沒有這個連結時,改讀 HEAD 裡的連結內容,長度沒有上限)
file: `scripts/lumos:2940`(doctor P2 整次共用同一個 ctx,快取一直留到 doctor 結束)

1. 第 3 輪修 F1 的做法是「每個資料夾的對照表只建一次」,快取的鍵是 `par = "/".join(pth[1:])`,也就是到目前這一段為止的整串路徑。問題在路徑走進一個提交裡沒有的名字之後:`_kill_resolve` 照字面接上,繼續往下走,所以每多一段都會產生一個新的、更長的 par,各自配一張空表存進 `fmaps`。一條 `a/a/a/…/prod.py` 共 N 段的配方,存下來的鍵總長大約是 N²。第 3 輪用 `"z/../" * N` 測,深度一直是 1,所以沒碰到這種情況。對照測試新加的那一格也只測 `z/../`。
2. 最小重現(`deep.py`:造一個只有 prod.py 的 repo,直接呼叫 `_kill_recipe_judge` 判一條 `file = "a/" * N + "prod.py"` 的配方;本機暫存資料夾 fold=(True, True),也就是 macOS 預設):
   ```
   $ /usr/bin/time -l python3 deep.py lumos_r3.py 40000 "a/"
   len(file)=80007 status=missing 13.69s …   34258944  maximum resident set size
   $ /usr/bin/time -l python3 deep.py lumos_r4.py 40000 "a/"
   len(file)=80007 status=missing 14.38s …   1880539136  maximum resident set size
   ```
   80KB 的 file 字串,記憶體從 34MB 變成 1.88GB,而且跟長度平方成正比(N=20000 時多 445MB)。
3. 完整跑 doctor:一篇筆記放兩條 `dK/` 重複 25000 次的配方(整篇筆記 150KB),在 repo 頂執行 `python3 <版本> --vault docs/kg-knowledge doctor`:
   ```
   lumos_r3.py   15.72 real   199884800  maximum resident set size
   lumos_r4.py   16.49 real  1950547968  maximum resident set size
   ```
   兩版 P2 都只列「2 條對不上」,使用者看不出是哪一條在吃記憶體。快取在整次 doctor 共用,不同配方用不同的名字就會一直疊上去:每加一條 25000 段的配方大約多 0.9GB。筆記裡放幾條長一點的配方,就能把開發機的記憶體吃光、讓系統開始大量換頁,或讓 doctor 被系統砍掉,實際上等於擋住推送。用 macOS 跑的 CI 一樣會中。Linux 的 `_kill_fs_fold` 回 (False, False),會提早返回,不受記憶體這一項影響。
4. 變形:筆記本身可以完全不顯眼。在提交裡放一個模式 120000 的連結 `l`,連結內容是 `"a/" * 30000 + "prod.py"`。這麼長的連結在 macOS 上 checkout 不出來,工作目錄裡就沒有它,`_kill_readlink` 便退回去讀 HEAD 裡的連結內容,長度沒有上限。配方只要寫 `"file": "l"`(3 個字):
   ```
   $ python3 link.py lumos_r3.py 30000 → link in workdir: False / recipe file='l' status=missing 8.04s maxrss 34MB
   $ python3 link.py lumos_r4.py 30000 → link in workdir: False / recipe file='l' status=missing 8.17s maxrss 1022MB
   ```
5. 兩版的時間一樣:不管 fold 怎麼設,`_kill_path_kind` 和 `(*path, name)` 每一段都要把整串路徑重新組一次,本來就是平方級。在 Linux 模型(fold=(False, False))下 N=40000 也要 8.1 秒,第 3 輪版本就是這樣了,這次修正沒有讓它更慢。**這一條 finding 判 major 的依據只有記憶體**:記憶體的退步是這次加快取帶進來的。不過深路徑讓時間變成平方級這件事,在整個功能裡沒有任何上限,doctor P2 也沒有時間上限,建議一起處理。
6. 修法建議(已驗):在 `_kill_alias` 建表之前加 `if par not in tree_kids: return None`。提交裡沒有的資料夾底下不可能有別名,判斷結果完全一樣,也不會再存東西。我在 `lumos_fix.py` 改了這一行後重跑 N=40000:maxrss 212MB → 212MB(跟沒跑之前一樣)。時間的部分可以順手處理:一旦某一段已經不在提交裡,後面的段在遇到能退回提交內的 `..` 之前都不必再查表、不必重組路徑(例如記一個「已經在提交外面幾層」的計數)。對照測試建議加一格「很深的不存在路徑」,同時限定時間與記憶體(例如用 tracemalloc 看高峰)。

## F2 Check T「平台前綴未定義」那行只跳脫了 test 段和前綴,第 3 輪 F3 的原始重現(設定檔的平台名)還是原樣印出;同一段的懸空、偽證據那兩行也一樣
severity: minor
blocking: 否
引句:「f"{rel}: [test:{_kill_esc(seg)}] 平台前綴 '{_kill_esc(plat)}' 未定義於 platforms"」
file: `scripts/lumos:1669`(同一行的 `{rel}` 沒處理;下一行 `f"({', '.join(split)})")` 的平台名清單也沒處理)
file: `scripts/lumos:1679`(`fake`:`[test:{seg}]` 原樣印出)
file: `scripts/lumos:1681`(`dangling`:`[test:{seg}]` 原樣印出)

1. 第 3 輪 F3 寫明 `{seg}`、`{plat}`、`', '.join(split)` 三個都沒處理,當時的重現就是把跳脫碼放在**設定檔的平台名**(會出現在 split 裡)。第 4 輪只處理了 seg 和 plat,split 和同一行的 rel 都沒動。測試 ⑪b 只在 `[test:]` 那一段放跳脫碼,所以照樣是綠的。收貨紀錄把 s3 記成「平台名與 test 段過 `_kill_esc`」,但實際上平台名沒有處理。
2. 重現(`mkT.py`):設定檔的平台叫 `"a\x1b]52;c;cm0gLXJmIH4=\x07\x1b[1A\x1b[2K"` 加上 `"b"`;筆記 `Systems/Limit.md` 和 `Systems/Ev\ril.md` 的 KEY 行寫 `[test:zz:TestLimitFive]`;`Systems/Dang.md` 寫 `[test:b:Nope\x1b[1A\x1b[2KX]`。跑 `lumos_r4.py --vault docs/kg-knowledge doctor --verbose`,把輸出按 `\n` 切開後取出的原始行:
   ```
   '      • Systems/Ev\ril.md: [test:zz:TestLimitFive] 平台前綴 'zz' 未定義於 platforms(a\x1b]52;c;cm0gLXJmIH4=\x07\x1b[1A\x1b[2K, b)'
   '      • Systems/Limit.md: [test:zz:TestLimitFive] 平台前綴 'zz' 未定義於 platforms(a\x1b]52;c;cm0gLXJmIH4=\x07\x1b[1A\x1b[2K, b)'
   '      • Systems/Dang.md: [test:b:Nope\x1b[1A\x1b[2KX] 在程式碼中找不到'
   ```
   OSC 52(在允許它的終端機上會改寫剪貼簿,base64 解開是 `rm -rf ~`)、游標上移、清整行、回行首,全都原樣進了推送前的終端與 CI 日誌。
3. 懸空、偽證據那兩行不是這次改的,但跟被修的那行在同一個迴圈、印的是同一個 `seg`;懸空那行只要寫一個程式裡沒有的測試名就會走到,比 bad_platform 更容易觸發。範圍外的同族還有 `resolve_test_refs` 丟出的錯誤訊息(`scripts/lumos:4641`,`{seg}`、`{plat}`、`', '.join(platforms)` 都沒處理),在這裡註記一下,不另外報。
4. 修法:1669–1670 的 `rel` 改走 `_kill_rel`,`split` 每一項過 `_kill_esc`;1679、1681 的 `seg` 過 `_kill_esc`。測試 ⑪b 補兩種情況:設定檔的平台名放跳脫碼、懸空的 test 名放跳脫碼。這跟第 3 輪 F3 一樣是終端顯示被干擾,不會損壞資料、也不會擋錯推送,所以判 minor。

最高等級:major
