severity: minor

## g1 標註加字串、布林、null、字元常數仍被當成非常數 key,文件卻宣稱「標註加常數同樣算常數」
severity: minor
blocking: 否 這是規則收窄不完整,實際寫法極罕見,只會多產一個等價變異,不會讓守衛失效或壞資料。

- 輸入:`LaunchedEffect(@Suppress("x") "s") { load() }`、`LaunchedEffect(@Suppress("x") true)`、`LaunchedEffect(@Suppress("x") null)`、`LaunchedEffect(@Suppress("x") 'c')`。`remember` 的寫法同理。
- 走到的函式:`configs/ast-grep/kotlin-choice/rules-choice/api.yml` 裡 C-36 與 C-37 各一份的 `literal-arg`。修補把 `prefix_expression` 的 `regex: '^[-+]'` 拿掉,但 `has` 的末子節點仍只收數字類型(integer、real、long、hex、bin、unsigned)。
- 預期:計劃文字寫「標註加常數 `@Suppress("x") 1` 也是前綴運算式、同樣算常數」,所以標註加任何常數都該算字面值、不命中。
- 實際:只有標註加數字被收掉。其餘四種仍命中 C-36(這個 key 的變異 `(Unit)` 必然等價,規則本來就要排除這種情況)。
- 兩版結果相同:修前 c261a154 與修後 8333987a 對 t2.kt 的輸出都是 C-36 命中第 2 到 5 行。修後沒有退步,只是修得不夠徹底。
- 歸因:有證據的原有漏查。修前與修後我都用 `ast-grep scan -r rules-choice/api.yml` 跑過同一個 t2.kt,結果一致。
- 附帶:`!true`、`-(1)`、`- -1` 同樣仍命中。這些是更早就有的邊角,語法上不實際。

引句:「標註加常數 `@Suppress("x") 1` 也是前綴運算式、同樣算常數」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:240`

## 圖譜鏡頭(固定席逐條判)
- kotlin規則包(家):不影響程式行為。api.yml 與樣本改動已跟計劃文字同步,`t_choice_samples_batch2` 與 `t_choice_table_batch2` 在修後各是 33/0 與 22/0 通過。
- bound-tests-gate、guard-kill、lumos-cli-lifecycle、測試假綠形態、lumos-cli-read:不影響。修補沒動 `scripts/lumos`,只動 api.yml、樣本和測試檔,各自的 ★INVARIANT★ 綁的測試不在這次改動路徑上。
- pitfalls-code-loop、loop-convergence-recording(★RISK★,牽連檔 `scripts/lumos`):不影響。這個修補沒碰 `scripts/lumos`。
- 殘留(最後一段必答):`governance/residual-index.json` 在 6857e3d6 到 8333987a 之間沒有 diff,修補也沒有換編號或改字重問,第二個代理沒有換人。派工鏡頭的殘留清單因超時算不出來,我只憑 `git diff --stat` 判斷,沒有核對治理帳的 residual-ask 列,這部分標未判定。

## 三問與已驗主張的證據
1. 原問題的修復效果:`remember(@Suppress("x") 1)`(`t.kt` 第 18 行)修前命中 C-37,修後不再命中。`LaunchedEffect(@Suppress("x") 1)` 修前命中 C-36,修後不再命中。
   - 為什麼不是假修:我把修前的 api.yml 換回修後的 repo,跑 `-k choice_samples_batch2`,結果是 `✗ S6 … 樣本 choice-batch2.kt 第 119 行標 MISS,規則卻有節點從這一行開始`,即 32 通過 1 失敗。這證明新樣本能抓到被還原的修補。
2. 修補處的正常、錯誤、相鄰路徑:
   - 仍命中(預期命中):`@Suppress("x") k`、`!flag`、`-k`、`++k`、`k++`、`@Suppress("x") 1.coerceAtLeast(k)`、`@Suppress("x") "s${k}"`、`remember(@Suppress("x") k)`。
   - 沿用既有行為:`-1`、`-0x1F`、`-1L` 等負數常數仍不命中,既有測試都通過。
   - 副作用:`prefix_expression` 拿掉開頭比對後,任何末子節點是數字的前綴運算式都算常數。以我試的寫法,沒有看到把非常數誤當常數的情況。
   - C-36 與 C-37 兩份 `literal-arg` 一字不差,由 `t_choice_samples_batch2` 的比對守住。我只驗了 C-36 樣本能翻紅,C-37 沒有標註加數字的樣本行,靠兩份一致的比對守住。
3. 新發現 g1 的同一案例:修前與修後都是命中,見 g1。
   - 測試補強:`C-0`、`A-0` 兩個案例在修前版本就已通過(`check.py` 本來就拒絕零),所以它們是新增的釘子,不是翻紅證據。
   - 這個修補沒有改 `check.py`,這兩條只確認既有行為。

- 未驗範圍:沒跑全套測試。其他 hunk(樣本新增的名字頭尾、套件名、點號空白、`finally` 等)只靠 `-k choice_samples_batch2` 的 HIT/MISS 核對,我沒有逐行另造反例。
- 清理:臨時目錄已用字面絕對路徑刪除。

最嚴重:minor;blocking 共 0 條
