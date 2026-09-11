severity: major

### F1 Gradle/src 錨定沒有比照 suffix 分支限定副檔名,任意副檔名可透過同模組 src/main 的無關檔案偷渡免家
severity: major
blocking: 是 — 「每支檔有家」的核心承諾是新程式檔一定要有家,這條分支能讓完全無關的程式檔靜默免家、不留任何提醒,已用完整判定管線重現。
引句:「if parts[i] in under_src and parts[i - 1] == "src" and ext in main_exts.get("/".join(parts[:i]), ()):」
1. suffix 分支(頂層 `<X>Tests`)先過濾「副檔名要屬於貢獻那個結尾樣式的棧」才繼續判(`if ext not in exts or not top.endswith(suf): continue`,scripts/lumos:17845),但 Gradle/`src` 分支完全沒有對等限定——只要同一個模組 `src/main/` 底下**任何深度、任何棧**出現過同副檔名的檔,`ext in main_exts.get(...)` 就會為真,不管那個副檔名跟 Kotlin/Gradle 有沒有關係。
2. `_nodehome_layout` 把 `main_exts` 累加成「該模組 src/main 底下出現過的所有副檔名」,沒有分棧(scripts/lumos:17808-17823),所以一支放在 `src/main/` 裡跟 Kotlin 無關的 `.py`/`.sh`/`.go` 檔,就能讓 `src/androidTest/`、`src/test/` 底下**同副檔名的任何程式檔**被誤判成測試資料夾成員、整支免家。
3. 已在 /tmp 暫存複本(未動 repo)用完整 `_nodehome_required` 管線重現:建 `svc/src/main/Cart.kt`、`svc/src/main/gen_proto.py`、`svc/src/androidTest/exploit_business_logic.py` 三支檔,後者(明顯是業務碼、放錯位置)被排除在 `req` 之外,输出 `required set contains target: False`,`req` 只剩前兩支。
file: `scripts/lumos:17850-17851` `_nodehome_in_stack_test_dir` Gradle 分支缺副檔名家族限定
file: `scripts/lumos:17808-17823` `_nodehome_layout` 的 `main_exts` 不分棧累加副檔名
重現指令與輸出(在 `/tmp/nodehome_review.OpC7dY`,複製 scripts/ 後跑,未寫回 repo):
```
python3 repro2.py
required set contains target: False
['svc/src/main/Cart.kt', 'svc/src/main/gen_proto.py']
```

### F2 漂移守衛重算 names 沒有比照 production 的 if d 過濾,TEST_PROFILES 混進空字串資料夾名時會假紅
severity: minor
blocking: 否 — 只在 TEST_PROFILES 未來新增空字串資料夾名時觸發,現狀(檢查過現有全部棧的 dirs)不含任何空字串,不影響現在的判定結果,只是守衛本身跟 production 認知不一致。
引句:「names = {d for inc, _exc in prof["dirs"].values() for d in inc}」
1. production 建 `sufs`/`under_src` 時用 `if d` 濾掉假值資料夾名(scripts/lumos:17792),漂移守衛(scripts/test_lumos.py:36776)重算同樣的 `names` 卻沒有這個過濾——這行從第一輪就在、兩輪修正都沒碰到它。
2. 若未來某個 suffix 或 `rglob_under=="src"` 的棧在 `dirs` inc 清單裡混進空字串,production 會正確濾掉(等於沒發生這個「資料夾」),守衛卻會把它當真實樣式去造 `Demo/x{ext}` 這種路徑丟給 `_nodehome_is_test` 判——production 判不是測試,守衛就記成 miss,check ⑤ 假紅擋下一個其實沒改變任何行為的 TEST_PROFILES 修訂。
file: `scripts/lumos:17792` production 的 `if d` 過濾
file: `scripts/test_lumos.py:36776` 漂移守衛重算 `names` 沒有 `if d`
重現(monkeypatch `TEST_PROFILES` 加一個帶空字串資料夾名的假棧,同一份 production 程式碼跑兩種算法):
```
production sufs keys: ['FakeTests', 'IntegrationTests', 'Tests', 'UITests']
drift-guard's local names (no `if d` filter): ['', 'FakeTests']
guard would record as miss (=> check ⑤ 假紅): ['Demo/x.fk']
```

## 逐項判定

- **風險掃描(`_NODEHOME_STACK_TEST_DIRS` 鎖保護)**:誤報。整支 `scripts/lumos` 沒有 `threading`/`multiprocessing`/`asyncio`(grep 零命中),lumos 是單執行緒 CLI;即使被重入呼叫,module-level 變數賦值在 CPython 是單一參照替換,最壞只是重算一次同樣的靜態值(輸入只來自常數 `TEST_PROFILES`),不會半寫壞值。寫法跟既有 `_TESTMAP_DIR_RE = None` 這種 lazy cache 是同一種既有模式,不是這次新增的風險面。

- **bound-tests-gate.md / canary-audit.md / guard-kill.md / slim-get-一行安裝.md / slim-install-安裝器.md / slim-uninstall-一行卸載.md / 授權與歸屬.md**:不影響。這幾篇的 ★INVARIANT★ 全綁在跟本次改動不相干的子系統(code-loop bound tests、canary 落盤驗證、guard kill 的 rc 優先序與 JSON 純度、Windows 安裝器/CLAUDE.md 注入冪等、卸載四步驟獨立性、`_VENDORED_TOOLKIT` 白名單與 SPDX);列進固定席只是因為共用 `scripts/lumos`、`scripts/test_lumos.py` 這兩支大檔,diff 本身只新增/改了 `_nodehome_*` 系列函式與一支新測試,沒有碰到這些子系統的任何函式、資料結構或掛鉤流程。

- **測試假綠形態.md**:不影響。它的 ★INVARIANT★ 要求「還原翻紅釘」要配前置斷言證明現場成立,防的是第④型「現場走不到被測分支」。新增的 `t_nodehome_stack_test_dirs_not_required` 直接呼叫 `_nodehome_required` 真跑判定、斷言回傳集合的成員關係,不是 mock 或猜現場,不落入這個假綠形態。

- **超出上限只列名的 15 篇(lumos-cli-read/lifecycle、design-loop、pitfalls-code-loop、loop-convergence-recording、節點範圍與索引守衛、lumos-deinit、reversibility-governance-ledger、lumos-refcheck、doctor-irreversible-hint、core-invariant-baseline、check-r-guard、check-t-sentinel、cochange-guard、judge-severity-gate)**:不影響。同樣只是「間接相依」(共用兩支大檔),diff 改動範圍侷限在測試資料夾判定這一段。特別查了「節點範圍與索引守衛」的合約門檻(一篇最多 10 條 ★INVARIANT★ 才不算超載)——用 `lumos contracts "Systems/每支檔有家"` 查證,回「這篇沒有登記任何動了會壞的合約」,這次新增的兩行 KEY 也還是候選、沒標 ★INVARIANT★,不會踩到那個門檻。

總結:最高 severity major,blocking 共 1 條
