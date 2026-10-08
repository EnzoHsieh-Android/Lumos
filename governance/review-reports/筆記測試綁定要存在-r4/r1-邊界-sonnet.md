severity: major

# 邊界-sonnet 席報告(筆記測試綁定要存在,完整版第 r4 輪)

實驗環境:`git clone --shared` 到 `tb4-r1-work-邊界-sonnet/repo`,用 `/opt/homebrew/bin/python3` 把 `scripts/lumos` 當模組載入,直接呼叫現有函式;另造 mini repo(含子模組、符號連結、類別內測試)、bare remote + 兩份 clone 模擬本機與 CI。沒有跑全套測試,沒有動凍結快照或主 repo。

## F1 起點與主線整庫改用逐篇 git show 讀,本 repo 一次就要 14.8 秒,20 秒共用上限先被讀檔吃光
severity: major
blocking: 是
引句:「`_nodehome_list` 列檔、`_nodehome_reader` 讀內容,跟 note-shape 讀終點同一套」
引句:「整組(讀起點、判存在)共用一個 20 秒上限,用完剩下的名稱這次不查、印一行。」
file: `scripts/lumos:26138`(`_nodehome_reader`:起點不是 HEAD 時,每篇都 `git show <sha>:<path>` 開一次子程序)
file: `scripts/lumos:26196`(`_nodehome_side` 的 deadline 與 share 優化存在,spec 沒用)
file: `scripts/lumos:26440`(`_nodehome_cat_blobs`:同一批檔一次批次讀)
1. 實測(本 repo 的 630 篇筆記,起點取 HEAD~5):`_nodehome_reader` 逐篇讀完全部 = 14.76 秒;同一批用 `_nodehome_cat_blobs` = 0.24 秒;起點剛好等於 HEAD 時走磁碟只要 0.09 秒。指令:`python3 e_time.py`(`_nodehome_list` 取檔、`reader(p)` 迴圈計時)。
2. spec 要讀兩次整庫(起點一次、主線一次),而且共用同一個 20 秒上限。本 repo 光起點就吃 14.8 秒,主線再讀一次必然超過 20 秒;消費專案筆記更多時,起點一次就超過。
3. spec 沒寫「讀到一半上限用完」的行為,字面只講「剩下的名稱這次不查」。照字面有兩種實作,都壞:(a) 拿讀了一半的起點集合繼續比,沒讀到的筆記裡的舊名稱全算新加,但名稱已經沒時間查,頂多是白算;(b) 乾脆整組放棄。不管哪種,這個規則在本 repo 對「起點不是 HEAD」的推送(也就是平常的推送與 CI)實際上永遠只印「這次不查」,等於沒上線,而 RETIRE-IF 的「抽查帳上擋下的名稱」永遠抽不到東西(零擋下),會被誤判成「零觸發該降級」。
4. 提交時(起點 = HEAD)走磁碟,0.09 秒,量不出這個問題,所以〈實務隱患〉的「實作時量一次推送多幾秒」只在提交側量會得到好看的數字。
5. 修法方向:起點與主線改走 `_nodehome_cat_blobs` 批次讀(或 `_nodehome_side` 的 share/changed:只讀範圍內有變動的筆記,沒變動的筆記名稱用終點那版,因為沒變就一樣)。這會改變「全庫起點集合」的算法,所以要照字面接一次再量。
6. 同類:上限用完時剩下的名稱「連不用 git 的第①道也不做」。本 repo 量到 20 個不存在的名稱第①道只要 0.12 秒、20 個真名稱兩道都過 0.84 秒(每個約 0.04 秒,不是 spec 說的 0.2 秒),而〈做法〉4 的順序是名稱去重後一個一個送 `_dispositions_check_test`、沒有先把全部名稱過一遍便宜的第①道。名稱上千個時(例如 regen 重建或整批匯入的筆記),只查得到前面一小段,後面連肯定指不到的也直接放行,而且報告只有一行「這次不查」。

## F2 主線名稱集合沒有「已包含終點」的守衛:CI 推主線、或本機主線沒設 upstream 時,整組規則什麼都擋不到
severity: major
blocking: 是
引句:「主線那一版同樣讀一次(`_mainline_ref` 找得到才讀)。」
引句:「起點集合 = 起點那一版整個知識庫出現過的名稱,再加上主線現在那一版知識庫的名稱(找得到主線時;」
file: `scripts/lumos:27220`(`_ns_exclusions`:docstring 寫「CI 上本地 main 追蹤的 origin/main 就是這次推上來的頂端,拿它排除等於整批不查」,所以只留「沒有已經包含 tip」的參照)
file: `scripts/lumos:38736`(`_mainline_ref`:remote_only=False 時 upstream 找不到會退到本地 `main`/`master`;docstring 寫「推主線時本地 main 就是要推的頂端,拿它當已在主線上會把整批都排除掉」)
1. 同一個 repo 裡已經有兩次踩過這個坑的紀錄,`_notelines_range_added` 的排除路徑用 `_ns_exclusions` 擋掉,但 spec 的主線名稱集合只寫了「`_mainline_ref` 找得到才讀」,沒寫 remote_only,也沒寫要先確認主線沒有包含終點。
2. 實驗一(模擬 CI,doctor 給的步驟:bare remote、clone、`git branch --track main origin/main`、HEAD = 剛推上來的頂端):`_mainline_ref(root, remote_only=True)` 回 `('main@{upstream}', e5b4e45…)`,等於 HEAD 的 sha;`_ns_exclusions(root, HEAD)` 回 `[]`(它正是為了把這種情形濾掉)。如果主線名稱集合照字面直接用 `_mainline_ref` 的結果,終點整個知識庫的名稱都在「主線現在那一版」裡,每個名稱都不算新加,CI 對推主線一個都擋不到。
3. 實驗二(本機沒設 upstream):`git branch --unset-upstream main` 後 `_mainline_ref(root)`(spec 沒寫 remote_only,預設 False)回 `('main', e5b4e45…)`,也等於終點。這個 repo 的使用者慣例是用 worktree 開工、直接在 main 上推,新 worktree 或新 clone 沒設 upstream 很常見。
4. S3、S29 的測試是「合進主線、主線那段新加壞名字不算在這次推送」,方向剛好相反的情形(主線比終點多東西)才會綠,擋不住「主線 = 終點」,所以這兩條測試過了也看不出來。
5. 修法方向:主線名稱集合用 `_ns_exclusions` 同一個判法(只收 remote_only 的 upstream、而且 `merge-base --is-ancestor <終點> <主線>` 不成立的才用),並加一條測試:CI 形狀(origin/main == 終點)下,新加的壞名字照擋。

## F3 1c 的「舊條目」比對只涵蓋區塊寫法的摘要,計劃正文的條款定義行與單行 summary 永遠判成新寫,S12 對它們不可達、會誤擋
severity: major
blocking: 是
引句:「當作廢條目在起點就已標作廢、這次只是重排折行或改了別的字時,note-shape 應不擋」
引句:「不是舊條目(新寫的),或是舊條目但起點那條還沒標作廢(這次才在舊行補上 `[status:superseded]`,rtb 那 12 條的寫法)→ 違規;」
file: `scripts/lumos:28175`(`_ns_slot_key`:行首不是 `SYMBOL_RE` 的前綴就回 None)
file: `scripts/lumos:28208`(`_ns_is_old`:key 是 None 回 `(False, False)`)
file: `scripts/lumos:28292`(`_ns_base_summary_lines`:舊行只來自起點那一版 `_ns_summary_logical` 的區塊摘要)
file: `scripts/lumos:28148`(`_ns_summary_logical`:只認 `summary:` 之後縮排的區塊行)
1. 實驗:`m._ns_slot_key("- [S1] 當 X 時,應 Y [status:superseded] [被取代:[[Z]]] [test:t_live]")` 回 `None`;`m._ns_is_old(None, …)` 回 `(False, False)`。條款定義行不是 `前綴:` 開頭,而且在正文,舊行來源(起點摘要邏輯行、diff 刪掉的摘要行)裡也沒有正文行。
2. 結果:凡是在 rows(新寫的行)裡的條款定義行,只要帶 `[status:superseded]` 又指得到活測試,一律當「這次才作廢」擋下,不管起點那一版是不是已經標作廢。S12 的情境(起點已標作廢、只改了別的字)對條款行永遠擋錯;但 spec 又明寫條款定義行要算 1c(rtb 那 12 條就是計劃條款行),也就是這個規則的主要對象正好被誤判。
3. 單行寫法的 summary 同樣:`summary: "WHY:… [status:superseded]…"` 在 `_notelines_regions` 是 `other`,`_ns_summary_logical` 回 `{}`(實驗:`m._ns_summary_logical(t)` 對單行 summary 的文字回 `{}`),所以起點那一邊也查不到舊條目,整條判成新寫。spec 做法 1 為單行 summary 補了抽取(`_note_summary_entries` 的補法),但 1c 要的「起點那條有沒有標作廢」的來源沒補。
4. 這是 `_ns_is_old` 的天然範圍(它是為格子的摘要行設計的),spec 把它說成可以通用到「計劃條款定義行」。要嘛為正文條款行另寫舊行比對(用起點那一版同一支抽取,以條款編號為鍵最直接),要嘛把 S12/S24 縮成只管摘要條目並明講條款行「只要碰到又掛活測試就擋」。

## F4 1c 只看「這次才標作廢」,已作廢的條目這次新掛上活測試照樣放行
severity: major
blocking: 是
引句:「起點那條就已標作廢(只重排折行、或碰到舊帳)不算。」
file: `scripts/lumos:28208`(`_ns_is_old` 回 `(算不算舊, 對上的舊條目有沒有標作廢)`,只比核心句與連結,不比 `[test:]` 的值)
1. 實驗:舊條目 `PITFALL:坑 [出處:a] [根因:b] [test:t_dead] [status:superseded] [被取代:[[Y]]]`,新條目在同一條上把 `[test:t_dead]` 改成 `[test:t_dead, t_live]`:`_ns_is_old(_ns_slot_key(new), _ns_old_keys([old]))` 回 `(True, True)`,1c 照 spec 放行。`t_live` 是這次新加的名稱,判存在那組會驗它是真測試(指得到),也放行。兩條規則各自都過,結果是一條已作廢的條目被新掛上一支活測試,正是路線圖 1c 要擋的「撤除的東西不准再掛活測試」。
2. 同形:舊條目標作廢時 `[test:]` 是指不到的死名,後來改成另一支存在的測試名(改名、把別條的測試搬過來),同樣放行。
3. 修法方向:1c 的判定改成「這次新出現的活測試名稱(不在起點那一條的名稱集合裡)掛在已作廢的條目上」或「條目作廢且新加了活測試」也算違規;起點那條已作廢且名稱沒增加才放行。

## F5 `_dispositions_check_test` 對 git 出錯與子模組回的是「指不到」,spec 的判不了(含外層 try/except)接不到,會擋錯
severity: major
blocking: 是
引句:「判不了(不擋、印一行):git 出錯或逾時、平台根在 repo 外或是子模組(只做第①道,第①道過就算指得到)」
引句:「外面包例外——丟例外(含 git 逾時)算判不了。」
file: `scripts/lumos:41244`(`_dispositions_check_test`:rc 1 與 rc 非 0/1 都是 `return False, "…"`;只有 `relative_to` 失敗與 `TimeoutExpired` 的路徑不同)
1. 實驗一(子模組):mini repo 設 `platforms.sm.root = vendor/sub/tests`(`vendor/sub` 是 `160000` 的子模組,裡面有 `def t_sub_one()`)。`_dispositions_check_test(rr, None, "test:sm:t_sub_one", pidx)` 回 `(True, '')`;帶 `at_sha` 回 `(False, "測試 't_sub_one' 在推送版本 83f799ce 的樹裡整字 grep 不到(未追蹤/未提交的測試不算證據)")`。`relative_to` 不丟例外,git grep 對子模組路徑回 rc 1(靜默沒有結果),函式回 False,呼叫端分不出這是「指不到」還是「子模組判不了」。
2. 實驗二(git 出錯):`_dispositions_check_test(rr, "deadbeef…(40 碼不存在)", "test:py:t_main_one", pidx)` 回 `(False, "測試 't_main_one' 無法對推送版本的樹驗證(git grep rc=128:fatal: unable to parse object: …)")`,是回傳值不是例外。spec 的外層 try/except 只攔例外。S26 要求「git 出錯」不擋,字面實作會擋。
3. 另一種子模組寫法:平台根在子模組「裡面」(上面實驗就是),「平台根是子模組」字面也只涵蓋根本身就是子模組的情形;spec 沒寫怎麼偵測(`git ls-tree` 看 160000、或路徑任何一段是 gitlink),實作者要自己發明。
4. 修法方向:`_dispositions_check_test` 補第三種回傳(例如 `(None, 原因)` 表示判不了:rc 非 0/1、gitlink、symlink 路徑),表態閘一起受益;並用 mini repo 加兩條測試:子模組根、不存在的 at_sha。S26 的測試名 `t_note_shape_test_refs_undecidable` 目前只寫了例外/逾時/Python 類別。

## F6 平台前綴後的空白與空名稱沒有處理:`[test:py: t_x]` 誤擋、`[test-gone:py:]` 空名稱放行、`,` 結尾的空片段未定義
severity: minor
blocking: 否
引句:「值再用半形或全形逗號切開、去前後空白;設定有 `platforms` 時可帶 `平台:` 前綴,沒有時整串當名稱。」
引句:「驗的是內容:名稱不能是空的或佔位字,而且現在不能指得到真測試(還指得到就是假話)。」
file: `scripts/lumos:40910`(`_dispositions_split_test`:`plat, name = body.split(":", 1)` 不去空白)
file: `scripts/lumos:5169`(`resolve_test_refs`:合約行那條路徑對 plat 與 name 都 `.strip()`)
1. 實驗:`_dispositions_split_test("test:py: t_main_one", {"py":1}, "py")` 回 `('py', ' t_main_one')`,名稱帶前導空白,`' t_main_one' not in methods_for` 於是第①道判「掃不到」。同一個名稱放在合約行,`resolve_test_refs` 會 strip 後判存在。spec「去前後空白」是切逗號之後整段去,前綴後面那個空白沒人處理。
2. `_dispositions_split_test("test:py:", {"py":1}, "py")` 回 `('py', '')`。`[test-gone:py:]`:整個值非空(`py:`)通過 `slot_check` 的「名稱非空」,去掉前綴後名稱是空的,而空名稱「不指得到」,所以 test-gone 被當成合法。佔位字那條寫的是「去掉平台前綴後」,空名稱那條沒寫,兩邊不一致。`[test:py:]`(新寫的摘要條目)不會被「方括號沒有名稱」那條抓到(括號裡有 `py:`),會走到判存在,以「掃不到」的訊息擋下,訊息不好但至少有擋。
3. `[test:a,]`、`[test:,]`:`slot_parse` 回 `'a,'`、`','`,切逗號後有空片段。`invariant_test_refs` 會濾掉空片段,spec 沒寫,實作者各猜。
4. 單平台設定(沒有 `platforms`)帶冒號的名稱:`_dispositions_split_test("test:a::b", {}, "py")` 回 `(None, "這個專案沒開多平台…不支援平台前綴 'a'")`,跟名詞定義的「沒有時整串當名稱」不一致(合約行那邊 `resolve_test_refs` 是整串當名稱)。結果同樣是指不到(識別字不含冒號),只有訊息不同,所以只列在這條。
5. 另外,全形冒號只在「鍵」那一層(`[test：x]`)被 `slot_parse` 收,平台分隔符 `py：t_x` 不收,會整串當名稱。S10 的測試是「全形冒號」,但只測鍵層就會綠。

## F7 擋下訊息與帳本裡的名稱沒有控制字元與長度上限
severity: minor
blocking: 否
引句:「印筆記、行號、名稱、`_dispositions_check_test` 給的原因與改法」
引句:「多一個 `test_refs` 鍵(條數、前 20 個名稱與各自原因)」
file: `scripts/lumos:10468`(`_esc_clean`:既有的控制字元消毒與截斷)
file: `scripts/lumos:28685`(`_note_shape_report` 對路徑與片段都 `_esc_clean`,註解寫明片段是筆記原文、檔名可夾 ESC 序列)
1. spec 只說「印的筆記路徑照既有的跳脫」。名稱是 `slot_parse` 從筆記原文切出的字串,可以含 ESC(`[test:x\x1b]` 這種,值裡沒有 `]` 就不需要閉合巧思)、C1 控制碼,直接印到終端,是既有程式碼已經防過的同一類(代碼審資安席)。
2. 帳本:前 20 個名稱沒有長度上限。一個 1MB 的名稱(`[test:AAAA…]`,`slot_parse` 不限長度)進 `extra`,治理帳一行就是幾 MB;`_SLOT_METRIC_MAX_WEEKS` 旁邊的註解寫明治理帳只讀檔尾 24MB,幾筆就能擠掉別的事件。`_dispositions_check_test` 把這種名稱放進 `git grep -e` 參數,超過 argv 上限會丟 OSError,被判成「判不了」不擋,所以惡意或誤貼的長名稱反而讓自己放行。
3. 修法方向:名稱印出與入帳前走 `_esc_clean(名稱, 200)`,長度上限在抽取層就收,過長算違規或略過並印一行。

## F8 正文抽取用的 `_visible_lines` 不懂縮排 4 格的圍欄與 HTML 註解,範例名稱會被當真名稱誤擋
severity: minor
blocking: 否
引句:「程式碼圍欄裡的不算。」
引句:「正文用 `_visible_lines` 略過圍欄」
file: `scripts/lumos:4157`(`_visible_lines`:圍欄標記縮排 ≤3 格才算,docstring 寫明「不偵測 HTML 註解」)
1. 實驗(`e5.py`):正文有 `1. 項目` 底下縮排 4 格的 fenced 區塊,裡面寫 `範例 [test:t_in_nested_fence]`;`_visible_lines` 回的可見行包含第 7、8、9 行(把 4 格縮排的 ``` 當一般文字),`t_in_nested_fence` 被抽成真名稱。`<!-- [test:t_in_comment] -->` 同樣可見。兩者新寫就會被當新加名稱、指不到、擋下。S9 的測試只涵蓋頂格圍欄。
2. 本 repo 現在沒有縮排 4 格的圍欄(`grep -rlE '^( {4,}|\t)(```|~~~)' docs/…` 無輸出),但消費專案與巢狀清單裡很常見;`clause_bindings` 同樣有「HTML 註解不特別處理」的已知取捨,只是它的失敗是報錯不是靜默。
3. 修法方向:S9 補一條縮排與註解的邊界測試;或明講這兩種是已知會誤擋、用 `[test:` 前寫成反引號包起來避開。

## 實務隱患鏡頭

- 誤擋:見 F3(條款行與單行 summary 的 1c)、F5(git 出錯與子模組)、F6(前綴後空白)、F8(縮排圍欄、註解)。另一個真實存在的舊寫法 `[test:t_slim_install_filesystem_error_reports_cleanly_without_traceback 綁的是 traceback 那半,不是早退那半]`(本 repo 有一處):名稱後面接說明並含半形逗號,切逗號後變成兩個「名稱」,都指不到;新寫這種行會被擋,訊息會列出兩個奇怪的名稱。可以接受(規則本意就是只放名稱),但改法訊息要提示「說明請移出方括號」。
- 漏網:見 F2(主線 = 終點)、F4(已作廢條目新掛活測試)、F1 第 6 點(上限用完剩下的連便宜的第①道都不做)。
- 時間:見 F1;另外 `_dispositions_check_test` 的單次 git 預設上限是 8 秒(`_disp_git_timeout`),一個慢 git 就吃掉 20 秒的 40%。
- 起點空樹:`base_where=None` 時 `_nodehome_list(None)` 回 `({}, [])`,起點集合為空,所有新寫行的名稱都算新加。`_lens_push_base` 找不到主線(例如新專案第一次推、或 CI 沒建本地 main)會回空樹,這時整個知識庫的舊壞名稱(本 repo 量到 26 個)第一次推送就全被擋。這跟其他 note-shape 規則「從空樹算、截到上線點」同一個行為,而且上線點存在時 `_nodehome_clamp_base` 會把起點截到上線點,所以只有「沒有上線點也找不到主線」的專案會中;spec 沒提這一種,建議在〈漏網〉或〈相容〉補一句、並給 `warn` 的退路提示。已讀,沒有獨立 finding。
- 淺層 clone:`cmd_note_shape` 在 `--diff` 模式遇到淺層 clone 就整個跳過並記 `skipped-env`,這組規則不會走到,已讀,無 finding。提交時 HEAD 不存在(第一個提交)`base_where=None`,起點集合為空,但提交時只提醒,已讀,無 finding。
- 多平台 / 單平台:單平台(legacy)預設 `csharp-xunit` 且沒有設定檔時,`methods_for` 掃不到任何 Python 測試,spec S14「掃不到任何測試方法 → 那個平台不查」有涵蓋,已讀,無 finding。多平台時裸名歸 default_platform,測試實際在別的平台會誤擋,訊息會寫「在平台 X 的工作樹掃不到」,可接受。
- 「類別.方法」只認方法名那段(`_classify_test_refs` 同款 `rsplit('.', 1)[-1]`):`Other.t_x` 在 `Other` 類別不存在、只要別處有 `t_x` 也判指得到。這是既有合約行判法的同一取捨,不另列。
- 作廢條目的各種改法:補 status(F3、F4)、只改 `[被取代:]`(起點已作廢,不擋,符合 spec)、刪 status(不算作廢,不查)、`[status: Superseded ]` 空白與大小寫(`_ns_superseded` 都收,實驗確認)、`[status:被取代]`(不收,符合「只認 superseded」)、兩條同核心句一條作廢一條未作廢時 `_ns_is_old` 回 `(True, True)`(取 any),短核心句撞鍵會讓新作廢的條目被當成「舊條目且起點已作廢」而放行;屬於既有函式的已知取捨,不另列。
- `[test-gone:]` 的鍵:`test-gone` 9 個字元,在 `_SLOT_KEY_RE` 的 12 字上限內,大小寫由 `_SLOT_CANON` 收,實驗確認登記後可被 `slot_parse` 解出;`[test_gone:x]`(底線)不是鍵,整段變核心句,名稱完全不被查,但 PITFALL 會被格子的三選一抓到,非 PITFALL 條目拿它沒意義,不列。

## 逐節交代
- 白話、依據、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding(RETIRE-IF 的「抽查帳上擋下的名稱」受 F1 影響,見 F1 第 3 點)。
- 名詞:F2、F3、F5、F6 涵蓋。
- 範圍:已讀,無獨立 finding。
- 做法 1 抽取:F6、F8。做法 2:已讀,無 finding(`keep_other` 與 `_notelines_rows` 的 `texts` 比對讀過,單行 summary 在 `other` 區塊會進來)。做法 3:F1、F2。做法 4:F1、F5。做法 5:F3、F4、F6。做法 6、7:已讀,無 finding。做法 8:F7。做法 9:F6。做法 10:已讀,無 finding(doctor 只做第①道,不涉及 F1 的讀檔)。做法 11:已讀,無 finding。
- 條款:S3、S29 見 F2 第 4 點(測試方向);S12、S24 見 F3;S26 見 F5;S9、S10 見 F6、F8。其餘已讀,無 finding。
- 回退、實務隱患:已讀,無 finding。

最高等級:major,blocking 共 5 條
