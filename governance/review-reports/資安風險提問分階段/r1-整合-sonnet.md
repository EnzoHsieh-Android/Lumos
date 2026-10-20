severity: major

整合-sonnet 席,審 `資安風險提問分階段_計劃`(凍結 b47535c5)。已對照 `scripts/lumos`(`_secinv_*`、`_REQUIREMENT_FACETS`、`_pitfalls_stage`)、`Systems/情境出題`、`Systems/pitfalls-code-loop`、姊妹計劃、母計劃與盤點計劃。〈現況〉的 222/358 與 188/298 重跑一致,25 項(15 一般加 10 前端)也核對無誤。

## F1 〈四〉〈S10〉每格「建立時的表版號」沒有地方存
- 位置:〈二〉表版號段、〈四〉開頭「一格的狀態只由盤點資料算出」、S10。
- 引句:「盤點算出的每一格帶著建立時的表版號。」
- 問題:格子每次由 inventory 現算,護欄與 considerations 的欄位清單裡都沒有表版號欄,「建立時」的資訊沒有載體。
- 具體例:表 v1→v2 新增 `audit2` 類別。照 spec 實作,所有格子都用現行表(v2)算,舊格子也被標 v2;S10 要的「舊格子帶 v1、新格子 open 帶 v2」做不出來。
- 另一缺口:類別被改名或刪除時,指著舊 id 的 `threat_categories` 或 considerations 怎麼處理(報錯、忽略,還是保留),spec 沒寫。
- 佐證:``file: `scripts/lumos:7207-7236` ``,`_secinv_surface` 與 `_secinv_coverage` 是純現算,沒有持久欄位。
severity: major
- blocking: 是(S10 照字面寫不出紅綠測試,實作者得自己決定版本存哪)。

## F2 〈四〉護欄覆蓋格子的三條件漏了生命週期與關注面
- 位置:〈四〉第一列「controls 條目同時滿足三件事」。
- 引句:「controls 條目同時滿足三件事:`surfaces` 含該入口、`assets` 含該資產」
- 問題:只要求入口、資產、`threat_categories`,沒要求 `lifecycle=active`、`concerns` 含 security、非 retired。
- 具體例:AI 登記一條 candidate 護欄,`threat_categories` 填滿,格子狀態就成 `control:<id>`。現行 `_secinv_surface` 把 candidate 與 active 分開(`candidate_only`),母計劃與姊妹計劃 Q3 也都不擋 candidate,所以這是不被任何東西檢查的「補洞」。純 business 的 Invariant 若填了這欄也一樣。
- 佐證:``file: `scripts/lumos:7207-7213` `` 用 `"security" in r["concerns"]` 過濾、`state` 分 mapped、candidate_only、unmapped。
severity: major
- blocking: 是(放寬了守衛面,與 spec 自己的「想過沒下文必須看得見」目標相反)。

## F3 `@repo` 保留入口與資產會被現行引用檢查擋成錯誤
- 位置:〈一〉`@repo` 條、〈四〉最後一條「護欄的 `surfaces` 與 `assets` 寫 `@repo`」。
- 引句:「它不寫在 surfaces 裡、作者不能自己宣告同名入口」
- 問題:`_secinv_check_links` 要求控制項的 `assets`、`surfaces` 都在 inventory 已宣告的 id 內,否則 `reference_error`。spec 規定 `@repo` 不得出現在 inventory,卻要護欄引用它,沒寫檢查要放行保留 id。
- 具體例:secrets-crypto 護欄寫 `surfaces:["@repo"]`、`assets:["@repo"]`,照 spec 實作後 `security list` 退出 2,三類永遠登記不上。
- 佐證:``file: `scripts/lumos:7154-7168` ``,`known = {x["id"] for x in inv[k]}`。
severity: major
- blocking: 是。

## F4 v1 到 v2 的舊資料相容完全沒寫
- 位置:〈一〉inventory schema v2、〈四〉controls 加 `threat_categories`、回退節。
- 引句:「照盤點規矩升 `schema_version`,不用未知字串冒充。」
- 問題:現行讀取器 `schema_version` 只收 1,頂層與 inventory 內每個物件都是 exact keys,多一個欄位就整塊報錯。圍欄名 `lumos-security-v1` 與 `_SECINV_MARK` 是硬編字面,v2 圍欄叫什麼、兩版能不能並存、`security list` 讀到 v1 區塊怎麼辦,都沒寫。
- 具體例:order-demo 已有 v1 登記。升級後它的 surfaces 沒有 `kind`、`actor_ids`、`trust_boundary`,controls 沒有 `threat_categories`。spec 沒說這是整塊報錯、沒有 cells,還是自動轉寫。
- 回退節只說「不對消費專案自動轉寫」,與「v2 為必填」互相卡住。
- 佐證:``file: `scripts/lumos:6989-6992` `` 與 ``file: `scripts/lumos:7068-7075` ``。
severity: major
- blocking: 是(「舊資料與舊帳相容」是必答風險類,實作者會做出讓唯一在用的專案讀不了的版本)。

## F5 「最低證據種類」下限與「沒有工具時」欄互相矛盾
- 位置:〈二〉威脅類別表兩欄、其下第一條「下限」、config-deploy 例外說明。
- 引句:「`required_evidence` 不能比它所屬類別的這一欄少(姊妹計劃 S14 擋)。」
- 問題:只有 config-deploy 寫了替換規則(config_scan 改 deployment)。其他類的「沒有工具時」(例:input-injection 寫「可執行反例」、secrets-crypto 寫「人工審」)沒說能不能替換最低種類,S14 一律擋。
- config-deploy 那條替換的判準「沒有設定與容器掃描工具」,機械上無從判斷。`security list` 只讀筆記庫,讀不到 `.lumos/security-tools.json`,作者宣告沒工具就自動降級。
- 具體例:order-demo 依姊妹計劃 d4 只核可了 k6、JUnit、guard kill。它登記 input-injection 護欄,最低要 static_analysis,沒核可工具就永遠 `insufficient_required_evidence`,在姊妹計劃 d9 下被擋推送。唯一出路是 risk_accepted 最長 30 天,這與 d3 要拿 order-demo 驗證完整提問流程衝突。
- 佐證:姊妹計劃〈三〉工具類別表與 d4;``file: `scripts/lumos:6862` `` 的證據種類值域。
severity: major
- blocking: 是(實作者要麼讓 S14 擋死沒工具的專案,要麼把降級做成無守衛的自述)。

## F6 risk_accepted 的簽章核准沒有落點,姊妹計劃沒接 considerations
- 位置:〈四〉「`risk_accepted` 的『只有使用者能核可』……不另做一套」、〈一〉與 d2、姊妹計劃〈例外核准用簽章金鑰〉。
- 引句:「寫進這一列的提交要由使用者釘住的簽章金鑰簽」
- 問題:姊妹計劃的驗章流程是對護欄的 `exception` 列與 `revisions` 跑 `git blame`、`verify-commit`,位置在 code-loop check。
  - `considerations` 在整份姊妹計劃(grep 為 0)與它的 S 條款裡都沒出現,也不在它的驗章範圍。
  - `security list` 讀的是記憶體快照,不碰 git,不驗章。
  - 姊妹計劃只說會審 schema v2,但它的〈二〉v2 欄位清單只有 `question_refs`、`revisions`、`exception` 擴充,沒有 actors、kind、`considerations`、`threat_categories`、cells。兩邊互相指對方,沒有人持有這份契約。
- 具體例:AI 直接寫一列 `outcome: risk_accepted`、核可決策指向任一條有效 decision、到期日 30 天內。格子顯示 `risk_accepted`,沒有任何機制檢查簽章。
- 佐證:姊妹計劃 grep `considerations` 為 0。
severity: major
- blocking: 是(d6「AI 不能自己放自己」在格子層失效,且 d2 的「併審」審不到本篇的 schema 變更)。

## F7 S13 spec-gate 提醒的「這些 Systems 的 open 格子數」算不出來
- 位置:〈三〉最後兩條、S13。
- 引句:「計劃 `lands_in` 或 `related` 連到的 Systems 有資安登記時,印出那些護欄與 open 格子數」
- 問題:格子是 inventory(全庫最多一份)的 入口×資產×類別,不屬於任何 Systems。open 格子定義上就是沒有護欄,所以沒有「家」可連。
  - 若只算連到 Systems 的護欄所涵蓋的入口,最危險的完全無護欄入口被排除。
  - 若算全庫,就與計劃無關,每份計劃都印同一個數。
- 讀取路徑也沒定:`security list` 用有界 fd 讀取器(2MiB、64MiB、10000 檔上限)建快照,spec-gate 用普通 Env。要呼叫 `_secinv_build` 就得多一次整庫讀。`security list` 退出 2 時 spec-gate 怎麼辦(不擋、印錯、略過)也沒寫。
- 家的缺口:spec-gate 的家是 `Systems/規格閘`,不在 `lands_in`。
- 佐證:``file: `scripts/lumos:7250-7283` `` 的 `_secinv_build` 吃 `snap`;``file: `scripts/lumos:9391-9560` `` 是 spec-gate 區。
severity: major
- blocking: 是(S13 後半照字面不可測,且新程式會落在沒有登記的家)。

## F8 「由格子長出問題」沒有產生題目的機制,模板的 {角色} 無定義
- 位置:〈接手先讀〉、〈二〉第一段、〈三〉「問題怎麼進待決問題」、S1–S14。
- 引句:「每格產生一個候選問題,問題句由表的模板加上入口、資產、角色名稱組成。」
- 問題:沒有任何子命令、輸出欄位或條款會把格子變成候選題。〈三〉只說「照既有 `question-add` 寫」,等於人工看 `security list` 手抄。
  - `pitfalls --stage` 不讀筆記庫,所以需求與架構階段只能靠 7 個靜態面,格子只在驗證、交付階段被一行指路。
  - 這與母計劃〈提問依決策時機安排〉「權限設計早就定了」的時機訴求並不相同。
  - 模板的 `{角色}`:格子的軸是 入口×資產×類別,角色不是軸,一個入口可有多個 `actor_ids`。出一題列全部角色,還是每個角色一題,沒定義。S1 只驗格子清單,沒有任何條款驗題句。
- 佐證:``file: `scripts/lumos:49095-49100` `` 只讀計劃那一個檔。
severity: major
- blocking: 是(核心賣點「問題從清單長出來」在條款裡不存在,實作者只會做出 cells 清單)。

## F9 新風險面直接進全體預設,P2 的 A 臂被污染
- 位置:〈五〉推廣線、母計劃 P2「A 既有流程」。
- 引句:「新增的風險面先以提醒上線(本來就只是提醒)。」
- 問題:7 個新項與 `triggers` 引擎寫進 `scripts/lumos` 就是所有人的預設。A 臂跑的 lumos 若含新項,就不是「既有流程」,漏放比較失去基準,Q3 與 RETIRE-IF 都靠這個比較。
- spec 沒要求 A 臂釘舊版 lumos 或加關閉開關,母計劃 P2 的處置說明也沒被列為要同步修改的檔。
severity: major
- blocking: 是(量測設計與上線方式不相容,三個月後接手的人會發現量不出來)。

## F10 詞界寫法與所稱「照前端字樣那條」不一致,英文複數漏觸發
- 位置:〈三〉「誤觸發怎麼壓」第一條。
- 引句:「前後不接英數字(`(?<![a-z0-9])詞(?![a-z0-9])`)」
- 問題:`_REQ_FE_WHEN` 的框架名實際是 `(?![a-z])`(讓 Vue3 能中),只有 `e2e` 與副檔名是 `(?![a-z0-9])`。spec 的寫法會讓 secrets、tokens、cookies、sessions 這些常見複數不命中。
- 具體例:計劃寫「JWT tokens 與 API secrets」,arch-sec-secrets 要兩個不同詞,實際 0 命中。
- 佐證:``file: `scripts/lumos:31056-31058` ``。
severity: minor
- blocking: 否(可在 S6、S7 補樣本時發現,不致做出壞系統)。

## F11 設計說要跟著改的地方有漏
- 位置:〈二〉末兩條、`lands_in`、回退節。
- 漏項:
  - `Systems/情境出題` 的需求風險面表與「25 項」敘述要加 7 列。現在只寫了威脅表要搬進去。
  - `Systems/pitfalls-code-loop` 的 `--stage` 段要加 `triggers`、新增項、指路行。
  - 盤點計劃契約段。
  - 母計劃 P2 處置說明。
- 另有三處規格不足:漂移測試只對威脅表,新 7 項的內容源與常數無同步守衛;S12 沒涵蓋標題上的版號;`triggers` 的正式 JSON 形狀沒進任何 Systems 筆記的 `KEY:` 或合約。
severity: minor
- blocking: 否。

## F12 多類別護欄與空資產入口兩個邊界未定
- 位置:〈二〉下限條、〈四〉。
- 邊界一:一條護欄的 `threat_categories` 有兩類以上時,`required_evidence` 要涵蓋聯集還是各類分別滿足,沒寫。
- 邊界二:`surfaces[].asset_ids` 現行允許空陣列(`_secinv_str_list` 對空 list 通過)。空陣列入口產生 0 格,等於整個入口從不被問。spec 沒要求 `asset_ids` 非空或把它列為缺口。
- 佐證:``file: `scripts/lumos:6749-6756` ``。
severity: minor
- blocking: 否(實作時一個決定即可,先在 spec 補一句)。

## 風險類逐類
- 守衛面:F2、F5、F6、F9。
- 舊資料與舊帳:F4。
- 已在途分支要不要重新表態:無新增。新項只是提醒,不碰推送閘。
- 跟其他計劃的交界:F6、F7、F11。

## 已讀無 finding
- 〈現況〉數字,已重算一致。
- 〈五〉量測設計(40 篇標註、REVISIT 日期)。
- 〈世界解與採用判斷〉。
- 〈實務隱患〉的金流、對外送出、不可逆三項排除理由。

最嚴重 severity:major,blocking 共 9 條(F1–F9)。
