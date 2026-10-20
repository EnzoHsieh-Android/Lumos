severity: major

邊界-sonnet 設計審,審材是凍結的 r1-snapshot.md。已讀全文,也核對了 `scripts/lumos` 的現況:inventory 解析在 6989 行附近,`_secinv_check_links` 在 7154 行,`_pitfalls_stage` 在 49082 行。

**F1 表版號沒有地方存,S10 沒法測**
severity: major
blocking: 是(照字面做,會做出一個永遠不通過 S10 的版號欄位)
- 段落:〈二〉威脅類別表 v1 的版號說明、〈四〉、S10。
- 問題:規格要求「每格帶建立時的表版號」,但〈四〉說格子狀態「只由盤點資料算出」。格子是每次現算的,規格沒說建立時的版號存在哪。controls 和 considerations 的新欄位清單裡都沒有表版號。
- 具體例:表從 v1 升到 v2,新增一個類別。S10 預期舊格子帶 v1、新類別格子帶 v2。照規格實作,每次現算時所有格子都只會帶「當前版」v2,舊格子看不出是 v1 建立的。
- 佐證:引句:「盤點算出的每一格帶著建立時的表版號。」
- 佐證:引句:「一格的狀態只由盤點資料算出,不靠作者勾選:」
- 要改的方向:要嘛把版號寫進 considerations 和 controls 的欄位,要嘛把 S10 改成不要求「建立時」。

**F2 schema_version 現況只吃 1,v2 與舊登記塊怎麼並存沒寫**
severity: major
blocking: 是
- 段落:〈一〉「照盤點規矩升 `schema_version`」、回退節。
- 問題:現行解析寫死 `sv != 1` 就丟 `unknown_schema_version` 並整塊不採用,見 `scripts/lumos` 6989–6992 行。inventory 還用 `_secinv_exact_keys` 限定只准 `revision/decision_ref/assets/surfaces` 四個鍵,見 7068–7075 行。
- 具體例:消費專案裡已有 `schema_version: 1` 的登記塊。工具升到 v2 後,若只認 2,舊塊全進錯誤,覆蓋變成「未知」。若兩版並收,規格沒寫 v1 的 surfaces 沒有 `kind` / `actor_ids` 時怎麼算格子。是整個入口 open,還是列錯誤?
- 規格也沒說同一個庫能不能 v1、v2 混用。
- 現況限制:盤點本來就規定「全庫最多一份 inventory」,見 7089 行附近。
- 佐證:引句:「照盤點規矩升 `schema_version`,不用未知字串冒充。」

**F3 `@repo` 資產過不了現有的連結檢查,三個 repo 級類別永遠無法登記護欄**
severity: major
blocking: 是
- 段落:〈一〉保留入口 `@repo`、〈四〉「以 repo 為單位的三類:護欄的 `surfaces` 與 `assets` 寫 `@repo`」。
- 問題:規格明說 `@repo` 不寫在 inventory 的 surfaces 和 assets 裡。但 `_secinv_check_links` 對 controls 的 `assets` 和 `surfaces` 逐項比對 inventory 的 id,不在就報 `reference_error`(7160–7164 行)。規格沒寫要為 `@repo` 開例外。
- 具體例:一條 control 寫 `surfaces:["@repo"], assets:["@repo"], threat_categories:["secrets-crypto"]`,照規格字面實作會被判 `reference_error`,secrets-crypto、supply-chain、config-deploy 的格子永遠只能 open。
- 還有一處衝突:「一個 repo 根一組 @repo 格子」與「全庫最多一份 inventory」。一份 inventory 只會有一組 `@repo`,多服務同 repo 的多庫情境沒有定義。
- 佐證:引句:「它不寫在 surfaces 裡、作者不能自己宣告同名入口」

**F4 入口的 `asset_ids` 是空陣列時,0 格靜默不產生**
severity: major
blocking: 是
- 段落:〈二〉「該入口對應的資產就是那個入口自己的 `asset_ids`」。
- 問題:`_secinv_str_list` 允許空陣列(6749–6753 行)。格子是入口 × 自己的資產 × 類別,資產是空集合就一格都沒有。
- 具體例:新增一個 `http_api` 入口、`asset_ids: []`,通過驗證,coverage 也沒有 open 格。入口存在,但覆蓋顯示一切正常。這與〈四〉「想過沒下文就一直 open」的精神相反。
- 規格沒寫空 `asset_ids` 要當錯誤,還是產生「入口無資產」的 open 項。
- 佐證:引句:「該入口對應的資產」就是那個入口自己的 `asset_ids`,不是全部資產

**F5 最低證據種類與「沒有工具時」欄互相矛盾,S5 會誤判**
severity: major
blocking: 是
- 段落:〈二〉表的「最低證據種類」「沒有工具時」兩欄、S5、config-deploy 那條說明。
- 問題:多類的「沒有工具時」只留人工審或可執行反例,低於同列的最低證據種類。
- 具體例:secrets-crypto 的最低是 `secret_scan、review`,沒有工具時是「人工審」。專案沒有秘密掃描工具,登記 `required_evidence:[review]`,S5 會報 `insufficient_required_evidence`。supply-chain(`dependency_scan`)、authn-identity(`behavior`)、outbound、file-handling 同型。
- 規格只替 config-deploy 寫了 `config_scan` 換 `deployment` 的替換規則,其他類沒有。
- 即使有替換規則,「有沒有設定與容器掃描工具」是專案現況,規格沒說盤點從哪個欄位知道。S5 無法機械判定該要求哪一組下限。
- 佐證:引句:「沒有設定與容器掃描工具時 config_scan 改成 deployment」
- 佐證:引句:「`required_evidence` 不能比它所屬類別的這一欄少」

**F6 considerations 沒有驗證規則,邊界輸入無定義**
severity: minor
blocking: 否(不改,實作者要自己猜,但猜錯不會做出壞系統)
- 段落:〈四〉、S3、S4。
- 問題:只定義了「同格兩列」和「護欄與 considerations 並存」兩種錯誤。
- 以下輸入規格沒寫怎麼判:
  - considerations 指到不存在的入口、資產或類別。
  - 類別對該入口 kind 不適用(例如 `cli` 入口標 `authz-object`)。
  - 資產不在該入口自己的 `asset_ids` 裡。
  - 類別在改版後被拿掉。
  - `outcome` 是兩值以外。
- 具體例:一列 considerations 指到不存在的格子,照字面是靜默忽略,作者以為已處理,實際上沒有。

**F7 risk_accepted 的 30 天邊界與 S4 樣本沒對齊**
severity: minor
blocking: 否
- 段落:〈四〉risk_accepted 的期限、S4。
- 問題:「到期日晚於 decided 加 30 天就無效」,所以剛好第 30 天是有效的。S4 的六份樣本是「到期前、當天、隔天、超過 30 天、缺補償措施、決策作廢」,沒有「剛好 30 天」,也沒有 `到期日` 早於 `decided` 的樣本。
- 另外,核可決策缺 `decided` 欄時怎麼判也沒寫。
- 具體例:實作者把比較寫成 `>=` 而非 `>`,S4 全綠,但剛好 30 天的有效列被誤判成 open。

**F8 觸發詞表在本 repo 的假設不成立,詞界寫法與現況差一個字元**
severity: minor
blocking: 否
- 段落:〈三〉誤觸發怎麼壓、S6。
- 問題一:通用強詞和秘密詞裡的 `token`、`session` 在本 repo 的計劃裡極常見。這份計劃自己就寫了「token 與費用」「session」之類的詞。「只收少歧義的詞」對 LLM 工具鏈類計劃不成立。
- 影響:消費專案的真實計劃可能不受影響,但〈五〉量測用的 40 篇正好含本 repo。
- 問題二:規格說「照 `_REQ_FE_WHEN` 的詞界寫法」,並寫成 `(?<![a-z0-9])詞(?![a-z0-9])`。但現況的框架名那條是 `(?![a-z])`,刻意允許緊貼版本號(Vue3、React18),見 `scripts/lumos` 31057 行。`token2`、`jwt2` 這類寫法在兩種寫法下結果不同。
- 問題三:S6、S7 的樣本是「固定十篇」,沒指定是哪十篇,字面上不可重現。

**F9 「想過沒下文」不靠追問題;其餘各節**
已讀,無 finding:
- 〈三〉`triggers` 資料形狀的判法:空文字、`min_distinct` 剛好卡在 1 或 2 都有定義。
- 既有 25 項(15 一般 + 10 前端)的數量和 `_pitfalls_stage` 只收單一檔案路徑的說明,與現況相符。
- S8、S9、S11、S13 的對象和條件。
- 〈五〉、回退、世界解各節。

最嚴重 severity:major,blocking 共 5 條(F1、F2、F3、F4、F5)。
