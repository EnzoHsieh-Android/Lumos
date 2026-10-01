severity: major

# 設計審第 1 輪 正確性-opus:殺傷力驗證編譯快取誤判_計劃

席名:正確性-opus。鏡頭:照 spec 字面實作,能不能真的消掉「沿用舊編譯結果」的誤判,有沒有新的誤判或副作用。

實驗做法:在 `pc-r1-work-正確性-opus/repo`(--shared clone)把 spec〈做法〉照字面加進 `cmd_guard_kill`(寫入壞法後、還原成功後各設一次 `max(現在+1, 上一次+1)`,每組初始 0,`os.utime` 失敗印 stderr 照跑),用環境變數切三種模式比對:none=改動前、write=只在寫入後設(前置掃描之前的版本)、full=spec 現版。合成 repo 一律走真的 `lumos guard kill --json`。直譯器:run_cmd 分別用 `python3`(本機 3.9.6,快取在 ~/Library/Caches)與 `/opt/homebrew/bin/python3`(3.14.6,快取在工作樹 `__pycache__`)。改好的副本跑既有 `-k kill` 子集 355 passed、0 failed。

## 實驗總表(full=spec 現版)

| 情境 | none(改動前) | write(只設寫入) | full(spec) |
|---|---|---|---|
| S1:同檔兩條、第二條無害同大小(3.9) | 第二條 killed 2/5、另一批 10/10 | survived 5/5 | survived 5/5 |
| S1 同上(3.14) | killed 5/5、另一批 9/10 | survived 5/5 | survived 5/5 |
| 改 a 再改 b、測試 import 兩支、壞法先睡 1.4 秒(3.9/3.14) | survived 4/4 | killed 1/4、2/4(新誤判) | survived 4/4、4/4 |
| 改 a 再改 b、壞法快速失敗(3.9/3.14) | killed 4/4(舊誤判) | 3.14 killed 1/4 | survived 全部 |
| 六條混合(a、a、b、a、b、a,含同大小無害條)對照單獨跑的真值 | 4/4 次都錯(第一條真該 killed 卻 survived) | — | 4/4 次全對 |
| make(macOS /usr/bin/make 3.81,APFS) | 第一條真該 killed 卻 survived 4/4 | — | killed/survived 正確 4/4 |
| 多平台兩組各兩條(每組各自工作樹) | 全 survived(第一條錯) | — | 兩組各 killed+survived,正確 3/3 |
| revert 失敗(壞法跑時刪掉工作樹 .git) | (第一條吃 baseline 快取 survived,沒走到) | — | error、整組 break,工作樹照常清掉,git worktree list 只剩主樹 |
| drifted(old 找不到) | 不寫檔 | — | 不寫檔、不設時間;不需要設:該檔快取狀態仍是上一次合法設定的結果 |
| 測試比對檔案修改時間與現在(條件式 GET) | survived、rc1(正確) | — | **killed、rc0(新誤判)** |
| `os.utime` 換成丟 OSError(行程內呼叫) | — | — | rc0「全 killed」(第二條其實無害)、stderr 4 行、JSON 照判 killed |

結論:spec 現版確實把「同檔/跨檔沿用舊編譯結果」兩個方向(假 killed 與假 survived)都消掉,write-only 版本引入的「還原吃到壞法快取」也被「還原後也設」補上;Python 3.9/3.14、make、多平台、revert 失敗、drifted 都照預期。新問題在「未來時間」本身,見 F1。

## 逐節核對

### 開頭欄位與白話
已讀,無 finding(F4 另論白話只講一個方向)。核對了「第二條就會拿到第一條留下的編譯結果」:3.14 下 none 模式 S1 情境 9~10/10 重現,屬實。

### 依據
已讀,無 finding。核對了「兩條改完檔案大小相同是必要條件」:對「壞法對壞法」成立;六條混合實驗另顯示「壞法與原檔同大小」時第一條會吃 baseline 的快取(見 F4)。「本機實測 5/5」:我量到 3.9 一批 2/5、另一批 10/10,時序依賴屬實,〈實務隱患〉已承認會假綠,S2 補位,不另立 finding。

### PRIOR-ART / RETIRE-IF / REVISIT
見 F3、F5;REVISIT 偵測不到的失敗型態併入 F1。

### 範圍
已讀,無 finding。核對了「不改 guard kill 的判法、回傳碼、`--json` 輸出」:副本實作只加 `os.utime` 與 stderr,`-k kill` 355 支全綠;stdout JSON 形狀不變。

### 做法
見 F1、F2。核對了「每個平台組開工作樹之後,記一個」初始 0 的上一次時間:多平台兩組實驗正確;各組工作樹路徑不同,快取鍵不會跨組相撞。另核對「還原(`git checkout -- <file>`)成功之後也照同一條規則設一次」:write-only 版本在「改 a 再改 b、壞法慢」時重現假 killed,full 版本消失,這條補得對。小註(不立 finding):第 3 點寫「測試跑超過 1 秒時」才撞,實際條件是「壞法寫入那一秒的小數部分 + 測試時間」落在 1~2 秒之間,壞法快速失敗也會撞(3.14 write 模式 1/4),但 full 版本兩種都蓋到,只影響說理。

### 條款
見 F2(S3 措辭)。S1、S2 照字面實作的副本都過。

### 回退
已讀,無 finding。核對了「revert 實作提交:guard kill 回到不設修改時間,舊的誤判會回來」:none 模式即回退後行為,實驗表第一欄就是回退後會回來的誤判(兩個方向都有)。

### 實務隱患
見 F1、F3。另一個觀察(不立 finding):full 版本還原後設時間,工作樹裡的檔案狀態資訊跟 git 索引對不上;`git status` 會自己刷新、照樣判乾淨(實測),guard kill 自己的 `git status` 只跑在使用者 repo、建工作樹之前,不受影響;`worktree remove --force`、`prune`、`rmtree` 都正常(實測 worktree list 只剩主樹)。但不刷新索引的 `git diff-files`、`git diff-index --quiet HEAD` 會把還原過的檔報成有改動(實測 none=乾淨、full=a.py、b.py 有改)——同組後面才跑的 baseline 如果裡面有「工作樹要乾淨」這類檢查會變 abort。屬可見錯誤、不是假判定,記一筆供〈實務隱患〉參考。

### 實作紀錄
(實作後補),無 finding。

## F1 未來修改時間會在「測試或被測程式拿檔案時間跟現在比」時造出新的假 killed,而且 REVISIT 抓不到
severity: major
blocking: 是
引句:「工作樹裡被改的那支檔修改時間會比現在晚幾秒」
file: `scripts/lumos:13948`

1. 輸入:一個靜態檔服務的合約「檔案沒改過就回 304」,綁定測試 `status_for('static/index.html', time.time()) == 304`,被測程式用 `os.stat(path).st_mtime <= if_modified_since` 判斷;配方改 `static/index.html` 的內容(`hello`→`hellp`)——這條壞法其實傷不到這條合約,正確判定是 survived。
2. 改動前(none):3/3 判 survived、rc1——正確,guard kill 正確地說「這條配方接不住」。
3. 照 spec 實作(full):在 `scripts/lumos:13948` 寫入壞法後把檔設成「現在+1 秒」,測試跑時檔的修改時間比 `time.time()` 晚,回 200、測試紅 → 3/3 判 killed、rc0,印「✓ 全部 killed——綁定測試咬得住」。這正是本計劃要消滅的「假的合約有守住」,只是換了一個來源。
4. 同型態的真實程式:HTTP 條件式請求(If-Modified-Since / Last-Modified)、以修改時間判斷快取是否過期且拒收未來時間的模組、「最近 N 秒內改過才重載」的熱重載邏輯、Go 的測試結果快取(修改時間太新就不快取,這個無害)。配方檔不限程式碼,可以是靜態檔、設定檔、範本。
5. 〈實務隱患〉這句後面寫「不影響判定」,只考慮了 make 警告;REVISIT 第 29 行要看的是「新的警告或錯誤」,而這個失敗型態沒有任何警告或錯誤——它長得跟一條成功的 kill 一模一樣,rtb 那邊照 REVISIT 去看是看不到的。
6. 可行修法(已實測):設完未來時間後等到時鐘追上那個時間才跑測試(副本加一個模式:`os.utime` 後 `while time.time() < 新時間: sleep`)。實測結果:條件式 GET 情境回到 survived;S1、六條混合、make 三組判定與 full 相同、全對。代價:我實測是寫入與還原兩處都等,六條 1.2 秒→13.5 秒(每條約 +2 秒);只在「寫入壞法後」等就夠(還原設的時間一定早於下一條寫入設的時間,下一次等待時一併被追上;只剩「同組後面才跑的 baseline」可能看到未來時間),推估每條 +≤1 秒(這個省一半的版本未實測)。不想付時間代價的話,至少要把這個型態寫進〈實務隱患〉並改掉「不影響判定」,REVISIT 改成能抓到的檢查(例:對 rtb 某幾條已知會 survived 的配方,修前修後判定要一致)。

## F2 S3「印一行」跟實作次數對不上,而且設時間失敗時 --json 與 kill-log 都看不出這次證據已經退化
severity: minor
blocking: 否
引句:「設時間失敗(`os.utime` 丟出 OSError)不擋:印一行提醒到標準錯誤」
file: `scripts/lumos:13999`

1. 照〈做法〉,寫入後與還原後各設一次,失敗各印一次;行程內把 `os.utime` 換成丟 OSError 的替身,兩條配方實測 stderr 印 4 行。S3 寫「應在標準錯誤印一行提醒」——測試若照字面斷言恰一行會紅;要寫明是「每次失敗一行」還是「整次執行只印一行」。
2. 同一次實測:第二條無害配方照舊被判 killed、rc0,`--json` 輸出裡是普通的 killed,`scripts/lumos:13999` 算 `weak` 只看整套跑/flaky/筆記沒提交,kill-log 寫 `weak: false`;用 `--json` 或讀 kill-log 背書的下游(hook、表態背書)看不到 stderr 那幾行,會把這次當強證據。設時間失敗在自己建的暫存工作樹裡很少見(Windows 防毒鎖檔、特殊掛載),所以列 minor;建議失敗時把該條 `weak` 設 true(或結果帶一個欄位),並在 S3 寫明「判定不變、證據強度降級」。

## F3 PRIOR-ART 對 make 的描述跟 macOS 預設 make 的實際行為不符,〈實務隱患〉的時鐘偏差警告也沒出現
severity: minor
blocking: 否
引句:「GNU make 在支援奈秒時間戳的檔案系統上看得出同一秒內的先後」
file: `governance/review-reports/殺傷力驗證編譯快取誤判/r1-snapshot.md:27`

1. 實測 macOS 內建 `/usr/bin/make`(GNU Make 3.81)在 APFS(支援奈秒)上:規則 `out.txt: prod.txt`,改動前的 guard kill 第一條真壞法 4/4 被判 survived——壞法跟 baseline 建出的 out.txt 落在同一秒,make 沒重建。也就是說這版 make 在奈秒檔案系統上照樣只看秒,這句會讓讀者以為「make 在現代檔案系統上沒這問題」。
2. 同一個 make 把來源設成未來 3 秒、30 秒再跑,都沒有印任何時鐘偏差警告(只有 Linux 上較新的 GNU make 才印)。〈實務隱患〉「make 會印「時鐘偏差」警告」要加版本條件;括號裡「Python、Gradle、jest、go 不會」沒有實測佐證,前置掃描也標了未驗。
3. 對判定沒有影響(full 版本 make 情境 4/4 正確),所以是 minor;但這兩句是 REVISIT 拿來對照 rtb 的依據,寫錯會讓 rtb 那邊以為「沒看到警告=沒事」。

## F4 舊誤判其實雙向(也會把真壞法判成 survived),白話與 REVISIT 只講假 killed,修好後判定會雙向翻
severity: minor
blocking: 否
引句:「第二條就會拿到第一條留下的編譯結果」
file: `scripts/lumos:13922`

1. 六條混合實驗(none):第一條 `A = 5`→`A = 6`(真壞法、跟原檔同大小)4/4 被判 survived——它吃到的是 `scripts/lumos:13922` baseline 剛編好的原檔快取(原檔在建工作樹那一秒寫出,壞法同一秒寫入、大小相同)。make 情境同樣第一條假 survived 4/4。
2. 這個方向的誤判會讓 guard kill 回 rc1、擋人,也是本計劃修好的東西(full 全對),但〈白話〉、依據、Issue 都只描述「第二條吃第一條、判成殺得掉」。後果:rtb 套上修法後,會有原本 survived 的配方變成 killed——若 REVISIT 那天只預期「有些 killed 變 survived」,會把反方向的翻轉誤讀成新 bug。建議白話補一句「也可能讓真的壞法沿用原檔快取被判 survived」,REVISIT 寫明兩個方向的翻轉都屬預期。

## F5 「其他 3 處呼叫」的組成寫錯:探針只有一處,第三處是 guard kill 自己的 baseline
severity: minor
blocking: 否
引句:「還有其他 3 處呼叫(合約測試閘的跑測試與兩處探針)」
file: `scripts/lumos:38139`

1. `_kill_run(` 全檔 4 處:`scripts/lumos:13922`(guard kill 的 baseline)、`:13950`(guard kill 跑壞法)、`:38139`(過濾探針,跑假測試名)、`:38192`(合約測試閘逐支跑)。除了跑壞法那處,其他 3 處是「guard kill 的 baseline + 一處探針 + 合約測試閘」,不是「兩處探針」。
2. 這句是否決甲的理由之一(「改它的環境會波及」);實際上 guard kill 自己就有兩處呼叫,甲可以只在這兩處傳環境變數而不波及另外兩處。不影響選乙的結論(乙還有「make 也蓋到」的理由,實測成立),所以 minor,但理由要寫對。

最高等級:major;blocking 共 1 條
