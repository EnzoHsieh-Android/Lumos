---
type: project
status: doing
created: 2026-10-18
updated: 2026-10-18
self_audit: gpt-5.6-sol/2026-10-18
tags:
  - type/project
  - status/doing
  - scope/retrieval
related:
  - "[[Projects/消費專案產品安全Brief與證據驗收_計劃]]"
lands_in:
  - Systems/lumos-cli-read
---
# 資安護欄唯讀盤點_計劃

## 目的與授權

白話：把專案的安全護欄、證據與缺口攤在一張清單上；清單讀完不代表產品安全。

依[[Projects/消費專案產品安全Brief與證據驗收_計劃]] d5、d6，獨立設計唯讀盤點指令。Invariant仍是通用合約；安全要求可引用Invariant或獨立政策。本篇是待審設計，status doing表示設計進行中，不代表指令已存在或可放行實作。

母計劃Q3只限制故障執行，Q4限制正式交付接線；本案不執行這兩種行為，不改其狀態。實作須先過本案規格閘與必要設計審，不因唯讀而略過輸入安全、錯誤處理及證據語意檢查。

## 世界解、最小解與落點

PRIOR-ART: 借用[NIST OSCAL的要求／實作／評估分層](https://pages.nist.gov/OSCAL/learn/concepts/layer/)（2026-10-18查閱），僅借資料與結論分離的原則，不實作OSCAL相容格式、不宣稱認證。最小新增是既有CLI的唯讀匯總入口，安全讀取後以Env.from_texts重用既有筆記與合約解析，不直接呼叫load_vault或一般Env(vault)，不引入資料庫、網路服務或第三方依賴。

既有程式導航：CLI的cmd_contracts、cmd_query、cmd_enforcement、load_vault與parse_frontmatter。前兩者作合約與節點查詢參考，enforcement作「盤點不等於正確性判定」的介面參考；不能把工具鏈掛鉤生效與消費產品安全混在一張清單。實作前讀[[Systems/lumos-cli-read]]的合約，不改search既有過濾語意。

lands_in採[[Systems/lumos-cli-read]]，本案只增加讀取與展示；若實作需要拆出獨立程式檔，先建負責解析與盤點的新System家，再修改lands_in，不擴充既有合約語法來承載安全分類。

## CLI契約

候選入口：`lumos security list`；JSON模式：`lumos security list --json`。沿用全域vault選擇，未明確選定唯一vault時報錯，不在多專案間猜測。首版無篩選旗標、無自動寫入、無自動執行測試；命令說明及每份輸出均標示「唯讀盤點，不是安全驗收」。

預設列整個選定vault的全部已登記項，包括候選、失效、缺陷、不適用、接受風險與撤除歷史；活躍與撤除分區。未登記分類的既有合約列待分類提示，不自動列為安全護欄；已明確登記business-only者列在excluded_business區（含其來源與排除分類），不混入安全主清單或安全分母。business-only的撤除項也留在此區並顯示lifecycle，不重複列入retired。

退出碼0表示已完整讀取並產出盤點，即使有未驗、缺陷或覆蓋未知；2表示輸入、schema、引用或讀取不完整。兩者都不表示產品安全。JSON頂層固定帶purpose=inventory及security_verdict=not_assessed；無任何overall_pass或安全百分比分數。

## 資料位置與單一來源（候選schema v1）

先採負責功能／政策的Systems筆記正文內專用JSON圍欄 `lumos-security-v1`，不在總表或sidecar複製規則。每篇最多一塊，內容是含schema_version=1、controls陣列與可選inventory物件的JSON物件；只認頂層圍欄，不讀程式碼範例裡的巢狀示例。JSON採標準庫嚴格解析，拒絕重複鍵、NaN、未知schema版本及未列出的欄位；不擴充通用YAML parser。這是待審的新資料入口，不是已支援語法。

選正文JSON而非新增巢狀YAML的理由：避免為本功能擴充通用frontmatter解析；選分散於各System而非獨立權威總表，避免規則有兩個家。代價是新增專用圍欄讀取及嚴格驗證，需由架構席核對是否有更小的既有可用結構。若架構審否決此選擇，先改設計而非並存兩套格式。

圍欄文法：開頭必須在column 0，整行恰為三個反引號加lumos-security-v1；結尾整行恰為三個反引號。不得帶空白尾碼、縮排、blockquote或list前綴；這些變體若含專用標記列malformed_block，不登記。掃描先辨識一般反引號／波浪號圍欄，其內示例忽略；未閉合一般圍欄也列解析錯誤，避免其後登記被隱藏。CRLF按行結尾處理。

鍵的必填規則：頂層schema_version、controls必填，inventory可省略但不可null；controls下表所有列出的鍵皆必填，僅retirement_reason與replacement_id只在retired時必填、其他lifecycle禁止。source為物件：invariant恰含kind、node、exact_claim、decision_ref；requirement恰含kind、claim、decision_ref。exception非null時三個鍵皆必填，reason及decision_ref不得空。inventory與其assets、surfaces各項列出的鍵皆必填。所有字串除明示null者皆不得空白；陣列可空，但必要資訊為空時列缺項，不當成已核對。replacement_id為既有control ID或null，不得指自己。

### controls每列

| 欄位 | 型別與語意 |
|---|---|
| id、revision | 非空字串；id限ASCII字母數字及點、底線、連字號，專案內唯一且不得因改名重用；revision為需求修訂身份 |
| concerns | 非空去重字串陣列，值僅business、security、unclassified；unclassified不得與其他值並存 |
| source | kind為invariant或requirement；invariant用node與exact_claim定位既有合約，requirement用claim存唯一權威要求文字；兩者皆有decision_ref |
| lifecycle | candidate、active、retired；retired另含同層retirement_reason非空字串與replacement_id字串（無取代者為null） |
| assets、surfaces | 去重字串ID陣列，對應inventory；候選缺盤點時可空但列缺口 |
| scope、trust_boundary、enforcement | 非空文字，描述適用條件、信任邊界與防護位置；未知寫null並列缺項，不虛構位置 |
| legitimate_control、abuse_case | 文字判準，非執行命令；未知null列缺項 |
| required_evidence | 去重字串陣列，首版值為behavior、fault_sensitivity、review、deployment、dependency_scan；新增種類須升schema，不用未知字串冒充已支持 |
| evidence_refs | vault內Verification節點完整相對路徑陣列；只讀取既有紀錄，不因連結存在就認定有效 |
| reported_status | untested、partial、verified、defect、not_applicable；是作者宣告，不是盤點程式認證 |
| status_reason、owner、revalidate_when | 非空文字；未知null列缺項，說明狀態理由、權責人與重驗條件 |
| exception | null或含decision_ref、reason、expires_on的物件，expires_on為ISO日期；不覆蓋reported_status |

Invariant引用只能指到同vault的完整Systems節點（不接受模糊檔名），exact_claim以既有extract_contracts及清除測試／audit等標記後的宣稱全文完全匹配，恰一條才有效；不以子字串比對。合約行是原始規則，JSON不另存claim。獨立requirement的claim只存本欄，正文散文可說理由但不另立同義權威條款。decision_ref採完整節點加dN，引用不存在、已作廢或不唯一的決策均列錯誤。

同一來源被不同ID重複登記時列duplicate_source，不任選其中一條；未分類的候選全部顯示。僅有既有Invariant但無登記引用者列在unclassified_contracts，不直接當安全缺陷，也不宣稱已審過純業務。標籤精確為flag/security-relevant但沒有條目的節點列unregistered_nodes；散文中未登記且無標籤的規則不能靠此工具保證發現。

### 可選inventory物件

整個vault最多一份inventory權威宣告，放在負責資產與入口盤點的Systems筆記；不是額外建立一份controls總表。欄位：revision、decision_ref、assets陣列、surfaces陣列；assets每項含id與description，surfaces每項含id、asset_ids與description。description應講清入口及信任邊界。ID在各陣列內唯一；asset_ids不得懸空。缺inventory或核可依據失效時coverage=unknown，多份則列錯誤，不能任選。

controls.surfaces反查每個surface的候選與active security護欄：無active映射列unmapped，有候選但無active列candidate_only。已映射只代表登記關係，不代表防護已實作或測試通過；not_applicable及例外仍列原狀態，不能讓該入口變成「安全」。庫外未盤點入口不在工具的可證範圍。

## 讀取、證據與狀態算法

1. 以選定vault與推得的repo為界，列舉所有Markdown，包含作廢筆記；新入口不能套query預設隱藏superseded的濾網。對每篇只讀一次內容快照供本次解析，紀錄內容指紋；偵測到列舉或讀取失敗則read_complete=false，保留已讀項及錯誤。
2. 專用圍欄只允許在Systems出現；其他資料夾出現時列misplaced_block而非靜默忽略。任何專用標記未閉合、多塊、型別不符均列明位置與原因；不能退回「此篇沒有安全條目」。一般JSON示例不參與登記。
3. 原始專用JSON欄位不經eval、不執行其中命令、不開啟URL。引用只允許vault內正常檔案；拒絕絕對路徑、父目錄跳脫與符號連結，不讀其他專案、家目錄或外部檔案。不得把原始整份壞JSON或筆記全文輸出到錯誤訊息，以免暴露無關資料。
4. 輸出分開保留reported_status、evidence_check、issues。evidence_check值為missing、incomplete、stale或declared_only，絕不產生verified。逐引用保留來源status：stale及superseded映stale；pending及abandoned映incomplete；缺失／未知status、非Verification、缺valid_under或revalidate_when映incomplete；pass且前提兩欄非空才映declared_only。不存在或不可讀映missing並列引用錯誤；未知status列schema錯誤。控制項聚合優先序missing > stale > incomplete > declared_only，空evidence_refs為missing；所有逐引用問題仍保留。required_evidence為空或證據種類對應未核對時，聚合至少incomplete。即使reported_status=verified且引用pass，也不超過declared_only，說明未重跑、未做完整依賴指紋與可信執行驗證；runner結果不冒充Verification節點status。
5. 本案不從日期或mtime推斷安全有效期，不以audit、verified_by或測試名存在代替執行。例外過期以執行當日UTC日期判expires_on小於今日，當日仍列到期日並提示；無核可或失效決策列無效例外。沒有宣告必要證據、或無法對應證據種類時列未核對，不填已滿足。
6. 各問題累積，不因一條壞掉停止列其他條目。schema錯誤的列保留node及可安全抽取的id，標invalid_record；重複ID保留每個出處不覆寫。來源修訂／證據適用性未由此工具計算者，一律列未核對；盤點只是母計劃驗收閘的輸入，不直接實作G1–G5。

## 輸出契約

文字依node、id穩定排序，先列讀取範圍與完整性，再列active/candidate、retired、待分類、覆蓋缺口與錯誤。每條展開來源、判準、證據清單、宣告狀態及機械核對限制，不截斷到只剩摘要。

JSON至少含schema_version、purpose、security_verdict、vault、observed_at、read_complete、records、retired、excluded_business、unclassified_contracts、unregistered_nodes、coverage、errors。records收security或unclassified的非retired項，retired收這兩類的撤除項，excluded_business收全部business-only項；三區不重複。各列包含來源原欄位、node、evidence_check及issues；coverage含inventory來源、status（known_inventory或unknown）、unmapped、candidate_only及限制說明。read_complete只講讀取，不能冒充所有登記都有效；registration_complete另計schema及引用錯誤，零條目時為false。security_verdict永遠not_assessed。

文字輸出把控制字元與雙向控制符可視化，不能讓資料注入終端格式；JSON用標準escaping保留字面值，不因文字消毒改變機器身份。異常錯誤走stderr，JSON stdout始終僅一個可解析物件；用法錯誤沿argparse行為。輸出僅記非秘密的驗收資料，登記規範禁止放真憑證。

## 首案登記與實作順序

1. 先跑本案規格閘與完整設計審；資料格式為主要審查面。未過閘不實作，文件自足性審不代替設計審。
2. 先建固定隔離vault測試樣本與CLI入口測試，再實作解析／引用核對／呈現。測試不啟動Docker、不執行樣本中的任何命令；以檔案前後比對驗證唯讀。
3. 正反樣本包括純業務、雙關注面、獨立安全政策，以及故意缺來源、壞JSON、零條目、重複ID、斷引用、symlink、候選與撤除、報告自稱pass但無證據、未映射入口。
4. 再對order-demo真實筆記做唯讀盤點。條目登記是另一步明示寫入：逐條核對規則來源才新增，沿用OD-01／OD-02身份並保留OD-03／OD-04未驗；若尚未登記就誠實輸出未登記，不靠暗中補條目讓演示好看。不遷移其他消費專案、不更新它們的vendor工具。
5. 完成後保存驗證紀錄與使用方式；不改母計劃Q3／Q4、不自動啟用CI或push閘。產品安全成效與方法五案仍歸母計劃。

## 驗收條款

以下manual是實作前的可執行測試設計，不代表已驗；實作時替換為實際測試綁定。

[S1] 三類來源樣本應只把security及unclassified列入主清單，雙關注面同來源只列一次，business-only列excluded_business且不算安全。 [manual:固定三類來源及重複來源樣本核對文字JSON與來源身份]

[S2] 壞JSON、重複鍵、未知schema、未閉合圍欄、錯資料夾及重複ID應列錯誤且退出2，不靜默漏項。 [manual:每個缺陷獨立樣本加一條正常護欄，驗正常項仍列出且壞項有明確原因]

[S3] 缺失或作廢來源、跨vault路徑與符號連結應拒絕引用；不得讀取repo外哨兵檔案內容。 [manual:隔離目錄建立內外哨兵與斷鏈，核對不洩露內容且退出2]

[S4] 盤點應保留reported_status但不得產生安全通過；有pass紀錄也只顯示declared_only。 [manual:固定未驗缺陷stale及pass來源，核對security_verdict永遠not_assessed且原因未被覆寫]

[S5] 零條目、缺inventory與未映射入口應分別列未登記、覆蓋未知及缺口，不輸出安全百分比。 [manual:三種樣本與完整映射對照，驗完整映射也只表示登記關係]

[S6] 文字與JSON應保留相同條目、來源及狀態，撤除與例外不抹去缺陷；過期核可必須列問題。 [manual:比較兩模式的身份集合與狀態，凍結UTC日期測到期前當日及過期]

[S7] 命令應保持唯讀、無網路及無程序執行，筆記中的命令或控制字元不能變成操作。 [manual:隔離樣本含命令誘餌及控制符，核對檔案指紋不變無誘餌產物且終端資料被轉義]

[S8] 指定vault有讀取失敗時應read_complete=false且退出2，不能回傳完整零條目；合法完整盤點含未驗時退出0但仍not_assessed。 [manual:模擬列舉讀取錯誤與合法未驗案例並核對CLI退出碼和可解析JSON]

## 實務隱患

已排除:金流:本案只讀本機筆記，不呼叫付款或訂單API。
已排除:對外送出:命令不連網、不上傳證據、不呼叫模型。
已排除:不可逆:不變更來源資料、不刪檔、不部署；回退只撤本次CLI功能。
守衛面:輸出可能被誤當放行，故固定not_assessed、分開宣告與核對，安全閘接線不在本案。
資源與效能:遍歷所選vault，單檔大小上限2MiB、總讀取上限64MiB、檔案數上限10000；超限列不完整並退出2，不靜默截掉尾端。上述是首版防失控設計值，並非量測容量或產品SLA。
來源安全:筆記內容是不可信資料，不執行命令、不追外部連結；工具本身必須由可信安裝啟動。未登記規則與盤點本身漏項無法靠清單保證發現，顯示覆蓋限制並留給獨立審計。
併發:本工具鏈不新增鎖或多人一致性協議；輸出描述本次讀取快照，不宣稱跨檔原子時點。若讀取期間偵測到檔案清單或內容變動，列不完整退出2；不得悄悄用混合結果作驗收。

## 回退

回退撤除本次命令與專用解析，保留既有筆記、原始報告及登記歷史；不改contracts、query、enforcement的語意。若格式被設計審否決，先修本規格，不對消費專案自動轉寫。

RETIRE-IF: 既有讀取入口能完整輸出相同來源、狀態及覆蓋缺口時合併重複入口；若成本超過使用者核可範圍停止擴大，不能把未知改成通過以減少工作。

REVISIT:2026-11-18 核對本指令的設計審與實作證據；未完成S1–S8前不得宣稱可用，未完成母計劃驗收閘前不得把盤點當安全放行。
