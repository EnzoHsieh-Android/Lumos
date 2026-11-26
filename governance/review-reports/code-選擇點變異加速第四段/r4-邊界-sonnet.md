severity: minor

我替極端輸入發聲:新的殼層元字元擋門把該擋的都擋住了,也沒有誤擋常見的合法寫法。能找到的只有兩條 minor,都只影響速度,不改變判定。

## 已驗主張

我載入修後 `scripts/lumos`,用 python3.14 對 `_choice_merge_shape`、`_choice_merge_cmd`、`_choice_merge_events` 餵輸入。修前版用 `git show 1265bdf4:scripts/lumos` 取出對照。

**形狀判斷**

- 這些合法寫法修前修後都照樣合併,沒被誤擋:
  - `--tests {method}`
  - `--tests '*{method}'`
  - `--tests="{method}"`
  - `--tests "{method}" > out.txt`
  - `{method} 2>&1 | tee o`
  - `gradlew.bat ... --tests {method}`
  - `cd x && ./gradlew ...`
- 這些寫法修前會判成可合併(seg 含元字元),修後都回 None:
  - `{method}&& echo`
  - `{method};echo`
  - `{method}|tee o`
  - `{method}>out`
  - `{method}2>&1`
  - `{method}&`
- 漏掉的三種貼身寫法:反引號、`$(...)`、`(...{method})` 子殼層。實測它們組出的合併指令在 `sh -c` 下都是語法錯誤,rc=2。
  - 結果是合併基準判不乾淨,最多多跑一次不帶腳本的重試,最後回逐支流程。
  - 沒有 rc 為 0 的錯誤合併,所以不構成判錯。

**事件行解析**

- 這些輸入都正確處理或安全降級,沒有丟例外:
  - 空輸出與 None
  - CRLF
  - `a()` 與 `a[1]` 這類參數化名稱
  - 截斷標記
  - 同名重跑
  - ANSI 字元:行首不是空白,但結尾不是事件字樣,所以回 None
  - `ba` 不會誤對 `a`
- 舊帳缺欄:`merge_init_off` 缺欄時,讀取端(`scripts/lumos:18571`)用 `or {}` 當空字典。
- 剩下時限為 0 或負數:`max(mg.remaining(), 1.0)` 夾住,重試上限也是 `min(cap, max(remaining, 1.0))`。

## Finding

**1. 引號內的合法元字元被新規則擋掉,這個壞法只走逐支(只慢不錯)**

- 引句:「if any(ch in seg for ch in "&;|<>"):   # 含 {method} 的那一段緊接殼層元字元」
- file: `scripts/lumos:28811`
- 輸入:`./gradlew :app:testDebugUnitTest --tests "x>{method}"`,或 `--tests 'a|{method}'`。
- 修前:判成可合併,組出 `--tests "x>a" --tests "x>b"`,語意正確。
- 修後:回 None,整個平台組不合併。
- 後果:`seg` 的檢查沒看引號,引號內的元字元也被擋。逐支判定不變,只失去加速。
- 現實性:Gradle 篩選字串幾乎不會用這些字元,觸發機率低。
- 歸因:有證據的修復回歸。
- 修前命令:`git -C /Users/enzo/harness/lumos-choice-speed4 show 1265bdf4377121730725a6d930893c5fbc0c04e6:scripts/lumos` 載入後呼叫 `_choice_merge_shape`,回傳 dict,seg 是 `"x>{method}"`。
- 修後命令:載入 `scripts/lumos` 後呼叫同一函式,回傳 None。
severity: minor
blocking: 否

**2. `_choice_merge_events` 對名單與事件數相乘,上千支測試時單次呼叫要數秒(只慢)**

- 引句:「evs = [e for f, e in last.items() if _choice_merge_hits([f], m) > 0]」
- file: `scripts/lumos:28925`
- 輸入:3000 支測試,每支一行 STARTED 與一行 PASSED,names 也是 3000 支。
- 結果:單次約 2.8 秒;修前版同一輸入約 2.7 秒。
- 影響:每個沒跑乾淨的快篩都會呼叫一次,所以每個壞法多這一筆。256KB 的輸出上限讓它有上界,而且逾時本身遠比它慢。
- 歸因:有證據的原有漏查(修前就有,修補未改這段)。
severity: minor
blocking: 否

## 未驗範圍

- 沒有真跑 Gradle 或 Windows 的 `cmd.exe`,Windows 只驗了字串形狀。
- `{method}\` 緊貼反斜線的寫法,我判斷會組成 `a --tests b` 這種單一參數,Gradle 會報找不到測試而回退。只做了推理,沒有實跑。
- 圖譜固定席的逐條判讀,以及「殘留段」的問答與代理對應,我沒有逐條核對。

最高 minor,blocking 0 條
