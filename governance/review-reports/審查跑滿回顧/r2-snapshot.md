---
type: project
status: doing
created: 2026-10-05
updated: 2026-10-05
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/loop-convergence-recording
  - Systems/loop-retro
decisions:
  - content: 跑滿上限沒有合格回顧時,在凍結判定前擋下;留 --skip-retro --note 出口並記治理帳。考慮過只提醒(問閘時印、週報列),但專案慣例偏好機械擋,只提醒的規則容易被跳過。代價:跑滿的迴圈收尾多一步。
    id: d1
    decided: 2026-10-05
    valid: false
    superseded_by: Projects/審查跑滿回顧_計劃.md#d3
    ended: 2026-10-05
  - content: 回顧由沒參與該迴圈的乾淨代理起草歸族,編排者補怎麼避免與行動項。考慮過編排者自己寫,省一個代理額度,但編排者容易替自己的修法找理由、把責任推給審查員。代價:每次跑滿多派一個代理。
    id: d2
    decided: 2026-10-05
    valid: true
  - content: 跑滿上限的迴圈沒有合格回顧時,處置閘判不過(第八步「跑滿回顧」,跟收貨紀錄一樣算留痕的一部分);凍結時處置閘會在內部重跑,所以凍結也一併擋;回放以凍結當下為準不重判。跳過寫進回顧檔本身(跳過理由欄),不另開旗標。考慮過:①擋在凍結前(前掃查出凍結是手冊步驟、程式不強制,沒凍的迴圈會整個繞過);②只提醒。代價:處置閘多一個條件,跑滿的迴圈要多一步才過得了閘。
    id: d3
    decided: 2026-10-05
    valid: false
    superseded_by: Projects/審查跑滿回顧_計劃.md#d5
    ended: 2026-10-05
  - content: 回顧只涵蓋「跑滿未過」:多席(帶輪次)迴圈到分級上限還沒過閘——治理帳有這個編號的 cap-reached 事件,或輪數已超過上限。剛好在最後一輪過閘的不算;light 與循序單審不算(light 上限只有兩輪,也不經過處置帳)。考慮過:①輪數達上限都算(近期約六成迴圈,多數是第三輪剛好過閘,每三個迴圈就有兩個要多派代理);②都算但過閘的可由編排者自寫。Enzo 2026-10-05 裁只算到上限還沒過的。代價:看不到「勉強在最後一輪收斂」這種最常見情況。
    id: d4
    decided: 2026-10-05
    valid: true
  - content: 擋點放在跑滿未過之後「要繼續」的三個時刻:記超過上限那一輪的帳時(破例再一輪)、超過上限後問處置閘時(第八步)、loop next 判到 cap-reached 時印回顧指令;回顧與跳過都用 lumos loop retro 指令寫進治理帳(帶檔案指紋),閘上比對指紋。人裁直接放行或整份重寫的路徑擋不到,由 doctor 列出。考慮過:①擋在凍結前(凍結是手冊步驟、程式不強制,且凍結本來就容許把 FAIL 判定存起來);②處置閘一律加第八步(跑滿未過的迴圈閘本來就 FAIL,加了只是多一個原因)。代價:人裁放行那條路只有提醒。
    id: d5
    decided: 2026-10-05
    valid: true
---
# 審查跑滿回顧_計劃

PRIOR-ART: 事後回顧沿用 Google SRE 無責回顧的做法——固定欄位、寫根因與行動項、行動項要有落點,跨事件彙整靠固定分類而不是讀散文(《Site Reliability Engineering》〈Postmortem Culture〉);「無責」在本案的意思是歸族只描述問題怎麼來,不記哪一席或哪個編排者的錯。本 repo 既有 [[Projects/審查跑滿上限提示_計劃]]:跑滿時印每輪折入數與提示,只印不存;它當時刻意拿掉「同類重複」「修補引起」兩個機械訊號,理由是機器比對不準、新旗標靠編排者自律。本案不重做機械判斷,改由沒參與審查的代理讀卷證歸族,並在跑滿未過之後要繼續時擋。機制層全部沿用既有:跑滿判定抽出 `_cap_hint_scope` 與 `_cap_hint` 已有的輪數、分級、上限算法成共用函式(三方共用,不另寫);每輪折入與最高嚴重度呼叫 `_cap_hint_round`;卷證資料夾照既有慣例 `governance/review-reports/<編號>/`;治理帳寫入用 `_loop_gov_mark`,新事件種類登記進 `LOOP_NOT_CLOSE_EVENTS`;報告條號辨識抽出 `_report_findings_missing_severity` 裡既有那條規則成共用函式;處置閘新一步照「落點」那步的接法;跨迴圈統計照 `escape-stats` 做成獨立子指令;doctor 提醒段用既有 `warn_soft`。
RETIRE-IF: ①上線三個月後,`retro-stats` 列出的行動項裡,拿不出任何一條對應提交(規則、工具、派工詞或手冊)——回顧變成填表;②上線三個月內跳過次數多過寫了回顧的次數;③三個月內零次跑滿未過。

## 一句話

多席審查迴圈跑到分級上限還沒過閘(要人裁)時,要先留一份固定格式的「跑滿回顧」才能繼續:每輪的問題歸成哪幾族、哪一族跨輪重複、當初怎樣能少跑一輪、下次要改哪條規則或工具;回顧與跳過都記進治理帳;另有指令把所有回顧按族別彙整,給之後調整審查方式用。

## 名詞

- **卷證資料夾**:一個審查迴圈存席報告、派工單、凍結快照、收貨紀錄的資料夾,`governance/review-reports/<編號>/`。
- **席報告**:一位審查員交回的報告,帳上那一列的 `report_path`。
- **收貨紀錄**:編排者每輪寫的 `rN-intake.md`,含重現表。
- **跑滿未過**:多席(帳列都帶輪次)迴圈,輪數到了分級上限而沒過閘。機械判法(兩者任一):①治理帳有這個編號的 `cap-reached` 事件(`loop next` 在到上限、處置閘沒過時寫的那筆);②帳上輪數已超過上限(到上限沒過才會破例再開一輪)。剛好在最後一輪過閘的不算(Enzo 2026-10-05 裁,見決策 d4)。
- **合格回顧**:回顧檔存在、`lumos loop retro <編號> --check` 回 0,而且治理帳最新一筆 `cap-retro` 事件記的指紋等於檔案現在的指紋;或治理帳有一筆 `cap-retro-skipped` 事件。

## 為什麼要做

- 跑滿這件事已經有記(治理帳的 cap-reached、`gov --stats` 的人裁放行率),跑滿時也會印每輪折入數,但**為什麼跑滿、下次怎麼避免**只寫在各計劃審計修正紀錄的散文裡,沒有欄位,沒辦法跨迴圈統計。
- 實例:代碼審 `code-lumos事件帳`(2026-10-05,卷證在分支 mod-event-ledger 上那個編號的卷證資料夾,本工作樹開分支時還沒合進主線)三輪折入 28/26/19 條,第三輪仍有 major,Enzo 裁全修不開第四輪;後兩輪的 major 都是「同一族沒一次掃完」——修了一個出口,下一輪從另一個出口冒出來。類似的軌跡也寫在 [[Projects/新增告警閘_計劃]] 前段(第二輪抓到修正本身引入的反向錯),但沒有人說得出這種模式總共發生幾次。

## 適用範圍

- **觸發**:跑滿未過(見〈名詞〉)。輪數、分級、上限一律用新抽出的共用函式,跟 `_cap_hint` 同一套:只看帳列都帶輪次的迴圈;沒定錨照 standard;上限查 `_TIER_PARAMS`;規格閘留痕不算。
- **不涵蓋**:light(上限兩輪,也不記處置帳)、代碼審循序單審(不帶輪次)、剛好在最後一輪過閘的。
- **只管上線之後**:上線日 = 這份計劃實作合進主線的那個時刻,寫成程式常數(精確到秒);判斷看迴圈首筆帳的時間,首筆早於上線時刻的不擋也不唸。
- 設計審與代碼審都算。

## 做法

### 一、回顧檔

- 位置:`governance/review-reports/<編號>/cap-retro.json`(沒有這個資料夾就建;一個編號一個資料夾,`-v2`、`-std` 這類新編號各自一份,不會互相覆蓋)。編號含 `/`、`\`、`..` 一律拒絕(照 `cmd_loop_replay` 既有的編號檢查)。
- 欄位(第 1 版):
  - `version`:1。
  - `loop`:審查編號,要等於指令給的編號。
  - `rounds`:輪次清單,要跟帳上這個編號的輪次完全一致(順序照帳上第一次出現的順序)。跑滿後又破例多開一輪,舊回顧就不再合格,要更新後重新記(見〈二〉)。
  - `drafted_by`:起草的代理名稱;`completed_by`:補完的人或編排者。兩者不得相同,`drafted_by` 也不得是這個編號帳上任何一列的 `auditor`(起草者不得是這個迴圈的審查席)。
  - `families`:至少一項,每項 `{family, rounds, evidence, note}`:
    - `family` 從固定清單挑:`same-family-unswept`(同族沒一次掃完)、`fix-induced`(修補本身帶出新問題)、`scope-too-big`(改動範圍太大)、`spec-unclear`(規格或設計寫不清)、`seat-noise`(審查員誤判或判準錯)、`bar-moved`(判準或規則中途改變)、`hostile-surface`(本來就多邊界、縮不掉的領域)、`other`(要附 `note` 至少 10 字)。
    - `rounds`:這族出現在哪幾輪,要是帳上這個編號有的輪次。
    - `evidence`:至少一條。每條是一份席報告的路徑(repo 相對路徑),可以加 `#F<n>` 指到條號。路徑要是這個編號帳上某一列的 `report_path`(不接受其他檔);加了條號時,用共用的條號辨識函式在那份報告裡找得到 `F<n>` 那一段(跟收貨數條數同一條規則:圍欄裡的不算、`F1.1` 子標題不算)。報告本身沒有 `F<n>` 標題的舊格式,只寫路徑不加條號即可。
  - `why_cap`:為什麼跑滿,至少 20 字。
  - `avoid`:當初怎樣做能少跑一輪,至少 20 字。
  - `changes`:至少一項,每項 `{target, ref, change}`;`target` 從 `rule`(規則或規格)、`tool`(lumos 程式)、`dispatch`(派工詞)、`skill`(手冊)、`none` 挑;`none` 要附 `reason` 至少 10 字,其他要有 `ref`(改哪裡)與 `change`(改什麼,至少 10 字)。
- 壞檔:讀不到、不是 UTF-8、不是合法 JSON、根不是物件、欄位型別不對、檔案超過 256KB,一律判不合格並印原因,不丟錯誤堆疊。

### 二、指令

- `lumos loop retro <編號> --template`:骨架 JSON 印到標準輸出(`version`、`loop`、`rounds` 填好,另附唯讀的 `context`:每輪折入數與最高嚴重度、帳上這個編號的所有 `report_path` 與 `auditor`);該放的路徑與下一步指令印到標準錯誤(照 `fix-check --record-template` 的分流)。`context` 取不到(帳上欄位壞)時印 null,不丟錯誤;驗證不看 `context`。
- `lumos loop retro <編號> --check`:驗回顧檔;合格回 0,不合格回 1 並逐條印哪裡不合格,用法錯回 2。
- `lumos loop retro <編號> --record`:先跑 `--check`,合格才在治理帳寫一筆 `kind=cap-retro`(nodes 帶編號,note 帶檔案路徑與 sha256);不合格回 1、不寫帳。
- `lumos loop retro <編號> --skip --note "<理由>"`:理由至少 10 字,在治理帳寫一筆 `kind=cap-retro-skipped`(note 帶理由);不需要回顧檔。
- `lumos loop retro-stats [--json]`(獨立子指令,照 `escape-stats`):讀治理帳的 `cap-retro` 與 `cap-retro-skipped` 事件,印:跑滿未過的迴圈總數(上線後)、其中記了回顧幾個、跳過幾個、兩者都沒有的清單;每個族別出現在幾個迴圈與名單,分級別(standard、high)分開算;所有行動項逐條列出(target、ref、change、所屬迴圈),給回頭看時對照有沒有對應提交。每個迴圈各自讀檔,壞檔只標那一個,不中斷整份統計。
- 新事件種類 `cap-retro`、`cap-retro-skipped` 登記進 `LOOP_NOT_CLOSE_EVENTS`(寫回顧不是關門)。

### 三、擋點

1. **破例再一輪**:`canary record` 要記的那一輪會讓帶輪次的迴圈輪數超過上限、而且這個迴圈還沒有合格回顧 → 回 2、不寫帳,三段式印原因與 `--template` 指令。同一輪的第二席以後(輪次已經在帳上)不再擋。
2. **處置閘第八步「跑滿回顧」**:輪數已超過上限的迴圈,`loop status --disposal` 要求合格回顧,否則這一步 ✗、處置閘 FAIL 並印指令;不適用印 —(附原因:沒跑滿、首筆早於上線、light 或循序)。照「落點」那步的接法:凍結的第二趟與回放(帶 `spec_sha_override`)印 — 不重判,所以凍結與回放的行為與既有一致(凍結本來就容許存 FAIL 判定),回顧檔也不進凍結閉包(它可能在凍結後補內容,進閉包會讓回放假紅)。
3. **loop next 判到 cap-reached**:原本的「停下來交給人裁」後面多印一行:人裁要繼續(破例再一輪、或過閘)之前要先記回顧,附 `--template` 指令;已經有合格回顧就印「回顧已記」。
- 擋不到的路:人裁直接放行(代碼審 `code-loop pass` 本來就不回頭驗處置閘)、或整份重寫開新編號。這兩條由 doctor 列出。

### 四、收工體檢提醒

- `lumos doctor` 多一段:上線之後跑滿未過、但治理帳沒有 `cap-retro` 也沒有 `cap-retro-skipped` 事件的迴圈,逐個列出並附 `--template` 指令。只提醒,不算進 issues;每個迴圈各自判,一個帳列壞了只略過那一個。

### 五、誰來寫

- 跑滿未過時,編排者派一個**沒參與這個迴圈的乾淨代理**起草:給它 `--template` 的骨架、各輪席報告與收貨紀錄,要它歸族並附證據;不給它編排者的看法。編排者再補 `avoid` 與 `changes`,填 `completed_by`,跑 `--record`。理由:編排者容易替自己的修法找理由、把責任推給審查員(Enzo 2026-10-05 裁,決策 d2)。
- 起草派工詞寫進 `skills/lumos-design-loop/templates.md`(代碼審手冊本來就指向這份範本)。「到頂沒過 → 停」那句在五處:`skills/lumos-design-loop/SKILL.md`、`skills/lumos-design-loop/reference.md`(兩處)、`skills/lumos-code-loop/SKILL.md`、`skills/lumos-code-loop/reference.md`,另有指令速查 `skills/lumos-project-notes/commands/05-設計審查迴圈.md` 的「跑滿上限還沒過 → 停,攤給人裁」;每處後面都接「繼續之前先寫跑滿回顧」與指令。

## 條款

- [S1] 若帶輪次的迴圈要記的新一輪會讓輪數超過分級上限、而且沒有合格回顧,則 `canary record` 應回 2 且不寫帳;有合格回顧或已記跳過時照常寫帳;同一輪已在帳上的後續席不擋 [test:t_cap_retro_record_blocks_extra_round]
- [S2] 當輪數已超過上限的迴圈問處置閘、而且沒有合格回顧,處置閘第八步應 ✗、整體 FAIL 並印 `--template` 指令,其餘七步的判定不變 [test:t_cap_retro_gate_fails_past_cap]
- [S3] 若回顧檔合格且治理帳最新一筆 `cap-retro` 的指紋等於檔案現在的指紋,則第八步應 ✓;指紋不符(記帳後被改)應 ✗ 並叫人重新 `--record` [test:t_cap_retro_gate_fingerprint]
- [S4] 若迴圈沒跑滿、首筆帳早於上線時刻、是 light 或循序單審,或處置閘在凍結第二趟或回放中被呼叫,則第八步應印 — 並附原因,不讀回顧檔 [test:t_cap_retro_out_of_scope_not_checked]
- [S5] 當 `loop next` 判到 cap-reached,輸出應多一行回顧指令(已有合格回顧則印已記),階段名與退出碼不變 [test:t_cap_retro_loop_next_hint]
- [S6] 當 `--check` 驗回顧檔,`family` 不在固定清單、`rounds` 跟帳上不一致、`evidence` 不是這個編號帳上的報告或條號找不到、`drafted_by` 等於 `completed_by` 或是這個編號的審查席、`other` 沒附說明、`changes` 的 `none` 沒附理由、欄位型別不對,任一項都應判不合格並逐條列出 [test:t_cap_retro_check_rejects_each_defect]
- [S7] 若回顧檔讀不到、不是 UTF-8、不是合法 JSON、根不是物件或超過 256KB,則 `--check` 應回 1 並印原因,不丟錯誤堆疊;`retro-stats` 與 doctor 只標那一個迴圈、不中斷 [test:t_cap_retro_bad_file_no_traceback]
- [S8] 當 `--record` 執行,合格時應在治理帳寫一筆帶路徑與指紋的 `cap-retro`,不合格回 1 不寫帳;`--skip --note` 理由至少 10 字時寫一筆 `cap-retro-skipped`,不足回 2 [test:t_cap_retro_record_and_skip_write_gov_log]
- [S9] 當 `--template` 執行,骨架應印到標準輸出、路徑與下一步印到標準錯誤,`context` 帳上欄位壞時印 null 不丟錯誤 [test:t_cap_retro_template_prefills_rounds]
- [S10] 當 `retro-stats` 執行,應印跑滿未過的迴圈總數、記了回顧與跳過的個數、兩者都沒有的清單、各族別出現的迴圈數與名單(分級別)、所有行動項 [test:t_cap_retro_stats_aggregates_families]
- [S11] 當 `doctor` 執行,應列出上線後跑滿未過、卻沒有回顧也沒有跳過事件的迴圈,且不計入 issues [test:t_cap_retro_doctor_lists_missing]
- [S12] 當新的跑滿判定共用函式取代原本的算法,`_cap_hint` 的判定與輸出應與原本相同 [test:t_cap_retro_shared_cap_state_keeps_cap_hint]
- [S13] 當新的條號辨識共用函式取代原本的寫法,`_report_findings_missing_severity` 的判定應與原本相同 [test:t_cap_retro_shared_finding_heads_keeps_check]
- [S14] 當新增 `cap-retro`、`cap-retro-skipped` 兩種事件,`t_loop_close_kinds_classified` 應維持綠,且這兩種事件不得讓迴圈被當成已關門 [test:t_loop_close_kinds_classified]
- [S15] 當手冊與範本檔更新,五處到頂句與指令速查都應接到回顧指令,範本檔應有起草派工詞且不含編排者結論的欄位 [manual:讀五處到頂句、指令速查與範本檔,確認指令與派工詞都在]

## 回退

- 拿掉 `canary record` 的檢查、處置閘第八步與 loop next 多印的那行,即回到現狀;治理帳的 `cap-retro`、`cap-retro-skipped` 事件與回顧檔是新增的資料,留著不影響任何既有判定(兩種事件登記為不算關門)。`retro-stats` 與 doctor 段是唯讀的,拔掉呼叫即可。兩支共用函式是重構,行為由 S12、S13 釘住,不用回退。

## 實務隱患

- 併發:兩支 `--record` 同時對同一編號寫治理帳,各自 append 一行,以最新一筆為準;治理帳寫入照 `_loop_gov_mark` 既有做法(失敗不擋)。`canary record` 的檢查只讀帳。
- 效能:處置閘第八步只讀一份回顧檔(上限 256KB)、被引用的幾份報告、治理帳一次;`retro-stats` 與 doctor 掃治理帳一次加上跑滿未過的迴圈各一份小檔。
- 舊迴圈:首筆早於上線時刻的不回溯,避免一上線舊迴圈問閘或補帳時被擋。
- 已排除:金流:只讀寫本機檔案,不碰付款
- 已排除:對外送出:不呼叫任何外部服務
- 已排除:不可逆:新增的擋點只讓破例再一輪與過閘晚一步,有跳過出口;新事件與回顧檔都是新增資料
- 守衛面:`canary record` 與處置閘各多一個擋下條件,都有 `--skip --note` 出口且會留在治理帳被統計;S1 到 S4 綁測試。

## 誠實界線

- 歸族靠起草代理讀卷證判斷,不是機器算的;同一個迴圈換一個代理可能歸成不同的族。`evidence` 的檢查只保證指到這個迴圈自己的報告、條號存在,不保證歸族正確。
REVISIT:2026-12-05 抽三份已寫的回顧給另一個乾淨代理重新歸族,看族別一致的比例;太低就收斂族別定義
- `drafted_by` 只能檢查「不是這個迴圈的審查席、不等於 completed_by」,檢查不了起草者真的沒看過編排者的看法。
- 人裁直接放行、或整份重寫開新編號的迴圈只會被 doctor 列出,不會被擋。
REVISIT:2026-12-05 看 doctor 與 retro-stats 列出的「跑滿未過、沒回顧也沒跳過」有幾個;多的話把檢查接進推送前的代碼審檢查
- 行動項有沒有落地只能人工對照(`retro-stats` 逐條列出,沒有機械比對提交)。
- 只管上線之後;事件帳那次(上線前)的回顧當第一份樣本手寫,用來驗證欄位夠不夠用。

## 審計修正紀錄

- r1(2026-10-05,4 席:正確性、邊界、整合、架構對齊;外家否決席依 Enzo 指示不派):28 條/blocking 14/方向沒被推翻,但擋點、範圍、檔案位置、留痕方式都要重做。席報告在 `governance/review-reports/審查跑滿回顧/`,收貨紀錄 `r1-intake.md`。
  - Enzo 裁:範圍改成「只算到上限還沒過的」(決策 d4)。
  - 折入:凍結本來就容許存 FAIL 判定、回放會因閉包指紋假紅(四席獨立指出)→ 擋點改成破例再一輪、超過上限後問閘、loop next 提示三處,凍結與回放照落點慣例不重判、回顧檔不進閉包(決策 d5);跑滿判定改用抽出的共用函式(架構);跳過與回顧都用指令記進治理帳、閘上比對指紋(架構、邊界、正確性);回顧檔放在 `governance/review-reports/<編號>/`,各編號一份(四席);證據改成這個編號帳上的報告路徑、條號選填、沿用既有條號辨識(邊界、正確性);light 與循序單審排除(三席);壞檔判不合格不丟堆疊、`--template` 不炸(邊界、正確性);起草者不得是本迴圈審查席(邊界、正確性、整合);統計改獨立子指令、`version` 欄名、骨架與提示分流(架構);手冊到頂句改列五處(整合、邊界);上線時刻精確到秒(邊界);退場條件改成量得到的(整合、正確性、邊界);落點另開 `Systems/loop-retro`(架構)。
