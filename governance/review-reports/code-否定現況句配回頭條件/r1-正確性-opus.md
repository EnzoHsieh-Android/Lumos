severity: minor

# 否定現況句配回頭條件 代碼審 r1:正確性-opus

實驗環境:`git clone --shared` 到自己的臨時目錄(HEAD=1ca70d4f),`/opt/homebrew/bin/python3`(3.14.6)。

## 查過、沒問題的(不列 finding)

- **真 git repo 跑提交前掛鉤**:把 clone 的 `core.hooksPath` 指到它自己的 `scripts/hooks`,在計劃筆記尾端加一行「前端頁面還沒做,下一個增量補。」,另一組再加一行程式行號引用,`.lumos/config.json` 的 `note_shape.gate` 分別設 block/warn/off 真的 `git commit`:
  - block + 只有提醒 → commit rc0、印提醒、只記一筆 `hinted`(extra `check/lines/notes`、`nodes: []`、`head_sha` 是提交前的 HEAD)。
  - block + 行號引用 → commit rc1(被擋);順序:擋下段 → 尾句 → 提醒段;帳是先 `blocked`(「新違規 1 條」,沒把提醒算進去)再 `hinted`。
  - warn + 只有提醒 → rc0、只有 `hinted`;warn + 行號引用 → rc0、先 `warned` 再 `hinted`。
  - off(兩種)→ rc0,只印「note_shape.gate=off,跳過」,沒有提醒也沒記帳。
  - 跟改之前那版 `cmd_note_shape` 逐行比過:違規段搬進 `_note_shape_report` 後,字樣、帳、回傳碼都一樣;三種 gate 下的回傳碼沒有任何改變。
- **`--diff` 與 doctor**:`note-shape --diff e6213559..1ca70d4f` rc0、不印提醒;doctor 那一行放在 `if ci: return out` 之前;`doctor --ci` 的提醒行只加進 `_top_soft`,不影響回傳碼。
- **子開關各值**:null、block、false、"OFF"、壞 JSON、`note_shape` 不是物件,都照計劃〈做法〉5 處理。
- **例外防護**:讀設定、逐篇判定、組字樣三處都有 try。把 try 拿掉(`prepare-no-try`、`collect-no-try`、`format-no-try`),測試都變成 EXCEPTION 翻紅;`emit` 只看 `neg_items` 也翻紅(⑨–⑪)。
- **lint 放行**:用 `_lint_new_verdict(repo, "e6213559..1ca70d4f")` 跑兩次。放行檔照現況:clean、waived 1。放行檔換回改之前那版:只多出一條新告警 `49597fef45294440 C901 scripts/lumos _note_shape_eval is too complex (23 > 10)`。ruff 對新舊兩版的量法:`_note_shape_eval` 前後都是 23;`cmd_note_shape` 從 22 降到 19,它的 def 那一行沒動,所以指紋不變。放行只放了該放的那一條。
- **版本與 CHANGELOG**:`-k version` 28 項全綠(含 t_version_single_source);兩份注入區塊的標頭都是 v1.1;repo 裡沒有別處還寫著 v1.0 的版本戳。
- **範本、skill 與注入**:`-k discipline`、`inject`、`claude_block`、`template`、`skill`、`graph_disc` 全綠。「緊鄰原句」「旁邊必須有」在 governance 以外已經搜不到。
- **既有子集**:`-k note_shape`(174)、`revisit`、`gov_stats`、`lint_new`、`anchor`、`doctor_summary` 全綠;`anchor verify` 綠;`drift check --diff` 同一段範圍 rc0;兩篇改到的筆記 `lumos lint` 都是 0 問題。
- **還原翻紅(清 __pycache__ 後一次改一處)**:下面這些都照宣稱翻紅——拿掉固定組合遮罩、歷史字眼改看整段、拿掉 lead 位移、「時/前」改看視窗尾端、區塊多收 decisions、形狀一律當 prose、片段取原行、hinted 帳多帶 paths、設定值不分大小寫、`--diff` 也傳 hints、rc 把提醒算進去、doctor 那行只在 ci=False 時印、拿掉 `→`、切段拿掉破折號、視窗 9 改 4。
- 沒翻紅的列在下面 F1–F3。

## F1 測試說明寫「修飾語視窗改 8 字會翻紅」,實際改成 8 字照樣全綠
severity: minor
blocking: 否
引句:「判定跟量測程式分岔(例:修飾語視窗改 8 字)→ ③紅」
file: `scripts/test_lumos.py:57927`
file: `scripts/lumos:25277`
file: `docs/lumos-toolchain-knowledge/Projects/否定現況句配回頭條件_計劃.md:253`

1. 測試說明與實作紀錄對不上:t_note_shape_negation_lexicon_pinned 的說明寫視窗改成 8 字 ③ 會翻紅;計劃〈實作紀錄〉寫的是「9 字改 4 字 → 例句比對翻紅」。
2. 重現:把 `_ns_neg_is_modifier` 的 `m.end() + 9` 改成 `m.end() + 8`,清掉 __pycache__,跑 `python3 scripts/test_lumos.py -k negation_lexicon`,結果 **4 passed, 0 failed**。改成 4 字才翻紅(「★還沒查根因★——找的時候」)。
3. 影響:照說明信「窗口差一字會被抓」的人,會漏掉差一字的分岔。修法:說明改成「改 4 字」;或者在 ③ 的例句補一句「的」剛好落在第 9 個字的,例如「功能還沒做完整支援新版本的」(還沒後面 8 個字接「的」:9 字判成修飾語、8 字會提醒),這樣 8 字也會翻紅。

## F2 〈做法〉1 第 4–5 點有四個分支沒有任何測試守,改掉照樣 69 項全綠
severity: minor
blocking: 否
引句:「if _NS_NEG_RULE_RE.search(unq[a:b]) or _NS_NEG_HIST_RE.search(unq[a:m.start()]):」
file: `scripts/lumos:25330`
file: `scripts/lumos:25276`
file: `scripts/lumos:25279`
file: `scripts/lumos:25281`
file: `scripts/test_lumos.py:57975`

1. 背景:[S8] 是一次性的手動比對,沒提交。之後「正式判定跟量測程式逐句相同」只剩 [S9] ③ 的例句清單在機械守;常數與正則由 ② 比對。可是有四個判定分支,清單裡沒有一句會碰到。
2. 下面四種各改一處、清掉 __pycache__,跑 `-k negation`,結果都是 **69 passed, 0 failed**:
   - `rule-before-only`:規則字眼改成只看否定字眼前面(`unq[a:b]` → `unq[a:m.start()]`)。計劃寫的是「那一段裡有規則字眼就不算」,應該看整段。能抓到的例句:「還沒審不准推」——現在不提醒,改壞後會提醒。
   - `exist-haiyou-off`:拿掉「還沒」後面緊接「有」算講有沒有這一條(那段條件換成 `False`)。能抓到的例句:「還沒有對應的節點管這支檔」——現在會提醒,改壞後被「的」當成修飾語丟掉。
   - `modstop-off`:拿掉遇到停止字元就停(`if ch in _NS_NEG_MOD_STOP: return False`)。能抓到的例句:「功能還沒做 的部分另談」——現在會提醒(遇到空白就停),改壞後被丟掉。
   - `deshihou-off`:拿掉「的時候」這個記號(只留 `→`)。這個分支現在也只靠「的」順便蓋到,例句要挑講有沒有的字眼,例如「目前沒有的時候先跳過」。
3. 影響:目前判定是對的,這不是行為 bug。缺的是防回歸:以後有人調整這幾個分支,正式工具就會跟量測程式分岔,第 8 週重產被提醒的行時靠的正是「兩邊相同」。修法:把上面幾句加進 S9 的 `extra`,③ 就會拿量測程式逐句比到。

## F3 「設定的提醒只在有要判的新筆記行時才印」沒有測試守
severity: minor
blocking: 否
引句:「設定的提醒只在這次有要判的新筆記行時印,不是每次提交都印。」
file: `scripts/lumos:25702`

1. 計劃〈做法〉5 寫「這些提醒只在這次提交有要判的新筆記行時印」,實作用 `hints["seen"]` 管這件事(實作紀錄特別提到為此加了 `seen`)。
2. 重現:把 `if hints.get("seen"):` 改成 `if True:`,跑 `-k negation`,結果 **69 passed, 0 failed**。改壞之後,`note_shape.negation` 寫錯值的專案每一次只改程式、沒動筆記的提交,都會多印一行「看不懂」。
3. 修法:在 S4 ⑦ 旁邊補一項——同一份錯的設定下,只改程式檔或只改筆記開頭欄位其他欄的提交,不印「看不懂」。

最高等級:minor
