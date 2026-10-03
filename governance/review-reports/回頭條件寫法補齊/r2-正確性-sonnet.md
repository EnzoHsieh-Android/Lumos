severity: major

# r2 正確性席審查:回頭條件寫法補齊(第 2 版修訂稿)

審材:`/tmp/回頭條件寫法補齊-r2.md`。對照 repo:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw`(下稱 rw,只讀)。實驗在 `/tmp/revisitA-r2/exp/`(用 importlib 載入 `scripts/lumos`,沒動 repo)。

先講已核對過、沒問題的:
- 第 1 輪修法有真的解決:新規則不扣(`_NS_FRAG_KEY_RULES` 只有「程式行號引用、釘版本不合法」,file: `scripts/lumos:27693`,`_ns_append_subtract` 對其他規則一律保留,S4 成立);開頭欄位「- REVISIT:日期」行首形狀 `_revisit_split` 判 date、E5 讀得到(實驗:`_revisit_lines` 回了 frontmatter 清單項),不重報成立;`_retire_lines` 抽取層跳過 superseded 的先例存在(file: `scripts/lumos:31866`);`_issue_close_revisits` 與 E5 是 `_revisit_lines` 僅有的兩個呼叫端(grep 驗過,file: `scripts/lumos:2303`、`scripts/lumos:31749`)。
- 本 repo 量測 68 行屬實(我用同口徑重跑:68 行,其中開引號前綴 1 行、其餘 67 行會被新規則命中)。
- 文件內部交叉引用:`Projects/` 與 `Systems/` 的 8 篇連結目標、`skills/lumos-project-notes/commands/03-寫回圖譜.md`、`scripts/graph-rename.sh`、`scripts/templates/graph-discipline.md`、`t_graph_discipline_negation_revisit` 都存在。本稿新測試名(`t_revisit_*`、`t_doctor_revisit_lists_misplaced`)是新寫的,不算。

---

**C1 把句中 REVISIT 塞進 `_probe_lines` 的「不評估」清單,會同時漏進 `drift scan` 與 doctor 既有那一行**
severity: major
blocking: 是 — 照字面實作,doctor 與 scan 會印出錯誤的計數和說明,而 spec 只驗了 drift check 沒被影響
引句:「`drift check` 只用 `_probe_lines` 的第一個回傳值,不受影響。」

1. spec 第 1 節第 3 點:把「REVISIT 寫在句中」收進 `_probe_lines` 回傳的第二個清單(dead),再讓 `_drift_doctor_lines` 另起一行。spec 只清查了 `drift check` 這一個讀者。
2. 問題:dead 清單還有兩個讀者沒列進來。
   - `_drift_doctor_lines` 自己的既有那一行:`n_dead += len(dead)`,印出「條件式回頭條件 N 條…;寫在不評估的地方 {n_dead} 處」(file: `scripts/lumos:34806-34820`)。新種類進了 dead,同一批 67 行會在既有那行被算一次「寫在不評估的地方」,又在新那行算一次「寫在句中的 REVISIT」,同一件事兩個數字。而且 `if n_rows or n_dead:` 會讓只有句中 REVISIT、沒有任何條件式的圖譜印出「條件式回頭條件 0 條(由 lumos drift scan 評估);寫在不評估的地方 67 處」,說的是不存在的條件式。
   - `lumos drift scan`(文字與 `--json`):`_drift_probe_scan` 做 `probs += [(p, no, tx, why) for no, tx, why in dead]`(file: `scripts/lumos:32495-32512`),`cmd_drift_scan` 把 probs 印成「[回頭條件與撤除條件的問題] N 處」並寫進 JSON 的 `problems`(file: `scripts/lumos:34751-34790`)。工具鏈圖譜會多 67 行、消費專案多 9 行,scan 標題括號列舉的原因(「寫錯、沒帶期限、指不到、寫在不評估的地方、判不了」)也對不上。
3. 例子:輸入=現在的工具鏈圖譜(68 行句中 REVISIT)→ `lumos doctor` 的 Z 段既有那行變成「寫在不評估的地方 68 處」,新那行再印「寫在句中的 REVISIT 68 處」;`lumos drift scan --json` 的 `problems` 多 68 筆,下游(`drift exam`、消費專案的清理循環)讀到的問題數暴增。S5 只驗「多一行」與 drift check 不受影響,兩個副作用都測不到。
4. 查證:file: `scripts/lumos:34806`、`scripts/lumos:32495`、`scripts/lumos:34751`;`_probe_lines` 另兩個呼叫端(`scripts/lumos:31547`、`scripts/lumos:32302`)只取 `[0]`,確實不受影響。

---

**C2 RETIRE-IF 與 REVISIT 要「從治理帳數擋下、跳過幾次」,但帳上根本沒有分規則的紀錄,spec 又明寫不新增欄位**
severity: major
blocking: 是 — 撤除條件與回頭條件都量不到,違反本專案鐵則 4「回頭條件要接電」
引句:「設定與帳本格式沒變;不新增治理帳欄位。」

1. spec 在 RETIRE-IF ①(「改用單次跳過、專案開關或 `--no-verify` 的次數超過擋下次數的三成」)與 `REVISIT:2026-12-03`(「從治理帳數…擋下幾次、跳過幾次」)都靠治理帳數這條規則;〈實務隱患〉併發、〈回退〉兩處都說不新增帳欄位。
2. 問題:note-shape 的 blocked 事件只寫 `note="block:新違規 N 條"`(加 nodes),不含規則名;格子與測試綁定才有 `extra` 結構欄位,形狀規則沒有。`skipped-env`(單次跳過)只寫 `"LUMOS_SKIP_NOTE_SHAPE"`,更看不出是為了哪條規則跳過。`--no-verify` 與專案把 note_shape 設 off/warn 根本不產生帳(off 只能看「目前設定」,歷史不留)。
3. 例子:2026-12-03 到期那天,照 REVISIT 去帳上數「回頭條件寫在句中」:數不到——同一次提交被擋可能是程式行號引用、沒寫來源、或這條,帳上都記成「新違規 N 條」;分子(跳過)與分母(擋下)都無法分規則。RETIRE-IF ① 的判準因此永遠無法成立或不成立,只剩憑感覺。
4. 查證:file: `scripts/lumos:29584`(blocked 事件 note 只有 `{mode_word}:{count}`)、`scripts/lumos:29399`(skipped-env 的 note 固定字串)、`scripts/lumos:2331-2334`(對照:E5 的 `note` 有 `due=… bad=…`,所以 RETIRE-IF ② 還量得到,只有 ① 量不到)。

---

**C3 結案標記寫在行尾(最自然的位置)會被靜默當普通文字,沒有任何一層回報——正是本案要消滅的「寫了卻沒人讀」**
severity: major
blocking: 是 — 作者照直覺寫的寫法會默默失效,條件照樣到期、照樣評估,且沒有擋、沒有 Z 段列、沒有提示
引句:「其他位置的 `[closed:…]` 不認,當普通文字」

1. spec 第 2 節第 1 點把結案標記限定在「日期之後第一個東西」或「條件式開頭標記之一」;第 4 點又限定「只在 REVISIT 行上看」且只對 `_revisit_closed` 回的 errs 報錯。
2. 問題:標記放在別的位置(`REVISIT:2026-10-05 原本的待辦 [closed:2026-10-03 已改用新閘道]`,即行尾,跟「~~…~~ 已改用」之類的舊寫法最像)既不是結案,也不是 errs(「其他位置當普通文字」),所以第一層放行、E5 照唸、doctor Z 段不列。作者以為結案了、事實上這條還在每天唸。這跟 spec 〈做法〉開頭要解的問題同形(寫錯位置等於沒寫卻沒人知道),而且第 1 輪為了不誤擋「別的筆記用 `[closed: #123]`」,把整個位置問題切掉了。
3. 例子:輸入=新寫一行 `REVISIT:2026-10-01 補測試 [closed:2026-10-03 已補上測試]` → 第一層不擋(`_revisit_split` 判 date、`_revisit_closed` 回 closed=None、errs=[])→ 提交成功 → 2026-10-04 doctor E5 照唸「逾 3 天」。作者找不到原因。
4. 查證:實驗中 `_revisit_split` 對 `REVISIT:2026-10-05 ... [closed:...]` 回 `date`、summary 保留整段文字(E5 唸的是 `_revisit_lines` 的 date 欄,與行尾標記無關);file: `scripts/lumos:31700-31718`。

---

**C4 理由:「不受 E5 軟段 3 條上限擠掉」對 Z 段自己不成立,新那一行在有 c1–c5 發現時預設就被收進「另 N 條」**
severity: minor
blocking: 否 — 存量清單仍在 `--verbose` 與標題計數可見,只是預設看不到那一行
引句:「也不受 E5 軟段 3 條上限擠掉到期清單。」

1. spec 第 1 節第 3 點用這句當作把存量放 Z 段不放 E5 的理由之一。
2. 問題:Z 段同樣走 `warn_soft`,同一個 `_SOFT_CAP = 3`(file: `scripts/lumos:1379`、`scripts/lumos:1383-1396`)。`_drift_doctor_lines` 的輸出順序是:閘提醒(0–3 行)→ 條件式那一行 → c1…c5 → (新)句中 REVISIT。spec 沒指定新行放哪;依「照 c1–c5 那幾行的呈現」放最後,任何一個專案只要有 ≥3 行別的 Z 發現,新行就被折成「… 另 N 條」。不影響 E5 到期清單這點成立,但「Z 段就看得到存量」不成立。
3. 例子:消費專案現有 c2、c3 各一筆加條件式那一行=3 行,句中 REVISIT 那行是第 4 行,預設 doctor 看不見,要加 `--verbose`。
4. 查證:file: `scripts/lumos:1379`、`scripts/lumos:34797-34830`。

---

**C5 E5 與 Issue 結案列出的提示字串要改,但既有測試對舊字串有逐字斷言,spec 沒列要同步改的既有測試**
severity: minor
blocking: 否 — 推送前的全套閘會當場翻紅,是可預見的補丁,不是設計錯
引句:「doctor E5 的處理提示 應 提到 `[closed:日期 理由]`」

1. spec 第 2 節第 3 點把 E5 提示從「…日期改下一次或刪行」改成「日期改下一次、刪行,或…」;Issue 結案列出的提示也改。〈驗收條款〉S9 只新增斷言。
2. 問題:`t_doctor_revisit_reminder` 逐字斷言 `"日期改下一次或刪行" in r.stdout`(file: `scripts/test_lumos.py:35877`),新字串「日期改下一次、刪行,或在…」不含這個子字串,舊測試會紅。〈做法〉第 3 節、〈驗收條款〉都沒寫「同時更新既有 `t_doctor_revisit_reminder`」。
3. 例子:實作者照 spec 只改提示字串、只加 S9 測試 → 本地跑 `-k doctor_revisit` 紅一條,不知道是改法對、舊斷言過期。
4. 查證:file: `scripts/test_lumos.py:35877`;`scripts/lumos:2320`(`_head5` 的現行字串)。

---

**C6 「一行最多一個」與「其他位置不認」對日期式互相打架,一行兩個結案標記有一種寫法無從判定**
severity: minor
blocking: 否 — 影響範圍只有少見的重複標記,最糟是多報或漏報一次
引句:「當新寫的 REVISIT 行的結案標記日期不合格、理由不到 4 個實字、一行兩個,提交時 應 擋下並報」

1. spec 第 2 節第 1 點:日期式的結案標記只認「日期之後隔一個空白、摘要的第一個東西」;其他位置當普通文字。S8 又要求「一行兩個」要報錯。
2. 問題:條件式有「連續標記」可以數(`_probe_parse` 的迴圈會看到兩個 closed);日期式只認第一個位置,第二個只要不緊接第一個後面就是「普通文字」、不算兩個,規則寫不出來「什麼算兩個」。`REVISIT:2026-10-05 [closed:A 理由四字] [closed:B 理由四字] x` 算兩個還是一個合格加一段普通文字?spec 沒定;兩種實作都符合字面。順帶:「日期之後隔一個空白」是要求恰好一個空白還是容許多個(`_PROBE_TOKEN_RE` 前面是 `[ \t]*`,條件式是容許的)也沒寫。
3. 例子:`REVISIT:2026-10-05  [closed:2026-10-03 已改用新閘道] x`(兩個空白)→ 照字面「隔一個空白」是不合格、照 `_PROBE_TOKEN_RE` 的慣性實作是合格,測試與實作分歧時沒有裁決依據。
4. 查證:file: `scripts/lumos:31694`(`[ \t]*\[(when-…|by):…\]`)、`scripts/lumos:31804-31840`。

---

**C7 `_PROBE_LEAD_RE` 沒在改動清單、〈回滾〉說的「留著無害」對標記排在 `[by:]` 前面的條件式不成立**
severity: minor
blocking: 否 — 只影響顯示的摘要與還原後的讀取,不影響結案判定本身
引句:「寫過的 `[closed:]` 留在筆記裡無害」

1. spec 第 2 節第 1 點要 `_probe_parse` 多認一個鍵 `closed`,但 `_PROBE_LEAD_RE`(`_revisit_lines` 用來剝開頭標記取摘要的正則,file: `scripts/lumos:31697`)是另一條只列 `when-…|by` 的正則,spec 沒提。未結案(例如結案標記寫錯而被當沒寫)的條件式行,E5 摘要會多顯示 `[closed:…][by:…] 待辦`。
2. 〈回滾〉說還原後 `[closed:]` 無害;實驗(spec 自己第 122 行的例子 `REVISIT:[when-file:a.py][closed:2026-10-03 已改用新閘][by:2026-12-31] t`):現行碼 `_probe_parse` 在 `closed` 處停手,`by=None`、第一層報「沒帶期限」(實驗輸出:`('條件寫錯', …, '沒帶期限 [by:YYYY-MM-DD]…')`)。所以還原後,結案標記夾在條件與 `[by:]` 之間的行會失去期限,E5 不再唸它,下一次有人碰那行就被擋。「無害」只對標記擺在 `[by:]` 後面成立。
3. 例子:同上;還原本案提交後,這行從「已結案」變成「沒有期限的條件式」,既不到期提醒也不列在 E5。
4. 查證:實驗檔 `/tmp/revisitA-r2/exp/t.py` 的第 13 行輸出;file: `scripts/lumos:31804-31826`。

---

**C8 漏列平行讀者:`drift fix` 寫入前也會跑 `_ns_revisit_violations`,新規則會連帶擋它寫的自由文字**
severity: minor
blocking: 否 — 擋下的訊息會講哪條規則,使用者可改寫;只是 spec 沒列、沒測
引句:「推送前與 CI 的 `note-shape --diff` 走同一支,一樣擋。」

1. spec 說明「第一層」有哪些入口時只列提交、推送前、CI。
2. 問題:`_drift_fix_shape_err` 對 `drift fix` 要寫進筆記的每段文字呼叫 `_ns_check_line` 與 `_ns_revisit_violations(t, reg, True)`(file: `scripts/lumos:33358-33375`、`scripts/lumos:33507`)。新增的兩條規則會讓 `drift fix --kind c2 --close --reason "…"` 這類帶使用者自由文字的指令,在理由裡提到 `某事 REVISIT:2026-10-05 …` 時被擋;訊息格式是「要寫進去的文字過不了筆記形狀擋(回頭條件寫在句中)…」。行為合理,但不在〈做法〉、〈驗收條款〉、天花板任何一處,沒有測試保護,日後回頭改共用函式的人看不到這條依賴。
3. 例子:`lumos drift fix Issues/X 3 --kind c2 --close --status done --reason "後續 REVISIT:2026-11-01 再看"` → rc 非 0,什麼也沒寫。
4. 查證:file: `scripts/lumos:33372`。

---

## 逐節結論

- 〈範圍〉:已讀,無 finding。
- 〈做法〉1(句中 REVISIT):判定本身(`_revisit_split` 回 None + 日期或 `[when-` + 前一字元不是開引號)經實驗可行;問題在落點(C1、C4、C8)。引號集合裡的 `"` `'` 同時當開閉用,極少數貼著前一字寫 `"REVISIT:` 的會被放過,屬已承認的天花板 1,不另報。
- 〈做法〉2(結案標記):C3、C6、C7。
- 〈做法〉3(說明與同步):已讀,無 finding(`t_graph_discipline_negation_revisit` 逐字釘住範本屬實:file: `scripts/templates/graph-discipline.md:59`)。
- 〈實務隱患〉逐類:
  - 繞過:已逐條列入天花板,新增一條 C3(行尾結案標記靜默失效)。
  - 效能:第一層對新寫行多一個正則、Z 段每篇已逐行掃,多一個正則,量級可忽略。無 finding。
  - 併發:無——只讀筆記、不寫檔、不新增治理帳事件(跟 C2 的缺口是不同件事)。
  - 回滾:C7(「留著無害」對標記在 `[by:]` 前面的條件式不成立)。
  - 誤擋:S3 排除引號與行內程式碼;本 repo 68 行存量只有 1 行是引號框起來的範例,其餘 67 行是真句中 REVISIT,誤擋面由此估得出來(圖譜新寫、被改到舊行才會踩),spec 已寫出口(單次跳過)。無 finding。
- 〈驗收條款〉:S5、S9 見 C1、C5;其餘已讀,無 finding。
- 〈回退〉、〈天花板〉、〈審計修正紀錄〉:已讀,無 finding。

最嚴重 severity 是 major,blocking 共 3 條(C1、C2、C3)。
