severity: blocker

### f1 表態閘 CI 路徑訊息改成跟既有機制相反
severity: blocker
blocking: 是
引句:「改成講清楚 CI 讀的是標記檔、治理帳是本機備援」
scripts/lumos:21379、21421-21449 的既有設計是先寫治理帳、CI 端靠 `_codeloop_read_dispositions` 讀治理帳 fallback 重建,governance/.gitignore:9-10 明寫 marker 目錄「committer 一提交 HEAD 就移動→自作廢,本機守衛用,不版控、不跨機當權威」,calc-ios 驗證節點(`docs/calc-ios-knowledge/Verification/2026-09-09_Lumos的iOS支援首次真專案驗證.md:57`)也獨立寫著「表態閘在 CI 端是靠讀治理帳重建的」。計劃卻要把「治理帳是 CI 唯一讀得到的地方」判成錯訊息、改講成「CI 讀的是標記檔」,並要文件教人提交那個依設計不該提交、一提交就自失效的標記目錄。實作照這份計劃寫下去,產出的訊息與文件會跟既有機制互相矛盾,而且指示的動作技術上不會生效。

### f2 -only-testing 缺類別段的靜默沒有修復項
severity: blocker
blocking: 是
引句:「在計算機專案上重跑一次，四道靜默都變成有聲音」
「要做什麼」[A]-[E] 與驗收條款 [S1]-[S6] 全文找不到任何一項處理「-only-testing 少寫類別段」這件事——沒有對應的修復動作,也沒有對應的 `[test:]`。但 summary 與 [S6] 都寫「四道靜默都變成有聲音」,等於宣稱四個問題全接住,實際只接住①③④三個。這是計劃自己列的範圍(四道靜默)跟自己收尾宣稱(四道都有聲音)之間的內部不一致。

### f3 about_code 提醒噪音已超過計劃自訂門檻
severity: major
blocking: 是
引句:「健檢新增的三段提醒對既有專案可能一次冒出很多條」
對 `docs/lumos-toolchain-knowledge` 底下 35 篇帶 about_code 的節點逐一核對(正文是否以反引號寫出自己 about_code 列的路徑),至少 29 篇沒有,例如 `Verification/2026-07-10_guard殺傷力驗證.md` 的 about_code 只在 frontmatter 出現、正文完全沒提。REVISIT:2026-10-09 把這件事框成「以後去看冒幾條」,但套用計劃自己定的門檻(超過十條要收斂),現在——這份計劃連實作都還沒開始——就已經超標三倍,不是等之後才會發生的風險。[C] 一旦照原樣上線,本 repo 自己的 `lumos doctor` 會先被這批新提醒淹過去。

### f4 no-pins 狀態把 vault 找不到誤判成無節點引用
severity: minor
blocking: 否
引句:「沒有節點引用／有節點但沒綁測試」
scripts/lumos:20938-20944 顯示 `_bound_tests_for_diff` 在 `pins` 為空與 `vault is None`(vault 完全找不到)兩種不同情況下回的是同一個 `no-pins` 狀態。[E]/[S4] 只準備了「沒有節點引用這些檔」與「節點沒綁測試」兩種訊息,沒有第三種涵蓋 vault 找不到。真的發生 vault 找不到時(例如跑錯目錄、專案還沒 init),使用者會被告知「沒有節點引用這些檔」,誤以為圖譜正常只是沒覆蓋到,而不是環境本身有問題。

### f5 猜棧骨架的確認提示未進驗收條款
severity: minor
blocking: 否
引句:「依副檔名猜棧，多語言 repo 會猜到其中一個」
[S1] 只要求「偵測不到時寫出帶說明的骨架」,沒有把實務隱患段承諾的「猜到的骨架要帶確認提示」寫進驗收條款或 `[test:t_init_writes_config_skeleton]`。也就是說即使猜對副檔名、寫出看似正確的骨架,也沒有機制強制它帶上「這是猜的,請確認」。多語言 repo 猜錯棧時,使用者拿到的會是一份沒有任何確認提示、看起來很篤定的錯誤骨架。

最嚴重 severity: blocker，blocking 條數 3
