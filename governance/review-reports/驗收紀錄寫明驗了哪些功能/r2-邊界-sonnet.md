severity: major

審查方式:`git clone --shared` 到自己的臨時目錄,用真的 `parse_frontmatter`、`link_target`、`env.resolve`(經 `Env.from_texts`)逐形狀試,並在臨時 clone 裡把 `system_refs` 暫加進 `LIST_KEYS` 跑真的 `lumos append`/`remove`/`set`。repo 本身未動。探針腳本在 `vr-r2/probe.py`。

先講結論(白話):「寫壞的形狀分得出來嗎」——有三種不同的寫法解析後完全是同一個值,工具單靠 `parse_frontmatter` 分不出來;合法的寫法裡有幾種會被誤判;`無 <理由>` 的邊界沒定死,其中一種會讓檢查被默默關掉。

## F1 三種寫法解析成同一個空清單,其中「沒縮排的 - 項」是合法 YAML,而 append 的修法會把檔案寫成非法 YAML
severity: major
blocking: 是
引句:「其他任何形狀——區塊寫法、空值、空字串、空清單 `[]` 或沒縮排而解析成空清單、純量多連結」
file: `scripts/lumos:477`(parse_frontmatter:`val == ""` 後只吃以空白開頭的行,遇到沒縮排的 `- ` 就 break,`fields[key] = []`)
1. 實測 `parse_frontmatter` 結果:`system_refs:`(後面什麼都沒有)、`system_refs: []`、`system_refs:` 加沒縮排的 `- "[[Systems/A]]"`,三者 `fields['system_refs']` 都是 `[]`,lint 都是空。`system_refs: ""` 與 `''` 是字串 `''`(as_list 變 `['']`),`- ''` 是 `['']`,`system_refs: |` 是字串且在 `block_keys`——這四種分得出來,但前三種分不出來。
2. 沒縮排的 `- ` 項是合法 YAML(PyYAML 預設就這樣輸出;實測 `yaml.safe_load("a: 1\nsystem_refs:\n- \"[[Systems/A]]\"\n")` 得到 `['[[Systems/A]]']`)。使用者明明寫了一項,doctor 卻只能報「宣告是空的」,原因與事實不符。要報對原因,共用函式得另外掃 `n.fm_lines`,計劃沒寫。
3. 更糟:實測 `lumos append Verification/y2 system_refs "[[Systems/lumos-cli-read]]"` 對這種檔回 `✓`,結果檔案變成 `system_refs:` + 縮排的一項 + 底下殘留一行沒縮排的 `- "…"`;`yaml.safe_load` 對這個結果直接報錯(Obsidian 會讀不到整份欄位)。若「寫壞」訊息的改法叫人跑 `lumos append`(做法 2 寫「每項印…改法」),這個形狀的改法會把檔案寫壞。
4. 建議:共用函式對「鍵在、值解析成空」另掃原始行分辨三種(真空、有沒縮排的 `- ` 項、純 `[]`);沒縮排的情形原因寫「項目沒縮排,工具讀不到」、改法寫「手動縮排兩格」,且 `append` 對這種形狀要擋(比照現有對一行清單的「擋下」)。補一支條款測沒縮排項。

## F2 `無` 的邊界沒定死:`無 [[Systems/A]]` 單項會被當成合法的「沒驗任何功能」,檢查被默默關掉
severity: major
blocking: 是
引句:「②整份清單只有一項、是 `無` 加至少 4 個字的理由」
1. 實測解析:`system_refs: 無 [[Systems/A]]` 得到字串 `'無 [[Systems/A]]'`,`n.targets` 為空(因為不是整個值恰為單一連結)。照 ② 的字面,它是「只有一項、無 加 ≥4 字」→ 合格。結果:使用者寫了連到功能的 `無 [[Systems/A]]`,工具當作「宣告沒驗任何功能」,A 不要求反向登記、sync 不補,也不報——正是 r1 要堵的「默默關檢查」。條款 S3 只說「`無` 跟連結混用」,講的是清單裡兩項混用,沒講同一項內含連結。
2. 分隔字元沒定義,各寫法解析後的字串實測:`無:只是指路用`→`'無:只是指路用'`;`無　只是指路用`(全形空白 U+3000)→ 保留 `　`;`無需驗證功能`(無空白,自然會這樣寫)→ 原樣;`無 `(尾端空白)→ 被 strip 成 `'無'`。實作者用 `startswith("無 ")`、`split(None,1)`、`s[1:].strip()` 三種寫法,對這五種輸入會得到三種不同答案;而 `無法確認 X 是否通過` 這類以「無」開頭的普通句,用 `s[1:]` 版會被當成合格宣告。
3. 「4 個字」沒說怎麼數:數 strip 後的理由?標點、`....`、`xxxx` 算不算?門檻只是減速帶,擋不了敷衍,但至少要寫死怎麼數(建議:`re.fullmatch(r"無[ 　]+(\S.{3,})", s)`,理由裡禁含 `[[`)。
4. 建議:②改成明確的語法——`無` 後面必須有至少一個半形或全形空白,理由 strip 後 ≥4 字且不含 `[[`;`無需…`、`無:…` 歸寫壞並在原因寫「`無` 後要空一格」。補測:`無 [[Systems/A]]` 單項、`無　理由`(全形)、`無需驗證功能`、`無 `、`無:理由`。

## F3 合法 YAML 的寫法被判寫壞,而且原因文字會講錯
severity: minor
blocking: 否
引句:「純量多連結、純文字路徑、全形括號、連結後面多一句、解析不到、不是 Systems」
1. 帶引號 `"[[Systems/A]]"`、`'[[Systems/A]]'`、`[[Systems/A.md]]`、`[[Systems/A|顯示]]`、`[[Systems/A#段]]`、`[[Systems/sub/B]]` 實測 `fields` 都是乾淨的單一連結字串,`link_target` 抽出 `Systems/A`(.md、別名、段落都去掉),這些會正確通過。
2. 行尾註解 `- [[Systems/A]]  # why` 與 `- "[[Systems/A]]" # why` 實測 `fields` 保留 ` # why`(parser 在整個 repo 都不處理行尾註解),不是單一連結 → 落入「連結後面多一句」。這在 YAML 裡是註解、不是「一句」,原因文字會誤導。
3. 單項的行內清單 `system_refs: ["[[Systems/A]]"]` 實測 `fields` 是字串 `'["[[Systems/A]]"]'`(只有一個連結,所以也不是「純量多連結」);`system_refs: [[[Systems/A]]]` 同樣。這兩種是合法 YAML,卻會被歸到不貼切的類別。`lumos append` 對這種形狀自己會擋並說「工具不解析這種寫法」(實測),doctor 的原因文字應與它對齊。
4. 建議:不需放寬,但原因文字要分類:偵測 ` #` 註解、行內清單(開頭 `[` 且不是 `[[`)各給專屬原因與改法(「拿掉註解/改成一行一項」),別全塞進「連結後面多一句」。

## F4 `lumos append` 不擋「無」與連結混用,也不擋第二個「無」;理由含 `#` 或 `|` 時去重誤判
severity: minor
blocking: 否
引句:「用 `lumos append <新紀錄> system_refs "無 <理由>"`」
file: `scripts/lumos:17298`(edit_fm_append 以 `link_target` 做去重)
1. `append` 白名單只看鍵名。實測:已有 `無 只是指路用` 的紀錄再 append `無 理由很長很長`,回 `✓`,結果兩個「無」項;對只有 `無 理由很長很長` 的紀錄再 append `[[Systems/lumos-cli-read]]`,回 `✓`,結果混用。兩者都是計劃自己判寫壞的形狀,寫端不吭聲、下一次 doctor 才擋。
2. 去重用 `link_target`,它會把 `#` 與 `|` 後面切掉:實測先 append `無 見 Issue #12 的說明`,再 append `無 見 Issue #34 的說明`,第二個回「已經有 無 見 Issue #34 的說明,檔案沒動」——訊息說謊(沒有這一項)。
3. `append` 把含 ` #` 或 `: ` 的理由自動加引號(`"無 見 Issue #12 的說明"`),解析回來沒問題,這點正常。
4. 建議:對 `system_refs` 在寫端加輕量守衛(加「無」前若已有任何項、加連結前若已有「無」就擋並講原因),或至少在寫完印一句警告;`無` 項去重改成整串精確比對。

## F5 寫壞形狀的「改法」靠 CLI 走不通的有好幾種,計劃沒說到要怎麼講
severity: minor
blocking: 否
引句:「每項印紀錄、原文、原因與改法」
1. 實測:`system_refs: |`(區塊寫法)被 append 擋(「是block型欄位」)、`set` 擋(system_refs 不在 set 白名單)、`remove` 不帶值整欄拿掉也擋(清單欄位不准);一行清單 `["…"]`、`"[[A]], [[B]]"` 被 append 擋(「只能手動改」)。這幾種形狀唯一出路是手動編輯檔案。
2. `system_refs: ""`、`''`、`[]`、`system_refs:` 空鍵則 append 可以救(實測會改寫成多行清單);`- ''` 項 append 會留著空項、必須另外 `remove "" `才清得掉(實測 `remove … system_refs ""` 成功),所以只 append 的人會留著寫壞的空項,doctor 仍紅。
3. 建議:原因與改法逐形狀寫死(區塊/一行清單 → 「手動改成一行一項」;空項 → 用 `remove`),避免訊息叫人跑會被擋的指令。

## F6 寫壞項很多時的訊息量:`warn` 不封頂,每項重複同一段改法,2/4 還會再報一次
severity: minor
blocking: 否
引句:「每項印紀錄、原文、原因與改法——照 doctor 4/4 對 `plan_refs` 斷鏈自己報的先例,指到不存在的節點 2/4 也會報,重複可接受」
file: `scripts/lumos:1361`(`warn` 逐條全印,`issues += len(lines)`;只有 `warn_soft` 預設封頂 3 條)
1. 做法 2 把寫壞放 `warn`(硬問題),不像 `warn_soft` 有 `_SOFT_CAP`。一份紀錄 100 項寫壞(例如整串貼成 100 行純文字路徑)→ 100 條 bullet,每條帶紀錄名、原文、原因、改法,以每條約 150–250 字估計約 15–25 KB,而且 `issues` 加 100,收尾行的問題數被單一紀錄撐爆。
2. 「解析不到」的項同時進 2/4(`unresolved`)與 3/4,同一個打錯字算 2 個 issue;多份紀錄時翻倍。
3. 原文沒截斷:貼一個超長字串會原樣印出。
4. 建議:改法放 `warn` 的 `advice`(只印一次),每項只印「紀錄:原文(截 80 字):原因」;或同一份紀錄聚成一行;解析不到的項在 3/4 不重複計數(只提示見 2/4);補一個 100 項的測試確認輸出行數上限。

## F7 路徑一致檢查依賴 `resolve`,而 `resolve` 對大小寫、`./`、`/` 開頭會解到別的資料夾,原因文字會誤導 ⚠
severity: minor
blocking: 否
引句:「而且連結有寫路徑時路徑要跟解析結果一致(防 `[[Projects/A]]` 被檔名救成 `Systems/A`)」
file: `scripts/lumos:626`(make_resolver:路徑不在 `rels` 就退回只用最後一段比對 stem,取 `hits[0]`)
1. 實測(Systems/A、Projects/A 同名並存):`[[systems/a]]`、`[[./Systems/A]]`、`[[/Systems/A]]` 都 resolve 成 `Projects/A.md`(依排序第一個),`[[sub/B]]` 解成 `Systems/B.md`(不是 `Systems/sub/B.md`)。這些會被一致檢查擋成寫壞(方向對),但原因會寫成「解析到 Projects/A,不是 Systems」,使用者其實只是大小寫或多了 `./`,改法應是「寫成 `[[Systems/A]]`」。
2. 重複鍵:`system_refs` 寫兩次時 parser 後者蓋前者、前者的內容被默默丟掉,只有一條 lint 提醒(實測),共用函式看不到第一份。建議在共用函式把「同鍵重複」也列入寫壞(或至少在原因提到)。
3. 對非驗收紀錄(例如計劃)`lumos append <計劃> system_refs …` 會成功(白名單只看鍵名),但 doctor 3/4 只掃 `Verification/`,這個欄位不會被判也不會被報(⚠ 判不準是否值得擋,建議至少在 append 時對非 Verification 的節點提醒一句)。

最高等級:major,blocking 共 2 條
