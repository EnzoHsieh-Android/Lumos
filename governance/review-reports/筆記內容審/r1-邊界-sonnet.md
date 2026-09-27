severity: blocker

# 審查範圍與方法

逐節讀完 `governance/review-reports/筆記內容審/r1-work.md`(155 行,與已提交的 `docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md` 逐字相同,已用 `diff` 核對無差異)。對照 `clone-ns` 這份程式碼(`scripts/lumos` 33062 行、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`)逐一開檔驗證 spec 提到的函式/常數/掛鉤/CI 步驟是否存在、語意是否相符;並核對〈判定者能不能用:小實驗〉那張表的數字是否能從 `governance/audits/2026-09-27-rtb-notes/judge-experiment/` 的原始卷證(`judge_key.json`、`judge_opus.md`、`judge_sonnet.md`)重算出來;並核對〈前身 r3 發現怎麼處理〉一段對 `governance/review-reports/筆記不存程式碼推得出的事/r3-*` 六份席報告的計數與內容是否屬實。審查鏡頭聚焦「邊界可執行」:待審為空、重複文字、計劃狀態來回切換、判定檔資料夾異常(不存在/上千個檔/壞掉/被手改)、多分支同推、search 證據字串等極端輸入。

# 逐節記錄

## 開頭欄位(frontmatter)
已讀,無 finding。`lands_in: Systems/筆記內容審`、`related` 五個連結(`Projects/筆記不存程式碼推得出的事_計劃`、`Projects/筆記形狀擋_計劃`、`Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋`、`Systems/筆記內容閘`、`Issues/治理帳多個寫入者都沒上鎖`)逐一開檔核對,全部存在。`Systems/筆記內容審` 目前還不存在(spec 自己說是「新開」的家),屬預期中的「尚未落地」,不算壞連結。

## 白話 / 依據
已讀,無 finding。「依據 d1–d6、d8」對照 `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md` 的 `decisions:` 欄,d1–d6、d8 確實存在且 `valid: true`;d7 存在但 `valid: false`、`superseded_by: d8`,spec 正確地把 d7 排除在引用之外。

## ★這篇是重寫稿★ 段落
已讀,無 finding。核對 `governance/review-reports/筆記不存程式碼推得出的事/` 下 r3 六份席報告(`r3-正確性-opus.md`、`r3-併發-sonnet.md`、`r3-接手-sonnet.md`、`r3-邊界-sonnet.md`、`r3-架構對齊-sonnet.md`、`r3-外家否決-codex.md`),用 `grep -cE "^#+ F[0-9]+"` 逐檔算 finding 數,加總 12+3+5+5+4+6=35,與 spec 講的「共 35 條」相符。邊界席 F5(`r3-邊界-sonnet.md:95`)確實在講「〈擋什麼的初步實測〉查無此篇」,而 `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:127` 確實是一個段落標題不是獨立筆記,spec 講的「1 條駁回」對得上、駁回理由也站得住。

## PRIOR-ART / RETIRE-IF / REVISIT
已讀,無 finding。RETIRE-IF③引用的「新增的脈絡行月量」與實務隱患〈容量〉段的「近一個月 473 個提交」都能在 `docs/lumos-toolchain-knowledge/Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋.md:127` 找到同一數字(473 個提交、25,282 行),兩處互相一致。

## 判定者能不能用:小實驗
已讀,無 finding——逐格重算過。`judge_key.json` 裡 `src:"audit"` 55 筆、`src:"why_chosen"` 13 筆(`why_chosen` 的 `n` 值為 3,4,7,14,16,20,30,47,53,54,55,59,68)。拿這組當 ground truth 跟 `judge_opus.md`/`judge_sonnet.md` 的逐句標記做交叉表:
- opus:CONTEXT={3,4,14,16,20,30,54,55,59}(9 筆,全在 why_chosen 集合內)、MIXED∩why_chosen={7,47,53,68}(4 筆)、CODE∩why_chosen=0——精確對上 spec 表格「0(9 脈絡、4 一半一半)」;fact 集合(55 筆)裡 CODE 53+MIXED 2=55、CONTEXT 0,精確對上「55(53 推得出、2 一半一半)」。
- sonnet:CONTEXT∩why_chosen={3,7,14,16,20,30,54,59}(8 筆)、MIXED∩why_chosen={4,68}(2 筆),剩 47,53,55 落在 CODE——精確對上「3」句理由誤判成純程式碼;fact 集合裡漏判的唯一一句是編號 27,`judge_key.json` 裡 n=27 的原句是「AI 那一步呼叫模型前續租,續租是租約表新增一列」,sonnet 的判詞(`judge_sonnet.md:29`)寫「句子講的是 Phase13 當時的歷史行為,機制已整支刪除」而判成 CONTEXT,opus 同一句(`judge_opus.md:29`)判 CODE 並引 `src/rtb/analyzer/task_store.py:22-27`——精確對上 spec 講的「漏 1 句:在講已刪掉的程式,它判成歷史」,也對上 spec 之後加的第①句派工詞補丁(現在式描述已刪掉的程式也算推得出)。
- 「68 句同意 64 句」:opus 與 sonnet 的 CONTEXT 集合對稱差 = {4,55} ∪ {7,27} = 4 句,68-4=64,精確相符。

## 做法 1:哪些行要審
已讀,無 finding。開檔核對 `_ns_range_added`(`scripts/lumos:23579`)回傳值確實是「{路徑: 行文字集合}」(`dest.setdefault(p, set()).update(...)`),不帶行號,加了又刪的行仍在集合裡(它是整段範圍的聯集,不因後來刪除而移除)——跟 spec 講的「只回範圍裡每個提交加過的行文字的集合,不帶行號、後來刪掉的也還在」一致。「終點版本裡還在、落在哪一塊、第幾行」確實是 `_note_shape_eval`(`scripts/lumos:23763`)自己的迴圈邊查邊算(`for p, linenos in sorted(cand.items())` 之後讀 `reader(p)`、`_ns_regions(text)`、逐行比對 `texts_by`)。三處寫死 `scripts/hooks/pre-commit` 字面路徑的位置核對到:`_nodehome_golive`(`scripts/lumos:22946-22947`,`"--", "scripts/hooks/pre-commit"`)、`_ns_range_added` 內的 `mark` 判斷(`scripts/lumos:23603`,`f"{c[0]}:scripts/hooks/pre-commit"`),`_nodehome_clamp_base`(`scripts/lumos:22954-22966`)透過呼叫 `_nodehome_golive` 間接寫死——三處都存在且都缺「哪支掛鉤」這個維度,只有 `mark` 字串可換,spec 說的「加參數」精確對上程式碼現在缺的那一半。

## 做法 2:內容編號與判定檔——F1、F2

## 做法 3:指令(`lumos note-audit`)——F1(續)、F3
逐條核對:`--orchestrator claude|codex` 必填的先例在 `cmd_canary`(`scripts/lumos:7699,7821-7837`)與 `cmd_loop_next`(`scripts/lumos:10852-10869`)裡都有「定錨後不能中途換家」的既有規矩,spec「照 loop next 的既有規矩」屬實。`_validate_repo_ref`(`scripts/lumos:19819-19832`)確實拒絕空字串、絕對路徑與含 `..` 的 token,S7 講的「它本來就拒絕絕對路徑與 `..`」屬實。`judge_prompt.md` 確實存在(`governance/audits/2026-09-27-rtb-notes/judge-experiment/judge_prompt.md`)且開頭寫死 `/Users/enzo/rtb-mainwt`、`Python`,跟 spec 講的「那支檔開頭寫死 rtb 的路徑與『Python』」一致。`home check --diff` 與 `note-shape --diff` 在 `scripts/hooks/pre-push:236,247` 確實背靠背呼叫同一段 `_hrange`,spec 講「跟 home check、note-shape --diff 並排」屬實。`governance/.gitignore`(`scripts/lumos:17367-17377`)只忽略 `code-loop/`、`runtime/` 兩個子目錄,不會誤傷 `governance/note-verdicts/`,spec 沒討論到這點但也沒踩到這個坑。

## 做法 4:上線前校準與接線
已讀,無 finding。「推送前掛鉤全 repo 只有一份,分不出這次推送是哪一家在編排」跟 `scripts/hooks/pre-push` 是單一 bash 腳本、沒有依編排者分流的機制吻合。

## 做法 5:規範文字與路由
已讀,無 finding。

## 條款 S1–S16
逐條核對過用到的既有機制存在(`_gate_event`/`scripts/lumos:856`、`--orchestrator` 家族鎖定、`_note_shape_config` 的 `block/warn/off`),S1–S16 描述的驗收條件本身內部一致,唯 S9(見 F2)在「合併不衝突」的宣稱範圍上有留白。

## 回退
已讀,無 finding。「`.github/workflows/ci.yml` 不在 lumos update 的同步清單裡」核對 `_VENDORED_TOOLKIT`(`scripts/lumos:16901-16905`)與 `_VENDORED_TREE_FILES`(`scripts/lumos:16912-16922`),確實沒有 `ci.yml`,但有 `scripts/hooks/pre-push`、`scripts/hooks/pre-commit`——跟回退步驟 1(手改 ci.yml)與步驟 3(`lumos update` 拉回 hook 裡的呼叫)的不對稱描述完全吻合。

## 實務隱患——F1(續)、F2(續)、F3(續)
見下方 finding。

## 誠實界線
已讀,無 finding。「本機與 CI 的範圍可能不同」一段核對 `scripts/hooks/pre-push:220-226`(本機用「不在任何遠端分支上的最早提交」)與 `.github/workflows/ci.yml:130-143`(CI 從空樹截到上線點、只排除主線),兩套算法確實不同,spec「不會放過,只會多擋」的結論在程式碼層面站得住(both err on the side of 多查)。

## 前身 r3 發現怎麼處理
已讀,無 finding(見上方「★這篇是重寫稿★」段落的核對)。

## 審計修正紀錄
「(本篇新開,待 r1。)」——空段落,符合「這是 r1 審查」的現況,不是遺漏。

# Findings

## F1 判定檔沒有任何真偽/竄改檢查,任何人手寫一個 JSON 檔就能偽造「已涵蓋」
severity: blocker
blocking: 是 —— 整個機制的核心承諾(程式碼推得出來的內容要刪掉才推得上去)可以被一個沒有任何機關擋、也不留痕的手寫檔完全繞過,而且連 doctor 的事後掃描都會把偽造的判定當成正當涵蓋

引句:「兩個會談同時寫、兩條分支各自寫,都不會互相蓋或合併衝突,所以不用鎖」

file: `governance/review-reports/筆記內容審/r1-work.md:60`(判定檔寫法)、`governance/review-reports/筆記內容審/r1-work.md:78`(check 讀判定檔)、`scripts/lumos:19676-19698`(`cmd_anchor_verify`:本 repo 既有的「裁判檔案防竄改」機制,只 hash 一份固定 baseline)

理據:
1. spec 第 60 行說判定檔是「每次 record 或 skip 寫一個新檔 `governance/note-verdicts/<時間>-<亂數>.json`」,`record` 的驗證(做法第 71–77 行,S6/S7)只管「這次 `record` 呼叫收到的報告」——檢查報告開頭三行、`file:`/`search:` 證據是否合法。這些驗證只在**寫入那一刻**跑一次,寫出來的 `.json` 檔本身之後不帶任何簽章、雜湊清單或跟原始報告綁定的機制。
2. `check`(做法第 78 行,S10)只讀「被推送頂端提交裡的判定檔」,邏輯是「這個內容編號有沒有出現在某個判定檔裡、標成脈絡或略過」——完全不重新驗證那個判定檔裡的 `file:`/`search:` 證據、`seat:`/`provider:`/`model:` 欄位是否曾經通過 `record` 的驗證管線。任何人只要在工作目錄手寫一個 `governance/note-verdicts/x-1.json`(內容自訂,宣稱某個內容編號的判定是「脈絡」),提交推上去,`check` 就會判它涵蓋、放行 push;doctor 第 8 點的事後掃描(做法第 83 行)一樣是「從遠端頂端提交讀判定檔」,一樣不驗證內容,一樣會被同一份偽造檔騙過。
3. 本 repo 已經有專門處理「裁判被改過而沒人簽名」這類問題的機制:`anchor verify`(`scripts/lumos:19676`、`scripts/hooks/pre-push:130-143`)——它對 hook/測試腳本這種固定「裁判」檔案做 baseline sha256 比對,改了沒重新簽名就擋下推送。判定檔本質上也是一種「裁判輸出」(記錄了審查員判過什麼),但 spec 完全沒有把它納入任何類似的防竄改機制,也沒有解釋為什麼判定檔不需要——`anchor verify` 這個既有先例證明本專案的作者群知道「裁判檔案沒簽名等於裁判形同虛設」這個問題類別,但這份 spec 對「判定檔」這個新裁判檔案類型完全沒討論到。
4. 對照 spec 自己在實務隱患〈守衛面〉(第 125 行)列出的「已知放過路子」:「刻意把一句話拆成很多行並讓每一行單獨看都像脈絡」——這比手寫一個 JSON 檔麻煩得多,而且 spec 為它設計了對應防禦(上下文、派工詞第⑤句、RETIRE-IF②抽樣)。手寫判定檔這條路徑比它簡單、有效、且完全不留痕(不像 `skip`/`gate=warn|off`/`--no-verify`/`LUMOS_SKIP_NOTE_AUDIT` 那樣至少會在治理帳或 doctor 裡露出「這裡被跳過了」的痕跡),spec 卻完全沒有提到,〈誠實界線〉段落也沒有承認這條路。

## F2 「兩條分支各自寫判定檔,合併不衝突」只證明 git 機械上不衝突,沒討論到「取最重」規則會讓合併後突然重新擋下另一分支已經通過的內容
severity: minor
blocking: 否 —— 不是機制被繞過,是機制按照自己宣稱的「取最重、寧可多擋」原則正常運作,只是這個後果沒被明講,實際觸發需要兩分支各自寫出完全相同(去頭尾空白後逐字相同)的新增行文字,場景不算常見

引句:「兩條分支各自寫判定檔 → 檔名不同,合併不衝突」

file: `governance/review-reports/筆記內容審/r1-work.md:127`(實務隱患〈資源併發〉)、`governance/review-reports/筆記內容審/r1-work.md:61`(取最重規則)

理據:設想 A、B 兩條分支各自獨立在同一篇筆記同一區塊新寫了逐字相同的一行文字(內容編號因此相同)。A 分支的判定者判成「脈絡」並 `record` 通過、B 分支的判定者(在 A、B 分岔之後獨立跑,看不到彼此)判成「推得出」並 `record` 通過——兩次 `record` 各自在自己的分支狀態下都合法通過驗證(S6/S7 檢查的是報告本身格式與證據,不是跨分支一致性)。合併這兩條分支時,git 對兩個不同檔名的新增檔案確實不會產生衝突(spec 這句話本身沒錯),但合併後的頂端提交同時看得到兩份判定檔,依「取最重的那次非申訴判定」(第 61 行)這一行會被判定為「推得出」,即使 A 分支的作者當初拿到的是「脈絡」、以為已經通過。這不是被繞過(方向是更嚴格,不是更寬鬆),但 spec 在「不衝突」這句話旁邊沒有講清楚「衝突」在語意層面其實可能發生,只是被恰好收斂成「偏嚴格」的方向而已——跟本節其餘每一條隱患都附一句「會怎樣」的寫法不一致。

## F3 search 證據的掃描上限(5,000 支檔)非常接近本 repo 目前的檔案數,而這個機制的落地首站正是本 repo
severity: minor
blocking: 否 —— 判定者仍可改用 `file:line` 證據頂上,不會讓機制整個失效,只是 search 這條路會提前失靈

引句:「跳過 .git、最多掃 5,000 支檔或 50 MB,超過就判這條證據無效」

file: `governance/review-reports/筆記內容審/r1-work.md:76`

理據:`git ls-files | wc -l` 在 `clone-ns`(本 repo 的凍結工作副本)量到 4,686 支已追蹤檔案,離 5,000 的上限只剩約 6%。spec 自己在〈容量〉隱患段(第 129 行)估計「本 repo 近一個月 473 個提交,估一個月一兩百個小檔」——而這些小檔(`governance/note-verdicts/*.json`、`governance/rel-cascade/*.jsonl` 這類本機制自己會持續新增的檔案)正好會被同一支 `git ls-files` 算進去。照這個成長速度,`search:` 這種證據形式會在本機制上線後數月內對本 repo 本身失效(掃描超過上限 → 整條證據判無效),屆時判定者只能改用 `file:line`——spec 沒有把這個時間點寫進 REVISIT,也沒有討論上限是否該隨 repo 規模調整。

# 總結

檔級最嚴重等級 blocker,共 1 條 blocking(F1);另有 2 條 minor、不 blocking(F2、F3)。其餘各節逐一核對過交叉引用、函式存在性與語意、以及〈判定者能不能用〉小實驗的原始數字,均與程式碼及卷證相符,未發現壞連結或杜撰數字。
