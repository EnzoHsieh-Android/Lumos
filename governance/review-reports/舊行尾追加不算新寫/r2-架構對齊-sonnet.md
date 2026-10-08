severity: major

我只讀了程式與計劃,沒有跑任何東西,也沒有寫檔。以下行號都對 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw` 底下的 `scripts/lumos`。

## 1. 分層與依賴方向

整體對齊,沒有跨層直呼。

- `_notelines_append_pairs` 和 `_notelines_parse_hunks` 放在 `_notelines_*` / `_ns_*` 這一層,由第一層 `_note_shape_eval` 與第二層 `_note_audit_items` 往下呼叫。這跟 `_notelines_new` 被兩層共用的方向相同。file: `scripts/lumos:27178`(`_notelines_parse_added`)、file: `scripts/lumos:28942`(`_note_audit_items`)
- 它往下呼叫的 `_ns_diff`、`_nodehome_cat_blobs_capped`、`_notelines_regions`、`_visible_lines`、`_ns_mainline_refs`,都是同層或更低層既有的工具。其中 `_nodehome_cat_blobs_capped` 在 `scripts/lumos:23735`、`scripts/lumos:41202` 也被別處用。file: `scripts/lumos:26424`
- 容器用「有預設值的參數、只有 `cmd_note_shape` 傳」,跟 `hints` 的傳法一樣。file: `scripts/lumos:28640`(`_ns_negation_prepare`)
- `_gate_event_fit` 放在治理帳那一層(`_gate_event_build` 旁),由 `_drift_m1_ledger` 與 note-shape 往下呼叫,方向正確。file: `scripts/lumos:1147`、file: `scripts/lumos:33705`

## 2. 命名與錯誤處理

- 命名:`_notelines_*` 加 `_NS_APPEND_*` 常數、`check: "append-only"`、`tail_of` 都跟鄰居同一套。file: `scripts/lumos:27521`(`done=False` 的選用尾段)
- 失敗回傳方式(Z2)、帳的欄位與種類命名(Z3、Z4)跟鄰居不一致。

**Z2 配對失敗的回傳方式跟鄰居不同**
severity: minor
blocking: 否 — 結構對,只是失敗出口的寫法跟鄰居不一致
引句:「任何失敗(git 失敗、讀不到、例外)一律回空表(這次全不配對、照今天整行查),另帶一個失敗原因字串給記帳用」
- 鄰居的慣例是 git 失敗回 `None`,由呼叫端 fail-open。file: `scripts/lumos:28266`(`_ns_slots_old_lines` 註明批次讀失敗回 None)、file: `scripts/lumos:27207`(`_ns_git`)。
- 另一個鄰居用旗標,並明寫了為什麼不回 None。file: `scripts/lumos:27400`(`_NotelinesNet.failed`)。
- 例外則由收集器的 try 吞掉,只留類別名字串。file: `scripts/lumos:28640`(`_ns_negation_prepare`)。
- 計劃選「空表加原因字串」,並刻意說呼叫端不分 None 與空表。這在 `_ns_negation_prepare` 有回傳元組的先例,所以只算 minor。
- 計劃的簽名寫 `→ {…}`,內文又說「另帶」原因字串,回傳到底是元組還是字典沒寫清楚,實作前要定。
- 例外在函式內吞掉,跟「例外在收集器的 try 吞」的做法也不同。

**Z3 治理帳欄名和 4 KB 裁法的參數跟 drift 那邊不一致**
severity: minor
blocking: 否 — 欄名與參數形狀對不上,結構沒錯
引句:「把 `_drift_m1_fit` 拆成共用的 `_gate_event_fit`(閘名、要裁的清單欄名當參數」
- 抽共用方向對,消除了重複,不是第二種做法。
- 但 `_drift_m1_fit` 有兩段:先從 `rows` 尾端丟,再把 `nodes` 截到 20,而且記的旗標叫 `rows_truncated`。file: `scripts/lumos:33635`–`scripts/lumos:33650`。
- 計劃的「一個清單欄名」參數表達不了第二段。實作時 drift 那邊要嘛留一份 `nodes` 截斷(同一個預算兩處各裁),要嘛參數做成多段。
- 計劃新帳用 `total` 與 `truncated`,鄰居用 `rows_truncated`。同一個 `_gate_event_fit` 的產出,旗標名應統一。

**Z4 失敗帳另立一個種類,鄰居的做法不是這樣**
severity: minor
blocking: 否 — 記帳方式跟同閘慣例不一致,結構對
引句:「推送模式記一筆種類 `relaxed-failed`」
- 同一道閘的先例有兩種:
  - 提醒類失敗只在 stderr 印一句,不寫帳。file: `scripts/lumos:27960` 附近。
  - drift 用同一個 kind 加 `extra.state` / `extra.error`。file: `scripts/lumos:33690`–`scripts/lumos:33705`。
- repo 裡確實也有 `step-failed`、`escape-auto-failed` 這種 `-failed` 種類,所以不算孤例,只標 minor。
- 新增 `relaxed-failed` 後,`_SLOT_METRIC_KINDS`(file: `scripts/lumos:3759`)計劃只加 `relaxed`,沒說 `relaxed-failed` 要不要進度量名單。

## 3. 第二種做法

**Z1 配對起點是「找主線分岔點」的第三套算法**
severity: major
blocking: 是 — 引入了第二種做法(同一件事在筆記閘周邊並存兩套,本案再加一套)
引句:「HEAD 已在主線上就用 HEAD,否則用 HEAD 與主線的分岔點」
- 專案已有兩套,而且註明要收斂:
  - `_lens_push_base`:`merge-base tip ml[1]`,筆記形狀擋與筆記內容審就用這支。file: `scripts/lumos:38558`–`scripts/lumos:38564`、file: `scripts/lumos:27027`、file: `scripts/lumos:28600`。
  - `_push_range_start`:`merge-base --all` 取最近分岔點,漂移檢查用。file: `scripts/lumos:38657`–`scripts/lumos:38663`。
  - 兩支的說明都寫「並存的理由與收斂路見 Issues/推送前其他閘的範圍在合過主線時會多算」,改規則時先看另一支。file: `scripts/lumos:38535`–`scripts/lumos:38552`、file: `scripts/lumos:38736`–`scripts/lumos:38745`。
- 筆記閘取「已推上去的 upstream」另有 `_ns_mainline_refs` 與 `_ns_exclusions`(`merge-base --is-ancestor tip ref`)。file: `scripts/lumos:27212`–`scripts/lumos:27229`。
- 計劃在 `_notelines_append_pairs` 裡另寫一個條件:起點是主線祖先就用它,否則用 `merge-base`;提交前則是 HEAD 對主線。
  - 這是「主線參照」加上自己的 `merge-base`,第三個變體。
  - 同一次 `note-shape --diff` 執行裡會同時有「範圍起點」(來自 `_lens_push_base`)和「配對起點」兩個基準。
  - 計劃沒說要共用 `_lens_push_base` 的 `merge-base` 那段,也沒把這個新變體登記到那份 Issue 的收斂路。
- 建議:把「起點不在主線就取分岔點」抽成 `_lens_push_base` 與配對共用的一支。至少要在 Issue 和兩支的說明裡加第三個消費者。
- 公平地說:`merge-base` 在 repo 裡散落多處(`scripts/lumos:39713`、`scripts/lumos:40590`、`scripts/lumos:41585` 等),所以這不是新發明主線判定,而是沒走既有的收斂路。

**Z5 diff 解析與 `_ns_diff` 旗標(⚠ 交編排者)**
severity: minor
blocking: 否 — 鄰居本身就有多支讀同一份 diff 的寫法,沒有單一既有做法可對
引句:「兩個解析器之外的另一支被刪行讀法 `_ns_deleted_summary_lines`」
- 計劃把 `_notelines_parse_added` 改成包新的 `_notelines_parse_hunks`,筆記閘內「讀新增行」收斂成一支,方向對。
- 沒收的幾處:
  - `_ns_deleted_summary_lines` 自己讀 `-` 行,仍有 `startswith("---")` 這個洞(內容是 `-- x` 的被刪行會被丟掉)。file: `scripts/lumos:28240`–`scripts/lumos:28262`。
  - 更大圈的 `_diff_added_lines` 同樣有 `+++` / `---` 的洞。file: `scripts/lumos:23944`–`scripts/lumos:23965`。
  - 照 `@@` 計數走的,`_lens_hunks_base_ranges` 已經有(只看標頭,不讀行)。file: `scripts/lumos:38918`。
- 計劃明說不併第三支,理由站得住;「同一族一次掃完」的取捨要交編排者裁。
- 計劃另外說「`_ns_diff` 新旗標讓所有呼叫端的區塊切法跟本機設定無關」,這句偏大。
  - `_ns_deleted_summary_lines` 自己組一份 diff 旗標,不走 `_ns_diff`(file: `scripts/lumos:28245`–`scripts/lumos:28248`),新旗標不會到它那裡。
  - `_renames` 用 `--name-status`,切法不影響結果。file: `scripts/lumos:27274` 附近。
  - 這是已有的旗標組重複,不是本案新增。計劃的措辭要收窄,或讓 `_ns_deleted_summary_lines` 也帶新旗標。
- 內容編號:`tail_of` 跟 `done` 是同一種做法(選用的尾段併進雜湊,範圍進編號),沒有跟既有那支重複。file: `scripts/lumos:27521`–`scripts/lumos:27526`。

## 4. 落點

都放進既有的兩篇,不用另開。`Systems/筆記內容閘` 的 responsibility 已含「兩層共用的新行抽取」與內容編號。file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:6`。

**Z6 兩處說明寫進的家不是程式實際落點**
severity: minor
blocking: 否 — 只是筆記落點偏了,不影響程式結構
引句:「送審標出追加段、分範圍的內容編號、派工詞第 2 版、作者怎麼處理」
- 這句歸在 `Systems/筆記內容審`。但那篇自己寫「新筆記行怎麼抽(…內容編號)是兩層共用的,家在 [[Systems/筆記內容閘]]」。file: `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md:61`。
- 所以 `tail_of` 與分範圍編號的說明應寫進閘。審只放 `appended` 欄位、清單印法、派工詞版本。
- `_drift_m1_fit` 拆成 `_gate_event_fit` 改到的是舊句檢查那支。它的家是 `Systems/存量漂移守衛`,責任明寫含「舊句檢查(m1)」。file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:6`。
- 計劃只列了 `Projects/存量漂移防線_計劃` 與 `Systems/reversibility-governance-ledger`,沒列這篇。依鐵則 5,改到哪支函式就寫進它的家。

不對齊共 6 條,其中 major 1 條
