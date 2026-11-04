severity: major

我審的是 `r1-snapshot.md`,對照 `/Users/enzo/harness/lumos-tq-android` 的現況。我只讀檔,沒建任何暫存。

**第 1 問 分層與依賴方向:部分對齊,有一處不對齊(發現 1)。**
- 配套四處同步(`_VENDORED_TOOLKIT`、指紋表、載入順序、兩支掛鉤的豁免清單)跟 test-quality 三支配套一致:`scripts/lumos:31959`、`scripts/lumos:69701`、`scripts/lumos:69706`。
- 閘(主程式)呼叫配套模組有先例,方向沒反:`_secev_tq()` 在 `scripts/lumos:8816` 就是主程式取用已驗的 `test_quality`。
- 子指令層的寫法鄰居是 `add_parser`/`dispatch`,在 `scripts/test_quality.py:284` 與 `scripts/test_quality.py:461`。scan 是 `add_scan_arguments` 加 `main(args=)`,在 `scripts/test_quality_scan.py:229` 與 `scripts/test_quality_scan.py:285`。計劃沒寫 guard 要不要照這個形狀,也沒寫它的測試檔放哪。
- 「只有碰到五類檔才載入」跟配套的實際行為不同。`main()` 一啟動就整組載入(`scripts/lumos:69780`)。閘要做的是像 `_secev_tq` 那樣取用已載入的模組,不是「載入」。
- guard 的 `tq/too-large` 要用閘的單檔上限,而上限的設定在主程式(`_lint_new_config`,`scripts/lumos:38429`)。獨立執行 `lumos test-quality guard` 時,上限從哪來,計劃沒說:是複製一份常數,還是由閘傳參數。這點我判不準,標 ⚠ 交編排者。
- 不構成跨層直呼:guard 沒有反過來呼叫主程式。

**第 2 問 命名與錯誤處理:大致對齊,有兩處不一致(發現 3、4、5、6,都是 minor)。**
- 規則代號 `tq/` 加 kebab 寫法,跟 scan 的 `rule_id`(`scripts/test_quality_scan.py:190`)同風格。
- 放行指紋用 sha256 前 16 碼,跟既有算法同形:`_lint_new_diff_claims` 在 `scripts/lumos:38654`,算 `[:16]`。`lint-waive` 的 `--rule`/`--file` 也本來就有:`scripts/lumos:37840`。
- 退出碼:計劃的 guard 是「有候選回 1」,跟 `room-guard` 一致(`scripts/lumos:48016`),但跟同層 `test-quality scan` 不同。scan 的候選不影響 rc,只有不完整回 2(`scripts/test_quality_scan.py:285` 往下)。`dispatch` 出錯回 `not_assessed` 的 JSON 加 rc 2(`scripts/test_quality.py:461` 往下)。
- 治理帳:計劃寫的 kind 是「跳過」,字彙裡沒有這個值。環境變數跳過的鄰居寫法是 `skipped-env`:`scripts/lumos:47959`、`scripts/lumos:48079`。設定 off 時,`room-guard` 是直接回 0 不記帳(`scripts/lumos:48016` 往下)。
- `skipped-env` 不在 `_GOV_LOCAL_PAIRS`(`scripts/lumos:1638`),所以會進有進版控的帳。設成 off 的專案每次推送都會寫一行,噪音要先想好。

**第 3 問 第二種做法:有兩處(發現 1、2),另有一處有先例的判為不算(發現 3)。**
- Kotlin/Java 測試函式辨識:這個 repo 已有 `KOTLIN_TEST_RE`(`scripts/lumos:5981`)、`JAVA_TEST_RE`(`scripts/lumos:5995`)、`TEST_PROFILES["kotlin-junit"/"java-junit"]`(`scripts/lumos:6136`),還有 Room 守衛的 `_rg_methods`/`_rg_balanced`(`scripts/lumos:47768`、`scripts/lumos:47377`)。計劃的 PRIOR-ART 只查了外面的工具(detekt、Konsist、Android Lint、Sonar),沒查本 repo。
- 讀 git 改動:鄰居有 `_lint_new_changed_files`(`scripts/lumos:38469`)、`_lens_git`(`scripts/lumos:62974`)、`_nodehome_reader`(`scripts/lumos:43423`)。test_quality 三支配套裡一行 git 呼叫都沒有(grep 確認過)。計劃讓配套模組自己跑 git。
- 失敗語意「出錯就擋」:不算第二種做法,有三個先例。
  - 閘自己的預算用完不歸自動放行,直接擋:`scripts/lumos:38766`。
  - 閘的「檔太大沒檢查」直接擋:`scripts/lumos:38744`。
  - Android 端到端驗收「判不清就擋」:`scripts/lumos:42445`。
- room-guard 的 WHY 也寫明「跟端到端驗收的判不清就擋刻意不同」(`Systems/room-guard`),所以專案裡兩種語意並存、各自有理由。
- 放行機制沿用 `lint-waive`,沒有第二套,對齊。

**第 4 問 落點:部分合理,有兩處待處理(發現 7)。**
- `test-quality-cli` 掛 0 份計劃、管 3 支檔,容量沒問題。但它的 responsibility 寫的是「明示本機命令收證與 JUnit 一致性核對」。guard 是推送前看 diff 的防竄改,責任不同,要改寫那段。
- 對照:scan 檔有自己的家 `test-quality-scan`。Room 守衛也有獨立的 `room-guard`,責任裡含推送前呼叫那段。
- 六條小修與配套部署同步落在 `test-quality-cli` 合理。
- Semgrep 一條落 `test-quality-scan` 合理。
- 閘的部分落 `pitfalls-lint-adapter` 可以。但上一份《新增告警閘》的 lands_in 是 `pitfalls-lint-adapter` 加 `pitfalls-code-loop`,「判」的那段在後者(`Systems/pitfalls-code-loop` 的〈新增告警閘怎麼判〉)。這份計劃的〈二、併進新增告警閘〉改的正是判定順序與擋下訊息,卻漏了 `pitfalls-code-loop`。
- `pitfalls-lint-adapter` 沒寫負責範圍,再多掛一份計劃會更糊。

---

**發現 1**
severity: major
blocking: 是
引句:「用括號配對找函式本體,略過字串與註解裡的括號。」
- 計劃自建一套 Kotlin/Java 測試函式辨識(`fun 名稱(`、`void 名稱(`)、測試路徑分類、括號配對。本 repo 已有同用途的實作:
  - `scripts/lumos:5981`、`scripts/lumos:5995`、`scripts/lumos:6136`:既有的測試函式辨識。
  - `scripts/lumos:47364`:既有的測試路徑判斷。
  - `scripts/lumos:47377`:既有的括號配對。
  - `scripts/lumos:6756`:剝註解與字串。這支的 docstring 明寫「全庫只有這一支……不留兩套掃描」。
- 測試路徑已有三份定義,這份是第四份:`scripts/lumos:37566`、`scripts/lumos:47364`、`scripts/lumos:6136`。
- 配套不能 import 主程式,所以要嘛複製、要嘛由主程式傳進去。計劃沒交代,等於默認複製。

佐證 file: `scripts/lumos:6756`

**發現 2**
severity: major
blocking: 是
引句:「判讀只用逐行比對與括號配對,跟輸入大小成正比。」
⚠ 判不準:「讀 git 的方式算不算第二種做法」有爭議,請編排者裁。
- 閘已經算好兩端提交,也有自己的改動檔清單(`_lint_new_changed_files`,`scripts/lumos:38469`)。計劃讓 guard 在配套裡再跑一次 `git diff --name-status` 加讀 blob(做法第一節「兩邊都從 git 讀」)。這是三支配套首次碰 git(grep 確認過)。
- 同一次閘裡會有兩份可能不一致的改動清單(改名偵測各算各的)。
- 配套自己跑 git,也沒有 `_lens_git`(`scripts/lumos:62974`)的逾時與 NUL 防護。
- 有利於計劃的理由:`_lint_new_changed_files` 刻意不收刪除(`scripts/lumos:38469` 往下),而 guard 要看刪除。`_lint_new_changed_files` 自己的 docstring 也說過「另開一支只給這道閘用的查詢」,有先例。
- 較一致的做法是:閘把含刪除的清單加一個 reader 傳進純函式 guard,或把 guard 放主程式像 `_rg_*`。

佐證 file: `scripts/lumos:38469`

**發現 3**
severity: minor
blocking: 否
引句:「比對工具只讀 git、不靠外部工具,出錯多半是程式錯,放行等於靜默關掉。」
- 「出錯就擋」本身有先例,不算第二種做法。
- 但 `_codeloop_lint_new_step` 在外層把 `_lint_new_verdict` 的任何例外接成 fail-open:`scripts/lumos:67962`。
- 所以 guard 的例外必須在 verdict 內接住,轉成非 env 的 `undone`(像 budget 那種),否則跟計劃的「擋下」相反。計劃沒寫這一點。

佐證 file: `scripts/lumos:67962`

**發現 4**
severity: minor
blocking: 否
引句:「閘被設定 off 或 `LUMOS_SKIP_LINT_NEW` 跳過時,補寫一筆治理帳」
- kind 應用字彙內的 `skipped-env`(環境變數)。
- 設定 off 時鄰居不記帳,記的話要先處理噪音。

佐證 file: `scripts/lumos:47959`

**發現 5**
severity: minor
blocking: 否
引句:「| `tq/too-large` | 測試檔、正式程式檔或建置檔任一版本超過新增告警閘的單檔上限(行數或位元組),沒比 | 不靜默略過 |」
- 閘已有「太大沒檢查」的機制:`out["oversize"]` 加路徑綁定的指紋,`scripts/lumos:38744`。
- guard 另立一套 `tq/too-large`,身分字串沒定義。
- 它的指紋若綁內容,每改一次就要重新放行,正是 `scripts/lumos:38744` 註解警告過的。
- 建議說明為什麼不併進現有 oversize,或明定綁路徑。

佐證 file: `scripts/lumos:38744`

**發現 6**
severity: minor
blocking: 否
引句:「退出碼:沒有候選 0、有候選 1、讀不了(不是 git、任一端不是提交)2。」
- 同層 `test-quality scan` 的 rc 與 JSON 欄位形狀不同,見 `scripts/test_quality_scan.py:198`、`scripts/test_quality.py:461`。
- rc1 對齊 room-guard 沒問題,但計劃沒明說為什麼跟同層 scan 不同。
- 還缺三項:模組形狀(`add_guard_arguments` 加 `main(args=)`)、`add_parser` 的 `ModuleNotFoundError` 退路(`scripts/test_quality.py:289`)、單元測試檔的位置。scan 與 cli 各有 `test_test_quality_*.py`,再用 `t_` 包一層。

佐證 file: `scripts/test_quality.py:284`

**發現 7**
severity: minor
blocking: 否
引句:「它的家是 `Systems/test-quality-cli`(收證工具的家,實作時把這支檔加進那篇的 about_code)。」
- guard 檔建議另開一篇(例如 `Systems/test-quality-guard`),不要硬塞進 cli 現有責任。
- lands_in 補上 `pitfalls-code-loop`(閘的「判」那段)。

佐證 file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:6`

不對齊共 7 條,其中 major 2 條(發現 2 標 ⚠,等編排者裁)。
