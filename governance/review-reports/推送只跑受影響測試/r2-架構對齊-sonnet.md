severity: major

**① 分層與依賴方向**

severity: major
blocking: 是(跨層重複:掛鉤自己認主線,lumos 那層已有認主線的函式)
spec 段落:「做法」第 1 點。
問題:計劃讓掛鉤用字串比對判定「名字不是 `main` 或 `master`」,把這個結果當降級依據。但專案裡「哪條是主線」已由 lumos 那層負責,判定也不只看名字。`_push_mainlines` 的候選是 `refs/remotes/<遠端>/HEAD`、`main@{upstream}`、`master@{upstream}`、`<遠端>/main`、`<遠端>/master`,而且會跳過「就是這次被推的那條」。計劃的字串比對只看名字,遠端預設分支叫 `develop`、`trunk` 之類時,推主線會被誤當功能分支,本機全套就被跳過。
引句:「目的是 `refs/heads/<名>` 而且名字不是 `main` 或 `master` → 這個 ref 算功能分支」
佐證:`scripts/lumos:65263`(`_push_mainlines`)、`scripts/lumos:65274`(候選含遠端 HEAD)、`scripts/lumos:65710`(`_mainline_ref`)。

**② 命名與錯誤處理**

severity: minor
blocking: 否(名稱與訊息不一致,結構沒壞)
spec 段落:「做法」第 2 點與「現況」。
問題:
- 掛鉤現有的判定一律走 `pf_json` 加 grep(`_suite_this`、`light_ok`、`autoloop_full`),不另判分支名。計劃在同一段 `case` 前塞一個新的字串分支,風格不同。
- 現有逃生寫法是 `LUMOS_SKIP_*`,會留帳。計劃的「不做」寫明不提供強制全套的環境變數,只能手動跑 `test_lumos.py`,跟其他閘「有逃生旗標且留帳」的慣例不一致。這是刻意取捨,但屬於不對齊。
- 計劃要印的訊息,措辭要跟現有那一行對齊:現有訊息已經寫「CI 會跑全套當後盾」。
佐證:`scripts/hooks/pre-push:544-578`、`scripts/hooks/pre-push:872-890`。

**③ 第二種做法**

severity: major
blocking: 是(就是這一問要抓的情況:掛鉤與 lumos 各有一套認主線)
spec 段落:「做法」第 1 點最後一句「不另寫 lumos 子指令」。
問題:專案裡已經有兩套認主線的做法,`_mainline_ref`(只認 main/master)和 `_push_mainlines`(多候選)。兩者並存的理由與收斂路已寫在 `scripts/lumos:65269` 與 `scripts/lumos:65714`。計劃在掛鉤裡再加第三套純字串判法,還明說不走 lumos。計劃在「不做」裡聲稱不另開主線起點算法,但這裡等於另開了一套「什麼是主線」的判定。
建議:讓 `pitfalls --json` 輸出一個欄位(例如 `pushed_ref_is_mainline`),由 lumos 用 `_push_mainlines` 的結果算;掛鉤只讀結果,跟 `light_ok`、`autoloop_full` 同一模式。這也符合 `scripts/hooks/pre-push:816` 的註解「判斷在 lumos 裡做,這裡只讀結果(別在 bash 另刻一份)」。
引句:「判斷寫在掛鉤裡、用字串比對,跟掛鉤現有「`refs/heads/*` → 分支」的判法同一處同一種寫法,不另寫 lumos 子指令。」
佐證:
- `scripts/hooks/pre-push:584`(現有的 `refs/heads/*` 只用來判「是不是分支」,從沒用來判主線)。
- `scripts/hooks/pre-push:814-816`(「判斷在 lumos 裡做」的慣例)。
- 我在掛鉤裡沒搜到任何字串比對 main/master 的先例,所以計劃說的「同一種寫法」沒有對應的既有先例。

⚠ 計劃宣稱「不改 `pitfalls --json` 的欄位」是為了避開新舊版本錯開的問題。這是刻意取捨,但代價就是上面這個第二套做法。

**④ 落點 lands_in**

severity: minor
blocking: 否
spec 段落:frontmatter 的 `lands_in`,以及「做法」第 5 點。
問題:
- `lands_in` 只列 `Systems/bound-tests-gate`。該節點目前掛 0 份計劃、沒寫負責範圍、管 3 支檔。測試套件閘的降級邏輯在 `scripts/hooks/pre-push`,而這支檔牽連 56 篇筆記,計劃沒指出哪一篇是它的家。
- 改動同時動了 `scripts/templates/graph-discipline.md`、專案 `CLAUDE.md` 和 `AGENTS.md`,這些檔的家也沒列進 `lands_in`。
- 專案鐵則 5 要求「改到的每支檔都得先有家」。建議在 `lands_in` 補上掛鉤與範本各自的家,或在 `bound-tests-gate` 補上負責範圍後明寫它管推送測試套件閘。
佐證:`scripts/templates/graph-discipline.md:59`(範本裡「全套留給推送前的閘」那句)。

不對齊共 3 條,其中 major 2 條。
