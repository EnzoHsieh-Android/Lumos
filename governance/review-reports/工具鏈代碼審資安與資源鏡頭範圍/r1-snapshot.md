---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/pitfalls-code-loop
related:
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Projects/代碼審資安席_計劃]]"
  - "[[Systems/design-loop]]"
  - "[[Projects/必要合約清單_計劃]]"
  - "[[Systems/bound-tests-gate]]"
pending_questions:
  - id: Q1
    text: 設計審(散文 spec)在工具鏈本 repo 也要照同樣範圍收窄嗎(§1 審計員第 5 點併發題、§7 設計審 panel 的資源併發席)?建議:先不收窄,等代碼審新範圍跑一季再議
    class: 範圍
    stage: 需求
    status: 已決
    decision: "#d1"
  - id: Q2
    text: §3 代碼審派工詞第 1 點「冪等與併發」在工具鏈本 repo 要不要只留重跑與中途失敗、拿掉兩個請求同時進來與讀兩次中間被改?建議:要,跟新規則 2 一致
    class: 範圍
    stage: 需求
    status: 已決
    decision: "#d2"
decisions:
  - content: 工具鏈本 repo 的設計審不跟著收窄鏡頭範圍,只改代碼審
    id: d1
    context: 新範圍是使用者針對代碼審資安與併發席裁的;設計審也有併發題與資源併發席
    why_chosen: 使用者原話只講代碼審;先讓代碼審新範圍跑一季,有實際數字再議設計審,不擴大這次的改動面
    decided: 2026-10-14
    valid: true
  - content: 工具鏈本 repo 的代碼審派工詞第 1 點只留重跑與中途失敗,拿掉兩個請求同時進來與讀兩次中間被改
    id: d2
    context: 派工詞第 1 點的併發子題跟新規則 2(不審多人或多會談同時寫入)衝突
    why_chosen: 跟新規則 2 一致,否則同一個席位會被派工詞要求審新規則說不審的東西
    decided: 2026-10-14
    valid: true
---
# 工具鏈代碼審資安與資源鏡頭範圍_計劃

> 白話:lumos 是一個人在自己電腦上、讓 AI 依序操作的工具,不是雲端系統。所以審 lumos 自己的程式時,資安審查員只看三種真的會出事的洞(外部文字混進給 AI 的指令、讀寫跑到不該碰的地方、平常操作一步就意外繞過守衛),「有人刻意花好幾步偽造帳本或 git 內部」這類就不再追著加機制;原本的「併發與資源」審查員改成只看「資源」(殘留程序、逾時誤擋、記憶體與大輸入)。用 lumos 的其他專案照舊。

## 裁定來源

使用者 2026-10-14 原話:
- 「幫我思考一下，工具開發的併發鏡頭和資安鏡頭到底該不該存在，這工具是讓人在本機使用，並不是雲端系統，也需要這兩個鏡頭，耗費過度設計在這些防範上嗎」
- 之後裁定:「先照新範圍收尾手上五項,再開一份計劃把規則正式改掉。 但消費專案用舊規則」
- 更早(2026-10-13,待決問題改存開頭欄位代碼審第九輪):「先不用過度設計，只要思考中英文、一個人使用，全權讓AI操作的時候也沒什麼併發問題」

這份計劃只把上面的裁定落成正式規則與派工範本,不重新討論要不要。

## 現況:規則散在哪(2026-10-14 查)

查法:`lumos search "資安席 範圍"`、`lumos search "併發 鏡頭"`,再對 skills 與 scripts/lumos 全文搜「併發與資源」「資源併發」「§7.8」「_is_toolchain_repo」。

| 位置 | 現況 | 這次要不要改 |
|---|---|---|
| `skills/lumos-design-loop/templates.md` §7.8 資安席派工 | 一份派工詞給所有專案:六類清單(注入、登入權限、密鑰個資、加密、執行邊界、行動端)+依賴;「不報」只排 DoS、測試假資料、無攻擊路徑的輸入驗證 | 改:加〈工具鏈本 repo 的範圍〉段,原六類段一字不動 |
| templates.md §7.7 立場表「資源併發(W>3)」列 | 立場「最壞時序的安排者」,預設同時、重試、中途失敗都會發生 | 改:加工具鏈本 repo 的「資源」寫法 |
| templates.md §7 平行 panel「鏡頭各異」那行 | 列「(W>3)資源併發」 | 改:同一行補一句工具鏈本 repo 改資源 |
| templates.md §7.8「不報」裡的「歸併發資源席」 | 把資源耗盡交給併發資源席 | 改:補「工具鏈本 repo 歸資源席」 |
| templates.md §3 代碼審派工詞第 1 點「冪等與併發」 | 問重跑、兩個請求同時進來、讀兩次中間被別人改、對外重試 | 已決(d2):工具鏈本 repo 只留重跑與中途失敗 |
| `skills/lumos-code-loop/SKILL.md` 步驟 2 | 多席鏡頭列「正確性 / 併發與資源 / 邊界與輸入 / 合約與圖譜一致」;high 必派資安席、問閘會擋 | 改:鏡頭列後補一句工具鏈範圍,指向 §7.8 |
| `skills/lumos-code-loop/reference.md` 步驟 2 列席位處 | 同上一份鏡頭列 | 改:同一句 |
| `skills/lumos-project-notes/commands/06-代碼審與推送.md` 第一列 | high 必派資安席(§7.8,問閘會擋) | 改:補一句工具鏈範圍 |
| scripts/lumos 編制表 `_TIER_ROSTER` 的 `("code","high")` | 席位叫 鏡頭1~5(沒寫鏡頭名)+ `資安`(required-gated) | **不改**:見〈不改的部分〉 |
| scripts/lumos 處置閘資安席一步(`_gated_seats_for`、`_disposal_security_step`) | 定錨 high 的代碼審要有資安席帳列、報告 sha 對、看過的檔涵蓋最後一版 | **不改**(使用者指定) |
| [[Systems/pitfalls-code-loop]] 決策 d6 與摘要 KEY 行 | 「高風險代碼審一律必派資安席(所有專案,工具鏈自己也算)」 | 不改 d6;新增決策 d8(d7 已被「擋推鏈改成會跑檢查工具」占用)與兩條 RULE 行 |
| [[Projects/代碼審資安席_計劃]] | d6 的單源;KEY 寫「工具鏈自己也納入」 | 不改正文;只在 related 補一條連到本篇(讓讀它的人知道範圍後來收窄) |
| [[Systems/bound-tests-gate]] 一條 WHY(sitecustomize 那條)的 `[因:]` 括號 | 寫「工具鏈本身的資安只看提示注入、讀寫越界、非刻意的一步繞過;2026-10-14 使用者確認」,出處是口頭 | 改:括號改成指向本案落地的 RULE,見〈做法〉7(那條所在的分支 2026-10-14 已合進主線) |
| 使用者記憶 `toolchain-review-lens-scope`、`lumos-threat-model-single-user` | 以記憶形式寫了同一個範圍(記憶不算規則) | 不在 repo;落地後編排者把記憶改成只指向 [[Systems/pitfalls-code-loop]] |

圖譜裡另有一個先例:[[Projects/必要合約清單_計劃]]〈威脅模型:防忘記,不防繞過(2026-09-22 Enzo 裁定)〉,以及 [[Projects/代碼審資安席_計劃]]〈承認的限制〉「帳本是本機 append-only 檔,改得動它的人也改得動程式;這是整個記帳制度的共同天花板」。本案把這個天花板從「各案各自承認」變成「資安席派工時就講明不追」。

## 怎麼分辨「工具鏈本 repo」

沿用 scripts/lumos 既有的 `_is_toolchain_repo(root)`:repo 根有 `skills/lumos-project-notes/SKILL.md` 就是工具鏈本 repo。這支檔是 user-scope skill 的唯一來源,`lumos update` 不會把它複製進消費專案(該函式說明與 `_self_repo_origin` 同一個判別鍵)。現有 6 處呼叫(推送前分級、提交前檢查跳過工具自裝檔等)都靠它,不另寫一套。

root 取法照 `loop next` 既有那支:`Path(repo).resolve() if repo else _vault_repo_root(env)`。

## 新規則

只套工具鏈本 repo 的代碼審;消費專案(用 lumos 的其他 repo)照舊。

1. **資安席照樣必派,處置閘那一步不動**。派工範圍只看三類:
   - ①提示注入:作者或外部可控的自由文字(筆記內容、檔名、分支名、帳本欄位、席報告)進到給 AI 的派工詞、hook 附加段或指令。
   - ②讀寫越界:讀寫跑到 repo 外、使用者全域設定、圖譜外,或照著外來路徑寫檔(含捷徑跟過去)。
   - ③非刻意、一步就能繞過的守衛:照平常操作一個指令或一次編輯就意外走過去(例:按一次 Ctrl-C、檔名帶空白或中文、舊版工具、合併提交、新分支首推)。
   - **範圍外(系統天花板)**:刻意多步偽造——偽造 git 內部物件或 ref、自己手填帳本欄位、換編號或改檔名重來、刻意設定環境變數讓閘提早回 0。席位找到時,編排者二選一:附理由放行(理由寫「範圍外:刻意多步偽造,見 Systems/pitfalls-code-loop RULE」);或文件裡原本宣稱擋得住它,就照實改文件拿掉那句不存在的保護說法,算折入。**不加機制**。
   - blocker 照處置閘規則不能放行;範圍外的 blocker 只能走「改文件拿掉保護說法」那條折。
2. **原「併發與資源」席在工具鏈本 repo 改成「資源」鏡頭**:孤兒行程(子程序沒收掉)、逾時誤擋(預算不夠把正常操作擋下或放行)、記憶體與大輸入耗時(大 diff、大帳本、深層巢狀)。不再審多人或多會談同時寫入的競態(兩個程序同時寫同一個檔、檢查與寫入之間被換檔)。
3. 消費專案的代碼審照舊:§7.8 原六類、併發與資源鏡頭都不變。

## 做法

1. **規則落點**:[[Systems/pitfalls-code-loop]](代碼審的家,d5/d6 資安席決策都在這篇)。
   - `lumos decision-add Systems/pitfalls-code-loop` 記 d8「工具鏈本 repo 代碼審的資安與併發鏡頭收窄」(工具會自動配下一個編號;d7 已被占用),四欄:context=上面三句原話;alternatives=①照舊(每輪被偽造類發現拖著加輪)②整個拿掉資安席(使用者要留)③所有專案一起收窄(使用者指定消費專案照舊);why_chosen=工具單人本機、AI 依序操作,偽造類要先能改帳本與程式,改得動的人也改得動閘;trade_offs=工具鏈本 repo 不再有人找刻意偽造與多會談競態。不 supersede d6(d6 的「必派、處置閘會擋」照舊)。
   - 摘要加兩條 RULE 行(用 `lumos append` 或 regen 指令寫,不手改開頭欄位):
     - `RULE:工具鏈本 repo(根有 skills/lumos-project-notes/SKILL.md)的代碼審,資安席只看提示注入、讀寫越界、非刻意一步就能繞過三類;刻意多步偽造(git 內部物件或 ref、手填帳本欄位、換編號或改檔名重來、刻意設環境變數)是系統天花板,附理由放行或改文件拿掉不存在的保護說法,不加機制;消費專案照舊 [依據:人] [since:2026-10-14] [retire:人裁] [until:2027-04-14] [confirmed:2026-10-14]`
     - `RULE:工具鏈本 repo 的代碼審,原併發與資源席改成資源鏡頭,只看孤兒行程、逾時誤擋、記憶體與大輸入耗時,不審多人或多會談同時寫入的競態;消費專案照舊 [依據:人] [since:2026-10-14] [retire:人裁] [until:2027-04-14] [confirmed:2026-10-14]`
   - [[Projects/代碼審資安席_計劃]] 用 `lumos append … related` 補一條連到本篇,正文不動。
2. **templates.md §7.8**:在現有派工詞圍欄之後加一段〈工具鏈本 repo 的範圍〉,說明「`lumos loop next` 印出『鏡頭範圍: 工具鏈本 repo』時,改用下面這份」,附一個獨立圍欄:同樣的開頭與 LUMOS-SEAT 行、同樣的席名 `資安-<模型>`(處置閘靠席名認)、同樣的攻擊路徑四件與嚴重度錨;「逐類想過」換成上面三類;「不報」多列範圍外那幾種手法並寫「看到可以順手提一句,標 minor、blocking: 否」。原本那個圍欄一字不動,開頭補一句「消費專案用這份」。
3. **templates.md §7.7 與 §7**:立場表「資源併發(W>3)」列的預設姿態後補「工具鏈本 repo 的代碼審改資源鏡頭(設計審照舊,d1):你是**把機器資源用光的人**,預設子程序會殘留、預算會被大輸入吃光、記憶體會被翻倍輸入撐爆;不考慮兩個程序同時寫」;§7「鏡頭各異」那行的「(W>3)資源併發」後補「(工具鏈本 repo 的代碼審改資源,見 §7.7;設計審照舊)」;§7.8 原圍欄「不報」的「歸併發資源席」補「;工具鏈本 repo 歸資源席」。
4. **代碼審說明同步**:`skills/lumos-code-loop/SKILL.md` 步驟 2、`skills/lumos-code-loop/reference.md` 步驟 2 列席位處、`skills/lumos-project-notes/commands/06-代碼審與推送.md` 第一列,各補一句「工具鏈本 repo:資安席只看三類、併發與資源改資源鏡頭,見 templates.md §7.8〈工具鏈本 repo 的範圍〉;消費專案照舊」。
5. **`loop next` 印一行範圍**(唯一的程式改動):代碼審編號(編號以 `code-` 開頭,跟同一支指令裡修正關卡提醒的判法同一口徑;沒連字號的舊 `code…` 編號不印)、而且 `_is_toolchain_repo(root)` 成立時,在「應派」段後印(編制表算不出來、印「目前算不出該派誰」時也照印) `  鏡頭範圍: 工具鏈本 repo——資安席照 templates.md §7.8〈工具鏈本 repo 的範圍〉、併發與資源席改資源鏡頭(消費專案照舊)`;`--json` 多一欄 `lens_scope`,值 `toolchain` 或 `default`。設計審編號不印、`lens_scope` 為 `default`。消費專案輸出除了 JSON 多的那一欄,逐字不變。理由:派工範本是整台機器共用的 skill,編排者在消費專案也讀得到工具鏈那段;讓機器說「這裡是哪一種」,比靠編排者自己判可靠。
6. **測試**:新增 `t_loop_next_lens_scope_toolchain_vs_consumer`、`t_loop_next_lens_scope_design_untouched`、`t_templates_toolchain_lens_scope`、`t_templates_toolchain_resource_lens`、`t_toolchain_lens_scope_doc_sync`(照 `t_security_seat_doc_sync` 的逐檔列舉寫法)、`t_templates_rm_literal_absolute_path`、`t_templates_toolchain_idempotency_scope`;既有 `t_templates_security_seat_section`、`t_disposal_security_seat_required`、`t_roster_code_high_has_security_seat` 不改、要照樣綠。動到 test_lumos.py 要先過錨定簽核(`anchor approve`)。
7. **口頭出處改指規則**:把 [[Systems/bound-tests-gate]] sitecustomize 那條 WHY 括號裡的「2026-10-14 使用者確認」改成「見 Systems/pitfalls-code-loop 工具鏈資安範圍 RULE」(那條所在的分支已合進主線,本案一起改)。
8. 落地後:記憶 `toolchain-review-lens-scope` 改成只寫「去 Systems/pitfalls-code-loop 看 RULE」;`lumos-threat-model-single-user` 加同一個指標(兩篇在使用者目錄,不進提交)。
9. **派工詞的刪檔紀律**(2026-10-14 使用者裁,所有專案都適用、不限工具鏈):templates.md §0(所有派工詞共用的審查席規矩)加一條「刪檔一律寫成不含變數的字面絕對路徑,不准先 cd 到變數路徑再用相對路徑刪、不准 `目錄/*` 萬用字元、不准 `"$S/tmp"` 變數接路徑;派子代理時這條原文寫進派工詞」;§1、§3、§7.8 各份派工詞圍欄第二行(寫 `git -C <那個目錄>` 那句)句尾補「刪檔照 §0 那條寫字面絕對路徑」。理由:Claude Code 內建的關鍵路徑刪除保險絲在略過權限模式下照樣會問,官方文件明寫允許規則與工具前掛鉤都批准不了,無人看顧的子代理會卡兩分鐘再被拒、連三次之後同會談直接拒;目標事先算得出來才不觸發。
10. **§3 第 1 點「冪等與併發」的工具鏈範圍**(落實 d2):§3 是所有專案共用的代碼審派工圍欄,不另寫第二份;第 1 點句尾補「(工具鏈本 repo 的代碼審:「兩個請求同時進來」「同一次計算讀了兩次、中間被別人改了」這兩問不用答,見 §7.8〈工具鏈本 repo 的範圍〉;重跑與對外重試照問)」。中途失敗是另一條「寫一半」,照舊。

## 不改的部分與理由

- **編制表席名**:`("code","high")` 的鏡頭席本來就叫 鏡頭1~5,鏡頭名是派工時編排者給的,沒有程式認「併發」這個席名(查過 scripts/lumos,沒有比對併發席名的地方)。改名或拆表沒有好處,反而讓工具鏈與消費專案的編制表分岔。席報告的席名在工具鏈本 repo 寫 `資源-<模型>`。
- **處置閘資安席一步**:使用者指定不動;判法(席名、報告 sha、看過的檔涵蓋最後一版)兩種 repo 一樣。
- **資安席席名** `資安-<模型>`:處置閘靠它認席,不能因為範圍收窄就改名。
- **風險分級(`pitfalls --diff`)與推送前的棧別檢核題**:類軸與題目裡的「併發」照舊。規則講的是審查席看什麼,不是推送前要不要表態;表態題是另一道閘,要改另開。
- **d6 不作廢**:d6 是「必派而且會擋」,本案沒推翻它,只收窄工具鏈本 repo 的派工範圍。

## 不做

- 不改消費專案的任何派工、編制、閘。
- 不改設計審的鏡頭(§1 審計員第 5 點的併發題、§7 設計審 panel 的資源併發席);使用者這次講的是代碼審。已決不一起收窄(d1)。§7、§7.7 是兩種審查共用的段落,〈做法〉3 補進去的句子都寫明只限代碼審。
- 不加任何新機制去防範圍外的偽造;也不回頭把舊迴圈裡已經為偽造類加的機制拿掉(拿掉也是改動,要另外審)。
- 不改處置閘、`code-loop pass`、帳本格式。
- 不做「依 `.lumos/config.json` 宣告範圍」這類可設定開關:只有工具鏈本 repo 一種情況,沿用既有判別就夠。

## 承認的限制(附回頭條件)

- 範圍要靠編排者照 `loop next` 那一行選派工詞;資安席一步只看席名與留痕,看不出派工詞用的是哪一份。
REVISIT:2026-12-14 抽查工具鏈本 repo 本季高風險代碼審的資安席派工單(rN-dispatch.json 與席報告),看是否用工具鏈範圍;再抽 3 個消費專案的,看有沒有誤用工具鏈範圍,誤用一次就議把範圍做成派工鏡頭自動附
- 範圍外的手法被放行後,真實損害只會在事後被發現。
REVISIT:2027-04-14 人裁兩條 RULE 要不要續:數本 repo 卷證裡以「範圍外」放行的發現有幾條,事後有沒有任何一條造成真實損害(帳本或閘結果被意外改壞)

PRIOR-ART: ①同 repo 先例:[[Projects/必要合約清單_計劃]]「防忘記,不防繞過」、[[Projects/代碼審資安席_計劃]]〈承認的限制〉帳本天花板、[[Systems/存量漂移守衛]] 那條「只防疏忽、不防存心繞過」的 RULE;②世界解:OWASP Threat Modeling 先定攻擊者與信任邊界再列威脅(範圍外的威脅明寫接受);Anthropic claude-code-security-review 的「硬排除清單」(本 repo §7.8 的「不報」就是借它),本案只是把排除清單在工具鏈本 repo 加長;③裁定=借用:沿用 §7.8 的排除清單形狀與既有 `_is_toolchain_repo` 判別,自建只有 `loop next` 印的一行;零新依賴。
RETIRE-IF: 任一條成立就撤掉這兩條 RULE、回到所有專案同一份資安與併發鏡頭——①工具改成多人共用或雲端執行(例:帳本或圖譜放到共用伺服器、多人同時對同一工作目錄跑 lumos);②範圍外手法累計 2 次被證實造成真實損害;③工具鏈本 repo 的審查在範圍內三類漏掉、事後證實是真洞,累計 2 次 [retire:人裁] [until:2027-04-14]。

## 實務隱患

- 守衛面:本案讓工具鏈本 repo 的資安審查少看一類東西,方向是「漏報」,不是「誤擋」。防誤用靠三件事:處置閘資安席一步不動(資安席照樣得派、照樣要看過最後一版);範圍只由既有 `_is_toolchain_repo` 判、`loop next` 印出來;兩條 RULE 有人裁到期日。消費專案自己在根目錄放一支 skills/lumos-project-notes/SKILL.md 就會被當成工具鏈本 repo——那正是範圍外的刻意手法,不另防。
- 注入:`loop next` 多印的那一行是固定字串,不帶編號、路徑或任何帳上的自由文字;templates 的新段落是範本,不讀外部輸入。
- 併發:`loop next` 只多一次檔案存在檢查,不寫任何檔、不拿鎖;照本案新規則,工具鏈本 repo 也不再審多會談同時寫入。
- 效能:多一次 `is_file()`;`loop next` 是人手動跑、一輪一次,不在熱路徑。無。
- 資源:不開子程序、不開連線、不讀大檔。無。
- 版本錯位:新範本配舊版 lumos(不印那一行的版本)時,編排者看不到「鏡頭範圍」,會照原圍欄派——結果是工具鏈本 repo 暫時照舊規則審,方向是多審不是少審。消費專案裝了新範本也一樣:沒有那一行就用原圍欄。
- 可逆性:純文件、一行輸出與測試,revert 就退;帳本格式不變;舊迴圈的處置帳不用遷移(見〈回退〉)。
- 已排除:對外送出:本案不送任何東西出本機;命中是因為計劃裡提到「對外重試」「外家席」等字樣。資安席與資源席仍是本機子代理,跟其他審查席同一條路。
- 已排除:金流:不碰金流或支付程式。
- 已排除:不可逆:不刪改任何帳本或專案檔;已用新規則放行的處置帳照留,回退後新迴圈回到舊規則即可。
- 已排除:認證、個資、快取、遷移、限流:本案不改這些程式,它們只是資安席要審的對象。

## 驗收條款

- [S1] 當 `lumos loop next code-x --tier high --orchestrator claude` 在根目錄有 skills/lumos-project-notes/SKILL.md 的 repo 執行時,人讀輸出應多一行以「鏡頭範圍: 工具鏈本 repo」開頭並含「§7.8」,`--json` 的 lens_scope 應為 toolchain;在沒有那支檔的消費專案,應不印那一行、lens_scope 應為 default,其餘人讀輸出應與改動前逐字相同。 [test:t_loop_next_lens_scope_toolchain_vs_consumer]
- [S2] 當 `lumos loop next` 的編號是設計審(不是 code 開頭)時,工具鏈本 repo 也應不印「鏡頭範圍」那一行、lens_scope 應為 default。 [test:t_loop_next_lens_scope_design_untouched]
- [S3] 當讀 templates.md §7.8 時,應有〈工具鏈本 repo 的範圍〉段,段內圍欄應含提示注入、讀寫越界、一步就能繞過三類,範圍外清單應含偽造 git 內部、手填帳本欄位、換編號或改檔名,並寫明附理由放行或改文件拿掉保護說法兩種處置;原本圍欄的六類(注入、登入與權限、密鑰與個資、加密與傳輸、執行邊界、行動端)應仍完整在段外,兩個圍欄都應寫席名 `資安-<模型>`。 [test:t_templates_toolchain_lens_scope]
- [S4] 當讀 templates.md §7.7 立場表與 §7 鏡頭列時,資源併發那列應寫明工具鏈本 repo 改資源鏡頭,並含孤兒、逾時、記憶體三個詞;§7.8 原圍欄的「不報」應含「工具鏈本 repo 歸資源席」。 [test:t_templates_toolchain_resource_lens]
- [S5] 當讀 skills/lumos-code-loop/SKILL.md 步驟 2、skills/lumos-code-loop/reference.md 步驟 2、skills/lumos-project-notes/commands/06-代碼審與推送.md 時,每一份都應提到「工具鏈本 repo」與「§7.8」,且寫明消費專案照舊。 [test:t_toolchain_lens_scope_doc_sync]
- [S6] 當工具鏈本 repo 的高風險代碼審沒有資安席帳列時,處置閘應照舊判不過(退出碼 1、訊息含「資安席」)。 [test:t_disposal_security_seat_required]
- [S7] 當讀編制表 code/high 時,應照舊有一席 `資安`、派工要求為 required-gated。 [test:t_roster_code_high_has_security_seat]
- [S8] 當跑 `lumos lint Systems/pitfalls-code-loop` 時,應無錯,兩條新 RULE 行應各自帶齊依據、since、retire、until、confirmed,decisions 應有本案新增的那條(d8)且 d6 未被標取代;[[Systems/bound-tests-gate]] sitecustomize 那條 WHY 的括號應指向 Systems/pitfalls-code-loop 的 RULE。 [manual:跑 lumos lint Systems/pitfalls-code-loop 與 lumos decisions Systems/pitfalls-code-loop,核對兩條 RULE 欄位齊、d8 在、d6 仍有效;grep bound-tests-gate 那條括號]
- [S10] 當讀 templates.md §0 時,應有一條寫明刪檔一律用字面絕對路徑,並點名「先 cd 到變數路徑再相對路徑刪」與「萬用字元」兩種禁用寫法;§1、§3、§7.8 每份派工詞圍欄的第二行都應指回 §0 那條。 [test:t_templates_rm_literal_absolute_path]
- [S11] 當讀 templates.md §3 第 1 點時,應寫明工具鏈本 repo 的代碼審不用答「兩個請求同時進來」與「讀了兩次、中間被別人改了」兩問,並仍保留重跑與對外重試;消費專案原句一字不少。 [test:t_templates_toolchain_idempotency_scope]
- [S9] 當下一次工具鏈本 repo 的高風險代碼審派資安席時,派工單應用工具鏈範圍那份,席報告裡的範圍外發現應以附理由放行或改文件處置、不新增機制。 [manual:抽那次迴圈的 rN-dispatch.json、資安席報告與處置帳,逐條核對範圍外發現的去向]

## 回退

退回=templates.md 刪掉〈工具鏈本 repo 的範圍〉段與 §7.7、§7、§7.8「不報」補的那幾句;三份代碼審說明刪掉補的那句;`loop next` 拿掉那一行與 `lens_scope` 欄位、拿掉上面七支新測試、§0 那條與各圍欄第二行補的句尾、§3 第 1 點補的括號;[[Systems/pitfalls-code-loop]] 兩條 RULE 標 `[status:superseded]`、d8 用 decision-supersede 標取代。不碰帳本與處置閘;已經以「範圍外」放行的舊處置帳照留(帳只能追加),回退後新迴圈照舊規則審。
