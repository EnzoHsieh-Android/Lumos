severity: major

# 鏡頭:整合與知識同步(接手-sonnet)

## F1 `_lens_py_defs` 擴寫方向不明,可能靜默污染既有「既有相依」提示功能
severity: major
blocking: 是 — spec 沒說清楚是改既有共用函式還是另開新函式,實作者若選了前者,會讓一個已上線、跟本計劃無關的審查提示功能悄悄變糊,而且沒有任何回歸測試會發現
引句:「那支只抽頂層 def/class,要擴寫成也抽類別內方法與模組層大寫常數」
1. `scripts/lumos:29399` 的 `_lens_py_defs(text)` 目前只回傳頂層 def/class 的 `[(name, start, end)]`,docstring 明寫「base 版 python 原文→頂層 def/class」。
2. 這支函式現有至少一個既有消費者:`_lens_fallback` 的「呼叫者格」(`scripts/lumos:29517-29561`),在 `scripts/lumos:29526` 呼叫 `defs = _lens_py_defs(sh.stdout)`,`scripts/lumos:29532` 用 `for name, s, e in defs:` 把每個 def/class 名字當「候選識別字」去全碼庫搜「呼叫者」,產出設計審/代碼審會談看到的「既有相依」提示面板。
3. Spec 的 PRIOR-ART 句「借…的 ast 解析技法…不自刻正則」讀起來像只借技法、另開函式;但緊接著「那支只抽頂層…要擴寫成也抽類別內方法與模組層大寫常數」的主詞仍是「那支」(`_lens_py_defs`),可以讀成要在原地擴寫這支函式本身。
4. 若實作者選了「原地擴寫」:回傳清單裡混進模組層常數與類別方法,`_lens_fallback` 的呼叫者格不會報錯(仍是三元組解構得開),但會把常數當成可呼叫識別字去搜「誰引用了它」,把單純的變數引用誤標成「呼叫者」,汙染既有審查會談看到的「既有相依」提示——這是對一個跟存量漂移防線無關的既有功能的行為回歸,而〈做法〉與 S10 的測試 `t_drift_changed_things_extraction` 只釘新功能自己的抽取行為,沒有一條釘 `_lens_fallback` 呼叫者格沒被動到。
5. 做法應明講:是另開一支新函式(建議),還是要改 `_lens_py_defs` 本體——若改本體,S10 條款或測試清單要補一條回歸釘子鎖住 `_lens_fallback` 呼叫者格的既有行為(只認 def/class,不含常數)。

## F2 「筆記點名的程式符號已經不存在」(做法4.2/S13)跟既有 Check Y 高度重疊,卻沒沿用它已實測調校過的過濾機制
severity: major
blocking: 是 — 不重用會讓新掃描重新踩進 Check Y 已經用真實資料修過的同一種假陽性,而且 doctor 會同時印兩段互不參照的懸空符號清單,使用者不知道該信哪個
引句:「筆記行內反引號裡、形狀像程式符號的名稱」
1. `scripts/lumos:2608-2669`(Check Y,`section("Y", "筆記點名的方法或類別,程式碼裡找不找得到…")`)已經在 doctor 裡做幾乎一模一樣的事,而且有兩條經實測校準過的濾網:
   - 只掃 `type == "system"` 的節點(`scripts/lumos:2652-2654`)——docstring 自述「全型別掃 → 37 命中(多為計劃中的未來方法/已移除的歷史方法);限 Systems → 1 命中且為真陽性」(`scripts/lumos:2650-2651`)。
   - 逐行套 `NEG_LEXICONS["zh"]`(`scripts/lumos:3952-3956`,含「已移除/查無/已改名/棄用/廢棄/停用/deprecated/removed」等 20+ 詞)做否定語境豁免,註解明寫「這是最大宗誤報,且 2026-08-12 訂正圖譜時我們自己就寫了好幾條這種句子」(`scripts/lumos:2659-2662`)。
2. 存量漂移防線_計劃的做法 4.2 與條款 S13 都沒有提到 Check Y、沒有沿用「只掃 Systems」或 `NEG_LEXICONS` 這兩條濾網。它自己的豁免機制只有〈做法〉第 0 節「撤除過的節」——限定「小標題底下**第一個非空行**是含 5 個指定詞的引用區塊」(不是有含詞就通,不限段首的一般散文句不算)——比 Check Y 逐行掃否定詞窄得多。
3. 具體會壞的場景:一篇 Verification 節點正文寫「`RefundPointsAsync` 已移除,改走…」,不在引用區塊裡(不是 `> ` 開頭)——Check Y 因為該行含「已移除」而豁免;新的 drift scan 4.2 因為這行不落在「撤除過的節」形狀裡,而且 4.2 沒有排除 Verification 型別,會把它列成懸空符號。
4. 全篇 spec 沒有任何一處提到 `Check Y`、`check-y-symbol-existence` 或 `NEG_LEXICONS`,〈做法〉0 節的撤除節機制也沒有註明「跟 Check Y 的否定詞判斷不是同一套」。使用者/doctor 讀者拿到兩段各自報告的懸空符號清單(Check Y 的「Y」段跟新的「Z」段),沒有互相參照或去重規則。

## F3 消費專案更新後,新推送閘的預設模式只用 rtb 一個 Python 專案的考卷校準,卻對所有語言棧一體適用達兩個月
severity: major
blocking: 是 — 會讓非 Python 消費專案在完全沒被量過誤報率的情況下,一更新就吃到跟 rtb 同一個全域預設(多半是 block),推送可能被沒寫過的舊句擋下
引句:「REVISIT 那天看 pos-ios、taroko_app 等專案的擋下事件。」
1. 消費專案不是即時拉最新程式碼:根據 `ONBOARDING.md:104`「在該專案跑 `lumos update`——自動拉最新、重新複製進專案、同步 CLAUDE.md」,以及 `scripts/lumos:17157-17197` 的 `_vendor_toolchain`(`copy2` 覆寫 `_VENDORED_TOOLKIT`/`_VENDORED_TREE_FILES` 清單裡的檔,`scripts/hooks/pre-push` 在清單內)——所以這是專案主動跑 `lumos update` 才會拿到新掛鉤,不是自動推播,這點沒有「突襲」風險。
2. 但一旦專案跑了 `lumos update` 並提交、推送這個更新,`drift check` 立刻用工具鏈這邊寫死的預設模式生效(未設定時照既有三態閘慣例是 block——`note_shape`(`scripts/lumos:23508`)、`note_audit`(`scripts/lumos:24215`)、`lint_new`(`scripts/lumos:21028` `"mode": "block"`)三個既有閘全部驗證過這個「未設定=block」慣例),而消費專案的 `.lumos/config.json` 不會自動被加上 `drift_check.gate`。
3. 這條預設值(做法 6.4:「「要處理」層在考題提交上的平均筆數超過 20 就先 warn」)只用 `governance/eval/drift-exam/rtb-2026-09-28.json` 這一份、33 題、全部來自 rtb(Python 專案)的考卷去算。而 spec 自己的〈實務隱患〉已經承認:「其他語言的抽法粗…非 Python 專案的「要處理」層照樣擋,考試只考了 Python(rtb),其他棧的誤報沒量」。
4. 也就是說:同一個全域門檻(block 或 warn)一旦定案,會套用到所有消費專案,不分語言棧——包含 pos-ios(Swift)、taroko_app 等從沒被量過的專案。跟 note-shape/note-audit/lint-new 三個既有閘不同的是,那三個閘的觸發面是「這次推送**新寫的**筆記行/告警」,作者主動寫壞才會踩到;drift-check 的觸發面是「既有筆記內容跟這次**程式改動**衝突」,任何一次正常改名、刪參數都可能誤觸,風險面更廣、更被動。
5. 唯一的補救排程是 REVISIT:2026-11-28(spec 開頭:「REVISIT:2026-11-28 跑上面三個量;順便看 drift-check 閘的擋下與表態事件分布」),意味著在此之前這些從沒被量過誤報率的專案已經暴露在同一個全域預設下最多兩個月。做法沒有提出「非 Python 專案先強制 warn,量出數字才跟 Python 走同一個判定」這類分棧預設,也沒有在 6.4 的接線步驟裡要求先對其他語言棧補跑一次小規模考試再決定全域預設。

## 其餘檢查項:已讀,無 finding

- **delguard d0 決策關係**:已讀 `docs/lumos-toolchain-knowledge/Projects/code側刪除傳播守衛_計劃.md` 的 d0/d1 決策(2026-08-10,delguard 提交時維持 advisory、理由是誤報率未知)。存量漂移防線的丙(推送閘)明講「本計劃的丙不翻那條決策(delguard 在提交時照舊只提醒),另開一道推送閘,而且比 delguard 窄三處」——三處收窄(只收整支檔消失的名稱、只看這次推送帶進來的、只有家筆記與摘要行擋)加上「「要處理」層在考題提交上的平均筆數超過 20 就先 warn」的門檻機制,是在推送層(而非 commit 層)另立一道範圍更窄的閘,沒有把 delguard 本身從 advisory 升級成 block,也沒有更動 d0/d1 決策文字本身。判定:不衝突。
- **筆記內容審(第二層)分工**:範圍〈不做〉③明講「新寫的否定句(「目前沒有 X」)要不要擋——那是筆記內容審的事(判定者派工詞規則第 3 條…),本計劃不重做」,邊界清楚、沒有重疊到筆記內容審現有的判定者派工職責。判定:不衝突。
- **doctor 既有 S5/T 的重疊**:做法第 4 節第 1 點明講「計劃條款那種 doctor S5 已經在唸的照舊,這裡不重複列」,範圍收斂到「不限計劃條款」的其餘 `[test:]` 標記,分工清楚。Check T(`scripts/lumos:1317`,★INVARIANT★→測試綁定)驗的是合約標記綁定,跟本計劃無關,spec 也沒有聲稱借用或修改它。判定:不衝突。
- **doctor 既有 E5(REVISIT 到期檢查)**:`scripts/lumos:1944-1991` 的 Check E5 用 `_restv.partition(" ")` 取第一段當日期字串、`date.fromisoformat` 解析失敗即計入 `_rv_bad`(壞損格式)。Spec 的 S9/做法 2.2 要求「doctor 既有的 REVISIT 日期檢查改一處:第一格是 `[when:` 開頭的行跳過,不算「日期格式壞損」」——因為 partition 邏輯只取第一個空白前的字串當判準,`[when:file src/x.py] …` 這種行 partition 出來的第一段會是 `[when:file`,仍然以 `[when:` 開頭,所以「開頭是否為 `[when:`」這個防呆條件不受條件值內部含空白影響,改法可行、不會因為條件式內容帶空白而誤判。判定:可行,不衝突。
- **lands_in(Systems/存量漂移守衛、Systems/筆記內容閘)與「每支檔有家」規則相容性**:`scripts/lumos` 本身已經有 31 篇 Systems 節點同時把它列進 `about_code`(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md`:「本工具鏈主程式有 31 篇,2026-09-12 機械數」),包含 `Systems/筆記內容閘.md`(`about_code` 已列 `scripts/lumos`、`scripts/hooks/pre-commit`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`,2026-09-27 建立)與 `Systems/節點範圍與索引守衛.md`(`about_code: scripts/lumos`)。「每支檔有家」規則本身承認這個天花板:「散文講另一支也有家的檔、家很多的檔…都驗不出來——落點靠規則五(計劃 lands_in、設計審看)」,這正是存量漂移防線_計劃用 `lands_in` 欄位指定落點的做法。判定:相容,是既有慣例的正常延伸,不是新違規。

最嚴重等級為 major,blocking 共 3 條(F1/F2/F3)。
