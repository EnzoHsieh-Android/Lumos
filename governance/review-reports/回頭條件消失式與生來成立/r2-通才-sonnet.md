severity: major

# 第 2 輪審查報告(無鏡頭通才,席位字首 U)

對照程式碼:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw`(下稱 rw)。

**U1 「讀位元組」的修法建在 `_read` 上,但 `_read` 存的是已解碼的文字,r1 要的「讀不準一律判不了」做不到**
severity: major
blocking: 是 — 〈做法〉1.2 的核心保證(誤讀亂碼不會讓條件提早成立)照字面實作無法成立,實作者得自己決定換一條讀法
引句:「是一般檔就讀位元組(既有的 `_read`,讀不出判不了)」
1. 位置:〈做法〉1.2 帶字串那一條,是 r1 正確性席 C2 的修法。
2. 問題:既有 `_DriftProbeTree._read` 讀到的位元組立刻經 `_drift_decode`(`b.decode("utf-8-sig", errors="replace")`)變成文字存進 `_text`,位元組沒留。工作目錄模式更是直接 `_drift_decode((Path(root)/p).read_bytes())`。「內容含 NUL 位元組」「LFS 指標檔」「把字串編成 UTF-8 在位元組裡找」三件都需要原始位元組;`_read` 回傳的 None 只代表「樹上有、git 讀不出」,不代表「不是合法 UTF-8」。
3. 例子:`src/legacy.c` 是 Big5 編碼,條件 `[when-gone:src/legacy.c::注意:此處]`。`_read` 把中文位元組換成 U+FFFD,字串「找不到」,條件在寫下當下就判成立,正是 r1 C2 想擋的情形;但此時 `_text[path]` 不是 None,所以不會走「讀不出判不了」。UTF-16 檔的 NUL 在解碼後還在文字裡可偵測,Big5/GBK/Latin-1 偵測不到。
4. 另:`_read` 走 `_nodehome_cat_blobs`,沒有大小上限(同檔已有 `_nodehome_cat_blobs_capped` 可用,spec 沒採用)。`[when-gone:assets/demo.mp4::x]` 會把整支影片讀進記憶體、解碼、再檢查 NUL。
5. 查證:`rw/scripts/lumos:32180`(`_drift_decode`)、`rw/scripts/lumos:32267-32283`(`_read` 兩條路徑)、`rw/scripts/lumos:26527`(`_nodehome_cat_blobs_capped`)。

**U2 往回查的 git 呼叫:spec 宣稱的「既有旗標」與「剩餘預算逾時」在 `_nodehome_git` 上都不存在**
severity: minor
blocking: 否 — 實作者看程式一眼就會發現,改走 `_lens_git` 即可;但 spec 對「不受本機設定影響」的安全宣稱沒有根據
引句:「走 `_nodehome_git`,`-c` 關掉外部差異與文字轉換的既有旗標,`--` 隔開路徑」
1. 位置:〈做法〉2.2、〈做法〉2.5(逾時取剩餘預算)、〈實務隱患〉跨環境。
2. 問題:`_nodehome_git(repo_root, *args)` 只轉呼叫 `_lens_git(..., binary=True)`,沒有任何 `-c` 旗標,也不接 timeout;`_lens_git` 的 timeout 固定預設 20 秒。要讓逾時取「剩餘預算與 20 秒的較小值」就得直接呼叫 `_lens_git(..., timeout=)`,或替 `_nodehome_git` 加參數;兩者 spec 都沒寫。「外部差異與文字轉換」的旗標(`--no-ext-diff`、`--no-textconv`)在本檔是加在 `diff`/`show` 呼叫上,`git log --format=%H -- path` 本來不經過它們,所以這句既不是現況也不是需要。
3. 例子:照字面實作 `_nodehome_git(root, "log", "--format=%H", rev, "--", path)`:逾時固定 20 秒,預算只剩 3 秒時仍會卡到 20 秒,r1 B9 的問題原樣留著;〈實務隱患〉寫的「本機設定不影響」沒有任何旗標支撐 ⚠(是否有影響 `git log --format=%H` 輸出的本機設定,我沒找到實例,但 spec 的理由是錯的)。
4. 查證:`rw/scripts/lumos:26179-26184`(`_nodehome_git`)、`rw/scripts/lumos:39854`(`_lens_git` 簽名)。

**U3 新增的「判不了」原因沒接上點名機制,「scan 列成問題」也沒指到寫入點**
severity: minor
blocking: 否 — 只影響訊息可讀性,不影響判定對錯;但推送時「判不了」會擋,擋下的人看不到原因
引句:「路徑在、但不是一般檔(連結檔、子模組、資料夾)→ 判不了」
1. 位置:〈做法〉1.2 帶字串。
2. 問題:(a)spec 說這情形 scan「列成問題」,但 scan 的寫法問題產生處是 `_drift_probe_row_problems`,spec 全文沒提它要改;只改 `one` 回 None 的話,scan 只會印通用的「判不了(git 讀不出程式檔或筆記…)」。(b)點名讀不出的檔是 `_drift_row_unread`/`unread_for`,只認「樹上有、`_text` 為 None」的檔;NUL、LFS、資料夾這三種新原因都不在其中,點名會是空的:訊息變成「git 讀不出程式檔或筆記」後面不帶任何路徑。(c)同一條會在 scan 重複:「寫法問題」一筆加「判不了」一筆。
3. 例子:`[when-gone:docs/guide.pdf::foo]`(pdf 含 NUL),推送改到 guide.pdf → 候選 → 判不了 → 推送被擋,訊息只說「條件判不了(git 讀不出程式檔或筆記)」,沒有路徑,作者無從判斷是檔壞了還是條件選錯。
4. 查證:`rw/scripts/lumos:32520-32550`(`_drift_row_unread`)、`rw/scripts/lumos:32618-32650`(`_drift_probe_row_problems`)、`rw/scripts/lumos:32650-32690`(`_drift_probe_scan` 判不了分支)。

**U4 列舉條件鍵的位置仍漏兩處技能文件,守衛測試也不涵蓋**
severity: minor
blocking: 否 — 只是說明文件落後一種鍵,不影響判定
引句:「技能手冊 `skills/lumos-project-notes/commands/03-寫回圖譜.md` 四種鍵那句補第五種。」
1. 位置:〈做法〉1.4。
2. 問題:同樣寫「四種鍵」或逐一列出四個鍵的地方不只這一份:`skills/lumos-project-notes/SKILL.md` 第 73 行「四種鍵怎麼選見 commands/03-寫回圖譜.md」,`skills/lumos-project-notes/reference.md` 第 404 行列出「事件:when-file、when-symbol、when-test、when-status」。新守衛測試只要求兩句錯誤訊息與筆記形狀擋提醒提到每個鍵,技能文件不在其中,上線後這兩處會靜默落後。
3. 例子:使用者讀 reference.md 學到事件條件只有四種,不知道有 `when-gone`。
4. 查證:`rw/skills/lumos-project-notes/SKILL.md:73`、`rw/skills/lumos-project-notes/reference.md:404`、`rw/skills/lumos-project-notes/commands/03-寫回圖譜.md:50`。

**U5 往回查用的路徑沒釘成字面路徑,本 repo 其他處都釘了**
severity: minor
blocking: 否 — 筆記檔名含萬用字元的機率低,後果是標錯提交
引句:「這篇筆記改到它的提交清單用 `git log --format=%H <起點> -- <筆記路徑>`」
1. 位置:〈做法〉2.2。
2. 問題:`--` 隔開只擋「以 - 開頭被當旗標」,不擋 git 的 pathspec 萬用字元與魔術前綴。本檔對讀單一路徑的 git 呼叫一律加 `--literal-pathspecs`(例:`rw/scripts/lumos:14692`、`:30926`、`:33198`,註解寫「檔名裡的 * 不當萬用字元」)。另外 `版本:路徑` 形式的批次讀取在本檔另有已知坑:樹清單的路徑是 NFC,git 內存可能是 NFD,`_drift_cat` 的註解專門講過,要用內容編號讀。spec 的「每一版的筆記內容用一次批次讀(`_nodehome_cat_blobs_capped`)」走的是「版本:路徑」形式。
3. 例子:筆記檔名 `Projects/[草稿]x_計劃.md`,`git log -- <路徑>` 把 `[草稿]` 當字元集,可能列出別篇筆記的提交,「這一世」找錯。
4. 查證:`rw/scripts/lumos:32186-32192`(`_drift_cat` 說明)、`rw/scripts/lumos:26527-26545`。

**U6 「沿筆記提交清單一版一版往回」假設歷史是一條直線,有合併提交時順序不保證是祖先鏈**
severity: minor
blocking: 否 — 影響是個別存量行的「寫下時」可能標錯或判成刪過重寫,scan 不是閘
引句:「從被掃的那一版往回,一版一版看這篇筆記,找連續都還有這一條的最早那一版」
1. 位置:〈做法〉2.1、2.2。
2. 問題:`git log --format=%H <起點> -- <路徑>` 預設按時間序列出,不是沿某條父鏈;分支各自改過這篇筆記再合併時,清單裡會交錯出現不同分支的版本。「連續都還有」在這個序列上不等於「祖先鏈上連續」。我用兩條分支各改同一檔再合併實測,清單順序是 合併、A1、B1、base,A1 有條件、B1 沒有:順序若調換成 B1 排在 A1 前面,在 B1 就會被當成「中間刪掉過」而停在合併提交。spec 沒說用 `--first-parent`、`--topo-order` 還是別的,也沒說合併提交怎麼處理。⚠ 實際會不會出現取決於消費專案是否用合併式工作流,我沒有查證。
3. 例子:主線 M 合併分支 A(新增條件 C)與分支 B(改筆記別處);log 順序 M、B1、A1、base,逐版看:M 有 C、B1 沒有 C → 停在 M,「寫下時」判成 M 而非 A1。
4. 查證:實驗目錄 `/tmp/r2m`(臨時,可重現);spec 〈天花板〉沒有這一項。

**U7 往回查的成本估算漏掉「每個不同提交都要讀一遍程式碼語料」與樹快取上限**
severity: minor
blocking: 否 — 超過預算只會標判不了,不擋
引句:「同一個提交的樹與圖譜只建一次」
1. 位置:〈做法〉2.5、〈實務隱患〉效能。
2. 問題:(a)往回查在寫下那一版的樹上用 `_drift_probe_line` 判一次;若條件含不帶路徑的 `when-symbol`/`when-test`,`_DriftProbeTree.one` 會走 `corpus()` 把該版整棵樹所有程式檔讀一遍。〈實務隱患〉的數字(git log 0.05 秒、建圖譜 0.19 秒)沒含這一項,成立條件雖是個位數,分散在個位數個不同提交,每個提交都是一次全語料讀取。(b)`_drift_list` 的快取上限是 8 個提交,滿了就整個清掉;往回查超過 8 個不同提交時,「只建一次」不成立,連目前掃描用的那棵 HEAD 樹清單也會被清掉重列。
3. 例子:消費專案有 12 條成立的不帶路徑 `when-symbol` 條件,分別寫於 12 個不同提交 → 12 次整樹讀取與列檔,預算 60 秒內可能多數標成「判不了(超過預算)」,使用者看到的是一堆判不了而不是結果。
4. 查證:`rw/scripts/lumos:32150-32172`(`_drift_list` 快取清除)、`rw/scripts/lumos:32300-32315`(`corpus`)。

**U8 「提交時報條件寫錯」的反引號檢查落在哪支函式沒指定,放在共用解析器裡永遠不會觸發**
severity: minor
blocking: 否 — 屬於可執行性缺口,實作者會在寫測試時發現
引句:「新寫的 REVISIT 行原文裡 `[when-gone:` 之後同一個標記內出現反引號,提交時報條件寫錯」
1. 位置:〈做法〉1.1 字串規則、驗收 S3。
2. 問題:`_probe_lines` 先對整行跑 `_strip_inline_markup`(剝行內程式碼、遇到沒閉合的反引號整段截掉),`_probe_parse` 只看到剝過的文字,反引號不可能到達 `_probe_value_err`。spec 要的是「看原文」,只有 `_ns_revisit_cond_viol(ln, rest)` 手上同時有原文 `ln` 與剝過的 `rest`。spec 只在〈說明與同步〉提筆記內容閘要補一行 WHY,沒寫檢查要加在這支函式。同理 `[retire:when-gone:…]` 路徑(`_retire_lines` 讀的是摘要原文、不剝反引號)完全沒交代:反引號會留在比對字串裡,與 REVISIT 行的規則不一致。
3. 例子:`REVISIT:[when-gone:a.py::`x`][by:2027-01-01] 待辦` → 剝過後變 `[when-gone:a.py::]`,現有解析器只會報「字串是空的」(S3 要求的是反引號的訊息);沒閉合的 ``` ` ``` 則截到只剩 `[when-gone:a.py::foo`,變成「沒有條件標記」。S3 的測試若直接對 `_probe_parse` 斷言反引號,永遠紅。
4. 查證:`rw/scripts/lumos:31998-32015`(`_probe_lines`)、`rw/scripts/lumos:27982-27990`(`_ns_revisit_cond_viol`)、`rw/scripts/lumos:32021-32040`(`_retire_lines`)、`rw/scripts/lumos:368-377`(`_strip_inline_markup`)。

## 其餘各節

- 前言與依據、範圍、PRIOR-ART/RETIRE-IF/REVISIT:已讀,無 finding(交叉引用的 `Projects/回頭條件寫法補齊_計劃`、`存量漂移防線_計劃`、`漂移防治路線圖_計劃`、`Systems/存量漂移守衛`、`Systems/筆記內容閘` 皆存在;路線圖第 63 行確實把第 6、11 項寫成「另案待開」;既有測試 `t_drift_when_probes_evaluate_and_trigger` 的 ⑨ 確為「新寫一條終點已經成立的條件式:擋」)。
- 〈做法〉1.3 推送判定候選、〈做法〉2.3–2.7、〈實務隱患〉其餘條目(併發、回滾、相容、金流/對外/不可逆的排除):已讀,無 finding。實務隱患鏡頭逐類:併發無(只讀 git 物件,scan 不寫帳);回滾無(r1 已寫清,且舊版對 `when-gone` 的處理確為 `_probe_parse` 回 `bad`、`_drift_probe_check` 略過,與 spec 一致);誤擋/繞過見 U3(判不了擋推送的可診斷性)與 spec 自己寫的表態繞過;效能見 U1(無上限讀檔)、U7;跨環境見 U2、U5、U6。
- 〈驗收條款〉:已讀,無 finding(未見未綁測試的條款;條款數與測試名一致)。
- 〈回退〉〈天花板〉:已讀,無 finding(U6 的合併歷史情形不在天花板,已併入 U6)。

最嚴重 severity 是 major,blocking 共 1 條(U1)。
