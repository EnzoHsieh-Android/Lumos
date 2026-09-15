severity: major

# 標註防污染 r1——測試品質審查(sonnet)

只判一件事:這批新增的兩支測試(`t_delta_sheet_is_shuffled`、`t_rater_material_has_no_labels`)守不守得住——日後有人把對應修法改回去,會不會翻紅,還是靜靜地繼續綠。方法是把 `governance/eval/refresh_labels.py` 複製到 `/tmp/mut-review/`,逐條拆掉修法、跑 `python3 scripts/test_lumos.py -k <關鍵字>`、看翻不翻紅、還原確認轉綠,每次拆完都先清 `__pycache__` 再跑。全程沒有修改 repo 裡任何檔案。

另外做了一件額外的事:工作目錄裡 `scripts/test_lumos.py` 與 `governance/eval/refresh_labels.py` 目前有未提交的改動,比 r1-snapshot.patch 記載的內容更新。為了確定我測的是「這份 r1-snapshot.patch 真正落地的樣子」,用 `git cat-file blob 8705765f`(refresh_labels.py)、`git cat-file blob fb8890f9`(test_lumos.py)——也就是這份 diff 記載的「+」側 hash——單獨抽出兩支檔案的確切內容來核對,不受工作目錄後續改動干擾。這兩個 blob 剛好等於 commit `f6d481c5`(當前 HEAD),但工作目錄比 HEAD 更新的部分被排除在這次審查之外——不過下面發現一會用到它作材料外佐證。

## 發現一:`material` 有一條真實漏洞測試從沒餵過,不是斷言失靈,是測試沒讓被測路徑跑起來

`cmd_material` 組編輯題那段,把題庫裡的 `delta`(改動說明文字)原樣接進輸出:

severity: major
blocking: 是——這條漏洞在 r1 這個 commit 裡本來就是活的,我拿 r1 版本的 `cmd_material` 實測會漏,不是理論上的邊界案例;另一位審查員(`r1-外家finder-codex.md`)已獨立判定這條是 blocker 並列出修法,尚未併入這批 patch。測試套件目前對外顯示「全綠、防污染已補齊」,實際防線有缺口。

引句:「lines.append(f"- {c['id']}｜改到的檔:`{c['file']}`｜改動:{c.get('delta', '(未記)')}")」

我用 `git cat-file blob 8705765f` 還原出 r1 這支確切版本的 `refresh_labels.py`,直接呼叫它的 `cmd_material`,餵一個編輯題、`delta` 欄位寫成 `"# 見 Systems/Beta.md 的說明;另參 Projects/Gamma.md"`(`Systems/Beta.md` 是題庫裡已判 `final: 2` 的答案節點),產出的 `material.md` 原文一字不動印出這段文字,答案節點路徑就這樣混進了卷頭寫著「★這份刻意不含任何既有標註★」的材料裡。

要強調的是:**現有的判斷方式(掃 `"Systems/Beta.md" not in txt`)如果真的跑到這個輸入,是抓得到的**——問題不是「掃文字擋不住答案換形式出現」這種斷言強度問題,而是 `t_rater_material_has_no_labels` 自己的 fixture 從頭到尾兩個編輯題的 `delta` 都寫死 `"(x)"`,從沒有一次讓 `delta` 帶節點路徑,所以這條真實存在、後來被判定可利用的洩漏路徑,測試從來沒跑到過。這是「被測的路徑根本沒跑到,測試卻綠」的空過,只是這次空的不是防線本身,是防線從沒被檢查過。

材料外的佐證:
- 工作目錄裡 `governance/eval/refresh_labels.py`(尚未提交)已經多出一段專門處理這件事的正規表示式遮蔽邏輯,註解寫著這是「2026-09-15 外家席 blocker」,而且自陳「現況題庫剛好零命中,但那是運氣不是守衛」。file: `governance/eval/refresh_labels.py:136`
- 我另外直接對版控裡目前的正式題庫(`governance/eval/retrieval-goldset.json`)跑了一次同樣的偵測樣式:23 題編輯題裡 0 題的 `delta` 命中節點路徑——證實「零命中」目前是真的,但只是資料剛好乾淨,不是有東西在擋。file: `governance/eval/retrieval-goldset.json`
- r1-snapshot.patch 自己在計劃筆記裡列出的變異驗證清單,三種變異都圍繞「整份題庫被複製 / 洗牌邏輯被拆」,沒有一種是「答案透過 `delta` 欄位夾帶進題目內容」——是完全不同的攻擊面,清單再長也沒照到這條:

引句:「全套 6086 綠;兩支新測試各自做過變異驗證(拆先排序、拆整個洗牌、材料改成複製整份題庫)。」

## 發現二:`t_delta_sheet_is_shuffled` 的翻紅釘數字跟實測對不上

docstring 寫:

severity: minor
blocking: 否——測試整體仍會被判定 FAILED(FAIL 計數確實增加),不影響它抓不抓得住這個迴歸;只是條號跟實測對不上,將來有人只看 docstring 決定某條斷言能不能刪,可能因為誤標而砍錯東西。

引句:「翻紅釘:把 cmd_delta 的洗牌拿掉 → 第 1、2 條翻紅(順序變回名次序)。」

我把 `cmd_delta` 的洗牌整段拆掉(還原成 patch 之前的寫法:`cases = [{"id": cid, "unjudged": nodes} for cid, nodes in sorted(u["per_case"].items())]`),連跑三次確認結果穩定。實際翻紅的是「★端出去的順序不是名次序★」跟「★上游順序被打亂時吐出來的表仍要一樣★」這兩條(檢查清單裡實際排序的第 1 條與第 4 條),而 docstring 點名的「第 2 條」——

引句:「★同一份題庫跑兩次順序一樣★(不可重現的話標註結果回溯不到當初看的是什麼)」

——在這個 fixture 底下就算洗牌整段拆光仍然是綠的,因為兩次子行程呼叫在這組固定夾具、固定候選內容上,排序本身就是穩定可重現的,不需要靠洗牌來保證。

## 發現三:任務特別點名要查的「作者自己承認第一版是假的」那個毛病,這版確認真的修掉了

先前版本的問題是測試自己重算一遍排序邏輯,把產品端的修法拆掉照樣全綠。現在這版的關鍵斷言不再自己重算,而是換掉 `refresh_labels` 模組的 `_load_re` 入口,讓上游 `collect_unjudged` 回傳「同一批候選、但順序被打亂」,再真的呼叫一次產品的 `cmd_delta` 本體:

severity: clean
blocking: 否——沒有發現問題,列出來是因為這正是本次審查特別要求核對的項目。

引句:「_rl._load_re = _load_shuffled」

比對基準(`ranked`)也不是測試自己算出來的排序結果,是另外用一份乾淨的 `retrieval_eval` 模組實例呼叫真正的 `collect_unjudged` 拿到的原始名次序,拿來跟洗過的輸出比對「不相等」。我實測了兩種對應的變異:①整段洗牌邏輯拆光(還原成 patch 前寫法)②只拆「先排序」那一步、保留隨機洗牌本身(直接洗未正規化的 `nodes` 而不先 `sorted()`)。兩種都會讓「★上游順序被打亂時吐出來的表仍要一樣★」翻紅(見下方變異測試表第 1、2 列),因為這條斷言比的是「產品真的跑過一次」的輸出,不是測試自己心裡的期望值。這條斷言目前守得住。

## 發現四:洗牌測試的「候選數要 ≥4」前置條件,不成立時不會被誤判成整支測試通過

severity: clean
blocking: 否——沒有發現問題,列出來是因為這正是任務要求特別核對的項目(前置條件會不會空過)。

引句:「★前置★ 有候選數夠多的案例可驗(不然這支測試等於空過)」

兩支新測試都有一條「★前置★」開頭的斷言,失敗時函式會提早 `return`,函式結尾仍會印一行「✓ <測試名>」——單看這行容易誤以為測試通過了。我實測把 fixture 縮到只造 1 個未標候選(必然低於前置門檻 4),結果整支測試被判定 `FAILED`,總計「0 passed, 1 failed」。原因是前置斷言本身也是用同一個全域 `check()` 記的,前置一旦不成立就已經算一條失敗,函式尾端那行「✓」只是函式自己的收尾訊息,不會蓋掉全域的失敗計數,不影響最終判定。

## 變異測試結果

| # | 植入什麼 | 跑哪支 | 實際輸出 | 判定 |
|---|---|---|---|---|
| 1 | `cmd_delta` 洗牌整段拆光,還原成 patch 前寫法(`sorted(u["per_case"].items())` 直接輸出,不排序不洗牌) | `t_delta_sheet_is_shuffled` | `5 passed, 2 failed`;「★端出去的順序不是名次序★」與「★上游順序被打亂時吐出來的表仍要一樣★」翻紅,「★同一份題庫跑兩次順序一樣★」仍是綠的 | 守得住(整體判 FAILED),但紅的是第 1、4 條而非 docstring 講的第 1、2 條(見發現二) |
| 2 | 只拆「先排序」,保留洗牌:`_shuffled = sorted(nodes)` 改回 `_shuffled = list(nodes)`(直接洗未正規化的上游順序) | `t_delta_sheet_is_shuffled` | `6 passed, 1 failed`;僅「★上游順序被打亂時吐出來的表仍要一樣★」翻紅 | 守得住——這正是任務點名的「作者自己承認第一版是假的」那個場景,現在的斷言會抓到(見發現三) |
| 3 | 保留完整洗牌邏輯,但洗完後砍掉一個候選(`_shuffled = _shuffled[:-1]`) | `t_delta_sheet_is_shuffled` | `6 passed, 1 failed`;「洗牌不得增減候選(只換順序)」翻紅,detail 顯示「洗過 8 個、名次 9 個」 | 守得住 |
| 4 | fixture 縮到只造 1 個候選節點,讓前置條件「候選數 ≥4」必然不成立 | `t_delta_sheet_is_shuffled` | `0 passed, 1 failed`;前置斷言本身翻紅,函式提早返回,但整體判定 FAILED | 守得住,不會空過成「通過」(見發現四) |
| 5 | `cmd_material` 改成把整份 goldset(含 `labels`)`json.dumps` 直接寫進材料檔 | `t_rater_material_has_no_labels` | `3 passed, 2 failed`;「★材料裡找不到任何標註欄位名★」與「★材料裡找不到既有答案的節點路徑★」翻紅,與 docstring 講的「第 2、3 條」吻合 | 守得住,翻紅釘數字也對 |
| 6 | 不動任何程式碼,直接用 r1 版本的 `cmd_material`(`git cat-file blob 8705765f`)餵一個編輯題,`delta` 欄位寫 `"# 見 Systems/Beta.md 的說明;另參 Projects/Gamma.md"`(`Systems/Beta.md` 是已判 `final: 2` 的答案節點) | 手動呼叫 r1 版 `cmd_material`(不是跑既有測試——既有測試的 fixture 從不產生這種輸入,無從測起) | `material.md` 原文照印出「見 Systems/Beta.md 的說明;另參 Projects/Gamma.md」,答案節點路徑外洩,`cmd_material` 回傳 0(正常結束) | 守不住——`t_rater_material_has_no_labels` 從未產生過這種輸入,不會發現這條真實漏洞(見發現一) |

## 小結

最高等級是 major,一條列為阻塞。兩支新測試對它們自己設計要擋的主要威脅(端出去的順序洩漏名次、材料檔含整份 `labels`)都做了會真的呼叫產品程式碼的變異驗證,經我獨立重跑對應的四種拆解,結果都撐得住,包含任務特別點名要查的「自己重算一遍」那個舊毛病確認已經改成呼叫真產品程式碼。但 `t_rater_material_has_no_labels` 沒有涵蓋答案透過編輯題 `delta` 欄位夾帶流入材料的路徑,這條路徑在 r1 送審當下就是可利用的真實漏洞,而且已由另一位審查員判定阻塞、修法尚未併入這批 patch。
