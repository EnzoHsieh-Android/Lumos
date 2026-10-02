severity: major

# 設計審 整合-sonnet 席(整合與接手鏡頭)

做法:照計劃逐步當實作者寫出每一步要呼叫哪支既有函式、傳什麼、從哪拿,在 `git clone --shared` 的臨時 repo(`scratchpad/tb4-r1-work-整合-sonnet/`)用真函式跑過。下面每條 major 都有當場能重現的實驗或明確標「未實測,依據是讀碼」。

## F1 主線那一版用 `_mainline_ref` 預設參數,CI 與沒設 upstream 時主線等於推送終點,整組規則永遠不擋
severity: major
blocking: 是
引句:「主線那一版同樣讀一次(`_mainline_ref` 找得到才讀)」
file: `scripts/lumos:38736`(`_mainline_ref` 預設會退到本地 main,且 `main@{upstream}` 優先)
file: `scripts/lumos:27220`(`_ns_exclusions` 為同一個坑寫的「主線已包含 tip 就不算」過濾)
1. 計劃第 3 步要把「主線現在那一版知識庫的名稱」併進起點集合,但只寫「`_mainline_ref` 找得到才讀」,沒寫要不要 `remote_only`、也沒寫「主線已包含終點就不用」。
2. 照字面呼叫 `_mainline_ref(root)`:CI 上 `actions/checkout` 之後本地 main 追蹤的 origin/main 就是這次推上來的頂端;本機推 main 且沒設 upstream 時退到本地 main,也等於頂端。這時「主線那一版」= 終點那一版,終點每個名稱都在起點集合裡,「新加的測試名」恆為空,S1、S7、S28 在 CI 與這兩種本機情形永遠不擋。
3. 同一個坑 note-shape 自己已經踩過並寫進 `_ns_exclusions` 說明(「CI 上本地 main 追蹤的 origin/main 就是這次推上來的頂端,拿它排除等於整批不查」),計劃沒有指到這支。
4. 重現(CI 形狀的 clone,`main` 追蹤 `origin/main` 且同一個 sha):
   `cd tb4-r1-work-整合-sonnet/ci/c2 && /opt/homebrew/bin/python3 ../p2.py`
   輸出:`tip 17cf432f…` / `mainline_ref default ('main@{upstream}', '17cf432f…')`(同一個 sha)/ `exclusions []`。
5. 影響:本地推 feature 分支時有擋,但 CI 這道後盾(計劃寫「推送時與 CI 擋」)在最常見的「push 到 main」事件上是空的,S29 與 S1 用不同夾具會一個綠一個紅(夾具若只做 feature 分支就看不出)。

## F2 起點與主線整個知識庫用 `_nodehome_reader` 逐篇 `git show`,本 repo 一個版本就要約 17 秒,共用 20 秒上限一定先被吃光
severity: major
blocking: 是
引句:「`_nodehome_list` 列檔、`_nodehome_reader` 讀內容,跟 note-shape 讀終點同一套」
file: `scripts/lumos:26138`(`_nodehome_reader`:只有「讀的版本就是 HEAD」才走磁碟,其餘每篇一次 `git show` 子程序)
file: `scripts/lumos:28378`(`_note_shape_eval` 讀整個圖譜時用的是 `_nodehome_cat_blobs` 批次讀,不是 reader)
1. 計劃第 3 步說讀起點與主線兩個版本的整個知識庫,「跟 note-shape 讀終點同一套」。但 note-shape 讀整庫(喚醒舊引用那段)用的是 `_nodehome_cat_blobs` 一次批次,`_nodehome_reader` 只用來讀個別候選檔。
2. 推送時起點、主線都不是 HEAD,reader 的磁碟捷徑不成立,每篇一個 `git show`。實測本 repo(673 篇):
   `/opt/homebrew/bin/python3 ../p3.py` 輸出 `150 reads 3.86s`(約 26ms/篇,外推 673 篇約 17 秒)、`batch all 0.158s`(同樣 673 篇用 `_nodehome_cat_blobs` 批次)。
3. 起點 + 主線兩個版本 ≈ 34 秒,計劃第 4 步寫「整組(讀起點、判存在)共用一個 20 秒上限,用完剩下的名稱這次不查、印一行」。結果:本 repo 只要這次推送有任何新加的測試名,讀起點就把預算吃光,判存在整段被跳過,規則在這個 repo 實質上推送時不運作(fail-open 只印一行)。消費專案圖譜更大(rtb 計劃正文就有 57 個懸空名稱,篇數只會更多)。
4. 提交時(staged)也一樣:HEAD 在 feature 分支時主線那一版也不是 HEAD,每個含測試名的提交多等最多 20 秒。單次跳過那條路徑(第 8 步要「先算一次」再放行)同樣先付這筆時間才放行,逃生口變慢。
5. 修法選項(實作者必須自己選):改用 `_nodehome_cat_blobs`(eval 內已有先例),或限定只讀「有 `test` 字樣的篇」。計劃沒寫,字面實作走 reader 這條。

## F3 1c 的「起點那條有沒有標作廢」要的舊行來源沒定義:借 `_ns_slots_old_lines` 但容器不帶 `texts2` 時,新行會比對到自己,1c 在推送時永遠不擋;且 1c 要查的舊名稱不在第 4 步的輸入裡
severity: major
blocking: 是
引句:「不是舊條目(新寫的),或是舊條目但起點那條還沒標作廢」
file: `scripts/lumos:28193`(`_ns_old_keys(logical, physical)`:physical 的每一行都併進 text 桶)
file: `scripts/lumos:28264`(`_ns_slots_old_lines`:推送時把「摘要新行裡不在 `texts2` 的」全部放進 physical)
file: `scripts/lumos:28208`(`_ns_is_old` 回 (算不算舊, 對上的舊條目有沒有標作廢))
1. 計劃只說「用格子的舊行判定 `_ns_is_old`」,沒寫 `_ns_old_keys` 的 logical、physical 兩個參數從哪來。唯一現成的產生者是 `_ns_slots_old_lines(repo_root, staged, base_where, tip_where, vault_rel, notes, sink)`。
2. 它在推送時 `phys += 每條摘要新行 (ln.strip() not in sink["texts2"])`;`texts2` 只在 eval 的容器帶了 `mark2`(格子上線記號)才會有。計劃第 2 步說「這組傳自己的容器」,沒有 `mark2`(格子沒上線、`note_shape.slots: off` 的專案本來就是這樣)→ `texts2` 缺 → 每條新摘要行都進 physical → 新行拿自己當舊行。
3. 最小實驗(舊條目 `PITFALL:… [test:t_live]` 在第二個提交補 `[status:superseded] [被取代:無 撤了]`,正是 S11 的情形):
   `cd tb4-r1-work-整合-sonnet/e1 && /opt/homebrew/bin/python3 ../p5.py <起點sha> <終點sha>`
   輸出:`old (['PITFALL:舊的坑 … [test:t_live]', 'PITFALL:舊的坑 … [test:t_live]'], ['PITFALL:舊的坑 … [test:t_live] [status:superseded] [被取代:無 撤了]'])`,然後 `5 (True, True)`。也就是判成「是舊條目、起點就已標作廢」→ 1c 放行,S11 照字面實作會綠不了。只用 logical(起點版本加刪掉的行,不併 physical)才得 `(True, False)`。
4. 計劃沒寫 1c 該用「只含起點版本的整條」這個子集;兩種選法在有 `mark2` 時行為還不同(帶 `mark2` 時 physical 含格子上線前的提交行,等於把「上線前就標作廢」的算舊;不帶時全算舊)。這是「條款只在一種實作成立」。
5. 另一個接點洞:1c 要對「這次才變成作廢的條目」判活測試,但那個條目上的名稱(如 `t_live`)本來就在起點集合裡,不是第 3 步算出的「新加的測試名」。第 4 步「有要查的名稱時才 `_platform_test_index` 一次,名稱去重後每個交給 `_dispositions_check_test`」的「要查的名稱」沒說包含 1c 這批舊名稱;字面只拿「新加的」去查 → S11 的 `t_live` 根本不會被判存在。

## F4 1c 的舊行判定只認摘要前綴行;計劃條款行(正文)、單行寫法 summary 沒有舊行可比,舊條目會被當新寫誤擋
severity: major
blocking: 是
引句:「但它們標了作廢還掛活測試時照樣算 1c(rtb 那 12 條就是計劃條款行)」
file: `scripts/lumos:28167`(`_ns_slot_key` 開頭 `SYMBOL_RE.match`,不是前綴行回 None)
file: `scripts/lumos:28148`(`_ns_summary_logical` 不收 `summary: "…"` 單行那一行,該行區塊是 other)
1. 計劃把條款定義行與合約行納入 1c,又說 1c 以 `_ns_is_old` 判「這次才標作廢」。`_ns_is_old(None, …)` 恆回 `(False, False)`,而 `_ns_slot_key` 只對 `WHY:`/`RULE:`/… 前綴行回鍵。
2. 實測:
   `/opt/homebrew/bin/python3 ../p4.py` 輸出 `slot_key body: None` 與 `(False, False)`(行 `- [S1] 當 X 時應 Y [test:t_a] [status:superseded] [被取代:無 撤除]`)。
3. 後果:計劃條款行只要被動到(改個字、重排)而且已經是作廢帶活測試,就走「不是舊條目(新寫的)→ 違規」。S12(起點就已標作廢、只改別的字應不擋)對條款行與合約行以外的正文行無法成立;1c 的「既有的不擋」承諾對條款行破功,會把舊帳當新違規擋下。
4. 單行寫法 summary(S21 要求抽得到)同理:起點版本的單行 summary 不在 `_ns_summary_logical` 結果裡,`_ns_slots_old_lines` 的 base_lines 為空,該條永遠被判新寫。這點未實測,依據是讀碼(`_ns_summary_logical` 對 region 非 summary 的行直接 `last = None`)。
5. 計劃沒有條款行與單行 summary 的舊行比對法;S12/S24 的夾具只要選了前綴行或只選新條款行就看不出。

## F5 「git 出錯」與「平台根是子模組」在 `_dispositions_check_test` 裡不丟例外,第 4 步的「外面包例外」接不住,S26 不能實作
severity: major
blocking: 是
引句:「外面包例外——丟例外(含 git 逾時)算判不了」
file: `scripts/lumos:41244`(`_dispositions_check_test`:`git grep` rc 非 0/1 回 `(False, "…無法對推送版本的樹驗證(git grep rc=…")`,不丟例外)
1. 計劃把判不了拆成「丟例外」與名詞節列的「git 出錯、平台根是子模組」,以為都走 try/except。實際:只有 `subprocess.TimeoutExpired` 會丟;git 出錯是 in-band 的 `(False, 說明)`,與「指不到」同一個回傳形狀。
2. 實測 git 行為(臨時 repo):終點 sha 不存在 → `git grep` rc=128 → 函式回 `(False, "無法對推送版本的樹驗證…")`,呼叫端無法與「grep 不到」區分,只能比對字串。
3. 子模組:平台根在子模組裡時 `git grep <sha> -- ':(glob)ext/**/*.py'` 回 rc=1(沒命中,不是錯誤)→ 函式回 `(False, "…整字 grep 不到")` → 真測試被判指不到而擋。實驗:`tb4-r1-work-整合-sonnet/sm/main` 上 `git grep -w -F -q -e t_foo $T -- ':(glob)ext/**/*.py'` 印 `rc sub=1`(`ext` 是 gitlink、`t_foo` 在子模組內存在)。
4. 計劃補的是「類別.方法」與路徑跳脫,沒有寫「怎麼偵測子模組」(可用 `_nodehome_list` 的 160000 模式,但計劃沒指)、也沒寫要把 `(False, 無法…)` 改成三態。三態會動到表態閘現有的「無法驗證=擋」語意(`_dispositions_verdict` 對此文案處理),計劃只說「表態閘一起受益」。S26 依字面實作只能在例外一種情形成立。

## F6 「第①道沒過但測試檔裡有 `def 名稱(`」唯一現成載體是 `hay_for`,它掃的是全部程式檔不是測試檔,一般函式名也會被判成判不了而放行
severity: major
blocking: 是
引句:「第①道沒過但測試檔裡有 `def 名稱(` 這種 profile 認不得的寫法」
file: `scripts/lumos:6704`(`clause_bindings` 的 `unrecognized` 分支:用 `hay_for(pl)` 做 `^\s*def\s+名稱\s*\(`)
file: `scripts/lumos:12856`(`_platform_test_index` 的 `hay_for` = `build_code_haystack`,掃 repo 內所有程式副檔名,不限測試檔)
1. 計劃寫「測試檔裡」,但 PRIOR-ART 只列了條款綁定既有的「設定認不到」,而那支用的 `hay_for` 是整個 repo 的程式字串。
2. 實測(本 repo,Python 平台):`hay` 內 `^\s*def\s+_git\s*\(` 與 `^\s*def\s+main\s*\(` 皆為 True(`scripts/*.py` 內的一般函式)。第①道對 `cmd_note_shape` 判「掃不到」,但 `[test:main]` 或 `[test:run]` 這種「函式名不是測試」會落到「判不了、不擋」。計劃 r2 折入的例子(「`[test:cmd_note_shape]` 函式名不是測試 → 擋」)只在該函式剛好寫在沒副檔名的 `scripts/lumos` 時成立。
3. 若實作者改為「只掃測試檔」,要自己用 `_walk_test_files` 重做一份,計劃沒指名、也沒說快取;兩種選法分別讓 S1(函式名不算測試)或 S30(Python 類別裡的測試判不了)其中之一在不同夾具下才成立。
4. 驗證指令:`cd tb4-r1-work-整合-sonnet/repo && /opt/homebrew/bin/python3 ../probe1.py` 末三行印 `_git True`、`main True`。

## F7 `_note_shape_eval` 只有一個 `slots` 容器參數,「這組傳自己的容器」無法照字面做;選錯會弄壞格子規則
severity: minor
blocking: 否
引句:「這組傳自己的容器、帶 `keep_other` 讓單行寫法的 summary 也進來」
file: `scripts/lumos:28378`(`_note_shape_eval(..., slots=None)` 只收一個容器,內部 `_notelines_new(... keep_other=True, mark2=…, sink=slots)`)
file: `scripts/lumos:28551`(`cmd_note_shape` 把 `slots` 傳 eval 後又傳給 `_ns_slots_collected`)
1. `keep_other=True` 在 eval 內早已固定,不需要「帶」;要多出一個容器參數,簽名得改,計劃沒列。
2. 兩種自然的做法都有坑:(a) 用自己的 `{}` 取代 `slots=` → 格子開著時格子拿不到 `mark2`/`texts2`,格子規則推送時行為變(既有 `t_note_shape_slots_*` 會紅);(b) 共用格子容器 → 格子 off 時 `_ns_slots_prepare` 回 None,test_refs 沒有 `notes` 可讀,而若為此替它補 `{}`,`_ns_slots_collected(…, slots)` 就會對 off 的格子照算。
3. 既有格子測試會抓到這類回歸,所以評為 minor;但計劃應寫明「eval 多一個參數」或「統一從 `slots['notes']` 讀、格子 off 時另開旗標」。

## F8 S31 的夾具必須把測試放在平台根的子目錄裡,放在根目錄第一層時不跳脫也找得到(測試不會先紅)
severity: minor
blocking: 否
引句:「平台根路徑含 `[` `]` 時,`_dispositions_check_test` 的第②道應照樣找得到真測試」
file: `scripts/lumos:41290`(`:(glob){_base}**/*{e}` 組路徑)
1. 實測 git 2.39:根 `app[x]`、測試在 `app[x]/test_a.py`:`:(glob)app[x]/**/*.py` 回 rc=0(git 先做字面前綴比對,沒跳脫也找得到);測試在 `app[x]/sub/deep/test_d.py`:同樣的 pathspec 回 rc=1,`:(glob)app\[x\]/**/*.py` 回 rc=0。
2. 實驗:`tb4-r1-work-整合-sonnet/gl` 內 `git grep -w -F -q -e t_deep HEAD -- ':(glob)app[x]/**/*.py'` 印 `deep rc=1`,跳脫版印 `escaped deep rc=0`。
3. 若 S31 夾具照直覺把測試放根目錄第一層,跳脫前後都綠,「先紅」規則(全域鐵則)失效。另有反向副作用:未跳脫的 `a[bc]` 會讓 `ab/` 底下的測試也算命中(`cross-hit ab rc=0`),跳脫正好修掉。夾具須含深一層的測試並可再放一個鄰近目錄的同名測試驗不誤中。

## F9 帳本與報告接線:`check` 欄是單值且是去重鍵、`_note_shape_report` 沒有放這組模式的位置、單次跳過路徑沒法照 `_ns_skip_slot_extra` 照抄
severity: minor
blocking: 否
引句:「`extra` 裡既有的違規種類欄照既有寫法再多列一項」
file: `scripts/lumos:28375`(`_ns_slot_extra` 的 `check` 只有 "slots" 與 "shape+slots" 兩個字串)
file: `scripts/lumos:7991`(治理帳讀端去重鍵含 `r.get("check")`)
file: `scripts/lumos:28572`(跳過路徑的條件是 `staged and slots_flag`)
1. 「再多列一項」沒有可套的欄:`check` 是純字串,不是清單。只有 test_refs 擋下時 `kw` 目前只在 `sviol` 為真才有 `extra`,`check` 缺或為空 → 跟同提交同節點的純 shape 擋下事件在 `lumos gov` 讀端被去重折成一筆。要定義新的 `check` 值(如 "test_refs"、"shape+test_refs"…)與混合規則。
2. `_note_shape_report(root, mode, mode_word, viol, errs, slot=(smode, sviol))` 的 `blocked` 與 `nodes`、`count` 都只認 gate 模式與格子模式;test_refs 有自己的 block/warn、提交時一律 warn、保險時只提醒,需要新參數帶「有效模式」。計劃第 7 步只寫「呼叫條件加上這組違規」。
3. 第 8 步「照 `_ns_skip_slot_extra` 先算一次記進去(不靠 `--slots`)」:該函式在格子 off 時回 None,且呼叫端只在 `slots_flag` 為真時才叫它。要新寫一支合併版(格子 extra 加 test_refs extra,再跑一次 eval),也要改呼叫條件,計劃未寫。

## F10 doctor S20 的零件:`Note` 沒有全文、`_note_test_refs(text, is_plan, rows)` 沒有「全部行」的呼叫形
severity: minor
blocking: 否
引句:「用同一支抽取掃全庫(不限新寫行)」
file: `scripts/lumos:552`(`class Note` 的 `__slots__` 只有 `rel stem fields block_keys fm_lines targets lint mtime`,沒有 body/text)
file: `scripts/lumos:2365`(S5 的先例:`(env.vault / rel).read_text(...)` 再丟 `_clause_bindings_for`)
1. S20 要抽正文的 `[test:]`,但 doctor 手上的 `notes` 沒有全文,要像 S5 那樣逐篇重讀磁碟;計劃沒說。
2. 抽取簽名 `(text, is_plan, rows)` 中 `rows` 在「不限新寫行」(起點集合、doctor)時要傳什麼(None?全部行?)沒寫;第 3 步、第 10 步兩處都要用。
3. S20 位置(S19 之後、S8 之前)與「截斷測試窗口」我查過:截斷窗口是 `[S]` 到 `[E1]`,S19 在 E1 之後,不受影響。已讀,無衝突。

## F11 名詞定義與實際判定函式不一致,以及合約行/條款行的佔位字與空括號規則範圍矛盾
severity: minor
blocking: 否
引句:「設定有 `platforms` 時可帶 `平台:` 前綴,沒有時整串當名稱」
file: `scripts/lumos:40910`(`_dispositions_split_test`:含 `:` 且沒開多平台就回「沒開多平台,不支援平台前綴」,不是整串當名稱)
file: `scripts/lumos:5170`(`resolve_test_refs` 才是 legacy「整串當名稱」)
1. 計劃名詞說沒有 platforms 時整串當名稱,但判存在改借 `_dispositions_split_test`,對含 `:` 的名稱回 `(None, 原因)`。實測:`_dispositions_check_test(…, "test:Foo::bar", …)` → `(False, "這個專案沒開多平台…不支援平台前綴 'Foo'")`。含 `::` 的 Rust/C++ 名稱因此落在「指不到」並被第 5 步 S25 提示「改用 `[manual:]`」,對真測試是錯誤指引。兩處要擇一。
2. 範圍節寫「不做:合約行與條款定義行(各有檢查)」,第 5 步卻說佔位字與空 `[test:]` 規則對「新寫的摘要條目」一律違規,合約行也是摘要條目。字面實作會對新寫的 `KEY: ★INVARIANT★ … [test:待補]` 另擋一次(Check T 本就唸它)。需寫明這兩條規則是否略過合約行。

---

## 實務隱患(逐類)

- 時間與資源:F2(逐篇 `git show` 兩個整庫版本,本 repo 約 17 秒/版,共用 20 秒上限先耗盡)。抽取本身不貴:對 630 篇、約 65k 行全庫 `slot_parse` 約 0.3 秒、`clause_bindings` 全庫約 0.1 秒(`../p6.py`)。
- 誤擋:F3、F4(舊條目被當新寫)、F5 子模組、F6 反向(漏放而非誤擋)、F11(`::` 名稱)。
- 漏網:F1(CI 與沒 upstream 時整組空轉)、F6(一般函式名放行)。
- 相容與回退:新鍵 `test-gone` 進 `_SLOT_KEYS`:既有 `t_slots_single_table` 只比 `_keys <= set(m._SLOT_KEYS)`,不會紅(已讀 `scripts/test_lumos.py:30351`)。「類別.方法」補丁與路徑跳脫:現有表態閘測試沒有釘帶點的 `test:X.Y` 證據、也沒釘方括號根路徑(grep 無命中),不會翻紅;但這也代表現有表態閘測試完全沒覆蓋這兩條路,S23、S31 要靠新測試先紅(見 F8)。
- 並行會談:無新增風險,規則只讀;單次跳過路徑會先跑一次整組(F2、F9),放行前最多多等 20 秒。
- 帳本:F9。
- 金流、對外送出、不可逆:無(計劃已排除,我核對過:只讀筆記與測試檔、只印提醒)。

最高等級:major,blocking 共 6 條
