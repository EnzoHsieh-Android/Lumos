severity: major

設計審 回滾-sonnet(依鏡頭:我是要收拾殘局的人)

白話:這份設計把「擋推送」的門裝得很牢,但退路只寫了一條「整道回退」。門卡死時,唯一的小出口(例外)要靠一把還沒釘、又很脆的金鑰。以下先列所有入口,再列同族發現。

## 一、入口清單與「誤擋要退回時怎麼辦、帳救不救得回」

| 入口 | 擋或寫什麼 | 誤擋或要退回時 | 帳救得回? |
|---|---|---|---|
| E1 code-loop check 新判定(本機 pre-push 與 CI push 事件) | 擋推送 | 只有「例外」或「整道回退」。沒有 `gate: warn` 設定,也沒有單次跳過(見 F1) | 無帳可救 |
| E2 治理帳「資安背書」(本機算好寫入) | 寫 `docs/.governance-log.jsonl` | 撤回後舊行留著。舊讀者容忍未知 gate:`_gov_vc_gate_events` 按 gate 名過濾,`_gov_event_types_ok` 只驗欄位型別 | 救得回,無害 |
| E3 治理帳「例外使用」記帳 | 每次用到例外就寫一行 | 同上 | 救得回,無害 |
| E4 merge-base 凍結比對與 `revisions` 核可修訂 | 重算必驗集合 | 見 F2、F5 | 部分救不回 |
| E5 `.lumos/security-approvers` 金鑰清單與簽章核對 | 例外失效或整道擋 | 見 F3、F4 | 救不回 |
| E6 `lumos update` 發給所有專案(上線第 3 步) | 分發新判定 | 回退要另發版本,消費端自己沒有關的辦法 | 見 F1 |
| E7 schema v2 | 登記圍欄改版 | 見 F6 | 舊工具讀不了 |

## 二、發現

### F1 沒有降級開關和單次跳過,「誤擋」的退路只有整道回退
spec 段落:〈回退〉、〈舊專案升級的過渡〉、〈四〉擋下條件。

問題:本 repo 的同類閘門都留了出口,這道沒有。
- `node_home.gate`、`note_shape.gate`、`drift_check.gate`、`note_reread.gate` 都能設成 `warn`。
- `LUMOS_SKIP_NOTE_SHAPE`、`LUMOS_SKIP_DRIFT_CHECK`、`LUMOS_SKIP_REREAD_CHECK` 都能單次跳過並留帳。
- 這份 spec 的 Q4(過渡期)還沒裁,就算裁了「要」,也沒有任何設定鍵可以實現它。

具體例:order-demo 登記 OD-01 到 OD-04 為 active,OD-03、OD-04 沒證據,所以被擋。這是 spec 自己說的預期行為。
- 想退路:例外要由「母提交版清單裡的金鑰」簽,但〈例外核准用簽章金鑰〉寫「在那之前所有例外都不算數」。上線順序又沒有「先釘金鑰」這一步。
- 改把 OD-03、OD-04 降成 candidate:這是被降級的必驗條目,要核可修訂紀錄,紀錄也要金鑰簽,同樣死鎖。
- 結果只剩「改 lumos 版本回退」或 `--no-verify`。`--no-verify` 讓 CI 的 push 事件照樣紅,而 main 已經收下了那個提交。

照 spec 做:實作者不會加降級開關,上線後第一個誤擋只能整道撤。

修法方向(判準,非鑿死做法):
- 〈四〉要加專案端 `security_evidence.gate: warn|block` 這類開關。
- 〈六〉上線順序要把「先釘金鑰」排在 order-demo 開閘之前。
- 〈回退〉要寫消費端自己怎麼退。

引句:「誤擋時不准在執行中把判定改成通過;照〈四〉的例外流程由使用者限時放行,或整道回退。」
引句:「在那之前所有例外都不算數」
引句:「是否給一段只提醒不擋的過渡期、多長」
佐證:
- ``file: `scripts/hooks/pre-push:501` ``、`:513`、`:651`、`:677` 各有 gate=warn 或 SKIP 的逃生句。
- ``file: `.github/workflows/ci.yml:187` `` CI 對 bound-tests 也有跳過。

severity: major
blocking: 是(照 spec 實作會做出「誤擋沒有退路」的壞系統)

### F2 「整道」類代碼沒有任何出口,其中環境型的任何提交都修不好
spec 段落:〈四〉擋下條件、〈原因代碼〉的「整道判不清」列。

問題:
- 例外只蓋「護欄 × 種類」,見彙總規則 1、3。`freeze_base_unavailable`、`commit_unavailable`、`unexpected_empty`、`read_incomplete`、`registration_error`、`approvers_change_unsigned` 屬於整道,不在任何例外的蓋住範圍。
- 其中前兩個是環境決定的,改任何檔都不會變綠:
  - 本機淺層 clone,
  - 沒有 `origin/main` 的 worktree,
  - 新專案第一個根提交就帶登記。
- 〈四〉只說「起點算不出來而有登記痕跡:擋」,沒有出口。

具體例:新建專案的根提交就含 `lumos-security-v1` 圍欄,沒有 merge-base,推送被擋。要退只能刪登記,但刪登記在凍結比對下又算「被刪的必驗條目」,同樣需要簽章的核可修訂紀錄(見 F1)。

引句:「起點算不出來(沒有 merge-base、全零起點找不到真起點)而專案有資安登記痕跡」
引句:「護欄層有問題就是 unsound,例外蓋不掉」
佐證:本 repo 其他閘遇淺層 clone 是跳過並記帳,例如 ``file: `scripts/lumos:40987` `` 的 REREAD 跳過記進治理帳。

severity: major
blocking: 是(判不清擋、卻不給任何一條能走通的路)

### F3 簽章金鑰遺失、輪替或被刪檔時沒有復原路,且「母提交沒這個檔」可被利用
spec 段落:〈例外核准用簽章金鑰〉的「公鑰清單本身的修改」與「第一次釘金鑰」。

問題:
- 只有一把金鑰時,例如硬體金鑰壞了或密碼忘了:
  - 所有例外失效,
  - `.lumos/security-approvers` 無法再修改(`approvers_change_unsigned` 整道擋),
  - F1 的降級修訂也簽不出來。
  - spec 沒有 break-glass 流程,也沒要求至少兩把金鑰。
- 「母提交還沒有這個檔」被當成「第一次釘金鑰」,而第一次由使用者手動完成,工具驗不了。
  - 刪檔是不是「修改」沒寫。
  - 推送若是多個提交的範圍,spec 沒說是逐提交核對還是只核對最前端與其母提交。
  - 若只核對最前端與其母提交,AI 在同一次推送放兩個提交:先刪檔,再以自己的金鑰重建。最前端的母提交沒有檔,就被當成第一次釘金鑰而放行。

具體例:範圍 [刪 `.lumos/security-approvers`; 新增含 AI 公鑰的同名檔],只看「最前端 vs 它的母提交」,母提交沒檔,判成合法首釘。

引句:「的每次修改,也要由母提交那一版清單裡的金鑰簽」
引句:「母提交還沒有這個檔時,沒有現有金鑰可驗」
佐證:spec 全文沒有「逐提交走完 before..sha」的措辭。S26 的四份樣本也沒有「刪檔」和「範圍內先刪後建」。

severity: major
blocking: 是(漏洞加不可復原,實作者會做錯)

### F4 例外靠 `git blame` 找「最後改到的提交」,在本專案的壓縮與重寫流程下會被無聲洗掉
spec 段落:〈例外核准用簽章金鑰〉的「找出要驗的提交」。

問題:blame 到的提交必須有效簽章。
- 本專案慣例是「做到一半的本機提交,推之前壓成一個」,見專案 CLAUDE.md〈提交與推送〉。
- 簽章綁在原提交上。壓縮或 rebase 會產生新提交,簽的人變成當時的提交者。要重簽每個提交,而且每次簽章都要實體觸碰。
- AI 的任何格式化、regen、`lumos set` 動到那幾行,最後改到的提交就換成 AI 的未簽提交,例外靜默失效。
- GitHub 的 squash 合併會讓 main 上的提交變成 web-flow 的簽章,不在釘住清單。

具體例:使用者簽好例外提交,AI 依慣例把分支壓成一個再推。blame 指向 AI 的未簽提交,`exception_unsigned`,原本放行的推送被擋。出口(例外)自己最脆,而且是在你最需要它的時候脆。

引句:「找出最後改到那幾行的每個提交」
引句:「本機推送前與 CI 跑的是同一段核對,資料都來自 git 歷史,所以兩邊判定完全相同。」
佐證:專案 CLAUDE.md 寫「做到一半的本機提交,推之前壓成一個」。S26 沒有「壓縮或 rebase 後的簽章」樣本。

severity: major
blocking: 是(照字面實作,例外在常態流程下就會被洗掉)

### F5 `revisions` 核可紀錄放在「被刪的那個節點」,節點被刪就讀不到
spec 段落:〈四〉的「核可修訂紀錄」。

問題:
- spec 自己寫「被刪的條目整個不在了,紀錄就留在原 Systems 節點的 `revisions` 裡」。
- 如果要刪的是整個 Systems 節點(整個模組下線),節點本身不在要推的提交裡,紀錄也隨之消失。
- 結果是 `missing:control_removed_unapproved`,沒有任何地方能放有效紀錄。
- 節點改名或搬家時,舊節點的圍欄被視為被刪,新節點的同 id 是否算同一條,也沒寫。

具體例:下線一個帶資安護欄的模組,把它的 Systems 節點整篇刪掉。紀錄無處可放,推送被擋,F1 與 F2 都沒有出口。

引句:「被刪的條目整個不在了,紀錄就留在原 Systems 節點的」

severity: major
blocking: 是(合法的下線操作無路可走)

### F6 回退宣稱「證據、清單、例外都留著,撤回只是不再讀」,但 schema v2 舊工具讀不了;v1 圍欄在新工具的處置也沒寫
spec 段落:〈回退〉、〈一〉契約變更點。

問題:
- 現有 v1 解析器對 `schema_version` 不是 1 就直接拒絕:``file: `scripts/lumos:6989-6992` `` 的訊息是「schema_version 只支援 1」,整篇登記不採用。它對未列欄位也拒收:``file: `scripts/lumos:6995-6997` ``。
- 所以消費專案一旦把圍欄升成 v2,回退到舊 lumos 後,`security list` 會報 `unknown_schema_version`。回退並不是「只是不再讀」。
- 反方向:order-demo 現有的是 v1 圍欄。新工具若只認 v2,升級當下整篇「登記錯誤」,再被〈四〉的「讀取不完整或登記錯誤且有痕跡 → 擋」整道擋住,而此時金鑰也沒釘(F1)。
- spec 說「只多認 v2 新欄位」,但沒寫 v1 圍欄在新工具裡是照 v1 解讀、還是升級才認,也沒寫 v1 圍欄缺 v2 新必填時的行為。

具體例:`lumos update` 發新版,order-demo 的 v1 圍欄被判登記錯誤,整個專案推不出去,出口見 F1、F2。

引句:「消費專案的證據檔、工具清單、例外紀錄都留著不刪,撤回只是不再讀。」

severity: major
blocking: 是(兩個方向的相容矩陣沒定,實作者會做出升級即全擋)

### F7 回退的兩個提交其實不獨立,且撤 ② 要連動改另一篇計劃與測試常數
spec 段落:〈回退〉、〈四〉要跟著改的地方。

問題:
- spec 說「閘門呼叫的是同一支判定函式」,即 ② 依賴 ① 的函式,所以不能單撤 ①,只能先撤 ② 再撤 ①。〈回退〉的措辭暗示可各自撤。
- ② 要改 `_cl_say_block`、`pp_cl_reason`、`_PPC_KIND_SENTENCES` 加第五句,還要改〈推送前一次列出全部擋下原因_計劃〉那一行成「五句」。
  - 撤 ② 時若那篇計劃的行沒一起撤,`t_prepush_cl_reason_sentences_match_plan` 會因為「恰好四句」對「五句」而紅。
  - spec 沒說這行歸哪個提交。

引句:「實作分兩個提交可以各自撤」

severity: minor
blocking: 否(撤的時候測試紅一次就會發現,不會做出壞系統,但回退清單不完整)

### F8 時鐘觸發的擋下:同一個提交隔天就從放行變擋下,CI 在合併後才翻紅
spec 段落:〈四〉例外核可與記帳、〈二〉依賴掃描 14 天(Q5)、review 的 `expires_on`。

問題:
- 例外到期、`vulndb_stale`、`review_expired` 都隨日期變,不需要任何提交。
- 本機推送前通過的分支,到 main 的 push 事件再跑 CI 時可能剛好過期。spec 的「兩邊判定完全相同」(F4 的引句)只在同一時刻成立。
- main 上已經收下的提交被標紅後,後續任何推送(包括修它的推送)都要先補新證據或新例外。證據要跑工具,依 d4 需使用者核可;例外要金鑰簽。在無人看顧的流程裡,這個狀態停住就是停住。
- S25 只測了「隔天恢復擋」,沒測「本機放行與 CI 擋」的時間差。

引句:「每次判定都用當天日期重算,過期隔天自動恢復擋」

severity: minor
blocking: 否(是設計本意的副作用;補一句 CI 與本機的時間差處置與一份 S25 樣本即可)

### F9 抽出 `test_quality.check()` 核心時沒寫「既有行為與測試照舊」的條款
spec 段落:〈證據從哪來〉fault_sensitivity 路徑 ②。

問題:
- spec 要求「閘門要先把核對本體抽成只吃資料的函式」。
- 對 SARIF 抽 uri 正規化,有寫「抽出前後既有測試照綠、抽不乾淨就兩邊各寫」;對 `check()` 沒有同樣的條款。
- 〈Verification/測試品質第四輪修補驗證〉與 test-quality-cli 是直接相依。

引句:「`check()` 現在吃 argparse 參數並寫輸出檔,閘門要先把核對本體抽成只吃資料的函式。」(此行含反引號,僅作位置指引)

severity: minor
blocking: 否(補一句不變量條款即可)

## 三、附加節點判定

- `Systems/test-quality-cli`(家):spec 要動 `scripts/test_quality.py` 抽函式。只要 F9 補上「抽出前後 CLI 輸出與既有測試不變」就不破壞;現況沒寫,所以標 F9。
- `Systems/lumos-cli-lifecycle` ★INVARIANT★(re-inject 只覆蓋 sentinel 內、sentinel 外 byte-equal):不影響。這份設計不碰 CLAUDE.md 的注入與 sentinel;`lumos update` 的版本變更說明是另一條路,與該合約的行為無關。
- `Verification/測試品質第四輪修補驗證`:同上,依賴 F9 的不變量條款。
- `scripts/hooks/pre-push`、`scripts/test_lumos.py`、`scripts/lumos`(太泛):各有一處綁死的測試,即 `t_prepush_cl_reason_sentences_match_plan`。改法已寫(F7),只是回退清單漏了。

## 四、已讀無 finding 的部分
- 〈一〉區隔與彙總規則、〈二〉各格式合格判準、〈三〉工具接入:從回滾角度看,這幾節只讀不寫,撤掉不留狀態,已讀無 finding。
- 治理帳新行:舊讀者容忍未知 gate(``file: `scripts/lumos:11439-11540` `` 的 `_gov_event_types_ok` 與 `_gov_row`),撤回無害。

最嚴重 severity:major,blocking 共 6 條(F1、F2、F3、F4、F5、F6)。
