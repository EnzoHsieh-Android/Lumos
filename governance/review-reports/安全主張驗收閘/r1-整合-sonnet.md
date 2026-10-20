severity: major

# 整合-sonnet 設計審報告(安全主張驗收閘_計劃,凍結審材 r1-snapshot)

鏡頭是整合與知識同步。我逐節讀完整份,並對照母計劃 d9 與整合控制、姊妹計劃(資安風險提問分階段)、盤點計劃和 `scripts/lumos` 現況。有 8 條 finding,其中 6 條 major。我沒有建立臨時目錄,也沒改任何檔。

## F1 用「標籤」判定登記痕跡,會讓工具鏈自己和只貼標籤的專案每次推送被擋

位置:〈四〉擋下條件第二條,以及〈不受影響〉第一條。

引句:盤點讀取不完整或登記錯誤
引句:而這個專案有任何資安登記痕跡

問題:
- spec 把 `flag/security-relevant` 標籤算成「有登記痕跡」。判定條件是「讀取不完整或登記錯誤」。
- 盤點現況是:`registration_complete` 在零條目時固定為 false,只有一個欄位名叫 `registration_complete`。這一項不必有任何 fence,只要有標籤、零條目就成立。
- 這個 repo 自己的圖譜就符合:`Projects/跨session傳訊用途調研.md` 和 `Verification/2026-08-14_跨session傳訊互動視窗實測.md` 的 tags 都有 `flag/security-relevant`,而且沒有任何 `lumos-security-v1` fence。

具體例:
- 輸入:在本 worktree 跑 `python3.14 scripts/lumos security list`。
- 實測輸出:`read_complete: true  registration_complete: false`,「沒有任何登記條目」。
- 照字面實作:閘會判「痕跡存在加登記不完整」,擋下工具鏈自己的每次推送。
- 預期:至少「只有標籤、零條目」該有明確判法。同樣的情形也適用於任何只貼了標籤的消費專案。
- 衝突:〈六〉第 3 步寫「沒登記的專案行為不變」,和這個結果矛盾。

佐證:``file: `scripts/lumos:7274` ``(`"registration_complete": bool(read_complete and not errors and rows)`)。

severity: major
blocking: 是 — 實作者必須自己決定「標籤無 fence」算擋還算提醒,選錯會擋死工具鏈本身或放過標籤項。

## F2 「綁版本」完全靠作者自報的 `bindings`,舊證據可以改個 blob 就變 qualified

位置:〈二〉綁版本與環境指紋。

引句:閘門用 git 讀那個提交裡每個綁定檔的 blob

問題:
- 閘拿來比對的 blob 清單,是證據圍欄裡作者自己填的 `bindings`。
- 除了 `tq_capture` 的 receipt 帶 sha256 快照,和 k6 摘要帶腳本全文之外,JUnit、SARIF、guard_kill 都沒有任何「這份報告對的是哪份程式碼」的內容錨。
- spec 沒有要求閘把 `tq_capture` 的 receipt 快照雜湊拿去對提交內容。receipt 用的是 sha256,和 git blob 是兩套雜湊,也沒說怎麼對。

具體例:
- 輸入:JUnit 報告是 A 版程式跑的。AI 改了實作成 B 版,把圍欄 `bindings` 的 blob 改成 B 版,不重跑測試。
- 預期:stale(母計劃 G3「缺指紋不得默認相同」)。
- 照 spec:每個綁定檔 blob 都等於提交內容,判 qualified。
- 同理:`evidence_ref` 指到的 JUnit 檔也沒說是從提交讀還是從工作目錄讀。`test_quality.py` 的 `load_receipt` 現況讀檔案系統。

佐證:
- ``file: `scripts/test_quality.py:282` ``(`read(folder/'receipt.json')` 直接讀路徑)。
- 〈二〉自己寫的「機械能保證的只到這份結果對應這些檔案的這個內容」,對 JUnit、SARIF 並不成立。

severity: major
blocking: 是 — 母計劃 G3 靠這一層,照字面做會讓換實作後的舊證據過關。

## F3 簽章例外和專案既有的壓提交、留痕與背書規則互撞,spec 沒寫操作順序

位置:〈例外核准用簽章金鑰〉、〈四〉要跟著改的地方。

引句:找出最後改到那幾行的每個提交
引句:本機推送前與 CI 跑的是同一段核對

問題有三處:
- **壓提交會洗掉簽章。**
  - 專案規則要求「推之前壓成一個」(``file: `CLAUDE.md` 〈提交與推送〉``)。壓提交或 rebase 會重建提交,使用者的簽章不存在,`git blame` 指到 AI 的無簽章提交,例外變 `exception_unsigned`。
  - 現有程式也有對應處理:``file: `scripts/lumos:56809-56813` `` 就是專門講「壓過提交或 rebase」。
- **使用者簽章提交必須放最後,但那會讓留痕和背書失效。**
  - 例外通常在被擋之後才補,所以是推送前的最後一個提交。
  - 這個提交改的是 Systems 筆記或 `.lumos/security-approvers`,不在簿記清單裡(``file: `scripts/lumos:31960-31983` `` 的 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS`)。
  - 因此它會讓 tier=high 的代碼審留痕失效,也會讓治理帳裡 guard kill 背書的「head_sha 是祖先、中間只動簿記檔」判定失效(``file: `scripts/lumos:56826` ``)。
- 結果:使用者簽完例外,其他證據立刻 stale。

spec 沒有規定「例外提交要最先做、之後 AI 不得壓或 rebase」。S26 和 S28 的樣本也沒有「簽完再壓提交」的情境。

severity: major
blocking: 是 — 照 spec 做出來的例外流程在這個專案自己的日常推送路徑上會自相矛盾,實作者得自己編順序規則。

## F4 「例外列的那幾行」怎麼對到檔案行號沒定義,取錯行數會被繞過

位置:〈例外核准用簽章金鑰〉做法第 2 條。

引句:對每條有效期內的例外列

問題:
- 例外是 JSON 物件,可能跨多行。標準庫 `json.loads` 不給行號。spec 沒說怎麼從解析出的物件找回它佔哪幾行。
- 這決定安全性:若實作者只 blame `"exception"` 鍵那一行,AI 可以在另一行把 `expires_on` 延長或把「蓋住的種類」加一個,而 blame 那一行仍是使用者的簽章。

具體例:
- 輸入:例外寫成多行,`"expires_on"` 單獨一行。使用者簽章提交寫了 `expires_on` 是 10-30。AI 後來把那一行改成 11-30(超過 30 天)。
- 預期:例外無效。
- 照 spec 可能得到:取決於實作者怎麼取行,spec 沒鎖。S26 的四種樣本也都沒測「例外多行、只改其中一行」。

severity: major
blocking: 是 — 防 AI 自放例外的核心機制,「那幾行」的判法會決定能不能被繞,必須在 spec 裡定。

## F5 schema v2 欄位清單不完整,v1 圍欄在新程式的處境也沒寫

位置:〈一〉契約變更點、〈二〉schema v2。

引句:只多認 v2 的新欄位
引句:不對消費專案自動轉寫

問題有三處:
- **缺 `threat_categories`。**
  - 本篇〈一〉和〈二〉要求逐護欄比對威脅類別的最低證據種類,輸出也有「威脅類別」欄,但本篇列出的 v2 新增欄位裡沒有「護欄屬於哪些威脅類別」。
  - 這個欄位只在姊妹計劃定義:``file: `Projects/資安風險提問分階段_計劃.md:180` `` 的「controls 加這個欄位,schema v2」。
  - 本篇的 v2 欄位清單也沒提 `considerations`、`cells`、`inventory.applicability_pending_cells`。兩篇併審,v2 契約沒有單一完整清單,實作者拼不出來。
- **「insufficient_required_evidence」有兩個擁有者。**
  - 姊妹計劃 S5 說「盤點應列 insufficient_required_evidence」(``file: `Projects/資安風險提問分階段_計劃.md:216` ``)。
  - 本篇說盤點契約「一字不動」,檢查在閘門做。
  - 兩篇都有條款綁同一個代碼卻放在不同指令。
- **v1 與 v2 的相容性沒寫。**
  - 現況程式見到不認得的 schema_version 就報錯,且拒絕未列欄位:``file: `scripts/lumos:6991` `` 的 `unknown_schema_version`。
  - 本篇的 v2 例外欄位是「必填」。order-demo 現有的 v1 圍欄,新程式是接受、拒絕、還是當缺欄位?
  - 反過來,消費專案圍欄升 v2、但 lumos 還是舊版時,`security list` 會整個報錯 rc2。
  - spec 只說「不自動轉寫」,沒說新程式讀 v1 的行為。

severity: major
blocking: 是 — 這是母計劃要求的「舊資料與舊帳相容」,不定的話 order-demo(唯一已登記專案)升級當下行為不明。

## F6 圍欄證據項和 Verification 節點、`evidence_refs` 的配對規則沒定,節點被作廢仍可 qualified

位置:〈二〉「其他種類與全部 behavior」。

引句:指路從散文改成機器讀得懂的一塊

問題有兩處:
- 盤點現況是每個 `evidence_ref` 讀 Verification 節點的 `status`、`valid_under`、`revalidate_when`(superseded、stale 映成 stale)。本篇的圍欄項自帶 `control_id`、`kind`,spec 沒說:
  - 圍欄項的 `kind` 和 `evidence_refs` 的 `kind` 不一致時以誰為準;
  - 護欄 A 引用的節點裡有 `control_id` 是 B 的項怎麼辦;
  - 有項但沒被任何 `evidence_refs` 引用怎麼辦。
- 閘門完全不看 Verification 節點本身的 `status`。節點已標 superseded 或 stale,圍欄仍寫 qualified,閘判 sound,但同一時刻 `security list` 的 evidence_check 是 stale。「指令看到的」與「閘判的」在盤點層分裂。

具體例:Verification 節點被標 `status: superseded`,圍欄內容未動。預期:至少不比盤點更鬆。照 spec:sound。

severity: major
blocking: 是 — 作廢的證據仍能放行,與 G3、G4 方向相反。

## F7 guard kill 的「配方對護欄」只靠作者宣告,寫背書的新子命令沒有名字也沒有條款

位置:〈二〉fault_sensitivity ①、guard kill 帳那一列、〈五〉。

引句:背書只認圍欄列名的配方

問題有兩處:
- **配方沒有綁到護欄的程式。**
  - kill-log 的列沒有任何「這個配方改的是哪條護欄的哪支檔」的紀錄。``file: `scripts/lumos:57603` `` 的 `_backing_judge_groups` 只比題號。
  - 現行判法只看有沒有非弱 killed、沒有 survived。
  - 新規則等於作者在圍欄任寫一個已經 killed 的配方 id,就能讓不相干的 fault_sensitivity 變 qualified。
  - 沒有「配方 mutate 的檔必須在 `bindings` 內」之類的機械連結。
- **缺條款。**
  - 「本機寫入時算資安背書」那個新子命令沒給名字,也沒列進〈要跟著改的地方〉。
  - 〈五〉的 S1 到 S30 沒有任何一條針對治理帳背書的寫入、讀取、失效(head_sha 不是祖先、只動簿記檔)。S7、S17 只提到 test-quality 路。
  - guard kill 這條路是 CI 唯一能讀的 fault_sensitivity 路,卻沒有驗收條款。

severity: major
blocking: 是 — 缺口一讓 fault_sensitivity 可被不相干配方冒充;缺口二讓這條路徑上線時沒有測試守住。

## F8 母計劃 d9 的「例外」在姊妹計劃有第二個入口,核准機制沒接 d6

位置:〈四〉例外核可與記帳。

問題:
- 姊妹計劃的 `considerations` 有 `outcome: risk_accepted`,同樣走「只有使用者核可、最長 30 天」(``file: `Projects/資安風險提問分階段_計劃.md:182` ``),但該計劃沒寫核准機制。
- 本篇的 d6 簽章只管護欄條目的 `exception` 與 `revisions`,沒提 `considerations` 的 `risk_accepted`、`not_applicable`。AI 能自己寫一筆 `not_applicable` 把格子抽出必驗,而閘門不讀 `considerations`。
- 這屬於格子層(提問階段)而不是必驗集合,影響的是母計劃 d9「AI 不能自行核可」的涵蓋面。實作者需要被告知「`considerations` 的核准是否同樣要簽」。

severity: minor
blocking: 否 — 屬於兩篇計劃的交界缺口,不影響本篇閘門機制本身能不能實作,但要一句話交代歸屬。

## 其他已讀小節

- 〈承接對照〉、〈三〉工具接入、〈六〉上線順序、〈世界解〉、〈回退〉:已讀,無 finding。
- 原因代碼表:已對照散文裡出現的代碼,未見缺漏(refcheck 已掃的類別不報)。
- 母計劃 d9 的四項與 G1 到 G5:本篇逐條都有落點。唯一例外是上面 F2 對 G3、F8 對 d9 ③。

## 風險類逐類

- **守衛面**:F1(誤擋)、F2 和 F7(誤放)、F4 和 F6(可繞過)。
- **舊資料與舊帳相容**:F5。
- **已在途分支要不要重新表態**:Q4(過渡期)仍待人。spec 的預設是升級當下就擋,和母計劃 d9「預設擋」一致,無新 finding。
- **跟其他會談或計劃的交界**:F3(專案既有壓提交規則)、F5、F8。
- **CI**:fetch-depth 為 0,歷史足夠 blame 與驗章,無問題(``file: `.github/workflows/ci.yml:30` ``)。

最嚴重 severity: major;blocking 共 7 條(F1 到 F7)。
