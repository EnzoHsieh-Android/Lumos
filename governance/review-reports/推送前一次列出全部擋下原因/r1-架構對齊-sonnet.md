severity: major

審查依據:被審材料 `/tmp/推送前一次列出全部擋下原因-r1.md`(以下簡稱材料)對照 `scripts/hooks/pre-push`、`scripts/hooks/pre-commit`、`scripts/lumos`。

## 1. 分層與依賴方向
**大致對齊,有一處結構偏離。**
- 判定放在 `scripts/lumos`、掛鉤只呼叫並看回傳碼,這是既有分工。
  - 對照:`scripts/hooks/pre-push:431` 的 `spec-gate --push-check`。
  - 對照:`scripts/hooks/pre-push:458` 的 `code-loop check`。
  - 對照:`scripts/hooks/pre-commit:222` 與 `:231`,註明「判定全在 lumos 裡,這裡只呼叫」。
  - 材料做法 4 把 `--collect` 放進 CLI,做法 1 把收集邏輯放進掛鉤,分工與此一致。
- 掛鉤本身已有共用函式與外部旗標先例。`pp_stop_if_signaled` 在 `scripts/hooks/pre-push:70`,`--bound-tests-advisory` 在 `scripts/lumos:51766`。新增 `pp_record_block` 沒有問題。
- 偏離處是預演。材料做法 5 讓 `lumos push-preview` 自己組出掛鉤要讀的 stdin 那一行,再回頭跑掛鉤。這是 CLI 去模擬 git 對掛鉤的呼叫。
  - 既有的 `push-range`(`scripts/lumos:51498`)方向相反:掛鉤呼叫 CLI。
  - 預演的判定本體是掛鉤,所以 CLI 要重算 upstream、遠端 sha、全零等推送細節,這些邏輯目前只在掛鉤和 `push-range` 裡。這一點歸入第 3 問的發現 B。

## 2. 命名與錯誤處理
**命名多數對齊,有兩處不一致,輸出格式未寫死。**
- `pp_record_block`:對齊掛鉤內 `pp_` 前綴函式(`scripts/hooks/pre-push:40`、`:70`)。
- `_PP_BLOCKS`:對齊 `_PP_LINES`(`scripts/hooks/pre-push:28`)與 `_PP_BR`(`:54`)。
- 子命令 `push-preview`:對齊 `push-range`(`scripts/lumos:51498`),動詞或名詞連字號的形態一致。
- `--collect`:現有旗標是形容式或名詞式,例如 `--bound-tests-advisory`(`scripts/lumos:51766`)、`--from-json`、`--strict`(`:50868`)。`--collect` 是動詞,語意也不直觀,是「全判完」還是「彙總」看不出來。這個差異很小,不另列。
- `LUMOS_PUSH_PREVIEW`:既有的 `LUMOS_` 變數有兩類。
  - 使用者逃生閘:`LUMOS_SKIP_*` 與 `*_OFF`,例如 `LUMOS_SKIP_DRIFT_CHECK`(`scripts/lumos:39415`)。
  - 掛鉤傳給 lumos 的內部旗標:`LUMOS_PUSH_ATTEMPT`(`scripts/hooks/pre-push:260`)。
  - `LUMOS_PUSH_PREVIEW` 屬第二類,命名對齊。但那一類的注釋明講「hook 只負責產生它、lumos 端讀」,這裡方向反了:lumos 產生、掛鉤讀。這是發現 C 的一部分。
- 預演的命名慣例是旗標,不是新的子命令。`update --dry-run`(`scripts/lumos:22863`)、`updated-sync --dry-run`(`:19673`)、`drift fix --dry-run`(`:39257`)都是 `--dry-run`。材料用 `push-preview` 加環境變數,偏離了。見發現 C。
- 彙總格式:現有「擋下:…」說明段是 `echo ""` 加 `擋下:<原因>` 加一段逃生句。
  - 對照:`scripts/hooks/pre-commit:178` 與 `:225`,`pre-push:516` 與 `:543`。
  - 材料寫「這次推送共有 N 道擋下」和「逐筆一行:閘名、ref、原因」,沒說逃生句是否仍逐道保留,也沒說尾句格式。
  - 格式本身可以對齊,屬實作細節,留待落地時核對。

## 3. 第二種做法
**有發現,三條。**

**發現 A:「收集多個問題再一起報」在 pre-commit 已經有做法,材料沒沿用,另造一套。**
- 對照:`scripts/hooks/pre-commit:195-205` 的 Gate L。做法是 `lint_fail=1`、迴圈繼續、各自印「擋下:…」、迴圈後統一判斷、`exit 1`。
- 對照:`scripts/lumos` 的 `doctor` 各段也是收集後統一報。
- 材料的 PRIOR-ART 只提外部的 pre-commit 框架與 `make -k`,沒提本專案已有的同型做法。
- 材料用的 `pp_record_block`、`_PP_BLOCKS`、彙總段不是新輪子,而是 Gate L 做法的跨閘版本。方向對,但沒有說明與 Gate L 的承襲關係,也沒有說明兩個機制為何不共用一種旗標變數寫法。
- 另一處不同:pre-commit 本身在 Gate PY、Gate H、Gate NS 之間仍是遇錯就停(`scripts/hooks/pre-commit:178`、`:222`、`:231`)。材料只改 pre-push,沒說明 pre-commit 為何不一起改。這屬於範圍問題,但會形成「兩個掛鉤兩種做法」。
- 判為 major 的理由:同專案同型問題已有收集做法,材料另立一套且不說明差異。
- 引句:「Git 生態最常用的 pre-commit 框架預設 `fail_fast: false`——每個 hook 都跑、最後一次列出全部失敗」
severity: major
- blocking: 是 — 引入與既有 Gate L 並存的第二種收集做法,且沒交代是承襲還是不共用

**發現 B:預演指令 `push-preview` 與既有 `spec-gate --push-check`、`code-loop check` 同屬跑閘的入口,但它是在 CLI 內重造一份「推送範圍與 stdin 組裝」,與 `push-range` 並存。**
- 對照:`scripts/lumos:45907` 的 `push-range` 已負責推送範圍的算法,且文件註明新分支首推時掛鉤與存量漂移檢查共用同一支(`scripts/hooks/pre-push:49-51`)。
- 材料做法 5 要在 `push-preview` 裡另外組「本地 ref、本地提交、遠端 ref、遠端提交」,含「沒有追蹤就用主線所在的遠端、同名分支」「遠端查不到就填全零」。這是第二份範圍推導。
- 材料只描述掛鉤讀它,沒說明與 `push-range` 或 `_push_range_start` 共用哪一段。
- 判為 major 的理由:出現第二份推送範圍推導,可能與 `push-range` 分歧。
- 引句:「用目前分支推到它追蹤的遠端分支(沒有追蹤就用主線所在的遠端、同名分支)組出掛鉤要讀的那一行」
severity: major
- blocking: 是 — 另造一份推送範圍與 stdin 組裝邏輯,沒有指明共用 `push-range`

**發現 C:預演的機制選擇與既有慣例不同(`--dry-run` 旗標對 `LUMOS_PUSH_PREVIEW` 環境變數加新子命令)。**
- 既有預演都是在原指令加 `--dry-run`:`scripts/lumos:22863`、`:19673`、`:39257`。
- 內部傳遞給掛鉤的環境變數先例 `LUMOS_PUSH_ATTEMPT`(`scripts/hooks/pre-push:260`)是掛鉤產生、lumos 讀;材料反向。
- 結構上沒有跨層直呼,但它引入的是「為預演新建一個子命令,再用環境變數讓整支掛鉤改行為」的第二種預演做法。
- 判為 minor 的理由:命名與機制跟鄰居不一致,但沒有重複邏輯,結構仍成立;重複邏輯那一面已在發現 B 計為 major。
- 引句:「帶環境變數 `LUMOS_PUSH_PREVIEW=1` 跑掛鉤;掛鉤看到它,到統一判斷那一步就停」
severity: minor
- blocking: 否 — 命名與機制和鄰居不一致,但結構上正確

## 4. 落點
**部分合理,有一處不足。**
- `Systems/bound-tests-gate` 的 `about_code` 列了 `scripts/hooks/pre-push` 與 `scripts/lumos`(該筆記 frontmatter 的 `about_code` 區塊,約第 50-53 行)。掛鉤改動寫進這篇合理,而且它綁的 `t_prepush_gates_stop_on_signal` 等守衛正好是被改動的對象。
- `Systems/pitfalls-code-loop` 的 `about_code` 只列 `scripts/lumos`。`code-loop check --collect` 屬此篇,合理。
- 缺口:新子命令 `push-preview` 與新增的 `--collect` 都落在 `scripts/lumos`,而管 `scripts/hooks/pre-push` 的家不只一篇,另有 `Systems/每支檔有家`、`Systems/筆記內容閘`、`Systems/存量漂移守衛` 等也提到它。
  - 材料沒指明掛鉤收集邏輯以哪一篇為主、其他篇只放連結。
  - `push-range` 的相關說明散在這幾篇。
  - 這是文件分工問題,不是程式結構問題,列為提醒。⚠ 我沒有逐篇核對每篇 `about_code`,判不準。
- 判定:`lands_in` 兩篇合理;建議材料補一句「`push-preview` 說明寫進 `Systems/bound-tests-gate`,`--collect` 寫進 `Systems/pitfalls-code-loop`」。
- 判為 minor 的理由:落點方向合理,但新增 `push-preview` 說明的歸屬沒寫明。
- 引句:「Systems/bound-tests-gate」
severity: minor
- blocking: 否 — 落點方向合理,只缺新增子命令的歸屬明示

不對齊共 3 條,其中 major 2 條
