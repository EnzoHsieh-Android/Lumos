severity: blocker

〈frontmatter / 白話 / 依據 / PRIOR-ART / RETIRE-IF / REVISIT〉已讀,無 finding。

〈判定者能不能用:小實驗〉已讀,無 finding。

## F1 「預設分支的分岔點」用哪支既有函式沒講,推導失敗時會退回會重演 57,474 行那個問題

severity: blocker
blocking: 是 —— 不改,消費專案只要預設分支不叫 main/master,新分支每次推送都會把整庫舊筆記當新增,S3 想修的問題原封不動重演,而且擋的是每一次推送

引句:「連分岔點都找不到(孤兒分支)才整支算,並印一句原因」

引句:「起點應為與預設分支的分岔點;找不到分岔點時才整支算並印原因」

1. spec 從頭到尾沒講「預設分支」怎麼取得——沒有指名沿用哪支既有函式,也沒有定義它是「GitHub/GitLab 設定的 default branch」還是「本地 main/master」。
2. 查證:repo 裡唯一算「主線 tip」的既有函式是 `_mainline_ref`,file: `scripts/lumos:27443`,內容只認四個候選:`"main@{upstream}", "master@{upstream}", "main", "master"`,認不到就回 `None`——沒有任何機制去問 git 的 `origin/HEAD`(真正的「預設分支」)或讀 GitHub API。這支函式目前只有 `_bound_tests_range`(file: `scripts/lumos:29168-29198`)在用,且那支函式在 `_mainline_ref` 回 `None` 時的處置是「算不出來」而非往下硬猜。
3. `git grep` 全 repo 找不到任何 `symbol-ref`/`origin/HEAD`/「default branch」等更通用的判定(已用 Bash 查證,`grep -n "symbolic-ref\|default.branch\|預設分支\|origin/HEAD"` 只命中兩處與本案無關的「lumos 自己發版分支」邏輯,不是通用主線判定)。
4. 本計劃明講這支機制是要靠 `lumos update` 推給其他消費專案的(見〈規範文字跟著改〉「各專案各自跑 `lumos update` 拉新版」),而這個工具鏈本身就服務多種棧(java/kotlin/python/node/…的 idioms skill 佐證多消費專案存在)。只要有一個消費專案的預設分支不叫 main 或 master(業界常見:`develop`、`trunk`、公司內規改名),`_mainline_ref` 就回 `None`。
5. 若實作沿用 `_mainline_ref`(spec 沒說不要,也沒說替代方案),S3 的「連分岔點都找不到(孤兒分支)才整支算」這句話會把「主線判準本身就抓不到」誤判成「孤兒分支」,兩者被同一套語言蓋住——結果是任何預設分支不叫 main/master 的專案,每次推新分支都會落入「整支算」,把整庫舊筆記當成這次新增,重演 spec 自己引的 r1 事故(整庫 57,474 行)。這不是邊角案例,是「這支機制在非 main 專案上第一天就會炸」的系統性缺口。

## F2 分岔點算不出時,`decision-amend` 的「範圍起點不存在」判準會失守,讓已推上遠端的決策也能被改

severity: blocker
blocking: 是 —— 不改,F1 的「整支算」一觸發,decision-amend 對「已推上遠端」的保護就整個失效,任何歷史決策都能被静默改寫而不留翻案紀錄

引句:「只准改還沒推上遠端的決策——範圍起點不存在那個編號」

引句:「應只准改範圍起點不存在的決策編號,已推上遠端的應拒絕並指向翻案指令」

1. `decision-amend` 判斷一個決策編號能不能改,依據是「範圍起點不存在那個編號」——這個「範圍起點」用的正是〈共用〉段定義的同一套範圍推導(含 F1 的分岔點邏輯)。
2. 當 F1 的情況發生(預設分支判不到、或本來就是孤兒分支)時,spec 自己講的處置是「才整支算」——也就是把範圍起點退到「空樹」(repo 從無到有那個狀態)。
3. 空樹狀態下「不存在」的決策編號 = 全部決策編號,因為空樹本身什麼檔都沒有。於是「範圍起點不存在那個編號」這條判準,在整支算模式下對**任何一條歷史決策**都成立(包括三個月前就推上 main、已經被別人讀過、引用過的決策)。
4. 結果:decision-amend 原本要保護的「已推上遠端的決策只能翻案,不能改」這條線,在整支算模式下完全失守——任何人都能用 decision-amend 直接改寫早已公開的決策內容,而不會被引導去走「翻案指令」,也不會留下翻案該有的稽核痕跡(翻案通常會留 `superseded_by`/`valid: false` 這類機械可查的軌跡,直接改是覆蓋)。
5. 這正是題目提示裡點名的「decision-amend」legal 手段——搭配 F1 的觸發條件,兩層防護(分岔點判斷 + 已推遠端保護)一起被同一個輸入打穿。

## F3 record 的機械驗證只驗「search 的路徑存在」,不驗字串真的命中;且成立的申訴會讓未編輯的一半一半行整行免改

severity: major
blocking: 是 —— 不改,審查員只要寫一個存在但不相關的路徑當 search 證據就能讓推得出的判定通過機械驗證;而作者只要拿到任何一次「較輕」的申訴,就能讓原本判一半一半的整行原封不動留在筆記裡

引句:「由工具自己用字串比對跑一次(不開 shell),確認路徑存在」

引句:「證據的檔不存在、行號超出檔長、search 的路徑不存在應拒絕」

引句:「判推得出或一半一半的行已不在集合裡,除非有成立的申訴」

引句:「推得出的整行刪;一半一半刪掉推得出的子句」

1. 〈做法〉第二層第 4 點與條款 [S7] 兩處都把 `search:` 這種證據的機械驗證,寫成「確認路徑存在」——字面上只驗「search 指到的那個檔案路徑是不是真的存在於 repo」,沒有一處要求工具真的把 `search: <字串> in <路徑>` 的那個字串,在該路徑裡跑一次比對確認命中(儘管前半句寫「由工具自己用字串比對跑一次」,但緊接著講的驗證結果只是「確認路徑存在」,兩句話對不上——如果真的跑了字串比對,理應驗的是「有沒有命中」而不是「路徑存不存在」)。
2. 這是專門為「沒有 X」「只有 N 種」這類負向存在宣稱設計的證據形式(見〈做法〉第二層第 2 點④句),恰恰是最難驗證、最容易被審查員或作者用一個文字上看起來合理、實際上不相關的字串矇混過去的那一類——而機械驗證只檢查路徑存在與否,等於這類最需要把關的證據完全沒有實質查核。
3. 條款 [S7] 又進一步用測試名稱把這個弱點釘死:`search 的路徑不存在應拒絕`,沒有並列「search 字串在該路徑找不到也應拒絕」這一句,代表這不是文字疏漏,是設計者自己没把「字串真的命中」寫進判準裡。
4. record 的第②項判準「判推得出或一半一半的行已不在集合裡,除非有成立的申訴」,沒有區分「申訴把推得出降成脈絡」和「申訴把推得出降成一半一半」兩種情況——按〈做法〉第二層第 3 點,一半一半的行本來就該由作者刪掉推得出的子句才算處理完,但只要申訴成立(哪怕只是降到一半一半這種還帶著程式碼推得出成分的判定),record 的機械檢查就直接放行整行不變的內容,不會要求作者真的把那個子句刪掉。
5. 對照 r1→r2 的實際變動:r1 的申訴規則要求「第二席也判脈絡才算申訴成立」(全降到脈絡才算數);r2 改成「較輕就採用」,把「推得出→一半一半」也算申訴成立——但 record 端的機械檢查沒有跟著細分,兩處銜接處出現新的不一致:規則放寬了(接受部分降級),機械把關卻沒跟上(部分降級後仍要求刪子句這件事沒有被強制檢查)。
6. 綜合 1–5:一個作者只要能讓任何一行「推得出」的判定,經由申訴拿到「一半一半」這個較輕結果(而不需要真的被判成脈絡),就能讓那一行完全不改地通過 record,而且不需要造假 search 證據——這是題目提示裡「申訴」這個合法手段被用成空殼審查的具體路徑。

## F4 `.lumos/config.json` 的 `note_audit: off` 是靜默的專案級關閉開關,沒有任何機制持續曝光,也不計入本計劃自己的三個 RETIRE-IF 量

severity: blocker
blocking: 是 —— 不改,任何一次提交就能把整個第二層永久關掉,而且這個關閉狀態不會被 doctor、RETIRE-IF 或任何既有機制持續看見

引句:「block(預設)/ report / off;環境變數」

引句:「skip 與跳過次數進 RETIRE-IF 的量」

引句:「設 off 時 check 應放行並說一句,report 時應只印不擋」

1. 出口段列了三種正當跳過方式:`note-audit skip`(要寫理由、綁指紋、寫進治理帳)、`LUMOS_SKIP_NOTE_AUDIT=1`(單次跳過、寫帳)、以及 `.lumos/config.json` 的 `note_audit` 專案開關(block/report/off)。
2. 緊接著那句「skip 與跳過次數進 RETIRE-IF 的量」只點名了前兩種(skip 與環境變數跳過),完全沒提到「有多少專案/多少次推送是靠把 `note_audit` 設成 off 或 report 繞過的」——這代表 RETIRE-IF 的三個回頭條件(申訴率、抽樣仍程式碼推得出比例、CONTEXT 行月量)全部只看「還在跑第二層」的那些專案/推送,對「已經整批關掉」的完全是盲區。一個專案把 `note_audit` 設成 off 之後,不會再產生任何申訴、任何抽樣母體、任何 CONTEXT 行紀錄——這條路徑本身就會讓自己在回頭量測裡「消失」,而不是被算進「擋掉的比救下的多」那個警訊裡。
3. 條款 [S11] 把「off 時 check 應放行並說一句」寫成測試判準,但那句話只在**推送當下**印給正在推的那個人看(而且很可能被 CI log 淹沒),不是持久性、可被定期巡檢看到的訊號。
4. 對照本 repo 已有的同類先例:`node_home.gate`(每支檔有家)在設成 off/warn 時,`lumos doctor` 每次跑都會主動印出提醒——`這個專案把「每支檔有家」的擋設成 {mode}(.lumos/config.json 的 node_home.gate)`(file: `scripts/lumos:999`,另見 `scripts/lumos:22228`)。這是本 repo 自己確立的慣例:凡是有專案級開關能弱化某道閘,`doctor` 就要把這件事持續攤在眼前,不能只在觸發那一刻講一句就過去。note-audit 的設計完全沒有比照這個既有慣例,`doctor` 段的 spec 內容裡也沒有一句提到要在 doctor 輸出裡體現 `note_audit` 的模式。
5. 這正是題目提示點名的「專案開關」——任何一個對 `.lumos/config.json` 有提交權限的人,寫一行 JSON、一個提交,就能讓第二層永久停擺,不需要理由、不留治理帳、不會被本計劃自己設計的回頭機制發現,也不會被既有的 doctor 巡檢揪出來(除非另外照 node_home.gate 那樣補一行提醒,但 spec 沒寫)。

## F5 「decisions 文字欄」列的欄位名跟本 repo 實際慣例對不上,主流寫法會被排除在兩層審查之外

severity: major
blocking: 是 —— 不改,實作者照字面比對「alternatives」這個鍵名,會漏掉本 repo 裡 14 篇實際用的 `alternatives_considered`,那正是最容易夾帶程式現況描述的長文推理欄位

引句:「decisions 每條的文字欄(content / context / why_chosen / alternatives / trade_offs)」

1. 查證:`parse_decisions`(file: `scripts/lumos:12904`)是逐鍵掃描的通用解析器,不限定固定欄位名,所以 decisions 底下能出現任意手寫的鍵——但這代表「哪些鍵算數」完全要靠 spec 自己明確列名,列漏的鍵不會被工具自動含括進去。
2. 本 repo 實際筆記(已用 Bash 查證 `grep -rl alternatives_considered docs/lumos-toolchain-knowledge/`)裡有 14 個檔案使用 `alternatives_considered:` 這個鍵名寫「否決過什麼方案」,例如 `docs/lumos-toolchain-knowledge/Projects/Java補棧_計劃.md:35` 與 `docs/lumos-toolchain-knowledge/Projects/code側刪除傳播守衛_計劃.md:37/50`;只有 1 個檔案(`docs/lumos-toolchain-knowledge/Projects/推筆記認家_計劃.md:25`)用了 spec 字面列的 `alternatives:`(不帶 `_considered`)。`trade_offs:` 這個鍵名倒是跟 spec 一致(16 個檔案使用,已查證)。
3. `decision-add` 這支 CLI(file: `scripts/lumos:14899`)本身也沒有 `--alternatives`/`--alternatives-considered` 這種內建旗標,`alternatives_considered` 全部是手改 frontmatter 寫進去的(違反 CLAUDE.md「開頭欄位用指令改,別手改」的鐵則,但確實是這個 repo 目前的實況)——這代表這個欄位本來就沒有單一權威寫法可依賴,spec 若不明講「含 `alternatives_considered` 這個實際常見拼法」,實作者字面比對 `alternatives` 鍵名時會漏掉 14/15 的既有內容。
4. 效果:decisions 裡用來寫「為什麼否決某個方案」的長文——正是最常夾帶「這支函式什麼時候加的、程式現在怎麼運作」這類程式碼推得出內容的地方——因為欄位名對不上,完全不會被算進〈共用〉段定義的「新增行」範圍,兩層審查都碰不到它,而這條路徑不需要任何人蓄意鑽漏洞,只是照本 repo 現有寫作習慣自然發生。

〈做法 > 第一層〉已讀,無 finding(內容依賴的「每支檔有家」判定與圍欄判定都指名沿用既有實作,查證存在:`_is_code_file` file: `scripts/lumos:6181`,`_visible_lines` file: `scripts/lumos:3218`)。

〈做法 > 上線前校準〉已讀,無 finding。

〈做法 > 規範文字跟著改〉已讀,無 finding。

條款 S1、S2、S4(除 F5 指出的欄位名問題外)、S5、S6、S9、S10、S13、S14、S15 已讀,無 finding。

〈回退〉已讀,無 finding。

〈實務隱患〉已讀,無 finding。

〈誠實界線〉已讀,無 finding。

〈審計修正紀錄〉已讀,無 finding。

---
總結:最嚴重 severity 為 blocker(F1、F2、F4);blocking 共 5 條(F1、F2、F3、F4、F5)。
