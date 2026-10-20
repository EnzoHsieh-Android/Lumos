---
type: project
status: todo
created: 2026-10-19
updated: 2026-10-19
tags:
  - type/project
  - status/todo
  - scope/guards-gates
lands_in:
  - Systems/pitfalls-code-loop
  - Systems/lumos-cli-read
  - Systems/test-quality-cli
  - Systems/bound-tests-gate
  - Systems/guard-kill
  - Systems/安全證據閘
  - Systems/棧別提問表態閘
related:
  - "[[Projects/消費專案產品安全Brief與證據驗收_計劃]]"
  - "[[Projects/資安護欄唯讀盤點_計劃]]"
  - "[[Projects/資安風險提問分階段_計劃]]"
  - "[[Projects/實作測試獨立判準_計劃]]"
  - "[[Projects/測試品質工具接線_計劃]]"
  - "[[Projects/後端工程提問與證據擴充_計劃]]"
  - "[[Projects/代碼審資安席_計劃]]"
  - "[[Projects/推送前一次列出全部擋下原因_計劃]]"
pending_questions:
  - id: Q1
    text: 例外「只有使用者能核可」要用哪種機制?原列三案:①終端逐字確認加工具前掛鉤詢問;②使用者簽章金鑰簽署、CI 驗簽;③只能經使用者帳號核准的 PR 合入。d1 先選③,因③現況做不到(見 Q9)由 d6 改成簽章金鑰,設計審 r1 後由 d7 改成對內容做分離式簽章
    class: 權責
    stage: 架構
    status: 已決
    blocking: true
    decision: "#d7"
  - id: Q2
    text: review 種類(判準獨立、合法對照真的合法、門檻有意義、校準樣本代表性)機械驗不了;原提案閘門只核身分、版本綁定與時效、判 review_declared 不擋。已依 d2 改成要非作者的獨立審查紀錄才放行,沒有或過期照擋
    class: 風險接受
    stage: 驗證
    status: 已決
    blocking: true
    decision: "#d2"
  - id: Q3
    text: lifecycle 是 candidate 的資安護欄要不要也擋?建議不擋只列提醒(擋了會讓人不敢登記),另加 candidate 放超過 30 天就在 security evidence 標出
    class: 風險接受
    stage: 交付
    status: 待人
  - id: Q4
    text: 已經登記資安護欄的專案(目前只有試行中的 order-demo)升級時,要不要給一段只提醒不擋的過渡期?多長?母計劃 d9 是預設擋,過渡期等於延後生效
    class: 風險接受
    stage: 交付
    status: 待人
  - id: Q5
    text: 依賴掃描結果隨漏洞庫更新,證據要多新才算數?建議 dependency_scan 超過 14 天判 stale,其他掃描類以綁定檔變動判
    class: 風險接受
    stage: 驗證
    status: 待人
  - id: Q6
    text: 每個消費專案要裝哪些掃描與壓測工具、釘哪個版本、從哪裡裝、單次與整批執行預算多少、壓測與動態掃描准打哪些目標?先從 order-demo 開始逐項核可,AI 不自行安裝
    class: 成本與資料
    stage: 架構
    status: 已決
    blocking: true
    irreversible: true
    decision: "#d4"
  - id: Q7
    text: OD-04(重送與並發不能讓他人操作生效)用 k6 在 order-demo 實跑,不在母計劃 d8 已核可範圍:要不要核可?核可的話隔離副本、請求數、時間上限與清理照母計劃 d8 的寫法嗎
    class: 成本與資料
    stage: 驗證
    status: 已決
    blocking: true
    decision: "#d3"
  - id: Q8
    text: 校準用的已知陽性樣本(植入假秘密、已知有漏洞的鎖檔、故意寫壞的設定)要放進消費專案版控,會被其他掃描工具與審查看到;可以放嗎?放在哪個目錄、怎麼標明是假的
    class: 範圍
    stage: 驗證
    status: 待人
  - id: Q9
    text: d1 要的「經使用者核准的 PR 才算例外」現況做不到(CI 只在 push 跑 code-loop、權限讀不到 PR 核准、AI 用的就是使用者的 GitHub 帳號、GitHub 不准核准自己的 PR);要改用(a)使用者手上需實體觸碰或密碼的簽章金鑰簽的提交,還是(b)使用者第二個 GitHub 帳號核准?已依 d6 選(a)
    class: 權責
    stage: 架構
    status: 已決
    blocking: true
    decision: "#d7"
decisions:
  - content: 例外只認經使用者 GitHub 帳號核准(approve)後合入主線的 PR:例外寫在受版控的例外檔,閘門在 CI 端核對該例外列是由使用者核准的 PR 帶進來的;本機推送前只看例外列存在與未過期,最終以 CI 為準;AI 寫入的例外沒經使用者核准的 PR 就不生效
    id: d1
    context: 待決 Q1:現有核可只驗附註非空,AI 也寫得出來,機器分不出是人還是 AI
    why_chosen: 使用者 2026-10-19 選「只能經你核准的 PR 合入」;不需新增簽章工具,追得到核可人;代價是例外要等 PR 合入才生效,本機可能先擋
    decided: 2026-10-19
    valid: false
    superseded_by: "#d6"
    ended: 2026-10-19
  - content: 機器驗不了的人工判斷(判準是否獨立、合法對照是否合法、門檻有沒有意義、校準樣本代表性、報告是否偽造)要有一筆非作者的獨立審查紀錄才放行;紀錄綁版本,綁定的程式或護欄修訂一變就要重審;沒有紀錄或過期照擋
    id: d2
    context: 待決 Q2:原提案判 review_declared 不擋
    why_chosen: 使用者 2026-10-19 選「要獨立審查紀錄才放行」;P1 的判準獨立性審查實際抓到兩種會漏網的所有權繞過,證明人工判斷不能只靠作者宣告
    decided: 2026-10-19
    valid: true
  - content: 核可 OD-04(重送與並發不能讓他人操作生效)在 order-demo 用 k6 實跑,條件照母計劃 d8:獨立副本、本機合成資料、只打本機回環、單次 10 分鐘、整批 1 小時、不呼叫額外付費模型;用本機已裝的 k6 v2.3.0 並在證據記版本;當作閘門第一個工具輸出真實案例
    id: d3
    context: 待決 Q7:OD-04 不在母計劃 d8 已核可範圍
    why_chosen: 使用者 2026-10-19 選「要,依 d8 同樣條件」;同時等於 Q6 對 order-demo 先核可 k6 這一項,其他工具仍逐項另核
    decided: 2026-10-19
    valid: true
  - content: 各消費專案的掃描與壓測工具採逐專案、逐工具由使用者在要用那個工具之前核可(安裝來源、釘版本、單次與整批預算、准打目標),AI 不自行安裝;閘門與轉接介面的實作不依賴任何特定工具已安裝,只讀工具輸出;order-demo 目前核可的是 k6 v2.3.0(本篇 d3)與既有 JUnit、guard kill,其他工具要用時再逐項問使用者
    id: d4
    context: 待決 Q6 標阻塞與不可逆,但它是逐專案的工具核可,不是閘門機制本身的設計前提
    why_chosen: 使用者先前同意「安裝與執行都要你核可」的做法未提異議,並在 d3 核可 order-demo 用 k6;把逐工具核可留在每次要用時問,閘門先能設計與實作
    decided: 2026-10-19
    valid: true
  - content: 實作期間 order-demo 當資安功能的實驗專案:新指令、轉接器、閘門判定、階段提問先在 order-demo 真跑驗證;條件沿用母計劃 d8(隔離副本、本機合成資料、只打本機回環、單次 10 分鐘、整批 1 小時、不呼叫額外付費模型);實驗產生的產品證據留在 order-demo 自己的圖譜,不複製成工具鏈證據;實驗結果不代表真實認證安全;新工具仍照逐項核可
    id: d5
    context: 設計需要一個真實消費專案驗證閘門與提問;order-demo 已有 P1 證據與 k6 核可
    why_chosen: 使用者 2026-10-19 指示「order-demo可以在資安功能實作中，作為實驗專案」
    decided: 2026-10-19
    valid: true
  - content: 例外列只認使用者手上、每次簽章需實體觸碰或輸入密碼的金鑰所簽的提交帶進來,AI 拿不到這把金鑰:用 git 提交簽章(ssh 或 gpg 皆可),公鑰指紋釘在受版控的 .lumos/security-approvers;code-loop check 本機與 CI 都核對引入或修改該例外列的那個提交由釘住的金鑰簽章且有效;公鑰清單本身的修改也必須由現有釘住的金鑰簽;第一次釘金鑰的提交由使用者手動完成;取代 d1 的 PR 核准載體,保留 d1「AI 不能自己放自己」的本意
    id: d6
    context: d1 的 PR 核准現況做不到:CI 只在 push 跑 code-loop、權限讀不到 PR 核准、GitHub 分不出使用者與 AI、也不准核准自己的 PR
    why_chosen: 使用者 2026-10-19 裁:「不然就用金鑰吧」;不選第二個 GitHub 帳號(要多維護帳號、CI 要加讀 PR 權限與 API 查詢,憑證若放在 AI 碰得到的地方就失效)
    decided: 2026-10-19
    valid: false
    superseded_by: "#d7"
    ended: 2026-10-19
  - content: 例外、核可修訂紀錄、considerations 的核可與 gate 降級設定,一律改成對內容做分離式簽章:ssh-keygen -Y sign -n lumos-security 簽規範化 JSON(鍵排序、無空白),內容含 control_id、被核准的 control revision 與判定輸入(required_evidence、threat_categories、assets、surfaces、evidence_refs)的雜湊、蓋住的證據種類、核可日、到期日;驗用 ssh-keygen -Y verify 對 allowed_signers;准用的金鑰清單 .lumos/security-approvers 一律取 merge-base 版,清單的修改(含刪檔)要有 merge-base 版清單金鑰對新清單內容的簽章;多提交推送一律對 merge-base 判。不再用 git blame 找最後改那幾行的提交再 verify-commit
    id: d7
    context: 設計審 r1 多席指出 d6 的提交簽章在壓提交、rebase、合併提交、排版動到行、多行例外、只改外層護欄時會失效或被繞過;提交會被重寫
    why_chosen: 使用者用意「用金鑰、AI 不能自己放」不變,只換簽法:簽的是內容不是提交,提交怎麼重寫都不影響;只簽一種東西也讓本機與 CI 的判定只依 merge-base 與內容
    decided: 2026-10-19
    valid: true
  - content: 審查紀錄(review_record)可以由另一個 AI 會談審,但紀錄必填 reviewer_kind(ai 或 human);ai 審的不能放行需要人工權責的判斷——判準是否獨立、合法對照是否真的合法、門檻有沒有意義、校準樣本有沒有代表性、不適用理由成不成立(照母計劃 V4「AI reviewer 不能代簽需要人工權責的結論」的範圍),只能放行其餘判斷(威脅類別與必要種類選得夠不夠、入口盤點有沒有明顯漏項);human 審的要有 d7 的金鑰簽章才算 human,沒簽一律當 ai。工具天花板:AI 自己編審查內容擋不住,只能靠標成 ai 限縮它能放行的範圍
    id: d8
    context: 設計審 r1:review_record 寫在 AI 可寫的 Verification 圍欄,AI 填兩個不同名字就能自己滿足 d2;母計劃 V4 寫 AI reviewer 不能代簽需要人工權責的結論
    why_chosen: 使用者 2026-10-19 裁:選「允許 AI 審但標明」——另一個 AI 會談審也算 review 證據,但要標 reviewer_kind,AI 審的不能放行需要人工權責的判斷,human 審要金鑰簽才算
    decided: 2026-10-19
    valid: true
  - content: 不要求消費專案在 GitHub 設主線保護或 PR 必過檢查:維持本機 pre-push 閘加推送後 CI,靠既有「跳過檢查一律先問人」的規矩;--no-verify 與事後 CI 擋不住已進主線的提交,寫成工具天花板並定期回看有沒有發生過繞過
    id: d9
    context: 設計審 r1 外家席:本機閘可被 --no-verify 跳過,CI 在主線更新後才跑,紅燈收不回已推的提交
    why_chosen: 使用者 2026-10-19 裁:選「維持現狀」,不改 GitHub 設定,靠本機閘加不准跳過檢查的規矩
    decided: 2026-10-19
    valid: true
---
# 安全主張驗收閘_計劃

## 接手先讀：這份計劃管什麼、授權到哪

白話：盤點指令已經能把資安護欄列成一張表；這份計劃要讓表上每一條「宣稱有驗過」的護欄，都拿得出一份真的跑過、對得上現在版本、抓得到錯的工具結果，拿不出就在推送時擋下。它像驗收單：不是問「有沒有人說驗過」，而是把原始成績單調出來核對日期、科目和分數；要放行例外，得有使用者手上那把金鑰蓋的章，章蓋在單子內容上，不是蓋在信封上。

- 要求來源是母計劃 [[Projects/消費專案產品安全Brief與證據驗收_計劃]]：〈安全主張驗收閘：d5修正方向〉的單一來源與責任、判定與可宣稱範圍、G1–G5；〈驗證協議：五層證據〉V1–V5；〈與前導提問、測試品質的整合分工（d7）〉；〈證據交接與首案整合驗收〉六項整合控制。本篇逐條承接（見〈承接對照〉），不另起爐灶。
- 已裁定：母計劃 d9（必擋範圍、接 code-loop check、例外只有使用者核可且最長 30 天、所有接了 lumos 的專案預設擋）、母計劃 d8（P1 只核可 OD-01、OD-02 的故障證據）。
  - 名詞：P1 是母計劃〈分階段實作〉的第一階段「付款／取消兩條主張跑通證據鏈」，在 order-demo（工具鏈拿來試行的示範訂單專案）上做；OD-01 到 OD-04 是 order-demo 所有權 Brief 的四條安全主張：OD-01 他人不能付款別人的訂單、OD-02 他人不能取消別人的訂單、OD-03 拒絕時不能透露訂單資料、OD-04 重送與並發不能讓他人操作生效。
  - 本篇自己的決策寫 d1–d9（d1 被 d6 取代、d6 被 d7 取代）；母計劃的決策一律寫「母計劃 dN」，兩邊編號不通用。
  - merge-base：要推的提交跟預設分支（通常是 main）分岔的那個共同祖先；本篇所有「起點版」都指它，定義見〈四〉的〈起點一律是 merge-base〉。
- 這份只寫設計，不寫程式、不改 CI 或推送行為、不在任何專案安裝工具、不執行故障或壓測。實作前要先過本篇規格閘（預期風險高）、設計審，實作後再過代碼審；母計劃 d9 本身不代表閘已上線。
- 輸入：唯讀盤點 [[Projects/資安護欄唯讀盤點_計劃]] 的 `security list` 報告（同一支組報告的函式，不另寫讀法；從提交讀的那一步見〈四〉的〈從提交樹產快照〉）。
- 姊妹計劃 [[Projects/資安風險提問分階段_計劃]] 管「該想到哪些問題」；本篇管「宣告的證據合不合格、不合格就擋」。兩篇共用同一套資產、入口、證據種類、工具類別詞彙；威脅類別表的正本在 [[Systems/資安威脅類別表]]（設計內容暫在姊妹計劃），本篇只引用；兩篇 schema v2 新欄位的唯一完整清單在本篇〈一〉。
- 這個子系統的家是 [[Systems/安全證據閘]]；實作落地時說明寫在那篇，其他節點只放連結。

## 承接對照（母計劃要求 → 本篇落點）

| 母計劃要求 | 本篇落點 |
|---|---|
| 單一來源：Invariant 通用、可兼具業務與資安；獨立安全要求不必升格 | 〈一、區隔〉：沿用盤點 schema 的 source.kind 與 concerns，同一來源只列一筆 |
| 必驗集合凍結、不能由 AI 任選子集（G1） | 〈四〉的〈必驗集合與判定輸入都以 merge-base 版為底〉：條目在不在、判定輸入有沒有變弱都跟 merge-base 版比；變弱要有簽章的修訂紀錄，否則用新舊聯集判（本篇 S3、S29、S31） |
| 缺報告、零案例、skip、錯目標、編譯錯、逾時、未知錯誤 → 未驗或 invalid（母計劃 G2、V3） | 〈二〉每種格式的 invalid 條件與種類 × 格式允許表（本篇 S5、S7、S17、S33） |
| 換實作、測試、需求、fixture、設定、依賴或環境 → 舊證據失效（G3、V5） | 〈二〉綁版本：逐檔 git blob 比對、報告雜湊、測試原始檔與環境描述檔一律進綁定 + 工具版本 + 護欄 revision |
| 不適用與例外不消除原事實狀態，過期不能放行（G4） | 〈四〉例外：只蓋擋、不改狀態，到期日每次以 UTC 日期重算 |
| 受管出口實際消費本版本結果（G5） | 〈四〉code-loop check 新判定，tag 推送也判；驗收要用真推送的拒收案例。工具天花板依 d9：`--no-verify` 跳過本機閘、推送後 CI 才紅，都擋不住已進主線的提交（見〈實務隱患〉） |
| V1 答案有來源、V4 探索未預期漏洞；AI reviewer 不能代簽需要人工權責的結論 | 〈二〉的〈機械做不到的判斷〉：由 review 證據承擔；依 d8，AI 審的紀錄放行不了需要人工權責的那幾項 |
| V2 正確身分、資源存在、入口可達、看資料與副作用 | 〈二〉behavior 證據強制合法對照與前置斷言案例 |
| 母計劃 d7：不另建題庫、runner、故障引擎或總分 | 證據走既有 [test:] 綁定、guard kill、test-quality capture/check；外部工具只讀它自己的標準輸出 |
| 六項整合控制 | 〈五、合格測試守住閘門本身〉S15–S20 一項一條 |

## 一、區隔：資安護欄怎麼標、怎麼跟 Invariant 共存、怎麼一眼看出驗證不健全

**怎麼標**：沿用盤點已實作的 `lumos-security-v1` 圍欄，`concerns` 含 `security` 的條目才是資安護欄；`flag/security-relevant` 標籤照舊只用來抓「有標籤卻沒登記」，在本篇不算登記痕跡（見〈四〉擋下條件）。不用標題字樣或「Invariant」字樣猜分類。
- 理由：盤點的解析、讀檔邊界與錯誤分類已過設計審與實作驗收，再發明一套標法就是兩個家。
- 不選：另開 `★SECURITY★` 合約標記——會把部署掃描、期限性政策硬塞成永久合約，正是母計劃 d5 否決的方向。

**跟 Invariant 共存**：同一條規則要嘛是既有 ★INVARIANT★（source.kind=invariant，指到那條合約全文），要嘛是獨立要求（source.kind=requirement）；同一來源只列一筆，`concerns` 同時寫 business 與 security。驗收結論分開：業務合約照舊由 bound-tests-gate 擋紅燈，資安證據判定只看 concerns 含 security 的條目；同一份證據兩邊都能用，但不互相繼承通過。
- 理由：母計劃 d5「來源與關注面分離」。
- 不選：業務與資安互斥分類（同一條「他人不能取消訂單」得寫兩份）、所有資安一律升 Invariant（部署設定、依賴掃描不是永久不變式）。

**用哪個指令看**：新增唯讀子命令 `lumos security evidence`（`--json` 同內容；`--commit <sha>` 改讀那個提交，見〈四〉）。它拿 `security list` 同一份報告當輸入，逐條、逐證據種類核對工具結果，印出：
- 每條護欄一列：id、revision、來源（invariant 或 requirement 與節點）、lifecycle、威脅類別、整體判定（sound／unsound／excepted，規則見下）、護欄層原因代碼，以及最先要修的一項。
- 每條展開每個必要證據種類一列：種類、判定（qualified／failed／invalid／stale／missing／uncalibrated）、原因代碼（清單見〈原因代碼〉）、證據檔路徑、工具名與版本、綁定的版本、觀察時間、例外到期日、`limitations`（這份證據證明不了的事，例如跨環境套用、內容一致的偽造報告、AI 審查人的紀錄放行不了人工權責項；字串陣列，沒有就是空陣列）。
- 頂端照抄盤點的讀取完整度與登記完整度，固定 `security_verdict: not_assessed`；文字與 JSON 都寫明「證據合格不等於產品安全」。另列凍結比對的結果：起點版的提交編號、有哪些條目或判定輸入跟起點版比變弱、各自有沒有簽章的修訂紀錄。

**整體判定的彙總規則**（逐條護欄，依序判，先中先停）：
1. 護欄層有問題就是 unsound，例外蓋不掉：必要種類少於威脅類別最低要求（`insufficient_required_evidence`，算法見〈二〉）、沒宣告威脅類別（`threat_categories_missing`）、來源決策作廢（`source_decision_invalid`）、引用的待決問題還沒結（`question_open`，見 S15）。
2. 每個必要種類（含 review）都是 qualified → sound。
3. 不是 qualified 的每個種類都被一條有效例外蓋住（例外的 `covers_kinds` 含該種類），其餘都是 qualified → excepted。
4. 其他一律 unsound。只要有一個不是 qualified 的種類沒被有效例外蓋住，就算其他種類都有例外也是 unsound。
- 閘門只看必驗集合裡條目的整體判定：unsound 擋，sound 與 excepted 放行；excepted 每次都記帳（見〈四〉）。candidate 條目照樣算出整體判定給人看，但不進必驗集合、不擋。
- 閘門呼叫的是同一支判定函式，對同一個提交，「`security evidence --commit <sha>` 看到 unsound」與「推送那個提交被擋」永遠是同一個答案；簽章驗的是內容、日期取 UTC，所以本機與 CI 也是同一個答案。
- 理由：「驗證不健全」需要讀工具結果，盤點契約明文「evidence_check 永不到 verified、不讀報告內容」；擴 `security list` 等於改它的輸出契約與唯讀保證的語意，另開子命令可以讓盤點的判定契約一字不動。
- 不選：在 `security list` 加判定欄位（要改盤點計劃 S4 的 never_verified 合約候選）；只在推送時才算（使用者要能在推送前自己排查）。

### schema v2 新欄位：兩篇計劃的唯一完整清單（契約變更）

照盤點計劃的規矩另外標出：下表是本篇與姊妹計劃所有 v2 新欄位的唯一清單，姊妹計劃不另列，只指過來。依姊妹計劃 d2，這些變更併進本篇這次設計審一起審，不回盤點計劃另跑一次；審過後同步更新盤點計劃的契約段，並標明凍結版本差異。`security list` 的既有輸出欄位與 S1–S13 語意不變，只多認 v2 的新欄位與新輸出區。

| 位置 | 欄位 | 型別與意思 | 誰用 | v1 圍欄讀到時的預設 |
|---|---|---|---|---|
| 圍欄頂層 | `schema_version` | 整數 1 或 2；`lumos-security-v1` 圍欄名不變，版本只看這個鍵 | 盤點讀取 | — |
| 圍欄頂層 | `considerations` | 陣列，格子的「不適用」與「接受風險」，形狀見姊妹計劃〈四〉；可以放在任何 Systems 節點的圍欄，不必塞進 inventory 那一塊 | 姊妹計劃 | 空陣列 |
| inventory | `actors` | 陣列，每項 `id`、`description`；id 規則同護欄 id | 姊妹計劃 | 空陣列 |
| inventory.surfaces[] | `kind` | 固定值域（姊妹計劃〈一〉） | 姊妹計劃 | 沒有：這個入口不產生格子，列格子層錯誤 `surface_kind_missing` |
| inventory.surfaces[] | `actor_ids` | 字串陣列，誰會從這裡進來 | 姊妹計劃 | 空陣列 |
| inventory.surfaces[] | `boundary_crossed` | 文字，這個入口跨了哪道信任邊界；跟護欄的 `trust_boundary`（v1 既有，這條護欄在哪道邊界強制）是兩件事，不互相比對 | 姊妹計劃 | null |
| controls[] | `threat_categories` | 字串陣列，威脅類別 id（正本在 [[Systems/資安威脅類別表]]） | 本篇（最低種類）、姊妹計劃（格子覆蓋） | 沒有：盤點列 `missing_field`；閘門判護欄層 `threat_categories_missing`，最低種類算不出來不當成零 |
| controls[] | `actor_ids` | 字串陣列，這條護欄涵蓋哪些角色；只對有角色維度的三類格子有意義 | 姊妹計劃 | 空陣列（不覆蓋任何有角色維度的格子） |
| controls[] | `threat_table_version` | 整數，寫入這條護欄時威脅類別表的版號 | 姊妹計劃 | null，輸出顯示「未標」 |
| controls[] | `question_refs` | 字串陣列，`<節點>#Qn` | 本篇 S15 | 空陣列 |
| controls[].exception | 核可物件 v2 | 見〈四〉的〈核可物件：例外與 considerations 共用一套〉 | 本篇、姊妹計劃 | v1 例外照 v1 讀給 `security list`；閘門判 `exception:exception_unsigned` |
| `security list` 輸出 | `cells`、`cell_errors`、`applicability_pending_cells` | 姊妹計劃〈三〉〈四〉 | 姊妹計劃 | v1 圍欄沒有 kind：cells 為空、cell_errors 列每個缺 kind 的入口 |
| `security list` 參數 | `--commit <sha>`、`--all`、`--questions` | 前者見本篇〈四〉，後兩者見姊妹計劃 | 兩篇 | — |

另有四份不在圍欄裡的受版控檔，格式也在本篇定：`.lumos/security-tools.json`（工具清單，〈三〉）、`.lumos/security-approvers`（准用公鑰，〈四〉）、`.lumos/security-revisions.json`（核可修訂紀錄，〈四〉）、`.lumos/config.json` 的 `security_evidence` 鍵（擋或只提醒，〈四〉）。證據圍欄 `lumos-evidence-v1` 是另一種圍欄、自己的 `schema_version: 1`，見〈二〉。

**v1 與 v2 怎麼並存**：
- 新工具同時讀 v1 與 v2：每一塊圍欄依自己的 `schema_version` 讀，同一個庫可以混用；v1 塊裡出現 v2 鍵照舊是「未列出的欄位」錯誤，要用 v2 鍵就把那一塊升成 2。
- 上線順序：先發「雙讀版」工具給所有專案，確認都升上去之後，消費專案才准把圍欄升成 2；在那之前寫 v2 圍欄的專案，舊工具會整塊拒收（現況 `schema_version` 只收 1，設計審 r1 實跑,見 `governance/review-reports/安全主張驗收閘/r1-intake.md` 的〈r1 機械重現〉）。
- 回退到舊工具之前，消費專案要先把 v2 圍欄降回 1（拿掉 v2 鍵），寫進〈回退〉。

## 二、合格驗證的判準：每種證據怎麼由真實執行結果機械判定

### 證據種類（schema v2，契約變更）

盤點 v1 的五種（behavior、fault_sensitivity、review、deployment、dependency_scan）表達不了並發壓測、靜態分析、秘密、動態掃描、模糊測試與設定掃描。v2 改成下表；新增種類照盤點規矩升 schema_version，不用未知字串冒充。

| 種類 | 證明什麼 | 合法對照要求 | 允許的 format |
|---|---|---|---|
| behavior | 非法操作被正確拒絕、資料與副作用不變（單元、整合、HTTP 實測） | 同一份證據必須另有合法操作成功的案例，與前置斷言（目標存在、身分正確） | `junit` |
| fault_sensitivity | 只拿掉這條防護時，同一支測試的目標斷言翻紅、還原再綠 | 基準綠、還原綠，且還原版與基準版指紋相同 | `tq_capture`、`guard_kill` |
| concurrency | 重送、並發、壓力下他人操作仍不生效 | 同次執行另有合法流量成功計數，避免服務掛掉也「全被拒」 | `k6_summary`、`junit`（並發測試） |
| static_analysis | 指定規則在指定範圍掃過、沒有未處置的命中 | 同工具同版本對已知陽性樣本命中（校準） | `sarif` |
| dependency_scan | 指定鎖檔掃過、沒有未處置的已知漏洞 | 校準：已知有漏洞的鎖檔樣本命中 | `sarif` |
| secret_scan | 指定範圍掃過、沒有未處置的秘密 | 校準：植入假秘密的樣本命中 | `sarif` |
| dynamic_scan | 對本機或已授權目標掃過、登入狀態成立、路由有觸及 | 校準：已知漏洞路由命中；加登入成功證據 | `sarif` |
| fuzz | 指定目標跑了足夠次數、沒有未處置的當機 | 校準：已知會當的種子確實被抓到 | `junit`（一個 fuzz 目標＝一個案例） |
| config_scan | 容器、IaC 或部署設定掃過、沒有未處置的違規 | 校準：已知錯誤設定樣本命中 | `sarif` |
| deployment | 實際部署設定符合（沒有工具時） | 人工核對；跟 review 同一套審查紀錄規則 | `review_record` |
| review | 判準獨立、適用性、合法對照是否真的合法等人工判斷 | 不是機械判定；依 d2、d8 要有審查紀錄，閘門核紀錄齊全、審查人不是作者、審查人種類、版本綁定與時效 | `review_record` |

- **種類 × 格式只准用上表那一欄**：圍欄項的 `kind` 跟 `format` 不在同一列，判 `invalid:kind_format_mismatch`；工具在清單登記的工具類別（〈三〉的表）產生不了這個種類，判 `invalid:tool_kind_mismatch`。這樣 secret_scan 拿一份兩個案例都通過的 JUnit 就過不了關。
- 一筆 `review_record` 只算它自己宣告的那一個 `kind`：護欄同時要 review 與 deployment，就要兩項，不能一筆紀錄算兩次。

護欄條目在 v2 另外新增一個選填欄位 `question_refs`：這條護欄的權限或適用性答案所在的待決問題，寫成 `<節點>#Qn`（指消費專案計劃開頭欄位的 `pending_questions`）。S15 只看這個欄位：列了的題目只要有一題不是「已決」或「已驗」、或找不到，該護欄整體判 unsound（`question_open`）；沒列就不判這一項（盤點計劃 v1 沒有護欄連到待決問題的欄位，工具不從文字猜是哪一題）。解析走既有 `_pq_decision_target`、`_pq_decision_state` 那一組 `_pq_*` 函式（同族的「節點#編號」解析），不另寫。

**最低種類怎麼算（`insufficient_required_evidence` 的唯一擁有者在本篇閘門）**：
- 每條資安護欄的 `required_evidence` 不能比它全部威脅類別最低種類的**聯集**少；最低種類與「沒有工具時改成什麼」的替代欄以 [[Systems/資安威脅類別表]] 為準。
- 「有沒有工具」只看要推的提交裡的 `.lumos/security-tools.json`：某個最低種類要的工具類別在清單上一個核可工具都沒有，才照類別表的替代欄換成替代種類（例如沒有秘密掃描工具時 secret_scan 換成 deployment）；不由作者在護欄裡自述沒工具。清單讀不出來時不做任何替代，照原最低種類判。
- 只有閘門讀得到工具清單，所以 `insufficient_required_evidence` 只由閘門（與同一支函式的 `security evidence`）判；`security list` 不判這一項，姊妹計劃 S5 指到本篇 S14。
- 這是防「為了合格而合格」的第一道：作者不能只宣告最好過的那一種。每類的最低集合都含 `review`，因為判準獨立（V1）機械做不到。

### 證據從哪來：沿用既有收證，外部工具只讀它自己的輸出

依有效決策（[[Projects/後端工程提問與證據擴充_計劃]] d6：證據走既有測試綁定與破壞測試，塞不進的再另開小計劃），不另建證據帳：
- **behavior，來源是 Invariant**：bound-tests-gate 的推送當場真跑不能當資安證據來源（2026-10-19 讀 `scripts/lumos` 的 `_bound_tests_for_diff` 與 `_bound_tests_check`、`.github/workflows/ci.yml` 的 code-loop gate 步驟）：它只跑這次改動波及到的合約，沒被波及的合約不跑；CI 那一步設了 `LUMOS_SKIP_BOUND_TESTS=1` 整道跳過；低風險推送帶 `--bound-tests-advisory`，紅了只提醒不擋。所以資安的 behavior 證據不分來源，一律要有自己的執行收據（工具輸出檔加證據圍欄，跟非 Invariant 的 behavior 同一條路），閘門讀收據判；bound-tests-gate 照舊管業務合約，它當次的綠燈不升格成資安證據。
- **fault_sensitivity**：兩條既有路擇一。
  - ① guard kill：照表態閘的做法（`code-loop dispositions` 寫表態時在本機算背書、存進會被提交的治理帳 `docs/.governance-log.jsonl`），新增子命令 `lumos security backing <護欄 id>`：在本機讀 `.kill-log.jsonl`、沿用合約背書的有效列判法（`_backing_valid_rows`：head_sha 是目標版本的祖先、中間只動簿記檔；`_backing_judge_groups`：同一配方組至少一筆非弱的 killed、沒有 survived），把結果連同護欄 id、revision、配方 id、配方改到的檔與 head_sha 寫進治理帳；閘門（本機與 CI）只讀治理帳那一筆，不讀 kill-log。原因：kill-log 在 scaffold 寫的 `.gitignore` 裡、不進消費專案版控，推送前的 CI 讀不到。治理帳讀取走既有 `_ledger_lines`。
  - 背書的冪等鍵是（護欄 id、種類、head_sha）：同鍵已有一筆就不再寫；閘門讀到多筆時只取 head_sha 等於要推的提交或是它祖先的那幾筆裡最新的一筆。沒有任何一筆判 `missing:backing_missing`；背書的 head_sha 不是祖先、或中間動到非簿記檔，判 `stale:binding_changed`。
  - ② test-quality check：閘門自己從要推的提交讀三份 capture，重跑同一套 load_receipt 與三階段核對，不採信作者存的 check 結果檔。`check()` 現在吃 argparse 參數並寫輸出檔，所以把核對本體抽成只吃資料的純函式，放在 `scripts/test_quality.py` 自己裡面（它的家是 [[Systems/test-quality-cli]]），`check()` 改成呼叫它；抽出前後 `test-quality check` 的輸出與既有測試照綠；`scripts/lumos` 裡 `_TEST_QUALITY_BUNDLE_DIGESTS` 的雜湊跟著更新。配套缺檔（`_test_quality_load_bundle` 回部署不完整）而專案有資安登記痕跡時，整道擋 `toolchain_incomplete`，不放行。
  - **配方對到哪條護欄是新增的對應方式**：現有配方的 `covers` 是棧別檢核題的題號（`_backing_judge_groups` 拿題號 qid 比），沒有任何「這個配方守哪條 Invariant 或資安護欄」的比對。本篇新增：證據圍欄的 fault_sensitivity 項寫明 `recipe_ids` 與它對的護欄 id，背書只認圍欄列名的配方；配方改到的每支檔都要在那一項的 `bindings` 裡，不在判 `invalid:kill_recipe_unbound`（擋「拿一個不相干、早就 killed 的配方 id 冒充」）。不沿用 `covers`，也不從配方內容猜。
- **其他種類與全部 behavior**：工具自己的標準輸出檔，進消費專案版控；由那條護欄引用的 Verification 節點正文裡一塊 `lumos-evidence-v1` JSON 圍欄指路。
  - **跟盤點圍欄的關係**：盤點規定它自己的 `lumos-security-v1` 圍欄只准在 Systems，放在別處列 `misplaced_block`；`lumos-evidence-v1` 規定反過來：只准放在 Verification。兩種圍欄共用同一支讀法：把 `_secinv_blocks` 改成吃「圍欄標記」與「准放的節點類型」兩個參數，底下照舊用 `_fence_regions` 的嚴格結果（[[Systems/lumos-cli-read]] 已定另寫一份 toggle 或正則就是第二套邊界判定），盤點的 `misplaced_block` 判法只認 `lumos-security-v1`，不受影響。JSON 一律用 `_secinv_json_loads`（拒重複鍵、NaN、巢狀太深）。一篇一塊、未閉合或多塊或壞 JSON 都列錯並判讀取不完整，不退回「這篇沒有證據」。
  - **配對規則**：一項只算 `control_id` 等於引用這篇的那條護欄的證據；項的 `kind` 必須等於該護欄 `evidence_refs` 指到這篇那一列的 `kind`，不等判 `invalid:evidence_kind_mismatch`；沒有任何護欄引用的項只列提醒 `orphan_evidence_item`、不擋。Verification 節點本身的 `status` 是 superseded 或 stale 時，它裡面的每一項都判 `stale:verification_node_stale`，不比盤點的 evidence_check 鬆。
  - **鍵名與必填**（頂層物件 `{"schema_version": 1, "items": [...]}`，兩個鍵都必填、不准有未列的鍵；`items` 每項不准有未列的鍵）：

| 鍵 | 必填 | 型別與意思 |
|---|---|---|
| `kind` | 必填 | 證據種類，值域見上表 |
| `format` | 必填 | `junit`、`tq_capture`、`guard_kill`、`sarif`、`k6_summary`、`review_record` 之一；跟 `kind` 的組合照上表 |
| `path` | 必填（`guard_kill` 除外） | 證據檔相對 repo 根的路徑；`tq_capture` 是三份 capture 的目錄 |
| `report_sha256` | `junit`、`sarif`、`k6_summary` 必填 | 證據檔內容的 sha256；閘門從要推的提交讀那個檔、自己算雜湊比對，不等判 `invalid:report_hash_mismatch` |
| `coverage_path` | `sarif` 必填 | 覆蓋證明所在的工具自家輸出（Semgrep JSON、ZAP 統計等）；工具的覆蓋證明本來就在 SARIF 裡時填同一個路徑 |
| `tool`、`tool_version` | 必填（`review_record` 除外） | 工具名與版本，要對得上工具清單 |
| `control_id`、`control_revision` | 必填 | 涵蓋的護欄 id 與 revision；一項只對一條護欄 |
| `bindings` | 必填 | `[{"path":…, "blob":…}]`，綁定檔與當時的 git blob |
| `test_sources` | `junit`、`tq_capture` 必填 | 測試原始檔路徑陣列（仿 test-quality 的 `--test-source`），每一支都要在 `bindings` 裡 |
| `environment_ref` | 必填（`review_record` 除外） | 一支受版控的環境描述檔（Dockerfile、部署設定、鎖檔之一），必須在 `bindings` 裡 |
| `targets` | 必填 | 物件：`tests`、`legit_controls`、`preconditions`、`rules`、`thresholds`、`recipe_ids`（意思同前，都是字串陣列）；該種類要的鍵缺了或是空陣列都判 `invalid:targets_empty`，用不到的鍵省略 |
| `calibration_path` | 掃描類必填 | 校準輸出檔路徑；校準樣本夾具也要在 `bindings` 裡 |
| `environment` | 必填 | 執行環境描述字串，只記不比對 |
| `observed_at` | 必填 | 觀察時間（ISO 8601 含時區）；晚於要推的提交的提交時間判 `invalid:observed_in_future` |
| `vulndb_fetched_at` | dependency_scan 必填 | 漏洞庫抓取時間，只收 ISO 8601 含時區；不收版本號（算不出幾天） |
| `reviewer`、`author`、`reviewer_kind`、`judgments`、`expires_on` | review_record 必填 | 審查人、被審內容的作者（字串或字串陣列）、`ai` 或 `human`、這筆紀錄審了哪幾項判斷（id 見〈機械做不到的判斷〉）、到期日 |
| `signature` | `reviewer_kind: human` 必填 | 依 d7 的內容簽章，簽的內容見〈四〉；沒有或驗不過一律當成 `ai` |

  - 圍欄本身讀不出來（壞 JSON、未列的鍵、必填缺、型別錯）時，那條護欄引用到這篇的所有證據判 `invalid:evidence_fence_invalid`。
  - 理由：盤點已定「evidence_refs 指 Verification、由 Verification 指路原始報告」；指路從散文改成機器讀得懂的一塊，家還是同一個 Verification 節點，不是第二本帳。
  - 不選：把報告路徑塞進護欄條目（盤點已否決）；frontmatter 巢狀 YAML（要擴通用解析器）；lumos 自己再存一份雜湊帳（後端計劃 d4 已作廢的方向）。

### 綁版本與環境指紋

- 推送時以要推的那個提交為準：閘門用 git 讀那個提交裡每個綁定檔的 blob、證據檔與工具清單，跟證據記的比；任一不同、或綁定檔不在了，就是 stale。不讀工作目錄（見〈四〉的〈從提交樹產快照〉）。
- **報告本身也綁**：JUnit、SARIF、k6 的 `report_sha256` 讓「改了報告一行」變成 invalid；`tq_capture` 沿用 receipt 自己記的雜湊。作者把綁定的 blob 改成新版、卻不重跑測試時，報告雜湊沒變但綁定檔的內容是新的——這擋不住，因為雜湊只證明「這份報告與這些檔一起被提交」，不證明報告是用這些檔跑出來的；這一句寫進每份證據的 `limitations`，由〈機械做不到的判斷〉的「報告是不是真的跑出來的」承擔。
- 綁定集合至少要涵蓋：護欄所在 Systems 節點 about_code 列的全部程式檔、`test_sources` 列的測試原始檔、腳本、鎖檔、runner 設定、`environment_ref` 那支環境描述檔、校準夾具；少一類就是 `binding_incomplete`（invalid）。借「每支檔有家」：家列了哪些檔，那條護欄的證據就得綁哪些檔，作者不能挑；測試原始檔則由作者明列——測試 id 推不回檔案（Gradle、pytest、Jest 的 id 形狀各不相同），所以照 test-quality 的做法要呼叫端明示。
- 護欄 revision 改了、威脅類別或必要種類改了，舊證據 stale。
- 工具版本要等於消費專案工具清單（見〈三〉）登記的釘版本；不等就是 `tool_version_mismatch`（invalid）。工具輸出自己帶版本的（SARIF 的 driver.version、k6 新格式的 k6_version）以輸出為準，作者寫的只用來交叉比對。
- **環境**：`environment_ref` 指的那支描述檔（Dockerfile、部署設定、鎖檔）在綁定裡，內容一改舊證據就 stale；`environment` 字串只記描述、不比對。描述檔沒寫到的環境差異（作業系統、執行時才決定的資料庫版本）仍偵測不到，這一句寫進 limitations。
- 機械能保證的只到「這份結果與這些檔案的這個內容一起被提交」；結果是不是偽造的，雜湊證明不了（見〈機械做不到的判斷〉）。

### 每種格式的「合格」判定

所有格式共用三條：真的跑過（案例數或請求數或掃描檔數大於 0、有觀察時間、版本與綁定對得上）；目標有被評估到（指定的測試 id、規則 id、門檻真的出現在結果裡，宣告清單不能是空的）；失敗與 invalid 分開：failed＝證據有效地跑完、結論是負面，代表有缺陷（行為證據的目標斷言紅、掃描對宣告規則有未處置的命中、壓測安全計數超標，或故障證據裡拿掉防護後測試照綠的 survived——那是「測試咬不住」的缺陷）；invalid＝沒驗到（跑不起來、零案例、逾時、非目標失敗、格式或綁定不合格）。兩者都擋，但訊息不同。

**同一護欄同一種類有多筆證據**：每筆各自判；只要有任何一筆不是 qualified，這個種類就取那幾筆裡最差的判定（優先序 failed、invalid、stale、uncalibrated），不准用好的蓋壞的。逐筆判定照樣在 `security evidence` 列出，所以「一壞一好」時人看得到好的那份是 qualified、種類卻不是。作者把壞的那份從圍欄刪掉是一個看得到的動作，會留在 diff 與 Verification 的歷史裡；機械上擋不住刪除，這一句寫進 limitations。

| 格式 | 讀法（沿用） | qualified 的條件 | invalid 的條件（failed 與 uncalibrated 另註） |
|---|---|---|---|
| JUnit XML | 沿用 `scripts/test_quality.py` 的 junit()（拒 DTD、核對 suite 計數、拒重複身份、拒零案例、拒 suite 層 error），餵它從提交讀出的位元組 | 宣告的非法案例與合法對照案例都在、都 passed、不是 skipped；合法對照與非法案例是不同的測試身份 | 零案例、目標不在或被跳過、suite error、計數矛盾、缺合法對照（`missing_legit_control`）、宣告清單為空（`targets_empty`）、雜湊不符 |
| test-quality 三份 capture | 沿用 load_receipt 與三階段核對（抽出的純函式） | 只有目標翻紅且是斷言失敗、基準與還原全綠、還原指紋等於基準 | 非目標失敗、非斷言失敗、hash 不符、receipt 不是 executed；survived 判 failed |
| guard kill 帳 | 治理帳裡 `security backing` 寫的那一筆 | 非弱的 killed、head_sha 是祖先且中間只動簿記檔、配方 id 列在證據圍欄的 `recipe_ids`、配方改到的檔都在 `bindings`、圍欄的 `control_id` 是這條護欄 | killed_unattributed、timed_out_weak、drifted、abort、error、全是弱證據、配方沒綁；survived 判 failed；沒有那一筆判 missing |
| SARIF 2.1.0 | 新寫一支只吃資料的嚴格解析（見下〈SARIF 另寫嚴格解析〉），不共用新增告警閘的寬鬆解析 | 有 run、`results` 是陣列（空陣列＝跑完沒找到）、driver 名與版本對得上清單、`coverage_path` 那份有登記的覆蓋證明、對宣告規則沒有未處置的命中、同工具同版本的校準檔對每一條宣告規則都命中 | 沒有 run、`results` 是 null、invocation 標失敗、通知裡有 level=error、`version` 不是 2.1.0、缺 driver 名、沒有覆蓋證明、宣告規則為空；有未處置命中判 failed；缺校準、校準版本不同、校準沒命中某條宣告規則判 uncalibrated |
| k6 summary | 新寫一個只讀 JSON 的小讀法：讀 k6 新的機器可讀摘要（帶 k6_version 與腳本全文） | 版本等於清單、摘要裡的腳本全文雜湊等於該提交的腳本 blob、請求數不少於工具清單登記的下限、合法流量成功計數大於 0、宣告的安全指標都在而且門檻全過 | 版本或腳本對不上、請求數為 0 或低於登記下限、宣告的安全指標不在結果裡、門檻不是允許的寫法、退出碼是逾時或中止類 |
| 其他工具自家 JSON | 先不接；能出 SARIF 的工具一律走 SARIF | — | 沒有讀法的格式一律判 `unsupported_format`（invalid），不猜 |

k6 的坑（2026-10-19 本機 k6 v2.3.0 實測，見 PRIOR-ART）：
- 舊格式的 `--summary-export` 裡門檻值是反的：`true` 代表「沒過」；`handleSummary` 收到的舊格式則是 `ok: true` 代表過。兩種都不帶 k6 版本。
- 新的機器可讀摘要（`--new-machine-readable-summary`）帶 `metadata.k6_version` 與 `config.script` 腳本全文，但沒有門檻結果。
- 所以安全門檻不讀 k6 的門檻旗標，改由閘門用新格式的計數自己算，而且只接受最單純的一種寫法：`指標 計數或比率 比較符號 數字`（例如自訂計數 `foreign_effects` 的 count 等於 0）。延遲 p95 這類效能門檻不是安全主張，不進安全證據。
- 自訂計數從沒被加過時可能不出現在摘要裡；這樣最好的結果（`foreign_effects` 一次都沒發生）反而會判 `k6_metric_missing`。所以宣告的每個安全指標，腳本開頭都要先 `add(0)` 讓它出現；沒出現照判 `k6_metric_missing`，不當成 0。
- 請求數下限不由作者在圍欄宣告，由工具清單那一列登記（每支腳本一個 `min_requests`），清單沒登記就判 `k6_requests_below_floor`。
- 不選：同時讀新舊兩種檔（同一次執行只吐得出一種，兩次執行就不是同一份證據）；信任作者宣告的退出碼（只拿來交叉比對）。

REVISIT:[when-file:.lumos/security-tools.json][by:2027-01-31] order-demo 實作 k6 讀法時,用 k6 v2.3.0 實測一次自訂計數從沒加過與先 add(0) 兩種情況在新格式摘要裡出不出現,把結果寫回〈每種格式的合格判定〉的 k6 那幾行

**SARIF 另寫嚴格解析，不共用新增告警閘的讀法**（2026-10-19 讀 `scripts/lumos` 的 `_lint_run_and_parse`）：那支函式會自己 `Popen` 執行指令，不是純解析；`results` 是 null 時用 `or []` 當成空陣列，缺 driver 名的 run 直接跳過，不看 invocations、notifications，同時接受 SARIF 1.0 與 2.1。這些對新增告警閘是刻意的寬鬆（要吃各家 linter，包括只吐 v1 的 dotnet），對安全證據正好是 invalid 條件。取捨：新寫一支只吃資料的嚴格解析給安全證據用；新增告警閘的既有行為一字不改。
- **uri 正規化現在就決定：不抽、各寫**。理由：那一小段現在內嵌在 `_lint_run_and_parse` 裡、沒有獨立函式；抽出來就得改一支會執行外部指令、有既有測試釘住的函式，只為了共用十來行；而兩邊的語意也不同（新增告警閘遇到解析不了的 uri 是跳過那一筆，安全證據要判 invalid）。安全證據自己寫一支，在本篇子系統裡測。
- 不選：直接共用 `_lint_run_and_parse`（要嘛新增告警閘開始拒收它現在吃得下的 v1 與缺欄位報告，要嘛安全證據把 null 當空陣列）。

**SARIF 證明不了「真的掃到東西」，要另一份覆蓋證明**（2026-10-19 查各工具官方文件與原始碼）：規格只把 `invocations` 的 executionSuccessful 列為選填，`rules` 可以只列打中的規則、`artifacts` 不必列全部掃過的檔；gitleaks 與 ZAP 的 SARIF 沒有 invocations，Trivy 預設有發現也回 0，OSV-Scanner 回 128 是「沒找到可掃的套件」、CodeQL 回 32 是「沒找到可分析的程式碼」。所以每個掃描工具在工具清單登記一種覆蓋證明，從固定的小集合裡選，閘門照它讀 `coverage_path` 那份工具自己的 JSON 或 SARIF 欄位：SARIF invocation 成功且無 error 通知、Semgrep 的 `paths.scanned` 非空、OSV-Scanner 以 `--all-packages` 輸出的套件清單非空、Trivy 或 Checkov 的設定檢查計數（Successes、resource_count）大於 0、ZAP 的內部統計（登入成功數、送出請求數、主動掃描 URL 數）大於 0。集合外的工具判 `coverage_unproven`（invalid），要用就先補讀法與正反樣本。退出碼一律只拿來交叉比對，不當主判據，因為各工具語意互相衝突（gitleaks 的 1 同時代表有發現與出錯）。

**依賴掃描結果跟著漏洞庫變**：OSV-Scanner、Trivy 查的是會更新的漏洞庫，釘工具版本不夠。證據要記 `vulndb_fetched_at`；距今（UTC 日期）超過多少天算 `stale:vulndb_stale` 待使用者裁（Q5，建議 14 天：第 14 天仍有效、第 15 天起 stale）。

**合法對照強制存在**：behavior 要宣告合法對照案例 id；concurrency 要宣告合法流量成功計數指標；掃描類要有校準檔。前兩者缺了或是空陣列判 invalid，掃描類缺校準判 uncalibrated；三者都擋，不是提醒。

**「找到 0 個問題」不等於證成**：掃描類只有「跑過、沒找到」加上「同工具、同版本、同規則對已知陽性樣本找得到」兩份一起，才算 qualified；只有前者判 `uncalibrated`，照擋。校準檔必須對 `targets.rules` 的每一條都命中，少一條判 `uncalibrated:calibration_rule_missing`。校準樣本放消費專案的固定夾具、進綁定，跟正式掃描同一版本的工具與規則；工具或規則升版就要重做。

### 讀不可信資料的上限與失敗處理

證據檔是不可信資料，而且比筆記大得多（大專案的 SARIF、JUnit 動輒數 MB）。盤點的上限（單檔 2 MiB、總量 64 MiB、一萬檔）是為 Markdown 筆記定的，不沿用：
- 單一證據檔上限 16 MiB：比 test-quality `read()` 的 10 MiB 寬，因為閘門從 git 讀位元組直接餵只吃資料的解析，不經 `read()`；16 MiB 夠裝中型 repo 的 Semgrep、CodeQL SARIF，再大多半是掃描範圍設錯。
- 一次判定讀的證據總量上限 256 MiB（盤點總量的 4 倍，給「一千條護欄、每條數份證據」留餘地），證據項總數上限 10000（跟盤點檔數上限同一個量級）。
- 超過任一上限，只把超限的那一項（或總量超過之後的每一項）判 `invalid:evidence_too_large` 並指出是哪個檔，不判整道讀取不完整，所以一份過大的 SARIF 只擋引用它的那幾條護欄。
- JSON 巢狀沿用 `_secinv_json_loads` 的深度上限；JUnit XML 在解析時數元素深度，超過 64 層判 invalid。
- 同一次判定內，以（路徑、blob）當鍵快取解析結果：一份專案級 JUnit 被一千條護欄引用，只解析一次。
- git 讀取批次化：要推的提交與起點版各用一次 `git ls-tree -r -z` 加一次 `git cat-file --batch` 取全部需要的 blob，不逐檔開子程序。
- 判定函式裡任何沒預期到的例外（型別錯、遞迴過深、記憶體錯誤）一律轉成擋下，整道代碼 `evaluation_error`，訊息指出當時在判哪條護欄、哪個檔；不放行、不印 traceback 給推送流程。

REVISIT:[when-status:Projects/安全主張驗收閘_計劃=done][by:2027-01-31] 實作完成後,對一千條護欄、每條十份證據的合成 vault 量一次判定時間與記憶體;超過 pre-push 可接受的時間就調上面的上限或快取,並把量到的數字寫回本節

### 機械做不到的判斷（承接盤點計劃 Q1 與母計劃 V1、V4）

以下由 review 證據種類承擔。依 d2，要有一筆非作者的審查紀錄才放行；依 d8，紀錄分 AI 審與人審，兩者能放行的範圍不同。紀錄寫在 Verification 的證據圍欄（`format: review_record`），閘門核：
- 紀錄存在；`reviewer` 跟 `author` 比對時先去頭尾空白、統一全形半形、不分大小寫，任一作者等於審查人判 `invalid:review_not_independent`。
- 綁定的程式與護欄 revision 等於要推的提交，一變判 stale；`expires_on` 當天有效、隔天判 `stale:review_expired`；`expires_on` 晚於 `observed_at` 加 90 天判 `invalid:review_expiry_too_long`（紀錄綁版本、版本一變就重審，期限只防長期沒人看，90 天對齊一季）。
- **審查人種類（d8）**：`reviewer_kind: human` 要有 d7 的內容簽章（簽的內容含護欄 id、revision、判定輸入雜湊、`judgments`、`reviewer`、`expires_on`），驗不過或沒有一律當成 `ai`。下表標「要人」的判斷，只有 human 紀錄能放行；某一項只有 ai 紀錄蓋到，該 review 種類判 `missing:human_review_missing`。
- **deployment 一律要人**：deployment 是「沒有工具時的人工核對」，代替的是一個掃描工具，所以 `kind: deployment` 的紀錄只有 `reviewer_kind: human` 且簽章有效才算數，ai 紀錄判 `missing:human_review_missing`。
- 缺紀錄判 `missing:review_record_missing`。review 的 qualified 只代表紀錄齊全、對得上版本、審查人種類夠格，不代表人工判斷本身對。

| 判斷 id | 要審什麼 | 要人 |
|---|---|---|
| `independent_oracle` | expected 是不是來自獨立來源：測試照抄錯的規則、故障照樣翻紅，fault_sensitivity 會是 qualified，但這只證明抓得到錯，不證明規則對 | 是 |
| `legit_control_real` | 合法對照是不是真的走合法路徑、非法案例是不是被真正的那道防護擋下（不是登入失敗或資料不存在代打） | 是 |
| `threshold_meaningful` | 門檻有沒有意義：例如 order-demo 既有壓測有一條 `max>=0`，永遠會過；閘門只能限制寫法，判不了有沒有意義 | 是 |
| `calibration_representative` | 校準樣本有沒有代表性 | 是 |
| `not_applicable_sound` | 不適用理由成不成立 | 是 |
| `category_sufficient` | 威脅類別與必要種類選得夠不夠 | 否 |
| `inventory_complete` | 入口盤點有沒有明顯漏項 | 否 |

- 每條護欄的 review 種類要蓋住哪幾項判斷：表裡全部「要人」的項一律要蓋；「否」的項由 AI 或人審都可以。
- **工具天花板（d8）**：AI 自己編審查內容、自己填一個不同的審查人名字，機械上擋不住；能做的只是把這種紀錄當成 ai，讓它放行不了要人的那幾項。人審的簽章只證明「持有釘住金鑰的人簽過這段內容」，不證明那個人真的讀過。這兩句寫進 review 證據的 `limitations`。
- **報告是不是真的跑出來的**：內容一致的偽造報告，雜湊與計數都對得上。閘門不執行任何工具，所有證據（含來源是 Invariant 的 behavior）都有這個限制；這一句寫進每份證據的 `limitations`。這一項不設判斷 id，因為人審也判不出來，只能靠可信的執行來源（母計劃 V5）。

## 三、工具接入：一套轉接介面，k6 只是第一個

**對照鏈（兩篇共用）**：威脅類別（[[Systems/資安威脅類別表]]）→ 需要的證據種類（同一張表的最低種類欄）→ 能產生該證據的工具類別（下表）→ 消費專案選定的具體工具與版本（消費專案的工具清單）。每個威脅類別都要回答「這要什麼工具才驗得了」，以及沒有工具時換成什麼證據（類別表有這一欄，替代規則見〈二〉）。

| 工具類別 | 產生的證據種類 | 標準輸出 | 候選工具（只是例子，裝不裝由使用者逐專案核可） |
|---|---|---|---|
| 既有單元與整合測試 runner | behavior、concurrency（並發測試） | JUnit XML | 專案既有的 Gradle、pytest、Jest 等 |
| 破壞測試與故障收證 | fault_sensitivity | kill 帳、test-quality capture | lumos guard kill、lumos test-quality |
| 壓測與並發 | concurrency | k6 新格式摘要 | k6 |
| 動態掃描（只對本機或已授權目標） | dynamic_scan | SARIF | ZAP |
| 靜態分析 | static_analysis | SARIF | Semgrep、CodeQL |
| 依賴漏洞掃描 | dependency_scan | SARIF | OSV-Scanner、Trivy |
| 秘密掃描 | secret_scan | SARIF | gitleaks |
| 模糊測試 | fuzz | 各語言 fuzzer 輸出，先經既有 runner 轉成 JUnit（一個 fuzz 目標＝一個案例） | Go 原生 fuzz、Jazzer、Atheris |
| 設定與容器掃描 | config_scan | SARIF | Trivy config、Checkov、hadolint |
| 人工或獨立審查 | review、deployment | Verification 節點本身 | — |

- **lumos 只讀、不跑、不裝**：工具裝在消費專案、由消費專案執行並把輸出存進它自己的版控；lumos 核心維持零依賴。閘門不替任何人執行掃描或壓測。簽章驗證用系統的 `ssh-keygen`（OpenSSH 內建，macOS 與 GitHub 的 Linux runner 都有），不算新依賴；找不到 `ssh-keygen` 時所有簽章都當成驗不過。
- **消費專案工具清單**：`.lumos/security-tools.json`，每個工具一列：類別、名稱、釘死的版本、安裝來源與核對方式（例如 release 的 sha256 或容器映像 digest）、核可決策（消費專案某篇筆記的 dN）、執行預算（單次與整批上限）、允許的目標（壓測與動態掃描只准 `loopback` 或核可決策裡列名的目標）、覆蓋證明（掃描類必填，從上面那個固定小集合裡選一種；非掃描類不填）、壓測腳本的 `min_requests`（壓測類必填）。閘門從要推的提交讀這個檔，用 `_secinv_json_loads` 嚴格讀：壞 JSON、未列的鍵、型別錯一律當成「清單讀不出來」，裡面每個工具都算沒登記，不像 `_lint_load_config` 那樣靜默回空。沒列在清單上的工具，產出的證據判 `tool_unregistered`（invalid）；掃描類沒填覆蓋證明判 `coverage_unproven`（invalid）。
- **壓測與動態掃描的目標限制**：證據要記目標位址；不是回環位址、也不在核可清單上，判 `target_not_authorized`（invalid）。這只檢查作者記的值；真正防誤打靠消費專案腳本自己檢查（order-demo 的 k6 腳本已經在非本機時中止）。
- **之後接新工具**：能出 SARIF、JUnit 的工具不需要改 lumos，只要登記清單與校準樣本；只有吐自家格式又無法轉 SARIF 的工具，才在 lumos 加一個讀法，而且要先有那個工具的正反樣本。
- 理由：一個格式一個讀法，比一個工具一個讀法少；SARIF 已是本 repo 新增告警閘在用的格式。
- 不選：每個工具寫專屬解析（工具多一個就多一套）；lumos 代為安裝或執行（違反零依賴、成本與授權都不在 lumos）。

**k6 第一個接**：k6 跑在消費專案（order-demo 既有的搶購壓測腳本可參考，腳本的家在 order-demo 自己的建置與啟動節點）；釘版本照清單（容器映像 digest 或 release 二進位的 sha256）；腳本一律開新的機器可讀摘要並寫到固定路徑。安全門檻對應主張的方式以 OD-04「重送與並發不能讓他人操作生效」為例：腳本用 B 身分對 A 的有效訂單重送與並發，自訂計數 `foreign_effects`（伺服器回成功的次數，開頭先 `add(0)`）門檻是等於 0、`foreign_rejected` 不少於清單登記的請求下限，另一段 A 自己的合法流量 `legit_ok` 大於 0；k6 看不到資料庫，所以「訂單與庫存保持不變」另由同一次執行後的整合測試讀資料庫（behavior 證據），兩份一起才算這條的 concurrency 主張驗完。

**要使用者核可的**（不由 AI 決定）：每個專案裝哪些工具與版本、執行預算、壓測與動態掃描的目標，依 d4 逐專案、逐工具在要用時問使用者，AI 不自行安裝；OD-04 的 k6 實跑已依 d3 核可（order-demo、k6 v2.3.0、條件照母計劃 d8）；校準樣本放不放進消費專案版控還待人（Q8）。

## 四、閘門：code-loop check 的「安全證據」判定

**位置**：`code-loop check` 的判定函式（`_codeloop_guard_verdict`）裡，跟表態閘、新增告警閘並列、不看 tier（母計劃 d9 要求所有專案都擋），但**排在所有放行早退之前**：取到要推的提交（marker_sha）之後、推導 diff 範圍之前就判。
- 為什麼不照原案排在新增告警閘之後（2026-10-19 讀 `_codeloop_guard_verdict`）：那個位置前面有五條直接放行的早退——取不到 HEAD、merge-base 等於 HEAD、算不出 merge-base、全零起點找不到真起點、pitfalls 失敗（`return _fin(pf_fail)`）。排在後面，這五條路上安全判定根本跑不到，跟母計劃 d9 的「判不清就擋」衝突。
- 選「往前排」而不是「把這五條早退對有資安登記的專案改成擋」：安全判定看的是要推的那個提交的內容與 merge-base，不需要 diff 範圍與 tier，排到最前面就不必去改五條早退的既有放行行為（它們對其他幾道仍然照舊）。
- 取不到要推的提交時：工作目錄有資安登記痕跡（見下〈擋下條件〉）就擋，原因代碼 `commit_unavailable`；沒有痕跡照舊放行。
- 形狀照新增告警閘那一步：沒擋回 None，擋了回帶 `reason_kind: security_evidence` 的結果；帶 `--keep-going` 時各道各自記、各自印。
- **tag 與其他非分支的 ref 也判**：現在 pre-push 對不是 `refs/heads/*` 的 ref 根本不叫 `code-loop check`、只提醒，CI 也只聽 main 的 push（設計審 r1 實跑,見 `governance/review-reports/安全主張驗收閘/r1-intake.md` 的〈r1 機械重現〉）。新增 `code-loop check --security-only --at-sha <sha>`，只跑這一道；pre-push 在非分支那條路徑也呼叫它、照擋；CI 加 `push: tags` 觸發，跑同一個指令。母計劃 d9 要的是「推得出去的東西都判過」，不只分支。
- 本機與 CI 判定完全相同：依 d7，所有核可都是內容簽章，兩邊都用同一份 merge-base 版的公鑰清單在本機資料上驗；日期一律取 UTC，所以台灣深夜與 CI 不會跨日不同步。CI 那一步目前沒帶 `--keep-going`，訊息會只印第一道擋下，實作時一起評估。

**要跟著改的地方**（避免漏接）：
- `scripts/lumos`：合併各道明細的鍵清單（`_codeloop_kg_finish` 現在只列 bound_tests、dispositions、lint_new）、每次判定開頭清掉的暫存屬性（加 `last_security`）、放行時的小結。
- `scripts/lumos`：新開 `_cl_say_sec_block`，跟 `_cl_say_disp_block`、`_cl_say_lint_block` 同族，印三段式——發生什麼（哪條護欄哪個種類、原因代碼）、為什麼在意（這條安全主張現在沒有合格證據）、怎麼修（指令獨立一行）；`_cl_say_block` 遇到 `security_evidence` 分派過去，不落進印「這次高風險改動還不能推」的預設分支。
- `scripts/lumos`：新子命令 `security evidence`、`security backing`、`security payload`（印出要簽的規範化 JSON，見下）、`code-loop check --security-only`、`security list --commit`；新函式 `_secinv_snapshot_tree`（見下〈從提交樹產快照〉）；`_secinv_blocks` 參數化。
- `scripts/test_quality.py`：抽出核對本體的純函式；`scripts/lumos` 的 `_TEST_QUALITY_BUNDLE_DIGESTS` 同步。
- `scripts/hooks/pre-push`：擋下原因對照表 `pp_cl_reason`（有測試雙向比對）、放行時只顯示特定字樣那一行的過濾條件、非分支 ref 那條路徑呼叫 `--security-only`。
- `.github/workflows/ci.yml`：加 tag 觸發與只跑安全判定的一步。
- `scripts/test_lumos.py` 的 `_PPC_KIND_SENTENCES` 加第五句；`t_prepush_cl_reason_sentences_match_plan` 會讀 [[Projects/推送前一次列出全部擋下原因_計劃]] 裡標著「對照表四句的正本在這裡」的那一行、抽出恰好四句比對——那一行要先改成五句的正本（標記字樣跟著改成「五句」），測試裡的「四句」判準與字樣同步改，否則這支必紅。照那篇的規矩：先改計劃那一行，再改掛鉤與常數。
- git 呼叫一律走既有包裝（`_lens_git`、`_nodehome_git`），並帶 `-c log.showSignature=false`（使用者設了 `log.showSignature` 會把簽章訊息夾進輸出，`scripts/lumos` 既有註解記過這個坑）。
- pitfalls 失敗那條分支不用另外處理：安全判定已在它之前跑完。

**輸入**：要推的提交裡的盤點報告、各條護欄引用的 Verification 節點裡的證據圍欄、證據檔、工具清單、`.lumos/security-revisions.json`、`.lumos/config.json`；治理帳裡的資安背書；merge-base 那一版的盤點報告與公鑰清單。全部唯讀，不執行任何工具。

**從提交樹產快照**：盤點的 `_secinv_snapshot` 只會從工作目錄逐層開檔，`_secinv_build` 吃的是快照字典，接縫就在這裡。新增一支 `_secinv_snapshot_tree(repo_root, sha, vault_rel)`：用一次 `git ls-tree -r -z` 列檔、一次 `git cat-file --batch` 取內容，產出跟 `_secinv_snapshot` 同形狀的快照；沿用同一組容量常數與錯誤代碼（`file_too_large`、`too_many_files`、總量超限；樹裡的符號連結照 `symlink_rejected`）。要推的版與 merge-base 版都用它，不讀工作目錄，所以 checkout 停在 main 而推的是別的分支時也判對版本。`security list` 加 `--commit <sha>` 走同一支，S4 比的是「`security list --commit <sha> --json`」與閘門對同一提交的輸入。不另寫第三條快照路徑，也不沿用 `_drift_tree_env`（它沒有盤點那套容量上限）。
- 廉價預檢：先用一次 `git grep -l -F lumos-security-v1 <sha> -- <vault>` 找出提到這個字樣的檔；一篇都沒有就直接判「沒有登記痕跡」，不建完整快照。有命中才建快照、照盤點的嚴格讀法判有沒有真的圍欄（散文裡提到這個字樣不算痕跡）。

**起點一律是 merge-base**：
- 起點＝要推的提交跟預設分支在這次推送之前的位置的 merge-base：pre-push 用遠端追蹤的 `origin/<預設分支>`；CI 的 push 事件用 `before`（預設分支推送前的位置）；pull_request 事件用 base 的提交；tag 推送用 `origin/<預設分支>`。不用「這個 ref 的遠端舊值」——那是這個分支上次推送的位置，中途若有一次繞過把縮小推上去，之後每次比的都是已經縮小的版本。
- 多個提交的推送一律只對 merge-base 判，不逐提交、不看要推的提交的母提交。
- 預設分支還不存在（新 repo 的第一次推送，根提交就帶登記）：起點＝空樹，所有護欄當成新增照判。
- 預設分支存在但跟要推的提交沒有共同祖先：擋 `freeze_base_unavailable`。
- 淺層 clone（`git rev-parse --is-shallow-repository` 是 true）：擋 `shallow_clone`，訊息給一行 `git fetch --unshallow`；CI 的 checkout 已是完整歷史（`fetch-depth: 0`）。

**必驗集合與判定輸入都以 merge-base 版為底**（承接母計劃 G1 的凍結要求）：
- 必驗集合 = 要推的提交裡 active 且關注面含 security 的全部條目，再加上 merge-base 版有、但這次被刪除、被降成 candidate 或 retired、或 `concerns` 拿掉 security 的條目——後者除非有一筆簽章有效的**核可修訂紀錄**，否則照樣當必驗、用 merge-base 版的內容判（被刪的那條沒有證據可讀，判 `missing:control_removed_unapproved`）。
- **判定輸入也凍結**：同一條護欄的 `required_evidence`、`threat_categories`、`assets`、`surfaces` 跟 merge-base 版比少了任何一個值、或 `evidence_refs` 有任何一列被換掉或刪掉，都算「變弱」。變弱而沒有核可修訂紀錄時，用新舊兩版的聯集判（集合欄位取聯集，`evidence_refs` 新舊兩邊的都要合格），不用作者改弱的那一版；`security evidence` 列出哪一欄變弱、照聯集判。只新增不刪除不算變弱。
- **核可修訂紀錄放在受版控的獨立檔** `.lumos/security-revisions.json`，不放在 Systems 節點裡，所以整篇 Systems 節點刪掉、改名或搬家都還讀得到。每筆：`control_id`、`before`（revision 與判定輸入雜湊）、`after`（同上）或 `removed: true`、`decision_ref`、`approved_on`、`signature`。簽章簽的是這一筆去掉 `signature` 之後的規範化 JSON，驗法同下〈內容簽章〉。一筆紀錄只核可「從這個雜湊變到那個雜湊」，同一條護欄改成別的樣子要另一筆；舊紀錄可以直接刪，刪了只會少一筆可用的核可，不會放寬。`decision_ref` 指不到有效決策（走 `_pq_decision_state`）、或缺任何一欄、或簽章驗不過，紀錄不算數。
- 起點算不出來而專案有資安登記痕跡：擋，代碼見上；判不清不放行。

**擋下條件**（任一）：
- 必驗集合裡有任何條目的整體判定是 unsound（規則見〈一〉的彙總規則）。
- 盤點讀取不完整或登記錯誤（`errors`，不含姊妹計劃的格子層錯誤 `cell_errors`；閘門不讀 `cell_errors`），而要推的提交或 merge-base 版有資安登記痕跡：判不清就擋，不當零條目放行。
- **登記痕跡只認 `lumos-security-v1` 圍欄**（盤點讀到一塊合格的或是 `malformed_block`）；只有 `flag/security-relevant` 標籤、零條目的專案不算痕跡，只在 `security evidence` 與 `--json` 列提醒。2026-10-19 在工具鏈自己的工作樹實跑 `security list`：`read_complete: true`、`registration_complete: false`、零條目、`errors` 空，有兩篇只帶標籤、沒有圍欄——照舊判法會被當成「有痕跡又登記不完整」擋下工具鏈自己的每次推送，照現在的判法不擋（設計審 r1 實跑,見 `governance/review-reports/安全主張驗收閘/r1-intake.md` 的〈r1 機械重現〉）。
- 必驗集合**意外為空**而專案有資安登記痕跡：要推的提交的必驗集合是空的，而 merge-base 版的必驗集合不是空的、這中間又沒有把它們全部移出的核可修訂紀錄。只有 candidate、從來沒有 active 條目的專案，merge-base 版也是空的，不算意外為空，照下面〈不受影響〉放行並列提醒。
- 凍結比對的起點算不出來、淺層 clone、取不到要推的提交、test-quality 配套缺檔（見上）。
- 判定函式本身出錯（`evaluation_error`）。
- 例外過期、超過 30 天、缺欄位、簽章驗不過或核准的內容跟現在不同——這些情況例外不算數，底下的種類照原判定。

**擋或只提醒的設定**：`.lumos/config.json` 的 `security_evidence.gate`，值 `block`（預設）或 `warn`，跟 `node_home.gate`、`note_shape.gate` 同族。改成 `warn` 時判定照算、照印、照記帳，只是不擋；但這份設定要有 d7 的內容簽章（簽 `{"type":"gate_setting","value":"warn","approved_on":…}`，簽章放在同一個鍵下的 `signature`）才生效，沒簽或驗不過一律當成 `block`，並印一行說明為什麼。所以 AI 改一行設定關不掉這道閘；使用者要給過渡期（Q4）或誤擋時要退，簽一次就能降成只提醒。

**不受影響**：
- 沒有任何資安登記痕跡的專案，這一步回 None、不寫治理帳，輸出與退出碼跟現在逐字相同；只在 `--json` 輸出多一個鍵 `security_evidence: {"status": "no_registration"}`，文字輸出不加行。這樣沒登記的專案每次推送不會弄髒工作樹、也不讓治理帳增長。
- 純業務合約（concerns 只有 business）不進必驗集合。
- candidate 不擋、只列提醒；要不要改成也擋待使用者裁（Q3）。
- review 種類照 d2、d8 判，沒有合格的審查紀錄或過期就擋（見〈機械做不到的判斷〉），不再有「只宣告不擋」的狀態。

**訊息形狀**（由 `_cl_say_sec_block` 印，三段式）：每個擋下的「護欄 × 種類」：
- 發生什麼：`安全證據 擋下：OD-01 [fault_sensitivity] invalid:zero_cases 證據 governance/…/receipt.json`；護欄層的問題寫成 `安全證據 擋下：OD-01 [護欄] insufficient_required_evidence`。
- 為什麼在意：一句白話，例如「這條安全主張現在沒有一份真的跑過的故障證據，等於沒驗」。
- 怎麼修：指令獨立一行；最後一行指路 `lumos security evidence` 看全表。JSON 鍵 `security_evidence` 帶完整逐條判定。

### 原因代碼

一律寫成 `<判定>:<代碼>`（護欄層與整道的代碼單獨寫，例外無效寫 `exception:<代碼>`），代碼是小寫英文加底線，同一個代碼只屬於一種判定；文字、JSON、治理帳都用同一串。實作時這張表放進程式當單一來源，測試逐一對照。

| 判定 | 代碼 |
|---|---|
| invalid（沒驗到） | `zero_cases`、`target_missing`、`target_skipped`、`targets_empty`、`suite_error`、`count_mismatch`、`missing_legit_control`、`missing_precondition`、`nontarget_failure`、`nonassertion_failure`、`receipt_hash_mismatch`、`receipt_not_executed`、`report_hash_mismatch`、`binding_incomplete`、`kind_format_mismatch`、`tool_kind_mismatch`、`evidence_kind_mismatch`、`tool_unregistered`、`tool_version_mismatch`、`target_not_authorized`、`unsupported_format`、`coverage_unproven`、`sarif_no_run`、`sarif_results_null`、`sarif_invocation_failed`、`sarif_error_notification`、`sarif_version_mismatch`、`sarif_driver_missing`、`k6_script_mismatch`、`k6_requests_below_floor`、`k6_metric_missing`、`k6_threshold_form`、`k6_aborted`、`kill_unattributed`、`kill_timed_out_weak`、`kill_drifted`、`kill_abort`、`kill_error`、`kill_weak_only`、`kill_recipe_unbound`、`evidence_fence_invalid`、`evidence_too_large`、`observed_in_future`、`review_not_independent`、`review_expiry_too_long` |
| failed（有缺陷） | `assertion_failed`、`finding_unresolved`、`survived`、`threshold_exceeded` |
| stale（版本對不上） | `binding_changed`、`binding_missing`、`revision_changed`、`tool_version_changed`、`vulndb_stale`、`review_expired`、`verification_node_stale` |
| missing（沒有證據） | `no_evidence`、`review_record_missing`、`human_review_missing`、`control_removed_unapproved`、`backing_missing` |
| uncalibrated（沒校準） | `calibration_missing`、`calibration_version_mismatch`、`calibration_rule_missing` |
| 護欄層（整體 unsound，例外蓋不掉） | `insufficient_required_evidence`、`threat_categories_missing`、`source_decision_invalid`、`question_open` |
| 整道判不清（不屬於單一護欄） | `read_incomplete`、`registration_error`、`unexpected_empty`、`freeze_base_unavailable`、`shallow_clone`、`commit_unavailable`、`approvers_change_unsigned`、`toolchain_incomplete`、`evaluation_error` |
| 例外無效（例外不算數，底下種類照原判定；寫成 `exception:<代碼>`） | `exception_expired`、`exception_too_long`、`exception_fields_missing`、`exception_unsigned`、`exception_content_changed` |

### 核可物件：例外與 considerations 共用一套

母計劃 d9 的「例外只有使用者能核可、最長 30 天」在兩篇計劃有兩個入口：本篇護欄的 `exception`，與姊妹計劃格子的 `considerations`（`risk_accepted` 與 `not_applicable`）。兩者用同一個核可物件形狀、同一支檢查函式（從既有 `_secinv_check_exception` 長出來），不各寫一套：

| 鍵 | 例外 | considerations 的 risk_accepted | considerations 的 not_applicable |
|---|---|---|---|
| `decision_ref`、`reason`（v1 既有） | 必填 | 必填 | 必填 |
| `compensating`（補償措施） | 必填 | 必填 | 不填 |
| `approved_on`（核可日，UTC 日期） | 必填 | 必填 | 必填 |
| `expires_on`（v1 既有） | 必填 | 必填 | 不填（不適用不會過期，靠表改版與重審） |
| `covers_kinds`（蓋住哪些證據種類） | 必填 | 不填 | 不填 |
| `signature` | 必填 | 必填 | 必填 |

- **30 天怎麼算**：`expires_on` 減 `approved_on` 小於等於 30 天有效，31 天起無效（`exception_too_long`）；`approved_on` 晚於今天（UTC）無效；`expires_on` 當天有效、隔天起無效（`exception_expired`）。不再用核可決策的 `decided` 日起算，兩篇都用 `approved_on`，因為它在簽章內容裡、改不了。
- 每次判定都用當天 UTC 日期重算，過期隔天自動恢復擋，不需要任何人去改狀態。例外只蓋「擋不擋」，不改證據判定本身，`security evidence` 照樣顯示底下是 invalid 還是 missing。
- 用到例外的每次推送，在治理帳記一行（護欄、種類、到期日、核可決策），與表態、新增告警的記帳同一處；冪等鍵是（護欄、種類、head_sha），同一個提交重試推送不重記。治理帳是簿記檔，這一行留在工作樹、下次提交時帶上。

### 內容簽章（d7，取代 d6 的提交簽章）

**為什麼不是 PR 核准**（2026-10-19 核對現況，d1 原寫「CI 端核對該例外列是由使用者核准的 PR 帶進來的」，做不到）：
- 本 repo 的 CI（`.github/workflows/ci.yml`）在 push 到 main 與 pull_request 兩種事件觸發，但 code-loop gate 那一步只在 push 事件跑；PR 上不跑，等例外合進 main 才判，已經晚了。
- CI 的權限是 `contents: read`，讀不到 PR 的核准紀錄；`scripts/lumos` 唯一呼叫 GitHub API 的地方是 lint-watch 查工具最新版本，沒有任何讀 PR 核准的程式。
- AI 推送與開 PR 用的就是使用者本人的 GitHub 帳號，GitHub 上分不出這個核准是使用者按的還是 AI 按的；而且 GitHub 不准 PR 作者核准自己的 PR。

**為什麼也不是提交簽章（d6 改成 d7 的原因）**：d6 原本用 `git blame` 找最後改到例外那幾行的提交、再 `git verify-commit`。設計審 r1 指出提交會被重寫：推前壓成一個、rebase、合併提交、GitHub 的 squash 合併都會產生新提交，簽章不是消失就是換人；排版或 `lumos regen` 動到那幾行，blame 就指到 AI 的提交；例外跨多行時「那幾行」怎麼取沒定，只 blame 一行就能被改另一行繞過；而且簽章只綁那幾行文字，AI 不動例外、只改外層護欄的要求，舊核准照樣蓋住新內容。d7 改成簽內容：

**做法**：
- **簽什麼**：一份規範化 JSON（鍵排序、無多餘空白、UTF-8，`json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`）。例外的內容是 `{"type":"exception","control_id","control_revision","inputs_sha256","covers_kinds","decision_ref","reason","compensating","approved_on","expires_on"}`，其中 `inputs_sha256` 是那條護欄判定輸入（`required_evidence`、`threat_categories`、`assets`、`surfaces`、`evidence_refs`）規範化後的 sha256。considerations、修訂紀錄、gate 設定、人審紀錄各有自己的 `type` 與欄位，一律把「它核可的對象的內容」放進去。`lumos security payload <對象>` 印出這份 JSON，使用者自己用 `ssh-keygen -Y sign -n lumos-security -f <私鑰>` 簽。
- **簽章放哪**：放在被核可物件自己的 `signature` 欄（ssh 簽章文字整段放進 JSON 字串）。不選「同節點旁的簽章檔」：檔案要跟物件配對，節點改名或物件搬家時簽章會掉隊或指錯；放在物件裡，物件搬到哪簽章就跟到哪，驗的時候也不用找檔。
- **驗**：閘門用 merge-base 版的 `.lumos/security-approvers` 寫一份暫時的 allowed_signers，對每個物件重算規範化 JSON，跑 `ssh-keygen -Y verify -f <allowed_signers> -I <簽章人> -n lumos-security -s <簽章>`；驗不過、物件內容跟簽的不同（例如護欄 revision 或判定輸入變了）一律不算數（例外寫成 `exception:exception_unsigned` 或 `exception:exception_content_changed`）。暫時檔放系統暫存目錄、判完就刪。
- **公鑰清單**：`.lumos/security-approvers` 就是 allowed_signers 格式（每列一把：簽章人、金鑰類型、公鑰），每列上一行用註解寫持有人說明。只收 ssh 金鑰；不選 gpg，因為 gpg 分離簽章要匯入鑰匙圈、CI 還得建暫時鑰匙圈，`ssh-keygen -Y` 一支指令就能對一個檔驗。
- **清單本身的修改**：要推的提交裡的清單跟 merge-base 版不同（含整個刪掉）時，要有 merge-base 版清單裡某把金鑰對**新清單全文**的簽章，放在 `.lumos/security-approvers.sig`；沒有或驗不過整道擋 `approvers_change_unsigned`。刪檔的情況簽的是空內容。因為只對 merge-base 判，同一次推送裡「先刪清單、再用 AI 的金鑰重建」也一樣要 merge-base 版的舊金鑰簽，不會被當成第一次釘金鑰。
- **第一次釘金鑰**：merge-base 版沒有這個檔時，沒有現有金鑰可驗；新清單照收，但在它進到預設分支之前，用它簽的東西都不算數（因為驗章一律用 merge-base 版的清單）。所以第一次釘金鑰要先單獨合進預設分支，之後的例外才生效。工具每次判到核可物件時都印出現在 merge-base 版釘住的指紋，讓使用者看得到是哪把。
- **金鑰數量與遺失**：建議至少釘兩把，一把日常用、一把離線備份。一把遺失時用另一把簽新清單換掉。

**為什麼五種問題不再發生**：
- 壓提交、rebase：簽章不在提交上，在物件裡；提交怎麼重寫，物件內容沒變就照樣驗得過。
- 合併提交與 GitHub 的 squash 合併：不看任何提交是誰簽的，只看 merge-base 版清單與要推的提交裡的物件內容，合併方式不影響。
- 排版動到行、`lumos regen`、縮排調整：簽的是規範化 JSON，空白、換行、鍵的順序都不進簽章內容。
- 多行例外：整個物件一起規範化、一起簽，沒有「哪幾行」的問題，改任何一個欄位都驗不過。
- 只改外層護欄：簽章內容含護欄 revision 與判定輸入雜湊，外層一變，舊簽章就對不上（`exception_content_changed`），要使用者重簽。

**工具的天花板**：
- 「每次簽章都要實體觸碰或輸入密碼」是使用者那端的金鑰設定（例如 `ed25519-sk` 硬體金鑰要求觸碰、私鑰加密碼），工具只驗得到「由這把公鑰對應的私鑰簽的」，驗不到簽的時候有沒有觸碰或輸入密碼；私鑰若沒設這兩樣、又放在 AI 碰得到的地方，AI 就簽得出來。
- 第一次釘金鑰沒有東西可驗；若 AI 搶先用自己的金鑰建立 `.lumos/security-approvers` 並合進預設分支，工具分辨不出來，只能靠使用者看指紋。
- 全部金鑰都遺失時，工具沒辦法自救：換清單要舊金鑰簽，舊金鑰沒了就換不了，例外與修訂紀錄也都簽不出來。剩下的路只有使用者自己決定跳過本機閘（依 d9 的規矩，跳過檢查一律由使用者本人裁）或整道回退工具版本；伺服器端的強制或救援依 d9 不做。
- 不選：使用者另開第二個 GitHub 帳號只拿來核准例外 PR——要多維護一個帳號，CI 要加讀 PR 的權限與一步 API 查詢，帳號憑證若放在 AI 碰得到的地方就失效，而且 PR 上不跑 code-loop 的問題照舊。

REVISIT:[when-file:.lumos/security-approvers][by:2027-01-31] 第一個專案釘金鑰時,請使用者確認至少釘了兩把、私鑰設了實體觸碰或密碼、指紋與工具印出的一致;確認不了就把天花板那幾句寫進 security evidence 的 limitations
REVISIT:[when-status:Projects/安全主張驗收閘_計劃=done][by:2027-01-31] 內容簽章實作後,把〈內容簽章〉改成現況說明,並寫明實測擋得住與擋不住哪種繞過(AI 直接改例外、只改外層護欄、壓提交後再推、同一次推送先刪清單再重建、搶先第一次釘金鑰各試一次)
REVISIT:2027-03-31 回看有沒有任何消費專案遇過全部金鑰遺失;遇過就把當時怎麼救的寫回〈工具的天花板〉,並重新評估要不要做伺服器端救援

**舊專案升級的過渡**：已接 lumos、沒有任何資安登記的專案升級後行為不變。已經登記了護欄的專案（目前只有試行中的 order-demo 會有），升級當下就會依現有證據被判；是否給一段只提醒不擋的過渡期、多長，待使用者裁（Q4），裁了要就由使用者簽一份 `security_evidence.gate: warn`，不另做開關。不論是否有過渡期，`lumos update` 的版本變更說明都要寫出這一道新判定。

## 五、合格測試守住閘門本身

下列條款實作前逐條改綁真測試（先紅）；可機械化的不准長期停在 manual。測試全在隔離的合成 vault 與合成工具輸出上跑，不在任何真專案執行工具；簽章樣本用測試當場產生的 ssh 金鑰。

**區隔與範圍**

- [S1] 當專案沒有任何 `lumos-security-v1` 圍欄時,code-loop check 的安全證據判定應回不擋、文字輸出與退出碼跟既有判定逐字相同、不寫治理帳,只在 `--json` 輸出多一個 no_registration 鍵;只有 `flag/security-relevant` 標籤而零條目的專案應同樣不擋,只在 `--json` 多一行提醒。 [manual:合成 vault 無登記與只有標籤兩種樣本跑 check 前後比對文字輸出、退出碼與治理帳行數]
- [S2] 當同一條 Invariant 同時登記 business 與 security 關注面時,`security evidence` 應只列一筆並只對 security 判定證據,純 business 條目應不進必驗集合。 [manual:純業務、雙關注面、獨立安全要求三種樣本核對清單與擋下結果]
- [S3] 當盤點報告讀取不完整、登記有錯或必驗集合意外為空而專案有資安登記痕跡時,閘應擋下並說明判不清,不得當零條目放行;merge-base 版與現在都只有 candidate 的專案應放行並列提醒。 [manual:注入壞 JSON、重複 ID、讀取失敗、全部條目被刪四種擋下樣本與一份只有 candidate 的放行對照]
- [S4] 當 `security evidence --commit <sha>` 與 code-loop check 對同一提交判定時,兩者的逐條判定應完全相同,而且閘的輸入應等於 `security list --commit <sha> --json` 的報告內容,即使工作目錄停在別的提交。 [manual:同一合成 repo 把 checkout 停在 main、對 feature 提交分別跑兩個入口並比對 JSON]

**合格判準與為了合格而合格的反例**

- [S5] 當 JUnit 報告零案例、目標測試不在、被跳過或有 suite 層錯誤時,該證據應判 invalid 並擋下,不得判 qualified 或 failed。 [manual:四份合成 JUnit 各跑一次]
- [S6] 當 behavior 證據只有非法案例、沒有宣告或找不到合法對照案例時,應判 invalid:missing_legit_control 並擋下。 [manual:只測合法路徑、只測非法路徑、兩者都有三份樣本]
- [S7] 當故障證據的翻紅來自非目標測試、編譯錯、逾時或非斷言失敗時,應判 invalid,不得算成抓到錯。 [manual:沿用 test-quality check 的既有負例卷證並經閘門重驗]
- [S8] 當測試照抄錯誤規則而故障仍翻紅時,fault_sensitivity 應判 qualified,但缺 review 證據的護欄整體應判 unsound 並擋下。 [manual:重抄錯規則的合成案例，有無 review 證據各一]
- [S9] 當證據綁定的任一檔案 blob、護欄 revision 或工具版本跟要推的提交不同時,應判 stale 並擋下;綁定集合少了家節點 about_code 的檔、`test_sources` 列的測試原始檔、`environment_ref` 或校準夾具時,應判 invalid:binding_incomplete。 [manual:逐種改動實作、測試、鎖檔、revision、工具版本，逐種漏綁一類，同版本完整證據作正常對照]
- [S10] 當 JUnit、SARIF 或 k6 證據檔的內容跟圍欄記的 `report_sha256` 不同、或 tq_capture 的 receipt 雜湊跟原始報告對不上時,應判 invalid;輸出應註明內容一致的偽造報告與「改綁定不重跑」不在可偵測範圍。 [manual:改報告一行、改 receipt 一欄、兩者一起改三份樣本]
- [S11] 當掃描類證據只有零發現的正式報告、沒有同工具同版本對已知陽性樣本命中的校準檔、或校準檔沒命中某一條宣告規則時,應判 uncalibrated 並擋下。 [manual:有校準、無校準、校準版本不同、校準只命中別的規則四份 SARIF 樣本]
- [S12] 當 SARIF 的 results 為 null、invocation 標失敗、通知有 error、或 `coverage_path` 那份缺登記的覆蓋證明時,應判 invalid,不得把空結果當沒找到問題。 [manual:各工具官方格式的合成 SARIF 與自家 JSON 正反樣本，含 ZAP 的 SARIF 加統計兩份檔]
- [S13] 當 k6 摘要的版本或腳本全文跟清單與提交對不上、請求數低於清單登記的下限、合法流量成功數為零、宣告的安全指標沒出現或門檻不是允許的計數寫法時,應判 invalid;安全計數超標時應判 failed。 [manual:以 k6 v2.3.0 新格式摘要為底製作各一份樣本，含一份沒 add(0) 的指標缺席樣本]
- [S14] 當護欄宣告的必要種類少於其全部威脅類別最低種類的聯集時,應判 insufficient_required_evidence 並擋下;工具清單上沒有某工具類別時,應照類別表的替代欄換算最低種類,作者在護欄裡自述沒工具應不影響換算。 [manual:只宣告 behavior 的資安護欄、兩個類別的聯集、清單有無秘密掃描工具三組樣本]

**六項整合控制（母計劃〈證據交接與首案整合驗收〉）**

- [S15] 當護欄的來源決策作廢、或它 `question_refs` 列的待決問題有一題不是已決或已驗或找不到時,該護欄整體應判 unsound 並指路到那一題。 [manual:作廢 decision_ref、列了待人問題、列了不存在的題號三種樣本與全已決的正常對照]
- [S16] 當非法請求的拒絕原因是缺身分或資源不存在時,behavior 證據應因缺前置斷言案例判 invalid,不當所有權防護通過。 [manual:只有不存在訂單被拒的合成證據，另附完整對照]
- [S17] 當同一護欄同一種類有兩份證據、一份是只產生編譯錯或零案例的故障版、另一份是真正的目標翻紅時,好的那份應逐項判 qualified,而該種類整體應判 invalid 並擋下,不得用好的蓋掉壞的。 [manual:同護欄兩份故障證據一壞一好，另附只留好的那份的放行對照]
- [S18] 當需求修訂、實作或 `environment_ref` 指的環境描述檔改了之後套用舊證據時,真實推送應被擋下並判 stale,而不是只在報告列待重驗。 [manual:在合成消費 repo 改實作、改 Dockerfile 各一次後真推送到本機裸 repo,保留拒收輸出]
- [S19] 當清單完整、引用都在但仍有未驗項或過期例外時,真實推送應被擋下,而且盤點仍維持 not_assessed。 [manual:同上合成 repo 的兩種樣本與完整有效的正常對照]
- [S20] 當測試 expected 重抄錯誤規則但故障翻紅時,報告應保留抓錯證據並另列判準獨立性未成立,不得改寫成需求正確。 [manual:同 S8 樣本核對輸出文字與 JSON 的兩個欄位]

**工具清單與目標**

- [S21] 當證據的工具不在 `.lumos/security-tools.json`、版本不等於釘版本、缺核可決策或清單本身是壞 JSON 時,應判 invalid:tool_unregistered 或 tool_version_mismatch 並擋下。 [manual:清單缺項、版本差一號、決策作廢、壞 JSON 四種樣本]
- [S22] 當壓測或動態掃描證據記的目標不是回環位址也不在核可清單時,應判 invalid:target_not_authorized。 [manual:127.0.0.1、localhost、外部網址三份樣本]

**例外與簽章**

- [S23] 當例外的到期日已過、到期日減核可日為 31 天、缺理由、缺補償措施或缺簽章時,例外應無效且閘應照擋;到期日減核可日恰為 30 天的有效例外應放行。 [manual:五種壞例外與 30 天整的有效例外]
- [S24] 當有效例外蓋住某護欄某種類時,閘應放行並在治理帳記一行,同一提交重試推送應不重記,而 `security evidence` 應照樣顯示底下原本的 invalid 或 missing。 [manual:同一護欄有無例外各跑一次比對，再對同一提交重跑一次數治理帳行數]
- [S25] 當今天(UTC)是例外到期日當天時,閘應放行;到期日隔天時,不需任何人改檔,閘應自動恢復擋下。 [manual:以固定今天日期的測試接縫跑到期前一天、當天、隔天三點，另以台灣時間清晨對應的 UTC 前一日跑一次]
- [S26] 當例外沒有簽章、用不在 merge-base 版清單的金鑰簽、簽完後內容改一個字、或公鑰清單被換掉或刪掉再重建而沒有 merge-base 版金鑰對新清單的簽章時,閘應判例外無效或整道擋下;合格簽章的例外在壓提交、rebase 與合併提交之後應仍有效。 [manual:合成 repo 以測試當場產生的 ssh 金鑰製作未簽、錯金鑰、改一字、換清單未簽、刪清單再建、壓提交後仍有效六份樣本]

**閘門接線**

- [S27] 當安全證據判定與表態閘、新增告警閘同時擋下而帶 `--keep-going` 時,三道應各自出訊息,`LUMOS-BLOCKS` 應列出 security_evidence,pre-push 的原因對照表應認得它,擋下訊息應由 `_cl_say_sec_block` 印三段式。 [manual:合成 repo 同時觸發三道]
- [S28] 當本機推送前與 CI 對同一提交跑 code-loop check 時,安全證據判定應完全相同,包括例外的簽章核對結果。 [manual:同一合成提交在本機 hook 與 CI 腳本各跑一次比對 JSON，含一份合格簽章例外與一份未簽例外]
- [S29] 當要推的提交跟 merge-base 版比,有資安條目被刪、被降成 candidate 或 retired、或 concerns 拿掉 security,而 `.lumos/security-revisions.json` 沒有簽章有效的紀錄時,閘應照舊把它當必驗並擋下;有簽章有效的紀錄時應放行並列出前後版本;整篇 Systems 節點被刪時紀錄應仍讀得到。 [manual:合成 repo 逐種縮小必驗集合的四份擋下樣本、一份未簽紀錄、一份刪整篇節點加簽章紀錄的放行對照]
- [S30] 當安全判定遇到取不到 HEAD、merge-base 等於 HEAD、算不出 merge-base 或 pitfalls 失敗這些既有放行早退時,有資安登記痕跡的專案應照樣被判;起點算不出、淺層 clone 或取不到提交時應擋,淺層 clone 的訊息應給 `git fetch --unshallow`;預設分支還不存在時應以空樹當起點照判。 [manual:合成 repo 逐一製造四種早退情境，有無登記痕跡各一，另加淺層 clone 與根提交帶登記兩種]
- [S31] 當護欄的 required_evidence、threat_categories、assets 或 surfaces 跟 merge-base 版比少了值、或 evidence_refs 被換掉,而沒有簽章有效的修訂紀錄時,閘應用新舊聯集判定並在輸出列出變弱的欄位。 [manual:逐欄改弱四份樣本與一份只新增的對照]
- [S32] 當推送的是 tag 時,pre-push 與 CI 應對 tag 指的提交跑安全判定並照擋。 [manual:合成 repo 推 refs/tags/release-1，有無合格證據各一]

**證據圍欄與種類**

- [S33] 當證據項的 kind 與 format 不在允許表同一列、工具類別產生不了該種類、或 targets 該種類要的鍵是空陣列時,應判 invalid:kind_format_mismatch、tool_kind_mismatch 或 targets_empty。 [manual:secret_scan 配 junit、static_analysis 配 k6 工具、behavior 的 tests 為空陣列三份樣本]
- [S34] 當證據圍欄是壞 JSON、有未列的鍵、缺必填或型別錯時,引用它的護欄的所有證據應判 invalid:evidence_fence_invalid;沒有讀法的 format 應判 invalid:unsupported_format。 [manual:四種壞圍欄與一份自家 JSON 格式樣本]
- [S35] 當圍欄項的 kind 不等於護欄 evidence_refs 那一列的 kind、或 Verification 節點的 status 是 superseded 或 stale 時,應分別判 invalid:evidence_kind_mismatch 與 stale:verification_node_stale。 [manual:兩種樣本各一與正常對照]
- [S36] 當 dependency_scan 的 vulndb_fetched_at 距今超過門檻、或填的不是 ISO 8601 時間時,應分別判 stale:vulndb_stale 與 invalid:evidence_fence_invalid。 [manual:門檻當天、隔天、填版本號三份樣本，門檻值以 Q5 裁定為準]
- [S37] 當 guard kill 的配方改到的檔不在證據項 bindings 裡時,應判 invalid:kill_recipe_unbound;治理帳沒有 `security backing` 寫的那一筆時應判 missing:backing_missing,那一筆的 head_sha 不是祖先或中間動到非簿記檔時應判 stale。 [manual:配方沒綁、沒寫背書、背書後改程式三份樣本與 security backing 寫入後的正常對照]
- [S38] 當 `security backing` 對同一護欄、種類與 head_sha 跑兩次時,治理帳應只多一筆,閘門讀到多筆時應取 head_sha 相符的最新一筆。 [manual:連跑兩次數行數，另造兩筆不同 head_sha 的帳]

**審查紀錄（d2、d8）**

- [S39] 當審查紀錄的 reviewer 正規化後等於任一作者時,應判 invalid:review_not_independent;expires_on 已過時應判 stale:review_expired;expires_on 晚於 observed_at 加 90 天時應判 invalid:review_expiry_too_long。 [manual:大小寫與空白不同的同名、過期、到期日太遠三份樣本與正常對照]
- [S40] 當要人的判斷只有 reviewer_kind 為 ai 的紀錄蓋到、或標 human 卻沒有有效簽章時,review 種類應判 missing:human_review_missing;不要人的判斷由 ai 紀錄蓋到時應算數。 [manual:ai 紀錄蓋 independent_oracle、human 無簽章、human 有簽章、ai 紀錄蓋 category_sufficient 四份樣本]

**資源與健壯**

- [S41] 當單一證據檔超過 16 MiB 或一次判定的證據總量超過 256 MiB 時,應只把超限的那幾項判 invalid:evidence_too_large 並指出檔名,其他護欄的判定應不受影響。 [manual:一份 17 MiB 合成 SARIF 與一份小 JUnit 同庫]
- [S42] 當證據檔是巢狀過深的 JSON 或 XML、或判定時拋出未預期例外時,閘應擋下並判 evaluation_error 或 invalid,不得放行或把 traceback 印給推送流程。 [manual:深度 10 萬的 JSON、深度 1000 的 XML、注入一個會拋錯的讀法三份樣本]
- [S43] 當同一份證據檔被一千條護欄引用時,判定應只解析一次,讀 blob 應是批次讀取。 [manual:合成 vault 數解析次數與 git 子程序數]
- [S44] 當證據的 observed_at 晚於要推的提交的提交時間時,應判 invalid:observed_in_future。 [manual:晚一天與早一天兩份樣本]

**設定與相容**

- [S45] 當 `.lumos/config.json` 的 security_evidence.gate 是 warn 而有 merge-base 版金鑰的有效簽章時,閘應照算照印但不擋;沒簽或驗不過時應當成 block 並印出原因。 [manual:有簽、沒簽、簽了別的值三份樣本]
- [S46] 當庫裡同時有 schema_version 1 與 2 的圍欄時,新工具應兩種都讀,v1 塊缺 v2 欄位時應照〈一〉表的預設處理;v1 塊出現 v2 鍵時應列未列出的欄位錯誤。 [manual:v1 與 v2 混用、v1 夾帶 threat_categories 兩份樣本]
- [S47] 當 test-quality 配套缺檔而專案有資安登記痕跡時,閘應擋下並判 toolchain_incomplete。 [manual:合成部署拿掉 test_quality.py 跑 check]

## 六、跟 P1 的關係與上線順序

- **首個真實驗收案例**：P1 在 order-demo 為 OD-01（付款）、OD-02（取消）各收三格（正常綠、只拿掉該條所有權防護後 B 操作 A 訂單的反例翻紅、還原再綠），另附 A 操作自己訂單成功的合法對照。這正好對上本篇 behavior（含合法對照）與 fault_sensitivity 兩種證據；review 種類由審查紀錄補（要人的判斷要使用者簽）。OD-03、OD-04 照舊列未驗，閘門上線後它們若已登記為 active，就會被擋——這是預期行為，不為了好看把它們留在 candidate。
- **前提**：盤點計劃 Q2（OD-01、OD-02 要不要在 order-demo 明示登記、由誰核對）還待人；沒登記，閘對 order-demo 不起作用。P1 的證據目前在 order-demo 的另一個工作樹進行中，本篇不碰。
- **上線順序**：
  1. 工具鏈自己：先在測試用的合成 vault 與合成消費 repo 驗全部 S 條款（不在任何真專案跑工具）。
  2. 發雙讀版：新工具同時讀 v1 與 v2，先發給所有專案，消費專案還不准升 v2。
  3. order-demo 先釘金鑰：使用者手動建 `.lumos/security-approvers`（至少兩把）並單獨合進預設分支；在這之前閘若上線，例外、修訂紀錄與降級設定都簽不出來，誤擋只能整道回退。
  4. order-demo：P1 證據收齊、OD-01／OD-02 登記後，讀真實筆記跑 `security evidence`，再用真推送驗擋下與放行各一次（S18、S19 的真實版）。
  5. 全部接了 lumos 的專案：前面幾步都過、使用者確認後才隨 `lumos update` 發出；沒登記的專案行為不變。
- OD-04 用 k6 實跑已依 d3 核可（條件照母計劃 d8）；實跑前 k6 讀法先用合成摘要驗，第一份真實摘要照 d5 在 order-demo 產生。

REVISIT:2026-11-30 核對上線順序第 1 到 4 步的實跑證據;任一步沒完成就不隨 lumos update 發給其他專案,並把沒完成的原因寫回本節

## 世界解與採用判斷

PRIOR-ART: 最小解落在既有 code-loop check 加一道並列判定，證據沿用 bound-tests-gate、guard kill、test-quality capture/check；外部工具只讀標準輸出：JUnit（沿用 `scripts/test_quality.py` 的讀法）、SARIF（另寫嚴格解析，uri 正規化也各寫）、k6 新格式摘要（新寫一個小讀法）。核可用 OpenSSH 的 `ssh-keygen -Y sign/verify`（git 自己的 ssh 簽章也是用它）簽內容，不自建簽章格式。借用 OSCAL「要求／實作／評估分層」的原則（盤點計劃已引，只借資料與結論分離）。不另造掃描器、runner、證據帳或安全總分。

以下 2026-10-19 查閱；版本號是查閱當天的最新穩定版，消費專案採用時重核並釘自己的版本：

| 來源 | 借什麼 | 不外推什麼 |
|---|---|---|
| [k6 releases](https://github.com/grafana/k6/releases)（v2.3.0，2026-09-21）、[end-of-test summary](https://grafana.com/docs/k6/latest/results-output/end-of-test/)、[custom summary](https://grafana.com/docs/k6/latest/results-output/end-of-test/custom-summary/)、[options](https://grafana.com/docs/k6/latest/using-k6/k6-options/reference/)、[k6-summary schema 1.0.0](https://github.com/grafana/k6-summary)；源碼 v2.3.0 的 `internal/js/summary-wrapper.js`、`errext/exitcodes/codes.go` | `--new-machine-readable-summary`（v1.5.0 起）帶 `metadata.k6_version` 與 `config.script`；舊格式 export 的門檻 `true` 代表沒過；退出碼 99＝門檻失敗；官方不建議 `--summary-export`、改用 handleSummary；v2 拿掉 legacy 摘要模式；`--summary-mode=disabled` 連結果檔都不產生 | 文件說新格式會成 v2 預設，v2.3.0 源碼預設仍是關；本機 k6 v2.3.0 2026-10-19 實測（離線空腳本，暫存已刪）證實新格式有版本與腳本、沒有門檻結果；自訂計數沒加過時出不出現還沒實測（見 REVISIT） |
| [SARIF 2.1.0 OASIS 規格](https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html) | results 空陣列＝沒找到、null＝沒跑；通知 level=error 代表 run 失敗；result.kind=pass 才表示規則評估過 | rules 與 artifacts 都可以只列部分，不能拿來證明掃了什麼 |
| [testmoapp/junitxml](https://github.com/testmoapp/junitxml)、[Surefire XSD](https://maven.apache.org/surefire/maven-surefire-plugin/xsd/surefire-test-report.xsd) | failure＝斷言失敗、error＝非預期錯誤、skipped＝沒執行 | JUnit 沒有官方規格，各 reporter 的失敗型別另驗（沿用測試品質接入標準） |
| [ZAP](https://www.zaproxy.org/docs/desktop/addons/report-generation/templates/)（2.17.0）、[內部統計](https://www.zaproxy.org/docs/internal-statistics/) | SARIF 報告模板；登入成功、送出請求、主動掃描 URL 的統計可當覆蓋證明 | 報告沒有掃描 URL 總數；未登入或零路由不是安全通過 |
| [Semgrep CLI](https://docs.semgrep.dev/cli-reference)（1.181.0）、[輸出格式](https://raw.githubusercontent.com/semgrep/semgrep-interfaces/main/semgrep_output_v1.atd) | `paths.scanned` 當覆蓋證明；errors 陣列 | 測試品質掃描已鎖 1.179.0 試行，兩處版本各自釘 |
| [CodeQL SARIF](https://docs.github.com/en/code-security/codeql-cli/codeql-cli-reference/sarif-output)、[退出碼](https://docs.github.com/en/code-security/codeql-cli/using-the-advanced-functionality-of-the-codeql-cli/exit-codes)（2.27.2） | rules 至少含跑過的規則；32＝沒找到可分析的程式碼 | 查詢包另釘版本 |
| [OSV-Scanner 輸出](https://google.github.io/osv-scanner/output/)（2.7.0；本機已裝 2.5.1） | json／sarif；128＝沒找到可掃套件；`--all-packages` 列全部套件 | 查線上漏洞庫，結果會隨時間變 |
| [Trivy](https://github.com/aquasecurity/trivy)（0.76.0）、[2026-03 供應鏈事件](https://www.aquasec.com/blog/trivy-supply-chain-attack-what-you-need-to-know) | json／sarif；設定掃描的 MisconfSummary 計數 | 預設有發現也回 0；必須釘 commit 或映像 digest，不釘標籤 |
| [gitleaks](https://github.com/gitleaks/gitleaks)（8.30.1） | sarif 列全部規則、沒發現時 results 為空陣列 | 沒有 invocations 與掃描量；退出碼 1 同時代表有發現與出錯 |
| [Checkov](https://github.com/bridgecrewio/checkov)（3.3.29）、[hadolint](https://github.com/hadolint/hadolint)（2.15.1） | Checkov 的 resource_count 與 passed/failed 計數；hadolint 有 sarif | `--soft-fail`、`--no-fail` 會讓退出碼永遠成功 |
| [Go fuzzing](https://go.dev/doc/security/fuzz/)、[libFuzzer](https://llvm.org/docs/LibFuzzer.html)、[Jazzer](https://github.com/CodeIntelligenceTesting/jazzer)（0.30.0） | Jazzer 走 JUnit；Go 與 libFuzzer 的失敗輸入檔位置 | Go 與 libFuzzer 沒有結構化的執行次數，fuzz 證據只能證明「跑過這個目標、沒留下失敗輸入」 |
| OpenSSH `ssh-keygen` 的 `-Y sign`、`-Y verify` 與 allowed_signers 格式（OpenSSH 8.0 起；git 的 `gpg.format=ssh` 也用它） | 對任意內容做分離式簽章、用命名空間 `-n` 隔開用途、用 allowed_signers 檔列准用的公鑰 | 只證明「持有這把私鑰的人簽過」，不證明簽的時候有觸碰或密碼 |

RETIRE-IF: 連續 8 週所有登記了資安護欄的專案，安全證據判定的擋下全是格式或綁定問題、沒有一次抓到真的缺陷或過期證據，且使用者判定維護成本大於價值時，降回只提醒並交人裁；若既有合約鏈或某個成熟工具已能直接提供凍結必驗集合、逐條證據對帳與出口拒收，撤掉本篇的重複讀法，保留證據與判定紀錄。

## 實務隱患

已排除:金流:本篇只讀筆記與工具輸出檔，不呼叫付款或任何業務 API；order-demo 的付款是合成資料上的模擬付款，執行歸 P1。
對外送出:lumos 不執行掃描或壓測;動態掃描與壓測只准對回環或核可目標,由消費專案工具清單登記、證據記目標、腳本自己檢查三層把關(S22),實跑另需使用者核可。
已排除:不可逆:閘門只讀不寫業務資料,擋下只是推送不出去;回退撤掉這一道即恢復原行為。
守衛面:這一道會擋所有登記了資安護欄的專案的推送,誤擋會卡住開發。處理:上線順序先工具鏈、再雙讀版、再 order-demo 釘金鑰、最後全部;判定與 `security evidence` 同一支函式讓人推送前就看得到;例外流程讓使用者能限時放行,`security_evidence.gate: warn` 由使用者簽章後能整道降成只提醒;誤擋的回退見〈回退〉。
受管出口(d9 工具天花板):本機閘可被 `git push --no-verify` 跳過,CI 在主線更新之後才跑,紅燈收不回已經進主線的提交;依 d9 不要求消費專案設伺服器端的主線保護,靠「跳過檢查一律先問人」的規矩。這道閘能保證的只到「照規矩推送的提交都判過」。
併發:多個會談同時推送只是各自讀檔,閘門不寫共用檔(治理帳沿用既有的附加寫法,冪等鍵防重記)。
資源:證據檔有自己的單檔、總量、項數上限,超限只判該項 invalid(見〈二〉〈讀不可信資料的上限與失敗處理〉);沒登記的專案用一次 `git grep` 預檢就結束,不建快照。
供應鏈:被讀的工具輸出是不可信資料,JUnit 沿用拒 DTD 的讀法,JSON 用 `_secinv_json_loads` 嚴格解析;Trivy 2026-03 的事件說明工具本身也可能被換掉,清單一律釘 digest 或 sha256。

REVISIT:2027-01-31 回看治理帳與 CI 紀錄,有沒有任何登記了資安護欄的專案發生過跳過本機閘(--no-verify)把證據不合格的提交推上主線;發生過就把次數與情境帶給使用者重裁 d9
REVISIT:[when-file:.lumos/security-tools.json][by:2027-01-31] 第一個消費專案建了工具清單時,核對清單的核可決策與釘版本方式是否照本篇寫法,不符就先修清單格式再擴大

## 回退

實作分兩個提交:①`security evidence`、`security backing`、`security payload` 子命令、讀法與 `security list --commit`(唯讀,撤掉不影響任何既有指令);②code-loop check 的新判定、`--security-only`、pre-push 對照表與非分支路徑、CI 的 tag 觸發,以及 [[Projects/推送前一次列出全部擋下原因_計劃]] 那一行「四句改五句」與 `_PPC_KIND_SENTENCES` 的第五句(這一行與常數歸 ②,跟 ② 同進同退,否則 `t_prepush_cl_reason_sentences_match_plan` 會紅)。② 呼叫 ① 的判定函式,所以要撤就先撤 ② 再撤 ①,不能單撤 ①。消費專案的證據檔、工具清單、例外與修訂紀錄都留著不刪,撤回只是不再讀。誤擋時不准在執行中把判定改成通過;照〈四〉由使用者簽例外限時放行、或簽 `security_evidence.gate: warn` 整道降成只提醒,或整道回退。環境型的整道擋下各有自己的出路:淺層 clone 跑 `git fetch --unshallow`,新 repo 根提交以空樹為起點照判,其他判不清的由使用者簽降級設定。回退到不認得 v2 的舊工具之前,消費專案要先把 v2 圍欄降回 schema_version 1(拿掉 v2 鍵),否則舊工具會整塊拒收、`security list` 讀取不完整。schema v2 的欄位變更若被盤點計劃的設計審否決,先修規格,不對消費專案自動轉寫。

## 審計修正紀錄

- r1(2026-10-19,7 席:正確性、邊界、整合、資源、回滾、架構對齊各一席 sonnet,外家 finder 一席 Codex):60 條/blocking 37 條,機器從各席報告的逐條 blocking 行數出;全部有去向(major 全折),處置與機械重現在 `governance/review-reports/安全主張驗收閘/r1-intake.md`,席報告在同一個目錄。
- 結論:例外核可從提交簽章改成內容簽章(d7 取代 d6),凍結比對擴到判定輸入、修訂紀錄搬出節點,補上種類 × 格式允許表、報告雜湊、測試原始檔與環境描述檔綁定、資源上限、tag 推送與 v1/v2 雙讀;G11、G12 由使用者裁成 d8(AI 審要標明、放行不了要人的判斷)與 d9(不設伺服器端保護,寫成天花板)。
