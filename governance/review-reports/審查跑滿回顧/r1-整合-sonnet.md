severity: major

審稿角度:三個月後接手實作與使用的人。未動 repo 任何檔,只讀碼、查圖譜、對帳本做唯讀統計。
前掃升級的 p1(擋點從凍結前改到處置閘第八步,d1→d3)我單獨判:方向沒跟處置閘的 ★INVARIANT★(第五步條款綁定)或 loop-convergence-recording 打架。圖譜沒有「改制回測」節點登記合約,只有「replay 唯讀、治理帳零寫入」被標成 INVARIANT 候選。但 d3 的落地說法有三處跟程式現況對不上,見 F1。

### F1 「凍結也一併擋」不成立:凍結現況不因處置閘 FAIL 而停,回放與凍結又走同一個旁路
severity: major
blocking: 是 — 照 spec 實作,S5 與「回退」節的敘述無法同時成立,接手者會做出不一致的行為
- 段落:〈做法 三〉第三、四點、S5、〈回退〉。
- 引句:「凍結(`loop replay --freeze`)在內部重跑處置閘,所以凍結也一併擋;回放(`--golden`)照「落點」那步的慣例以凍結當下的判定為準,不重判這一步。」
- 問題一:凍結現況擋不住 FAIL。
  - file: `scripts/lumos:1056-1062` 凍結第一趟呼叫 `_loop_status_disposal`,只有 `rc == 2` 才 `return 2`,`rc == 1` 會繼續寫 verdict。
  - file: `scripts/lumos:1089-1093` 帳面判定存成 `{"rc": rc, "fails": ...}`,凍結本來就容許把 FAIL 判定存起來。
  - 實測 `governance/replay/*/verdict.json`:220 份裡有 3 份是 `rc=1, fails=['留痕']`。
  - 所以「所以凍結也一併擋」是 spec 臆測。S5「應回 2 不寫凍結檔」要求新增行為:凍結第一趟若 `fails` 含「跑滿回顧」就停。spec 沒寫這個改動,也沒說為何只對這一步改。
- 問題二:凍結第二趟與回放無法區分。
  - file: `scripts/lumos:1066-1068` 凍結第二趟(`spec_sha_override=spec_sha_frozen`,真正存進 verdict 的那趟)與回放(`scripts/lumos:1224-1226`,同樣傳 `spec_sha_override`)用同一組旗標。
  - 「落點」那步靠 `spec_sha_override is not None` 就跳過(`scripts/lumos:22654-22656`)。第八步照這個接法,凍結第二趟也會跳過,存進 verdict 的 fails 永遠不含這一步。
  - 要擋凍結,只能靠第一趟(override 為 None)額外讀 `out["fails"]`。這是新分支,spec 只寫「照落點接法」,沒說。
- 問題三:回顧檔指紋寫進閉包與「回放不重判、不受影響」衝突。
  - 〈做法 三〉說「凍結時寫進判定閉包」。
  - file: `scripts/lumos:1178-1190` 回放第②步對閉包 `files` 逐一驗 sha,不符就 `red`(「凍結檔被動」)。這是檔案完整性檢查,跟「重判」無關。
  - 〈回退〉說「回放照凍結當下為準,不受回退影響」。但回顧檔事後只要被改(例如補 `changes[].ref` 的落地提交),週跑回放(`governance/autonomous_loop/replay_weekly.py`)就紅燈。
  - 回顧檔的設計本來就是事後補行動項,等於預設會被改。
  - 「指紋進閉包」要嘛不做,要嘛明講回顧檔凍結後唯讀。spec 兩者都沒說。
- 問題四:`_REPLAY_ENGINE_REV`(`scripts/lumos:8570`)是否 bump,spec 沒提。
  - 若為了納入新指紋改 verdict 結構而 bump,220 份存量 golden 全變「golden 過期」,要逐包重凍並留治理帳。
  - 若不 bump,新舊 verdict 欄位並存,spec 沒寫舊檔如何讀。
- 情境:接手者照 S5 寫測試。「凍結缺回顧回 2」要自己加第一趟檢查才過,但加了之後同一支檔 3 份既有 rc=1 的凍結先例行為不一致。

### F2 回顧檔固定叫 `cap-retro.json` 放在共用卷證資料夾,兩個共用資料夾的編號會互相覆蓋
severity: major
blocking: 是 — 〈一、回顧檔〉的位置規則與 `loop` 欄必須等於帳上編號兩條互相打架
- 段落:〈做法 一〉位置、`loop` 欄、S11。
- 引句:「位置:判定輪席報告所在的資料夾(由帳上判定輪的 `report_path` 推出),檔名 `cap-retro.json`。」
- spec 自己承認 `-v2`、`-std` 共用前一版資料夾。實測帳本:17 個資料夾被多個編號共用,例如:
  - `governance/review-reports/精簡版update指令` 的編號有 `精簡版update指令` 與 `精簡版update指令-std`
  - `about-code-field` 的編號有 `-v2`、`-v3`
  - `bound-tests-gate` 的編號有 `-b`、`-c`
- 問題:`loop` 欄要等於帳上編號。同資料夾兩個編號都跑滿(light 2 筆跑滿後升級成 `-std` 再跑滿 3 輪,或 v1 跑滿後 v2 又跑滿)時,只有一個檔名可用。
  - 後寫的覆蓋前一份,前一個編號的回顧立刻變不合格(`loop` 欄不符)。
  - 處置閘第八步 FAIL、doctor 永遠唸。
  - S11 只測「路徑照 report_path」,沒測兩個編號共檔名。
- 順帶:`evidence` 的 `<檔名>#F<n>` 同樣假設資料夾內檔名(`r1-<席名>.md`)唯一,v1 與 v2 的 r1 會同名,指到哪一邊不確定。
- 檔名要帶審查編號(例如 `cap-retro-<編號>.json`),或 spec 明寫共用資料夾時怎麼分。

### F3 light(與 round-less)被算成「跑滿」,但處置閘第八步永遠不會被問到
severity: major
blocking: 是 — S10 的條款在現行流程下無法觸發,doctor 會對合法流程永久告警
- 段落:〈適用範圍〉第一、三點、S10、〈四、收工體檢〉。
- 引句:「設計審與代碼審、帶輪次與不帶輪次的都算;它們都要問處置閘(代碼審循序單審也問 `--disposal`)。」
- 現況一:light 不問處置閘。
  - file: `skills/lumos-design-loop/SKILL.md:52` 寫明 light 不帶 `--round`、不記處置帳,閘只問 `--light`。
  - file: `scripts/lumos:13236` `disposal = panel_fmt and not light and ...`,light 永遠走 `--gate --light`。
  - light 上限是 2 筆(`scripts/lumos:11711` `_TIER_PARAMS["light"]=(1,2)`),所以「2 筆就算跑滿」。
  - 實測 2026-09-15 後的帳:light 有 5 個編號,其中 3 個跑滿(2 筆)。
  - 這些迴圈永遠不會被處置閘問到第八步,只會出現在 doctor 清單。doctor 的 `--template` 指令對 light 也無處可寫(判定輪是「筆序 #2」,沒有輪的卷證結構)。
- 現況二:round-less 且有發現的迴圈根本過不了處置閘。
  - file: `scripts/lumos:22740-22745` round-less 帶處置結果直接 rc2。
  - file: `scripts/lumos:22780` 之後沒 carrier 且有發現 → FAIL「無處置帳」。
  - 所以只有「末筆 0 發現」的 round-less 才可能過閘。
  - 2026-09-15 後只有 1 個 `standard` round-less 迴圈。S10 與 `#1/#2` 筆序命名在做一條近乎不存在的路。
- 升級路徑:SKILL.md:16/52 的 light 升 `-std` 是同資料夾新編號(見 F2)。light 那個編號的「跑滿」由 doctor 永遠唸,而沒有任何一條合法流程能消掉它。
- 「S10 跑滿時處置閘…照樣判」對 light 為假。要嘛 light 與 round-less 排除出範圍,要嘛 spec 寫 light 怎麼被擋(它不問處置閘,擋不到)。

### F4 loop next 在末輪過閘但缺回顧時,會被標成 cap-reached 並叫人停手
severity: minor
blocking: 否 — 訊息誤導與帳上暫時多一筆事件,補回顧再問即自癒
- 段落:〈做法 三〉、〈名詞〉跑滿。
- 引句:「這跟 `loop next` 的 cap-reached 不同——cap-reached 只算「到上限還沒過」;本案刻意把「剛好在最後一輪過閘」也算進來」
- file: `scripts/lumos:13236-13250` `loop next --spec` 對新迴圈呼叫處置閘(`readonly=True`);`rc != 0` 且 `rounds_count >= cap` 就 `_loop_gov_mark(... "cap-reached")` 並印「跑滿 N 輪還沒收斂——停下來,剩下的交給人裁決」。
- 第八步加入後,「末輪其餘七步全過、只缺回顧」變 rc=1,於是落進這個分支:
  - 治理帳寫一筆 `cap-reached`。
  - 輸出叫編排者去攤給人裁,而不是去寫回顧。
  - 接手者照手冊(code-loop SKILL.md:59「到頂沒過 → 停,攤給人裁」)停手。
- 補回顧再問後會有 `converged`,`gov --stats`(`scripts/lumos:8145`)因「有 converged 就不算 capped」而自癒;但中間那筆事件與訊息是錯的。
- 實測 2026-09-15 後約 135 個迴圈中 80 個(high 39、standard 40、其餘雜項)達上限,所以這個誤導訊息是常態路徑。
- spec 未提 `loop next` 路徑。

### F5 手冊落點只列三處,實際至少五處;觸發語意「到頂沒過」與跑滿(含末輪過閘)對不上
severity: minor
blocking: 否 — 只影響手冊同步,S12 是 manual 驗收
- 段落:〈做法 五〉、S12。
- 引句:「後面都接「跑滿就要寫回顧」與指令。」
- 實際「到頂沒過 → 停」的句子:
  - file: `skills/lumos-design-loop/SKILL.md:65`
  - file: `skills/lumos-design-loop/reference.md:332` 與 `:542`(同一句出現兩次,後者在「舊頭版/入口頁舊版全文」段內)
  - file: `skills/lumos-project-notes/commands/05-設計審查迴圈.md:29`
  - file: `skills/lumos-code-loop/SKILL.md:59`
- spec 說「三處到頂段」,漏數(reference.md 有兩份、SKILL.md 與 reference.md 是不同檔)。S12 只靠人讀,漂移沒有守衛。
- 語意問題:這些句子的前提是「到頂**沒過**」。但 spec 把「末輪剛好過閘」也算進跑滿(實測占達上限迴圈近半),那種迴圈走的是「過閘 → pass」路徑,不會讀到這些停手句。編排者要等問閘 FAIL 才發現要補回顧,手冊沒在「過閘後」路徑提醒。

### F6 彙整數字撐不起「改審查方式」:行動項落地無法統計,「無責/乾淨代理」只是形式檢查
severity: minor
blocking: 否 — spec〈誠實界線〉承認歸族主觀;這裡補的是 `--stats` 與 RETIRE-IF 實際算不出來的部分
- 段落:〈做法 一〉`changes`/`drafted_by`、〈二〉`--stats`、RETIRE-IF ①。
- 引句:「上線三個月內寫了 5 份以上回顧,卻沒有任何一條行動項真的落地(規則、工具、派工詞或手冊有對應提交)」
- 問題:
  - `changes[].ref` 是自由文字,`--check` 不驗檔案或提交存在。`--stats` 的「落點分布」只能數 `target` 分類,算不出「真的落地」。RETIRE-IF ① 沒有機械讀法,三個月後沒人能判。
  - `drafted_by ≠ completed_by` 只比字串,不比對該迴圈帳上的審查席名。編排者隨手填兩個不同標籤就過。spec 把「乾淨代理」寫成 d2 的核心理由,卻不檢查。
  - 同一輪可多族並列、族別有重疊(`same-family-unswept` / `fix-induced` / `scope-too-big`),`--stats` 以「出現在幾個迴圈」計數,沒有分母(該分級跑滿迴圈總數)、也不分 light/standard/high,tier 差異會混在一起。
  - 跳過(`skipped`)沒有族別資料,跳過率高時統計偏誤,spec 只用 RETIRE-IF ③ 處理。
- 情境:兩個月後 `--stats` 顯示「same-family-unswept 出現在 6 個迴圈」,接手者無法判斷是樣本偏、起草者差異還是真的問題,更看不出對應行動有沒有做。

### F7 觸發頻率讓回顧變常態,RETIRE-IF ② 與成本沒對上
severity: minor
blocking: 否 — 設計取捨,但 spec 的假設與帳本實測相反
- 段落:〈名詞〉跑滿、RETIRE-IF ②、d2 代價「每次跑滿多派一個代理」。
- 引句:「連續三個月零次跑滿」
- 實測 2026-09-15 後約 135 個迴圈中 80 個達上限(high 53 個裡 39 個、standard 76 個裡 40 個)。「滿三輪」是多數、不是例外。
- 結果:
  - 大約每三個迴圈就有兩個要多派一個乾淨代理起草。
  - RETIRE-IF ② 幾乎不可能成立。
  - 失去「例外才回顧」的篩選功能,易退化成填表(RETIRE-IF ① 自己的擔憂)。
- 跳過出口寫在回顧檔裡且不寫治理帳,CI 與別機看不到被跳過的頻率,只剩 `--stats` 掃檔能看。

## 其他已讀節
- 〈一句話〉〈為什麼要做〉〈誠實界線〉:已讀,無 finding。
- 平行路徑:Codex 編排時,派工詞走 `templates.md` §3 ④,不在此複述。第八步讀的是帳與卷證檔,與編排者無關,無 finding。自主迴圈 `/tmp` 工作區(帳上 2 個絕對路徑編號 `code-精簡版update指令`、`repro-pathbug`)在上線日前,不回溯,無 finding。
- 實務隱患:
  - 併發:無 — 只讀帳與卷證檔。但 F1 的「凍結閉包含回顧檔」會讓回顧檔被改時週跑回放紅燈,屬寫入後的完整性問題。
  - 效能:無 — 回顧檔與席報告標題都是小檔,doctor 掃約 415 個編號、跑滿者各讀一份小 JSON,量級可接受。
  - 回滾:風險見 F1 第三點,拿掉第八步本身沒有副作用,但凍結閉包若已含指紋,回放不會自動忽略。

總結:最嚴重 major,blocking 3 條
