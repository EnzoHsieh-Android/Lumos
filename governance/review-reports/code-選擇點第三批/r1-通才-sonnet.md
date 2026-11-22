severity: minor

我逐 hunk 讀完整份 diff,並追了 `_choice_anchor`、`_choice_anchor_edits`、`_choice_also`、`_choice_pick`、`_choice_file_points` 的呼叫者。批次三相關的 `-k choice_points_batch3`、`choice_samples_batch3`、`choice_table_batch3`、`choice_scope_rule_output` 全部通過。我另外用真規則加真 ast-grep 對自造輸入實跑過:retry 鏈、換行與註解、`?.`、`Result` 排除、深巢狀 150 層、3000 條敘述、1500 個 retry 串接。結果都沒有出錯,耗時都在 2 秒內。

圖譜鏡頭:這次沒附固定席節點,不逐條答。我只判斷:`_choice_anchor` 與 `_choice_anchor_edits` 新增的「整個呼叫」分支都擋在既有分支前面,而且只在 `row["anchor"] == "整個呼叫"` 時進入,所以既有錨點(含 C-31 的 `(拿掉呼叫)`)的行為不變。`_choice_also` 放寬後,原有列只有 C-18 是「運算元起始」類,其「需補的 import」欄是 `(無)`,仍回 None,不受影響。

## g1 C-38/C-39 對「建立後立刻 await」的作用域產出等價壞法
severity: minor
blocking: 否

引句:「supervisorScope { val a = async { f() }; a.await() } // MISS C-38」

file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(C-38 的 `many-co` 與 `child-co`)

失敗場景:
- 輸入是兩個子協程各自立刻 `.await()` 的作用域:`supervisorScope { val a = async { f() }.await(); val b = async { g() }.await() }`。
- 我實跑,C-38 與 C-39 都命中,並且挑出把 `supervisorScope` 換成 `coroutineScope` 的壞法。
- 這個寫法下,第一個 `await()` 失敗會在作用域大括號本體裡直接丟出例外,第二個 `async` 根本沒開始。兩種作用域的行為相同,所以這是等價變異,守門測試不可能殺掉它,只會逼作者補一個不存在的需求。
- 同一批的 C-50 已經把「建立後立刻 `.await()`」排除,C-38/C-39 沒有同樣處理。樣本也只有「單一 `async` 加 `a.await()`」的 MISS,沒有這種兩個都立刻 await 的形狀。

重現:
- 把上述單行或多行片段放進 `package x` 的 suspend 函式。
- 用 `ast-grep scan` 搭配真的 `configs/ast-grep/kotlin-choice` 規則掃,會看到 C-38 在 `supervisorScope {` 那一行命中。
- 再用 `m._choice_file_points` 跑,會挑出 `coroutineScope` 的壞法。

總結:最高嚴重度 minor,blocking 共 0 條
