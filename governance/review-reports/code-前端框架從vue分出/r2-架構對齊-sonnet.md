severity: major

這份回報只靠讀碼和 grep 對照,沒有跑 `lumos pitfalls --diff`。對照基準是修後 b9ff5494 的 `scripts/lumos`,我把它取出來比對,下面的行號都是那一版的。

上一輪的兩項要求都做到了:
- **不另立第二套讀檔快取:** 做到了。`_worktree_text`(`scripts/lumos:30292`)沿用原本的 `_NODE_FLAVOR_CACHE`,`_node_pkg_text` 改成薄包裝。
- **`android_only` 照 `shape_only` 在出題函式內消化:** 做到了。`_stack_applicability` 多了 `exclude` 參數(`scripts/lumos:30759`),`_stack_whole_group`(`scripts/lumos:30257`)統一派生舊語意清單。三個呼叫點是 `scripts/lumos:47536`、`scripts/lumos:47554`、`scripts/lumos:50358/50364`,都走同一條路。

但修補又帶進兩處新的做法,見下。

## 1. 分層與依賴方向

結構與鄰居一致,沒有跨層直呼。

- 新的 Kotlin 判定函式(`_kt_flavor_at`、`_kt_flavor`、`_kt_role`、`_stack_platform_excluded`)放在 `_node_flavor` 與 `_stack_key_for_file` 之間。這是「判棧別」那一層,跟 package.json 的判定同位。
- 出題端(`_pitfall_diff_collect`、`cmd_impact`)只呼叫 `_stack_platform_excluded` 和 `_stack_whole_group`。角色端(`_review_role_for`)只呼叫 `_kt_role`。
- 讀取走批次讀取(`_nodehome_cat_blobs_capped`)或 `_worktree_text`。新增的 `max_total_bytes=_ROLE_MAX_TOTAL_BYTES` 用的是既有參數,同層的 `scripts/lumos:33634` 也這樣用。
- `_ROLE_MAX_TOTAL_BYTES` 緊貼 `_ROLE_MAX_BYTES` 放置,位置一致。

## 2. 命名與錯誤處理

出題端的消化方式和錯誤處理跟鄰居一致,有一處命名與鍵形狀的不一致。

- **一致:**
  - `android_only` 與 `shape_only` 同為題目規格裡的布林旗標。
  - 「讀不到回空字串、沒有檔回 None」沿用原 `_node_pkg_text` 的語意,`except OSError` 也同。
  - 判錯方向只准落在「判不出」,這點跟 `_node_flavor` 的做法同調。
- **不一致(minor):**
  - `_NODE_FLAVOR_CACHE`(`scripts/lumos:30276`)原本專放 node 的 package.json,鍵是字串。現在要放 Kotlin 建置檔和 `.kt` 檔頭,鍵也變成三元組(`scripts/lumos:30298`)。函式改名叫 `_worktree_text`,快取變數沒跟著改名。
  - 這點看起來能用,只是會誤導讀的人。

severity: minor
blocking: 否
引句:「key = (str(Path(repo_root) / rel), head, max_bytes)」
file: `scripts/lumos:30276`

## 3. 第二種做法

我先搜了專案內有沒有先例。專案的快取全是模組層 `_X_CACHE = {}` 加測試 `.clear()`(例如 `scripts/lumos:30276`、`:41313`、`:49346`、`:49390`、`:49697`)。時間注入的先例是以參數傳入,不是模組層全域。

**(a) `lru_cache` 是專案裡唯一的一處 `functools` 用法。**
- 整份 `scripts/lumos` 只有這一處用 `functools`。
- 其他派生結果的記憶都是模組層 dict。例如 `_DRIFT_OID_CACHE` 是依附 `_DRIFT_LS_CACHE` 的派生快取,測試一律呼叫 `.clear()`。
- 這裡還為它在檔案中段加了 `import functools as _functools`。專案慣例是函式內延遲匯入,或檔頭匯入。
- 測試也因此要用另一套重置法:`m._kt_build_verdict.cache_clear()`,見 `scripts/test_lumos.py:98424` 與 `:98445`。
- 上一輪架構席要的就是不另立第二套快取。讀檔那層守住了,判定結果這層又多了一種機制,所以我判 major。
- 改法:用 `_KT_BUILD_VERDICT_CACHE = {}` 加現有的 `.clear()` 慣例。

severity: major
blocking: 是
引句:「import functools as _functools   # 只給下面這支記憶判定結果用」
file: `scripts/lumos:30403`

**(b) `_ROLE_CLOCK` 是模組層可替換的時鐘。** ⚠ 判不準,交編排者。
- 專案裡可替換時鐘的先例,形式是函式參數或物件欄位:
  - `now=time.monotonic`:`scripts/lumos:44770`,docstring 寫「測試換掉它來造『掃到一半時間到』」。
  - `run.now()`:`scripts/lumos:44676`。
- 另有 `self._t` 持有 time 模組(`scripts/lumos:41444`),但不是為了替換。
- 模組層「`= None` 就用預設」的全域開關,專案裡有,但用途是 lazy 快取(`_STACK_GUESS_CACHE`、`_TESTMAP_DIR_RE`),不是時鐘。所以 `_ROLE_CLOCK` 在「時鐘」這個用途上沒有先例。
- `_review_roles` 本來就有 `budget=` 參數,最貼近先例的做法是補一個 `now=time.monotonic` 參數。測試端現在是 `m._ROLE_CLOCK = lambda: ...` 並在 finally 還原(`scripts/test_lumos.py:98468` 至 `:98477`)。
- 理由是注入的意圖有先例,只是形式不同,所以我判 minor。編排者若認為模組全域時鐘本身就是新做法,可升為 major。

severity: minor
blocking: 否
引句:「_now = _ROLE_CLOCK or _t.monotonic   # 測試可換成虛擬時鐘,讓預算判定跟機器快慢無關」
file: `scripts/lumos:30612`

## 小結

不對齊共 3 條,其中 major 1 條。
