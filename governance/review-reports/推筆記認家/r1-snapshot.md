---
type: project
status: doing
created: 2026-09-12
updated: 2026-09-12
aliases: []
tags:
  - type/project
  - status/doing
  - scope/retrieval
lands_in:
  - Systems/retrieval-ranking
  - Systems/節點還原
  - Systems/check-j-regen-guard
summary: |-
  KEY:改檔前推筆記把「家」(每支檔有家驗過的 about_code)當成一條入口:改哪支檔,一定推它的家;只加入口、不降級任何既有必推項
  KEY:依舊案 固定席扇出降權_計劃 d4 的重提條件而重提(「丙:第四條保送需先把漏標率壓到零,無新證據不重提」)——新證據是每支檔有家讓新檔一定有家、每次提交驗
  KEY:節點還原把 about_code 設成必要條件:從程式重建的節點(蓋 regen 章)沒寫 about_code 就 lint 擋;SOP 第 4 步寫明必要、第 6 步出口看健檢 S8
---
# 推筆記認家_計劃

> 白話:每支程式檔現在都有一篇「管它的」節點(家)。改那支檔時,家應該是最該被推給 agent 看的那一篇——可是推筆記的機制到現在還沒在用它。這案讓推筆記認家;另外讓接手舊專案、還原節點時,每篇還原出來的節點都一定寫明它管哪幾支檔。

## 為什麼(這批的來源)

- Enzo 2026-09-12 問:about_code 這個標籤,能不能讓節點相關性、推給 agent 的精準度再提升。
- 查證(讀程式+乾淨審查員拿原始問題查,兩個來源一致):
  - 決定推哪幾篇的只有四條路:正文用反引號寫的檔案路徑(完整路徑、或在受版控檔裡唯一的裸檔名)、從那些節點沿連結往外擴、事故筆記的觸發條件。★about_code 不是入口★,只在「一定會推的那幾篇」裡當排序。
  - 那個排序還要「預標指紋」沒過期,而 `lumos append about_code` 與 `lumos new --code` 都不寫指紋——每支檔有家補的家,全部不會觸發這個排序。
  - 推送前的波及計算聚合時把這個排序丟掉;派審查員時的圖譜參考完全沒用到。
- ★舊案攔截★:[[Projects/固定席扇出降權_計劃]] 三輪設計審沒收斂,Enzo 裁 about_code 只做排序;成績單那條決定寫明「丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提」。★圖譜攔截★站:開案前;源:固定席扇出降權_計劃 d4。
  - 新證據:[[Projects/每支檔有家_計劃]](2026-09-11 上線)讓新增的程式檔提交當下一定有家、原本有家的檔變沒家會擋;三個 POS 專案整理後健檢 S8 幾乎沒有沒家的檔。這正是當年缺的「漏標率壓到零」。
  - 舊案 r1 的教訓照單全收:當時把「有 about 欄但不含目標檔」降到自由席,結果把該看的筆記踢出必推名單(必看裡 2/9、3/5 根本不是 about)——★本案只加入口,不降級任何既有必推項★。
- 另一半:Enzo 同日要設計審順便看「既有專案還原節點,能不能把 about_code 也設成必要條件」。現況:SOP 第 4 步已寫用 `--code` 開節點,但沒寫必要、也沒有任何檢查。

PRIOR-ART:最小解在讀側排序那一層——多一條入口,不改分數公式、不動其他三條路。世界解過:GitHub 的 CODEOWNERS 用「檔 → 負責者」的宣告直接點名審查者,結構化的宣告優先於文字比對。裁定=借用(把家當宣告式路由),自建只有接到既有排序的那一段;不採新依賴。

## 名詞

- **家**:照 [[Projects/每支檔有家_計劃]] 的定義——狀態 doing/done/stale 的 Systems 節點,about_code 列了這支檔;比對用同一支字面比對鍵,不看預標指紋。
- **必推名單**:推筆記的固定席——事故、帶合約的直接節點、一跳合約間接,不截斷,一定會推給 agent。
- **可選名單**:其餘候選照分數競爭,最多 10 篇加 3 篇保底。
- **大檔**:家的篇數 ≥ `LUMOS_IMPACT_ABOUT_MAX`(預設 8)的檔,例如本工具鏈主程式有 31 個家。
- **從程式重建的節點**:蓋了 `regen: from-scratch/<日期>` 章的 Systems 節點(節點還原 SOP 第 4 步蓋)。

## 核心裁定

### 甲、推筆記認家

- [S1] 家的定義與比對鍵沿用每支檔有家那一支(同一個函式,不另寫一套);不看預標指紋。 [test:t_impact_home_uses_nodehome_definition]
- [S2] 改檔前推筆記(`lumos impact --file --ranked`,也就是 Edit 前那個自動推筆記的 hook)把目標檔的家當成一條入口:家一定進候選、而且進必推名單,不必正文用反引號寫這支檔。 [test:t_impact_home_is_entry_and_pinned]
- [S3] 必推名單的順序:事故最前,其次家,其餘照原本;家之間照分數。取代原本要預標指紋沒過期的「關於命中」排序。 [test:t_impact_pins_order_incident_home_rest]
- [S4] 大檔不整批進必推:只有帶合約的家進必推,其餘家在可選名單照分數競爭(不另加分,避免巨檔噪音——舊案 held 那題 22 誤放全出自改主程式)。 [test:t_impact_home_cap_for_big_files]
- [S5] 只加不降:事故、帶合約的直接節點、一跳合約間接照原本規則進必推,不因為不是家而被降;不是家、只被反引號提到的節點照原本規則。 [test:t_impact_home_is_additive_only]
- [S6] 推送前的波及計算(`impact --diff`)聚合時保留家的入口與順序;派審查員時的圖譜參考(dispatch-lens 的 diff 與 spec 兩種)也認家。 [test:t_impact_diff_keeps_homes] [test:t_dispatch_lens_includes_homes]
- [S7] 新增旋鈕 `LUMOS_IMPACT_HOME`(預設 1;0=完全照原本),給離線評測對照用,不是使用者旗標(同既有 `LUMOS_IMPACT_*` 慣例)。 [test:t_impact_home_knob_off_is_old_behavior]
- [S8] 顯示:Edit 前推筆記的清單上,家標「★家★」;原本的「★關於★」標示拿掉(它依賴的預標指紋不再影響排序)。 [test:t_impact_hook_shows_home_label]
- [S9] 預標指紋不再影響推筆記;`about-code restamp/revert/migrate-stamp` 指令保留(舊資料與回滾用),說明改寫成「指紋只記標記當時的正文,不影響推筆記」。 [test:t_about_stamp_no_longer_affects_ranking]
- [S10] 評測:用既有評測器跑練習題與保留題,P@8 與「輸出前 3 名必看命中率」都不得比現行低超過 1 個百分點(活語料本身有 ±1pp 漂移);前後數字寫進驗證紀錄。 [manual:上線前後各跑一次 governance/eval/retrieval_eval.py 兩組,數字寫進驗證紀錄]

### 乙、節點還原把 about_code 設成必要條件

- [S11] 從程式重建的節點 about_code 至少要有一支檔;`lumos lint` 對這種節點缺 about_code 報錯(提交前的逐篇 lint 會擋)。 [test:t_lint_regen_node_requires_about_code]
- [S12] 節點還原 SOP:第 4 步寫明「about_code 是必要條件,每篇還原節點都要帶 `--code`」;第 6 步出口多一項——這批還原動到的模組,它們的程式檔在健檢 S8 不再列為沒家(真的不該有家的,寫進專案設定 `node_home.ignore` 並說明理由)。快查表(commands/09)與完整版(reference.md)兩處一致。 [test:t_restore_sop_requires_about_code]
- [S13] `lumos new system` 沒帶 `--code` 時多印一句提醒(不擋):不管任何程式檔的節點通常是「主題」不是「模組」;確定要這樣,就在負責範圍講清楚它不管檔的理由。 [test:t_new_system_without_code_reminds]

## 範圍外(刻意不做)

- 不動反引號、連結擴展、事故觸發這三條入口,也不改分數公式。
- 不剔除舊反引號造成的誤推——那是舊帳整理(健檢 S9 列著),新寫的由每支檔有家擋。
- 不重開「關於欄位」的模型預標——那是舊案的主案方向;本案用的是每支檔有家驗過的家。
- 不替 POS 專案另建標準答案題(成本高、樣本少);消費專案的效果改看推播漏網量測的週清單。
- 乙只管「從程式重建的節點」;一般手寫的 Systems 節點不強制 about_code(概念型、跨模組的說明篇是合法的),只在 [S13] 提醒。

## 落點

- **推筆記那一段**(甲):[[Systems/retrieval-ranking]]——改檔前推筆記的排序本來就記在這篇;實作時把 Edit 前推筆記那支 hook 檔明文加進它管的範圍(那支檔現在掛在棧別提問表態閘與 Codex 接線兩篇底下,都不是講推筆記的)。
- **SOP 那一段**(乙):[[Systems/節點還原]]。
- **lint 那一條**(乙):[[Systems/check-j-regen-guard]]——regen 章的規則集中在這篇。

## 實務隱患

- **噪音變多**:家一定推,家很多的檔會把必推名單撐大——[S4] 大檔門檻擋;門檻沿用既有 8,不另校準(REVISIT 見回頭條件)。
- **寫錯的家**:about_code 路徑存在但語意不對(掛錯篇),會把錯的那篇推上來——每支檔有家只驗路徑、不驗語意;靠規則三「寫回要落在家」長期把錯的家曝出來。已排除:不另做語意檢查(舊案走過模型預標,三輪沒收斂)。
- **評測尺量不到**:標準答案題出在本工具鏈圖譜上,最常改的主程式是大檔,認家對它沒有鑑別力——[S10] 只當「不退步」的尺;真正的效果看消費專案的推播漏網週清單(回頭條件)。
- **效能**:Edit 前推筆記那支 hook 外層 30 秒超時、多檔 patch 總預算 20 秒;找家要掃全圖的 about_code——既有的 about 計數已經有快取,本案沿用,不另掃一次。
- **舊專案沒更新**:沒跑 `lumos update` 的專案照舊行為,不會壞。
- **從程式重建的章是自己蓋的**:不蓋 regen 章就完全繞過 [S11](既有天花板,check-j-regen-guard 那篇已記);本案不處理,SOP 第 6 步出口的健檢 S8 是第二道。
- **兩家一致**:Claude 與 Codex 的 Edit 前推筆記都呼叫同一支 lumos,行為一致。
- **不可逆、金流、對外寄送**:不碰。已排除:這案只改讀側排序、lint 與文件,不寫任何正式環境。

## 驗收怎麼跑

- 子集:`python3 scripts/test_lumos.py -k impact_home`、`-k impact_pins_order`、`-k dispatch_lens_includes_homes`、`-k about_stamp_no_longer`、`-k regen_node_requires`、`-k restore_sop_requires`、`-k new_system_without_code`、`-k impact_hook_shows_home`。
- 評測:`python3 governance/eval/retrieval_eval.py --goldset governance/eval/retrieval-goldset.json` 與加 `--split held`,上線前後各一次。

## 回頭條件

- 消費專案的效果量不到上線當下。REVISIT:2026-10-12 看推播漏網量測的週清單裡「關於欄」那一類(沒推、agent 卻自己讀了、而那篇是那支檔的家),比較上線前後的筆數;沒下降就回頭查家有沒有真的進必推名單
- 大檔門檻 8 是沿用舊數字。REVISIT:2026-10-12 用練習題、保留題重跑一次,並抽三個 POS 專案各五次 Edit 看必推名單有沒有被家撐爆

## 合約候選(收斂時複核,候選≠已標)

- 家一定進必推名單(大檔除外,[S2][S4])。
- 只加不降:既有必推項不因為不是家而被降([S5])。

## 審計修正紀錄
