# code-選擇點第二批 r5 待驗行為(修補鏡頭配對案例)

只列待驗範圍,不是「已修好」的證據。修前 59c410383b0337ed842ce8e1a9e25d8eb7a3c476、修後 c261a15476b435bc8fb9297df77dc16a3e93e265。來源:計劃 docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md 的範圍 2、範圍 4、條款 S5 S6 與預期值表。修後版本的選擇點相關測試跑過一次全綠(choice_points 105、kt_catalog 320、choice 408、choice_table_batch2 20、choice_samples_batch2 33),check.py 型錄檢查 0 問題。修正關卡結果在 r4-fix-check.txt。

| 組 | 角色 | 待驗行為(輸入 → 預期) | 出處 | 相關測試(修後) |
|---|---|---|---|---|
| G1 | repair | api.yml 的 C-34 到 C-37 任一行刪掉、或行內任一 `{kind: …}`、`matches`、`regex`、`stopBy` 選項拿掉 → 樣本核對翻紅;例外只有作者判等價的幾類(父節點種類本來固定的限定、`regex: '^[-+]'`、`stopBy: end`、literal-arg 的 nthChild reverse)與 C-37 literal-arg 區(由 C-36 與 C-37 literal-arg 一字不差的比對測試守) | 計劃範圍 2;Semgrep 規則測試每個排除條件各一行 | t_choice_samples_batch2 |
| G1 | repair | 拿掉方法名比對的 `regex`(let、combine、LaunchedEffect、remember)→ `x.also`、`a.zip`、`LaunchedEffectCompat`、`run`、`rememberSaveable` 那幾行 MISS 樣本被誤命中而翻紅 | 計劃範圍 2 | t_choice_samples_batch2 |
| G1 | repair | 拿掉註解排除(`line_comment`、`multiline_comment`)→ 最後一個陳述後面接行尾註解的兩行 HIT 樣本翻紅 | 計劃範圍 2「最後一個陳述」 | t_choice_samples_batch2 |
| G1 | preserve | 第四輪前既有的 C-32 到 C-37 樣本行(else-if 鏈不收、`-1.coerceAtLeast(k)` 命中、`LaunchedEffect(-1)` 不命中、catch 區塊當陳述不收)結果不變 | 預期值表 | t_choice_samples_batch2、t_choice_points_compose |
| G2 | repair | 選擇點表列號寫成 `C-040`、`C-４０`、`C-4０`,乾節點表寫成 `A-01` → 報「列號要寫成…」,不因規則 id 跟著寫成同樣子而繞過撤號 | S5、計劃範圍 4 | t_choice_table_batch2 |
| G2 | preserve | 正常列號 `C-1`、`C-40`、`A-1` 照認;撤號那一行的判法(只認半形不帶前導零、恰好一行頂格)不變;規則 id 要等於列號的檢查照舊 | S5、S6 | t_choice_table_batch2 |

未覆蓋:逐條拿掉的掃描是編排者手動跑(r4-intake 重現表 c1 列與〈等價存活〉),不是測試的一部分;第三輪放行的兩條(括號包住的常數 key 照樣命中、引數層層巢狀的輸出平方成長)沒有自動測試。
