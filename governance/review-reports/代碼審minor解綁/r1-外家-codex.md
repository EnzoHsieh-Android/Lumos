severity: major

解除 minor 的連帶必修有助於減少修補，但這版把「哪些條目可以放行」換成「有多少放行額度」，仍可能讓未修的 major 過閘。以下為完整閱讀凍結設計、核對程式與記憶體內實驗後的發現；未寫入任何檔案。

**F1．數量配平不能阻止 major 借用另一條 minor 的額度**

severity: major
blocking: 是
引句:「這擋的是數量,不保證每條對應正確;對應正確靠收貨紀錄與審查。」

可重現推演：

- 原報告有 A＝major、B＝minor；席級 severity 忠實記 major，原報告不修改。
- 載體把 A、B 都標 minor，`folded={B}`、`accepted={A}`，理由齊備。
- 分子為 1，報告的 minor 分母也是 1，數量檢查通過；逐條檢查也因 A 被標 minor 而通過。
- A 沒有修、沒有反證，也沒有登記降級，卻能通過新的處置集合判定。既有規則會因輪內 major 與非空 accepted 擋下。

讀碼確認，`finding_severities` 目前只驗值域與鍵集合完整，沒有驗每個 ID 的原始評等；報告綁定只驗席級最高值，所以以上資料不會撞到低報守衛。

file: `scripts/lumos:10865`
file: `scripts/lumos:10976`
file: `scripts/lumos:27144`

應讓每個 accepted ID 連回原報告 finding，保存原始／有效評等；原始 major 的有效評等若變低，必須有該條裁決證據。其他 minor、已折入或已反駁項目不能提供可轉讓額度。這正是先前診斷要求的逐條來源與證據鏈。

file: `governance/review-reports/收斂診斷/codex-gpt-6-astra.md:225`

**F2．降級清單的驗收條件不足以證明辯方真的作出有證據的降級**

severity: major
blocking: 是
引句:「辯方附證據把某條原報 major 的發現降成 minor 時記。」

這句宣稱要有辯方證據，後面的機械條件卻只要求 ID、有效評等、四字理由及 intake 同列命中。

最小反例：原報告只有 A＝major，載體填 A＝minor、accepted A，降級理由填「影響範圍有限」，intake 寫一列 `A | HIT | 已重現問題`。這些資料符合列出的驗收條件，但 HIT 證明的是原問題成立，完全沒有反證。分母因降級清單增加 1，A 因而可以放行。

現有 `refuted-set` 同列檢查接受 `HIT/MISS/重現/採信` 任一字樣，不驗裁決者、反證內容或證據指標；照它移植，不能得到設計宣稱的證據守衛。既有 `refute_verdicts` 又是選填，省略即可避開 agree／concern 必須折入的一致性檢查。

file: `scripts/lumos:10803`
file: `scripts/lumos:10813`
file: `scripts/lumos:10888`
file: `scripts/lumos:10922`

應要求降級項連到原 finding、獨立辯方的 evidence 裁決與可核對反證；缺件、只有 concern、只有重現成功，均維持原評等。既有辯方規則及先前診斷都明確要求這個界線。

file: `skills/lumos-code-loop/reference.md:101`
file: `governance/review-reports/收斂診斷/codex-gpt-6-astra.md:244`

**F3．把 clean 宣告算進分母，會把「沒有問題」變成放行額度**

severity: major
blocking: 是
引句:「去掉檔級那行後,數 minor 與 clean 的宣告行」

`_report_severities` 只回傳宣告值，不判斷該段是不是 finding。既有 `_report_reported_count` 則明確排除 clean。

記憶體內實跑一份含「A＝major」及「已驗過的檢查項＝clean」的報告：

- 正規化檢查：通過。
- 宣告解析：`[major, major, clean]`。
- 既有 reported：1。
- 設計的新放行額度：1。

把唯一真正 finding A 誤標 minor 並 accepted，就能用「已驗過、沒問題」那段取得額度。這不是只有人工構造的格式：現有歷史席報告有五個逐項 clean，各段都明寫「已讀,無 finding」。

file: `scripts/lumos:10069`
file: `scripts/lumos:10252`
file: `governance/review-reports/code-test-quality-native-push/r2-歷史-codex.md:3`
file: `governance/review-reports/code-test-quality-native-push/r2-歷史-codex.md:31`

應排除無 finding 的檢查結論；若某條原 finding 經裁決成 clean，應走該 finding 的裁決關聯，不能把任意 clean 宣告當成另一條問題的額度。

**F4．設計誤認 latest 的含義，指定的去重鍵也不等於每席最新報告**

severity: major
blocking: 是
引句:「分母:同輪各席最新一筆帳」
引句:「同一席同一份報告只算一次」

現行 `_disposal_round_groups` 把同輪所有列追加進清單；處置閘取得的 `latest` 是「最後一輪的全部列」，沒有按 auditor 取最新一筆。

`_review_yield_round` 使用 `(auditor, report_sha256)` 去重，因此：

- 同席 A 先記報告 h1，再記 h2：兩份都算。
- 同一報告 h1 分別掛 A、B 席：也算兩次。

記憶體內實跑同席 h1、h2、h2 三列，`latest` 長度為 3，去重後計數為 2；不是設計所說的每席最新一份。不同席掛相同 hash 的結果也為 2。

file: `scripts/lumos:26821`
file: `scripts/lumos:27077`
file: `scripts/lumos:10258`

若照「沿用 latest 與既有鍵」實作，同一條 minor 的報告修訂版就會累積額度；多席撞題也會累積額度，足以掩護錯標或拆出的 accepted ID。若另寫「每席只取最後一筆」，則已經不是現有 latest 語意，還須說明早先 major 報告如何保留其處置義務。

應明定報告替代關係及原 finding 身分；同席重記、報告修訂、多席同題、單條拆 ID 都不能憑空增加可放行範圍。既有鍵適合計算報告產出量，不能直接升格為放行授權。

**F5．測試缺口是否阻擋，被不當綁到有沒有登記合約／驗收測試**

severity: major
blocking: 是
引句:「受影響的是合約行(★INVARIANT★ 等)或計劃驗收條款綁的測試、而且能舉出一個合理的改壞照綠 → major;一般測試完整度的改善 → minor。」

照這個新增門檻，一條修 bug 必要的回歸測試，只要沒有綁到圖譜合約或計劃條款，即使還原原缺陷仍綠，也不符合列出的 major 條件。

具體推演：修補某個漏拒非法輸入的錯誤，新增測試卻 mock 掉真正的驗證函式；還原原 bug，測試仍綠。這是修補聲稱具備的回歸證據失效，不能只因測試沒有 `[test:]` 綁定而歸入一般完整度改善。

既有手冊明確允許非合約級實作測試只進測試套件、不硬掛圖譜，同時要求修 bug 具備還原翻紅證據。新條件會讓合法的測試存放方式改變缺口嚴重度。

file: `skills/lumos-code-loop/reference.md:108`
file: `skills/lumos-code-loop/reference.md:114`

應按「必要行為保護是否失效、能否指出具體合理退化」判斷；綁定欄位可以提供依據，不能成為 major 的必要前提。先前診斷用的是「關鍵合約或具體合理退化」，並未限定已登記綁定的測試。

file: `governance/review-reports/收斂診斷/codex-gpt-6-astra.md:236`

**F6．不區分判定版本，會使計劃自己的回退流程產生假的邏輯漂移**

severity: major
blocking: 是
引句:「改回後,上線期間在 major 輪放行過 minor 的迴圈會判不過,要改折入重記或攤人裁。」

設計要求新舊制度沿用 `_REPLAY_ENGINE_REV`，回退又只改回判定條件。可重現的時間序列是：

1. 新制下，major 已折、minor accepted 的輪通過並凍結，記 rc＝0。
2. 按本計劃回退到舊制。
3. 對該凍結檔執行 replay：引擎版本相同，程式直接重算；舊制得到 rc＝1。
4. replay 把這次已授權的制度回退報成「邏輯漂移」。

現行程式明確用引擎版本區分「制度已演進」與「同制度判定漂移」；版本相同而 rc／fails 改變就報錯。

file: `scripts/lumos:10024`
file: `scripts/lumos:1224`
file: `scripts/lumos:1250`
file: `scripts/lumos:1267`

應為新制及回退建立可辨識的判定版本，或保留按版本回放的路徑。只確認今天既有 golden 沒命中新分支，不能支持未來仍共用版本。

本次確實未找到既有凍結**判定輪**會因新分支改判的案例。另外，設計聲稱舊帳沒有這種載體並不精確：`code-規格閘半套` r1 已有 major、逐條評等與 accepted minor；只是它凍結的是 r3，因此不能拿 r1 宣稱整份 golden 現在就會變判。

file: `docs/.canary-log.jsonl:1628`
file: `governance/replay/code-規格閘半套/verdict.json:9`

其餘鏡頭判讀：文件不一致那條保留了「會導致錯誤操作／合約衝突」的 major 條件，未找到同等明確的降級洞；第二種寫法維持架構席既有裁定，不能宣稱本案也完成了先前建議的架構尺度統一。解除 minor 連帶必修能增加合理停止的選項，但目前不能由放行件數推出輪數或總成本改善；更不能省略先前診斷要求的獨立查證及缺證維持阻擋。

本次派工未附固定席節點清單，無該段逐條裁定對象。已核對 d2、散文 d5 及試行生效資料，未修改圖譜。

總結：最嚴重 major；blocking 共 6 條。
