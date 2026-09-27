severity: major

## 三問逐答

**1. 分層與依賴方向**
沒有新的跨層直呼——`cmd_note_shape` 仍只呼叫既有同層工具:`_lens_range_ok`(`scripts/lumos:23968`)、`_lens_full_sha`、模組層常數 `_EMPTY_TREE_SHA`(`scripts/lumos:29838`)。新增的 `if re.fullmatch(...)` 區塊(`scripts/lumos:23979-23982`)在同一支函式內、同一層,沒有繞過或跨過任何邊界。
但這也正是問題所在:40 個 0 → 空樹的正規化,語意上屬於「`--diff` 範圍怎麼解析」,而這件事這個 repo 已經指定共用層 `_lens_range_ok`(`scripts/lumos:28081-28090`)在管——`cmd_home_check`(`scripts/lumos:23370`)跟 `cmd_note_shape`(`scripts/lumos:23968`)兩個呼叫端目前呼叫的是同一支。這份 diff 把正規化寫進其中一個呼叫端裡面,而不是共用層——詳見 F1(對應第 3 問)。

**2. 命名與錯誤處理**
錯誤訊息、rc、fail-open 語意都跟同函式既有寫法(`筆記形狀擋:範圍 … 在本機找不到,跳過(fail-open)`,`scripts/lumos:23986`)一致,沒有另創詞彙。
兩處小不一致:
- doctor 建議的 CI 片段只加了 `case` 判斷,沒有補本專案 `ci.yml` 兩處同型步驟都有的 `git cat-file -e … || BEFORE=$EMPTY` 後備行(見 F2)。
- 40 個 0 的判斷用了行內未編譯的 `re.fullmatch(r"0{40}", a or "")`,而同一區塊本來的慣例是模組層編譯好的常數,如 `_LENS_SHA_RE = re.compile(...)`(`scripts/lumos:28063`,就在 `_lens_full_sha` 旁邊、同一支函式會用到)(見 F3)。

**3. 第二種做法**
是。專案已經有兩層現成的「40 個 0 → 空樹」機制:
- shell 層:`.github/workflows/ci.yml:110`(code-loop gate)與 `.github/workflows/ci.yml:134`(note-shape gate 自己的既有步驟)都是 `case "$BEFORE" in 0000000000000000000000000000000000000000|"") BEFORE="$EMPTY";; esac`。
- Python 層:`_bound_tests_range`(`scripts/lumos:29841-29871`)假設呼叫端已經把起點換成 `_EMPTY_TREE_SHA`,只用 `r.startswith(_EMPTY_TREE_SHA)` 判斷,不認 40 個 0。

這份 diff 沒有把新邏輯放進兩者共用的 `_lens_range_ok`(`scripts/lumos:28081`),而是在 `cmd_note_shape` 內再寫一份行內判斷(`scripts/lumos:23979-23982`)。結果是:結構完全相同、呼叫同一支 `_lens_range_ok` 的姊妹指令 `cmd_home_check`(`scripts/lumos:23370-23384`,同樣是 `base = a if a == _EMPTY_TREE_SHA else _lens_full_sha(root, a)` 這行,`scripts/lumos:23377`)完全沒有拿到這個修法——40 個 0 當起點時,`home check` 現在還是會走到 `_lens_full_sha` 解析失敗、印「範圍在本機找不到,跳過(fail-open)」而整批放行,跟這份 diff 要修的 note-shape 漏洞是同一個洞,只是沒被一起堵上。

---

### F1 40 個 0 正規化寫成呼叫端局部邏輯,沒有進共用的 `_lens_range_ok`,姊妹指令仍是原洞
severity: major
blocking: 是 —— 這是同一段「`--diff` 範圍怎麼把 40 個 0 當空樹」的邏輯,在專案裡新開第三種寫法(shell case、`_bound_tests_range` 的 `startswith` 假設之外),沒放進兩個呼叫端共用的 `_lens_range_ok`;結構相同的 `cmd_home_check` 對同一種輸入(新分支首推)行為沒變,還是 fail-open 放行,兩支姊妹閘現在對「40 個 0」這件事行為不一致。
引句:「if re.fullmatch(r"0{40}", a or ""):」
file: `scripts/lumos:23979` 對照 `scripts/lumos:23377`(`cmd_home_check` 同型解析,未修)與 `scripts/lumos:28081`(共用的 `_lens_range_ok`)

### F2 doctor 建議的 CI 片段少補了本專案自己兩處同型步驟都有的 `git cat-file` 後備
severity: minor
blocking: 否 —— 結構對(用同一顆 `case` 慣例、同一個 `_EMPTY_TREE_SHA` 值),只是給消費專案抄的片段比本專案自己在跑的版本少一層防線(非零但本機解不出來的 `BEFORE`,如 force-push/歷史被剪,ci.yml 會再退回空樹,doctor 給的片段不會);不影響本專案自己的 CI,因為 `ci.yml` 本身沒被這份 diff 改動,仍保留 cat-file 那行。
引句:「B=4b825dc642cb6eb9a060e54bf8d69288fbee4904;; esac; 」
file: `scripts/lumos:23888` 對照 `.github/workflows/ci.yml:134-135`(同一個 note-shape gate 步驟,多一行 `git cat-file -e "$BEFORE^{commit}" 2>/dev/null || BEFORE="$EMPTY"`)

### F3 40 個 0 的比對用行內未編譯 regex,沒有沿用同函式旁既有的模組層編譯常數慣例
severity: minor
blocking: 否 —— 純命名/寫法層級,不影響正確性或分層,且只出現一次、不是熱路徑。
引句:「re.fullmatch(r"0{40}", a or "")」
file: `scripts/lumos:23979` 對照 `scripts/lumos:28063`(`_LENS_SHA_RE = re.compile(...)`,與 `_lens_full_sha` 同區塊)

---

不對齊共 3 條,其中 major 1 條。
