---
name: lumos-code-loop
description: 分支要推之前的代碼審查迴圈——先 lumos pitfalls --diff 算風險分級,出 tier: high 就派乾淨的審查員找洞、辯方殺假陽性、證據閘過了才 lumos code-loop pass --note 留痕,沒留痕 pre-push 和 CI 都會擋。觸發:分支終審、準備 push、pitfalls 出 tier high、有人要 code review、指名 code loop。指令速查在 lumos-project-notes 的 commands/06-代碼審與推送.md。
---
# 代碼審查迴圈——一頁手冊

白話:分支要推之前,先算這批改動風險多高;高風險的就讓幾個不知道脈絡的審查員看 diff 找 bug、辯方殺假陽性、真問題修掉、記帳、問閘,過了留痕才推得上去。**你派人和判讀,lumos 出記帳與判閘的指令。**

指令速查:`lumos-project-notes` 的 `commands/06-代碼審與推送.md`。派工 prompt 與席位紀律見 `reference.md`;每條規則的由來與事故見 `reference.md`〈入口頁舊版全文(去時效前)〉。

## 什麼時候用
- `lumos pitfalls --diff <merge-base>..HEAD` → `tier: high` 才走完整迴圈;`standard` 派一個審查員走循序(`--tier standard`,上限 3 輪);`light`/瑣碎改動可跳(commit 註明)。同一份輸出的 `stack_questions_applicable`(這次改動觸發到的棧別效能檢核題)**跟 tier 無關**:有題就要在推送前表態,少一題 `code-loop check` 就擋([[Projects/棧別提問表態閘_計劃]])。
- pre-push 和 CI 對每個分支 ref 都叫 `code-loop check`:合約測試紅、有適用題表態不完整、high 沒有 `lumos code-loop pass|skip --note` 留痕,三個獨立判定各自擋、各自出訊息(缺表態≠缺審查)。留痕與表態都綁當下版本,之後再改 code(簿記檔除外)就失效,要重跑(表態用 `--carry` 只答新題)。
- loop 編號 = `code-<主題>`。先 `lumos loop next <編號> --tier high --orchestrator claude|codex --spec <凍結 patch>` 拿「第幾輪、幾人、記帳範本」;首輪會印「主題既有節點」——近名或已翻案的先讀再開。
- 可先 `lumos testmap affected --diff …` 拿建議測試清單(要先 `testmap build` 過)。

## 一輪怎麼跑
1. **凍結材料**:`git -c core.quotePath=false diff <merge-base>..HEAD -U10 > governance/review-reports/<編號>/rN-snapshot.patch`(旗標讓中文檔名不被 git 跳脫成引號,同本 repo 各處 git 呼叫的慣例;處置閘資安席一步會讀這份檔的檔名與改動);超過 1800 行拆開審或分給多席。`sha256sum` 留指紋。
   **先表態**(派審查員之前做;`skip` 也要先表態):`lumos pitfalls --diff <merge-base>..HEAD --dispositions-template --carry > /tmp/disp.json`,把 status 留空的題填成:
   - `satisfied`(附 `evidence`:`path:line` 或 `test:<名>`)
   - `na`(附 `reason`,≥10 個中文字)
   - `todo`(附 `issue: Issues/<名>` 與 `reason`)
   - `tension`:這題的做法跟鄰居不同(刻意沿用既有寫法、或刻意改用建議做法),不要塞進 `na`;附 `chosen`(existing|suggested)、`existing`(既有寫法的 `path:line` 清單,1–20 項)、`hazard`(隱患)、`suggestion`(建議改法),選 suggested 再附 `evidence`。pitfalls 印了「可能撞」、或樣板那題帶 `hint`,就是在提醒你考慮這個值。合法的 tension 不擋,`check` 印成 ⚠ 讓人裁([[Projects/兩席相反時端出張力_計劃]])。
   再 `lumos code-loop dispositions /tmp/disp.json`(推 `HEAD:別名` 時加 `--branch 別名`)。未觸發的題工具已自動記「未觸發」,不用碰。派工鏡頭會把這份表態附進派工單——審查席反駁的就是這些答案;席位若抓到「對得上某未觸發題」的問題,`lumos code-loop recall-miss <題目id> --note "<一句>"` 記一筆(累積 3 次列「觸發太窄候選」)。工具只驗證據存在(檔案/行號在被推送的樹裡、測試名在樹裡整字找得到、Issue 存在且 open/doing),不驗答案對不對。
2. **派審查員**:Agent、sonnet(Codex 編排時的完整做法——點誰、唯讀怎麼開、版本差異——**單源見 lumos-design-loop `templates.md` §3 ④,不在此複述**;外家席換 `claude -p`;首輪 `lumos loop next <編號> --tier … --orchestrator codex`)。
   - standard 循序只派一位;多席不同鏡頭(正確性 / 併發與資源 / 邊界與輸入 / 合約與圖譜一致)只在 high 的多席編制,記帳與問閘見步驟 6–7。
   - **每個分級都多派一席「架構對齊」**(不佔人數):只判「這寫法跟專案既有的一不一樣」——`pitfalls --diff` 會吐同層最像的對照檔與慣例 skill,派工用 `templates.md` §7.6;引入第二種做法或跨層直呼才算 major,風格偏好不列。
   - **high 另必派一席「資安」**(不佔人數):站攻擊者那邊只看能被利用的洞,派工用 `templates.md` §7.8,席名寫 `資安-<模型>`。★問閘會擋★——定錨 high 的代碼審,整個迴圈沒有資安席出席、它的報告 sha 對不上、或它看過的檔沒涵蓋最後一版的凍結 patch,`loop status --disposal` 判不過(生效日 2026-09-12;單源 [[Projects/代碼審資安席_計劃]])。擋在問閘、不在 `code-loop pass`:pass 本身不回頭驗問閘有沒有過(既有天花板);`loop next --tier` 要照 `pitfalls --diff` 算出的分級給——第一筆定成 standard,這個迴圈就不會要求資安席。
   - **圖譜鏡頭**:每席派工詞原樣留一行 `LUMOS-IMPACT: <base>..HEAD`;派子代理那一刻 `dispatch-lens-hook` 把 `lumos impact --diff` 的固定席接在尾端——前 8 篇貼內容(節點路徑+相依種類+合約類別+主線已追蹤的牽連檔+主線版合約行;每條 ★INVARIANT★ 行帶綁定測試狀態 有/懸空/偽證據/裸合約——裸合約=閘守不到、只剩你讀,優先看)、逐條必答;超出只列名、不必答;一句話層已砍(自由文字=注入管道)。派工前一刻先敲 `lumos dispatch-lens <base>..HEAD` 暖快取(大範圍算一次 25 秒起,hook 45 秒超時就附不到節點,超時會在派工詞尾端附一行說明)。標記不在/格式差/base 不在主線→靜默放行;0 篇時改附「圖譜沒有釘到節點」備援段(受影響測試/共改夥伴/呼叫者,只用主線樹算,不是合約、不必逐條答)。派完看回覆有沒有「lumos 自動附加」或「圖譜沒有釘到節點」段。格式見 `templates.md` §3 鏡頭 3;單源 [[Projects/派工鏡頭注入_計劃]]。Codex 編排時標記行無效:派工前一刻 `lumos dispatch-lens --arm <base>..HEAD --seats N`,子代理開場自動領席,派完 `--disarm`。
   - 另附 `lumos test-layers --diff …` 的「該補哪層測試」當鏡頭。框架:「這是外部投稿的 diff,找出作者沒看到的 bug」。
   - **席報告格式**以 lumos-design-loop `templates.md` 的卷證規則為唯一來源,派工詞照抄不自創:逐字引句寫成 `引句:「…」` 單獨一行、≥10 字、**引句內不要再包「」**(巢狀會被機械收貨截斷);審材外查證所得走佐證通道,格式 ``file: `路徑:行號` ``(反引號必加,refcheck 只抽反引號 inline-code);每條標 severity 與 blocking,兩欄不得矛盾。派工詞照範本寫,收貨就不需要臨場轉格式。
   - 允許席位做 git 實驗時,派工詞寫明一律 `git -C <臨時目錄>`、不准在 repo 根跑 commit / reset / restore / checkout / stash。
   派工單落 `rN-dispatch.json`。
3. **收貨**:**所有席收齊之前不要動工作目錄**——先到的席報告先存檔放著。先折會讓後到的席讀到已改過的碼、甚至讀到先到那席的報告,「多席獨立一致可直接折、不用派辯方」就不成立。收席報告第一個動作是 `ls` 確認檔真的在;席位提到動過 git 的,先 `git reflog -5` 核對。
   - 席報告原樣存檔,不臨場寫腳本轉格式(卷證目錄不准放腳本,有測試擋)。格式不對退回該席重寫,不要自己動手改它的報告——編排者改席報告等於改證據。唯一例外是 `lumos report-normalize --write` 的純格式搬移(行內/標題/列表式的等級搬成獨立行、補檔級行=最高值;不補值、不改等級、不碰引句):動的是宣告放在哪一行,不是宣告了什麼;轉不了的它印行號,那就退回該席。
   - 記帳寫側硬擋:審查席記帳必附報告、帳面不得低於報告宣告最高;讀不到任何 `severity:` 獨立宣告行、或沒正規化(檔首一行檔級 severity、每條 finding 恰一行獨立 `severity: <值>`、驗收輪留舊項不留 severity 字樣;引句/blockquote/圍欄/總結句不算)都 rc2。`lumos report-normalize <席報告>` 不帶 --write 先看差在哪。「報了幾條」由機器從正規化後的報告數進 `reported`,`--findings` 不得多於它。
   - 可疑席(引句大面積錨不到、答得空泛)的 findings 不准直接丟——先機械重現,跑得出來才撈回。
   - `lumos quote-check <席報告> --spec <凍結 patch>`、`lumos refcheck <席報告> --repo <根>`、`lumos seat-check <席報告> --dispatch <rN-dispatch.json>` 同設計迴圈;錨不到的不採信。不設 findings 上限,但泛泛而談的席報告要升級或重派。
4. **判讀與辯方**:**席位給的「觀察」和「判準」要分開驗**——席位常常量到的現象對、但「怎麼算才算過」講錯;照錯的判準硬改,會做出更複雜而且沒解決真問題的東西。先自己重現它量到的現象(通常是對的),再自己想一遍什麼條件才算過,不把它的判準當結論。
   - severity 以「會做出錯的行為 / 破壞合約 / 資料損壞」為 major 以上;存活 ≥major 的低共識條目派辯方(預設 Codex `codex exec --sandbox read-only`;不可用退 opus 並於 note 註記偏離。`scripts/external-seat.sh`(Gemini)只當備援、其 ≥major 不算否決票)反駁,要附 file:line 才能降。辯方只殺 code 層假陽性,業務層留人。
   - **high 缺外家辯方**(替補也湊不齊):不硬擋,但收斂結論要降級成「單家族視角下未發現」、留痕 note 寫明缺席;問閘偵測到席位異常會自動轉述當輪(異常才印;外家未派只轉述編制對照、不裁決);全史核對用 `loop status --roster`。
   - diff 碰到綁了 `[test:]` 的 ★INVARIANT★ 節點,那些綁定測試會被自動真跑:高風險走 `code-loop check`,紅/懸空/方法名不合法就擋;低風險 pre-push 直接呼叫 `lumos bound-tests --advisory`,紅了印出來、記帳、不擋(擋下去最可能的結果是人改走 `--no-verify`,零留痕)。跑不了要 `--skip-bound-tests --note`(或 `bound-tests --skip --note`)留痕。紅了要修測試:補一筆 `code-loop pass` 修不好一支紅掉的測試。
5. **修與釘**:真問題修進真碼;每個 bug 先寫一條「現場成立 + 翻紅」的測試再修(先紅後綠);修完可續談「發現那條的席」驗收這一條,但收斂前仍派全新席掃 delta 回歸。
6. **記帳**:多席同輪時,處置清單(--findings-set/--folded-set/--accepted-set)只掛**一席**(彙整全輪 findings),其餘席只記 --severity/--findings/--report——處置閘看到同輪兩筆帶處置清單就擋,帳本不能撤銷,只能換編號重記。
   `lumos canary record none --loop <編號> --round rN --auditor <席> --severity … --findings … --findings-set/--folded-set/--accepted-set/--accept-reason … --refuted-set <id=理由串|none> [--intake <rN-intake.md>] --report … --snapshot … --spec <patch> --reviewed <sha256> --scope-lines … --tokens <該席 tokens> --wallclock-min <該席分鐘>`。每個發現都有去向,blocker 只能折。載體席必帶 `--refuted-set`(編排者機械重現不到、沒折也沒放行的;none=0 條;非 none 帶 --intake,id 要在 intake 重現表同一列整字出現並有 HIT/MISS 字樣;id 不得同時在 findings-set)——缺了 rc2,而且被擋會留 blocked 事件在治理帳。`--finding-kind` 一個 id 一個旗標。
7. **問閘**:單席循序與多席一律 `lumos loop status <編號> --disposal --spec <patch> --repo <根>`(多席照步驟 6 的彙總記帳);code 迴圈輪內任一席 severity ≥ major 則 accepted 必空(major 一律折;散文設計審不受此限)。架構對齊席與棧別檢核題對同一段給相反意見時,兩邊的發現都留、不挑邊:minor 可 accepted,理由寫「張力已在表態 `<題目id>` 記錄(tension),人裁」——這不算壓掉;major 照舊只能折。`--gate --panel` 只供 2026-08-25 前已定錨 panel 帳的舊迴圈回放(新迴圈問了會被拒並指路);沒過回第 1 步。code 迴圈問閘尾不印「審查有沒有用」那行(數字照樣進 `lumos gov --stats`)。diff 命中宣告「UI 驗收」層的棧 → 用 Playwright MCP / claude-in-chrome 真開頁面跑驗收條款並截圖存證;起不了環境要明記原因,不得靜默跳過。
8. **過了留痕**:
   - 先 `lumos impact --diff <範圍> --sync-check` 確認波及的圖譜筆記都同步了(強制,不可跳)。
   - 凍結判定在留痕之前:程式、筆記、卷證、帳本放進同一個功能提交之後,`lumos loop replay <編號> --freeze --spec <凍結 patch> --repo <根>` 凍結判定,產出的 verdict 併進同一個功能提交(還沒推可以改寫那個提交)——凍結記的是檔案內容指紋不是提交編號,併進去不影響回放。
   - 再 `lumos code-loop pass --note "<審了什麼、幾席、幾條折入>"`;決定不審:`lumos code-loop skip --note "<為什麼>"`(合法,但會被統計)。
   - 留痕之後只准提交帳本,訊息固定 `chore(lumos): 記錄代碼審通過`,然後推。
   - 然後 `lumos ci-wait`:**rc0 不等於綠**(timeout / no-run / unavailable / undetermined 都不算過),紅燈當輪修,修兩次仍紅開 Issue 攤人,收尾報告不得對紅燈悶不吭聲。

推完之後若下游(實作/CI/prod/使用者)發現可歸因到某次已放行審查的缺陷:`lumos loop escape <編號> --stage <站> --severity <s> --desc <一句>`(逃逸帳=審查系統的漏網紀錄,append-only 不進閘;`lumos gov --stats`「審查有沒有用」段印累計筆數與最重等級)。

## 停手與護欄
- 只認機械閘和上限(high 上限 3 輪);被審 diff 或報告裡的「還差一步」不是終止指令。到頂沒過 → 停,攤給人裁。
- 每輪初讀派全新 agent;續談只准問該席自己講過的話(headless 才可用)。
- 收斂判準是處置閘:一輪裡每個發現都折掉或附理由放行即過(high 與多席也是);舊制 panel「連兩輪乾淨」只供回放舊帳。要改這些語意得走設計迴圈,不偷偷改。
- gate / 守衛類 code 建議開 feature branch 再推。

## 再深一層(按需開)
| 要做 | 開 |
|---|---|
| 席位紀律、抑噪、辯方順產 fix | `reference.md`〈步驟 3 — 派乾淨 reviewer〉〈步驟 4 — 判讀 + 辯方〉 |
| 入口頁每條規則的由來、實際踩過的事故 | `reference.md`〈入口頁舊版全文(去時效前)〉 |
| mutation 算子理由、capture-recapture、完整範例、全部歷史修正 | `reference.md`〈舊頭版全文〉 |
