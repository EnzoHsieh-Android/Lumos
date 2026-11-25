severity: major

第一個非空行已寫檔級嚴重度。鎖檔 `.warming` 不存在(`cat` 回 No such file),所以沒有鎖要處理,也沒刪任何東西。

## 問 1 分層與依賴方向:大致對齊,有一處重複

對齊的部分有三項。
- 快篩結果走 `mg` 物件帶出。`mg.kinds` 的寫法跟既有 `mg.survived`、`mg.streak` 同一種(新碼 file: `scripts/lumos:29136`;既有 file: `scripts/lumos:28902`)。`_ChoiceKillRun.finish` 讀它的方式跟讀 `merge.survived` 一樣(file: `scripts/lumos:79023`)。
- 逐支次數走既有的 hook 列通道。`cmd_guard_kill` 給列打 `_single`(file: `scripts/lumos:28563`),`_KillHooks.note` 轉成列欄位 `single`(file: `scripts/lumos:28708`),`on_row` 數成 `single_runs`(file: `scripts/lumos:79050`)。這跟既有的 `_mtime_unsure`、`_weak_why`、`compile_error` 同一條路,JSON 輸出也把 `_single` 加進剔除清單(file: `scripts/lumos:28619`)。這不是新通道。
- `c.merge_need`、`c.merge_failed` 直接掛在 `c` 這個 SimpleNamespace 上,跟既有的 `c.sh = sh` 同一種做法。`classify` 的 `failed=` 傳出參數,也有 `mt_warned = [False]` 這個既有先例(file: `scripts/lumos:28404`)。
- 沒有跨層直呼。新碼都留在合併快篩那一族(`_kill_merge_*`、`_choice_*`)裡。

不對齊的部分:同一件事「這個平台組為什麼沒合併」,現在有兩個存放處。既有的 `mg.plats[plat] = (啟用, 原因)` 在 file: `scripts/lumos:29090`、`29166`、`29171` 寫入。新的 `mg.off[plat] = why`(file: `scripts/lumos:28923`)是另一份。兩邊的原因詞彙不一樣:`plats` 用「條件不合」「基準」「斷路器」,`off` 用九種固定原因。`plats` 的原因欄位只被寫入,沒有被讀來輸出,所以 `off` 實際上取代了它的功能,卻沒有把 `plats` 的原因欄位拿掉或改成讀 `off`。這條放在問 3 算 major。

## 問 2 命名、錯誤處理、印字、帳欄位:大致對齊,兩處 minor

對齊的部分:
- 標準錯誤印字沿用 `⚠ {_kill_esc(plat)}:…,照逐支跑` 的既有格式(file: `scripts/lumos:29006`、`28926`)。
- 帳欄位命名帶 `merge_` 前綴,跟 `merge_tripped` 一致。
- 型別登記用 `dict.fromkeys(..., (dict,))` 加 `"single_runs": (int,)`,跟既有 `_GOV_FIELD_TYPES` 同形(file: `scripts/lumos:18471`)。
- `_gov_row` 的缺欄預設用 `or {}`、`or 0`,跟既有的 `d.get("judged") or "single"` 同一種處理(file: `scripts/lumos:18564`)。
- `_kill_merge_off` 裡的 `import math` 寫在函式內,跟全檔慣例一致(file: `scripts/lumos:28922`)。
- `_kill_merge_iter` 接住 `_KillHalt` 記「中斷」再丟出去,例外流向跟既有相同。

不對齊的部分有兩條。

**finding B(minor):印字與記帳對同一個原因用了兩套說法,還靠字串前綴當控制流程。**
- `_kill_merge_base` 印字走既有 `_CHOICE_MERGE_BASE_WHY` 換字(file: `scripts/lumos:29006`),記帳卻另外手寫成「合併基準:」加原因,「N 支對不到……」還被特別改寫成「對不到名字」(file: `scripts/lumos:29008`)。
- `_kill_merge_off` 為了不重複印那一行,用字串判斷:`why.startswith("合併基準:") or why == "中斷"` 就直接 return(file: `scripts/lumos:28924`)。鄰居(`_kill_merge_ready`、`_kill_merge_base` 原本)用的是「呼叫端自己決定印不印」,不是靠原因字串的內容分流。
- 另外跳開斷路器那行直接印 `classify` 的原始 `why`(file: `scripts/lumos:29091`),同一批原因字串在合併基準那邊卻是先經 `_CHOICE_MERGE_BASE_WHY` 換字才印。結構對,只是詞彙跟分流方式不一致。

severity: minor
blocking: 否
引句:「if why.startswith("合併基準:") or why == "中斷":」
file: `scripts/lumos:28924`

**finding C(minor):「single」同一個詞在同一族裡有三種意思。**
- 既有的 run 欄位 `single` 是「判法為逐支的壞法數」(file: `scripts/lumos:78975`、`79023`)。
- 新增的 hook 列欄位 `single` 是布林,表示「這一列是逐支真的跑出來的」(file: `scripts/lumos:28708`)。
- 再加上 `single_runs`。
- 讀 `ck` 子字典時,`single` 和 `single_runs` 並排出現,容易混。結構是對的,只是命名重載。

severity: minor
blocking: 否
引句:「p["single_runs"] = p.get("single_runs", 0) + 1」
file: `scripts/lumos:79051`

## 問 3 第二種做法:有一處 major

**finding A(major):新增了第二份「不合併原因」存放處 `mg.off`,既有的 `mg.plats` 原因欄位原樣留著。**
- 既有做法:`mg.plats[平台] = (是否啟用, 原因)` 一個地方記原因。斷路器跳開、條件不合、基準失敗都寫進這裡(file: `scripts/lumos:29090`、`29166`)。
- 新做法:`mg.off[平台] = 原因` 另記一份,詞彙不同(`平台不穩或筆記未提交`、`指令形狀不支援`、`時限不夠` 等九種),並且刻意不含斷路器跳開那種(`_KillMerge` 文件字串明說「啟用的與斷路器跳開的不在裡面」)。
- 後果:同一個平台組在 `_kill_merge_iter` 裡被記兩次,`plats` 記「條件不合」,`off` 記「指令形狀不支援」(file: `scripts/lumos:29166`)。run 事件的 `merge_off` 帳欄位只取 `off`(file: `scripts/lumos:79108`),`plats` 的原因欄位沒人讀。
- 對鄰居的做法是把 `plats` 的原因字串細分到夠用,或讓 `off` 取代 `plats` 的第二欄。現在兩邊並存,正是「另一張原因字串表」。

severity: major
blocking: 是
引句:「self.off, self.unclean, self.last_unclean, self.kinds = {}, {}, {}, {}」
file: `scripts/lumos:28903`

第 3 問其餘各項都對齊:
- 時限估算沿用 `_CHOICE_MERGE_UNIT_SECS` 與 `_CHOICE_MERGE_BUDGET_K`(file: `scripts/lumos:28959`、`29028`),只是把原本的「已量平均」在還沒量到時退回單價,沒有新公式。
- 假 Gradle 是延伸同一支腳本,加 `__mfail__`、`__merge_by__`,跟既有 `__merge__`、`__mark__` 同一種寫法。
- 沒有自創鄰居已有的工具函式。

## 彙總

不對齊共 3 條,其中 major 1 條(finding A)。finding B、C 是 minor。

我沒有判不準、需要交編排者的項目。

主要證據檔:
- `/Users/enzo/harness/lumos-choice-speed2/scripts/lumos`
- `/Users/enzo/harness/lumos-choice-speed2/governance/review-reports/code-選擇點變異加速第二段/r1-snapshot.patch`
