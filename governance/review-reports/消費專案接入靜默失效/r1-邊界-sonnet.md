severity: blocker

### f1 兩條 REVISIT 寫在句子中間，doctor 的到期掃描抓不到

severity: major
blocking: 是
引句：「健檢新增的三段提醒對既有專案可能一次冒出很多條。REVISIT:2026-10-09 看本 repo 與計算機專案各冒幾條，超過十條就要想辦法收斂或分批。」
doctor 的 Check E5（回訪到期）判準是「strip 行首空白與 - / * 列表前綴後以 REVISIT: 開頭」，見 file: `scripts/lumos:1811` 與實作 `scripts/lumos:1828`（`if not _l5.startswith("REVISIT:")`）。本篇兩條 REVISIT（本行、以及 r1-snapshot.md 第 81 行）都接在同一個項目符號的敘述句尾巴，strip 後那一行仍以「- **既有專案**：…」開頭，不是「REVISIT:」開頭，doctor 永遠掃不到、到期也不會被唸。這正是「回頭條件寫下來但接不了電」，而不是本篇宣稱的機制化回頭看。

### f2 S4 要塞的訊息會被 pre-push 自己的關鍵字過濾器吞掉，DEP 也沒點名真正要改的三個位置

severity: blocker
blocking: 是
引句：「合約測試閘回零覆蓋時印出原因（沒有節點引用／有節點但沒綁測試），不再完全靜默；既有的綠／紅／跳過訊息不變」
no-pins/no-bound 目前在三處都是純靜默：`cmd_bound_tests` 只處理 red/green/whole-suite-deferred 三種狀態就結束，其餘狀態直接 `return 0` 不印一行（file: `scripts/lumos:21215`-`scripts/lumos:21220`）；`lumos code-loop check` 非阻擋時只印「✅ …OK」加 dispositions 小結，完全不提 bound_tests 狀態（file: `scripts/lumos:22100`）；而 pre-push 對 `code-loop check` 的非阻擋輸出還會先用 `grep -E '提醒|受波及合約測試|表態閘'` 過濾一次才顯示（file: `scripts/hooks/pre-push:222`），新訊息若不含這三個關鍵字之一會被這層過濾器吃掉。DEP 只寫「scripts/lumos(cmd_init 的 scaffold 段、load_test_profile/load_symbol_profile 的 fallback 提示、doctor 新增一段 about_code 未接上檢查、_cmd_codeloop_dispositions 的錯誤訊息)」，三個真正要動的地方一個都沒點名，測試 t_bound_tests_explains_no_pins 若只打 `_bound_tests_check`/`cmd_bound_tests` 會通過，但 calc-ios 真跑 `code-loop check` 走 pre-push 那條路依然靜默，S6 驗收會在真專案上打臉。

### f3 profile 不符檢查只認「還在吃預設值」，抓不到「一個棧設對了、另一個棧沒設」的多語言 repo

severity: major
blocking: 是
引句：「但符號 profile 是 C# 預設），符合時不出聲」
S2 的觸發條件是「目前生效的 profile == 原始預設值 csharp」，`load_symbol_profile`/`load_test_profile` 的邏輯是整包單一 profile 名稱（`scripts/lumos:3186`、`scripts/lumos:3327`），沒有「這個副檔名完全沒有任何 profile/platform 涵蓋」這種判準。構造：一個 repo 同時有 .swift 與 .kt，`.lumos/config.json` 把 `test_profile`/`symbol_profile` 正確設成 swift 系列（不是預設值）——S2 不會觸發，因為現在生效的 profile 已經不是 C# 預設，但 .kt 檔案仍然完全零覆蓋且沒有任何提醒，比「整包吃預設」的情況更危險，因為看起來已經「設定過」。

### f4 S3「正文有提到該路徑」沒說用哪一套比對規則，若不是逐字比對反引號寫法，提醒會沉默地失效

severity: major
blocking: 是
引句：「節點標了 `about_code`，但連結是靠正文裡用反引號寫的路徑抽的」
波及計算的 code→node 反查明寫「只認 body inline-code」（file: `scripts/lumos:19091`，`_impact_reverse_lookup`），也就是正文用裸路徑或 `[文字](路徑)` 連結寫法都不算命中，這點被本篇自己在現象表裡點出來。但 [S3]／[C] 只說「正文有提到就不出聲」，沒有指定 doctor 的新檢查要用同一套「只認反引號」規則——如果實作換一套更寬鬆的比對（裸路徑或連結都算「有提到」），就會出現「about_code 沒接上、doctor 說沒事、bound-tests 仍然 no-pins」的組合，等於把本案要消滅的那種靜默重新做進解法本身。

### f5 多語言 repo 的骨架策略只挑一個棧「用猜的」，沒有用到工具已經有的多平台設定格式

severity: minor
blocking: 否
引句：「`lumos init` 依副檔名猜棧，多語言 repo 會猜到其中一個」
`scripts/lumos` 已經有成熟的多平台設定格式（`platforms`/`default_platform`，見 `load_platforms`，`scripts/lumos:3392` 起），正是為了同一個 repo 裡多個棧（例如 iOS 前端＋Node 後端）而設計，PRIOR-ART 也主張「最小解在既有機制層」。[S1] 對多語言 repo 只承諾「猜一個、標成猜的」，沒有把「偵測到 ≥2 個互斥的 code_exts 家族」接到既有的 `platforms` 骨架上，這件事本篇自己承認是限制、不是意外，所以不算新的靜默，但屬於捨近求遠。

最嚴重 severity: blocker，blocking 條數 4
