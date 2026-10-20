severity: major

# 架構對齊審查報告(架構對齊-sonnet)

審材:`r1-snapshot.md`(凍結版)。我只對照既有程式與筆記,看設計跟專案做法一不一致,不找 bug。

白話先說:這份設計大半是照現有的家規走的,例如閘門排在表態閘旁邊、同一支判定函式、輸出形狀沿用 `security list`。但有兩處會讓專案裡多出第二套做法,另有幾處只是沒寫明該用哪支既有函式。

我沒有動工作樹,也沒建臨時目錄,所以沒有東西要刪。

## 問 1:分層與依賴方向

**finding 1(圍欄讀法)**
- 設計把 `lumos-evidence-v1` 寫成獨立的一支讀法,沒說要共用 `_fence_regions`。
- 既有的 `_secinv_blocks` 把圍欄標記寫死成 `lumos-security-v1`。依設計,證據圍欄多一套標記、放置規則和未閉合判定。
- `Systems/lumos-cli-read` 第 16 行有現成的決策:另寫一份 toggle 或正則就是第二套邊界判定。
- 修法很小:把 `_secinv_blocks` 改成吃標記參數,把「只准放哪」做成參數。
- 引句:「是另一種圍欄、另一支讀法」
- file: `scripts/lumos:6720`(`_secinv_blocks`),`scripts/lumos:4990`(`_fence_regions`),`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:16`
severity: major
- blocking: 是

**finding 2(閘門呼叫 test_quality)**
- 設計要閘門自己重讀 capture,並沿用 `junit()`、`load_receipt` 和 `check()` 的三階段核對。
- `scripts/lumos` 現在碰 test_quality 只有兩條路:`main()` 啟動時載入帶雜湊驗證的配套,以及 `dispatch` / `add_parser` 的子命令入口。code-loop 的判定函式從沒直呼過它的內部函式。
- 所以設計等於新增一條「推送閘 → 可選配套」的依賴,卻沒回答三件事:
  - 配套缺檔(`_test_quality_load_bundle` 回「部署不完整」)時,閘門是擋還是放。
  - 抽出「只吃資料的核對函式」會改 `test_quality.py`,而 `_TEST_QUALITY_BUNDLE_DIGESTS` 要跟著更新。
  - 抽出的函式放哪一層。
- 這是跨層直呼,又沒有失效行為。
- 引句:「閘門自己重讀三份 capture 目錄,重跑同一套 load_receipt 與三階段核對,不採信作者存的 check 結果檔」
- file: `scripts/lumos:58684`,`scripts/lumos:58730`,`scripts/lumos:58763`,`scripts/lumos:59878`
severity: major
- blocking: 是

**finding 3(從提交讀盤點)**
- 設計說「用 git 讀起點那一版的筆記,跑同一支盤點函式」,S4 又要求閘的輸入等於 `security list --json`。
- 但 `_secinv_snapshot` 只會從工作目錄逐層 `dir_fd` 開檔。`_secinv_build` 吃的是 `snap` 字典,所以接縫在這裡,只是設計沒寫出「從提交樹產 snap」由誰做。
- 專案已有 `_drift_tree_env`(從提交樹建 `Env.from_texts`),但它沒有 `security list` 那套容量上限和變動偵測。
- 若實作者各寫一條,就會長出第三條快照路徑。
- 設計應寫明:從 git 產 `snap`,沿用同一組容量常數,並說明讀不全時怎麼進 `errors`。
- 引句:「用 git 讀起點那一版的筆記,跑同一支盤點函式,得到起點的必驗集合」
- file: `scripts/lumos:6660`(`_secinv_snapshot`),`scripts/lumos:7250`(`_secinv_build`),`scripts/lumos:41882`(`_drift_tree_env`)
severity: minor
- blocking: 否
- 這條在 major 與 minor 之間拿不準,請編排者裁。

## 問 2:命名與錯誤處理

**finding 4(擋下訊息形狀)**
- 設計的「訊息形狀」只有三塊:一行擋下、下一行說怎麼修、最後一行指路。缺中間「為何在意」那段。
- 同族的 `_cl_say_disp_block` 和 `_cl_say_lint_block` 都是三段式,各自有專屬函式。
- 設計只說在 `_cl_say_block` 加一句「專用句」,沒說要不要另開 `_cl_say_sec_block`。
- 原因代碼 `<判定>:<代碼>` 和 `reason_kind: security_evidence` 的命名與既有一致,不用改。
- 引句:「下一行白話說怎麼修」
- 引句:「安全證據擋下跟風險分級無關」
- file: `scripts/lumos:57932`,`scripts/lumos:57952`,`scripts/lumos:57921`
severity: minor
- blocking: 否

## 問 3:第二種做法

除了 finding 1 與 2,還有兩處:

**finding 5(沒指名既有共用函式)**
- 設計要的這些能力,lumos 裡都已有共用函式,設計沒指名:
  - 讀提交內檔案:`_lens_git`、`_nodehome_git`。
  - 嚴格 JSON(拒重複鍵與 NaN):`_secinv_json_loads`。工具清單、證據圍欄、k6 摘要都該走它。設計只寫「標準庫嚴格解析」。
  - 治理帳讀取:`_ledger_lines`。
- 驗章用的 `git log --format=%G?` 還有一個已知坑:使用者設了 `log.showSignature` 會把 gpg 訊息夾進輸出。`scripts/lumos:38540` 的註解寫了這件事,設計沒提。
- `git verify-commit` 和 `git blame` 在 lumos 裡是第一次出現,沒有第二套的問題,但要走統一的 git 包裝。
- 另外,`.lumos/security-tools.json` 的現有對照是 `_lint_load_config`,但它在解析失敗時靜默回 `None`。設計若照抄,壞清單就會被當成沒有清單。要寫明用嚴格讀法,且從要推的提交讀。
- 引句:「找出最後改到那幾行的每個提交」
- file: `scripts/lumos:52501`,`scripts/lumos:34166`,`scripts/lumos:6688`,`scripts/lumos:15224`,`scripts/lumos:32078`,`scripts/lumos:38540`
severity: minor
- blocking: 否

**finding 6(SARIF 另寫嚴格解析)**
- 這是有意的第二種做法。設計附了對 `_lint_run_and_parse` 的查證:`scripts/lumos:32586` 會 `Popen`,`:32615` 接受 SARIF 1.0,`:32621` 缺 driver 名就跳過,`:32623` 把 null 當空陣列。我逐行核對過,屬實。
- 理由成立,不計入 major。
- 但「抽 uri 正規化,抽不乾淨就兩邊各寫」留了第三種可能。建議在實作前先決定抽或不抽,別留給實作者臨場判斷。
- 引句:「新寫一支只吃資料的嚴格解析給安全證據用;新增告警閘的既有行為一字不改」
- file: `scripts/lumos:32553`
severity: minor
- blocking: 否

**finding 7(待決問題與決策引用的解析)**
- 設計新增 `question_refs`,格式 `<節點>#Qn`,並判「已決或已驗」。專案已有 `_pq_decision_state` / `_pq_decision_target`,管 `節點#dN` 的解析與翻案判定,`guard-kill` 的殘留指標也共用它們。
- 設計沒說 `question_refs` 與 `decision_ref` 的解析是否走同一支。
- 另外,`_secinv_check_exception` 已存在,例外欄位擴充是在它上面長,這點一致。
- 引句:「工具不從文字猜是哪一題」
- file: `scripts/lumos:8762`,`scripts/lumos:8795`,`scripts/lumos:7138`
severity: minor
- blocking: 否

## 問 4:落點

**finding 8(沒有新子系統的家)**
- `lands_in` 列的五篇都是既有節點。這份計劃新增的東西有:證據圍欄讀法、六種格式的判定、工具清單、簽章核可與公鑰清單,以及閘門步驟。它們分散到各篇後,沒有任何一篇會有完整的說明。
- 只有 `security evidence` 放 `Systems/lumos-cli-read` 確定合理,因為 `security list` 就在那裡。閘門步驟放 `Systems/pitfalls-code-loop` 也合理。
- `pitfalls-code-loop` 已有 20 行 KEY,再塞簽章核可會更擠。建議評估另開一篇(例如「安全證據閘」),寫明負責範圍,其餘五篇只放連結。
- 同族閘的家沒列入:`Systems/棧別提問表態閘` 有表態閘的判定函式,`Projects/推送前一次列出全部擋下原因_計劃` 的對照表要從四句改五句,這些牽連的筆記也沒進 `lands_in`。
- `scripts/test_quality.py` 屬 `Systems/test-quality-cli`,抽函式的改動落那裡是對的。
- 引句:「那一行要先改成五句的正本」
- file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`,`docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md`,`docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:68`
severity: minor
- blocking: 否

## 對齊的部分(不計 finding)

- 閘門並列在 `_codeloop_lint_new_step` 與表態閘旁,用 `kg.hit`、不看 tier,形狀一致。
- 閘門排在放行早退之前,理由有查證,錯誤分支也都有指名。
- `security evidence` 另開子命令而不改 `security list` 契約,與盤點的唯讀保證一致。
- 本機算背書、寫進治理帳、CI 只讀治理帳,沿用 `scripts/lumos:57762` 註解說的表態閘做法。
- 例外到期用 `_secinv_today` 做測試接縫,沿用既有慣例。

不對齊共 8 條,其中 major 2 條。
