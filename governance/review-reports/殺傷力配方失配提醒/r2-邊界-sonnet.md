severity: major

## F1 符號連結只查「路徑上每一層」會漏掉連結串鏈
severity: major
blocking: 是
引句:「★路徑上任一層是符號連結、而且連結目標是絕對路徑★ → 也算 `outside`」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard/governance/review-reports/殺傷力配方失配提醒/r2-snapshot.md:43`
1. guard kill 的圍欄是對隔離工作樹裡的 `realpath` 判,`realpath` 會把整條連結鏈走完(見 `scripts/lumos` cmd_guard_kill 的 `os.path.realpath(os.path.join(wt, ...))` 與 `startswith(wt_real + os.sep)`)。
2. spec 的判法是逐層看「路徑上的某一層是不是絕對路徑連結」。輸入:`a.py` 是相對連結指向 `b.py`,`b.py` 本身是絕對路徑連結指向原 repo 內的真檔。路徑 `a.py` 只有一層、它是相對連結,不命中;但真正解析會經過 `b.py` 的絕對連結。工作目錄裡 realpath 落在 repo 內判 `ok`,guard kill 在工作樹裡 realpath 落到原 repo(工作樹外)判 error 逃逸。兩邊分家,正是 S5 對照測試想釘住的東西。
3. 目錄連結同理:`d` 是相對目錄連結指向 `sub`,`sub/x` 是絕對連結,路徑 `d/x` 的各層不會檢出 `sub/x`。
4. 折法:規定「沿著解析的每一跳(含連結的連結)只要出現一次絕對目標就歸 outside」,對照測試題目補一題「相對連結 → 絕對連結」。

## F2 同一條配方在筆記裡出現兩次時 kill-rm 永遠移不掉
severity: major
blocking: 是
引句:「零條或多條就擋下、rc2、不動筆記(多條時列出候選的完整身分)」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard/governance/review-reports/殺傷力配方失配提醒/r2-snapshot.md:64`
1. 配方身分是 `_kill_recipe_key(節點, invariant, file, old)` 的雜湊,kill-add 只擋新增時的重複,手改或合併衝突留下的兩條完全相同的配方(invariant、file、old 一樣)身分一模一樣。
2. P2 會對這兩條各印同一個短身分和同一行修法;照貼 `kill-rm --id <短身分>` 對到「多條」被擋、rc2;列出的「候選完整身分」兩條相同,使用者給再長的身分也分不開。spec 沒有任何出路(沒有索引、沒有「全相同就都移除/移除一條」規則),失配配方「有路可修」的承諾在這個輸入破功。
3. 折法:身分相同的多條視為同一條,一併移除(或移除第一條並提示還有重複);或候選列出陣列位置供 `--index` 區分。

## F3 型別壞的配方 P2 會印出 kill-rm 修法,但 kill-rm 找不到它;invariant 缺值時身分也對不上
severity: major
blocking: 是
引句:「顯示時 `invariant` 缺或不是字串一律當空字串。」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard/governance/review-reports/殺傷力配方失配提醒/r2-snapshot.md:41`
1. 現有程式算身分一律用原值:`_kill_recipe_key(str(rel), r.get("invariant"), r.get("file"), r.get("old"))`(`scripts/lumos` kill-add 判重與 kill 寫 recipe_id 都是),缺欄位時是 `None`,序列化成 `null`,跟空字串算出來的身分不同。spec 說顯示時當空字串,若印短身分的人也拿這個空字串去算,P2 印的身分跟 kill-rm(照原值算)永遠對不上。spec 沒寫「身分用原值算、只有顯示才換空字串」。
2. 更糟:`malformed` 的第一種就是「配方不是物件」(例如陣列裡有一個字串或 null)。這種元素沒有 `invariant`、`file`、`old`,`_kill_recipe_key` 與現有的 `r.get(...)` 對它直接出錯或算不出有意義的身分。P2 與 kill-add 的提醒對 `malformed` 照樣要附「修法:lumos guard kill-rm <節點> --id <短身分>」(見做法 3、5),但 kill-rm 的搜尋「在那篇的配方裡找身分以它開頭的」對非物件元素沒有定義。兩個 null 元素還會撞出同一個身分。
3. 結果:最需要被移除的壞配方(整條型別壞掉)正是 kill-rm 修不了的。
4. 折法:明定身分一律用原值算、顯示才轉空字串;非物件元素用「陣列位置」或固定規則(例如把元素本身 json 序列化後入雜湊)產生身分,kill-rm 同一支函式找;或 malformed 的修法改印別種(手改筆記),不印 kill-rm。

## F4 load_platforms 的設定錯誤例外沒被接住,kill-add 會比現在更容易炸
severity: major
blocking: 是
引句:「解析得了才呼叫 `load_platforms`,★一次判定裡只呼叫一次★,結果給每條配方共用。」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard/governance/review-reports/殺傷力配方失配提醒/r2-snapshot.md:53`
1. `load_platforms` 對「解析得了且是物件」的設定仍會 raise:`platforms` 底下某平台不是物件、`profile` 不認得、多平台缺 `default_platform`、`default_platform` 指向不存在鍵(皆 ValueError);`root: null` 時 `spec.get("root", ".")` 回 `None`,`repo_root / None` 會是 TypeError(`scripts/lumos` load_platforms,`root_str = spec.get("root", ".")`)。cmd_guard_kill 自己有 `except ValueError`,spec 這一節沒寫。
2. spec 的「設定檔讀不了」只定義了「JSON 解析不了或不是物件」兩種。照字面實作,kill-add 在這些設定下直接拋 traceback、回傳碼從 0 變非 0(而 kill-add 現在根本不讀設定檔,所以是新回歸),違反「照舊寫入、回傳碼不變」。P2 靠每篇筆記各自的例外保護只會變成「這條判不了」,也不符 S4 想要的單一句式。
3. 折法:「設定檔讀不了」定義成「自己解析失敗、不是物件、或 `load_platforms` 丟出任何 Exception」,三者同一條出路(kill-add 印沒驗提醒照寫;P2 印一句跳過);對照測試補一題缺 default_platform 的多平台設定與 `root: null`。

## F5 kill-rm 的 --id 沒有最短長度,空字串或一個字元就可能移掉唯一一條配方
severity: major
blocking: 是
引句:「在那篇的配方裡找身分以它開頭的,恰好一條就移除」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/negguard/governance/review-reports/殺傷力配方失配提醒/r2-snapshot.md:64`
1. 比對是「以它開頭」。該篇只有一條配方時,`--id ""`(空字串前綴對所有身分都成立)或 `--id a` 等只要碰巧是前綴就「恰好一條」而直接移除;spec 沒有最短長度、沒有限定十六進位字元、也沒說 `--id` 缺值怎麼處理。
2. 這是破壞性寫入,而規則的保護全靠「恰好一條」,在單配方節點(工具鏈自己就是 1 條配方)形同沒有保護。
3. 折法:`--id` 要求至少 8 個十六進位字元(印出的是 12),不合直接擋下 rc2 不動筆記;條款 S6 補「太短的身分擋下」一題。

## 其他各節
已讀,無 finding:做法 1 其餘(基準、型別先判、非一般檔、讀檔狀態、快取鍵)、做法 3、做法 5、範圍、回退、誠實界線。符號連結的相對目標、平台根在 repo 外獨立 repo、設定檔空檔與陣列(先自解析)、同一支檔被多條指到(快取)均已核對,無 blocking。

最高等級:major;blocking 共 5 條
