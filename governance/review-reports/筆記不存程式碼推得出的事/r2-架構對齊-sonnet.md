severity: major

## F1 新分支範圍起點用「merge-base 預設分支」——repo 已有兩套解法且都刻意不用這一種

severity: major
blocking: 是 —— 這是本 repo 裡「新分支範圍怎麼算」這個具體問題的第三種解法,而且直接復用了 2026-07-21 因「main-direct 盲區」被拿掉的 merge-base 手法,不是單純命名差異

引句:「當範圍是新分支或本機沒有遠端版本,起點應為與預設分支的分岔點」

計劃(條款 S3、〈共用〉段)把「新分支/本機沒有遠端那個版本」的起點定成「這個分支跟預設分支的分岔點」,也就是 `merge-base(branch, 預設分支)`。但這個 repo 對「新分支怎麼定起點」已經有兩套現成、各自為了不同目的刻意選的解法,兩套都**不是**「merge-base 對預設分支」:

1. `pitfalls`/`code-loop check` 用的 `_range`(pre-push 逐 ref 推導):2026-07-21《prepush主幹範圍修法_計劃》把原本的 `merge-base(HEAD, main)` **整段拿掉**,原因記在 `docs/lumos-toolchain-knowledge/Projects/prepush主幹範圍修法_計劃.md`——main-direct 時 `merge-base(HEAD,main)==HEAD`,導致整組守衛靜默跳過(事故:`Issues/code-loop守衛main-direct盲區`)。換成讀 stdin 推送範圍、無遠端物件才退回 empty-tree 掃全部。
2. `home check`(nodehome-check gate,2026-09-11 新增)為了「新分支不要把整庫舊筆記當新增」另訂一套:「不在任何遠端分支上的提交」裡最早那個的上一個提交,不是 merge-base 對預設分支。`scripts/hooks/pre-push:216-219` 明講「★跟上面 _range 是刻意不同的兩套★……新分支不沿用上面的空樹兜底」,`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:31` 同一件事再寫一次並釘了測試:「推送前新分支的起點=不在任何遠端分支上的最早提交的上一個,不沿用空樹兜底……兩套刻意不同……別合併」。

`merge-base(branch, 預設分支)` 在「這條分支是從另一條已推上遠端、還沒併回預設分支的分支切出來的」這個常見情境下,會把那條上游分支已經審過、已經在遠端的舊提交也算成「這次新增」——跟 home-check 特別避開的「把整段歷史當新改動」是同一種病灶,只是觸發條件窄一點。計劃裡的 PRIOR-ART 段對「綁定方式」有明確做過鄰居對照(★綁定方式照②不照①★),但對「新分支起點」這一段沒有對照到 home-check 已經解過同一題、也沒有對照到 2026-07-21 merge-base 被拿掉的事故,等於在同一個 repo 裡第三次重新發明「新分支範圍怎麼定」,而且復用了其中已知會出事的那一種手法。

file: `scripts/hooks/pre-push:216`
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:31`
file: `docs/lumos-toolchain-knowledge/Projects/prepush主幹範圍修法_計劃.md:15`

## F2 通過紀錄寫進治理帳的路徑繞過了既有的通用寫入器 `_gate_event`

severity: major
blocking: 是 —— 治理帳(`.governance-log.jsonl`)只有一個被明文指定給「所有閘」共用的寫入器,計劃另組一套寫法等於在同一個檔案上開第二條寫入路徑

引句:「事件種類沿用鄰居的 passed / skipped / blocked,登記進既有閘名單」

計劃(做法第二層第 4 點)講的是要把 `note-audit` 這個閘的通過/跳過事件寫進「治理帳」,而且事件種類就是 `_gate_event`/`_gate_event_or_warn` 那一套通用寫入器所定義的字面值(`passed`/`skipped`/`blocked`,對照 `nodehome-check` 呼叫 `_gate_event_or_warn(root, "nodehome-check", kind, ...)` 的 `kind` 值,`scripts/lumos:23355`)——這正是 `home check` 這個最相近鄰居實際用的寫法。但計劃選的寫入機制不是 `_gate_event`,而是「既有的 `_jsonl_append_verified` 並拿既有寫入鎖」。

`_gate_event`(`scripts/lumos:856`)的函式說明裡明講它就是被設計成「治理帳唯一的通用寫入器」,而且是刻意的:「這樣既保住那條釘子的用意,又不必為了通過它把通用寫入器拆成六份」——換句話說,repo 裡已經有明文禁止「每個閘各自寫一套寫入器」的立場,`nodehome-check`、`anchor`、`canary` 的擋/放行事件都走這一支。`_jsonl_append_verified` 是另一種東西:它是給 `.canary-log.jsonl`、design-loop 這類「以 token 為鍵、每筆各自獨立」的記錄檔用的讀回自驗 helper(`scripts/lumos:8187` 及其呼叫點都用 `key_field="token"`),不是給 `gate`/`kind` 這種共用治理帳事件模型設計的。`_vault_write_lock` 的合約也是「同一個筆記庫的 set/append/remove」(vault 筆記的讀—改—寫),不是治理帳日誌檔的寫入鎖。

計劃比較的鄰居只有 `_codeloop_gov_log`(code-loop 自己的舊寫法,已知無鎖),沒有比對到本題目清單裡明列的另一個近鄰 `home check` 實際在用的 `_gate_event`/`_gate_event_or_warn`——這才是「登記進 `_KNOWN_GATES`、事件種類 passed/skipped/blocked」這個形狀真正對應的既有寫法。S10 要求「兩個行程同時 record 時,兩筆通過紀錄都應完整落在治理帳」的併發疑慮是真的(`_gate_event` 本身也沒鎖),但解法應該是替 `_gate_event` 補併發安全或在它之上包一層,而不是為同一個治理帳檔另開一條用途不符的寫入路徑。

file: `scripts/lumos:856`(`_gate_event` 的「通用寫入器」定位與說明)
file: `scripts/lumos:23355`(`home check` 實際呼叫 `_gate_event_or_warn` 寫 passed/warned/blocked)
file: `scripts/lumos:8187`(`_jsonl_append_verified` 的 token 鍵設計,非治理帳事件模型)

---

第 1 問(分層與依賴方向)對齊:`note-shape` 掛在提交前(`--staged`)與推送前/CI(`--diff <範圍>`),跟 `home check` 完全同一種掛法——`scripts/hooks/pre-commit` 呼叫 `lumos home check --staged --repo`,`scripts/hooks/pre-push` 對每個 ref 算出範圍後呼叫 `lumos home check --diff <範圍> --repo`(`scripts/hooks/pre-push:222-227`);計劃裡 `note-audit check` 明講「另開一支平行呼叫(跟 `home check` 同形狀,不併進 `code-loop check`)」,呼叫方向與獨立性都跟既有的閘一致,沒有 hook 越層直接讀寫治理帳或直接嵌審查邏輯的情形——判定者仍是「編排會談派乾淨審查席」這個既有形態,不是新開一支對外服務。唯一的例外是上面 F1/F2 提到的範圍起點與治理帳寫入兩處具體做法,不是分層本身出問題。

第 2 問(命名與錯誤處理)大致對齊,除一處(見下)。回傳碼「0 過、1 擋、2 參數錯」跟 `code-loop check`/`home check` 一致;跳過用的環境變數 `LUMOS_SKIP_NOTE_AUDIT` 跟 `LUMOS_SKIP_LINT_NEW`(`scripts/lumos:21479`)、`LUMOS_SKIP_CODE_LOOP`、`LUMOS_SKIP_BOUND_TESTS` 同一個命名族;閘名要登記進 `_KNOWN_GATES`(`scripts/lumos:6586`)這件事計劃也有講到;`decision-amend` 這個新指令名跟既有的 `decision-add`/`decision-supersede`/`decision-reindex` 是同一個「decision-<動詞>」族,沒有另立門戶。

## F3 `.lumos/config.json` 的三段式開關值用 `report`,跟鄰居的 `warn` 不一致

severity: minor
blocking: 否 —— 只是列舉值的字面不同,結構(三段:擋/只提醒/關)跟鄰居一樣

引句:「block(預設)/ report / off」

既有兩個同形狀的專案開關,`lint_new.gate` 的合法值是 `_LINT_NEW_GATE_MODES = ("block", "warn", "off")`(`scripts/lumos:20935`),`node_home.gate` 是 `_NODEHOME_GATE_VALUES = ("on", "warn", "off")`(`scripts/lumos:22177`)——兩者「只提醒不擋」那一格都叫 `warn`。計劃裡 `note_audit` 的三段式開關把同一格叫成 `report`,是同一個位置換了一個字面值,沒有結構性差異。

file: `scripts/lumos:20935`
file: `scripts/lumos:22177`

## F4 ⚠ 申訴另派一席,沒提是否要求跟第一席不同人

severity: minor
blocking: 否 —— 判不準,交編排者;就算缺這條,也只是少了一道機械核對,不影響整體分層或誰呼叫誰

引句:「另派一席不知道前一席結論的審查員單判那一行」

本 repo 已有的「第二判者覆核」鄰居是 `canary second`(`cmd_canary_second`,`scripts/lumos` 約 8218 行起),它明文機械擋「覆核的人跟原判的人是同一位」——分權的核心防的就是自己審自己。計劃對 note-audit 的申訴只講「不知道前一席結論」,沒有提是否也要求審查員身分跟第一席不同(乾淨 agent 派工模式下,「不同席次」本身可能已隱含身分不同,是否需要額外核對看不出來,故標 ⚠)。

file: `scripts/lumos:8218`(`cmd_canary_second` 的同判者拒絕邏輯,約略行號,函式内容見上文擷取)

第 3 問(第二種做法)其餘部分對齊:內容指紋的設計思路(以「規則/檔名 + 正規化片段」這種內容特徵當身分、不用行號)跟 `lint-waive` 的 `_lint_new_key`(`scripts/lumos:21288`)同一個做法,計劃本文也明講「★綁定方式照②不照①★」,清楚對照過 `lint-waive` 的內容指紋而不是 `code-loop` 的提交祖先鏈綁定,這一段是對的;`skip` 出口(`lumos note-audit skip --diff <範圍> --note "<理由>"`,寫一筆 skip 綁同一指紋)跟 `lint-waive`/`code-loop skip` 的「留理由、進治理帳」形狀一致;`.lumos/note-audit/<指紋>.md` 這種不進版控的清單檔,跟既有的 `.lumos/lintbase-<隨機>/`(新增告警閘的快照解壓目錄,`.gitignore:36`、`scripts/lumos:20950`)、`.lumos/test-cache*.json` 一樣是「專案底下、`.lumos/` 內、不進版控的暫存」慣例,不是新地點。真正偏離既有做法的只有 F1(新分支範圍起點)與 F2(治理帳寫入路徑)。

第 4 問(落點)對齊:本 repo 對「每支檔有家」的既有做法本來就是「一個閘機制一篇 Systems 節點,`about_code` 各自列自己要管的程式檔,同一支檔可以同時是好幾篇的家」——`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md` 自己的 `about_code` 就列了 `scripts/lumos`、`scripts/hooks/pre-commit`、`scripts/hooks/pre-push`,而同一支 `scripts/lumos` 也同時是 `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md` 與 `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md` 的 `about_code`;`每支檔有家.md` 自己也承認這是天花板現象(「本工具鏈主程式有 31 篇」機械數,見該檔「KEY:天花板」那行)。新開 `Systems/筆記內容閘` 專門管 note-shape/note-audit/decision-amend 這一整組新機制,完全對齊「一個閘機制一篇」的既有分法,不是額外的做法。

file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:6`(`about_code` 列 `scripts/lumos` 等三檔)
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:12`

不對齊共 4 條,其中 major 2 條。
