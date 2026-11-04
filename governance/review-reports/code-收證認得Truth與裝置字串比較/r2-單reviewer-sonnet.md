severity: major

派工詞檢查:鎖檔 `…/f6c34f9a….json.warming` 不存在,沒東西要處理。固定席節點本次未附,我另用 `lumos impact --file scripts/test_quality.py` 查了直接關聯,結果在第 5 節。

白話:修補把「Caused by 之後才有 Assert 堆疊就不認」的切法改成「從第一個堆疊行起算」。但判斷「第一個堆疊行」的正則太窄,碰到某些真實的堆疊行形狀就找不到,於是切點跑到 Caused by 區塊裡面,把原本該拒收的收進來。

## Findings

### 1. 第一個堆疊行認不出時,Caused by 內的 Assert 堆疊被當成本體,收窄的承諾失效
severity: major
blocking: 是
歸因:有證據的修復回歸(修前 c08dc36 判 False,修後 d5e8f27 判 True)
位置:`scripts/test_quality.py:137-139`
引句:「frame = re.search(r'\n[ \t]*at [\w$.]+\(', text)」

- **失敗輸入**:第一行是 `java.lang.AssertionError: x`,第一個堆疊行含 `<init>`、Kotlin 值類別的連字號(如 `plus-abc123`)、以 D8 脫糖產生的 `-$$Lambda$` 類別名,或 Kotlin 反引號含空白的方法名。接著是 `Caused by:` 區塊,區塊內才有 `at org.junit.Assert.fail(…)`。
- **執行路徑**:`[\w$.]+\(` 不收這些字元,所以第一個堆疊行被跳過。`frame` 落在 Caused by 內的 Assert 行,`cause` 從那一點往後找不到下一個 `Caused by:`。`own` 因此涵蓋 Caused by 區塊內的 Assert 堆疊,判成斷言失敗。
- **對照合約**:這違反計劃 S5 寫的「只在 Caused by 之後才有 Assert 堆疊的,都不應認定」,也違反驗證紀錄的「刻意收窄(寧可拒收)」。

三版同輸入結果(我在暫存複本載入三個版本的 `test_quality.py`,用 `junit()` 比對,base = 3383ff253):

| 輸入 | base | 修前 c08dc36 | 修後 d5e8f27 |
|---|---|---|---|
| 首個堆疊行 `at com.example.Foo.<init>(Foo.kt:3)`,其後 `Caused by: java.lang.IllegalStateException: y` 與 `at org.junit.Assert.fail(Assert.java:86)` | True | False | **True** |
| 首個堆疊行 `at com.example.Money.plus-abc123(Money.kt:3)`,其後同上 | True | False | **True** |
| 首個堆疊行 `at com.example.T.does the thing(T.kt:3)`,其後同上 | True | False | **True** |
| 對照:首個堆疊行 `at com.example.T.doesTheThing(T.kt:3)`,其後同上 | True | False | False |

- **影響範圍的限制**:要真的誤收,得是 `java.lang.AssertionError` 外殼的 Caused by 鏈裡帶 Assert 堆疊,條件偏窄。但它朝「放寬證據」的方向壞,而安全證據閘的 fault_sensitivity 路徑共用這個判定。
- **測試為何沒抓到**:所有負例的首個堆疊行都是 `[\w$.]+`。我在複本把正則放寬成 `[^\s(]+`,測試照綠。
- **建議修法**:把「第一個堆疊行」改成較寬的 `\n[ \t]*at \S+\(`,並補上述三種形狀的負例。

### 2. 陣列比較型別沒有近似名反例
severity: minor
blocking: 否
位置:`scripts/test_quality.py:118`、`scripts/test_test_quality_cli.py:250`
引句:「'org.junit.internal.ArrayComparisonFailure'):」

- `test_truth_lookalike_types_are_not_attributed` 只測 Truth 的近似名(別家套件同名、後面多字)。
- 我把陣列型別改成 `kind.endswith('ArrayComparisonFailure')`,或另加 `com.x.ArrayComparisonFailure`,43 個相關測試照綠。
- 修補宣稱要擋近似型別名,但新增的第三個型別沒有對應反例。
- 歸因:有證據的原有漏查(這個型別是修後才加,修前不存在)。

### 3. S5 綁定測試的說明點名了計劃裡已不存在的清單
severity: minor
blocking: 否
位置:計劃 S5、`scripts/test_lumos.py:120109`
引句:「[test:t_drill_quality_cli_cases_present](計劃點名的十支正反例方法都在)」

- 修後的計劃本文沒有列出這十支方法名(grep 為 0 次),名單只在 `Systems/test-quality-cli.md` 的 PITFALL 行和測試本身。
- 測試 docstring 的「計劃點名的」同樣懸空。
- 歸因:有證據的修復回歸。修前 S5 本文列了六支,修後換成引用,但沒把名單搬回來。

### 4. 文件說「第一個堆疊行之後」,實際是從第一個堆疊行起算
severity: minor
blocking: 否
位置:標準 `test-quality-standard.md`、計劃 S5
引句:「而且第一個堆疊行之後第一個 `Caused by:` 之前有 JUnit `Assert` 或 Hamcrest `MatcherAssert.assertThat` 堆疊」

- 程式 `own = text[frame.start():…]` 把第一個堆疊行本身算進去。
- 測試 CRLF 那條只有一個堆疊行 `at org.junit.Assert.fail`,也判通過。
- 照字面讀,「只有一個 Assert 堆疊行」會被當成不收。
- 歸因:有證據的修復回歸(措辭是這一輪新寫的)。

### 5. 沒解的「包成 IllegalStateException」現象沒有回頭條件
severity: minor
blocking: 否
位置:驗證紀錄「外推邊界」
引句:「這是收證工具原本就有的歸因面,這批沒動,排進下一份計劃查。」

- 專案規則第 4 條要求承認風險時附 `REVISIT:`。
- 我在 `Verification/…實機演練.md` 和計劃全文 grep REVISIT,找不到這件事的條目。
- 計劃只為另外三件事各寫一行 REVISIT,「排進下一份計劃」是沒人會回頭的純散文。
- 歸因:有證據的原有漏查(這句是新加的)。

## 已驗為正常的主張(兩版證據)

- **二次方已修**:輸入為 `java.lang.AssertionError: x` + N 個 `\n` + Assert 堆疊行。N=10000/20000/40000 時,修前 0.167/0.668/2.657 秒(確為二次方),修後 0.001/0.002/0.003 秒。
- **其他對抗輸入修後都線性**:共 13 種(20 萬換行、換行加空白、CRLF、無右括號的超長詞、20 萬行 `at`、5 倍長的 `Assert.assert…` 字串等),每種都在 0.002 到 0.074 秒內。
- **repair(近似型別名)**:Truth 近似名、`AssertionErrorX`、`ComparisonFailureX`、Hamcrest 的 `org.hamcrest.Other.assertThat` 都判 False。我把 Hamcrest 放寬成 `org\.hamcrest\.\w+\.assertThat`,測試轉紅。
- **preserve**:
  - 裝置字串比較、不帶訊息的 `AssertionError`、Hamcrest、訊息自帶 `Caused by:` 行、前導空行與 CRLF,修後都判 True;其中 Hamcrest 修前是 False。
  - 訊息提到斷言名的一般例外維持 False。
  - 把 Truth 型別拿掉後,兩支安全閘測試轉紅,紅的原因是 `receipt_hash_mismatch` 與 `nonassertion_failure`,不是指紋不符。我同步更新了指紋表,排除指紋不符這個干擾。
- **變異實驗**:
  - 被殺掉的:切點改成從頭找、不切 Caused by、`own` 延伸到結尾、無框架時用整份文字、`fail|assert` 縮成 `fail`、Hamcrest 放寬、第一行前綴放寬、不 strip 全文。
  - 倖存的:陣列近似名(見 #2)、拿掉 `[ \t]*`(裝置樣本都在第 0 欄,不構成失敗場景)、拿掉 `\b`、第一行不 strip(`.` 吃掉 `\r`)。這幾條沒有具體失敗輸入,不另報。
- **指紋與測試**:`test_quality.py` 的 sha256 與指紋表一致(`ad4702a5…`)。`python3.14 scripts/test_test_quality_cli.py` 為 64 項 OK。`-k secev_drill` 為 7 項通過、`-k secev_s07` 為 5 項通過,`t_drill_quality_cli_cases_present` 與 `t_test_quality_standard_android_drill_lessons` 都通過。
- **舊新收據**:`load_receipt_data` 比對 `cases != r.get('tests')`,拒收碼 `receipt_hash_mismatch`、訊息 `recorded test outcomes differ from raw report`,與文件一致。`capture` 的舊報告拒絕(`stale report refused`)也與計劃描述一致。
- **語料回歸**:repo 內 86 份真實 XML 在三版之間的歸因零差異。

## 三問

1. **原問題的修復效果**:近似型別名不認、二次方已消除、Hamcrest 與訊息內 Caused by 已認,證據如上。唯一例外是 #1,收窄在首個堆疊行形狀特殊時失效。
2. **修補處的正常、錯誤與相鄰呼叫路徑**:
   - 本機型別路徑、一般斷言、`fault_check` 與 `_secev_junit_declared` 的流向都成立。
   - 未驗:安全證據閘沒有直接用「裝置文字」輸入跑 fault_sensitivity 路徑(測試輔助只能造本機型別),只靠共用同一個函式。
3. **新發現在修前、修後的結果**:#1 修前 False、修後 True(已列表)。#2 到 #5 是修後才有或文件層級的問題,修前沒有對應行為可比。

## 圖譜鏡頭

- `lumos impact` 的直接關聯是 `Systems/test-quality-cli`(此檔的家)、`Projects/安全主張驗收閘_計劃`、`Verification/測試品質第四輪修補驗證`。
- 唯一牽連到的合約是安全閘計劃 S7(非斷言失敗不得算成抓到錯)。S7 的綁定測試通過,但 #1 表示判定函式在特殊堆疊形狀下仍可能把非斷言算成斷言,屬 S7 精神上的缺口。
- 其餘節點的描述不受這份 diff 影響。

## 未驗範圍

- 真機 AGP 報告的其他輸出格式。
- Suppressed 段內的 Assert 堆疊:作者已註明照舊,我只確認修前、修後行為相同。
- 設計審折入與卷證去識別化部分(B 包)。
- `test_lumos.py` 全套(依規定留給推送前的閘)。

我建立的暫存已用字面絕對路徑刪除。

總結:最嚴重等級 major,blocking 1 條
