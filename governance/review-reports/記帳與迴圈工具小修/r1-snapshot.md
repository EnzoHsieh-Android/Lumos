---
type: project
status: doing
created: 2026-10-15
updated: 2026-10-15
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/loop-convergence-recording
  - Systems/pitfalls-code-loop
  - Systems/棧別提問表態閘
  - Systems/design-loop
decisions:
  - content: 分級 standard/high 的迴圈每筆記帳都帶 --round、light 都不帶;寫進去會讓迴圈有的帶有的不帶、或第一筆就選錯格式時,canary record 當場擋;loop next 對全新的 code standard 編號不再給循序(無輪次)範本,舊的全無輪次迴圈照舊
    id: d1
    context: 前端示範照 loop next 的 standard 代碼審範本記了一筆沒輪次的帳,處置帳又必須帶輪次,迴圈混用後 loop next 與處置閘都判不了,只能換編號重記三輪(F23/F24)
    why_chosen: 處置帳必綁輪次之後,無輪次的 standard 代碼審一有發現就判不過,循序形狀對新迴圈只剩坑;真帳 147 個 standard 代碼審 144 個早已每筆帶輪次。不選:①只改 loop next 範本(record 照樣收第一筆無輪次帳,手打的照樣中毒);②處置帳放寬成可不帶輪次(2026-08-26 為關低報繞道才規定必綁,不能重開);③逐條在訊息加提醒(帳撤不掉,提醒在寫完後才看到沒用)
    decided: 2026-10-15
    valid: true
  - content: "--regression-set 只收代碼審;設計審帶這欄就擋,不改成提醒"
    id: d2
    context: 設計審記帳照代碼審習慣帶了 --regression-set none,工具收了也沒提醒;帳撤不掉(F20)
    why_chosen: 讀這欄的只有代碼審修正關卡與代碼審範本,templates.md §3.1 標明僅供 code-loop;擋法照 --finding-source 只給代碼審的既有形狀。不選:收下並提醒(提醒在寫完後才出現,帳已經寫了);為設計審補一套回歸量測(沒有讀者,另案)
    decided: 2026-10-15
    valid: true
---
# 記帳與迴圈工具小修_計劃

> 白話:前端示範(order-web)記審查帳時踩到的一串小坑,最痛的是「照 `loop next` 給的範本記了一筆沒輪次的帳,整個迴圈就判不了、只能換編號重記」。這份把它收成一條規則——**分級 standard/high 的迴圈每筆都帶輪次,寫進去會讓迴圈「有的帶、有的不帶」就當場擋**——再順手修九個「工具沒講清楚」的小地方:`none` 當成 id、設計審收了用不到的欄位、表態證據型別錯看不懂、留痕入帳後沒提醒不能改、pitfalls 判 standard 沒講還要審、拆包審填錯整份、資安包與載體最後記的順序、首輪先排乾再凍結。來源:示範流水帳 F11、F16、F20–F25、F28、F31——這些編號是那次示範編排者自己記的流水帳序號,逐條比對表收在調研筆記 `Projects/Web示範前端缺口_調研`(2026-10-15 寫這份時它在 EnzoHsieh-Android/web-gaps 分支,所以這裡寫路徑、不寫連結)。

REVISIT:[when-file:docs/lumos-toolchain-knowledge/Projects/Web示範前端缺口_調研.md][by:2026-11-15] 那篇合進主線後,把白話段的出處改成 [[ ]] 連結

PRIOR-ART: 全部借既有做法、不新建機制:輪次一致性早就在 `loop next` 與處置閘的讀側擋(「有的帶輪次、有的不帶」),這次照「載體席必須全錨,記帳當下就驗」與 [[Projects/代碼審minor解綁_計劃]]「記帳當下核對、錯了不寫帳」的前例,把同一個條件往前挪到寫帳之前;`none` 等於空集合沿用 `--refuted-set`/`--regression-set` 既有寫法;「只給代碼審」照 `--finding-source` 的既有擋法;提醒文字照工具輸出白話三段式。外部對照:append-only 帳本在寫入端驗格式(事件溯源的 schema 驗證放在寫入端,而不是事後讀時才發現)是通行做法。
RETIRE-IF: 輪次格式寫側擋上線 8 週內,治理帳裡它的擋下事件有 2 次以上是合法流程被誤擋(例如結局帳、舊迴圈補記被擋)——撤回成只提醒;其餘各條提醒若 8 週內示範與真帳仍重犯同一個坑(提醒沒人看),就改成擋或拿掉那條提醒。

## 用詞

- **載體(載體席)**:同一輪審查裡,唯一帶處置清單(`--findings-set`/`--folded-set`/`--accepted-set`)記帳的那一席;其餘席只記嚴重度、條數與報告。處置閘看到同輪兩筆載體就擋。
- **寫側／讀側**:寫側=`canary record` 把一筆寫進審查帳(`docs/.canary-log.jsonl`)之前的檢查;讀側=之後讀帳判定的指令(`loop next`、`loop status --disposal` 處置閘、回放)。帳本只能追加,寫側擋得住的錯,讀側只能事後判不過。
- **佔人數(W)**:分級規定每輪要幾位審查員(`loop next` 印的「這輪要 N 人審」)。名冊上「不算進人數／不佔 W」的席(架構對齊、資安、外家)是額外加派,不抵這個數。
- **載體最後記**:代碼審 minor 解綁(PR #95,2026-10-15 合進主線,單源 [[Projects/代碼審minor解綁_計劃]])加的寫側規則——同一輪已經有帶 `--finding-source` 的載體之後,再記同輪任何一席都擋,因為新報告會讓逐條放行的核對失效;要補只能記下一輪。

## 範圍

- 做:①輪次一條規則(`loop next` 範本、文字輸出、`canary record` 寫側,F23/F24);②集合旗標認 `none`(F16);③`--regression-set` 只收代碼審(F20);④表態證據型別錯講清楚(F21);⑤留痕入帳後提醒不能改(F22);⑥pitfalls 每個分級印要派誰(F25);⑦拆包審的範圍與材料(F28);⑧高風險代碼審的資安包與載體最後記順序(F31);⑨設計審首輪先排乾再凍結(F11);⑩兩份手冊同步。
- 不做:見〈不做〉。

## 做法

### 1. 輪次一條規則(F23、F24)

現況(以程式為準,2026-10-15 在 web-ledger 工作樹重現):
- `cmd_loop_next` 對 code- 迴圈、分級 standard、帳上沒有帶輪次的記錄時把 `seq` 設成真(循序單審,[[Projects/循序codeloop-tier錨定_計劃]] 的設計);`_tpl_flags` 對 `seq` 省略 `--round`,所以**全新的** standard 代碼審第一輪印的 `record_cmd` 與 `disposal_cmd` 都不帶 `--round`。實測 `loop next code-zzz-probe --tier standard --orchestrator claude` 的兩條範本都沒有 `--round`。
- 但 `cmd_canary` 對處置帳(`--findings-set`)硬要 `--round`(「處置帳必須綁 --round 和 --auditor」),所以 `disposal_cmd` 那條範本照抄必被擋;而 `record_cmd` 那條照抄會寫進一筆沒輪次的帳。之後載體加上 `--round` 寫進去,迴圈就變成「有的帶、有的不帶」,`loop next` 與處置閘(`cmd_loop_status` 的 disposal 路徑)都 rc2,帳撤不掉,只能換編號重記。
- 文字輸出只印 `canary_type/record_cmd/scope_cap/cluster_hint/note` 五個鍵,`disposal_cmd` 只在 `--json` 裡看得到——人照文字走,只看得到不帶處置清單的那條。
- 真帳(2026-10-15 數 `docs/.canary-log.jsonl`):定錨 standard 的 code- 迴圈 147 個,144 個每筆都帶輪次,2 個全不帶,1 個混用(`code-兩席相反時端出張力`)。循序不帶輪次的形狀實際上只剩極少數,而且**它記不了處置帳**(處置帳必綁輪次),有發現就過不了處置閘。

做法(一條規則,三處用同一支判法):
- **新增一支判法** `_loop_round_format(rows)` 回 `empty / all / none / mixed`,排除條件跟 `loop next` 現在數 `n_round` 用的一樣(讀 `_loop_records`,規格閘留痕已在讀帳時濾掉)。`cmd_loop_next` 開頭那道「有的帶輪次、有的不帶」守衛改呼叫它(條件與訊息都不變)。處置閘(`cmd_loop_status` 的 disposal 路徑)也有一道條件相同的守衛,但訊息不同(「分不出哪輪是判定輪」),本案不動它(見〈不做〉);寫側擋住之後,新帳不會再走到那道守衛。
- **規則**:分級 standard 或 high 的迴圈(不分代碼審、設計審)每筆都帶 `--round`;light 每筆都不帶。迴圈已經有的格式定死,寫進去會變成 `mixed` 就擋。
- **`loop next`**:`seq` 只留給「帳上已經有記錄、而且全部不帶輪次」的舊循序迴圈(相容,行為不變);**全新編號**(帳上零筆)的 code standard 不再走 `seq`,`record_cmd`、`disposal_cmd` 都帶 `--round r1`。人數照舊取應派名冊(一位審查員,架構對齊不佔人數),上限照舊 3 輪。名冊表 `("code","standard")` 的 `mode` 標籤改成 `single`(一位審查員、帶輪次),只影響 `--json` 的 roster 描述字串。
- **`loop next` 文字輸出**:印的鍵多一個 `disposal_cmd`(只在 JSON 已有它時印),讓人照文字走也看得到處置帳範本帶 `--round`。
- **`canary record` 寫側**(放在既有「載體最後記」那段讀帳之後、寫帳之前,跟它共用同一次 `_loop_records_checked` 讀帳,不多讀一次):
  - 這筆是結局帳(`--outcome`)就跳過整段(結局帳結構上不能帶 `--round`)。
  - 既有列加上這一筆,`_loop_round_format` 會變成 `mixed` → rc2:「擋下:這個審查編號既有的 N 筆都[帶/不帶]輪次,這筆[不帶/帶]——寫進去之後 loop next 和處置閘整個判不了、帳撤不掉,只能換編號重記。照既有格式[補上/拿掉] --round 再記」。
  - 帳上零筆(這是第一筆)時,用這筆的 `--tier` 判:standard/high 而沒帶 `--round` → rc2(「處置帳一定要輪次,第一筆不帶就會毒到整個迴圈」,並印補了 `--round r1` 的同一條指令提示);light 而帶了 `--round` → rc2(鏡像 `loop next` 既有的 light 守衛)。第一筆沒帶 `--tier`、編號又是代碼審(`_roster_kind` 不是 design,看不出種類的照最嚴當代碼審)而沒帶 `--round` → 同樣 rc2,訊息說「代碼審第一筆要帶 --tier 與 --round;照 loop next 印的範本記」。設計審沒帶 `--tier` 的第一筆照舊放行(舊制 legacy 形狀,不溯及)。
  - 有既有列時分級用帳上定錨(`_loop_anchor_tier`),沒定錨就只做 `mixed` 判斷。
  - 擋下照既有做法用 `_gate_event_or_warn(..., "canary", "blocked", "round-format ...", hard=True)` 留擋下事件,RETIRE-IF 數的就是它。
- **手冊**:`skills/lumos-code-loop/SKILL.md` 第 12 行「standard 派一個審查員走循序」改成「standard 派一位審查員加一席架構對齊,每筆記帳都帶 `--round`」,第 29 行「standard 循序只派一位」同步;步驟 6 的指令範例本來就帶 `--round rN`,不動。
- **回應既有決策**:[[Projects/循序codeloop-tier錨定_計劃]] 當初放寬的是「code∧standard∧無輪次」不被 `loop next` 誤擋,範圍刀寫明收斂閘一字不動;那時處置閘還沒取代 panel 閘。現在處置帳必綁輪次,無輪次的 standard 代碼審一有發現就判不過,循序形狀對新迴圈只剩坑。本案不收回舊迴圈的放寬(帳上全無輪次的舊迴圈 `loop next` 照舊走循序樣式),只讓新迴圈不再進這個形狀。
- **跟 [[Issues/代碼審next把新處置帳誤判舊panel]] 的關係**:那張是「帶輪次的新處置帳被 `loop next` 送進退役 panel 閘」;現行 `old_panel` 已用 `_panel_retired_for` 分流。本案讓新 standard 代碼審一律帶輪次,所以要多一條條款確認這條路走得通([S3]);過了就可以順手把那張 Issue 關掉(在實作提交寫回)。

### 2. 集合旗標認 `none`(F16)

現況:`cmd_canary` 的內部函式 `_ids` 只把空字串當空集合;`--accepted-set none` 被當成一個叫 `none` 的 id,接著被「放行清單裡有 id 不在發現清單」擋。真帳已有 5 筆 `folded_set` 裡真的寫進了 `none` 這個 id(舊帳,不動)。

做法:`_ids` 把整串去空白後不分大小寫等於 `none` 的值當成空集合(跟 `--refuted-set`/`--regression-set` 同一個寫法),`--findings-set`/`--folded-set`/`--accepted-set` 一起受益。**行為改變**:`--findings-set none` 現在被當成一個叫 `none` 的發現照收,改了以後等於空集合,會被既有的「--findings-set 不能是空的」擋下(訊息沿用既有那句)。`none` 跟別的 id 混在同一串(`a1,none`)→ rc2「none 表示一條都沒有,不能跟其他 id 寫在一起」。`--regression-set` 那段原本自己判 `none`,改用同一支,行為不變。

### 3. `--regression-set` 只收代碼審(F20)

現況:`--regression-set` 對任何迴圈都收;實際讀這個欄位的只有 `loop fix-check`(代碼審修正關卡,看第 2 輪起的載體有沒有記這欄、沒有就提醒),`loop next` 只是在代碼審範本裡寫出這個旗標、不讀帳上的值;設計審手冊沒要求,`templates.md` §3.1 標明「僅供 code-loop」。真帳設計審也記過 16 筆(9 筆有 id),沒有任何地方讀。

做法:照 `--finding-source` 的既有擋法,`_roster_kind(loop) == "design"` 時帶 `--regression-set` → rc2:「--regression-set 只給代碼審(code- 開頭的迴圈)用——設計審沒有讀它的地方,記了也不會被用到;拿掉再記」。看不出種類的編號照最嚴當代碼審(收)。舊帳不溯及。

### 4. 表態證據型別錯講清楚(F21)

現況:`_dispositions_validate` 與 `_dispositions_tension_shape` 用 `str(ent.get("evidence") or "")`,清單被轉成 `"['a.py:3', …]"` 再拿去切 `path:line`,訊息是「evidence '[…]' 切不開」,看不出是型別錯;`existing` 每一項同樣先 `str()`。

做法:兩支共用一個小判斷——`evidence` 有給但不是字串、或 `existing` 某項不是字串時,直接印「evidence 要是一個字串(path:line 或 test:<名>),你給的是清單;多個證據挑最直接的一個,其餘寫進 reason」(依實際型別講「清單 / 物件 / 數字」),不再往下切。讀側(`code-loop check` 對治理帳重建的紀錄)照舊先過 `_dispositions_tension_shape`,同一句訊息自然帶到。

### 5. 留痕入帳後提醒不能改(F22)

現況:`canary record` 對 `--report`/`--snapshot`/`--intake` 都算 sha256 入帳,但記完什麼都不說;記帳後再改 intake,要到問閘才看到指紋不符。

做法:記帳成功、真的寫進帳之後,只要這筆帶了上述任一份留痕,往 stderr 印一行:「提醒:<列出這筆入帳的留痕檔名> 的指紋已經寫進帳,之後改一個字處置閘就判不過;要更正請另開一份檔(例如 rN-intake-更正.md)寫在卷證裡,不要改這幾份」。不擋、不改帳的內容、不改回傳碼。訊息只印一次(一筆一行),不分迴圈種類。

### 6. pitfalls 每個分級印要派誰(F25)

現況:`_pitfall_tier` 判 standard 時人可讀輸出只印「tier: standard(有程式檔改動、沒命中風險型樣)」(審查帳有全靠人驗的風險低留痕時,括號裡再接一段「跑 lumos spec-gate --push-check 看是不是 light」),沒有任何一句講 standard 仍要審;示範時後端代理讀成「standard 不用審」。

做法:人可讀輸出在 `tier:` 那行下面多印一行「這級仍要代碼審:<該派的席>」,席位清單**從應派名冊 `_TIER_ROSTER[("code", tier)]` 讀**(必派席列名;條件席與 `required-gated` 席照 `loop next` 既有的 `_REQUIREMENT_LABEL` 標示,名冊沒有的字樣這裡不新造),不在 pitfalls 另寫一份;後面接 `lumos loop next code-<編號> --tier <tier> --orchestrator claude` 一行。light 也印(只派一席架構對齊)。`--json` 不動(pre-push 讀 JSON,不加欄位免得動到熱路徑的解析)。

### 7. 拆包審的範圍與材料(F28)

現況:`--scope-lines` 只看自填數字,超過 `_CANARY_SCOPE_SOFT_CAP_LINES`(1800)就在帳上標 `scope_oversize`(弱證據),標了撤不掉;`record_cmd` 只寫 `--scope-lines <這輪審了幾行>`、`--snapshot <凍結快照.md>`,沒講拆包時填該席那一包。派工單 `rN-dispatch.json` 每席有 `materials`,但記帳不讀它。

做法:
- `record_cmd` 的佔位字改成 `--snapshot <這一席審的那份凍結材料(拆包審時填該席那一包)>`、`--scope-lines <這一席那份的行數>`;`disposal_cmd` 同步。
- `canary record` 寫側(留痕路徑正規化之後、寫帳之前):只在**這筆會被標 `scope_oversize`** 時多做一步——找 `governance/review-reports/<編號>/<--round>-dispatch.json`(repo 根底下,照手冊的固定位置;沒帶輪次或檔不在就跳過),讀得懂後找這一席的材料——派工單有兩種既有形狀:多席形狀是 `seats` 清單、每席自帶 `materials`(找 `auditor` 跟這筆 `--auditor` 完全相同的那席);單席形狀只有頂層 `materials`(這時要頂層 `auditor` 或 `seat` 跟 `--auditor` 相同才算這一席的,`seat-check` 既有讀法只讀頂層這一種)。找到的材料非空,而 `--snapshot` 不是其中任一份(比正規化後的路徑或 sha256)→ rc2:「這一席派到的材料是 <materials>,你填的 --snapshot 是另一份(多半是整份);拆包審時 --snapshot 與 --scope-lines 要填這一席那一包,不然帳上會被標成範圍過大、整輪算弱證據」。派工單讀不懂、找不到該席、或 `--snapshot` 就在那席的材料裡 → 照舊只標 `scope_oversize` 並提醒,不擋。
- 既有的超標提醒多一句「拆包審時 --scope-lines 填該席那一包的行數」。
- 資安席的包本來就要含全部改到的檔(見下一節),整份大於 1800 行時它照舊會被標,這是真話,不另開例外。

### 8. 高風險代碼審的資安包與順序(F31)

現況:`loop next` 對 high 代碼審只在應派席印一行「資安…必派(問閘會擋)」;`_disposal_security_step` 要求資安席看過的檔涵蓋判定輪凍結 patch 的全部檔,而且每支檔的改動指紋(`_patch_file_changes` 算的 hunk 內容)要跟資安席那份凍結 patch 裡的相同——之後又改過的檔算沒看過,訊息分「內容跟資安席看的不一樣」與「資安席沒看過」兩種;到問閘才擋。PR #95 加了「載體最後記」:同輪已有帶 `--finding-source` 的載體後,再記同輪任何一席都被擋,要補只能記下一輪——示範時就是因此在上限之後多記一輪。

做法:
- `loop next` 新增一個提示清單 `hints`(JSON 鍵 `hints`,文字輸出每項一行 `  提醒: …`),由一支小函式依「迴圈種類、分級、第幾輪」組出來,第 8、9 節的提示都放這裡,不各自散印。高風險代碼審印兩條:「資安包要含這輪凍結 patch 改到的全部檔(含筆記與文件),不要拆掉;最後一次修補之後要對最新的凍結 patch 再派一次資安」、「記帳順序:資安與其他席先記,帶處置清單(與 `--finding-source`)的載體最後記——載體記了以後同輪不能再補,補資安只能記到下一輪,已到上限要先 `lumos loop cap-decision`」。
- PR #95 的「載體最後記」擋下訊息(`cmd_canary` 裡那段)不動判斷,只在被擋的這筆席名對得上資安席(用既有 `_auditor_matches_slot`)時多印一句「要補的是資安席:記到下一輪 r<N+1>,那一輪只派資安、對最新凍結 patch;已到上限先記 cap-decision」。判斷式與核對流程一字不改,不跟 `_minor_release_check`、`_disposal_minor_release_step` 衝突。

### 9. 設計審首輪先排乾再凍結(F11)

現況:手冊步驟 1–3 寫「先機械排乾(首輪加前掃)→ spec-freeze → 派工」,`loop next` 首輪不提順序;`spec-freeze --out` 遇到已存在而內容不同的快照會拒絕覆寫,凍早了要刪舊快照才能重凍。

做法:
- 第 8 節的 `hints` 對設計審(`_roster_kind` 是 design)、階段 plant-canary 印一條:「順序:先排乾(refcheck、prose-lint、pitfalls --check)再 spec-freeze 凍這輪快照、才派工;凍了以後才修真檔,席位會審到舊版」;第一輪多一句「首輪還要先跑前掃(手冊步驟 2 的四項),前掃排乾之後才凍」。
- `spec-freeze` 的 `out_conflict` 訊息補半句:「這份快照還沒派給任何席的話,刪掉它再凍同一個檔名也可以」。判斷不變。

### 10. 手冊與筆記同步

- `skills/lumos-code-loop/SKILL.md`:第 1 節的 standard 描述(上面)、步驟 6 補一句「`--accepted-set`/`--folded-set` 沒有就寫 none」、步驟 2 補「資安包含全部改到的檔、最後修補後再派、載體最後記」各一句(單源指回本計劃)。
- `skills/lumos-design-loop/SKILL.md`:步驟 1〈準備材料〉已寫「排乾完才在第 3 步凍結快照」,在步驟 3〈派審查員〉開頭補一句「`loop next` 首輪也會提醒先排乾再凍」。
- 圖譜寫回:`Systems/loop-convergence-recording`(輪次一條規則、集合 none、regression-set 只收代碼審、留痕提醒、拆包核對、hints)、`Systems/pitfalls-code-loop`(分級印要派誰)、`Systems/棧別提問表態閘`(證據型別訊息)、`Systems/design-loop`(首輪順序提示)。

## 驗收條款

- [S1] 當全新的 code- 編號以 `loop next --tier standard` 開第一輪時,`record_cmd` 與 `disposal_cmd` 都應帶 `--round r1`。[test: t_loop_next_new_code_standard_emits_round]
- [S2] 當 code- 編號帳上已有記錄而且全部不帶輪次時,`loop next` 應照舊走循序樣式(範本不帶 `--round`、不 rc2)。[test: t_seq_code_std_anchor]
- [S3] 當新的 standard 代碼審每筆都帶輪次、第一輪有一筆處置載體時,`loop next` 應吐下一動作而不 rc2、也不走退役的 panel 閘。[test: t_loop_next_code_standard_round_not_panel]
- [S4] 當 `loop next` 以文字輸出、JSON 裡有 `disposal_cmd` 時,文字輸出應印出 `disposal_cmd` 那一行。[test: t_loop_next_text_prints_disposal_cmd]
- [S5] 當一個迴圈既有的記錄都帶輪次、這筆不帶 `--round` 時,`canary record` 應 rc2、不寫帳,訊息講「既有都帶輪次」與補上 `--round`。[test: t_canary_record_blocks_round_format_mix]
- [S6] 當一個迴圈既有的記錄都不帶輪次、這筆帶了 `--round` 時,`canary record` 應 rc2、不寫帳。[test: t_canary_record_blocks_round_format_mix_reverse]
- [S7] 當迴圈帳上零筆、這筆 `--tier standard` 或 `--tier high` 卻沒帶 `--round` 時,`canary record` 應 rc2、不寫帳,訊息含補上 `--round r1` 的指令。[test: t_canary_record_first_row_needs_round]
- [S8] 當迴圈帳上零筆、這筆 `--tier light` 卻帶了 `--round` 時,`canary record` 應 rc2、不寫帳。[test: t_canary_record_light_first_row_rejects_round]
- [S9] 當 code- 迴圈帳上零筆、這筆沒帶 `--tier` 也沒帶 `--round` 時,`canary record` 應 rc2;設計審同樣形狀應照舊寫帳。[test: t_canary_record_code_first_row_without_tier]
- [S10] 當帶 `--outcome` 的結局帳寫進一個每筆都帶輪次的迴圈時,`canary record` 應照舊寫帳、不被輪次規則擋。[test: t_canary_record_outcome_exempt_round_format]
- [S11] 當輪次規則擋下一筆時,治理帳應多一筆 `canary` 的 `blocked` 事件,說明含 `round-format`。[test: t_canary_record_round_format_blocked_event]
- [S12] 當 `--accepted-set` 或 `--folded-set` 寫 `none`(大小寫不拘)時,應當成空集合處理,帳上該欄是空清單。[test: t_canary_record_set_none_is_empty]
- [S13] 當 `none` 跟其他 id 寫在同一串時,`canary record` 應 rc2、不寫帳。[test: t_canary_record_set_none_mixed_rejected]
- [S14] 當設計審(非 code- 編號)的記帳帶 `--regression-set` 時,`canary record` 應 rc2、不寫帳;code- 編號照舊收。[test: t_canary_record_regression_set_code_only]
- [S15] 當表態檔的 `evidence` 是清單時,`code-loop dispositions` 的錯誤訊息應講「要是一個字串」與實際型別,不出現「切不開」。[test: t_dispositions_evidence_type_error]
- [S16] 當 tension 表態的 `existing` 某一項不是字串時,錯誤訊息應講那一項的型別錯。[test: t_dispositions_existing_item_type_error]
- [S17] 當 `canary record` 帶 `--intake`、`--report` 或 `--snapshot` 而且成功寫帳時,stderr 應印一行「指紋已經寫進帳、更正另開檔」的提醒,回傳碼照舊 0。[test: t_canary_record_fingerprint_reminder]
- [S18] 當 `pitfalls --diff` 判 standard 時,人可讀輸出應在 tier 那行下面印「仍要代碼審」與名冊上的必派席(含架構對齊);`--json` 輸出應跟改之前同一組鍵。[test: t_pitfalls_tier_prints_review_seats]
- [S19] 當記帳 `--scope-lines` 超過軟上限、派工單裡同名席的 materials 不含這筆的 `--snapshot` 時,`canary record` 應 rc2、不寫帳,訊息列出那席的材料。[test: t_canary_record_scope_split_package]
- [S20] 當記帳 `--scope-lines` 超過軟上限、但派工單不存在或 `--snapshot` 就在那席的材料裡時,`canary record` 應照舊寫帳並標 `scope_oversize`。[test: t_canary_record_scope_oversize_without_dispatch]
- [S21] 當 `loop next` 對定錨 high 的代碼審印派工資訊時,應印出「資安包要含全部改到的檔、最後修補後再派」與「載體最後記、之後補資安只能記下一輪」兩條提醒。[test: t_loop_next_high_code_security_hints]
- [S22] 當同輪已有帶 `--finding-source` 的載體、又要記一筆資安席時,擋下訊息應多一句「記到下一輪」與 cap-decision 指引,回傳碼與其他席的擋下訊息照舊。[test: t_canary_record_carrier_last_security_hint]
- [S23] 當 `loop next` 對設計審第一輪印派工資訊時,應印出「先前掃、排乾,才 spec-freeze」的順序提醒;代碼審不印這條。[test: t_loop_next_design_first_round_freeze_order]
- [S24] 當 `spec-freeze --out` 遇到已存在而內容不同的快照時,訊息應多「還沒派給任何席就可以刪掉重凍」半句,回傳碼照舊。[test: t_spec_freeze_out_conflict_hint]
- [S25] 當讀 `skills/lumos-code-loop/SKILL.md` 第 1 節時,standard 的描述應是「一位審查員加一席架構對齊、每筆帶 --round」,不再寫「走循序」。[manual: 讀 skills/lumos-code-loop/SKILL.md 第 1 節與步驟 1 有這句]

## 實作時要跑的子集

- 本案新測試:`python3.14 scripts/test_lumos.py -k round_format`、`-k first_row`、`-k set_none`、`-k regression_set`、`-k dispositions`、`-k fingerprint_reminder`、`-k pitfalls_tier`、`-k scope`、`-k security_hint`、`-k freeze_order`、`-k spec_freeze`。
- 防改壞 PR #95(代碼審 minor 解綁):`-k disposal`、`-k canary_record`、`-k report_normalize`(含 `t_disposal_code_minor_release`、`t_canary_record_finding_source`、`t_report_normalize_items`)。
- 防改壞循序相容與 loop next:`-k seq_`、`-k loop_next`、`-k cap_hint`、`-k retro`。
- 既有測試裡用 `canary record` 寫「code- 編號、`--tier standard`、沒 `--round`」第一筆的,會被新規則擋;實作時逐支看:測的是循序舊帳的改用直接寫帳的測試輔助函式(像 `_seq_rec`)造帳,測的是別的就補 `--round`。不准為了讓舊測試過而放寬規則。

## 實務隱患

- 守衛面:**會碰**。`canary record` 新增四種擋(輪次格式、`none` 混寫、設計審帶 `--regression-set`、拆包材料對不上),`loop next` 改範本與輸出。帳本只進不出,寫側擋錯的代價是「這筆記不上、照訊息改了再記」,比現在「記上了、整個迴圈作廢換編號」輕;誤擋面最可能在結局帳與舊循序迴圈,兩者都有條款釘住([S2]、[S10])。這也回應否決清單裡「`loop next` 屬守衛面,一行提示就要整套設計審」([[Projects/否決提案收齊查重_計劃]]):本案接受走設計審,不主張小改動跳過。
- 相容:舊帳一律不溯及;全無輪次的舊循序迴圈照舊可以繼續記(不帶輪次);帳上已經混用的迴圈本來就判不了,這次不修(換編號是唯一路)。
- 範圍外影響:新 standard 代碼審一律帶輪次後,會落進「多席格式」的那幾個功能——跑滿上限提示與跑滿回顧([[Projects/審查跑滿上限提示_計劃]]、[[Projects/審查跑滿回顧_計劃]] 都排除「循序單審」)。真帳 144/147 個 standard 代碼審早就帶輪次,等於已經在範圍內,實際行為不變;實作時用 `-k cap_hint`、`-k retro` 確認。
- 效能:寫側只多用既有那一次讀帳(跟「載體最後記」共用),拆包核對只在超標時讀一份派工單;不碰 pre-push 熱路徑(`pitfalls --json` 不變)。
- 併發:單人、AI 依序操作(專案威脅模型),不處理兩個會談同時記同一個編號。
- 中英文:訊息只出中文;`none` 判斷不分大小寫。
- 已排除:金流:不碰任何付款、點數或計費。
- 已排除:對外送出:只改本機指令的檢查與輸出,不寄信、不呼叫外部系統。
- 已排除:不可逆:新規則只會讓帳少寫錯的筆,不刪不改既有帳;還原提交即可退回。

## 不做

- 不修帳上已經混用輪次的迴圈(帳只進不出,換編號重記)。
- 不收回舊循序迴圈的放寬,也不讓 `loop next` 把舊循序迴圈導去帶輪次。
- 不改處置閘(含它自己那道「有的帶輪次、有的不帶」守衛的條件與訊息)、`_minor_release_check`、`_disposal_minor_release_step` 與「載體最後記」的判斷式;「載體最後記」只多一句提示文字。
- 不從派工單自動填 `--scope-lines`/`--snapshot`(派工單形狀各家不一,只在超標時核對)。
- 不改 `loop next` 對結局帳列的計數(結局帳寫進帶輪次的迴圈後 `loop next` 會判混用,是既有行為;本案只確保寫側不擋它)。
- 不對設計審補一套「修補造成的回歸」欄位;要量設計審的回歸另案。
- 不提供跳過新規則的旗標。

## 回退

- 各節獨立;輪次規則若誤擋,先還原 `cmd_canary` 寫側那一段(`loop next` 範本可保留,帶輪次本來就合法),其餘提示性改動還原提交即可。
- 帳本沒有被改寫,回退不用動帳。

## 合約候選

- (可空)輪次規則穩定一段時間後,可考慮把「standard/high 迴圈每筆帶輪次、寫進去會混用就擋」升成 `Systems/loop-convergence-recording` 的合約行並綁 [S5]、[S7] 的測試;現在不標。

## 審計修正紀錄

