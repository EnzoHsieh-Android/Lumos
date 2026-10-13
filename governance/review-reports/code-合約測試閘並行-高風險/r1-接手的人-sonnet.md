severity: major

## 發現

### 1. 計劃寫的「回退」步驟會讓 S3 測試翻紅
severity: major
blocking: 是
引句:「只想關掉不還原程式時,把本 repo 設定的 `bound_tests.parallel` 拿掉或改成 1,行為就回到循序」
引句:「[S3] 本 repo 的 `.lumos/config.json` 應 有 `bound_tests.parallel` 且為 2–16 的整數,程式讀到的也是這個值」
file: `docs/lumos-toolchain-knowledge/Projects/合約測試閘並行執行_計劃.md`(回退節與 [S3])
file: `scripts/test_lumos.py`(`t_bound_tests_parallel_repo_config_on`)
1. 三個月後的接手者照回退節把 parallel 改成 1。`RETIRE-IF` 也叫人「把本 repo 的設定改回 1」。
2. `t_bound_tests_parallel_repo_config_on` 斷言本 repo 設定必須是 2 到 16 的整數。
3. 我複製 `scripts/lumos`、`scripts/test_lumos.py` 和一份把 parallel 設成 1 的設定,執行 `python3.14 scripts/test_lumos.py -k t_bound_tests_parallel_repo_config_on`。輸出是 `✗ FAILED t_bound_tests_parallel_repo_config_on(1 條斷言)`,`1 passed, 1 failed`。
4. 結果是:官方寫的「關掉」路徑會讓全套測試轉紅,推送閘擋下。接手者得同時改設定和測試,或刪掉 S3 條款。計劃沒講這件事。
5. 這個測試只在證明「設定現在是開的」,不是在守行為。它和計劃自己的回退路徑互相矛盾。

### 2. 計劃與筆記說「執行緒池」,程式明確沒有用
severity: minor
blocking: 否
引句:「N≥2 時用執行緒池同時跑這些鍵(每支仍呼叫既有的 `_kill_run`」
引句:「# ★不用 ThreadPoolExecutor★(代碼審 r2):它的工作者不是 daemon,程式結束時會 join」
file: `docs/lumos-toolchain-knowledge/Projects/合約測試閘並行執行_計劃.md`(做法節)
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`(新段 WHY:「再用執行緒池同時跑」)
1. 計劃「做法」和 `bound-tests-gate` 的 WHY 都寫「執行緒池」。
2. 同一份計劃的「實務隱患」寫「不用標準執行緒池」,程式註解也一樣。計劃內部自相矛盾。
3. 實際做法是自建 daemon 執行緒加 queue。筆記沒有保留「為什麼不能換成 ThreadPoolExecutor」(結束時會 join、出錯例外要等前面的跑完才浮上來)。
4. 接手者只讀筆記,會把它簡化成 `ThreadPoolExecutor.map`,重新引入 r2 已修掉的問題。S5 測試會抓到,但要等紅了才知道。
5. 應把「daemon 執行緒,不用 ThreadPoolExecutor,原因…」寫進 WHY 的 `[不選:]`。

### 3. 消費專案找不到怎麼打開
severity: minor
blocking: 否
引句:「各專案的測試工具能不能同時跑(例如會互搶建置目錄的工具)由專案自己判斷要不要打開。」
file: `skills/lumos-project-notes/commands/07-安裝維運.md`
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md`
file: `docs/指令參考.md:127`
1. 計劃說消費專案自己判斷要不要打開,但這份 diff 沒有任何面向使用者的說明。
2. 我用 Grep 查 skills、README、`docs/*.md` 裡的 `bound_tests` 和 `parallel`,只找到 `scripts/lumos` 與測試檔,沒有任何手冊提到。
3. 同類的 `note_shape.*` 設定在 `07-安裝維運.md` 和 `06-代碼審與推送.md` 都有寫。
4. 使用者看不到鍵名、合法範圍(2 到 16)、不該開的情況(測試工具互搶建置目錄、共用資料庫、固定埠)和不合法時的提醒。計劃只寫了「由專案自己判斷」,沒有給判斷依據。
5. 那段說明該放在 `07-安裝維運.md`,並在 `06` 的合約測試閘列補一句。

### 4. 同一篇 bound-tests-gate 的舊段落沒跟著改
severity: minor
blocking: 否
引句:「三次 check 超過 3 分鐘 → 加只跑 direct 相依的縮圈選項。」
引句:「real 的逐支用 `.lumos/config.json` 的 run_cmd 真跑(`_kill_run`,同 kill);去重鍵=完整指令。」
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`(「怎麼跑」第 3 點、「回頭看條件」)
1. 「怎麼跑」第 3 點仍只描述逐支循序,沒有指向設定 `parallel`。新段落放在檔案最尾,在「推送前掛鉤的回頭重讀那一段」之後。讀流程的人讀不到它。
2. 「回頭看條件」的 3 分鐘門檻是計劃明文「另案」的縮圈方案。並行已把耗時壓到約 56 秒,但這條沒說在 parallel 開啟後怎麼算。
3. 「帳的類別」那段說 `secs` 是「跑測試」。這個意思其實已變成牆上時間,那裡沒提 `secs_kind`。

### 5. 計劃的 REVISIT 沒有指出讀 `secs` 的工具
severity: minor
blocking: 否
引句:「REVISIT:2026-12-15 看上線後 8 週治理帳 bound-tests 那一欄 secs(已改成牆上時間)的中位數」
file: `scripts/lumos:8707`(`"secs": d.get("secs") if d.get("gate") == "fix-check" else None`)
1. 整合後的治理事件只對 fix-check 帶 `secs`,對 bound-tests 一律丟成 None。
2. `gov --stats` 看不到 bound-tests 的 `secs` 或 `secs_kind`。三個月後的人只能直接解析 `docs/.governance-log.jsonl`。
3. 計劃也沒有說要用 `secs_kind == "wall"` 篩掉舊帳(舊帳 secs 是相加值)。不篩,中位數會把舊帳混進去。
4. 日期當天會撞牆。要在 REVISIT 補上取數方法(jq 或 python 一行),並寫明篩 `secs_kind=wall`。

## 鏡頭逐條判定

- **量測數字與程式**:51 支去重、59 項、4 路約 56 秒對 176.5 秒,和程式的去重鍵、排程邏輯一致。我沒有重跑量測。
- **各條款綁的測試**
  - S1 到 S5 的測試都驗到條款說的事。
  - S1 條款寫「N=1 與 N=3」,測試實際用 `None`(未設定)對比 3。兩者都走循序,語意相同。
  - S3 是狀態斷言,見發現 1。
- **程式註解 vs 程式**
  - 註解說「daemon 執行緒自己取工作、任一支丟例外就停止派新的、主流程每 0.1 秒看一次」,程式相符。
  - 註解說「跟循序時按 Ctrl-C 一樣成為孤兒」,`_kill_run` 沒有 `KeyboardInterrupt` 清理,所以屬實。差別是並行時最多 N 支一起成為孤兒,計劃沒提這個數量差。
  - `secs_kind` 註解與程式相符。
- **其他文件有沒有提到一支一支跑**:`docs/指令參考.md`、`docs/command-reference.md`、`skills/lumos-code-loop/SKILL.md`、`06-代碼審與推送.md` 都沒有寫循序,所以不需要改。`secs_kind` 沒進 `_GOV_FIELD_TYPES`,未列鍵會通過型別檢查,不會造成事件被丟棄。
- **lint**:`lumos lint` 對 `Systems/bound-tests-gate` 和計劃兩篇都是 0 問題。
- **意外副作用**:我跑 lint 之後,repo 出現 `docs/.canary-log.jsonl`、`docs/.governance-log.jsonl` 的修改。我沒有手動寫它們,疑似 lint 或先前席位留下的。這是副作用,不是這份 diff 的問題。

## 圖譜鏡頭(固定席節點)

- **`bound-tests-gate` ★INVARIANT★**(任一紅、懸空、偽證據、不合法、證不出跑過,就 rc1 擋)
  - 未破壞。紅綠判定、逾時、跑過證據都在組結果階段、照原項目順序、用同一套規則。
  - S1 測試覆蓋了紅、綠、unproven、逾時、懸空。
  - 唯一語意變動是 `secs`(發現 4、5)。
- **`guard-kill`、`測試假綠形態`、`design-loop`、`lumos-cli-read`、`lumos-cli-lifecycle`**
  - 這份 diff 沒碰到這些合約的邏輯。
  - guard-kill 與 `_kill_run` 共用,但 `_kill_run` 本體沒改。
- **`loop-convergence-recording`、`pitfalls-code-loop`(★RISK★)**
  - 規格閘與修正關卡也經 `_run_bound_tests`。`parallel` 打開後它們也變並行,計劃已寫在「實務隱患」,判定結果不變。
- **「超出上限只列名」的那批節點**:我沒有逐一檢查。

總結:最高等級 major
