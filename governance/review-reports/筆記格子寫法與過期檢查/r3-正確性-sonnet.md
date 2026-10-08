severity: major

固定席筆記:這次派工沒有附固定席筆記,無法逐條判「不影響」。

以下查證用的 repo 都是 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw`,下文只寫相對路徑。

**R3C1**
severity: major
blocking: 是——不改的話,凌晨本機時間寫的合法 `[confirmed:今天]` 會在 CI 被擋成「寫錯」,實作者會做出會誤擋的壞系統。
- 輸入:台北時間 10-02 07:00 提交,新行帶 `[confirmed:2026-10-02]` 或 `[since:2026-10-02]`。
- 走到〈格子規格〉的日期規則和〈擋〉的「CI 照擋」:推上去後 `.github/workflows/ci.yml` 在 ubuntu-latest(UTC,當時還是 10-01)跑 `note-shape --diff`。
- 壞在哪:spec 沒定義「今天」用哪個時區或哪個基準,字面實作會拿跑檢查那台機器的 `date.today()`。UTC+8 每天 00:00 到 08:00 寫「今天」的日期,本機掛鉤和推送前會過,CI 會紅。
- 既有碼的慣例是 `date.today()` 取行程本機時間(`scripts/lumos:3381`),那只是 lint 提醒。本篇把它升級成擋,時區問題就變成誤擋。
- 該補的是容忍一天,或改比提交日期。
引句:「`[since:]` `[confirmed:]` 晚於今天算寫錯;`[until:]` 可以是未來。」
佐證:`.github/workflows/ci.yml:11`、`.github/workflows/ci.yml:141`、`scripts/lumos:3381`

**R3C2**
severity: major
blocking: 是——字面實作會擋掉每一個剛用 `lumos new system` 建立、`FLOW:` 還空著的新節點提交。
- 輸入:`lumos new system` 的骨架 `summary: |-` 下是 `FLOW:` `KEY:` `DEP:` `TEST:` 四個空前綴行,提交時整行都是新增行。
- 走到〈格子規格〉:FLOW 在必有鍵表裡(要 `[來源:]`、`[confirmed:]`),S4 寫「缺 `[來源:]` 或 `[confirmed:]` 應被擋」,「核心一句空的算缺」。
- 空前綴的豁免只寫了 `DEP:` 和 `SEE:`,沒有 `FLOW:`,也沒有寫成「任何前綴什麼都沒寫都不算」。
- 既有碼的豁免是通用的:`skip = (not body) or ...`,對所有前綴都成立。照 spec 字面,新規則反而比舊規則更嚴。
- 該改成通用寫法,例如「任一前綴後面什麼都沒寫的骨架行不算違規」,並與 S1「核心一句是空的應被擋」劃清界線(S1 只指 WHY、RULE、PITFALL)。
引句:「骨架留的空前綴(`DEP:`、`SEE:` 什麼都沒寫)照舊不算違規。」
佐證:`scripts/lumos:17347`、`scripts/lumos:25906`

**R3C3**
severity: minor
blocking: 否——是定義不清,實作者自己會挑一種,最壞是個別指路行被誤擋或誤導。
- 輸入:`DEP:[[A]]、[[B]]`、`FLOW:見 [[Systems/付款流程]]`、`DEP:[[A]][[B]]`。
- 既有的「只放連結」判法(`_NS_POINTER_ONLY_RE`)容許 `見`、`→`、`、`、`,`、`|` 這些連接詞和標點。
- 新文法 SEE 寫「連結以外不准有字」,S4 又說「只放連結的新寫 DEP/FLOW 要改用 SEE」,但「只放連結」沒定義。
- 若「只放連結」採新的嚴格定義,`FLOW:見 [[X]]` 兩邊都不算:不算指路(有「見」),又當一般 FLOW 被要求補 `[來源:]`、`[confirmed:]`。
- 這種寫法在 `skills/lumos-project-notes/reference.md:404` 還是官方範例。
- 該補一句連接詞與標點允不允許,以及提示訊息怎麼指。
引句:「只放連結的新寫 DEP/FLOW 應 被擋並提示改用 SEE」
佐證:`scripts/lumos:25856`、`skills/lumos-project-notes/reference.md:404`、`skills/lumos-project-notes/reference.md:411`

**R3C4**
severity: minor
blocking: 否——只是把「單一來源」的承諾釘得比字面弱,範本與程式的欄位文法仍可能各自漂移。
- 輸入:範本與程式在 PITFALL 的「三選一」、RULE 的「`[retire:人裁]` 另必有 `[until:]`」、`[依據:人|外部|審計|法規|相容]` 的可選值上不一致。
- 走到〈lint 與擋同一張表〉的比對方式:只投影成「前綴 → 必有鍵集合」,表格拆 `\|` 轉義後再比。
- 壞在哪:三選一(OR 組)、條件式必有鍵、列舉值,在「鍵集合」這個投影裡都表達不出來。
- 這幾處正好是最容易漂移的地方,合約候選又把「單一來源」列為承諾。
- 另外,把 `\|` 轉義去掉後,`依據` 欄位的 `人|外部|…` 會不會被誤切成多格,也沒講。
- 該把投影擴成含 OR 組、條件鍵、列舉值,或者在天花板承認這幾處沒釘。
引句:「範本那邊先拆表格、去掉反引號與 `\|` 轉義」

**R3C5**
severity: minor
blocking: 否——只造成 lint 和 doctor 對舊行多唸,不擋;但違反本篇自己說的「舊筆記不檢查」。
- 輸入一:舊 WHY 行,日期寫在句中而不是行首方括號。本 repo `docs/lumos-toolchain-knowledge` 摘要裡 170 條 WHY 有 5 條冒號後不是 `[`,例如 `WHY:立案(2026-09-29 Enzo 裁…)`。
- 這 5 條現在過 lint,因為 `_CTX_SRC_RE` 認句中任何位置的日期。
- 走到〈lint〉的新舊分界:冒號後第一個東西不是 `[日期` 開頭的方括號,就「其他都算新文法」,於是這些舊行被唸缺 `[出處:]` 和 `[因:]`。
- 輸入二:FACT 11 條裡有 3 條不以方括號開頭,同樣會被改套新表。
- 輸入三:舊 FACT 行沒有 `[confirmed:]`。過期表那列寫「超過 `[recheck:]` 或來源預設」,沒寫缺 `[confirmed:]` 時怎麼辦。
- 字面實作可能把缺失當成過期,對所有舊 FACT 行唸 doctor 提醒。
- 該補:新舊分界改用「欄位是否出現任何新文法鍵」,或明寫「沒有 `[confirmed:]` 的 FACT 不判」。
引句:「算舊寫法,照舊判準、不因新表多唸;其他都算新文法、用新表。」
佐證:`scripts/lumos:3277`(`_CTX_SRC_RE` 認任意位置日期)

**R3C6**
severity: minor
blocking: 否——是引用寫錯,但 spec 自己的 S5 範例在 doctor 一跳檢查時可能被判成「指到不存在」。
- 指令名:spec 寫 `lumos decision supersede`,實際子指令是 `decision-supersede`(`scripts/lumos:40862`)。
- 格式:spec 說 `節點#dN`「跟 `decision-add` 印的同一種」。`decision-add` 實際只印 `{rel}` 和 `編號 d3`,全域形式 `rel#dN` 只是回傳值(`scripts/lumos:16532`、`scripts/lumos:16533` 附近)。
- 圖譜裡實際出現的全域 id 都帶 `.md`,例如 `Projects/cochange守衛_計劃.md#d1`。spec 範例卻是 `Projects/新判法_計劃#d2`(無 `.md`)。
- 該明寫解析時接受哪種節點寫法(含不含 `.md`、含不含 `[[ ]]`),否則範例本身可能被 doctor 判成不存在。
引句:「全域決策編號 `節點#dN`(跟 `decision-add` 印的同一種,單寫 `d3` 算寫錯)」

**R3C7**
severity: minor
blocking: 否——只是治理帳欄位命名重複,不影響判定,但讀帳端會碰到同鍵不同型別。
- 同閘 `note-shape` 的既有 `hinted` 事件已用 `extra={"check":..., "lines":..., "notes": 整數}`(`scripts/lumos:26475`)。
- 本篇的擋下與跳過事件把 `notes` 定成路徑清單,同一個閘同一個鍵出現整數和清單兩種型別。
- 既有的 `blocked` 事件已有 `nodes=` 欄位放路徑(上限 50),RETIRE-IF 的「同一批筆記路徑」配對直接用 `nodes` 就夠。
- 該改用 `nodes`,或把鍵改名(例如 `note_paths`)。
引句:擋下事件 `extra={"check":"slots","lines":條數,"missing":{鍵:次數},"notes":[筆記路徑]}`
佐證:`scripts/lumos:26475`、`scripts/lumos:26493`

**R3C8**
severity: minor
blocking: 否——只影響 doctor 提醒(時間類不擋),但會產生「該撤除」的假提醒。
- 輸入:某專案把 `drift_check.gate` 設成 `off`(或根本沒裝掛鉤),事件數是 0。
- RULE 寫 `[retire:度量 drift-check.blocked == 0 近8週]`。
- doctor 看到近 8 週 0 筆,判成符合,提醒撤掉這條 RULE。
- 零筆可能只是這道閘當時沒開或被跳過,spec 只在天花板 9 說了「整閘而非單條 RULE」,沒處理「閘沒開」。
- 該補:閘被關掉或跳過的期間不判,或度量條件的主詞要先確認閘在開。
引句:「數的是整個閘的事件數,不是這條 RULE 自己的(治理帳不認得是哪條 RULE 觸發的)。」

**R3C9**
severity: minor
blocking: 否——「只是字串比對」的成本宣稱不成立,但實作者做得出來,只是要重排單次跳過那段碼。
- 輸入:`LUMOS_SKIP_NOTE_SHAPE=1 git commit`。
- 既有 `cmd_note_shape` 在 `skipped-env` 分支是函式最前面就記帳 `return 0`,此時還沒有 vault、設定、`--staged` 的 diff(`scripts/lumos:26370`)。
- 要「先算一次格子違規」得把整套 vault 偵測、讀設定、抽新增行、舊行比對搬到跳過之前。
- 這會讓「保證能逃生」的路徑多一個會失敗的步驟。spec 沒說這步丟例外時要不要照樣放行。
- 該補:算不出來就 `slots_lines` 留空並照樣放行,且用 `--slots` 與開關 off 先決定要不要算。
引句:「單次跳過時先算一次格子違規(只是新增行的字串比對)」
佐證:`scripts/lumos:26370`

**各節檢查結果**
- 前置與 frontmatter:已讀,無 finding。
- 〈格子規格〉(欄位、重複鍵、日期、作廢、撤除條件、確認週期):除 R3C1、R3C2、R3C6 外已讀,無 finding。
  - 核對過:`parse_rule_fields` 重複取最後一個、`rule_field_truncated` 的 `]` 截斷、`_PROBE_KEYS` 四種、`_probe_value_err` 的值文法,都與 spec 宣稱相符。
  - 核對過:`_PROBE_ANY_RE` 不會誤抓 `[retire:when-…]`。
  - 核對過:`<閘>.<種類>` 例子 `note-shape.blocked`、`drift-check.skipped-env` 在 `_gate_event_or_warn` 呼叫點確實存在(`scripts/lumos:26493`、`scripts/lumos:30380`)。
- 〈擋〉(`--slots`、格子記號、舊行、子開關、擋下訊息、治理帳):除 R3C7、R3C9 外已讀,無 finding。
  - 核對過:上線點找不到時「不過濾、全查」的既有行為成立(`scripts/lumos:25678`)。
  - 核對過:逐提交用該提交自己的 `scripts/hooks/pre-commit` 內容判記號的做法成立(`scripts/lumos:25589`)。
  - 核對過:pre-push 與 pre-commit 用同一份 `$REPO_ROOT/scripts/lumos`(`scripts/hooks/pre-push:83`、`scripts/hooks/pre-commit:140`),版本不會分叉。
  - 核對過:`_notelines_range_added` 回傳按路徑彙整的行文字集合,實作要拆出「有格子記號的提交」那一組,是可做的新能力。
  - 核對過:提交對 HEAD、推送對範圍起點的「上一版」,在 doctor 事後掃描有 200 個提交上限時,「上一版」會落在上線點。此時早於掃描窗口、之後又只改欄位的舊行會被當成新寫,這是邊緣誤報,未達 finding 門檻。
- 〈lint 與擋同一張表〉:見 R3C4、R3C5。
- 〈格子欄位的過期檢查〉:撤除條件推送一列已讀,無 finding。
  - 核對過:`_drift_probe_old` 以(筆記、條件組)當「同一條」;`_drift_probe_judge` 的「新寫時已成立也擋、起點早已成立不列」與 spec 描述相符。
  - 核對過:預算共用同一個 `deadline`,「排在回頭條件之後、用剩下的」可行。
  - 核對過:治理帳讀檔尾 24MB 上限確有其事(`scripts/lumos:2053`)。「歷史短於 N 週不判」若以讀到的檔尾最早事件為準,檔尾被截斷時結果也是不判,字面實作不會判錯。
- 〈分期〉:已讀,無 finding。第 1 步撤回(程式不認 `--slots`)與開擋步撤回的次序,因為 hook 與程式一起由 `lumos update` 分發,不會出現只更新一半的情況。
- 〈天花板〉〈不做〉〈實務隱患〉〈驗收條款〉〈回退〉〈合約候選〉〈審計修正紀錄〉:已讀,無 finding(除上述各條對應處)。
- 文件內部交叉引用:`天花板 3`、`天花板 5`、`天花板 8` 目標都存在。

**實務隱患逐類**
- 併發:無新增。治理帳 append 沿用既有寫法,spec 已說明。
- 效能:無新增。逐提交記號走既有的一趟抽取。
- 資源:無。不開長駐程序。
- 相容(新舊互讀):見 R3C5(舊行在 lint 和 doctor 的判界)。其餘舊行豁免、`--slots` 與記號兩段式、舊寫法保留舊判準,字面行為一致。
- 時間:見 R3C1(時區)、R3C8(閘沒開時的零筆)。
- 注入:無新增。擋下訊息截斷與清控制字元已寫明。
- 不可逆與金流、對外送出:無,因為只讀筆記與程式文字,且擋都可降級。

最高嚴重度:major,blocking 2 條
