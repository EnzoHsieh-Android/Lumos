severity: major

### f1 ②「少寫類別段」的靜默沒有對應解法
severity: major
blocking: 是
引句:「少寫類別段，識別字對不到任何測試」
summary 的裁定行宣稱「四項全部是把靜默變成有聲音」,但「要做什麼」[A]–[E] 與「驗收條款」S1–S6 通篇沒有任何一項對到②(沒有 scaffold 產出的 run_cmd 格式驗證、沒有健檢檢查既有 run_cmd 是否缺類別段)。scripts/lumos 目前也沒有任何 `-only-testing` 格式檢查(全檔搜尋 0 命中),不是「已有別處覆蓋」而是真空。S6「四道靜默都變成有聲音」在②上因此無法達成。

### f2 ④的訊息修正方向與既有、附事故佐證的設計相反
severity: major
blocking: 是
引句:「且沒有任何文件叫人提交標記目錄」
`_codeloop_read_from_ledger` 明寫「governance/code-loop/ 被 gitignore,CI 的乾淨 checkout 一定沒有」,而且是為了修 2026-08-22 那次「marker 不在 checkout 而假紅」的事故才建的治理帳 fallback(file:`scripts/lumos:20801-20805`);governance/.gitignore 也把 code-loop/ 寫死排除,理由是「per-machine runtime 狀態…不版控、不跨機當權威」(file:`governance/.gitignore:9-10`)。[D] 卻要教人「標記目錄要提交」、把治理帳降級成「本機備援」,和這兩處既有、帶事故佐證的設計方向相反,DEP 清單裡也沒列這兩處,像是沒讀到就下了判斷。

### f3 [A] 技術棧偵測沒指名重用既有的副檔名對照
severity: major
blocking: 是
引句:「把測試 profile、符號 profile、測試指令的形狀先填好」
scripts/lumos 已有三張各自獨立的「副檔名→棧」對照(SYMBOL_PROFILES.code_exts、TEST_PROFILES.exts、`_stack_key_for_file`),其中 `_stack_key_for_file` 的 docstring 明寫「兩個消費者都走這一支,別各自抄副檔名邏輯」(file:`scripts/lumos:15254-15263`)。[A] 沒有指名要重用哪一張表,若另起一套獨立的「偵測技術棧」判斷,會是這條反重複邏輯家規的第三/四次違反。

### f4 REVISIT 事件式回頭條件沒寫入口
severity: minor
blocking: 否
引句:「或第二個非 C# 專案接入時回來補」
CLAUDE.md 鐵則 4 要求綁事件的回頭條件要「明寫事件入口在哪」,這行只講「第二個非 C# 專案接入時」,沒有任何登記機制記錄現在是第幾個(iOS 與 Node 後端補棧_計劃只留「首個接入專案回填」字樣,無計數器或檢查點)。本計劃自己連結了 [[Issues/寫下風險當成處理風險]],這行正落入該篇警告的「承認句沒有回頭動作」形狀。

最嚴重 severity: major,blocking 條數 3
