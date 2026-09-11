severity: major

三問逐答(每問附對照 file:line):

1. 分層與依賴方向:新碼全部留在 `_nodehome_*` 家族內(`_nodehome_stack_test_dirs` scripts/lumos:17783、`_nodehome_in_stack_test_dir` scripts/lumos:17802、`_nodehome_is_test` scripts/lumos:17824、`_nodehome_required` scripts/lumos:18005),呼叫的都是這組函式原本就在用的依賴(`TEST_PROFILES`、`side.all_paths`)。`_nodehome_required` 裡新增的 `top_dirs` 只讀同一個 `side` 物件既有欄位(`s.files, s.all_paths = lst`,scripts/lumos:17981),不是另開一條資料來源、也沒有跨層直呼鄰層(如直接呼叫 `_detect_test_dir` 那種走活體檔案系統的 scaffold 邏輯,scripts/lumos:8638)。判:分層方向跟鄰居一致,沒問題。

2. 命名與錯誤處理:變數命名(`top_dirs`/`sufs`/`base`/`ext`)、guard-before-use 風格(先 `top.endswith(suf)` 才切片、先確認有 `.` 才 `rsplit`,不用 try/except)、docstring 掛「★年月日 出處反例★」的註解慣例,都跟鄰近函式一致。快取寫法(`_NODEHOME_STACK_TEST_DIRS = None # lazy` 沿用既有的 `_TESTMAP_DIR_RE = None # lazy` 模式,scripts/lumos:19859)也沒有另開一種快取機制。判:命名/錯誤處理本身跟鄰居一致——問題出在下面問 3,是「重寫了一份邏輯」而非「寫法風格不同」。

3. 第二種做法:找到兩處,見 F1、F2。

### F1 副檔名判定另外手刻一份,沒用既有的 `_testmap_ext` / `Path(...).suffix.lower()`
severity: major
blocking: 是 — 專案裡已有「用 TEST_PROFILES 的 dot-prefixed exts 比對副檔名」的既定寫法 `Path(f).suffix.lower() in exts`(`discover_test_methods`,scripts/lumos:3894),同一支檔也有現成的 `_testmap_ext` 可用(scripts/lumos:19862)。新碼在 `_nodehome_in_stack_test_dir` 裡另外手刻一段 `rsplit`/`lstrip` 邏輯取副檔名,而且它的呼叫者 `_nodehome_is_test` 三行之後就真的呼叫了 `_testmap_ext(path)`(scripts/lumos:17833)——同一個函式的呼叫鏈裡並存兩種副檔名取法。新寫法保留 `.` 前綴、也不 `.lower()`,跟鄰居的大小寫不敏感比對行為不同(大小寫不同的副檔名會判不進去),是引入第二種做法。
引句:「ext = "." + name.rsplit(".", 1)[1] if "." in name.lstrip(".") else ""」
佐證 file: `scripts/lumos:17816`

### F2 頂層資料夾集合另外重算一份,沒沿用 `_nodehome_refs` 既有算法
severity: major
blocking: 是 — 同一支檔案裡 `_nodehome_refs` 已經有「從 `side.all_paths` 抽頂層資料夾名」的寫法(scripts/lumos:18061),而且明確排除點開頭項目(`not p.startswith(".")`,避免把 `.git`/`.github` 這類目錄當成頂層程式資料夾)。新碼在 `_nodehome_required` 另外寫一行幾乎相同的算法(scripts/lumos:18009),卻沒有那個排除條件——是同一概念(「這個版本 repo 頂層有哪些資料夾」)的第二種算法,行為跟鄰居不同。
引句:「top_dirs = frozenset(p.split("/", 1)[0] for p in side.all_paths if "/" in p)」
佐證 file: `scripts/lumos:18009`

總結:最高 severity major,blocking 共 2 條
