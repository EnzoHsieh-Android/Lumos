severity: minor

**1. 分層與依賴方向:對齊。**
- `cmd_arch_template` 現在改用 `_lens_repo_root(None)` 找根,跟同類子命令一樣(`scripts/lumos:63646`、`63717`、`63771`、`63794`)。擋下訊息仍走區域函式 `fail`、rc 2、印到 stderr。
- `_arch_tpl_konsist_test` 是自帶的小判斷函式,供 `_arch_tpl_legacy_file` 呼叫,依賴方向是產生器內部往下,沒有跨層直呼。
- 它和 `_rg_is_test_path`(`scripts/lumos:46996`)、`_PITFALL_DIFF_TEST_PAT` 判的是不同的事。前者照 Konsist 0.17.3 的原始碼集算法,後者是 lumos 自己的測試路徑判斷。`_arch_tpl_legacy_file` 仍先呼叫 `_arch_code_file`(`scripts/lumos:57489`),所以不算重複實作。
- 補丁只把原本的正規式換成函式,沒有新增第二條路徑。
- 產出的 Kotlin 領域層測試仍是 `scope.files … assertFalse` 的結構,和參考檔一致(`ArchitectureRulesTest.kt:37-38`)。差別只在前綴改成 `frameworkPrefixes` 清單、lambda 參數取名 `imp`。
- 資料檔的讀法沒有動:`readLegacyFiles` 仍是兩條正規式。

**2. 命名與錯誤處理:大致對齊,有一處小不一致。**
- 新函式 `_arch_tpl_konsist_test`、`_arch_tpl_java_legacy_read`、`_arch_tpl_kotlin_legacy_patterns` 都沿用 `_arch_tpl_*` 前綴。
- 測試檔的臨時目錄用 `tempfile.mkdtemp(prefix="gctl-java-")`,並在 `finally` 用 `shutil.rmtree(d, ignore_errors=True)` 清掉,和既有寫法一致(`scripts/test_lumos.py:183`、`10402`)。
- 判斷外部工具在不在,用 `shutil.which("java")`,在不在就跳過,和既有測試一致。
- 不一致處是「沒有 java」時的跳過提示,見 A41。

**3. 第二種做法:沒有。**
- 找根、判測試原始碼集、讀清單三處,都沒有繞開鄰居已有的函式。
- `_arch_tpl_java_legacy_read` 是新增的實跑輔助,專案裡沒有同功能的函式。
- `_arch_tpl_kotlin_legacy_patterns` 是從原本的 `_arch_tpl_kotlin_legacy_reader` 裡抽出來的,讓兩邊共用,沒有重複實作。
- 測試檔 `konsist_scans` 的另一種寫法(`re.match(r"(?:(?:[^/]*/)*?src/)?([^/]*)/", f)`)是有意跟產品碼分開寫,好讓測試能獨立驗證,不算第二種做法。

## A41 缺 java 時的跳過提示格式跟既有測試不同
severity: minor
blocking: 否
引句:「print("  · S8:這台機器沒有 java,跳過」
file: `scripts/test_lumos.py:24930`

既有的「工具不在就跳過」寫法有兩種。一種是 `print("  ⚠ 這台沒有 dart,…沒驗到")` 後 return(`scripts/test_lumos.py:24930-24932`)。另一種是 `check("★skip★ 本機無 pwsh——★這是環境限制,不是「驗過了」★…", True, …)`(`scripts/test_lumos.py:41549-41552`)。新的跳過提示用了 `"  · "` 前綴,也沒有標明「沒驗到」或「不是驗過了」。這只是提示格式不同,結構是對的。

總結:不對齊共 1 條。
