severity: major

## 四問逐答

**1. 分層與依賴方向**
`cmd_impact` 的 ranked 分支(改檔前推筆記/Edit-hook,`scripts/lumos:21444` 起)目前完全不呼叫任何 `_nodehome_*` 函式——`_nodehome_*` 家族是「每支檔有家」守衛專用的獨立資料層,靠 `_NodehomeSide`(`scripts/lumos:17812` `__slots__ = ("files","all_paths","notes",...)`)與 `_nodehome_parse_note`(`scripts/lumos:17905`,自己重讀磁碟/`git show` 解析 frontmatter)運作,跟 `cmd_impact` 用的 `Env`/`env.notes`(`Note.fields`)是兩條平行資料路徑,兩邊现狀零交叉呼叫(`scripts/lumos:20900-22100` 掃過 `_nodehome_` 零命中)。計劃 S1/S2 要求 `_impact_mark_about` 的後繼邏輯去讀「家」,但沒有交代怎麼跨過這條資料層邊界——見下方 F1。

**2. 命名與錯誤處理**
旋鈕 `LUMOS_IMPACT_HOME`(S7,`r1-snapshot.md:56`)符合既有 `LUMOS_IMPACT_ABOUT`/`LUMOS_IMPACT_ABOUT_MAX`/`LUMOS_IMPACT_BASENAME_MATCH` 命名慣例,走同一支 `_impact_knob`(`scripts/lumos:21295`)。顯示標記「★家★」取代「★關於★」(S8)沿用既有 `★關於★`/`★COMBO★`/`★INVARIANT★` 星號標記慣例(`scripts/hooks/claude/impact-hook.py:647`)。S13 的「不擋只提醒」訊息風格與 `cmd_new` 既有「擋下:」/「提醒:」二分慣例一致(`scripts/lumos:12496` 起多處「提醒:筆記建好了,但…」)。這三處命名/訊息都跟鄰居一致,沒有問題。

**3. 第二種做法**
有,見 F1(家的查找)與 F3(Check J 的檢查對象)兩處。

**4. 落點合不合理**
`retrieval-ranking`/`節點還原`/`check-j-regen-guard` 三篇都已存在且主題對得上,不需要另開新篇,這點合理。但 lands_in 清單(`r1-snapshot.md:75-79`)漏列了 `Systems/每支檔有家`——見 F2(純落點記錄不完整,不影響本次改動結構本身)。

## 正式發現

### F1 「家」的查找沿用宣稱跟計劃自己寫的效能作法互相矛盾,逼出跨層直呼或第二套實作
severity: major
blocking: 是 — 判準:major 錨定「引入第二種做法或跨層直呼」,本案兩個出口都踩。

S1 寫「家的定義與比對鍵沿用每支檔有家那一支(同一個函式,不另寫一套)」,測試名稱也叫 `t_impact_home_uses_nodehome_definition`,字面上要求直接呼叫 `_nodehome_homes(repo_root, side)`(`scripts/lumos:17995`)。但這支函式吃的 `side` 是 `_NodehomeSide`(`scripts/lumos:17812`),必須經 `_nodehome_reader`/`_nodehome_side`(`scripts/lumos:17880`)用 `git show`/`git diff` 子行程去重讀、重解析(`_nodehome_parse_note`,`scripts/lumos:17905`)每篇 Systems 筆記的 frontmatter——跟 `cmd_impact` 早就 `Env(vault)` 讀好的 `env.notes[*].fields` 是兩條完全獨立的資料路徑,現狀零交叉呼叫。改檔前推筆記這支 hook 是 30 秒外層逾時、20 秒總預算的熱路徑,`_impact_mark_about` 的既有設計明文寫著「懶觸發:先查欄位,命中才讀該篇正文算雜湊(無 git、無子行程)」(`scripts/lumos:21273`)——這是刻意避開 git 子行程的既有分層原則。

同一份計劃的「實務隱患」段又寫:「找家要掃全圖的 about_code——既有的 about 計數已經有快取,本案沿用,不另掃一次」(`r1-snapshot.md:86`)。這句指向的是 `_impact_about_counts`(Env-based,純記憶體掃 `env.notes.values()`,無 git),不是 `_nodehome_homes`(git-plumbing based)。也就是說計劃內部兩句話(S1 vs 實務隱患段)已經在講兩套不同的「怎麼拿到家」機制——S1 要求「同一個函式」,實務隱患段實際打算重用的是另一個 Env-based 的快取。真的實作出來,要嘛把 git 子行程拉進本來刻意零子行程的熱路徑(跨層直呼進 nodehome 的快照機制),要嘛照著 `_impact_about_counts` 的樣子在 impact 這層另寫一支語意等價、但物理上獨立的「家」查找(第二種做法)。兩條路都撞上 major 錨定的判準,計劃沒有交代要走哪一條、也沒有指出這個矛盾。

引句:「家的定義與比對鍵沿用每支檔有家那一支(同一個函式,不另寫一套)」(`governance/review-reports/推筆記認家/r1-snapshot.md:50`)

佐證 file: `scripts/lumos:17995`(`_nodehome_homes` 簽名要 `side`)、`scripts/lumos:17812`(`_NodehomeSide.__slots__`)、`scripts/lumos:21273`(`_impact_mark_about` docstring「無 git、無子行程」)、`governance/review-reports/推筆記認家/r1-snapshot.md:86`(隱患段講的是另一套快取)

### F2 lands_in 漏列「家」機制真正的定義來源節點
severity: minor
blocking: 否 — 判準:結構本身沒錯(三篇落點都是既有同主題節點,不必另開新篇),只是計劃書裡少記一條「這次改動也依賴/影響 Systems/每支檔有家」的落點連結——屬於命名/記錄跟鄰居慣例不完全一致的層級,不到「引入第二種做法或跨層直呼」的 major 門檻,不足以擋下這份設計本身。

「家」的機械定義、比對鍵、五種違規判定、`about_code` 必填的先例都記在 `Systems/每支檔有家`(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md`)——這篇的 `DEP` 行已經寫明「`scripts/lumos`(判定、指令、健檢三段)」,而且其中一條 KEY 行就是「新開或這次才成為現況的節點沒寫負責範圍…沒寫也擋」,跟 S11 要新增的「regen 節點缺 about_code 就擋」是同一種「必填欄位式」檢查風格的近親。但計劃的落點清單(`r1-snapshot.md:75-79`)只列了 `retrieval-ranking`/`節點還原`/`check-j-regen-guard` 三篇,完全沒提到 `每支檔有家`——即便 S1 明講要重用它的定義、S2/S6 讓 impact 的固定席機制開始依賴它的語意。這篇既是「家」概念的唯一權威來源,這次改動卻不在它的落點清單裡,以後有人查 `每支檔有家` 這篇時看不到「原來 retrieval-ranking 現在也在用我的定義」這條依賴關係——建議補一行落點連結,但不必因此擋下整份設計。

引句:「推筆記那一段(甲):[[Systems/retrieval-ranking]]…SOP 那一段(乙):[[Systems/節點還原]]…lint 那一條(乙):[[Systems/check-j-regen-guard]]」(`governance/review-reports/推筆記認家/r1-snapshot.md:77-79`)

佐證 file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:7-9`(about_code 三檔清單與 DEP 行)、`governance/review-reports/推筆記認家/r1-snapshot.md:75-79`(落點清單)

### F3 S11 要驗的欄位跟 Check J 自己記載的機械範圍(「只掃 summary 行」)對不上
severity: major
blocking: 是 — 判準:規格落點明寫「lint 那一條…regen 章的規則集中在這篇」,而現有 regen 節點檢查全部走同一支共用函式 `check_regen_provenance`(cmd_lint 與 run_doctor 同呼叫,明文防「兩入口規則漂移」)——字面上最可能的接法就是把 S11 塞進這支函式,而不是另開一條全新入口。這樣接下去,等於在一支文件明載「只掃 summary 行」的既有檢查器裡,混進一種全新的驗證方式(frontmatter 欄位存在性檢查),對既有 J-a~J-d 全是「掃 summary 逐行找標記」這一種做法來說,就是引入了第二種做法,落在 major 錨定的判準內。

`check_regen_provenance`(`scripts/lumos:3970`)的 docstring 明寫「只對 frontmatter 帶 regen 的節點生效;非 regen 節點回三空。只掃 summary 行」(`scripts/lumos:3972`),skill 文件把這句話升格成「機械把關的真實範圍(誠實地圖)」的正式陳述:「Check J 只掃 summary 行」(`skills/lumos-project-notes/reference.md:1100`),J-a 到 J-d 全部是對 `summary` 文字逐行做標記解析——這是這支函式從設計起唯一在用的檢查手法。S11 要新增的規則是「regen 節點 `about_code` 至少要有一支檔」——這驗的是 frontmatter 的 `about_code` 清單欄位是否非空,跟「掃 summary 逐行找標記」是不同種類的檢查(欄位存在性 vs. 行級正則比對)。計劃只說「`lumos lint` 對這種節點缺 about_code 報錯」、落點寫「regen 章的規則集中在這篇」,沒有另外交代要開一條獨立入口、也沒有提到要同步改掉 `check_regen_provenance` 的 docstring 與 reference.md 的「誠實地圖」陳述——依現有「同一函式防兩入口漂移」的慣例最可能被直接塞進 `check_regen_provenance`,屆時這支函式與它掛的文件說明會同時變得不準確,而且是在既有單一做法的檢查器裡多長出一種新做法。

引句:「從程式重建的節點 about_code 至少要有一支檔;`lumos lint` 對這種節點缺 about_code 報錯」(`governance/review-reports/推筆記認家/r1-snapshot.md:63`)

佐證 file: `scripts/lumos:3972`(check_regen_provenance docstring「只掃 summary 行」)、`skills/lumos-project-notes/reference.md:1100`(誠實地圖陳述)、`governance/review-reports/推筆記認家/r1-snapshot.md:79`(落點「規則集中在這篇」)

---

總結:最高 severity major,blocking 共 2 條(F1、F3)。
