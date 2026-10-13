severity: major

**1. 分層與依賴方向:大致對齊(⚠ 寫入端的定位器沒交代)**

- 對齊的部分:
  - 規格閘接在 `_spec_gate_front` 判門之後。這跟既有做法一致:前段先印判門與擋下清單,有結論就回 rc,不用再往下跑(`scripts/lumos:7727-7757`)。
  - lint 掛 `_lint_new_rules`,每條規則一支 `_nl_rule_*`,擋不擋看 `note_lint.gate`(`scripts/lumos:6840-6845`、`6862`)。`_nl_rule_about_code(env, n)` 已經有拿 `env` 的先例,所以計劃說「正文用既有的 `env_text` 讀」站得住(`scripts/lumos:6875`、`761`)。
  - `--stage` 的新增走 `_pitfalls_stage`,`cmd_pitfalls` 只多一個分支(`scripts/lumos:42891`)。
  - 寫入用 `atomic_write_verify(path, new_lines, key, expected_check)`,嚴格驗證放進 `expected_check` 這個既有的鉤子(`scripts/lumos:19501`),層次不錯。
- 不對齊的部分:計劃只講「讀」的範圍自己掃,沒講「寫」的時候怎麼定位項目。
  - 鄰居的寫入定位器 `decisions_items` 在 `fm_structure(...)` 裡寫死找 `k == "decisions"`(`scripts/lumos:19415-19422`)。
  - 計劃說「改哪行動哪行」。這要有一支項目定位器,可以把 `decisions_items` 加上 key 參數,也可以複製一份。計劃沒選,而且它又明講讀端不沿用既有的結構定位。
  - 讀端範圍跟寫端定位若各算各的,就是常見的「寫入慣例≠讀取保證」缺口。細節併入第 3 問。

**2. 命名與錯誤處理:大致對齊,有兩處不一致**

- 對齊的部分:
  - 指令名 `question-add` / `question-set` 對應 `decision-add` / `decision-supersede`(`scripts/lumos:51330`、`51354`)。
  - 全域編號 `<計劃>#Q<n>` 對應 `<rel>#d<N>`(`scripts/lumos:20482`)。
  - 擋下用 stderr 印「擋下:…」並回 rc 2,對應 dispatcher 的 `except (ValueError, RuntimeError, OSError)`(`scripts/lumos:52377-52434`)。
  - 「現有最大號加 1」對應 `_max_decision_id`(`scripts/lumos:20428`)。
  - 值的引號格式化共用 `_fmt_decision_value` 底下那套 `_yaml_plain_ok` / `_yaml_quote`(`scripts/lumos:20332`、`19216-19238`)。計劃寫的「錯誤訊息的欄位名改成可傳入」,是 `_yaml_quote(v, "決策內容")` 已有的參數,所以這是擴充,不是另起一套。
- 不一致一:`question-set <計劃> Q<n> <鍵>=<值> …` 是專案裡新的參數形狀。
  - 鄰居的形狀:`lumos set` 是 `key value`(`scripts/lumos:19697`);`decision-amend` 是 `--field … --text …`(`scripts/lumos:51336-51340`);`append`/`remove` 是 `key value`,其中 `value` 是 `nargs="+"`(`scripts/lumos:51289`)。
  - 我 grep 過,沒看到別的子命令用 `k=v` 位置參數。
  - 引句:「`lumos question-set <計劃> Q<n> <鍵>=<值> [<鍵>=<值> …]`:一次可改好幾個鍵(例如 `status=已決 decision=#d3`)」
severity: minor
  - blocking: 否
  - 理由站得住一半:原子地改多個鍵,是為了讓「已決必附 decision」這種跨鍵必附條件能一次過。但這是新形狀,計劃應該寫明為什麼不用 `--field/--text` 或多次呼叫。
- 不一致二:計劃沒寫寫入鎖。
  - `cmd_set` / `cmd_append` / `cmd_remove` 都包 `_vault_write_lock`(`scripts/lumos:19697-19700`、`19991-19994`、`20030-20033`),因為它們是讀—改—寫。
  - `cmd_decision_add` 沒包鎖,是 last-write-wins(`scripts/lumos:20439-20483`;`_write_lf` 的註解也承認,`scripts/lumos:19477`)。
  - 計劃只說「寫法照決策紀錄那一套」。`question-set` 是對既有項目的讀—改—寫,照決策那套就等於繼承「沒鎖」。
  - 引句:「寫法照決策紀錄那一套(`cmd_decision_add` 加 `atomic_write_verify`)」
severity: minor
  - blocking: 否
  - 這點判不準,標 ⚠:我不確定「決策那套」指的是要不要鎖,計劃該明講。
- 回碼:`question-add` 回 0 時印全域編號,與 `decision-add` 的 `(rc, id)` 加 print 做法一致。
- 語意:計劃寫的「必附不齊不寫、回 2」,與鄰居用 `ValueError` 加「擋下:」同路。
- lint 閘門:`_nl_rule_decisions` 是「新規則那一路」,走 `note_lint.gate`。決策的結構性錯誤另外在 `cmd_lint` 裡一律報(`scripts/lumos:6677-6680`)。計劃把「清單無法判定」放進可 warn 的那一路,同時規格閘硬擋,兩者不衝突,不列。

**3. 第二種做法:有,而且理由只站一半**

- 計劃自己寫了「借用,不自建新格式」,可是它另寫了嚴格讀法,範圍也自己掃。
  - 引句:「另寫一支嚴格讀法(決策紀錄的讀法 `parse_decisions` 遇到看不懂的行會略過,不能拿來擋關)。範圍自己掃…不沿用既有的結構定位」
  - 既有的開頭欄位清單讀寫有三塊:`parse_decisions`(讀,`scripts/lumos:18106`)、`decisions_items`(定位,`scripts/lumos:19415`)、`atomic_write_verify`(寫入驗證,`scripts/lumos:19501`)。計劃要新增的是第四塊,而且是跟定位器平行的另一套。
- 理由站得住的部分:
  - `parse_decisions` 遇到看不懂的行直接 `i += 1; continue`,不報(`scripts/lumos:18130-18142`)。
  - `fm_structure` 與 `parse_frontmatter` 把「頂格不是鍵:的行」或 tab 行當成區塊結束。它們遇到 tab 開頭或頂格 `- id:` 會靜默放過,擋關用不得(`scripts/lumos:19168-19200`、`522-560`)。
- 站不住的部分:
  - 專案已有處理這個缺口的做法,不是另寫一支讀法。
    - 在指令入口各自擋:`cmd_decision_supersede` / `cmd_decision_reindex` 遇到 0 縮排或 tab 就 `raise ValueError("決策區塊讀不出任何一條,通常是縮排不對…")`(`scripts/lumos:20352-20355`、`20493-20494`)。
    - 用 `parse_frontmatter` 的 `lint` 指紋,配合 `atomic_write_verify` 的 `introduced = set(new_lint) - orig_lint` 把關(`scripts/lumos:19501-19520`)。
  - 所以較對齊的做法是擴充既有那幾支:
    - `decisions_items` 與 `parse_decisions` 加 key 參數,並加一個 `strict` 模式讓它在看不懂時回報,而不是略過。
    - 讀端與寫端共用同一支定位器,這樣「寫入時驗過」與「閘讀到的」是同一份判定。
    - 另開一支嚴格讀法,等於讓 `decisions` 與 `pending_questions` 各有一份「怎麼認清單項」的定義。這些定義日後只要一邊修(例如縮排規則),另一邊就漂移。
  - 計劃也沒寫為什麼不改成擴充,只寫了為什麼不能直接用。
severity: major
  - blocking: 是(實作前要在計劃裡二選一寫明:擴充 `decisions_items` / `parse_decisions` 的 key 與 strict 參數,或把「為什麼必須平行一支」連同寫入端定位器怎麼辦一併寫進〈做法〉)
- 清單項的格式本身不算第二套。
  - 計劃用的 `- id:` 起頭的巢狀清單,與 `decisions` 的 `- content:` 起頭同一種形狀,`parse_decisions` 的 `^(\s*)-\s+([\w-]+):\s*(.*)$` 認得。
  - 值是單行值加 `tests: a, b`(逗號字串),而 `parse_decisions` 的子清單用 YAML 清單。這是欄位內的小差異。
severity: minor
  - blocking: 否
  - 引句:「都是單行值;`tests` 用半形逗號分隔」
- `_KNOWN_FRONTMATTER_KEYS` 補一個鍵,與 `plan_risk`、`lands_in` 等當初的做法一致(`scripts/lumos:6422-6432`),對齊。

**4. 落點:不對齊,兩個 lands_in 都有問題**

- `Systems/情境出題`:
  - 它的 `responsibility` 明寫「不負責〈待決問題〉的資料格式與擋法(改存開頭欄位另案)」(`docs/lumos-toolchain-knowledge/Systems/情境出題.md` 第 5 行)。那篇是量測與需求風險面表內容源的家。
  - 把整套資料格式、讀法、指令寫進去,等於直接違反它自己寫的範圍,除非同一提交把那句改掉。
  - 引句:「lands_in: - Systems/規格閘 - Systems/情境出題」
severity: minor
  - blocking: 是(落點與家的負責範圍互相矛盾;要嘛改家的 responsibility,要嘛換落點)
- `Systems/規格閘`:
  - 它掛著約 20 行 KEY,`responsibility` 寫的是判門、條款句式、綁定、回退節、真跑、相依回歸、風險低放行、`--push-check`,沒有待決問題。
  - 新增的消費端(前段多一道擋)確實屬於它。
  - 但資料格式與指令、嚴格讀法、lint 規則、`--stage` 三個消費端都擠進同一篇,會再養一個巨型節點。
- 較對齊的落點:
  - `Systems/lumos-cli-write`:`question-add` / `question-set` 的家。`decision-add`、`atomic_write_verify` 都寫在這裡,所以這是最像鄰居的位置。
  - `Systems/lumos-cli-read`:lint 的 `_lint_new_rules` 與 `note_lint` 這一路寫在這裡。
  - `Systems/pitfalls-code-loop`:`--stage` 的家。
  - `Systems/規格閘`:只放前段新增的那道擋。
  - 我的核對:這三篇是我用 grep 關鍵字(`decision-add` / `atomic_write_verify` / `pitfalls --stage` / `_lint_new_rules`)對應出來的,沒有逐篇讀完它們的 `responsibility`,各自的負責範圍標 ⚠。
  - 計劃用「資料格式與擋法」當主題另開一篇也行,但現有節點已涵蓋指令與 lint 的家,新開要說明為什麼不寫進它們。
severity: major
  - blocking: 是(因為 CLAUDE.md 鐵則五「改了程式要寫說明就寫進改到那支檔的家」,而這個計劃的 lands_in 沒對到實際改到的幾篇家)

不對齊共 5 條,其中 major 2 條

總結:最嚴重 major;blocking 共 3 條
