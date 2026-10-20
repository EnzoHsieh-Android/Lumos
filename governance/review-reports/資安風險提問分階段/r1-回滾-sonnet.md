severity: major

回滾席(回滾-sonnet)。我先列出這份設計裡會擋推送、寫治理帳或重算判定的入口,再逐個答「誤擋或要退回時怎麼辦」。

**入口清單**
- (a) `pitfalls --stage` 七個新風險面:只提醒,不擋、不寫帳。
- (b) `spec-gate` 新增的一行提醒:`spec-gate` 本來就會寫門的留痕。
- (c) `security list` 的 `cells`、`considerations` 與 S3 衝突判定:退出 2。
- (d) 經姊妹計劃 d2 併審的 schema v2:改 `schema_version`,影響盤點讀取。
- (e) `threat_categories` 與 `required_evidence` 下限(S5)。
- (f) 威脅類別表版號與漂移測試(S12)。

(a) 的回退成立:七項只有一個讀表的地方(`_pitfalls_stage`,已用 grep 確認),撤掉即回原狀。其餘入口有下面的洞。

## 逐條 finding

### 1. 格子層錯誤會經姊妹閘擋下整個專案的推送,跟「open 不擋」互相矛盾
severity: major
blocking: 是
判準:照 spec 實作會做出誤擋推送的系統,而且回退時沒有限時放行的辦法。
- spec 段落:〈四〉S3「列錯誤、退出 2」,以及守衛面「不改規格閘的擋法與推送閘」。
- 問題:`_secinv_exit_code` 是「`errors` 非空就回 2」。姊妹計劃〈四、閘門〉規定:「盤點讀取不完整或登記錯誤,而這個專案有任何資安登記痕跡」就擋,原因是「判不清就擋」。本篇新增的錯誤種類有:S3 去向衝突、同格兩列 considerations、`@` 開頭的 surface id、未知的類別 id。spec 沒說它們算不算姊妹閘的「登記錯誤」。
- 具體例:消費專案作者在 considerations 把某格寫成 `not_applicable`,同一格又有護欄覆蓋。`security list` 退出 2。姊妹閘上線後,該專案所有推送被擋。姊妹計劃的例外流程只蓋「證據種類」,蓋不到這種結構錯誤。照 spec 實作,一個格子的文字筆誤就能卡死整個專案。
- 佐證:file: `scripts/lumos:7284-7286`(退出碼規則)。
- 要補:寫明格子層錯誤是否進 `errors`,或另開不影響姊妹閘的錯誤類別;並給誤擋時的出路。

### 2. schema v2 的回退斷在讀取層:舊工具遇到 v2 圍欄會整塊拒收
severity: major
blocking: 是
判準:照〈回退〉字面操作,會讓全部已寫 v2 的消費專案推送被擋。
- spec 段落:〈回退〉「已寫進消費專案的 considerations 與 pending_questions 不刪」,以及〈一〉「照盤點規矩升 `schema_version`」。
- 問題:舊讀取器只收 `sv == 1`,否則記 `unknown_schema_version` 並 `return None`,整塊圍欄(連 v1 就有的護欄)都不採用。〈回退〉只講撤七個風險面、`triggers` 與 spec-gate 一行,沒有涵蓋「把盤點讀取器退回 v1」。
- 具體例:消費專案 order-demo 在 d3 實驗期間已升 v2 並寫了 considerations。設計審或上線後出問題,工具鏈退回舊讀取器。order-demo 的圍欄全部變成 `unknown_schema_version`,`read_complete` 為假。姊妹閘因此擋 order-demo 推送,而「消費專案的 considerations 不刪」又禁止退回資料。兩邊互鎖。
- 另一個缺口:〈回退〉也沒說 v2 圍欄何時算「可以升」。需要先有一版同時讀 v1、v2 的工具再讓消費專案升,這個順序 spec 沒寫。
- 佐證:file: `scripts/lumos:6990-6993`;file: `docs/lumos-toolchain-knowledge/Projects/安全主張驗收閘_計劃.md:488-489`(姊妹〈回退〉只講「欄位變更被審否決就修規格」,同樣沒處理已升版的專案)。
- 要補:讀取器同時支援 1 與 2 的過渡版必須先於任何消費專案升 v2;〈回退〉要寫明退回 v1 讀取器的前提,是消費專案先降圍欄或工具保留 v2 讀取。

### 3. 類別表改版或回退後,舊資料引用的類別 id 沒有去向
severity: major
blocking: 是
判準:表退版會讓已存在的 controls 或 considerations 變成無效,走進 finding 1 的誤擋。
- spec 段落:〈二〉「舊格子的狀態照舊保留」,以及 S10。
- 問題:controls 的 `threat_categories` 與 considerations 的類別欄引用表裡的 id。表由 v1 退回,或改名、刪類時,這些引用變成未知 id。spec 只寫「舊格子狀態保留」,沒說未知 id 是忽略、報錯還是轉成 open。
- 具體例:表升到 v2 新增 `x-new`,消費專案某護欄寫了 `threat_categories: [x-new]`。表退回 v1 後,該護欄覆蓋的格子不存在。報錯就是 finding 1 的誤擋,忽略就是靜默失去覆蓋,二者 spec 都沒選。
- 另一個缺口:S10「每格帶建立時的表版號」站不住。格子由 inventory 即時重算,spec 並沒有給「建立時」的版號找一個存放處(considerations 欄位、治理帳都沒列)。照字面實作時,每次重算只會帶當前版號,S10 寫不成真測試。
- 要補:未知類別 id 的處理規則;版號存在哪、誰寫。

### 4. spec-gate 新增提醒沒寫失敗時放行,可能把規格閘本身弄壞
severity: major
blocking: 是
判準:照 spec 實作,新增一行提醒讀盤點出錯時,可能卡住所有連到資安 Systems 的計劃進實作。
- spec 段落:〈三〉「spec-gate 這一行是新增的提醒…印出那些護欄與 open 格子數,不擋」,以及 S13。
- 問題:`spec-gate` 是會寫門留痕(`spec-gate-run`)的入口。這一行要讀盤點;盤點讀取錯誤時(finding 1、2 的情境),spec 沒寫該行是跳過、印警告還是讓整個規格閘失敗。「不擋」只描述正常路徑。
- 具體例:`lands_in` 連到的 Systems 圍欄是 v2、而工具已退回 v1。提醒那行拿到 `unknown_schema_version`。若例外沒被吞掉,spec-gate 整個報錯,計劃無法留門、不能進實作。
- 要補:寫明提醒那行出錯一律吞掉並只印一行警告,且不影響門的判定與留痕。

### 5. 漂移測試是回滾時的單邊風險
severity: minor
blocking: 否
判準:實作者做對了也只是回滾時多踩一次紅燈,可靠流程補一句就能避免。
- spec 段落:〈二〉S12 漂移測試。
- 問題:表的正本在 `Systems/情境出題`,鏡像常數在 `scripts/lumos`,測試逐欄比對。回滾時若只退其中一邊(例如只還原圖譜筆記),測試紅,而測試是推送閘的一部分,推送被擋。spec 沒寫回滾必須兩邊同提交。
- 要補:〈回退〉加一句,表正本與鏡像常數要在同一個提交一起退。

## 已讀,無 finding 的部分
- (a) `pitfalls --stage` 的七個新風險面與 `triggers` 判法:只提醒、不寫帳。確認唯一讀 `f["when"]` 的地方是 `scripts/lumos:49099`,spec 說要收成一支函式,沒有第二個讀者會因新項缺 `when` 而報錯。回退乾淨。
- S5 的 `required_evidence` 下限:屬姊妹計劃 S14 擋,本篇只負責類別表欄位。
- 〈五〉P2 推廣線:新風險面只是提醒,不寫帳、不重算判定。

## 風險類(第 4 點)
- 守衛面:見 finding 1,新錯誤種類可能被姊妹閘當成「登記錯誤」擋推送。
- 舊資料與舊帳相容:見 finding 2、3。
- 已在途分支要不要重新表態:無。新增項只提醒,在途分支不被重算。
- 跟其他計劃的交界:見 finding 1、2、4,都在跟姊妹計劃的接口。

最嚴重 severity:major;blocking 共 4 條(finding 1、2、3、4)。
