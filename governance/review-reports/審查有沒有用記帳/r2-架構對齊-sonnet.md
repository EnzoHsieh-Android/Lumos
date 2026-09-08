severity: major

## 問一:分層與依賴方向

[S1]~[S4] 仍然全部掛在既有的單檔零依賴 CLI(`scripts/lumos`)上:寫側加在 `cmd_canary` 既有的處置帳驗證段落之後,讀側加在 `_loop_status_disposal` 尾端與 `_render_gov_stats` 的新段,沒有新開帳本、沒有新指令、沒有跨檔案的新資料流,跟 r1 的結論一致,r1 折入沒有動到這一層。

這輪特別查了「`_loop_status_disposal` 觀測尾的印法與回放模式跳過」:程式碼裡 `readonly` 這個開關實際擋的是**有寫入副作用**的兩截尾巴——`_roster_tail()`/`_severity_tail()` 各自會 append `roster-alerts.log`,以及 intake 檢查同樣被 `if not readonly and not str(loop_id).startswith("code")` 包住;而「canary(觀測,不進合取): caught X / missed Y」這段是純讀(從 `latest` 直接算,零寫入),寫在 `if not readonly:` 判斷**之外**,恆印,不受回放模式影響。`cmd_loop_replay` docstring 講「唯讀:治理帳零寫入、不跑觀測尾巴」,對照實碼可知這句指的正是那兩截會寫檔的尾巴,不含這段純讀摘要。[S3] 新增的「席位報 N…」那一行同樣是純讀——直接讀帳列裡已存的 `reported`/`self_found_set`/`findings_set`/`refuted_set` 等欄位做算術,沒有任何檔案寫入,跟既有 canary 摘要同一種副作用等級,放進同一段落、不被 readonly 擋是對的,不是漏判回放邊界。

severity: clean
blocking: 否
引句:「不新開帳本(全部加在既有 canary 列與 gov --stats 上)」

file: `scripts/lumos:13802`(`if not readonly: _roster_tail(); _severity_tail()`——只有這兩截與 intake 檢查被 readonly 條件包住,擋的是各自的寫入副作用)

file: `scripts/lumos:563`(`cmd_loop_replay` docstring「唯讀:治理帳零寫入、不跑觀測尾巴」)、`scripts/lumos:13746`(既有 canary 觀測摘要行不在任何 `readonly` 判斷內,恆印——[S3] 新行沿用同一位置合理)

## 問二:命名與錯誤處理

r1 這一席原本記的第三條(`--refuted-set` 沒帶時視同 0、不擋,跟同家 `--folded-set`/`--accepted-set` 的硬擋慣例不一致)已經折入:[S2] 現在寫成「有 `--findings-set` 就必帶 `--refuted-set`」,套用「跟 folded/accepted 同一種硬擋慣例」,把先前那條寬容路徑拿掉,三個手足旗標的驗證嚴格度統一了。

`id=理由` 的「≥4 字且含實字」門檻也不是這輪憑空發明的新標準:專案已有同款判準——`_MANUAL_MIN_CHARS = 4` 配「至少一個實字」的正則,用在 `[manual:]` 標記的驗證上(`≥4 字且至少一個實字(四個標點不算「講了怎麼驗」)`)。[S2] 借的正是這個既有下限,而且比既有 `--accept-reason` 現行的「非空即可」更嚴,是刻意引用了專案裡更嚴格的既有先例,不是各自為政或另訂一套。

`--self-found-set`(選填,⊆ findings-set)的形狀是單純逗號 id 清單,跟它的手足 `--findings-set`/`--folded-set`/`--accepted-set` 同一種「純成員清單」形狀——不是 `--finding-kind`/`--refute-verdict` 那種「id=值」標註旗標。這個差異是語意本來就不同造成的,不是不一致:self-found 只是二元判斷「有沒有在自找清單裡」,不需要每個 id 再帶一個分類值;finding-kind/refute-verdict 是「每個 id 要標一個封閉列舉裡的值」。形狀跟著語意分家,是對的分類,不是命名鬆散。

這一問沒有查到新的或殘留的不對齊。

severity: clean
blocking: 否
引句:「跟 folded/accepted 同一種硬擋慣例」

file: `scripts/lumos:3060`(`_MANUAL_MIN_CHARS = 4`)、`scripts/lumos:4147`(既有「≥4 字且至少一個實字」判準,[S2] 的理由門檻與此同款,且比 `--accept-reason` 現行的非空門檻更嚴)

## 問三:第二種做法

r1 原本這一席記的兩條(自動計數另寫一份解析規則;新值 `resolved` 不在 `_SEV_ORDER` 值域)都折入了。[S1] 現在明寫「專案只准一份 severity 解析 `_report_severities`,不得另寫寬鬆版」,新的「下限守衛」只在既有唯一 parser `_report_severities()` 的回傳值上做衍生統計(扣掉檔序第一個宣告當檔級、排除 clean、數個數),這跟既有 `_severity_check_row` 在同一份 `_decl` 上取 `_rmax = max(...)` 是同一種「同一份 parse 結果、不同統計量」的做法,不是另開一份平行 parser。方向上也跟既有「帳面不得低於報告最高 severity」同構:兩者都只擋「填的比報告少」(低報),不擋「填的比報告多」(高報)——一個是拿 ordinal 值的 max 比、一個是拿宣告行數的 count 比,聚合方式不同但「只守下限、不守上限」的骨架一致,不是第二種做法。`resolved` 也明寫「不引入新值」,值域仍單一來源 `_SEV_ORDER`,兩條都已折清。

但這輪新加的「refuted id 對 intake 子字串驗」是一套沒有沿用專案唯一錨定實作的新機制。專案在同一個問題——「某段文字有沒有出現在另一份文件裡」——上已經燒過一次「兩份實作各自漂移」的教訓,才收斂出 `_quote_norm`(唯一正規化,docstring 明寫「抽取與比對共用這一份——嚴禁第二份實作」)與 `_quote_rows`(quote-check 唯一實作),並且量出「一字引句必然錨得到=紀律被架空」之後把下限訂在 `_QUOTE_MIN_NORM_LEN = 10` 字。[S2] 的做法是「每個駁回 id 要在 intake 檔文字裡出現(子字串),沒有就 rc2」——沒有走 `_quote_norm` 的正規化,也沒有訂任何長度下限;而 id 本身照 spec 自己舉的例子是 `i4`、`i9` 這種 1~2 個字元的短字串,遠低於既有的 10 字下限。這正是專案已經燒過一次、才立下安全門檻的同一個失敗模式:短字串子字串比對幾乎必然巧合命中(intake 檔裡任何日期、行號、編號、路徑片段都可能含 `i4` 這樣的短序列),讓「駁回 id 要對得上 intake」這條防線名存實亡。這不是命名或錯誤處理細節的不一致,是在專案已有唯一實作與明文教訓的地方,另開一條沒有正規化、沒有長度門檻的平行文字錨定路——量級上是第二種做法。

severity: major
blocking: 是
引句:「每個駁回 id 要在 intake 檔文字裡出現(子字串),沒有就 rc2」

file: `scripts/lumos:13409`(`_quote_norm` docstring「唯一正規化…★抽取與比對共用這一份——嚴禁第二份實作★」)、`scripts/lumos:13422`(`_QUOTE_MIN_NORM_LEN = 10`,註解「錨定紀律「引句 ≥10 字」轉機械(r1 否決席:一字引句必然錨得到=紀律被架空)」)——[S2] 的 id 子字串驗既沒有走這份正規化,也沒有訂任何長度下限,而 spec 自己舉例的 id(`i4`/`i9`)遠短於既有下限

不對齊共 1 條,其中 major 1 條
