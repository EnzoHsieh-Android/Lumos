severity: minor

我找不到會出錯的輸入,所以這份改動沒有 blocker 或 major。

## 驗證方式
- 原版跑 `-k kotlin_rulepack`:511 通過、0 失敗(ast-grep 0.51.1)。
- 在複本裡逐個拿掉規則的 14 個比對樣式或排除,每次重跑 `t_kotlin_rulepack_security_rules`,14 個全部翻紅。
  - 拿掉的有:四個 collect 寫法、四個 launch 寫法、兩個 launchIn 寫法、兩個 repeatOnLifecycle 排除、兩處 flowWithLifecycle 排除。
  - 其中拿掉 `$F.collect { $$$ }` 是被 C231 等既有例子抓到,不是 C242;因為 `$F.collect($$$)` 也吃得下尾隨 lambda,C242 第 5 行本來就蓋不到它。這個樣式有人守著,所以不算洞。
- 邊界輸入直接餵規則(複本上的 `p/rule.yml`),結果都合理。
  - 「Service 在類別宣告跨行」「有主建構子」不報。
  - 同檔 Fragment、頂層函式、Fragment 內的內部 Service 照報。
  - 巢狀 launch 只報一次,裡面有 repeatOnLifecycle 的那條排除。
- 唯一的偏差:`object : LifecycleService() { ... }` 這種匿名物件,夾在 Fragment 裡收集時仍會報。匿名 Service 實務上不存在,不值得標。

## i1
severity: minor
blocking: 否
引句:「規則例外判斷不了「這段收集在需求上該不該在背景跑」;自寫基底類別間接繼承 Service 的情況認不出。」
file: `docs/lumos-toolchain-knowledge/Projects/簡報審查抓到的機制缺口_計劃.md`(〈天花板〉節)
失敗場景:天花板節沒寫到 `object : LifecycleService()` 這類匿名物件(物件字面量不是 class_declaration)。但這個輸入實務上不會出現,而且只會讓它多報一次,不會漏報,所以只是文件精度。
歸因:原有漏查。這個盲點隨第一版「外圍要是 class_declaration」的寫法就存在,不是 r3 修補造成的。修補差異沒動 `state.yml`,只動了測試與計劃。
兩版證據:`p/src/a.kt` 的 D 案例(Fragment 裡有匿名 `object : LifecycleService()` 內收集)在修前、修後都報第 16 行,因為規則檔兩版相同。

## 圖譜固定席逐條判定
- `測試假綠形態`(★INVARIANT★ 要求還原翻紅釘要有前置斷言證明現場成立):不影響,而且新測試符合。C242 先要求「七行全報、行號寫死」,等於前置斷言;C243 要求「零報」,靠 C242 同一套寫法證明偵測段有效。上面 14 次改壞都翻紅,證明不是假綠。
- `授權與歸屬`:不影響,沒動授權檔或 `_VENDORED_TOOLKIT`。
- `arch-alignment-lens`、`test-quality-handbook`:不影響。逐例表是既有格式(第五欄是預期行號)。
- `lumos-cli-read`、`design-loop` 等其餘列名節點:不影響,因為本次沒動 search 的過濾,也沒動設計審的處置閘。
- 超出上限、只列名的節點:沒有逐條判。

## 三問
1. 原問題「刪掉規則偵測段測試照綠」的修復效果:
   - claim:C242、C243 守住原有偵測與排除。
   - input:對 `state.yml` 逐項拿掉 12 個比對樣式或排除,再各拿掉兩處 flowWithLifecycle 排除。
   - expected:每次都有逐例紅。
   - case_source:本席複本實驗。
   - before:r3 之前沒有 C242、C243,作者說拿掉 launchIn 整段照綠。我沒有重跑舊版,所以「修前照綠」是未判定。
   - after:14 次全紅,例如拿掉 `$F.launchIn(lifecycleScope)` 時 C242 報 `[5,6,8,9,10,11]`、缺第 7 行,而 C243 已包生命週期的寫法在拿掉 repeatOnLifecycle 或 flowWithLifecycle 排除時各翻紅。
   - attribution:有證據的修復有效(修後行為);修前缺證據。
2. 修補處的正常、錯誤與相鄰呼叫路徑:C227–C241 與樣本自測照舊通過(511 通過)。Service 例外的路徑也還在:跨行宣告、有主建構子、同檔 Fragment、Fragment 內的內部 Service 都符合預期。
3. 新發現同案例修前、修後:i1 的 D 案例兩版相同(規則檔沒變),屬原有漏查,不是回歸。

未驗範圍:
- 完整樣本自測 `t_kotlin_rulepack_samples` 通過,但我沒另外檢查樣本內容是否充分。
- 其他規則檔、型錄與 README 的同步沒逐行核對。
- 修前版(771f6c11)的實際測試結果沒跑,所以「修前照綠」只憑作者描述。

最高等級:minor
