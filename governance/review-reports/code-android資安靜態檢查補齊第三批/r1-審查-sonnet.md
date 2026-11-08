severity: minor

我實跑了規則,三支針對性測試和 `check.py` 全過。沒有 major 以上的問題,只有兩條 minor。

實跑做了這些事:
- 把 `ast-grep` 放進 PATH,跑 `python3.14 scripts/test_lumos.py -k kotlin_rulepack_security_rules`,逐例表 C95~C116 共 187 項全過。
- 跑 `-k kt_catalog_security_lint_batch3` 與 `-k kt_catalog_stats_consistent`,都過。
- 跑 `check.py`,「規則 229 條,問題 0 個」。
- 用 `dt_table` 重數情境決策表,57 列的主寫 `(無)`、例外寫 `(無)`、兩段都 `(無)` 分別是 15、34、11,和型錄一致。
- 規則檔與卷證 `draft-rules-v3-pwd.yml.txt` 的規則本體逐行相同,凍結雜湊 `2eacf1e6…` 與該草稿一致(草稿的 message 是另一版,計劃准許進 repo 時改訊息與排版)。

另外跑了 17 種 Compose 寫法(尾隨 lambda、多行、無空白、引數換位、`remember { PasswordVisualTransformation() }`、巢狀 TextField、字串裡出現關鍵字、`NumberPassword`、`if-else` 鍵盤型別)。報與不報都符合〈範圍〉2 和預期值表。Jackson 另跑了 `?.`、`!!.`、換行點號、`also { it.… }`、型別參數、`::` 引用、字串與註解裡出現關鍵字,結果也都符合。

## Finding 1
severity: minor
blocking: 否
檔案:`configs/ast-grep/kotlin-android/rules/compose.yml`(新增的 `kt-compose-password-keyboard`)。

漏報場景:字面 `KeyboardOptions(...)` 裡只要有註解寫到 `KeyboardType.Password`,規則就不報。
- 輸入:
  ```
  TextField(value = p, onValueChange = {}, visualTransformation = PasswordVisualTransformation(),
      keyboardOptions = KeyboardOptions(
          imeAction = ImeAction.Done, // TODO: use KeyboardType.Password
      ))
  ```
- 路徑:`not: regex: 'KeyboardType\s*\.\s*(Number)?Password\b'` 對整個 value_argument 的原文比對,註解也算在內,所以判成「已設密碼鍵盤」。
- 實跑結果:命中數 0,實際上並沒有設密碼鍵盤。
- 括號寫在註解裡(`\([^()]*\)` 比不上)也會漏報。

這個漏報不在計劃〈天花板〉清單,也不在預期值表。形狀已凍結,只能寫進〈天花板〉並補一條逐例,不能改規則。我沒有給最小重現的測試,只有上面的實跑輸出。

引句:「regex: '^keyboardOptions\s*=\s*KeyboardOptions\s*(\.\s*Default|\([^()]*\))\s*$'」

## Finding 2
severity: minor
blocking: 否
檔案:`scripts/test_lumos.py` 的 `_KTSEC_CASES`(C95~C116)。

測試抓不到的改壞有兩個。兩者都不是驗收條款 S1 預期值表上的列,所以不升 major。
- Jackson 規則的正規式把 `activateDefaultTypingAsProperty`、`enableDefaultTypingAsProperty` 兩個名字拿掉,C113~C116 全綠。我實跑確認這兩個名字現在會報,但沒有任何逐例釘住。`samples/bad` 只有三處命中(`activateDefaultTyping` 兩處加 `enableDefaultTyping` 一處),不含 AsProperty。
- 密碼欄規則內層的 `(,|\)\s*$)` 拿掉逗號那支,也沒有案例變紅。C103 的 `KeyboardType.Text` 後面直接是 `)`,走的是另一支。「`keyboardType = KeyboardType.Text, imeAction = …`」這種寫法(〈範圍〉2 ② 文字有涵蓋)只靠規則本身,沒有案例。

引句:「regex: '\.\s*(activateDefaultTyping|enableDefaultTyping|activateDefaultTypingAsProperty|enableDefaultTypingAsProperty)$'」

## 圖譜固定席逐條判定與查過但不構成問題

**測試假綠形態(INVARIANT:還原翻紅釘要配前置斷言)**
- 新測試 `t_kt_catalog_security_lint_batch3` 的第一個改壞(刪 UI-112 列)有「★前置★ 刪列有套上」。
- 第二個改壞(多放 `D-57.kt.txt`)沒有獨立前置斷言,檢查函式是在檢查自己剛寫的檔存在。不過 `check.py` 的 `situation_sample_problems` 另外會抓「樣本沒有作用」,測試 ② 對真型錄也跑它。不構成假綠。
- 逐例表 S3 的案例有「報一次」和「不報」兩類。「不報」類一旦規則整個失效就會假綠,但同表裡「報一次」的案例會拉住,不影響合約。

**授權與歸屬、test-quality-handbook、arch-alignment-lens、bound-tests-gate、canary-audit、lumos-cli-read**
- 這份 diff 只動 `scripts/test_lumos.py` 的測試資料與新測試、規則包與型錄。
- 沒碰授權白名單、`search` 預設排除、`canary` 落盤、合約綁定測試閘。判不影響。

**回頭重讀指紋(RISK)**
- 沒改指紋計算相關程式。

**型錄與統計**
- 型錄三列、D-57、〈統計〉各數、`_KT_STATS_LINES` 都與計劃〈範圍〉1、3、4 一致,`stats_problems` 與測試寫死值同步。

**第二批計劃回頭條件**
- 三處改寫都附 `[closed:…]` 或指向第三批,格式與既有先例相同。

**表態記錄**
- 「全是同步命令列流程、無外呼」這項宣稱屬實。diff 只增加 Python 測試資料與一支純函式檢查,沒有新增子程序或迴圈。

我建過的路徑(都在 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第三批/審查-sonnet/` 底下):
- `src/main/kotlin/A.kt`
- `j/src/main/kotlin/J.kt`
- `j/src/main/kotlin/K.kt`
- `c/src/main/kotlin/C.kt`

最高等級 minor;blocking 0 條
