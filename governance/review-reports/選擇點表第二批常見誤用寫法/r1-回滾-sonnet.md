severity: major

查證範圍:我讀完整份 spec,並逐項對 `scripts/lumos` 和 `check.py` 驗證。〈白話〉〈用詞〉〈不做〉〈依據來源〉〈預期值表〉〈天花板〉已讀,無 finding。

回滾入口總表(逐項對照程式碼):
- **有效處置的鍵**:`(檔, 行指紋)`,`_choice_ledger_index`。不含列號、壞法或 `new_sha`。
- **放行**:`choice:<檔>:<行指紋>`,`_choice_waived_keys`。不含列號。
- **帳上事件**:`choice-kill` 的 run、blocked、unverified、每個壞法那筆。壞法那筆帶 `row` 和 `new_sha`,但判定不讀它們。
- **推送前判定**:`_choice_push_judge` 與 `_choice_disposition`。只看同鍵最新一筆。
- **回報上限抽樣**:`_choice_cap_pick`,種子是曾經存活的 `(檔, 行指紋)` 集合。
- **gov --stats**:`_gov_choice_counts` 現在依原因文字和 `(列號, 外層宣告)` 計。
- **型錄表**:`check.py` 的 `choice_tables` 與 `_choice_rules_match`,表和規則 id 必須一一對上。

1. 〈回退〉第 1、2 項「舊帳照算」是錯的:換列後同一行的舊處置會套到另一個壞法上
severity: major
   blocking: 是,撤列之後推送閘會對沒跑過的壞法直接放行或擋下,屬於判定錯誤。
   - 段落:〈實務隱患〉換壞法、〈回退〉1、〈不做〉。
   - 引句:「處置鍵是 (檔, 行指紋),已記的殺掉照算,只有之後重跑時壞法可能不同」
   - 引句:「單列誤報或跑不出結果多:從〈選擇點表〉拿掉那一列(下一次推送就不再算;舊帳以行為單位照算)」
   - 問題:
     - 同一行同時有第一版語法和第二批語法時(例如 `x?.filter { … }`、`a ?: b > c`、`.let` 接 `sortedBy`),加入第二批會讓 `_choice_pick` 的挑法改變。撤掉時挑法改回去。
     - 帳上同鍵最新一筆是另一個壞法(例如 NUL 那個)的 killed、survived 或放行。
     - 撤掉後,推送前那一道把「同鍵最新一筆」當成這一行現在挑到的壞法的處置。killed 且測試仍被條款綁著就 `continue`,放行也直接略過。第一版那個壞法因此永遠沒跑過,卻被當成已處置。
     - 反方向同理:最新一筆是 survived 時,`tests_sha` 沒變就被 carried,沒跑過的壞法被當成存活要人處置。
     - 放行理由「不適用」的語意是「那個壞法不適用」(見 `_CHOICE_PUSH_FIX["跑不出結果"]`)。撤掉那一列後,這筆放行仍然永久豁免該行的其他壞法。
   - 為什麼不是少見情形:Kotlin 裡 `?.`、`?:`、`.let` 很常跟 `filter`、`any`、比較運算同行。S7 只守「不含六種語法」的行,守不到混合行。
   - 佐證:
     - file: `scripts/lumos:77718`,`_choice_disposition` 只看 `evs[-1]` 的 verdict 和 `killing_test`。
     - file: `scripts/lumos:78424`,`_choice_push_judge` 用 `key in waived` 和 `_choice_disposition(evs, False, bound)`,沒用 `row` 或 `new_sha`。
     - file: `scripts/lumos:77368`,`_choice_pick` 依行內有哪些類別洗牌。行內類別一變,挑出的壞法就換。
   - 影響:加入和撤掉都有這個問題。spec 只在加入方向承認「壞法可能不同」,卻在〈回退〉宣稱可以乾淨撤掉。

2. 〈回退〉第 1 項「只拿掉那一列」做不到:漏拿規則和樣本,表就整個壞掉,所有 Kotlin 推送被擋
severity: major
   blocking: 是,照字面回退會讓推送前那一道對每次 Kotlin 推送硬擋。
   - 段落:〈回退〉1、2,〈範圍〉1、2。
   - 引句:「整批撤掉:拿掉 C-32 起的列與新規則檔」
   - 問題:
     - `_choice_rules_match` 對「規則 id 在規則目錄卻在型錄沒有列」回報問題(`規則 C-3x(…)在型錄沒有對應的列`)。
     - `_choice_tables` 看到任何問題就整張表不用。`_choice_push_scan` 回 `("bad", …)`,記 blocked「表壞」。
     - 第 1 項只寫「從〈選擇點表〉拿掉那一列」。實際上同時要:
       - 把規則從 `nul.yml`、`compose.yml` 這類一個檔放兩條規則的檔裡刪掉。
       - 把 `api.yml` 裡新增的 `let` 和 `combine` 規則刪掉。
       - 把樣本檔的 `// HIT C-3x` 標記刪掉。標記還在而規則沒了,`choice_sample_problems` 會報。
       - 把型錄〈統計〉的 `- 選擇點表:N 列` 改回去。check.py 會比對列數(`check.py:632`)。
       - 把〈選擇點表〉說明段「六種錨點」那句改回去。
     - 〈回退〉第 2 項「整批撤掉」也沒列這三項:樣本、統計列數、說明段。
   - 因為表是從安裝版型錄讀的(`_kt_catalog_path`),不是從被推版本讀的,半退狀態會立刻影響每一次推送。這不是只擋第二批。
   - 佐證:
     - file: `configs/ast-grep/kotlin-android/check.py:1477-1487`,`_choice_rules_match` 回報多出來的規則 id。
     - file: `scripts/lumos:76891`,`_choice_tables` 有問題就回 `None`。
     - file: `scripts/lumos:78351` 附近的 `_choice_push_scan` 對 `why` 回 `bad` 並硬擋。
   - 要補:〈回退〉寫成單列退出的完整清單,並指定一支守衛(例如型錄自檢)在漏掉任何一項時紅燈。

3. 「新錨點、NUL 類別與『依列號』統計的程式碼留著不影響第一版」沒有測試支撐,撤掉後還有兩批測試會紅
severity: major
   blocking: 是,〈回退〉第 2 項的前提不成立,而且 spec 自己宣稱的 S7 只守加入方向。
   - 段落:〈回退〉2、〈驗收條款〉S1–S8。
   - 引句:「新錨點、NUL 類別與」這一句的上下文是整批撤掉後「程式碼留著不影響第一版」。
   - 問題:
     - S1、S2、S3、S4、S6 的測試(`t_choice_points_nul_elvis`、`t_choice_points_nul_safecall`、`t_choice_points_batch2_api`、`t_choice_points_compose`、`t_choice_samples_batch2`)都靠 C-32 起的列和 `nul.yml`、`compose.yml`。
     - 這些測試若讀真型錄,整批撤掉後全紅。若用 fixture 型錄,則沒驗到上線資料。spec 沒說是哪一種。
     - 撤掉後留下的三個 `_choice_edits` 分支和兩個錨點,沒有任何列會走到,沒有測試保證它們不誤觸第一版的列。
     - `CHOICE_CATEGORIES` 尾端加 `NUL` 會讓 `choice_tables` 的 `categories` 多一項。留在表裡時,「第一版五類加 API 的相對順序不動」只靠 S7 守。
     - S7 的比較是「加入前後」,沒有「加入再撤掉後」的對照。
   - 佐證:file: `scripts/lumos:77368`,`cats` 是 `categories` 過濾後洗牌,所以尾端多一個空類別不影響。這個我驗過,是撤掉後安全的少數部分。但上述測試與樣本缺口仍在。

4. 撤列或整批撤掉後,回報上限抽樣會重洗,無關的第一版存活行也會被放過或擋下
severity: minor
   blocking: 否,影響限於抽樣邊界,方向是多擋或少擋同一批已知存活行,有人工放行出口。
   - 段落:〈不做〉「不改…回報上限」、〈回退〉1。
   - 引句:「不改一行一個壞法、回報上限、乾節點、殺傷力判定與推送前那一道的規則」
   - 問題:
     - `_choice_cap_pick` 的種子是 `ever`(曾經存活的 `(檔, 行指紋)` 集合)。`ever` 只收這次範圍 `res["lines"]` 裡還有壞法的行。
     - 撤掉一列後,那些行不再有壞法,`ever` 變小,種子改變,同一批第一版存活行被抽中的子集整個重洗。
     - 這跟「放行一行不會讓抽中的那批重洗」(`_choice_push_judge` docstring)是同一個設計目標,撤列卻會破壞它。
   - 佐證:file: `scripts/lumos:78410` 與 `scripts/lumos:78424`。

5. 列號 C-32… 沒有防重用機制,撤掉後再加回會把舊帳算到新列
severity: minor
   blocking: 否,目前只有一個人依序操作,而且重用要人為造成,但 spec 沒寫一句「撤掉的列號不重用」。
   - 段落:〈範圍〉1「列號接 C-32 起」、〈回退〉1。
   - 引句:「列號接 C-32 起」
   - 問題:
     - `check.py` 只檢查表內「列號重複」,不看歷史。
     - 撤掉最後一列(例如 C-37)後,下一個新增列自然拿 C-37。帳上舊的 `row: C-37` 事件就算進新列。
     - S8 的「依列號」統計靠 `row`,RETIRE-IF 的八成、一半門檻跟著失真。
   - 要補:型錄明寫「撤掉的列號保留不再發」,或統計把 `catalog` 雜湊(事件已帶,`scripts/lumos:77888`)併入分組。

6. 「依列號」的放行理由歸列與存活事件對不上,RETIRE-IF 的分母分子無法按列相接
severity: minor
   blocking: 否,影響的是撤除條件能不能算準,不影響閘本身。
   - 段落:〈範圍〉5、S8、RETIRE-IF。
   - 引句:「第二批與第一版每一列各自的壞法數、殺掉數、存活數、跑不出結果數,以及被回報存活後的放行理由分布」
   - 問題:
     - 放行事件的 `row` 取自放行當下 `_choice_waive_target` 的 `x["mutant"]["row"]`(`scripts/lumos:78641` 起),是目前挑到的壞法的列。
     - 存活事件的 `row` 是當時跑的那個壞法的列。型錄改過或混合行換挑法後,兩者可以不同。
     - 所以「某一列被回報存活之後的放行」在帳上沒有可 join 的鍵,除非另外用 `(檔, 行指紋)` 對接。
     - gov 現有的放行去重鍵是 `file:fp`(`scripts/lumos:18416`)。spec 沒說新統計怎麼對。
     - 同一個壞法重跑多次會在帳上累積多筆,S8 的「壞法數」是算事件還是算 `(檔, 行指紋, new_sha)` 沒定義。
   - 要補:規定用 `(檔, 行指紋)` 或 `new_sha` 去重並接放行,再寫進 S8 預期值。

7. 實務隱患鏡頭(風險類逐類)
severity: minor
   blocking: 否,以下是對〈實務隱患〉缺漏的補充,見前面各條。
   - 帳與處置的版本相容:有隱患,見 1、4、5。spec 的〈不可逆〉寫「拿掉第二批列即回到第一版行為」,與 1 矛盾。
     - 引句:「不可逆:治理帳照舊逐筆追加,拿掉第二批列即回到第一版行為」
   - 放行紀錄殘留:有隱患,見 1。AI 放行會一直被 doctor 列出直到有人 ack,撤列後這些放行對應的壞法已不存在,卻不會自動失效。
   - 表壞連動:有隱患,見 2。半退會讓所有 Kotlin 推送被擋。
   - 計劃端殘留:`situation-rule --point`(「寫回規格」路徑)寫進計劃的條款和綁定測試,撤列後仍在,仍被 `_choice_bound_names` 算作綁著。〈回退〉沒提。
   - 併發:已排除,沿用第一版,單人依序。
   - 金流、對外送出:無,spec 只動型錄、規則與本機產壞法,查證過 `scripts/lumos` 的選擇點段不對外呼叫。

最嚴重 severity:major,blocking 共 3 條(第 1、2、3 條)。
