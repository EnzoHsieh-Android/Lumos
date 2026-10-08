---
type: project
status: doing
created: 2026-10-03
updated: 2026-10-03
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/lumos-cli-read
  - Systems/lumos-cli-write
related:
  - "[[Projects/漂移防治路線圖_計劃]]"
  - "[[Systems/lumos-cli-read]]"
  - "[[Systems/lumos-cli-write]]"
---
# 驗收紀錄寫明驗了哪些功能_計劃

白話:健康檢查(doctor)第 3 段「驗收紀錄說它驗了某功能,功能那邊有沒有反向登記」(下稱 doctor 3/4)——但驗收紀錄本身沒有任何欄位寫「驗了哪些功能」,工具只能拿正文裡的每一個 `[[Systems/X]]` 連結反推。正文裡寫「現況見 [[Systems/X]]」這種指路連結(只是帶讀者去看、不代表驗過),就被當成「驗過 X」,要求 X 反向登記,推送被擋。這份計劃讓驗收紀錄可以在開頭欄位 `system_refs` 明寫驗了哪些功能;有寫就只看它,正文連結不算;沒寫的舊紀錄照舊從正文推。

依據:
- rtb(另一個用 lumos 的消費專案)清理循環第 1 輪回傳第 2 項(rtb 的 governance/audits/2026-10-01-drift-sweep/2026-10-02-cleanup/return-to-toolchain.md):在驗收紀錄補更正括號「現況見 [[Systems/X]]」,doctor 立刻要求 7 篇 Systems 反向登記,算 7 個 issue、推送被擋;rtb 只好把 14 個指路連結改成純文字。
- Enzo 2026-10-03 裁:加新欄位、範圍收窄(第一版只接健康檢查、建紀錄指令、同步指令、合法欄位清單,不接圖譜連線等其他用到 `plan_refs` 的地方)。
- [[Projects/漂移防治路線圖_計劃]] 清理與防治循環第 1 輪排序:1b 之後就是這項(擋錯推送、修法小)。

PRIOR-ART: 照驗收紀錄既有的 `plan_refs`(這份驗收對應哪份計劃)開頭欄位寫法——清單欄位、每項一個 `[[連結]]`、`lumos append` 加、`new verification --plan` 建檔時寫。推「驗了誰」的邏輯(含跳過作廢、失效、不通過的紀錄)在 doctor 3/4 與 `sync-verified-by` 各寫了一份一模一樣的,這次整段抽成共用一支 `_verification_system_targets`,兩邊改用它,跳過哪些狀態也只留這一份。世界解:文件系統常見「明確宣告的依賴 vs 從內文推出的引用」分兩種(例如套件管理的宣告依賴對比原始碼 import 掃描),宣告的優先、沒宣告才退回推。
RETIRE-IF: 滿 8 週全部專案的驗收紀錄都沒寫過 `system_refs`、doctor 3/4 也沒再出現指路連結誤報 → 欄位留著但說明降級;或寫了 `system_refs` 的紀錄裡,有一半以上漏列真的驗了的功能(反向登記因此少掛)→ 改回只從正文推、另給指路連結的寫法。
REVISIT:2026-12-01 數本 repo 與 rtb 的驗收紀錄有幾篇寫了 system_refs、doctor 3/4 有沒有再出現指路連結誤報,判 RETIRE-IF

## 範圍

- 做:驗收紀錄的開頭欄位 `system_refs`(清單,每項 `[[Systems/X]]`);doctor 3/4 與 `sync-verified-by` 改用共用函式判「驗了誰」;`new verification --systems` 建檔時兩邊都寫;登記成可 `append`/`remove` 的清單欄位;`system_refs` 指到存在但不是 Systems 的節點時 doctor 3/4 列出(指到不存在的節點,doctor 2/4 本來就會報,不重複報)。
- 不做:不接具名連線(`TYPED_EDGE_FIELDS`)、作廢連鎖、反向索引、圖譜視覺化等其他寫死 `plan_refs` 的地方(Enzo 裁範圍收窄)——但 `system_refs` 每一項是單一連結,照既有通則會進 `n.targets`,一般圖譜邊(孤兒、壞連結、推薦等)照樣算它,這是既有行為、本案不改;不加進 `LINK_KEYS`(它不做寫法檢查,只影響「只改連結欄位的提交算不算假同步」的判定,本案用不到);不改驗收紀錄範本(範本預放空欄位會讓忘了填的紀錄變成「沒驗任何東西」,反而把檢查關掉);不自動把舊紀錄補上 `system_refs`;不改功能筆記那側的 `verified_by`。

## 做法

1. **共用判法** `_verification_system_targets(env, rel, n)` → None(這份紀錄是 stale、fail 或 superseded,不構成雙向義務,呼叫端跳過)或(驗了哪些 Systems 的 rel 集合, `system_refs` 裡指到存在但不是 Systems 的項):開頭欄位有 `system_refs` 這個鍵(寫成空清單也算)→ 只看它,解析每項連結,落在 `Systems/` 的收進集合,存在但不是 Systems 的收進問題清單,解析不到的不收(doctor 2/4 會報);沒有這個鍵 → 照舊用現行 `n.targets`(正文去掉程式碼區塊後的連結,加上開頭欄位裡「整個值恰為單一連結」且不是區塊寫法的項)落在 `Systems/` 的。
2. **doctor 3/4** 與 **`sync-verified-by`** 改呼叫它(跳過哪些狀態由它決定,兩邊不再各寫一份)。3/4 的 `system_refs` 問題項另用一個 `warn`(同一段、另一個標題「有 N 項 system_refs 指到的不是功能筆記」,算 issue),不混進漏寫 verified_by 那個標題的數字。`sync-verified-by` 的 dry-run 說明句補一句「有 system_refs 的紀錄只看它」。
3. **建紀錄** `new verification --systems A,B`:照舊對 A、B 加 `verified_by`,另對新紀錄自己加 `system_refs`(每項一行,走既有的 `cmd_append`,照 `plan_refs` 那段的寫法);寫失敗時提醒句另給 `lumos append <新紀錄> system_refs "[[Systems/X]]"`(既有那句叫人跑 `sync-verified-by --apply`,它只補功能那側、補不到 `system_refs`)、rc2。建紀錄當下印的教學(`NEW_HINT` 的 verification 那段)補一句 `system_refs`。
4. **登記**:`system_refs` 只進 `LIST_KEYS`——`append`/`remove` 的白名單、多個連結塞同一行的 lint 都看它,lint 的已知欄位清單也併入它,所以不必另加 `_KNOWN_FRONTMATTER_KEYS`。
5. **要同步的文件**:[[Systems/lumos-cli-read]](doctor 3/4)、[[Systems/lumos-cli-write]](new verification、sync-verified-by、append 清單欄位);`skills/lumos-project-notes/commands/03-寫回圖譜.md`(驗收紀錄怎麼寫)、`commands/04-自檢與健康.md`(3/4 段)、`skills/lumos-project-notes/reference.md`;精簡版 `slim/skills/lumos-project-notes/reference.md` 沒有驗收紀錄欄位那一節,不用同步。

## 條款

(測試名是預先宣告,實作時新增。)

- [S1] 當驗收紀錄寫了 `system_refs: [[Systems/A]]`、正文又連到 Systems/B 時,doctor 3/4 應只要求 A 反向登記,B 沒登記不算漏 [test:t_doctor_check3_system_refs_authoritative]
- [S2] 當驗收紀錄沒寫 `system_refs` 時,doctor 3/4 應照舊從正文連結推 [test:t_doctor_check3_system_refs_authoritative]
- [S3] 當 `system_refs` 寫成空清單時,doctor 3/4 應不要求任何功能反向登記 [test:t_doctor_check3_system_refs_authoritative]
- [S4] 當 `system_refs` 有一項指到存在但不是 Systems 的節點時,doctor 3/4 應另起一個標題列出並算 issue;指到不存在的節點時只由 doctor 2/4 報、3/4 不重複報 [test:t_doctor_check3_system_refs_bad_entry]
- [S5] 當跑 `sync-verified-by` 時,有 `system_refs` 的紀錄應只補它列的功能,正文指路連結不補 [test:t_sync_verified_by_system_refs]
- [S6] 當 `new verification <名> --systems A` 時,新紀錄應帶 `system_refs` 列 A,A 應帶 `verified_by` 回指新紀錄;寫 `system_refs` 失敗時提醒句應給 `lumos append` 的補法 [test:t_new_verification_writes_system_refs]
- [S7] 當 `lumos append` 對驗收紀錄加 `system_refs` 時應成功,lint 應不把它當成打錯的欄位名 [test:t_system_refs_registered_field]
- [S8] 當驗收紀錄是 stale、fail 或 superseded 時,不論有沒有 `system_refs`,doctor 3/4 與 sync 都應照舊跳過 [test:t_doctor_check3_system_refs_authoritative]

## 回退

- revert 實作提交即可。已寫進筆記的 `system_refs` 留著:revert 後 lint 會唸「不認得的欄位」(只提醒),doctor 3/4 照舊從 `n.targets` 推(`system_refs` 每項是單一連結,本來就在 `n.targets` 裡,不會少掛)。

## 實務隱患

- **漏網**:寫了 `system_refs` 卻漏列真的驗了的功能,反向登記就少掛一篇,doctor 不會發現——宣告優先的代價,RETIRE-IF 第二條在量。
- **誤擋**:`system_refs` 指錯(打錯字、指到計劃)會算 issue、推送前 `doctor --ci` 擋——本意,訊息要講改法。
- **相容**:舊紀錄不寫就照舊,消費專案 `lumos update` 後行為不變;只有自己寫了欄位的紀錄換判法。
- **時間**:判法跟現行一樣是逐篇讀開頭欄位,不多讀檔。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只讀寫筆記,不連網
- 已排除:不可逆:只改判法與新增欄位,revert 回得去
- 已排除:併發:寫入走既有的 cmd_append(逐檔原子、自帶鎖),不新增寫入路徑
- 守衛面:doctor 3/4 本來就算 issue、推送前會擋;這次讓它少擋指路連結、多擋寫壞的 `system_refs`。

## 實作紀錄

(還沒開始)
