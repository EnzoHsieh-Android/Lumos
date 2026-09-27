severity: blocker

〈前言/白話/依據〉已讀,無 finding

## F1 抽取器加釘版本解析會讓三處既有 2-元組拆解當場炸掉

severity: blocker
blocking: 是 —— 這不是理論上的相容性瑕疵,是作者一旦真的照條款寫出「放行寫法」`路徑@<提交>:數字`,就會讓三個既有硬閘的既有測試立即失敗或在生產中丟未捕捉例外。

引句:「拆成路徑、行號、釘住的提交,交給既有」

spec 在「程式行號引用」規則與 PRIOR-ART ⑧ 都要求 `_node_code_ref_tokens` 對含釘版本寫法的 token 額外解析出「提交」這第三項資訊([S9] 也把這一點寫成條款:「含釘版本寫法的應拆出路徑、行號與提交」)。但 spec 完全沒交代這第三項資訊要用什麼形狀回傳,而目前 `full` 清單的三個既有消費者全部是嚴格 2-元素拆解,一旦 `full` 裡出現任何 3 元組(不論是只對釘版本那幾筆變 3 元組,還是整份清單統一變 3 元組),下列三處會直接丟 `ValueError: too many values to unpack`:

1. file: `scripts/lumos:22611-22612` `_nodehome_refs`(每支檔有家「別人的檔」判定,S7/S8 用的正是這支):`full, bare = _node_code_ref_tokens(text, top_dirs)` 後面接 `refs = {nfc(t) for t, _l in full if nfc(t) in req}` ——這支函式是每支檔有家 pre-commit/pre-push 硬閘的一部分,對應既有測試 `t_nodehome_foreign_ref_uses_impact_extraction`(`scripts/test_lumos.py:42949`)。
2. file: `scripts/lumos:26421-26422` `_node_code_ref_tokens_all`(docstring 自己寫「回傳形狀同 `_node_code_ref_tokens`」):`seen = {t for t, _l in full}`。
3. file: `scripts/lumos:26452-26453` `_home_confirmed`(每支檔有家判「about_code 是否算確認過的家」用的正是這支):`if nfc(_posix_norm(path)) in {nfc(t) for t, _l in full}:`。

只有 `scripts/lumos:19887-19890` 的 `_refcheck_scan`(`for token, line in full:`)spec 有明講要一起改(「同一套拆解也讓 `lumos refcheck` …對釘版本的引用改成對那個提交驗」);另外三處 spec 隻字未提要不要跟著改。

而且這不是「有人碰巧寫了看起來像釘版本的字串」的低機率巧合——note-shape 自己的「放行寫法」就是教作者去寫 `路徑@<提交>:數字` 來避免被 S1 擋下;換句話說,第一篇真的照 note-shape 的建議修好、寫進釘版本引用的筆記,下一次任何人 commit(讓每支檔有家重新讀過全庫 Systems 節點文字)就會撞上這個炸裂點,把「每支檔有家」這個現行硬閘整個弄壞,而且壞掉之後不會自己好——它每次都會重新解析全庫文字。

重現(等實作落地後可直接照這個腳本驗):在任一 Systems 節點摘要或正文寫入一個反引號包住、形如 `real/path.py@<12+位十六進位且真的存在的提交>:1` 的 token,讓 `_node_code_ref_tokens` 對它抽出第三項後,呼叫 `_nodehome_refs`(或執行 `lumos home check --staged`),確認是否拋出 `ValueError` 或靜默吞掉(取決於實作怎麼包例外,但 spec 完全沒提這條路徑要怎麼處理)。

對 LUMOS-SPEC 附帶節點 [[Systems/每支檔有家]] 的判斷:**會破壞它的合約**——這篇節點的 KEY 行明講「三個進入點共用同一套判定」,而 `_nodehome_refs`/`_home_confirmed` 正是這套判定拿來抽取「別人的檔」引用的共用函式;spec 沒有描述怎麼讓這兩處在遇到釘版本語法時不炸,也沒有把它們列進要修改的清單。

## F2 消費專案淺層 CI 會讓「最壞退到上線點」的安全網失效,退化成整庫都算新違規

severity: blocker
blocking: 是 —— 這條安全網的失效方向不是「少擋」而是「炸開全庫舊帳當新違規」,會讓任何用預設(淺層)checkout 的消費專案第一次接上 note-shape 的 CI 步驟就被灌爆,逼人立刻永久關閉這道閘或全面 `--no-verify`,直接命中自己寫的 RETIRE-IF①。

引句:「最壞退到上線點,不會退到空樹」

這句安全網宣稱建立在兩個前提上:①`_nodehome_golive`(`scripts/lumos:22854-22861`)靠 `git log --reverse -S<標記> tip -- scripts/hooks/pre-commit` 在歷史裡找到第一次出現標記字串的提交;②`_nodehome_clamp_base`(`scripts/lumos:22864-22876`)在起點早於上線點(或起點是空樹)時把起點改成上線點。但這兩步都要走得到「上線點那個提交還在本地」——淺層 clone(GitHub Actions `actions/checkout` 預設 `fetch-depth: 1`,而非本工具鏈自己 CI 用的 `fetch-depth: 0`,見 `.github/workflows/ci.yml:14-16`)恰好會讓這兩步都失靈:

- `git log -S... -- path` 在淺層歷史裡搜不到早於 shallow 邊界的提交,回傳空,`_nodehome_golive` 就回 `None`,`_nodehome_clamp_base` 直接 `return base`(不截斷)。
- 找起點那一步(`scripts/hooks/pre-push:216-231`,note-shape 的 CI 段落照抄同一套算法:「不在任何遠端分支上的提交」裡最早那個的上一個)在淺層歷史裡,`git rev-list … HEAD --not --remotes` 找到的「最早那個」本來就是 shallow 邊界本身(grafted commit,沒有可用的上一個),`git rev-parse -q --verify "$_hold^"` 會失敗,於是照 `scripts/hooks/pre-push:230` 那一行落到 `_EMPTY_TREE..$_lsha`——整段歷史當新改動。

我實測過這兩點(在暫存目錄用 `git init` 造 5 個提交、`git clone --depth 1 --no-single-branch` 複製一份):`git rev-parse -q --verify HEAD^` 在淺層 clone 回傳非 0(找不到上一個提交);`git log --reverse -S<任意標記字串> HEAD -- <path>` 在淺層邊界即是 HEAD 的情況下回傳空字串——兩者剛好是上面兩段推理各自依賴的那一步。

spec 的「CI」小節提到要先 `git fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*'` 抓遠端分支,但這只更新 refs、不會加深歷史(不是 `--unshallow`),所以在淺層 clone 上這一步之後,golive 搜尋與「找上一個」照樣搜不到——★三者最後都經上線點截斷★這句安全網宣稱在淺層 CI 上根本不會啟動。而「消費專案的 CI」小節只要求 doctor 檢查專案有沒有呼叫 `note-shape --diff`,完全沒有要求或提醒消費專案的 CI 要 `fetch-depth: 0`(或至少 unshallow),而本工具鏈自己的 `.github/workflows/ci.yml:16` 明講「code-loop gate 要算 before..sha 的 diff」才特意設成 0——這個教訓沒有被帶進「消費專案的 CI」小節。

一旦這條安全網失效,結果不是「多擋幾行」,而是把全庫每一篇既有筆記裡本來就存在、從未被審過的行號引用與沒來源的 FACT/FLOW/DEP 行,一次全部當成「這次推送新增」而擋下——這正是 RETIRE-IF① 想量的「誤擋多到大家繞過」,而且是在第一次接上就命中,不是慢慢累積出來的。

對 LUMOS-SPEC 附帶節點 [[Systems/每支檔有家]] 的判斷:這個失效模式本身不是 note-shape 新造出來的——每支檔有家目前的淺層 clone 弱點只記在關於 remerge-diff 的 PITFALL(該節點摘要:「淺層複製…回頭條件:有人回報在淺層複製裡推送被合併提交誤擋,就在 remerge-diff 前先問 `git rev-parse --is-shallow-repository`」),範圍只涵蓋合併判定,不涵蓋 golive 搜尋與起點計算這條路徑,而且每支檔有家擋的是「檔案沒家」這種相對少見的違規,爆炸半徑遠小於 note-shape 要擋的「筆記裡任何一行 FACT/FLOW/DEP 沒來源、任何一個行號引用」。note-shape 直接借用同一套 golive/clamp 機制,但爆炸半徑被放大了一個數量級,而 spec 沒有把這個放大後的風險寫進 RETIRE-IF 或誠實界線。

## F3 把 FLOW/DEP 併進 `_CONTEXT_MARKER_RULES` 會讓 `lumos lint` 對全庫既有 277 行 FLOW/DEP 重新開始噴警告,超出 d6 授權範圍且提前推翻一條尚未到期的碼內裁決

severity: major
blocking: 是 —— 這不只是噪音問題,是實作者若照字面做,會讓 `lumos lint`(pre-commit Gate L 每次 commit 都跑)對任何一篇「touched 到、裡面剛好有舊 FLOW/DEP 行」的筆記重新炸出成串警告,而且這個決定既沒有被記進 rtb 回饋那份決策紀錄,也搶在程式碼自己訂的複查日期之前生效。

引句:「的 FACT 規則並加上 FLOW、DEP」

`_CONTEXT_MARKER_RULES`(`scripts/lumos:2890-2901`)目前只收 `WHY`/`PITFALL`/`FACT` 三個鍵;緊接在它前面的註解(`scripts/lumos:2876-2881`)明講原因:「★只套四個新前綴★……FLOW:/DEP: 在本 repo 就有 277 行舊的,一開就是幾百條警告——『誤報多過真報』的機制活不過一週,舊帳不追改,新寫的現況描述請改用 FACT:」,並且已經寫了自己的 `REVISIT:2026-11-21 看觸發統計,順便決定要不要延伸到 FLOW:/DEP:`。這段話本身就是 CLAUDE.md 定義裡「程式碼答不了、但有出處、近期確認過」那類線索之外、更直接的「程式碼自己記的裁決+複查日期」——note-shape 這份 2026-09-27 的稿子在 2026-11-21 之前就要把 FLOW/DEP 併進同一張規則表,而且理由(統一 note-shape 新增行判定與 `lumos lint` 整篇判定)完全沒提到會不會重新炸出那 277 行。

而 `context_marker_warnings` 在 `lumos lint` 裡是對整篇摘要文字跑(`scripts/lumos:5037` `warns.extend(context_marker_warnings(summ))`,`summ` 是節點目前完整的 summary 內容,不是本次新增的行)——一旦 `_CONTEXT_MARKER_RULES` 加了 FLOW/DEP 鍵,任何人只要 `lumos lint` 到一篇含舊 FLOW/DEP 行的節點(不需要那幾行是本次改動),就會立刻收到「缺程式碼答不了的來源標註」警告,跟這段程式碼自己 2026-09-21 才寫定、原因正是要避免這件事的決策直接衝突。note-shape 只在 pre-commit/pre-push 的新行判定上不會受影響(那邊本來就只看新增行),但共用同一張規則表意味著 `lumos lint` 的整篇判定會被一起牽動。

另外,rtb 回饋 Issue 的決策 d6(`docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:57`:「兩層都做:形狀固定的硬擋(行號引用、done 計劃現況段、FACT 沒寫程式碼答不了的來源)+推送前派無脈絡 AI 審查員判新增筆記行是不是程式碼推得出來」)只把第一層(本計劃)的範圍寫成「FACT 沒寫程式碼答不了的來源」,沒有提到 FLOW/DEP;本稿把第一層範圍擴大到 FLOW/DEP,卻沒有回頭改 d6 或另外記一筆決策說明為什麼擴大——照 CLAUDE.md 的規矩,decisions 欄位是能挑戰程式碼現況的少數東西之一,這裡是反過來:稿子本身的範圍超出了它自己引用的決策授權,而沒有留痕。

對 LUMOS-SPEC 附帶節點 [[Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋]] 的判斷:不會破壞這篇 Issue 宣稱的行為(d1–d7 本身沒被推翻),但本稿在 d6 授權範圍之外做了擴權,而沒有寫決策更新——建議把 FLOW/DEP 併表這件事單獨補一筆決策或至少寫進本計劃「依據」段,而不是隱含在「實作是改既有規則」這句話裡。

## 其餘小節

〈做法〉裡「範圍與行」段落除 F2 指出的淺層 clone 外,合併提交、改名、刪檔、非 UTF-8、decisions 巢狀清單的處理描述與 [S5][S6] 條款文字一致,已讀,無 finding。

〈做法〉裡「回傳碼、開關與跳過」段落(`_gate_event` 契約、`note_shape.gate` 從快照讀、`LUMOS_SKIP_NOTE_SHAPE`)已讀,與既有鄰居(每支檔有家)寫法一致,無 finding。

「治理帳寫入加鎖(移出)」段落對照 [[Issues/治理帳多個寫入者都沒上鎖]] 判斷:**不影響**它宣稱的行為——那篇 Issue 自己已經寫明「本計劃上線後,每次擋下與環境變數跳過會多寫一筆(放行不寫),寫帳頻率會略增」,跟本稿「實務隱患」段落的措辭一致,沒有新增未被那篇記錄到的風險。

「紀律範本改寫」「消費專案的 CI」(除 F2 指出的淺層 clone 缺口)已讀,無其他 finding。

條款 [S1][S2] 除 F1 指出的抽取器共用消費者問題外,文字本身可逐字寫成測試,無其他 finding。[S3] 見 F3。[S4] 見 F2。[S5][S6][S7][S8][S10][S11] 已讀,可逐字寫成測試,無 finding。[S9] 見 F1(這條本身就是 F1 所指問題的條款來源)。[S12]:新增程式檔要掃「全部筆記」找沒釘版本的舊引用——若真的逐次全庫掃描,效能會隨知識庫篇數線性增加(本庫已有上百篇 Projects/Issues),但條款本身寫得出測試,不再展開判成 finding,只在此提醒:「實務隱患」段落目前只從誤擋角度寫 RETIRE-IF①,沒有從全庫掃描成本角度寫回頭條件。

〈回退〉〈實務隱患〉(除上述)〈誠實界線〉〈審計修正紀錄〉已讀,無 finding。

---

總結:最嚴重 severity 是 blocker(F1、F2 各一);blocking 共 3 條(F1、F2、F3)。
