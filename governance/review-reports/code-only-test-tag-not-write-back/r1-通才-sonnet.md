severity: major

# code-r1 通才席報告(只換測試綁定不算寫說明)

LUMOS-IMPACT / 固定席筆記:這次沒附固定席節點,無可逐條判,略。

## F1 英文散文可整句塞進單行 [test:...] 而被整行拿掉,放寬被利用來繞過寫回落點守衛
severity: major
blocking: 是(守衛被繞過:程式改動的說明寫進非家筆記而不被擋,正是本案要防的洞)
file: `scripts/lumos:26856`(_NODEHOME_TEST_TAG_VALUE_RE 與 _nodehome_test_tag_value_ok,diff 新增段)
引句:「_NODEHOME_TEST_TAG_VALUE_RE = re.compile(r"[A-Za-z0-9_.:/#@,()\[\]'> -]+")」

失敗場景:判「像測試名」只看字元集,字元集含空白、逗號、句點、括號、單引號、>、#,所以任何英文句子(至多 200 字、單行)都過。測試 ④ 還把 `a long english test name` 明寫成要放行,等於承認英文句子可當綁定值,設計審 r1 只防了中文與跨行,沒防單行英文。結果:A 改了程式,把行為說明寫進不是家的 B,只要包成 `- [test:<英文句>]`,整行被當綁定拿掉,sig 不變,不被擋。

最小重現(臨時 repo,用 test_lumos.py 的 _nh_repo/_nh_node 夾具;實驗腳本 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/e3f520f1-d42a-46c6-9fbc-9facf25c84a0/scratchpad/exp.py)。B 的正文由 `實作在 `src/b.py`。` 新增一行,同一個提交改 src/a.py(A 是 a 的家、B 是 b 的家),跑 `home check --staged`:
- 新增 `- [test:Now a returns two and callers must handle none because of the new cache]` → rc=0(只剩「A 沒動」提醒)
- 在既有行尾加 `[test:From now on b writes into the registry and never into the log file]` → rc=0
- 新增 `[test:Do not call foo(x) before bar(y), see issue #12, it deadlocks]` → rc=0
- 對照 `- [test:中文說明]` → rc=1(被擋)
推送前 --diff 路徑共用同一個 sig,同樣放行。

修法方向:值要更像識別字,例如不含空白(或只允許 pytest 參數化/Kotlin 反引號名的窄形),或值內空白數、單詞數設上限;反引號 Kotlin 名稱若要允許空格,另設更窄上限。⚠ 取捨需人裁:Kotlin/JUnit5 反引號名稱本來就含空格。

## 其他逐 hunk 檢查(無額外 finding)
- _slot_scan 抽出:對照 _slot_parse_reference 的全 repo 逐字比對測試,未見分岔;未收尾欄位吐到行尾後 return,與原 break 等價。
- _slot_strip_keys:未收尾欄位原樣保留(err 非 None),無法借此藏字。
- 圍欄內行不拿(vis 過濾)、行內程式碼不拿(_slot_scan 跳過反引號段),測試 ②③ 覆蓋。
- 標記前空白被一併拿掉造成「foo [test:x]bar」與「foo bar」同 sig,只差空白,不構成說明。

總結:全份最高等級 major
