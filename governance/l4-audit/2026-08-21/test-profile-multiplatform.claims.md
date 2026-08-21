C1. `load_platforms(repo_root)` 讀 `.lumos/config.json` 的 `platforms` 鍵，回傳 `{multiplatform, default_platform, platforms:{plat:{profile,root}}}`；無 `platforms` 鍵時視為 legacy 單一條目 | 預期驗證點: scripts/lumos 的 `load_platforms` 函式；測試 t_load_platforms

C2. `resolve_test_refs(inv_text, platforms, default_platform)` 把 `[test:...]` 解析為 `[(platform, name)]`；`platforms` 為空（legacy）不切分整串；非空時冒號前綴須為已定義平台，否則 raise；無冒號段落歸 `default_platform` | 預期驗證點: scripts/lumos 的 `resolve_test_refs` 函式；測試 t_resolve_test_refs

C3. `_platform_test_index(repo_root)` 惰性建立「平台 → (method set, code haystack)」索引，供 Check T、`classify_invariants`、`cmd_archive` 共用，且 haystack 跨 repo | 預期驗證點: scripts/lumos 的 `_platform_test_index` 函式

C4. 內建 test profile 共 6 個：`csharp-xunit`、`kotlin-junit`、`maestro`、`playwright`、`dart`、`python` | 預期驗證點: scripts/lumos 的 `TEST_PROFILES` dict 鍵集合

C5. 平台前綴（`android`/`backend`/`maestro`/`playwright`）不等於 profile 名；只有 `maestro`/`playwright` 平台前綴與 profile 名同名，`android` 對應 profile `kotlin-junit`、`backend` 對應 profile `csharp-xunit` | 預期驗證點: `.lumos/config.json` 的 `platforms` map 內各平台的 `profile` 欄位設定

C6. `discover_test_methods` 新增選填 knob `file_must_match`，讀檔後、去註解前過濾（例如 maestro profile 用 `^appId:` 濾非 flow yaml）；用 `.get()` 相容無此鍵的舊 profile | 預期驗證點: scripts/lumos 的 `discover_test_methods` 函式與 `file_must_match` 欄位處理

C7. `maestro` profile 綁定 `name:` 欄位識別字，含空白的多字 `name` 視為 NO MATCH | 預期驗證點: scripts/lumos 的 `TEST_PROFILES["maestro"]` 定義；測試 t_maestro_profile_discover

C8. `playwright` profile 綁定 `test('id')`，多字 `title` 視為 NO MATCH | 預期驗證點: scripts/lumos 的 `TEST_PROFILES["playwright"]` 定義；測試 t_playwright_profile_discover

C9. `guard bind` / `guard scaffold` 新增 `--platform` 旗標；`bind` 寫入格式為 `[test:plat:method]` 並依完整 ref 去重/verify；`scaffold` 的範本/`scaffold_ext`/測試目錄偵測隨平台 root 走 | 預期驗證點: scripts/lumos 的 `guard bind`、`guard scaffold` CLI 子命令實作；測試 t_guard_bind_scaffold_platform

C10. `dart` profile：`DART_TEST_RE` 只認 `test('id')` / `testWidgets('id')`（識別字名才可綁，含空白視為 NO MATCH，同 playwright 設計）；檔名錨定 `*_test.dart`；`comment_strip="c-style"`；`scaffold_name={m}_test`；純測試目錄為 `test/`，behavioral 目錄含 `integration_test/` | 預期驗證點: scripts/lumos 的 `TEST_PROFILES["dart"]` 定義、`DART_TEST_RE`；測試 t_dart_profile_discovery

C11. `python` profile：`PYTHON_TEST_RE` 行首錨定；新增欄位 `file_name_match`（對 basename 做 fnmatch，與 maestro 的 `file_must_match` 是內容錨的不同機制）；`comment_strip="none"`；含 `scaffold_name` 模板 | 預期驗證點: scripts/lumos 的 `TEST_PROFILES["python"]` 定義、`PYTHON_TEST_RE`、`file_name_match` 欄位

C12. `discover_test_methods` 的註解剝離改為語言感知（`c-style` 為預設以維持向後相容），修正原本對所有語言一律剝 `/*..*/` 導致 Python 檔案中文註解/字串巧合配對吃掉大段內容的問題（本 repo 實測方法數從 260 降到誤剝後的 94，修正後應恢復） | 預期驗證點: scripts/lumos 的 `discover_test_methods` 語言感知註解剝離邏輯（comment_strip 欄位分派）

C13. `csharp-xunit` 為預設 profile：辨識 `.cs` 檔、`[Fact]` 標記、頂層 `*Tests` 命名 suffix；`kotlin-junit` 為 Android 單元測試 profile：辨識 `.kt` 檔、`@Test` 標記，於 `src/` 下 rglob 搜尋 | 預期驗證點: scripts/lumos 的 `TEST_PROFILES["csharp-xunit"]`、`TEST_PROFILES["kotlin-junit"]` 定義

C14. 相關測試套件列舉且全數通過（333 passed）：t_maestro_profile_discover、t_playwright_profile_discover、t_load_platforms、t_resolve_test_refs、t_multiplatform_guard_list、t_multiplatform_doctor_check_t、t_archive_live_guard_multiplatform、t_guard_trace_multiplatform、t_guard_bind_scaffold_platform | 預期驗證點: 對應測試函式存在且執行通過（pytest 或專案測試 runner，333 passed 的總數）

C15. 多平台缺省 `default_platform` 時（多平台情境下未指定）視為報錯而非猜測；未定義平台前綴（如 `[test:foo:X]`）Check T 明確報錯而非 fallback | 預期驗證點: scripts/lumos 的 `resolve_test_refs` 或 Check T 相關錯誤處理路徑
