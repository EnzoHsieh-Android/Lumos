severity: minor

第1問 分層與依賴方向 對齊。第一層沿用「hook 只呼叫 lumos、判定全在 lumos 裡」這一條:鄰居 Gate H 的說明明講「判定全在 lumos 裡,這裡只呼叫」(`scripts/hooks/pre-commit:116`),提交前只吃 `home check --staged`(`scripts/hooks/pre-commit:124`)、推送前只吃 `home check --diff`(`scripts/hooks/pre-push:236`)。計劃第一層「入口」段落寫的正是同一形狀——提交前逐篇檢查旁加一道、推送前與 CI 對整段範圍再跑同一支指令(`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/loop/r1-work.md:49`),沒有把判定邏輯外洩到 hook 殼層。第二層真正會呼叫 AI 的那一步,計劃寫明是「編排的對話」派席(`.../r1-work.md:54`),不是 hook 或 lumos 內部發起——這與 code-loop 的既有分工一致:hook/CI 只呼叫 `code-loop check` 讀已經寫好的留痕、rc 判斷擋不擋(`scripts/hooks/pre-push:298-322`、`.github/workflows/ci.yml:113`),真正的審查(讀程式碼、判斷)發生在對話裡、事後用 `code-loop pass/skip` 把結論寫回(`scripts/lumos:30325-30334`)。`note-audit prepare` 只機械列行、`note-audit record` 只機械驗報告與寫帳,兩端都不越權去跑判定,依賴方向跟鄰居一致。

第2問 命名與錯誤處理:結構對,但有兩處鄰居明講、計劃沒講清楚。

## F1 rc 語意與治理帳事件欄位沒有明講
severity: minor
blocking: 否 —— 沒有引入新做法,只是規格描述比鄰居鬆,實作時才會撞到
引句:「若暫存區新增或改動的筆記行含程式行號引用,且不在程式碼圍欄內、也不是引句行,則提交應被擋下並列出每一處;同一篇沒改動的舊行含行號時不應擋」
file: `scripts/lumos:30281-30282`
file: `scripts/lumos:23259`
file: `scripts/lumos:20492-20496`
補充:鄰居每一個閘都在文件字串裡把 rc 語意寫死成一行——`cmd_code_loop` 開頭寫「rc: 0=OK / 1=check:blocked / 2=參數錯」(`scripts/lumos:30281-30282`),`cmd_home_check` 開頭寫「有新違規 rc1,沒有 rc0;沒有圖譜/合併中/開關 off 說一句跳過、rc0」(`scripts/lumos:23259`)。計劃的 S1–S8 條款只講「應被擋下 / 不應被擋下」,通篇沒有一次寫「擋=rc1、參數錯=rc2、環境壞=rc0 fail-open」這種對照,`lumos note-audit record` 要寫進治理帳的那筆事件用哪個 gate 名字、`kind` 用哪個字(鄰居的字彙是 blocked/passed/skipped-env/warned,見 `_gate_event_or_warn` 呼叫點 `scripts/lumos:30466`、`scripts/lumos:23354`)也沒登記。這不是引入了第二種做法,是這份設計計劃在「跟鄰居一樣把 rc 與事件欄位寫進規格」這件事上比鄰居鬆,實作的人得自己補。

## F2 第二層推送前查核是併進既有 check 還是另開一支指令,計劃沒定案
severity: minor
blocking: 否 —— 兩種鄰居寫法都存在(code-loop 把多個關切點折進同一個 verdict;home check 另開一支平行呼叫),計劃留了空,不是矛盾
引句:「推送前與 CI 查:範圍內有新增筆記行、卻找不到指紋對得上的通過紀錄,就擋。沒有新增筆記行的推送直接放行。」
file: `scripts/lumos:30342-30470`
file: `scripts/hooks/pre-push:234-245`
補充:`code-loop check` 的既有做法是把「表態閘」「受波及合約測試」「tier=high 缺留痕」三個獨立判定折進同一個 verdict,一次呼叫印出三種不同的擋法(`reason_kind` 分支見 `scripts/lumos:30359`、`30376`、`30396`);另一種鄰居做法是像每支檔有家那樣完全另開一支平行呼叫(`scripts/hooks/pre-push:234-245` 的 `home check --diff` 跟後面 `code-loop check` 是兩段獨立程式碼)。計劃第二層第 5 步只講「推送前與 CI 查」,沒有講這查核要嘛是 `code-loop check` 多一種 `reason_kind`、要嘛是新開一支 `note-audit check` 平行呼叫——兩種都是本 repo 既有形狀,選哪種只影響 pre-push/ci.yml 要改幾行,不算引入陌生做法,但影響實作落點,值得請編排者定案。

第3問 第二種做法 對齊,沒有找到憑空冒出來的新機制。兩個關鍵設計點在本 repo 都有既有先例可對照:
(1) 治理帳「通過」紀錄綁「這批新增筆記行」的內容指紋、不綁 commit sha(`.../r1-work.md:56` 附近)——這正是 `lint-waive` 的既有先例:「放行綁指紋不綁版本:綁版本的話每次提交都要重新放行,吵到沒人會用」(`scripts/lumos:20492-20496`);跟 code-loop 的 sha 綁定(`scripts/lumos:30327-30332` 「這筆紀錄只認目前這個版本」)是兩種本來就並存的綁定方式,計劃選的是前者,不是第三種。
(2) 附程式位置的判定要機械核對「檔案真的存在、行號沒超出檔長」(S6,`.../r1-work.md:70`)——這正是既有的引用核對機制:design-loop 的 G1 settle 閘核對「文件裡的檔案/行號引用對不對」(`scripts/lumos:9393-9396`、`10183-10199`),以及 quote-check 對報告與帳面指紋核對、報告佚失或指紋不符就拒收(`scripts/lumos:7591-7742`)。
(3) 申訴要另派一席不知道前一席結論的獨立審查員、兩席都判脈絡才算數(S7,`.../r1-work.md:55、71`)——這對應 design-loop 既有的多席交叉判定與爭議狀態(`resolved/accepted-minor/disputed-major`,`scripts/lumos:7088、8571-8609`),不是自創的爭端解決流程,而且跟 lint-waive「作者自己寫理由就放行、事後統計」那種自證式逃生門明顯不同——這裡刻意不採用自證式,因為要防的正是「作者自己說是脈絡就過」,採用既有的獨立交叉判定合乎判定者本身不可靠的前提。
沒有看到新的對外服務依賴(判定者是對話內派的既有審查席型態,計劃自己也把「對外送出」列為已排除,`.../r1-work.md:36`)、沒有新的逃生環境變數(逃生路徑沿用既有 `git commit/push --no-verify`,`scripts/hooks/pre-commit:15-16`、`scripts/hooks/pre-push` 逃生文案)。

第4問 落點 對齊,新開 Systems/筆記內容閘合理。「每支檔有家」自己宣告的負責範圍是「程式檔歸屬與寫回落點的提交前、推送前檢查與健檢舊帳三段;不管節點內容好壞,也不管設計審出口」(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:6`)——明文排除了「節點內容好壞」,而這份計劃管的正是節點內容(筆記行是不是程式碼推得出來),照它自己的責任邊界不該塞進去。`Systems/pitfalls-code-loop` 的整篇摘要圍繞代碼風險分級與代碼審留痕(`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:21-30` 一帶),管的是「這次改動的程式碼有多危險」,不是「筆記寫的內容是不是程式碼推得出來」,範圍也不重疊。`Systems/bound-tests-gate`(CLAUDE.md 提到的測試子集規則)管的是測試怎麼跑,更不相關。計劃自己在 frontmatter 就寫「lands_in: Systems/筆記內容閘」且派工詞附註「還不存在(要新開)」(`.../r1-work.md:10-11`),與既有節點的責任邊界互不重疊,開新節點是合理落點而非另立門戶架空既有節點。

不對齊共 2 條,其中 major 0 條
