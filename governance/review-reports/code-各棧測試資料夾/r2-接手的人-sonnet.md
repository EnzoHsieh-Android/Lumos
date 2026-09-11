severity: minor

### F1 頂層 Tests 結尾資料夾新加的「同名資料夾」錨,對沒有 App 名前綴的裸資料夾(單純叫 `UITests/`、`IntegrationTests/`)會判失效,回頭要求要家
severity: minor
blocking: 否 — 失效方向是「多要求家」不是「放行不該放行的」,跟節點自己寫的「錨定過嚴不漏、對不上的照舊要家」設計方向一致,不構成新的逃逸缺口。
引句:「if base and ext in exts and base in top_dirs:」
1. `base = top[:-len(suf)].rstrip(".") if top.endswith(suf) else ""`:當頂層資料夾名稱剛好等於樣式本身(沒有 App 名前綴,例如就叫 `UITests/`、`IntegrationTests/`,不是 `<App>UITests/`/`Foo.IntegrationTests/`)時,`top[:-len(suf)]` 算出空字串,`if base and ...` 直接判 False——這種裸資料夾底下的檔不會被新機制認成測試資料夾。
2. 實測(隔離複本、in-process 載入,repo 本身未寫入):`_nodehome_is_test("UITests/LaunchHelper.swift", frozenset({"UITests"}))` 與 `_nodehome_is_test("IntegrationTests/Fixture.cs", frozenset({"IntegrationTests"}))` 都回 `False`(要家)。這兩個副檔名(.swift/.cs)剛好是貢獻該樣式的棧,不是誤判成別種語言——純粹因為沒有前綴資料夾陪它才落空。相對地 `_nodehome_in_stack_test_dir("Tests/AppTests/Helper.swift", ...)` 直接算單獨也是 False,但整支 `_nodehome_is_test` 仍回 True——因為前面既有的測試地圖正則 `(^|/)(tests?|__tests__|specs?)/` 剛好把裸 `Tests/`(大小寫不分)接住,這是巧合命中舊規則,不是新機制生效。
3. r1 修前的寫法(`if sufs and parts[0].endswith(sufs): return True`,沒有 base 檢查)反而認得這種裸資料夾——這次補防「業務資料夾被誤放行」時,對「無前綴的裸樣式資料夾」是新引入的收斂,節點的「沒涵蓋」段落只列了巢狀資料夾、名字對不上、Kotlin 多平台三種,沒有提到這個子情況。
佐證:file: `scripts/lumos:17802` `_nodehome_in_stack_test_dir` 的 base 計算與 `if base and ext in exts and base in top_dirs` 判斷式,是這個落空的來源。
佐證:file: `docs/lumos-toolchain-knowledge/Issues/各棧測試資料夾被當成要家.md` 「沒涵蓋」段落未列「裸資料夾(無前綴)」這個子情況。
未能重現部分:無——上面兩行 `_nodehome_is_test` 呼叫已在隔離複本 in-process 實際執行重現。

## 逐項判定

- **風險掃描(延遲快取 `_NODEHOME_STACK_TEST_DIRS` 無鎖)**:誤報。全檔(`scripts/lumos`)搜尋 `threading`/`multiprocessing`/`concurrent.futures` 零命中,`lumos` 是單行程 CLI,一次 `home check` 呼叫不會有兩條執行緒同時把這個 lazy cache 從 `None` 寫成 tuple;同檔既有的 `_TESTMAP_DIR_RE`(19848 行附近)、`_STACK_GUESS_CACHE`(14015 行)是同款寫法,delta 對這段完全沒動,跟 r1 判定(refuted)結論一致。
- **測試地圖不動**:屬實。diff 沒有修改任何 `_testmap_*` 函式;在隔離複本實跑 `python3 scripts/test_lumos.py -k testmap` 與 `-k nodehome`(177 案例)全過,`-k stack_test_dirs` 單獨也全過。
- **對照表多一個就自動跟著認,對每種棧都成立**:對 `dir_mode=="suffix"`(csharp-xunit、swift-xctest)與 `rglob_under=="src"`(kotlin-junit)兩類成立,有漂移守衛(check⑤/⑤b)覆蓋;親自對三個關鍵錨點做突變測試(拿掉副檔名錨、拿掉同名資料夾錨、拿掉 `.rstrip(".")`)全部被 `t_nodehome_stack_test_dirs_not_required` 抓到翻紅,確認測試不是空殼,`測試假綠形態` 這條紀律在這支新測試上有落實。
- **反例(ABTests、PaymentGatewayTests 裡的 .py、LoadTests、CheckoutIntegrationTests 裡的 .go)都真的在測試裡**:核對 `scripts/test_lumos.py` 的 `req_ok` 元組與 check④c/④d,四個反例都在其中且都斷言仍在 `req`(要家)。
- **逃逸帳(`ESC-18f03ede`)寫得對不對**:欄位齊全(`ts/token/loop/stage/severity/desc`,跟同檔最近兩筆同形狀),`severity: major` 在值域內,`loop: code-每支檔有家` 在既有紀錄裡有據可查,不是掛空迴圈名。
- **圖譜殘留舊說法**:diff 本身沒有動任何其他節點或 skill 文件;經讀碼確認新機制只掛進 `_nodehome_required` 單一呼叫點(`scripts/lumos:18016`),沒有第二套「測試檔判定」邏輯留在別處會跟這次改動打架。
- **圖譜鏡頭固定席逐條判**(這次改動範圍只在 `_nodehome_stack_test_dirs`/`_nodehome_in_stack_test_dir`/`_nodehome_is_test`/`_nodehome_required` 四處與一支新測試,經讀碼確認跟以下節點的合約敘述所管的程式路徑無交集):
  - `bound-tests-gate.md`:diff 只新增/引用一支測試方法,沒有動 code-loop 找測試、判紅、判懸空的邏輯——不影響。
  - `canary-audit.md`、`guard-kill.md`:diff 完全沒有碰 canary record/second 或 guard kill 的任何函式——不影響。
  - `slim-get-一行安裝.md`/`slim-install-安裝器.md`/`slim-uninstall-一行卸載.md`:diff 沒有觸碰安裝/卸載/CLAUDE.md 注入相關函式——不影響。
  - `授權與歸屬.md`:diff 沒有動 `_vendor_toolchain` 或白名單清單——不影響。
  - `測試假綠形態.md`:見上方「測試假綠形態」條——這次新測試有配前置斷言(親自突變驗證),遵守了這條紀律;F1 提到的裸資料夾情境沒有被這支測試覆蓋到,屬覆蓋缺口而非違反本節點合約字面。
  - 其餘只列名的 11 篇(lumos-cli-read/lumos-cli-lifecycle/design-loop/pitfalls-code-loop/loop-convergence-recording/lumos-deinit/節點範圍與索引守衛/reversibility-governance-ledger/doctor-irreversible-hint/lumos-refcheck/check-r-guard/check-t-sentinel/cochange-guard/core-invariant-baseline/judge-severity-gate):列名成因是 `scripts/lumos`、`scripts/test_lumos.py` 是巨型共用檔、被很多節點的 about_code 列為家,不是這次改動邏輯範圍碰到——不影響。

總結:最高 severity minor,blocking 共 0 條
