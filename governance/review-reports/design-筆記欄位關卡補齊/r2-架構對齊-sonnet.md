severity: major

## 四問逐答

### 1. 分層與依賴方向

新推送前段落放在 `run_doctor` 裡,跟既有同類段落(S1–S15、Check L/M)同一層,這點對齊(`scripts/lumos:1002` `section(idx, title)` 這套框架)。但 lint 那一側不對齊:`cmd_lint` 文件明講「node-local 不掃 repo」,唯一例外是 Check J(regen 節點 `[src:]/[git:]` 驗證),而且明文標「opt-in、量小」(`scripts/lumos:4792`、`scripts/lumos:4532`)。S9(about_code 要在版控索引裡)要求 `cmd_lint` 對每篇有 about_code 的節點做 `git ls-files` 這類 repo 級查詢,不是 opt-in、也不小——見 F1。

### 2. 命名與錯誤處理

`note_lint.gate` 的 on/warn/off 三態沿用 `node_home.gate`(`scripts/lumos:21400` `_nodehome_config`)這點對齊;`warn()`/`warn_soft()` 分級（issues 計數決定 rc)的框架也對齊(`scripts/lumos:1008` 與 `scripts/lumos:1030`)。但「值看不懂」的預設不同:node_home 看不懂當 `on`(`scripts/lumos:21444`「已用 on」),note_lint 看不懂當 `warn`——spec 自己承認且解釋了理由(見 F4,判準只看一不一致,不評理由好壞)。另外 S8 的 valid 判準(只認 true/false)沒有對齊既有讀側慣例(`str(d.get("valid","true")).lower()=="false"`,`scripts/lumos:1816`/`1981`/`12276`/`12288`/`14114`/`14486`/`14660` 共 7 處同寫法)——見 F3。

### 3. 第二種做法

- lint 補欄位規則整體沿用既有 cutoff 機制的姊妹型(scope 值域「不走 created cutoff,宣告當下已回填」,`scripts/lumos:4897`-`4899`)而非 `_ALIASES_CUTOFF`/`_ENUM_CUTOFF` 那種按 created 日期分段的型(`scripts/lumos:4854`、`4863`)——這點是選了既有兩種既有做法裡的一種,不是新發明,對齊。
- about_code 查版控索引的判法,若真的走 `git ls-files`,跟 `_nodehome_list`(`scripts/lumos:21636`)读索引的邏輯是同類查詢,方向對;但發生的**位置**不對齊(見 F1,這是「地方」問題不是「方法」重複發明)。
- doctor 新段落本身則是把「全圖重跑 lint 錯誤等級規則、hard block」這個既有形狀(Check L,`scripts/lumos:1196`-`1205`,無開關、永遠硬擋)再做一次,但外面包一層新的三態開關——見 F2,是同一類功能的第二套機制。

### 4. 落點合不合理

`lands_in: [Systems/lumos-cli-write, Systems/lumos-cli-read]` 兩篇都存在(`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md`、`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md`),且都是 `scripts/lumos` 相關的既有落點,跟 S10 要求的格式與存在性判法一致,這段對齊,不另開一篇。

## F1 lint 新增 git 索引查詢,踩破「node-local 不掃 repo」的唯一 opt-in 例外

severity: major
blocking: yes

`cmd_lint` 的既有分層合約寫死只有一個例外、而且是窄的:

引句:「例外:regen 節點的 Check J 需檔案+git 存取,opt-in、量小」

`scripts/lumos:4792`(docstring 原文,同段亦見 `scripts/lumos:4532`:「本函式為 regen 節點對 lint「node-local 不掃 repo」原則的 opt-in 例外」)。設計案 S9 要求:

引句:「about_code』每一項要在版本控制的索引裡(`git ls-files` 列得到,已加進提交的也算)」

這條規則要套在**所有有 about_code 的節點**上(而不是像 Check J 只窄套在 regen 節點),而且是提交前 `lumos lint <node>` 這條 node-local 快路徑每次都要跑,不是 opt-in——等於在唯一一個「git 存取例外」之外,又開了一個更寬的第二個例外,卻沒有走既有那套「opt-in、量小」的收斂方式(例如像 Check J 一樣獨立成一支共用函式、限定觸發條件)。設計文本沒有提到這個既有邊界,也沒有交代要不要沿用 Check J 的「cmd_lint 與 run_doctor 共用同一函式」模式(`scripts/lumos:4526`)。

## F2 doctor 的「全圖重跑 lint、hard block」已有 Check L,新段落另開一套帶開關的平行機制

severity: major
blocking: yes

doctor 既有 Check L 已經在做「對圖譜每篇筆記重跑 lint 錯誤、全部用 `warn()`(會加進 issues、推當 rc)硬擋」這件事,而且不分專案、不能關:

引句:「筆記開頭欄位的格式有沒有踩到已知會讓工具讀錯的寫法」

(`scripts/lumos:1196` 段名,程式在 `scripts/lumos:1198`-`1205`,用 `warn(lint_lines, ...)` 無條件計進 issues)。這段目前只涵蓋 `n.lint`(frontmatter 指紋子集),沒有涵蓋 `cmd_lint` 裡 type/status/aliases/decisions 那批(這點設計案的盤點是對的)。但設計案填這個洞的方式不是擴充 Check L(例如把 `cmd_lint` 的完整 errs 併進 Check L、需要開關再加開關),而是另開一段:

引句:「對圖譜裡每一篇筆記跑 lint 的**錯誤等級**規則(提醒等級不跑,避免重複嘮叨);有錯的列出篇名與第一條錯誤」

同一類「重跑 lint 輸出、全圖、doctor 裡擋」的功能,現在會有兩套並存的機制:Check L(永遠硬擋、無開關)跟新段落(三態開關、warn 預設)。設計文本完全沒提到 Check L,沒有交代為什麼不直接擴充它、或兩段日後語意會不會對不上(例如同一篇筆記同時被 Check L 判 error、又被新段落用 warn 模式放行)。

## F3 決策 valid 的判準沒有對齊既有讀側的容忍寫法

severity: minor
blocking: no

全庫至少 7 處讀 `valid` 欄位都用同一種容忍寫法,例如:

引句:「if str(d.get("valid", "true")).lower() != "false":」

(`scripts/lumos:1816`,同寫法另見 `scripts/lumos:1981`、`12276`、`12288`、`14114`、`14486`、`14660`)——判準是「小寫後等不等於 false 字串」,`True`/`FALSE`/`false` 都認得,只有 `no`/`0` 這類才會被誤判成有效。設計案的條款是:

引句:「[S8] 若一條決策的 valid 不是 true 或 false,則 lint 應報錯誤」

沒寫清楚「true/false」是要求字面型別(YAML bool)還是沿用讀側那套大小寫不敏感的字串判準;若 lint 只認嚴格小寫 `true`/`false` 而讀側能接受 `True`/`FALSE`,會出現「讀側判有效、lint 判違規」的落差,跟既有讀寫兩側同一套判準的慣例不一致。

## F4 gate 看不懂時的預設值跟 node_home 的既有慣例相反(spec 已自陳,仍記一筆)

severity: minor
blocking: no

`node_home.gate` 看不懂時的既有慣例:

引句:「設定檔的 node_home.gate={g!r} 看不懂(只認 {'/'.join(_NODEHOME_GATE_VALUES)}),已用 on」

(`scripts/lumos:21444`,即看不懂→當 on、照樣擋)。設計案的 `note_lint.gate` 反過來:

引句:「值看不懂:當 `warn`,並印一行設定看不懂」

雖然設計文本自己解釋了理由(新段落影響所有消費專案,看不懂寧可不擋),但這仍是同一類「設定值看不懂時的預設方向」上,跟既有 node_home 慣例不一致,依判準只記一不一致、不評理由好壞。

---

不對齊共 4 條,其中 major 2 條。
