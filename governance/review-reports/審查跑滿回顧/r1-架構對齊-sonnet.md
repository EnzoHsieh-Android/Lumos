severity: major

審查範圍:凍結快照 r1-snapshot.md 對照 /Users/enzo/harness/lumos-toolchain-cap-retro 的 scripts/lumos。四問逐問答在最後;不對齊逐條列在前。

### F1 「跑滿/輪數/上限」會有第三份算法,既有共用的 `_cap_hint_scope` 沒被用
severity: major
blocking: 是 — 引入第二種做法:同功能已有共用 helper,計劃卻說「同 cmd_loop_next」,會再抄一份。
引句:「輪數與上限的算法同 `cmd_loop_next`(`rounds_count`、`_loop_anchor_tier`、`_TIER_PARAMS`)」
佐證:
- `rounds_count` 只是 `cmd_loop_next` 裡的區域變數,不是可呼叫的函式。file: `scripts/lumos:12943`
- 專案裡「是否到上限」已有共用實作 `_cap_hint` / `_cap_hint_scope`,loop next 與處置閘共用。file: `scripts/lumos:8826-8862`
- `_cap_hint_scope` 把循序單審與 light 排除。計劃要把它們算進去(筆數、legacy 上限 6)。兩邊口徑不同,又各算一份,日後必然漂移。
- 建議:抽一支共用函式(輪數、分級、上限、是否跑滿),讓 `_cap_hint`、`cmd_loop_next`、retro 三方共用;或明講為什麼不能共用。
- 另外計劃寫「直接呼叫 `_cap_hint_round`」,這點與既有一致。file: `scripts/lumos:8865`

### F2 「跳過」留痕方式是第二套:寫在回顧檔裡、不進治理帳
severity: major
blocking: 是 — 另一套「跳過」留痕方式;既有的跳過都會落治理帳事件。
引句:「不另開旗標、不另寫治理帳事件。」
佐證:
- 既有跳過一律落治理帳事件:`_gate_event_or_warn(..., "skipped-env", ...)`,並帶 token 與 head_sha。file: `scripts/lumos:12645-12648`
- 其他閘也一樣。file: `scripts/lumos:27701`、`scripts/lumos:30089`、`scripts/lumos:31322`、`scripts/lumos:31937`
- `code-loop pass|skip` 也走帳。file: `scripts/lumos:10292`
- 計劃自己被推翻的 d1 原本要「留 --skip-retro --note 出口並記治理帳」。d3 改成自報的 `skipped: {reason, by}`,只存在回顧檔,可事後改、不進跨迴圈帳。
- 計劃 RETIRE-IF ③ 要靠「跳過次數」判斷機制要不要撤,但這個次數只有 `loop retro --stats` 掃檔才算得出,`gov --stats` 看不到。
- 建議:跳過沿用 `_gate_event_or_warn` 寫一筆事件。回顧檔的 skipped 欄可留,但要以事件為準。

### F3 回顧檔「指紋照收貨紀錄」其實沒有可比對的對象,是另一種(較弱的)指紋做法
severity: major
blocking: 是 — 另一套指紋留痕;既有做法是「記帳時把 sha256 寫進帳,讀側重算比對」。
引句:「回顧檔的 sha256 跟收貨紀錄一樣要能重算:問閘時把路徑與指紋印出;凍結時寫進判定閉包。」
佐證:
- 收貨紀錄的指紋是 `canary record` 時寫進帳列 `intake_path` / `intake_sha256`,讀側用 `_prov_check` 比對,不符就 FAIL。file: `scripts/lumos:22432-22443`;file: `scripts/lumos:22846-22862`
- 回顧檔在迴圈之後才寫,計劃又說「只讀帳本與卷證檔,不寫任何帳」。所以閘裡沒有「帳面指紋」可比,印出的 sha 只是當下自算,事後改檔偵測不到。
- 只有凍結閉包有記,而凍結本身受 F4 影響。
- 措辭「跟收貨紀錄一樣」與實作不符。
- 建議:要嘛承認這步不做防竄改(改措辭),要嘛寫一筆帳列帶 `retro_path` / `retro_sha256`,走 `_prov_check`。

### F4 由編號找資料夾:另開「由判定輪 report_path 推」,既有一律用 `review-reports/<編號>`
severity: major
blocking: 是 — 另一套由編號找資料夾的方法,而且沒有共用函式。
引句:「不用審查編號推資料夾:帳上 415 個編號有 108 個沒有同名資料夾」
佐證:
- 既有都是 `governance/review-reports/<loop_id>`。file: `scripts/lumos:8597`、`scripts/lumos:11930`、`scripts/lumos:12308`、`scripts/lumos:12314`、`scripts/lumos:22913`、`scripts/lumos:22942`
- 計劃的實測理由站得住(`-v2`、`-std` 共用前一版資料夾)。但它代表既有那 6 處也有同樣缺口,而計劃只在自己這裡換法。
- 結果:同一個迴圈,fix-check 的 `rN-fix.json` 與 retro 的 `cap-retro.json` 可能指到不同資料夾。
- ⚠ 交編排者:這條是否算 major,取決於要不要把「由帳列找卷證資料夾」抽成共用函式。若計劃明講「只此一處、不動既有」並記 Issue,可降 minor。

### F5 跨迴圈統計掛在 `--stats` 旗標上,與既有 `X-stats` 子指令形狀不同
severity: minor
blocking: 否 — 命名不一致,結構(唯讀、掃帳、`--json`)一致。
引句:「`lumos loop retro --stats [--json]`:掃帳上所有跑滿迴圈的回顧檔」
佐證:
- 既有跨迴圈統計是獨立子指令:`escape-stats`(無位置參數,只有 `--json`)與 `canary-stats`。file: `scripts/lumos:46165-46171`
- 另有 `gov --stats`。file: `scripts/lumos:8289`
- 單一迴圈操作用旗標是對的:`fix-check` 的 `--record-template`。file: `scripts/lumos:46119-46134`
- 建議:改成 `loop retro-stats`,或確認 `<編號>` 在 `--stats` 時可省略並寫進 argparse 規格。

### F6 欄位命名 `v` 與專案既有的 `version` 不同
severity: minor
blocking: 否 — 欄位名不一致,不影響結構。
引句:「`v`:1。」
佐證:既有 JSON 檔都叫 `"version": 1`。file: `scripts/lumos:31208`、`scripts/lumos:31897`、`scripts/lumos:23790`、`scripts/lumos:38935`。另一個差異:既有 `--record-template` 把骨架印標準輸出、提示印標準錯誤(file: `scripts/lumos:12412-12430`),計劃只說「印骨架 JSON 與它該放的路徑」,沒講分流。

### 四問答覆
1. 分層與依賴方向:新增處置閘第八步、`cmd_loop_retro`、doctor 提醒段,放的層與鄰居一致。
   - 步驟簽名與回傳值("fail"/"ok"/"skip"/"abort")、skip 條件(回放以問閘當下為準、上線日常數不回溯)都照 `_disposal_landing_step`。file: `scripts/lumos:22646-22694`
   - 步驟呼叫與加進 `fails`、橫幅 `_extra` 的接法,見 file: `scripts/lumos:22972-22999`
   - doctor 提醒段用 `warn_soft` 不計 issues,與既有一致。file: `scripts/lumos:1669`
   - 沒有跨層直呼。重複實作的問題見 F1、F4。
2. 命名與錯誤處理:
   - 回傳碼 0/1/2 與 `--template` 旗標形狀跟 `fix-check` 一致。file: `scripts/lumos:12630-12648`
   - 擋下訊息「擋下:…」沿用。
   - `cap-retro.json` 是迴圈層級的檔,與 `rN-fix.json` 的輪級命名不衝突。
   - 不一致處:F5(stats 形狀)、F6(`v`)。計劃沒提迴圈編號含 `/` `..` 的檢查(fix-check 有 `_FIX_ID_BAD_RE`)。因為路徑從 `report_path` 推,風險低,但值得寫一句。
3. 第二種做法:F1(第三份輪數/上限算法)、F2(跳過留痕)、F3(指紋留痕)、F4(找資料夾)。
   - 回顧歸族不是機械比對,沒有與既有重複的功能。
   - `--stats` 掃檔與 `escape-stats` 掃帳是不同資料來源,不算第二套統計。
4. 落點:`Systems/loop-convergence-recording` 現在 25864 bytes,about_code 只列 `scripts/lumos`,摘要已累積 20 多行 KEY/WHY。
   - 有先例:上限提示、逃逸帳、修正關卡都寫進這篇,所以 lands_in 與既有慣例一致,不算不對齊。
   - 它已經是「一篇包全部」(計劃自己引用過這個教訓,見 `Systems/design-loop` 第六步「落點」那行,43705 bytes)。
   - ⚠ 交編排者:建議列為 minor 的取捨。要嘛照先例寫進這篇,要嘛新開 `Systems/loop-retro`(`lumos new system loop-retro --code scripts/lumos --responsibility "…"`)並在計劃 lands_in 寫兩篇。
   - 我判斷新開比較符合「每支檔有家、節點別長成一篇」的方向,但這是取捨,未列入不對齊條目。

不對齊共 6 條,其中 major 4 條
總結:最嚴重 major,blocking 4 條
