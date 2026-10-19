severity: major

審查範圍:正確性/邏輯鏡頭,逐節讀完凍結審材,並對 `scripts/lumos` 現況核對過。前掃(r1-intake.md)已修的項目不重報。

### F1 summary-line 的格子檢查傳 old=None,舊行被誤當新行
severity: major
blocking: 是(照字面做,summary-line 會鎖死改舊行這條路;要改的是實作者的決定)
- spec 段落:〈做法〉1 第 4 點與第 6 點、S7。
- 問題:第 4 點用 `_ns_slot_line_problems(新行, None, 現在)`,第 6 點叫 summary-line 跑「第 4 點同一支」。提交時的做法不同:`_ns_slot_line_problems` 拿 HEAD 的舊行集合比對,「同前綴、同文字鍵」就算舊行,「改了欄位的舊行不套必有鍵」。summary-line 改欄位時句子沒變,提交會放行,傳 `old=None` 卻當新行逐格檢查。
- 具體例:
  - 舊筆記有一行 `RULE:某限制 [依據:人]`,缺 since、retire、confirmed。
  - 輸入:`summary-line 節點 "[依據:人]" "[依據:人] [since:2026-10-15]"`,補一格、其餘仍缺,專案格子開關為 block。
  - 預期:提交時是舊行,放行,工具也該放行。
  - 照 spec:rc2 擋下。
  - 後果:舊行無法逐格補、也無法更新 `[confirmed:]`,只剩手改開頭欄位,這正是 d1 要消除的做法。
  - 對照:第 4 點 `summary-add` 全是新行,傳 None 沒問題,問題只在第 6 點沿用。
- 佐證:`scripts/lumos` 的 `_ns_slot_line_problems(line, old, commit_time, head=None)` 與 `_ns_is_old`;`_summary_line_locked` 手上有 `old_line`。
引句:「擋不擋照 `_ns_slots_mode` 讀到的專案開關:block 就 rc2 不寫、warn 寫入並印提醒、off 不看」

### F2 summary-add 沒要求新行有前綴,形狀與格子檢查全部空轉
severity: major
blocking: 是(d1 的承諾是寫前跑提交時同一套檢查,這個輸入會繞過)
- spec 段落:〈做法〉1 第 1 點、S3。
- 問題:第 1 點的輸入檢查只擋空行、換行、單行值摘要,沒要求新行以 `RULE:` 等合法前綴開頭。`_ns_slot_line_problems` 對不是 `SYMBOL_RE` 開頭的行直接回 `[]`;`_ns_check_line` 同樣只看有前綴的行。
- 具體例:
  - 輸入:`summary-add 節點 "前端頁面還沒做,程式在 scripts/lumos:1234"`,沒有前綴。
  - 預期:rc2,因為摘要每行必有前綴、行號引用會被提交擋。
  - 照 spec:兩道檢查都空轉,寫入成功。
  - 後果:同縮排的無前綴行讓 `_ns_summary_logical` 的 `last` 歸 None,成為不屬於任何條目的孤行,不受任何格子規則管。
- 佐證:`scripts/lumos` 的 `_ns_summary_logical`、`_ns_slot_line_problems` 開頭的 `SYMBOL_RE.match`。S3 的三種壞輸入也沒列「無前綴」。
引句:「輸入:新行去頭尾空白後不得是空的、不得含 `str.splitlines` 認得的換行類字元(同 summary-line 那條檢查,抽成一支共用)」

### F3 B1(b) 教的 `git restore --source` 對新增的實作檔會失敗
severity: major
blocking: 是(擋下訊息要印的步驟,在示範的原始情境走不通,S25 的測試卻照樣會綠)
- spec 段落:〈做法〉10 B1(b)、實務隱患(b)。
- 問題:動機是示範代理「把新檔搬走跑紅再搬回」,實作檔是新檔。`git restore --source=<實作前的提交> -- <新檔>` 在來源提交裡沒有該路徑,git 直接 `error: pathspec ... did not match any file(s) known to git`,rc1。我在臨時 repo 實測過。
- 具體例:
  - 實作是新檔 `web/api.js`,測試 import 它。
  - 照訊息操作 → git 報錯。
  - 就算換成移走檔案,測試因 import 失敗是「跑不起來」,依實務隱患(b)算弱證據、不算紅,規格閘仍擋。
  - 所以新檔實作沒有任何一條可走通的補法。
  - 只有「改既有檔」的實作才走得通。
- 佐證:實測 `git restore --source=HEAD -- new`(new 不在 HEAD)→ error,rc=1。
引句:「用 `git restore --source=<實作前的提交> -- <實作的程式檔>` 把實作檔暫時換回實作前的版本(測試檔留現在的)」

### F4 F29 逐條件判斷,忽略推送閘是「全部條件成立才算」
severity: major
blocking: 是(lint 會對推送不會擋的行說「推送會擋」)
- spec 段落:〈做法〉5 第 3 點、S13。
- 問題:推送閘 `_drift_probe_line` 是「一行的全部條件成立才成立,有一個 False 就是 False」。第 3 點對「三種條件」各自判,沒說一行有多個條件時要整組判。
- 具體例:
  - 輸入:`REVISIT:[when-file:scripts/lumos][when-test:scripts/test_lumos.py::t_new] ...`,檔現在就在,新測試還沒寫。
  - 預期:整組 False(t_new 不存在),推送不擋,lint 不該唸。
  - 照 spec:`when-file` 命中就唸「推送時漂移檢查會擋下,請改日期」。
  - 後果:誘導作者把正確的組合條件改掉。
  - 另外:含 `when-symbol`、`when-test` 的組合是「判不了」(None),spec 沒說該不該唸。
- 佐證:`scripts/lumos` 的 `_drift_probe_line`、`_drift_probe_check`(「在終點評估全部條件」)。
引句:「三種不用讀程式內容就判得出的條件」

### F5 F29「跟 HEAD 比」會讓已提交、未推送的新寫條件漏唸
severity: minor
blocking: 否(lint 本來只是提醒,推送閘仍擋)
- spec 段落:〈做法〉5 第 2 點。
- 問題:推送閘比的是推送範圍起點,lint 比的是 `HEAD`。作者先 commit 再跑 lint 時,新條件已在 HEAD,被當舊行跳過,而推送閘仍把它當新寫擋下。
- 具體例:commit 後才 `lumos lint`,條件原樣在 HEAD → 不唸 → 推送被擋。
- 佐證:`_drift_probe_judge` 的 `old` 是範圍起點版本;spec 自己把「已提交」歸為 drift scan 範圍。
引句:「用 `git show HEAD:<這篇>` 讀上一個提交的版本(一次,只這一篇)」

### F6 B3 只在審查帳找不到留痕時才讀治理帳,多機時會誤判過期
severity: minor
blocking: 否(往嚴的方向錯,重跑規格閘可解,但重跑會撞 B1(b))
- spec 段落:〈做法〉10 B3 讀的規則、B1(a)。
- 問題:消費專案的審查帳是各機器本機的。機器 A 的本機帳有舊留痕(token1)。機器 B 改條款後重跑,新留痕(token2)只進治理帳。A 拉下後,審查帳「有」舊留痕,不去讀治理帳,指紋對不上被判過期。B1(a) 的「相符留痕」也只看審查帳,於是落到 B1(b) 的硬擋與手動補跑流程。
- 具體例:同一人先後在兩台機器上作業(依序,不違反威脅模型),A 推送被擋。
- 佐證:`_spec_gate_latest_records` 取審查帳最後一筆。
引句:「推送閘有候選計劃在審查帳找不到留痕時,才讀一次治理帳」

### F7 「若」當條件開頭詞會誤吞「若干」
severity: minor
blocking: 否(只是提醒,且可關)
- spec 段落:〈做法〉4 記號 3、S11。
- 問題:記號 3 要求「在它前面出現」若、如果…,是子字串比對。
- 具體例:`若干接口還沒實作` 是現況句,應照列,「若」讓它被豁免。
- 佐證:`_NS_NEG_SEG_CUT_RE` 只在標點切段,同一小段裡「若干」會落在否定字眼前面。
引句:「在它前面出現條件或時序開頭詞「若、如果、假如、要是、一旦、等到、只要、這時、此時」」

### F8 開頭編號數不一致
severity: minor
blocking: 否(文字精度)
- spec 段落:白話段、〈名詞〉、範圍表。
- 問題:白話段寫「F、G、H 三組 17 個編號」。〈名詞〉與範圍表實際列了 F8、B6、W8、B7、F14、F17、W9、F29、F6、F9、W5、B8、B9、W6、B1、B11、B2、B3、W10、F15,共 20 個,字母是 B、F、W,沒有 G、H。
引句:「這份把 F、G、H 三組 17 個編號收成 11 節」

### 其他節
已讀,無 finding:
- 〈做法〉2(set 說明)
- 〈做法〉3(append 的 lands_in 正規化;正規化後再去重,順序可行)
- 〈做法〉6、7、8(單看規則)
- 〈做法〉9 B9
- 〈做法〉10 B2、B11、W10:
  - W10 搜過現有測試,沒有斷言該警告的,不會因模組層集合而順序相依。
  - B2 的候選迴圈已含 `touched_plans`,只需放寬 `full` 的狀態判斷。
- 〈做法〉11
- 風險類:
  - 守衛面:B1(a) 的放行條件綁指紋加規則版本,沒看到放寬漏洞。
  - 舊帳相容:見 F6。
  - 在途分支:無,各提交獨立。
  - 跨計劃交界:無新增。

最嚴重 severity:major;blocking 共 4 條(F1、F2、F3、F4)。
