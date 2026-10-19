severity: major

三問都對照了 9591e609 的 `scripts/lumos`。三項要求中,記憶別用 lru_cache 與中段 import、快取名字對上共用讀檔這兩項有做到;時鐘改參數也有做,但寫法有一處小出入。另外,新的 `_KT_SCAN_TOKEN` 是一套專案裡已有做法之外的第二套剝註解實作。

## 1. 分層與依賴方向

結構沒有跨層直呼,依賴方向和鄰居一致。

- **讀檔快取**
  - `_node_pkg_text` 這個只轉手的包裝已刪掉,`_node_flavor` 的 reader 直接呼叫 `_worktree_text`。這對上了上一輪「快取名字對上共用讀檔」的要求。
  - 快取更名為 `_WORKTREE_TEXT_CACHE`,`scripts/lumos:30276`,和函式名、docstring 一致。全檔已搜不到 `_NODE_FLAVOR_CACHE`、`_node_pkg_text`、`_ROLE_CLOCK`。
- **判定記憶**
  - `lru_cache` 和中段 `import functools` 都拿掉了,改成模組層 dict 加上限常數,`scripts/lumos:30393`。
  - 逐出寫法是「滿了丟最早那筆」:`pop(next(iter(...)))`。專案已有同一寫法,`route_cache` 在 `scripts/lumos:33679`。另一個有上限的快取 `_DRIFT_LS_CACHE`(`scripts/lumos:41336`)用的是整個清掉,但它的註解已自承「跟本檔其他快取不同」。所以上限做法沒有引入新東西。
- **先問大小再讀**
  - `_review_roles` 先 `_nodehome_cat_sizes`,再把 `sizes=` 傳進 `_nodehome_cat_blobs_capped`。這和既有呼叫端同形,見 `scripts/lumos:38805` 傳 `sizes=[size]`、`scripts/lumos:34752` 先問大小。
  - 「物件在但超限」改成空字串,語意對齊 `_worktree_text`。`timeout=max(0.2, budget - (_now() - t0))` 是手算剩餘時間,沒有走 `deadline=` 參數。原因是 `deadline` 底層用真時鐘(`_git_timeout`,`scripts/lumos:50851`),而這裡要吃注入的虛擬時鐘,可以接受,不算分歧。

## 2. 命名與錯誤處理

沒有命名或回傳碼上的不一致,只有一處小出入。

- **時鐘參數**
  - `_review_roles(..., now=None)` 加 `_now = now or _t.monotonic`,`scripts/lumos:30608`。
  - 該行註解寫「照 `_drift_old_sentence_check` 的 now= 先例」,但那個先例是 `now=time.monotonic`,在定義時就綁死,見 `scripts/lumos:44773`。
  - 新寫法是預設 `None`、呼叫時才取值,形狀其實跟 `now = now or ...` 那一類一致,例如 `scripts/lumos:4366`。同檔兩種 `now=` 都有先例,結構沒歪,只是註解引的先例和實際形狀不同。
- **正規式與守衛**
  - 行首空白改成 `[ \t]*`,和同區既有的 `_KT_BUILD_ANDROID` 一致。
  - `_linter_config_hits` 的 `isinstance(..., dict)` 和該函式上方的防禦寫法一致。
- **常數與函式命名**:`_KT_BUILD_VERDICT_MAX`、`_KT_BUILD_VERDICT_CACHE` 沿用同區 `_KT_*` 前綴。

severity: minor
blocking: 否
引句:「_now = now or _t.monotonic」
理由:註解說「照 now= 先例」,但先例 `now=time.monotonic` 是定義時綁定,這裡是預設 None 再取值。兩種寫法在專案內都存在,僅註解引的先例對不上。⚠ 可由編排者決定要不要改註解。

## 3. 第二種做法

專案原本已有 c-style 註解剝除的做法,新碼另起一套,這是本輪最主要的不一致。

- **既有做法**
  - `_strip_test_comments(txt, strip)`,`scripts/lumos:6273`,是整段文字剝 `//` 與 `/* */`。
  - 單行字串用 `_PITFALL_STRLIT_RE` 加 `_strip_string_literals`,`scripts/lumos:30825-30831`,另有單行的 `_stack_norm_line`。
  - 文字寫的是「不許第二份實作」。`_quote_norm` 的 docstring 有「嚴禁第二份實作」,`_strip_test_comments` 也有「共用這一份」的紀律。
- **新碼**
  - `_KT_SCAN_TOKEN`,`scripts/lumos:30375`,是專案內第三套「字串加註解」的正規式。字串樣式 `"(?:\\.|[^"\\\n])*"` 與 `_strip_test_comments` 的字串樣式相同,`""" … \Z` 與 `/* … \Z` 吃到檔尾的行為是新的。
  - `_kt_strip_comments` 位置在 Kotlin 建置檔區,沒放在 `_strip_test_comments` 旁邊,也沒說為什麼不延伸那一支。
- **理由是否站得住**
  - 它是為了修「先剝區塊再剝行註解會被字串帶歪」才改成單一掃描,動機成立。
  - 但合乎專案做法的路是把「字串感知」做進既有的 `_strip_test_comments`,或至少在 docstring 寫明不共用的理由。現在是第二套實作並存。
  - 上一輪已有自寫剝註解,本輪是換成另一套自寫的,沒有收斂到既有 helper。

severity: major
blocking: 是
引句:「return _KT_SCAN_TOKEN.sub(lambda mo: "" if mo.group(0)[:2] in ("//", "/*") else mo.group(0), txt)」
理由:這是專案內第二套多行 c-style 剝註解實作,與 `scripts/lumos:6273` 的 `_strip_test_comments` 並存,字串樣式也和 `_PITFALL_STRLIT_RE` 重複。⚠ 若編排者認定「字串感知」足以構成不能共用的理由,可降為 minor,但至少要補一句不共用的理由,或把掃描器移到 `_strip_test_comments` 旁。

不對齊共 2 條,其中 major 1 條

相關檔案:`/Users/enzo/orca/workspaces/lumos-toolchain/web-react/scripts/lumos`
