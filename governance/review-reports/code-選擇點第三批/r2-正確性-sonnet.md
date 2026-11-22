severity: major

## c1 C-38/C-39 的「立刻 await/join 不算子協程」排除不看順序,把真正同時跑的兄弟排掉

severity: major
blocking: 是

歸因:有證據的修復回歸(修前命中、修後不命中,同一輸入)

引句:「建立後同一個運算式就 .await()/.join() 的不算(做完才開下一支,兩種作用域必然等價;同 C-50 只看直接接在後面那一層」

失敗場景:`child-co` 只看這一支子協程自己是否被直接 `.await()`/`.join()`,不看它前面有沒有還在跑的兄弟。規則的理由是「做完才開下一支」。但「先開一支沒等的,再開一支立刻等的」時,前一支在等待期間仍同時執行。前一支失敗時,`coroutineScope` 會取消正在等的那支,`supervisorScope` 不會。兩種作用域在這裡不等價,是該命中的選擇點。

- 輸入 A:`supervisorScope { val a = async { f() }; val b = async { g() }.await(); a.await() }`。
- 輸入 B:`coroutineScope { launch { a() }; val r = async { b() }.await() }`。
- 走到的行:`child-co` 新加的 `not: inside: navigation_expression … (await|join)`。`b` 被排掉後只剩 `a` 一支子協程,`many-co` 的配對湊不成兩支,整個作用域不命中。

兩版查證(`ast-grep scan --config configs/ast-grep/kotlin-choice/sgconfig.yml --json=stream` 掃同一個探針檔,分別在 763081c0d 與 926c72056 的 worktree 內跑):
- 修前:輸入 A 命中 C-38;輸入 B 命中 C-39。
- 修後:兩個都不命中。

測試為何抓不到:新增的 MISS 樣本是 `supervisorScope { val a = async { f() }.await(); launch { g() } }`,也就是「先等完、後開」,剛好是真正循序的順序。沒有任何樣本涵蓋「沒等的在前、立刻等的在後」。把排除條件改成「只排掉前面沒有其他子協程的」,測試照綠。

可行的修法:排除條件要加上順序判斷(例如只排掉前面沒有其他子協程的那一支),或承認這是天花板、寫進計劃與型錄。

重現指令:把輸入 A 存成 `.kt`,用上面的 ast-grep 指令在兩版 worktree 各掃一次,對照 C-38 是否出現。

## 已驗主張與證據

對應三問(原問題修復效果、修補處相鄰路徑、新發現同案例的前後結果)。

- G2 repair 成立:
  - claim:`supervisorScope { val a = async{f()}.await(); val b = async{g()}.await() }` 不命中。
  - input:同上,另加 `coroutineScope { launch{a()}.join(); launch{b()}.join() }`、`ids.map { async{load(it)}.await() }`、`?.await()`、多行換行寫法。
  - expected:不命中(循序)。
  - case_source:席位自寫探針,加 r2-behavior-cases.md 的 G2。
  - before:C-38 命中。
  - after:不命中。
  - comparison:修復有效。
- G2 preserve 成立:
  - 兩個都沒立刻 await 的 `async`、`ids.map { async }`、括號包住的 `(async{}).await()`(保守命中)、`launch{}.join(); launch{}; launch{}`(C-39 照命中)、`async { async{1}.await() }; async{2}`,修前修後結果一致。
  - 輸入 B、輸入 A 是例外,見 c1。
- G1 repair 成立:
  - 命中:`onBufferOverflow = BufferOverflow.SUSPEND`、完整套件名、裸 `SUSPEND`、後面帶註解、搭配 `extraBufferCapacity = 5`。
  - 排除:`extraBufferCapacity = 0x0`、`0b0`、`-0`、`0 /* z */`、`- 0`、`0_0`。
  - before:帶 SUSPEND 的那幾種不命中(修前以為換 0 會丟例外)。
  - after:命中。
  - 零寫成 `0x0` 等寫法:修前、修後都排除。
  - 保守邊界(已知,不算新洞):`(0)` 命中,變數 `policy` 不命中。
  - preserve:非零 `extraBufferCapacity`(`0xFF`、`0b101`、`10` 等)仍命中。
- G3 repair:`python3.14 scripts/test_lumos.py -k choice_scope_rule_output` 14 項全過。
  - C-48 輸出 193824 位元組,拿掉雙重否定是 73098534 位元組。
  - C-53 輸出 196549 位元組,拿掉雙重否定是 89532423 位元組。
  - 新的 `not: inside` 沒有讓巢狀作用域列超量。
  - 修前沒有跑,因此「修前缺這兩列守衛」未驗;這輪只驗修後行為。
- G4 repair:`_CB3_S7_PIN` 是獨立字面值,用 `ast.literal_eval` 比對與 `_CB2_S7_PIN` 都是 82 筆且完全相同。
- G5:
  - 全 repo 沒有殘留的 `_cb2_points`、`_cb3_points` 呼叫。
  - 沒給 `skip` 時回 None,給了就 raise `_SrcOnly`,訊息字串與修前相同。
  - 暫存目錄改成用完即刪,是行為上的小改善。
  - `python3.14 scripts/test_lumos.py -k choice_points` 142 項全過;`-k choice_samples_batch3` 40 項全過。
- G7:`_choice_err_start` 與修前的內嵌三元式等價。「方法名」分支改用帶 pos/endpos 的 `_CHOICE_CALL_NAME_RE.match`,與切片後 `re.match` 等價,因為 `\s*` 超不出 endpos,`\w` 都是 ASCII。相關測試(S1、S2)隨 `-k choice_points` 全綠。

未驗範圍:
- G6(api.yml 註解與 kotlin規則包 WHY 是否對得上)是文件類,沒有核對 kotlin規則包 筆記。
- 沒對 `0u`、`0B0`、`0UL` 等罕見零寫法做全面窮舉。
- 角色卡 be-api-compat 與 be-authz 不適用:diff 只含規則包、型錄與測試,沒有對外 API 或授權端點。

總結:最高嚴重度 major,blocking 共 1 條
