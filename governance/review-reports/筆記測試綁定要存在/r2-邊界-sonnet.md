severity: major

# 設計審第 2 輪:邊界-sonnet 席(邊界與輸入鏡頭)

實驗環境:`git clone --shared` 到我自己的臨時目錄,用 `importlib` 載入 `scripts/lumos` 直接呼叫既有函式(`slot_parse`、`_strip_inline_markup`、`_ns_summary_logical`、`_classify_test_refs`、`_platform_test_index`)與 git 指令實跑;實作還不存在,所以「照字面實作會錯」的判斷都標明是哪個既有零件的實測輸出推出來的。

## F1 複查的「測試檔」沒定義範圍,平台根是 repo 根時筆記自己就讓複查永遠說「有」
severity: major
blocking: 是
引句:「再到**被檢查的版本**裡,各平台根下的測試檔用 `git grep -w -F`(提交時 `--cached`、推送時對終點)整字找這個名稱(去掉平台前綴)。」
file: `scripts/lumos:5084`(`load_platforms` 無 `platforms` 設定時 root 就是 repo_root)
file: `scripts/lumos:5387`(`_walk_test_files` 用 profile 的副檔名、`file_name_match`、`file_must_match` 選測試檔;git pathspec 表達不了最後一項)
1. 〈做法〉3 只說「各平台根下的測試檔」,沒說 git grep 怎麼只挑測試檔。本 repo 與多數消費專案是單平台、根就是 repo 根;照字面把根當 pathspec 交給 git grep,搜的是整個 repo,包含剛新加這個名稱的筆記本身。
2. 實測(本 repo,HEAD):`git grep -l -w -F -e t_note_shape_test_refs_new_names HEAD -- .` 命中 `docs/.canary-log.jsonl`、計劃筆記、`r1-snapshot.md`,而這個名稱在程式碼裡根本不存在。新加的壞名字寫進筆記後,終點版本裡就有它自己,複查必回「有」。
3. 結果:分類器說 dangling、複查說有,「兩邊說法不同算判不了,不擋」,所以〔S1〕在單平台、根為 repo 根的專案(含本 repo)永遠不會擋任何一個名稱。1c 與 `[test-gone:]` 那兩條也共用這個判法,同樣失準。
4. 修法方向(只寫缺口):計劃要明寫複查只掃哪些路徑(例如依 profile 副檔名與 `file_name_match` 轉成 pathspec,並排除知識庫目錄與 `.jsonl` 等),`file_must_match` 這類 pathspec 表達不了的要寫明怎麼辦。
5. 實測限制:還沒有實作,這是用 git grep 實跑 + 讀 `load_platforms` 得出,不是跑 note-shape 紅綠。

## F2 複查放行面連「測試檔呼叫了這個函式」都算,「只出現在程式文字裡」那一類大半被放行
severity: major
blocking: 是
引句:「複查找得到就放行,名稱只要出現在測試檔裡(註解、字串)就過——寧可少擋」
file: `scripts/lumos:40248`(`_classify_test_refs`:只在原始碼文字裡 → `fake`)
1. 計劃自己量到本 repo 有 7 個「只出現在程式文字裡」的 `[test:]`(綁到被測函式而非測試)。這類才是 `fake` 的典型,也是規則要擋的主力。
2. 但〈漏網〉只講「註解、字串」會放行。實際上測試檔裡每一處呼叫、import、字串提到都算「整字找到」。實測 `git grep -c -w -F -e <名稱> HEAD -- scripts/test_lumos.py`:`cmd_note_shape` 6 筆、`run_doctor` 9 筆、`slot_parse` 1 筆都命中;抽 5 個被測函式名,3 個會被複查放行。
3. 於是「把 `[test:]` 綁到被測函式本身」(最常見的寫錯法)只要那支函式被任何測試呼叫過就不擋,規則對 `fake` 類實際擋下的比例遠低於計劃量到的 7 個。這不是註解字串那種邊角,是主路徑。
4. 計劃的 RETIRE-IF 看「索引沒認出的超過一半」會抽查誤擋,但完全沒有量這個方向(該擋沒擋)的辦法。

## F3 判「新加」用範圍淨差,合過主線時別人寫的名稱算在推送者頭上;「不另設上線記號」讓這點在升級後第一輪就發生
severity: major
blocking: 是
引句:「這次改到的筆記清單用 `git diff --name-status -z --no-renames 起點 終點 -- 知識庫`(提交時起點是 HEAD、終點是提交索引)」
引句:「升級前寫好的提交只有真的新加了壞名字才會被擋,不會把整段歷史當新寫」
file: `scripts/lumos:27250`(`_notelines_range_added`:`exclude_remote` 排除已在主線的提交、合併提交只算自己多寫的行 `_merge_new_lines`、`mark` 排除上線前寫的提交)
file: `scripts/lumos:38535`(`_lens_push_base` 的說明:合過主線時範圍會多算,所以兩套起點並存)
file: `scripts/lumos:28578`(`cmd_note_shape` 提交時遇 MERGE_HEAD 直接跳過,理由是「推送前只查合併自己多寫的行」)
1. 既有規則為了不怪罪推送者,逐提交算、排除遠端主線已有的、合併提交只看合併自己多寫的、再用上線記號排除上線前的提交。新規則整個換成「兩端整篇次數相減」,這三層都沒有。
2. 實測(臨時 repo):feat 分支合進 main,main 上另一人新增了 `v/B.md` 含 `[test:t_old_dangling]`;`git diff --name-status --no-renames feat~1 HEAD -- v` 回 `A v/B.md`。推送者的範圍起點(自己分支上次推的頂端)落在那次新增之前,B.md 的名稱就被算成「這次新加」。
3. 照計劃「只在升級後才擋」的說法,升級前別人推上主線的壞名字(存量,計劃自己量到本 repo 26 個、rtb 57 個)沒有上線記號可以把它們排除:任何一條在升級前就開出、升級後才合進 main 的分支,在 B.md 這種筆記被別人新增過時都會被擋,而且擋下訊息指向的是別人的行。
4. 提交時擋合併被跳過、推送時擋合併卻重算整段,兩邊對合併的處理反向,〈範圍〉也沒講這個行為是有意的。
5. 逃生口是單次跳過(記帳),但被擋的人解不了別人的名稱;跟筆記形狀擋既有承諾「別人的舊帳不擋你」對不上。

## F4 1c 判「新寫」用接回後整條逐字比對,CJK 摘要重排折行就變成新寫
severity: major
blocking: 是
引句:「找不到一模一樣的,所以搬篇、改名不算新寫」
file: `scripts/lumos:28148`(`_ns_summary_logical` 用 `" ".join` 接續行)
file: `scripts/lumos:28167`(`_ns_text_key` 的註解:中文任意處折行、續行接回多一格都不算改,既有規則為此專門去掉 CJK 相鄰空白)
1. 實測:同一條作廢的 RULE,折行位置從「這條規則已經作廢了」後移到「作廢」後(只有排版不同),`_ns_summary_logical` 分別回 `...已經作廢了 [status:superseded]...` 與 `...已經作廢 了 [status:superseded]...`,兩者不相等。
2. 〈名詞〉對新加名稱明寫「摘要重排折行,次數不變,都不算新加」,但 1c 的「新寫」判定走的是整條逐字比對,折行位置一變、接回多一個空白,一個舊的、掛著活測試的作廢條目就被當新寫擋下。作者沒改任何字。
3. 計劃只承認「只改了錯字也算新寫」,沒提折行與格式整理(`lumos set`、編輯器重排、regen)這個更常見的來源。

## F5 「方括號整個在反引號裡不算」與「名稱外包反引號要拿掉」的實作順序沒定,既有唯一的行內剝除函式會把後者剝成空名稱
severity: minor
blocking: 否
引句:「整個方括號落在反引號裡(例:寫成程式碼的」
引句:「名稱外圍的反引號拿掉」
file: `scripts/lumos:368`(`_strip_inline_markup` 的說明要求全檔只用這一份,不要自寫第二份)
file: `scripts/lumos:3764`(`slot_parse` 的反引號處理只認單反引號)
1. 實測 `_strip_inline_markup("PITFALL: a [test:`x`] b")` 回 `PITFALL: a [test:] b`;`[test:`a`,`b`]` 回 `[test:,]`。若實作者依該函式的「別寫第二份」註解先剝再掃,〔S9〕要求抽到的 `` [test:`x`] `` 會變成空名稱,被〔S17〕當成 `[test:]` 擋下,合法寫法被誤擋。
2. 同一函式其他界線實測正確:`` `[test:x]` `` 與 `` `a` [test:x] `b` `` 剝成沒有/只剩 `[test:x]`;未閉合 `` `a [test:x] `` 回 (`PITFALL: `, True) 之後不算。
3. `slot_parse`(格子認的寫法)對雙反引號 `` ``[test:x]`` `` 不認 span,仍回 test 欄位 x;`_strip_inline_markup` 把它剝掉。計劃說「跟筆記格子對齊」,但〔S8〕要不算的雙反引號範例,格子那邊算,兩處對「這一行有沒有 test」說法不同。
4. 計劃要明寫:先在原行找方括號、再判整個方括號是否在反引號 span 內(看方括號起訖位置與 span 是否包含),而不是先剝掉再找。⚠ 這條是實作陷阱,字面讀法不衝突,交編排者判是否升 major。

## F6 git grep 的失敗、`-` 開頭名稱、根在 repo 外或子模組,回傳碼的意義沒規定
severity: minor
blocking: 否
引句:「某平台的根不存在或掃不到任何測試方法時」
file: `scripts/lumos:38713`(`_lens_git` 預設 timeout=20、跑不起來或逾時回 None)
1. 實測:名稱 `-x` 不帶 `-e` → `git grep -w -F -x` 回 129(usage);帶 `-e` 才正常。`[test:-x]` 在分類器是 bad-name、會走複查,所以一定要 `-e`;計劃沒寫。曾實測名稱 `-f/etc/passwd` 讓同一指令跑超過 120 秒(被當成 `-f <檔>` 選項),不是命名上的好行為。
2. 根在 repo 外:`git grep -- /tmp` 回 128 `outside repository`;根在子模組:未帶 `--recurse-submodules` 回 1 且沒命中;兩者與「真的沒有」(1)無法區分,而〈做法〉4 只列根不存在與索引壞。分類器(工作目錄 os.walk)能讀到這些根,所以名稱只會落在「說法不同不擋」,不會誤擋;但 1c 與 `[test-gone:]` 要「兩邊都說有」,對這些專案永遠成立不了,規則靜默失效。
3. git grep 在大 repo 超過 `_lens_git` 預設 20 秒回 None,計劃沒寫那算「判不了」還是「沒有」。實測本 repo(6190 檔)對整個 tip 每次約 0.22 秒、100 個名稱 21.8 秒;名稱數上千(新分支首推、空樹起點)時單支掛鉤拖數分鐘。計劃只寫「有要查的名稱時才」,沒提逐名稱各跑一次 subprocess 的成本。

## F7 `[test-gone:名稱@提交]` 的 `@` 解析規則有缺口
severity: minor
blocking: 否
引句:「有 `@` 時後面至少 7 碼十六進位」
1. 未規定多個 `@`(`a@b@abc1234`):用第一個 `@` 切與用最後一個 `@` 切結論不同,前者報後綴格式錯、後者把 `a@b` 當名稱。
2. 「至少 7 碼十六進位」沒說是整段 fullmatch 還是前綴比對:`a@abc1234zzz`、`a@ abc1234`(`@` 後空白)、大寫十六進位、超過 40 碼都沒定。
3. `[test-gone:a,b@abc1234]` 逗號列表:`@` 屬於誰、「名稱還在不在」要全部不在還是任一不在,沒定;現有 `_SLOT_REPEATABLE` 讓同一行可寫多個方括號,但逗號形式沒寫。
4. 計劃的測試條款〔S6〕〔S7〕只測單名稱帶不帶 `@提交`。

## F8 抽取正則若自寫成常見的 `[^\]]*`,單行出現大量未閉合 `[test:` 時是平方時間
severity: minor
blocking: 否
引句:「自己的寬鬆正則」
file: `scripts/lumos:3764`(既有 `slot_parse`、`_strip_inline_markup` 在同樣輸入下線性)
1. 實測:`re.compile(r"\[\s*test\s*[:：]\s*([^\]]*)\]", re.I)` 對 `"x [test: a "*20000`(22 萬字元單行)跑 26.7 秒;8 千次 4.3 秒。既有 `slot_parse` 同輸入 0.01 秒、`_strip_inline_markup` 近 0。
2. 這支會在每次提交的提交前掛鉤對所有改到的筆記兩側整篇跑;一篇貼進大段日誌或機器輸出的筆記就拖死掛鉤。計劃要寫明抽取要線性(照 `_slot_value_end` 的做法找收尾),或限制單行長度。
3. 巢狀:`[test:t_x[1]]` 這類參數化名稱,`[^\]]` 會在第一個 `]` 截斷成 `t_x[1`,`slot_parse` 的層數計算會取完整 `t_x[1]`;兩邊對名稱邊界說法不同,「對齊格子」這句沒說清楚用哪一個。

## F9 摘要裡「同縮排、沒前綴」與清單寫法的行不會被抽到(靜默漏掉)
severity: minor
blocking: 否
引句:「摘要用 `_ns_summary_logical` 接回續行」
file: `scripts/lumos:28148`(續行定義是縮排比前綴行深且不以前綴開頭;其他行 `last=None` 丟掉)
1. 實測:`summary: |-` 下依序放 `PITFALL: ...`、同縮排的 `[test:t_same_indent] 沒前綴的行`、`- PITFALL: 清單寫法 [test:t_list]`,`_ns_summary_logical` 只回第一條;後兩行的名稱不在摘要條目、也不在正文(正文從開頭欄位之後算),兩邊的抽取都不會看到。
2. 摘要條目是先接回整條再判反引號、正文是逐實體行判:同一段 `` `foo `` 換行 `` bar` `` 在摘要接回後成對、在正文各自未閉合,兩邊對「哪些字算在反引號裡」說法不同;單行的未閉合反引號則在摘要會連帶吃掉接回的所有續行。
3. 都是少抽(fail-open),不會誤擋;列出來是因為〔S18〕只測「單行寫法與續行」,沒涵蓋這兩種。

## 已讀,無 finding 的節
- 〈名詞〉的「佔位字」:`TODO`、`待補` 等在分類器實測為 fake(名稱出現在程式文字裡),計劃明寫先於判存在、不過複查,避免了這個坑;已讀,無 finding。
- 〈做法〉6 開關:`_note_shape_slots_parse`(`scripts/lumos:28113`)的壞值(非字串、不在 block/warn/off)→照 block 並唸一句,新 `_note_shape_test_refs_parse` 沿用同形狀;設定檔讀不了時回 block,與計劃「寫壞照 block」一致;已讀,無 finding。
- 空推送(起點等於終點,`git diff` 為空)、刪分支(終點全 0)、淺層 clone:`cmd_note_shape` 在新組規則之前已 return 0(`scripts/lumos:28578` 與 `28596` 的早退),新規則掛在 `_note_shape_eval` 之後不會繞過這些早退;已讀,無 finding。
- 名稱含正則特殊字元:git grep 用 `-F`,不當正則;分類器 `_KILL_METHOD_OK_RE` 先擋非 `[\w .]` 字元(bad-name);已讀,無 finding(`-` 開頭的參數問題見 F6)。
- 名稱很長:`_lens_git` 對 OSError(含 argv 過長)回 None,不會丟例外;已讀,無 finding。
- 測試檔是符號連結:`git grep` 讀到的是連結目標路徑文字、找不到名稱,工作目錄那邊讀得到,結果落在「說法不同不擋」,fail-open;已讀,無 finding。

最高等級:major,blocking 共 4 條
