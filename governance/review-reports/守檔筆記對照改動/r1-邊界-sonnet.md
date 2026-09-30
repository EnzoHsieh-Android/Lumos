severity: major

## F1 被刪掉的程式檔,它的家永遠不會成為候選
severity: major
blocking: 是
引句:「再用每支檔有家的 `_nodehome_required` 判哪些是要有家的程式檔(讀頂端快照,不讀磁碟;判定檔、簿記檔因為副檔名 .json/.jsonl 本來就不在程式檔清單裡)」
file: `scripts/lumos:23822`
1. `_nodehome_required(repo_root, side, ...)` 只迭代 `side.files`,而頂端快照裡被刪掉的檔已經不在了。所以 `_nodehome_changes` 回的 `(D, 舊路徑, None)` 這一筆,套上這個過濾就被丟掉,家不進候選。
2. 「刪掉一支程式、筆記只改了別處」正是筆記還在描述已不存在的檔的典型漂移。實驗一自己也說被刪或改名的測試要看得到。
3. 既有的每支檔有家沒有這個洞:`_nodehome_evaluate` 另外用起點那一邊的 `reqB` 算 `code_deleted`(scripts/lumos:24234,註解寫「第二輪外家席」)。spec 沒有寫要用起點側的 required 與家對照表。
4. 頂端的家對照表 `_nodehome_homes(頂端)` 只反映頂端筆記的 about_code。作者刪檔時順手把 about_code 那一項拿掉,頂端表就查不到家。刪檔的情形必須改用起點側的家對照表。
5. 照字面實作:刪檔且家有被碰過 → 不提醒(漏報),而且沒有任何 finding 或紀錄說明為什麼漏。

## F2 手動 prepare 的起點與 hook 的起點不同,指紋對不上,提醒永遠不消
severity: major
blocking: 是
引句:「手動跑不帶那兩個參數時照 `_lens_push_base`。」
file: `scripts/lumos:34609`
1. 項目指紋含「給的 diff 全文雜湊」,而 diff 是「範圍起點到終點」。hook 與 CI 的起點走 `_push_range_start`,手動 prepare 走 `_lens_push_base`。
2. `_lens_push_base` 的 docstring 自己承認在合過主線、沒設 upstream、CI 已 fetch 時算錯(scripts/lumos:34618-34621)。合過主線正是 spec 選 `_push_range_start` 的原因。
3. 結果:在合過主線的分支上,作者照 reread-check 印的指令跑 prepare(沒帶推送參數)、派判定者、record 並提交。推送時 check 用 `_push_range_start` 算出較小的範圍,diff 雜湊不同、指紋不同,查不到同指紋紀錄,同一篇又被列出。這種分支的每次推送都提醒、對照過也沒用。
4. 增量推送(起點是遠端舊值)也一樣:第一次對照的範圍比第二次大,指紋不同。spec 第 4 節只說「筆記改了才會再列」,沒提範圍起點。
5. spec 沒說 reread-check 印的 prepare 指令要不要帶 `--push-remote/--pushed-ref`,也沒說 reread-prepare 是否接受這兩個參數。指紋是否只該綁 diff 的實際內容,而不是綁範圍算法,也沒交代。

## F3 抽共用函式的描述跟現有程式碼對不上,照寫會改弱存量漂移檢查的 strict 語意
severity: major
blocking: 是
引句:「把 `_notes_status_flipped` 裡「範圍裡任一提交碰過的筆記(`git log --name-only -z -M`,改名取新路徑、頂端讀不到的丟掉)」那幾行抽成共用函式」
file: `scripts/lumos:25825`
1. 現有 `_notes_status_flipped` 裡 `git log --name-only -z -M` 那幾行只做 git log 加 `.md` 過濾與 `only` 篩選,沒有「頂端讀不到的丟掉」這一步。頂端讀取發生在後面的 `_note_flipped_one` 裡的 `blob = reader(p)`。
2. `_note_flipped_one` 在 `blob is None and strict` 時回 None,也就是「判不了」。存量漂移那條路用 strict=True,刻意把「讀不到」當判不了而不是放行(見 docstring:代碼審 r3、r4 的 blocker)。
3. 若照 spec 把「頂端讀不到的丟掉」放進共用函式,`reader` 回 None(暫時性 git 失敗)會在 drift 的 strict 路徑被靜默丟掉而不是回 None。存量漂移檢查(推送前會擋的閘)會在 git 出錯時誤放行。
4. S12 的測試「行為不變」只有在注入 reader 失敗時才會紅,spec 沒要求,一般綠測試抓不到。
5. spec 也沒說共用函式回什麼路徑形式。touched 是 repo 相對路徑(如 docs/x-knowledge/Systems/a.md);`_nodehome_side().notes` 的鍵是圖譜相對路徑(Systems/a.md,scripts/lumos:23811)。第 1 節「家 ∩ 被改過的筆記」沒寫鍵怎麼對,直接做交集會是空集合。

## F4 非 UTF-8 筆記與「恆回 0」:沒有涵蓋不預期例外
severity: minor
blocking: 否
引句:「★任何情況都回 0★:包括範圍格式錯、終點找不到(`_note_audit_resolve` 回 2 的那兩種)、git 失敗」
file: `scripts/lumos:23763`
1. 這句只列了三種原因,沒有要求整個子指令外包一層 try/except。指紋要讀筆記全文、算 diff 雜湊。`_nodehome_parse_note` 讀筆記用 `errors="replace"` 所以非 UTF-8 筆記是合法的家,但 spec 沒說派工詞的全文與指紋用不用同一種解碼。
2. 實作若用嚴格 `decode("utf-8")` 就會在 UnicodeDecodeError 上帶 traceback 結束,rc 是 1。掛鉤不看回傳值,但 CI 沒有寫「不看」以外的保護,只靠 `|| true`。
3. reread-record 的報告與 prepare 的項目檔同樣沒寫非 UTF-8 怎麼辦。既有 record 是「照位元組讀、解不開回 2」(scripts/lumos:26437)。
4. 建議寫明:一律用 replace 解碼,或跳過那篇並印原因;主指令頂層吞掉例外、印一行、回 0。

## F5 派工詞的行號用什麼方式切行沒定,可能跟檔案行號不一致
severity: minor
blocking: 否
引句:「終點版本全文,每行開頭加行號(跟檔案行號一致,含開頭欄位)。」
file: `scripts/lumos:26272`
1. 未指定切行法。實作最自然的寫法 `text.splitlines()` 會在 `\x0c`、`\x85`、U+2028、U+2029 上也斷行。實測 `"a b\nc\x0cd\n"` 得 4 行,以 `\n` 切只有 2 行。
2. 筆記常有貼上來的 U+2028 或 form feed。這時判定者報的行號跟檔案行號差幾行,「原句」與「行號」對不上。
3. record 的「超出筆記行數」判斷與「那一行當時的全文」也要用同一套切法。spec 沒說行數與那一行全文從哪裡取。項目檔檔頭只有編排者、判定者模型、範本版本、項目指紋,沒有 tip sha、行數,record 又沒有 `--diff`,只能反解析項目檔裡帶行號的排版。
4. CRLF 筆記與末尾換行的行數也沒寫。

## F6 報告 json 區塊的抽取規則與逐項驗證太簡略
severity: minor
blocking: 否
引句:「最後一個 ```json 區塊是 `[{"line": 行號, "quote": "原句節錄", "why": "為什麼不成立"}]`(可以是空清單)。」
file: `scripts/lumos:26272`
1. 沒定義怎麼找「最後一個 ```json 區塊」。筆記本身滿是 ``` 圍欄,判定者的 `quote` 常抄到 "```json" 這種行。用非貪婪 regex 找結尾 ``` 會在字串中間截斷,整份被判成「解析不了」而拒收 rc2。請寫成「行首的 ```json 到下一個行首單獨的 ```」。
2. 沒寫的輸入:頂層不是清單(如 `{"items": [...]}`)、項目不是物件、缺 `quote` 或 `why`、`line` 是布林(Python 的 `isinstance(True, int)` 為真)、`line` 是 0 或負數、`line` 是字串 "12"、同一行重複出現。spec 只寫「不是整數或超出行數」。
3. 字串型行號被整項丟掉,這是 LLM 常見的格式漂移。重複行會灌高 `reread-recorded` 的「點出幾行」,而 REVISIT 要拿這個數字抽 30 行。
4. 「沒有 json 區塊」與「多個 json 區塊」應該有明確結果(S5 只寫「解析不了」)。

## F7 多個 vault 只看得到一個
severity: minor
blocking: 否
引句:「改到的程式檔的家 ∩ 這次被改過的筆記。候選是空的」
file: `scripts/lumos:26099`
1. `_note_audit_resolve` 只挑一個 vault_rel(所在目錄的,或排序第一個),`_notes_status_flipped` 的 `git log ... -- vault_rel` 與 `_nodehome_side` 的 notes 也只涵蓋那個 vault。
2. 一個 repo 有 docs/a-knowledge 與 docs/b-knowledge 時,另一個 vault 的家筆記被改了也不會提醒。spec 的〈誠實界線〉沒列這一項。

## F8 改名路徑用 NFC 後拿去當 pathspec,NFD 樹會查不到
severity: minor
blocking: 否
引句:「這次被改名的檔把舊路徑一起放進 pathspec(用第 1 節 `_nodehome_changes` 算出的新舊對照)」
file: `scripts/lumos:23900`
1. `_nodehome_changes` 回傳的路徑已經過 `nfc()`。`_nodehome_name_status` 的 docstring 明講:要拿去問 git 的呼叫端要用 `norm=False`,「NFC 過的路徑對 NFD 樹查不到」(scripts/lumos:23922 附近,筆記形狀擋驗收輪)。
2. 樹裡有 NFD 檔名(含濁音的日文、帶重音的西文,非 macOS 提交進來的)時,`git diff -- <nfc 路徑>` 什麼都不回。項目檔的 diff 是空的,判定者看不到那次改動,提醒無聲失效。spec 沒說 pathspec 要用原樣路徑。

## F9 項目檔的檔頭與本文之間沒有定義分隔,record 讀檔頭可能被材料誤導
severity: minor
blocking: 否
引句:「檔頭寫編排者、判定者模型、範本版本、項目指紋;一次推送有 N 篇就產 N 份,印出每份的派工指令」
file: `scripts/lumos:26248`
1. 既有清單檔用 `\n---本文---\n` 切檔頭與本文。spec 沒寫新項目檔是否也用,以及 record 讀「範本版本」與「項目指紋」的方式。
2. 若用整檔 `re.search(..., re.M)`,本文裡的 diff 或筆記剛好有一行叫「範本版本: xxx」時就會被當成檔頭。這個 repo 自己就有一大堆講這種格式的筆記與程式。
3. 建議寫明:先切開再只讀檔頭。

## F10 起點算不出來與空範圍、刪除分支等提早結束情形,沒有說怎麼區分,ledger 事件會亂
severity: minor
blocking: 否
引句:「治理帳記 `reread-reminded`(帶沒對照的篇數)或 `reread-skipped`(帶原因)。」
file: `scripts/lumos:26099`
1. `_note_audit_resolve` 對淺層 clone、刪除分支(終點全 0)、起點為 None、沒有圖譜、清單讀失敗都回 `(None, 0, None)`,呼叫端分不出是哪一種,拿不到原因。spec 要求 `reread-skipped` 帶原因,做不到。
2. resolve 內部還會自己以 `gate="note-audit"` 記 `skipped` 與 `skipped-env` 事件(scripts/lumos:26120、26133),跟 reread 自己的事件混在一起。REVISIT 要按 `reread-recorded` 等事件計次,也會夾雜到筆記內容審自己的統計。
3. 範圍格式錯與終點找不到時 resolve 印的是「擋下:…」,與 spec 要的「這次沒提醒:<原因>」措辭不一致,提醒版看到「擋下」會被嚇到。
4. `_PUSH_START_UNKNOWN` 時 resolve 回的 base 是 tuple `(判不了, 說明)`,呼叫端要自己判 `isinstance(base, tuple)`,spec 只寫「印一行」。

## F11 diff 過大與逾時沒交代
severity: minor
blocking: 否
引句:「上限 10 萬字元,超過先把上下文縮成 0 行,仍超過再各檔平均截斷並在截斷處註明。」
file: `scripts/lumos:34801`
1. `_lens_git` 對每次 git 呼叫有 20 秒逾時,回 None。首推新分支(空樹起點)、大擠壓提交或壓縮過的產物檔(副檔名是 .js 的 bundle)會在 20 秒內跑不完。
2. prepare 遇到 diff 呼叫失敗要怎麼辦沒寫:整份跳過還是給判定者空 diff?空 diff 會被判成「沒有不成立的行」,而且會被 record 收成有效的零行紀錄。
3. 逾時可能把讀完整個輸出到記憶體的成本也算進去,先讀再截斷。建議先用 `--numstat` 或 `--shortstat` 估大小。

最高等級:major;blocking 共 3 條
