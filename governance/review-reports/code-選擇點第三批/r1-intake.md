# code-選擇點第三批 r1 收貨

席位:正確性、邊界、資源、通才、整合、架構對齊、資安,全 sonnet,全新代理。材料:程式包 r1-pack-a.patch(1357 行,正確性、邊界、資源、通才、架構對齊)、文件包 r1-pack-b.patch(481 行,整合;程式包可讀來對照)、完整凍結 r1-snapshot.patch(1838 行,資安;資安包照規矩不拆,超過 1800 行上限 38 行,帳上照實標範圍)。派工單 r1-dispatch.json(base_commit 763081c0d)。
七份收齊後才一次從逐字稿存檔;收齊前沒動工作目錄。正確性席回報時說還有背景工作在跑,取的是它最後一份以 `severity:` 開頭的完整報告。
收貨三道:七份都已是正規化格式;六份有發現的引句全數錨定;資安席 severity: clean、零發現,沒有引句可抽。refcheck 全 ok。
reflog 只有編排者自己的提交;席位沒留 worktree;這一輪臨時目錄收齊後已刪。派工鏡頭這輪逾時,固定席節點沒附上(資源、正確性兩席自述),各席改從 diff 自判,不逐條答。

發現共 18 條:正確性 c1;邊界 b1–b3;資源 r1–r3;通才 g1;整合 i1–i5;架構對齊 a1–a4(另有一則 ⚠ 交編排者:retry 兩列首次用 ast-grep 的 `constraints:`)。major 2 條(a1、a2)。

## 重現表

| id | 席 | 等級 | 編排者重現 | 處置 |
|---|---|---|---|---|
| a1 | 架構對齊 | major | HIT:`_cb2_points` 與 `_cb3_points` 各 18 行,unified diff 只差說明句、沒裝 ast-grep 時回 None 或 raise、暫存前綴、規則字典名四處 | 折:兩批共用一支 |
| a2 | 架構對齊 | major | HIT(讀規則):C-36、C-37 與 C-18 把 not 放進關聯規則裡,C-38 起整條外包;C-38 起的註解寫「同 C-18、C-34~C-37」 | 折:保留整條外包(多層鏈改放進去不等價),改註解、在 kotlin規則包 記成第二種寫法與適用條件 |
| a3 | 架構對齊 | minor | HIT(讀 `_choice_file_points`) | 折:收成小函式 |
| a4 | 架構對齊 | minor | HIT(讀 `_choice_anchor`) | 折:改用 `_CHOICE_CALL_NAME_RE` |
| a-⚠ | 架構對齊 | — | retry 兩列首次用 `constraints:`;既有寫法做不到「排除後設變數 `$A` 的值」,專案沒有可對照的做法 | 判:接受,寫進 a2 那條 WHY 一起說明(不另開發現) |
| g1 | 通才 | minor | HIT(席位實跑:兩個子協程各自立刻 `.await()` 的作用域命中 C-38、C-39) | 折:子協程不算立刻 await/join 的,照 C-50 判法 |
| c1 | 正確性 | minor | HIT(席位實跑:顯式 `onBufferOverflow = BufferOverflow.SUSPEND` 不命中 C-48) | 折:排除只在值不是 SUSPEND 時 |
| b2 | 邊界 | minor | HIT:同 c1,另 `extraBufferCapacity = 0x0` 加 DROP_OLDEST 仍命中 | 折:同 c1,零值認得十六進位、二進位、正負號、L 尾 |
| b1 | 邊界 | minor | HIT(席位在臨時 repo 實跑 choice-points:只在大括號裡加第二個 launch,有選擇點的行 0) | 折:天花板第 3 條寫明(錨點選在識別字那一行的取捨) |
| b3 | 邊界 | minor | HIT(席位實跑完整套件名與裸名稱 0 命中) | 折:天花板第 3 條補 |
| r1 | 資源 | minor | HIT(現象,席位實測 retry 串接 N=1000 約 23MB) | 折:實務隱患補「約 1500 個以上超過讀取上限」 |
| r2 | 資源 | minor | HIT(讀 `t_choice_scope_rule_output` 只取候選是 supervisorScope 那一列) | 折:S9 加 C-48、C-53 的巢狀合成輸入 |
| r3 | 資源 | minor | HIT(現象,席位實測 800 層 0.66 → 2.18 秒) | 折:實務隱患記數字 |
| i1 | 整合 | minor | HIT(讀計劃與 Verification 互指上線日) | 折:上線日寫死 2026-11-22、REVISIT 改 2027-01-22 |
| i2 | 整合 | minor | HIT(席位實跑 S9:平鋪 300 個 launch 正面寫只有約 60KB) | 折:預期值表與實務隱患的數字改成實作規則的實測值 |
| i3 | 整合 | minor | HIT(讀計劃仍寫候選與暫定列號) | 折:改成定案說法 |
| i4 | 整合 | minor | HIT(讀 kotlin規則包 那條同族「這次沒改」沒有回頭條件) | 折:補一行 REVISIT |
| i5 | 整合 | minor | HIT(讀 `_CB3_S7_PIN = tuple(_CB2_S7_PIN)`) | 折:改成獨立字面常數 |

## 分組(依根因)

- 重做既有東西(a1、a4):測試小工具與正規式各有一份現成的。
- 規則形狀與慣例(a2、a-⚠、a3):第二種雙重否定寫法要講清適用條件;依錨點分流收進小函式。
- 等價或白殺的壞法(g1、c1、b2):照 C-50 與 MutableSharedFlow 的建構限制補排除,排除條件看值不看有沒有那個引數。
- 守衛涵蓋面(r2、i5):S9 只守一列、S7 釘值不獨立。
- 漏判與成本照實記(b1、b3、r1、r3):寫進天花板與實務隱患。
- 文件跟現況對不上(i1、i2、i3、i4)。

## 先查世界

- PRIOR-ART:等價壞法事前排除——Trivial Compiler Equivalence 與常見寫法造成的等價可用便宜的靜態分析抓(https://discovery-pp.ucl.ac.uk/id/eprint/1499169/1/Jia_Trivial_Compiler_mutation-testing-papadakis-icse15.pdf 、https://homes.cs.washington.edu/~rjust/publ/equi_mutants_ems_issta_2024.pdf )。採用:立刻 await 的子協程照 C-50 的判法排除。
- PRIOR-ART:幾乎任何測試都殺得掉的壞法沒有資訊量(Ammann 與 Offutt 的 trivial mutant 分類 https://www.inf.ed.ac.uk/teaching/courses/st/2016-17/Mutest.pdf );MutableSharedFlow 只在 replay 或 extraBufferCapacity 大於 0 時接受 SUSPEND 以外的策略(https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow.html )。採用:排除條件看 onBufferOverflow 的值,顯式 SUSPEND 不排除。
- PRIOR-ART:整數零的寫法——Kotlin 語法的整數字面值含十進位、十六進位 `0x`、二進位 `0b`、底線與 `L` 尾(https://kotlinlang.org/spec/syntax-and-grammar.html ,IntegerLiteral、HexLiteral、BinLiteral)。採用:照規格列的形式認零;正負號在語法樹是前綴運算式,一併認;括號包住的不認(寫進天花板)。
- PRIOR-ART:關聯規則的寫法——ast-grep 關係規則與 `not` 組合(https://ast-grep.github.io/guide/rule-config/relational-rule.html 、https://ast-grep.github.io/reference/rule.html );專案內兩種雙重否定:單層「父節點是 X」放進關聯規則裡(C-18、C-34~C-37),多層鏈整條外包(第三批;設計審 r2 實測命中集合不變)。採用:兩種都保留,寫明適用條件。
- 重用既有測試小工具與正規式:專案內既有函式,不需查外部。
- 不加新機制的最小解:這輪沒有新增機制(排除條件、樣本與測試輸入都在既有規則與既有測試裡改)。
