severity: major

## F1 抽取器加釘版本解析:回傳形狀變了,但四個既有消費者只交代了一個

severity: major
blocking: 是 —— 未點名的兩個既有消費者仍用二元組拆解讀 `full`,一旦 `_node_code_ref_tokens` 為了帶出釘住的提交而改變回傳形狀,這兩處會在拆解時壞掉或被迫另開一條路徑,等於同一支抽取結果活出兩種形狀

引句:「抽取器的三個新選項預設關閉,refcheck、改檔前推筆記、每支檔有家對不含釘版本寫法的文字抽取結果應與改動前相同;含釘版本寫法的應拆出路徑、行號與提交」

計劃只明確交代 `lumos refcheck`(與設計審引用檢查)要改成消費新的釘版本欄位,但 `_node_code_ref_tokens` 的回傳 `full` 目前是 `(token, line)` 二元組,還有兩個既有呼叫點用同樣的二元組拆解手法讀它,計劃完全沒提到要不要動它們:
- `_nodehome_refs`(每支檔有家算「這篇引用了哪些需要家的檔」的入口)用 `for t, _l in full`
- `_node_code_ref_tokens_all`(`_home_confirmed` 判「確認過的家」用的全文掃描)用 `{t for t, _l in full}`

若照計劃字面「拆出路徑、行號與提交」把 `full` 的每一項從二元組變成三元組,這兩處的二元拆解會直接壞掉(`ValueError: too many values to unpack`)。若為了不驚動它們而改成只在另一個管道(例如新的第三回傳值或另一個 dict)交出釘住的提交,則等於同一段抽取邏輯同時活出「舊二元組給三個舊呼叫點」與「新形狀給 refcheck」兩種樣子——這正是 PRIOR-ART 開頭講的「照名字借」在 r2 已經翻過車的那種借不動,只是這次換了一個新地方發生。計劃的 S9 條款只驗「refcheck、改檔前推筆記、每支檔有家……結果應與改動前相同」,沒有驗這兩個既有呼叫點在「回傳形狀本身改變」之後還能不能正常解出來,是條款層級的漏洞,不只是實作細節。

file: `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:72`
file: `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:23`
file: `scripts/lumos:22611`
file: `scripts/lumos:22612`
file: `scripts/lumos:26421`
file: `scripts/lumos:26422`
file: `scripts/lumos:19887`

## F2 「放行不寫事件」跟這一類閘最像的兩個鄰居的實際寫法不一樣

severity: minor
blocking: 否 —— 只是治理帳的記錄粒度跟同類鄰居不同,不影響擋不擋、不影響資料結構,換成跟鄰居一致的寫法或在計劃裡承認這是刻意的分歧都能收斂

引句:「只有擋下(blocked)與環境變數跳過(skipped-env)寫事件,放行不寫,每次提交都寫一筆會讓治理帳多一堆沒資訊的行」

r2 審查修正紀錄把這條折入的理由寫成「照鄰居(架構對齊)」,但 note-shape 真正同類型的鄰居——同樣是「每次提交/每次推送都自動跑一遍」的閘——實際上都是每次都寫一筆事件,不分過或不過:
- 每支檔有家(`nodehome-check`)在提交前/推送前每次執行都算出 `kind ∈ {blocked, warned, passed}` 再呼叫 `_gate_event_or_warn`,沒有「放行就不寫」這回事
- 受波及合約測試真跑閘(`bound-tests`)一樣是每次 pre-push 都跑,通過時也寫 `kind="green"` 這筆

真正「只在擋下時才寫」的是 `anchor` 這種非逐次觸發的檢查,跟 note-shape 的觸發頻率(每次提交/推送)不是同一類。計劃援引「照鄰居」把「放行不寫」說成貼齊既有慣例,但貼的其實是不同類的鄰居;跟它形狀最像、也是計劃自己在 PRIOR-ART 裡逐項照抄分層與判定邏輯的那個鄰居(每支檔有家),寫法剛好相反。這不影響擋不擋,只是治理帳往後想拿「note-shape 零觸發」之類的統計去跟 nodehome-check/bound-tests 的歷史帳做同類比較時,粒度對不上。

file: `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:46`
file: `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:109`
file: `scripts/lumos:23349`
file: `scripts/lumos:23355`
file: `scripts/lumos:29327`
file: `scripts/lumos:19657`

## 第1問 對齊

分層(判定全在 lumos、hook 只呼叫且只認 rc1)與每支檔有家完全一致,依賴方向沒有反過來(note-shape 依賴既有 helper,不是既有 helper 依賴 note-shape)。

file: `scripts/hooks/pre-commit:124`
file: `scripts/hooks/pre-commit:125`
file: `scripts/hooks/pre-push:236`
file: `scripts/hooks/pre-push:237`

## 第2問 討論(見 F2)

環境變數命名 `LUMOS_SKIP_NOTE_SHAPE`、設定鍵 `note_shape.gate`、`skipped-env` 這個 kind 詞、找不到 git/lumos 時 fail-open 印一句的措辭,都跟既有的 `LUMOS_SKIP_LINT_NEW`/`LUMOS_SKIP_BOUND_TESTS`、`node_home.gate`/`lint_new.gate`、bound-tests 的 `skipped-env`、nodehome 的 fail-open 訊息同一套寫法,命名與錯誤處理本身沒有問題。唯一的不一致是事件要不要每次都寫,見 F2。

file: `scripts/lumos:21479`
file: `scripts/lumos:29215`
file: `scripts/lumos:29219`
file: `scripts/lumos:6586`

## 第3問 討論(見 F1;喚醒檢查部分對齊)

抽取器擴充多數是「加參數」等級的借法,查了程式碼站得住:①上線點兩支函式目前把標記字串寫死成常數 `_NODEHOME_GOLIVE_MARK`,計劃要加的「標記字串參數、預設值維持原樣」是單純加參數,可行;②合併函式目前本來就在內部算出「新行集合」再回傳 `any(...)` 的布林,計劃要拆的「回傳集合本身」只是把已經算好的中間值換個回傳方式,不是另寫邏輯;④「設定從快照讀」這個形狀本身在這個 repo 就是「一閘一份讀取器」的既有慣例(note_lint 的設定讀取器也是照這個形狀開的),另開一份不算引入新做法。抽取器唯一站不住的是釘版本解析那一項,見 F1。

新程式檔喚醒舊引用不該直接借每支檔有家那支函式,這點計劃判斷是對的:每支檔有家的 `foreign-awakened` 用「該篇是不是那支檔的家(ownership)」當排除條件,只認反引號抽取的結果;note-shape 要的排除條件是「有沒有釘版本」,而且要認裸文字,兩者排除條件與抽取基礎都不同,不是同一支函式換個呼叫方式就能用。計劃在 PRIOR-ART 段落結尾也老實把這條列進「新寫、沒有先例的」,沒有假借用之名蓋掉這個事實,這部分對齊。

file: `scripts/lumos:22854`
file: `scripts/lumos:22757`
file: `scripts/lumos:22184`
file: `scripts/lumos:22961`
file: `scripts/lumos:22966`
file: `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:23`

## 第4問 對齊

`lands_in: Systems/筆記內容閘` 開新節點跟這個 repo 既有慣例一致:同一支 `scripts/lumos` 裡,每支檔有家(`每支檔有家.md`)與受波及合約測試真跑閘(`bound-tests-gate.md`)已經是「同一支程式檔、依不同閘各自開一篇 Systems 節點當家」的先例,note-shape 是獨立的新指令、有自己的一串 S1–S12 合約,另開一篇不是重複造輪,是照抄這個既有形狀。

file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:1`
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:1`
file: `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:11`

不對齊共 2 條,其中 major 1 條
