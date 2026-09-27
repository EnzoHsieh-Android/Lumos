severity: major

第1問 對齊:新機制的分層跟鄰居一樣——判定全放在 `scripts/lumos` 裡,hook 只負責算範圍字串、呼叫、轉譯回傳碼,doctor 只讀不改。這跟 `cmd_home_check` 的分層完全同款:`scripts/lumos:23258-23261`(docstring 明講「判定全在 lumos 裡」)、`scripts/hooks/pre-commit:122-126`(提交前只呼叫 `home check --staged`,依 rc 決定 exit)、`scripts/hooks/pre-push:216-244`(推送前先在 hook 層算出 `_hrange` 字串,再呼叫 `home check --diff`,依 rc 決定 exit)。計劃裡「新分支起點」那段演算法(範圍與行小節)跟 `scripts/hooks/pre-push:222-233` 現有那段逐字同構(不在遠端分支上的最早提交、取上一個提交、真的全新才用空樹),顯示是照抄既有分層位置,沒有把判定下放到 hook 或上提到別的層。doctor 加一段檢查消費專案 CI 有沒有呼叫 `note-shape --diff`、並列出上線後違規,方向跟既有「doctor 印一行提醒 + 健檢舊帳」的唯讀分層一致(`scripts/lumos:999` node_home.gate 提醒;`scripts/lumos:23315-23319` cfg 從被檢查版本讀、doctor 類推同一分層)。此問對齊,沒有發現。

第2問 命名與錯誤處理:大部分跟鄰居一致。回傳碼 0/1/2 對齊 `cmd_home_check` 的 rc 慣例(`scripts/lumos:23266` 非 git 環境回 2、`scripts/lumos:23283` 範圍參數錯回 2、`scripts/lumos:23358` 新違規回 1);環境變數 `LUMOS_SKIP_NOTE_SHAPE` 命名對齊 `LUMOS_SKIP_LINT_NEW`(`scripts/lumos:21479`);設定值集合 `block/warn/off` 正確對齊 `_LINT_NEW_GATE_MODES`(`scripts/lumos:20935`)而不是誤用 `node_home` 的 `on/warn/off`(`scripts/lumos:22177`),挑對了最近鄰;閘名要登記進 `_KNOWN_GATES`、事件走 `_gate_event`,跟既有動態閘名檢查一致(`scripts/lumos:6586-6600`、`scripts/lumos:898-902`)。但事件的 kind 詞彙與「off/warn 都要寫帳」這件事跟兩個被引用的最近鄰實際行為不符,見 F3。

## F3 off/warn 模式落治理帳事件的詞彙與時機跟兩個引用鄰居的實際行為不一致
severity: minor
blocking: 否 —— 結構(閘名登記、_gate_event 呼叫、回傳碼)都對,只是 kind 值與「要不要寫帳」跟鄰居不同,屬於命名/日誌層級的落差
引句:「每次印一行、每次放行寫一筆 skipped 事件」
file: `scripts/lumos:23317-23319`(node_home.gate 設 off 時只 print 加 return 0,完全沒有呼叫 `_gate_event_or_warn`——不是每次放行都寫帳)
file: `scripts/lumos:21478-21481`(lint_new 設定檔 off 或 `LUMOS_SKIP_LINT_NEW` 時只設 `status/reason`,`out["autopass"]` 維持預設 `False`)
file: `scripts/lumos:30110-30111`(呼叫端只在 `lv.get("autopass")` 真為真時才呼叫 `_gate_failopen`——所以 lint_new 的 config-off/env-skip 一樣不落帳,只有真正環境壞掉的 autopass 分支才落帳,kind 是 `fail-open` 不是 `skipped`)
兩個被計劃引為 PRIOR-ART 的鄰居,「人主動設定 off/warn」都是靜默的,只有「環境真的失效」才落帳,而且用的詞是 `fail-open` / `skipped-env`,沒有裸的 `skipped`。計劃卻要求 off/warn 每次放行都寫一筆 `skipped` 事件,跟兩個鄰居的實際行為都對不上。

第3問 有沒有引入專案裡原本沒有的第二種做法:範圍演算法完整借用 home check 既有算法(見第1問),程式檔判定借用 `_is_code_file`,圍欄判定借用 `_visible_lines`,這三處對齊、沒有問題。但兩處另起爐灶,見 F1、F2。

## F1 `[src:]` 標記名稱與既有機制衝突,S2 規則跟既有的 FACT 佐證檢查是重複機制
severity: major
blocking: 是 —— 沿用一個已經有不相容語意的既有標記名稱,且另建一套新指令重做「檢查前綴有沒有帶合格佐證」這件事,而不是延伸已經掛在 `lumos lint` 上在跑的既有機制,屬於引入第二種做法
引句:「現況類前綴沒寫出程式碼答不了的來源」
file: `scripts/lumos:4269-4270`(`SRC_REF_RE = re.compile(r"\[src:\s*([^\]]+?)(?::(\d+(?:-\d+)?))?\s*\]")`,註解明講 `[src:路徑(:行號)]` 是 regen 守衛的 Tier A「現 code 可驗」證據標記——語意是「指向程式碼裡的位置」)
file: `scripts/lumos:2884-2887`(`_CTX_SRC_RE` 把 `\[src:` 列為 WHY: 行既有「出處」標記之一,同一個名字已經在跑)
file: `scripts/lumos:2890-2901`(`_CONTEXT_MARKER_RULES["FACT"]` 已經是「檢查 FACT: 前綴有沒有帶合格佐證」的既有機制,現行判準是「以程式碼為準」+反引號查詢)
file: `scripts/lumos:5037`(`context_marker_warnings(summ)` 被 `lumos lint` 呼叫,證明這套機制不是死碼、是目前真的在跑的檢查路徑)
計劃的 S2(FACT:/FLOW:/DEP: 前綴要帶 `[src:部署]` 等五類之一)想做的事,跟既有 `_CONTEXT_MARKER_RULES`/`context_marker_warnings` 是同一件事的加強版(判斷一行有沒有帶合格佐證),但計劃選擇另開 `lumos note-shape` 自己認 `[src:類別]`,而不是延伸既有函式;更關鍵的是把標記名字訂成跟既有 Tier A 標記一模一樣的 `[src:]`,兩邊語意不相容(既有指程式碼位置,新的指程式碼答不了、要去哪查)。計劃 PRIOR-ART 一節列了 5 條借用來源(①-⑤),唯獨沒提到這兩支既有機制,像是漏找而非刻意評估後才繞開。

## F2 治理帳新鎖沒有借用既有 `_excl_lock_try`/`_vault_write_lock`,PRIOR-ART 清單漏列
severity: major
blocking: 是 —— 若真的另起一份鎖檔邏輯(即使只是重寫一份等待/接手迴圈),就是本 repo 明文記過帳、且被第四輪架構席打掉過的「第二種鎖」重演
引句:「改成兩者寫入時拿同一把治理帳檔案鎖」
file: `scripts/lumos:28183-28185`(`_excl_lock_try` 的 docstring:「專案裡唯一的一套鎖檔做法……與筆記庫寫入鎖 `_vault_write_lock` 共用」)
file: `scripts/lumos:14233-14237`(`_vault_write_lock` docstring 記著「第三輪另開了一套 flock,是專案裡第二種鎖」,被第四輪架構席打掉的舊帳)
file: `scripts/lumos:28242-28243`(dispatch-lens 也直接呼叫 `_excl_lock_try`,證明這是可跨用途重用的通用原語,不是 vault 專屬)
計劃「治理帳寫入加鎖」整段沒有一次提到 `_excl_lock_try` 或 `_vault_write_lock`,PRIOR-ART 的①-⑤清單也沒把這個新鎖列進去——跟計劃自己開頭寫的「全部借本 repo 既有形狀,不發明新做法」矛盾。既有原語的介面(鎖路徑+逾時秒數)可以直接指到治理帳檔案重用,計劃沒有講清楚會不會這樣做。

第4問 落點:對「note-shape 指令本體 + 範圍與行共用函式 + 紀律範本改寫 + 消費專案 CI 健檢」開一篇新節點 `Systems/筆記內容閘` 是合理的,結構上跟「每支檔有家」同款——都是「新增獨立子指令 + 兩個 hook 呼叫點 + 自己的設定區塊」,值得有自己的家(對照 `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:1-9` 的 frontmatter,about_code 列 `scripts/lumos`+兩個 hook 檔,是同款新開新閘就新開節點的先例)。但「治理帳寫入加鎖」這部分不該整段落進新節點,見 F4。

## F4 治理帳鎖的說明應該落進既有的 `Systems/reversibility-governance-ledger`,不是整段塞進新開的 `Systems/筆記內容閘`
severity: minor
blocking: 否 —— 不影響程式架構分層,只是筆記歸屬,寫回時把這一段拆到正確的家即可修正
引句:「Systems/筆記內容閘」
file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:1-20`(既有節點,about_code 已列 `scripts/lumos`,正文本來就在管治理帳寫入這件事)
file: `scripts/lumos:856-933`(`_gate_event`)與 `scripts/lumos:28796-28819`(`_codeloop_gov_log`)——這兩支要加鎖的函式,家已經是上面那篇既有節點,不是新開的 note-shape 節點
`_gate_event` 與 `_codeloop_gov_log` 已經有家。「每支檔有家」鐵則本身要求「節點只准用反引號寫自己家的檔,別人的檔寫成那支檔的家的 [[連結]]」——這段改動如果整段寫進新開的 `Systems/筆記內容閘`,就是把別人家的檔案內容寫進自己節點,方向剛好相反;應該是在 `reversibility-governance-ledger.md` 補一段講加鎖的脈絡,`筆記內容閘` 只用連結指過去。

不對齊共 4 條,其中 major 2 條。
