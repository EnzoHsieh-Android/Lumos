# code-選擇點第二批 r6 待驗行為(修補鏡頭配對案例)

只列待驗範圍,不是「已修好」的證據。修前 c261a15476b435bc8fb9297df77dc16a3e93e265、修後 8333987ac69606c3b1ec1068f55066fa923bc619。來源:計劃 docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md 的範圍 2、範圍 4、條款 S5 S6 與預期值表。修後版本的選擇點相關測試跑過一次全綠(choice_points 105、kt_catalog 320、choice 410、choice_table_batch2 22、choice_samples_batch2 33),check.py 型錄檢查 0 問題。修正關卡結果在 r5-fix-check.txt。

| 組 | 角色 | 待驗行為(輸入 → 預期) | 出處 | 相關測試(修後) |
|---|---|---|---|---|
| G1 | repair | 方法名比對 regex 的頭尾錨點拿掉任一個 → `x.letX`、`a.combineLatest`、`MyLaunchedEffect`、`myremember` 那幾行 MISS 樣本被誤命中而翻紅;`Unit` 的錨點拿掉 → `LaunchedEffect(distanceUnit)`、`LaunchedEffect(UnitX)`、`remember(distanceUnit)` HIT 樣本翻紅 | 計劃範圍 2 | t_choice_samples_batch2 |
| G1 | repair | C-35 接收者寫法 regex 拿掉安全呼叫那支或 `\s*` → `a?.combine(b)`、`a . combine(b)` HIT 樣本翻紅;完整套件名 regex 拿掉 `\s*` → 跨行 `kotlinx.coroutines` / `.flow.combine` MISS 樣本翻紅 | 計劃範圍 2 | t_choice_samples_batch2 |
| G1 | repair | C-34 if 區塊裡最後一個陳述後接註解、`finally` 區塊、點號前後空白、沒有呼叫的 `x.let` 各一行樣本,對應子句拿掉時翻紅 | 計劃範圍 2「最後一個陳述」 | t_choice_samples_batch2 |
| G1 | repair | C-36、C-37 literal-arg 不再比對開頭是不是 `-`、`+`,只看前綴運算式包常數:`LaunchedEffect(@Suppress("x") 1)` 不命中;`LaunchedEffect(-k + 1)` 是二元運算、照命中;拿掉 `kind: prefix_expression` 時後者翻紅 | 計劃範圍 2 字面值說明 | t_choice_samples_batch2 |
| G1 | preserve | 第五輪前既有的 C-32 到 C-37 樣本行(`-1`、`-1L`、`-0x1F`、`+2.5` 不命中,`-1.coerceAtLeast(k)`、`-k` 命中,else-if 鏈不收、catch 區塊當陳述不收)結果不變;C-36 與 C-37 的 literal-arg 兩份仍一字不差 | 預期值表 | t_choice_samples_batch2、t_choice_points_compose |
| G2 | repair | 選擇點表列號 `C-0`、乾節點表 `A-0` → 報「列號要寫成…」 | S5、計劃範圍 4 | t_choice_table_batch2 |
| G2 | preserve | 正常列號 `C-1`、`C-40`、`A-1` 照認;前導零與全形照擋;撤號那一行判法不變 | S5、S6 | t_choice_table_batch2 |

未覆蓋:變異掃描與差異比對是編排者手動跑(r5-intake〈等價存活〉與 r5-mutsweep.txt),不是測試的一部分;差異比對只證明編排者那份語料分不出來,不證明等價;第三輪放行的兩條(括號包住的常數 key 照樣命中、引數層層巢狀的輸出平方成長)沒有自動測試。
