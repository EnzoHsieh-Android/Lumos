severity: minor

審查範圍:/tmp/slots/r3.md 凍結稿。對照 repo 是 scratchpad/rw。第 3 輪重點(`--slots` 旗標與格子記號、`[被取代:]`、撤除條件判不了與預算、度量文法、lint 併進第 0 步)我都開檔核對過語意。

整體結論:沒有發現「專案已有同一種做法、設計卻另寫一套」的 major。剩下的是新段落對照既有程式時的銜接不齊,共 8 條 minor。

### 1. 分層與依賴方向
結構對得上,沒有跨層直呼。
- 擋的規則掛在 note-shape 的新增行抽取上。對照 `scripts/lumos:25656`(`_notelines_new`)、`scripts/lumos:26221`(`_ns_check_line` 的呼叫點)。
- 撤除條件交給既有的回頭條件判定,不另寫判定器。對照 `scripts/lumos:29088`(`_drift_probe_check`)、`scripts/lumos:29200`(`_drift_probe_judge`)。
- doctor 的度量直接讀治理帳檔尾、上限 24MB,跟 ledger-growth 段是同一種讀法。對照 `scripts/lumos:2053`。
- 逐提交記掛鉤記號,是在既有的 `_notelines_range_added(mark=…)` 上多記一個記號。對照 `scripts/lumos:25567`。它是擴充,不是第二套。
- 「找不到記號就整段不跑」跟既有「找不到上線點就全查」相反,稿裡明寫為例外。對照 `scripts/lumos:26210`(`_nodehome_clamp_base` 找不到回原 base)。

有三處接點稿裡沒交代,見 R3A3、R3A4、R3A8。

### 2. 命名與錯誤處理
- 跳過開關 `LUMOS_SKIP_NOTE_SHAPE=1` 和 `LUMOS_SKIP_DRIFT_CHECK=1` 的寫法、只認 `1`,跟既有一致。對照 `scripts/lumos:26370`。
- 子開關值 `block|warn|off`、壞值回預設並講一句,跟既有一致。對照 `scripts/lumos:25467`(`_note_shape_config`)、`scripts/lumos:30318`(`_drift_old_sentence_config`)。
- 結構欄位用 `extra={"check":…}` 記帳,跟否定現況句提醒同一種寫法。對照 `scripts/lumos:26476`。
- 不一致的點見 R3A1、R3A2、R3A5、R3A6、R3A7。

### 3. 第二種做法
沒有新增求值器。上線點記號沿用 `git log -S` 找記號的機制。新欄位語法、新前綴、新格子都是專案原本沒有的新能力,不算。
- 唯一接近第二種的,是用掛鉤旗標 `--slots` 決定「開不開」,而既有的閘靠 `.lumos/config.json`。稿裡說明了理由(掛鉤要各專案更新才生效),我不標 major。
- 這個選擇留下的缺口(開關狀態看不見)是 R3A7。
- 相關的 R3A5、R3A6、R3A8 是「宣稱沿用既有、實際銜接處沒說清」,不是另寫一套。

### 4. 落點
- 擋、`--slots` 旗標、掛鉤範本寫進 Systems/筆記內容閘:對。它的 about_code 有 `scripts/lumos`、`scripts/hooks/pre-commit`、`scripts/hooks/pre-push`。
- 推送時撤除條件寫進 Systems/存量漂移守衛:對。它的 responsibility 明寫不管新句子形狀,只管漂移檢查。
- lint、欄位解析、doctor 提醒寫進 Systems/lumos-cli-read:對。`parse_rule_fields` 和 lint 脈絡標記規則的說明都在那篇。
- Systems/lumos-cli-lifecycle:對。範本注入、`lumos update` 的說明在那裡。
- `scripts/templates/graph-discipline.md` 不是程式檔,不需要家,不算缺。
- 建議:Systems/筆記內容閘 的 responsibility 目前只寫「程式行號引用、沒寫來源的現況描述」,收工時要一併改寫,否則範圍寫小了。這條不單獨列為不對齊。

### 不對齊清單

**R3A1**
severity: minor
blocking: 否。稿裡斷言「跟 `decision-add` 印的同一種」,實際並不是;屬宣稱跟程式不符,結構是對的。
引句:「全域決策編號 `節點#dN`(跟 `decision-add` 印的同一種,單寫 `d3` 算寫錯)」
說明:
- CLI 的 `decision-add` 只印局部編號「編號 d2」,回傳的全域編號被丟掉。
- 全域編號內部是 `<rel>#d<N>`,而 `rel` 帶 `.md`。圖譜裡實際寫法也帶 `.md`,例如 `Projects/Codex完全支援_計劃.md#d6`。
- 稿裡的範例 `Projects/新判法_計劃#d2` 沒有 `.md`,是第二種拼法。doctor 查「決策存在」時兩種拼法要有一種正規化。
file: `scripts/lumos:16543`、`scripts/lumos:41865`

**R3A2**
severity: minor
blocking: 否。欄位命名跟同閘鄰居不一致,結構對。
引句:「擋下事件 extra={"check":"slots","lines":條數,"missing":{鍵:次數},"notes":[筆記路徑]}」
說明:
- `_gate_event_build` 把 `extra` 直接併進事件頂層(`ev.update(extra)`)。
- 事件本來就有 `nodes=` 參數放路徑,擋下事件 `_note_shape_report` 已經在用。
- 同一個閘 note-shape 的否定現況句事件,`notes` 是整數。再放一個 `notes: [路徑]` 會讓同閘同名欄位型別不同。
- 另一個閘 nodehome-check 的 `notes` 是路徑清單,又是第三種。
- 建議路徑走 `nodes=`,`extra` 只放 `check`、`lines`、`missing`。
file: `scripts/lumos:1175`、`scripts/lumos:26476`(`notes` 是整數)、`scripts/lumos:25433`(`notes` 是路徑清單)

**R3A3**
severity: minor
blocking: 否。子開關與總開關的關係沒寫,而鄰居(舊句檢查)是寫死的。
引句:「子開關 `drift_check.retire`(`block` 預設 / `warn` / `off`,同 `drift_check.old_sentence` 的寫法)」
說明:
- 既有 `drift_check.old_sentence` 跟 `drift_check.gate` 是「各管各的、互不牽連」,而且預設是 warn,不是 block。
- 舊句檢查 m1 刻意放在另一支函式,不併進 `_drift_check_core`,因為那支也給考試與歷史重放用,併進去會改掉既有噪音基準。
- 稿沒說 `retire` 在 `gate=off` 時還跑不跑。它要「交給回頭條件判定」,而回頭條件在 `gate=off` 時整段跳過。
- 稿也沒說抽取段放在 `_drift_check_core` 內還是像 m1 另開一支。
- 對比 `note_shape.slots` 那段把總開關關係寫得很清楚。
file: `scripts/lumos:30286-30298`、`scripts/lumos:30318`、`scripts/lumos:30372-30410`(`_drift_check_c`,「兩個開關各管各的」)、`scripts/lumos:30454-30458`(m1 另開一支的說明)

**R3A4**
severity: minor
blocking: 否。登記範圍寫小了,結構對。
引句:「新種類登記進 `drift ack` 與種類名稱表」
說明:
- 實際牽動的有 `_DRIFT_KINDS`、`_DRIFT_KIND_NAMES`、`_DRIFT_SCAN_KINDS`(doctor 與 scan 用,m1 靠它排除)、`_DRIFT_FIX_KINDS`。
- 還有改法提示 `_drift_fix_hint`:擋下時每一筆要印一條改法,probe 已有專屬說法。
- 稿沒說新種類要不要進 scan(第 3 步 doctor 說「沿用 `drift scan` 的工作目錄判定」,等於要進)。
- 稿也沒說 `drift fix --kind` 的 choices 怎麼處理。
file: `scripts/lumos:28146-28151`、`scripts/lumos:29453`、`scripts/lumos:29637`、`scripts/lumos:41199`

**R3A5**
severity: minor
blocking: 否。宣稱「同一套」,但沒交代怎麼接,有長出第二個正規化器的風險。
引句:「跟回頭條件同一套條件語法(既有 `_PROBE_KEYS` 四種)與同一個值文法檢查」
說明:
- 既有流程是:`_PROBE_TOKEN_RE` 切出 `[when-鍵:值]`,再做反斜線轉斜線,然後 `_probe_value_err`、`_probe_norm_value`(去 `./`、NFC),最後 `_drift_probe_old` 用正規化後的值比「同一條」。
- 撤除條件的外形是 `[retire:when-file:路徑]`,值是 `when-file:路徑`,不是獨立的 `[when-…]` 標記。
- 不把它包成 `[when-…]` 交給 `_probe_parse`,實作者就得自己再做一次正規化,同一條件在 REVISIT 與 RULE 兩邊可能對不上。
- 稿的 S2、S12 沒有條款釘住「兩邊走同一支 `_probe_parse`」。
file: `scripts/lumos:28505-28507`、`scripts/lumos:28540-28576`(`_probe_value_err`)、`scripts/lumos:28586`(`_probe_norm_value`)、`scripts/lumos:28621`(`_probe_parse`)、`scripts/lumos:29200`(`_drift_probe_old`)

**R3A6**
severity: minor
blocking: 否。「改成呼叫新解析器、不留兩套」跟既有語意有三處對不上,稿沒處理。
引句:「RULE 六個鍵的既有解析(含值被 `]` 截斷的提醒)改成呼叫新的欄位解析器,不留兩套」
說明:
- 重複鍵:`parse_rule_fields` 是「重複出現取最後一個」,新文法是「寫兩次算寫錯(擋)」。lint 舊寫法行改走新解析器後,舊行會多出新的唸法,跟「舊寫法照舊判準」相衝。
- 日期:`_rule_date` 用 `date.fromisoformat`,Python 3.14 接受 `20261001` 和週日期。稿說「只認 YYYY-MM-DD」。兩邊的日期判法會分歧,稿只要求新解析器嚴格。
- `[test:]`:專案已有 `TEST_REF_RE`(`[^\]]+`,遇 `]` 截斷,合約綁測試與規格追蹤在用)。新解析器也要認 `[test:]`(可重複、值可含方括號)。同一欄位兩個解析器,對 `[test:t_x[param]]` 這種值判斷不同。稿只說 RULE 六個鍵走新解析器,沒說 `[test:]` 的對應。
file: `scripts/lumos:3310-3345`、`scripts/lumos:3346`(`_rule_date`)、`scripts/lumos:4195`(`TEST_REF_RE`)

**R3A7**
severity: minor
blocking: 否。doctor 的開關提醒跟既有「關掉要看得見」的先例不齊。
引句:「slots 不是 block 時 doctor 講一句(同既有開關的先例)」
說明:
- 既有 `_note_shape_doctor_lines` 的原則是「新寫的行不會被擋」這件事要看得見。
- 格子規則實際有沒有在跑,取決於掛鉤有沒有 `--slots`,不取決於 `note_shape.slots`。
- 程式上線後到開擋前,每個專案都是「slots=block 預設、實際不跑」。這是最常見的狀態,doctor 卻不講。
- 建議 doctor 偵測掛鉤沒帶 `--slots` 時講一句。這跟 doctor 事後掃描「找不到記號就不跑」是同一個判斷。
file: `scripts/lumos:26277-26288`

**R3A8**
severity: minor
blocking: 否。記號怎麼找的語意沒寫清,上線點可能被意外提前。
引句:「用 `note-shape --staged --slots` 這串當格子自己的上線點記號」
說明:
- 既有上線點是對整支 `scripts/hooks/pre-commit` 檔跑 `git log -S<記號>`,不是只找實際呼叫那一行。
- 這支掛鉤第 227 行的註解本身就寫了 `note-shape --staged` 這串字。
- 所以第 1 步若在註解、說明文字裡先提到 `--slots` 這串(解釋記號用途很自然),格子的上線點就提前到那個提交。「程式上線但沒有任何掛鉤帶 --slots」就不成立。
- 稿該加一條:記號只准出現在實際呼叫行,註解裡改用別的寫法,並用測試釘住。
file: `scripts/lumos:24922-24931`(`_nodehome_golive`)、`scripts/hooks/pre-commit:227`

不對齊共 8 條,其中 major 0 條
