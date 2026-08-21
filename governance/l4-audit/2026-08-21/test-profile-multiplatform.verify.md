C1 [✅] load_platforms 讀 .lumos/config.json 的 platforms 鍵，回傳 {multiplatform, default_platform, platforms:{plat:{profile,root}}}；無 platforms 鍵時視為 legacy 單一條目 | 證據: scripts/lumos:2084-2134（legacy 分支 2102-2111；多平台分支 2112-2134）；test_lumos.py:2418-2475 t_load_platforms 案例 1/2 覆蓋 legacy 行為

C2 [✅] resolve_test_refs 把 [test:...] 解析為 [(platform, name)]；platforms 空（legacy）不切分整串；非空時冒號前綴須為已定義平台否則 raise；無冒號段落歸 default_platform | 證據: scripts/lumos:2164-2182；test_lumos.py:2478-2511 t_resolve_test_refs 六案例逐條對應（多平台雙前綴/fallback/裸 ref/未定義前綴報錯/legacy 不切分/legacy 含冒號整串當方法名）

C3 [✅] _platform_test_index 惰性建立「平台 → (method set, code haystack)」索引，供 Check T、classify_invariants、cmd_archive 共用，且 haystack 跨 repo | 證據: scripts/lumos:4998-5023 定義；呼叫點 scripts/lumos:732（Check T）、5050（classify_invariants）、8048（cmd_archive）；hay_for() 用 p["root"] 依平台各自 build_code_haystack，跨 repo（scripts/lumos:5017-5021）

C4 [✅] 內建 test profile 共 6 個：csharp-xunit、kotlin-junit、maestro、playwright、dart、python | 證據: scripts/lumos:1972-2039 TEST_PROFILES dict 恰 6 個頂層鍵

C5 [✅] 平台前綴（android/backend/maestro/playwright）不等於 profile 名；只有 maestro/playwright 平台前綴與 profile 名同名，android 對應 profile kotlin-junit、backend 對應 profile csharp-xunit | 證據: scripts/lumos:2112-2124（platforms[plat].profile 為獨立欄位、plat 鍵名任意字串，不受限於 TEST_PROFILES 名）；具體映射見 test_lumos.py:2447-2449（"android":{"profile":"kotlin-junit"}, "backend":{"profile":"csharp-xunit"}）。註：本 repo 自身 .lumos/config.json 為單平台 python legacy 設定（無 platforms 鍵），此規則以程式碼 schema + 測試固定樣本佐證，非本 repo 實際部署多平台

C6 [✅] discover_test_methods 新增選填 knob file_must_match，讀檔後、去註解前過濾；用 .get() 相容無此鍵的舊 profile | 證據: scripts/lumos:2329（must = profile.get("file_must_match")）、2340-2347（讀檔後先套 file_must_match，2352 才進 comment_strip）

C7 [✅] maestro profile 綁定 name: 欄位識別字，含空白的多字 name 視為 NO MATCH | 證據: scripts/lumos:1880 MAESTRO_NAME_RE = r"(?m)^name:\s*[\"']?([A-Za-z_]\w*)[\"']?\s*$"（\w* 後緊接引號/行尾錨，含空白即不匹配）；test_lumos.py:2336 t_maestro_profile_discover

C8 [✅] playwright profile 綁定 test('id')，多字 title 視為 NO MATCH | 證據: scripts/lumos:1885 PLAYWRIGHT_TEST_RE = r"\btest(?:\.describe)?\(\s*[\"']([A-Za-z_]\w*)[\"']"；test_lumos.py:2374 t_playwright_profile_discover

C9 [✅] guard bind / guard scaffold 新增 --platform 旗標；bind 寫入格式為 [test:plat:method] 並依完整 ref 去重/verify；scaffold 的範本/scaffold_ext/測試目錄偵測隨平台 root 走 | 證據: CLI 旗標 scripts/lumos:14348（gs）、14354（gb）；cmd_guard_bind scripts/lumos:5231-5288（ref=f"{platform}:{method}"、5262 完整 ref 去重、5282 atomic_write_verify 完整 ref）；cmd_guard_scaffold scripts/lumos:5138-5228（5185-5188 範本走 platform_root、5204 _detect_test_dir(platform_root,...)、5213-5215 scaffold_name/scaffold_ext 取自該平台 profile）；test_lumos.py:2633 t_guard_bind_scaffold_platform

C10 [✅] dart profile：DART_TEST_RE 只認 test('id')/testWidgets('id')；檔名錨 *_test.dart；comment_strip="c-style"；scaffold_name={m}_test；純測試目錄 test/，behavioral 含 integration_test/ | 證據: scripts/lumos:1889 DART_TEST_RE；scripts/lumos:2017-2027 TEST_PROFILES["dart"]（file_name_match=["*_test.dart"]、comment_strip="c-style"、scaffold_name="{m}_test"、dirs.pure=(["test"],[])、dirs.behavioral=(["integration_test","test"],[])）；test_lumos.py:1758 t_dart_profile_discovery

C11 [✅] python profile：PYTHON_TEST_RE 行首錨定；新增 file_name_match 對 basename fnmatch；comment_strip="none"；含 scaffold_name 模板 | 證據: scripts/lumos:1893 PYTHON_TEST_RE = r"(?m)^def ((?:t|test)_[A-Za-z0-9_]+)\s*\("；scripts/lumos:2028-2038 TEST_PROFILES["python"]（file_name_match=["test_*.py","*_test.py"]、comment_strip="none"、scaffold_name="test_{m}"）；file_name_match 套用邏輯於 scripts/lumos:2330,2338（fnmatch 對 basename）

C12 [✅] discover_test_methods 註解剝離改語言感知（c-style 為預設向後相容），修正原本全語言一律剝 /*..*/ 導致 Python 中文註解/字串誤配對吃掉大段內容（本 repo 實測 260→94，修正後應恢復） | 證據: scripts/lumos:2331,2348-2354（strip 欄位分派，c-style 才剝 // 與 /*..*/，python 走 none）；修復動機與實測數字見程式內註解 scripts/lumos:2009-2012（"實測 test_lumos.py 260→94"）

C13 [✅] csharp-xunit 為預設 profile：辨識 .cs 檔、[Fact] 標記、頂層 *Tests 命名 suffix；kotlin-junit 為 Android 單元測試 profile：辨識 .kt 檔、@Test 標記，於 src/ 下 rglob 搜尋 | 證據: load_test_profile 預設 scripts/lumos:2046（prof = dict(TEST_PROFILES["csharp-xunit"])）；TEST_PROFILES["csharp-xunit"] scripts/lumos:1973-1980（exts={".cs"}、dir_mode="suffix"、dirs.pure=(["Tests"],...)）；TEST_METHOD_RE scripts/lumos:1860-1866 認 [Fact]/[Theory]/[SkippableFact]；TEST_PROFILES["kotlin-junit"] scripts/lumos:1981-1988（exts={".kt"}、dir_mode="rglob"、rglob_under="src"）；KOTLIN_TEST_RE scripts/lumos:1874-1876 認 @Test/@ParameterizedTest/@RepeatedTest

C14 [❌] 相關測試套件列舉且全數通過（333 passed）——函式全部存在且通過為真，但「333」這個總數對不上任何合理範圍 | 證據: 9 個函式皆存在（scripts/test_lumos.py:1426,1758,2336,2374,2418,2478,2514,2555,2606,2633 覆蓋全部 9 個名字，含 t_dart_profile_discovery 額外一個），逐一以 `python3 scripts/test_lumos.py -k <name>` 實跑全數 0 failed，但 check() 斷言數加總僅 25（2+2+6+6+2+2+1+1+3），非 333；放寬到 -k 涵蓋 "platform"/"profile"/"maestro"/"playwright"/"dart" 等關鍵字分別跑出 16/27/2/2/7 passed，均遠低於 333；全檔 `grep -c "^def t_"` 共 492 個測試函式（非 333）；repo 內（排除 docs/lumos-toolchain-knowledge）搜尋不到任何「333 passed」字樣。故「全數通過」屬實但「333」這個數字缺乏對應依據

C15 [✅] 多平台缺省 default_platform 時（多平台情境下未指定）視為報錯而非猜測；未定義平台前綴（如 [test:foo:X]）Check T 明確報錯而非 fallback | 證據: scripts/lumos:2125-2131（len(out)>1 且未指定 default_platform → raise ValueError）；scripts/lumos:730-736（Check T 對未定義前綴 append 到 bad_platform 明確報錯，非 fallback）；test_lumos.py:2458-2465（load_platforms 多平台缺 default_platform 且 >1 → 報錯 案例）、2499-2504（resolve_test_refs 未定義前綴 → 報錯 案例）

✅13 ❌1 ❓0 ⏭0
