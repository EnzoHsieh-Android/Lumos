severity: major

我對照的是 `/Users/enzo/harness/lumos-auto-device/scripts/lumos` 與範本腳本。r2 把 r1 提的幾件事都收進來了:共用逐句對照函式、單向門共用 `_door_keyword_hits`、範本腳本把 debug 路徑寫進 `evidence.debug`、`_e2e_record_err` 驗 `checks`、`lands_in` 改成規格閘。r2 新補的段落裡,有一處引入第二種放行語意(major),另有五處小的不一致。

## 1. 分層與依賴方向:大致對齊,一處小出入

對齊的部分:
- judge 只記事實、推送檢查才判擋,跟現有分法一樣。judge 只吃 run 目錄與 steps.json:file: `scripts/lumos:40920`(`_e2e_judge_ui`)。
- 主線、分岔點、`_e2e_norm` 都沿用推送檢查已有的:file: `scripts/lumos:41922`(`_e2e_gate_mainline`)、`scripts/lumos:42045`(`_e2e_gate_body` 已持有 `ml_e2e`、`base_full`)。
- 範本腳本只多記一個路徑,跟現有「範本碰裝置、lumos 判定記帳」同一型:file: `scripts/templates/android-e2e-run.sh:495`(`evidence.dir`、`evidence.crash` 同一處寫入)。

不對齊的一處:
- 計劃寫 judge「只在整套跑寫紀錄時做」,但 `_e2e_judge_ui` 整套與按功能兩條路共用:file: `scripts/lumos:41080`、`scripts/lumos:41423`。照此寫法要在共用函式裡加一個「是整套才記」的分支,鄰居沒有這種分岔。
- 預覽的出口也沒指名。鄰居的 judge 提醒一律走 `notices`:file: `scripts/lumos:41029`、`scripts/lumos:41074`。計劃只寫「終端多印一段」,沒說走 `notices`。

severity: minor
blocking: 否 判準:分層方向對,但 judge 內多一個只在整套跑才記的分支,預覽出口也沒對到鄰居的 `notices`,實作時改成兩條路都記、預覽走 `notices` 即可。
引句:「只在終端多印一段預覽(零檢查的流程、有 `accept` 的情境沒對到的句子)」

## 2. 命名與錯誤處理:大致對齊,三處跟鄰居不一致

對齊的部分:
- 設定檢查掛進共用的 `_e2e_case_err` 鏈,回傳「錯誤訊息或 None」:file: `scripts/lumos:40597`。
- 紀錄欄位型別在 `_e2e_record_err` 驗:file: `scripts/lumos:40849`。
- `evidence.debug` 跟 `evidence.dir`、`evidence.crash` 同形,欄位不對就當沒有的處理跟 `_e2e_ui_evidence` 一樣:file: `scripts/lumos:40907`。
- `checks_reason` 平放是合理的,因為同一個 dict 的 `reason` 已被 fail 原因占用:file: `scripts/lumos:40920`。

不對齊 A:`accept_review.by` 把名字塞進 `by`
- 計劃的理由是放行紀錄的 `by` 只記 human/ai,所以這裡要自己記「誰」。這個理由不成立,因為放行紀錄本來就有分開的 `who` 欄:file: `scripts/lumos:42342`(`{"by", "who", "at", "note"}`)。
- 同一份紀錄體系裡,「誰簽的」現在有 `by`+`who` 與 `by:"human:名"` 兩種寫法。

severity: minor
blocking: 否 判準:結構對,但同一個欄位名 `by` 在放行紀錄與驗收句審查有兩種值形狀,而且計劃給的理由跟現況不符。
引句:「跟放行紀錄的 `by` 只記 human/ai 不同:這裡要記「誰」,單向門要能看出是哪個人點的頭。」

不對齊 B:新擋下代碼和鄰居的用法不同
- 現有 e2e 擋下的各種後續處方靠旗標分派,例如 `bad_record`、`newer_schema`、`merge_main`、`uncommitted`:file: `scripts/lumos:41995`、`scripts/lumos:42006`、`scripts/lumos:68478`(`_cl_say_e2e_next`)。
- `gate_code` 目前只有 `evaluation_timeout`、`evaluation_error`,意思是「判定自己壞了或逾時」:file: `scripts/lumos:42083`、`scripts/lumos:42093`。
- 治理帳的 `extra.gate_code` 欄位現成可用:file: `scripts/lumos:67856`。
- 計劃沒說新代碼的名字形狀(是否沿用 snake_case 英文)。也沒說 `_cl_say_e2e_next` 的分派改看 `gate_code` 還是旗標,可能同一個函式混用兩種判法。

severity: minor
blocking: 否 判準:能寫進治理帳,但把規則擋下塞進原本只表示「判定壞了」的欄位,後續處方分派的判法也沒定,容易長出旗標與代碼並存。
引句:「這幾條各自一個擋下代碼,寫進治理帳的 `gate_code`(撤除條件要數)」

不對齊 C:兩處新讀 JSON 沒指名沿用既有讀法
- 讀 commands.json 要「專用上限」,理由合理(深度確實可能超過 20 層)。但計劃沒說是給 `_e2e_load_json` 加參數,還是另寫一支讀法:file: `scripts/lumos:40972`,深度 20 層寫死在函式內;`scripts/lumos:35547`(`_events_depth_ok`)。
- 分岔點的舊紀錄(第 7 條)沒說要走 `_e2e_tree_json(limit=E2E_RECORD_FILE_MAX)` 加 `_e2e_record_err`:file: `scripts/lumos:41684`、`scripts/lumos:40849`。
- 舊紀錄讀不懂時也沒說要降成「這次不比」。照現有 `_e2e_gate_load` 的寫法會變成擋下,但這條只該是提醒:file: `scripts/lumos:41986`。
- 注意:`scripts/lumos:41686` 附近是否已有現成的帶上限讀法,我沒逐行確認 ⚠。

severity: minor
blocking: 否 判準:設計意圖是專用上限,結構沒錯,但沒寫沿用哪支讀法,實作時有長出第二套讀檔與驗證的風險。
引句:「巢狀層數與檔案大小給專用上限(實作第 0 步量過實際形狀再定,不沿用 `_e2e_load_json` 的 20 層)」

## 3. 第二種做法:一處放行語意不一致(major),其餘對齊

放行語意不一致(major)
- 現有放行只有一種語意:任何一筆 `_e2e_waiver_ok` 為真的放行,人或 AI 都算,直接放行:file: `scripts/lumos:41713`、`scripts/lumos:42064`(`any(_e2e_waiver_ok(w)...) → "waived"`)。
- AI 放行另有「還沒人看過、提醒」的配套:file: `scripts/lumos:41718`(`_e2e_ai_pending`)、`scripts/lumos:42274`(`--ack`)。
- r2 新補的第 5 條說新規則排在放行判斷之前,而且只有 `by` 是 human 的放行蓋得過、AI 放行蓋不過。這等於同一份 `waivers` 在兩段判定裡有兩套語意。
- 計劃有理由:成因是設定與流程內容、不是裝置狀態,而且單向門要人點頭。但它沒有評估沿用既有 AI 放行加 `--ack` 的路徑,也沒說這個語意由 `_e2e_waiver_ok` 旁邊的哪支單源函式承擔,只在 S9 用測試釘住結果。
- 這是 r2 新補的行為,r1 沒有。

severity: major
blocking: 是 判準:引入了「只有人放行蓋得過」這套跟 `_e2e_waiver_ok` 並存的放行語意;意圖有理由,但屬於改變放行規則的裁量,要先請 Enzo 確認並寫成單源判法再往下走。
引句:「放行只有人放的(`by` 是 human)蓋得過這幾條;AI 放行蓋不過」

其餘對齊的部分:
- 新舊認定沿用 `_e2e_norm` 與推送檢查已有的主線和分岔點兩份設定,沒另寫挑主線的邏輯:file: `scripts/lumos:41922`、`scripts/lumos:41747`(`_e2e_runs_missing` 同樣用 `_e2e_norm`)。
- 單向門掃描共用 `_door_keyword_hits` 加類別篩選,沒另起一套詞表:file: `scripts/lumos:13974`、`scripts/lumos:36543`。
- 外來文字出口:`_e2e_gate_out` 已統一用 `_out_clean` 清所有字串,計劃再點名一次不衝突:file: `scripts/lumos:41633`。
- 提醒出口:計劃沿用 `_cl_say_e2e_notes` 的「提醒」行,方向一致。但該函式現在只在 ci、skipped-env、pass-by-feature 與 `pending_ai` 印,實作時要擴到整套 pass 與 waived:file: `scripts/lumos:68512`。

## 4. 落點:大致合理,一處缺口

對齊的部分:
- `Systems/android-e2e-acceptance` 在這個 repo 已存在,about_code 是 `scripts/lumos` 與 `scripts/templates/android-e2e-run.sh`,管 judge、e2e 段、推送檢查,新判定和新設定鍵寫進去合理。
- `Systems/規格閘` 補一行「第三個消費者」合理。那張詞表目前的消費者是門判定與 `pitfalls --check`:file: `scripts/lumos:36543`,註解要求改表時升 `_DOOR_RULE_VERSION`。

缺口:
- 落點第三條要改 lumos-project-notes 的〈產 maestro UI flow 的派工要求〉,但它不在 `lands_in`,也沒說這份技能檔的家是哪一篇。
- 計劃只處理了 lumos-android-evidence 的家(掛進 android-e2e-acceptance 的 about_code)。lumos-project-notes 的 commands 檔沒有對應的處理。
- 專案鐵則 5 要求改到的每支檔都要先有家。

severity: minor
blocking: 否 判準:兩個 `lands_in` 本身合理,但落點一節多列了一個沒有家的改動檔,寫計劃時補一句歸哪篇即可。
引句:「lumos-project-notes 的〈產 maestro UI flow 的派工要求〉:第 1 段(斷言)與第 4 段(完成判準)補驗收句與 label」

不對齊共 6 條,其中 major 1 條
