severity: major

審查範圍:逐節讀完 r1-snapshot.md,並對照 `scripts/lumos`、`scripts/test_lumos.py` 與審查帳 `docs/.canary-log.jsonl`(3024 列、404 個迴圈)。固定席節點:hook 沒有附,不適用。

### F1 「凍結重跑處置閘所以一併擋」與程式現況不符,S5 與「指紋寫進閉包」跟「回放不重判」互相矛盾
severity: major
blocking: 是 — 照 spec 做,凍結不會被擋;若另補專用判斷,又會破壞凍結檔的既有慣例,或讓閉包指紋反過來害回放誤紅。
- spec 段落:決策 d3、〈三、處置閘第八步〉、S5。
- 引句:「凍結時處置閘會在內部重跑,所以凍結也一併擋;回放以凍結當下為準不重判。」
- 引句:「凍結(`loop replay --freeze`)在內部重跑處置閘,所以凍結也一併擋」
- 現況:
  - `cmd_loop_replay` 凍結模式跑兩趟 `_loop_status_disposal`。第一趟(活 spec、不帶覆寫)只在 rc==2 時中止,rc==1(FAIL)直接放行;第二趟帶 `spec_sha_override`,只用來產 verdict,同樣不因 rc==1 拒凍。
  - 現行測試 `t_disposal_security_seat_freeze`(`scripts/test_lumos.py:44022` 起)接受「凍結後 verdict rc=1、fails 含資安席」。凍結 FAIL 的迴圈是合法用法,verdict 會記 `{"rc":1,"fails":[...]}`。
  - 所以「處置閘多一個 FAIL 條件」本身擋不了凍結。S5 要回 2、不寫凍結檔,得在凍結端額外寫「只有第八步 FAIL 才拒凍」的特判,spec 沒寫。其他任何步驟 FAIL 照凍,只有這一步拒凍,規則不一致。
- 矛盾一(第二趟被略過):spec 說第八步照「落點」那步接法。`_disposal_landing_step` 在 `spec_sha_override is not None` 時直接回 "skip"。若第八步照做,第二趟(凍結 verdict 那趟)就略過這步,verdict 的 fails 永遠不含「跑滿回顧」。
  - 具體輸入:跑滿、缺回顧的迴圈,凍結 rc 0、verdict 記 rc 0/fails 空,凍結檔留下「通過」的判定。
  - 要擋就得改讀第一趟的 `out`。第一趟用活 spec,可能因 G3 失敗而與第二趟不同構,這正是現有程式註解說兩趟要分開的原因。
- 矛盾二(指紋與回放):spec 說「凍結時寫進判定閉包」回顧檔指紋,又說「回放…不重判這一步」。
  - 閉包的 `files` 目前只收各列 `report_path` / `snapshot_path`。回放時對每個 files 驗 sha,不符就紅「凍結檔被動」。
  - 若回顧檔進 `files`,日後任何人補字、修筆誤,回放都報假紅。這份檔是活文件,`--stats` 還要讀它。
  - 若不重判,這個指紋就沒有消費者。
  - 另外 `files` 要求檔案已進版控(`_replay_git_blob`),spec 沒說回顧檔要先 commit 才能凍。
- 「問閘時把路徑與指紋印出」只印到 stdout,沒有任何地方存。`_loop_gov_mark` 只寫「disposal gate PASS」,所以「跟收貨紀錄一樣要能重算」只有凍結閉包可重算,而凍結閉包的做法已如上自相矛盾。
- 判決:p1 問的「破壞既有判定或回放」——依 spec 的接法,不破壞既有 goldens,因為上線日前的迴圈皆 skip。凍結與回放的一致性沒有被破壞,是根本沒接上。
- file: `scripts/lumos:1058-1076` 第一趟只擋 rc==2、第二趟帶 override。
- file: `scripts/lumos:22653-22655` 落點步在 override 時略過。
- file: `scripts/lumos:1118-1128` `files` 只收各列 report/snapshot。
- file: `scripts/lumos:1220-1230` 回放帶 `spec_sha_override` 重算並比對 fails。

### F2 `-v2`、`-b`、`-2` 這類改版編號共用資料夾,但每個資料夾只有一個固定檔名 `cap-retro.json`,多個跑滿迴圈會互相覆蓋
severity: major
blocking: 是 — 同資料夾的兩個迴圈只要都跑滿,至少一個永遠過不了閘或每次都互相作廢,實作者必須決定檔名規則,spec 沒給。
- spec 段落:〈一、回顧檔〉位置;S11。
- 引句:「位置:判定輪席報告所在的資料夾(由帳上判定輪的 `report_path` 推出),檔名 `cap-retro.json`。」
- 引句:「`loop`:審查編號,要等於帳上的編號。」
- 查證:帳上 17 個資料夾被兩個以上迴圈共用,每個迴圈的判定輪 `report_path` 都指到同一個資料夾(我寫小腳本按判定輪 `report_path` 的資料夾分組算出)。
  - `about-code-field`:{`about-code-field`, `-v2`, `-v3`}。
  - `code-ablation-probe`:{`code-ablation-probe`, `-2`}。
  - `code-兩席相反時端出張力`:{原編號, `-v2`}。
  - `節點範圍與索引守衛`:`-v2` 到 `-v4`。
- 具體失敗:`code-ablation-probe`(跑滿)與 `code-ablation-probe-2` 若兩個都跑滿。
  - 先寫的 retro 內 `loop` = 前者。後者問閘讀同一檔,`loop` 不等於帳上編號,不合格。
  - 後者若覆寫,前者即時重算閘(閘是讀側重算,不是一次性)從 PASS 變 FAIL。
  - 兩者交替互相作廢。
  - 這與已凍結的前者 verdict 無關(回放不重判),但前者之後任何即時問閘都 FAIL。
- spec 自己把共用資料夾列為動機(S11 與「帳上 415 個編號有 108 個沒有同名資料夾」),卻沒處理檔名衝突。〈名詞〉「卷證資料夾」把資料夾與迴圈視為一對一。
- 檔名至少要含審查編號,例如 `cap-retro-<編號>.json`。

### F3 回顧檔路徑由判定輪 `report_path` 推出:缺值、絕對路徑、各席不同資料夾、帳長大後判定輪移動,四種形狀都沒定義
severity: major
blocking: 是 — 實作者必須自己決定「推不出路徑時」是 FAIL、skip 還是 rc2;選錯會出現「閘判不過卻無處可寫回顧、跳過也無處可寫」的死路。
- spec 段落:〈一、回顧檔〉位置、S7、S11。
- 引句:「位置:判定輪席報告所在的資料夾(由帳上判定輪的 `report_path` 推出),檔名 `cap-retro.json`。」
- 引句:「輸出應帶好 `loop`、`rounds` 與回顧檔路徑(由判定輪 `report_path` 推出)」
- 帳上查證:
  1. 缺值:404 個迴圈中,判定輪完全沒有 `report_path` 的有 38 個。這些是帶輪次或不帶輪次的舊帳。
     - spec 適用範圍明說要含不帶輪次與 light,且 light 上限只有 2。
     - 帳上 36 個無輪次迴圈全數沒有 `report_path`。這類迴圈跑滿時,路徑無法推導,`--template` 印不出路徑,`--check` 沒地方找,skip 也沒地方寫。
     - spec 沒說這種情形怎麼辦。`_disposal_security_step` 對 `__seq` 判定輪另有特殊處理,正是因為這類帳列欄位不全。
  2. 絕對路徑:`code-精簡版update指令` 的 r2 列 `report_path` 是 `/Users/enzo/.claude/projects/.../subagents/agent-….jsonl`(repo 外)。若它是判定輪,retro 會被推到家目錄下的 subagents 資料夾。
     - 凍結端對絕對路徑明確拒絕(`cmd_loop_replay` 的「卷證在 repo 外」)。
     - 回顧檔放這裡既不在版控、也不能進閉包。
  3. 同輪各席不同資料夾:spec 只說「判定輪席報告所在的資料夾」,沒說多席時取哪一席。帳上目前沒有同一輪席位分居不同資料夾的實例,但 `report_path` 是自由字串,`canary record --report` 不驗資料夾。
     - 不同資料夾時回哪一個、是否 rc2,都沒定義。
     - 同輪還有 `report_path` 空與非空混雜的可能。
  4. 判定輪移動:retro 的 `rounds` 必須與帳「一致」,而帳是 append-only。
     - 跑滿且 FAIL(cap-reached)後人裁多給一輪(帳上有 `code-最低python版本改3-14` 4 輪、`code-存量漂移防線甲` 6 輪的實例),判定輪從 r3 換成 r4。
     - 原 retro 的 `rounds` 少一輪,不合格;路徑也可能換資料夾。spec 的 `--check` 沒說這是「回顧作廢要重寫」。
     - 對照〈五、誰來寫〉:retro 要在處置閘通過前寫,而處置閘通過常常與人裁加輪同時發生,順序沒有定義。
- file: `scripts/lumos:22513-22516` 對 `__seq` 判定輪的特殊處理,說明這類帳列欄位不全。
- file: `scripts/lumos:1085-1092` 凍結對絕對 `report_path` 直接拒絕。

### F4 `--check` 對合法回顧的誤擋與空洞回顧的放行
severity: minor
blocking: 否 — 不影響閘的判定正確性,主要是可用性與防空填的強度;spec〈誠實界線〉已承認歸族不保證正確。
- 空洞放行:`families` 一項即可、`evidence` 只驗「檔案存在且有 `F<n>` 標題」,不驗該 F 是否屬於 `rounds` 所列的那一輪;`why_cap`、`avoid` 只驗 20 字長度;`drafted_by != completed_by` 只是兩個字串不同。
  - 具體輸入:編排者自己填 `drafted_by:"x"`、`completed_by:"y"`,任挑一份報告的任一 `### F1`,`family:"other"` 加 10 字備註,即合格。`drafted_by` 沒有對帳上席名,也無法確認起草者真的「沒參與」。
- 空洞放行:跳過路徑只需 `reason` 10 字。
  - 引句:「回顧檔只寫 `v`、`loop`、`rounds`、`skipped: {reason, by}`(`reason` 至少 10 字)也算合格」
  - 決策 d1 原本要求「記治理帳」,d3 改成不寫治理帳事件。跳過只剩檔案本身,而檔案可被覆寫、刪除(RETIRE-IF ③ 的統計依賴這份檔)。
- 誤擋:evidence 要求檔裡有 markdown 標題 `### F3`。`governance/review-reports` 下我數到的席報告檔(排除 intake)共 2808 份:1010 份有 `#…F<n>` 標題;66 份有以 F<n> 開頭、但不是標題的行;其餘 1732 份兩種都沒有。
  - 舊格式的報告無法被引用為證據,只能走 `other` 空填或跳過。例:`Codex行為精修/r1-邊界可執行.md`、`code-metric-guard/r2-seat.md`。⚠ 這 1732 份裡含非報告檔,實際誤擋面我沒逐份分類。

### F5 「跑滿」的涵蓋面:輪數 ≥ 上限在現行帳上幾乎等於常態,light 也納入
severity: minor
blocking: 否 — 屬於範圍取捨,實作可依 spec 做;只是 RETIRE-IF 與成本估計沒有跟著現實。
- 帳上 2026-09-12 以後開的 149 個迴圈,依 spec 算法有 89 個算跑滿,約 60%。其中標準檔多數就是第 3 輪收斂。
- spec 把「剛好第 3 輪過閘」也算跑滿,等於大多數迴圈都要多派一個代理加一份回顧。
  - 引句:「本案刻意把「剛好在最後一輪過閘」也算進來」
  - RETIRE-IF ②「連續三個月零次跑滿」在這個比例下永遠不會觸發。
- light 的上限是 2(`_TIER_PARAMS["light"]=(1,2)`)。`_cap_hint_scope` 刻意排除 light,spec 卻納入。
  - 帳上 `code-資料狀態鏡頭`、`code-測試py39相容` 等 light 迴圈各兩輪就算跑滿。
  - Enzo 的原話是「滿三輪的都要收集」,light 兩輪不在其內。
  - 「照 `loop next` 同一套」對 light 帶輪次的帳沒有對應判法:`cmd_loop_next` 對這種帳直接 rc2 擋下。
- file: `scripts/lumos:11711` `_TIER_PARAMS`。
- file: `scripts/lumos:8895` `_cap_hint_scope` 排除 light。

### F6 沒問閘就留通過紀錄的缺口:可接受,但 d3 的「代價」漏了這一條
severity: minor
blocking: 否 — spec 已在〈三〉末與〈誠實界線〉承認並掛 REVISIT:2026-12-05,屬已揭露的天花板。
- 查證:`cmd_code_loop`(`scripts/lumos:45066` 起)的 `pass` 路徑沒有讀處置閘結果或 `converged` 治理帳標記。spec 對「本來就不回頭驗」的描述屬實。
- 判斷:缺口對「第八步」的影響與既有的「條款綁定」「資安席」「落點」三步相同,不是新增的弱點,可以接受。
- 問題在決策紀錄:d1 否決「只提醒」的理由正是「只提醒的規則容易被跳過」。d3 的實際效果是「問閘的人才被擋」,而代碼審的推送前掛鉤看的是 `code-loop pass`,不是處置閘。代碼審佔跑滿迴圈的大宗,在不問閘的路徑上,這步實質上只剩 doctor 提醒。
  - 引句:「由下一節的 doctor 提醒兜底。」
  - d3 的「代價」欄應補一句「不問閘的代碼審只被 doctor 提醒」。

### 其餘各節
- 一句話、名詞、為什麼要做、適用範圍的上線日規則(`keys and min<since`,帳列全有 `ts`,實測 0 個迴圈缺 `ts`):已讀,無 finding。
- 〈四、收工體檢提醒〉、〈五、誰來寫〉、〈回退〉:已讀,無 finding。若 F1 照現狀(第八步不入 verdict),回退確實不影響已凍結的閉包。
- 〈實務隱患〉:
  - 併發:「只讀帳本與卷證檔,不寫任何帳」對閘本身成立。但 `cap-retro.json` 由代理以一般寫檔產生,非原子寫;閘讀到半寫入的檔會遇到 JSON 解析失敗。spec 未規定「壞 JSON」是 FAIL 而不是 traceback,S2/S6 沒有涵蓋。寫成 FAIL 即可,併入實作。
  - 效能:doctor 與 `--stats` 掃全部跑滿迴圈(目前約 89 個)的小 JSON,各讀一次 3000 列帳本與幾份報告標題,量級可忽略。無問題。
  - 回滾:見〈回退〉,無問題。

總結:最嚴重 major,blocking 3 條
