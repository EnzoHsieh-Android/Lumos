severity: major

## F1 預設 block 門檻沒有召回下限，零偵測實作也能通過

severity: major

blocking: 是 — 不補召回門檻，完全抓不到漂移的實作仍會被配置成正式阻擋模式。

引句:「預設模式應照〈做法〉第 4 節第 4 點的門檻決定」

1. 第 4 節門檻只要求非漂移題零誤列，以及每提交「要處理」不超過 5 筆，沒有要求 11 題正例至少抓到幾題。
2. 一個永遠輸出零發現的實作會得到零誤列、噪音 0，完整滿足門檻，卻漏掉全部正例。
3. `drift exam` 雖計算「漏」，接線決策完全沒有使用它；實作者照規格會把無效守衛設成 block。門檻必須加入甲、乙各自的最低命中率或必過正例集合。

## F2 日期與事件二擇一無法忠實改寫既有條件，B5 已證明會提前擋人

severity: major

blocking: 是 — 不補合成語意，修復階段會把尚未到期且內容屬實的回頭條件改成即時阻擋。

引句:「日期或條件二擇一放在 `REVISIT:` 後第一個位置。」

file: `governance/eval/drift-exam/rtb-2026-09-28.json:209`

file: `governance/eval/drift-exam/rtb-2026-09-28-probes.json:22`

1. B5 原文的期限是 2026-12-31，考卷判定 `true_not_drift`；它表達的是「到該日期時，依啟動程式是否存在採取不同動作」。
2. 改寫檔被迫丟掉日期，只保留 `[when-file:src/rtb/analyzer/runner.py]`，因此在 8ff8c95 當場阻擋；改寫檔自己把預期記成 `blocked_but_not_drift`。
3. 規格又把 B5 排除於誤報門檻，掩蓋了文法無法表達「日期到達且事件成立」或「事件成立但不得早於日期」的缺口。
4. 第 4 節要求修復舊回頭條件；在沒有日期與事件合成規則時，實作者只能丟掉期限或丟掉事件，兩者都會改變原合約。

## F3 完整考卷仍含第五種已拆出的事件，exam 指令沒有可執行的處置規則

severity: major

blocking: 是 — 不定義跳過或分卷規則，規定必跑的三次考試會報錯或產生不同分母與分數。

引句:「本計劃用甲的 6 題、乙的 5 題加非漂移對照;機制①那 9 題給實驗計劃」

file: `governance/eval/drift-exam/rtb-2026-09-28.json:14`

file: `governance/eval/drift-exam/README.md:11`

1. `lumos drift exam` 的介面只接收整份 JSON，沒有 `--mechanism`、題號篩選或本計劃專用分卷參數。
2. S13 只定義 `commit`、`status_replay`、`probe`、`current_state` 四種考法，但 JSON 另有 9 題使用 `mechanism1_experiment`。
3. 實作者可以把未知事件當錯誤、靜默跳過或算成漏；三種結果都符合目前文字，卻會讓 S16 的三次考試得到不同結果。
4. 這是拆出「丙」後留下的直接依賴，不是重審機制①；本 spec 必須明訂略過規則，或提供只含甲乙題目的輸入。

## F4 E2 沒有結構化指定 status_replay 的目標計劃

severity: major

blocking: 是 — 不補目標欄位，實作者會重放錯誤計劃或把無關計劃一起算入噪音。

引句:「取失效提交的**上一版**的樹,在記憶體裡把那份計劃的 status 改成 done」

file: `governance/eval/drift-exam/rtb-2026-09-28.json:377`

1. E2 只有 Issue、失效提交 7413936 與人讀的 `code_evidence`，沒有 `status_target` 或計劃路徑欄位。
2. 唯讀重驗 `git -C <rtb-exam> show --format= --unified=0 7413936 -- 'docs/*-knowledge/Projects/*.md'`，該提交同時把 Phase 11B 與 Phase 8 兩份計劃由 doing 改成 done。
3. 「那份計劃」無法由現有結構唯一決定；解析散文、選第一份或重放兩份會產生不同待辦與噪音。
4. 每個 `status_replay` 題目必須提供機讀的目標節點與目標狀態，S13 也必須綁定該欄位。

## F5 settle 的鎖沒有涵蓋其他會改同一篇家筆記的指令

severity: major

blocking: 是 — 只鎖 settle 仍會發生成功回報互相覆蓋，留下 pending 守衛卻沒有預告行的壞狀態。

引句:「整個 settle 包在 `_vault_write_lock` 裡;先改家筆記的預告行(既有邏輯),再**一次寫入**守衛紀錄」

file: `scripts/lumos:11588`

file: `scripts/lumos:11626`

file: `scripts/lumos:11855`

file: `scripts/lumos:11890`

1. 現行 `guard plan` 在鎖外讀取並重寫家筆記；`guard abandon` 也先在鎖外重寫家筆記，最後的 `cmd_set` 才取鎖。
2. 同一篇家筆記上，程序 A 執行 settle，程序 B 同時 plan 新守衛：B 寫入新預告後，A 可用較早讀到的整份內容覆寫家筆記，把 B 的預告刪掉。
3. 兩個命令都能回報成功，但 B 的守衛紀錄已是 pending，家筆記卻沒有對應預告；既有補救只涵蓋 settle 自己的兩段寫入，修不了這個交錯。
4. 同一筆記的所有讀—改—寫者必須取得同一把鎖，至少涵蓋 plan、settle、abandon 的完整操作。

## F6 候選過濾漏掉純改名造成的 false→true

severity: major

blocking: 是 — 不把路徑與檔案分類變化納入候選，條件已成立的推送會直接以 0 放行。

引句:「`symbol`、`test` 的名稱出現在範圍裡程式檔或測試檔的改動行」

file: `scripts/lumos:22453`

file: `scripts/lumos:22474`

1. 先放一條既有條件 `[when-test:tests/new/test_x.py::test_x]`，起點只有 `tests/old/test_x.py`，條件不成立。
2. 推送只做 `git mv tests/old/test_x.py tests/new/test_x.py`，內容完全不變；終點條件成立，但 `test_x` 不會出現在任何內容改動行。
3. 規格的候選規則會跳過該條件，與「其他條件起點與終點結果一定一樣」的宣稱矛盾。
4. 同樣缺口存在於程式檔路徑限定，以及檔案改名後從非測試檔變成 `_nodehome_is_test` 所認測試檔的情形。候選判定必須納入路徑、改名及分類前後變化。

## F7 改一個字會把已觸發的舊條件降級成只列出

severity: major

blocking: 是 — 不改行身分判法，作者或一般文字整理都能繞過本來應阻擋的 false→true 事件。

引句:「作者改了那一行任何一個字,就算新寫(他已經碰過這行)。」

1. 起點有尚未成立的條件式 REVISIT；同一次推送加入觸發檔案，並只修改該行標點或任務措辭。
2. 一字不差比對失敗後，該行被歸為「新寫」；依第 2 節，新行終點成立只列出、回傳 0。
3. 第二層又明確排除條件式 REVISIT，因此沒有另一道阻擋要求作者處理或留下 `drift ack` 理由。
4. 「作者碰過這行」不等於作者已處理觸發事件。行身分必須依條件與任務的穩定識別比對，或讓已成立的新寫／改寫行也要求正式表態後才放行。

## F8 表格行既未定義又被一律當範例，會產生無人評估的活條件

severity: major

blocking: 是 — 不界定並拒絕表格中的活語法，合法 Markdown 內容可以繞過第一層、check、scan 與 doctor。

引句:「圍欄內的行、表格行、行內程式碼(一對反引號)裡的標記都不算——那是範例。」

file: `scripts/lumos:3236`

file: `scripts/lumos:23802`

file: `scripts/lumos:23807`

1. `_visible_lines` 只處理圍欄，沒有表格判定；現行內容審只把表格分隔列視為結構，普通資料列仍是可審的正文。
2. 規格沒有定義「表格行」是任何含 `|` 的行、以 `|` 開頭的行，還是必須位於合法 Markdown 表格中；不同實作會吞掉不同正文。
3. 新增 `| 待辦 | REVISIT:[when-file:src/x.py] 補測試 |` 時，第一層依規格不管，條件評估也忽略，doctor 又只警告開頭欄位等不評估位置，不警告表格。
4. 這不是範例而是正常表格資料，條件會永久失效。表格若禁止活語法，第一層必須明確阻擋並由 doctor 列出；若允許，就必須定義表格解析並納入共用分類器。

逐節覆核：

- 文件開頭、依據、PRIOR-ART、RETIRE-IF、範圍：已讀，無額外 finding；機制①的功能本身沒有重報。
- 做法 0：F6、F7、F8；其餘指令、既有函式及旗標語意已核對，無額外 finding。
- 做法 1：F5；五種一致檢查與 settle 補救正文均已讀，無額外 finding。
- 做法 2：F2、F6、F7、F8；其餘四鍵終點判法已讀，無額外 finding。
- 做法 3：F3、F4；A4–A6 的更正提交、`note_at_event`、A7/B1–B5 的事件前後翻轉均以 RTB 唯讀複本重驗，無額外 finding。
- 做法 4：F1、F2；掃描、修復清單與接線順序已讀，無額外 finding。
- 做法 5：已讀，落點均存在或明載新開，無額外 finding。
- 條款 S1–S18：已逐條對正文；除上述 findings 的條款缺口外，交叉引用均存在，無額外 finding。
- 回退：已讀，settle、第二層與條件評估的回退順序有交代，無額外 finding。
- 實務隱患：已讀；漏抓／繞過見 F6–F8，誤擋與時序見 F2，併發與狀態一致性見 F5，評測與接線決策見 F1、F3、F4。效能有總預算及 fail-closed 處置，無額外 finding；金流、對外送出、不可逆均未進入此功能，無 finding；輸入安全已有相對路徑限制及 `-e`、`--` 隔離，無額外 finding。
- 誠實界線：已讀；F7 雖被記錄為限制，仍構成可直接繞過阻擋的錯誤行為，其餘無額外 finding。
- 審計修正紀錄：已讀；r2 摘要所列文法、共用分類、c3/c5、B3、`note_at_event`、回退順序與落點均已落入正文。F2、F3、F4、F8 是修補與正文接縫留下的新缺口。
- 考試結果、修復結果：已讀，仍是依 S16/S17 待填的占位，無 finding。

相關既有節點：

- `Projects/舊句偵測實驗_計劃`：機制①演算法未被本 spec 依賴；F3 只指出共用考卷仍缺少跳過該類題目的執行合約。
- `Projects/code側刪除傳播守衛_計劃`：本設計沒有改動 delguard 的刪除傳播行為，無影響。
- `Projects/筆記形狀擋_計劃`、`Systems/筆記內容閘`：新增 REVISIT 規則會受 F7、F8 影響，無法提供宣稱的第一層覆蓋。
- `Projects/筆記內容審_計劃`、`Systems/筆記內容審`：條件式 REVISIT 的排除本身已落正文，但與 F7 組合後會讓改寫過的已觸發條件沒有任何阻擋者。
- `Systems/guard-kill`：F5 會破壞其守衛紀錄與家筆記同步的宣稱。
- `Issues/存量筆記漂移三種機制_rtb根因回饋`：甲乙方向有覆蓋，但 F2、F6–F8 會讓機制②仍產生誤擋及漏抓。
- `Issues/治理帳多個寫入者都沒上鎖`：spec 已把新增 JSONL 寫入者登記進該 Issue，沒有假稱已解決；F5 是另一類筆記檔讀—改—寫競態，不受該登記化解。
- `Systems/reversibility-governance-ledger`：新閘名與事件種類的落點明確，無額外 finding。

最嚴重等級 major，blocking 共 8 條。