severity: clean

三問逐答:

**1. 分層與依賴方向**
新增的三支共用函式 `_nodehome_top_dirs`(`scripts/lumos:17802`)、`_nodehome_layout`(`scripts/lumos:17808`)、`_nodehome_in_stack_test_dir`(`scripts/lumos:17827`)全部留在 `_nodehome_*` 家族內,只被同層的 `_nodehome_is_test`(`scripts/lumos:17856`)、`_nodehome_required`(`scripts/lumos:18037`,呼叫處 `18041`)、`_nodehome_refs`(`scripts/lumos:18090`,呼叫處 `18093`)呼叫;三者本來就是既有呼叫鏈的節點,呼叫方向沒變(誰呼叫誰跟上一輪一致)。這輪新增的兩支 helper 沒有反過來被 `_detect_test_dir`(`scripts/lumos:8638`,scaffold 用的活體檔案系統走法)或 CLI/hook 層直呼——沒有新的跨層直呼。
引句:「top_dirs = _nodehome_top_dirs(side.all_paths)」
佐證 file: `scripts/lumos:18093`

**2. 命名與錯誤處理**
新函式命名沿用既有 `_nodehome_*`/`_NODEHOME_*` 字首與延遲快取慣用法——`_NODEHOME_STACK_TEST_DIRS = None`(`scripts/lumos:17780`)跟 `_TESTMAP_DIR_RE = None  # lazy`(`scripts/lumos:19891`)是同一個「模組級單例、global 守衛」模式;四支新函式都是純函式、沒有 try/except,跟同區塊 `_nodehome_resp_ok`、`_nodehome_code_kind` 一樣不包例外。沒有發現命名或錯誤處理跟鄰居不一致的地方。
引句:「_NODEHOME_STACK_TEST_DIRS = None   # lazy:({頂層資料夾結尾樣式」
佐證 file: `scripts/lumos:17780`

**3. 第二種做法**
這輪(對第二輪修正的差異,`r3-delta.patch`)正是在收斂第二輪架構對齊席抓到的兩個 major(F1 副檔名另手刻一份、F2 頂層資料夾另算一份)——現在 `_nodehome_in_stack_test_dir` 改呼叫既有的 `_testmap_ext`(定義於 `scripts/lumos:19894`),不再自己 `rsplit`/`lstrip`;`_nodehome_required`(`18041`)與 `_nodehome_refs`(`18093`)都改呼叫同一支新抽出的 `_nodehome_top_dirs`(`17802`),不再各自重算一份「頂層資料夾」。全檔搜了 `split("/", 1)[0]` 這個模式,只剩 `scripts/lumos:17805`(即 `_nodehome_top_dirs` 自己)這一處,沒有殘留第三份。`_nodehome_stack_test_dirs`(`17783`)仍是從 `TEST_PROFILES`(`3487`)動態推導,不是另寫清單,跟第一輪認過的路數一致;它讀 `TEST_PROFILES` 的方式(`dir_mode`/`rglob_under`)跟既有 `_detect_test_dir`(`8638`)是同一種讀法、語意一致,不是另一套解讀。沒找到引入第二種做法或另一套漂移守衛寫法。
引句:「e = _testmap_ext(p)」
佐證 file: `scripts/lumos:17814`

總結:最高 severity clean,blocking 共 0 條
