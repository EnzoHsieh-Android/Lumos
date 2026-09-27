severity: blocker

## 開頭與 PRIOR-ART 已讀,無 finding

「WHY:」「PITFALL:」「RETIRE-IF」「REVISIT」段落已讀,無 finding——這幾行本身沒有可執行性缺口,問題都出在後面〈做法〉節具體借用的函式上,見下方 F1–F3。

## F1 圍欄選項救不了圍欄內容,因為抽取器一開始就把圍欄整段吃掉

severity: blocker
blocking: 是 —— 不改,note-shape 會誤以為自己已經補上「圍欄內也查」這個 r1 三席指出的洞,實際上圍欄裡的行號引用永遠偵測不到,原洞照樣繞得過。

引句:「行號引用抽取擴充既有共用抽取器 `_node_code_ref_tokens`(加兩個選項:認裸文字、認 `#L`),預設行為不變」

spec 同時宣稱(做法/範圍與行節):「★程式碼圍欄裡的行照樣查★(原稿不查,r1 三席指出包進圍欄就一鍵繞過、圍欄沒關好連後面都看不到)。」

實測:`_node_code_ref_tokens(text, top_dirs)` 目前實作在抽取前無條件呼叫 `_strip_fences_text(text)`,而 `_strip_fences_text` 又是呼叫 `_visible_lines(text.split("\n"))`(預設 `keep_fenced=False`)——這會把整段圍欄★內容★(不只是 ``` 標記行)從文字裡刪掉,不是「認得圍欄但跳過反引號 span」那種輕量濾除。

- file: `scripts/lumos:19861` `spans = [s.strip("`") for s in INLINE_CODE_RE.findall(_strip_fences_text(text))]`——抽取前就先剝圍欄。
- file: `scripts/lumos:3277` `return "\n".join(ln for _no, ln in _visible_lines(text.split("\n")))`——`_strip_fences_text` 沒有任何參數可以保留圍欄內容,`keep_fenced` 寫死沒傳。
- 實際跑一次(python 匯入 `scripts/lumos` 呼叫 `_node_code_ref_tokens`):
  1. 輸入 `FACT: 這是筆記\n\n\`\`\`\n輸出範例:\nscripts/lumos:1234 這裡壞了\n\`\`\`\n`(裸文字、無反引號包住路徑)→ `full=[]`。
  2. 輸入把圍欄內那行改成加反引號 `` `scripts/lumos:1234` ``(標準寫法)→ `full=[]` 仍是空的。
  3. 對照 `_strip_fences_text(text2)` 的輸出:`'FACT: 這是筆記\n\n'`——圍欄整段(含反引號包住的 `scripts/lumos:1234`)已經在抽取前被物理刪除,不管後面加不加「認裸文字」「認 `#L`」選項都看不到這段文字了。

推得的失敗場景:一篇被審筆記在圍欄裡貼了舊指令輸出(例如 `\`\`\`\nscripts/lumos:5000 這裡有洞\n\`\`\``),提交前 note-shape 依 PRIOR-ART 描述的做法(只加兩個選項)去跑,rc0 放行——跟 r1 三席原本抓到的「圍欄一鍵繞過」是同一個洞,只是形式從「r1 審查時的原稿完全不查圍欄」變成「r2 修訂稿宣稱查了,但用來查的函式本身結構性看不到圍欄內容」。要真的做到「圍欄內照查」,`_node_code_ref_tokens`(或它呼叫的 `_strip_fences_text`)需要第三個選項——保留圍欄內容(例如改用 `_visible_lines(text.split("\n"), keep_fenced=True)` 這條路),但 PRIOR-ART 只承諾「加兩個選項:認裸文字、認 `#L`」,沒有這第三個選項,也沒在別處提到會改 `_strip_fences_text` 的呼叫方式。

## F2 合併提交借的是「檔案有沒有新行」的布林判定,不是「哪幾行是新的」——note-shape 需要行級資料,借來的東西給不了

severity: major
blocking: 是 —— 不改,實作者要嘛照抄檔案級判定去核對整支檔全文(誤把合併雙方帶進來的舊行也當新行掃、over-block),要嘛得另外重寫一套行級 diff(等於 PRIOR-ART 沒講清楚的額外工作量,審查沒機會先看過)。

引句:「推送前的合併提交只算它自己多改的行(不算從另一個父提交帶進來的)。」

[S5] 條款也要求同樣的行級判定:「推送前的合併提交只應算它自己多改的行,從另一個父提交帶進來的不應算」。

佐證:

- file: `scripts/lumos:22757` `def _nodehome_merge_wrote_new_lines(merged, olds):`——docstring 自述「合併提交裡,這支檔有沒有『兩個上一版都沒有的新行』」,回傳值是 `bool`(見 22776:`return any(...)`),不是新行本身或行號集合。
- file: `scripts/lumos:22708-22716` `_nodehome_merge_own_changes` 內部迴圈裡把每支檔的 `merged`/`olds` blob 讀出來只為了呼叫 `_nodehome_merge_wrote_new_lines` 判斷要不要把這支檔加進 `kept`(一個路徑集合),blob 內容本身在函式回傳前就丟棄,呼叫端(`_nodehome_evaluate` 等)拿到的只是「這些檔要當合併自己改的」路徑清單,不是行號或行內容。

推得的失敗場景:兩條分支各自改同一篇筆記的不同段,合併時 git 自動合起來(無衝突,兩段都留)。按 PRIOR-ART「合併提交處理...`_nodehome_merge_own_changes`」整套借的說法,note-shape 若真把回傳的 `kept` 路徑集合當「這支檔本次要查」的訊號,接下來要嘛(a)對整支檔案在該提交裡的內容全文重新跑一次規則——這樣兩條分支各自早就寫好、通過檢查的舊 FACT:/行號引用內容,只因為同一支檔被合併記進 `kept`,也會被當成「這次提交新增」重新核對一次,分支甲那段裡如果本來就有一個沒被攔過的舊違規(甲分支自己提交時沒被攔到,例如上線點以前寫的),合併這下反而被攔下,跟「只算它自己多改的行」矛盾;要嘛(b)另外寫一套行級 diff 邏輯來抓「這個合併真正新增的具體行是哪幾行」——但這是 PRIOR-ART 沒承認過的新發明(它說「唯一新發明的是放行寫法 `路徑@<提交>:數字`」),條款 [S5] 要求的行為在字面上寫不出對應測試會通過的一種明確演算法。

## F3 golive 標記字串寫死成 node_home 自己的,不是 note-shape 的——照名字直接借這兩支函式會夾到錯的上線點

severity: major
blocking: 是 —— 不改,`_nodehome_clamp_base` 會把 note-shape 的範圍夾到「每支檔有家」2026-09-11 上線那個提交,而不是 note-shape 自己實際加進 pre-commit 的那個提交(兩者相差至少兩週),導致上線前就存在、依 d2 該當舊帳的內容被當成本次推送的新違規重新查一次。

引句:「起點早於 note-shape 上線的那個提交」

佐證:

- file: `scripts/lumos:22181` `_NODEHOME_GOLIVE_MARK = "home check --staged"          # [S39] 提交前掛鉤裡有這串=這道檢查上線了`——這是 node_home 專屬的標記字串常數,寫死在模組層級。
- file: `scripts/lumos:22856` `raw = _nodehome_git(repo_root, "log", "--reverse", "--format=%H", f"-S{_NODEHOME_GOLIVE_MARK}", tip or "HEAD", "--", "scripts/hooks/pre-commit")`——`_nodehome_golive` 內部直接引用模組常數 `_NODEHOME_GOLIVE_MARK`,函式簽名 `_nodehome_golive(repo_root, tip)` 沒有讓呼叫端傳入別的標記字串的參數。
- Systems/每支檔有家.md 的 `created: 2026-09-11`,而本計劃(筆記形狀擋)`created: 2026-09-27`——兩道閘上線相差超過兩週,絕不會是同一個提交。

推得的失敗場景:若照 PRIOR-ART 字面「連同它緊鄰的三個配套一起借——上線點截斷(`_nodehome_golive` / `_nodehome_clamp_base` 那種用提交前掛鉤裡的標記字串找上線提交)」的寫法直接呼叫這兩支既有函式(而不是另外寫一份參數化、可傳入 note-shape 自己標記字串的版本),`_nodehome_golive` 找到的永遠是「home check --staged」第一次出現的提交(2026-09-11 那批),`_nodehome_clamp_base` 就會把 note-shape 的範圍起點夾在那裡而不是 note-shape 實際掛進 pre-commit 的那個提交。後果:2026-09-11 到 note-shape 真正上線之間所有筆記異動(舊帳)全部落在「上線後」的範圍內,被當成這次推送的新增內容重新核對兩條規則——這正是 d2「舊筆記不回頭清,只在有人改到才順手處理」與 RETIRE-IF ①(誤擋)要防的情境,而且沒有任何 [SN] 條款測到「note-shape 自己的 golive 標記字串是什麼、跟 node_home 的是不是同一個」這件事,[S4] 的測試名 `t_note_lines_range_base_and_golive_clamp` 字面上驗的是「早於上線點時改從上線點算」,並不會驗到「找到的是誰的上線點」,所以這個洞不會被 [S4] 的測試抓到。

## 兩條規則(其餘部分)已讀,無 finding

規則 1 的「路徑在被檢查版本裡真的存在」「放行寫法 `路徑@<提交>:數字` 要求至少 12 位十六進位、找得到、該提交裡有此路徑」邏輯上可執行(`git cat-file`/`git ls-tree` 拿得到這些資訊),`HEAD`/分支名/相對寫法一律不算放行的判準清楚,沒有交叉引用或內部矛盾。規則 2 把 `[src:]` 改成 `[來源:…]` 這個改名,已用 `scripts/lumos:4600-4607`(`J-c:[src:] substring gate...直走 _validate_repo_ref`)核對過——`[src:部署]` 確實會被既有的 regen 佐證掃描器當成檔案路徑判成 dangling,所以改名是對的修正,不是新洞。

## 開關與跳過已讀,無 finding

「`note_shape.gate` 從被檢查的版本讀」與 `_nodehome_config(..., from_snapshot=True)` 的既有模式一致(`scripts/lumos:22184`、`23202`、`23314`),`block/warn/off` 三值與 `LUMOS_SKIP_NOTE_SHAPE` 環境變數兩者都是照既有鄰居 `lint_new.gate`/`LUMOS_SKIP_LINT_NEW` 的命名慣例(`scripts/lumos:20935`、`21479`),沒有內部矛盾。

## 治理帳寫入加鎖(移出)、紀律範本改寫、消費專案的 CI 已讀,無 finding

移出到 Issues/治理帳多個寫入者都沒上鎖 一節與該篇筆記內容核對一致(該篇也提到本計劃上線後寫帳頻率會變高,已預先寫明,不算遺漏)。紀律範本改寫與消費專案 CI 兩節沒有讀到可執行性缺口。

## 條款 [S1]–[S11] 逐條判

[S1] 依 F1,字面上寫不出會通過的測試(圍欄內容在抽取前已被物理清除)。[S2][S6][S7][S8][S9][S10][S11] 已讀,無 finding——判準與既有函式/慣例對得上,執行路徑清楚。[S3] 已用程式碼核對過 `[來源:]` 改名不會被 regen 佐證掃描誤傷,無 finding。[S4] 依 F3,測試名字面驗不到「用錯上線點」這個具體風險,但 clamp 的方向性描述(早於上線點時改用上線點)本身沒錯,是借用函式的參數化缺口造成的執行落差,已併入 F3 陳述。[S5] 依 F2,行級新增判定所需的資料結構,借來的函式沒有提供。

## 回退、實務隱患、誠實界線、審計修正紀錄已讀,無 finding

回退順序與「note-shape 指令先留一版空殼再刪」的考量,與代碼審 r1 折入紀錄描述一致,沒有發現新的矛盾;實務隱患與誠實界線兩節誠實揭露的天花板(圍欄誤擋抽樣沒做過、句型漂移比對三分之一準度)跟本席查到的 F1 是同一類風險(圍欄行為),但角度不同(spec 承認的是「誤擋」風險,F1 抓到的是「根本測不到」——方向相反,不是同一顆洞,故仍需獨立列 F1)。

## 總結

最嚴重 severity:blocker(F1)。blocking 共 3 條(F1、F2、F3)。
