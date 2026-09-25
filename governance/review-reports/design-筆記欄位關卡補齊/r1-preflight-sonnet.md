# 前掃:筆記欄位關卡補齊_計劃

掃的計劃:`docs/lumos-toolchain-knowledge/Projects/筆記欄位關卡補齊_計劃.md`
比對的程式:`scripts/lumos`、`scripts/hooks/pre-commit`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`

## 1. 未定義的詞

### HIT-1:「上線日」全篇沒定義是什麼、怎麼算

計劃原句(逐字,出現於摘要 WHY 行與「做法三」開頭):
> 「新規則再加一道『上線日之後建立的筆記才擋』」
> 「以下都只對『上線日之後建立的筆記』算錯誤、之前的算提醒」

問題:整篇計劃(含條款 S5–S9、S11)反覆用「上線日」當判準,但沒有任何一句說這個日期
1) 是單一寫死常數(像 `scripts/lumos:4855` 的 `_ENUM_CUTOFF = "2026-08-06"`,五條新規則共用一個日期,寫進 code 那天就固定)、
2) 還是照 PRIOR-ART 段引用的「每支檔有家」那套機制——`_nodehome_golive()`(`scripts/lumos:22070`)用 `git log --reverse -S"home check --staged"` 動態搜「守衛第一次被寫進提交前掛鉤」那個提交,對每個消費專案各自算出不同的「上線點」、
3) 還是五條規則各自一個日期(像現有 `_ALIASES_CUTOFF`/`_ENUM_CUTOFF` 各自獨立)。

程式證據:
- `scripts/lumos:21397` `_NODEHOME_GOLIVE_MARK = "home check --staged"` + `scripts/lumos:22070-22088` `_nodehome_golive`:每支檔有家的「上線點」是動態算出來的,不是寫死日期。
- `scripts/lumos:4855-4856` `_ENUM_CUTOFF = "2026-08-06"`:既有 lint 值域規則的 cutoff 是寫死常數。
兩種既有先例形狀完全不同,計劃 PRIOR-ART 段只說「沿用...上線點之前的算舊帳」卻沒說沿用哪一種算法。

建議改成的句子:在「做法三」開頭明講「上線日」的定義來源,例如:「上線日 = 這五條新規則第一次進推送前掛鉤的那個提交(用 `git log -S<標記字串>` 算,跟『每支檔有家』的 `_nodehome_golive` 同一套函式),五條規則共用同一個上線日;如果之後想各自分開上線,要在這裡先說清楚」。

## 2. 壞引用

已逐一開檔核對,以下全部存在、可用,沒有 HIT:
- `lands_in` 引用的三個節點:`Systems/lumos-cli-write.md`、`Systems/lumos-cli-read.md`、`Systems/每支檔有家.md` 都存在。
- `--touched-from`(`scripts/lumos:30349-30352`)、`pp_touched_file`/`_TOUCHED_F`(`scripts/hooks/pre-push:50-62,178-180`)都真的存在且如計劃所述。
- 「每支檔有家」讀提交內容的現成函式 `_nodehome_reader`(`scripts/lumos:21678`)、`_nodehome_list`(`scripts/lumos:21636`,`git ls-files -s`/`git ls-tree`)確實存在,可被提交前 lint 借用。
- `lumos set responsibility`(`scripts/lumos:13564` `cmd_set`,`SCALAR_KEYS` 含 `responsibility`)、`lumos new system --responsibility`(`scripts/lumos:15028,15049-15053`)都存在。
- 「順手修」提到的 Issue 檔 `docs/lumos-toolchain-knowledge/Issues/把自己的推論寫成repo明文寫過.md` 存在,且它的 `about_code` 確實指向一篇 `.md` 筆記路徑(`Projects/中文無空白查詢回退_計劃.md`),不是程式檔——跟計劃描述一致。
- CI 的 `BEFORE`(`github.event.before`)在 push 事件下可用,`.github/workflows/ci.yml:34,38-44,105-111` 已有兩處在用同一個值算範圍,計劃要「CI 改成用推送前的起點算出同一份清單」技術上有現成可抄的樣板。

## 3. 範圍自相矛盾

### HIT-2:golive 判準掛在「筆記建立日」而非「那個欄位/那條決策什麼時候寫進去」,會讓 S7/S8/S9 對舊筆記永久失效

計劃原句(條款 S11,逐字):
> 「若建立日沒填或不是年-月-日,則判『是否上線日之後建立』時應當成之後(從嚴)」

這條把「上線日之後建立」的判斷錨在整篇筆記的 `created` 欄位(單一、寫死、不會再變)。但 S7(決策 valid 值域)、S8(about_code 是否版控存在)、S9(計劃要有 lands_in)三條要抓的違規,其實是「筆記裡的某個子項目」——一條決策、一項 about_code、一個 lands_in 清單——而子項目可以在筆記建立很久之後才被加進去或改壞。

問題:一篇 2026-01-01(上線日之前)建立的舊筆記,就算今天(上線日之後)才被人加進一條 `valid: no` 的爛決策,或加進一項指到磁碟上根本沒進版控的 `about_code`,這篇筆記的 `created` 永遠 < 上線日,S7/S8/S9 對它就永遠只是「提醒」、不會變成「錯誤」——即使這正是「這次碰到、新犯的違規」。這跟計劃「誠實界線」段自己講的方向(擋新違規、舊帳才提醒)矛盾:判準用的是「筆記多老」而不是「這條資料多新」,結果新犯的錯躲在舊筆記底下永遠逃過擋。

程式證據:目前 lint 既有的兩個 cutoff(`_ALIASES_CUTOFF`/`_ENUM_CUTOFF`,`scripts/lumos:4855-4856`)也是同一種「筆記整篇建立日」判準,不是子項目時間戳——所以這不是計劃自己發明的新問題,是沿用既有模式時沒注意到它在 S7/S8/S9 這三條新規則上會失效,跟 S5(status)/S6(日期格式)這種「整篇欄位」規則不同源。

建議改成的句子:在做法三加一句「S5、S6 判『這篇筆記的建立日』;S7、S8、S9 因為抓的是子項目(某條決策/某項 about_code/lands_in 清單本身),改判『這次碰到清單裡有沒有這篇』(用 S1/S2 的碰到清單機制頂上),不再疊用筆記建立日,否則舊筆記加新爛資料永遠只會提醒」。

### HIT-3:S9 的 lands_in 必填範圍(檔名尾碼)跟既有 design-loop 落點閘的範圍(type 欄位)不一致,計劃沒有調和

計劃原句(做法三,逐字):
> 「計劃(專案筆記名稱以『_計劃』結尾)必須有 `lands_in`(現在兩道關都不查)」

程式證據:既有落點閘 `_disposal_landing_step`(`scripts/lumos:17919-17954`)判定「這是不是計劃」的條件是 `str(fields.get("type", "")).strip() != "project"` 且路徑在 `Projects/` 底下(`scripts/lumos:17948-17950`)——完全不看檔名尾碼。repo 裡確實存在 `type: project` 但檔名不是「_計劃」結尾的筆記(例:`docs/lumos-toolchain-knowledge/Projects/TypeSafe-Jev_調研.md`,`type: project`),這篇會被既有落點閘算進「是計劃、要看 lands_in」,但按計劃 S9 的新規則卻因為檔名不是「_計劃」結尾而被排除、永遠不擋。

這不一定是錯(CLAUDE.md 本身也說「計劃一律寫成 `Projects/<主題>_計劃`」,暗示「_調研」這類不算計劃),但計劃文字沒有講清楚:S9 用的「計劃」範圍(檔名尾碼)跟系統裡另一個同名機制(design-loop 落點閘)用的「計劃」範圍(type 欄位)是兩套不同判準,沒有互相對照或解釋為什麼要用不同判法——讀的人會以為兩邊在管同一群筆記。

建議改成的句子:在做法三加一句「S9 用檔名尾碼、不用 type==project,是因為 type==project 還包含『_調研』這類不要求 lands_in 的研究筆記(design-loop 落點閘用 type 判是因為它只在 Projects/ 底下跑、範圍本來就比較寬);兩套判準刻意不同」。

## 4. 機械宣稱驗語意(逐句核對程式碼)

### HIT-4:about_code 寫入驗的是「磁碟上有這支檔」,不是「版本控制裡有這支檔」——跟計劃講的不是同一件事

計劃原句(做法三,逐字):
> 「`about_code`:每一項要是版本控制裡存在的檔(現在只有用指令寫入時驗)」

問題:這句話暗示現在的寫入驗證(`lumos append <節點> about_code <檔>`)已經在檢查「版本控制裡存在」,新規則只是把同一種驗證搬到 lint。但實際讀 `_about_code_path`(`scripts/lumos:13652-13680`)看到的驗證是:
```
target = (root / v).resolve()
...
if not target.is_file():
    return None, (f"「{v}」不是這個 repo 裡的檔案" ...)
```
它檢查的是「這支檔在磁碟上存不存在、是不是檔案」(`Path.is_file()`),完全沒有呼叫 git(不像「每支檔有家」用 `git ls-files -s` / `git ls-tree`,見 `scripts/lumos:21636-21661` `_nodehome_list`)。一支剛建立、還沒 `git add` 的檔(或被 `.gitignore` 排除的檔)今天用 `lumos append about_code` 一樣會通過,但它並不在版本控制裡。

如果 S8 新規則真的照「每支檔有家」的做法用 git 讀取(`git ls-files`/`git ls-tree`)判定「版本控制裡存在」,就會出現:今天 `lumos append` 允許寫入的值,明天 lint 卻把它判成錯誤——兩層驗證語意不一致,而計劃文字把它們寫成同一件事。

建議改成的句子:把做法三那句改成「`about_code`:每一項要是版本控制裡存在的檔(現在寫入時只驗磁碟上存不存在,不驗有沒有進版控——`_about_code_path` 用 `Path.is_file()`,不像每支檔有家用 `git ls-files`;這次順便把寫入驗證也改成查版控,兩層才會一致)」,並在條款裡補一條「S8b:`lumos append about_code` 遇到磁碟有但未進版控的檔要擋」,或者明講「這次故意不動寫入驗證,允許兩層語意不同」。

### 已核對、沒問題的機械宣稱(逐句列出)

- 「提交前 lint 讀磁碟不讀提交內容」:`cmd_lint`(`scripts/lumos:4790`)透過 `env.find(node)` 讀 `env.notes`,而 `Env.__init__`(`scripts/lumos:398-401`)是 `self.notes = load_vault(vault)`——`load_vault` 讀的是磁碟路徑,不接觸 git 索引。Gate L(`scripts/hooks/pre-commit:95-112`)呼叫的就是這個 `lumos lint <節點>`,沒有傳任何 index 內容。→ 屬實。
- 「推送前掛鉤本來就傳碰到清單」:`scripts/hooks/pre-push:178-180` 確實把 `pp_touched_file()` 的結果當 `--touched-from` 傳給 `doctor --ci`。→ 屬實。
- 「`--touched-from` 只影響預告合約那段」:在 `run_doctor`(`scripts/lumos:989-2890`)整個函式體裡搜尋,`touched` 參數只在 `scripts/lumos:2331` 的 `_guard_touches(_gn, env, touched)` 這一行被讀,而那一行在 S15「預告了但還沒做的合約」段落(`scripts/lumos:2310`)裡。→ 屬實,S1/S2 要新增的邏輯目前完全沒有掛上去。
- 「CI 現在不傳碰到清單」:`.github/workflows/ci.yml:97` `python scripts/lumos doctor --ci` 沒有帶 `--touched-from`。→ 屬實,跟摘要①的問題描述一致。
- 「`lumos set responsibility` 現在只有新開節點時要求 10 字」:`_cmd_set_locked`(`scripts/lumos:13569-13593`)對任何 key(含 `responsibility`)都沒有長度檢查;只有 `cmd_new`(`scripts/lumos:15049-15053`)在建節點當下呼叫 `_nodehome_resp_ok`(`_NODEHOME_RESP_MIN_CHARS = 10`,`scripts/lumos:21395,21492`)驗過。→ 屬實。
- 「決策的 valid:現在寫成 no、0 會被當成有效」:所有讀 `valid` 的地方(`scripts/lumos:1816,1981,12276,12288,14486,14660`)都是 `str(d.get("valid","true")).lower() != "false"`——只跟字串 `"false"` 比對,`"no"`、`"0"` 都會被判成「非 false」= 有效。→ 屬實。
- 「日期格式現在只擋加引號」:`cmd_lint` 裡完全沒有對 `created`/`updated`/`date`/`decided`/`ended` 做 `date.fromisoformat` 式格式檢查(`scripts/lumos:4790-5063` 掃過一遍,只有 aliases/enum cutoff 讀 `created` 字串比大小,不驗格式);加引號的擋在 pre-commit 的 Gate 1(`scripts/hooks/pre-commit:64-89`,正則抓 `"YYYY-MM-DD"` 帶引號的寫法)。→ 屬實。
- 「status 現在沒填完全不擋」:`scripts/lumos:4864-4866` 的判斷式是 `if t in _STATUS_ENUM and _st and _st not in _STATUS_ENUM[t]`,`_st` 是空字串時 `and _st` 直接短路,不會報錯。→ 屬實。
- 「決策的 `decided`/`ended` 是真實欄位」:`parse_decisions` docstring(`scripts/lumos:12219`)明寫「content/decided/valid/superseded_by/ended」,`fmt_decision`(`scripts/lumos:12276`)確實讀 `d.get('decided')`。→ 屬實。
- 「CI 拿得到推送前的起點(push 事件)」:`.github/workflows/ci.yml:33-44` 的「這次推送要跑哪個測試範圍」步驟與 `98-120` 的 code-loop 步驟都已經在用 `github.event.before`/`github.sha` 算 diff 範圍,且都明講 `pull_request` 事件沒有 `before`。→ 屬實,跟計劃「沒有碰到清單時(例如 pull request 事件拿不到起點)」的前提一致。

## 統計

- 未定義的詞:1 HIT
- 壞引用:0 HIT(6 項全 MISS)
- 範圍自相矛盾:2 HIT
- 機械宣稱驗語意:1 HIT(另有 9 條逐句核對過、皆屬實/MISS)

**HIT 總數:4**
