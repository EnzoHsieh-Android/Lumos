severity: major

# 筆記測試綁定要存在 設計審(另開一輪)— 正確性-opus

實驗都在 `tb4-r1-work-正確性-opus/repo`(對被審 repo 的 --shared clone,HEAD 9f9dd695)與同目錄的臨時 git 專案裡跑;以下 `$W` = `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/tb4-r1-work-正確性-opus`,實驗腳本 `$W/exp1.py`–`$W/exp6.py`、`$W/t_reader.py` 都留在那裡。

## F1 推送時照字面拿格子的舊行來源,每一條新寫的摘要條目都被判成舊的:1c 與佔位字/空名稱在推送時永遠擋不到
severity: major
blocking: 是
引句:「(1c)作廢的條目掛著活測試,而且這次才變成作廢:用格子的舊行判定 `_ns_is_old`」
引句:「這組傳自己的容器、帶 `keep_other` 讓單行寫法的 summary 也進來」
file: `scripts/lumos:28266`
file: `scripts/lumos:28284`
file: `scripts/lumos:28204`
1. 計劃只說用 `_ns_is_old`,沒說它要的 old 結構從哪裡來。現有程式裡唯一能做出這個結構的路是 `_ns_old_keys(*_ns_slots_old_lines(...))`。這支在推送模式會把 rows 裡「不在 `sink["texts2"]` 的摘要行」整批放進實體行來源(phys),`_ns_old_keys` 再把 phys 併進 text 桶。
2. 本案照〈做法〉2 傳的是自己的容器,沒有 mark2,所以 `texts2` 不存在。結果是每一條新寫的摘要行都進了 phys,自己對上自己,被判成舊條目;它自己身上帶的作廢標記,也就成了「對上的舊條目已標作廢」。消費專案還沒開格子時,就算借格子的容器也一樣:沒有提交帶格子記號,live2 是空的,所有行都進 pre2/phys。
3. 重現:`cd $W/repo && W=$W python3 $W/exp1.py $W/repo 'PITFALL:x 會壞 [test:t_live]' 'PITFALL:x 會壞 [test:t_live] [status:superseded] [被取代:[[B]]]'`(起點→終點兩個提交,呼叫 `_note_shape_eval(..., slots=box)` 後照格子那條路建 old)輸出:
   - `自帶容器 {} | 新行: PITFALL:x 會壞 [test:t_live] [status:superseded] [被取代:[[B]]] | _ns_is_old → (True, True)`。這正是 rtb 那 12 條的寫法,1c 判成「起點就已標作廢」放行,r3 標題那顆 blocker 原地重現。
   - 第二組 `'KEY:舊句' → 'PITFALL:全新一條 [test:待補]'`:`_ns_is_old → (True, False)`。全新的條目被當成舊條目,佔位字規則不看它,S28 擋不到。
4. 提交時 phys 是空的(`_ns_slots_old_lines` 的 `if not staged` 段不跑),判得對,但提交時本來就只提醒。所以這兩條規則在唯一會擋的時機(推送與 CI)永遠不擋,S11、S24、S4、S5、S20、S28 的推送情境都造不出來。
5. 計劃要寫明:old 只用「起點那一版的整條摘要行(第 3 步已經要讀)+這次刪掉的行」來建,`_ns_old_keys(logical, physical=())`,不經 `_ns_slots_old_lines`。

## F2 `_ns_is_old` 對「已作廢的條目改了核心句的字」、條款定義行(正文)、單行寫法的 summary 一律回「不是舊條目」,S12 照字面造不出來
severity: major
blocking: 是
引句:「當作廢條目在起點就已標作廢、這次只是重排折行或改了別的字時,note-shape 應不擋」
file: `scripts/lumos:28175`
file: `scripts/lumos:28208`
file: `scripts/lumos:3513`
1. `_ns_is_old` 比的是(前綴, 核心句文字鍵),核心句改一個字就對不上。重現:`cd $W/repo && python3 $W/exp2.py . 'PITFALL:x 會壞 [test:t_live] [status:superseded] [被取代:[[B]]]' 'PITFALL:x 會壞掉 [test:t_live] [status:superseded] [被取代:[[B]]]'`(old 只放起點那條,也就是 F1 修好之後的建法)輸出 `_ns_is_old → (False, False)`。照〈做法〉5「不是舊條目(新寫的)→ 違規」,修個錯字就被擋,跟 S12「改了別的字…應不擋」相反。
2. 條款定義行在正文,不是前綴行。`_ns_slot_key` 對它回 None,`_ns_is_old(None)` 固定回 `(False, False)`。同一支 exp2 帶 `'- [S3] 當 x 時應 y [test:t_live] [status:superseded]'` → `'- [S3] 當 x 時應該 y …'` 輸出 `_ns_slot_key(這次) → None`、`(False, False)`。S24 把 1c 擴到條款定義行,所以起點就已作廢、還掛活測試的條款行只要被碰到一個字、或在同篇裡搬位置(推送時逐提交新增的文字會再出現一次),就照 1c 擋,S12 對條款行永遠不成立。
3. 單行寫法的 summary(`summary: "PITFALL:… [status:superseded]"`)在 `_ns_summary_logical` 裡是 other 區塊,起點那版收不進 old(`_note_summary_entries` 的說明自己寫了「單行寫法的 summary 兩邊都漏」)。這種條目只要改了一個欄位就判成新寫,一樣違反 S12。
4. 要嘛 S12 收窄成「只重排折行、或只改欄位」,並明寫改核心句算新寫(配合條款行另寫判法);要嘛 1c 的「起點已作廢」改成「起點那一版同一篇有沒有同前綴、同一組測試名、已作廢的條目/同編號的條款行」。現在條款與機制互相矛盾,實作者兩邊都滿足不了。

## F3 起點與主線那一版用 `_nodehome_reader` 逐篇讀,本 repo 一版就要 14–15 秒,兩版直接吃光 20 秒預算,整組每次推送都不查
severity: major
blocking: 是
引句:「起點那一版整個知識庫用 note-shape 自己的讀檔零件(`_nodehome_list` 列檔、`_nodehome_reader` 讀內容,跟 note-shape 讀終點同一套」
file: `scripts/lumos:26138`
file: `scripts/lumos:26162`
1. `_nodehome_reader(root, where)` 只有 where 是 HEAD 或 index 時才讀磁碟。推送時起點是遠端舊頂端、主線是 `main@{upstream}`,兩者都不是 HEAD,每一篇都各開一次 `git show`。
2. 重現:`cd $W/repo && python3 $W/t_reader.py`(對 HEAD~5 的 629 篇筆記)兩次輸出 `reader per-file 629 notes 15.17 s` 與 `13.83 s`;同一批用 `_nodehome_cat_blobs` 批次讀只要 `0.19 s`/`0.17 s`。
3. 起點加主線兩版大約 28–30 秒,超過〈做法〉4 的整組 20 秒上限。照計劃「用完剩下的名稱這次不查、印一行」,本 repo 每次推送這組都在讀起點的階段就 fail-open,實務上等於 off;實作紀錄要量的「推送多幾秒」也會量到 20 秒。note-shape 讀全庫本來就用 `_nodehome_cat_blobs`(喚醒舊引用那段與 `_ns_base_summary_lines`),計劃挑錯了零件。

## F4 CI 推主線時,`_mainline_ref` 找到的主線那一版就是推送終點,起點集合吞下終點全部名稱,CI 永遠不擋
severity: major
blocking: 是
引句:「主線那一版同樣讀一次(`_mainline_ref` 找得到才讀)」
file: `scripts/lumos:38742`
file: `scripts/lumos:27220`
1. 計劃把「主線現在那一版知識庫的名稱」併進起點集合,條件只有「找得到」。CI 照 doctor 給的那一步會 `git branch --track main origin/main`,推上主線後 `origin/main` 就是這次的終點。這時主線那一版就是終點那一版,所有新加的名稱都在起點集合裡,沒有任何東西算新加。
2. 重現:`python3 $W/exp5.py`(bare 遠端、clone 後提交一個再推、fetch)輸出:`_mainline_ref(預設) → ('main@{upstream}', '1a54d8d0…')`、`_mainline_ref(remote_only=True) → ('main@{upstream}', '1a54d8d0…')`、`終點 = 1a54d8d0…`。既有的 `_ns_exclusions` 對同一個狀況回 `[]`:它先剔掉已經包含終點的主線,說明裡就寫了這個坑。
3. 本機的狀況:`git push -u origin main` 第一次推、本地 main 沒有 upstream 時,預設參數會落到本地 `main`,也就是終點,同樣整批算舊。計劃把 `--no-verify` 與「推的分支不是目前簽出那條」都交給 CI 接,這條讓主線推送的 CI 接不住。
4. 要照 `_ns_exclusions` 寫:用 `remote_only=True`,而且主線已經包含終點時不讀。

## F5 「判不了」三種裡有兩種,`_dispositions_check_test` 回的形狀跟「指不到」一樣,只包例外分不出來,照字面會擋(S26 造不出來)
severity: major
blocking: 是
引句:「外面包例外——丟例外(含 git 逾時)算判不了」
引句:「兩項都補在 `_dispositions_check_test`,表態閘一起受益」
file: `scripts/lumos:41272`
file: `scripts/lumos:41275`
1. git 出錯:`git grep` 回 rc≠0,1 時,這支不丟例外,回 `(False, "…無法對推送版本的樹驗證(git grep rc=…)")`。重現:`cd $W/repo && python3 $W/exp4.py`,at_sha 給 40 個 0,輸出 `(False, "測試 '…' 無法對推送版本的樹驗證(git grep rc=128:fatal: unable to parse object: …)") (沒丟例外)`。照〈做法〉4「包例外」的字面,這會落進「指不到」而擋。
2. 子模組:平台根在 repo 內但是子模組時,`root.relative_to(rr)` 成立,照樣對終點的樹 `git grep`。樹裡只有 gitlink,不會往下找,所以回 rc 1,判「grep 不到」。重現:`$W/subexp/outer`(子模組 `sub/` 裡有 `def t_in_sub`),`git -C outer grep -w -F -q -e t_in_sub <HEAD> -- ':(glob)sub/**/*.py' …` 得到 `rc=1`。工作目錄第①道過、第②道 rc 1,照字面就是指不到,擋下。
3. 計劃對 `_dispositions_check_test` 只列兩處修改(類別.方法、路徑跳脫),沒有子模組偵測,也沒有把「驗證不了」和「grep 不到」分成兩種回傳。S26 裡的「git 出錯」與「平台根是子模組」照字面造不出來。要在修改清單裡加上:回傳改成三態(或另給一個原因代碼),並在第②道之前判子模組(`_nodehome_list` 的 160000 模式已經認得)。

## F6 第三種判不了「檔裡有 `def 名稱(`」照字面兩頭錯:非測試函式名放行,Python 類別測試寫成「類別.方法」反而擋
severity: major
blocking: 是
引句:「第①道沒過但測試檔裡有 `def 名稱(` 這種 profile 認不得的寫法」
file: `scripts/lumos:6696`
file: `scripts/lumos:4995`
1. 計劃說這條借條款綁定既有的「設定認不到」,那段在 `hay_for`(整個 repo 的程式碼草堆)裡找 `^\s*def\s+名稱\s*\(`,行首的 def 也算。重現:`cd $W/repo && python3 $W/exp3.py`,輸出 `_ns_repo … hay有def=True → 照計劃:判不了(不擋)`、`_nh_commit …判不了(不擋)`、`main …判不了(不擋)`。測試檔裡的輔助函式、任何 Python 檔裡的 `main`,寫進 `[test:]` 都不擋,而 r2 才剛折掉「函式名不是測試卻放行」那一類。就算收窄成「只看測試檔」,`_ns_repo` 也在 `test_lumos.py` 裡。
2. 反方向:Python profile 只認行首 def,類別裡的方法不在 `methods_for` 裡,所以〈做法〉補的「類別.方法只認方法名」在 Python 上第①道照樣不過;def 判法拿的是整串 `TestFoo.test_bar`,也找不到。重現:`python3 $W/exp6.py`(`tests/test_x.py` 有 `class TestFoo: def test_bar`)輸出 `TestFoo.test_bar ①(補類別.方法後)=False 檔裡有 def 名稱( =False → 照計劃字面:指不到(擋)`,寫裸名 `test_bar` 反而是 `判不了`。S30 想放過的那一類測試,用最自然的寫法反而被擋。
3. 判法要明寫成:只認縮排過的 `def`(類別裡的),而且用「類別.方法」的方法名那段去找。

## F7 `_note_shape_eval` 沒有第二個容器參數;借 `slots=` 交出 rows 會把格子規則一起打開
severity: minor
blocking: 否
引句:「`_note_shape_eval` 本來就接受一個容器把它向 `_notelines_new` 要到的 rows 交出」
file: `scripts/lumos:28414`
file: `scripts/lumos:28032`
1. eval 只有 `slots` 這一個容器參數,只在 `slots is not None` 時寫 `notes`。`cmd_note_shape` 隨後的 `_ns_slots_collected` 也只看 `slots is None` 決定跑不跑格子。本案如果照「本來就接受」借 `slots=` 傳自己的容器,`note_shape.slots` 是 off、或掛鉤沒帶 `--slots` 時,格子規則也會被打開。
2. 實作得給 eval 加一個新參數,或在格子容器存在時共用它。計劃這句寫成「不用改 eval」不準確。另外 `keep_other=True` 在 eval 裡本來就寫死(`scripts/lumos:28408`),「帶 `keep_other`」不是本案能選的。

## F8 HEAD 就是推送終點、但工作目錄裡沒提交地刪了或改名了測試,第①道不過,推送被誤擋
severity: minor
blocking: 否
引句:「保險只有一種:推送時目前簽出的提交不是推送終點」
file: `scripts/lumos:41252`
1. 第①道看的是工作目錄的索引。情境:提交 A 新寫了 `[test:t_a]`,`t_a` 也在 A 裡;推 A 之前,工作目錄已經把 `t_a` 改名成 `t_b`,還沒提交。HEAD 等於終點,保險不啟動,第①道找不到 `t_a`,判指不到並擋下,但被推的版本其實一致。
2. 〈實務隱患〉誤擋那一條只列了反方向的「測試寫了沒提交」。這個方向要嘛寫進誤擋,要嘛保險加一條「工作目錄的測試檔跟終點不一致時只提醒」。

## 逐節核對
- 開頭欄位、白話、依據、PRIOR-ART、RETIRE-IF、REVISIT:已讀。交叉引用的四篇節點都在(`Projects/漂移防治路線圖_計劃`、`Systems/bound-tests-gate`、`Systems/lumos-cli-read`、`Systems/check-t-sentinel`)。PRIOR-ART 的零件名都查到定義;接點的問題見 F1、F3、F5、F6。
- 名詞:測試名、一條、新寫的行、新加的測試名、指得到/判不了、合約行與條款定義行、明標刪除、作廢、佔位字,逐條對了程式。條款定義行照 `clause_bindings` 吃全文、「第一次在行首」、先引用後定義的判法,實作上抽得出來,無 finding。其餘問題見 F2、F4、F5、F6。
- 範圍:已讀,無 finding。
- 做法 1(抽取):`slot_parse` 對 `[test:]` 給空值欄位、對沒收尾的方括號給錯誤欄位,都核過,與計劃說法一致。單行 summary 在 rows 裡是 other 區塊,keep_other 會收進來,推送時要對上淨差異的行號才算,符合計劃。無另外的 finding。
- 做法 2:F7。
- 做法 3:F3、F4。
- 做法 4:F5、F6、F8。
- 做法 5:F1、F2。
- 做法 6–9:開關讀法照 `_note_shape_slots_parse`/`_ns_slots_mode` 做得出來;`_note_shape_report` 的 blocked 條件、extra 合併、推送時跳過在讀範圍之前就返回,都核過程式碼(`scripts/lumos:28569`–`28575`),與計劃說法一致。`test-gone` 9 個字,在 `_SLOT_KEY_RE` 的 12 字上限內;登記成鍵之後,舊行把 `[test:X]` 改成 `[test-gone:X]`,核心句不變,`_ns_is_old` 判舊,S22 成立。已讀,無 finding。
- 做法 10(doctor S20):S17–S19 與 `warn_soft` 都在(`scripts/lumos:2538`、`1354`)。只做第①道的語意與 `at_sha=None` 一致。已讀,無 finding。
- 做法 11、條款、回退:條款逐條對照做法;造不出來的已經併進 F1(S4、S5、S11、S20、S24、S28 的推送情境)、F2(S12)、F5(S26)、F6(S30)。回退已讀,無 finding。
- 實務隱患:F3(時間)、F8(誤擋)補了漏掉的情境。

## 實務隱患鏡頭(逐類)
- 誤擋:有,見 F5(git 出錯、子模組)、F6(Python 類別.方法)、F2(已作廢條目修錯字、條款行搬位置)、F8。
- 漏網:有,見 F1(推送時 1c 與佔位字全漏)、F4(CI 主線推送全漏)、F6(非測試函式名放行)、F3(超時 fail-open)。
- 效能與逾時:有,見 F3。
- 相容與上線:計劃把「`lumos update` 前寫的壞名稱推送時會被擋」列為代價。`_notelines_new` 的上線點確實沿用 note-shape 那個,核對一致,無 finding。
- 帳本與觀測:無 finding。extra 合併寫法與推送時跳過不記,都對得上現有 `_note_shape_report` 與 `cmd_note_shape`。
- 金流、對外送出、不可逆:無。只讀筆記與測試檔、不連網,warn/off 可退,revert 回得去。

最高等級:major,blocking 共 6 條
