severity: major

# r3 回滾席(sonnet)——治理帳例行紀錄分流

白話:第 2 輪「舊使用紀錄帳改寫新檔、不停止追蹤」這個修法是對的,我在 /tmp 用真 git 驗過,別台機器 pull 不會刪檔也不會中止。但「還原提交後本機帳仍被忽略」這句對本 repo 是假的:忽略規則跟著提交一起被還原,兩本本機帳會變成永遠髒的未追蹤檔。

## 實驗(/tmp/r3exp,真 git,未動 /home/user/Lumos)

- 兩個 clone(A、B)加一個 bare origin。A 提交「根 .gitignore 加兩行本機帳」,並產生兩本本機帳;B 的 `docs/.usage-log.jsonl`(凍結的舊追蹤檔)有舊版工具寫的未提交改動。
- B `git pull --ff-only`:成功,凍結檔照舊 ` M`,沒刪檔、沒中止。R2 的修法站得住。
- A `git revert` 該提交後:`git status --porcelain` 出現 `?? docs/.governance-local.jsonl`、`?? docs/.usage-local.jsonl`,`git add -A -n` 會把兩本都暫存。B 再 pull 還原提交:成功,B 上的本機帳同樣變成 `??`。

## Findings

1. 還原後本 repo 的兩本本機帳不再被忽略,永遠髒;一次 `git add -A` 就讓它們進版控,之後重新上線無法再讓它們回到忽略
severity: major
blocking: 是——〈回退〉與〈實務隱患〉回滾的陳述與實測相反,而且本案要解的就是「工作目錄不乾淨」,還原等於把病原樣放回來並加上兩個永遠清不掉的未追蹤檔。
引句:「兩本本機帳留在磁碟、仍被忽略,不影響任何判定;要清就刪 `docs/.governance-local.jsonl` 與 `docs/.usage-local.jsonl`。」
- 場景:本 repo 的忽略只靠根 `.gitignore`(spec 做法 5 第一項;`git ls-files` 沒有 `docs/.gitignore`)。單一功能提交含這兩行,還原就把兩行拿掉(上面實驗已重現)。舊版工具不再寫這兩個檔、也不會刪,所以是永遠的 `??`。雲端工作階段每回合的「有沒提交的改動」打斷(spec 開頭的 WHY)原樣回來。
- 連帶:`_lint_aligned` 用不帶 `-uno` 的 `git status --porcelain` 判對齊,未追蹤檔使其回 False(`scripts/lumos:24270`、呼叫點 `scripts/lumos:37514`);`lumos` 自己的狀態顯示也會標「有未提交的改動」(`scripts/lumos:302`)。
- 更糟的二次傷害:有人在還原後順手 `git add -A`,本機帳被追蹤;之後重新上線,`.gitignore` 不會讓已追蹤的檔停止被追蹤,新版會一直寫進被追蹤的檔,且兩台機器各自追加會在 pull 時衝突。這直接打破〈實務隱患〉相容段「沒有任何檔停止追蹤,所以別台機器 pull、合併都不會刪檔或衝突」的前提。
- 修法方向:回退節要寫明「還原後要手動刪兩本本機帳,或把兩行忽略規則留在一個不隨還原消失的地方(例如獨立的前置提交、或不隨功能提交一起還原)」,並把「還原後本 repo 會出現兩個未追蹤檔」列成已知後果;消費專案不受影響(忽略規則在它們自己已提交的 `docs/.gitignore`)。

2. 既有 vault 沒有 `docs/.gitignore` 時,init 建出的整份(約 7 行)會同時忽略 bypass、kill、signoff、canary 帳,與範圍的「不動五本」及回滾的「多出的兩行無害」都不符
severity: major
blocking: 是——對舊 vault 靜默改變「繞道、擋人相關帳本進不進版控」,而且還原提交救不回來(init 寫進消費專案的檔不隨還原消失)。
引句:「不存在就照 `governance/.gitignore` 的先例建一份(內容同新建 vault 的那份;已追蹤的檔不受 .gitignore 影響)」
- 場景:新建 vault 的那份內容是 `.bypass-log.jsonl`、`.rot-queue.jsonl`、`.canary-log.jsonl`、`.kill-log.jsonl`、`.signoff-log.jsonl`、`.usage-log.jsonl`、`.ci-log.jsonl`(`scripts/lumos:20879-20881`)。2026-08-21 之前建的 vault 沒有這份檔(spec 盤點自己這麼說),所以它們的 bypass、kill、signoff、canary 帳若還沒被提交過,從此被忽略、永遠不進版控;spec 〈不做〉明說「不動 canary、bypass、kill、signoff、escape 五本」,而〈盤點〉又說繞道痕跡要照舊進版控。「已追蹤的檔不受影響」只救得了已提交過的那幾本。
- 回滾面:還原提交不會動消費專案裡 init 已建好、或使用者已提交的 `docs/.gitignore`,所以〈實務隱患〉「多出的兩行忽略規則無害」對「整份新建」的情況不成立(多的是七行,不是兩行)。
- 修法方向:既有 vault 缺檔時只建兩行本機帳(加註解),不套整份新建 vault 的清單;或明講取捨並讓使用者裁。⚠ 若專案另有裁定「舊 vault 也該靠齊新 vault 的忽略清單」,這條降為 minor,但 spec 要明寫並刪掉「無害」。

3. 新舊版混用時,舊版 `lumos gov --nags` 的「最近一次 doctor」基準會落在版控帳裡的舊 doctor-run,導致空轉提醒靜默
severity: minor
blocking: 否——只影響統計類軟提醒,判定類不受影響,spec 已承認「統計看不到」但沒點出 nags 會偏向靜默而不是偏吵。
引句:「舊版不讀本機帳,上線期間的例行觀察在統計裡看不到(判定不受影響)」
- 場景:機器 X 跑新版,doctor-run 與 warned 都進本機帳;機器 Y(或還原後)的舊版 `_render_gov_nags` 取 `doctor-run` 的最大時間當 last_run、再比 warned 的最後一次(`scripts/lumos:8050`、`scripts/lumos:8058-8060`),版控帳裡沒有新版期間的 doctor-run 與 warned,基準停在上線前,「最後一次提醒就在最近一次體檢那天」不成立,`autonomous-loop.sh` 週報的空轉訊號回 rc0。後果是少報,不是多報,與天花板 2 講的「偏吵」方向相反。

4. 回退提交本身要過代碼審關卡的事實沒寫
severity: minor
blocking: 否——是操作成本,不是正確性。⚠ 我沒有實跑 pre-push,只依 CLAUDE.md 描述與 `_BOOKKEEPING_DIRS` 推得。
引句:「還原本案的單一功能提交(〈實務隱患〉回滾)。」
- 場景:還原提交改到 `scripts/lumos`,會讓 code-loop 留痕失效、推送被擋(見 CLAUDE.md〈提交與推送〉的代碼審說明);緊急回滾時沒有寫「走審查還是走 bypass」。建議回退節補一句。

## 已驗、無問題(不編號)

- 「使用紀錄帳改寫新檔不停止追蹤」:別台機器 pull 不刪檔、不中止(實驗已證)。`_pull_source_or_abort` 對來源 clone 的簿記帳聯集合併仍認 `docs/.usage-log.jsonl`(`scripts/lumos:24193`),凍結檔不再被寫,反而減少該路徑的觸發。
- 兩本新本機帳不在 `_BOOKKEEPING_FILES`:它們被忽略、不進 porcelain(`scripts/lumos:12512` 本來就 `--untracked-files=no`),不影響代碼審留痕判斷;僅在「回滾後未忽略」時才會在 `status` 出現(併入 finding 1)。
- 已被 init 補過 `.gitignore` 的消費專案多出的本機帳兩行:單看這兩行確實無害(finding 2 講的是整份新建的情況)。

總結:R2 的「改寫新檔、不停止追蹤」修法經真 git 驗證有效;但〈回退〉在本 repo 的「仍被忽略」是假的(還原即取消忽略,出現兩個永遠髒的未追蹤檔、且有被誤提交成永久追蹤的路徑),且既有 vault 建整份 `docs/.gitignore` 會順帶忽略 bypass、kill、signoff、canary 帳,最嚴重 severity: major。
