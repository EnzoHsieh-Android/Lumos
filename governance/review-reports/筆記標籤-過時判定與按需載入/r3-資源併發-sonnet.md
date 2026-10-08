severity: major

固定席筆記:這次派工詞尾端沒有附固定席筆記,沒有「不影響」可判。

我的鏡頭是資源與時序。r2 資源併發席的 R2R1 到 R2R5 全部圍繞依賴欄位的重算、判不了與預算,那段整個拆走了。本版 spec 已沒有對應文字,我逐條核過,視為不再適用,不重報。本版新增的成本集中在三處:搜尋行模式的 `--about`、提交前的新提醒、doctor 清單。

**R3R1**
severity: major
blocking: 是——`--about` 的家解析有兩套現成算法,spec 沒選,對最常被改的「大檔」更沒定義,照字面實作會做出把上下文灌爆的指令。
- 輸入:`lumos search --about scripts/lumos --prefix RULE,PITFALL,WHY`,即改程式前清單的取行入口,用在多篇筆記共管的大檔上。
- 走到〈搜尋行模式〉的 `--about`:spec 說「用既有『每支檔有家』的對照算,不是所有 about_code 列了它的筆記」。
  - 既有的對照有兩套。
    - `_impact_home_map` 只看 about_code,不讀 git、不讀正文。
    - `_impact_confirmed_homes` 才是「確認過的家」。它要 `git ls-files` 全 repo,還要逐篇讀家的正文比對路徑,並回傳「是不是大檔」旗標(`scripts/lumos:34597`)。
  - 「不是所有 about_code 列了它的」暗示要走確認版,但 spec 沒點名函式。實作者可能選便宜的 about_code 版,結果正好是 spec 說不要的那種。
  - 大檔(家 ≥ `LUMOS_IMPACT_ABOUT_MAX`,預設 8)在推筆記那邊整批不當入口,因為「家」沒有鑑別力(`scripts/lumos:34642`)。spec 完全沒提大檔,而行模式又規定「不套每篇 8 行截斷」「`--top` 預設 0 全給」。
- 本 repo 實測:管 `scripts/lumos` 的 Systems 節點約 41 篇,這 41 篇的 WHY/RULE/PITFALL 摘要行合計約 160 行、約 44KB 字元。
  - 這是每次改主程式前清單都要拉的量。
  - 全 repo 同類前綴行約 277 行。上千篇筆記的 repo,熱點檔的輸出沒有上限。
- 實作者得自己決定三件事:大檔是全給、截斷還是不給;用哪一套家算法;`--top` 對行模式是否有別的預設。
- 引句:「`--top` 預設照舊是 0(全給,不靜默截斷),給了才限總行數」
- 佐證行 file: `scripts/lumos:34597`、`scripts/lumos:34533`、`scripts/lumos:34642`

**R3R2**
severity: major
blocking: 是——`--about` 在 git 失敗或家沒確認時會靜默回空,空輸出在清單裡的意思是「沒有限制」,沒有任何訊號區分。
- 輸入:大型 repo 上 `git ls-files -z` 超過 20 秒;CI 淺複製;不在 git 底下。
- `_impact_repo_files` 靠 `_nodehome_git`。逾時或失敗時 `_lens_git` 回 None(逾時寫死 20 秒,`scripts/lumos:35746`),`_nodehome_git` 再回 None,結果是空清單(`scripts/lumos:34216`)。
- 空的 `all_paths` 使 `top_dirs` 為空。`_home_confirmed` 的完整路徑與裸檔名比對都因此落空(`scripts/lumos:34580`)。
- 結果:`--about` 輸出 0 行、退出碼 0。改程式的 AI 看到的是「這支檔沒有 WHY/RULE/PITFALL」,而不是「沒查成」。
- 同樣的空輸出還會出現在:檔沒有家、家沒確認(摘要與正文都沒寫出路徑)、檔名拼錯。spec 只有 S13 一條正向驗收,四種空結果沒有區別,也沒有 stderr 說明。
- 這是反向的失敗方式:「判不了」被當成「沒有約束」。spec 其他地方對判不了的處理(fail-open 或擋)都有講,唯獨這個新入口沒有。
- 引句:「`--about <檔>`:那支檔的家筆記(用既有「每支檔有家」的對照算,不是所有 about_code 列了它的筆記)的摘要行。」
- 佐證行 file: `scripts/lumos:34216`、`scripts/lumos:35746`、`scripts/lumos:34580`

**R3R3**
severity: major
blocking: 是——新提醒套進否定現況句的管線時,開關與失敗隔離的耦合沒寫,照字面實作會讓 `negation: off` 的專案漏掉全部新提醒,或一條新提醒出錯就清空另一種的結果。
- 輸入一:專案設 `note_shape.negation: off` 且 `tag_hints` 用預設 warn。
- 輸入二:H2 的正則或字串處理在某篇丟例外。
- 先例的接法:
  - `_ns_negation_prepare` 在 negation 為 off 時回 `hints=None`(`scripts/lumos:25848`)。
  - `cmd_note_shape` 只在 `--staged` 時才準備 hints(`scripts/lumos:25835`)。
  - `_ns_negation_collect` 是單一 try:任何例外就清空 `items`,並把同一個 `error` 旗標壓在整批上(`scripts/lumos:25570`)。
  - 印出與記帳是「否定現況句」專用字樣與專用 `check: negation`(`scripts/lumos:25868`)。
- spec 只說「照 `note_shape.negation` 的先例」,沒寫:
  1. `tag_hints` 與 `negation` 兩個開關各自獨立時,hints 容器怎麼準備。照先例,negation 為 off 時容器不存在,所有 tag 提醒收不到。S4 只測 `tag_hints: off`,測不到這個方向。
  2. 新提醒是否有自己的例外隔離與失敗訊息。現有的「提醒失敗不能讓閘失敗」只涵蓋否定現況句。W4、H1 到 H3 若寫進 `_ns_check_line` 這條會產生違規的路徑,例外就會讓 rc=1 擋提交。「本案不新增任何擋」會被破壞。
  3. 帳:新提醒是否也記 `hinted` 事件,`check` 欄用什麼值。
- 提醒只在提交前跑(`--staged`),推送前與 CI 路徑 `hints=None`,所以漏看的提醒不會在後面補回。
- 引句:「子開關 `note_shape.tag_hints`:`warn`(預設)/ `off`,第 0 步就加(W4 跟它一起上線),照 `note_shape.negation` 的先例」
- 佐證行 file: `scripts/lumos:25835`、`scripts/lumos:25848`、`scripts/lumos:25570`、`scripts/lumos:25868`

**R3R4**
severity: minor
blocking: 否——兩個數字矛盾,但實作者選哪個都不壞;最差是輸出量大。
- 同一條寫「提醒全部印出、不設上限(同否定現況句提醒)」,又接「同一次提交同一條規則超過 10 行時只印前 10 行加總數」。
- 否定現況句的格式函式是全印(`_ns_negation_format`,`scripts/lumos:25513`),沒有 10 行上限的實作可沿用。
- 上限要新寫,而且要說「超過 10 行」之後被省略的行有沒有地方看。S8 到 S10 都沒釘這個上限。
- 引句:「提醒全部印出、不設上限(同否定現況句提醒),但同一次提交同一條規則超過 10 行時只印前 10 行加總數。」
- 佐證行 file: `scripts/lumos:25513`

**R3R5**
severity: minor
blocking: 否——只是 CLI 邊界沒寫,實作者補一個判斷就行。
- 位置參數 `term` 目前是必填(`scripts/lumos:40168`)。`cmd_search` 開頭就 `nfc(term).lower()`(`scripts/lumos:3787`),後面排序路徑還會把 term 傳給 `_rank_score_candidates`。省略 term 的行模式要整段改道,不是只放寬 argparse。
- 給了 `--prefix` 或 `--about` 的同時又給 term 時,term 是否仍然過濾行,spec 沒說。「進入行模式」的字面讀法是無論有沒有 term 都進,但 S13 只測沒給 term 的情況。
- 引句:「給了 `--prefix` 或 `--about` 時 `term` 可以不給(位置參數改成可省略),進入「行模式」」
- 佐證行 file: `scripts/lumos:3787`、`scripts/lumos:40168`

各節覆核:
- 〈doctor 過期 RULE 清單〉已讀,無 finding。成本是掃摘要行字串,跟既有 lint 同量級;`lumos doctor` 的 lint 迴圈只收錯誤等級(`scripts/lumos:1546`),所以 spec 說「舊行送不到」成立。清單沒有筆數上限,但這是 doctor 一次性輸出,我給不出具體失敗場景,不標。
- 〈判定者多判一層〉已讀,無 finding。成本跟筆記內容審相同,沒有接進推送前掛鉤,不增加推送時間。
- 〈不溯及既往〉〈回退〉已讀,無 finding。

實務隱患(逐類):
- 併發(兩個推送):提醒只在提交前跑、只寫既有治理帳,沒有新共享寫入。無,理由是沒有新增寫入點。
- 推送中途失敗:提醒不進推送閘,所以沒有半途狀態。無。
- CI 淺複製:提醒在 CI 不跑。`--about` 靠 `git ls-files`,淺複製不影響清單。無額外隱患。
- git 逾時:有,見 R3R2。
- 大型 repo:有,`--about` 在大檔上無上限(R3R1);結構性提醒是新增行的字串比對,線性、無 git 呼叫,無隱患。
- 改檔前 hook:spec 明寫不動,hook 不多附速查表。但 skill 的查詢表新增一行,使 AI 每改一支檔就會多跑一次 `--about`,成本落在 R3R1 的輸出量上。

最高嚴重度:major,blocking 3 條
