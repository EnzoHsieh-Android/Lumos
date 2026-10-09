severity: major

已逐節讀完整份 spec,並對照四支腳本與 repo 歷史。我跑了 `historical_test_quality.py`(preflight_passed=true)、`historical_case_corpus.py`(12 組全 qualified)、`historical_handbook_trial.py --controls`(8 項控制全過),都沒叫模型。另用 `grade()` 餵自造測試做探針,探針與輸出放在 `/tmp/lumos-seat-work/歷史弱測試手冊評估/通才-sonnet/t/`。已完成的兩批 2/2 平手結論不受下列問題推翻,問題都出在後續階段或這份 spec 寫的規則與程式不一致。

ID: GEN-1
severity: major
blocking: 是
引句:「檢出需修復版有非零測試、非零明示斷言、全綠，錯版無 errors、有該斷言失敗且觀測到 depth>0 的 fallback 取鎖卡住。」
審材外佐證 file: `governance/eval/historical_handbook_trial.py:212`
審材外佐證 file: `governance/eval/historical_handbook_trial.py:213`

spec 只要求修復版有非零明示斷言,程式卻要求兩個版本都有。第 212 行的 `valid = all(... s['evidence']['assertions'] > 0 ...) for s in scores.values()` 對 faulty 也適用。錯版一進巢狀取鎖就卡住,後面的斷言根本跑不到。

探針結果如下,三個測試都在錯版真的觸發 `lock-enter-incomplete`:

| 探針 | 內容 | 判定 |
|---|---|---|
| `nested_no_pre` | cache-moved 下直接 `with s.lock(): with s.lock(): assertTrue(s.held())` | invalid(faulty assertions=0、blocked_nested_fallback=True) |
| `triple_nested_no_assert_after` | 巢狀後才 `assertFalse(s.held())` | invalid |
| `nested_pre` | 巢狀前多一條 `assertTrue(s.fallback_ready())` | detected |

- **對檢出率的影響:** 最自然的寫法(直接巢狀再斷言)被判 invalid,開頭多一條前置斷言才算檢出。
- **為何偏向手冊臂:** 手冊第 4 條(`03-寫回圖譜.md:35`)明講要「建立該情境及前置斷言」,所以手冊臂結構性占便宜。
- **斷言計數的怪處:** 計數是全檔累計,同檔別的方法先跑出一條斷言,巢狀方法就不會被判 invalid。探針 `two_methods_one_pre` 就是這樣 detected。
- **控制組沒擋到:** 8 項控制的 strong 範本開頭都帶 `assertTrue(s.fallback_ready())`,沒有「無前置」的控制。
- **判準:** spec 與程式對「檢出」的定義不一致,且差異與臂別相關。

ID: GEN-2
severity: major
blocking: 是
引句:「整體15秒程序逾時、語法超出支援範圍、匯入錯誤、零測試列 invalid，不当 survived，也不計改善。」
審材外佐證 file: `governance/eval/historical_handbook_trial.py:112`
審材外佐證 file: `governance/eval/historical_handbook_trial.py:207`

錯版上每個巢狀方法都要吃滿 2 秒 alarm(第 112 行),整個子程序上限卻是 15 秒(第 207 行)。我造 N 個相同的 cache-moved 巢狀方法實測:

| N | 結果 | 耗時 |
|---|---|---|
| 6 | detected | 13.9 秒 |
| 7 | detected | 15.9 秒 |
| 8 | invalid | faulty 為 TimeoutExpired |

- **後果:** 測試越多、越徹底,越容易被判 invalid,而且 invalid「不計改善」。這剛好懲罰手冊想鼓勵的做法。
- **機器負載:** 負載高時門檻更低,N 小於 7 也會超時。
- **已完成的批次:** 這個上限沒被碰到,各臂最多兩個巢狀方法。
- **spec 缺什麼:** 沒有寫「每方法 2 秒 × 方法數」與 15 秒上限的關係,也沒有針對超時的獨立處置(例如逐方法計時或放寬上限)。

ID: GEN-3
severity: major
blocking: 是
引句:「handbook 強制提供正式共用手冊〈實作測試品質〉全文」
審材外佐證 file: `governance/eval/historical_handbook_trial.py:266`
審材外佐證 file: `governance/eval/historical_handbook_trial.py:267`
審材外佐證 file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:45`

手冊在每次執行時才從工作樹即時讀取,不是釘死在某個 commit。我用現行檔重抽,和先前兩批 manifest 存的 `handbook` 比對,結果不同:先前是 1129 字,現在是 1234 字。manifest 也沒有手冊 SHA 欄。

- **漂移來源:** 3717917e 之後,`03-寫回圖譜.md` 又被改過多次(10-08、10-09 各有提交),多出一段「各棧接入測試撰寫…讀 [測試品質接入標準](test-quality-standard.md)」。
- **帶來的新問題:** 手冊臂的模型可能真去 Read 這個不存在的路徑。這會讓 `only_visible_material_read` 為假(第 294 行),或被權限拒絕,整場變 invalid。這個失效只會發生在手冊臂。
- **潛在截斷:** 第 267 行用 `.split('## ')[0]` 切段,手冊之後若加入 `### 子節`,`'### '` 也含 `'## '`,手冊會在子節處被截斷。
- **判準:** 後續案例集階段的處理臂和先前批次不是同一份手冊,而 spec 稱它「正式共用手冊」並要求固定。

ID: GEN-4
severity: major
blocking: 是
引句:「鎖取用2秒故障細節及語法中的巢狀字眼；保留同程序可重入、快取搬移、可信位置與釋放等正常行為需求」
審材外佐證 file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:35`
審材外佐證 file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:26`

lean 題目拿掉了「巢狀」字眼,但手冊臂的手冊第 4 條仍寫「宣稱測併發、巢狀或寫入失敗」。所以 lean 對照的減提示只作用在題目,手冊臂另外帶著線索。

- **手冊與案例同源:** 手冊那條是 2026-10-07 加入(`0d504411`),晚於鎖案例的 2026-09-16。`測試假綠形態.md:26` 把「巢狀測試寫成前後兩個不重疊的區塊」列成這次事故的失效形態,手冊的前置斷言原則和它同調。Java 辨識案例也列在同一篇(第 35 行,`[test:t_java_profile_discovery]`)。
- **⚠ 未證實的一點:** 手冊第 4 條是否直接由該事故萃取,我沒有 commit 層級的直接證據。
- **為什麼重要:** 三案中有兩案(鎖、Java)的來源事故就記在手冊所依據的筆記裡。手冊臂若勝出,分不出是學到通則還是記住事故線索。
- **spec 缺什麼:** 「不同失效歷史案例集」的獨立性只談了案例間不獨立,沒談案例與手冊的獨立性。

ID: GEN-5
severity: minor
blocking: 否
引句:「強測試修復版全綠；錯版只允許manifest預定失敗索引。」
審材外佐證 file: `governance/eval/historical_case_corpus.py:98`
審材外佐證 file: `governance/eval/historical_case_corpus.py:93`

- **資格只比失敗索引:** 第 98 行的 `qualified` 只比對檢查數和 `failed == expected`,不比失敗標籤或 detail。spec 的 RETIRE-IF 寫的是「強錯版失敗理由超出固定目標」,這點沒有被機器強制。單案腳本 `historical_test_quality.py` 才檢查標籤與 detail 字串。
- **Java 不查前置標籤:** 第 93 行 `require_precondition_label=case['id'] != 'java-discovery'`。S1 的「現場前置斷言為真」對 Java 不成立,spec 沒標明這個豁免。
- **目前結果:** 我核對了實際輸出,標籤與 spec 相符,所以今天沒有誤判。屬於防線缺口。

ID: GEN-6
severity: minor
blocking: 否
引句:「固定案例集應保留提交或快照來源、各檔SHA、原／實跑測試SHA、12組原始結果及預定失敗索引」
審材外佐證 file: `governance/eval/historical_case_corpus.py:96`

corpus 的輸出只有執行版測試的 `test_sha256`。原測試只有全文存在 `test-materials.json`,沒有 SHA。實際輸出的 keys 也證實這點:`manifest.json` 只有檔案 SHA,`results.json` 每列只有一個 `test_sha256`。S3 要求的「原測試 SHA」沒有落地。`historical_test_quality.py` 有 `original_test_sha256`,兩支腳本不一致。另外 manifest 先寫的內容不含任何測試 SHA,所以「先寫 manifest」預先登記的只有檔案 SHA、案例數和失敗索引。

ID: GEN-7
severity: minor
blocking: 否
引句:「兩臂皆全抓到記平手，不立改善結論。」
審材外佐證 file: `governance/eval/historical_handbook_trial.py:294`
審材外佐證 file: `governance/eval/historical_handbook_trial.py:299`

invalid 在比較裡怎麼算,spec 只寫了「不計改善」,沒有規則。例如「控制 2 檢出 vs 手冊 1 檢出加 1 invalid」要怎麼判,沒有定義。invalid 又有不對稱的觸發路徑:

- 沒呼叫 Read 就整場 invalid(`bool(reads)`)。
- 輸出的 python fence 不剛好一個就整場 invalid(第 299 行 `len(matches)==1`)。
- 手冊臂多了不可讀路徑的指令(見 GEN-3)。

這些都是臂別相關的儀器失效。spec 應規定:invalid 率要分臂單獨報告、分母口徑固定,不能只寫「如實報平手」。

ID: GEN-8
severity: minor
blocking: 否
引句:「[closed:2026-10-07 四場模型對照完成，兩臂2/2平手，後續固定案例集入口見本次模型驗證紀錄]」
審材外佐證 file: `docs/lumos-toolchain-knowledge/Verification/2026-10-07_歷史鎖案例手冊模型對照.md:37`

這條 REVISIT 的條件是「執行模型對照前凍結…強弱控制與首次生成指標」,但關閉理由寫的是「對照完成」,不是「凍結已做到」。Verification 自己寫了「原始四場全 invalid…補齊正常 fixture 與精確標準尾段支持後對四場一致重算」。也就是看過模型輸出後才改評分器,而「先凍結控制」那批控制沒涵蓋 normal 模式與 main 尾段這兩種最自然的寫法。評分器改動對兩臂一致,平手結論不受影響。但標題「預先凍結」與關閉理由和事實有落差。

ID: GEN-9
severity: minor
blocking: 否
引句:「取鎖等待兩秒時由fixture捕捉 TimeoutError，轉成具體 AssertionError: lock-enter-incomplete」
審材外佐證 file: `scripts/lumos@2b4cb7ce:24644`
審材外佐證 file: `governance/eval/historical_handbook_trial.py:117`

fixture 用 SIGALRM 丟 `TimeoutError`,而 `TimeoutError` 是 `OSError` 的子類。錯版的 `_excl_lock_try`(`scripts/lumos@2b4cb7ce:24644`、24650 起)有多處 `except OSError`。若 alarm 剛好落在這些 try 區段,例外會被吞掉,迴圈繼續到 60 秒上限,子程序 15 秒逾時,真檢出變 invalid。我連跑 60 場(8 並行)沒遇到。發生率我無法量化 ⚠;機率在迴圈 sleep 佔絕大多數時間下很低,但機制成立,且只會影響本來會被檢出的測試。

ID: GEN-10
severity: minor
blocking: 否
引句:「[manual:執行固定入口並核對四組明細]」
審材外佐證 file: `governance/eval/historical_test_quality.py:102`
審材外佐證 file: `governance/eval/historical_test_quality.py:106`

S1 和 S3 的人工驗收步驟都沒寫入口路徑、Python 版本、`--out` 必須是全新目錄,要靠 `lands_in` 的筆記才查得到。`report.json` 沒記 Python 版本、OS、uid 這類環境資訊,而判定依賴 `_trusted_private_dir`(owner 與 group/other 寫入權限)的行為。`historical_file` 用 `git show` 需要完整歷史,淺 clone 會直接拋 `CalledProcessError`,不是列成 invalid。腳本對 S2 要求的欄位大體齊備(提交、檔案 SHA、runner SHA、instrument、原始輸出)。

**其餘各節**
- 「目的與最小試行」:引句中的提交 SHA、日期、版本號與 `historical_test_quality.py` 的 `VERSIONS` 吻合,SHA 與日期一致(2026-09-16)。
- 修復版 810beb93 為單一提交,diff 確實含鎖退路修復與假測試修正,與 spec 敘述相符。
- 「回退」:已讀,無 finding。
- 「案例資格結果」:12 組我重跑全 qualified,與 spec 敘述一致。
- 三個 Verification 連結、`Systems/historical-test-quality` 皆存在。
- 「模型對照預先凍結」中:`claude-opus-5-5`、effort low、Read-only、順序 control/handbook 與 handbook/control、一個 python fence、無回饋,都與 `run_model` 的 `--effort low`、`--tools Read` 和 repeat 順序吻合。
- 「模型對照預先凍結」中:`--safe-mode` 排除自訂 CLAUDE.md、skills、hooks,所以沒有手冊從別的管道漏進控制臂的跡象。

**實務隱患**
- **併發:** 無。每場評分是循序子程序,各自獨立 tmp 目錄與 HOME,SIGALRM 只在單一子程序主執行緒使用。唯一的競態是 GEN-9。
- **效能:** 見 GEN-2。corpus 約 18 秒、單案 preflight 約 9 秒,沒問題。
- **資源:** 暫存目錄由 `TemporaryDirectory` 清掉,逾時子程序由 `subprocess.run(timeout)` 殺掉。模型階段的額度與時間(180 秒逾時、opus 5.5)spec 沒寫,但已知單場不大。
- **回滾:** 輸出只寫到全新 `--out` 目錄,不改 production,可直接撤提交。中途中斷會留下半成品目錄,下次要換新目錄。無問題。

總結最嚴重 severity: major;blocking 共 4 條
