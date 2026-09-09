severity: blocker

### f1 主力證據被輸出截斷吃掉,健康的 jest verbose+coverage 設定會被誤判 unfilterable
severity: blocker
blocking: 是
file: `scripts/lumos:8745`(`_kill_cap`)對照 `scripts/lumos:21344`(`_RAN_EVIDENCE["node-jest"]`)
引句:「"node-jest": (r"Tests:.*?[1-9]\d*\s+passed",」
用 `_load_lumos_inproc()` 直接構造 jest --verbose(逐支印測試名)+ --coverage(摘要後接覆蓋率表)這種常見 CI 輸出組合,總長度一旦超過 `_KILL_OUT_CAP`(256KB),`_kill_cap` 保留頭尾各半,「Tests: 1 passed, 1 total」那行剛好落在被砍掉的中段。把這段構造輸出直接餵給 `_kill_cap`→`_ran_evidence_check` 驗證:回傳 False,一支真的跑過、真的通過的測試被判 unfilterable,不是假設出來的邊界情況——verbose+coverage 是很多專案 CI 的預設組合,測試套件越大越容易踩到。

### f2 低風險推送(advisory)下 unfilterable 完全不印一個字,「紅了照樣印」的承諾沒兌現
severity: blocker
blocking: 是
file: `scripts/lumos:22644`(`cmd_code_loop` 的列印分流)對照 `scripts/lumos:22291`
引句:「if bt["status"] in ("red", "unfilterable") and not bound_advisory:」
`_codeloop_guard_verdict` 已經把 unfilterable 跟 red 併進同一個 tuple 判斷擋不擋,但真正把訊息印給人看的 `cmd_code_loop`(pre-push 實際呼叫的那支)印訊息時只認 `_st in ("green", "red")`,沒有 "unfilterable"。實測 `m.cmd_code_loop("check", repo=..., bound_advisory=True)`(用一支「rc=0 但輸出全靜默」的假執行器,`last_bound` 確認 status 是 unfilterable):stdout 只印一行「✅ code-loop check: OK——可以推」,stderr 完全空白,沒有任何一行提到測試證不出跑過。低風險推送因此在假綠上完全靜默放行,直接違反同一段程式碼自己寫的「高風險擋、低風險比照紅只提醒」設計意圖。

### f3 擋下時的訊息沒有給 unfilterable 專屬的逃生指令,red 有、它沒有
severity: major
blocking: 否
file: `scripts/lumos:21733`(`cmd_bound_tests` 的逃生指令)對照 `scripts/lumos:22644`-`22652`(`cmd_code_loop` 只認 green/red/no-config 三種)
引句:「(推送關卡那條路用 lumos code-loop check --skip-bound-tests --note」
`cmd_bound_tests` 這支獨立指令有把 `--skip-bound-tests --note` 的完整語法印給人看,但真正擋下推送的 `cmd_code_loop check`,它的訊息分流只處理 `_st in ("green","red")` 與 `_st=="no-config"` 三種,不含 unfilterable。實測擋下時(非 advisory)只看得到一行「BLOCKED:……無法確認測試真的跑過:<原因>」,沒有任何一行講出 `--skip-bound-tests --note` 這個逃生指令,使用者只能靠 pre-push 腳本結尾那句通用、只點名「合約測試紅」的收尾提示自己猜。

### f4 反查表把 .vue/.sql/.ps1 的 symbol_profile 悄悄猜成 csharp,而且不會有任何警告
severity: major
blocking: 是
file: `scripts/lumos:13366`
引句:「sp = pick if pick in owners else (owners[0] if owners else "")」
直接呼叫 `_stack_guess()` 驗證:`.vue`/`.sql`/`.ps1` 三個副檔名的 symbol_profile 都被反查成 `"csharp"`(因為 `SYMBOL_PROFILES["csharp"]["code_exts"]` 本來就收了這三個副檔名),不是留空。這個值是合法的 profile 名,所以 `load_symbol_profile` 不警告、`_config_left_blank` 因欄位非空不唸、`_profile_stack_mismatch` 因 .vue/.sql/.ps1 本來就在 csharp 的 code_exts 裡也不唸——一個以 SQL/PowerShell/Vue 為主的專案會拿到完全錯誤但暢行無阻的符號設定。這正是這批診斷要根治的「猜錯沒人知道」,只是從舊版「猜出一個不存在的值、大聲警告」換成「猜出一個存在的錯值、完全靜默」,復發成更隱蔽的版本。

### f5 整套跑(whole=True)完全不驗跑過證據,合約測試可以被跳過還報綠
severity: major
blocking: 否
file: `scripts/lumos:21458`
引句:「ran, fix = (None, "") if whole else _ran_evidence_check(pentry.get("profile_name"), tail)」
run_cmd 沒有 `{method}` 佔位符(whole=True)時,不管平台的 profile 是不是 `_RAN_EVIDENCE` 有收錄,一律不驗,rc==0 就直接判 green。實測:構造一支「整套跑」腳本,先印「t_pay_ok: SKIPPED(flaky, disabled by team)」再 exit 0,`_bound_tests_check` 照樣回 `status=green`、reason 寫「1 支全綠」。這是這批診斷自己在文件裡承認的既有天花板、不是這次新引入的退步,但它跟這批要解決的「合約測試被靜默跳過還報綠」是同一個症狀,沒被這次修正碰到。

### f6 快取讀取端沒有走 _trusted_private_dir,跟寫入端判準不一樣
severity: major
blocking: 是
file: `scripts/lumos:21393`(讀取端裸查)對照 `scripts/lumos:21411`(寫入端呼叫共用檢查)
引句:「st.st_uid == _os.getuid() and not (st.st_mode & (_stat.S_IWGRP | _stat.S_IWOTH))」
寫入端已經改走共用的 `_trusted_private_dir(cache.parent, ...)`(逐段拒 symlink、比對解析後路徑),但讀取端只裸查快取「檔案本身」的 uid/mode/mtime,沒有檢查父目錄有沒有被換成 symlink、也沒檢查路徑每一段是不是字面目錄。這正是 r1 兩席都點名要修的「同一支共用檢查,別再各自漂」,現在讀寫兩端在同一支函式裡又各自維護一套不同判準,是同一種漂移的新變體。

### f7 TTL 保鮮期沒有任何測試驗證它真的會過期
severity: minor
blocking: 否
file: `scripts/test_lumos.py:34075`
引句:「isinstance(m._FILTER_PROBE_TTL, int) and m._FILTER_PROBE_TTL > 0」
全測試檔搜尋 `_FILTER_PROBE_TTL` 只有這一處引用,只驗證常數是正整數,沒有任何測試把快取檔的 mtime 往回撥超過 TTL 再驗真的被當成過期重探。實測手動把 mtime 撥到超過 14 天,現在的實作確實會正確重探(功能沒問題),但如果日後有人不小心把 TTL 判斷條件拿掉或改壞,五支新測試裡沒有一支會翻紅。

### f8 「逐支精準度靠 _RAN_EVIDENCE」這句話言過其實,真正擋住 r1 f7 案例的是既有的 real/fake 靜態檢查
severity: minor
blocking: 否
file: `scripts/lumos:21379`-`21380`
引句:「逐支精準度靠 _RAN_EVIDENCE 那條路,」(緊接下一行「這條備援路上沒有解。」)
`_ran_evidence_check` 只數輸出裡有沒有出現「N passed」,不比對是哪一支測試的名字,本身不具備分辨「選中的是不是正確那支」的能力。實測構造 r1 原本的 pytest -k 子字串誤中情境(合約寫 `t_pay`,repo 裡只存在 `t_pay_extra_ok`):真正擋下這個案例、回 red 的是更早、這次沒改的靜態存在性檢查(`methods_for`/`"fake"` 判定),不是新加的 `_RAN_EVIDENCE`。對 kotlin-junit/dart/playwright 這三個沒有 `_RAN_EVIDENCE` 樣式的 profile,精準度問題確實還是懸而未解、程式碼自己也承認,但「逐支精準度靠 _RAN_EVIDENCE 那條路」這句話把既有防線的功勞算給了新機制,容易誤導以後的維護者以為單靠 `_RAN_EVIDENCE` 就夠。

---

**上一輪 14 條逐條核對(r1-單reviewer f1-f9 + r1-架構對齊 f1-f5):**

| 來源 | 判定 | 依據 |
|---|---|---|
| 單f1(dotnet/jest 骨架必被判不可信) | 真的解掉 | 主力機制換成 `_RAN_EVIDENCE`(不靠退出碼);C# 骨架另外加 `-- RunConfiguration.TreatNoTestsAsError=true` 修 rc |
| 單f2(unfilterable 從沒真的擋) | 真的解掉,但有新缺口 | `_codeloop_guard_verdict` 已把 unfilterable 併入擋的判準(f2 quote 驗證),但下游列印分流沒跟上,advisory 路徑完全靜默——見 f2/f3 |
| 單f3(symbol_profile 警告被 out[:8] 吃掉) | 真的解掉 | 兩組各自 cap=4、截斷會印「還有 N 條沒列出來」,已用真實 doctor 輸出核對 |
| 單f4(兩支掃描 skip 名單不同步) | 真的解掉 | 兩處都改走共用的 `_stack_ext_counts`/`_stack_scan_skip` |
| 單f5(rglob 沒真的剪枝) | 真的解掉 | 改用 `os.walk` 搭配 `dirnames[:] = [...]` 就地剪枝 |
| 單f6(bound-filter 快取沒走 `_trusted_private_dir`) | 只解一半 | 寫入端補上了,讀取端仍是裸檢查——見 f6 |
| 單f7(冒煙測試證不了精準度) | 解錯方向的宣稱,實際靠別的機制擋住 | 見 f8:新機制本身不驗精準度,擋住 r1 案例的是既有靜態存在性檢查 |
| 單f8(快取沒有 TTL/版本) | 真的解掉,但沒測試釘住 | schema/TTL 都加了且實測有效,惟 TTL 過期路徑零測試覆蓋——見 f7 |
| 單f9(猜不到的語言骨架留空、S3 抓不到) | 真的解掉 | `_config_left_blank` 已接進 S3 的 `_mismatch`,本 repo 實跑 doctor 驗證有效;但同一份反查表在「猜得到但猜錯」這一側開了新洞——見 f4 |
| 架構f1(冒煙測試自動嵌進推送擋關) | 未處理(該報告自己也判 minor/不擋) | 這次沒有把它拆回顯式 `--smoke` 兩階段;非本輪要求範圍 |
| 架構f2(`_init_config_skeleton`/`.gitignore` 被兩層早退連坐) | 真的解掉 | `_init_additive_setup` 抽出來,`cmd_init` 在早退前呼叫;新測試 `t_init_additive_setup_reaches_existing_projects` 驗證既有 vault 也拿得到 |
| 架構f3(docstring 的 status 列舉沒更新) | 真的解掉 | `_bound_tests_check` docstring 已補 unfilterable/no-vault 等新狀態 |
| 架構f4(`_STACK_GUESS` 第三份表、`.vue`/`.dart` 寫壞值) | 真的解掉,但衍生新問題 | 改成反查兩張正典表,不再手打;但反查出來的答案本身在 `.vue`/`.sql`/`.ps1` 上是錯的、只是不再觸發警告——見 f4 |
| 架構f5(快取繞過 `_trusted_private_dir`) | 只解一半 | 同單f6——見 f6 |

**圖譜鏡頭(LUMOS-IMPACT: HEAD~1..HEAD):**
`Systems/bound-tests-gate.md`(hop1,固定席分數 0.70)的 ★INVARIANT★ 已經改寫成「……任一紅/懸空(dangling/fake)/方法名不合法/★證不出跑過(unfilterable)★ → blocked=True」。對 tier=high(非 advisory)那條路徑,這句話字面成立(f2 的引句 `bt["status"] in ("red", "unfilterable")` 就是實作);f2/f3 講的是低風險(advisory)那半沒兌現「比照紅只提醒」的程式碼自己的設計承諾,不是這條 INVARIANT 字面斷言被破——INVARIANT 本身判「不影響」。其餘 hop1/hop2 命中(canary-audit、guard-kill、slim-install/uninstall/一行安裝、授權與歸屬、測試假綠形態、lumos-cli-read/lifecycle、reversibility-governance-ledger、design-loop、pitfalls-code-loop、loop-convergence-recording、check-t-sentinel、core-invariant-baseline、doctor-irreversible-hint、lumos-deinit、check-r-guard、cochange-guard、lumos-refcheck、judge-severity-gate 等)都只是同檔 `scripts/lumos` 的 hop1 關聯,讀過各自摘要行沒有一條提到 unfilterable/`_RAN_EVIDENCE`/`_stack_guess`/`_init_additive_setup`,判「不影響」。本輪唯一以「直接」命中、分數 1.00 排最前的 `Issues/vendored測試套件在消費端假紅.md`,查證是因為它的正文提到 `governance/review-reports/code-接入靜默/r2-snapshot.patch` 這個路徑字串(這份審查素材本身),不是這次 diff 改動的程式碼邏輯跟它有函式層面的關聯,判「不影響」。

最嚴重 severity: blocker,blocking 條數 4
