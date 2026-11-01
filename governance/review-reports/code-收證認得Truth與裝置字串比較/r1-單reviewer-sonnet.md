severity: major

白話:這次改動的程式本身(Truth 兩個精確型別、裝置那路改成第一行精確比對加 `Assert` 堆疊)在我走過的輸入上都正確。有問題的是文件對安全證據閘影響面的說法,它說錯了。另外有幾處反例測試擋不住稍微放寬的改法。

**環境與範圍**
- 鎖檔 `…/9d3d9961….json.warming` 不存在,沒有可處理的鎖。
- 派工詞沒附固定席節點,也沒附角色卡,這兩段略過。
- 配套指紋表與三支檔的實際 sha256 完全一致。
- 我用舊版(`3383ff2`)和新版 `test_quality.py` 對照跑了探針,並把 repo 內 40 份已提交的 `receipt.json` 配 `report.xml` 重算:判定結果一份都沒變,不會讓既有收據突然被拒。
- `python3.14 scripts/test_test_quality_cli.py`:新增六支全過。我設了不寫位元組碼的環境變數,所以另有三支位元組碼測試紅,與這份 diff 無關。
- `python3.14 scripts/test_lumos.py -k test_quality_standard_android`:32 支全過。
- 審後我已刪掉自己的暫存目錄 `/tmp/lumos-seat-work/code-收證認得Truth與裝置字串比較/單reviewer-sonnet`。

---

**1. 文件說安全證據閘「兩者都不放行」,但 fault_sensitivity 那條路改動後會放行**
severity: major
blocking: 是

引句:「同一個判定函式也被安全證據閘用:Truth 或字串比較寫的安全測試失敗時,判定從「無效:不是斷言失敗」變成「失敗:斷言失敗」;兩者都不放行。」

同樣的說法還出現在:
- 計劃的「守衛面」那條:「安全證據閘同一類失敗的判定也從無效變成斷言失敗」。
- `Systems/test-quality-cli` 新增的那條 PITFALL:「安全證據閘共用這個判定,同類失敗從無效變斷言失敗,兩者都不放行」。
- 驗證紀錄:「安全證據閘那組測試 625 支全綠」。

**實際行為**
安全證據閘用到這個判定有兩條路:
- **JUnit 宣告路徑**:`_secev_junit_facts` 加 `_secev_junit_declared`。這條路 `nonassertion_failure`(無效)變 `assertion_failed`(失敗),確實兩者都不放行,文件這部分是對的。
- **fault_sensitivity 路徑**:`_secev_judge_tq` 呼叫 `fault_check`。這條路的故障版只要失敗是「斷言失敗」就判 `detected`,而 `detected` 在閘裡是合格證據。

所以 Truth 型別或裝置字串比較寫的故障收據,在這條路原本被拒(`nonassertion_failure`),現在會被收下。這是新增的放行面,文件卻寫成「都不放行」。

最小重現(`fault_check` 實測,只差 `test_quality.py` 版本):
```
舊版(3383ff2): REJECT nonassertion_failure
新版(c08dc36): detected
```
做法:baseline 和 restored 用綠報告;fault 報告是
`<failure type='com.google.common.truth.ComparisonFailureWithFacts' message='m'>`,exit_code 1,實作快照不同,target 為 `C::t`。

放行 Truth 斷言本身是合理的設計。問題是:
- 文件把影響面寫反了,審查者據此會略過這條路。
- 證明這件事的 625 支測試都沒覆蓋「Truth 型別的故障收據過 `_secev_judge_tq`」。
- 計劃的回退段只說「判定回到原樣」,沒提這條路的放行會一起撤。

**建議**
- 四處文字改成區分兩條路。
- 在 `test_lumos.py` 補一支:Truth 型別的 fault 收據過 `_secev_judge_tq`,預期結果寫死。

---

**2. 反例測試擋不住「稍微放寬」的 Truth 型別比對與 ComparisonFailure 比對**
severity: minor
blocking: 否

引句:「if kind in ('com.google.common.truth.ComparisonFailureWithFacts', 'com.google.common.truth.AssertionErrorWithFacts'):」

我在副本上各做一次放寬,跑六支新增測試,結果全綠:
- 改成 `kind.endswith('WithFacts')`:仍綠。
- 改成用 `re.search(r'truth\.(?:Comparison|Assertion)\w*', kind)` 比對:仍綠。
- 在裝置那路,只把 `org\.junit\.ComparisonFailure` 後面加 `\w*`:仍綠。具體輸入是第一行 `org.junit.ComparisonFailureX: …` 加 `Assert` 堆疊,會被認成斷言失敗。

原因是反例只涵蓋 `Truth$SimpleAssertionError`(被前綴放寬擋住)和 `java.lang.AssertionErrorX`(被 search/startswith 擋住)。計劃自稱「精確型別」,但沒有近似型別名的反例。

**建議**
- 補 `com.example.ComparisonFailureWithFacts`、`com.google.common.truth.ComparisonFailureWithFactsX` 兩個反例。
- 補一個 `org.junit.ComparisonFailureX:` 反例。

我另外試了這幾種放寬,測試都會紅,不必補:
- 把 `fullmatch` 換成 `search`。
- 拿掉 `Caused by` 切分。
- 讓裸 `AssertionError` 必須帶冒號。
- 把 `kind` 改成 `startswith('com.google.common.truth.')`。

---

**3. 衛兵測試的 `--rerun` 檢查被 `--rerun-tasks` 滿足**
severity: minor
blocking: 否

引句:「("Gradle 跳過測試要強制重跑", "--rerun"),」

`w in sec` 是子字串比對。把標準裡單獨建議的 `--rerun` 刪掉、只留舊版替代 `--rerun-tasks`,`t_test_quality_standard_android_drill_lessons` 仍綠。計劃 S6 明寫要有「`--rerun`(舊版用 `--rerun-tasks`)」兩層。

**建議**:改成比對 `` `--rerun`(Gradle 7.6 ``,或用正則排除 `-tasks`。

---

**4. 標準與計劃引的錯誤訊息,不是工具實際輸出的字串**
severity: minor
blocking: 否

引句:「收據裡存著當時的歸因結果,收證工具換了版本,舊收據核對會回「記錄的結果跟原始報告不同」,要重收,不是偽造。」

`scripts/test_quality.py:381` 實際丟的是英文 `recorded test outcomes differ from raw report`,CLI 以 `{'verdict':'not_assessed','reason':...}` 輸出。中文字串不存在於任何程式輸出,守衛測試也只核對文件本身。照這句去搜輸出會找不到。

**建議**:引文改成英文原句,或註明是意譯。

---

**5. 「只看第一個例外」的說法與實作不符:Suppressed 區塊裡的 `Assert` 堆疊也算**
severity: minor
blocking: 否

引句:「裝置那路的 Assert 堆疊只看第一個例外(遇到 Caused by 之前),Caused by 底下才有 Assert 堆疊的不認。」

實作只切 `Caused by:`。我跑過這個輸入,新舊版都判 True:
```
java.lang.AssertionError: x
at com.H.check(H.kt:1)
	Suppressed: java.lang.IllegalStateException
at org.junit.Assert.fail(Assert.java:86)
```
這個 `Assert.fail` 屬於被抑制的例外,不是第一個例外。這也是舊版就有的行為,不是新增的洞。條件很人為,所以只算精度問題。

**建議**:文字改成「Caused by 之前」,不要寫「只看第一個例外」。

---

**6. 收窄了舊行為:Caused by 底下才有 `Assert` 堆疊的失敗,以前認、現在不認**
severity: minor
blocking: 否

引句:「own = re.split(r'\n\s*Caused by:', text, maxsplit=1)[0]」

舊版 `startswith('java.lang.AssertionError:')` 加整段文字找 `Assert` 堆疊,下面這種會判 True,新版判 False:
```
java.lang.AssertionError: expected:<10> but was:<0>
at com.x.T$a$1.invokeSuspend(T.kt:9)
(Coroutine boundary)
Caused by: java.lang.AssertionError: expected:<10> but was:<0>
at org.junit.Assert.fail(Assert.java:89)
```
這是我構造的輸入(形狀仿 kotlinx.coroutines 堆疊還原會產生的包裝),我沒有實跑報告可以證明裝置上會出現。

這個改動走的是不放行的方向(偏保守),測試 `test_device_runtime_around_comparison_failure_is_not_attributed` 的第 6 個案例也刻意釘住。但文件只說「新增認得什麼」,沒說「收窄了什麼」,計劃的舊收據說明只談新增型別。

**建議**:在驗證紀錄補一句,說明這是有意的取捨。

---

**文件事實主張逐項核對**
- 「零選中時沒有新報告、`capture` 在讀報告那一步就判無效、報告存在時 `--target` 才輪到」:與 `capture()` 的順序相符(先擋舊報告,再讀報告,再比對 target)。
- 「`--report` 一次只收一個檔」:`add_argument('--report', type=Path)`,相符。
- 「Gradle 7.6 起有 `--rerun`」:與我所知 Gradle 7.6 起才有相符,我沒有上網複核。
- 「`capture` 要求報告在跑之前不存在」:`report must be new; stale report refused`,相符。
- 「Kotlin 靜態掃描沒帶 `--semgrep` 就回不完整、零候選」:程式碼為 `unsupported` 加 `complete=False` 加 exit 2,相符。但 `--semgrep` 其實需要一個可執行檔參數(`--semgrep EXECUTABLE`)。標準和 Systems 筆記寫「帶 `--semgrep`」沒說要給路徑,`03-寫回圖譜.md` 的範例才有路徑。建議補上,屬措辭精度。
- 正反例樣本形狀:AGP 儀器報告 `failure` 沒有 `type`/`message`、文字是堆疊,合理。我無法驗證樣本是否逐字來自平板實跑,原始檔在私有分支。
- 新舊互讀:舊工具讀新收據會因重算不同而拒收,失敗方向是保守的。
- 邊界輸入我實跑過:空字串、前導空行、尾端空白、小寫型別名、冒號後無訊息、訊息含換行,結果都合理。前導空行和尾端空白被 `strip()` 容忍,比「第一行剛好」的字面寬一點,無害。

severity: major
(最高值,第 1 條,文件對安全證據閘 fault_sensitivity 路徑影響面的說法有誤)
