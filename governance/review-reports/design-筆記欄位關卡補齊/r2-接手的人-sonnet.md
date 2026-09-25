severity: blocker

## F1 S10 沒寫 created 日期的 cutoff,實作出來會比摘要宣稱的「10 篇違規」多出至少 132 篇

條款 S10 與做法二對「計劃筆記要有 lands_in」這條規則的文字裡,完全沒有提到任何「只管某個日期之後建立的筆記」這種回溯範圍限制,跟同一支 `cmd_lint` 裡既有的兩條新規則(aliases 宣告制 `_ALIASES_CUTOFF`、值域執法 `_ENUM_CUTOFF`)不同——那兩條都明寫「cutoff 制不回溯」。但摘要的 FACT 行量測違規數時,是先加了「09-11 起建」這個隱性篩選條件才數出 9 篇,做法四也只打算修那 9 篇計劃 + 1 篇 Issue。若照 S10 字面實作(無 cutoff),對整個圖譜重跑會抓到的違規遠不止 10 篇:實際掃了本 repo `docs/lumos-toolchain-knowledge/Projects/*_計劃.md`,162 篇裡有 141 篇完全沒有 `lands_in:` 這個鍵,扣掉即將被補上的 9 篇還剩 132 篇不在做法四的修復清單裡,例如 `docs/lumos-toolchain-knowledge/Projects/panel收斂判準改革_計劃.md:4`(created: 2026-08-05,type: project)與 `docs/lumos-toolchain-knowledge/Projects/工具分類_計劃.md:4`(created: 2026-09-08)都會被新規則判錯。這會直接讓 S12「本 repo 圖譜的每一篇筆記都應通過 lint」做不到,也讓 CI 與推送前健檢在改動落地當下就整批擋下——「接手的人」拿到的第一批錯誤訊息會是上百篇跟本次改動無關的舊筆記,而不是文件承諾的個位數字。

引句:「現存的 10 篇違規在同一次改動裡修掉」

severity: blocker
blocking: yes

## F2 S10「指到存在的節點」跟它自己引用的落點判法矛盾,會擋下合法的「新開」落點宣告

做法二明寫這條規則「跟設計審落點那一步同一套判法」。那一步的實作是 `_disposal_landing_step`(`scripts/lumos:17920`),它呼叫的格式檢查函式 `_lands_in_bad`(`scripts/lumos:17910`)只驗字串長成 `Systems/<名稱>` 且不帶 `.md`,完全不驗節點存不存在;`_disposal_landing_step` 本身在格式通過後(`scripts/lumos:17966`)還會把不存在的落點標成「(新開)」照樣判 `ok` 放行——也就是說,現行「同一套判法」的實際行為是**允許**計劃宣告一個還沒開的 Systems 節點當落點,這是既有慣例(計劃先寫 lands_in 表明要開哪篇,節點後補)。但 S10 額外要求 lint「指到存在的節點」才算過,兩者行為相反:凡是照現行慣例宣告「新開」落點的計劃,一旦踩到新的 lint 規則就會被判錯,而錯誤訊息只會說「指到不存在的節點」,不會解釋這正是設計審落點那一步刻意允許的寫法——消費專案更新後第一個撞到的人,對照文件說的「同一套判法」去查落點那一步的原始碼,只會得到相反的答案。

引句:「或其中一項不是 `Systems/<名稱>` 的純字串、或指到不存在的節點,則 lint 應報錯誤」

severity: major
blocking: yes

## 已讀、無 finding 的段落

一、推送前健檢加「筆記格式」段:node_home.gate 的 on/warn/off 三態與「看不懂當 on」的行為(`scripts/lumos:21442-21444`)跟本段刻意寫成「看不懂當 warn」的差異,文件自己講清楚理由且與程式現況一致,不再重覆列。
S1–S9、S11、S12 條款文字對照現行 `cmd_lint`(`scripts/lumos:4790` 起)、`cmd_set`(`scripts/lumos:13564`)、`_about_code_path`(`scripts/lumos:13652`)、`_nodehome_resp_ok`(`scripts/lumos:21492`)的現況描述(「現在只擋加引號」「現在沒填完全不擋」「valid 寫成 no/0 會被當有效」「about_code 只驗磁碟」「responsibility 只在新開節點要求」)逐條實測跟程式碼一致,見上方查證過程,未再列成獨立 finding。
回退、實務隱患、誠實界線三節文字自洽,「about_code 查的是索引裡有沒有這支檔」與 git ls-files 語意一致(已用腳本核對全 repo 唯一一筆過期項與 FACT 行吻合)。
審計修正紀錄與〈不做的〉的交叉引用(比上一版形狀、CI 碰到清單、提交前讀提交內容)三項在文中都查得到完整說明,無壞引用。

最嚴重 severity: blocker;blocking 共 2 條。
