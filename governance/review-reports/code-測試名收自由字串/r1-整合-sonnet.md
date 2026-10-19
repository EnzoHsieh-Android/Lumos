severity: minor

整體判斷:文件包和主程式的實際行為大致對得上,我沒有找到 major。以下 5 條是三個月後接手的人會踩到的對不上和壞引用。

## 已核對、沒問題的部分
- 8 篇改到的筆記(計劃、調研、Systems 六篇)跑 `lumos lint` 都是 0 問題。
- 文件列出的所有 `[test:]` 名稱都在 `scripts/test_lumos.py` 找得到。
- 固定席的 `[test:]` 綁定仍指到存在的測試。`t_guard_kill_rc_precedence` 實跑 4 passed。
- 實作紀錄與兩處 FACT 行(Jest、Vitest、Playwright 的篩選行為)的 `[來源:外部] [confirmed:] [查:]` 三鍵齊全。
- 筆記說程式會做的事,我開 `scripts/lumos` 對過的都符合:
  - `[test:\`rejects 中文 name\`]` 單平台解成整串。
  - 多平台裡 `y: 逾時 x` 被擋,訊息補了「要寫平台前綴」。
  - 懸空時印 `⚠ — N 條全標(…),懸空 k 只提醒不擋`。
  - 全懸空時跑那一行改講「綁了測試但全懸空」。
  - `guard bind` 多平台、名稱有冒號、沒帶 `--platform` 時擋下。
  - 歸檔與 `guard trace` 改用 `_test_name_boundary_re`。
  - `_apply_test_overrides` 與 `_name_filter_collisions` 都存在。
- 固定席(lumos-cli-read、guard-kill、測試假綠形態、bound-tests-gate、lumos-cli-lifecycle、授權與歸屬、design-loop):這份 diff 沒碰它們宣稱的行為,判不影響。bound-tests-gate 的撞名判「證不出」是新增行為,沒有破壞它的 INVARIANT。

## Findings

1. 調研筆記的落點指向 3 篇不存在的計劃
severity: minor
   blocking: 否
   - 位置:`Projects/Web示範前端缺口_調研.md` 的落點段與比對表。
   - 問題:筆記說「每列標出要落到哪篇計劃」,但 `[[Projects/前端知識與風險詞_計劃]]`、`[[Projects/記帳與迴圈工具小修_計劃]]`、`[[Projects/筆記指令健檢與規格閘小修_計劃]]` 這 3 篇都沒有檔案。
   - 影響範圍:C、D、E、F、G、H 六組、約 30 列的「落到哪篇計劃」都落在這 3 篇上。
   - 佐證:`lumos doctor` 第 2 步印「有 3 個連結連到不存在的筆記」,列出這三個名字。`find docs` 也找不到這三個檔。
   - 後果:接手的人照表找做法會撲空。RETIRE-IF 的結案條件(「對應計劃裡結案」)也沒有可結案的對象。
   - 修法:補開這三篇,或在表上註明「待開」。
   - 引句:「落點:A → [[Projects/測試名收自由字串_計劃]];B → [[Projects/前端框架從vue分出_計劃]](該篇 todo,開工條件「有 React 專案真的要接」這次已滿足);C、D → [[Projects/前端知識與風險詞_計劃]];E → [[Projects/記帳與迴圈工具小修_計劃]];F、G、H → [[Projects/筆記指令健檢與規格閘小修_計劃]]」

2. 「測試名只能是識別字」的舊說法還留在兩處活文件,而計劃的 S25 清單沒涵蓋
severity: minor
   blocking: 否
   - 位置一:`skills/lumos-project-notes/reference.md:1196` 寫「要綁的 Kotlin 測試函式名也必須是識別字——反引號中文名綁不上」。
     - 實測:`resolve_test_refs("[test:\`rejects 中文 name\`]", {}, None)` 回 `[(None, 'rejects 中文 name')]`。
     - 實作紀錄也寫「條款與合約裡寫反引號 Kotlin 名從判壞名變成配得到」。
     - 這句已經過期,是會誤導人的行為說法。
   - 位置二:`Systems/linter精選目錄.md:153` 寫 dart「識別字名錨」。
     - 現在 dart 標題整串收,`attr_hint` 也改了。
   - 為何漏:S25 只 grep「NO MATCH」「識別字名才可綁」「method 維持識別字」三個詞,漏掉這兩處的措辭。
   - 修法:這兩句改寫,並把 S25 的 grep 詞擴到「必須是識別字」「識別字名」。
   - 引句:「要綁的 Kotlin 測試函式名也必須是識別字——反引號中文名綁不上。」

3. `test-profile-multiplatform` 的 API 描述保留舊切法
severity: minor
   blocking: 否
   - 位置:`Systems/test-profile-multiplatform.md` 的 `resolve_test_refs` 條目。
   - diff 只在這篇尾端加了新段,沒改這條。
   - 這條仍寫「含冒號段前綴須為已定義平台(否則 raise)」。
   - 實際行為(`_split_test_ref`,`scripts/lumos:6053` 起):
     - 前綴不是已定義平台時,只有「半形冒號且前面像平台名」才 raise。
     - 其他情況整串當名稱,例如 `API: 逾時`。
   - 同一篇新段與這條矛盾。
   - 修法:改寫那一條,或標「已被下段取代」。
   - 引句:「`resolve_test_refs(inv_text, platforms, default_platform)`：`[test:...]` → `[(platform, name)]`。`platforms` 空（legacy）不切分；非空則含冒號段前綴須為已定義平台（否則 raise）、無冒號段歸 default。」

4. 計劃本文的「做法」跟實作和 Systems 節點不一致
severity: minor
   blocking: 否
   - 計劃自稱是單源,Systems 節點都指回它。
   - 不一致一:做法 2 寫「字面裡只認 `\'`、`\"`、`\\` 三種跳脫」。
     - 實際 `_test_name_of_match` 認 5 種:`'`、`"`、`\\`、反引號、`$`(`scripts/lumos:6338`)。
     - Systems 節點寫的是 5 種,所以兩篇互相矛盾。
   - 不一致二:做法 3 的 ⚠ 句式寫「N 條都有標,懸空 k…」。
     - 實際輸出是「N 條全標(綁了…/靠人…),懸空 k 只提醒不擋」(`scripts/lumos:8691`)。
     - 實作紀錄有說明「照舊寫 N 條全標」,但做法本文沒回頭改。
   - 引句:「字面裡只認 `\'`、`\"`、`\\` 三種跳脫並還原;出現其他跳脫(`\n`、`中`、`\x41`)就不收」

5. 調研筆記有文字殘缺,且 W1 的現況和統計互相矛盾
severity: minor
   blocking: 否
   - 殘缺:
     - F12 列:「(的說明、`spec_commit` 共 23 處)」
     - F10 列:「的席位立場仍是後端語彙」
     - F23 列:「;的處置帳必須綁 `--round`」
     - 這幾處都缺主詞或路徑,應該是拿掉行號引用時整段誤刪。
     - 讀的人無法照這些列重現。
   - 矛盾:
     - W1 列寫「2026-10-15 已由本列落點的計劃處理」。
     - 同篇的「各組條數」表仍把 A 組 W1 算成「仍存在(部分)」,「W1 寫計劃時多查到的」一段也還在用現在式描述現象。
   - 引句:「2026-10-15 已由本列落點的計劃處理(句子名可綁、懸空印 ⚠、多平台逃生口)」

## 補充
- 兩處 FACT 的 `[查:order-web 的副本實跑…]` 指向 repo 外的副本。三個月後無法重驗,但鍵是齊的,不算缺鍵。
- 各篇 Systems 新增段落都是正文清單,沒有新增摘要行,所以不涉及摘要行分類問題。
- 每支檔有家:這次只改 `scripts/lumos` 與 `scripts/test_lumos.py`,計劃 `lands_in` 列的 6 篇都在 diff 內,對得上。
- 我沒有跑全套測試。

最嚴重 severity:minor,blocking 共 0 條。
