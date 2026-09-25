severity: blocker

## F1 S9 沒說 about_code 寫成純量字串（非清單）時怎麼查，repo 裡現有兩篇筆記正踩在這個邊界上，會讓 S12「全部通過」直接翻車

S9 只講「有一項不在索引裡」，完全沒提 about_code 允許用單一純量寫法（`about_code: scripts/lumos`，不是清單），也沒交代這個 lint 要不要／怎麼把純量正規化成清單再逐項查。frontmatter parser（`parse_frontmatter`，`scripts/lumos:296` 起）對非空的行內純量值一律存成 `str`，不會自動包成 list；只有讀的一側用 `as_list()`（`scripts/lumos:390`）才會把它當一項清單讀。若實作照字面「逐項查」直接 `for item in n.fields.get("about_code")` 而沒經過 `as_list`，遇到純量字串就會逐字元疊代（`s`、`c`、`r`、`i`、`p`、`t`……），每個字元都查不到對應檔案，整篇筆記會被判一堆假錯誤。

repo 裡現在就有兩篇筆記是這個純量寫法：`docs/lumos-toolchain-knowledge/Systems/節點範圍與索引守衛.md:7`（`about_code: scripts/lumos`）與 `docs/lumos-toolchain-knowledge/Issues/健檢技術棧那段撞到多平台設定就整支中斷.md:7`（同樣 `about_code: scripts/lumos`）。這正是圖譜裡有名有姓的既有事故：那篇 Issue 自己在 `docs/lumos-toolchain-knowledge/Issues/健檢技術棧那段撞到多平台設定就整支中斷.md:108-112` 記載「讀的一側把單一值寫法當成一項的清單，沒問題；寫的一側……」，且明講「第一版修錯了」——這個 repo 對「單一值 about_code」曾經真的寫壞過一次。S9 的條款文字完全沒提這個已知邊界，若實作沒沿用既有 `as_list` 慣例，S12「本 repo 圖譜的每一篇筆記都應通過 lint」會在交付當下就對這兩篇筆記失敗。

severity: blocker
blocking: yes

引句:「about_code 有一項不在版本控制的索引裡,則 lint 應報錯誤」

file: `scripts/lumos:13261`
file: `scripts/lumos:1483`
file: `docs/lumos-toolchain-knowledge/Systems/節點範圍與索引守衛.md:7`
file: `docs/lumos-toolchain-knowledge/Issues/健檢技術棧那段撞到多平台設定就整支中斷.md:7`

## F2 S10「指到不存在的節點就擋」跟同一份 spec 說要沿用的設計審落點判法互相矛盾，而且 S10 的觸發條件只看檔名、沒排除非 project 類型

做法二那段明講 S10「跟設計審落點那一步同一套判法」，但那一步（`_disposal_landing_step`，`scripts/lumos:17921` 起）對 lands_in 指到還不存在的節點是放行的：`scripts/lumos:17961` 把不存在的項目歸進 `news`（新開），`scripts/lumos:17963` 印出來時只標「(新開)」，回傳仍是 `"ok"`，不是 `"fail"`——換句話說，現行「同一套判法」故意允許計劃先寫下要新開的 Systems 節點、之後再補檔。S10 條款卻直接要求「指到不存在的節點,則 lint 應報錯誤」，這跟「同一套判法」互相衝突：照字面實作 S10 會把「新開節點」這個既有、被設計審容許的合法工作流程判成 lint 錯誤；若反過來為了不衝突而放行不存在的節點，S10 的既有格式（「type『project』且以『_計劃』結尾就必須存在」）又跟條款文字寫的「應報錯誤」矛盾。spec 沒有交代這兩者要怎麼並存。

同一段另外還說「用檔名不用 type: project」，理由是「研究筆記（『_調研』）也是 project 但不要求落點；設計審落點那一步用 type 判,是因為它只跑在已經送審的計劃上」——這代表 S10 的觸發條件刻意脫離 `type` 欄位、只看檔名尾碼「_計劃」。但這樣一來，任何 `type: moc` 或其他類型的筆記，只要檔名剛好以「_計劃」結尾，就會被 S10 強制要求 `lands_in` 指到存在的 Systems 節點——這個要求對 moc（目錄型筆記，不代表要落地的功能改動）沒有意義，而現行 codebase 沒有任何機制阻止 moc 節點取名為「⋯_計劃」（`_LANDS_IN_ITEM_RE`／`_lands_in_bad` 只驗格式，不驗檔名跟 type 的搭配）。

severity: major
blocking: yes

引句:「設計審落點那一步用 type 判,是因為它只跑在已經送審的計劃上。兩套刻意不同。」

file: `scripts/lumos:17957-17964`
file: `scripts/lumos:17910-17916`

---

總結:最嚴重 severity 為 blocker;blocking 共 2 條(F1、F2)。
