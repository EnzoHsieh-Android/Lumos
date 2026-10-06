severity: major

審稿立場:極端輸入。以下實測都對真帳(docs/.canary-log.jsonl,403 個迴圈、約 2.9k 列)與 governance/review-reports/(339 個資料夾)算過。未改任何 repo 檔。

### F1 凍結不會被「處置閘第八步」擋住:d3 的理由與 S5 的 rc 2 都沒有對應的現有機制
severity: major
blocking: 是 — 照 spec 實作,凍結擋點(d3 取代 d1 的唯一理由)不會生效,S5 的測試要嘛寫不出來、要嘛逼出 spec 沒寫的凍結新邏輯。
- 段落:frontmatter d3、§做法三、條款 S5、§回退。
引句:「凍結(`loop replay --freeze`)在內部重跑處置閘,所以凍結也一併擋;回放(`--golden`)照「落點」那步的慣例以凍結當下的判定為準,不重判這一步。」
- 凍結跑兩趟處置閘。第一趟(帶 spec)只檢查 `rc == 2`;rc 1(FAIL)不會停,verdict.json 照寫,現況下 FAIL 的迴圈本來就能凍結。
- 第二趟(正式寫進 verdict 的那趟)帶 `spec_sha_override=spec_sha_frozen`。spec 要求這步「照落點那步的接法」,而落點那步在 override 非 None 時直接 skip,所以第二趟一定跳過第八步。
- 輸入:跑滿、沒有 cap-retro.json、其餘七步過的迴圈 → `loop replay X --freeze --spec …`。第二趟 rc=0,凍結成功,verdict 裡 fails 不含回顧。
- S5 要求「回 2 不寫凍結檔」,但程式裡 rc 1 只是記進 verdict 的 `{"rc","fails"}`。要擋得自己加「第一趟 fails 含跑滿回顧就回 2」之類的分支。spec 沒寫這個分支,也沒說會不會順便擋住其他步驟的 FAIL,而現況是不擋的。
- 「凍結時寫進判定閉包」沒有機制。閉包的 `files` 只由帳列的 report/snapshot 路徑(再加資安席列)組成,回顧檔不在任何帳列上。
- 就算硬塞進 `files`,有兩個副作用。凍結前置檢查要求它已 commit(`_replay_git_blob`)。事後改了回顧檔(例如改跳過理由),回放會報「凍結檔被動」紅。這與 §回退「回放照凍結當下為準,不受回退影響」衝突。
- 引句:「回顧檔的 sha256 跟收貨紀錄一樣要能重算:問閘時把路徑與指紋印出;凍結時寫進判定閉包。」
- file: `scripts/lumos:1059-1073` 兩趟的呼叫,第一趟只看 rc==2(1060 行),第二趟帶 override。
- file: `scripts/lumos:1111` verdict 只存 rc 與 fails,不拒凍。
- file: `scripts/lumos:22646-22652` 落點那步在 override 非 None 時 skip。

### F2 證據格式 `F<n>` 標題與真實席報告大面積對不上:約五分之一的跑滿迴圈只能走「跳過」
severity: major
blocking: 是 — 「至少一條 evidence、檔裡有 F<n> 標題」對這批迴圈不可能滿足,合格回顧只剩跳過,規則被架空。
- 段落:§做法一 `families.evidence`、S6。
引句:「檔案要在同一個卷證資料夾,而且檔裡有以 `F<n>` 開頭的 markdown 標題(`### F3 …` 這種,跟收貨格式一致)。」
- 實測:2026-09-20 之後開的 113 個迴圈中,72 個會跑滿,占 64%。這 72 個裡有 16 個(22%),所有輪、所有席的報告都找不到 `^#{2,6} F<n>` 標題。這 16 個是:併發與效能表態要合約背書、code-併發與效能表態背書、筆記標籤-過時判定與按需載入、筆記格子寫法與過期檢查、code-筆記格子第0到3步、舊行插字不算新寫、舊行尾追加不算新寫、code-舊行尾追加不算新寫、code-回頭條件寫法補齊、回頭條件消失式與生來成立、code-回頭條件消失式與生來成立、gov-ledger-split、code-過期鎖收斂修復。
- 這些報告用 `**[1] …**` 或 `**R1 …**` 當發現標題。例:`governance/review-reports/筆記格子寫法與過期檢查/r1-資源併發-sonnet.md` 第 5 行是 `**R1 推送時…**`;`併發與效能表態要合約背書/r1-邊界-sonnet.md` 用 `**[1]`。
- 整體來看,近期非 clean 的席報告約 254 份沒有 F 標題,對 738 份有。
- 輸入:上述任一迴圈要寫 families → 無任何合法 `<檔名>#F<n>` 可引 → 只能走 `skipped`。
- 後果:這些迴圈的族別永遠進不了 `--stats`,而且推高跳過次數,逼近 RETIRE-IF ③「填跳過理由的次數多過真的寫了回顧的次數」。
- spec 說「跟收貨格式一致」並不成立。收貨端對發現段的辨識是 `^\s{0,3}#{2,6}\s*F\d+(?![.\d])`,排除 fenced 區塊、F1.1 子標題、標題含「已驗過/無」的段。spec 沒說 evidence 檢查是否沿用這支。
- 如果不沿用,放在 fenced code 裡的假 `### F1` 或 `F1.1` 子標題都算證據,「只保證指到真的那一條」的誠實界線也破功。
- file: `scripts/lumos:8695` 既有的 F 標題判法。

### F3 固定檔名 `cap-retro.json` 與共用資料夾衝突:改版編號各自跑滿會互相覆蓋或判不合格
severity: major
blocking: 是 — S11 自己承認 `-v2` 共用資料夾,但回顧檔名固定、`loop` 欄必須等於本迴圈編號,同資料夾第二個跑滿的迴圈無處可放。
- 段落:§做法一「位置」、S11。
引句:「位置:判定輪席報告所在的資料夾(由帳上判定輪的 `report_path` 推出),檔名 `cap-retro.json`。」
- 實測:帳上有 17 個資料夾被兩個以上編號共用。about-code-field(v1、v2、v3,v3 已 3/3 跑滿)、code-ablation-probe(本編號跑滿、`-2` 共用)、節點範圍與索引守衛(v1 到 v4)。
- 輸入:code-ablation-probe 之後 `-2` 也跑滿 → 要在同資料夾寫 `cap-retro.json`。
- 後果:覆蓋前一份,舊迴圈 `loop` 不符變不合格,doctor 又列出舊迴圈缺回顧;或兩邊永遠有一邊不合格。
- 檔名要含編號才能共存,spec 沒處理。`--stats` 與 doctor 由編號反推資料夾時,同一資料夾的檔也會被讀到好幾次。

### F4 round-less(循序單審、light)的跑滿規則在處置閘到不了第八步,或到了也只能跳過
severity: major
blocking: 是 — S10 宣稱「不帶輪次…跑滿時處置閘與 doctor 照樣判」,但閘本身對這形狀的行為與 spec 的假設相反。
- 段落:§適用範圍第三條、S10。
引句:「設計審與代碼審、帶輪次與不帶輪次的都算;它們都要問處置閘(代碼審循序單審也問 `--disposal`)。」
- `_loop_status_disposal` 對無輪次帳列帶 `findings_set`(處置結果)直接 rc 2,不進後面步驟。沒有載體時,只要某列 findings 不是 0,就判「判定輪有發現但無處置帳」FAIL。
- 結果是 round-less 的迴圈只有「全部 findings=0 的空輪」才能過閘。這種迴圈沒有任何 `F<n>` 標題,families 的 evidence 不可能填,只剩跳過。
- 其餘情況(有發現)根本到不了或過不了第八步,retro 對它們無意義。
- 輸入:light 兩筆帳、都有發現 → 閘 FAIL「無處置帳」,與回顧無關。輸入:light 兩筆都 0 發現 → 閘過,第八步只能填跳過。
- 實測 2026-08-15 以後的 round-less 迴圈(不含 `auto-*` 自動迴圈)只有 5 個,2026-09-29 以後的 `代碼審資料狀態鏡頭`(light 2 筆)是少數會碰到上限的例子。
- 還有一個口徑問題。「同一席先留痕一筆、再當載體一筆」(`_review_yield_round` 註解)的帳形,在 round-less 下一輪佔兩筆,筆數即輪數會把單輪當成跑滿。這點 spec 沒說明,我沒在真帳找到實例,⚠ 判不準。
- file: `scripts/lumos:22738-22742` round-less 帶 findings_set 直接 rc 2。
- file: `scripts/lumos:22782-22793` 無載體且非全零的 FAIL 分支。

### F5 跑滿占大多數,「跑滿」成常態:每個迴圈都多派一個代理,RETIRE-IF 的兩個觸發條件都不可能觸發
severity: minor
blocking: 否 — 成本與設計取捨,spec 已寫「代價」,但規模與其退場條件沒對上。
- 段落:§名詞「跑滿」、RETIRE-IF、d2。
- 實測:2026-09-20 之後 113 個迴圈中 72 個(64%)輪數 ≥ 上限。standard 三輪 31 個、high 三輪 27 個、四輪以上 11 個。連設計審與其對應的代碼審各算一個,同一功能常要兩份回顧。
- 規則實際變成「幾乎每個迴圈收尾要多派一個乾淨代理+寫一份 JSON」。RETIRE-IF ② 的「連續三個月零次跑滿」永遠不會成立;①、③ 才是會動的,且受 F2 的 22% 只能跳過影響。
- 上線日以當日 00:00 起算(落點慣例)。合進主線當天已開、已經跑到一半的迴圈(包括本案自己的設計審迴圈)會被整個劃進適用範圍,與 §舊迴圈「上線日以前開的不回溯」的意圖不符。

### F6 手冊落點只掛在「到頂沒過 → 停」,但要回顧的主力是「剛好在最後一輪過閘」
severity: minor
blocking: 否 — 閘會印 `--template`,不至於沒人知道,但手冊與規則目標不一致,且 S12 計數錯。
- 段落:§五、S12、§名詞。
引句:「後面都接「跑滿就要寫回顧」與指令。」
- 現有四處(`skills/lumos-design-loop/reference.md:542`、`SKILL.md:65`、`skills/lumos-code-loop/SKILL.md:59`、`skills/lumos-project-notes/commands/05-設計審查迴圈.md:29`)都是「到頂沒過 → 停」。另有 `skills/lumos-code-loop/reference.md:586` 同句,spec 沒列。
- 實測 72 個跑滿迴圈裡,67 個是過了處置閘(gov 帳有 converged)。接在「沒過」那一句後面,過了閘的情境(多數)手冊沒指到。
- S12 寫「三處到頂段」,但 spec 自己列了四處(reference.md、design SKILL.md、code SKILL.md、commands/05),加上 code-loop reference.md 共五處,數量對不上。

### F7 回顧檔的壞輸入、巨大檔、證據路徑沒有「不合格」規則
severity: minor
blocking: 否 — 一個壞檔會讓 doctor/--stats 整支炸,而不是只標那一個迴圈不合格。
- 段落:§二 `--check`、S6、§實務隱患「效能」。
- spec 的 S6 只列欄位缺陷,沒寫:非 UTF-8、壞 JSON、JSON 根不是物件(`[]`、`null`)、`families` 不是清單、`rounds` 元素非字串、巨大檔(沒有大小上限)。落點那步已有對應慣例(讀不了回 abort/fail,不 traceback)。
- 輸入:cap-retro.json 內容為 `[]` → `--check` 取欄位拋例外。`--stats` 與 doctor 掃全部迴圈時沒說每個迴圈要獨立 try,一個壞檔就讓整段掃描中止。
- evidence 路徑:`<檔名>#F<n>` 若寫成 `../別的迴圈/r1-x.md#F1`、絕對路徑、符號連結,或檔名本身含 `#`,spec 沒說怎麼切(最後一個 `#`?)、是否擋 `..`/絕對路徑/符號連結。「在同一個卷證資料夾」不足以判定。
- 效能:§實務隱患寫「判定輪那幾份席報告的標題」,但 evidence 可指任何一輪的檔,實際會讀所有被引的檔,沒設上限。
- `--template` 直接呼叫 `_cap_hint_round` 沒有防護:帳上 `reported` 欄壞值(如 `"abc"`)會讓 `_review_yield_round` 的 `int(...)` 拋例外。閘裡的 `_cap_hint_print` 專門 try/except 吞掉這種例外,而 `--template`(閘要使用者去跑的指令)沒有,會在剛需要它時炸。
- file: `scripts/lumos:8801-8825` `_review_yield_round` 內 `int(r["reported"])`。
- file: `scripts/lumos:8865` `_cap_hint_round`(無防護);`scripts/lumos:8893` `_cap_hint_print` 的 try/except 對照。

### F8 「跳過」與「乾淨代理」都只是自我宣稱,且不留不可竄改的痕
severity: minor
blocking: 否 — spec 已在 RETIRE-IF ③ 與〈誠實界線〉承認部分風險,但具體缺口沒列。
- 段落:§一「跳過」、§三第二點、§五。
- `skipped: {reason, by}` 只要 `reason` ≥10 字,內容不查。回顧檔是版控內的可改檔,spec 又決定「不另寫治理帳事件」,所以事後把有效回顧改成跳過、或刪檔重寫,都沒有 append-only 的帳可對。「sha256 能重算」只有凍結才有可比的值,沒凍結的迴圈沒有。
- `drafted_by != completed_by` 只比字串。輸入:`drafted_by` 填這個迴圈裡的某個審查席名(如 `正確性-opus`)、`completed_by` 填 `orchestrator` → S6 全過,但「沒參與這個迴圈的乾淨代理」被違反。工具可以拿帳上 `auditor` 集合比對,spec 沒寫。
- §五說「編排者再補 avoid 與 changes」,檢查只看字數(≥20 字),起草者與編排者的欄位分工在檔內看不出來。
- 回顧在輪 3 問閘 FAIL 時就會印 `--template`;若人裁再多跑一輪(實例:code-存量漂移防線甲 6 輪、code-殺傷力配方失配提醒 5 輪),先寫好的回顧 `rounds` 與帳不一致而失效。spec 沒寫「到頂後再加輪」時回顧何時才算定稿。

## 逐節判讀
- frontmatter / PRIOR-ART / RETIRE-IF:除 F5 的 RETIRE-IF 規模問題外已讀,無 finding。
- 一句話 / 名詞 / 為什麼要做:已讀,無 finding。引用的 `Systems/loop-convergence-recording`、`Projects/審查跑滿上限提示_計劃`、`Projects/新增告警閘_計劃` 與各手冊檔都存在。
- 適用範圍:F4、F5。
- 做法一:F2、F3、F7、F8。
- 做法二(`--template`/`--check`/`--stats`):F7;`--stats` 掃全帳 2.9k 列、162 個跑滿迴圈只是單次讀一遍,規模無問題。
- 做法三:F1。
- 做法四(doctor):無獨立 finding(併入 F3、F7)。
- 做法五:F6、F8。
- 回退:與 F1 的 replay 完整性有衝突(見 F1),其餘已讀,無 finding。
- 實務隱患:併發 — 無,只讀帳與卷證,不寫帳(唯一寫入是人與代理寫回顧檔,不與 lumos 程式競爭;但同資料夾共用見 F3)。效能 — 見 F7 的「讀所有被引檔」。回滾 — 無新問題,同〈回退〉。
- 條款 S1 到 S12:S5 見 F1、S6 見 F7/F2、S10 見 F4、S11 見 F3、S12 見 F6。其餘已讀,無 finding。

## 前掃升級的 p1(擋點從凍結前改到處置閘第八步,d1→d3)
- 方向判斷合理:凍結是手冊步驟、程式不強制(spec 說法與 `cmd_loop_replay` 現況相符),擋在凍結前會讓沒凍的迴圈整個繞過。
- 但 d3 的理由「凍結時處置閘會在內部重跑,所以凍結也一併擋」不成立,見 F1。D3 的 valid:true 與 S5 要待 F1 修完才站得住。
- 同時 d3 把「跳過」寫進回顧檔(不另開旗標、不寫治理帳),見 F8,代價是失去 d1 原本的治理帳痕。

（本案無固定席節點附件。）

總結:最嚴重 major,blocking 4 條
