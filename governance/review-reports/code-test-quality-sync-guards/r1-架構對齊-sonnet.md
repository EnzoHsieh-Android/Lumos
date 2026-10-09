severity: minor

**1. 分層與依賴方向**

跟鄰居一致,沒有跨層直呼。

- `HELP_WHEN` 新增五條,用 `"test-quality scan"` 這種「父 子」鍵,跟 `"code-loop recall-miss"`、`"loop rewrite"` 同形。
  - 查找邏輯 `HELP_WHEN.get(f"{parent} {name}".strip()) or HELP_WHEN.get(name)` 在 `scripts/lumos:49426`,已涵蓋這種鍵。
  - 新增的 `scripts/test_quality.py` 自己的 `add_parser` 只給 `help=`、沒給 `description`,所以 `_fill_help_when`(`if not sp.description`)會補上說明。
- 你問的 `help=` 與 `HELP_WHEN` 並存,是既有做法,不算第二種。
  - `home`、`note-audit`、`drift` 的 `add_parser` 都同時帶 `help=`(`scripts/lumos:50317`、`50332`、`50376`)和 `HELP_WHEN` 條目(`49385`、`49395`、`49399`)。
  - `help=` 給上層清單看,`HELP_WHEN` 灌進 `lumos X --help` 的 description。
- 兩支掛鉤的豁免清單:新增三檔的順序,跟 `scripts/lumos:22331-22332` 的 `_VENDORED_TOOLKIT` 一致(排在 `test_lumos.py` 之後)。兩支掛鉤的註解本來就寫「與 `_VENDORED_TOOLKIT` 同源」,沿用同一寫法。
- `ARCHITECTURE.md` 和 `reference.md` 的指令數都從 84 改 85,三處同步。

**2. 命名與說明文字的寫法**

整體跟鄰居一致,只有一處條目寫法不一致。

- `HELP_WHEN` 的語氣、標點(全形冒號、句號、半形逗號)、長度,都落在 `note-audit`、`drift` 條目的範圍內。
- 新五條都以「情境」開頭(「想知道…」「要留下…」「要證明…」),跟 `"note-audit prepare"` 的「推送前要審…時:」同型。
- 排版:新條目接在 `"skip"` 之後,沒有跟 `"code-loop"` 家族並排。這是純排版,不列。
- ID: SGA-1
severity: minor
  blocking: false
  引句:「`test-layers` `test-quality` scan·capabilities·capture·check 測試品質候選與收證」
  file: `skills/lumos-project-notes/reference.md:107`
  敘述:全覽裡其他帶子指令的條目,寫法是子指令名接一句「用途」,例如 `drift` check·scan·fix·ack·exam 後面接括號說明(`reference.md` 同段),`guard` 用 list/scaffold/…。新條目把分隔符號和用途說明直接接在反引號後面,沒有括號,讀起來像一串名詞。
  這算命名寫法不一致,結構沒問題。

**3. 第二種做法或沒統一的地方**

沒有引入第二種做法,但有兩處「應統一沒統一」。

- ID: SGA-2
severity: minor
  blocking: false
  引句:「-寫測試或接各技術棧的測試品質工具：先讀 [測試品質接入標準](test-quality-standard.md)，再依專案 runner 保存證據。」
  file: `skills/lumos-project-notes/commands/INDEX.md:34`
  敘述:這次為了壓字數上限,直接刪掉 INDEX 裡指向 `test-quality-standard.md` 的那一行,沒有搬到別處。
  - INDEX 九類子檔表的 03 列(`INDEX.md:36` 一帶)「裡面有」仍沒列 `test-quality`。同表其他列,如 `testmap`、`guard`、`drift`,都逐個列出子指令。
  - 只靠 `t_command_index_complete` 掃全部 `commands/*.md` 當語料才過關,INDEX 本身沒有指路。
  - 另一個佐證:`t_command_index_complete` 的子指令檢查只涵蓋 `loop`、`canary` 等八個父指令,沒有 `test-quality`(`scripts/test_lumos.py:8178`),所以守衛不會替它補洞。
- ID: SGA-3
severity: minor
  blocking: false
  引句:「`rel-cascade` `test-layers` `test-quality` scan·capabilities·capture·check 測試品質候選與收證」
  file: `skills/lumos-project-notes/commands/INDEX.md:34`
  敘述:`test-quality` 的分類在兩處不一致。
  - `reference.md` 把它放在「巡檢/治理」。
  - INDEX 的情境分類把測試相關歸「03 寫回圖譜」(「寫／掃測試」列),而同表的 `test-layers` 歸 02。
  - `test-layers` 和 `test-quality` 在全覽裡被排在一起(`test-layers` 後面緊接 `test-quality`),但 INDEX 把它們分在不同子檔。同一組指令兩處歸屬不同,屬於「應統一沒統一」。
  - 判不準哪邊才是正確歸屬,標 ⚠。

另外,`Systems/test-quality-cli.md` 新增的 PITFALL 用「日期+事件」當 `[出處:]`(`2026-10-09 測試品質分支推送前全套`)。同檔其他 PITFALL 的出處多是 `review-reports/…md` 檔名。專案規範範例本來就允許日期+事件(`CLAUDE.md` 的 `[出處:2026-09-30 事故]`),不列。

不對齊共 3 條,其中 major 0 條。
總結最嚴重 severity: minor；blocking: 0
