severity: minor

審查範圍:/tmp/回頭條件消失式與生來成立-r1.md,對照 rw 副本的 scripts/lumos(行號都是該副本)。結論:沒有跨層直呼,也沒有真的第二套判定或第二套往回查;主要不對齊在「拆值函式另立一支」與「列舉四種鍵的地方沒盤點全」。

## 四問

1. 分層與依賴方向:對齊。新鍵走既有的文法驗證 → 正規化 → `_DriftProbeTree.one` → `_drift_probe_one` / `_drift_probe_line` → 推送候選 `_drift_probe_cond_candidate` 這條鏈,誰呼叫誰沒變(scripts/lumos:31910、31929、32377、32388、32430)。scan 的往回查放在 scan 這一層、不碰推送判定,跟「scan 不寫帳」(scripts/lumos:34893 的 cmd_drift_scan 與 Systems/存量漂移守衛 d1 那條 WHY)一致。唯一沒講清楚的是 born 的計算放哪一支,見 Z4。
2. 命名與錯誤處理:大致對齊(鍵名 `gone`、`_probe_gone_err` 對應 `_probe_named_err`、錯誤字串列鍵),但列舉鍵名的地方沒盤點全,見 Z2;born 的呈現與鄰居不同形,見 Z4。
3. 第二種做法:拆值函式見 Z1;往回查歷史見 Z3。其餘(判定沿用 `_drift_probe_line`、RULE 撤除條件走 `_retire_lines` → `_probe_parse`)都是沿用,沒有另寫。
4. 落點:`Systems/存量漂移守衛` 是對的主家(about_code 含 scripts/lumos,〈條件式回頭條件(乙)〉在那篇),不用另開;但 lands_in 漏列一篇,見 Z5。

## Findings

**Z1 `_drift_gone_split` 另立第二支拆值函式,跟「一個條件碰到哪支檔只有一份」的家規並排**
severity: minor
blocking: 否 — 結構方向對(拆值、判定、預讀、候選、點名五處共用同一支),差的是多了一支平行函式而不是把既有那支加一個參數;未達「第二種做法」是因為拆法的語意真的不同(第一個 `::` 對最後一個 `::`)且 spec 已明講理由。⚠ 若實作時有一處(例如 `prefetch` 的 `k in ("symbol","test")` 過濾或 `unread_for`)漏改、仍呼叫 `_drift_cond_split`,就退化成代碼審 r5 抓過的「四處各自拆」,屆時升 major。
引句:「所以 `when-gone` 另用一支 `_drift_gone_split`(判定、預讀、點名讀不出的檔、候選篩選、正規化共用它)」
對照:scripts/lumos:32195(`_drift_cond_split(v)` 沒帶鍵,rsplit);scripts/lumos:32298 起 `prefetch`/`unread_for`/`one` 都以 `_drift_cond_split` 拆(32290、32316、32356);scripts/lumos:31929(`_probe_norm_value` 的 rsplit);Systems/存量漂移守衛.md:59(r5 WHY:「一個條件碰到哪支檔、哪篇筆記只有一份……根因是四處各自拆條件」)。建議:`_drift_cond_split(k, v)` 加鍵參數,gone 時從第一個切,讓既有五個呼叫點(其中 `k` 本來就在手上)不用改成判兩套;或至少在 spec 列出要改的呼叫點清單,並寫一條「新鍵漏改任一處」的測試。

**Z2 列舉「四種鍵」的地方沒盤點全,「RULE 撤除條件自動支援」的說法不完整**
severity: minor
blocking: 否 — 結構對,只是同一個事實(合法條件鍵有哪幾個)散在 spec 沒點到的幾處,上線後會出現「報錯訊息說只有四種、實際認五種」。
引句:「RULE 的撤除條件 `[retire:when-gone:…]` 走同一支解析(`_retire_lines` 改寫成回頭條件標記再交給 `_probe_parse`),自動支援,不另寫。」
對照:
- scripts/lumos:3891(撤除條件文法的總錯誤訊息寫死「只收 when-file/when-symbol/when-test/when-status、度量、人裁」),而且該函式在 scripts/lumos:3881–3890 自己有一段 `v.startswith("when-")` 分支,對 symbol/test 另加「要帶路徑」的規則,gone 要不要比照(`[retire:when-gone:路徑]` 允許、不帶路徑的字串版沒有)spec 沒定。
- scripts/lumos:27968(REVISIT 寫法提示)、28184–28185(「條件怎麼選」那段,spec 只說補一句)、28371(RULE 範本)、31756(文法註解區塊)都舉四種鍵的例子。
- scripts/lumos:32630–32643 `_drift_probe_row_problems`/`_drift_probe_path_warn` 對 file/symbol/test 各有「路徑指不到」的 scan 提示,spec 沒說 gone 要不要有、或明說不要(路徑不存在正是 gone 的成立條件,理應不警告,但要寫出來,免得實作者照鄰居補一個)。
建議:spec 〈做法〉1.4 補一份「列舉鍵名的點」清單,至少把 3891 的總錯誤訊息與 3881 分支寫進去。

**Z3 「往回查寫下那一版」的先例引用不準,實際可沿用的既有做法 spec 沒點名,實作時容易手刻第二份**
severity: minor
blocking: 否 — 概念上沒有第二種做法(`git log -S` 找首次出現加「在那個提交的樹上重判」都有先例),只是 spec 把先例指給 `drift exam`,而 exam 的重放是換行後呼叫 `_drift_check_core`(推送判定)、不是在歷史樹上直接 `_drift_probe_line`。⚠ 判不準:若實作者照 spec 字面去找 exam 的重放來抄,會找錯地方;若自己手刻 subprocess 的 git 呼叫,就成了第二種做法。
引句:「本 repo 的 `drift exam` 已經在歷史上重放條件,判定沿用同一支 `_drift_probe_line`。」
對照:
- 真正可借的「在某個提交的樹與圖譜上跑 scan」是 scripts/lumos:34905–34918(`cmd_drift_scan --at`:`_lens_full_sha` → `_drift_vault_rel(root, sha)`(圖譜資料夾改過名就用那一版自己的位置)→ `_drift_tree_env` → `_drift_probe_tree`)。born 應抽出這一段共用,不是另寫。
- drift exam 的 probe 重放是 scripts/lumos:35093–35127(`_drift_exam_probe` 在記憶體換行後走 `_drift_check_core`),不是 `_drift_probe_line` 直呼。
- `git log -S` 找首次出現與淺層判斷的既有寫法:scripts/lumos:26692(`_nodehome_golive`,用 `_nodehome_git` 加 `-S`)、13626–13632(`_guard_pass_commit_date`,先 `_git_is_shallow` 再查,並註明為何不用 `-S`:原地換行出現次數不變),以及 Systems/存量漂移守衛.md:66 的慣例(`--literal-pathspecs`)。spec〈跨環境〉自述「淺層時不往回查」卻沒說用 `_git_is_shallow`。
建議:spec 改引 `cmd_drift_scan --at` 那段與 `_nodehome_git`/`_git_is_shallow` 當實作錨點。

**Z4 `born` 的呈現與計算位置跟鄰居不同形**
severity: minor
blocking: 否 — 不引入新層,但欄位型別與「判不了」的歸處跟既有慣例不一致。
引句:「`--json` 的發現多一個欄位 `born`:`{"commit": 短碼}`、`"unknown"` 或沒有這欄。」
對照:
- 既有「判不了」一律進 `probs`(第二個回傳值,scan 文字輸出另開 `[回頭條件與撤除條件的問題]` 段,JSON 在 `problems`):scripts/lumos:32650(`_drift_probe_scan` 的 probs)、34893 起 `cmd_drift_scan` 輸出 `problems`、`_drift_scan_print` 的 probs 段。spec 把「判不了寫下時成不成立」做成發現上的標記,是新的歸法。
- 發現上附加欄位的先例是 `prev_ack`(`dict` 或不存在),文字另起一行以括號印(`_drift_prev_ack_line`,scripts/lumos:34968 附近與 32806):型別單一。born 為 dict 或字串 `"unknown"` 混型,讀 JSON 的人要多判型別。
- 已表態的發現文字輸出只印一行、不印 why(`_drift_scan_print` 的 `if not acked:` 分支),spec 的「那一行後面加標記」要同時適用兩種路徑,格式沒定。
- 計算位置沒寫:`_drift_probe_scan` 只收一棵樹且被 retire 共用(spec 說 retire 不查),放進去要加分支;放在 `cmd_drift_scan` 於 `_drift_split_acked` 之後逐筆補欄位較自然(已表態的才查得到)。
建議:born 用單一型別(例如 `{"commit": 短碼}` 或 `{"unknown": true}`),或把判不了併入 `problems`;並寫明由 `cmd_drift_scan` 呼叫一支新 helper。

**Z5 lands_in 漏列改到提示文字的那一篇**
severity: minor
blocking: 否 — 主家選對(Systems/存量漂移守衛),但依「改到的每支檔都得先有家、說明寫進家」,spec 同時改筆記形狀擋的提示文字與技能手冊,落點沒跟上。
引句:「lands_in:
  - Systems/存量漂移守衛」
對照:同一輪的姊妹計劃 Projects/回頭條件寫法補齊_計劃.md:10–12 因為同樣要改提示文字,lands_in 列了 `Systems/存量漂移守衛` 與 `Systems/筆記內容閘`;本 spec〈做法〉1.4 要改的 scripts/lumos:28184–28185 「條件怎麼選」屬同一塊提示。`skills/lumos-project-notes/commands/03-寫回圖譜.md` 的家是 Systems/lumos-cli-read(該篇 about_code 引它)。建議 lands_in 補 `Systems/筆記內容閘`,並在〈說明與同步〉寫明技能手冊那一行歸 lumos-cli-read。是否另開新篇:不需要,條件式回頭條件(乙)就在存量漂移守衛。

## 沒問題的部分(對照後確認一致)

- 推送候選對 `when-gone` 看路徑在不在 `touched`,跟 `file`、帶路徑 symbol 同(scripts/lumos:32430–32440)。
- 轉變判定、起點用同一支、預算、判不了不擋 scan:全沿用(scripts/lumos:32458–32486、32673)。
- doctor Z 段不評估條件、scan 不寫帳:跟既有決定一致(scripts/lumos:34943 起 `_drift_doctor_lines`、Systems/存量漂移守衛 d1)。
- 新規則名、改法字串:沒有新增 drift kind 與新的 `drift fix` 修法,沒有漂離 `_DRIFT_KIND_NAMES`(scripts/lumos:31399)。

不對齊共 5 條,其中 major 0 條
