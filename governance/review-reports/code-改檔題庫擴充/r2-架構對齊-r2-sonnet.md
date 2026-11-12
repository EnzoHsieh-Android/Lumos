severity: minor

整體結論:新碼沒有跨層直呼,也沒有引入第二種做法;只有兩條寫法跟鄰居不一致的 minor。

## 問 1 分層與依賴方向:對齊
- **載入掛鉤**
  - `_load_hook` 用 `importlib.util.spec_from_file_location` 加 `exec_module` 載入 `impact-hook.py`。這跟鄰居 `refresh_labels._load_re` 同一套寫法。
  - 對照:`governance/eval/refresh_labels.py:34-38`、`governance/eval/home_audit.py:46-48`。
  - 它呼叫掛鉤自己的 `_decide_one`(`scripts/hooks/claude/impact-hook.py:149`),沒有另抄一份副檔名清單。這是重用,不是跨層直呼。
- **依賴方向**
  - 呼叫鏈是 `main` → `_run_append` → `edit_cases` / `edit_pool` / `append_edit_cases`。
  - 外部資料仍然只經過 `lum_json` / `lum_lines`(`search_pool` 與 `edit_pool` 在用)和 `git -C`,方向沒變。
- **快取**
  - 行程內字典快取 `_HOOK_CACHE` 跟 `scripts/lumos:67014` 的 `_REPO_FILES_CACHE` 同型。
  - 差別只在 `refresh_labels._load_re` 不快取,這算快取有無,不算第二種做法。
- **測試端**
  - 新增的 `_load_build_goldset`(`scripts/test_lumos.py:45480`)跟同檔 `_load_retrieval_eval`(`scripts/test_lumos.py:45405`)是同一型 fixture 載入器。
  - 它也沿用同檔 `_need_src`、`check`、`_git_init_commit`、`tempfile.mkdtemp` 加 `shutil.rmtree` 的慣例。

## 問 2 命名與錯誤處理:大致對齊,2 條 minor
- 對齊的部分
  - 私有函式一律 `_` 開頭,跟 `_is_junk_edit_file`、`_run_append` 一致。
  - 參數驗證失敗時,`print("ERROR: …", file=sys.stderr)` 加 `return 2`,跟 `refresh_labels.py:47`、`refresh_labels.py:210` 的慣例一致。
  - 子程序呼叫維持 `capture_output=True, text=True`,另外加了 `errors="replace", check=False`。
  - 沒有日誌函式,只用 stderr 印字,跟鄰居一致。
- 不對齊 1:出題腳本頂部 `build_goldset.py:9` 已有 `ROOT = Path(__file__).resolve().parents[2]`,新增的 `HOOK` 常數卻在 `build_goldset.py:145` 重新算一次 `parents[2]`。
- 不對齊 2:「同檔名額已滿、同提交、同改動片段」這組判斷,在三處各寫了一遍。
  - 出現位置:`append_edit_cases`、`_run_append` 的預先過濾、`edit_cases`。
  - 資料結構已抽成共用的 `_edit_quota`,但判斷式本身沒有抽。
  - 鄰居同目錄的作法是共用判斷:`_is_junk_edit_file` 被 `edit_cases` 與 `append_edit_cases` 共用,`_edit_quota` 的 docstring 也寫了「兩端共用同一套」。
  - `_run_append` 的註解自己說明這是「預先過濾、最後把關是同一套」,所以屬於刻意重複,結構上沒錯。

## 問 3 第二種做法:沒有
- 沒有新的 HTTP client、DI 方式或狀態管理。
- 掛鉤載入、快取、`git -C`、`argparse` 都沿用鄰居與主程式既有的寫法。
- 測試裡用 `m.edit_cases = lambda …` 和 `m.edit_pool = lambda …` 對載入的模組做 monkeypatch。這跟 `_load_retrieval_eval` 之後 `m.ROOT = root` 的模組屬性覆寫同一路,不算新做法。

## Finding
**F1(minor)**:`HOOK` 常數沒有重用同檔已有的 `ROOT`。
- 歸因:未判定。兩端之間只有一個修補提交 `e3ecb0a2`,程式與測試沒有拆開,看不出這行是修補前就有還是修補新增。

severity: minor
blocking: no
引句:「HOOK = Path(__file__).resolve().parents[2] / "scripts" / "hooks" / "claude" / "impact-hook.py"」
對照:`governance/eval/build_goldset.py:9`(`ROOT` 的定義)

**F2(minor)**:「名額已滿、同提交、同改動片段」的判斷式在三處各寫一遍,沒有抽成共用的判斷函式。
- 歸因:未判定,理由同 F1。

severity: minor
blocking: no
引句:「if per.get(f, 0) >= per_file or (f, c["commit"]) in seen_commits or (f, c["delta"]) in seen_deltas:」
對照:`governance/eval/build_goldset.py:94-97`(`append_edit_cases` 內的同一判斷);鄰居共用判斷的做法見 `governance/eval/build_goldset.py` 的 `_is_junk_edit_file`

不對齊共 2 條,其中 major 0 條。

棧別檢核題 py-eventloop 答 na,與本次沒有撞到,沒有 tension。
