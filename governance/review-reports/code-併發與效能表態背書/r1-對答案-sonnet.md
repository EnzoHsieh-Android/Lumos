severity: minor

〈做法〉各點與 S1~S16 全部已實作,只有幾處措辭或精度縮水(皆 minor)。

## 已實作
[S1] 七題標 needs_backing(fe-race 按〈實作紀錄〉拿掉);[S2] --covers 逐個驗 needs_backing、擋空、去重、列可用 id;[S3] same_rest 成立取代 covers、印前後、check() 讀回;--note 預設改 None;[S4] `_kill_recipe_key` 簽名 (node, invariant, file, old)、kill-add 與 kill 共用;[S5] marks 逐平台蓋章、head_sha 先取完整 sha 再建沙盒、建沙盒前出錯為空字串、commit 仍短碼;[S6] weak 三來源;[S7] 補換行與容錯讀;[S8] --json 純度;[S9] 算背書七步與原因字串;[S10] 20 秒預算;[S11] 先全拿掉 backing、n/a;[S12] try 只包算背書、例外全記 none、寫帳失敗仍 rc2;[S13] 單行提醒進 warnings;[S14] 跟著 gate 提早結束;[S15] 派工鏡頭註記在截斷之後、表頭與說明已改;[S16] gov 分母與容錯讀取;[S17] 除下列兩項外已實作。

## 縮水

**C1**
severity: minor
blocking: 否
Systems/棧別提問表態閘 的正文「刻意的天花板」段與 KEY 行 patch 裡沒看到改動;patch 只在 summary 加兩條 WHY 與一條 REVISIT。⚠ 請編排者確認工作樹正文。
引句:「`Systems/棧別提問表態閘` 的現況行、KEY 行與正文「刻意的天花板」段(加上本案的 WHY)」
file: `/tmp/cpe/code-r1-snapshot.patch:61`

**C2**
severity: minor
blocking: 否
S17 的兩張說明圖不在 patch 裡(工作樹已有新字樣,是 patch 範圍問題);「改產生器」是否另有產生器檔未查到,⚠。
引句:「說明圖 `assets/stack-gate-zh.svg`、`assets/review-layers-zh.svg` 裡「工具只驗證據存不存在、不驗答案對不對」的字樣(改產生器再重產)」
file: `/tmp/cpe/code-r1-snapshot.patch:1`

**C3**
severity: minor
blocking: 否
步驟 7 的 head_sha:spec 寫「那一組」,實作跨所有涵蓋組取 ts 最新一筆;多組時會不同。⚠ spec 歧義。
引句:「"head_sha":"<那一組有效紀錄中最新一筆的 head_sha 前 8 碼>"」
file: `scripts/lumos:37405`

**C4**
severity: minor
blocking: 否
covers 混型清單實作只濾掉非字串元素;spec 寫整個當空清單。
引句:「`covers` 不是字串清單就當空清單」
file: `scripts/lumos:37430`

**C5**
severity: minor
blocking: 否
b is None 時派工鏡頭印「記錄沒有背書欄位」;spec 字面缺欄位也算形狀不對。⚠
引句:「`backing` 形狀不對一律印「背書:沒有(記錄形狀不對)」」
file: `/tmp/cpe/code-r1-snapshot.patch:682`

## 多做

**C6**
severity: minor
blocking: 否
預設呼叫者在 git diff 非 0 時,原本回「之後動了代碼(非純簿記增量)」,現在回「git diff 出錯」;ok 仍 False,why 文字變了,是預設行為的微變。
引句:「`_codeloop_record_valid` 加一個選填參數讓它多回一個「判不了」旗標(git 逾時或 git 出錯),預設行為不變」
file: `/tmp/cpe/code-r1-snapshot.patch:769`

逐點確認無偏離:不新增事件種類、不動 `_KNOWN_GATES`、kill-log commit 語意不變、沒有新增開關、推送前不讀 kill-log 也不跑 git、移除 covers 只能手改。

縮水+未實作共 5 條
