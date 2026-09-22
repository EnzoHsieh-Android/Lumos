severity: blocker

## F1 新語法的 `[guard:...]` 標籤跟既有可逆性軸的 `[guard:decisions]` 撞名,語意完全不同

severity: blocker
blocking: yes

引句:「KEY:★INVARIANT-PLANNED★ <一句話合約> [guard:Verification/<守衛節點>] [due:YYYY-MM-DD]」

觀察到什麼:第二版把預告合約的語法釘死成 `KEY:★INVARIANT-PLANNED★ … [guard:Verification/<守衛節點>] [due:YYYY-MM-DD]`,用 `[guard:…]` 這個方括號標籤指向守衛節點的路徑。但 `[guard:…]` 這個標籤名稱在同一支程式裡**早就存在,而且語意完全不同**:`scripts/lumos:4120` 的 `GUARD_REF_RE = re.compile(r"\[guard:\s*([^\]]+)\]")  # 可逆性軸,平行於 ROLLBACK_REF_RE`,配上 `scripts/lumos:4228` 的 `_guard_resolved(note, ref)`——它的合法值**只認字面值 `"decisions"`**(`ref.strip().lower() != "decisions"` 直接判不成立),意思是「去這篇節點的 `decisions[]` 裡找一條非空的 `guard` 欄位」,用來補 ★IRREVERSIBLE★/★CHECKPOINT★ 的回退證據。這個既有用法連 doctor 的錯誤訊息都在教使用者寫(`scripts/lumos:14243`:「退不了的外部動作…改用 [guard:decisions] 寫怎麼防重複」)。

實測驗證(不是猜):`GUARD_REF_RE.search()` 對 `KEY:★INVARIANT-PLANNED★ 之後要有的合約 [guard:Verification/未來守衛節點] [due:2026-10-01]` 這一行直接抓到 `Verification/未來守衛節點`——這個正則不看行首標記是什麼,誰呼叫它就套用在誰身上;目前沒撞上是因為 `extract_reversibility`(`scripts/lumos:4205` 附近)只對 `CHECKPOINT_RE`/`IRREVERSIBLE_RE` 匹配到的行才呼叫它,★INVARIANT-PLANNED★ 行不匹配那兩個正則,才躲過去。

會怎麼出事:第二版要新增「轉正指令」把預告行的 `[guard:Verification/<守衛節點>]` 解析出來、找到對應的守衛節點——這正是 `GUARD_REF_RE`/`reversibility_guard_ref()` 現成能做的事,而且函式名稱「guard_ref」在語感上跟新功能完全對得上,一個不知道這段既有語意的實作者(或下一個 session 的 AI)很自然會直接重用它,或至少沿用同一個標籤名字寫一支新的解析函式。兩種走法都會撞上既有的 `_guard_resolved` 只認 `decisions` 字面值的假設——要嘛新功能因為誤用舊函式而悄悄解析失敗(`_guard_resolved` 對非 `"decisions"` 的值一律回 False,不會報錯,只會讓 ★IRREVERSIBLE★ 行「缺實質回退」的判定悄悄壞掉或悄悄過關,取決於誰共用了狀態),要嘛以後有人在 ★CHECKPOINT★/★IRREVERSIBLE★ 行上依樣畫葫蘆寫成 `[guard:Verification/foo]`(照抄新語法的印象),`_guard_resolved` 一樣判不成立,擋下的錯誤訊息卻還是舊的那句「加 [guard:decisions]」,對不上他剛剛寫的東西,除錯會繞圈。

為什麼是設計問題不是實作細節:這不是「命名要不要改得更好聽」的風格問題,而是**同一份 KEY 行方括號標籤詞彙表裡,同一個字串鍵名被指派了兩種互斥的語法(固定字面值 vs 任意節點路徑)和兩種互斥的語意(可逆性回退證據 vs 預告合約的守衛節點指標)**。第二版的「機械驗過」表格只驗了 `INVARIANT_RE.match` 與格式檢查兩項,完全沒有把新語法丟去跟既有的方括號標籤家族(`[rollback:]`/`[guard:]`/`[src:]`/`[git:]`/`[test:]`/`[audit:]`)比對是否撞名——而這正是本次審查被要求核對的「有沒有哪個既有正則會誤撈」。撞名的後果會落在整套機制最容易被複製貼上的那一行(KEY 行語法本身),波及面是全體使用者手寫或工具產生預告行時的心智模型,不是單一次實作可以局部修掉的小事。

## F2 既有的長跑上下文壓縮白名單抓不到新記號,預告合約的提醒在 loop 裡會被當成可丟的散文

severity: major
blocking: yes

引句:「機械驗過(2026-09-22,兩種候選各測一次):」

觀察到什麼:第二版只驗了兩件事——會不會被 `INVARIANT_RE` 當成正式合約抓到、會不會被既有格式檢查誤報成「合約記號放錯位置」。但圖譜裡還有一個**同樣把 ★INVARIANT★/★IRREVERSIBLE★/★CHECKPOINT★ 三個記號當一組「絕對不能壓縮掉」白名單**的既有機制,沒被列進驗證範圍:`scripts/lumos:8165` 的 `_COMPRESS_PIN_RE = re.compile(r"★INVARIANT★|★IRREVERSIBLE★|★CHECKPOINT★|停在放行點|anchor\s*驗證|anchor\s*verify|\[PIN\]", re.I)`,用在 `scripts/lumos:8171` 的 `cmd_loop_compress`(`lumos loop compress`)——這支指令是給 design-loop / code-loop 這種長跑審查對話收斂上下文用的,規則是「壓不掉白名單」/「已驗證證據」/「未結約束」三欄分類,白名單那欄的存在理由(函式註解)是「治 governance decay 殘餘面:對話中途口頭約定寫成 [PIN] 行即壓不掉」。

實測驗證:`_COMPRESS_PIN_RE.search("KEY:★INVARIANT-PLANNED★ 之後要有的合約 [guard:Verification/foo] [due:2026-10-01]")` 回傳 False——跟 F1 同一個原因(字面上沒有連續的「★INVARIANT★」子字串),這條線索**不會**被歸進「壓不掉白名單」,會落進可以被摘要掉的一般散文。

會怎麼出事:設計本身的核心賣點是「預告那一行就寫在節點裡,下一個人查節點就會看到,不必等到逾期被擋」(第二版原文第 25 行的立場)。但如果這條預告行是在一次 design-loop / code-loop 的長跑對話裡被討論、被貼出來提醒(例如審查員或協調者把這行貼進轉錄稿裡說「這條快到期了別漏」),等對話跑到需要 `lumos loop compress` 收斂上下文時,這句提醒不會被判成白名單,會被當成可丟的散文摘掉——而這正是最忙、最需要提醒不被壓縮掉的場景(逾期規則本身就寫死不准延期,代價是「會在最忙的時候擋死推送」,見第二版〈誠實界線〉)。這跟威脅模型「防忘記」的宗旨直接衝突:一個為了防止人在長對話裡忘記而特別設計的新記號,卻沒被納入既有的「防止長對話裡把重要提醒壓縮掉」機制的識別範圍。

為什麼是設計問題不是實作細節:`_COMPRESS_PIN_RE` 和 `INVARIANT_RE`/格式檢查是三個各自獨立維護的正則,分別由不同意圖驅動(合約登記簿 vs 格式檢查 vs 上下文壓縮白名單),第二版選記號時只驗了前兩個,卻沒把「這個記號要不要也算進『不能壓縮的重要標記』家族」當成一個要裁的取捨寫進設計——這是遺漏了一整類既有機制,不是某一行程式碼寫錯。

## F3 「動手前一定要看」那段的標題語意跟預告合約不符,字面上會把還沒生效的合約講成已經生效

severity: minor
blocking: no

引句:「不然寫在摘要裡也還是不顯眼。這是這個改法的重點,不是附加。」

觀察到什麼:第二版的 S15 要求「查那篇節點時應在開頭…那段一併印出它與最遲日期」,把預告合約併進 `cmd_context`(`scripts/lumos:11377`)既有那段輸出。實測目前那段的固定文字是 `"提醒:這篇有「動了會壞」的合約,動手前一定要看:"`(`scripts/lumos:11407`),下面逐行印 `★INVARIANT★ {x}` 和 `★DEBT★ {x}`。這句話斷言「動了會壞」——對已綁測試的正式 ★INVARIANT★ 成立,但對預告中的 ★INVARIANT-PLANNED★ 不成立:它連測試都還沒有,依照第二版自己的定義是「還沒生效的合約」,動它現在不會「壞」,只是以後要補。

會怎麼出事:S15 沒有指定預告合約要用不同的標題或至少不同的措辭跟正式合約分開,只說「一併印出」。如果實作照字面把預告行塞進同一段、沿用同一句「動了會壞」的斷言,讀的人(人或下一個 AI session)會把「還沒做的東西」誤判成「現在就不能碰的東西」——這正好是第二版〈威脅模型〉那節反覆強調要避免的方向(「高估一道守衛比沒有守衛更危險」),只是這次不是防繞過的層面,是討論可見度時出現的同一種風險:呈現方式比實際狀態更嚴重。

為什麼是設計問題不是實作細節:S15 的驗收條款只規定「有沒有印出來」,沒有規定「印出來時要不要跟正式合約在語意上分開」,而這正是這整個改法唯一的賣點(讓預告顯眼但不誤導)。條款寫得不夠精確,實作者照字面做最省事的合併寫法就會踩雷,屬於條款本身留的空隙,不是哪一行程式碼會不會漏寫的問題。
