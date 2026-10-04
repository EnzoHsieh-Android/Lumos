severity: major

# 治理帳例行紀錄分流 r2 併發/時序席(sonnet)

審查對象:/tmp/gov-ledger-split-r2.md(第 2 版)。對照 scripts/lumos 現況逐項查證。

## 各節結論

- 盤點:寫入器清單(四支直接寫、其餘包裝)已對 `scripts/lumos:1358`、`1426`、`42423`、`43253` 查證屬實;hooks 不寫帳(scripts/hooks 無 governance-log)。已讀,除下列 finding 外無 finding。
- 範圍:已讀,無 finding。
- 做法 2(本機帳位置)、做法 3 的併發主張:`_gate_event` 單次 `f.write` 一行、`_append_governance_log` 同批多筆(`scripts/lumos:1426-1430`),兩本帳與今天同層同寫者,「併發樣貌不變」成立;兩本各自 try/except 的分開處理合理。已讀,無 finding。
- 驗收條款、回退、天花板:見 finding 1、5。

## Findings

1. 分流判準有一個開放缺口:觀察型閘名單是白名單、留痕種類名單是黑名單,bound-tests 有三種「略過/放寬/擋人」種類不在黑名單上,會被寫進本機帳,方向是「偏丟」,與 spec 自己的保證相反。
severity: major
blocking: 是(違反 spec 自己的守衛面保證,且會讓人當場被擋的紀錄 CI 與別台機器看不到;判準:讓擋人/繞道痕跡消失 = major)
引句:「新增的閘或種類沒放進名單,就照舊進版控帳——分錯只會偏吵,不會偏丟。」
file: `scripts/lumos:42844`(`LUMOS_SKIP_BOUND_TESTS` 以外的旗標跳過記 `skipped-flag`,註解寫「前者是人當下決定並留了理由」)、`scripts/lumos:42945`(`unfilterable` 記帳)、`scripts/lumos:42465`(`_bound_tests_log` 只有 `red-blocked` 才 `hard: True`)、`scripts/lumos:43783`(`unfilterable` 在非 advisory 時照紅一樣擋推送)。
失敗時序:使用者帶旗標略過綁定測試推送 → `_bound_tests_log(…, "skipped-flag", …)` → gate=bound-tests 在觀察型名單、hard 為假、`skipped-flag` 不在留痕種類名單(名單只有 skipped、skipped-env)→ 寫進本機帳。同理 `unfilterable`(推送被擋,但事件 hard=False)、`no-config`、`range-unavailable`、`diff-unavailable`、`whole-suite-deferred`(`scripts/lumos:42443` 註解自稱「fail-open 四情境」)都落本機。種類名單是黑名單,任何觀察型閘將來新增的略過類種類預設去本機,「新增的種類沒放進名單就進版控」只對「閘」成立,對「種類」是反的。
後果:另一台機器與 CI 看不到這次人為略過與這次被擋;`gov --stats` 的「被跳過」計數在別處少算。判定類讀者目前不讀 bound-tests,所以不是閘變放,但屬於守衛面主風險,且 spec 以「三道保險」宣稱沒有這個洞。
折入對不對:r1「繞道與自動放行痕跡全數留版控」折成名單枚舉,枚舉漏了現有的 `skipped-flag`。

2. 使用紀錄帳停止追蹤的提交,spec 沒寫與既有分支/其他 clone 的合併處置。
severity: minor
blocking: 否(可手動解,不丟判定;判準:有明確手動出路且不影響閘)
引句:「並對使用紀錄帳做一次停止追蹤(`git rm --cached`,檔案留在磁碟)。」
file: `scripts/lumos:16186`(`_usage_log` 每次 show/context 都 append);`git log -- docs/.usage-log.jsonl` 顯示它常被夾進不相干提交(例如 abcd1aa1、98a40ada);`scripts/lumos:20605-20635`(update 路徑的簿記帳聯集合併)。
時序:分支 B 含一個順手提交了 `docs/.usage-log.jsonl` 修改的提交,主線隨後上了「停止追蹤」提交 → B 合回或 rebase 時是 modify/delete 衝突;最省事的解法是 `git add` 該檔,等於悄悄把它重新追蹤,目標又失效。另外其他機器 pull 到這個提交時,git 會把乾淨的追蹤檔從磁碟刪掉(「檔案留在磁碟」只對下 `git rm --cached` 的那一台成立)。update 路徑的聯集合併會把髒的那份補回,所以只有「乾淨」的 clone 會丟歷史使用紀錄;spec 的「不搬舊紀錄」沒講這件事。
要補的:回滾/相容段寫明衝突時的解法(`git rm --cached` 而非 `git add`),並把「其他 clone 拉到後本機使用紀錄被刪」列進相容。

3. 兩本帳合併讀時,spec-gate 比例段是「後寫者勝」的檔序讀法,spec 沒定義兩本的合併順序。
severity: minor
blocking: 否(統計提醒,不擋;判準:只影響 doctor 軟提醒)
引句:「抽一支模組層級的小函式給它們共用,`cmd_gov` 的 `load` 不搬」
file: `scripts/lumos:2870-2878`(逐行讀,`_latest[str(_nd)] = note` 以檔案順序後者覆蓋前者)。`cmd_gov` 靠 `sorted(rows, key=ts)` 排序後去重(`scripts/lumos:8222-8230`),共用函式若只是兩檔串接,順序就由呼叫端決定。
時序:分流上線前的舊 `spec-gate-run`(版控帳)與上線後的新 `spec-gate-run`(本機帳)並存;串接順序若是 [本機, 版控] 則舊值蓋新值,doctor 顯示過期的紅綠弱證據;在全新副本只有版控帳,必然顯示上線前的最後一筆。spec 只說「兩本一起讀」,沒要求依 ts 排序,S3 只驗計數相同,驗不到「最近一次」。
要補的:共用函式規定以 ts 排序後再給 spec-gate 段取最後一筆,S3 加一條「新舊各一筆時取較新」。

4. init 補忽略規則的追加沒寫換行處理,會把既有規則黏壞。
severity: minor
blocking: 否(偏吵不偏丟;判準:fail-safe,但會弄壞既有 .ci-log 規則所以需修)
引句:「`docs/.gitignore` 存在而缺這一行就在尾端追加,不存在就不建(維持「只加不覆寫」)。」
file: 現行 scaffold 只用 `_write_lf` 整檔寫(`scripts/lumos:20877-20881`),`_init_additive_setup`(`scripts/lumos:20885-20906`)目前完全沒有「追加到既有檔」的先例;同檔另一處追加有處理結尾換行(`scripts/lumos:20625` 的 `sep`)。
時序:使用者手改過的 `docs/.gitignore` 最後一行沒有結尾換行(編輯器常見)→ 直接 append `.governance-local.jsonl\n` 得到 `.ci-log.jsonl.governance-local.jsonl`,本機帳與原本的 .ci-log 兩條規則一起失效,例行紀錄變成未追蹤髒檔。兩個行程同時補(例如 `lumos update` 與 init)各自讀到「缺」再各自追加,只會多一行重複,無害,不另標。「缺這一行」的比對是整行還是子字串也沒定義。
要補的:追加前檢查結尾換行,比對用逐行完全相等(去 `\r`),S5 加無結尾換行的案例。

5. 天花板漏列一個現有的跨機器消費者:每週空轉提醒(`gov --nags`)。
severity: minor
blocking: 否(只發 LINE 提醒,不擋;判準:軟提醒)
引句:「`gov --nags` 經 load 自動涵蓋」
file: `governance/autonomous-loop.sh:404-407`(每週對 `$REPO` 與 `$HOME/backend/LandmarkMember` 跑 `lumos gov --nags 14 --since 120`)、`scripts/lumos:8044-8071`(`_render_gov_nags` 用 check-* warned 與最近一次 doctor-run 的時間判「還在喊」)。
時序:開發者在別的 worktree/雲端工作階段 push,`doctor --ci` 的 check-* warned 與 doctor-run 寫進「那個 checkout 的」本機帳;排程所在 checkout 的版控帳不再收到它們 → 排程只看得到自己 checkout 的本機帳與上線前的舊紀錄。結果要嘛清單凍在最後一次舊紀錄(`last_run` 不再前進,舊提醒一直算「還在喊」,每週重複發 LINE),要嘛看不到真正在空轉的提醒。spec 的天花板只列 `--stats` 與 S18,沒列這個每週自動消費者,RETIRE-IF 的「有讀者要用別台機器的例行紀錄」其實現在就成立。
要補的:天花板列出 `--nags` 與兩處排程(toolchain、LandmarkMember),或在 REVISIT 加「上線後第一個週報是否仍有輸出」。

6. 其餘逐類實務隱患(本席查過、無 finding 的):
- 同批兩本各自寫、中途一本失敗:`_append_governance_log` 兩次獨立 open,部分成功的狀態讀者都容忍(去重鍵 `scripts/lumos:8224` 不依賴同批完整性);已讀,無 finding。
- pre-push 逐 ref 迴圈多次寫:`LUMOS_PUSH_ATTEMPT` 與 sha 欄位沿用,分流只換檔案;已讀,無 finding。
- 判定類讀者與 hard 判準:查 `drift-check`、`nodehome-check`、`note-shape`、doctor 的 check-r/check-j,hard 與 blocked 一致(`scripts/lumos:27372`、`34781`、`35713`、`1908`、`3394`),r1 折入的 hard 規則對這些閘正確;只有 bound-tests 例外(finding 1)。

總結:最嚴重為 major(finding 1:bound-tests 的 skipped-flag 與 unfilterable 等種類會被分到本機帳,與 spec 自己「只會偏吵不會偏丟」的保證相反),其餘 4 條 minor。
