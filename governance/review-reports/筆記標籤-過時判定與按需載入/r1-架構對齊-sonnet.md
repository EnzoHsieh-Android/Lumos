severity: major

本報告由兩份來源對照而成:計劃凍結快照 `/tmp/tags/r1.md`,以及 repo 唯讀副本裡的 `scripts/lumos`、`scripts/hooks/claude/impact-hook.py`。以下 `scripts/lumos` 的行號,都是在副本 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw` 上對的。

## 四問回答

**1. 分層與依賴方向**
- 大體一致。擋與提醒全在 `scripts/lumos` 單檔內,走「讀被檢查版本的設定、取新增行、記治理帳」這條路,跟既有閘同一層。`note_tags.gate` 的 block/warn/off 值域也跟既有的一樣。
- 求值器計劃寫的是沿用既有:回頭條件探針(`scripts/lumos:27913`)、doctor N 段重算、舊句檢查。這點是對齊的。
- 有兩處不確定:
  - 速查表由誰判斷 `note_tags.gate`,可能讓 hook 直讀設定(見 A7)。
  - `⚠` 「計劃轉 done 時擋」是新的擋點(掛在 `lumos set` 的狀態轉換)。我在 `scripts/lumos` 裡找不到既有閘掛在狀態轉換上,所以沒有對照,只能標 ⚠。

**2. 命名與錯誤處理**
- 設定鍵 `note_tags.gate` 跟 `note_shape.gate`、`drift_check.gate`、`note_reread.gate` 同形,這點對齊。
- 不對齊的有:
  - 跳過開關沒命名,也沒提閘名要進 `_KNOWN_GATES`(A6)。
  - 預設值「沒寫=off」是既有閘裡沒有的(A5)。
  - 欄位名 `retire-when-*`、`superseded-by` 跟鄰居拼法不一(A3、A4)。

**3. 第二種做法**
有五處:
- 行內數量語法(A2)。
- 撤除條件欄位家族(A3)。
- 取代鏈(A4)。
- 以設定開關當上線機制(A5)。
- 對 search 既有旗標的語意改用(A8)。

**4. 落點**
- 寫法規則的落點選錯(A1)。
- 新開 `Systems/筆記標籤` 作為欄位語法與求值的新家,這個方向合理。
- search 過濾與 hook 速查表各自該寫進哪篇,計劃沒講(A1、A7)。

## Findings

**A1 落點:新行的形狀規則寫進了不管這件事的節點**
severity: major
blocking: 是——lands_in 把「新寫句子的形狀」放進一篇自己聲明不負責它的節點,這是落點跟既有分工衝突。
引句:「寫法規則只看上線點之後新增的行(沿用 note-shape 的上線點截斷);欄位判過時只看帶欄位的行,而欄位只會出現在新行上。」
- `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md` 的 responsibility 寫明「不負責新寫句子的形狀(筆記內容閘)」。該節點只管存量漂移。
- 本案的 W1 到 W6、各欄位的提交與推送擋、沿用 note-shape 上線點截斷,全是「新增行」的形狀檢查。它們的家是 `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md`。該節點管 note-shape、「範圍裡新寫、終點還在的筆記行」抽取,以及否定現況句提醒。
- 比較合理的分法:
  - 欄位語法與求值寫進新開的 `Systems/筆記標籤`。
  - 新行擋與提醒掛回「筆記內容閘」。
  - 「存量漂移守衛」不改,或只在回頭重讀候選那一小段指路。
- search 過濾(`scripts/lumos:3986` 一帶)與 hook 速查表(`Systems/codex-harness.md`)各有自己的家,計劃沒標。

佐證行 file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:8`
佐證行 file: `scripts/lumos:25618`

**A2 行內 `[count:…]` 是第二套數量語法**
severity: major
blocking: 是——同一個重算器卻開出另一種寫法,等於專案裡兩套標記語法。
引句:「正則寫法跟 doctor N 段的 HTML 註解標記同一個重算器;rtb 試標 count 21 句全判得出、誤報 0,count 加 value 約可覆蓋四成數量句」
- 既有標記是 `<!--lumos:count=N re=… in=…-->`。
- 計劃另造 `[count:N re=… in=…]`,參數順序和分隔都不同。
- 既有重算用的 `_CNT_RE` 是定義在 doctor N 段函式內部的區域變數,沒有可共用的函式。「同一重算器」其實得先抽出共用函式,計劃沒提這個前置工作。
- S4 驗收的是兩種寫法得到同一個數。更少分歧的做法是讓行內欄位直接沿用 `lumos:count` 語法,或把兩邊都收斂成一種。

佐證行 file: `scripts/lumos:2933`
佐證行 file: `scripts/lumos:3017`

**A3 撤除條件欄位家族的命名跟既有條件記號不同**
severity: minor
blocking: 否——結構上沿用探針求值器,只有欄位拼法跟鄰居不一致。
引句:「`[retire-when-file:…]` `[retire-when-symbol:…]` `[retire-when-status:…]`,可加 `[expect:路徑::名稱]`」
- 既有條件記號是 `[when-file/symbol/test/status:…]` 與 `[by:…]`,由 `_PROBE_TOKEN_RE` 認。這個正則只匹配 `when-*|by`,所以 `retire-when-*` 會是它認不得的第三族。
- RULE 的 `[retire:]` 欄位(`_RULE_FIELD_RES`)又是另一族。
- 結果是「撤除」有三種寫法:`[retire:]`、`[retire-when-*]`、REVISIT 後面的 `[when-*]`。
- `[expect:]` 在既有條件文法裡沒有對應。⚠ 我沒有查到既有條件有類似的限定語。
- 計劃自己的原則 3 寫「語法跟回頭條件一致」,這裡跟它不一致。

佐證行 file: `scripts/lumos:27913`
佐證行 file: `scripts/lumos:3277`

**A4 取代鏈引入第三套取代標記與成對檢查**
severity: major
blocking: 是——專案已有兩套「被取代」的表示,本案再開一套並自帶成對求值。
引句:「兩端要成對,只有一端 → 擋;錨可以是合約編號、決策編號或 `[id:]`」
- 既有的取代表示有兩套:
  - decisions 結構鍵 `superseded_by` / `ended` / `replaces`,以及 `_is_forgotten` 讓 search 隱藏節點。
  - RULE 的 `[status:superseded]`。
- 計劃新增 `[supersedes:]` / `[superseded-by:]` / `[id:]` 行內欄位,拼法還是連字號(既有結構鍵是底線)。
- 計劃明說「舊寫法照認」,所以新舊並存,三套同時有效。
- 若要保留,至少該說明它跟 decisions 取代鏈的分工,以及 `[id:]` 怎麼跟 decisions 的 `id` 不衝突。計劃沒寫。

佐證行 file: `scripts/lumos:15852`
佐證行 file: `scripts/lumos:3277`
佐證行 file: `scripts/lumos:3986`

**A5 「沒寫設定=off」加 `lumos init` 寫 block,是第二種上線機制**
severity: major
blocking: 是——既有閘用「上線點截斷」做不溯及既往,本案另用「設定預設 off」當第二種上線點。
引句:「**設定裡沒有這個鍵 = off**,所以既有專案(工具鏈、rtb、其他已接入的)一律不受影響。」
- 既有閘的預設值沒有 off:
  - `note_shape` 與 `drift_check` 預設 block。
  - `note_reread` 與 `old_sentence` 預設 warn。
  - `stack_questions` 預設 all。
- 既有閘的不溯及既往,靠的是 `_NOTE_SHAPE_GOLIVE_MARK`:提交前掛鉤裡出現那串字,才算這道檢查上線,並只看上線後的新增行。計劃一邊說沿用上線點截斷,一邊又加了一層設定開關,而且沒說要新增哪個上線標記字串。
- `lumos init` 目前只寫技術棧骨架(`test_profile`、`symbol_profile`、`run_cmd`),且「既有設定一律不覆寫」。它從沒寫過任何閘的值。「init 寫入 block」是新行為,而且在已有 config.json 的專案不會生效,計劃沒處理這個情況。
- 最小對齊做法:沿用上線點截斷,預設值跟鄰居一樣由閘自己決定;工具鏈自己要降級就在設定寫 warn。

佐證行 file: `scripts/lumos:24875`
佐證行 file: `scripts/lumos:27571`
佐證行 file: `scripts/lumos:29725`
佐證行 file: `scripts/lumos:18671`
佐證行 file: `scripts/lumos:24851`

**A6 跳過開關與閘名登記沒定**
severity: minor
blocking: 否——只是命名與登記缺漏,結構對。
引句:「單次跳過用環境變數(會留帳、CI 照擋,跟 note-shape 的跳過同一套)」
- 既有每道閘各有一個 `LUMOS_SKIP_<閘名>`,只認 `== "1"`,並呼叫 `_gate_event_or_warn(root, <閘名>, "skipped-env", …)`。
- 計劃只說「環境變數」,沒給名字(例如 `LUMOS_SKIP_NOTE_TAGS`)。
- 新閘名沒進 `_KNOWN_GATES` 的話,治理帳會直接拒寫並印警告(`scripts/lumos:1220`),RETIRE-IF 靠「誤報比例從治理帳量」就量不到。計劃沒提這步。
- 擋下訊息的格式(指出哪篇哪行、怎麼跳過)只有 S3 一句,沒對齊既有閘「印出跳過指令」的慣例。

佐證行 file: `scripts/lumos:25777`
佐證行 file: `scripts/lumos:6951`
佐證行 file: `scripts/lumos:1220`

**A7 hook 速查表的判斷點可能讓 hook 直讀設定**
severity: major
⚠
blocking: 是——若 hook 自己去讀 `note_tags.gate`,就跨過「hook 只格式化、內容與開關由 lumos 算」的既有分層;計劃沒說清楚,所以標 ⚠。
引句:「只在專案的 `note_tags.gate` 不是 `off` 時附;沒開的專案看不到,不增加負擔。」
- 既有做法:`build_ranked_context` 的註解寫明「本 hook 只格式化不持有內容」。棧別題單源在 `scripts/lumos` 的 `_STACK_PERF_QUESTIONS`,hook 只依 lumos 輸出的 `stack_questions_applicable` 鍵決定印不印。`stack_questions.gate` 由 lumos 的 `_stack_questions_config` 讀。
- hook 本身只讀 `.lumos/impact.json` 的 `ttl_min`,從沒讀過 `config.json`。
- 合理做法:`lumos impact` 的輸出新增一個鍵(類似 `tag_cheatsheet`),由 lumos 判斷開關並持有六行表,hook 只負責印。
- 這樣 S17 的 `off` 時不附也自然成立。計劃要補一句:誰讀開關、表放在誰手上。

佐證行 file: `scripts/hooks/claude/impact-hook.py:629`
佐證行 file: `scripts/hooks/claude/impact-hook.py:814`
佐證行 file: `scripts/lumos:21559`

**A8 search 既有旗標被賦予第二個意思**
severity: minor
blocking: 否——結構上擴充了既有指令,只是旗標語意從「節點」變成「行」。
引句:「search 應 預設不輸出它,`--include-superseded` 才輸出」
- 現行 `--include-superseded` 的意思是「含已作廢節點」。它在命中確認後以 `_is_forgotten` 整篇隱藏,並把隱藏筆數印到 stderr(`scripts/lumos:3986`、`scripts/lumos:4013`)。
- 計劃用同一個旗標去開關「單行被取代或撤除條件已成立」。同一旗標管兩層,隱藏筆數的提示也沒說會不會計行。
- 新增 `--prefix`、`--about` 沒有撞名。⚠ 我只確認了這兩個旗標目前不存在,沒有查它們跟 `--regex`、`--files-only`、`--top` 的互動規則。
- 建議:要嘛行層另開旗標,要嘛在說明裡寫清楚兩層一起控制,並把行層隱藏數併進現有 stderr 提示。

佐證行 file: `scripts/lumos:40186`
佐證行 file: `scripts/lumos:3986`
佐證行 file: `scripts/lumos:4013`

不對齊共 8 條,其中 major 4 條
