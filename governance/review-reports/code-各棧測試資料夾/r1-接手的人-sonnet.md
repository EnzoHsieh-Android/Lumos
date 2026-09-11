severity: major

### F1 頂層「Tests」資料夾判定沒按副檔名/技術棧限定,任何棧的程式檔掉進同名資料夾就被判成不用家
severity: major
blocking: 是 — 這是新引入的判定漏洞,會讓程式檔悄悄逃過「每支檔有家」的機械擋,不是措辭問題。
引句:「if sufs and parts[0].endswith(sufs):」
1. `_nodehome_stack_test_dirs()` 從全域 `TEST_PROFILES` 收集 suffix 樣式(來源只該是 Swift `.swift`/C# `.cs` 兩棧),但 `_nodehome_in_stack_test_dir()` 比對時只看頂層資料夾名稱字串,完全沒檢查該檔案的副檔名是不是屬於貢獻該樣式的棧——名詞段寫的「頂層比對模式的棧(Swift、C#)取…」在實作裡並沒有真的把比對限定在那兩棧。
2. 實測:對 base commit(631d7e3b,diff 前)跑 `_nodehome_is_test("LoadTests/db_schema.py")` 與 `_nodehome_is_test("AcceptanceTests/pricing_engine.go")` 都回 `False`(正確,要家);對 diff 後的 `scripts/lumos` 跑同兩個路徑都回 `True`(被判成測試資料夾、不用家)——`.py`、`.go` 跟 Swift/C# 毫無關係,`LoadTests`/`AcceptanceTests` 正是這篇事故筆記自己在講 Java 駝峰字尾風險時點名的那種「業務名詞」(`測試檔:清單外副檔名也認 _test 等結尾`一段旁的既有取捨),只是這次沒把同樣的顧慮套用到資料夾層。
3. 測試 `t_nodehome_stack_test_dirs_not_required` 的 `not_req`/`req_ok` 兩組全部只用 `.kt`/`.java`/`.swift`/`.cs` 副檔名,沒有任何一筆是「非 Swift/C# 副檔名 + Tests 結尾頂層資料夾」的組合,所以綠燈證不出這裡沒有洞。
佐證:file: `scripts/lumos:17787` `_nodehome_stack_test_dirs()` 對 `TEST_PROFILES.values()` 全表掃描、不分棧地把 `dir_mode=="suffix"` 的資料夾名收進 `sufs`。
佐證:file: `scripts/lumos:17801` `_nodehome_in_stack_test_dir(path)` 只用 `parts[0].endswith(sufs)` 比對頂層資料夾名,函式簽名裡沒有 `ext`/棧別參數。
未能重現部分:無——上面兩個路徑在 diff 前後行為差異已用實際 python 呼叫重現(base 版讀自 `git show 631d7e3b:scripts/lumos`,diff 後版讀自本檔)。

### F2 模組層延遲快取 `_NODEHOME_STACK_TEST_DIRS` 沒鎖保護——判為誤報
severity: minor
blocking: 否 — 沒有並發寫入路徑,不會產生實際競態。
引句:「_NODEHOME_STACK_TEST_DIRS = None   # lazy:(頂層資料夾結尾樣式, src/ 底下的測試資料夾名)」
1. `scripts/lumos` 整支主程式沒有 `threading`/`multiprocessing`/`concurrent.futures` 的使用(grep 全檔查無),是單行程 CLI,`lumos home check` 一次呼叫裡不會有兩條執行緒同時把這個 lazy cache 從 `None` 寫成 tuple。
2. 這個寫法是既有慣例的延伸,不是新模式:同一支檔案裡 `_STACK_GUESS_CACHE`(scripts/lumos:14015)註解明寫「模組級單例,同 _TESTMAP_DIR_RE 的既有寫法」,而 `_TESTMAP_DIR_RE`(scripts/lumos:19848 附近)本來就用一模一樣的 `is None` 判斷延遲初始化,審查範圍內這支新加的沒有比既有的更危險。
佐證:file: `scripts/lumos:14015` `_STACK_GUESS_CACHE = None` 註解自陳跟 `_TESTMAP_DIR_RE` 同款寫法。
佐證:file: `scripts/test_lumos.py` 全檔搜尋 `threading`/`ThreadPoolExecutor`/`multiprocessing` 無命中,測試跑法也是單行程。

### F3 圖譜鏡頭列出的固定席 invariant,這次 diff 都不影響——逐組列理由
severity: minor
blocking: 否 — 純屬「不影響」判定,沒有翻紅路徑。
引句:「def t_nodehome_stack_test_dirs_not_required():」
1. bound-tests-gate.md(code-loop 綁測逐支真跑/rc 判定):diff 只新增一支測試函式並被引用進 `[test:t_nodehome_stack_test_dirs_not_required]`,沒有動 bound-tests 本身「怎麼找/怎麼跑/怎麼判紅」的邏輯——不影響。
2. canary-audit.md(record/second 落盤與唯讀 telemetry)、guard-kill.md(kill rc 優先序與 `--json` 純淨輸出):diff 完全沒有碰 canary/guard kill 相關程式碼路徑——不影響。
3. slim-get-一行安裝.md / slim-install-安裝器.md / slim-uninstall-一行卸載.md(BOM、CLAUDE.md 注入冪等、manifest、Windows shim):diff 沒有觸碰安裝/卸載任何函式——不影響。
4. 授權與歸屬.md(LICENSE 不得進 vendored 白名單、SPDX):diff 沒有動 `_vendor_toolchain` 或白名單清單——不影響。
5. 測試假綠形態.md(「還原修法就要翻紅」的前置斷言紀律):新測試本身有漂移守衛(check⑤,對照表每個樣式都真的造路徑驗證)算是遵守了這條紀律的字面要求;但 F1 顯示測試組合從沒覆蓋「非 Swift/C# 副檔名」這個現場,是同一份紀律精神在這次診斷裡的實際落空,關聯 F1、不算獨立違反本節點的合約字面。
6. 其餘只列名的(lumos-cli-lifecycle/lumos-cli-read/design-loop/pitfalls-code-loop/lumos-deinit/loop-convergence-recording/節點範圍與索引守衛/lumos-refcheck/cochange-guard/check-r-guard/doctor-irreversible-hint/reversibility-governance-ledger/check-t-sentinel/core-invariant-baseline/judge-severity-gate):列名成因是 `scripts/lumos`、`scripts/test_lumos.py` 是巨型共用檔、被很多節點的 about_code 列為家,不代表這次改動的邏輯範圍碰到它們——改動範圍就是 `_nodehome_stack_test_dirs`/`_nodehome_in_stack_test_dir`/`_nodehome_is_test` 三個函式加一支測試,經讀碼確認跟上述節點各自的合約敘述(裝解安裝、CI 觀測、refcheck 等)無交集,不影響。
佐證:file: `scripts/lumos:17780-17825` 這次唯一改動範圍(新增兩函式、改 `_nodehome_is_test` 插入一個 `if` 分支),行數之外沒有其它變更。

### F4 事故筆記/節點/計劃文字與 diff 行為一致;逃逸帳格式合規;查無圖譜殘留舊說法
severity: minor
blocking: 否 — 三項查證都對得上,沒有找到落差。
引句:「不動測試地圖的判定規格(那份是設計審定過、有導入專案實測的)」
1. 「測試地圖判定不動」屬實:diff 沒有修改 `_testmap_is_test`/`_testmap_camel_suffixes` 等測試地圖函式,實跑 `python3 scripts/test_lumos.py -k testmap` 73 個案例全過、`-k nodehome` 174 個案例全過(於本機 `/tmp` 隔離複本跑,repo 本身未寫入)。
2. 「對照表多一個就自動跟著認」對 `dir_mode=="suffix"` 與 `rglob_under=="src"` 這兩類棧成立(有測試 check⑤ 漂移守衛佐證且實跑綠);但如 F1 所述,這句話沒說清楚的副作用是它不分副檔名——這點文件沒揭露,屬 F1 的文件面延伸,不重複計分。
3. 逃逸帳新增那筆(`ESC-18f03ede`)格式合規:`severity: major` 在 `minor|major|blocker` 值域內、`stage: 使用者回報` 正是 CLI 提示裡給的例字、`loop: code-每支檔有家` 在 `.canary-log.jsonl` 裡有 12 筆既有紀錄可歸因,不是掛空的迴圈編號;跑 `lumos search` 全庫沒查到 `androidTest`/測試資料夾判定的舊說法殘留在其它節點或 skill 文件裡。
佐證:file: `docs/lumos-toolchain-knowledge/Issues/各棧測試資料夾被當成要家.md` 與 `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md` 兩篇皆 `lumos lint` 0 問題(於隔離複本跑)。
佐證:file: `docs/.canary-log.jsonl` grep `"loop": "code-每支檔有家"` 命中 12 筆,逃逸帳新條目的 loop 編號有據可查。

總結:最高 severity major,blocking 共 1 條
