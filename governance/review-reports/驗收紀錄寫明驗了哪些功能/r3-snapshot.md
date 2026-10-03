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

白話:健康檢查(doctor)第 3 段「驗收紀錄說它驗了某功能,功能那邊有沒有反向登記」(下稱 doctor 3/4)——但驗收紀錄本身沒有任何欄位寫「驗了哪些功能」,工具只能拿正文裡的每一個 `[[Systems/X]]` 連結反推。正文裡寫「現況見 [[Systems/X]]」這種指路連結(只是帶讀者去看、不代表驗過),就被當成「驗過 X」,要求 X 反向登記,推送被擋。這份計劃讓驗收紀錄可以在開頭欄位 `system_refs` 明寫驗了哪些功能;有寫就只看它,正文連結不算,每一項照 `verified_by` 那類欄位既有的連結規則判,寫壞了一律報出來、不默默當成沒驗;沒寫的舊紀錄照舊從正文推。

依據:
- rtb(另一個用 lumos 的消費專案)清理循環第 1 輪回傳第 2 項(rtb 的 governance/audits/2026-10-01-drift-sweep/2026-10-02-cleanup/return-to-toolchain.md):在驗收紀錄補更正括號「現況見 [[Systems/X]]」,doctor 立刻要求 7 篇 Systems 反向登記,算 7 個 issue、推送被擋;rtb 只好把 14 個指路連結改成純文字。
- Enzo 2026-10-03 裁:加新欄位、範圍收窄(第一版只接健康檢查、建紀錄指令、同步指令、合法欄位清單,不接圖譜連線等其他用到 `plan_refs` 的地方)。
- [[Projects/漂移防治路線圖_計劃]] 清理與防治循環第 1 輪排序:1b 之後就是這項(擋錯推送、修法小)。

PRIOR-ART: 照驗收紀錄既有的 `plan_refs`(這份驗收對應哪份計劃)開頭欄位寫法——清單欄位、每項一個 `[[連結]]`、`lumos append` 加、`new verification --plan` 建檔時寫、自己那段(doctor 4/4)報自己的斷鏈。★每一項怎麼判直接借具名欄位索引 `build_typed_index` 的既有規則★(只認整個值恰為一個連結;寫了路徑的要完全對上、不退回用檔名猜;沒寫路徑的用檔名找、只收唯一候選,多個候選報不明確;其他寫法列為「不是單一連結」)——把它判單項的那段抽成共用一支,索引與本案都用它,不另訂第二套。「宣告優先、沒宣告才推」在本 repo 的近似先例是 `aliases: []` 宣告制與「有宣告才驗」的 lint 設定(但那邊空清單合法,本案空宣告算寫壞,理由見〈做法〉1)。推「驗了誰」的邏輯在 doctor 3/4 與 `sync-verified-by` 各寫了一份一模一樣的,這次抽成共用一支 `_verification_system_targets`,兩邊與孤兒紀錄的推薦都改用它。世界解:文件系統常見「明確宣告的依賴 vs 從內文推出的引用」分兩種(例如套件管理的宣告依賴對比原始碼 import 掃描),宣告的優先、沒宣告才退回推;宣告寫壞時要報錯,不能默默當成沒有依賴。
RETIRE-IF: 滿 8 週全部專案的驗收紀錄都沒寫過 `system_refs`、doctor 3/4 也沒再出現指路連結誤報 → 欄位留著但說明降級;或寫了 `system_refs` 的紀錄裡,有一半以上漏列真的驗了的功能(反向登記因此少掛)→ 改回只從正文推、另給指路連結的寫法;或寫了的紀錄有一半以上曾被 doctor 3/4 判寫壞 → 寫法太難,回頭改設計。
REVISIT:2026-12-01 數本 repo 與 rtb 的驗收紀錄有幾篇寫了 system_refs、doctor 3/4 有沒有再出現指路連結誤報或寫壞的 system_refs,判 RETIRE-IF;順便看 rtb 自己複製進 repo 的 lumos 版本含不含 system_refs

## 範圍

- 做:驗收紀錄的開頭欄位 `system_refs`(清單,每項一個指到功能筆記的 `[[連結]]`);每項照具名欄位索引的既有規則判,另要求落在 `Systems/`;doctor 3/4、`sync-verified-by`、孤兒紀錄的推薦改用共用函式判「驗了誰」;寫壞的項 doctor 3/4 都列出、算 issue(不默默當成沒驗);`new verification --systems` 建檔時把其中的功能筆記寫進 `system_refs`;登記成可 `append`/`remove` 的清單欄位;功能那側多掛、紀錄沒宣告它的舊登記只提醒;作廢、失效狀態的判斷統一去空白、不分大小寫。
- 不做:不接具名連線(`TYPED_EDGE_FIELDS`)、作廢連鎖、反向索引、圖譜視覺化等其他寫死 `plan_refs` 的地方(Enzo 裁範圍收窄)——但 `system_refs` 每一項是單一連結,照既有通則會進 `n.targets`,一般圖譜邊(孤兒、壞連結等)照樣算它,這是既有行為、本案不改;不加進 `LINK_KEYS`(它不做寫法檢查,只影響「只改連結欄位的提交算不算假同步」的判定);不提供「沒驗任何功能」的宣告寫法(上一輪的 `無 <理由>` 拿掉:那種紀錄沒有任何筆記連進來,會被 doctor 1/4 當孤兒擋推送,幾段訊息互相打架;一個功能都沒驗、正文卻有指路連結的紀錄,把指路連結寫成純文字——已知限制);不改驗收紀錄範本;不自動把舊紀錄補上 `system_refs`;不自動拿掉功能那側多掛的舊 `verified_by`;不處理「清單項沒縮排的檔案再 `append` 會寫壞 YAML」這個所有清單欄位共有的既有行為。

## 做法

1. **判單項抽成共用** `_typed_link_target(env, s)` → 合格(落點 rel)或四種不合格(不是單一連結、寫了路徑但沒有這篇、沒寫路徑而找不到、沒寫路徑而有多篇同名):從 `build_typed_index` 裡判單項的那段原樣抽出,`build_typed_index` 改呼叫它、行為不變。
2. **共用判法** `_verification_system_targets(env, rel, n)` → None(紀錄已作廢或失效,呼叫端照各自原本的規則處理)或 `(宣告了沒, 驗了哪些 Systems 的 rel 集合, 寫壞的項)`:
   - 沒有 `system_refs` 這個鍵 → 沒宣告,照舊用現行 `n.targets` 落在 `Systems/` 的。
   - 有這個鍵 → 宣告了,只看它:鍵在區塊寫法 → 整欄一項寫壞;逐項交 `_typed_link_target`,合格而落在 `Systems/` 的收進集合;不合格、或落在別的資料夾的,收進寫壞的項(附原文、原因與改法);一項合格的都沒有(空值、空清單、清單項沒縮排而解析成空)→ 記一項寫壞「system_refs 讀不出任何一項——空的,或清單項沒縮排」。不提供空宣告的理由:空宣告會讓這份紀錄沒有任何筆記連進來,doctor 1/4 照樣擋。
   - 作廢、失效的判法抽成一支 `_verification_status(env, rel)`(status 去空白、轉小寫),doctor 1/4 孤兒清單、3/4、E1、`sync-verified-by` 四處都改用它取狀態,各處要跳過哪些狀態維持原本各自的集合。
3. **doctor 3/4** 改呼叫它,比對 `verified_by` 照舊;三個標題依序:漏寫 verified_by(`warn`,算 issue,照舊)→「有 N 項 system_refs 寫壞了」(`warn`,算 issue,照 doctor 4/4 對 `plan_refs` 斷鏈自己報的先例;最多印 20 項、其餘一行「另 N 項」,改法只在標題後印一次)→「有 N 篇功能筆記多掛了沒宣告它的驗收紀錄」(`warn_soft`,不計入問題數:只看 `Systems/` 的功能筆記、只看宣告裡沒有寫壞項的紀錄;改法照那篇 `verified_by` 原本寫的那一項字面給 `lumos remove`,或叫人補進紀錄的 `system_refs`)。三個都空才印綠勾。
4. **`sync-verified-by`** 改呼叫它:有宣告的紀錄只補它列的功能;有寫壞項的紀錄,在判斷「有沒有要補的」之前就印一行指到 doctor 3/4(不然只剩寫壞項時會先印「無漏寫」就結束)。dry-run 說明句補一句「有 system_refs 的紀錄只看它」。**孤兒紀錄的推薦**(doctor 1/4 的 `--suggest` 那段):共用函式回宣告且有合格項時,只推它列的功能;回 None 或沒宣告,照原本的推薦。
5. **建紀錄** `new verification --systems A,B`:照舊先驗每個都存在、對每個加 `verified_by`(本 repo 有 42 篇計劃帶 `verified_by`,掛在計劃上是既有做法);落在 `Systems/` 的,用 `env.notes` 裡那篇的真實路徑(檔名大小寫照檔案)寫進新紀錄自己的 `system_refs`(走 `cmd_append`,照 `plan_refs` 那段);一個 Systems 都沒有就不寫這個鍵。寫 `system_refs` 失敗時提醒句另給 `lumos append <新紀錄> system_refs "[[Systems/X]]"`、rc2。建紀錄當下印的教學(`NEW_HINT` 的 verification 那段)補一句 `system_refs` 是什麼、正文指路連結什麼時候會被當成驗過。
6. **登記**:`system_refs` 只進 `LIST_KEYS`——`append`/`remove` 的白名單、多個連結塞同一行的 lint 都看它,lint 的已知欄位清單也併入它。`remove` 拿掉最後一項時鍵會一起消失(既有行為),紀錄回到「沒宣告、從正文推」;不另加提醒(那是寫入指令依賴讀取端規則,不做)。
7. **要同步的文件**:[[Systems/lumos-cli-read]](doctor 1/4 推薦、3/4、E1 取狀態)、[[Systems/lumos-cli-write]](new verification、sync-verified-by、append 清單欄位);`skills/lumos-project-notes/commands/03-寫回圖譜.md`(驗收紀錄怎麼寫)、`skills/lumos-project-notes/SKILL.md` 決策與驗證那段、`skills/lumos-project-notes/reference.md`(健康巡檢列、list 追加那列、補 verified_by 漏寫那段、plan_refs 欄位那節旁補 system_refs、其他提到「Verification 連到 Systems 即視為驗證」的段落);`scripts/lumos` 裡 `append`、`new --systems`、`sync-verified-by` 的說明字串。精簡版 `slim/` 已凍結(2026-08-20 起獨立演進),不同步。

## 條款

(測試名是預先宣告,實作時新增。)

- [S1] 當驗收紀錄寫了 `system_refs` 列 Systems/A、正文又連到 Systems/B 時,doctor 3/4 應只要求 A 反向登記,B 沒登記不算漏 [test:t_doctor_check3_system_refs_authoritative]
- [S2] 當驗收紀錄沒寫 `system_refs` 時,doctor 3/4 應照舊從正文連結推;放在 `Verification/` 子資料夾的紀錄同樣適用 [test:t_doctor_check3_system_refs_authoritative]
- [S3] 當 `system_refs` 寫成空值、空清單、或清單項沒縮排而一項都讀不出時,doctor 3/4 應列一項「讀不出任何一項」並算 issue [test:t_doctor_check3_system_refs_bad_entry]
- [S4] 當 `system_refs` 的某項不是單一連結(行尾多一句、純文字路徑、多個連結)、寫了路徑卻沒有這篇、沒寫路徑卻找不到或有多篇同名、或落在 Systems 以外,或整欄是區塊寫法時,doctor 3/4 應在「system_refs 寫壞了」標題下列出並算 issue,判法跟具名欄位索引的單項規則一致 [test:t_doctor_check3_system_refs_bad_entry]
- [S5] 當 `build_typed_index` 改用抽出的單項判法後,它的反向索引、壞連結、不明確、非連結四份清單應跟原本一樣 [test:t_typed_link_target_unchanged]
- [S6] 當功能的 `verified_by` 列了某份有宣告、沒有寫壞項的紀錄,而那份的 `system_refs` 沒列這個功能時,doctor 3/4 應只提醒、不計入問題數;掛在計劃上的、或紀錄有寫壞項時都不唸 [test:t_doctor_check3_system_refs_extra_backlink]
- [S7] 當跑 `sync-verified-by` 時,有宣告的紀錄應只補它列的功能;只剩寫壞項時應先印指到 doctor 3/4 的一行,而不是只印「無漏寫」 [test:t_sync_verified_by_system_refs]
- [S8] 當 `new verification <名> --systems Systems/A,Projects/P` 時,新紀錄的 `system_refs` 應只列 A(照檔案的大小寫),A 與 P 都應帶 `verified_by` 回指;全是非 Systems 時應不寫 `system_refs` [test:t_new_verification_writes_system_refs]
- [S9] 當 `lumos append` 對驗收紀錄加 `system_refs` 時應成功,lint 應不把它當成打錯的欄位名;`remove` 拿掉最後一項後 doctor 3/4 應回到從正文推 [test:t_system_refs_registered_field]
- [S10] 當驗收紀錄的 status 是 stale、fail、superseded(不分大小寫、前後有空白)時,doctor 3/4、E1、sync 與孤兒清單應照各自原本的規則處理,不因大小寫判成不同 [test:t_verification_status_case_insensitive]
- [S11] 當孤兒驗收紀錄有宣告且有合格項時,doctor 1/4 的推薦應只推它 `system_refs` 列的功能;紀錄是失效或沒宣告時照原本的推薦 [test:t_doctor_orphan_suggest_system_refs]
- [S12] 當 `system_refs` 寫壞超過 20 項時,doctor 3/4 應只印 20 項加一行「另 N 項」,改法只印一次 [test:t_doctor_check3_system_refs_bad_entry]

## 回退

- revert 實作提交即可。已寫進筆記的 `system_refs` 留著:revert 後 lint 會唸「不認得的欄位」(只提醒),doctor 3/4 照舊從 `n.targets` 推——`system_refs` 每項的連結本來就在 `n.targets` 裡,不會少掛;但靠它擺脫指路連結誤報的紀錄,revert 後正文指路連結又會被要求反向登記、推送被擋,要把指路連結改成純文字或回到新版。`build_typed_index` 抽出的那段一起還原(行為本來就一樣)。

## 實務隱患

- **漏網**:寫了 `system_refs` 卻漏列真的驗了的功能,反向登記就少掛一篇,doctor 不會發現——宣告優先的代價,RETIRE-IF 第二條在量。功能那側多掛的舊登記只提醒,不自動拿。
- **誤擋**:`system_refs` 寫壞會算 issue、推送前 `doctor --ci` 擋——本意,寧可擋也不默默關掉檢查;判法跟 `verified_by`、`plan_refs` 的單項規則一致,所以 `[[systems/A]]` 大小寫寫錯、`[[sub/B]]` 部分路徑、功能筆記搬資料夾後的舊路徑,在這裡跟在那兩個欄位裡一樣算壞連結。訊息逐項講原因與改法。
- **相容**:舊紀錄不寫就照舊,消費專案 `lumos update` 後行為不變;只有自己寫了欄位的紀錄換判法。作廢、失效判斷改成不分大小寫:原本寫成 `Fail`、`Stale` 的紀錄會開始被當成失效(本 repo 實查沒有這種寫法)。還沒更新的舊版 lumos 讀到 `system_refs` 不認得這個語意,照舊從 `n.targets` 推,指路連結誤報不會解——要擺脫誤報得先 `lumos update`。
- **時間**:判法跟現行一樣是逐篇讀開頭欄位,不多讀檔;嚴格判每項多一次查表。
- 已排除:金流:不碰任何付款或計費
- 已排除:對外送出:只讀寫筆記,不連網
- 已排除:不可逆:只改判法與新增欄位,revert 回得去
- 已排除:併發:寫入走既有的 cmd_append(逐檔原子、自帶鎖),不新增寫入路徑
- 守衛面:doctor 3/4 本來就算 issue、推送前會擋;這次讓它少擋指路連結、多擋寫壞的 `system_refs`。

## 實作紀錄

(還沒開始)

## 審計修正紀錄

- r2(2026-10-03,4 席同編制):28 條/blocking 5/全折,無放行、無駁回。上一輪自訂的「逐項嚴格判」跟既有零件對不上(空鍵、空清單、沒縮排解析成同一個值;大小寫、部分路徑、同名、子資料夾的比法沒定),而 `無 <理由>` 帶出新的連鎖:那份紀錄沒有筆記連進來會被 doctor 1/4 當孤兒擋推送,照 1/4 的建議掛上去 3/4 又叫人拔;`無` 的邊界也定不清。同一類(怎麼判一項)第二輪,換形狀:單項判法直接借具名欄位索引 `build_typed_index` 的既有規則(抽成共用,索引改呼叫它、行為不變),只多一條「要落在 Systems」;拿掉 `無 <理由>`(一個功能都沒驗、正文卻有指路連結的紀錄寫純文字,列已知限制);空宣告算寫壞、訊息照實講「空的或沒縮排」;作廢與失效判斷抽一支不分大小寫,四處共用;孤兒推薦回 None 照原本;多掛提醒只在紀錄沒寫壞項時唸、改法照登記原字面;寫壞訊息封頂 20 項;sync 的指路句放在提早結束之前;`--systems` 照檔案大小寫寫;`remove` 刪光不另加提醒;精簡版已凍結不同步、補 reference.md 漏列的段落。例:`system_refs: [[systems/A]]`(大小寫錯)→ 修前規則沒定、修後跟 verified_by 一樣判壞連結;`system_refs` 只寫 `無 純調研` → 修前 3/4 放行但 1/4 當孤兒擋、修後不提供這寫法。條款重編 S1–S12。席報告同目錄。
- r1(2026-10-03,4 席:正確性-opus、邊界-sonnet、整合-sonnet、架構對齊-sonnet):20 條/blocking 8/全折,無放行、無駁回。三席獨立撞到同一個根:「有這個鍵就只看它」讓寫壞的形狀(空值、全形括號、區塊寫法、純量多連結、純文字路徑、連結後多一句)鍵存在、解出來是空,等於默默關掉檢查;`remove` 拿掉最後一項會連鍵刪掉,空清單用指令到不了。換形狀:每項嚴格判、寫壞的任何形狀都報 issue(照 doctor 4/4 對 plan_refs 自己報斷鏈的先例);「沒驗任何功能」改寫 `無 <理由>`(照 [被取代:無 <理由>] 先例);路徑式連結要跟解析結果一致(防檔名救援);`--systems` 只把 Systems 寫進 system_refs(計劃照舊掛 verified_by);status 判斷不分大小寫;功能那側多掛的舊登記只提醒;孤兒推薦也改用共用判法;同步清單訂正(精簡版說明書其實有 plan_refs 那節);回退與舊版相容講清楚。鏡像核對再補:多掛舊登記只算 Systems、撤除條件加寫壞率、空清單算寫壞、`remove` 刪光印提醒、裸檔名規則、子資料夾、REVISIT 看 rtb 的工具版本、建檔提示寫 `無`。例:`system_refs: ""` 加正文連到 Systems/A → 修前不要求任何反向登記也不報、修後列成寫壞;`system_refs: [[Projects/A]]` 而只有 Systems/A → 修前被救成 A、修後寫壞。條款擴成 S1–S11。席報告在 `governance/review-reports/驗收紀錄寫明驗了哪些功能/`。
