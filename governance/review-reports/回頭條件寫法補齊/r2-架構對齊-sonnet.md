severity: minor

總評:第 1 輪的 major(第三套「關掉提醒」)這版已用分工說明、`drift ack` 拒收已結案行處理;存量清單改放 Z 段、實字計數抽共用、死參數拿掉、WHY 分兩篇,都跟既有做法對齊。這輪沒有跨層直呼,也沒有新增第二套判定。剩下的都是銜接處的不一致(minor),其中一條(Z4)會讓 RETIRE-IF 量不到。

## 逐問回答

1. 分層與依賴方向:對齊。新判定 `_revisit_misplaced` 建在 `_revisit_split` 之上,由第一層(`_ns_revisit_violations`)與 `_probe_lines`(doctor Z 段)共用,跟既有「這行是不是 REVISIT 只有一支判定、各層共用」同一方向(scripts/lumos:31700、27915、31843;Systems/存量漂移守衛.md:97)。`_revisit_lines` 排除已結案、`_probe_lines` 在抽取層跳過已結案,跟 `_retire_lines` 在抽取層跳過 `[status:superseded]` 是同一個模式(scripts/lumos:31866-31880)。沒有跨層直呼。
2. 命名與錯誤處理:規則名「回頭條件寫在句中」「結案標記寫錯」與鄰居「回頭條件格式不合」「條件寫錯」「條件寫在不評估的地方」同型(scripts/lumos:27925-27937);整行層級不扣符合 Systems/筆記內容閘.md 既有規矩(新規則預設整行層級)。不一致處見 Z2、Z3、Z4。
3. 第二種做法:`[closed:]` 與 `drift ack`、`[status:superseded]` 的重疊已被分工說明化解大半,見 Z1(殘留,minor ⚠);另有同一個 token 兩支解析的疑慮,見 Z2。
4. 落點:對齊。`_ns_revisit_violations` 的 WHY 本來就在 Systems/筆記內容閘.md(「新寫的 REVISIT 行也在這一層擋」那條),E5、Z 段、`_retire_lines` 的 WHY 在 Systems/存量漂移守衛.md(「回頭條件(乙)」與 retire 兩條);計劃的兩篇分工正是各自鄰居所在,不需另開。

## Findings

**Z1 結案標記與 drift ack 在條件式上仍有兩個入口,判準靠作者自判**
severity: minor
⚠
blocking: 否 — 計劃已寫明分工與 `drift ack` 拒收已結案行,結構上不是不知情的第二套;判不準的是「待辦還要做」與「不用再回頭」兩者邊界是否機械可分,最終取捨交判定者。
引句:「條件式的判準:**待辦還要做或還要留著提醒** → `drift ack`;**不用再回頭了** → `[closed:]`。」
對照 file: scripts/lumos:32715(`cmd_drift_ack`,表態檔)、scripts/lumos:31866-31880(`_retire_lines` 跳過已標作廢)、scripts/lumos:28512(`_ns_superseded`)。
補充(同一條的小尾巴):`cmd_drift_ack` 對 `--kind probe` 目前不驗那一行是不是現行發現(只有 c2、c3 走 `_drift_current_finding`,scripts/lumos:32754 附近;m1 的 docstring 也寫明「不驗」),`--kind retire` 對已標 `superseded` 的行也沒有拒收。本案只替 probe 加「已結案就拒收」,是第一個「對特定行狀態拒收」的 probe 預檢,跟 retire 的待遇不對稱;做法本身沒錯(retire 有行號形狀預檢 scripts/lumos:32733 可作先例),但建議在計劃寫一句為什麼 retire 的已作廢行不比照。

**Z2 `[closed:]` 的解析在計劃裡有兩處,而且碰到的既有常數計劃沒列**
severity: minor
blocking: 否 — 結構方向對,但兩支解析同一 token 會漂移。
引句:「`_probe_parse` 的連續標記多認一個鍵 `closed`」
對照 file: scripts/lumos:31694(`_PROBE_TOKEN_RE` 鍵集寫死 `when-*|by`)、scripts/lumos:31697(`_PROBE_LEAD_RE` 同)、scripts/lumos:31732(`_revisit_lines` 用 `_PROBE_LEAD_RE` 切掉開頭標記取摘要)、scripts/lumos:31804(`_probe_parse`)、scripts/lumos:27927-27935(條件式的錯誤併成「條件寫錯」)。
說明:
- 計劃同時有 `_probe_parse` 多認 `closed`(條件式)與獨立的 `_revisit_closed(probe)`(日期式與條件式都處理),同一個標記兩處解析。條件式若 `_probe_parse` 把 closed 的錯誤放進 `errs`,第一層會經 27933 報「條件寫錯」,同時 `_revisit_closed` 的 `errs` 又報「結案標記寫錯」,同一個錯兩條規則名;日期式只會報後者。規則名依日期式或條件式而異,跟鄰居「一種錯一個規則名」不一致。
- 計劃只提 `_probe_parse`,沒提 `_PROBE_TOKEN_RE`、`_PROBE_LEAD_RE` 的鍵集要跟著改;不改的話 `_probe_parse` 吃不到 closed,且 `_revisit_lines` 的摘要會把 `[closed:…]` 當摘要字。
- 建議:條件式只在 `_probe_parse` 認 closed(擴兩個正則的鍵集、`errs` 照既有流到「條件寫錯」),日期式才用獨立小函式;或反過來全部走 `_revisit_closed`、`_probe_parse` 遇到 closed 只略過不驗。總之一個 token 一支解析、一個規則名。

**Z3 句中 REVISIT 放進 `_probe_lines` 的 `dead` 清單,會跟既有「寫在不評估的地方」那一行重複計數**
severity: minor
blocking: 否 — 呈現位置的銜接不一致,結構(放 Z 段)是對的。
引句:「`_probe_lines` 回傳的「寫在不評估的地方」清單多收一種「REVISIT 寫在句中」」
對照 file: scripts/lumos:34806-34815(`_drift_doctor_lines` 把 `dead` 的長度全數記進第一行「寫在不評估的地方 N 處」,`n_dead += len(dead)`)、scripts/lumos:31843-31863(`_probe_lines` docstring 與回傳都是「條件式回頭條件」,`dead` 裡的原因字串是條件標記專用)。
說明:
- 若句中 REVISIT 進同一個 `dead`,既有那一行會把它也算進「寫在不評估的地方 N 處」(而且觸發 `if n_rows or n_dead`),計劃又要另起一行,同一處被唸兩次;S5 的「沒有任何 Z 段發現時整段不印」也會被這個計數干擾。
- `dead` 的語意是「條件標記寫在不評估的地方」;日期式的句中 REVISIT 沒有條件標記,不屬於這個語意,硬塞會讓函式名與 docstring 的「條件式」變得名不符實。
- 建議:`_probe_lines` 多回第三個值(或用原因字串分流計數),Z 段分開數;`_probe_lines` 的第 31547 行與 `drift check` 只取 `[0]`,不受影響(已驗)。

**Z4 RETIRE-IF 要從治理帳數「擋下幾次、跳過幾次」,但治理帳不記規則名,而計劃又說不新增欄位**
severity: minor
blocking: 否 — 判準:跟鄰居做法不一致(鄰居靠 `extra` 欄位讓 RETIRE-IF 可配對),但不是第二種做法也不是跨層直呼,依本席嚴重度錨為 minor。
引句:「從治理帳數「回頭條件寫在句中」擋下幾次、跳過幾次」
對照 file: scripts/lumos:29584-29588(note-shape 的 blocked/warned 事件 note 只有 `新違規 N 條`,沒有規則名)、scripts/lumos:29397-29399(`skipped-env` 只在格子有 `extra`,「RETIRE-IF 配對用」)、scripts/lumos:29571-29575(`_ns_slot_extra` 的 `extra` 欄位)。另見計劃〈回退〉與〈實務隱患·併發〉的「不新增治理帳欄位/事件」。
說明:鄰居(筆記格子、測試綁定)為了 RETIRE-IF 可量,在 `extra` 帶分類計數,連跳過那條路也補算(`_ns_skip_slot_extra`)。本案的 RETIRE-IF ① 需要「擋下次數」與「跳過次數」兩個分子,現有帳只有總數,跳過事件不帶違規內容,數不出這一條規則。要嘛照鄰居在 `extra` 補一個計數(並改掉「不新增欄位」那句),要嘛把 RETIRE-IF 改成用別的可量來源(例如 doctor Z 段存量計數的升降)。

**Z5 E5 處理提示與 Issue 結案提示改字,但 E5 的呈現上限與開段條件不變,計劃沒交代已結案行對計數的影響**
severity: minor
blocking: 否 — 小的呈現銜接。
引句:「doctor E5 不唸這條(不算到期、不算壞行)」
對照 file: scripts/lumos:2303-2325(E5 迴圈與 `_rv_bad`、`_rv_due`;治理帳 note `due=N bad=M`)、scripts/lumos:31739-31757(`_issue_close_revisits`)。
說明:`_revisit_lines` 直接不回已結案行是對的(E5 與 Issue 列出兩個呼叫端都受益,且避免死參數),但 E5 的治理帳 note `due/bad` 與 RETIRE-IF ② 的「E5 逾期件數」因此會隨 `[closed:]` 的使用下降;這正是設計想看的訊號,卻沒有區分「結案掉的」與「真處理掉的」。建議在 Systems/存量漂移守衛.md 的 WHY 註一句:E5 件數下降不等於都處理了,可能有一部分是結案,量測時另數 `[closed:` 出現次數(RETIRE-IF 已有「數 `[closed:` 出現幾次」,只差在判讀時交代)。

不對齊共 5 條,其中 major 0 條
