severity: minor

結論:沒有第二種做法,也沒有跨層直呼。我只找到一條 minor,是命名與慣例上的小不一致。

**1. 分層與依賴方向:對齊**
- 新碼放在 `governance/eval/build_goldset.py`,這是出題流水線本來的位置。它呼叫 `lum_json` 和 `git -C`,這跟舊碼一樣(`build_goldset.py:24` 的 `cwd=ROOT`、`scripts/lumos` 子程序)。
- 新增的 `_edit_quota` 同時給 `append_edit_cases` 和 `_run_append` 用,依賴方向沒變。
- 對掛鉤腳本的依賴是單向的。出題腳本載入 `scripts/hooks/claude/impact-hook.py`,掛鉤不反向認識出題腳本。
- 派工詞點名的「用 importlib 從路徑載入掛鉤」不算第二種做法。專案裡要共用另一支腳本時,本來就用 importlib 依路徑載入,有三處:
  - `scripts/test_lumos.py:54761` 的 `_load_hook_mod`,用 `SourceFileLoader` 載入 `impact-hook.py`,並在 `test_lumos.py:12804` 呼叫它的私有函式 `imp._shebang_is_code`。
  - `governance/eval/refresh_labels.py:35` 用 `spec_from_file_location("retrieval_eval", HERE / "retrieval_eval.py")` 載入。
  - `governance/eval/home_audit.py:46` 用 `SourceFileLoader` 載入。
- `impact-hook.py` 檔名有連字號,不能用 `import` 直接引入,只能用路徑載入。`retrieval_eval_multiword.py:31` 靠 `sys.path` 直接 import `retrieval_eval`,是因為對方檔名合法,不適用這個情況。
- 呼叫底線開頭的 `_decide_one`,測試端也有先例(`test_lumos.py:12804`)。`impact-hook.py:146` 的公開入口帶的是 payload 解析,不是單檔判斷。
- 這個做法本身有理由:diff 的註解說明了要避免抄第二份副檔名清單。這跟 `retrieval_eval_multiword.py:10` 的「計分函式一律從 retrieval_eval import,不另寫一份」是同一個原則。

**2. 命名與錯誤處理:大致對齊,一條 minor**
- 私有函式的底線前綴、中文 docstring 加 `★…★` 標記、`print(..., file=sys.stderr)` 後回傳 2 這幾點,都跟鄰居一致。例如新增的 `--per-file`、`--window` 檢查,跟 `refresh_labels.py` 和 `retrieval_eval_multiword.py:80` 的 `ERROR:` 格式相同。
- 測試端沿用 `t_goldset_*` 命名、`check(...)`、`_git_init_commit`,跟 `t_goldset_append` 一樣。

**3. 第二種做法:無 major**
- 沒有新的 DI、HTTP client 或狀態管理。
- `_edit_quota` 是把原本散在兩處的「算不算重複」邏輯收成一個,是整併,不是另起一套。

**不對齊的 finding**

1. 掛鉤模組的快取寫法
   - 新碼用模組級空 list `_HOOK_MOD = []`,再用 `if not _HOOK_MOD:` 做延遲載入並快取。鄰居的 `refresh_labels._load_re`(`refresh_labels.py:34`)、`home_audit.py:46` 是每次呼叫直接載入,或在模組頂層載入一次,沒有「全域 list 當單例」這種寫法。
   - 另外 `spec_from_file_location` 加 `HOOK` 路徑這個機制,跟 `test_lumos.py:54761` 的 `SourceFileLoader` 變體不同。但 `refresh_labels.py:35` 就是 `spec_from_file_location`,所以這部分專案本來就有兩種寫法並存,不算新增。
   - 結構是對的,只有快取的寫法跟鄰居不同。
severity: minor
blocking: no
引句:「_HOOK_MOD = []」
對照: `governance/eval/refresh_labels.py:34`

不對齊共 1 條,其中 major 0 條

⚠ 交編排者:專案裡載入同層腳本的做法已有 `spec_from_file_location` 和 `SourceFileLoader` 兩種並存,鄰居本身就不一致。這份 diff 選了其中一種,我沒有判它偏離。
