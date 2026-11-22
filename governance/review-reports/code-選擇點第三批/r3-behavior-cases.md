# r3 待驗案例(修前 926c72056 → 修後見 r3-repair-binding.json 的 after_commit)

案例只是待驗範圍,不是「已修好」的證據;新席自己跑兩版核對,可補案例。測試指令一律 `python3.14 scripts/test_lumos.py -k <關鍵字>`;修前版本用 `git -C <臨時目錄> worktree add <目錄> 926c72056` 或 `git show 926c72056:<檔>` 取。

| 組 | 角色 | 待驗行為 | 出處 | 選例依據 |
|---|---|---|---|---|
| H1 | repair | `supervisorScope { launch { g() }; async { f() }.await() }`、`supervisorScope { val a = async { f() }; val b = async { g() }.await(); a.await() }`、`coroutineScope { launch { a() }; val r = async { b() }.await() }` → C-38/C-39 命中(兩支同時在跑) | 計劃〈用詞〉子協程;〈天花板〉第 3 條 | 席位實跑反例 |
| H1 | repair | 作用域裡 `launch{a()}` 後接 500 個 `.join()` 的長鏈 → 掃描回到 1 秒內 | 計劃〈實務隱患〉輸出量與時間 | 席位實測 |
| H1 | preserve | 只有一個子協程、外層只有內層作用域的 `async`、`scope.launch` 兩個 → 照常不命中;兩個沒等的 `async`、`map { async }`、`for { launch }` → 照常命中 | 計劃預期值表 S5 | 修前樣本 |
| H1 | 已知取捨 | 每支都建立後立刻 await/join 的作用域 → 照樣命中(換寫法必然等價,落成等價放行) | 計劃〈天花板〉第 3 條 | 這輪換形狀的代價 |
| H2 | repair | C-40~C-47 的規則形狀跟第一批 C-19~C-31 一字不差(正面 inside);`t_choice_rule_shape_batch3` 把 C-40 包回雙重否定、或拿掉 C-38 的雙重否定會紅 | 計劃 S11;Systems/kotlin規則包 WHY | 席位指出兩種並存條件對不上 |
| H2 | preserve | C-38、C-39、C-48~C-50、C-53 照舊整條外包;S9 輸出量照舊 ≤1MB;C-51、C-52(往上一層再往下看 BufferOverflow)照新判準保留外包 | 計劃 S9、S11 | 修前測試 |
| H2 | 已知取捨 | C-40~C-47 改回正面寫後,巢狀 200 層合成輸入的輸出約 24MB(第一版 C-19 同輸入約 23.5MB);真實專案最大檔多約 2 到 3KB | Systems/kotlin規則包 WHY 的代價欄;Verification r2 段 | 照既有寫法的代價 |

文件類(i1–i6)沒有產品案例:核對計劃、Verification、Systems 筆記的說法跟程式行為一致即可(上線日改回合併當天定、REVISIT 暫寫 2027-01-31)。
