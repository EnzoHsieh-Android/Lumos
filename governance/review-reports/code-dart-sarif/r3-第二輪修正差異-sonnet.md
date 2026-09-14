severity: clean

## 已確認

本輪只審 r2 兩條發現(k1 文件講清邊界、k2 ls-files 換未追蹤檔)的修正差異,逐項用實機重現查證,沒找到能翻紅的輸入。

1. **k2(ls-files 換檔)的修正是真的、新測試不是假守衛**。把 `scripts/lumos` 裡的
   引句:「r = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*." + str(stack)],」
   還原成修正前的 `git ls-files -z -- *.<stack>`,在乾淨臨時複本裡跑
   `python3 scripts/test_lumos.py -k t_lintcheck_smoke_fills_lint_files`——新增的第二個案例(還沒 `git add` 的檔)當場翻紅:
   `冒煙失敗:命令跑不出可解析 SARIF...`;改回修正版重跑轉綠。確認測試真的釘住這個行為,不是空案例。

2. **子模組/巢狀 repo 不會被冒煙誤收**。在臨時外層 repo 裡放一個有自己 `.git` 的巢狀目錄(`vendor/pkg`,內含
   `lib/inner.dart`),對外層跑 `git ls-files -z --cached --others --exclude-standard -- '*.dart'`,只列出外層自己的
   `lib/real.dart`,巢狀 repo 內的檔不會被列出來——git 對「有自己 .git 的目錄」視為邊界,`--others` 不會遞迴進去。

3. **`.gitignore` 生效時,`build/`、`.dart_tool/` 產物不會被拿去冒煙**。臨時 repo 裡放
   `build/gen.dart`、`.dart_tool/pkg_config.g.dart` 並加對應 `.gitignore` 規則,`--exclude-standard` 正確濾掉,只列出
   `lib/real.dart`。只有在專案連 `.gitignore` 都還沒建立的病態情境(比 `flutter create` 更早)才會把產物撈進來,而
   這只影響冒煙(驗證宣告的指令能不能執行),不影響新增告警閘真正跑的快照 diff 邏輯——沒有具體會被這條誤導出錯判的場景,不成立可標的發現。

4. **k1(文件講邊界)跟真實 dart 3.13.3 行為一致**。實機建三段真 bug(參數個數錯、型別不符、未定義名字)跑
   `dart analyze --format=json`,三條全部回報 `"type": "COMPILE_TIME_ERROR"`(`not_enough_positional_arguments`／
   `invalid_assignment`／`undefined_function`),跟
   引句:「參數個數錯、型別不符、用了沒定義的名字這些真 bug,dart 也歸在編譯期錯誤這一類」
   （`docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:123`）逐字對得上,沒有講輕代價。

5. **四處文件(程式註解、兩篇圖譜筆記、README.en)口徑一致,沒有殘留「會抓編譯錯誤」的暗示**。逐一核對
   `scripts/lumos` 裡 `_DART_SKIP_TYPES` 上方註解、`pitfalls-lint-adapter.md`、`linter精選目錄.md`、`README.en.md`
   四處對「這道閘對 Dart 抓不到編譯錯誤」的敘述,用詞與涵蓋範圍(參數錯/型別不符/未定義名字)相同,沒有一處只講
   舊版「只收警告、lint 規則與提示」而漏提代價的那半句。中文版 `README.md` 本來就沒有這張語言覆蓋表,不是這輪漏改。

6. **REVISIT 行格式與位置符合 CLAUDE.md 鐵則四、也符合 `lumos doctor` E5 的掃描規則**。
   引句:「REVISIT:2026-12-14 還沒有真 Flutter 專案接進來的話,重看 Dart 這道閘該不該補整份原始碼」
   （`docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:126`）獨立成行、行首無縮排無列表符號,直接
   `strip()` 後即以 `REVISIT:` 開頭,對照 `scripts/lumos` 裡 E5 檢查(約 1906 行)的判準「strip 行首空白與 - / *
   列表前綴後以 REVISIT: 開頭」會被正確收進到期掃描,不是死行;日期 2026-12-14 晚於今天(2026-09-14),尚未到期屬正常。

7. `python3 scripts/test_lumos.py -k dart` 全數 37 案例綠燈(含 `t_dart_sarif_bridge`、
   `t_dart_gate_with_fake_analyzer`、`t_lintcheck_smoke_fills_lint_files`),沒有連帶破壞既有案例。

沒有發現需要標記的 minor/major/blocker——所有查過的輸入(還原修正、巢狀 repo、gitignore 產物、真 dart 三種編譯錯誤)都沒能讓這次修正翻紅或跟文件對不上。
