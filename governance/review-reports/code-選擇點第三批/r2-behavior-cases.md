# r2 待驗案例(修前 763081c0d → 修後見 r2-repair-binding.json 的 after_commit)

案例只是待驗範圍,不是「已修好」的證據;新席自己跑兩版核對,可補案例。測試指令一律 `python3.14 scripts/test_lumos.py -k <關鍵字>`;修前版本用 `git -C <臨時目錄> worktree add <目錄> 763081c0d` 或 `git show 763081c0d:<檔>` 取。

| 組 | 角色 | 待驗行為 | 出處 | 選例依據 |
|---|---|---|---|---|
| G1 | repair | `MutableSharedFlow<Int>(replay = 1, onBufferOverflow = BufferOverflow.SUSPEND)` → C-48 命中;`replay = 1, extraBufferCapacity = 0x0, onBufferOverflow = BufferOverflow.DROP_OLDEST` → C-48 不命中(`0X00`、`0b0`、`0L`、`-0`、`+0` 同) | kotlinx.coroutines MutableSharedFlow 建構限制;計劃範圍 1、2 | 席位實跑反例 |
| G1 | preserve | `replay = 1, onBufferOverflow = BufferOverflow.DROP_OLDEST`(沒有 extraBufferCapacity)→ C-48 不命中;`replay = 1, extraBufferCapacity = 1, onBufferOverflow = …DROP_OLDEST` → 命中;`MutableSharedFlow<Int>(replay = 1)` → 命中 | 計劃預期值表 S5 | 修前就有的樣本 |
| G2 | repair | `supervisorScope { val a = async { f() }.await(); val b = async { g() }.await() }` → C-38 不命中;`launch { }.join()` 兩個同理 | 計劃〈用詞〉子協程;C-50 判法 | 席位實跑反例 |
| G2 | preserve | 兩個沒有立刻 await 的 `async`、`map { async }`、`for { launch }`、同陳述兩個 `async` → 照常命中;只有一個子協程、外層只有內層作用域的 `async` → 照常不命中 | 計劃預期值表 S5 | 修前樣本 |
| G3 | repair | S9 對 C-48、C-53 各一個巢狀 200 層的合成輸入:有雙重否定 ≤1MB,拿掉雙重否定的對照組明顯更大、命中相同 | 計劃 S9;Systems/kotlin規則包 PITFALL | 席位指出 S9 只守一列 |
| G3 | preserve | 作用域那列(平鋪 300 個 launch、巢狀 100 層)照舊 | 計劃 S9 | 修前測試 |
| G4 | repair | `_CB3_S7_PIN` 是獨立字面常數,改 `_CB2_S7_PIN` 不會連帶改它 | 計劃 S7 | 席位指出別名 |
| G4 | preserve | 第一版六支樣本檔不含第二、三批語法的行,挑法等於釘值 | 計劃 S7 | 修前測試 |
| G5 | repair | 第二、三批掃描測試共用 `_cb_points`;沒裝 ast-grep 時第二批回 None、第三批 raise `_SrcOnly` | 架構對齊 a1 | 席位指出複製品 |
| G5 | preserve | 第二批 S1–S4(`t_choice_points_nul_elvis`、`t_choice_points_nul_safecall`、`t_choice_points_batch2_api`、`t_choice_points_compose`)照綠 | 第二批計劃 | 修前測試 |
| G6 | repair | api.yml 第三批註解講清兩種雙重否定形狀;kotlin規則包 有對應 WHY | 架構對齊 a2 | 文件類 |
| G7 | repair | `_choice_err_start`:整個呼叫錨點從錨點行起算、其他錨點從命中第一行;方法名分支用 `_CHOICE_CALL_NAME_RE` | 架構對齊 a3、a4 | 重構 |
| G7 | preserve | 接收者含 ERROR、`.retry` 那行沒有 → 照樣挑出;方法名錨點(既有 API 列)挑法不變 | 計劃 S2;第二批 | 修前測試 |

文件類(b1、b3、r1、r3、i1–i4)沒有產品案例:核對計劃、Verification、Systems 筆記的說法跟程式行為一致即可。
