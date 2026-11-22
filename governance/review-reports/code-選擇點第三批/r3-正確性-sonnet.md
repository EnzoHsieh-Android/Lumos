severity: minor

驗收範圍:修補差異的程式一半逐 hunk 讀完。修前(926c72056)與修後(9ebd62d60)各開臨時 worktree,用同一批 Kotlin 樣本、同一份 `sgconfig.yml` 跑 ast-grep。本席未跑 `lint-new`,也沒讀文件那一半;臨時目錄已刪。

## c1 形狀測試對「id 行帶尾註解」的規則會靜默略過
severity: minor
blocking: 否

引句:「m = _re_mod.search(r"^id:\s*(C-\d+)\s*$", doc, _re_mod.M)」

- **失敗場景**:`api.yml` 裡某條規則若寫成 `id: C-41  # 備註`,正則吃不到,這條規則不進 `docs`。S11 對它一條斷言都不跑,也不報錯。當時把它包回雙重否定或拿掉外包,S11 都照綠。
- **目前沒有實際發生**:現行 `api.yml` 沒有這種寫法。實跑 `-k choice_rule_shape_batch3` 為 20 passed,即 1 條判準加 18 條規則加 1 條判準,全數有被檢。
- **缺的守衛**:沒有「`_CB3_IDS` 裡凡出現在 `api.yml` 的 id 都必須被解析到」這類下限檢查。
- **歸因:未判定**。這是這輪新增的測試本身的洞,不是修補造成的回歸,修前也沒有這支測試。
- 查證:`python3.14 scripts/test_lumos.py -k choice_rule_shape_batch3` 在修後為 20 passed。「尾註解漏檢」是從正則字面推出,我沒實際改檔重現,但推論只靠這條正則。

## 鏡頭 4 與三問的驗收(無 finding 的已驗主張)

**1. 拿掉 C-38、C-39 的「立刻 await/join 不算」排除後,原本被誤排的案例回到命中。**
- claim:三條「先開不等、再立刻等」的案例回到命中。
- input:
  - `supervisorScope { launch { g() }; async { f() }.await() }`
  - `supervisorScope { val a = async { f() }; val b = async { g() }.await(); a.await() }`
  - `coroutineScope { launch { a() }; val r = async { b() }.await() }`
- expected:C-38、C-38、C-39 各命中,兩支同時在跑。
- case_source:`r3-behavior-cases.md` 的 H1 repair。
- before:三條都沒有 C-38/C-39 命中。
- after:三條各命中(C-38 兩條、C-39 一條)。
- attribution:有證據的修復效果(同批樣本兩版對掃,差異只有這三行)。
- 變異驗證:把修前的 `api.yml` 換進修後樹,`t_choice_samples_batch3` 紅,列出 35、39、40、42、43、44 行標 HIT 但規則沒命中。測試咬得住。

**2. 長鏈效能。**
- input:`supervisorScope { launch { a() }.join().join()…(×500) }`。
- before:`real 8.19s`;after:`real 0.32s`。兩版命中數同為 0,因為只有一個子協程。
- attribution:有證據的修復效果。

**3. 拿掉排除後沒有別的寫法因此誤命中。**
- 我補的 10 種單子協程形態,修後都沒有新的誤命中。
- 這 10 種是:
  - `launch(Dispatchers.IO){}`
  - `async(start=…){}.await().also{}`
  - 巢狀 `async{ async{} }`
  - `foo(async{}, 3)`
  - if 表達式裡的 async
  - `.also{ it.join() }`
  - `launch{}.join(); println`
  - 其他單子協程變形
- 兩個各自立刻 await 的 `async`(`async { a() }.await(); async { b() }.await()`),修前未命中、修後命中。這是計劃〈天花板〉第 3 條已知的取捨,不算新洞,也不是誤命中。

**4. C-40~C-47 改寫前後命中集合相同。**
- input:同一個 `a.kt` 樣本,涵蓋 `?.`、`list::singleOrNull` 引用、`foo.bar.firstOrNull()`、鏈式 `.toLongOrNull().toDoubleOrNull()`、`list.map { it.singleOrNull() }`、`.mapLatest`、`.transformLatest`、`s.toIntOrNull` 無括號。
- 兩版的 `diff` 只差 C-38、C-39 那三行。C-40~C-47 全數相同,`?.singleOrNull` 的命中也一致。
- attribution:修補沒有改變命中集合。
- 已知代價(不算 finding):200 層 `.singleOrNull()` 鏈的輸出,雙重否定時約 0.72MB,正面寫時約 2.05MB,與 `r3-behavior-cases.md` 的已知取捨一致。實際輸出沒有失控。

**5. `t_choice_rule_shape_batch3` 的判準沒有誤判。**
- 把修前的 `api.yml`(C-40~C-47 包雙重否定)換進修後樹,S11 的 C-40 到 C-47 全部紅。
- 判準本身:第一版 C-19 判成不用包,C-38、C-39 判成要包。
- 測試 20/20 通過,另外 `-k choice_samples_batch3` 43 passed、`-k choice_scope_rule_output` 14 passed(S9 輸出量 ≤1MB 不變)。
- 我沒有另外做「拿掉 C-38 外包」的變異驗證,只靠讀 `top and not other` 的邏輯推判。

**角色鏡頭**:這次改動沒有對外 API 欄位或授權端點,`be-api-compat`、`be-authz` 兩題不適用。

總結:最高嚴重度 minor,blocking 共 0 條
