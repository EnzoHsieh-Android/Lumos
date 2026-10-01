severity: major

我只審設計跟專案既有做法一不一致,不找 bug、不評好壞。對照的是 repo `scratchpad/rw` 裡的 `scripts/lumos`。我也讀了 r1 架構席的報告。

r1 抓的洞多半真的補上了:
- 必有鍵表改成 lint 與擋讀同一張,並用 S11 逐字釘住。
- 事件式撤除條件改用 `when-*` 條件語法,不再另寫一套。
- `by` 改名 `[取代:]`。
- 格子有了自己的上線點。

下面是修訂稿還剩的不齊處,以及補進來的段落新帶出的。

## 1. 分層與依賴方向

大致一致,沒有跨層直呼。
- 擋掛在 `note-shape` 這條路(`scripts/lumos:26369` 的 `LUMOS_SKIP_NOTE_SHAPE`,`scripts/lumos:26440-26500` 的違規報告)。
- 推送時的撤除條件掛在存量漂移檢查,走 `drift_check.gate` 與 `LUMOS_SKIP_DRIFT_CHECK`(`scripts/lumos:30378`)。
- 時間類提醒掛 doctor。這跟既有「事件擋推送、時間只提醒」同向。

有兩處不齊:
- RULE 欄位出現兩套解析器(R2A1)。
- RULE 的過期提醒在 lint 與 doctor 各有一份(R2A2)。

另外,lint 要同時維持新表與舊表(R2A6)。

## 2. 命名與錯誤處理

沿用對了的部分:
- 單次跳過 `LUMOS_SKIP_NOTE_SHAPE=1`、`LUMOS_SKIP_DRIFT_CHECK=1`,只認 `1`。
- 壞值照 block 並講一句,跟 `scripts/lumos:25484` 一致。
- 擋下訊息一次最多印 20 條,跟 `_drift_print_findings`(`scripts/lumos:30355`)一致。

不齊處:
- 治理帳的欄位怎麼記(R2A4)。
- `[取代:]` 的命名與既有 `superseded_by` 不同(R2A5)。
- `when-symbol` 的路徑規則比既有的嚴(R2A7)。

## 3. 第二種做法

- 第二套 RULE 欄位解析器(R2A1)。
- 第二個檢查 RULE 過期的地方(R2A2)。
- 上線點記號的形狀跟既有的不同(R2A3)。

以下不算第二種做法:
- `[retire:when-*]` 外面多包一層 `retire:`,但判定走既有的 `_probe_value_err` 與轉變判定。這是新的抽取段,不是新的求值器。
- 新前綴 SEE、新鍵 `[出處:]` `[因:]` `[根因:]` 等、新的度量與人裁條件,專案原本都沒有,不算。
- 子開關 `note_shape.slots` 的寫法,跟 `note_shape.negation`(`scripts/lumos:26143`)與 `drift_check.old_sentence`(`scripts/lumos:30316`)同型。

## 4. 落點

計劃的 `lands_in` 只列兩篇,而且分配大致對:
- 擋、必有鍵表、上線點、`note_shape.slots` 放《筆記內容閘》。那篇的 `about_code` 已含 `scripts/lumos`、`pre-commit`、`pre-push`,沒問題。
- 推送時的撤除條件放《存量漂移守衛》,也對。

有三塊沒歸宿(R2A8):
- lint 的脈絡標記規則。
- doctor 的取代鏈、度量、人裁、確認週期、SEE 連結提醒。
- 紀律範本與 skill 子檔。

《存量漂移守衛》只管 doctor 的 Z 段,不管 lint 和其餘 doctor 段。我在 `docs/lumos-toolchain-knowledge` 搜 `_CONTEXT_MARKER_RULES`、`context_marker_warnings`、`rule_lifecycle_warnings`,只在 Projects 與 Verification 筆記出現,沒有任何 Systems 節點管它。

---

**R2A1** RULE 欄位出現第二套解析器
severity: major
blocking: 是——專案已有解析 RULE 六個鍵的做法,設計另寫一套同時讀 RULE。但設計沒說舊的是否改成委派新的,所以標 ⚠,請作者說清楚
引句:「新的欄位解析器(認得雙括號、鍵名白名單、空值與重複鍵)」
佐證行 file: `scripts/lumos:3316`(`_RULE_FIELD_RES`,逐鍵一個正則;上方註解記著 2026-09-21 架構席曾把「合併正則加 dict」判成第二種做法)
佐證行 file: `scripts/lumos:3321`(`parse_rule_fields`,RULE 行的欄位解析,重複鍵取最後一個)
佐證行 file: `scripts/lumos:3336`(`rule_field_truncated`,值裡有 `]` 就唸「會被截斷」)
說明:
- 設計的 RULE 必有鍵(`[依據:]` `[since:]` `[retire:]`)由新解析器讀,`rule_lifecycle_warnings` 仍由舊解析器讀。
- 同一行 RULE 用兩套規則切欄位:重複鍵舊的取後者、新的算寫錯;值含 `[[連結]]` 舊的唸截斷、新的合法。
- 新解析器對 WHY、PITFALL、FACT 等新前綴是新能力,不算。對 RULE 六個鍵是重複。
- 應明寫:`parse_rule_fields` 與 `rule_field_truncated` 改成呼叫新解析器,或新解析器只管 RULE 以外的前綴。

**R2A2** RULE 的過期提醒在 lint 與 doctor 各一份
severity: major
blocking: 是——「RULE 超過半年沒確認」「`[until:]` 到期」現在已經有檢查,設計又在 doctor 另開一個
引句:「RULE 超過半年;FACT 超過 `[recheck:]` 或來源預設」
佐證行 file: `scripts/lumos:3318`(`_RULE_CONFIRM_STALE_DAYS = 180`)
佐證行 file: `scripts/lumos:3388`(`rule_lifecycle_warnings` 的 `[until:]` 過期提醒)
佐證行 file: `scripts/lumos:3392`(同函式的 `[confirmed:]` 超過 180 天提醒)
佐證行 file: `scripts/lumos:5428`(lint 呼叫 `context_marker_warnings`,連帶跑上面兩條)
說明:
- 〈格子欄位的過期檢查〉表把 RULE 的 `[confirmed:]` 逾期,以及 `[retire:人裁]` 加 `[until:]` 到期,都掛成 doctor 新提醒。
- 這兩件事 `rule_lifecycle_warnings` 已經在做,設計沒說是否沿用。
- 照字面實作會有兩處各自算半年、各自判到期,常數與訊息容易分歧。
- FACT 的 `[recheck:]` 與來源預設週期是新能力,不算。
- 應明寫:doctor 的 RULE 過期提醒呼叫既有函式與 `_RULE_CONFIRM_STALE_DAYS`,新增的只有 FACT。

**R2A3** 格子上線點的記號形狀跟既有的不同
severity: minor
blocking: 否——上線點機制本身沿用了,只是記號怎麼放沒講清楚。標 ⚠
引句:「提交前掛鉤多一行格子專用的記號(新字串)」
佐證行 file: `scripts/lumos:25443`(`_NOTE_SHAPE_GOLIVE_MARK = "note-shape --staged"`,掛鉤裡真的被呼叫的指令字串)
佐證行 file: `scripts/lumos:28158`(`_DRIFT_GOLIVE_MARK = "drift check"`)
佐證行 file: `scripts/lumos:26504`(`_NOTE_AUDIT_GOLIVE_MARK = "note-audit check"`)
說明:
- 既有每道閘的上線記號,都是掛鉤裡實際執行的指令字串,「有這串」就等於「這道檢查在跑」。
- 格子規則跑在同一個 `note-shape --staged` 裡,沒有自己的指令,所以「多一行記號」只能是註解或額外旗標。
- 設計沒說是哪一種。
- 〈實務隱患〉還說擋要等第 0 步滿 14 天才由人把記號寫進 pre-commit。那是用掛鉤文字開關程式裡的規則,既有閘沒有這種用法,既有閘是掛鉤呼叫了才跑。
- 應明寫記號是旗標(例 `note-shape --staged --slots`)還是註解。若是註解,說明為什麼不沿用「呼叫了才跑」。

**R2A4** 治理帳的格子欄位用說明欄而非結構欄位
severity: minor
blocking: 否——帳的位置對,只是記法跟鄰居不同
引句:「擋下事件的說明欄多記格子違規條數與各鍵缺漏次數」
佐證行 file: `scripts/lumos:26455`(否定現況句的 `hinted` 帳用 `extra={"check":"negation","lines":…,"notes":…}` 記結構欄位)
佐證行 file: `scripts/lumos:26484`(`blocked` 帳目前只有說明字串加 `nodes`)
佐證行 file: `scripts/lumos:26371`(`skipped-env` 帳只記環境變數名,看不出被跳過的提交有沒有格子違規)
說明:
- RETIRE-IF 與 `[retire:度量 …]` 都要從帳裡算次數。
- 既有做法是把可重算的數字放進 `extra`,不塞進說明字串。
- 「各鍵缺漏次數」塞說明欄,之後只能解析中文字串。
- RETIRE-IF 第二句要的「帶格子違規又被單次跳過」,目前的 `skipped-env` 帳看不出來,設計沒補。
- 應改記結構欄位,並說明怎麼分辨格子違規的跳過。

**R2A5** `[取代:]` 命名與既有的翻案欄位不同,而且可作廢的對象變多
severity: minor
blocking: 否——專案已有決策翻案欄位 `superseded_by`,設計新增的是摘要行層級的作廢標記,對象不同,但命名方向與用語沒對齊。標 ⚠
引句:「有 `[status:superseded]` 就必須有 `[取代:[[節點]]或決策編號]`」
佐證行 file: `scripts/lumos:14513`(決策列印 `→ superseded_by`)
佐證行 file: `scripts/lumos:16436`(`decision supersede` 寫 `superseded_by`、`ended`)
佐證行 file: `scripts/lumos:3374`(RULE 的 `[status:superseded]` 目前訊息是「整行刪掉」)
說明:
- 「後來被誰取代」在決策那邊叫 `superseded_by`(英文、被取代者指向取代者),設計叫 `[取代:]`,讀起來像「我取代誰」。
- 例子 `WHY:… [status:superseded] [取代:[[…]]]` 指的是「被誰取代」,方向和字面相反。
- 設計把 `[status:superseded]` 從 RULE 擴到所有前綴。WHY 行被翻案的情形,專案本來有 `decisions:` 加 `superseded_by`,現在變成兩個地方都能記。
- 應說明何時用哪個,或把鍵名改成 `[被取代:]`。

**R2A6** lint 要同時維持新表與舊表
severity: minor
blocking: 否——結構對,但「單一表」的承諾被舊判準削弱。標 ⚠
引句:「舊寫法的行(行首 `[日期 出處]`、自由文字 retire)照舊判準」
佐證行 file: `scripts/lumos:3280`(`_CONTEXT_MARKER_RULES`)
佐證行 file: `scripts/lumos:25907`(`_NOTE_SHAPE_PREFIX_RULES`)
佐證行 file: `scripts/lumos:3399`(`context_marker_warnings(rules=…)`,是現成的換表入口)
說明:
- r1 抓的「兩張表」,修訂稿用 S11「逐字釘住」補了。
- 但舊寫法的行仍要走舊判準,程式裡實際會留新表、舊表兩份規則。
- lint 怎麼判「這一行是新文法」也沒定義。擋只看新增行不需要判,lint 看整篇需要。
- 應說明舊表何時退場,以及判新舊文法的條件。

**R2A7** `when-symbol` 的路徑規則比既有條件嚴
severity: minor
blocking: 否——判定共用,只是同一個條件在兩處的合法寫法不同
引句:「`when-symbol` 必須帶路徑(不做全庫掃符號)」
佐證行 file: `scripts/lumos:28603`(`_probe_named_err`:symbol 或 test 的值可以只寫名稱,有 `::` 才驗路徑)
佐證行 file: `scripts/lumos:28616`(`_probe_parse`)
說明:
- 同一個 `when-symbol:名稱` 在 REVISIT 合法,在 `[retire:…]` 不合法。
- 設計的效能理由可以成立,但〈撤除條件的機器式〉那段列的是 `[retire:when-symbol:路徑::名稱]`,`when-test:測試名` 卻不帶路徑,寬嚴不一。
- 應說明這是刻意的差異並記下為什麼,或兩邊共用同一套驗證。

**R2A8** 計劃的 `lands_in` 漏掉三塊落點
severity: minor
blocking: 否——兩篇的分配本身對,缺的是另外幾塊的家
引句:「3. **doctor 的提醒**:取代鏈、度量、人裁、確認週期、SEE 連結。」
佐證行 file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:6`(`responsibility` 只含 doctor 的 Z 段,不含 lint 與其餘 doctor 段)
佐證行 file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:6`(`responsibility` 管 note-shape 與共用抽取,不含 lint 的脈絡標記規則或 doctor 提醒)
說明:
- 第 1 步「lint 改讀同一張表」、第 3 步的 doctor 提醒,在這兩篇的 `responsibility` 裡都找不到。
- 第 0 步的紀律範本與 skill 子檔、`lumos new` 骨架、算計劃連結的程式,也沒有明列家。
- 這些要嘛併進其中一篇並修改它的 `responsibility`,要嘛另開一篇。
- 依 CLAUDE.md 鐵則五,改到的每支檔要有家。

不對齊共 8 條,其中 major 2 條
