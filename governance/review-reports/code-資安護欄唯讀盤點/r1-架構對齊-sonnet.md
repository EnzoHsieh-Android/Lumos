severity: major

## 1. 分層與依賴方向

結構大致對齊,但有一處第二種做法(見第 3 問)。

- **放的位置:** `cmd_security_list` 放在 `cmd_contracts` 之後,屬於 `cmd_*` 唯讀指令層。它只呼叫 `_secinv_*` 私有輔助函式和既有的 `Env.from_texts`、`extract_contracts`、`status_of`、`_verification_status`、`_node_decisions`、`_pq_decision_target`、`_dref_parse`。這些都是同層共用的既有函式,沒有跨層直呼。
- **圍欄判定:** 抽成共用的 `_fence_regions`,讓 `_visible_lines` 和 `security list` 共用,沒有另寫第二套 toggle。這和專案「同一件事一個判法」一致。
- **`_regular_own_fd`:** 新加的 `dir_fd=None` 預設不變,既有呼叫端行為不動。它沿用既有的 `O_NOFOLLOW`、`O_NONBLOCK` 和開檔後判一般檔,沒有另抄一份。
- **呼叫端對照:** file: `scripts/lumos:1388`(base 版 `_regular_own_fd`),`scripts/lumos:15574`(`_retro_read_bytes`),`scripts/lumos:26255`(`.gitignore` 讀寫)。
- **簽名差異:** 鄰居 `cmd_contracts(env, rel)` 收 `env`,新指令 `cmd_security_list(vault, as_json)` 收 `vault`。這是刻意的:安全讀取之後才建 `Env`,所以只是形狀不同,不算跨層。
- **派發位置:** 鄰居 `contracts` 在 main 的 `vault = args.vault or find_vault(...)` 與 `env = Env(vault)` 之後派發(file: `scripts/lumos:59074-59078`)。新指令插在這兩行之前,繞過一般 `Env(vault)`。先於 `Env(vault)` 派發本身有前例(`loop capture counts` 在 `scripts/lumos:59071` 先派發)。差別是它繞過的是「讀圖譜」這一條路。

## 2. 命名與錯誤處理

- **命名:** `_secinv_*` 前綴一致,符合專案「功能前綴加底線」的慣例,例如 `_kill_*`、`_pq_*`、`_dref_*`。
- **擋下訊息:** 「擋下:{_serr}」寫到 stderr 並回 2,和 `cmd_enforcement` 的「擋下:--repo 指的不是目錄」同形。
- **子命令結構:** `security` 加 `list` 的巢狀 `add_subparsers(dest="seccmd", required=True)` 沿用既有慣例,例如 `accmd`、`ccmd`、`drcmd`。`--json` 用 `dest="sec_json"`,也和 `q_json`、`dh_json` 一致。
- **不一致一:退出碼語意。** 專案的唯讀檢查類是「發現問題 rc1,擋下或用法錯 rc2」,例如 `cmd_contracts` 回 `1 if errs else 0`(file: `scripts/lumos:6687`),`doctor strict` 也是 1。新指令把內容層的問題(schema、引用、讀取不完整)全回 rc2,rc1 沒用到。外層腳本可能分不出「用法錯」和「資料有問題」。
- **不一致二:新的錯誤種類詞彙。** 新增一組英文 snake_case 的 `kind` 詞彙,例如 `read_error`、`not_utf8`、`enumeration_failed`、`changed_during_read`。既有的讀檔失敗走中文 `_READ_FAIL = "讀檔失敗"` 加 `Note.lint`(file: `scripts/lumos:624`),治理事件的 `kind` 是 `blocked`、`warned`、`unreadable`、`stale`。`not_utf8` 在這裡同時用自己的種類名記一次錯,又交給 `Env.from_texts` 的 `unreadable` 管道再記一次。它是 `security list` 專屬的錯誤集合,跟既有的種類名沒有對照,日後治理帳或別的指令要吃這份錯誤時得多寫一層翻譯。

## 3. 第二種做法

先搜過,有兩處。

**(a) 新的圖譜讀取路徑。**
- 既有的圖譜讀取是 `load_vault` 加 `Env(vault)`(`rglob` 加 `read_text`)。這次另寫一整套:`_secinv_enumerate`、`_secinv_walk`、`_secinv_open_rel`、`_secinv_read_rel`、`_secinv_snapshot`,以及自己的單檔、總量、檔數上限。再把讀進來的文字交給 `Env.from_texts`。
- 這套是第二種「讀圖譜」的做法。diff 裡的註解也自己承認:一般載入跟隨捷徑、沒有容量上限。
- 不是改良 `load_vault`,而是新增一條只給資安盤點用的 vault 讀取路徑,vault 讀取因此有兩套分歧的規則(是否跟隨捷徑、有無上限)。
- 重判:我判定這確實是引入第二種做法,依規則標 major 加 blocking: 是。它有計劃依據(`Projects/資安護欄唯讀盤點_計劃`),是否接受這個例外,交編排者裁。⚠

**(b) 新的圖譜定位邏輯。**
- 既有的 `find_vault` 加 `_vault_in`(file: `scripts/lumos:27450-27475`)管「從 cwd 往上找 docs/*-knowledge、docs/knowledge、獨立 vault root」。
- `_secinv_select_vault` 把這三個候選規則整套重抄一份,只多一條「同層不只一個就報錯」。多出來的這一點是真需求,但完全可以給 `_vault_in` 加參數(例如回傳全部候選)重用,不必複製候選規則。日後 `_vault_in` 新增一種佈局時,`security list` 會悄悄落後。

### 不對齊清單

severity: major
blocking: 是
引句:「★不走下面的 Env(vault)★:一般載入會 read_text 跟隨捷徑、沒有容量上限」

(第 3(a):第二套圖譜讀取路徑。有計劃依據,⚠ 是否接受這個例外交編排者裁。)

severity: major
blocking: 是
引句:「find_vault 會取排序第一個,這裡不能沿用那個猜法」

(第 3(b):`_secinv_select_vault` 重抄了 `_vault_in` 的候選規則,而不是擴充它。)

severity: minor
blocking: 否
引句:「_SECINV_READ_KINDS = frozenset(("unsupported_safe_read", "read_error", "enumeration_failed", "symlink_rejected",」

(第 2 問:新的英文 snake_case 錯誤種類詞彙,跟既有的 `_READ_FAIL` 管道和治理事件 `kind` 都不對照。)

severity: minor
blocking: 否
引句:「return 0 if rep["read_complete"] and not rep["errors"] else 2」

(第 2 問:專案慣例是發現問題 rc1,擋下或用法錯 rc2;這裡把內容問題也歸 rc2。)

不對齊共 4 條,其中 major 2 條。

審材外佐證:file: `scripts/lumos:27450`(`_vault_in`),file: `scripts/lumos:624`(`_READ_FAIL`),file: `scripts/lumos:6687`(`cmd_contracts` 回 `1 if errs else 0`),file: `scripts/lumos:59071`(先於 `Env(vault)` 派發的前例)。

我沒有跑 `pitfalls --diff`,也沒有動 `security-list` 工作樹。這份審查是對照 base 版 `scripts/lumos`(`ec4c6307`)讀 diff 得出的,base 版放在 scratchpad 的 `base.py`。
