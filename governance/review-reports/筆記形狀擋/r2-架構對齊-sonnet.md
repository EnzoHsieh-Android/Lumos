severity: major

第1問 對齊:計劃明講「判定全在 lumos 裡,hook 只呼叫」「回傳碼照鄰居:0 過、1 擋、2 參數錯;不是 git 或找不到 lumos 就放行並說一句。hook 只認 1 為擋」,跟既有鄰居 `cmd_home_check` 的分層一致——所有判斷(範圍、規則、設定、fail-open)都在 `scripts/lumos` 裡,hook 只是呼叫並依 rc 決定要不要 `exit 1`,不在 shell 裡重寫任何判定邏輯。
對照:`scripts/lumos:23258`(`cmd_home_check` docstring 明講「git 跑不起來=fail-open」「判定全在 lumos 裡」)、`scripts/hooks/pre-commit:122-126`(`nh_rc=0; ... || nh_rc=$?; [[ "$nh_rc" -eq 1 ]] && exit 1`)、`scripts/hooks/pre-push:235-244`(同一種「算 rc、只認 1」寫法)。note-shape 描述的呼叫形狀跟這兩處逐字對得上,沒有跨層直呼或把判定塞進 shell 的跡象。

第2問 對齊(除 F1/F2 涉及的部分外):
- 閘名 `note-shape` 走既有 kebab-case 命名(對照既有 `nodehome-check`、`lint-new`),且計劃明講「閘名 note-shape 登記進既有閘名單」,對應 `_gate_event` 的白名單機制。對照:`scripts/lumos:6586-6600`(`_KNOWN_GATES` 元組)、`scripts/lumos:898-902`(`_gate_event` 對名單不在就不寫並喊出來)。
- 跳過環境變數 `LUMOS_SKIP_NOTE_SHAPE=1` 命名跟 `LUMOS_SKIP_LINT_NEW`(`scripts/lumos:21479`)同形狀;寫的事件種類 `skipped-env` 是既有詞彙,不是新發明。對照:`scripts/lumos:29219`(`kind = "skipped-env" if ...`)、`scripts/lumos:30198`(`_gate_event_or_warn(repo_root, "code-loop", "skipped-env", ...)`)。
- doctor 對非 block 模式每次印一行,計劃寫「照 node_home.gate」,對照既有印法:`scripts/lumos:999`(`每支檔有家」的擋設成 {_nh_mode}...node_home.gate)`)。
- `note_shape.gate` 選擇「從被檢查版本讀」而非像 `lint_new.gate` 直讀工作目錄(`scripts/lumos:21103` `_lint_new_config` 用 `p.read_text` 直讀磁碟),計劃在 PRIOR-ART 與做法段都明講是刻意挑 `node_home.gate` 那條(`scripts/lumos:22184-22194` `_nodehome_config` 的 `from_snapshot=True` 分支),因為 note-shape 跟每支檔有家一樣是掛鉤擋提交/推送的閘,而 lint_new 是另一種評估時機——這是有理由的「混搭借用兩個鄰居各自的一半」,不是憑空自創第三種寫法,判為對齊。

第3問(混合結果,對齊的部分先講,不對齊的另開 F1/F2):
- 設定「從被檢查版本讀」這件事本身不是直接呼叫 `_nodehome_config`,而是跟它一樣的「一閘一份讀取器」慣例——本 repo已有 `_nodehome_config`(`scripts/lumos:22184`)與 `_lint_new_config`(`scripts/lumos:21095`,docstring 自己寫「同 _stack_questions_config 慣例」)兩份並存的先例,note-shape 再開一份同形狀的讀取器不算第二種做法,是既有慣例的第三份實例。
- `_node_code_ref_tokens` 擴充兩個預設關閉選項:函式簽名目前是 `_node_code_ref_tokens(text, top_dirs)`(`scripts/lumos:19854`),既有三個呼叫點分別在 `scripts/lumos:19887`(`_refcheck_scan`)、`scripts/lumos:22611`(改檔前推筆記)、`scripts/lumos:26146`;函式本身已經是「多個既有使用者共用一份、加 kwargs 不動預設行為」的形狀,而且圍欄判定要用的 `_visible_lines` 本身就有 `keep_fenced=False` 參數(`scripts/lumos:3218`),note-shape 要「圍欄內照查」直接傳 `keep_fenced=True` 即可,不必另寫抽取或圍欄邏輯。此處判定為真的能直接借,不是第二種做法。
- `[來源:…]` 不會跟既有方括號欄位撞:本 repo 既有的 `[src:路徑(:行號)]` 是 regen 重生來源守衛(Check J)專用、會被機械驗證檔案是否存在的欄位(`SRC_REF_RE` 於 `scripts/lumos:4270`、J-c 子句於 `scripts/lumos:4600-4607` 會把 `[src:部署]` 這種非路徑值判成「dangling=幻覺證據」)。計劃正是為了避開這個撞名才改叫 `[來源:…]`(全文搜尋 `來源` 沒有既有的 `[來源:key]` 形式方括號欄位在用),這個判斷正確、沒有製造新衝突。

## F1 上線點截斷/合併處理目前寫死給每支檔有家專用,借用方式沒講清楚,有淪為第二套實作的風險
severity: major
blocking: 是 —— 這是「借既有函式」還是「照樣子另寫一份」沒講清楚,屬於條款3(第二種做法)要擋的情況
引句:「連同它緊鄰的三個配套一起借」
file: `scripts/lumos:22181`(`_NODEHOME_GOLIVE_MARK = "home check --staged"` 是模組層級常數,字面值就是每支檔有家自己 hook 裡的字串)
file: `scripts/lumos:22854-22862`(`_nodehome_golive(repo_root, tip)` 內部寫死 `f"-S{_NODEHOME_GOLIVE_MARK}"` 且只在 `"--", "scripts/hooks/pre-commit"` 這一支檔的歷史裡找,沒有 mark/path 參數)
file: `scripts/lumos:22864-22876`(`_nodehome_clamp_base` 直接呼叫 `_nodehome_golive(repo_root, tip)`,同樣沒有可替換 mark 的介面)
說明:跟「設定讀取」不同,golive/clamp_base 在本 repo 沒有「一閘一份」的既有並存先例(全域只搜到這一份,`grep -n "_golive\|_clamp_base"` 只命中 node_home 自己)。計劃要用 `note-shape --staged` 當上線點標記,但目前的函式簽名與搜尋路徑都寫死是 node_home 專屬,要嘛把這兩支函式加參數(標記字串、要搜的 hook 檔案)改成共用工具,要嘛就是另外寫一份形狀一樣、字串不同的 note-shape 專屬版——後者正是「不另寫第二份規則」在別處反覆強調卻在這裡沒講清楚的地方。計劃文字只說「那種」借用方式,沒有承諾走「參數化既有函式」這條路,審查時無法判定會不會變成複製貼上的第二套上線點判定。

## F2 note-shape 的正文掃描範圍跟 lumos lint 目前實際檢查的範圍不同步,S3「同一套判定」目前不成立
severity: major
blocking: 是 —— S3 條款宣稱兩處判定一致,但既有呼叫點的實際掃描範圍比 note-shape 窄,等於同一條規則有兩套不同步的執行路徑,屬於條款3的第二種做法疑慮
引句:「lumos lint 對同一行應給同樣判定」
file: `scripts/lumos:4913-4914`、`scripts/lumos:5037`(`context_marker_warnings(summ)` 唯一呼叫點,`summ = n.fields.get("summary")` 只吃 frontmatter 的 `summary:` 欄位,完全沒有餵正文)
file: `docs/lumos-toolchain-knowledge/Verification/2026-08-01_slim-manifest殘留與代碼審六輪.md:20-21`(這篇筆記沒有 frontmatter `summary:` 欄位,`FLOW:` 摘要行寫在正文的「## Summary」小節裡)
說明:計劃在「範圍與行」明講「落在正文…算」,note-shape 因此會掃到這種寫在正文「## Summary」小節裡的 `FACT:`/`FLOW:`/`DEP:` 行;但 `lumos lint` 目前唯一的 `_CONTEXT_MARKER_RULES` 呼叫點只看 frontmatter 的 `summary:` 欄位,永遠看不到正文裡的這類行。也就是說在沒有額外修改 `lumos lint` 呼叫點、把正文也餵進 `context_marker_warnings` 之前,S3 要求的「`lumos lint` 對同一行應給同樣判定」寫不出會過的測試——這種正文摘要行只會被 note-shape 擋、`lumos lint` 卻從沒檢查過同一行,兩邊實質上各管各的,借來的是同一支函式,卻不是同一套「誰來餵它文字」的執行路徑。計劃需要明講是否要一併擴大 `lumos lint` 既有呼叫點的範圍(這本身是另一個有全庫既有筆記受影響的決定,計劃目前沒提到),否則 note-shape 會變成唯一真的落地這條規則的地方。

第4問 對齊:`scripts/lumos` 是一支被 37 篇以上 Systems 節點各自認領一部分責任的共用檔(`grep -rl "scripts/lumos$" docs/lumos-toolchain-knowledge/Systems/*.md` 命中 37 篇,例如 `Systems/每支檔有家.md`、`Systems/bound-tests-gate.md`、`Systems/check-j-regen-guard.md` 各自只管自己那塊邏輯),本 repo「每支檔有家」的實際做法本來就是「一個閘/子系統一篇家,不是一支檔一篇家」。note-shape 是全新的獨立子指令與規則集,不屬於 `Systems/每支檔有家`(那篇管的是檔案-節點配對,不是筆記內容形狀),另開 `Systems/筆記內容閘` 收留 note-shape 自己新寫的程式碼與決策,跟既有慣例一致。唯一要提醒的是:計劃改動的 `_CONTEXT_MARKER_RULES`(`scripts/lumos:2890-2901`)與 `_node_code_ref_tokens`(`scripts/lumos:19854`)是既有共用程式碼,搜尋全圖譜(`grep -rl "_CONTEXT_MARKER_RULES\|context_marker_warnings\|_node_code_ref_tokens\b" docs/lumos-toolchain-knowledge/Systems/*.md`)沒有找到任何既有節點指名認領這兩處——找不到既有家可寫回,不代表計劃有錯,但落點段落沒有提到「順便替這兩處程式碼確認/補一個家」,建議收工前用 `lumos impact --diff` 確認這兩處改動後有沒有觸發每支檔有家的新違規。此點不升 F,標 ⚠ 交編排者複核是否要補一句。

不對齊共 2 條,其中 major 2 條
