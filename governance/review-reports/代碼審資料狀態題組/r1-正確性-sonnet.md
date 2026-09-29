severity: blocker

## 逐節閱讀記錄

frontmatter(WHY/PRIOR-ART/REVISIT):已讀,無獨立 finding(WHY 第 4 句的風險在下面 F5 展開)。
現況:已讀,無 finding。
設計 1-8:F1、F2、F3、F5 見下。
驗收條款 S1-S7:F1、F4、F5 見下(S1/S3/S7 分別被牽連)。
回退:已讀,查證屬實——`_dispositions_verdict`(scripts/lumos:31738-31760)只迴圈 `meta.items()`(即當次重算出的 `stack_questions_meta`)去 `disp.get(qid)` 找表態,從不迴圈 `disp` 自己的鍵,所以題表拿掉 `data` 鍵後,舊表態記錄裡殘留的 `ds-*` id 確實不會被讀到、也不會被拿來擋——「讀側對不在題表的 id 本來就忽略」這句對照程式碼查證屬實,無 finding。
實務隱患:F6 見下。
最小實驗、撤除條件、誠實界線:已讀,無 finding(誠實界線已自承 helper 藏寫檔的侷限,不重複標記)。

## F1 「不管副檔名是哪一棧」跟現有一檔一棧架構衝突,extension 已有棧的檔會漏問

severity: blocker
blocking: 是(literal 實作可以通過全部 7 條驗收測試,但功能對絕大多數真實檔案完全失效,直接違背本計劃的立案目的)
引句:「不是簿記檔的增刪行,不管副檔名是哪一棧」

設計第 2 條要求「這次改動裡所有『需要有家的程式檔』…不管副檔名是哪一棧」都要餵進資料狀態題組的觸發比對。但現有棧別觸發的收集管線是一檔一棧:`_pitfall_diff_collect` 裡 `_by_stack` 的收集迴圈(scripts/lumos:26116-26122)對每支改動檔只呼叫一次 `_stack_key_for_file(f, repo_root)`,拿到單一字串鍵就 `_by_stack.setdefault(sk, []).extend(lines_)`;`_stack_key_for_file`(scripts/lumos:20221-20230)本身也只 `return ext if ext in _STACK_PERF_QUESTIONS else None`,一支檔只能回一個鍵。凡是副檔名已經對到既有棧(`.py`/`.kt`/`.cs`/`.java`/`.sql`/`.swift`/`.js`/`.ts` 等,`_STACK_QUESTION_SPECS` 已涵蓋,scripts/lumos:20018-20168)的檔,`sk` 一律回該棧(例如 `.py` 回 `"py"`),這支檔的改動行就只會進 `_by_stack["py"]`,不會同時進 `_by_stack["data"]`——除非額外新寫一段跟 `_stack_key_for_file` 平行、以 `_is_code_file` 為準的第二收集路徑,而設計 1-8 條完全沒有提到要新增這第二條路徑;設計第 1 條反而寫「所以表態範本、`code-loop check`、`gov --stats`、`recall-miss` 全部照舊運作,不另寫閘」,暗示只是多加一個題表鍵,不需要改收集管線的形狀。

具體會做錯的輸入:改一支既有 `foo.py`,新增一行 `os.replace(tmp_path, final_path)`(spec 本身在 `ds-partial-write` 題目文字裡舉的正是「暫存檔再改名」這個範例)。這行不命中任何 `py-*` 題的 when(`py-eventloop`/`py-parallel`/`py-external`/`py-memory`/`py-hotpath` 五題的觸發字裡都沒有 `os.replace`,已逐一核對 scripts/lumos:20098-20107),所以 `_stack_key_for_file("foo.py", …)` 回 `"py"`,這行只進 `_by_stack["py"]`,py 棧全表都不適用(沒觸發、也沒超過行數門檻)。若實作沒有另外接一條「不論 sk 是什麼,只要 `_is_code_file` 為真就也塞進 `_by_stack["data"]`」的路徑,`_by_stack["data"]` 就不會拿到這行,`ds-partial-write` 永遠不會被列為適用——同一行改在沒有副檔名的 shebang 腳本裡(S1 的情境)卻會觸發,因為那種檔今天 `sk` 本來就是 `None`,不會跟既有棧打架。也就是說,S1 只驗證了「沒有棧衝突」的邊界情況,完全沒驗到「已有棧的檔」這個最常見的真實案例;一個只做到讓 S1-S7 逐字通過的實作,可以讓 `ds-` 題組對 py/kt/cs/java/sql/swift/js/ts 檔案裡的資料狀態改動永遠不出題。

## F2 `_is_code_file` 的副檔名白名單漏了 dart/cjs/mts/cts,這些檔永遠進不了資料狀態題組

severity: major
blocking: 是(依設計第 2 條字面選的收集判準本身有漏,會讓特定語言全棧漏問)
引句:「每支檔有家那套判定,含沒副檔名但首行是 `#!` 的腳本」

設計第 2 條明講收集判準沿用「每支檔有家」那套(即 `_is_code_file`)。但 `_is_code_file`(scripts/lumos:6199-6228)呼叫 `_nodehome_code_kind`(scripts/lumos:22474-22481):有副檔名的檔只有在副檔名落在 `_NODEHOME_CODE_EXTS`(scripts/lumos:22258-22259:`{".cs", ".vue", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".sql", ".py", ".kt", ".kts", ".java", ".swift", ".go", ".rs", ".c", ".cc", ".cpp", ".h", ".hpp", ".sh", ".ps1"}`)才算 `"ext"`(算程式檔),否則直接回 `None`(不是程式檔,不會落到 `"shebang?"`——`shebang?` 只給完全沒有點的檔名)。這份清單沒有 `.dart`,而 `_STACK_QUESTION_SPECS` 已經有完整的 `"dart"` 棧(scripts/lumos:20136-20168);清單也沒有 `.cjs`/`.mts`/`.cts`,而 `_stack_key_for_file` 透過 `_NODE_EXTS`(scripts/lumos:20218)把這三種副檔名歸進 `"node"` 棧。

具體會做錯的輸入:改一支 `lib/storage.dart`,新增一行 `await file.writeAsBytes(bytes)`(中途寫壞、沒有先寫暫存檔再 rename 的典型 partial-write 風險)。`_is_code_file(rr, "lib/storage.dart")` 因為 `.dart` 不在 `_NODEHOME_CODE_EXTS` 裡,`_nodehome_code_kind` 回 `None`,判定「不是需要有家的程式檔」。若資料狀態題組的收集迴圈真的照設計第 2 條字面用 `_is_code_file` 當閘,這行永遠進不了 `_by_stack["data"]`,`ds-partial-write` 對這支 `.dart` 檔永遠不會列為適用——即使同一段邏輯改在 `.py`(假設 F1 已修好)或沒有副檔名的腳本裡都會被問到。這跟設計第 2 條自己宣稱的「不管副檔名是哪一棧」直接矛盾:`_NODEHOME_CODE_EXTS` 與 `_STACK_QUESTION_SPECS`/`_NODE_EXTS` 是兩份沒有互相同步的清單,設計沒有指出要調和它們。

## F3 用 `_is_code_file` 當閘,遺漏 `vend_skip`,消費專案裝進去的工具自身檔會被誤問

severity: major
blocking: 是(重新引入程式碼裡明確記載、已經修過一次的誤判類別)
引句:「每支檔有家那套判定,含沒副檔名但首行是 `#!` 的腳本」

`_pitfall_diff_collect` 現有的棧別觸發收集(`changed_lines`)是透過 `_stack_changed_ok(cur_file, vend_skip)`(scripts/lumos:25853-25870,呼叫處 scripts/lumos:26081/26090/26095)過濾的;`vend_skip` 是消費專案裡「工具鏈自己安裝、內容沒被改過」的檔案集合(由 `_vendored_state` 算出,scripts/lumos:26052-26057),專門排除掉這類檔案,理由在程式碼註解裡寫得很白:2026-09-10 那次修法之前,消費專案第一次提交把工具鏈自己的 CLI/hook 一起帶進去,風險報告被工具自己的程式碼撐成 high,逼人審查不是自己寫的碼。

設計第 2 條選的收集判準是「每支檔有家那套判定」——也就是 `_is_code_file`,這支函式完全不知道 `vend_skip` 這件事,它只排除 `_NODEHOME_EXCLUDE_GLOBS`/測試檔/`.lumos` ignore 設定(scripts/lumos:6204-6210)。如果資料狀態題組的收集迴圈直接拿 `_is_code_file` 當唯一閘(而不是沿用已經被 `vend_skip` 過濾過的 `changed_lines`/`_by_stack` 既有結果去追加),消費專案裡跟安裝時一模一樣的 `scripts/lumos` 或它的 hook 檔——這些檔本身就有大量 `os.replace(`/`open(...'w')`/檔案寫入邏輯——只要被算進這次 diff 範圍,就會被 `_is_code_file` 判定為程式檔,資料狀態七題全部或部分被判適用,推播前的表態閘會要求消費專案的作者去回答「工具自己怎麼防止寫一半當掉」這種不屬於他們程式碼的問題。這正是 `vend_skip` 當初要擋掉的那一類誤判,設計裡完全沒提到資料狀態題組的收集要不要沿用 `vend_skip`。

## F4 為了讓 S1 過關而修改 `_stack_key_for_file`,會讓舊版 `stack_questions` 印出被 S7 明文禁止的標籤

severity: major
blocking: 是(S1 與 S7 兩條驗收條款所隱含的實作路徑互相打架)
引句:「當有資料狀態題適用,pitfalls 的 diff 模式人讀輸出應印」

S1 要求沒有副檔名、首行 `#!` 的腳本能讓 `ds-partial-write` 適用。要在現有一檔一棧架構裡讓這種檔案有任何鍵可用(不靠額外新收集路徑,只改 `_stack_key_for_file` 本身),最直接的做法是把 `_stack_key_for_file` 的 fallback 改成:副檔名為空、shebang 檢查通過、且沒有對到其他棧時,回傳 `"data"`。但 `_stack_key_for_file` 是單一源,同時餵給 `_pitfall_diff_collect` 裡舊語意的 `stack_qs` 收集(scripts/lumos:26106-26112:`sk = _stack_key_for_file(f, repo_root); if sk and sk not in stack_qs: stack_qs[sk] = _STACK_PERF_QUESTIONS[sk]`),這個 `stack_qs` 就是輸出裡 `data["stack_questions"]`(舊語意,非 `stack_questions_meta`)。而 `_pitfall_diff_mode` 印人讀輸出時,對 `stack_questions` 走的是完全通用、沒有特例的迴圈(scripts/lumos:26235-26238):

```
for stk, qs in data.get("stack_questions", {}).items():
    print(f"  [{stk} 效能檢核]")
```

一旦某支沒副檔名的 shebang 腳本讓 `_stack_key_for_file` 回 `"data"`,它就會被收進 `stack_qs["data"]`,這個通用迴圈會原樣印出 `"  [data 效能檢核]"`。這正是設計第 5 條與 S7 明文禁止的字串(S7:人讀輸出「不得印成『data 效能檢核』」,應印「資料狀態檢核(跨棧)」)。也就是說,滿足 S1 最直接的實作路徑,會自動產生違反 S7 的輸出,除非額外在這個通用迴圈裡把 `"data"` 特判掉——設計文件的第 5 條只交代了期望的最終字串,沒有交代要去改這個目前對所有棧都一視同仁的印表迴圈,也沒有交代 `"data"` 到底該不該流進舊語意的 `stack_questions`/`stack_qs` 這個 dict。

## F5 資料狀態棧的行數會是「跨全部程式檔的總和」,幾乎必超過 `ask_all_over_lines` 門檻,直接觸發設計第 4 條想避免的「全表適用」

severity: blocker
blocking: 是(計劃自己在 WHY 段承認這是要避免的失效模式,設計段落卻沒有給出防止它發生的機制)
引句:「其他棧超過門檻全表適用的規則照舊,資料狀態題組只看觸發字」

`_stack_applicability(lines_by_stack, threshold)`(scripts/lumos:20281-20311)對每一個棧鍵各自算 `over = len(raw_lines) > threshold`(scripts/lumos:20292),`over` 為真就讓該棧全部題目適用(scripts/lumos:20296-20297:`if over: hits = [f"行數>{threshold}"]`)。這支函式是所有棧共用同一份、沒有针對鍵名的特例。`threshold` 預設 300 行(`_STACK_ASK_ALL_DEFAULT`,scripts/lumos:20235),且是專案層級單一設定(`_stack_questions_config`,scripts/lumos:20238-20265),不分棧。

如果資料狀態題組按設計第 2 條收集「這次改動裡所有程式檔」的增刪行,`_by_stack["data"]` 的行數會是這次改動裡所有語言、所有棧加總的行數——遠大於任何單一語言棧自己的行數。只要這次改動總共動了 300 行以上的程式碼(對一個涉及多個檔案的正常 PR 來說太容易達到,即使個別檔案都很小),`_by_stack["data"]` 就會超過同一個 `threshold`,`_stack_applicability` 就會把全部 `ds-` 七題判定適用(`triggered_by=["行數>300"]`),不管有沒有任何觸發字命中——這正是 S3 明文要求不能發生的情況(「該檔所屬的棧全表適用,而 `ds-` 題全部維持不適用」),也正是計劃 WHY 段自己寫的「它跨所有程式檔,大一點的改動幾乎必過門檻,每次多七題 na 會把表態變成儀式」。設計 1-8 條裡沒有一條講到要把 `"data"` 這個鍵從 `_stack_applicability` 的 `over` 判斷裡摘出來,或是另外接一條不算行數門檻的判定路徑;直接沿用現有函式(設計第 1 條承諾的「全部照舊運作」)就會讓這個計劃在立案時就已經指名要避免的失效模式,在幾乎每一次夠大的改動裡發生。

## F6 逃生口只有專案層級整體開關,沒有只關資料狀態題組的旋鈕

severity: minor
blocking: 否(有逃生口存在,只是不夠精準,不到「做錯事」的程度)
引句:「誤擋的逃生口沿用既有的 `na`(附理由)與設定檔 `stack_questions.gate`(all/high-only/off)」

若 F5 那種誤亮成常態,作者唯一能整批關掉資料狀態題組噪音的手段是把 `stack_questions.gate` 設成 `high-only` 或 `off`(`_stack_questions_config`,scripts/lumos:20238-20265,值只認 `all/high-only/off` 三種,scripts/lumos:20234)。但這個開關是專案層級、對全部棧(kt/cs/vue/sql/swift/node/py/java/dart 全部九棧)一視同仁,不是只針對 `data` 鍵。也就是說,若某專案覺得資料狀態題組因為 F5 的問題太吵想關掉它,唯一手段會連帶關掉這個專案原本運作正常的 kt/cs/... 等其他棧別檢核題(或把它們一起降到 high-only)。設計沒有提供逐鍵(per-key)的 gate,只在 na 之外提到既有的整體開關,這會讓作者面臨「要嘛全部關、要嘛全部忍」的兩難,增加改走 `--no-verify` 的機率,但因為 na(附理由)這條路徑本身還在、且 blocking 判準要求要有具體失敗場景,這條先標 minor、不擋。

## 總結

最嚴重 severity:blocker(F1、F5)。blocking 共 5 條(F1、F2、F3、F4、F5);F6 不擋。
