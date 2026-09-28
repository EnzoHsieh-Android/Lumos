severity: major

# 架構對齊審查(存量漂移防線_計劃)

審查範圍:只判「跟既有做法一不一致」,不判 bug、不評風格。凍結快照 = `governance/review-reports/存量漂移防線/r1-snapshot.md`(路徑相對 clone-ns);程式碼引用皆對照 clone-ns 複本的 `scripts/lumos`。

## Q1 分層與依賴方向

新指令家族 `lumos drift check/scan/ack/exam` 的巢狀子指令形狀(`dr = sub.add_parser("drift", ...)` → `drsub = dr.add_subparsers(...)`)跟既有 `guard`(file: `scripts/lumos:33202-33203`,`g = sub.add_parser("guard", ...)`、`gsub = g.add_subparsers(dest="gcmd", required=True)`)、`note-audit`(`nasub`)、`dref`(`drsub` 同名但不同族,見 `scripts/lumos:33411-33413`)一致,沒有問題,已讀無 finding。

「check(推送閘,rc0/1/2)+ scan(健檢,不擋不寫帳)」這種一對二的切法,跟既有 `testmap-build` / `testmap-affected`(`scripts/lumos:26814`、`26887`)、`impact` / `impact --diff`(`scripts/lumos:28496`、`28987`)同形狀,已讀無 finding。

PRIOR-ART 段落列了六項借用(`scripts/lumos` 對照見下),其中一項是要**原地擴寫**別的子系統的共用函式,這點在依賴方向上有問題,見 F3。

## F3 原地擴寫別的功能域的私有共用函式,沒處理既有呼叫端的相容性
severity: major
blocking: 是 — 若真的原地擴寫 `_lens_py_defs` 讓它連模組層大寫常數與類別內方法都回傳,dispatch-lens 既有「格3:呼叫者」邏輯(`scripts/lumos:29526-29534`,`for name, s, e in defs: ov = sum(...)` 拿 defs 當候選定義去跟改動行範圍算重疊)會把新冒出來的常數名一併當「候選定義/呼叫者」納入審查範圍候選池,審查派工的範圍判斷會跑偏——這是會做錯決定的
引句:「要擴寫成也抽類別內方法與模組層大寫常數」
1. `_lens_py_defs`(`scripts/lumos:29399-29413`)目前只回傳頂層 `FunctionDef`/`AsyncFunctionDef`/`ClassDef` 的 `[(name, start, end)]`,唯一呼叫端是 dispatch-lens 的候選定義抽取(`scripts/lumos:29526`),用來跟 diff hunk 的行範圍算重疊、決定審查席位看到哪些候選(`scripts/lumos:29532-29534`)。
2. 這支函式屬於「審查派工範圍計算」這個功能域(dispatch-lens),不是筆記/圖譜這個功能域。
3. 計劃的借用清單(引句所在段)沒有說要另開一支函式或加參數隔離兩個消費者,寫的是直接「擴寫」既有函式的抽取範圍。
4. 類別內方法與模組層常數的行範圍性質跟頂層 def/class 不同(常數多半 `start == end` 單行賦值),混進 dispatch-lens 現有的候選池後,審查範圍候選名單、cap 截斷(`scripts/lumos:29536-29537` 的 `_LENS_CAND_CAP`)都會被稀釋,而這條路徑跟 drift 功能完全無關。
5. 建議:另開一支函式(如 `_lens_py_defs_ext`)或加 `include_methods=False`/`include_consts=False` 之類的旗標,讓 dispatch-lens 端行為維持不變;計劃目前的寫法沒有講這件事,是不是真的會共用同一份回傳值、有沒有隔離,凍結快照裡判不出來,標 ⚠。

## Q2 命名與錯誤處理

- rc 語意:「回傳碼 0 過、1 擋、2 參數錯」跟 `cmd_note_shape` 的 docstring「有新違規 rc1,沒有 rc0;參數錯 rc2」(`scripts/lumos:24081`)一致,已讀無 finding。
- 閘三態:`drift_check.gate` = block(預設)/warn/off,跟 `note_shape.gate`(`scripts/lumos:23518`,`_NOTE_SHAPE_GATE_VALUES`)、`note_audit.gate`(`scripts/lumos:24215`)同一組值、同一種「看不懂就照預設擋」寫法,已讀無 finding。
- 略過開關:「單次略過 `LUMOS_SKIP_DRIFT_CHECK=1`(只認 1,記 `skipped-env`)」跟 `LUMOS_SKIP_NOTE_SHAPE`(`scripts/lumos:24097`,「只認 1,跟 LUMOS_SKIP_BOUND_TESTS 等鄰居一致」)、`LUMOS_SKIP_NOTE_AUDIT`(`scripts/lumos:24804`)命名與語意一致,已讀無 finding。
- 治理帳事件種類:`blocked`/`warned`/`skipped-env`/`skipped`/`acked` 跟 `_note_shape_eval` 實際用到的事件字面值(`scripts/lumos:24099` skipped-env、`24123` skipped、`24148` blocked、`24157` warned)同一套詞彙,已讀無 finding。「沒發現的放行不寫帳(同筆記形狀擋)」跟 `cmd_note_shape` docstring 明講的行為(`scripts/lumos:24084-24085`)一致,已讀無 finding。
- doctor 段:選字母 `Z` 沒跟既有段落字母衝突(現有用到 `G/L/M/C/T/R/S/S2-S15/I/A1/A2/E1-E5/H/K/D/V/P/Y/N/J/W/F`,`Z` 未用,見 grep `section("` 全清單),已讀無 finding。
- 閘名登記:「閘名 `drift-check` 登記進既有閘名單」對照 `_KNOWN_GATES`(`scripts/lumos:6604-6621`)裡 `note-shape`、`note-audit`、`nodehome-check` 的命名形狀(`<主題>-<動作>` 全小寫連字號),`drift-check` 符合,已讀無 finding。
- 表態檔納入簿記豁免:`_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS`(`scripts/lumos:20344-20362`,單一源、兩個消費者的既有清單)是這類「新增只讀帳冊檔」該掛的地方,計劃寫「表態檔應在簿記豁免裡」跟這個既有做法一致,已讀無 finding。

本節整體:命名與錯誤處理跟鄰居高度一致,沒有 major/minor finding。

## Q3 第二種做法

## F1 `drift scan` 的「程式符號已不存在」偵測,跟既有 Check Y / `load_symbol_profile` / `drift-history` 是同一問題的第二套獨立機制,PRIOR-ART 未提及也未重用
severity: major
blocking: 是 — 不改的話會在同一支 `scripts/lumos` 裡養出兩套互相不知道對方存在的「筆記提到的符號還在不在程式碼裡」偵測器,且兩者都掛在字面上叫「drift」的指令下(一個是既有的 `lumos drift-history`,一個是新的 `lumos drift scan`),使用者與之後維護者無法從指令名判斷該查哪一個,是會做錯決定、也是做出壞系統的形狀
引句:「筆記點名的程式符號已經不存在」
1. `scripts/lumos:2608-2621` 既有 doctor Check Y 就是「筆記點名的方法或類別,程式碼裡找不找得到」(`section("Y", "筆記點名的方法或類別,程式碼裡找不找得到(寫錯或已改名;提醒,不擋)")`),靠 `load_symbol_profile`(`scripts/lumos:3963`)讀 `.lumos/config.json` 的 `symbol_profile`,支援 csharp/vue/sql/powershell/dart 等多語言形狀規則,不是 Python-only。
2. `scripts/lumos:4647-4750` 既有 `cmd_drift_history` 明講「沿 git 歷史取樣重放 Check Y 的核心邏輯」,已經在 LandmarkMember 專案實測「橫跨 77 天、11 個取樣點都在」的存量漂移,而且踩過「symbol 形狀規則沒對上就會從『2% 持續三個月』變成『0% 完全沒問題』」的坑(`scripts/lumos:4660-4662`)。
3. 這條指令目前是 `scripts/lumos:33354` 註冊的扁平頂層指令 `drift-history`(不是巢狀家族),而新計劃打算把 `drift` 這個字拿來當一個全新巢狀家族的名字(`drift check/scan/ack/exam`)。兩者在 CLI 詞彙上撞在一起(一個叫 `lumos drift-history`,一個叫 `lumos drift scan`),但彼此獨立、互不參照。
4. 新設計 S13(引句所在條款,`[S13] 當執行 drift scan,工具應列出點名已不存在測試的 test 標記...以及曾經定義過而現在不存在的程式符號`)用的是 Python-only 的 ast 定義索引 + `git log -G` 歷史確認,跟 Check Y 的 `symbol_profile`(可設多語言、csharp 預設)是兩條完全獨立的規則與程式碼路徑,做的是同一件事的不同精度版本。
5. PRIOR-ART 段落(凍結快照第 25 行)逐項列了六項借用來源與三項自建項目,唯獨完全沒提到 Check Y、`load_symbol_profile`、或 `cmd_drift_history` 這個同 repo、同問題、而且已經實測過的既有機制——連「為什麼不重用它、只重用它的取樣技法」這種交代都沒有。
6. 建議:至少應該把 S13 定位成「Check Y 的高精度 Python 子集,直接呼叫/擴充 `load_symbol_profile` 而非另立一套判斷」,或者明確在計劃裡寫清楚跟 Check Y 的分工(例如 Check Y 管全語言粗篩、S13 管 Python 精篩)並避免用「drift」這個字再開一個跟 `drift-history`撞名的家族。

## F2 丙(推送閘「列出還在講被改東西的舊句」)自建一整套跟 delguard 平行的抽取邏輯,而非沿用鄰居「同一函式、不同呼叫範圍」的既有分工模式
severity: major
blocking: 是 — 不改的話會在 repo 裡維護兩條各自演化的「code 刪除傳播到筆記」判斷邏輯(commit 側 delguard、push 側 drift check),兩者的識別字抽取規則、信心分級、命中判定會隨時間各自漂移,而這正是「存量漂移防線」這個計劃本身要防的問題形狀,是會做出壞系統的
引句:「另開一道推送閘,而且比 delguard 窄三處」
1. 本 repo 對「同一種檢查、commit 時與 push 時都要跑」的既有分工模式是**同一支函式,不同呼叫範圍**:`note-shape` 在 `scripts/hooks/pre-commit:133`(`--staged`)與 `scripts/hooks/pre-push:247`(`--diff`)都呼叫同一個 `cmd_note_shape`→`_note_shape_eval`(`scripts/lumos:24080`、`23926`),只是傳入的 base/tip 範圍不同;`note-audit` 也是同一支函式家族在兩處被呼叫。
2. `delguard` 目前只在 `scripts/hooks/pre-commit:61` 被呼叫(`--staged`),推送前掛鉤完全沒有呼叫它,而且 `cmd_delguard_check`(`scripts/lumos:25611`)docstring 明講「恆 rc0(內部錯誤/超時皆 fail-open 放行)」——這是 d0 決策(delguard 只提醒不擋)的既有實作。
3. 新計劃的丙不是「把 delguard 的判斷邏輯搬到 push 時再跑一次、加上更嚴格的過濾條件擋下」(也就是沿用既有的「同一函式、不同呼叫點」分工),而是重新刻一套獨立的偵測管線:Python 用「起點版與終點版各用 ast 解一次」(凍結快照第 72 行,plain 文字「起點版與終點版各用 ast 解一次」)比對消失的 def/class/常數,跟 delguard 現有的「diff 逐行抽識別字、兩檔信心判定」(`_delguard_parse_diff`、`_delguard_confidence`,`scripts/lumos:25654`、`25665`)是完全不同的程式碼路徑與資料結構。
4. 對「其他語言」才提到重用:「從 delguard 只讀改動行的抽法延伸」(凍結快照第 74 行),但這只涵蓋非 Python 語言那一小塊,Python(本計劃唯一有考卷驗證的語言)整條路徑跟 delguard 無關。
5. 計劃本身也承認這是刻意選擇而非疏漏(「本計劃的丙不翻那條決策…另開一道推送閘,而且比 delguard 窄三處」),理由是 delguard 誤報率未知、丙要更窄更精準;但「更精準」跟「該不該共用同一套抽取/掃描骨架、只是收窄輸出範圍與換成可擋模式」是兩回事——目前的做法是後者完全另起爐灶,前者(共用骨架收窄輸出)才是這個 repo 對「commit 版與 push 版同一檢查」的既有做法。
6. 建議:讓丙至少共用 delguard 現有的 vault 掃描與信心分級骨架(`_delguard_vault_scan`、`_delguard_confidence`),Python 的 ast 精化可以作為「提高信心分級精度」的輸入餵給同一套骨架,而不是另建一條完全獨立的掃描與分類路徑。

## F4 `[when:<種類> <值>]` 用空白分隔多段值,跟既有 bracket tag 的冒號複合值慣例不一致
severity: minor
blocking: 否 — 純新增語法,不影響既有 `[until:]`/`[retire:]`/`[test:]` 的解析,只是形狀跟鄰居不對稱,人讀得懂也能用,不會讓實作者做錯決定或做出壞系統,是風格層級的不一致
引句:「[when:<種類> <值>]」
1. 本 repo 既有的 bracket tag(`[since:]`、`[until:]`、`[retire:]`、`[confirmed:]`、`[status:]`、`[applies:]`、`[test:]`、`[audit:]`、`[kill:]`、`[rollback:]`、`[guard:]`)全部是 `[key:value]` 單值形狀;唯一有「複合值」需求的 `[test:]` 在多平台情境下用冒號分隔第二段(`scripts/lumos:33238`,「--platform 多平台 config 下寫成 [test:平台:方法](method 維持識別字)」)。
2. 新的 `[when:<種類> <值>]` 在冒號之後用**空白**分隔「種類」與「值」兩段,值裡面另外又用雙冒號 `::` 做第三層分隔(`symbol` 的 `<路徑>::<名稱>`,凍結快照第 61 行)——同一個 tag 混用「空白分段 + 雙冒號分段」兩種分隔符,跟本 repo 既有 tag 一律用單冒號分段的慣例不一致。
3. 這是新語法(自建,PRIOR-ART 自己也承認「既有工具沒有可借的」),不是對舊語法的破壞,危害有限,列 minor。

## Q4 落點合不合理

已讀,無 finding——落點合理,理由如下:
1. `Systems/筆記內容閘.md` 的 `responsibility` 欄明講範圍是「管筆記內容的機械擋:提交前與推送前擋**新寫的**程式行號引用、沒寫來源的現況描述…不管程式檔歸屬(那是每支檔有家)、不管推送前判定者怎麼判(那是筆記內容審)」(`docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:6`),其正文也明講「這篇管 `scripts/lumos` 裡的 note-shape 子指令…範圍、上線點、合併的算法本身的家是 [[Systems/每支檔有家]]」(同檔第 44 行)。
2. 存量漂移防線要管的是**已經寫進去、因程式後來改動而過期**的舊句子(凍結快照第 21 行:「已經寫進去的句子,程式後來改了,要有東西把它指出來」),這跟筆記內容閘管「新寫的句子該不該寫」是不同問題,兩篇責任邊界不重疊,開 `Systems/存量漂移守衛` 是合理的。
3. 計劃裡唯一真的動到 `note-shape`(筆記內容閘管的那支既有函式)本體的部分是 [S9](凍結快照第 117 行,「筆記形狀擋應在第一格不是日期也不是條件式、或條件語法寫錯時擋下」)——這條落在既有 `Systems/筆記內容閘` 是對的,計劃的 `lands_in` 也確實同時列了這篇(凍結快照 frontmatter 第 10-11 行),不是只開新篇。

不對齊共 4 條,其中 major 2 條。
最高等級 major,blocking 共 3 條。
