severity: clean

沒有 finding。我實跑了 ast-grep 與測試子集,沒找到修補引入的問題,也沒找到上輪沒人看的新洞。

## 三問

**① 原問題的修復效果有何行為證據?**
- r2 的問題有兩個:呼叫名的 `^` 錨點沒有測試釘住,〈天花板〉也少列了括號裡再有括號的漏報。
- 我把 `rules/compose.yml` 的密碼欄規則抽成臨時檔,拿掉呼叫名的兩個 `^` 做變異。
  - 原規則對 `MyTextField(...)`(C121)與 `androidx.compose.material3.TextField(...)`(C122)都不報。
  - 變異後兩者都報,所以 C121、C122 抓得住改壞。
- C123(`imeAction = if (x) … else …`)在原規則下輸出 0 筆。若有人把規則升級成能判括號,期望值 0 會翻紅,所以它確實釘住現行行為。
- 測試:`python3.14 scripts/test_lumos.py -k kotlin_rulepack_security_rules` 結果 194 passed、0 failed。
- 修前紅的部分只有 intake 自述,我沒有重跑 b3561e61 版本。這項標「未判定」。

**② 修補處的正常、錯誤與相鄰路徑是否仍成立?**
- 我另跑了 30 個表上沒列的 Compose 寫法,結果都跟預期值表與〈天花板〉一致。
- 報的有:
  - 沒有 `keyboardOptions`
  - `KeyboardOptions.Default`
  - `keyboardType = Text/Email/Ascii`
  - 逗號尾隨與換行
  - 位置參數的 `KeyboardOptions`
  - 尾隨 lambda
  - `PasswordVisualTransformation('*')`
  - `OutlinedTextField` 與 `BasicTextField`
  - 一個檔裡有兩個欄位
- 不報的有:
  - `KeyboardType.Password` 與 `NumberPassword`
  - 括號裡有 `if (..)` 或 `when (..)` 或註解括號
  - 變數形態的 `keyboardOptions`
  - `.copy(...)`
  - `TextField&lt;String&gt;`
  - `remember { PasswordVisualTransformation() }`
  - 靜態匯入的 `keyboardType = Password`
- 不報的這些都在〈天花板〉清單內,或漏報方向安全,沒有不在清單裡的誤擋。
- 要補一句:`remember { PasswordVisualTransformation() }` 也會被報(筆者誤讀成漏報),是正確的報。上面清單只是歸類,不影響結論。

**③ 新發現的同一案例在修前、修後各是什麼結果?**
沒有新發現。規則檔與 C95~C120 在 r2 到 r3 之間沒動,r3 只加了 C121~C123 三例與文件。

## 圖譜固定席逐條判定
- 測試假綠形態、授權與歸屬、test-quality-handbook、arch-alignment-lens、lumos-cli-read、bound-tests-gate、canary-audit 這幾篇:不影響。
  - 理由:這份 diff 對 `scripts/test_lumos.py` 只在逐例表加三筆資料,並改一段測試說明字串。
  - 沒動任何檢查邏輯,也沒動 INVARIANT 綁定的測試函式。
- 「還原翻紅釘需前置斷言」那條:不影響。
  - C121、C122 的現場成立,因為對照組(變異後)確實報出。
  - C123 是釘 0 筆的現況,以前述「規則升級就翻紅」作證。
- 回頭重讀指紋那篇計劃:不影響。這份 diff 沒碰指紋機制。
- 「這次新增的殘留」段:沒有附,這份 diff 沒改到那兩支檔。

## 查過但不構成問題
- 計劃〈天花板〉的「括號裡再出現任何一對括號(函式呼叫、`if`、`when`、註解括號)」,我逐項實跑,規則都不判,與文字一致。
- 預期值表新增的三列,與 C121~C123 的檔名、寫法、期望值一一對得上。
- 表態記錄裡「全是同步命令列流程」的說法與 diff 相符,沒有反證。
- 本案特定鏡頭③「每個新斷言想一個合理改壞」:`^` 錨點改壞已驗證會紅。`^visualTransformation`、`^keyboardOptions` 兩處我也想不出會產生失敗場景的輸入,與 r2 作者的判斷一致,不補例。

## 我建過的路徑
- `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/審查三-sonnet/`
  - `rule.yml`:密碼欄規則抽出的副本
  - `rule_mut.yml`:拿掉 `^` 的變異版
  - `src/`、`s2/`、`s3/`、`s4/`:實跑用的 kt 檔

最高等級 clean;blocking 0 條
