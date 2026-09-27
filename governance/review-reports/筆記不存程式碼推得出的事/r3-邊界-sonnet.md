severity: blocker

# 逐節閱讀紀錄

- frontmatter(tags/lands_in/related):有 finding,見 F4。
- 白話/依據/拆分公告/PRIOR-ART/RETIRE-IF/REVISIT:已讀。ebb44369 提交、[[Systems/pitfalls-code-loop]]、[[Systems/外部對照-code衍生wiki]]、[[Projects/筆記形狀擋_計劃]]、[[Issues/治理帳多個寫入者都沒上鎖]]、[[Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋]]、[[Projects/Lumos定位_程式碼為主脈絡為輔_計劃]] 六個交叉引用逐一開檔核對,節點都存在、commit 都查得到。
- 判定者能不能用:小實驗:有 finding,見 F5(Issue〈擋什麼的初步實測〉查無此節點)。
- 做法 > 哪些行要審(借第一層,不另寫):有 finding,見 F1(★blocker★)。
- 做法 > 通過紀錄怎麼綁:逐行,不綁整批:有 finding,見 F2。
- 做法 > 第二層:推送前的筆記內容審:第 1–2、5–8 點已讀,無 finding(prepare 的原子寫入、`.gitignore`、`_gate_event` 契約、`--orchestrator` 必填規矩、doctor 事後掃都各自核過對應程式或既有先例,見下方查證附註);第 3 點(decision-amend)見 F3。
- 上線前校準:已讀,無 finding。
- 規範文字跟著改:已讀,`skills/lumos-project-notes/reference.md`、`commands/INDEX.md` 確實存在,無 finding。
- 條款 S5–S9、S11、S12、S14–S17:對照測試代號逐條核過,`t_note_audit_*`/`t_decision_amend_*`/`t_doctor_note_audit_*` 系列在 `scripts/test_lumos.py`、`scripts/lumos` 裡都還不存在(尚未實作,與計劃 status: doing 一致),條款本身敘述內部一致,無另外 finding。
- 回退:已讀,永久保留空殼指令、消費專案各自關開關、治理帳舊筆數照留三段跟 [[Projects/筆記形狀擋_計劃]] 的回退段同形狀,無 finding。
- 實務隱患/誠實界線:治理帳大小估算(25,282 行、每個內容編號 12 位十六進位、約 300 KB)重算數量級吻合,無 finding;其餘併發、可用性段落見下方隱患鏡頭。
- 審計修正紀錄:歷史記錄,不逐條覆核;用來核對 S 編號與測試代號沿革時沒發現本輪之外的新矛盾。

# 逐條 Findings

## F1 借第一層的行集合函式時,漏改一個一樣寫死看 pre-commit 的地方

severity: blocker
blocking: 是 —— 若照〈做法〉字面實作,第二層會永久收不到任何待審行,審查機制形同虛設且不會有任何錯誤訊號,屬於安全性/治理承諾被靜默架空。

spec 在〈哪些行要審〉一節說第二層「直接呼叫、不另寫」`_ns_range_added`(範圍裡每個提交各自新增的筆記行),並說「寫的時候這道檢查在不在」看的是推送前掛鉤(`scripts/hooks/pre-push`)有沒有第二層自己的上線標記,而現有函式「寫死看提交前掛鉤」,只需要替 `_nodehome_golive`/`_nodehome_clamp_base` 這兩支「上線函式」加掛鉤路徑參數即可。

引句:「不是提交前掛鉤——那支函式現在寫死看提交前掛鉤」

引句:「範圍起點的上線截斷同理(每支檔有家那兩支上線函式已經有標記參數,再加掛鉤路徑參數)」

查證:`_ns_range_added` 本身(不是 `_nodehome_golive`/`_nodehome_clamp_base`)內部也有一段完全獨立、同樣寫死路徑的「這個提交當時檢查有沒有上線」判定,用來決定每個提交的新增行要放進 `by_path`(算數)還是 `old_by`(算舊帳,note-shape 只用它做「喚醒」,不進違規判定):

file: `scripts/lumos:23602-23606`
```
    if mark and commits:
        hb = _nodehome_cat_blobs(repo_root, [f"{c[0]}:scripts/hooks/pre-commit" for c in commits])
        if hb is None:
            return None
        live = {c[0] for c, b in zip(commits, hb, strict=False) if b is not None and mark.encode() in b}
```
這段路徑字串是硬編碼 `"scripts/hooks/pre-commit"`,跟傳進來的 `mark` 是兩件事——`mark` 只決定「找什麼字串」,「去哪支檔找」完全沒有參數化。而且這不是可有可無的枝節:`_note_shape_eval` 呼叫它時一定會把自己的 golive mark 傳進 `mark=`(見 `scripts/lumos:23792-23794`:`mk = mark or _NOTE_SHAPE_GOLIVE_MARK; ra = _ns_range_added(..., mark=mk if _nodehome_golive(repo_root, tip_where, mk) else None, ...)`),而 [[Projects/筆記形狀擋_計劃]] 的驗收輪明講這個逐提交檢查是為了修一個實測到的漏查(「兩條分支各自裝過時,另一條上繞過寫的違規原本整批漏查」)特意加上去的,不是備援。

後果:第二層若真的「不另寫」,把自己的上線標記(例如 `note-audit check`)當 `mark` 傳進 `_ns_range_added`,這支函式仍然只會去 `scripts/hooks/pre-commit` 的歷史裡找這串字——而第二層的標記照 spec 自己的設計是寫在 `scripts/hooks/pre-push`,永遠找不到,於是 `live` 永遠是空集合,每個提交的 `sha in live` 恆為 False,所有新增行永遠被歸進 `old_by`(視為「這道檢查還沒上線時寫的」)。`_note_shape_eval` 的主迴圈只吃 `texts_by`(即 `by_path`)裡的行,`texts_by` 永遠是空字典 → 每個路徑的 `linenos` 判定 `ln.strip() not in texts_by.get(nfc(p), ())` 恆真 → 每一行都被跳過。也就是說,如果第二層照著〈哪些行要審〉字面描述的「只改兩處」去實作(golive 函式加掛鉤路徑參數,`_ns_range_added` 不動),`prepare` 永遠回報「沒有待審的筆記行」、`check` 永遠放行,而且不會有任何報錯——跟设计目标「機械擋」正好相反,而且不會留下任何可觀察的異常(rc0、看起來一切正常)。這正是 spec 要求 review 特別注意的「補丁與原文銜接處的新不一致」:S17 的測試名稱(`t_note_audit_lines_reuse_note_shape_range`)雖然可能會在寫測試時意外抓到,但〈做法〉敘述本身沒有指出這第三處寫死的地方,屬於可執行性缺口。

## F2 `decision-amend` 的「不存在於任何遠端」判準,對兩條各自尚未推送、獨立指定同一個決策編號的分支會誤判

severity: major
blocking: 是 —— 會讓作者被擋在自己尚未推送過的內容外,且被導向語意錯誤的翻案指令。

spec S12 與正文都把「這個決策編號有沒有出現在任一遠端追蹤參照的同一篇裡」當成唯一判準,且強調這個判法「跟分支拓撲無關」:

引句:「逐一讀遠端追蹤參照上的同一篇來判,跟分支拓撲無關;沒有任何遠端就都能改」

查證:決策編號本身是每次 `decision-add` 時對「這個節點目前檔案內容」取 `max id + 1` 純本機、順序指派,完全不看任何遠端:

file: `scripts/lumos:14923-14924`
```
    loc = decisions_items(fm)
    new_id = f"d{_max_decision_id(fm) + 1}"
```
場景(可重現):main 上某篇筆記的決策編號到 `d5`。分支 A、分支 B 各自從同一個 base 切出,互不知道對方,各自對同一篇筆記 `decision-add` 一條新決策——兩邊本機算出來的都是 `d6`,但內容不同。A 先推、被判定者標成「程式碼推得出」後用 `decision-amend d6` 改寫成脈絡版本並推上 `origin/main`。B 這時還沒 rebase(甚至還沒 fetch 到 A 的推送前就已經 fetch 過),只是被自己這輪 judge 標記到「d6 也要修」,執行 `lumos decision-amend d6`——照 S12 的判法,`origin/main` 的同一篇筆記裡已經有 `d6`(A 寫的,內容完全無關),所以會被拒絕、導向翻案指令,即使 B 自己的 `d6` 從來沒推上任何遠端。翻案(supersede)在語意上是「這條決策後來被推翻」,但 B 的 `d6` 根本不是 A 的 `d6`,只是編號恰好相撞——這是決策編號指派機制(本機順序、無跨分支協調)本來就有的先天限制,S12 把它包裝成「跟分支拓撲無關」的強判準,反而在這個常見的平行分支情境下把一個純粹的編號碰撞誤判成「已推上遠端」,擋下作者對自己尚未推送內容的合法修改。

## F3 內容編號不分區塊,同一篇裡「巧合撞成一樣的一行文字」會被強制套同一個判定

severity: major
blocking: 是 —— 可能讓本該擋下的一行,因為跟別處一句被判成脈絡的文字巧合相同而被連帶放行(逃逸路徑),也可能反過來讓一句合法脈絡話被誤擋。

spec 定義內容編號時只取「路徑」與「去頭尾空白後的行文字」兩個維度,不含區塊(body/summary/decisions)、不含行號:

引句:「=(NFC 路徑,去頭尾空白的行文字)的短雜湊;通過紀錄列出這次判成可以留的那些內容編號」

而 `prepare` 對重複文字的處理方式,是把同一個內容編號底下的所有出現位置合併列出,交給判定者對「這一個編號」下「一個」判定:

引句:「同一段文字在同一篇出現好幾次,列出每一處的行號與次數」

配合〈做法〉第 2 點「每行判定寫成『內容編號 | 分類 | 證據 | 一句理由』」——判定的最小單位是內容編號,不是「某一次出現」。這代表:若同一篇筆記裡,某一行落在 `decisions` 的 `why_chosen`(敘事脈絡,例如逐字複製了摘要裡的一句話,YAML 區塊純量常見這種重複)恰好與 `summary` 裡一行沒帶 `[來源:]` 的 `FACT:` 摘要行(去頭尾空白後)逐字相同,兩者會共用同一個內容編號,判定者只能給出一個判定。若判定者(合理地)因為 `decisions` 脈絡的上下文把它判成「脈絡」,`record` 就會把這個內容編號記成通過——而 `check` 的涵蓋判斷只看內容編號在不在被涵蓋清單裡(S9:「每一行都被涵蓋才放行」),並不區分這行原本落在哪個區塊,於是 `summary` 裡那個本來該被擋下的 `FACT:` 行,會因為與別處巧合撞成同一個編號而搭便車過關。這不是理論上的極端輸入——`FACT:` 摘要行的措辭本來就常被直接搬進同一節點的決策敘事裡,是本專案自己的紀律範本鼓勵的寫法(先寫摘要再展開決策脈絡)。

## F4 本篇的 `lands_in` 指到一個明文宣告「不管」這篇內容的節點

severity: major
blocking: 是 —— 落點與現有節點責任邊界互相矛盾,影響「每支檔有家」規範下之後寫回脈絡該落在哪一篇的判斷。

r3-work.md frontmatter:

引句:「Systems/筆記內容閘」

查證:該節點自己的 `responsibility` 欄位明文排除本計劃要做的東西:

file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:6`
```
responsibility: 管筆記內容的機械擋:提交前與推送前擋新寫的程式行號引用、沒寫來源的現況描述(note-shape),以及它借用的範圍與行判定;不管程式檔歸屬(那是每支檔有家)、不管推送前 AI 審查員(第二層計劃)
```
同節點的正文也重複一次同樣的排除範圍(「這篇管...note-shape 子指令...另外管三處呼叫它的地方...」,完全沒提 note-audit),`about_code` 只列 `scripts/lumos`、`scripts/hooks/pre-commit`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml` 四支檔案的「note-shape 那一段」,沒有把 note-audit 相關新函式涵蓋進去的說明。本計劃的 8 個做法小節與 12 條條款都沒有提到要新開一個 Systems 節點,或修改 `筆記內容閘` 的 `responsibility`/`about_code` 來收留 note-audit——`lands_in` 指向一篇明確表態「這不是我的事」的節點,執行到「同一次工作內寫回」那一步時無處可落。

## F5 判定者實驗段引用的 Issue 節點在圖譜裡查無此篇

severity: minor
blocking: 否 —— 不影響機制本身能否運作,只是佐證論點的出處斷link,不需要重寫任何做法。

引句:「抽樣約三分之一是真的,見 Issue〈擋什麼的初步實測〉」

查證:`find docs/lumos-toolchain-knowledge -iname "*擋什麼*" -o -iname "*初步實測*"` 在凍結副本對照的程式碼 repo 裡零命中,`Issues/` 目錄下沒有任何同名或近似檔名的節點。這句話是用來支撐「句型比對抓不住這件事,才需要判定者」這個論證的關鍵實證數字(25,282 行抽樣、約三分之一為真),出處目前是斷的,無從覆核。

# 實務隱患鏡頭

- 守衛面(誤擋習慣繞過):spec 已有申訴、skip、專案開關三個逃生門,且都寫帳、doctor 持續印,設計合理。★但★見 F3:內容編號碰撞可能讓真正該擋的行被誤放行,這是一種「靜默逃逸」而非「誤擋」,spec 沒有為這個方向設計偵測(RETIRE-IF ② 的每月抽樣理論上抓得到,但要等一個月)。
- 對外送出:限定同一家供應商、不派外家席,合理;沒有新增疑慮。
- 資源併發:清單檔原子寫入(`_write_lf`)有實作佐證;治理帳不加鎖但援引既有讀端「壞行略過」慣例(`_codeloop_read_from_ledger` 的 `except Exception: continue`),方向正確,無新增finding。
- 可用性:模型限流走 skip,合理;但 F1 若真的照描述實作,不會出現任何「擋不住」的可觀測訊號(rc0 一路綠燈),導致「可用性故障」與「機制正常但無事可擋」在操作者眼中完全無法區分——這放大了 F1 的實際嚴重度,不是獨立隱患。
- 治理帳膨脹:量級估算(25,282 行、約 300 KB)重算吻合,無 finding。
- 逆向遊戲化(spec 未列的一類):判定單位是「整行去頭尾空白後的文字」,作者若刻意把一句程式碼推得出的話拆成幾個語氣委婉、單獨看像脈絡的片語分行寫,或刻意讓它跟別處一句已判脈絡的文字撞成同一個內容編號(見 F3),可以繞過判定而不觸發現有的申訴/skip 留痕機制,因為从表面上看是「判定者自己判過」而非「跳過審查」。spec 沒有把這類行為列進 RETIRE-IF 的觀察對象(RETIRE-IF ② 的「抽樣仍有一成以上程式碼推得出」勉強可以間接抓到,但抓不到「因撞編號而搭便車」這個特定成因)。
- 不可逆/金流:spec 自己排除,查核後同意——擋在推送前,提交都在本機;沒有金流或付款操作。

# 總結

最嚴重 severity:blocker(F1)。
blocking 條數:4(F1 blocker、F2/F3/F4 major)。non-blocking:1(F5 minor)。
