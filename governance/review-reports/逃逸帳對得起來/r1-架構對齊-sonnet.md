severity: minor

## F1 tier 分級「任何一列」跟既有 _loop_anchor_tier 的「第一筆」判準沒對齊,有長出第二套判法的風險
severity: minor
blocking: 否
引句:「審查帳裡這個迴圈任何一列記到的 tier」
file: `scripts/lumos:17905-17908` `_loop_anchor_tier(rounds)`——現有讀法明文取「帳上第一筆帶 tier 的值」,且註解交代了為什麼不用「任一筆」:`# 寫帳那側不擋中途改 tier,改用「任一筆 high」會對一個從沒被派過 high 編制的迴圈要求資安席(r1 邊界 B3)`(scripts/lumos:17906)。這支函式已經被 `loop next` 與處置閘資安席共用。spec 的「任何一列記到的 tier」在 tier 中途被改過的迴圈上,跟既有判法會給出不同答案(既有取第一筆、spec 字面上沒說怎麼在多值時收斂成一個),且沒有提到要不要複用 `_loop_anchor_tier`。這種「同一個問題(這個迴圈的分級是什麼)」在兩處各自寫一套邏輯、又沒有對齊既有判準與其設計理由,是新做法沒對齊鄰居的訊號;不到 major 是因為結構上仍是單純的讀取函式、沒有跨層或另起子系統。

## F2 `--defect-ref none:<理由>` 把撤回理由編碼進值字串前綴,跟既有「理由用獨立旗標」的命名慣例不一樣
severity: minor
blocking: 否
引句:「手動記帳兩個都沒有時,要明寫 `--defect-ref none:<為什麼沒有>`,否則擋下」
file: `scripts/lumos:30812-30826`(`lumos loop escape` 的 `--rule`/`--defect-ref` 旗標定義)與 `scripts/lumos:31203-31206`(`lint-waive` 的 `waive_key` + 獨立 `--note` 理由旗標)。專案裡「值裡填 none 代表沒有對應項」已有先例(`--rule` 允許填 `none`,scripts/lumos:30825 註解「真的沒有對應規則就寫 none」),但那是值本身就是 none、沒有夾帶理由;`lint-waive` 需要理由時是另開一個獨立旗標 `--note`(scripts/lumos:31204),不是把理由塞進被放行的那個值字串裡。spec 這裡新造一種「`none:<自由文字理由>`」的欄位內小型 DSL,讀側還要再切一次冒號分理由,跟現有「無值填 none」與「理由用獨立旗標」這兩條慣例都不完全對得上,屬於命名/形狀上的不一致,結構(擋下→給出可貼指令)本身沒問題。

## 已看,無:
- 第 1 問(分層與依賴方向):`_escape_rows_for`、`_auto_escape`、`_plan_for_loop`、`loop canary-stats`(scripts/lumos:7397、9319、9293、8925)都是頂層函式互相呼叫、不跨層直呼私有細節;spec 把 `loop escape-stats` 放進 `loop` 子指令、readonly、呼叫既有的 `_escape_rows_for`/`_plan_for_loop`,跟 `loop canary-stats` 同形狀(scripts/lumos:30835-30837、31647)。`loop_kind` 推法函式 spec 講明「寫的一側也呼叫它、讀的一側用同一支」,跟 `_loop_anchor_tier` 被 `loop next` 與資安席共用是同一種「單一實作、多處呼叫」的做法。
- 第 2 問(其餘部分):新欄位名 `loop_kind` 採底線分隔小寫值,跟既有 `defect_ref`/`plan_risk` 同款;撤回走「追加一列、不改舊列」跟稽核帳既有的「missed 席 findings 不作廢(d4)」「decisions 用 superseded_by 指向新決策、舊列留著」是同一種只進不出的沖銷哲學(docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:36、44);擋下訊息「擋下:...+可貼指令」的句式與 `cmd_loop_escape` 既有訊息(scripts/lumos:9478、9481、9484)一致。
- 第 3 問(第二種做法):沒發現另起一套已有機制的重做——Wilson 區間是新算式但沒有現成同款可比;撤回沿用既有 append-only 沖銷哲學而非另開新的「刪除/覆寫」路徑;去重統計(`_plan_for_loop`、scope/ 標籤)複用既有讀法(scripts/lumos:4966、9293)。
- 第 4 問(落點):`Systems/loop-convergence-recording` 已經在管 `.escape-log.jsonl` 的自動記(摘要 2026-09-17 兩則 KEY)且姊妹計劃 `Projects/逃逸自動記_計劃` 的 `lands_in` 也是同一篇,落點與既有慣例一致,沒有另開一篇的必要。

不對齊共 2 條,其中 major 0 條。
