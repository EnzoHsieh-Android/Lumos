severity: major

## 三問逐答

**問1(分層與依賴方向)**:對得上。`_lens_push_base` 定義在 `_lens_` 家族內(緊接 `_lens_range_ok`,緊接在 `_lens_git`/`_lens_full_sha`/`_mainline_ref` 之前,`scripts/lumos:28098`),它呼叫的 `_mainline_ref`(`scripts/lumos:28145`)本來就是同一家族的既有成員,且早就被 `_ns_mainline_refs`(`scripts/lumos:23568`)以同層方式呼叫過——不是新引入跨層依賴。三個呼叫端(`cmd_home_check` `scripts/lumos:23380`、`cmd_note_shape` `scripts/lumos:23985`、`_codeloop_guard_verdict` `scripts/lumos:30719`)都是「上層指令/判定式呼叫 `_lens_` 工具層」,跟修法前 `cmd_home_check`/`cmd_note_shape` 本來就直呼 `_lens_full_sha` 的既有方向一致。R1 講的「40 個 0 處理寫在單一呼叫端、沒進共用範圍解析」這條已經收斂成一支共用函式,三個呼叫端都改成呼叫它,姊妹指令 home check 的洞也補了(`scripts/lumos:23378-23385`)。

**問2(命名與錯誤處理)**:對得上。命名沿用 `_lens_` 前綴族(`_lens_range_ok`/`_lens_full_sha`/`_lens_git`→`_lens_push_base`);回傳 `(base, why)` 供呼叫端印 stderr 診斷、`why` 空字串當「沒話說」的慣例,跟既有 `_nodehome_clamp_base` 的「找不到就退回原值、不拋例外」錯誤處理風格一致;`_ZERO_SHA_RE` 沒掛 `_LENS_` 前綴,跟同樣被三個不同家族共用的 `_EMPTY_TREE_SHA`(`scripts/lumos:29868`)同一種「共用常數不掛特定家族前綴」慣例,不是隨意命名。

**問3(是否第二種做法)**:pre-push 的 `pp_range_for` 本來就跟 `_lens_push_base` 不是同一題——pre-push 是圖譜健康全量體檢,起點不明時故意「當空樹全掃」(它自己註解:不是 fail-open,是怕新分支變成穩定繞法),多掃不傷;`_lens_push_base` 要解的是「新增行/新增檔判定」,多掃(把主線舊帳當新增)會直接誤擋,所以要分岔點才對——語意不同,做法不同不算不對齊。**但 ci.yml 裡確實留了第二種做法**,而且剛好是同一題:code-loop 步驟(`.github/workflows/ci.yml:109-111`)還在用 shell 端 `EMPTY=4b825dc…` + `case`/`git cat-file` 把 40 個 0 或找不到的 BEFORE 換成空樹 sha,換完才交給 `lumos code-loop check --diff`;note-shape 步驟(同檔 `:134`)這一輪已經拿掉這段、改成「原樣交給 lumos,讓它自己用 `_lens_push_base` 判」。這兩步緊鄰、處理的是同一個 `BEFORE` 變數、同一種 40 個 0/找不到的狀況,現在卻是兩套邏輯——而且不是各自獨立選了不同做法就算了:`_codeloop_guard_verdict` 這一輪新增的分岔點判斷(`scripts/lumos:30711-30722`)在 CI 的 code-loop 步驟裡實際上永遠不會被觸發到——因為 shell 已經把 `a` 換成 `_EMPTY_TREE_SHA` 才傳進來,`a != _EMPTY_TREE_SHA` 這個條件必定為假,新加的判斷變成這條生產路徑上的死碼。等於這次的核心修法(分岔點算,不當空樹)只真正落地在 note-shape 與 home-check,code-loop 的 CI 入口原封不動,ESC-61fc2d87 那類「新分支開在主線頂端、把主線上線後的舊帳當新增」的誤判在 code-loop 這條路上照樣會發生(diff 範圍變成 `空樹..SHA`,整段歷史被當成這次的變動餵給 pitfalls/受波及測試判定)。

## F1 code-loop CI 步驟沒跟著換掉 shell 端空樹替換,新函式在這條路徑是死碼

severity: major
blocking: 是 —— 這一輪要解的正是「40 個 0/找不到不能當空樹、要接到分岔點」,`_codeloop_guard_verdict` 也接了這條邏輯,但 ci.yml 的 code-loop 步驟仍在 shell 端把 BEFORE 換成空樹 sha 才呼叫,新邏輯的觸發條件 `a != _EMPTY_TREE_SHA` 因此恆假——等於同一份 diff 對「note-shape」跟「code-loop」兩個緊鄰步驟給出兩種不同做法,而 code-loop 那份仍帶著本輪要修的那個洞(主線上線後的舊帳被當新增,拖累 tier 判定與受波及測試範圍)。
引句:「起點是 40 個 0(新分支首推)或本機找不到(force-push 後)時,照筆記形狀擋與每支檔有家共用的判法換成真的起點」
file: `scripts/lumos:30711`(對照未動的 `.github/workflows/ci.yml:109-111` `EMPTY=4b825dc642cb6eb9a060e54bf8d69288fbee4904` / `case "$BEFORE" in …` 那三行,與已改用「原樣交給 lumos」的同檔 note-shape 步驟 `.github/workflows/ci.yml:134`)

不對齊共 1 條,其中 major 1 條
