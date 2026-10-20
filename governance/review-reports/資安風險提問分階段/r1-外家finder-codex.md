severity: major

## F1 — 角色未進格子主鍵，單一護欄會錯誤覆蓋所有角色

severity: major  
blocking: 是 — 不改會讓只驗一種角色的護欄關閉整個入口的授權缺口。

spec 段落：〈一、從要保護什麼出發〉、〈二、每格套固定威脅類別〉、〈四、每個答案只有三條去向〉。

引句:「格子＝入口 × 該入口對應的資產 × 適用的威脅類別。」

問題：surface 雖有 `actor_ids`，但格子主鍵與護欄覆蓋判定都沒有 actor；controls 也未定義覆蓋哪些 actor。模板填入角色名稱不能補回機械判定漏掉的維度。

具體例：`orders-api` 的角色為 owner、stranger、admin；護欄只驗 stranger 不得改 owner 訂單 → 預期 admin 仍有獨立待問格 → 照 spec，control 只憑 surface、asset、threat category 即把唯一 authz-object 格標成 `control:<id>`，admin 缺口消失。

佐證：現行覆蓋演算法本來只按 surface 映射；新 spec 沒為 actor 增加對應鍵。  
file: `scripts/lumos:7207` `_secinv_surface` 只以 `sid in r["surfaces"]` 建立映射。  
file: `governance/review-reports/資安風險提問分階段/r1-snapshot.md:180` 新覆蓋判定仍只列 surface、asset、threat category。

## F2 — considerations 的核可沒有可執行驗章契約，AI 可自行把 open 改成不適用或接受風險

severity: major  
blocking: 是 — 不改會讓 AI 以自己提交的 considerations 清掉 open 缺口。

spec 段落：〈四、每個答案只有三條去向〉、S4。

引句:「risk_accepted 的只有使用者能核可跟驗收閘的例外用同一套核准來源，不另做一套。」

問題：文字宣稱共用簽章來源，但既有驗章設計只枚舉護欄 exception 與 revisions，沒有 considerations；本篇 S4 也未驗未簽、錯金鑰或 approver 清單遭替換。`not_applicable` 更只寫「核可決策」，沒定義核可提交須驗章。

具體例：AI 在未簽提交加入有效 decision_ref、理由與 30 天內到期日的 `risk_accepted` → 預期仍為 open 並報 unsigned → 照現有驗收條款，日期、決策與欄位都合格後成為 `risk_accepted`。`not_applicable` 甚至可用普通提交直接令 open 消失。

佐證：  
file: `docs/lumos-toolchain-knowledge/Projects/安全主張驗收閘_計劃.md:374` 驗章對象明列為例外列與 revisions，未含 considerations。  
file: `docs/lumos-toolchain-knowledge/Projects/安全主張驗收閘_計劃.md:433` S26 也只測例外列。  
file: `docs/lumos-toolchain-knowledge/Projects/消費專案產品安全Brief與證據驗收_計劃.md:105` 母計劃 d9 明定 AI 不能自行核可例外。

## F3 — 無效 consideration 與互斥規則互相衝突，且會蓋掉有效 control

severity: major  
blocking: 是 — 不改會使同一輸入依實作者選擇得到 rc2、open 或 control 三種不同結果。

spec 段落：〈四、每個答案只有三條去向〉、S3、S4。

引句:「同一格只要同時有覆蓋它的護欄與 considerations 裡 outcome 是 not_applicable 或 risk_accepted 的一列，就列錯誤、退出 2，不任選一個。」

問題：互斥規則說任何 consideration 列與 control 並存都退出 2；期限規則又說過期或不合格的 risk_accepted「這一列不算數、格子是 open」。兩者未定義先後，而且有有效 control 時判 open 也是錯的。

具體例：格子已有有效 control，另殘留昨天到期的 risk_accepted → 預期 control 保持覆蓋、過期列另報無效 → 照 S3 得 rc2；照期限段落則 consideration 不算數但格子變 open；兩者都不等於預期。

佐證：  
file: `governance/review-reports/資安風險提問分階段/r1-snapshot.md:187` 定義無條件互斥。  
file: `governance/review-reports/資安風險提問分階段/r1-snapshot.md:189` 又要求不合格列使格子回到 open。  
file: `docs/lumos-toolchain-knowledge/Projects/安全主張驗收閘_計劃.md:143` 既有上位契約要求不適用與例外不消除原事實狀態。

## F4 — 每格建立時版號無持久化來源，S10 無法照字面實作

severity: major  
blocking: 是 — 不改無法區分舊格與新版新增格，版本遷移結果不可判定。

spec 段落：〈二、每格套固定威脅類別〉、〈三、格子怎麼看〉、S10。

引句:「當威脅類別表改版時,舊格子的 considerations 與狀態應保留,新類別的格子應列為 open,每格應帶建立時的表版號。」

問題：cells 是每次從 inventory 與當前威脅表衍生的輸出，不是持久資料；controls、considerations 與威脅類別表均沒有 `created_in_version`／`introduced_in_version`。工具只能知道目前版號，推不出某格何時建立。

具體例：v1 已有 `api × orders × authz-object` 且為 not_applicable；v2 新增類別 X → 預期舊格保留 v1、X 標 v2/open → 照 schema，重算時兩格都只能取得目前 v2，或必須憑空猜歷史。

佐證：  
file: `governance/review-reports/資安風險提問分階段/r1-snapshot.md:169` cells 定義為 coverage 衍生區。  
file: `governance/review-reports/資安風險提問分階段/r1-snapshot.md:180` controls 映射欄位沒有格子版號。  
file: `governance/review-reports/資安風險提問分階段/r1-snapshot.md:181` considerations 欄位也沒有版號。

## F5 — schema v1 到 v2 沒有讀取與遷移契約，既有專案升級結果未定

severity: major  
blocking: 是 — 不改會讓既有登記在升級後被拒讀，或被不一致地默認補值。

spec 段落：〈一、從要保護什麼出發〉、〈回退〉。

引句:「inventory 要多三樣才長得出問題（schema v2，契約變更；依 d2 併進姊妹計劃那次設計審，審過後同步更新盤點計劃的契約段）。」

問題：未定義 v2 是否沿用 `lumos-security-v1` fence、解析器是否同時接受 schema 1/2、v1 缺 actors/kind 時輸出 unknown、提醒或 rc2，也沒有在途分支如何重新表態。回退又明說不自動轉寫，不能假設資料已遷移。

具體例：消費專案仍提交合法 `schema_version: 1` 區塊後升級 lumos → 預期有明確相容或遷移狀態 → 照 spec，實作者可刪除 v1 支援而使整份登記變 `unknown_schema_version`，也可偷偷替缺欄位補預設值，兩者安全語意不同。

佐證：  
file: `scripts/lumos:6385` 現行 fence 固定為 `lumos-security-v1`。  
file: `scripts/lumos:6989` 現行解析器只接受整數 1。  
file: `scripts/test_lumos.py:99772` 現行測試釘住 schema 2 為 `unknown_schema_version`。  
file: `governance/review-reports/資安風險提問分階段/r1-snapshot.md:251` 回退明定不自動轉寫消費專案資料。

## F6 — 候選問題沒有輸出或物化路徑，核心功能可在所有條款通過後仍未發生

severity: major  
blocking: 是 — 不改可只做 cells 與七個泛化提醒，卻完全沒有逐格問題進入 pending_questions。

spec 段落：〈二、每格套固定威脅類別〉、〈三、問題怎麼進待決問題〉、驗收條款。

引句:「每格產生一個候選問題，問題句由表的模板加上入口、資產、角色名稱組成。」

問題：`security list` 的 cells 契約只要求狀態與表版號；`pitfalls --stage` 只列七個泛化風險面；`question-add` 需要呼叫者提供目標計劃及完整文字。spec 沒指定哪個輸出帶候選問題、誰何時把 open cell 物化、如何防重複，也沒有 SN 驗收「一個 open cell 真的產生問題」。

具體例：inventory 產生 `orders-api/orders/authz-object` open cell → 預期看到含角色、入口、資產的候選題並可追進計劃 → 照全部 S1–S14 實作，`security list` 可只列 cell，`pitfalls --stage` 只列 req-sec-assets／req-sec-actors，pending_questions 仍是空的。

佐證：  
file: `scripts/lumos:24398` 現有 `question-add` 是獨立寫入入口，需要外部提供題目文字。  
file: `scripts/lumos:49099` 現行 `pitfalls --stage` 只從風險面表篩選問題。  
file: `governance/review-reports/資安風險提問分階段/r1-snapshot.md:212` 至 `:225` 的 S1–S14 沒有候選題產出或物化條款。

## 逐節與風險類覆核

- 開頭欄位、接手說明、現況：已讀，無額外 finding。
- 〈一〉：F5。
- 〈二〉：F1、F4、F6。
- 〈三〉：F6。
- 〈四〉：F1、F2、F3。
- 〈五〉：已讀；Q3、Q5 保持待人，未冒充已決，無 finding。
- 驗收條款：F2、F4、F6 缺可執行反例。
- 世界解與採用判斷：已讀，無額外 finding。
- 實務隱患與回退：守衛面由 F1–F3；舊資料與在途分支由 F5；姊妹計劃銜接由 F2；單人依序操作仍可重現全部 findings。依指定威脅模型，不報多程序及非中英文系統問題。
- 凍結審材中的 d1–d3、Q1–Q5、S1–S14 及節次引用均有目標；已由 refcheck 排乾的存在性問題未重報。

最嚴重 severity: major；blocking 共 6 條。


162,287
